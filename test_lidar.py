import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sensors.lidar import SimulatedLiDAR
import config

class TestLiDAR(unittest.TestCase):
    def test_lidar_creation(self):
        lidar = SimulatedLiDAR("LIDAR-UAV-01")
        self.assertEqual(lidar.sensor_id, "LIDAR-UAV-01")

    def test_scan(self):
        lidar = SimulatedLiDAR("LIDAR-UAV-01")
        drone_pos = [10.0, 20.0, 30.0]
        data = lidar.scan(drone_pos)
        
        self.assertIsNotNone(data)
        self.assertEqual(data["sensor"], "LiDAR")
        self.assertEqual(data["sensor_id"], "LIDAR-UAV-01")
        
        # Check point count
        self.assertEqual(len(data["ranges"]), config.NUM_LIDAR_POINTS)
        self.assertEqual(len(data["azimuth"]), config.NUM_LIDAR_POINTS)
        self.assertEqual(len(data["elevation"]), config.NUM_LIDAR_POINTS)
        
        # Check XYZ shape
        self.assertEqual(np.array(data["points_xyz"]).shape, (config.NUM_LIDAR_POINTS, 3))
        
    def test_finite_values_and_positive_range(self):
        lidar = SimulatedLiDAR("LIDAR-UAV-01")
        data = lidar.scan([0.0, 0.0, 0.0])
        
        ranges = np.array(data["ranges"])
        self.assertTrue(np.all(ranges >= 0))
        self.assertTrue(np.all(np.isfinite(ranges)))
        
        xyz = np.array(data["points_xyz"])
        self.assertTrue(np.all(np.isfinite(xyz)))

    def test_get_state(self):
        lidar = SimulatedLiDAR("LIDAR-UAV-01")
        self.assertIsNone(lidar.get_state())
        lidar.scan([0.0, 0.0, 0.0])
        self.assertIsNotNone(lidar.get_state())

if __name__ == '__main__':
    unittest.main()
