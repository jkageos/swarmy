import random

from swarmy.agent import Agent


class MyAgent(Agent):
    def __init__(self, environment, controller, sensor, config):
        super().__init__(environment, controller, sensor, config)
        self.environment = environment
        self.trajectory = []

    def initial_position(self):
        """Define initial position - spawn anywhere on torus (agents will avoid each other via bumper)"""
        # Simple random spawn - let the bumper sensor and escape behavior handle crowding
        x = random.randint(50, self.config["world_width"] - 50)
        y = random.randint(50, self.config["world_height"] - 50)
        gamma = random.randint(0, 360)

        self.actuation.position[0] = x
        self.actuation.position[1] = y
        self.actuation.angle = gamma
        self.set_position(x, y, gamma)

    def save_information(self, is_last_agent=False):
        if self.config.get("save_trajectory", 0):
            if is_last_agent and len(self.trajectory) > 1:
                from utils.plotting import (
                    plot_all_trajectories,
                    plot_light_distribution,
                    plot_trajectory,
                )

                behavior = self.config.get("braitenberg_behavior", "unknown")
                save_path = f"plots/task1/{behavior}"

                print(
                    f"\n=== Generating plots for {len(self.environment.agentlist)} agents ({behavior}) ==="
                )

                plot_light_distribution(
                    self.config, self.environment, save_path=save_path
                )

                light_source = None
                if hasattr(self.environment, "light_pos") and hasattr(
                    self.environment, "light_radius"
                ):
                    lx, ly = self.environment.light_pos
                    radius = self.environment.light_radius
                    light_source = (lx, ly, radius)

                for agent in self.environment.agentlist:
                    if agent.trajectory:
                        plot_trajectory(
                            agent.trajectory,
                            agent.unique_id,
                            self.config,
                            light_source=light_source,
                            save_path=save_path,
                        )

                plot_all_trajectories(
                    self.environment.agentlist,
                    self.config,
                    light_source=light_source,
                    save_path=save_path,
                )

                print(f"=== All plots saved to '{save_path}/' directory ===\n")
