import unittest
import math
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from communication.message import Message, MESSAGE_TYPES

class TestMessage(unittest.TestCase):
    def test_valid_message_creation(self):
        msg = Message("UAV-01", "UAV-02", "UAV_STATE", 1, {"battery": 90.0})
        self.assertIsNotNone(msg.message_id)
        self.assertEqual(msg.sender_id, "UAV-01")
        self.assertEqual(msg.recipient_id, "UAV-02")
        self.assertEqual(msg.message_type, "UAV_STATE")
        self.assertEqual(msg.sequence_number, 1)
        self.assertEqual(msg.payload["battery"], 90.0)
        
    def test_invalid_message_type(self):
        with self.assertRaises(ValueError):
            Message("UAV-01", "UAV-02", "INVALID_TYPE", 1, {})
            
    def test_nan_infinity_rejection(self):
        with self.assertRaises(ValueError):
            Message("UAV-01", "UAV-02", "UAV_STATE", 1, {"val": float('nan')})
            
        with self.assertRaises(ValueError):
            Message("UAV-01", "UAV-02", "UAV_STATE", 1, {"val": float('inf')})
            
    def test_payload_copying(self):
        original = {"battery": 100.0}
        msg = Message("UAV-01", "UAV-02", "UAV_STATE", 1, original)
        
        # Modify original
        original["battery"] = 0.0
        
        # Message payload should remain 100.0
        self.assertEqual(msg.payload["battery"], 100.0)
        
    def test_message_id_uniqueness(self):
        msg1 = Message("UAV-01", "UAV-02", "UAV_STATE", 1, {})
        msg2 = Message("UAV-01", "UAV-02", "UAV_STATE", 2, {})
        self.assertNotEqual(msg1.message_id, msg2.message_id)

if __name__ == '__main__':
    unittest.main()
