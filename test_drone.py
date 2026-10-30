import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.drone import Drone
import config

class TestDrone(unittest.TestCase):
    def test_drone_creation(self):
        d = Drone("UAV-01")
        self.assertEqual(d.drone_id, "UAV-01")

    def test_position(self):
        d = Drone("UAV-01", position=[1.0, 2.0, 3.0])
        np.testing.assert_array_equal(d.position, [1.0, 2.0, 3.0])

    def test_velocity(self):
        d = Drone("UAV-01", velocity=[0.1, 0.2, 0.0])
        np.testing.assert_array_equal(d.velocity, [0.1, 0.2, 0.0])

    def test_battery(self):
        d = Drone("UAV-01")
        self.assertEqual(d.battery, 100.0)

    def test_role(self):
        d = Drone("UAV-01")
        self.assertEqual(d.role, "UNASSIGNED")

    def test_state(self):
        d = Drone("UAV-01")
        state = d.get_state()
        self.assertEqual(state["status"], "READY")
        self.assertEqual(state["mission_state"], "IDLE")

    def test_position_update(self):
        d = Drone("UAV-01", position=[0.0, 0.0, 0.0], velocity=[1.0, 0.0, 0.0])
        d.update_position(0.1)
        np.testing.assert_array_almost_equal(d.position, [0.1, 0.0, 0.0])

    def test_battery_consumption(self):
        d = Drone("UAV-01", battery=100.0)
        d.consume_battery(5.0)
        self.assertEqual(d.battery, 95.0)

if __name__ == '__main__':
    unittest.main()
