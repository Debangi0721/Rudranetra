# 3D AI/ML Drone Navigation Simulator

## 1. Abstract
This project is a complete, working local 3D AI/ML drone navigation simulator built in Python. It demonstrates autonomous drone navigation in a 3D environment with dynamic obstacles using a hybrid architecture that combines classical 3D A* path planning with a machine learning-based local navigation policy. The simulation features realistic sensor modeling (GPS, IMU, and LiDAR) and dynamic visualization.

## 2. Problem Statement
Autonomous drone navigation in unknown or dynamic environments is challenging. Pre-planned paths often fail when new obstacles appear. A robust system must continuously perceive its environment, fuse sensor data, and make real-time decisions to avoid collisions while progressing toward a goal.

## 3. Objectives
- Build an interactive 3D simulation environment with randomly generated obstacles.
- Simulate realistic drone kinematics and sensors (GPS, IMU, LiDAR).
- Implement a 3D A* algorithm for global path planning.
- Train and integrate an AI/ML model (Random Forest) for local obstacle avoidance.
- Create a hybrid navigation system combining global planning and local AI safety overrides.
- Visualize the simulation comprehensively with a live dashboard.

## 4. Proposed System & Architecture
The system employs a Hybrid Controller that defaults to following a 3D A* global path. When the simulated LiDAR detects obstacles within a certain range, the AI/ML model takes over to execute local avoidance maneuvers. A final Safety Layer prevents the drone from entering a critical distance from any obstacle.

```
             ┌───────────────┐
             │ 3D Environment│
             └───────┬───────┘
                     │
         ┌───────────┴───────────┐
         │                       │
       GPS                      IMU
         │                       │
         └───────────┬───────────┘
                     │
                   LiDAR
                     │
                     ▼
            ┌─────────────────┐
            │ Sensor Fusion   │
            └────────┬────────┘
                     │
                     ▼
            ┌─────────────────┐
            │ State Estimator │
            └────────┬────────┘
                     │
          ┌──────────┴──────────┐
          ▼                     ▼
    ┌───────────┐        ┌────────────┐
    │ 3D A*     │        │ AI/ML      │
    │ Global    │        │ Navigation │
    │ Planner   │        └─────┬──────┘
    └─────┬─────┘              │
          └──────────┬─────────┘
                     ▼
             ┌──────────────┐
             │ Hybrid       │
             │ Controller   │
             └──────┬───────┘
                    ▼
             ┌──────────────┐
             │ Safety Layer │
             └──────┬───────┘
                    ▼
                ┌───────┐
                │ Drone │
                └───┬───┘
                    │
                    ▼
                 Sensors
                    │
                    └──── feedback
```

## 5. Technology Stack Explained
- **Python**: Core programming language.
- **Ursina Engine**: Chosen for lightweight, interactive, and Pythonic 3D visualization. It easily handles raycasting (LiDAR) and entity management.
- **NumPy**: Used extensively for vectors, matrices, distance calculations, and sensor noise simulation.
- **Pandas**: Used for logging simulation data, generating ML datasets, and analyzing sensor readings.
- **Scikit-Learn**: Used for training the Random Forest AI navigation model.

## 6. Sensor Explanations
- **LiDAR**: Simulates distance measurements by casting rays in multiple directions within the 3D environment. Crucial for the AI to "see" obstacles.
- **GPS & IMU**: Provide noisy measurements of position and orientation.
- **Sensor Fusion**: Combines GPS and IMU data to provide a smoothed estimate of the drone's state.

## 7. AI/ML Methodology
A Supervised Imitation Learning approach is used for local navigation. 
1. **Dataset Generation**: We simulate thousands of scenarios with LiDAR distances and goal directions. An expert rule-based policy labels each scenario with a safe action (FORWARD, LEFT, RIGHT, BRAKE, etc.).
2. **Model Training**: A Random Forest Classifier learns to map LiDAR features to the expert's actions. Random Forest is chosen for its robustness, fast inference time, and interpretability compared to deep reinforcement learning.

## 8. Setup & Execution

1. **Setup Environment**:
```cmd
setup.bat
```
*(Or manually: `python -m venv .venv`, activate it, and `pip install -r requirements.txt`)*

2. **Generate Training Data**:
```cmd
.venv\Scripts\activate
python scripts\generate_dataset.py
```

3. **Train AI Model**:
```cmd
python scripts\train.py
```

4. **Run Simulation**:
```cmd
run_simulation.bat
```
*(Or manually: `python scripts\run_simulation.py`)*

Press **ESC** to exit the simulation and save the log file.

## 9. Limitations & Future Improvements
- The current drone physics model is purely kinematic. A full rigid-body dynamics model with PID controllers for roll/pitch/yaw would increase realism.
- Sensor fusion uses a simplified weighted average. An Extended Kalman Filter (EKF) would provide better state estimation.
- The A* planner currently searches a simplified grid; RRT* might be more efficient for complex 3D environments.
