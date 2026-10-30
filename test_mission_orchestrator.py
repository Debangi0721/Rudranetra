import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.mission_orchestrator import MissionOrchestrator, MissionConfig

class TestMissionOrchestrator(unittest.TestCase):
    def setUp(self):
        self.config = MissionConfig(seed=42, num_drones=2, timestep=1.0, max_steps=10)
        self.orchestrator = MissionOrchestrator(self.config)

    def test_initialization(self):
        self.assertEqual(self.orchestrator.status, "CREATED")
        self.orchestrator.initialize()
        self.assertEqual(self.orchestrator.status, "READY")
        self.assertIsNotNone(self.orchestrator.env)
        self.assertIsNotNone(self.orchestrator.movement)
        self.assertEqual(len(self.orchestrator.swarm.get_all_drones()), 2)
        
    def test_single_step(self):
        self.orchestrator.initialize()
        self.orchestrator.step()
        self.assertEqual(self.orchestrator.status, "RUNNING")
        self.assertEqual(self.orchestrator.metrics["total_steps"], 1)
        self.assertEqual(self.orchestrator.metrics["sim_time"], 1.0)
        
    def test_bounded_run(self):
        self.orchestrator.initialize()
        self.orchestrator.run()
        
        # In a 10 step simulation, it should hit max_steps and STOP
        self.assertEqual(self.orchestrator.status, "STOPPED")
        self.assertEqual(self.orchestrator.metrics["total_steps"], 10)
        self.assertEqual(self.orchestrator.metrics["sim_time"], 10.0)

    def test_summary_generation(self):
        self.orchestrator.initialize()
        self.orchestrator.step()
        
        summary = self.orchestrator.get_summary()
        self.assertEqual(summary["status"], "RUNNING")
        self.assertEqual(summary["total_steps"], 1)
        self.assertIn("coverage_percentage", summary)
        self.assertIn("eligible_uavs", summary)

if __name__ == '__main__':
    unittest.main()
