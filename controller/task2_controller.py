import random

from swarmy.actuation import Actuation


class RuleBasedController(Actuation):
    """
    Simple rule-based controller for obstacle avoidance and exploration.
    Uses three proximity sensors (left, front, right) to navigate.
    """

    def __init__(self, agent, config):
        super().__init__(agent)
        self.config = config
        self.init_pos = True

        # Motion parameters
        self.base_velocity = self.config.get("default_velocity", 2)
        self.turn_velocity = self.config.get("default_angle_velocity", 3)

        # Sensor thresholds
        self.obstacle_threshold = (
            0.3  # Sensor value above which we consider obstacle close
        )
        self.critical_threshold = 0.6  # Very close obstacle

        # State for smooth exploration
        self.exploration_turn_counter = 0
        self.preferred_turn_direction = random.choice([-1, 1])

    def controller(self):
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False

        # Store trajectory
        self.agent.trajectory.append(self.agent.get_position())

        # Get sensor readings: (left, front, right)
        sensor_data = self.agent.get_perception()
        left_prox = sensor_data[1][0]
        front_prox = sensor_data[1][1]
        right_prox = sensor_data[1][2]

        # Rule-based control logic
        # Rule 1: Critical obstacle straight ahead - emergency stop and turn
        if front_prox > self.critical_threshold:
            # Strong obstacle ahead - turn away sharply
            if left_prox < right_prox:
                # More space on left, turn left
                self.turn_left(self.turn_velocity * 4)
            else:
                # More space on right, turn right
                self.turn_right(self.turn_velocity * 4)
            # Move forward slowly while turning
            self.stepForward(self.base_velocity * 0.3)
            return

        # Rule 2: Obstacle ahead - turn away
        if front_prox > self.obstacle_threshold:
            # Moderate obstacle ahead - choose turn direction based on side sensors
            if left_prox < right_prox:
                # More space on left
                self.turn_left(self.turn_velocity * 2)
            else:
                # More space on right
                self.turn_right(self.turn_velocity * 2)
            # Reduce forward speed
            self.stepForward(self.base_velocity * 0.5)
            return

        # Rule 3: Obstacle on left side - turn right
        if left_prox > self.obstacle_threshold:
            self.turn_right(self.turn_velocity)
            self.stepForward(self.base_velocity * 0.7)
            return

        # Rule 4: Obstacle on right side - turn left
        if right_prox > self.obstacle_threshold:
            self.turn_left(self.turn_velocity)
            self.stepForward(self.base_velocity * 0.7)
            return

        # Rule 5: Free space - explore with occasional random turns
        self.stepForward(self.base_velocity)

        # Add occasional random exploration turns to avoid getting stuck in patterns
        if random.random() < 0.02:  # 2% chance per frame
            self.exploration_turn_counter = random.randint(5, 15)
            self.preferred_turn_direction = random.choice([-1, 1])

        if self.exploration_turn_counter > 0:
            if self.preferred_turn_direction > 0:
                self.turn_left(self.turn_velocity)
            else:
                self.turn_right(self.turn_velocity)
            self.exploration_turn_counter -= 1

    def torus(self):
        """
        No torus wrapping - keep robot within bounds.
        This is handled by walls, but we add safety check.
        """
        x, y, gamma = self.agent.get_position()

        # Safety bounds check
        margin = 20
        x = max(margin, min(x, self.config["world_width"] - margin))
        y = max(margin, min(y, self.config["world_height"] - margin))

        self.agent.set_position(x, y, gamma)
