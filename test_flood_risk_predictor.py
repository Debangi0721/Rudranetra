import unittest
import sys
import os
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from ml.flood_risk_predictor import FloodRiskPredictor
from simulation.environment import FloodEnvironment
from mapping.flood_risk_map import FloodRiskMap

class TestFloodRiskPredictor(unittest.TestCase):
    def setUp(self):
        self.env = FloodEnvironment(seed=123)
        self.fmap = FloodRiskMap(self.env)
        self.predictor = FloodRiskPredictor(random_state=42)

    def test_untrained_prediction(self):
        # Predict should return safe default when untrained
        val, cls = self.predictor.predict_cell({"terrain_height": 10.0})
        self.assertEqual(val, 0.0)
        self.assertEqual(cls, "UNKNOWN")

    def test_synthetic_training_and_prediction(self):
        # Train
        success, metrics = self.predictor.train_synthetic(self.fmap)
        self.assertTrue(success)
        self.assertIn("mae", metrics)
        
        # Test individual predict
        val, cls = self.predictor.predict_cell({"terrain_height": 0.0, "safe_zone": 0.0})
        self.assertTrue(0.0 <= val <= 1.0)
        self.assertIn(cls, ["SAFE", "LOW", "MEDIUM", "HIGH", "CRITICAL"])
        
        # Test full map predict
        pred_map = self.predictor.predict_map(self.fmap)
        self.assertEqual(pred_map.shape, (self.fmap.num_cells_x, self.fmap.num_cells_y))
        
        # Ensure it didn't mutate the ground truth
        self.assertFalse(np.array_equal(pred_map, self.fmap.flood_risk_layer))

    def test_invalid_input_handling(self):
        self.predictor.train_synthetic(self.fmap)
        # Pass NaN
        val, cls = self.predictor.predict_cell({"terrain_height": float('nan')})
        self.assertEqual(val, 0.0)
        self.assertEqual(cls, "INVALID")

    def test_save_and_load(self):
        self.predictor.train_synthetic(self.fmap)
        path = "test_model.pkl"
        self.predictor.save(path)
        self.assertTrue(os.path.exists(path))
        
        new_predictor = FloodRiskPredictor()
        self.assertTrue(new_predictor.load(path))
        
        os.remove(path)

if __name__ == '__main__':
    unittest.main()
