import numpy as np

from swarmy.actuation import Actuation


class DirectGradientController(Actuation):
    """
    Controller that reacts directly to the gradient of the potential field.
    Velocity is determined directly by the gradient.
    """

    def __init__(self, agent, config):
        super().__init__(agent)
        self.config = config
        self.init_pos = True

        t32 = config.get("task32", {})
        self.dt = float(t32.get("dt", 1.0))
        self.velocity_scale = float(t32.get("direct_velocity_scale", 5000.0))
        self.max_velocity = float(t32.get("direct_max_velocity", 10.0))

        # Trajectory tracking
        self.trajectory = []

    def controller(self):
        """
        Direct gradient control:
        v_x(t) = ∂P/∂x
        v_y(t) = ∂P/∂y
        """
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False

        # Get current position
        x, y, angle = self.agent.get_position()

        # Store trajectory
        self.trajectory.append((x, y))

        # Get gradient from potential field
        env = self.agent.environment
        grad_x, grad_y = env.get_gradient(x, y)

        # Velocity is directly determined by gradient (negative for descent)
        v_x = -grad_x * self.velocity_scale
        v_y = -grad_y * self.velocity_scale

        # Normalize if velocity is too large
        velocity_magnitude = np.sqrt(v_x**2 + v_y**2)
        if velocity_magnitude > self.max_velocity:
            v_x = v_x / velocity_magnitude * self.max_velocity
            v_y = v_y / velocity_magnitude * self.max_velocity

        # Calculate displacement
        delta_x = v_x * self.dt
        delta_y = v_y * self.dt

        # Update position
        new_x = x + delta_x
        new_y = y + delta_y

        # Calculate new heading from velocity direction
        if velocity_magnitude > 0.1:
            new_angle = int(np.degrees(np.arctan2(v_x, v_y)) % 360)
        else:
            new_angle = int(angle)

        self.agent.set_position(new_x, new_y, new_angle)

        # Visualize gradient vector
        if self.config.get("rendering", 1) == 1:
            arrow_scale = 20
            end_x = x + grad_x * arrow_scale
            end_y = y + grad_y * arrow_scale
            env.add_dynamic_line_object([(0, 255, 0), (x, y), (end_x, end_y)])

    def torus(self):
        """
        Keep robot within bounds (no torus wrapping)
        """
        x, y, angle = self.agent.get_position()

        # Clamp to environment bounds
        x = np.clip(x, 10, self.agent.environment.width - 10)
        y = np.clip(y, 10, self.agent.environment.height - 10)

        self.agent.set_position(x, y, int(angle))
