import random

from swarmy.agent import Agent


class Task52Agent(Agent):
    """
    Agent for local sampling task.
    Each robot is randomly assigned a color (black or white).
    """

    def __init__(self, environment, controller, sensor, config):
        super().__init__(environment, controller, sensor, config)
        self.color = random.choice(["black", "white"])  # Random color assignment
        self.local_estimate = 0.0  # Estimate of black robot ratio
        self.local_count = 0  # Number of robots in neighborhood

    def initial_position(self):
        """
        Uniformly distribute robot in unit square [0, 1] x [0, 1].
        Scaled to actual world dimensions.
        """
        width = self.config["world_width"]
        height = self.config["world_height"]

        x = random.uniform(0, width)
        y = random.uniform(0, height)
        gamma = random.randint(0, 360)

        self.actuation.position[0] = x
        self.actuation.position[1] = y
        self.actuation.angle = gamma
        self.set_position(x, y, gamma)

    def save_information(self, last_agent=False):
        """
        Store local sampling results.
        """
        if last_agent:
            # Statistics will be collected by the experiment runner
            pass
