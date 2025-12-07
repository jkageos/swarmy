import random

from swarmy.agent import Agent


class Task42Agent(Agent):
    """
    Agent for flocking task.
    Spawns robots randomly throughout the toroidal arena.
    """

    def __init__(self, environment, controller, sensor, config):
        super().__init__(environment, controller, sensor, config)
        self.trajectory = []

    def initial_position(self):
        """
        Randomly place robot in the toroidal arena.
        """
        x = random.uniform(0, self.config["world_width"])
        y = random.uniform(0, self.config["world_height"])
        gamma = random.randint(0, 360)

        self.actuation.position[0] = x
        self.actuation.position[1] = y
        self.actuation.angle = gamma
        self.set_position(x, y, gamma)

    def save_information(self, last_agent=False):
        """
        Save flocking statistics and generate visualization.
        """
        if hasattr(self.actuation, "trajectory") and len(self.actuation.trajectory) > 0:
            if last_agent:
                # Generate order parameter plot after all agents are processed
                from utils.plot_flocking import compute_and_plot_order_parameter

                compute_and_plot_order_parameter(
                    self.environment.agentlist, self.config
                )
