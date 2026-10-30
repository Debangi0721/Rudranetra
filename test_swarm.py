import unittest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.swarm import Swarm
import config

class TestSwarm(unittest.TestCase):
    def test_swarm_creation(self):
        s = Swarm(number_of_drones=5)
        self.assertIsNotNone(s)

    def test_correct_number_of_uavs(self):
        s = Swarm(number_of_drones=5)
        self.assertEqual(len(s.get_all_drones()), 5)

    def test_unique_ids(self):
        s = Swarm(number_of_drones=5)
        ids = [d.drone_id for d in s.get_all_drones()]
        self.assertEqual(len(ids), len(set(ids)))

    def test_initial_positions(self):
        s = Swarm(number_of_drones=5)
        d1 = s.get_drone("UAV-01")
        d2 = s.get_drone("UAV-02")
        d3 = s.get_drone("UAV-03")
        d4 = s.get_drone("UAV-04")
        d5 = s.get_drone("UAV-05")

        np.testing.assert_array_equal(d1.position, [0.0, 0.0, 10.0])
        np.testing.assert_array_equal(d2.position, [10.0, 0.0, 10.0])
        np.testing.assert_array_equal(d3.position, [20.0, 0.0, 10.0])
        np.testing.assert_array_equal(d4.position, [0.0, 10.0, 10.0])
        np.testing.assert_array_equal(d5.position, [10.0, 10.0, 10.0])

    def test_getting_individual_uav(self):
        s = Swarm(number_of_drones=5)
        d = s.get_drone("UAV-01")
        self.assertEqual(d.drone_id, "UAV-01")

    def test_getting_all_uavs(self):
        s = Swarm(number_of_drones=5)
        drones = s.get_all_drones()
        self.assertEqual(len(drones), 5)

    def test_swarm_state(self):
        s = Swarm(number_of_drones=2)
        state = s.get_swarm_state()
        self.assertIn("UAV-01", state)
        self.assertIn("UAV-02", state)
        np.testing.assert_array_equal(state["UAV-01"]["position"], [0.0, 0.0, 10.0])

    def test_updating_all_uavs(self):
        s = Swarm(number_of_drones=2)
        d1 = s.get_drone("UAV-01")
        d1.velocity = np.array([1.0, 0.0, 0.0])
        s.update_all(0.1)
        np.testing.assert_array_almost_equal(d1.position, [0.1, 0.0, 10.0])

if __name__ == '__main__':
    unittest.main()
