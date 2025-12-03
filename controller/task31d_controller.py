import random

from swarmy.actuation import Actuation


class LevyFlightController(Actuation):
    """
    An exploratory behavior using Lévy flight pattern.
    Combines short movements with occasional long straight paths.
    """

    def __init__(self, agent, config):
        super().__init__(agent)
        self.config = config
        self.init_pos = True
        self.linear_velocity = config["default_velocity"]
        self.angle_velocity = config["default_angle_velocity"]

        self.straight_steps = 0
        self.max_straight_steps = 0
        self.turn_counter = 0
        self.trajectory = []

    def levy_flight_steps(self):
        """
        Generate step count following power-law distribution (Lévy flight)
        """
        # Simple power-law: mostly short flights, occasionally long ones
        if random.random() < 0.8:
            return random.randint(5, 20)  # Short flight
        else:
            return random.randint(50, 150)  # Long flight

    def controller(self):
        """
        Lévy flight exploration behavior
        """
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False
            self.max_straight_steps = self.levy_flight_steps()

        sensor_data = self.agent.get_perception()
        bumper_value = sensor_data[1]

        if bumper_value == 1:  # Collision
            # Back up and turn
            self.stepBackward(self.linear_velocity)
            self.turn_counter = random.randint(10, 25)
            self.straight_steps = 0
            self.max_straight_steps = self.levy_flight_steps()

        if self.turn_counter > 0:
            # Execute turn
            if random.random() > 0.5:
                self.turn_right(self.angle_velocity * 3)
            else:
                self.turn_left(self.angle_velocity * 3)
            self.turn_counter -= 1
        else:
            # Move forward
            self.stepForward(self.linear_velocity)
            self.straight_steps += 1

            # After completing a straight segment, turn and start new segment
            if self.straight_steps >= self.max_straight_steps:
                self.turn_counter = random.randint(5, 20)
                self.straight_steps = 0
                self.max_straight_steps = self.levy_flight_steps()

        x, y, _ = self.agent.get_position()
        self.trajectory.append((x, y))

    def torus(self):
        """
        No torus wrapping
        """
        pass
