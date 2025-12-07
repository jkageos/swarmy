import math
import random

import numpy as np

from swarmy.actuation import Actuation


class FlockingController(Actuation):
    """
    Reynolds-style flocking controller with separation, alignment, and cohesion.
    Operates in toroidal space with periodic boundary conditions.
    """

    def __init__(self, agent, config):
        super().__init__(agent)
        self.config = config
        self.init_pos = True

        # Flocking parameters (from config.yaml)
        self.rs = float(config["separation_radius"])
        self.ra = float(config["alignment_radius"])
        self.rc = float(config["cohesion_radius"])

        self.ws = float(config["separation_weight"])
        self.wa = float(config["alignment_weight"])
        self.wc = float(config["cohesion_weight"])

        self.v0 = float(config["flock_speed"])
        self.eta = float(config.get("heading_noise", 0.0))

        # Minimum safe distance (optional override in config)
        self.min_distance = float(config.get("min_separation_distance", 35.0))

        # State variables
        self.velocity = np.array([0.0, 0.0])
        self.trajectory = []

    def controller(self):
        """
        Main flocking control loop.
        Computes separation, alignment, and cohesion forces.
        """
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False
            # Initialize with random velocity matching the heading
            x, y, angle = self.agent.get_position()
            angle_rad = math.radians(angle)
            self.velocity = np.array(
                [math.sin(angle_rad) * self.v0, math.cos(angle_rad) * self.v0]
            )

        # Get perception data (neighbors)
        sensor_data = self.agent.get_perception()
        neighbors = sensor_data[1]

        x, y, angle = self.agent.get_position()
        self.trajectory.append((x, y))

        # Initialize force vectors
        sep = np.array([0.0, 0.0])
        ali = np.array([0.0, 0.0])
        coh = np.array([0.0, 0.0])

        n_sep = 0
        n_align = 0
        n_coh = 0

        # Track if we're in danger zone (too close to another agent)
        danger_zone = False

        # Compute forces from neighbors
        for delta, neighbor_vel, dist in neighbors:
            if dist < 1e-3:
                continue

            # CRITICAL: Emergency separation for very close neighbors
            if dist < self.min_distance:
                # EXTREMELY strong repulsion when too close
                emergency_strength = 10.0 / (dist + 1.0)
                sep -= (delta / (dist + 1e-6)) * emergency_strength
                danger_zone = True
                n_sep += 1
            # Normal separation
            elif dist < self.rs:
                # Strong separation: inverse square law with extra boost
                separation_strength = 5.0 / (dist**2 + 5.0)
                sep -= (delta / dist) * separation_strength
                n_sep += 1

            # Alignment: only if not too close
            if dist < self.ra and dist > self.min_distance:
                ali += neighbor_vel
                n_align += 1

            # Cohesion: only for distant neighbors
            if dist < self.rc and dist > self.rs:
                coh += delta
                n_coh += 1

        # Process separation (most important!)
        if n_sep > 0:
            sep = sep / n_sep
            # In danger zone: separation dominates completely
            if danger_zone:
                sep_mag = np.linalg.norm(sep)
                if sep_mag > 1e-6:
                    # Max separation force in danger zone
                    sep = (sep / sep_mag) * 15.0
            else:
                # Normal separation boost
                sep_mag = np.linalg.norm(sep)
                if sep_mag > 1e-6:
                    sep = (sep / sep_mag) * min(sep_mag * 3.0, 10.0)

        # Process alignment
        if n_align > 0:
            ali = ali / n_align
            ali = ali - self.velocity
            ali_mag = np.linalg.norm(ali)
            if ali_mag > 1e-6:
                ali = (ali / ali_mag) * min(ali_mag, 2.0)

        # Process cohesion
        if n_coh > 0:
            center_dir = coh / n_coh
            coh_mag = np.linalg.norm(center_dir)
            if coh_mag > 1e-6:
                coh = (center_dir / coh_mag) * min(coh_mag * 0.3, 0.8)
            else:
                coh = np.array([0.0, 0.0])

        # Weighted sum of forces
        # In danger zone, ONLY separation matters
        if danger_zone:
            v_desired = sep  # Pure separation
        else:
            v_desired = self.ws * sep + self.wa * ali + self.wc * coh

        # If no steering forces, maintain current velocity
        if np.linalg.norm(v_desired) < 1e-6:
            v_desired = self.velocity
        else:
            # Add desired steering to current velocity
            v_desired = self.velocity + v_desired

        # Add heading noise BEFORE normalization
        if self.eta > 0 and not danger_zone:  # No noise in danger zone
            v_desired = self._add_heading_noise(v_desired, self.eta)

        # Normalize to constant speed
        v_mag = np.linalg.norm(v_desired)
        if v_mag > 1e-6:
            self.velocity = (v_desired / v_mag) * self.v0
        else:
            self.velocity = self.velocity

        # Update position using velocity
        new_x = x + self.velocity[0]
        new_y = y + self.velocity[1]

        # Calculate heading from velocity
        new_angle = math.degrees(math.atan2(self.velocity[0], self.velocity[1])) % 360

        self.agent.set_position(new_x, new_y, int(new_angle))

        # Visualize forces for debugging
        if self.config.get("rendering", 1) == 1 and self.config.get(
            "show_velocity", False
        ):
            # Velocity vector (yellow)
            arrow_scale = 10
            end_x = x + self.velocity[0] * arrow_scale
            end_y = y + self.velocity[1] * arrow_scale
            self.agent.environment.add_dynamic_line_object(
                [(255, 255, 0), (int(x), int(y)), (int(end_x), int(end_y))]
            )

            # Separation vector (red) if active
            if np.linalg.norm(sep) > 0.1:
                sep_scale = 20 if danger_zone else 15
                sep_end_x = x + sep[0] * sep_scale
                sep_end_y = y + sep[1] * sep_scale
                color = (255, 0, 0) if danger_zone else (255, 100, 0)
                self.agent.environment.add_dynamic_line_object(
                    [color, (int(x), int(y)), (int(sep_end_x), int(sep_end_y))]
                )

    def _add_heading_noise(self, velocity, eta):
        """
        Add random angular perturbation to velocity.
        """
        angle = math.atan2(velocity[0], velocity[1])
        noise = random.uniform(-eta / 2.0, eta / 2.0)
        angle = angle + noise

        speed = np.linalg.norm(velocity)
        vx = speed * math.sin(angle)
        vy = speed * math.cos(angle)

        return np.array([vx, vy])

    def torus(self):
        """
        Periodic boundary conditions: wrap around toroidal space.
        """
        x, y, angle = self.agent.get_position()

        # Wrap x coordinate
        if x < 0:
            x = self.agent.environment.width + x
        elif x >= self.agent.environment.width:
            x = x - self.agent.environment.width

        # Wrap y coordinate
        if y < 0:
            y = self.agent.environment.height + y
        elif y >= self.agent.environment.height:
            y = y - self.agent.environment.height

        self.agent.set_position(x, y, angle)
