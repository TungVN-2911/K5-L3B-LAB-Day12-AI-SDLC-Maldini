"""Phần SÁNG TẠO của nhóm — chỉ dùng ở cửa sổ chơi `python -m chonoi.live --mode day`.

Headless / Test Contract KHÔNG dùng file này: `GatherSim`, `QuanSim` gốc giữ nguyên hành vi.
Hai lớp con ở đây thêm luật mới lên trên lớp gốc:

GatherPlus (buổi sáng):
  - vật phẩm buff dưới nước: `oxy` (đầy oxy + không tụt oxy một lúc), `net` (lưới lớn: bán kính bắt
    rộng hơn, một lần bắt hết cá trong tầm), `gun` (súng xiên: Space bắn mũi xiên theo hướng mặt)
  - cá lớn có Máu (cá đuối, cá bông lau): tuần tra, thấy người thì đuổi, chạm thì trừ Máu người chơi;
    đánh bằng Space (cận chiến) hoặc súng xiên; hạ được thì rơi nguyên liệu quý vào giỏ, sau đó hồi sinh
  - cá nhỏ sinh thêm theo thời gian để chơi nhiều ngày
QuanPlus (buổi tối, quầy bar nhìn ngang):
  - nhiều ghế, khách đến dồn dập, mỗi khách gọi một món làm được từ kho (không giữ chỗ nguyên liệu)
  - bấm E ở bếp trống -> mở bảng nấu: chọn món cho bếp TỰ nấu (chậm, chất lượng "good") hoặc
    TỰ CHỌN NGUYÊN LIỆU (đúng công thức -> nhanh, "great"; sai -> hỏng, mất nguyên liệu)
  - món để lâu trên bếp thành "cold"; cảm xúc khách = chất lượng món + thời gian chờ -> tip, uy tín
  - hết nguyên liệu bán được -> kết thúc ca (`sold_out`)

Số liệu đọc từ `chonoi/data/extras.json`; ngẫu nhiên đi qua `Streams` với luồng riêng `extras_*`.
"""

import copy
import json
import math
import os

from ..ids import sort_by_id
from ..inputs import InputState
from .gather import TICK, GatherSim
from .quan import QuanSim

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "extras.json")


def load_extras(path=DATA_PATH) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def merged_tuning(tuning: dict, extras: dict) -> dict:
    """Tuning gốc + phần ghi đè của chế độ day (không sửa dict gốc)."""
    t = copy.deepcopy(tuning)
    t["quan"].update(copy.deepcopy(extras["quan"]["override"]))
    t["menu"].update(copy.deepcopy(extras.get("menu_extra", {})))
    return t


def makeable(menu: dict, stock: dict) -> list:
    return [d for d in sorted(menu) if all(stock.get(k, 0) >= c for k, c in menu[d]["recipe"].items())]


def _ticks(seconds) -> int:
    return max(1, int(round(seconds * TICK)))


def _clamp(v, lo, hi):
    return lo if v < lo else hi if v > hi else v


# =====================================================================================
class GatherPlus(GatherSim):
    def __init__(self, tuning, scenario, streams, ids, extras):
        super().__init__(tuning, scenario, streams, ids)
        self.x = extras["gather"]
        self.buffs = {"net_ticks": 0, "gun_ammo": 0, "oxy_shield_ticks": 0}
        self.gun_cd_ticks = 0
        self.pickups = []
        self.projectiles = []
        self.big_fish = []
        for sp in self.x["big_fish_spawns"]:
            ids.reserve(sp["id"])
            k = self.x["big_kinds"][sp["kind"]]
            self.big_fish.append({"id": sp["id"], "kind": sp["kind"], "pos": [float(c) for c in sp["pos"]],
                                  "home": [float(c) for c in sp["pos"]], "patrol": list(sp["patrol"]),
                                  "dir": 1, "hp": k["hp"], "hp_max": k["hp"], "alive": True, "state": "patrol",
                                  "respawn_ticks": 0, "hurt_ticks": 0, "recoil_ticks": 0})
        self.elapsed = 0
        self.next_pickup = _ticks(self.x["pickup_first_s"])
        self.next_fish = _ticks(self.x["fish_respawn_s"])

    def _kind(self, f):
        return self.x["big_kinds"][f["kind"]]

    # --- một bước ---------------------------------------------------------------
    def step(self, inp):
        self.elapsed += 1
        b = self.buffs
        b["net_ticks"] = max(0, b["net_ticks"] - 1)
        b["oxy_shield_ticks"] = max(0, b["oxy_shield_ticks"] - 1)
        self.gun_cd_ticks = max(0, self.gun_cd_ticks - 1)
        catch = inp.pressed("catch")
        # nút catch do lớp này xử lý (bắn / đánh / lưới); lớp gốc lo bơi, oxy, hái, cập bến, đồng hồ
        base_inp = InputState(inp.move, inp.held, {"interact"} if inp.pressed("interact") else set())
        events = super().step(base_inp)
        if self.done:
            return events
        under = not self._at_surface()
        if under and b["oxy_shield_ticks"] > 0:
            self.oxygen_ticks = min(self.oxygen_max, self.oxygen_ticks + 1)  # bù lại phần lớp gốc vừa trừ
        if catch and under:
            self._use_catch(events)
        self._update_projectiles(events)
        self._update_big_fish(events, under)
        if self.done:
            return events
        self._update_pickups(events)
        self._respawn_fish(events)
        return events

    def _use_catch(self, events):
        gun = self.x["buffs"]["gun"]
        if self.buffs["gun_ammo"] > 0:
            if self.gun_cd_ticks > 0:
                return
            a = math.radians(self.heading)
            pid = self.ids.new("H")
            self.projectiles.append({"id": pid, "pos": list(self.pos),
                                     "vel": [math.cos(a) * gun["speed"], math.sin(a) * gun["speed"]], "dist": 0.0})
            self.buffs["gun_ammo"] -= 1
            self.gun_cd_ticks = _ticks(gun["cooldown_s"])
            events.append(("harpoon_fired", {"id": pid, "ammo": self.buffs["gun_ammo"]}))
            return
        if self.catch_cd_ticks > 0:
            return
        cd = int(round(self.t["catch_cooldown_s"] * TICK))
        reach = self.t["catch_radius"]
        bigs = [f for f in self.big_fish
                if f["alive"] and math.dist(self.pos, f["pos"]) <= reach + self._kind(f)["hit_radius"]]
        if bigs:
            f = min(bigs, key=lambda f: (math.dist(self.pos, f["pos"]), f["id"]))
            self.catch_cd_ticks = cd
            self._damage_big(f, self.x["melee_damage"], "melee", events)
            return
        net = self.buffs["net_ticks"] > 0
        radius = reach * (self.x["buffs"]["net"]["radius_mult"] if net else 1)
        cands = sorted((f for f in self.fish if math.dist(self.pos, f["pos"]) <= radius),
                       key=lambda f: (math.dist(self.pos, f["pos"]), f["id"]))
        if not net:
            cands = cands[:1]
        caught = False
        for fish in cands:
            if not self._try_catch(fish, events, "net" if net else "hand"):
                break
            caught = True
        if caught:
            self.catch_cd_ticks = cd

    def _try_catch(self, fish, events, tool):
        amount = int(self.t["fish_yield"][fish["kind"]])
        if len(self.hold) + amount > self.t["hold_capacity"]:
            events.append(("hold_full", {"source": "fish", "fish_id": fish["id"]}))
            return False
        self.hold.extend([fish["kind"]] * amount)
        self.fish.remove(fish)
        events.append(("fish_caught", {"fish_id": fish["id"], "kind": fish["kind"], "yield": amount, "tool": tool}))
        return True

    def _damage_big(self, f, dmg, tool, events):
        f["hp"] = max(0, f["hp"] - dmg)
        f["hurt_ticks"] = 12
        f["recoil_ticks"] = 30
        events.append(("big_fish_hit", {"id": f["id"], "kind": f["kind"], "hp": f["hp"], "damage": dmg, "tool": tool}))
        if f["hp"] > 0:
            return
        k = self._kind(f)
        f["alive"] = False
        f["respawn_ticks"] = _ticks(k["respawn_s"])
        drop = [kind for kind in sorted(k["drop"]) for _ in range(k["drop"][kind])]
        if len(self.hold) + len(drop) > self.t["hold_capacity"]:
            events.append(("hold_full", {"source": "big_fish", "fish_id": f["id"]}))
            got = {}
        else:
            self.hold.extend(drop)
            got = dict(k["drop"])
        events.append(("big_fish_defeated", {"id": f["id"], "kind": f["kind"], "drop": got, "pos": list(f["pos"])}))

    def _update_projectiles(self, events):
        gun = self.x["buffs"]["gun"]
        bx, bd = self.t["bounds"]["x"], self.t["bounds"]["d"]
        keep = []
        for p in self.projectiles:
            dx, dd = p["vel"][0] / TICK, p["vel"][1] / TICK
            p["pos"] = [p["pos"][0] + dx, p["pos"][1] + dd]
            p["dist"] += math.hypot(dx, dd)
            hit = next((f for f in sort_by_id(self.big_fish)
                        if f["alive"] and math.dist(p["pos"], f["pos"]) <= self._kind(f)["hit_radius"]), None)
            if hit:
                self._damage_big(hit, gun["damage"], "harpoon", events)
                continue
            small = [f for f in self.fish if math.dist(p["pos"], f["pos"]) <= gun["fish_hit_radius"]]
            if small:
                self._try_catch(min(small, key=lambda f: (math.dist(p["pos"], f["pos"]), f["id"])), events, "harpoon")
                continue
            if (p["dist"] >= gun["range"] or p["pos"][1] < 0 or not bx[0] <= p["pos"][0] <= bx[1]
                    or p["pos"][1] > bd[1]):
                continue
            keep.append(p)
        self.projectiles = keep

    def _update_big_fish(self, events, under):
        bx, bd = self.t["bounds"]["x"], self.t["bounds"]["d"]
        for f in sort_by_id(self.big_fish):
            k = self._kind(f)
            if not f["alive"]:
                f["respawn_ticks"] -= 1
                if f["respawn_ticks"] <= 0:
                    f.update(alive=True, hp=f["hp_max"], pos=list(f["home"]), state="patrol", recoil_ticks=0)
                    events.append(("big_fish_respawn", {"id": f["id"]}))
                continue
            f["hurt_ticks"] = max(0, f["hurt_ticks"] - 1)
            dx, dd = self.pos[0] - f["pos"][0], self.pos[1] - f["pos"][1]
            dist = math.hypot(dx, dd)
            ux, ud = (dx / dist, dd / dist) if dist > 1e-6 else (float(f["dir"]), 0.0)
            if f["recoil_ticks"] > 0:
                f["recoil_ticks"] -= 1
                f["state"], speed, ux, ud = "recoil", k["speed"], -ux, -ud
            elif under and dist <= k["aggro"]:
                f["state"], speed = "chase", k["chase_speed"]
            else:
                f["state"], speed = "patrol", k["speed"]
                if f["pos"][0] <= f["patrol"][0]:
                    f["dir"] = 1
                elif f["pos"][0] >= f["patrol"][1]:
                    f["dir"] = -1
                ux, ud = float(f["dir"]), _clamp((f["home"][1] - f["pos"][1]) * 0.3, -0.5, 0.5)
            vx, vd = ux * speed, ud * speed
            if abs(vx) > 0.05:
                f["dir"] = 1 if vx > 0 else -1
            f["pos"][0] = _clamp(f["pos"][0] + vx / TICK, bx[0], bx[1])
            f["pos"][1] = _clamp(f["pos"][1] + vd / TICK, k["min_depth"], bd[1])
            if under and self.invuln_ticks == 0 and math.dist(self.pos, f["pos"]) <= k["hit_radius"]:
                self.hp = max(0, self.hp - k["damage"])
                self.invuln_ticks = _ticks(self.x["hurt_invuln_s"])
                f["recoil_ticks"] = _ticks(self.x["big_recoil_s"])  # cắn xong thì bơi ra xa một lúc
                kb = self.x["knockback_m"]  # đẩy người chơi ra xa con cá
                px, pd = (dx / dist, dd / dist) if dist > 1e-6 else (float(f["dir"]), 0.0)
                self.pos[0] = _clamp(self.pos[0] + px * kb, bx[0], bx[1])
                self.pos[1] = _clamp(self.pos[1] + pd * kb, bd[0], bd[1])
                events.append(("player_hurt", {"by": f["id"], "kind": f["kind"], "hp": self.hp}))
                if self.hp <= 0:
                    events.append(("faint", {"hp": 0}))
                    self.hold.clear()
                    self._finish("fainted", events)
                    return

    def _update_pickups(self, events):
        x = self.x
        if self.elapsed >= self.next_pickup:
            self.next_pickup += _ticks(x["pickup_spawn_s"])
            if len(self.pickups) < x["pickup_max"]:
                r = self.rng.get("extras_pickups")
                kinds = sorted(x["pickup_weights"])
                kind = r.choices(kinds, weights=[x["pickup_weights"][k] for k in kinds])[0]
                pos = [round(r.uniform(*x["pickup_x"]), 2), round(r.uniform(*x["pickup_depth"]), 2)]
                p = {"id": self.ids.new("P"), "kind": kind, "pos": pos}
                self.pickups.append(p)
                events.append(("pickup_spawned", dict(p)))
        for p in sort_by_id(list(self.pickups)):
            if math.dist(self.pos, p["pos"]) <= x["pickup_radius"]:
                self.pickups.remove(p)
                self._apply_buff(p["kind"])
                events.append(("pickup", {"id": p["id"], "kind": p["kind"], "buffs": dict(self.buffs)}))

    def _apply_buff(self, kind):
        cfg = self.x["buffs"][kind]
        if kind == "oxy":
            self.oxygen_ticks = self.oxygen_max
            self.zero_oxy_ticks = 0
            self.buffs["oxy_shield_ticks"] = _ticks(cfg["shield_s"])
        elif kind == "net":
            self.buffs["net_ticks"] = _ticks(cfg["duration_s"])
        elif kind == "gun":
            self.buffs["gun_ammo"] = min(cfg["ammo_max"], self.buffs["gun_ammo"] + cfg["ammo"])

    def _respawn_fish(self, events):
        x = self.x
        if self.elapsed < self.next_fish:
            return
        self.next_fish += _ticks(x["fish_respawn_s"])
        if len(self.fish) >= x["fish_max"]:
            return
        r = self.rng.get("extras_fish")
        f = {"id": self.ids.new("F"), "kind": r.choice(x["fish_kinds"]),
             "pos": [round(r.uniform(*x["fish_x"]), 2), round(r.uniform(*x["fish_depth"]), 2)],
             "heading_deg": r.choice([0, 180])}
        self.fish.append(f)
        events.append(("fish_spawned", {"fish_id": f["id"], "kind": f["kind"]}))

    def snapshot(self) -> dict:
        s = super().snapshot()
        s["buffs"] = dict(self.buffs)
        s["gun_cd_ticks"] = self.gun_cd_ticks
        s["pickups"] = [{"id": p["id"], "kind": p["kind"], "pos": list(p["pos"])} for p in sort_by_id(self.pickups)]
        s["big_fish"] = [{k: (list(f[k]) if k == "pos" else f[k])
                          for k in ("id", "kind", "pos", "dir", "hp", "hp_max", "alive", "state", "hurt_ticks")}
                         for f in sort_by_id(self.big_fish)]
        s["projectiles"] = [{"id": p["id"], "pos": list(p["pos"]), "vel": list(p["vel"])} for p in self.projectiles]
        return s


# =====================================================================================
class QuanPlus(QuanSim):
    def __init__(self, tuning, scenario, streams, ids, inventory, extras):
        self.x = extras["quan"]
        super().__init__(merged_tuning(tuning, extras), scenario, streams, ids, inventory=dict(inventory or {}))
        self.stock = {k: v for k, v in self.stock.items() if v > 0}
        self.ui = None
        self._actions = []
        for st in self.stoves:
            st.update(quality=None, cook_ticks_total=0, auto=False)

    # --- hành động từ bảng nấu (live gửi qua /action) ----------------------------
    def queue_action(self, action: dict):
        self._actions.append(action)

    def step(self, inp):
        if self.done:
            return []
        events = []
        actions, self._actions = self._actions, []
        for a in actions:
            self._apply_action(a, events)
        events += super().step(inp)
        if not self.done:
            self._check_unservable(events)
        if self.ui:
            st = self._stove(self.ui["stove_id"])
            if st is None or st["state"] != "idle" or math.dist(self.pos, st["pos"]) > self.t["interact_radius"] + 0.3:
                self.ui = None
        if not self.done and not self._can_sell():
            self.done = True
            self.reason = "sold_out"
            self.customers = [c for c in self.customers if c["state"] == "eating"]
            events.append(("quan_end", {"reason": "sold_out", "money": self.money, "earned": self.earned,
                                        "shift_earned": self.shift_earned, "reputation": self.reputation}))
        return events

    def _stove(self, sid):
        return next((s for s in self.stoves if s["id"] == sid), None)

    def _has(self, items):
        return all(self.stock.get(k, 0) >= n for k, n in items.items())

    def _consume(self, items):
        for k, n in items.items():
            self.stock[k] -= n
            if self.stock[k] <= 0:
                del self.stock[k]

    def _apply_action(self, a, events):
        kind = a.get("type")
        if kind == "close":
            self.ui = None
            return
        if kind == "trash":
            if self.hand is not None:
                events.append(("dish_trashed", {"dish_id": self.hand.get("dish_id")}))
                self.hand = None
            return
        if kind == "quick_cook":
            # nấu nhanh: bấm vào món / phiếu order -> bếp trống đầu tiên tự nấu, không cần đi tới bếp
            dish = a.get("dish_id")
            if dish not in self.menu:
                return
            st = next((st for st in self.stoves if st["state"] == "idle"), None)
            if st is None:
                events.append(("cook_failed", {"reason": "no_stove", "dish_id": dish}))
                return
            a = {"type": "cook", "stove_id": st["id"], "dish_id": dish, "_remote": True}
        elif kind != "cook":
            return
        st = self._stove(a.get("stove_id"))
        if st is None or st["state"] != "idle":
            return
        if not a.get("_remote") and math.dist(self.pos, st["pos"]) > self.t["interact_radius"] + 0.3:
            return
        if a.get("dish_id") is not None:
            dish = a["dish_id"]
            if dish not in self.menu:
                return
            recipe = self.menu[dish]["recipe"]
            if not self._has(recipe):
                events.append(("cook_failed", {"stove_id": st["id"], "reason": "missing", "dish_id": dish}))
                return
            self._consume(recipe)
            ticks, quality, auto = _ticks(self.menu[dish]["cook_s"] * self.x["auto_cook_mult"]), "good", True
        else:
            ing = a.get("ingredients")
            ok = (isinstance(ing, dict) and ing and
                  all(isinstance(k, str) and isinstance(v, int) and not isinstance(v, bool) and v > 0
                      for k, v in ing.items()) and sum(ing.values()) <= self.x["max_ingredients"])
            if not ok or not self._has(ing):
                events.append(("cook_failed", {"stove_id": st["id"], "reason": "missing"}))
                return
            ing = {k: ing[k] for k in sorted(ing)}
            self._consume(ing)
            dish = next((d for d in sorted(self.menu) if self.menu[d]["recipe"] == ing), None)
            if dish is None:
                self.ui = None
                events.append(("cook_failed", {"stove_id": st["id"], "reason": "wrong_recipe", "ingredients": ing}))
                return
            ticks, quality, auto = _ticks(self.menu[dish]["cook_s"]), "great", False
        st.update(state="cooking", dish=dish, cook_ticks_left=ticks, cook_ticks_total=ticks, ready_ticks=0,
                  quality=quality, auto=auto, customer_id=None)
        self.ui = None
        events.append(("cook_started", {"stove_id": st["id"], "dish_id": dish, "auto": auto, "quality": quality,
                                        "quick": bool(a.get("_remote"))}))

    # --- khách: gọi món theo kho còn "chưa hứa" cho đơn khác ----------------------
    def _pending_need(self):
        orders, supply = {}, {}
        for c in self.customers:
            if c["state"] == "assigned":
                orders[c["dish_id"]] = orders.get(c["dish_id"], 0) + 1
        for st in self.stoves:
            if st["state"] in ("cooking", "ready") and st["dish"]:
                supply[st["dish"]] = supply.get(st["dish"], 0) + 1
        if self.hand is not None:
            d = self.hand.get("dish_id")
            supply[d] = supply.get(d, 0) + 1
        need = {}
        for d, n in orders.items():
            k = max(0, n - supply.get(d, 0))
            for kind, cnt in self.menu[d]["recipe"].items():
                need[kind] = need.get(kind, 0) + cnt * k
        return need

    def _assign_order(self, customer):
        need = self._pending_need()
        free = {k: v - need.get(k, 0) for k, v in self.stock.items()}
        dishes = makeable(self.menu, free)
        if not dishes:
            return False
        dish = self.rng.get("customer_orders").choice(dishes)
        customer.update(state="assigned", dish_id=dish, reserved={}, price=self.menu[dish]["price"])
        return True

    def _spawn_customer(self, events):
        if not self.random_customers or self.elapsed_ticks < self.next_customer_tick:
            return
        self.next_customer_tick += self.customer_interval_ticks
        occupied = {c["table_id"] for c in self.customers}
        free = [t for t in self.tables if t["id"] not in occupied]
        if not free:
            return
        table = self.rng.get("extras_seats").choice(free)
        pat = self._ticks(self.t["patience_s"])
        c = {"table_id": table["id"], "state": "waiting", "patience_ticks_left": pat, "patience_ticks_max": pat}
        need = self._pending_need()
        free_stock = {k: v - need.get(k, 0) for k, v in self.stock.items()}
        can = makeable(self.menu, free_stock)
        missing = [d for d in sorted(self.menu) if d not in can]
        oos = bool(missing) and self.rng.get("extras_oos").random() < self.x["out_of_stock_order_chance"]
        if oos:  # khách gọi đúng món đã hết nguyên liệu
            dish = self.rng.get("extras_oos").choice(missing)
            c.update(state="assigned", dish_id=dish, reserved={}, price=self.menu[dish]["price"])
        elif not self._assign_order(c):
            return
        c["id"] = self.ids.new("C")
        c["look"] = self.rng.get("extras_looks").randrange(1000)
        self.customers.append(c)
        events.append(("customer_arrived", {"customer_id": c["id"], "table_id": c["table_id"], "dish_id": c["dish_id"]}))
        if oos:
            self._send_away(c, events)

    # --- hết nguyên liệu cho món khách gọi: báo khách, khách thất vọng rời quán -------
    def _order_plan(self):
        """Phân bổ đơn đang chờ (gấp nhất trước): món đang nấu / xong / trên tay trước, rồi tới kho."""
        supply = {}
        for st in self.stoves:
            if st["state"] in ("cooking", "ready") and st["dish"]:
                supply.setdefault(st["dish"], []).append(st["state"])
        if self.hand is not None:
            supply.setdefault(self.hand.get("dish_id"), []).append("in_hand")
        free = dict(self.stock)
        plan = []
        waiting = sorted((c for c in self.customers if c["state"] == "assigned"),
                         key=lambda c: (c["patience_ticks_left"], c["id"]))
        for c in waiting:
            d = c["dish_id"]
            if supply.get(d):
                plan.append((c, supply[d].pop(0)))
                continue
            recipe = self.menu[d]["recipe"]
            if all(free.get(k, 0) >= n for k, n in recipe.items()):
                for k, n in recipe.items():
                    free[k] -= n
                plan.append((c, "waiting"))
            else:
                plan.append((c, "out_of_stock"))
        return plan

    def _check_unservable(self, events):
        for c, status in self._order_plan():
            if status == "out_of_stock":
                self._send_away(c, events)

    def _send_away(self, c, events):
        c.update(state="leaving", leave_ticks=self._ticks(self.x["leave_s"]), mood="that_vong")
        events.append(("out_of_stock", {"customer_id": c["id"], "table_id": c["table_id"], "dish_id": c["dish_id"]}))

    def _advance_customers(self, events):
        leaving = [c for c in self.customers if c["state"] == "leaving"]
        self.customers = [c for c in self.customers if c["state"] != "leaving"]
        super()._advance_customers(events)
        for c in sort_by_id(leaving):
            c["leave_ticks"] -= 1
            if c["leave_ticks"] > 0:
                self.customers.append(c)
                continue
            self.reputation = self._clamp_reputation(self.reputation + self.x["out_of_stock_rep"])
            events.append(("customer_left", {"customer_id": c["id"], "table_id": c["table_id"],
                                             "reputation": self.reputation, "reason": "out_of_stock",
                                             "mood": "that_vong", "dish_id": c["dish_id"]}))

    def _customer_left(self, customer, events):
        super()._customer_left(customer, events)
        events[-1][1].update(reason="patience", mood="tuc_gian", dish_id=customer.get("dish_id"))

    # --- bếp / phục vụ ---------------------------------------------------------
    def _interact_stove(self, stove, events):
        if stove["state"] == "idle" and self.hand is None:
            self.ui = {"type": "cook", "stove_id": stove["id"]}
            events.append(("cook_menu", {"stove_id": stove["id"]}))
        elif stove["state"] == "ready" and self.hand is None:
            q = stove.get("quality") or "good"
            if stove["ready_ticks"] > _ticks(self.x["cold_after_s"]):
                q = "cold"
            self.hand = {"dish_id": stove["dish"], "quality": q, "price": self.menu[stove["dish"]]["price"]}
            events.append(("dish_picked", {"stove_id": stove["id"], "dish_id": stove["dish"], "quality": q}))
            stove.update(state="idle", dish=None, cook_ticks_left=0, ready_ticks=0, customer_id=None,
                         quality=None, cook_ticks_total=0, auto=False)

    def _mood(self, ratio, quality):
        lo_hi = self.x["patience_bands"]
        score = self.x["quality_score"].get(quality, 0) + (2 if ratio >= lo_hi[0] else 1 if ratio >= lo_hi[1] else 0)
        for m in self.x["moods"]:
            if score >= m["min_score"]:
                return m
        return self.x["moods"][-1]

    def _interact_table(self, table, events):
        if self.hand is None:
            return
        c = next((c for c in self.customers if c["table_id"] == table["id"]), None)
        if c is None or c["state"] != "assigned":
            return
        dish = self.hand.get("dish_id")
        if dish != c["dish_id"]:
            events.append(("wrong_dish", {"customer_id": c["id"], "table_id": table["id"], "want": c["dish_id"], "got": dish}))
            return
        ratio = c["patience_ticks_left"] / max(1, c["patience_ticks_max"])
        m = self._mood(ratio, self.hand.get("quality"))
        tip = int(round(c["price"] * m["tip"]))
        c.update(state="eating", eat_ticks_left=self._ticks(self.t["eat_s"]), tip=tip, mood=m["mood"],
                 quality=self.hand.get("quality"), rep_delta=m["rep"])
        self.hand = None
        events.append(("served", {"customer_id": c["id"], "table_id": table["id"], "dish_id": dish,
                                  "price": c["price"], "tip": tip, "mood": m["mood"], "quality": c["quality"]}))

    def _pay(self, c, events):
        amount = c["price"] + c["tip"]
        self.money += amount
        self.earned += amount
        self.shift_earned += amount
        self.reputation = self._clamp_reputation(self.reputation + c.get("rep_delta", 0))
        events.append(("paid", {"customer_id": c["id"], "table_id": c["table_id"], "dish_id": c["dish_id"],
                                "price": c["price"], "tip": c["tip"], "amount": amount, "mood": c.get("mood"),
                                "money": self.money, "reputation": self.reputation}))

    def _can_sell(self):
        return bool(makeable(self.menu, self.stock) or self.hand is not None
                    or any(s["state"] in ("cooking", "ready") for s in self.stoves)
                    or any(c["state"] in ("eating", "leaving") for c in self.customers))  # chờ khách ăn xong / bước ra

    def snapshot(self) -> dict:
        s = super().snapshot()
        s["stoves"] = [{k: st.get(k) for k in ("id", "pos", "state", "dish", "cook_ticks_left", "ready_ticks",
                                               "quality", "cook_ticks_total", "auto")} for st in self.stoves]
        s["ui"] = dict(self.ui) if self.ui else None
        s["orders"] = [{"customer_id": c["id"], "table_id": c["table_id"], "dish_id": c["dish_id"],
                        "patience_ticks_left": c["patience_ticks_left"], "patience_ticks_max": c["patience_ticks_max"],
                        "status": status} for c, status in self._order_plan()]
        s["can_make"] = {d: min(self.stock.get(k, 0) // n for k, n in self.menu[d]["recipe"].items())
                         for d in sorted(self.menu)}
        return s
