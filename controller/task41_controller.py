import random

import numpy as np

from swarmy.actuation import Actuation


class AggregationController(Actuation):
    """
    Swarm aggregation behavior with waiting time to encourage clustering.

    Strategy:
    a) Robots stop when they detect nearby robots
    b) Robots wait for a defined duration before moving again
    c) After waking up, robots have a "cooldown" period before stopping again
    """

    def __init__(self, agent, config):
        super().__init__(agent)
        self.config = config
        self.init_pos = True

        # Movement parameters
        self.linear_velocity = config.get("default_velocity", 4)
        self.angle_velocity = config.get("default_angle_velocity", 4)

        # Aggregation parameters
        self.detection_range = config.get("proximity_range", 80)
        self.waiting_time = config.get("aggregation_waiting_time", 60)  # frames
        self.cooldown_time = config.get(
            "aggregation_cooldown", 30
        )  # frames after waking up

        # State variables
        self.state = "moving"  # 'moving', 'stopped', 'cooldown'
        self.state_counter = 0
        self.trajectory = []

        # Agent bounding box size (from swarmy/body.py)
        self.BOUNDING = 30  # Approximate radius of agent collision object

    def controller(self):
        """
        Main aggregation control loop with state machine.

        States:
        - moving: Robot explores freely
        - stopped: Robot detected nearby robot, stays stopped for waiting_time
        - cooldown: After waking up, robot moves but has reduced stopping sensitivity
        """
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False
            self.state = "moving"
            self.state_counter = 0

        # Get perception data (proximity sensor)
        sensor_data = self.agent.get_perception()
        proximity_distance = sensor_data[1]  # -1 if no robot detected, else distance

        x, y, angle = self.agent.get_position()
        self.trajectory.append((x, y))

        # State machine
        if self.state == "moving":
            # Move forward freely
            self.stepForward(self.linear_velocity)

            # Random walk for exploration
            if random.random() < 0.05:  # 5% chance to turn
                turn_angle = random.randint(-20, 20)
                if turn_angle > 0:
                    self.turn_left(abs(turn_angle))
                else:
                    self.turn_right(abs(turn_angle))

            # Detect nearby robot → stop
            if proximity_distance > 0 and proximity_distance <= self.detection_range:
                self.state = "stopped"
                self.state_counter = 0

        elif self.state == "stopped":
            # Robot stays still (don't move)
            self.state_counter += 1

            # Wait for waiting_time frames
            if self.state_counter >= self.waiting_time:
                self.state = "cooldown"
                self.state_counter = 0

        elif self.state == "cooldown":
            # Robot wakes up and moves, but won't stop immediately
            self.stepForward(self.linear_velocity)

            # Random walk
            if random.random() < 0.08:  # Slightly higher turn probability
                turn_angle = random.randint(-25, 25)
                if turn_angle > 0:
                    self.turn_left(abs(turn_angle))
                else:
                    self.turn_right(abs(turn_angle))

            self.state_counter += 1

            # After cooldown period, return to normal moving state
            if self.state_counter >= self.cooldown_time:
                self.state = "moving"
                self.state_counter = 0

    def torus(self):
        """
        Keep robot entirely within bounds (account for agent bounding size)
        """
        x, y, angle = self.agent.get_position()

        # Add margin for agent bounding box (prevents model from crossing border)
        margin = self.BOUNDING

        # Bounce off walls and clamp position
        if x <= margin or x >= self.agent.environment.width - margin:
            self.turn_right(90)
            x = np.clip(x, margin, self.agent.environment.width - margin)

        if y <= margin or y >= self.agent.environment.height - margin:
            self.turn_right(90)
            y = np.clip(y, margin, self.agent.environment.height - margin)

        self.agent.set_position(x, y, int(angle))
