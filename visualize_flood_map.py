import matplotlib.pyplot as plt
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.environment import FloodEnvironment
from mapping.flood_risk_map import FloodRiskMap

def visualize():
    env = FloodEnvironment()
    fmap = FloodRiskMap(env)
    
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    
    # 1. Flood Depth Map
    cax1 = axs[0].imshow(fmap.water_depth_layer.T, origin='lower', cmap='Blues', 
                         extent=[0, fmap.size_x, 0, fmap.size_y])
    axs[0].set_title('Flood Depth Map')
    axs[0].set_xlabel('X (m)')
    axs[0].set_ylabel('Y (m)')
    fig.colorbar(cax1, ax=axs[0], label='Depth (m)')
    
    # 2. Flood Risk Map
    cax2 = axs[1].imshow(fmap.flood_risk_layer.T, origin='lower', cmap='Reds', vmin=0, vmax=1,
                         extent=[0, fmap.size_x, 0, fmap.size_y])
    axs[1].set_title('Flood Risk Map')
    axs[1].set_xlabel('X (m)')
    fig.colorbar(cax2, ax=axs[1], label='Risk (0-1)')
    
    # 3. Priority Map
    cax3 = axs[2].imshow(fmap.priority_layer.T, origin='lower', cmap='magma', vmin=0, vmax=1,
                         extent=[0, fmap.size_x, 0, fmap.size_y])
    axs[2].set_title('Priority Map')
    axs[2].set_xlabel('X (m)')
    fig.colorbar(cax3, ax=axs[2], label='Priority (0-1)')
    
    plt.tight_layout()
    print("Close the plot window to continue...")
    plt.show()

if __name__ == '__main__':
    visualize()
