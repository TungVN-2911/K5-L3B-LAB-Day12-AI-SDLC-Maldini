"""Test phần SÁNG TẠO (chỉ chạy ở `chonoi.live --mode day`): buff dưới nước, ghe tạp hóa + đồ nghề, cá lớn có Máu,
quán nhiều khách + nấu theo nguyên liệu + cảm xúc khách, và vòng lặp sáng -> tối -> sáng."""

import copy
import json
import unittest

from chonoi.contract import load_contract
from chonoi.day import DaySession
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.live import LiveGame, LiveServer
from chonoi.rng import Streams
from chonoi.sim.extras import GatherPlus, QuanPlus, load_extras


def inp(move=(0.0, 0.0), *pressed):
    return InputState(move, {}, set(pressed))


def names(events):
    return [e[0] for e in events]


class GatherPlusTest(unittest.TestCase):
    def make(self, money=1000, slots=(), configure=None):
        tuning = load_contract()["tuning"]
        extras = load_extras()
        extras["gather"]["pickup_first_s"] = 9999  # không sinh buff ngẫu nhiên trong test
        extras["gather"]["fish_respawn_s"] = 9999
        if configure:
            configure(extras)
        profile = {"money": money, "slots": list(slots), "armor_hp": 3 if "armor" in slots else 0, "basket_level": 0}
        return GatherPlus(tuning, {"random_fish": False}, Streams(3), IdAllocator(), extras, profile)

    def open_shop(self, g):
        g.pos = list(map(float, g.shop["pos"]))
        ev = g.step(inp((0.0, 0.0), "interact"))
        self.assertIn("shop_open", names(ev))
        self.assertFalse(g.done, "E ở ghe tạp hóa không được cập bến")

    def buy(self, g, item):
        g.queue_action({"type": "buy", "item": item})
        return dict(g.step(inp()))

    # --- buff dưới nước -------------------------------------------------------
    def test_speed_pickup_boosts_swim_speed(self):
        g = self.make()
        base = g.t["swim_speed"]
        g.pos = [20.0, 10.0]
        g.pickups = [{"id": "P1", "kind": "speed", "pos": [20.0, 10.0]}]
        self.assertIn("pickup", names(g.step(inp())))
        self.assertGreater(g.t["swim_speed"], base)
        for _ in range(60 * 9):
            g.step(inp())
        self.assertAlmostEqual(g.t["swim_speed"], base)

    def test_heal_pickup_adds_hp_only_when_hurt(self):
        g = self.make()
        g.pos = [20.0, 10.0]
        g.pickups = [{"id": "P1", "kind": "heal", "pos": [20.0, 10.0]}]
        g.step(inp())
        self.assertEqual(len(g.pickups), 1, "đủ máu thì không nhặt")
        g.hp = 1
        g.step(inp())
        self.assertEqual((g.hp, g.pickups), (2, []))

    # --- ghe tạp hóa ----------------------------------------------------------
    def test_shop_buy_slots_unique_and_limited(self):
        g = self.make(money=2000)
        self.open_shop(g)
        ev = self.buy(g, "gun")
        self.assertIn("shop_buy", ev)
        self.assertEqual(g.profile["money"], 2000 - g.shop["items"]["gun"]["price"])
        self.assertEqual(self.buy(g, "gun")["shop_fail"]["reason"], "owned")
        for item in ("net", "armor", "tank", "fins"):
            self.assertIn("shop_buy", self.buy(g, item))
        self.assertEqual(len(g.profile["slots"]), 5)
        self.assertEqual(self.buy(g, "knife")["shop_fail"]["reason"], "slots")
        money = g.profile["money"]
        g.queue_action({"type": "sell", "item": "fins"})
        ev = dict(g.step(inp()))
        self.assertEqual(g.profile["money"], money + ev["shop_sell"]["money_got"])
        self.assertIn("shop_buy", self.buy(g, "knife"))

    def test_shop_needs_money_and_being_near(self):
        g = self.make(money=10)
        self.open_shop(g)
        self.assertEqual(self.buy(g, "net")["shop_fail"]["reason"], "money")
        g = self.make(money=1000)
        g.queue_action({"type": "buy", "item": "net"})  # chưa mở tiệm
        g.step(inp())
        self.assertEqual(g.profile["slots"], [])

    def test_tank_and_basket_upgrade(self):
        g = self.make()
        oxy, cap = g.oxygen_max, g.t["hold_capacity"]
        self.open_shop(g)
        self.buy(g, "tank")
        self.assertEqual(g.oxygen_max, oxy + g.shop["items"]["tank"]["oxygen_bonus_s"] * 60)
        self.buy(g, "basket")
        self.assertEqual(g.t["hold_capacity"], cap + g.shop["basket"]["step"])
        self.assertNotIn("basket", g.profile["slots"], "nâng cấp giỏ không chiếm ô đồ")

    def test_armor_absorbs_bites_then_breaks_and_can_be_rebought(self):
        g = self.make(slots=("armor",))
        bf = g.big_fish[0]
        for i in range(3):
            g.invuln_ticks = 0
            g.pos = list(bf["pos"])
            ev = g.step(inp())
            self.assertIn("armor_hit", names(ev))
        self.assertIn("armor_broken", names(ev))
        self.assertEqual(g.hp, g.t["hp_max"], "giáp đỡ hết, không mất Máu")
        self.assertNotIn("armor", g.profile["slots"])
        self.open_shop(g)
        self.assertIn("shop_buy", self.buy(g, "armor"))

    # --- đồ nghề dưới nước ----------------------------------------------------
    def test_net_catches_every_fish_in_wider_radius(self):
        g = self.make(slots=("net",))
        g.pos = [20.0, 10.0]
        g.fish = [{"id": "F1", "kind": "ca_loc", "pos": [22.5, 10.0], "heading_deg": 0},
                  {"id": "F2", "kind": "ca_he_vang", "pos": [17.5, 10.0], "heading_deg": 0}]
        ev = g.step(inp((0.0, 0.0), "catch"))
        self.assertEqual(names(ev).count("fish_caught"), 2)
        self.assertEqual(sorted(g.hold), ["ca_he_vang", "ca_loc"])

    def test_harpoon_damages_and_defeats_big_fish(self):
        g = self.make(slots=("gun",))
        self.assertEqual(g.gun_ammo, g.shop["items"]["gun"]["ammo_per_dive"])
        bf = g.big_fish[0]
        defeated = False
        for i in range(400):
            g.pos = [bf["pos"][0] - 4.0, bf["pos"][1]]  # đứng yên ngắm
            g.heading = 0.0
            g.invuln_ticks = 999
            ev = g.step(inp((0.0, 0.0), "catch") if i % 25 == 0 else inp())
            if "big_fish_defeated" in names(ev):
                defeated = True
                break
        self.assertTrue(defeated)
        self.assertIn(bf["kind"], g.hold, "hạ cá lớn rơi nguyên liệu vào giỏ")

    def test_knife_doubles_melee_damage(self):
        g = self.make(slots=("knife",))
        bf = g.big_fish[0]
        g.pos = [bf["pos"][0] - 2.0, bf["pos"][1]]
        g.invuln_ticks = 999
        ev = dict(g.step(inp((0.0, 0.0), "catch")))
        self.assertEqual(ev["big_fish_hit"]["damage"], 2)

    def test_boss_catfish_bites_two_hp_and_can_faint(self):
        g = self.make()
        boss = next(f for f in g.big_fish if f["kind"] == "ca_tra_dau")
        self.assertEqual(g.x["big_kinds"]["ca_tra_dau"]["damage"], 2)
        g.hp = 2
        g.hold = ["ca_loc"]
        g.pos = list(boss["pos"])
        ev = g.step(inp())
        self.assertIn("player_hurt", names(ev))
        self.assertTrue(g.done)
        self.assertEqual((g.reason, g.hold), ("fainted", []))


class QuanPlusTest(unittest.TestCase):
    def make(self, stock):
        tuning = copy.deepcopy(load_contract()["tuning"])
        extras = load_extras()
        return QuanPlus(tuning, {}, Streams(5), IdAllocator(), stock, extras)

    def run_until(self, q, name, limit=2000):
        for _ in range(limit):
            ev = q.step(inp())
            if name in names(ev):
                return ev
        self.fail(f"không thấy sự kiện {name}")

    def test_many_customers_and_manual_recipe_gives_great_dish(self):
        q = self.make({"ca_loc": 3, "bong_sung": 3})
        self.run_until(q, "customer_arrived")
        c = q.customers[0]
        stove = q.stoves[0]
        q.pos = [stove["pos"][0], 1.0]
        self.assertIn("cook_menu", names(q.step(inp((0.0, 0.0), "interact"))))
        q.queue_action({"type": "cook", "stove_id": stove["id"], "ingredients": dict(q.menu[c["dish_id"]]["recipe"])})
        ev = q.step(inp())
        self.assertIn("cook_started", names(ev))
        self.assertEqual(stove["quality"], "great")
        self.run_until(q, "dish_ready")
        q.step(inp((0.0, 0.0), "interact"))
        self.assertEqual(q.hand["quality"], "great")
        seat = next(t for t in q.tables if t["id"] == c["table_id"])
        q.pos = [seat["pos"][0], 1.0]
        ev = dict(q.step(inp((0.0, 0.0), "interact")))
        self.assertIn("served", ev)
        self.assertEqual(ev["served"]["mood"], "rat_hai_long")
        self.assertGreater(ev["served"]["tip"], 0)

    def test_wrong_recipe_wastes_ingredients(self):
        q = self.make({"ca_loc": 2, "bong_sung": 3})
        stove = q.stoves[0]
        q.pos = [stove["pos"][0], 1.0]
        q.queue_action({"type": "cook", "stove_id": stove["id"], "ingredients": {"ca_loc": 2}})
        ev = dict(q.step(inp()))
        self.assertEqual(ev["cook_failed"]["reason"], "wrong_recipe")
        self.assertNotIn("ca_loc", q.stock)
        self.assertEqual(stove["state"], "idle")

    def test_auto_cook_is_slower_and_good_quality(self):
        q = self.make({"ca_loc": 1})
        stove = q.stoves[0]
        q.pos = [stove["pos"][0], 1.0]
        q.queue_action({"type": "cook", "stove_id": stove["id"], "dish_id": "ca_loc_nuong_trui"})
        q.step(inp())
        self.assertEqual(stove["quality"], "good")
        self.assertGreater(stove["cook_ticks_total"], q.menu["ca_loc_nuong_trui"]["cook_s"] * 60)

    def test_quick_cook_uses_first_idle_stove_without_walking(self):
        q = self.make({"ca_loc": 1, "bong_sung": 2})
        q.pos = [2.0, 1.0]  # đứng xa bếp
        q.queue_action({"type": "quick_cook", "dish_id": "ca_loc_nuong_trui"})
        ev = dict(q.step(inp()))
        self.assertTrue(ev["cook_started"]["quick"])
        self.assertEqual(q.stoves[0]["state"], "cooking")
        self.assertEqual(q.stoves[0]["quality"], "good")
        for st in q.stoves:
            st["state"] = "cooking"
        q.queue_action({"type": "quick_cook", "dish_id": "goi_bong_sung"})
        ev = dict(q.step(inp()))
        self.assertEqual(ev["cook_failed"]["reason"], "no_stove")

    def test_order_without_ingredients_customer_leaves_disappointed(self):
        q = self.make({"ca_loc": 1, "bong_sung": 2})
        self.run_until(q, "customer_arrived")
        c = q.customers[0]
        q.stock = {}  # nguyên liệu bị dùng / làm hỏng hết
        ev = dict(q.step(inp()))
        self.assertEqual(ev["out_of_stock"]["customer_id"], c["id"])
        self.assertEqual(c["state"], "leaving")
        self.assertEqual(c["mood"], "that_vong")
        self.assertEqual(q.snapshot()["orders"], [])
        rep0 = q.reputation
        left = self.run_until(q, "customer_left", limit=400)
        data = dict(left)["customer_left"]
        self.assertEqual((data["reason"], data["mood"]), ("out_of_stock", "that_vong"))
        self.assertLess(q.reputation, rep0)

    def test_orders_snapshot_tracks_cooking_status(self):
        q = self.make({"ca_loc": 2})
        self.run_until(q, "customer_arrived")
        self.assertEqual(q.snapshot()["orders"][0]["status"], "waiting")
        q.queue_action({"type": "quick_cook", "dish_id": q.customers[0]["dish_id"]})
        q.step(inp())
        self.assertEqual(q.snapshot()["orders"][0]["status"], "cooking")

    def test_sold_out_ends_shift(self):
        q = self.make({"ca_linh": 1})  # không đủ cho món nào
        ev = q.step(inp())
        self.assertTrue(q.done)
        self.assertEqual(q.reason, "sold_out")
        self.assertIn("quan_end", names(ev))


class DaySessionTest(unittest.TestCase):
    def test_gather_to_quan_to_gather(self):
        d = DaySession(load_contract()["tuning"], 1)
        d.sim.hold = ["ca_loc"]
        d.sim.pos = [2.0, 0.0]
        rows = d.step(inp((0.0, 0.0), "interact"))
        self.assertIn("phase_end", [r["name"] for r in rows])
        self.assertEqual(d.transition["to"], "quan")
        while d.transition:
            d.step(inp())
        self.assertEqual(d.sim.mode, "quan")
        self.assertEqual(d.sim.stock, {"ca_loc": 1})
        snap = d.snapshot()
        json.dumps(snap)
        self.assertEqual(snap["mode"], "quan")
        # bán hết: bỏ kho để ca tối kết thúc vì hết hàng
        d.sim.stock = {}
        d.step(inp())
        self.assertEqual(d.transition["reason"], "sold_out")
        while d.transition:
            d.step(inp())
        self.assertEqual(d.sim.mode, "gather")
        self.assertEqual(d.day, 2)

    def test_money_and_gear_carry_over_to_next_day(self):
        d = DaySession(load_contract()["tuning"], 1)
        self.assertEqual(d.snapshot()["money"], d.x["day"]["start_money"])
        d.sim.pos = list(map(float, d.sim.shop["pos"]))
        d.step(inp((0.0, 0.0), "interact"))
        d.queue_action({"type": "buy", "item": "armor"})
        d.step(inp())
        self.assertEqual(d.profile["slots"], ["armor"])
        d.sim.pos = [2.0, 0.0]
        d.step(inp((0.0, 0.0), "interact"))  # cập bến, giỏ trống -> sang sáng hôm sau
        while d.transition:
            d.step(inp())
        self.assertEqual(d.day, 2)
        self.assertEqual(d.sim.profile["slots"], ["armor"])
        self.assertEqual(d.snapshot()["gear"]["armor_hp"], 3)

    def test_no_cookable_haul_skips_evening(self):
        d = DaySession(load_contract()["tuning"], 1)
        d.sim.pos = [2.0, 0.0]
        d.step(inp((0.0, 0.0), "interact"))
        self.assertEqual(d.transition["to"], "gather")
        while d.transition:
            d.step(inp())
        self.assertEqual(d.day, 2)


class LiveDayActionTest(unittest.TestCase):
    def test_action_endpoint_validation(self):
        import urllib.error
        import urllib.request

        def post(url, obj):
            req = urllib.request.Request(url, data=json.dumps(obj).encode(), method="POST",
                                         headers={"Content-Type": "application/json"})
            try:
                with urllib.request.urlopen(req, timeout=5) as r:
                    return r.status
            except urllib.error.HTTPError as e:
                e.close()
                return e.code

        server = LiveServer(LiveGame("day", load_contract()["tuning"], {}, 1), port=0)
        server.start()
        try:
            base = f"http://127.0.0.1:{server.port}"
            with urllib.request.urlopen(base + "/state", timeout=5) as r:
                st = json.loads(r.read())
            self.assertEqual(st["mode"], "gather")
            self.assertTrue(st["meta"]["day_mode"])
            self.assertEqual(post(base + "/action", {"type": "close"}), 200)
            self.assertEqual(post(base + "/action", {"type": "cook", "stove_id": "B1"}), 400)
            self.assertEqual(post(base + "/action", {"type": "hack"}), 400)
        finally:
            server.stop()

    def test_action_rejected_outside_day_mode(self):
        game = LiveGame("gather", load_contract()["tuning"], {}, 1)
        with self.assertRaises(ValueError):
            game.action({"type": "close"})


if __name__ == "__main__":
    unittest.main()
