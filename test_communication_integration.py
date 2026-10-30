import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.swarm import Swarm
from communication.network import CommunicationNetwork
from communication.shared_state import SharedStateStore
from communication.message import Message

class TestCommunicationIntegration(unittest.TestCase):
    def setUp(self):
        self.swarm = Swarm(number_of_drones=3)
        # Position them intentionally
        drones = self.swarm.get_all_drones()
        drones[0].position = [0.0, 0.0, 10.0]
        drones[1].position = [50.0, 0.0, 10.0] # In range of drone 0
        drones[2].position = [200.0, 0.0, 10.0] # Out of range of drone 0 and 1
        
        self.network = CommunicationNetwork()
        for drone in drones:
            self.network.register_drone(drone)
            
        self.store = SharedStateStore()

    def test_integration_flow(self):
        # 1. Publish state from UAV-01
        drones = self.swarm.get_all_drones()
        d1 = drones[0]
        
        msg = Message(
            sender_id=d1.drone_id,
            recipient_id="BROADCAST",
            message_type="UAV_STATE",
            sequence_number=1,
            payload={
                "drone_id": d1.drone_id,
                "position": d1.position,
                "battery": d1.battery
            }
        )
        
        # 2. Deliver messages
        self.network.send_message(msg)
        
        # 3. Update shared state for receiving drone 2
        d2 = drones[1]
        received = self.network.receive_messages(d2.drone_id)
        self.assertEqual(len(received), 1)
        for r in received:
            self.store.update_drone_state(r)
            
        # 4. Update shared state for receiving drone 3 (should be none because out of range)
        d3 = drones[2]
        received_d3 = self.network.receive_messages(d3.drone_id)
        self.assertEqual(len(received_d3), 0)
        
        # 5. Confirm each UAV state is correct
        state = self.store.get_drone_state(d1.drone_id)
        self.assertIsNotNone(state)
        self.assertEqual(state["battery"], d1.battery)
        
        # 6. Check out-of-range stats
        stats = self.network.get_network_statistics()
        self.assertEqual(stats["messages_failed"], 1) # Delivery to d3 failed due to range

if __name__ == '__main__':
    unittest.main()
