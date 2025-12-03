import random

from swarmy.actuation import Actuation


class VacuumCleanerController(Actuation):
    """
    A vacuum cleaning robot using a spiral pattern with random walk fallback.
    Strategy: Combine systematic coverage (spiral/boustrophedon) with random bouncing.
    """

    def __init__(self, agent, config):
        super().__init__(agent)
        self.config = config
        self.init_pos = True
        self.linear_velocity = config["default_velocity"]
        self.angle_velocity = config["default_angle_velocity"]

        # Cleaning strategy state
        self.mode = "spiral"  # 'spiral' or 'random_bounce'
        self.spiral_steps = 0
        self.spiral_max_steps = 30
        self.spiral_increment = 5
        self.turn_counter = 0

        # Track coverage (simple implementation)
        self.steps_in_mode = 0
        self.mode_switch_interval = 200

        self.trajectory = []

    def controller(self):
        """
        Vacuum cleaning behavior combining multiple strategies
        """
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False

        sensor_data = self.agent.get_perception()
        bumper_value = sensor_data[1]

        self.steps_in_mode += 1

        # Switch between modes periodically
        if self.steps_in_mode > self.mode_switch_interval:
            self.mode = "random_bounce" if self.mode == "spiral" else "spiral"
            self.steps_in_mode = 0
            self.spiral_steps = 0

        if bumper_value == 1:  # Hit obstacle
            # Back up and turn
            self.stepBackward(self.linear_velocity)
            self.turn_counter = random.randint(15, 30)
            if random.random() > 0.5:
                self.turn_right(self.angle_velocity * 3)
            else:
                self.turn_left(self.angle_velocity * 3)
            self.spiral_steps = 0  # Reset spiral

        elif self.turn_counter > 0:
            # Continue turning after collision
            self.turn_counter -= 1
            if random.random() > 0.5:
                self.turn_right(self.angle_velocity * 2)
            else:
                self.turn_left(self.angle_velocity * 2)

        elif self.mode == "spiral":
            # Spiral pattern: move forward, then turn slightly
            self.stepForward(self.linear_velocity)
            self.spiral_steps += 1

            # Periodic turns to create spiral
            if self.spiral_steps % 20 == 0:
                self.turn_right(self.angle_velocity * 10)

        elif self.mode == "random_bounce":
            # Random walk with occasional turns
            self.stepForward(self.linear_velocity)
            if random.random() < 0.02:  # 2% chance to turn
                if random.random() > 0.5:
                    self.turn_right(self.angle_velocity * random.randint(5, 15))
                else:
                    self.turn_left(self.angle_velocity * random.randint(5, 15))

        x, y, _ = self.agent.get_position()
        self.trajectory.append((x, y))

    def torus(self):
        """
        No torus wrapping
        """
        pass
