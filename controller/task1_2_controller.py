import random

from swarmy.actuation import Actuation


class BraitenbergController(Actuation):
    """
    Braitenberg vehicle controller with differential drive.
    Supports two behaviors: 'aggressor' and 'fear'.
    """

    def __init__(self, agent, config):
        super().__init__(agent)
        self.config = config
        self.init_pos = True

        # Get kinematic limits from world
        self.max_velocity = self.agent.environment.max_speed
        self.max_angle_velocity = self.agent.environment.max_turn_rate

        # Braitenberg behavior type: 'aggressor' or 'fear'
        self.behavior = self.config.get("braitenberg_behavior", "aggressor")

        # Proportionality constant for sensor -> wheel velocity
        self.k_motor = self.config.get("motor_gain", 5.0)

        # Constant for heading change: Δφ = c(v_r - v_l)
        self.c_turn = self.config.get("turn_constant", 0.5)

        # Base velocity for exploration when no light detected
        self.base_velocity = min(
            self.config.get("default_velocity", 2), self.max_velocity
        )

        # Escape state (for bumper collisions)
        self.escape_counter = 0
        self.turn_counter = 0
        self.turn_direction = 1

    def controller(self):
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False

        self.agent.trajectory.append(self.agent.get_position())

        sensor_data = self.agent.get_perception()
        bumper_hit = sensor_data[1] == 1
        left_light, right_light = sensor_data[2]

        # Braitenberg differential drive logic
        if self.behavior == "aggressor":
            v_left = self.k_motor * right_light
            v_right = self.k_motor * left_light
        elif self.behavior == "fear":
            v_left = self.k_motor * left_light
            v_right = self.k_motor * right_light
        else:
            v_left = self.base_velocity
            v_right = self.base_velocity

        v_left += self.base_velocity * 0.3
        v_right += self.base_velocity * 0.3

        print(
            f"Behavior: {self.behavior} | Left light: {left_light:.2f} | Right light: {right_light:.2f} | v_left: {v_left:.2f} | v_right: {v_right:.2f}"
        )

        # Clamp wheel velocities
        v_left = self.agent.environment.clamp_velocity(v_left)
        v_right = self.agent.environment.clamp_velocity(v_right)

        # Calculate heading change: Δφ = c(v_r - v_l)
        delta_phi = self.c_turn * (v_right - v_left)
        delta_phi = self.agent.environment.clamp_turn_rate(delta_phi)

        # Calculate linear velocity (average of wheels)
        linear_vel = (v_left + v_right) / 2.0
        linear_vel = self.agent.environment.clamp_velocity(linear_vel)

        # Execute motion
        self.stepForward(linear_vel)

        # Convert delta_phi to integer before turning
        if delta_phi > 0:
            self.turn_left(round(abs(delta_phi)))
        elif delta_phi < 0:
            self.turn_right(round(abs(delta_phi)))

    def _handle_collision(self):
        """Simple collision avoidance: turn and reverse"""
        angle_vel = self.agent.environment.clamp_turn_rate(self.max_angle_velocity)
        linear_vel = self.agent.environment.clamp_velocity(self.base_velocity)

        # Turning phase
        if self.turn_counter < 6:
            if self.turn_counter == 0:
                self.turn_direction = random.choice([-1, 1])
            # Ensure integer angle
            self.turn_right(round(self.turn_direction * angle_vel * 3))
            self.turn_counter += 1
            return

        # Reverse phase
        if self.escape_counter == 0:
            self.escape_counter = random.randint(4, 7)

        if self.escape_counter > 0:
            self.stepBackward(linear_vel)
            # Ensure integer angle
            self.turn_right(round(self.turn_direction * angle_vel * 2))
            self.escape_counter -= 1
            if self.escape_counter == 0:
                self.turn_counter = 0

    def torus(self):
        """Wrap position on torus boundaries"""
        x, y, gamma = self.agent.get_position()
        wrapped = self.agent.environment.wrap_position((x, y))
        if wrapped != (x, y):
            self.agent.set_position(wrapped[0], wrapped[1], gamma)
