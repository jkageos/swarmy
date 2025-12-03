import random

from swarmy.actuation import Actuation


class CollisionAvoidanceController(Actuation):
    """
    A controller that makes the robot move around while avoiding walls and obstacles.
    When a collision is detected, the robot backs up and turns away.
    """

    def __init__(self, agent, config):
        super().__init__(agent)
        self.config = config
        self.init_pos = True
        self.linear_velocity = config["default_velocity"]
        self.angle_velocity = config["default_angle_velocity"]
        self.turn_counter = 0  # Counter to continue turning after collision
        self.trajectory = []

    def controller(self):
        """
        Collision avoidance behavior:
        - Move forward if no collision
        - Back up and turn when collision detected
        """
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False

        sensor_data = self.agent.get_perception()
        bumper_value = sensor_data[1]  # Get bumper sensor value

        if bumper_value == 1:  # Collision detected
            # Back up
            self.stepBackward(self.linear_velocity)
            # Start turning (random direction)
            self.turn_counter = random.randint(20, 40)

        if self.turn_counter > 0:
            # Continue turning away from obstacle
            if random.random() > 0.5:
                self.turn_right(self.angle_velocity * 2)
            else:
                self.turn_left(self.angle_velocity * 2)
            self.turn_counter -= 1
        else:
            # Move forward
            self.stepForward(self.linear_velocity)

        x, y, _ = self.agent.get_position()
        self.trajectory.append((x, y))

    def torus(self):
        """
        No torus wrapping - let walls contain the robot
        """
        pass
