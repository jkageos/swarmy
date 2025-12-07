# =============================================================================
# created by:   Samer Al-Magazachi
# created on:   06/04/2021 -- 13/04/2022
# version:      0.9
# status:       prototype
# =============================================================================
import sys
from copy import deepcopy

import numpy as np
import yaml

from swarmy.experiment import Experiment

### load the configuration file
with open("config.yaml", "r") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

## ============================================================================
## TASK 3.1: Single Robot Behaviors
## ============================================================================
# from agent.my_agent import MyAgent
# from controller.task31a_controller import CollisionAvoidanceController
# from controller.task31b_controller import WallFollowerController
# from controller.task31c_controller import VacuumCleanerController
# from controller.task31d_controller import LevyFlightController
# from sensors.bumper_sensor import BumperSensor
# from world.task31_world import Task31Environment

# # Choose which controller to test (uncomment one):
# agent_controller = [CollisionAvoidanceController]  # Task 3.1a
# # agent_controller = [WallFollowerController]        # Task 3.1b
# # agent_controller = [VacuumCleanerController]       # Task 3.1c
# # agent_controller = [LevyFlightController]          # Task 3.1d

# # Add sensors
# agent_sensing = [BumperSensor]

# # Create and run experiment
# exp1 = Experiment(config, agent_controller, agent_sensing, Task31Environment, MyAgent)
# exp1.run(1)

## ============================================================================
## TASK 3.2: Potential Field Control
## ============================================================================
# from agent.task32_agent import Task32Agent
# from controller.task32a_controller import DirectGradientController
# from controller.task32b_controller import IndirectGradientController
# from world.task32_world import Task32Environment

# # Choose which controller to test (uncomment one):
# agent_controller = [DirectGradientController]  # Task 3.2a
# # agent_controller = [IndirectGradientController]  # Task 3.2b

# # No sensors needed for potential field navigation
# agent_sensing = []

# # Create and run experiment
# exp1 = Experiment(
#     config, agent_controller, agent_sensing, Task32Environment, Task32Agent
# )
# exp1.run(1)

## ============================================================================
## TASK 4.1: Swarm Aggregation
## ============================================================================
# from agent.task41_agent import Task41Agent
# from controller.task41_controller import AggregationController
# from sensors.task41_sensor import ProximitySensor
# from world.task41_world import Task41Environment

# # Aggregation controller with proximity sensor
# agent_controller = [AggregationController]
# agent_sensing = [ProximitySensor]

# # Create and run experiment
# exp1 = Experiment(
#     config, agent_controller, agent_sensing, Task41Environment, Task41Agent
# )
# exp1.run(1)

## ============================================================================
## TASK 4.2a: Reynolds Flocking in Toroidal Space
## ============================================================================
# from agent.task42_agent import Task42Agent
# from controller.task42_controller import FlockingController
# from sensors.task42_sensor import FlockingSensor
# from world.task42_world import Task42Environment

# # Create and run experiment
# agent_controller = [FlockingController]
# agent_sensing = [FlockingSensor]

# exp1 = Experiment(
#     config, agent_controller, agent_sensing, Task42Environment, Task42Agent
# )
# exp1.run(1)

## ============================================================================
## TASK 4.2b: Flocking with Heading Noise - Order Parameter Analysis
## ============================================================================
from agent.task42_agent import Task42Agent
from controller.task42_controller import FlockingController
from sensors.task42_sensor import FlockingSensor
from utils.plot_flocking import compute_order_parameter, plot_order_vs_noise
from world.task42_world import Task42Environment

# Configuration for noise sweep
config["rendering"] = 0

# Noise sweep parameters
noise_levels = np.linspace(0, 1.0, 11)
runs_per_noise = 3

va_means = []
va_stds = []

print("\n" + "=" * 70)
print("TASK 4.2b: Flocking with Heading Noise")
print("=" * 70)

completed_runs = 0
total_runs = len(noise_levels) * runs_per_noise

try:
    for eta in noise_levels:
        va_runs = []

        print(f"\nNoise intensity η = {eta:.2f}:")
        print("-" * 50)

        for run in range(runs_per_noise):
            try:
                print(f"  Run {run + 1}/{runs_per_noise}...", end=" ", flush=True)

                # Create a fresh config copy for each simulation
                config_copy = deepcopy(config)
                config_copy["heading_noise"] = eta

                agent_controller = [FlockingController]
                agent_sensing = [FlockingSensor]

                # Run simulation
                exp = Experiment(
                    config_copy,
                    agent_controller,
                    agent_sensing,
                    Task42Environment,
                    Task42Agent,
                )
                exp.run(rendering=0)

                # Compute order parameter
                va = compute_order_parameter(exp.world.agentlist)
                va_runs.append(va)
                print(f"va = {va:.4f}")

                completed_runs += 1
                print(
                    f"  Progress: {completed_runs}/{total_runs} runs completed",
                    flush=True,
                )

            except KeyboardInterrupt:
                print("\n  Interrupted during run")
                raise

            except Exception as e:
                print(f"\n  ✗ Error in run: {e}")
                import traceback

                traceback.print_exc()
                continue

        # Calculate statistics for this noise level
        if len(va_runs) > 0:
            va_mean = np.mean(va_runs)
            va_std = np.std(va_runs)
            va_means.append(va_mean)
            va_stds.append(va_std)

            print(f"  Average: {va_mean:.4f} ± {va_std:.4f}")
        else:
            print(f"  ✗ No valid runs for η = {eta:.2f}")
            va_means.append(0.0)
            va_stds.append(0.0)

    # Plot results if we have valid data
    if len(va_means) > 0 and max(va_means) > 0:
        print("\n" + "=" * 70)
        plot_order_vs_noise(noise_levels, va_means)
        print("=" * 70)

        # Print summary
        print("\nSummary:")
        print(f"  Noise range: η ∈ [{noise_levels[0]:.2f}, {noise_levels[-1]:.2f}]")
        valid_indices = [i for i, v in enumerate(va_means) if v > 0]
        if valid_indices:
            max_idx = max(valid_indices, key=lambda i: va_means[i])
            min_idx = min(valid_indices, key=lambda i: va_means[i])
            print(
                f"  Maximum order parameter: {va_means[max_idx]:.4f} at η = {noise_levels[max_idx]:.2f}"
            )
            print(
                f"  Minimum order parameter: {va_means[min_idx]:.4f} at η = {noise_levels[min_idx]:.2f}"
            )

            if len(va_means) > 1:
                drops = [
                    va_means[i] - va_means[i + 1]
                    for i in range(len(va_means) - 1)
                    if va_means[i] > 0 and va_means[i + 1] > 0
                ]
                if drops:
                    max_drop_idx = np.argmax(drops)
                    print(
                        f"  Largest drop in order: Δva = {drops[max_drop_idx]:.4f} between η = {noise_levels[max_drop_idx]:.2f} and η = {noise_levels[max_drop_idx + 1]:.2f}"
                    )
                    print(
                        f"  Potential phase transition region: η ≈ {noise_levels[max_drop_idx]:.2f}"
                    )

    print(f"\n✓ Completed: {completed_runs}/{total_runs} runs successful")

except KeyboardInterrupt:
    print(
        f"\n\n✗ Interrupted by user (Ctrl+C) after {completed_runs}/{total_runs} runs"
    )
    sys.exit(0)

except Exception as e:
    print(f"\n✗ Fatal error: {e}")
    import traceback

    traceback.print_exc()
    sys.exit(1)
