import matplotlib.pyplot as plt
import matplotlib.patches as patches
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.swarm import Swarm
from simulation.environment import FloodEnvironment
from mapping.flood_risk_map import FloodRiskMap
from planning.area_division import AreaDivision
from planning.assignment_manager import AssignmentManager

def visualize():
    env = FloodEnvironment()
    risk_map = FloodRiskMap(env)
    swarm = Swarm(number_of_drones=5)
    
    # Position UAVs
    drones = swarm.get_all_drones()
    for i, d in enumerate(drones):
        d.position = [(i + 1) * 30.0, (i % 3 + 1) * 40.0, 10.0]
        
    area_div = AreaDivision(risk_map)
    area_div.generate_regions()
    
    manager = AssignmentManager(swarm, area_div)
    manager.assign_regions()
    
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(0, env.size_x)
    ax.set_ylim(0, env.size_y)
    
    # Colors for drones
    colors = ['r', 'g', 'b', 'c', 'm']
    drone_colors = {d.drone_id: colors[i % len(colors)] for i, d in enumerate(drones)}
    
    for r in area_div.get_all_regions().values():
        x = r["x_min"]
        y = r["y_min"]
        w = r["x_max"] - r["x_min"]
        h = r["y_max"] - r["y_min"]
        
        edgecolor = 'black'
        facecolor = 'none'
        alpha = 0.5
        
        if r["status"] == "ASSIGNED":
            facecolor = drone_colors.get(r["assigned_drone_id"], 'gray')
            alpha = 0.3
            
        rect = patches.Rectangle((x, y), w, h, linewidth=1, edgecolor=edgecolor, facecolor=facecolor, alpha=alpha)
        ax.add_patch(rect)
        
        # Plot priority
        ax.text(r["center_x"], r["center_y"], f"{r['priority']:.2f}", ha='center', va='center', fontsize=8)
        
    # Plot UAVs
    for d in drones:
        ax.scatter(d.position[0], d.position[1], c=drone_colors[d.drone_id], s=100, marker='^', label=d.drone_id)
        
    ax.set_title("Swarm Area Division and Assignments")
    ax.set_xlabel("X (m)")
    ax.set_ylabel("Y (m)")
    ax.legend()
    
    print("Close the plot window to continue...")
    plt.show()

if __name__ == '__main__':
    visualize()
