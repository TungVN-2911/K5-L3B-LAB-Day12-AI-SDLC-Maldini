"""Buổi tối — Mở Quán. Luật khách, nấu ăn, phục vụ và tính tiền."""

import math

from ..errors import BadInput
from ..ids import sort_by_id
from ..inventory import validate_items
from .ramp import ramp_velocity

TICK = 60.0


class QuanSim:
    mode = "quan"
    phase = "quan"

    def __init__(self, tuning, scenario, streams, ids, inventory=None):
        t = tuning["quan"]
        self.t = t
        self.menu = tuning["menu"]
        self.rng = streams
        self.ids = ids
        p = scenario.get("player", {})
        self.pos = [float(c) for c in p.get("pos", t["start_pos"])]
        self.vel = [float(c) for c in p.get("vel", [0.0, 0.0])]
        self._tgt = None
        self._ramp_left = 0
        self.stock = dict(inventory if inventory is not None else scenario.get("stock", {}))
        self.hand = scenario.get("hand")
        self.time_left_ticks = scenario.get("time_left_ticks", int(round(t["duration_s"] * TICK)))
        self.elapsed_ticks = 0
        self.next_customer_tick = int(t["first_customer_tick"])
        self.customer_interval_ticks = max(1, int(round(t["customer_interval_s"] * TICK)))
        self.random_customers = scenario.get("random_customers", True)
        self.reputation = scenario.get("reputation", t["reputation_initial"])
        self.stoves = [dict(s, state=s.get("state", "idle"), dish=s.get("dish"),
                            cook_ticks_left=s.get("cook_ticks_left", 0), ready_ticks=s.get("ready_ticks", 0),
                            customer_id=s.get("customer_id"))
                       for s in self._merge(t["stoves"], scenario.get("stoves", []))]
        self.tables = self._merge(t["tables"], scenario.get("tables", []))
        self.customers = []
        for customer in sort_by_id(scenario.get("customers", [])):
            self.ids.reserve(customer["id"])
            self.customers.append(self._load_customer(customer))
        self.money = 0
        self.earned = 0
        self.shift_earned = 0
        self.done = False
        self.reason = None

    @staticmethod
    def _merge(defaults, updates):
        by_id = {d["id"]: dict(d) for d in defaults}
        for u in updates:
            if u["id"] not in by_id:
                raise BadInput(f"id bếp/bàn không tồn tại: {u['id']}")
            by_id[u["id"]].update(u)
        return sort_by_id(list(by_id.values()))

    def _ticks(self, seconds):
        return max(1, int(round(seconds * TICK)))

    def _recipe(self, dish_id):
        dish = self.menu.get(dish_id)
        if dish is None:
            raise BadInput(f"món không có trong menu: {dish_id}")
        return dish["recipe"]

    def _available_dishes(self):
        return [
            dish_id for dish_id in sorted(self.menu)
            if all(self.stock.get(kind, 0) >= count for kind, count in self.menu[dish_id]["recipe"].items())
        ]

    def _reserve_order(self, dish_id, reserved=None):
        recipe = self._recipe(dish_id)
        reservation = dict(recipe if reserved is None else validate_items(reserved))
        if reservation != recipe:
            raise BadInput(f"nguyên liệu giữ chỗ không khớp công thức món {dish_id}")
        if any(self.stock.get(kind, 0) < count for kind, count in reservation.items()):
            raise BadInput(f"kho không đủ nguyên liệu giữ chỗ cho món {dish_id}")
        for kind, count in reservation.items():
            self.stock[kind] -= count
        return reservation

    def _assign_order(self, customer):
        dishes = self._available_dishes()
        if not dishes:
            return False
        dish_id = self.rng.get("customer_orders").choice(dishes)
        customer["state"] = "assigned"
        customer["dish_id"] = dish_id
        customer["reserved"] = self._reserve_order(dish_id)
        customer.setdefault("price", self.menu[dish_id]["price"])
        return True

    def _load_customer(self, raw):
        customer = dict(raw)
        if not isinstance(customer.get("table_id"), str):
            raise BadInput("khách cần table_id")
        state = customer.get("state")
        if state is None:
            state = "assigned" if customer.get("dish_id") else "waiting"
        if state not in ("waiting", "assigned", "eating"):
            raise BadInput(f"trạng thái khách không hợp lệ: {state}")
        customer["state"] = state
        customer.setdefault("patience_ticks_left", self._ticks(self.t["patience_s"]))
        customer.setdefault("patience_ticks_max", self._ticks(self.t["patience_s"]))

        if state == "assigned":
            dish_id = customer.get("dish_id")
            if dish_id is None:
                raise BadInput(f"khách {customer.get('id')} trạng thái assigned phải có dish_id")
            else:
                customer["reserved"] = self._reserve_order(dish_id, customer.get("reserved"))
                customer.setdefault("price", self.menu[dish_id]["price"])
        elif state == "waiting":
            customer.setdefault("reserved", {})
            if customer.get("dish_id") is None:
                self._assign_order(customer)
            else:
                customer["reserved"] = self._reserve_order(customer["dish_id"], customer.get("reserved"))
                customer["state"] = "assigned"
                customer.setdefault("price", self.menu[customer["dish_id"]]["price"])
        else:
            if "price" not in customer or "tip" not in customer:
                raise BadInput(f"khách {customer.get('id')} đang ăn phải có price và tip")
            customer.setdefault("eat_ticks_left", self._ticks(self.t["eat_s"]))
            customer.setdefault("reserved", {})
        return customer

    def snapshot(self) -> dict:
        occupied = {c["table_id"]: c["id"] for c in self.customers}
        return {
            "player": {"pos": self.pos},
            "stock": {k: self.stock[k] for k in sorted(self.stock) if self.stock[k] > 0},
            "hand": self.hand,
            "stoves": [{k: s.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks")}
                       for s in self.stoves],
            "tables": [{"id": tb["id"], "pos": tb["pos"], "customer_id": occupied.get(tb["id"])} for tb in self.tables],
            "customers": sort_by_id(self.customers),
        }

    def step(self, inp):
        if self.done:
            return []
        events = []
        self.time_left_ticks = max(0, self.time_left_ticks - 1)
        self.elapsed_ticks += 1
        self._advance_customers(events)
        self._advance_stoves(events)
        self._move(inp)
        if inp.pressed("interact"):
            self._interact(events)
        self._spawn_customer(events)
        if self.time_left_ticks <= 0:
            self.done = True
            self.reason = "time"
            events.append(("quan_end", {"reason": "time", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
        return events

    def _advance_customers(self, events):
        remaining = []
        for customer in sort_by_id(self.customers):
            if customer["state"] == "eating":
                customer["eat_ticks_left"] = max(0, customer.get("eat_ticks_left", 0) - 1)
                if customer["eat_ticks_left"] == 0:
                    self._pay(customer, events)
                else:
                    remaining.append(customer)
                continue

            customer["patience_ticks_left"] = max(0, customer.get("patience_ticks_left", 0) - 1)
            if customer["patience_ticks_left"] == 0:
                self._customer_left(customer, events)
            else:
                remaining.append(customer)
        self.customers = remaining

    def _advance_stoves(self, events):
        for stove in self.stoves:
            if stove["state"] == "cooking":
                stove["cook_ticks_left"] = max(0, stove["cook_ticks_left"] - 1)
                if stove["cook_ticks_left"] == 0:
                    stove["state"] = "ready"
                    stove["ready_ticks"] = 0
                    events.append(("dish_ready", {"stove_id": stove["id"], "customer_id": stove.get("customer_id"),
                                                  "dish_id": stove["dish"]}))
            elif stove["state"] == "ready":
                stove["ready_ticks"] += 1

    def _customer_left(self, customer, events):
        in_cook = False
        for stove in self.stoves:
            if stove.get("customer_id") == customer["id"] and stove["state"] in ("cooking", "ready"):
                in_cook = True
                stove.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0, customer_id=None)
        if not in_cook:
            for kind, count in customer.get("reserved", {}).items():
                self.stock[kind] = self.stock.get(kind, 0) + count
        self.reputation = self._clamp_reputation(self.reputation + self.t["left_reputation_delta"])
        events.append(("customer_left", {"customer_id": customer["id"], "table_id": customer["table_id"],
                                         "reputation": self.reputation}))

    def _pay(self, customer, events):
        price = customer["price"]
        tip = customer["tip"]
        amount = price + tip
        self.money += amount
        self.earned += amount
        self.shift_earned += amount
        if tip > 0:
            self.reputation = self._clamp_reputation(self.reputation + self.t["tip_reputation"])
        events.append(("paid", {"customer_id": customer["id"], "dish_id": customer["dish_id"],
                                "price": price, "tip": tip, "amount": amount,
                                "money": self.money, "reputation": self.reputation}))

    def _clamp_reputation(self, reputation):
        return min(self.t["reputation_max"], max(self.t["reputation_min"], reputation))

    def _spawn_customer(self, events):
        if not self.random_customers or self.elapsed_ticks < self.next_customer_tick:
            return
        self.next_customer_tick += self.customer_interval_ticks
        occupied = {customer["table_id"] for customer in self.customers}
        free_tables = [table for table in self.tables if table["id"] not in occupied]
        if not free_tables:
            return

        customer_id = self.ids.new("C")
        table_id = free_tables[0]["id"]
        customer = {
            "id": customer_id,
            "table_id": table_id,
            "state": "waiting",
            "patience_ticks_left": self._ticks(self.t["patience_s"]),
            "patience_ticks_max": self._ticks(self.t["patience_s"]),
        }
        if not self._assign_order(customer):
            events.append(("no_dish", {"customer_id": customer_id, "table_id": table_id}))
            return
        self.customers.append(customer)
        events.append(("customer_arrived", {"customer_id": customer_id, "table_id": table_id,
                                            "dish_id": customer["dish_id"], "reserved": customer["reserved"]}))

    def _interact(self, events):
        candidates = []
        radius = self.t["interact_radius"]
        for stove in self.stoves:
            distance = math.dist(self.pos, stove["pos"])
            if distance <= radius:
                candidates.append((distance, 0, stove["id"], "stove", stove))
        for table in self.tables:
            distance = math.dist(self.pos, table["pos"])
            if distance <= radius:
                candidates.append((distance, 1, table["id"], "table", table))
        if not candidates:
            return
        _, _, _, kind, target = min(candidates, key=lambda candidate: candidate[:3])
        if kind == "stove":
            self._interact_stove(target, events)
        else:
            self._interact_table(target, events)

    def _interact_stove(self, stove, events):
        if stove["state"] == "idle" and self.hand is None:
            cooking = {s.get("customer_id") for s in self.stoves if s["state"] in ("cooking", "ready")}
            customer = next((c for c in sort_by_id(self.customers)
                             if c["state"] == "assigned" and c["id"] not in cooking), None)
            if customer is None:
                return
            dish_id = customer["dish_id"]
            stove.update(state="cooking", dish=dish_id, cook_ticks_left=self._ticks(self.menu[dish_id]["cook_s"]),
                         ready_ticks=0, customer_id=customer["id"])
            customer["reserved"] = {}
            events.append(("cook_started", {"stove_id": stove["id"], "customer_id": customer["id"],
                                            "dish_id": dish_id}))
        elif stove["state"] == "ready" and self.hand is None:
            self.hand = {"dish_id": stove["dish"], "customer_id": stove.get("customer_id"),
                         "price": self.menu[stove["dish"]]["price"]}
            events.append(("dish_picked", {"stove_id": stove["id"], "customer_id": stove.get("customer_id"),
                                           "dish_id": stove["dish"]}))
            stove.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0, customer_id=None)

    def _interact_table(self, table, events):
        if self.hand is None:
            return
        customer = next((c for c in self.customers if c["table_id"] == table["id"]), None)
        if customer is None or customer["state"] != "assigned":
            return
        dish_id = self.hand if isinstance(self.hand, str) else self.hand.get("dish_id")
        hand_customer_id = None if isinstance(self.hand, str) else self.hand.get("customer_id")
        if dish_id != customer.get("dish_id") or (hand_customer_id and hand_customer_id != customer["id"]):
            return

        patience_max = max(1, customer.get("patience_ticks_max", self._ticks(self.t["patience_s"])))
        patience_ratio = customer.get("patience_ticks_left", patience_max) / patience_max
        tip = int(round(customer.get("price", self.menu[dish_id]["price"]) * self.t["tip_rate"])) \
            if patience_ratio >= self.t["tip_min_patience_ratio"] else 0
        customer.update(state="eating", eat_ticks_left=self._ticks(self.t["eat_s"]),
                        price=customer.get("price", self.menu[dish_id]["price"]), tip=tip, reserved={})
        self.hand = None
        events.append(("served", {"customer_id": customer["id"], "table_id": table["id"],
                                  "dish_id": dish_id, "price": customer["price"], "tip": tip}))

    def _move(self, inp):
        speed = self.t["walk_speed"]
        mx, mz = inp.move
        self.vel = ramp_velocity(self, (mx * speed, mz * speed), int(self.t.get("ramp_max_ticks", 6)))
        b = self.t["bounds"]
        for i, axis in enumerate(("x", "z")):
            self.pos[i] += self.vel[i] / TICK
            lo, hi = b[axis]
            if self.pos[i] <= lo:
                self.pos[i], self.vel[i] = lo, max(0.0, self.vel[i])
            elif self.pos[i] >= hi:
                self.pos[i], self.vel[i] = hi, min(0.0, self.vel[i])
