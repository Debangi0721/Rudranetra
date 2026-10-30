import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from planning.path_planner import PathPlanner
from simulation.environment import FloodEnvironment
from mapping.flood_risk_map import FloodRiskMap
import config
import time

class DummySharedState:
    def __init__(self):
        self.drone_states = {}
    def get_all_drone_states(self):
        return self.drone_states

class TestPathPlanner(unittest.TestCase):
    def setUp(self):
        self.env = FloodEnvironment(seed=42)
        self.risk_map = FloodRiskMap(self.env)
        
        # Clear obstacle layer for simple tests
        self.risk_map.obstacle_layer[:] = 0.0
        
        self.shared_state = DummySharedState()
        self.planner = PathPlanner(self.risk_map, self.shared_state)

    def test_valid_route_free_space(self):
        start = [10.0, 10.0]
        goal = [50.0, 50.0]
        
        result = self.planner.plan_path("UAV-01", start, goal)
        self.assertTrue(result.success)
        self.assertGreater(len(result.waypoints), 0)
        self.assertEqual(result.waypoints[0][0], 10.0)
        self.assertEqual(result.waypoints[-1][0], 50.0)

    def test_blocked_start(self):
        # Block the start cell
        sx, sy = self.risk_map.world_to_grid(10.0, 10.0)
        self.risk_map.obstacle_layer[sx, sy] = 1.0
        
        result = self.planner.plan_path("UAV-01", [10.0, 10.0], [50.0, 50.0])
        self.assertFalse(result.success)
        self.assertIn("inside obstacle", result.reason)

    def test_unreachable_goal(self):
        # Create a wall
        for j in range(self.risk_map.num_cells_y):
            self.risk_map.obstacle_layer[self.risk_map.num_cells_x // 2, j] = 1.0
            
        start = [10.0, 10.0]
        goal = [config.ENVIRONMENT_SIZE_X - 10.0, 10.0]
        
        result = self.planner.plan_path("UAV-01", start, goal)
        self.assertFalse(result.success)
        self.assertIn("No path found", result.reason)

    def test_start_equals_goal(self):
        result = self.planner.plan_path("UAV-01", [10.0, 10.0], [10.0, 10.0])
        self.assertTrue(result.success)
        self.assertEqual(len(result.waypoints), 2) # Just start and goal

    def test_multi_uav_conflict_detection(self):
        t = time.time()
        self.shared_state.drone_states = {
            "UAV-02": {"drone_id": "UAV-02", "position": [30.0, 30.0, 15.0], "last_updated": t}
        }
        
        # Path passes right through UAV-02
        start = [10.0, 30.0]
        goal = [50.0, 30.0]
        
        result = self.planner.plan_path("UAV-01", start, goal, current_time=t)
        self.assertFalse(result.success)
        self.assertIn("spatially conflicts", result.reason)

if __name__ == '__main__':
    unittest.main()
