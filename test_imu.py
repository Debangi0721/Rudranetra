import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sensors.imu import SimulatedIMU
import config

class TestIMU(unittest.TestCase):
    def test_imu_creation(self):
        imu = SimulatedIMU("IMU-UAV-01")
        self.assertEqual(imu.sensor_id, "IMU-UAV-01")

    def test_read(self):
        imu = SimulatedIMU("IMU-UAV-01")
        accel = [1.0, 0.0, 9.8]
        yaw = 1.57
        data = imu.read(accel, yaw)
        
        self.assertIsNotNone(data)
        self.assertEqual(data["sensor"], "IMU")
        self.assertEqual(data["sensor_id"], "IMU-UAV-01")
        self.assertIn("accelerometer", data)
        self.assertIn("gyroscope", data)
        self.assertIn("orientation", data)
        
        self.assertEqual(len(data["accelerometer"]), 3)
        self.assertEqual(len(data["gyroscope"]), 3)
        self.assertEqual(len(data["orientation"]), 3)

    def test_noise(self):
        imu = SimulatedIMU("IMU-UAV-01")
        accel = [0.0, 0.0, 0.0]
        yaw = 0.0
        
        data1 = imu.read(accel, yaw)
        data2 = imu.read(accel, yaw)
        
        self.assertNotEqual(data1["accelerometer"][0], data2["accelerometer"][0])
        self.assertNotEqual(data1["orientation"][2], data2["orientation"][2])

    def test_get_state(self):
        imu = SimulatedIMU("IMU-UAV-01")
        self.assertIsNone(imu.get_state())
        imu.read([0.0, 0.0, 0.0], 0.0)
        self.assertIsNotNone(imu.get_state())

if __name__ == '__main__':
    unittest.main()
