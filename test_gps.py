import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sensors.gps import SimulatedGPS
import config

class TestGPS(unittest.TestCase):
    def test_gps_creation(self):
        gps = SimulatedGPS("GPS-UAV-01")
        self.assertEqual(gps.sensor_id, "GPS-UAV-01")

    def test_read(self):
        gps = SimulatedGPS("GPS-UAV-01")
        drone_pos = [10.0, 20.0, 30.0]
        data = gps.read(drone_pos)
        
        self.assertIsNotNone(data)
        self.assertEqual(data["sensor"], "GPS")
        self.assertEqual(data["sensor_id"], "GPS-UAV-01")
        self.assertIn("latitude", data)
        self.assertIn("longitude", data)
        self.assertIn("altitude", data)
        
    def test_noise(self):
        # Even with 0 position, noise should make it not exactly reference lat/lon
        gps = SimulatedGPS("GPS-UAV-01")
        drone_pos = [0.0, 0.0, 0.0]
        
        # Taking multiple readings to ensure noise makes them differ
        data1 = gps.read(drone_pos)
        data2 = gps.read(drone_pos)
        
        self.assertNotEqual(data1["x"], data2["x"])
        self.assertNotEqual(data1["latitude"], data2["latitude"])

    def test_get_state(self):
        gps = SimulatedGPS("GPS-UAV-01")
        self.assertIsNone(gps.get_state())
        gps.read([0.0, 0.0, 0.0])
        self.assertIsNotNone(gps.get_state())

if __name__ == '__main__':
    unittest.main()
