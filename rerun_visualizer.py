import rerun as rr
import numpy as np
import time

class RerunVisualizer:
    def __init__(self, orchestrator, headless=False):
        """
        Creates a high-performance 3D visualizer using Rerun.
        :param orchestrator: The MissionOrchestrator providing simulation state.
        :param headless: If True, disables spawning the Rerun viewer.
        """
        self.orchestrator = orchestrator
        self.headless = headless
        self.is_initialized = False

    def init_plot(self):
        rr.init("RudraNetra_Swarm", spawn=not self.headless)
        
        # Log the ground plane based on the map size if available
        fmap = self.orchestrator.fmap
        if fmap:
            # A large dark blue rectangle to represent the flood environment area
            cx, cy = fmap.size_x / 2, fmap.size_y / 2
            # Use points or boxes, a single box for the ground
            rr.log(
                "environment/ground",
                rr.Boxes3D(
                    centers=[[cx, cy, -0.5]],
                    half_sizes=[[fmap.size_x / 2, fmap.size_y / 2, 0.5]],
                    colors=[[20, 50, 100, 100]],
                    labels=["Ground Area"]
                ),
                static=True
            )
            
            # Log obstacles statically since they don't change
            ox, oy, oz = [], [], []
            half_sx, half_sy, half_sz = [], [], []
            colors = []
            
            h = 10.0 # arbitrary obstacle height
            res = fmap.resolution
            
            for i in range(fmap.num_cells_x):
                for j in range(fmap.num_cells_y):
                    if fmap.obstacle_layer[i, j] > 0.5:
                        x, y = fmap.grid_to_world(i, j)
                        ox.append(x)
                        oy.append(y)
                        oz.append(h / 2.0)
                        
                        half_sx.append(res / 2.0)
                        half_sy.append(res / 2.0)
                        half_sz.append(h / 2.0)
                        
                        # Check if it's a building or tree based on layers
                        if fmap.building_layer[i, j] > 0.5:
                            colors.append([150, 150, 150, 200]) # Grey buildings
                        else:
                            colors.append([100, 50, 50, 200]) # Dark red obstacles
            
            if ox:
                centers = np.column_stack((ox, oy, oz))
                half_sizes = np.column_stack((half_sx, half_sy, half_sz))
                rr.log(
                    "environment/obstacles",
                    rr.Boxes3D(
                        centers=centers,
                        half_sizes=half_sizes,
                        colors=colors
                    ),
                    static=True
                )
                
        self.is_initialized = True

    def _draw_regions(self):
        area_div = self.orchestrator.area_div
        assignment_manager = self.orchestrator.assignment_manager
        if not area_div or not assignment_manager: return
        
        cx, cy, cz = [], [], []
        ix, iy, iz = [], [], []
        
        for region in area_div.regions.values():
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
            rr.log("mission/completed_regions", rr.Points3D(np.column_stack((cx, cy, cz)), colors=[[0, 255, 0]], radii=1.0))
        if ix:
            rr.log("mission/incomplete_regions", rr.Points3D(np.column_stack((ix, iy, iz)), colors=[[255, 255, 0]], radii=1.0))

    def _draw_drones(self):
        swarm = self.orchestrator.swarm
        if not swarm: return
        
        dx, dy, dz = [], [], []
        colors = []
        radii = []
        labels = []
        
        for d in swarm.get_all_drones():
            dx.append(d.position[0])
            dy.append(d.position[1])
            dz.append(d.position[2])
            
            if getattr(d, 'status', '') == 'FAILED' or d.battery <= 0.0:
                colors.append([0, 0, 0, 255]) # Black for dead drones
            elif getattr(d, 'status', '') == 'RTB':
                colors.append([255, 100, 0, 255]) # Orange for returning to base
            else:
                colors.append([0, 150, 255, 255]) # Blue for active
                
            radii.append(2.0)
            labels.append(f"{d.drone_id} (Bat: {d.battery:.1f}%)")
            
        if dx:
            positions = np.column_stack((dx, dy, dz))
            rr.log("swarm/drones", rr.Points3D(positions, colors=colors, radii=radii, labels=labels))

    def _draw_paths(self):
        movement = self.orchestrator.movement
        if not movement: return
        
        strips = []
        colors = []
        
        for uav_id, active in movement.active_paths.items():
            path = active["path"]
            if not path or not path.waypoints: continue
            
            wps = path.waypoints
            if len(wps) > 1:
                strips.append(wps)
                if active.get("paused", False):
                    colors.append([255, 0, 0, 150]) # Red for paused/blocked
                else:
                    colors.append([0, 255, 0, 150]) # Green for active
                
        if strips:
            rr.log("swarm/paths", rr.LineStrips3D(strips, colors=colors))

    def update(self):
        if not self.is_initialized:
            self.init_plot()
            
        if self.headless:
            return
            
        rr.set_time_sequence("step", self.orchestrator.current_step)
        rr.set_time_seconds("sim_time", self.orchestrator.sim_time)
        
        self._draw_regions()
        self._draw_paths()
        self._draw_drones()
        
        # Log summary text
        summary = self.orchestrator.get_summary()
        status_text = (
            f"Mission: {summary['status']}\n"
            f"Regions Map: {summary['completed_regions']}/{summary['total_regions']} "
            f"({summary['coverage_percentage']:.1f}%)\n"
            f"Conflicts Avoided: {summary['collisions_avoided']}\n"
            f"Planning Failures: {summary['planning_failures']}\n"
            f"Active UAVs: {summary['eligible_uavs']}"
        )
        rr.log("mission/status_panel", rr.TextDocument(status_text))
        
        # Add a tiny delay to simulate real-time visualization update like matplotlib's pause
        time.sleep(0.05)

    def close(self):
        # Rerun doesn't need explicit teardown, but we can disconnect if needed
        pass
