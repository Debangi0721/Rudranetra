import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.drone import Drone
import config

class TestDroneSensors(unittest.TestCase):
    def test_drone_has_sensors(self):
        d = Drone("UAV-01")
        
        self.assertTrue(hasattr(d, 'lidar'))
        self.assertTrue(hasattr(d, 'gps'))
        self.assertTrue(hasattr(d, 'imu'))
        
        self.assertEqual(d.lidar.sensor_id, "LIDAR-UAV-01")
        self.assertEqual(d.gps.sensor_id, "GPS-UAV-01")
        self.assertEqual(d.imu.sensor_id, "IMU-UAV-01")
        
    def test_update_sensors(self):
        d = Drone("UAV-01")
        d.update_sensors()
        
        # Verify sensor states are populated
        self.assertIsNotNone(d.lidar.get_state())
        self.assertIsNotNone(d.gps.get_state())
        self.assertIsNotNone(d.imu.get_state())
        
    def test_get_sensor_data(self):
        d = Drone("UAV-01")
        d.update_sensors()
        data = d.get_sensor_data()
        
        self.assertIn("drone_id", data)
        self.assertEqual(data["drone_id"], "UAV-01")
        self.assertIn("lidar", data)
        self.assertIn("gps", data)
        self.assertIn("imu", data)
        
        self.assertEqual(data["lidar"]["sensor"], "LiDAR")
        self.assertEqual(data["gps"]["sensor"], "GPS")
        self.assertEqual(data["imu"]["sensor"], "IMU")

if __name__ == '__main__':
    unittest.main()
