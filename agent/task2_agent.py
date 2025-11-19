import random

from swarmy.agent import Agent


class Task2Agent(Agent):
    # cycle through 4 quadrants across instances
    _spawn_counter = 0

    def __init__(self, environment, controller, sensor, config):
        super().__init__(environment, controller, sensor, config)
        self.environment = environment
        self.trajectory = []

    def initial_position(self):
        """
        Spawn robot in a free area, avoiding walls and other robots.
        Ensures coverage across all four quadrants at least once by cycling spawns.
        """
        margin = 40  # Safe distance from walls
        max_attempts = 100

        # Compute quadrant bounds
        W = self.config["world_width"]
        H = self.config["world_height"]
        half_w = W // 2
        half_h = H // 2

        # Determine target quadrant for this agent (0..3)
        # 0: top-left, 1: top-right, 2: bottom-left, 3: bottom-right
        q = Task2Agent._spawn_counter % 4
        Task2Agent._spawn_counter += 1

        qx = 0 if q in (0, 2) else 1  # 0=left, 1=right
        qy = 0 if q in (0, 1) else 1  # 0=top, 1=bottom

        # Ranges per quadrant with margins
        if qx == 0:
            x_min, x_max = margin, max(margin + 1, half_w - margin)
        else:
            x_min, x_max = max(margin, half_w + margin), W - margin

        if qy == 0:
            y_min, y_max = margin, max(margin + 1, half_h - margin)
        else:
            y_min, y_max = max(margin, half_h + margin), H - margin

        # Fallback to whole map if ranges collapse (small worlds)
        use_full_space = (x_max <= x_min) or (y_max <= y_min)

        for attempt in range(max_attempts):
            # Random position in chosen quadrant (or full map as fallback)
            if not use_full_space:
                x = random.randint(x_min, x_max)
                y = random.randint(y_min, y_max)
            else:
                x = random.randint(margin, W - margin)
                y = random.randint(margin, H - margin)
            gamma = random.randint(0, 360)

            # Check collision with walls
            collision_detected = False

            # Create test rectangle for robot
            import pygame

            test_rect = pygame.Rect(x - 20, y - 20, 40, 40)

            # Check against all walls
            for wall in self.environment.get_static_rect_list():
                if test_rect.colliderect(wall[1]):
                    collision_detected = True
                    break

            # Check against other robots (during spawn this list is usually empty)
            if not collision_detected:
                for agent_rect in self.environment.get_agent_object():
                    if test_rect.colliderect(agent_rect):
                        collision_detected = True
                        break

            # Valid position found
            if not collision_detected:
                self.actuation.position[0] = x
                self.actuation.position[1] = y
                self.actuation.angle = gamma
                self.set_position(x, y, gamma)
                return

        # Fallback position (should rarely happen)
        print(f"Warning: Could not find free spawn after {max_attempts} attempts")
        x = self.config["world_width"] // 4
        y = self.config["world_height"] // 4
        gamma = random.randint(0, 360)
        self.actuation.position[0] = x
        self.actuation.position[1] = y
        self.actuation.angle = gamma
        self.set_position(x, y, gamma)

    def save_information(self, is_last_agent=False):
        """Save trajectory plots"""
        if (
            self.config.get("save_trajectory", 0)
            and is_last_agent
            and len(self.trajectory) > 1
        ):
            from utils.plotting import plot_all_trajectories, plot_trajectory

            save_path = "plots/task2"

            print(
                f"\n=== Generating plots for {len(self.environment.agentlist)} agents (Task 2) ==="
            )

            # Get walls from environment for visualization
            walls = self.environment.get_static_rect_list()

            # Plot individual trajectories
            for agent in self.environment.agentlist:
                if agent.trajectory:
                    plot_trajectory(
                        agent.trajectory,
                        agent.unique_id,
                        self.config,
                        walls=walls,
                        save_path=save_path,
                    )

            # Plot all trajectories combined
            plot_all_trajectories(
                self.environment.agentlist,
                self.config,
                walls=walls,
                save_path=save_path,
            )

            print(f"=== All plots saved to '{save_path}/' directory ===\n")
