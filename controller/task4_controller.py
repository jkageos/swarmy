import random

from swarmy.actuation import Actuation


class EvolvedController(Actuation):
    """
    Controller with evolved linear mappings from sensors to wheel velocities,
    but always applies rule-based obstacle avoidance first.
    """

    def __init__(self, agent, config, genome=None):
        super().__init__(agent)
        self.config = config
        self.init_pos = True

        # Kinematic limits
        self.max_velocity = self.agent.environment.max_speed
        self.max_angle_velocity = self.agent.environment.max_turn_rate

        # Genome: [(m0, c0), (m1, c1), (m2, c2)]
        if genome is None:
            genome = []
            for _ in range(3):
                m = random.uniform(-5, 5)
                c = random.uniform(0.5, 3.0)
                genome.append((m, c))
        self.genome = genome

        # Turn constant for differential drive
        self.c_turn = self.config.get("turn_constant", 0.5)

        # Rule-based thresholds
        self.obstacle_threshold = 0.3
        self.critical_threshold = 0.6
        self.base_velocity = self.config.get("default_velocity", 2)
        self.turn_velocity = self.config.get("default_angle_velocity", 3)

        # Exploration state
        self.exploration_turn_counter = 0
        self.preferred_turn_direction = random.choice([-1, 1])

    def controller(self):
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False

        # Always record position for trajectory
        self.agent.trajectory.append(self.agent.get_position())

        # Get sensor readings: (left, front, right)
        sensor_data = self.agent.get_perception()
        s_left = sensor_data[1][0]
        s_middle = sensor_data[1][1]
        s_right = sensor_data[1][2]

        # --- Rule-based obstacle avoidance ---
        if s_middle > self.critical_threshold:
            if s_left < s_right:
                self.turn_left(self.turn_velocity * 4)
            else:
                self.turn_right(self.turn_velocity * 4)
            self.stepForward(self.base_velocity * 0.3)
            return

        if s_middle > self.obstacle_threshold:
            if s_left < s_right:
                self.turn_left(self.turn_velocity * 2)
            else:
                self.turn_right(self.turn_velocity * 2)
            self.stepForward(self.base_velocity * 0.5)
            return

        if s_left > self.obstacle_threshold:
            self.turn_right(self.turn_velocity)
            self.stepForward(self.base_velocity * 0.7)
            return

        if s_right > self.obstacle_threshold:
            self.turn_left(self.turn_velocity)
            self.stepForward(self.base_velocity * 0.7)
            return

        # --- Evolved genome for exploration ---
        m0, c0 = self.genome[0]
        m1, c1 = self.genome[1]
        m2, c2 = self.genome[2]

        v_left = m0 * (1.0 - s_left) + c0
        v_right = m1 * (1.0 - s_right) + c1 + m2 * (1.0 - s_middle) + c2

        v_left = self.agent.environment.clamp_velocity(v_left)
        v_right = self.agent.environment.clamp_velocity(v_right)

        linear_vel = (v_left + v_right) / 2.0
        delta_phi = self.c_turn * (v_right - v_left)
        delta_phi = self.agent.environment.clamp_turn_rate(delta_phi)

        if abs(linear_vel) > 0.1:
            if linear_vel > 0:
                self.stepForward(linear_vel)
            else:
                self.stepBackward(abs(linear_vel))

        if abs(delta_phi) > 0.1:
            if delta_phi > 0:
                self.turn_left(round(abs(delta_phi)))
            else:
                self.turn_right(round(abs(delta_phi)))

    def torus(self):
        x, y, gamma = self.agent.get_position()
        margin = 20
        x = max(margin, min(x, self.config["world_width"] - margin))
        y = max(margin, min(y, self.config["world_height"] - margin))
        self.agent.set_position(x, y, gamma)
