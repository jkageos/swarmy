import random

from swarmy.agent import Agent


class MyAgent(Agent):
    def __init__(self, environment, controller, sensor, config):
        super().__init__(environment, controller, sensor, config)
        self.environment = environment
        self.trajectory = []

    def initial_position(self):
        """
        Define the initial position of the agent.
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
        Save trajectory and generate plot for Task 3.1

        Note: Accepts any arguments for compatibility with experiment.py,
        but doesn't use them (single robot scenario).
        """
        if hasattr(self.actuation, "trajectory") and len(self.actuation.trajectory) > 0:
            # Import plotting function
            from utils.plot_trajectories import plot_task31_trajectory

            # Get controller name
            controller_name = self.actuation.__class__.__name__.replace(
                "Controller", ""
            )

            # Generate plot
            plot_task31_trajectory(
                controller_name,
                self.actuation.trajectory,
                self.config["world_width"],
                self.config["world_height"],
            )

            print(f"\n✓ Trajectory saved: {len(self.actuation.trajectory)} steps")
