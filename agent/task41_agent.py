import random

from swarmy.agent import Agent


class Task41Agent(Agent):
    """
    Agent for swarm aggregation task.
    Spawns robots randomly throughout the arena.
    """

    def __init__(self, environment, controller, sensor, config):
        super().__init__(environment, controller, sensor, config)
        self.trajectory = []

    def initial_position(self):
        """
        Randomly place robot in the arena (avoiding walls).
        """
        x = random.randint(50, self.config["world_width"] - 50)
        y = random.randint(50, self.config["world_height"] - 50)
        gamma = random.randint(0, 360)

        self.actuation.position[0] = x
        self.actuation.position[1] = y
        self.actuation.angle = gamma
        self.set_position(x, y, gamma)

    def save_information(self, *args, **kwargs):
        """
        Save trajectory and generate visualization for Task 4.1.
        """
        if hasattr(self.actuation, "trajectory") and len(self.actuation.trajectory) > 0:
            # For now, just print summary
            traj = self.actuation.trajectory
            print(f"Robot {self.unique_id}: {len(traj)} steps recorded")
