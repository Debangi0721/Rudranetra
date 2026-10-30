import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from planning.assignment_manager import AssignmentManager
from planning.area_division import AreaDivision
import config

class DummyDrone:
    def __init__(self, drone_id, position, battery=100.0, status="IDLE"):
        self.drone_id = drone_id
        self.position = position
        self.battery = battery
        self.status = status

class DummySwarm:
    def __init__(self, drones):
        self.drones = drones
    def get_all_drones(self):
        return self.drones

class DummyAreaDivision:
    def __init__(self):
        self.regions = {
            "R1": {"region_id": "R1", "status": "UNASSIGNED", "priority": 0.9, "center_x": 10.0, "center_y": 10.0, "assigned_drone_id": None, "covered_fraction": 0.0},
            "R2": {"region_id": "R2", "status": "UNASSIGNED", "priority": 0.2, "center_x": 90.0, "center_y": 90.0, "assigned_drone_id": None, "covered_fraction": 0.0},
            "R3": {"region_id": "R3", "status": "BLOCKED", "priority": 0.5, "center_x": 50.0, "center_y": 50.0, "assigned_drone_id": None, "covered_fraction": 0.0},
            "R4": {"region_id": "R4", "status": "COMPLETED", "priority": 0.5, "center_x": 20.0, "center_y": 20.0, "assigned_drone_id": "UAV-01", "covered_fraction": 1.0}
        }
    def get_all_regions(self):
        return self.regions
    def get_region(self, region_id):
        return self.regions.get(region_id)

class TestAssignmentManager(unittest.TestCase):
    def setUp(self):
        self.drones = [
            DummyDrone("UAV-01", [10.0, 10.0, 10.0]),
            DummyDrone("UAV-02", [90.0, 90.0, 10.0]),
            DummyDrone("UAV-03", [50.0, 50.0, 10.0], battery=5.0) # Ineligible
        ]
        self.swarm = DummySwarm(self.drones)
        self.area_div = DummyAreaDivision()
        self.manager = AssignmentManager(self.swarm, self.area_div)

    def test_eligible_drones(self):
        eligible, ineligible = self.manager.get_eligible_drones()
        self.assertEqual(len(eligible), 2)
        self.assertEqual(len(ineligible), 1)
        self.assertEqual(ineligible[0].drone_id, "UAV-03")

    def test_assign_regions(self):
        self.manager.assign_regions()
        
        # R1 is high priority and close to UAV-01
        self.assertEqual(self.area_div.regions["R1"]["assigned_drone_id"], "UAV-01")
        self.assertEqual(self.area_div.regions["R1"]["status"], "ASSIGNED")
        
        # R2 is low priority but close to UAV-02
        self.assertEqual(self.area_div.regions["R2"]["assigned_drone_id"], "UAV-02")
        self.assertEqual(self.area_div.regions["R2"]["status"], "ASSIGNED")
        
        # R3 is blocked
        self.assertIsNone(self.area_div.regions["R3"]["assigned_drone_id"])
        
        # R4 is completed
        self.assertEqual(self.area_div.regions["R4"]["assigned_drone_id"], "UAV-01")
        self.assertEqual(self.area_div.regions["R4"]["status"], "COMPLETED")

    def test_workload_capacity(self):
        # Override config
        original_max = config.MAX_REGIONS_PER_DRONE
        config.MAX_REGIONS_PER_DRONE = 1
        
        # Add another unassigned region near UAV-01
        self.area_div.regions["R5"] = {"region_id": "R5", "status": "UNASSIGNED", "priority": 0.8, "center_x": 12.0, "center_y": 12.0, "assigned_drone_id": None, "covered_fraction": 0.0}
        
        # Note: R4 is completed by UAV-01, but the manager counts ASSIGNED or IN_PROGRESS towards current workload
        # So UAV-01 currently has 0 active assignments.
        
        self.manager.assign_regions()
        
        # UAV-01 can only take 1 new region due to limit.
        assigned_to_uav1 = sum(1 for r in self.area_div.regions.values() if r["status"] == "ASSIGNED" and r["assigned_drone_id"] == "UAV-01")
        
        self.assertLessEqual(assigned_to_uav1, 1)
        
        # Restore config
        config.MAX_REGIONS_PER_DRONE = original_max

    def test_coverage_update_and_completion(self):
        self.manager.assign_regions()
        
        self.manager.mark_region_in_progress("R1", "UAV-01")
        self.assertEqual(self.area_div.regions["R1"]["status"], "IN_PROGRESS")
        
        self.manager.update_region_coverage("R1", 0.5)
        self.assertEqual(self.area_div.regions["R1"]["status"], "IN_PROGRESS")
        
        self.manager.update_region_coverage("R1", config.MIN_REGION_COVERAGE_FOR_COMPLETION + 0.01)
        self.assertEqual(self.area_div.regions["R1"]["status"], "COMPLETED")

    def test_reassign_unfinished(self):
        self.manager.assign_regions()
        self.manager.mark_region_in_progress("R1", "UAV-01")
        
        # Simulate UAV-01 going offline
        self.drones[0].battery = 0.0 # Make UAV-01 ineligible
        self.manager.reassign_unfinished_regions("UAV-01")
        
        # R1 should now be assigned to UAV-02 (since UAV-03 is ineligible and UAV-01 was released)
        self.assertEqual(self.area_div.regions["R1"]["assigned_drone_id"], "UAV-02")
        self.assertEqual(self.area_div.regions["R1"]["status"], "ASSIGNED") # Reverts to ASSIGNED for new drone
        
        # R4 was completed, it should not be reassigned
        self.assertEqual(self.area_div.regions["R4"]["assigned_drone_id"], "UAV-01")
        self.assertEqual(self.area_div.regions["R4"]["status"], "COMPLETED")

if __name__ == '__main__':
    unittest.main()
