import unittest
import sys
import os
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from planning.collision_avoidance import CollisionChecker
from simulation.environment import FloodEnvironment
from mapping.flood_risk_map import FloodRiskMap
import config

class DummySharedState:
    def __init__(self):
        self.drone_states = {}
    def get_all_drone_states(self):
        return self.drone_states

class TestCollisionAvoidance(unittest.TestCase):
    def setUp(self):
        self.env = FloodEnvironment(seed=42)
        self.risk_map = FloodRiskMap(self.env)
        self.shared_state = DummySharedState()
        self.checker = CollisionChecker(self.risk_map, self.shared_state)

    def test_static_collision(self):
        # Center of a building in seed 42 is likely an obstacle. Let's find one.
        obs_i, obs_j = None, None
        for i in range(self.risk_map.num_cells_x):
            for j in range(self.risk_map.num_cells_y):
                if self.risk_map.obstacle_layer[i, j] > 0.5:
                    obs_i, obs_j = i, j
                    break
            if obs_i is not None:
                break
                
        if obs_i is not None:
            wx, wy = self.risk_map.grid_to_world(obs_i, obs_j)
            self.assertTrue(self.checker.is_static_collision(wx, wy))
            
    def test_out_of_bounds_collision(self):
        self.assertTrue(self.checker.is_static_collision(-10, -10))
        self.assertTrue(self.checker.is_static_collision(config.ENVIRONMENT_SIZE_X + 10, config.ENVIRONMENT_SIZE_Y + 10))

    def test_spatial_conflict(self):
        t = time.time()
        self.shared_state.drone_states = {
            "UAV-01": {"drone_id": "UAV-01", "position": [10.0, 10.0, 15.0], "last_updated": t},
            "UAV-02": {"drone_id": "UAV-02", "position": [90.0, 90.0, 15.0], "last_updated": t}
        }
        
        # Conflict with UAV-01
        is_conflict, peer = self.checker.is_spatial_conflict(12.0, 10.0, t, exclude_uav_id="UAV-03")
        self.assertTrue(is_conflict)
        self.assertEqual(peer, "UAV-01")
        
        # No conflict
        is_conflict_safe, _ = self.checker.is_spatial_conflict(50.0, 50.0, t, exclude_uav_id="UAV-03")
        self.assertFalse(is_conflict_safe)

    def test_stale_peer_ignored(self):
        t = time.time()
        self.shared_state.drone_states = {
            "UAV-01": {"drone_id": "UAV-01", "position": [10.0, 10.0, 15.0], "last_updated": t - 100.0} # Stale
        }
        
        # Should not conflict because the position is stale
        is_conflict, _ = self.checker.is_spatial_conflict(10.0, 10.0, t, exclude_uav_id="UAV-03")
        self.assertFalse(is_conflict)

if __name__ == '__main__':
    unittest.main()
