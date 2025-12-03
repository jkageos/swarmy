from swarmy.actuation import Actuation


class WallFollowerController(Actuation):
    """
    A controller that makes the robot follow walls without touching them.
    Uses a state machine approach.
    """

    def __init__(self, agent, config):
        super().__init__(agent)
        self.config = config
        self.init_pos = True
        self.linear_velocity = config["default_velocity"]
        self.angle_velocity = config["default_angle_velocity"]

        # States: 'seeking_wall', 'following_wall', 'avoiding_collision'
        self.state = "seeking_wall"
        self.turn_counter = 0
        self.wall_follow_direction = "right"  # Follow wall on right side
        self.steps_since_collision = 0
        self.trajectory = []

    def controller(self):
        """
        Wall following behavior using state machine
        """
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False

        sensor_data = self.agent.get_perception()
        bumper_value = sensor_data[1]

        if bumper_value == 1:  # Collision detected
            self.state = "avoiding_collision"
            self.turn_counter = 15
            self.steps_since_collision = 0

        self.steps_since_collision += 1

        x, y, _ = self.agent.get_position()
        self.trajectory.append((x, y))

        if self.state == "seeking_wall":
            # Move forward until we find a wall
            self.stepForward(self.linear_velocity)
            if bumper_value == 1:
                self.state = "avoiding_collision"

        elif self.state == "avoiding_collision":
            # Back up and turn away from wall
            if self.turn_counter > 10:
                self.stepBackward(self.linear_velocity)
            if self.wall_follow_direction == "right":
                self.turn_left(self.angle_velocity * 2)
            else:
                self.turn_right(self.angle_velocity * 2)

            self.turn_counter -= 1
            if self.turn_counter <= 0:
                self.state = "following_wall"

        elif self.state == "following_wall":
            # Move forward and gradually turn toward the wall
            self.stepForward(self.linear_velocity)

            # Gradually turn back toward wall to maintain distance
            if self.steps_since_collision > 10:
                if self.wall_follow_direction == "right":
                    self.turn_right(self.angle_velocity // 2)
                else:
                    self.turn_left(self.angle_velocity // 2)

    def torus(self):
        """
        No torus wrapping
        """
        pass
