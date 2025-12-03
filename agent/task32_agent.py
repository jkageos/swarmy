import random

from swarmy.agent import Agent


class Task32Agent(Agent):
    def __init__(self, environment, controller, sensor, config):
        super().__init__(environment, controller, sensor, config)
        self.trajectory = []

    def initial_position(self):
        """
        Place robot randomly at high potential (left side of arena)
        Robot faces RIGHT (towards low potential)
        """
        # Start on FAR LEFT side where potential is highest
        # Spawn in leftmost 50 pixels
        x = random.randint(20, 50)
        y = random.randint(
            self.config["world_height"] // 3, 2 * self.config["world_height"] // 3
        )

        # Face RIGHT (angle 90° in pygame = pointing right)
        # Range: 60-120° = generally rightward
        gamma = random.randint(60, 120)

        self.actuation.position[0] = x
        self.actuation.position[1] = y
        self.actuation.angle = gamma
        self.set_position(x, y, gamma)

        # Print starting potential (for verification)
        potential = self.environment.get_potential_value(x, y)
        print(
            f"Starting at position ({x}, {y}) with potential: {potential:.2f}, facing angle {gamma}°"
        )

    def save_information(self, *args, **kwargs):
        """
        Save trajectory and generate plot for Task 3.2

        Note: Accepts any arguments for compatibility with experiment.py,
        but doesn't use them (single robot scenario).
        """
        if hasattr(self.actuation, "trajectory") and len(self.actuation.trajectory) > 0:
            # Import plotting function
            from utils.plot_potential_field import plot_task32_trajectory

            # Get controller name
            controller_name = self.actuation.__class__.__name__.replace(
                "Controller", ""
            )

            # Generate plot
            plot_task32_trajectory(
                controller_name,
                self.actuation.trajectory,
                self.environment.potential_field,
                self.config["world_width"],
                self.config["world_height"],
            )

            # Print trajectory summary
            traj = self.actuation.trajectory
            start_x, start_y = traj[0]
            end_x, end_y = traj[-1]
            start_pot = self.environment.get_potential_value(start_x, start_y)
            end_pot = self.environment.get_potential_value(end_x, end_y)

            print(f"\nTrajectory Summary:")
            print(
                f"  Start: ({start_x:.1f}, {start_y:.1f}), Potential: {start_pot:.2f}"
            )
            print(f"  End: ({end_x:.1f}, {end_y:.1f}), Potential: {end_pot:.2f}")
            print(f"  Potential descent: {start_pot - end_pot:.2f}")
            print(f"  Steps: {len(traj)}")
