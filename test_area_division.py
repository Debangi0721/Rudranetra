import unittest
import sys
import os
import math

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from planning.area_division import AreaDivision
from simulation.environment import FloodEnvironment
from mapping.flood_risk_map import FloodRiskMap
import config

class TestAreaDivision(unittest.TestCase):
    def setUp(self):
        self.env = FloodEnvironment(seed=42)
        self.risk_map = FloodRiskMap(self.env)
        self.division = AreaDivision(self.risk_map)
        
    def test_generate_regions(self):
        self.division.generate_regions()
        regions = self.division.get_all_regions()
        
        self.assertGreater(len(regions), 0)
        
        expected_num_x = int(math.ceil(config.ENVIRONMENT_SIZE_X / config.AREA_REGION_SIZE))
        expected_num_y = int(math.ceil(config.ENVIRONMENT_SIZE_Y / config.AREA_REGION_SIZE))
        self.assertEqual(len(regions), expected_num_x * expected_num_y)

    def test_region_boundaries(self):
        self.division.generate_regions()
        regions = list(self.division.get_all_regions().values())
        
        # Check first region boundaries
        r1 = regions[0]
        self.assertEqual(r1["x_min"], 0.0)
        self.assertEqual(r1["y_min"], 0.0)
        self.assertLessEqual(r1["x_max"], config.ENVIRONMENT_SIZE_X)
        self.assertLessEqual(r1["y_max"], config.ENVIRONMENT_SIZE_Y)

    def test_deterministic_ids(self):
        self.division.generate_regions()
        regions1 = list(self.division.get_all_regions().keys())
        
        self.division.generate_regions()
        regions2 = list(self.division.get_all_regions().keys())
        
        self.assertEqual(regions1, regions2)

    def test_region_priority(self):
        self.division.generate_regions()
        regions = list(self.division.get_all_regions().values())
        
        for r in regions:
            self.assertGreaterEqual(r["priority"], 0.0)
            self.assertLessEqual(r["priority"], 1.0)

if __name__ == '__main__':
    unittest.main()
