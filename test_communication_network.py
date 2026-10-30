import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from communication.network import CommunicationNetwork
from communication.message import Message
import config

class DummyDrone:
    def __init__(self, drone_id, position):
        self.drone_id = drone_id
        self.position = position

class TestCommunicationNetwork(unittest.TestCase):
    def setUp(self):
        self.network = CommunicationNetwork()
        self.drone1 = DummyDrone("UAV-01", [0.0, 0.0, 10.0])
        self.drone2 = DummyDrone("UAV-02", [50.0, 0.0, 10.0]) # In range (100.0)
        self.drone3 = DummyDrone("UAV-03", [200.0, 0.0, 10.0]) # Out of range
        
        self.network.register_drone(self.drone1)
        self.network.register_drone(self.drone2)
        self.network.register_drone(self.drone3)

    def test_registration(self):
        self.assertEqual(len(self.network.registered_drones), 3)
        self.network.unregister_drone("UAV-03")
        self.assertEqual(len(self.network.registered_drones), 2)

    def test_unicast_delivery_in_range(self):
        msg = Message("UAV-01", "UAV-02", "UAV_STATE", 1, {})
        success = self.network.send_message(msg)
        self.assertTrue(success)
        
        received = self.network.receive_messages("UAV-02")
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].sender_id, "UAV-01")

    def test_unicast_delivery_out_of_range(self):
        msg = Message("UAV-01", "UAV-03", "UAV_STATE", 1, {})
        success = self.network.send_message(msg)
        self.assertFalse(success)
        
        received = self.network.receive_messages("UAV-03")
        self.assertEqual(len(received), 0)

    def test_unknown_recipient(self):
        msg = Message("UAV-01", "UNKNOWN", "UAV_STATE", 1, {})
        success = self.network.send_message(msg)
        self.assertFalse(success)

    def test_broadcast_delivery(self):
        msg = Message("UAV-01", "BROADCAST", "UAV_STATE", 1, {})
        success = self.network.send_message(msg)
        self.assertTrue(success)
        
        recv1 = self.network.receive_messages("UAV-01")
        self.assertEqual(len(recv1), 0) # Should not receive own broadcast
        
        recv2 = self.network.receive_messages("UAV-02")
        self.assertEqual(len(recv2), 1) # In range
        
        recv3 = self.network.receive_messages("UAV-03")
        self.assertEqual(len(recv3), 0) # Out of range

    def test_statistics(self):
        self.network.send_message(Message("UAV-01", "UAV-02", "UAV_STATE", 1, {}))
        self.network.send_message(Message("UAV-01", "UAV-03", "UAV_STATE", 2, {})) # fails
        
        self.network.receive_messages("UAV-02")
        
        stats = self.network.get_network_statistics()
        self.assertEqual(stats["registered_drones"], 3)
        self.assertEqual(stats["messages_sent"], 2)
        self.assertEqual(stats["messages_delivered"], 1)
        self.assertEqual(stats["messages_failed"], 1)

if __name__ == '__main__':
    unittest.main()
