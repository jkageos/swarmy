import random

from swarmy.actuation import Actuation


class MyController(Actuation):
    def __init__(self, agent, config):
        super().__init__(agent)
        """
        self.linear_velocity = <your value>
        self.angle_velocity  = <your value>
        """
        self.config = config
        self.init_pos = True
        self.linear_velocity = self.config["default_velocity"]
        self.angle_velocity = self.config["default_angle_velocity"]

        # Escape / recovery state
        self.escape_counter = 0
        self.turn_counter = 0
        self.stuck_counter = 0
        self.was_reversing = False
        self.turn_direction = 1

        # Tunable (with fallbacks if not in config)
        self.turn_frames = self.config.get("escape_turn_frames", 6)
        self.rev_min = self.config.get("escape_reverse_min", 4)
        self.rev_max = self.config.get("escape_reverse_max", 7)
        self.max_stuck = self.config.get("max_stuck_frames", 30)

        # Boundary pre-compute
        wall_thickness = 10
        robot_radius = 20
        margin = wall_thickness + robot_radius
        self.min_x = margin
        self.max_x = self.config["world_width"] - margin
        self.min_y = margin
        self.max_y = self.config["world_height"] - margin

    def is_near_boundary(self):
        x, y, _ = self.agent.get_position()
        tolerance = 15
        return (
            x <= self.min_x + tolerance
            or x >= self.max_x - tolerance
            or y <= self.min_y + tolerance
            or y >= self.max_y - tolerance
        )

    def controller(self):
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False

        sensor_data = self.agent.get_perception()
        bumper_hit = sensor_data[1] == 1
        boundary_hit = self.is_near_boundary()
        collision = bumper_hit or boundary_hit

        # Abort reverse immediately if collision persists behind
        if self.was_reversing and collision:
            self.escape_counter = 0
            self.turn_counter = 0

        if collision:
            self.stuck_counter += 1

            # Stuck rescue
            if self.stuck_counter > self.max_stuck:
                self.stepBackward(self.linear_velocity * 2)
                self.turn_right(self.angle_velocity * 6)  # integer multiplier
                self.was_reversing = True
                if self.stuck_counter > self.max_stuck + 10:
                    self.stuck_counter = 0
                    self.turn_counter = 0
                    self.escape_counter = 0
                    self.was_reversing = False
                return

            # Turning phase
            if self.turn_counter < self.turn_frames:
                if self.turn_counter == 0:
                    self.turn_direction = random.choice([-1, 1])
                self.turn_right(self.turn_direction * self.angle_velocity * 3)
                self.turn_counter += 1
                self.was_reversing = False
                return

            # Reverse phase (short & interruptible)
            if self.escape_counter == 0:
                self.escape_counter = random.randint(self.rev_min, self.rev_max)

            if self.escape_counter > 0:
                # Re-check collision every frame to prevent tunneling
                if bumper_hit and self.was_reversing:
                    # Stop reverse immediately, restart turn phase
                    self.escape_counter = 0
                    self.turn_counter = 0
                    self.was_reversing = False
                    return
                self.stepBackward(self.linear_velocity)
                self.turn_right(self.turn_direction * self.angle_velocity * 3)
                self.was_reversing = True
                self.escape_counter -= 1
                if self.escape_counter == 0:
                    self.turn_counter = 0
                return
        else:
            # Clear escape state
            self.escape_counter = 0
            self.turn_counter = 0
            self.stuck_counter = 0
            self.was_reversing = False

        # Normal exploration forward
        self.stepForward(self.linear_velocity)
        if random.random() < 0.08:
            delta = random.randint(-2, 2) * self.angle_velocity
            if delta > 0:
                self.turn_left(delta)
            elif delta < 0:
                self.turn_right(-delta)

    def torus(self):
        x, y, ang = self.agent.get_position()
        cx = max(self.min_x, min(x, self.max_x))
        cy = max(self.min_y, min(y, self.max_y))
        if cx != x or cy != y:
            self.agent.set_position(cx, cy, ang)
