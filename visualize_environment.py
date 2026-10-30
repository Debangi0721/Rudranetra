import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from simulation.environment import FloodEnvironment
import config

def visualize():
    env = FloodEnvironment()
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')
    
    # Draw Ground & Water
    x = np.linspace(0, env.size_x, 50)
    y = np.linspace(0, env.size_y, 50)
    X, Y = np.meshgrid(x, y)
    
    Z_terrain = np.zeros_like(X)
    Z_water = np.zeros_like(X)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z_terrain[i, j] = env.get_terrain_height(X[i, j], Y[i, j])
            Z_water[i, j] = env.get_flood_depth(X[i, j], Y[i, j]) + Z_terrain[i, j]
            
    # Terrain surface
    ax.plot_surface(X, Y, Z_terrain, color='saddlebrown', alpha=0.5)
    # Water surface
    ax.plot_surface(X, Y, Z_water, color='blue', alpha=0.3)
    
    # Draw Buildings
    for b in env.get_buildings():
        ax.bar3d(b['x'] - b['width']/2, b['y'] - b['length']/2, 0, b['width'], b['length'], b['height'], color='gray', alpha=0.8)
        
    # Draw Trees (Scatter)
    trees = env.get_trees()
    if trees:
        tx = [t['x'] for t in trees]
        ty = [t['y'] for t in trees]
        tz = [env.get_terrain_height(t['x'], t['y']) + t['height']/2 for t in trees]
        ax.scatter(tx, ty, tz, c='green', marker='^', s=50, label='Trees')
        
    # Draw Poles (Scatter)
    poles = env.get_poles()
    if poles:
        px = [p['x'] for p in poles]
        py = [p['y'] for p in poles]
        pz = [env.get_terrain_height(p['x'], p['y']) + p['height']/2 for p in poles]
        ax.scatter(px, py, pz, c='black', marker='|', s=50, label='Poles')
        
    # Plot formatting
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Altitude')
    ax.set_title('3D Flood Environment')
    ax.set_xlim(0, env.size_x)
    ax.set_ylim(0, env.size_y)
    ax.set_zlim(0, 40)
    plt.legend()
    
    print("Close the plot window to continue...")
    plt.show()

if __name__ == '__main__':
    visualize()
