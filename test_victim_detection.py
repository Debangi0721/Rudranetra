import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sensors.victim_detector import SimulatedVictimDetector, TargetTracker
from simulation.environment import FloodEnvironment
from decision.decision_agent import DecisionAgent
from decision.decision_result import DecisionResult, DecisionAction
from communication.shared_state import SharedStateStore
from simulation.drone import Drone

class TestVictimDetection(unittest.TestCase):
    def setUp(self):
        self.env = FloodEnvironment(seed=42)
        # Force a person near origin
        self.env.people = [{
            "id": "PERSON-TEST-01",
            "position": [10.0, 10.0, 0.0],
            "status": "STRANDED",
            "type": "person"
        }]
        
        self.detector = SimulatedVictimDetector("VD-01", detection_prob=1.0, false_positive_prob=0.0, noise_std=0.0)
        self.tracker = TargetTracker()
        
    def test_detection_range_and_noise(self):
        drone_pos = np.array([10.0, 10.0, 5.0])
        detections = self.detector.scan(drone_pos, self.env, sim_time=1.0)
        
        self.assertEqual(len(detections), 1)
        self.assertEqual(detections[0]["target_id"], "PERSON-TEST-01")
        self.assertEqual(detections[0]["urgency"], 10)
        
        # Out of range
        drone_pos = np.array([100.0, 100.0, 5.0])
        detections = self.detector.scan(drone_pos, self.env, sim_time=2.0)
        self.assertEqual(len(detections), 0)
        
    def test_target_tracking_and_assignment(self):
        drone_pos = np.array([10.0, 10.0, 5.0])
        detections = self.detector.scan(drone_pos, self.env, sim_time=1.0)
        self.tracker.process_detections(detections)
        
        unassigned = self.tracker.get_unassigned_high_priority()
        self.assertEqual(len(unassigned), 1)
        
        # Another scan, should average out (though noise is 0 here)
        detections2 = self.detector.scan(drone_pos, self.env, sim_time=2.0)
        self.tracker.process_detections(detections2)
        
        self.assertEqual(len(self.tracker.targets), 1)
        self.assertEqual(self.tracker.targets["PERSON-TEST-01"]["observations"], 2)
        
        self.tracker.assign_target("PERSON-TEST-01", "UAV-01")
        unassigned_after = self.tracker.get_unassigned_high_priority()
        self.assertEqual(len(unassigned_after), 0)
        
    def test_decision_agent_prioritization(self):
        drone = Drone("UAV-01")
        shared = SharedStateStore()
        
        # Inject target
        shared.target_tracker.targets["PERSON-TEST-01"] = {
            "id": "PERSON-TEST-01",
            "estimated_pos": [10.0, 10.0, 0.0],
            "urgency": 10,
            "last_seen": 1.0,
            "status": "UNASSIGNED"
        }
        
        agent = DecisionAgent(drone, shared)
        decision = agent.evaluate()
        
        self.assertEqual(getattr(decision, "action", ""), "RESCUE_TARGET")
        self.assertEqual(decision.target_region_id, "PERSON-TEST-01")

if __name__ == '__main__':
    unittest.main()
