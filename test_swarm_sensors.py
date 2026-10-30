import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.swarm import Swarm
import config

class TestSwarmSensors(unittest.TestCase):
    def test_swarm_sensors_initialization(self):
        s = Swarm(number_of_drones=5)
        s.update_all_sensors()
        
        drones = s.get_all_drones()
        for drone in drones:
            self.assertTrue(hasattr(drone, 'lidar'))
            self.assertTrue(hasattr(drone, 'gps'))
            self.assertTrue(hasattr(drone, 'imu'))
            
    def test_sensor_independence(self):
        s = Swarm(number_of_drones=5)
        s.update_all_sensors()
        
        d1 = s.get_drone("UAV-01")
        d2 = s.get_drone("UAV-02")
        
        # Verify independence of instances
        self.assertIsNot(d1.lidar, d2.lidar)
        self.assertIsNot(d1.gps, d2.gps)
        self.assertIsNot(d1.imu, d2.imu)
        
        # Move d1 and update
        original_d2_gps = d2.gps.get_state()["x"]
        d1.position += np.array([100.0, 100.0, 100.0])
        s.update_all_sensors()
        
        # Ensure d1's sensor updated while d2 remains independent
        self.assertNotEqual(d1.gps.get_state()["x"], d2.gps.get_state()["x"])
        
        # GPS has noise, so it won't be exactly equal, but the change should be small
        d2_diff = abs(d2.gps.get_state()["x"] - original_d2_gps)
        self.assertLess(d2_diff, 5.0) # Only noise changed
        
        # d1 moved by 100, so its reading should be far from d2
        self.assertGreater(abs(d1.gps.get_state()["x"] - d2.gps.get_state()["x"]), 80.0)

    def test_unique_sensor_ids(self):
        s = Swarm(number_of_drones=5)
        drones = s.get_all_drones()
        
        lidar_ids = [d.lidar.sensor_id for d in drones]
        gps_ids = [d.gps.sensor_id for d in drones]
        imu_ids = [d.imu.sensor_id for d in drones]
        
        self.assertEqual(len(lidar_ids), len(set(lidar_ids)))
        self.assertEqual(len(gps_ids), len(set(gps_ids)))
        self.assertEqual(len(imu_ids), len(set(imu_ids)))
        
    def test_get_all_sensor_data(self):
        s = Swarm(number_of_drones=5)
        s.update_all_sensors()
        
        data = s.get_all_sensor_data()
        self.assertEqual(len(data), 5)
        self.assertIn("UAV-01", data)
        self.assertIn("lidar", data["UAV-01"])

if __name__ == '__main__':
    unittest.main()
