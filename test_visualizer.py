import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.mission_orchestrator import MissionOrchestrator, MissionConfig
from visualization.live_visualizer import LiveVisualizer

class TestLiveVisualizer(unittest.TestCase):
    def setUp(self):
        self.config = MissionConfig(seed=42, num_drones=2, timestep=1.0, max_steps=5)
        self.orchestrator = MissionOrchestrator(self.config)
        self.orchestrator.initialize()
        
        # Always run headless in tests to avoid popping up windows
        self.visualizer = LiveVisualizer(self.orchestrator, headless=True)

    def test_initialization_headless(self):
        self.visualizer.init_plot()
        self.assertTrue(self.visualizer.is_initialized)
        self.assertIsNone(self.visualizer.fig) # Headless shouldn't create a real figure

    def test_update_headless(self):
        self.visualizer.update()
        self.assertTrue(self.visualizer.is_initialized)
        
        # Advance simulation
        self.orchestrator.step()
        self.visualizer.update() # Should not crash
        
    def test_close_headless(self):
        self.visualizer.update()
        self.visualizer.close()
        self.assertFalse(self.visualizer.is_initialized)

if __name__ == '__main__':
    unittest.main()
