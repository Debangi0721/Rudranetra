import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

class LiveVisualizer:
    def __init__(self, orchestrator, update_interval=0.1, headless=False):
        """
        Creates a live 3D visualizer using Matplotlib.
        :param orchestrator: The MissionOrchestrator providing simulation state.
        :param update_interval: Pause interval for rendering frames.
        :param headless: If True, disables actual GUI rendering (useful for CI/CD tests).
        """
        self.orchestrator = orchestrator
        self.update_interval = update_interval
        self.headless = headless
        self.fig = None
        self.ax = None
        self.is_initialized = False

    def init_plot(self):
        if self.headless:
            self.is_initialized = True
            return
            
        plt.ion()
        self.fig = plt.figure(figsize=(10, 8))
        self.ax = self.fig.add_subplot(111, projection='3d')
        self.ax.set_title("RudraNetra - 3D Swarm Visualization")
        self.is_initialized = True
        
    def _draw_environment(self):
        fmap = self.orchestrator.fmap
        if not fmap: return
        
        ox, oy, oz = [], [], []
        
        # Ground truth obstacles
        for i in range(fmap.num_cells_x):
            for j in range(fmap.num_cells_y):
                if fmap.obstacle_layer[i, j] > 0.5:
                    wx, wy = fmap.grid_to_world(i, j)
                    ox.append(wx)
                    oy.append(wy)
                    oz.append(5.0) # Arbitrary visualization height for obstacles
                    
        if ox:
            self.ax.scatter(ox, oy, oz, c='red', marker='s', alpha=0.3, label='Obstacles')
            
    def _draw_regions(self):
        area_div = self.orchestrator.area_div
        assignment_manager = self.orchestrator.assignment_manager
        if not area_div or not assignment_manager: return
        
        cx, cy, cz = [], [], []
        ix, iy, iz = [], [], []
        
        for region in area_div.regions.values():
            r_id = region["region_id"]
            x, y = region["center_x"], region["center_y"]
            coverage = region.get("covered_fraction", 0.0)
            
            if coverage >= 1.0:
                cx.append(x)
                cy.append(y)
                cz.append(0.5)
            else:
                ix.append(x)
                iy.append(y)
                iz.append(0.5)
                
        if cx:
            self.ax.scatter(cx, cy, cz, c='green', marker='o', alpha=0.5, label='Completed Regions')
        if ix:
            self.ax.scatter(ix, iy, iz, c='yellow', marker='o', alpha=0.5, label='Incomplete Regions')

    def _draw_drones(self):
        swarm = self.orchestrator.swarm
        if not swarm: return
        
        dx, dy, dz = [], [], []
        for d in swarm.get_all_drones():
            # Check availability
            if getattr(d, 'status', '') == 'FAILED' or d.battery <= 0.0:
                c = 'black'
            else:
                c = 'blue'
                
            dx.append(d.position[0])
            dy.append(d.position[1])
            dz.append(d.position[2])
            
            # Label
            label = f"{d.drone_id}\n{d.battery:.1f}%"
            self.ax.text(d.position[0], d.position[1], d.position[2] + 2.0, label, color=c, fontsize=8)
            
        if dx:
            self.ax.scatter(dx, dy, dz, c='blue', marker='^', s=100, label='Active UAVs', depthshade=False)

    def _draw_paths(self):
        movement = self.orchestrator.movement
        if not movement: return
        
        drawn = False
        for uav_id, active in movement.active_paths.items():
            path = active["path"]
            if not path or not path.waypoints: continue
            
            wps = path.waypoints
            px = [wp[0] for wp in wps]
            py = [wp[1] for wp in wps]
            pz = [wp[2] for wp in wps]
            
            # Use red if paused/blocked, green if active
            color = 'red' if active.get("paused", False) else 'green'
            self.ax.plot(px, py, pz, color=color, linestyle='--', alpha=0.5, label='Planned Path' if not drawn else "")
            drawn = True
            
    def _draw_status_panel(self):
        summary = self.orchestrator.get_summary()
        status_text = (
            f"Mission: {summary['status']}\n"
            f"Step: {summary['total_steps']} | Time: {summary['sim_time']:.1f}s\n"
            f"Regions Map: {summary['completed_regions']}/{summary['total_regions']} "
            f"({summary['coverage_percentage']:.1f}%)\n"
            f"Conflicts Avoided: {summary['collisions_avoided']}\n"
            f"Planning Failures: {summary['planning_failures']}\n"
            f"Active UAVs: {summary['eligible_uavs']}"
        )
        self.ax.text2D(0.02, 0.98, status_text, transform=self.ax.transAxes, 
                       fontsize=9, verticalalignment='top', 
                       bbox=dict(boxstyle='round', facecolor='white', alpha=0.9))

    def update(self):
        if not self.is_initialized:
            self.init_plot()
            
        if self.headless:
            # Just do nothing but confirm it works without crashing
            return
            
        if not self.ax: return
        self.ax.clear()
        
        # Extract environment bounds from map if available
        fmap = self.orchestrator.fmap
        if fmap:
            max_x = fmap.size_x
            max_y = fmap.size_y
            self.ax.set_xlim(0, max_x)
            self.ax.set_ylim(0, max_y)
            self.ax.set_zlim(0, 30) # Fixed altitude view
        
        self.ax.set_xlabel("X (m)")
        self.ax.set_ylabel("Y (m)")
        self.ax.set_zlabel("Z (Altitude m)")
        
        # Render layers
        self._draw_environment()
        self._draw_regions()
        self._draw_paths()
        self._draw_drones()
        self._draw_status_panel()
        
        # Legend (filter duplicates)
        handles, labels = self.ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        if by_label:
            self.ax.legend(by_label.values(), by_label.keys(), loc='center left', bbox_to_anchor=(1, 0.5))
            
        plt.pause(self.update_interval)

    def close(self):
        if self.headless:
            self.is_initialized = False
            return
            
        if self.is_initialized:
            plt.ioff()
            plt.close(self.fig)
            self.is_initialized = False
