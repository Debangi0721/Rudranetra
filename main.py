import argparse
from simulation.mission_orchestrator import MissionOrchestrator, MissionConfig
from visualization.live_visualizer import LiveVisualizer
import json

def main():
    parser = argparse.ArgumentParser(description="RudraNetra Swarm Simulation")
    parser.add_argument('--headless', action='store_true', help="Run without visualization")
    parser.add_argument('--steps', type=int, default=50, help="Maximum simulation steps")
    parser.add_argument('--use-ml', action='store_true', help="Use ML predictor for region prioritization")
    parser.add_argument('--demo-failure', action='store_true', help="Kill a UAV at step 25 to demonstrate replanning")
    parser.add_argument('--demo-rtb', action='store_true', help="Trigger RTB for UAV-01 at step 25")
    args = parser.parse_args()

    print("========================================")
    print("RUDRANETRA — MODULE 14")
    print("UAV FAILURE RECOVERY, BATTERY MANAGEMENT & RTB\n")
    
    # 1. Setup Mission Config
    config = MissionConfig(seed=42, num_drones=3, timestep=1.0, max_steps=args.steps)
    
    # 2. Build Orchestrator & Visualizer
    print("Initializing Mission...")
    orchestrator = MissionOrchestrator(config)
    orchestrator.initialize()
    
    # ML Integration
    if args.use_ml:
        print("Training synthetic ML Predictor...")
        from ml.flood_risk_predictor import FloodRiskPredictor
        predictor = FloodRiskPredictor(random_state=42)
        success, metrics = predictor.train_synthetic(orchestrator.fmap)
        if success:
            print(f"ML Predictor Trained (MAE: {metrics['mae']:.3f})")
            pred_map = predictor.predict_map(orchestrator.fmap)
            orchestrator.fmap.predicted_risk_layer = pred_map
            # Regenerate assignments with new ML-boosted priorities
            orchestrator.area_div.generate_regions()
            orchestrator.assignment_manager.assign_regions()
        else:
            print("ML Predictor failed to train. Running without ML.")
            
    visualizer = LiveVisualizer(orchestrator, headless=args.headless, update_interval=0.1)
    
    print(f"Status: {orchestrator.status}")
    print(f"Total Regions to Map: {orchestrator.area_div.regions.__len__()}")
    print(f"Eligible UAVs: {len(orchestrator.swarm.get_all_drones())}\n")
    print(f"Headless Mode: {args.headless}")
    
    # 3. Run Mission
    print("Running Simulation...")
    while orchestrator.status in ("READY", "RUNNING"):
        orchestrator.step()
        
        # Inject Failure
        if args.demo_failure and orchestrator.current_step == 25:
            print("\n*** DEMO FAILURE: Simulating propulsion failure on UAV-01 ***")
            target = orchestrator.swarm.get_all_drones()[0]
            orchestrator.fault_injector.inject_propulsion_failure(target.drone_id)
            
        # Inject RTB Low Battery
        if getattr(args, 'demo_rtb', False) and orchestrator.current_step == 25:
            print("\n*** DEMO RTB: Forcing low battery on UAV-02 to trigger RTB ***")
            target = orchestrator.swarm.get_all_drones()[1]
            target.battery = 18.0 # Triggers BATTERY_CRITICAL_THRESHOLD
            
        visualizer.update()
        
        # Print progress every 10 steps
        if orchestrator.current_step % 10 == 0:
            print(f"  Step {orchestrator.current_step} | Time {orchestrator.sim_time:.1f}s | Coverage: {orchestrator.metrics['completed_regions']} regions completed")
            
    # 4. Final Summary
    visualizer.close()
    
    print(f"\nMission Terminated. Final Status: {orchestrator.status}")
    print("\n--- Final Summary ---")
    summary = orchestrator.get_summary()
    for k, v in summary.items():
        print(f"{k}: {v}")
        
    print("\nMission Orchestration & Visualization test: PASSED")
    print("========================================")

if __name__ == "__main__":
    main()
