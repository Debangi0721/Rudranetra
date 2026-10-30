# RudraNetra — AI/ML-Based Simulated 3D UAV Swarm

RudraNetra is a comprehensive, deterministic, Python-based simulation for multi-UAV swarm coordination during flood and disaster navigation.

The system models a complete, decentralized 3D environment including environment generation, real-time sensing, inter-UAV communication, distributed decision making, dynamic path planning, battery management, target rescue prioritization, and ML-assisted risk prediction.

## Supported Features

- **Multi-UAV Swarm Foundation (Module 1):** Distributed simulation state and UAV models.
- **Simulated Sensors (Module 2):** LiDAR, GPS, IMU, and probabilistic Victim Detection tracking.
- **3D Flood Environment (Module 3):** Procedurally generated, deterministic maps with varied terrains, obstacles, safe zones, and risk profiles.
- **Flood Risk Mapping (Module 4):** A global map representation for UAVs to ingest and predict against.
- **Communication Network (Module 5):** Distance-based, message queue-limited mesh networking between UAVs.
- **Swarm Area Division (Module 6):** K-Means based geometric partitioning of flood areas to assign dynamic search regions.
- **Distributed Decision Making (Module 7):** Autonomous, decentralized state evaluation per drone. Prioritizes local hazards, low battery, rescue targets, and regional completion.
- **Path Planning & Collision Avoidance (Module 8):** A* routing in 3D voxel-space, with explicit temporal conflict resolution across swarm members.
- **Flight Execution (Module 9):** Kinematic movement over time steps.
- **Mission Orchestration & Visualization (Modules 10 & 11):** A unified `main.py` entry point and live Matplotlib 3D rendering.
- **ML Risk Prediction (Module 12):** Scikit-Learn based RandomForest regression for mapping hidden variables to risk priorities.
- **Dynamic Replanning (Module 13):** Autonomous unassignment and reallocation if tasks become stranded.
- **Failure Recovery & Battery Management (Module 14):** Feasibility checks, propulsion failure injection, and automated Return-To-Base (RTB).
- **Target Tracking & Rescue (Module 16):** Probabilistic victim detection, localization noise, multi-drone duplicate resolution, and prioritized rescue actions.
- **Performance Evaluation (Module 17):** Headless JSON metric generation for complex scenarios.

## Missing Capabilities & Limitations

- **Complex Multi-Hop RTB:** RTB logic relies on direct path planning to the nearest safe zone. If completely walled off post-failure, the UAV may freeze.
- **True Vision AI:** Sensor modeling relies on mathematical boundaries and RNG thresholds, rather than loading real images into a CNN.
- **Dynamic Water Flow:** Flood maps are static in depth relative to ground level. Hydrodynamics are not simulated.

## Installation

Ensure you have Python 3.10+ installed.

```bash
pip install numpy matplotlib scikit-learn
```

## Running the Simulation

**Launch the Interactive 3D Demo:**
```bash
python main.py
```

**Run in Headless Mode (Faster, no UI):**
```bash
python main.py --headless
```

**Run with ML Predictor Enabled:**
```bash
python main.py --use-ml
```

**Run with Failure Injection Demo:**
```bash
python main.py --demo-failure
```

**Run with RTB (Low Battery) Demo:**
```bash
python main.py --demo-rtb
```

## Testing & Benchmarking

**Run Unit & Regression Tests (136 Tests):**
```bash
python -m unittest discover tests
```

**Run Performance Evaluation & Stress Testing:**
```bash
python evaluation/scenario_runner.py
```
*Results will be saved as JSON outputs inside the `results/` folder.*
