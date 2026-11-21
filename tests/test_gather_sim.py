import unittest

from chonoi.contract import load_contract
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.gather import GatherSim


def state(move=(0.0, 0.0), *edges):
    return InputState(move, {"interact": False, "catch": False}, set(edges))


def make_sim(**scenario):
    tuning = load_contract()["tuning"]
    return GatherSim(tuning, scenario, Streams(1), IdAllocator())


class GatherOxygenTests(unittest.TestCase):
    def test_oxygen_decreases_underwater_and_recovers_at_surface(self):
        sim = make_sim(player={"pos": [20, 10], "oxygen_ticks": 10})
        sim.step(state())
        self.assertEqual(sim.oxygen_ticks, 9)

        sim.pos[1] = 0
        sim.step(state())
        self.assertEqual(sim.oxygen_ticks, 15)

    def test_faint_clears_hold_and_finishes(self):
        sim = make_sim(player={"pos": [20, 10], "oxygen_ticks": 0, "hp": 1,
                               "zero_oxy_ticks": 59}, hold=["ca_loc"])
        events = sim.step(state())
        names = [name for name, _ in events]
        self.assertEqual(names, ["choke", "faint", "gather_end"])
        self.assertTrue(sim.done)
        self.assertEqual(sim.reason, "fainted")
        self.assertEqual(sim.hold, [])
        self.assertEqual(events[-1][1]["inventory"], {"items": {}})


class GatherInteractionTests(unittest.TestCase):
    def test_nearest_node_is_gathered_and_regrows(self):
        sim = make_sim(player={"pos": [12, 0]}, nodes=[
            {"id": "N2", "kind": "bong_sung", "pos": [13, 0]},
            {"id": "N1", "kind": "bong_dien_dien", "pos": [11, 0]},
        ])
        events = sim.step(state((0, 0), "interact"))
        self.assertEqual(sim.hold, ["bong_dien_dien"])
        self.assertEqual(events[-1][0], "gather")
        node = next(n for n in sim.nodes if n["id"] == "N1")
        self.assertEqual(node["regrow_ticks"], int(load_contract()["tuning"]["gather"]["regrow_s"] * 60))

    def test_catch_requires_underwater_and_adds_yield(self):
        sim = make_sim(player={"pos": [15, 5]}, fish=[
            {"id": "F1", "kind": "ca_linh", "pos": [15, 5]}
        ])
        events = sim.step(state((0, 0), "catch"))
        self.assertEqual(events[-1][0], "fish_caught")
        self.assertEqual(sim.hold, ["ca_linh"] * 3)
        self.assertEqual(sim.fish, [])

    def test_dock_interaction_precedes_gathering(self):
        sim = make_sim(player={"pos": [2, 0]}, nodes=[
            {"id": "N1", "kind": "bong_sung", "pos": [2, 0]}
        ])
        events = sim.step(state((0, 0), "interact"))
        self.assertEqual([name for name, _ in events], ["gather_end"])
        self.assertEqual(sim.hold, [])

    def test_node_cannot_be_gathered_underwater(self):
        sim = make_sim(player={"pos": [12, 5]}, nodes=[
            {"id": "N1", "kind": "bong_sung", "pos": [12, 5]}
        ])
        events = sim.step(state((0, 0), "interact"))
        self.assertEqual(sim.hold, [])
        self.assertNotIn("gather", [name for name, _ in events])

    def test_hold_full_blocks_node_and_fish(self):
        sim = make_sim(player={"pos": [12, 0]}, hold=["ca_loc"] * 12,
                       nodes=[{"id": "N1", "kind": "bong_sung", "pos": [12, 0]}])
        events = sim.step(state((0, 0), "interact"))
        self.assertEqual(sim.hold, ["ca_loc"] * 12)
        self.assertEqual(events[-1][0], "hold_full")

        sim.pos[1] = 5
        sim.fish = [{"id": "F1", "kind": "ca_loc", "pos": [12, 5]}]
        events = sim.step(state((0, 0), "catch"))
        self.assertEqual(events[-1][0], "hold_full")
        self.assertEqual(len(sim.fish), 1)

    def test_fish_must_be_in_range_and_cooldown_blocks_repeat(self):
        sim = make_sim(player={"pos": [15, 5]}, fish=[
            {"id": "F1", "kind": "ca_loc", "pos": [15, 5]},
            {"id": "F2", "kind": "ca_loc", "pos": [20, 5]},
        ])
        first = sim.step(state((0, 0), "catch"))
        self.assertEqual(first[-1][0], "fish_caught")
        self.assertGreater(sim.catch_cd_ticks, 0)
        second = sim.step(state((0, 0), "catch"))
        self.assertNotIn("fish_caught", [name for name, _ in second])
        self.assertEqual([f["id"] for f in sim.fish], ["F2"])

    def test_time_end_keeps_hold(self):
        sim = make_sim(time_left_ticks=1, hold=["ca_loc"])
        events = sim.step(state())
        self.assertEqual(events[-1][0], "gather_end")
        self.assertEqual(events[-1][1]["reason"], "time")
        self.assertEqual(events[-1][1]["inventory"], {"items": {"ca_loc": 1}})


if __name__ == "__main__":
    unittest.main()
