import unittest
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.movement_controller import MovementController
from planning.path_planner import PathResult
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

class DummyCollisionChecker:
    def __init__(self):
        self.static_collision = False
        self.spatial_conflict = (False, None)
        
    def is_static_collision(self, x, y):
        return self.static_collision
        
    def is_spatial_conflict(self, x, y, current_time, exclude_uav_id=None):
        return self.spatial_conflict

class TestMovementController(unittest.TestCase):
    def setUp(self):
        self.drone1 = DummyDrone("UAV-01", [10.0, 10.0, 15.0])
        self.drone2 = DummyDrone("UAV-02", [20.0, 20.0, 15.0])
        self.swarm = DummySwarm([self.drone1, self.drone2])
        self.collision_checker = DummyCollisionChecker()
        self.controller = MovementController(self.swarm, self.collision_checker)

    def test_advance_valid_path(self):
        path = PathResult("UAV-01", [10.0, 10.0], [50.0, 10.0], [[10.0, 10.0, 15.0], [50.0, 10.0, 15.0]], True, 40.0, "")
        self.controller.set_path("UAV-01", path)
        
        # Advance 1 second. Speed is 5.0m/s
        results = self.controller.step(1.0, time.time())
        
        res1 = [r for r in results if r.uav_id == "UAV-01"][0]
        self.assertEqual(res1.status, "MOVING")
        self.assertEqual(self.drone1.position[0], 15.0) # 10.0 + 5.0
        self.assertEqual(self.drone1.position[1], 10.0)

    def test_waypoint_reached(self):
        # Place drone very close to waypoint 0
        self.drone1.position = [10.5, 10.0, 15.0]
        path = PathResult("UAV-01", [10.0, 10.0], [50.0, 10.0], [[10.0, 10.0, 15.0], [50.0, 10.0, 15.0]], True, 40.0, "")
        self.controller.set_path("UAV-01", path)
        
        # Step will trigger WAYPOINT_TOLERANCE check and increment wp_idx
        self.controller.step(1.0, time.time())
        self.assertEqual(self.controller.active_paths["UAV-01"]["wp_idx"], 1)

    def test_path_completed(self):
        path = PathResult("UAV-01", [10.0, 10.0], [50.0, 10.0], [[10.0, 10.0, 15.0]], True, 0.0, "")
        self.controller.set_path("UAV-01", path)
        
        # Manually force wp index past end
        self.controller.active_paths["UAV-01"]["wp_idx"] = 1
        
        results = self.controller.step(1.0, time.time())
        res1 = [r for r in results if r.uav_id == "UAV-01"][0]
        self.assertEqual(res1.status, "COMPLETED")

    def test_static_collision_blocks_movement(self):
        path = PathResult("UAV-01", [10.0, 10.0], [50.0, 10.0], [[10.0, 10.0, 15.0], [50.0, 10.0, 15.0]], True, 40.0, "")
        self.controller.set_path("UAV-01", path)
        
        # Force a collision
        self.collision_checker.static_collision = True
        
        results = self.controller.step(1.0, time.time())
        res1 = [r for r in results if r.uav_id == "UAV-01"][0]
        
        self.assertEqual(res1.status, "BLOCKED")
        self.assertEqual(self.drone1.position[0], 10.0) # Should not have moved

    def test_battery_consumption_and_depletion(self):
        path = PathResult("UAV-01", [10.0, 10.0], [50.0, 10.0], [[10.0, 10.0, 15.0], [50.0, 10.0, 15.0]], True, 40.0, "")
        self.controller.set_path("UAV-01", path)
        
        # Move for 10 seconds (Moving = 0.5/s)
        self.controller.step(10.0, time.time())
        self.assertEqual(self.drone1.battery, 95.8)
        
        # Deplete battery
        self.drone1.battery = 0.0
        results = self.controller.step(1.0, time.time())
        res1 = [r for r in results if r.uav_id == "UAV-01"][0]
        self.assertEqual(res1.status, "UNAVAILABLE")

if __name__ == '__main__':
    unittest.main()
