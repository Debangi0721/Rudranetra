import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.swarm import Swarm
from simulation.environment import FloodEnvironment
from mapping.flood_risk_map import FloodRiskMap
from planning.area_division import AreaDivision
from planning.assignment_manager import AssignmentManager
import config

class TestAssignmentIntegration(unittest.TestCase):
    def setUp(self):
        self.env = FloodEnvironment(seed=42)
        self.risk_map = FloodRiskMap(self.env)
        self.swarm = Swarm(number_of_drones=5)
        
        # Position UAVs across the map
        drones = self.swarm.get_all_drones()
        for i, d in enumerate(drones):
            d.position = [(i + 1) * 30.0, (i + 1) * 30.0, 10.0]
            d.battery = 100.0
            
        # One drone low battery
        drones[-1].battery = 10.0
            
        self.area_div = AreaDivision(self.risk_map)
        self.area_div.generate_regions()
        
        self.manager = AssignmentManager(self.swarm, self.area_div)

    def test_full_integration(self):
        # Initial check
        regions = self.area_div.get_all_regions()
        self.assertGreater(len(regions), 0)
        
        # Assign
        self.manager.assign_regions()
        
        report = self.manager.get_assignment_report()
        self.assertEqual(report["eligible_drones"], 4)
        self.assertEqual(report["ineligible_drones"], 1)
        self.assertGreater(report["assigned_regions"], 0)
        
        # Ensure no drone exceeds max regions
        for drone_id, count in report["assignments_per_drone"].items():
            self.assertLessEqual(count, config.MAX_REGIONS_PER_DRONE)
            
        # Complete a region
        assigned = [r for r in regions.values() if r["status"] == "ASSIGNED"]
        if assigned:
            r1 = assigned[0]
            self.manager.mark_region_in_progress(r1["region_id"], r1["assigned_drone_id"])
            self.manager.update_region_coverage(r1["region_id"], 1.0)
            
            self.assertEqual(r1["status"], "COMPLETED")
            
        # Simulate unavailability of a drone
        if assigned:
            d_id = assigned[-1]["assigned_drone_id"]
            unfinished_before = len(self.manager.get_drone_assignments(d_id))
            
            # Make ineligible
            drone = next(d for d in self.swarm.get_all_drones() if d.drone_id == d_id)
            drone.battery = 0.0
            
            self.manager.reassign_unfinished_regions(d_id)
            
            # Should have no assignments now except completed ones
            assignments_after = [r for r in self.manager.get_drone_assignments(d_id) if r["status"] != "COMPLETED"]
            self.assertEqual(len(assignments_after), 0)

if __name__ == '__main__':
    unittest.main()
