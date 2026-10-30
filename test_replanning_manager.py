import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.mission_orchestrator import MissionOrchestrator, MissionConfig
import config

class TestReplanningManager(unittest.TestCase):
    def setUp(self):
        self.config = MissionConfig(seed=42, num_drones=2, timestep=1.0, max_steps=10)
        self.orchestrator = MissionOrchestrator(self.config)
        self.orchestrator.initialize()

    def test_no_meaningful_change_no_replan(self):
        # Initial state should not trigger replanning instantly, only periodic review
        self.orchestrator.sim_time = 15.0
        self.orchestrator.replanning_manager.last_replan_time = 0.0
        triggers = self.orchestrator.replanning_manager._evaluate_triggers()
        self.assertIn("PERIODIC_REVIEW", triggers)
        
        self.orchestrator.replanning_manager.last_replan_time = 15.0 # ensure it won't hit periodic
        triggers = self.orchestrator.replanning_manager._evaluate_triggers()
        self.assertEqual(len(triggers), 0)

    def test_uav_unavailable_triggers_replanning(self):
        # Force assign a region to drone 0
        d0 = self.orchestrator.swarm.get_all_drones()[0]
        region_id = list(self.orchestrator.area_div.regions.keys())[0]
        self.orchestrator.assignment_manager.assign_region(region_id, d0.drone_id)
        
        # Kill battery
        d0.battery = 0.0
        
        triggers = self.orchestrator.replanning_manager._evaluate_triggers()
        self.assertIn(f"UAV_UNAVAILABLE_{d0.drone_id}", triggers)

    def test_route_blocked_triggers_replanning(self):
        d0 = self.orchestrator.swarm.get_all_drones()[0]
        # Fake a paused route
        self.orchestrator.movement.active_paths[d0.drone_id] = {"path": None, "paused": True}
        
        triggers = self.orchestrator.replanning_manager._evaluate_triggers()
        self.assertIn(f"ROUTE_BLOCKED_{d0.drone_id}", triggers)
        
    def test_replanning_clears_blocked_path(self):
        d0 = self.orchestrator.swarm.get_all_drones()[0]
        self.orchestrator.movement.active_paths[d0.drone_id] = {"path": "FAKE_PATH", "paused": True}
        
        self.orchestrator.replanning_manager.check_and_replan()
        
        # The path should be cleared (meaning it's gone or reset)
        self.assertNotIn(d0.drone_id, self.orchestrator.movement.active_paths)
        
    def test_uav_unavailable_reassigns_regions(self):
        d0 = self.orchestrator.swarm.get_all_drones()[0]
        region_id = list(self.orchestrator.area_div.regions.keys())[0]
        self.orchestrator.assignment_manager.assign_region(region_id, d0.drone_id)
        
        # Simulate unavailable
        d0.battery = 0.0
        self.orchestrator.replanning_manager.check_and_replan()
        
        # Check that d0 no longer has it
        assigned = self.orchestrator.assignment_manager.get_drone_assignments(d0.drone_id)
        self.assertEqual(len(assigned), 0)
        
        # Check that it was reassigned to someone else (or left unassigned if no eligible)
        region = self.orchestrator.area_div.get_region(region_id)
        self.assertNotEqual(region["assigned_drone_id"], d0.drone_id)

if __name__ == '__main__':
    unittest.main()
