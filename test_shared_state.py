import unittest
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from communication.shared_state import SharedStateStore
from communication.message import Message
import config

class TestSharedState(unittest.TestCase):
    def setUp(self):
        self.store = SharedStateStore()

    def test_uav_state_updates(self):
        msg1 = Message("UAV-01", "BROADCAST", "UAV_STATE", 1, {"drone_id": "UAV-01", "battery": 90.0})
        self.store.update_drone_state(msg1)
        
        state = self.store.get_drone_state("UAV-01")
        self.assertIsNotNone(state)
        self.assertEqual(state["battery"], 90.0)

    def test_old_sequence_rejection(self):
        msg1 = Message("UAV-01", "BROADCAST", "UAV_STATE", 5, {"drone_id": "UAV-01", "battery": 80.0})
        self.store.update_drone_state(msg1)
        
        # Old sequence
        msg2 = Message("UAV-01", "BROADCAST", "UAV_STATE", 2, {"drone_id": "UAV-01", "battery": 90.0})
        self.store.update_drone_state(msg2)
        
        state = self.store.get_drone_state("UAV-01")
        self.assertEqual(state["battery"], 80.0) # Should not have updated

    def test_heartbeat_updates(self):
        t = time.time()
        msg = Message("UAV-01", "BROADCAST", "HEARTBEAT", 1, {"drone_id": "UAV-01", "simulation_timestamp": t})
        self.store.record_heartbeat(msg)
        
        self.assertEqual(self.store.get_last_seen("UAV-01"), t)

    def test_stale_uav_detection(self):
        t = time.time()
        msg = Message("UAV-01", "BROADCAST", "HEARTBEAT", 1, {"drone_id": "UAV-01", "simulation_timestamp": t - 5.0})
        self.store.record_heartbeat(msg)
        
        status = self.store.get_drone_status("UAV-01", t)
        self.assertEqual(status, "STALE")
        
        status_unknown = self.store.get_drone_status("UAV-99", t)
        self.assertEqual(status_unknown, "UNKNOWN")

    def test_detection_deduplication(self):
        msg1 = Message("UAV-01", "BROADCAST", "SENSOR_DETECTION", 1, {"detection_id": "DET-01", "type": "building"})
        self.store.add_detection(msg1)
        self.assertEqual(len(self.store.get_detections()), 1)
        
        # Exact same message id
        self.store.add_detection(msg1)
        self.assertEqual(len(self.store.get_detections()), 1)
        
        # New message, same detection ID
        msg2 = Message("UAV-02", "BROADCAST", "SENSOR_DETECTION", 2, {"detection_id": "DET-01", "type": "building_updated"})
        self.store.add_detection(msg2)
        
        dets = self.store.get_detections()
        self.assertEqual(len(dets), 1)
        self.assertEqual(dets[0]["type"], "building_updated")

if __name__ == '__main__':
    unittest.main()
