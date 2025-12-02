from swarmy.agent import Agent


class Task4Agent(Agent):
    def __init__(self, environment, controller, sensor, config, genome=None):
        # Store genome before calling super().__init__
        self.genome = genome
        super().__init__(environment, controller, sensor, config)
        self.environment = environment
        self.trajectory = []
        self.visited_cells = set()

        # Initialize unique_id to satisfy type checker
        self.unique_id: int = 0

        # Grid parameters for fitness calculation
        self.grid_cell_size = config.get("grid_cell_size", 20)  # pixels

    def initial_position(self):
        """Fixed initial position for deterministic evaluation"""
        x = self.config.get("eval_start_x", self.config["world_width"] // 4)
        y = self.config.get("eval_start_y", self.config["world_height"] // 4)
        gamma = self.config.get("eval_start_angle", 45)

        self.actuation.position[0] = x
        self.actuation.position[1] = y
        self.actuation.angle = gamma
        self.set_position(x, y, gamma)

    def update_visited_cells(self):
        """Track which grid cells have been visited"""
        x, y, _ = self.get_position()
        cell_x = int(x // self.grid_cell_size)
        cell_y = int(y // self.grid_cell_size)
        self.visited_cells.add((cell_x, cell_y))

    def get_fitness(self):
        """Return number of unique cells visited"""
        return len(self.visited_cells)

    def save_information(self, is_last_agent=False):
        """Save trajectory plots with fitness information"""
        if (
            self.config.get("save_trajectory", 0)
            and is_last_agent
            and len(self.trajectory) > 1
        ):
            from utils.plotting import plot_trajectory

            save_path = "plots/task4"

            print(
                f"\n=== Generating plots for evolved behavior (fitness: {self.get_fitness()}) ==="
            )

            # Get walls from environment for visualization
            walls = self.environment.get_static_rect_list()

            # Plot trajectory
            plot_trajectory(
                self.trajectory,
                self.unique_id,
                self.config,
                walls=walls,
                save_path=save_path,
            )

            print(f"=== Plots saved to '{save_path}/' directory ===\n")
