import copy
import unittest

from chonoi.contract import load_contract
from chonoi.errors import BadInput
from chonoi.ids import IdAllocator
from chonoi.inputs import InputState
from chonoi.rng import Streams
from chonoi.sim.quan import QuanSim


class QuanSimTest(unittest.TestCase):
    def make_sim(self, scenario=None, configure=None):
        tuning = copy.deepcopy(load_contract()["tuning"])
        tuning["quan"]["first_customer_tick"] = 1000
        if configure is not None:
            configure(tuning)
        return QuanSim(tuning, scenario or {}, Streams(7), IdAllocator())

    @staticmethod
    def step(sim, *pressed):
        return sim.step(InputState((0.0, 0.0), {}, set(pressed)))

    def test_arrival_assigns_feasible_dish_and_reserves_stock(self):
        def configure(tuning):
            tuning["quan"]["first_customer_tick"] = 1

        sim = self.make_sim({"stock": {"ca_loc": 1}}, configure)
        events = self.step(sim)

        self.assertEqual([event[0] for event in events], ["customer_arrived"])
        customer = sim.customers[0]
        self.assertEqual(customer["dish_id"], "ca_loc_nuong_trui")
        self.assertEqual(customer["reserved"], {"ca_loc": 1})
        self.assertEqual(sim.snapshot()["stock"], {})

    def test_arrival_without_cookable_dish_emits_no_dish(self):
        def configure(tuning):
            tuning["quan"]["first_customer_tick"] = 1

        sim = self.make_sim({}, configure)

        events = self.step(sim)

        self.assertEqual([event[0] for event in events], ["no_dish"])
        self.assertEqual(sim.customers, [])

    def test_customer_leaving_releases_reserved_stock_and_lowers_reputation(self):
        scenario = {
            "stock": {"ca_loc": 1},
            "random_customers": False,
            "customers": [{
                "id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
                "patience_ticks_left": 1,
            }],
        }
        sim = self.make_sim(scenario)

        events = self.step(sim)

        self.assertEqual([event[0] for event in events], ["customer_left"])
        self.assertEqual(sim.stock["ca_loc"], 1)
        self.assertEqual(sim.reputation, 2.5)
        self.assertEqual(sim.customers, [])

    def test_cook_serve_eat_and_pay(self):
        def configure(tuning):
            tuning["quan"]["eat_s"] = 1 / 60
            tuning["menu"]["ca_loc_nuong_trui"]["cook_s"] = 1 / 60

        scenario = {
            "stock": {"ca_loc": 1},
            "random_customers": False,
            "player": {"pos": [2, 8]},
            "customers": [{
                "id": "C1", "table_id": "T1", "dish_id": "ca_loc_nuong_trui",
            }],
        }
        sim = self.make_sim(scenario, configure)

        self.assertEqual([event[0] for event in self.step(sim, "interact")], ["cook_started"])
        self.assertEqual([event[0] for event in self.step(sim)], ["dish_ready"])
        self.assertEqual([event[0] for event in self.step(sim, "interact")], ["dish_picked"])
        sim.pos = list(next(table["pos"] for table in sim.tables if table["id"] == "T1"))
        self.assertEqual([event[0] for event in self.step(sim, "interact")], ["served"])
        self.assertEqual([event[0] for event in self.step(sim)], ["paid"])
        self.assertEqual(sim.money, 72)
        self.assertEqual(sim.earned, 72)
        self.assertEqual(sim.reputation, 3.2)
        self.assertEqual(sim.customers, [])

    def test_eating_scenario_requires_price_and_tip(self):
        scenario = {
            "random_customers": False,
            "customers": [{
                "id": "C1", "table_id": "T1", "state": "eating",
                "dish_id": "ca_loc_nuong_trui",
            }],
        }

        with self.assertRaises(BadInput):
            self.make_sim(scenario)

    def test_assigned_customer_requires_a_dish(self):
        scenario = {
            "stock": {"ca_loc": 1},
            "random_customers": False,
            "customers": [{"id": "C1", "table_id": "T1", "state": "assigned"}],
        }

        with self.assertRaises(BadInput):
            self.make_sim(scenario)

    def test_shift_ends_once(self):
        sim = self.make_sim({"random_customers": False, "time_left_ticks": 1})

        events = self.step(sim)

        self.assertEqual([event[0] for event in events], ["quan_end"])
        self.assertEqual(events[0][1]["reason"], "time")
        self.assertEqual(self.step(sim), [])


if __name__ == "__main__":
    unittest.main()
