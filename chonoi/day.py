"""Chế độ "một ngày" cho cửa sổ chơi (`python -m chonoi.live --mode day`) — phần SÁNG TẠO của nhóm.

Nối hai buổi thành vòng lặp liền mạch, cùng giao diện `Session` mà `chonoi.live` dùng:
    sáng: GatherPlus (lặn, bắt cá) --cập bến / hết giờ / ngất--> chuyển cảnh
    tối:  QuanPlus (bán hàng) với kho = kho dư + giỏ vừa bắt --hết giờ / hết hàng để bán--> chuyển cảnh
    -> sáng ngày hôm sau ...
Tiền và uy tín cộng dồn qua các ngày. Không có nguyên liệu nấu được món nào thì bỏ qua buổi tối.
Headless không dùng file này.
"""

import math

from .ids import IdAllocator
from .rng import Streams
from .sim.extras import GatherPlus, QuanPlus, load_extras, makeable, merged_tuning, new_profile

TICK = 60


class DaySession:
    mode = "day"

    def __init__(self, tuning, seed, extras=None):
        self.tuning = tuning
        self.x = extras if extras is not None else load_extras()
        self.menu = merged_tuning(tuning, self.x)["menu"]
        self.seed = seed
        self.tick = 0
        self.day = 1
        self.profile = new_profile(self.x)  # tiền + đồ nghề, sống qua các ngày
        self.earned = 0
        self.reputation = tuning["quan"]["reputation_initial"]
        self.stock = {k: v for k, v in self.x["day"].get("start_stock", {}).items() if v > 0}
        self.phase_no = 0
        self.transition = None
        self._start("gather")

    # --- giao diện giống runner.Session ------------------------------------------
    @property
    def done(self) -> bool:
        return self.sim.done and self.sim.reason == "error"  # chỉ dừng hẳn khi luật lỗi

    @property
    def bank(self) -> int:
        return self.profile["money"]

    def queue_action(self, action: dict):
        if not self.transition and hasattr(self.sim, "queue_action"):
            self.sim.queue_action(action)

    def step(self, inp) -> list:
        if self.transition:
            self.tick += 1
            self.transition["ticks_left"] -= 1
            if self.transition["ticks_left"] > 0:
                return []
            to = self.transition["to"]
            if to == "gather" and self.transition["from"] == "quan" or self.transition.get("next_day"):
                self.day += 1
            self.transition = None
            self._start(to)
            return [self._row("phase_start", {"mode": to, "day": self.day})]
        evs = self.sim.step(inp)
        self.tick += 1
        self.phase_tick += 1
        rows = [self._row(n, d) for n, d in evs]
        if self.sim.done and self.sim.reason != "error":
            rows += self._finish_phase()
        return rows

    def snapshot(self) -> dict:
        sim = self.sim
        quan = sim.mode == "quan"
        s = {"type": "snapshot", "tick": self.tick, "sim_tick": self.tick, "mode": sim.mode, "phase": sim.phase,
             "phase_tick": self.phase_tick, "state": "playing", "time_left_ticks": sim.time_left_ticks}
        s.update(sim.snapshot())
        rep = sim.reputation if quan and not self.transition else self.reputation
        earned = self.earned + (sim.earned if quan and not self.transition else 0)
        s["money"] = self.bank + (sim.money if quan and not self.transition else 0)
        s["earned"] = earned
        s["reputation"] = rep
        s["score"] = earned + self.tuning["score"]["reputation_multiplier"] * math.floor(rep)
        s["day"] = {"day": self.day, "bank": self.bank,
                    "stock": dict(sim.stock) if quan and not self.transition else dict(self.stock)}
        s["transition"] = dict(self.transition) if self.transition else None
        return s

    def meta(self) -> dict:
        if self.sim.mode == "gather":
            m = dict(self.tuning["gather"])
            m["extras"] = self.x["gather"]
        else:
            m = dict(self.sim.t)
            m["extras"] = {k: v for k, v in self.x["quan"].items() if k != "override"}
            m["view"] = "side"
        m["menu"] = self.menu
        m["day_mode"] = True
        return m

    def write_inventory_if_done(self, inventory_out):
        pass

    # --- nội bộ -------------------------------------------------------------------
    def _row(self, name, data):
        return {"type": "event", "tick": self.tick, "phase": self.sim.phase, "name": name, "data": data}

    def _start(self, mode):
        self.phase_no += 1
        streams, ids = Streams(self.seed * 1000 + self.phase_no), IdAllocator()
        if mode == "gather":
            self.sim = GatherPlus(self.tuning, {}, streams, ids, self.x, self.profile)
        else:
            self.sim = QuanPlus(self.tuning, {"reputation": self.reputation}, streams, ids, dict(self.stock), self.x)
        self.phase_tick = 0

    def _transition(self, frm, to, reason, **extra):
        ticks = max(1, int(round(self.x["day"]["transition_s"] * TICK)))
        self.transition = dict({"from": frm, "to": to, "reason": reason, "day": self.day,
                                "ticks_left": ticks, "ticks_total": ticks, "stock": dict(self.stock)}, **extra)
        return self._row("phase_end", {k: v for k, v in self.transition.items() if k not in ("ticks_left",)})

    def _finish_phase(self):
        sim = self.sim
        if sim.mode == "gather":
            haul = sim.inventory_items()
            for k, n in haul.items():
                self.stock[k] = self.stock.get(k, 0) + n
            if makeable(self.menu, self.stock):
                return [self._transition("gather", "quan", sim.reason, haul=haul)]
            return [self._transition("gather", "gather", sim.reason, haul=haul, next_day=True, skip="no_dish")]
        self.profile["money"] += sim.money
        self.earned += sim.earned
        self.reputation = sim.reputation
        self.stock = {k: v for k, v in sim.stock.items() if v > 0}
        return [self._transition("quan", "gather", sim.reason, money=sim.money)]
