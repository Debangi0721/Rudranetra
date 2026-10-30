import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from decision.decision_agent import DecisionAgent
from decision.decision_result import DecisionAction
import config

class DummyDrone:
    def __init__(self, drone_id, battery=100.0, status="IDLE"):
        self.drone_id = drone_id
        self.battery = battery
        self.status = status

class DummySharedState:
    def __init__(self):
        self.detections = []
    def get_detections(self):
        return self.detections

class DummyAssignmentManager:
    def __init__(self):
        self.assignments = {}
    def get_drone_assignments(self, drone_id):
        return self.assignments.get(drone_id, [])

class TestDistributedDecision(unittest.TestCase):
    def setUp(self):
        self.drone = DummyDrone("UAV-01")
        self.shared_state = DummySharedState()
        self.manager = DummyAssignmentManager()
        self.agent = DecisionAgent(self.drone, self.shared_state, self.manager)

    def test_invalid_state(self):
        self.drone.status = 'FAILED'
        decision = self.agent.evaluate()
        self.assertEqual(decision.action, DecisionAction.HOLD_POSITION)

    def test_critical_battery(self):
        self.drone.battery = config.BATTERY_CRITICAL_THRESHOLD - 1.0
        decision = self.agent.evaluate()
        self.assertEqual(decision.action, DecisionAction.RETURN_TO_SAFE_ZONE)

    def test_local_hazard_assistance(self):
        self.shared_state.detections.append({
            "source_drone_id": "UAV-01",
            "object_class": "HUMAN"
        })
        decision = self.agent.evaluate()
        self.assertEqual(decision.action, DecisionAction.REQUEST_ASSISTANCE)

    def test_assigned_region_continue(self):
        self.manager.assignments["UAV-01"] = [
            {"region_id": "R1", "status": "ASSIGNED", "covered_fraction": 0.0}
        ]
        decision = self.agent.evaluate()
        self.assertEqual(decision.action, DecisionAction.CONTINUE_REGION)

    def test_assigned_region_completed(self):
        self.manager.assignments["UAV-01"] = [
            {"region_id": "R1", "status": "ASSIGNED", "covered_fraction": 1.0}
        ]
        decision = self.agent.evaluate()
        self.assertEqual(decision.action, DecisionAction.REQUEST_ASSIGNMENT)

    def test_no_assignment(self):
        self.manager.assignments["UAV-01"] = []
        decision = self.agent.evaluate()
        self.assertEqual(decision.action, DecisionAction.REQUEST_ASSIGNMENT)

if __name__ == '__main__':
    unittest.main()
