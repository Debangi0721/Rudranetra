import unittest
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.environment import FloodEnvironment
from mapping.flood_risk_map import FloodRiskMap
import config

class TestFloodRiskMap(unittest.TestCase):
    def setUp(self):
        self.env = FloodEnvironment(seed=42)
        self.map = FloodRiskMap(self.env)
        
    def test_initialization(self):
        self.assertIsNotNone(self.map)
        self.assertEqual(self.map.resolution, config.MAP_RESOLUTION)
        self.assertEqual(self.map.size_x, config.ENVIRONMENT_SIZE_X)
        self.assertEqual(self.map.size_y, config.ENVIRONMENT_SIZE_Y)

    def test_dimensions(self):
        expected_x = int(np.ceil(config.ENVIRONMENT_SIZE_X / config.MAP_RESOLUTION))
        expected_y = int(np.ceil(config.ENVIRONMENT_SIZE_Y / config.MAP_RESOLUTION))
        self.assertEqual(self.map.num_cells_x, expected_x)
        self.assertEqual(self.map.num_cells_y, expected_y)
        self.assertEqual(self.map.terrain_layer.shape, (expected_x, expected_y))

    def test_coordinate_conversions(self):
        x, y = 10.5, 20.5
        i, j = self.map.world_to_grid(x, y)
        self.assertIsNotNone(i)
        self.assertIsNotNone(j)
        
        rx, ry = self.map.grid_to_world(i, j)
        self.assertAlmostEqual(x, rx, delta=config.MAP_RESOLUTION)
        self.assertAlmostEqual(y, ry, delta=config.MAP_RESOLUTION)
        
        self.assertIsNone(self.map.world_to_grid(-10, -10))
        self.assertIsNone(self.map.world_to_grid(config.ENVIRONMENT_SIZE_X + 10, config.ENVIRONMENT_SIZE_Y + 10))
        self.assertIsNone(self.map.grid_to_world(-1, -1))
        self.assertIsNone(self.map.grid_to_world(self.map.num_cells_x, self.map.num_cells_y))

    def test_terrain_layer(self):
        self.assertTrue(np.all(np.isfinite(self.map.terrain_layer)))

    def test_water_depth_layer(self):
        self.assertTrue(np.all(np.isfinite(self.map.water_depth_layer)))
        self.assertTrue(np.all(self.map.water_depth_layer >= 0))

    def test_flood_risk_layer(self):
        self.assertTrue(np.all(np.isfinite(self.map.flood_risk_layer)))
        self.assertTrue(np.all(self.map.flood_risk_layer >= 0.0))
        self.assertTrue(np.all(self.map.flood_risk_layer <= 1.0))

    def test_risk_classification(self):
        self.assertTrue(np.all(self.map.risk_class_layer >= 0))
        self.assertTrue(np.all(self.map.risk_class_layer <= 4))

    def test_obstacle_layer(self):
        self.assertTrue(np.all((self.map.obstacle_layer == 0) | (self.map.obstacle_layer == 1)))

    def test_priority_layer(self):
        self.assertTrue(np.all(np.isfinite(self.map.priority_layer)))
        self.assertTrue(np.all(self.map.priority_layer >= 0.0))
        self.assertTrue(np.all(self.map.priority_layer <= 1.0))
        
    def test_coverage(self):
        self.assertEqual(self.map.get_coverage_percentage(), 0.0)
        self.map.update_cell(10.0, 10.0, "coverage_layer", 1)
        self.assertGreater(self.map.get_coverage_percentage(), 0.0)

    def test_cell_data(self):
        data = self.map.get_cell_data(10.0, 10.0)
        self.assertIsNotNone(data)
        self.assertIn("terrain_height", data)
        self.assertIn("flood_risk", data)

    def test_region_extraction(self):
        safe_cells = self.map.get_cells_by_risk("SAFE")
        self.assertIsInstance(safe_cells, list)
        
        hp_cells = self.map.get_high_priority_cells(0.5)
        self.assertIsInstance(hp_cells, list)
        
    def test_save_load(self):
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".npz", delete=False) as tmp:
            tmp_path = tmp.name
            
        try:
            self.map.save(tmp_path)
            
            new_map = FloodRiskMap() # Empty map
            new_map.load(tmp_path)
            
            np.testing.assert_array_equal(self.map.terrain_layer, new_map.terrain_layer)
            np.testing.assert_array_equal(self.map.flood_risk_layer, new_map.flood_risk_layer)
            np.testing.assert_array_equal(self.map.obstacle_layer, new_map.obstacle_layer)
            
            self.assertEqual(self.map.size_x, new_map.size_x)
            self.assertEqual(self.map.resolution, new_map.resolution)
        finally:
            os.remove(tmp_path)

    def test_determinism(self):
        env2 = FloodEnvironment(seed=42)
        map2 = FloodRiskMap(env2)
        
        np.testing.assert_array_equal(self.map.terrain_layer, map2.terrain_layer)
        np.testing.assert_array_equal(self.map.water_depth_layer, map2.water_depth_layer)
        np.testing.assert_array_equal(self.map.building_layer, map2.building_layer)
        
    def test_statistics(self):
        stats = self.map.get_statistics()
        self.assertIn("total_cells", stats)
        self.assertEqual(stats["total_cells"], self.map.num_cells_x * self.map.num_cells_y)

if __name__ == '__main__':
    unittest.main()
