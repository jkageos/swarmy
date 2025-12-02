"""
Hill climber algorithm utilities for evolving robot behavior.
"""

import copy
import random
from concurrent.futures import ProcessPoolExecutor

import pygame


class HillClimber:
    def __init__(self, config):
        self.config = config
        self.population_size = 1  # Hill climber has population of 1

        # Evolution parameters
        self.num_generations = config.get("num_generations", 50)
        self.mutation_rate = config.get("mutation_rate", 0.3)
        self.mutation_strength = config.get(
            "mutation_strength", 0.8
        )  # Reduced for stability

        # Best genome tracking
        self.best_genome = None
        self.best_fitness = -1

        # History for plotting
        self.fitness_history = []

    def random_genome(self):
        """Generate random genome within reasonable bounds"""
        genome = []
        for _ in range(3):
            # Bias towards positive intercepts for forward motion
            m = random.uniform(-5, 5)
            c = random.uniform(0.5, 3.0)  # Positive bias
            genome.append((m, c))
        return genome

    def mutate_genome(self, genome):
        """Mutate genome by adding Gaussian noise"""
        mutated = []
        for m, c in genome:
            new_m = m
            new_c = c

            if random.random() < self.mutation_rate:
                new_m = m + random.gauss(0, self.mutation_strength)
                # Keep slopes reasonable
                new_m = max(-10, min(10, new_m))

            if random.random() < self.mutation_rate:
                new_c = c + random.gauss(0, self.mutation_strength)
                # Bias intercepts towards positive values
                new_c = max(-3, min(5, new_c))

            mutated.append((new_m, new_c))
        return mutated

    def evaluate_genome(self, genome, generation, run_id):
        """Evaluate fitness of a genome by running simulation"""
        from agent.task4_agent import Task4Agent
        from controller.task4_controller import EvolvedController
        from sensors.task2_sensor import ProximitySensor
        from world.task2_world import Task2World

        # Initialize pygame
        pygame.init()

        # Create modified config for evaluation
        eval_config = copy.deepcopy(self.config)
        eval_config["number_of_agents"] = 1
        eval_config["rendering"] = -1  # No display for speed
        eval_config["save_trajectory"] = 0  # Don't save during evolution

        # Create environment
        environment = Task2World(eval_config)
        environment.render_init()

        # Create agent with evolved controller
        def controller_factory(agent, config):
            return EvolvedController(agent, config, genome)

        agent = Task4Agent(
            environment, controller_factory, [ProximitySensor], eval_config
        )
        agent.initial_position()
        agent.unique_id = 0

        # Run simulation
        timesteps = 0
        max_timesteps = eval_config.get("eval_timesteps", 1000)

        while timesteps < max_timesteps:
            timesteps += 1

            # Update agent
            agent.processing.perform(pygame.key.get_pressed())

            # Track visited cells
            agent.update_visited_cells()

            # Remove event handling loop during evolution (small speedup)
            # for event in pygame.event.get():
            #     if event.type == pygame.QUIT:
            #         pygame.quit()
            #         return 0

        # Get fitness (number of unique cells visited)
        fitness = agent.get_fitness()

        pygame.quit()

        # Format genome for cleaner printing
        genome_str = f"[({genome[0][0]:.2f}, {genome[0][1]:.2f}), ({genome[1][0]:.2f}, {genome[1][1]:.2f}), ({genome[2][0]:.2f}, {genome[2][1]:.2f})]"
        print(f"  Run {run_id}, Gen {generation}: {genome_str} -> Fitness {fitness}")

        return fitness

    def run_evolution(self, run_id=0):
        """Run hill climber evolution"""
        print(f"\n{'=' * 60}")
        print(f"Starting Hill Climber Run {run_id}")
        print(f"{'=' * 60}")

        # Initialize with random genome
        current_genome = self.random_genome()
        current_fitness = self.evaluate_genome(current_genome, 0, run_id)

        self.best_genome = copy.deepcopy(current_genome)
        self.best_fitness = current_fitness
        self.fitness_history = [current_fitness]

        print(f"Initial genome: {current_genome}")
        print(f"Initial fitness: {current_fitness}\n")

        # Evolution loop
        for generation in range(1, self.num_generations + 1):
            # Mutate genome
            candidate_genome = self.mutate_genome(current_genome)

            # Evaluate candidate
            candidate_fitness = self.evaluate_genome(
                candidate_genome, generation, run_id
            )

            # Accept or reject based on fitness
            if candidate_fitness >= current_fitness:
                # Accept (improvement or equal)
                current_genome = candidate_genome
                current_fitness = candidate_fitness
                print(f"  ✓ Accepted (fitness: {current_fitness})")

                # Update best
                if current_fitness > self.best_fitness:
                    self.best_genome = copy.deepcopy(current_genome)
                    self.best_fitness = current_fitness
                    print(f"  ★ New best fitness: {self.best_fitness}")
            else:
                # Reject (worsening) - current_genome stays unchanged (backtrack)
                print(f"  ✗ Rejected (fitness: {candidate_fitness})")

            self.fitness_history.append(current_fitness)

        print(f"\n{'=' * 60}")
        print(f"Evolution Complete - Run {run_id}")
        print(f"Best genome: {self.best_genome}")
        print(f"Best fitness: {self.best_fitness}")
        print(f"{'=' * 60}\n")

        return self.best_genome, self.best_fitness, self.fitness_history

    def visualize_best(self, genome, run_id=0):
        from agent.task4_agent import Task4Agent
        from controller.task4_controller import EvolvedController
        from sensors.task2_sensor import ProximitySensor
        from swarmy.experiment import Experiment
        from world.task2_world import Task2World

        print(f"\nVisualizing best behavior from run {run_id}...")

        # Enable rendering and trajectory saving for visualization
        vis_config = copy.deepcopy(self.config)
        vis_config["number_of_agents"] = 1
        vis_config["rendering"] = 1  # Full rendering
        vis_config["save_trajectory"] = 1
        vis_config["max_timestep"] = vis_config.get("eval_timesteps", 1000)

        # Create controller factory with best genome
        def controller_factory(agent, config):
            return EvolvedController(agent, config, genome)

        # Run experiment with visualization (this will save trajectory plot)
        exp = Experiment(
            vis_config,
            [controller_factory],
            [ProximitySensor],
            Task2World,
            Task4Agent,
        )
        exp.run(1)

    def plot_fitness_history(self, run_id=0):
        """Plot fitness over generations"""
        from pathlib import Path

        import matplotlib.pyplot as plt

        Path("plots/task4").mkdir(parents=True, exist_ok=True)

        plt.figure(figsize=(10, 6))
        plt.plot(self.fitness_history, marker="o", linewidth=2, markersize=4)
        plt.xlabel("Generation", fontsize=12)
        plt.ylabel("Fitness (Cells Visited)", fontsize=12)
        plt.title(f"Hill Climber Evolution - Run {run_id}", fontsize=14)
        plt.grid(True, alpha=0.3)

        filename = f"plots/task4/fitness_history_run_{run_id}.png"
        plt.savefig(filename, dpi=150, bbox_inches="tight")
        print(f"Saved fitness plot: {filename}")
        plt.close()


def _run_single_evolution(config, run_id):
    """
    Helper function to run a single evolution run (for parallel execution).
    Must be a top-level function for multiprocessing to work.
    """
    from utils.plotting import plot_task4_trajectory

    print(f"\n{'#' * 60}")
    print(f"# INDEPENDENT RUN {run_id + 1}")
    print(f"{'#' * 60}")

    climber = HillClimber(config)
    best_genome, best_fitness, fitness_history = climber.run_evolution(run_id)

    result = {
        "run_id": run_id,
        "genome": best_genome,
        "fitness": best_fitness,
        "history": fitness_history,
    }

    # Visualize best behavior and plot trajectory for this run
    print(f"\nPlotting trajectory for best evolved behavior (Run {run_id})...")

    # Run visualization and collect trajectory
    from agent.task4_agent import Task4Agent
    from controller.task4_controller import EvolvedController
    from sensors.task2_sensor import ProximitySensor
    from world.task2_world import Task2World

    pygame.init()

    vis_config = copy.deepcopy(config)
    vis_config["number_of_agents"] = 1
    vis_config["rendering"] = -1  # No display for trajectory collection
    vis_config["save_trajectory"] = 0
    vis_config["max_timestep"] = vis_config.get("eval_timesteps", 1000)

    environment = Task2World(vis_config)
    environment.render_init()

    def controller_factory(agent, config):
        return EvolvedController(agent, config, best_genome)

    agent = Task4Agent(environment, controller_factory, [ProximitySensor], vis_config)
    agent.initial_position()
    agent.unique_id = 0

    timesteps = 0
    max_timesteps = vis_config["max_timestep"]

    while timesteps < max_timesteps:
        timesteps += 1
        # Use pygame's actual key state
        agent.processing.perform(pygame.key.get_pressed())
        agent.update_visited_cells()

        # Handle pygame events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                break

    # Plot trajectory for this run
    walls = environment.get_static_rect_list()
    plot_task4_trajectory(
        agent.trajectory,
        agent.unique_id,
        run_id,
        config,
        walls=walls,
        save_path="plots/task4",
    )

    pygame.quit()

    return result


def _fmt_genome(genome):
    return "[(" + "), (".join(f"{m:.2f}, {c:.2f}" for (m, c) in genome) + ")]"


def run_hill_climber_experiment(config, num_runs=3, parallel=False):
    """
    Run multiple independent hill climber experiments.

    Args:
        config: Configuration dictionary
        num_runs: Number of independent runs to perform
        parallel: If True, run experiments in parallel (faster but more CPU/memory intensive)
    """
    # Override some settings for evolution
    config["eval_timesteps"] = config.get("eval_timesteps", 1000)
    config["grid_cell_size"] = config.get("grid_cell_size", 20)
    config["num_generations"] = config.get("num_generations", 50)
    config["mutation_rate"] = config.get("mutation_rate", 0.3)
    config["mutation_strength"] = config.get("mutation_strength", 0.8)

    # Fixed starting position for deterministic evaluation
    config["eval_start_x"] = config["world_width"] // 4
    config["eval_start_y"] = config["world_height"] // 4
    config["eval_start_angle"] = 45

    all_results = []

    if parallel:
        print(f"\n{'=' * 60}")
        print(f"Running {num_runs} experiments IN PARALLEL")
        print(f"{'=' * 60}")

        # Use fewer workers to reduce memory overhead
        max_workers = min(num_runs, 2)  # Limit to 2 parallel runs at a time

        with ProcessPoolExecutor(max_workers=max_workers) as executor:
            # Submit all runs
            futures = [
                executor.submit(_run_single_evolution, config, run_id)
                for run_id in range(num_runs)
            ]

            # Collect results as they complete
            for future in futures:
                result = future.result()
                all_results.append(result)
    else:
        # Sequential execution (original behavior)
        for run_id in range(num_runs):
            result = _run_single_evolution(config, run_id)
            all_results.append(result)

    # Summary
    # Sort by run_id to ensure stable summary order
    all_results.sort(key=lambda r: r["run_id"])

    print(f"\n{'=' * 60}")
    print("SUMMARY OF ALL RUNS")
    print(f"{'=' * 60}")
    for r in all_results:
        print(
            f"Run {r['run_id']}: Fitness = {r['fitness']}, Genome = {_fmt_genome(r['genome'])}"
        )
    print(f"{'=' * 60}\n")

    return all_results
