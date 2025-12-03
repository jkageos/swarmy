import numpy as np

from swarmy.actuation import Actuation


class IndirectGradientController(Actuation):
    """
    Controller that reacts indirectly to the gradient via acceleration.
    The gradient determines acceleration, and velocity has memory.
    """

    def __init__(self, agent, config):
        super().__init__(agent)
        self.config = config
        self.init_pos = True

        # Parameters for indirect control
        self.dt = 1.0  # Integration time step
        self.c = 0.95  # Discount factor (memory of former directions)
        self.acceleration_scale = 1000.0  # Scale for gradient acceleration
        self.max_velocity = 10.0  # Maximum velocity magnitude

        # State variables
        self.v_x = 0.0  # Current velocity in x
        self.v_y = 0.0  # Current velocity in y

        # Trajectory tracking
        self.trajectory = []

    def controller(self):
        """
        Indirect gradient control with memory:
        Δv_x(t) = c * v_x(t-Δt) + ∂P/∂x
        Δv_y(t) = c * v_y(t-Δt) + ∂P/∂y
        Then normalize to prevent velocity explosion
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

        # Update velocity with memory and acceleration
        # v(t) = c * v(t-1) + acceleration
        self.v_x = self.c * self.v_x - grad_x * self.acceleration_scale
        self.v_y = self.c * self.v_y - grad_y * self.acceleration_scale

        # Normalize velocity to prevent explosion
        velocity_magnitude = np.sqrt(self.v_x**2 + self.v_y**2)

        if velocity_magnitude > 0.01:
            # Normalize to unit vector, then scale to max velocity
            scale = min(self.max_velocity, velocity_magnitude)
            self.v_x = (self.v_x / velocity_magnitude) * scale
            self.v_y = (self.v_y / velocity_magnitude) * scale

        # Calculate displacement
        delta_x = self.v_x * self.dt
        delta_y = self.v_y * self.dt

        # Update position
        new_x = x + delta_x
        new_y = y + delta_y

        # Calculate new heading from velocity direction
        if velocity_magnitude > 0.1:
            new_angle = int(np.degrees(np.arctan2(self.v_x, self.v_y)) % 360)
        else:
            new_angle = int(angle)

        self.agent.set_position(new_x, new_y, new_angle)

        # Visualize velocity vector
        if self.config.get("rendering", 1) == 1:
            arrow_scale = 10
            end_x = x + self.v_x * arrow_scale
            end_y = y + self.v_y * arrow_scale
            env.add_dynamic_line_object([(255, 255, 0), (x, y), (end_x, end_y)])

    def torus(self):
        """
        Keep robot within bounds and handle collisions with damping
        """
        x, y, angle = self.agent.get_position()

        # Check bounds and damp velocity if hitting boundary
        if x <= 10 or x >= self.agent.environment.width - 10:
            self.v_x *= -0.5  # Reverse and damp
            x = np.clip(x, 10, self.agent.environment.width - 10)

        if y <= 10 or y >= self.agent.environment.height - 10:
            self.v_y *= -0.5  # Reverse and damp
            y = np.clip(y, 10, self.agent.environment.height - 10)

        self.agent.set_position(x, y, int(angle))
