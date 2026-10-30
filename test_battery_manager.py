import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.mission_orchestrator import MissionOrchestrator, MissionConfig
import config

class TestBatteryManager(unittest.TestCase):
    def setUp(self):
        self.config = MissionConfig(seed=42, num_drones=2, timestep=1.0, max_steps=100)
        self.orchestrator = MissionOrchestrator(self.config)
        self.orchestrator.initialize()

    def test_battery_consumption_updates(self):
        d0 = self.orchestrator.swarm.get_all_drones()[0]
        initial_battery = d0.battery
        
        # Advance simulation
        self.orchestrator.step()
        
        # Should have consumed some battery
        self.assertLess(d0.battery, initial_battery)
        
    def test_battery_bounds(self):
        d0 = self.orchestrator.swarm.get_all_drones()[0]
        d0.battery = 0.01 # Almost dead
        
        self.orchestrator.step()
        
        self.assertGreaterEqual(d0.battery, 0.0)
        
    def test_mission_feasibility_checks(self):
        d0 = self.orchestrator.swarm.get_all_drones()[0]
        d0.battery = 100.0 # Full battery
        
        target_pos = [100.0, 100.0, 10.0]
        is_feasible = self.orchestrator.battery_manager.is_mission_feasible(d0, target_pos)
        self.assertTrue(is_feasible)
        
        d0.battery = 1.0 # Very low battery
        is_feasible = self.orchestrator.battery_manager.is_mission_feasible(d0, target_pos)
        self.assertFalse(is_feasible)
        
    def test_rtb_trigger_and_route(self):
        d0 = self.orchestrator.swarm.get_all_drones()[0]
        d0.battery = 15.0 # Below critical threshold (20)
        
        self.orchestrator.step()
        
        # Drone should switch to RETURNING
        self.assertEqual(d0.status, "RETURNING")
        
        # Should have a route home
        active_path = self.orchestrator.movement.active_paths.get(d0.drone_id)
        self.assertIsNotNone(active_path)
        self.assertFalse(active_path["paused"])
        
    def test_fault_injection_propulsion(self):
        d0 = self.orchestrator.swarm.get_all_drones()[0]
        
        self.orchestrator.fault_injector.inject_propulsion_failure(d0.drone_id)
        
        self.assertEqual(d0.status, "FAILED")
        self.assertNotIn(d0.drone_id, self.orchestrator.movement.active_paths)
        
    def test_failed_drone_reassigned_region(self):
        d0 = self.orchestrator.swarm.get_all_drones()[0]
        
        # Assign a region
        region_id = list(self.orchestrator.area_div.regions.keys())[0]
        self.orchestrator.assignment_manager.assign_region(region_id, d0.drone_id)
        
        # Inject failure
        self.orchestrator.fault_injector.inject_propulsion_failure(d0.drone_id)
        
        # Replanning should catch it and unassign
        self.orchestrator.replanning_manager.check_and_replan()
        
        assignments = self.orchestrator.assignment_manager.get_drone_assignments(d0.drone_id)
        self.assertEqual(len(assignments), 0)
        
if __name__ == '__main__':
    unittest.main()
