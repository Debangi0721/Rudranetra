import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.environment import FloodEnvironment
import config

class TestEnvironment(unittest.TestCase):
    def test_environment_creation(self):
        env = FloodEnvironment()
        self.assertIsNotNone(env)

    def test_correct_dimensions(self):
        env = FloodEnvironment()
        self.assertEqual(env.size_x, config.ENVIRONMENT_SIZE_X)
        self.assertEqual(env.size_y, config.ENVIRONMENT_SIZE_Y)

    def test_deterministic_generation(self):
        env1 = FloodEnvironment(seed=42)
        env2 = FloodEnvironment(seed=42)
        env3 = FloodEnvironment(seed=99)
        
        b1 = env1.get_buildings()[0]
        b2 = env2.get_buildings()[0]
        b3 = env3.get_buildings()[0]
        
        self.assertEqual(b1["x"], b2["x"])
        self.assertEqual(b1["y"], b2["y"])
        
        # Depending on random generation, it's highly likely b1 != b3
        self.assertNotEqual(b1["x"], b3["x"])

    def test_buildings_inside_boundaries(self):
        env = FloodEnvironment()
        for b in env.get_buildings():
            self.assertTrue(env.is_inside_environment(b["x"], b["y"]))

    def test_trees_inside_boundaries(self):
        env = FloodEnvironment()
        for t in env.get_trees():
            self.assertTrue(env.is_inside_environment(t["x"], t["y"]))

    def test_poles_inside_boundaries(self):
        env = FloodEnvironment()
        for p in env.get_poles():
            self.assertTrue(env.is_inside_environment(p["x"], p["y"]))

    def test_people_inside_boundaries(self):
        env = FloodEnvironment()
        for p in env.get_people():
            self.assertTrue(env.is_inside_environment(p["position"][0], p["position"][1]))

    def test_vehicles_inside_boundaries(self):
        env = FloodEnvironment()
        for v in env.get_vehicles():
            self.assertTrue(env.is_inside_environment(v["position"][0], v["position"][1]))

    def test_safe_zones_inside_boundaries(self):
        env = FloodEnvironment()
        for sz in env.get_safe_zones():
            self.assertTrue(env.is_inside_environment(sz["center"][0], sz["center"][1]))

    def test_flood_depth_returns_valid_values(self):
        env = FloodEnvironment()
        depth = env.get_flood_depth(100.0, 100.0)
        self.assertGreaterEqual(depth, 0.0)
        self.assertTrue(np.isfinite(depth))

    def test_flood_risk_remains_between_0_and_1(self):
        env = FloodEnvironment()
        for _ in range(100):
            x, y = np.random.uniform(0, 200), np.random.uniform(0, 200)
            risk = env.get_flood_risk(x, y)
            self.assertGreaterEqual(risk, 0.0)
            self.assertLessEqual(risk, 1.0)

    def test_terrain_height_is_finite(self):
        env = FloodEnvironment()
        for _ in range(100):
            x, y = np.random.uniform(0, 200), np.random.uniform(0, 200)
            h = env.get_terrain_height(x, y)
            self.assertTrue(np.isfinite(h))

    def test_obstacle_queries_work(self):
        env = FloodEnvironment()
        # Query way outside
        self.assertFalse(env.is_obstacle_at(-10, -10, 0))
        # Query way below ground
        self.assertTrue(env.is_obstacle_at(100, 100, -10))
        
        # Check inside a building
        b = env.get_buildings()[0]
        self.assertTrue(env.is_obstacle_at(b["x"], b["y"], b["height"] / 2))
        
        # Check above a building
        self.assertFalse(env.is_obstacle_at(b["x"], b["y"], b["height"] + 10))

    def test_environment_summary_works(self):
        env = FloodEnvironment()
        summary = env.get_environment_summary()
        self.assertIn("buildings", summary)
        self.assertEqual(summary["buildings"], config.NUM_BUILDINGS)
        self.assertEqual(summary["trees"], config.NUM_TREES)

if __name__ == '__main__':
    unittest.main()
