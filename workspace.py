# =============================================================================
# created by:   Samer Al-Magazachi
# created on:   06/04/2021 -- 13/04/2022
# version:      0.9
# status:       prototype
# =============================================================================
import contextlib
import io
import os
import sys
from copy import deepcopy

import numpy as np
import yaml

from swarmy.experiment import Experiment


def _run_task52_config(args):
    """Run all experiments for one (N, r) in a separate process."""
    N, r, cfg_base, EXPERIMENTS_PER_CONFIG = args
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")  # headless pygame
    from agent.task52_agent import Task52Agent
    from controller.task52_controller import SamplingController
    from sensors.task52_sensor import ColorSensor
    from swarmy.experiment import Experiment  # re-import in subprocess
    from world.task52_world import Task52Environment

    estimates = []
    for run_idx in range(EXPERIMENTS_PER_CONFIG):
        cfg = deepcopy(cfg_base)
        cfg["number_of_agents"] = int(N)
        cfg["sensor_range"] = float(r)
        exp = Experiment(
            cfg, [SamplingController], [ColorSensor], Task52Environment, Task52Agent
        )
        with contextlib.redirect_stdout(io.StringIO()):
            exp.run(rendering=0)
        agent_estimates = [a.local_estimate for a in exp.world.agentlist]
        if agent_estimates:
            estimates.append(float(np.mean(agent_estimates)))

        # Heartbeat
        if (run_idx + 1) % 50 == 0:
            print(
                f"  [N={N}, r={r:.2f}] progress {run_idx + 1}/{EXPERIMENTS_PER_CONFIG}",
                flush=True,
            )

    return (N, r, estimates)


if __name__ == "__main__":
    ### load the configuration file
    with open("config.yaml", "r") as file:
        config = yaml.load(file, Loader=yaml.FullLoader)

    # Apply global multiprocessing safety limits once
    from utils.mp_utils import apply_mp_safety_env

    apply_mp_safety_env(
        blas_threads=str(config.get("multiprocessing", {}).get("blas_threads", 1))
    )

    # ========================================================================
    # TASK 3.1: Single Robot Behaviors
    # ========================================================================
    if config.get("task31", {}).get("active", False):
        from agent.my_agent import MyAgent
        from controller.task31a_controller import CollisionAvoidanceController
        from controller.task31b_controller import WallFollowerController
        from controller.task31c_controller import VacuumCleanerController
        from controller.task31d_controller import LevyFlightController
        from sensors.bumper_sensor import BumperSensor
        from world.task31_world import Task31Environment

        t31 = config["task31"]
        cfg = deepcopy(config)
        cfg["rendering"] = t31.get("rendering", cfg["rendering"])
        cfg["max_timestep"] = t31.get("max_timestep", cfg["max_timestep"])
        cfg["save_trajectory"] = t31.get("save_trajectory", cfg["save_trajectory"])

        controller_map = {
            "collision_avoidance": CollisionAvoidanceController,
            "wall_follower": WallFollowerController,
            "vacuum_cleaner": VacuumCleanerController,
            "levy_flight": LevyFlightController,
        }
        ctrl_key = t31.get("controller", "collision_avoidance")
        agent_controller = [controller_map[ctrl_key]]
        agent_sensing = [BumperSensor]

        print(f"\n🤖 Running Task 3.1: {ctrl_key}")
        exp = Experiment(
            cfg, agent_controller, agent_sensing, Task31Environment, MyAgent
        )
        exp.run(rendering=cfg["rendering"])

    # ========================================================================
    # TASK 3.2: Potential Field Control
    # ========================================================================
    if config.get("task32", {}).get("active", False):
        from agent.task32_agent import Task32Agent
        from controller.task32a_controller import DirectGradientController
        from controller.task32b_controller import IndirectGradientController
        from world.task32_world import Task32Environment

        t32 = config["task32"]
        cfg = deepcopy(config)
        cfg["rendering"] = t32.get("rendering", cfg["rendering"])
        cfg["max_timestep"] = t32.get("max_timestep", cfg["max_timestep"])
        cfg["save_trajectory"] = t32.get("save_trajectory", cfg["save_trajectory"])

        controller_map = {
            "direct_gradient": DirectGradientController,
            "indirect_gradient": IndirectGradientController,
        }
        ctrl_key = t32.get("controller", "direct_gradient")
        agent_controller = [controller_map[ctrl_key]]
        agent_sensing = []

        print(f"\n🤖 Running Task 3.2: {ctrl_key}")
        exp = Experiment(
            cfg, agent_controller, agent_sensing, Task32Environment, Task32Agent
        )
        exp.run(rendering=cfg["rendering"])

    # ========================================================================
    # TASK 4.1: Swarm Aggregation
    # ========================================================================
    if config.get("task41", {}).get("active", False):
        from agent.task41_agent import Task41Agent
        from controller.task41_controller import AggregationController
        from sensors.task41_sensor import ProximitySensor
        from world.task41_world import Task41Environment

        t41 = config["task41"]
        cfg = deepcopy(config)
        cfg["rendering"] = t41.get("rendering", cfg["rendering"])
        cfg["max_timestep"] = t41.get("max_timestep", cfg["max_timestep"])
        cfg["save_trajectory"] = t41.get("save_trajectory", cfg["save_trajectory"])

        agent_controller = [AggregationController]
        agent_sensing = [ProximitySensor]

        print("\n🤖 Running Task 4.1: Swarm Aggregation")
        exp = Experiment(
            cfg, agent_controller, agent_sensing, Task41Environment, Task41Agent
        )
        exp.run(rendering=cfg["rendering"])

    # ========================================================================
    # TASK 4.2a: Reynolds Flocking in Toroidal Space
    # ========================================================================
    if config.get("task42a", {}).get("active", False):
        from agent.task42_agent import Task42Agent
        from controller.task42_controller import FlockingController
        from sensors.task42_sensor import FlockingSensor
        from world.task42_world import Task42Environment

        t42a = config["task42a"]
        cfg = deepcopy(config)
        cfg["rendering"] = t42a.get("rendering", cfg["rendering"])
        cfg["max_timestep"] = t42a.get("max_timestep", cfg["max_timestep"])
        cfg["save_trajectory"] = t42a.get("save_trajectory", cfg["save_trajectory"])

        agent_controller = [FlockingController]
        agent_sensing = [FlockingSensor]

        print("\n🤖 Running Task 4.2a: Reynolds Flocking")
        exp = Experiment(
            cfg, agent_controller, agent_sensing, Task42Environment, Task42Agent
        )
        exp.run(rendering=cfg["rendering"])

    # ========================================================================
    # TASK 4.2b: Flocking with Heading Noise - Order Parameter Analysis
    # ========================================================================
    if config.get("task42b", {}).get("active", False):
        from agent.task42_agent import Task42Agent
        from controller.task42_controller import FlockingController
        from sensors.task42_sensor import FlockingSensor
        from utils.plot_flocking import compute_order_parameter, plot_order_vs_noise
        from world.task42_world import Task42Environment

        t42b = config["task42b"]
        cfg_base = deepcopy(config)
        cfg_base["rendering"] = t42b.get("rendering", cfg_base["rendering"])
        cfg_base["max_timestep"] = t42b.get("max_timestep", cfg_base["max_timestep"])
        cfg_base["save_trajectory"] = t42b.get(
            "save_trajectory", cfg_base["save_trajectory"]
        )

        noise_levels = t42b.get("noise_levels", [0.0, 0.5, 1.0])
        runs_per_noise = int(t42b.get("runs_per_noise", 3))

        va_means = []
        completed_runs = 0
        total_runs = len(noise_levels) * runs_per_noise

        print("\n" + "=" * 70)
        print("🤖 TASK 4.2b: Flocking with Heading Noise")
        print("=" * 70)

        try:
            for eta in noise_levels:
                va_runs = []
                print(f"\nNoise intensity η = {eta:.2f}:")
                print("-" * 50)
                for run in range(runs_per_noise):
                    try:
                        print(
                            f"  Run {run + 1}/{runs_per_noise}...", end=" ", flush=True
                        )
                        cfg = deepcopy(cfg_base)
                        cfg["heading_noise"] = float(eta)
                        agent_controller = [FlockingController]
                        agent_sensing = [FlockingSensor]
                        exp = Experiment(
                            cfg,
                            agent_controller,
                            agent_sensing,
                            Task42Environment,
                            Task42Agent,
                        )
                        exp.run(rendering=0)
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
                if len(va_runs) > 0:
                    va_means.append(float(np.mean(va_runs)))
                    print(f"  Average: {va_means[-1]:.4f} ± {np.std(va_runs):.4f}")

            if len(va_means) > 0 and max(va_means) > 0:
                print("\n" + "=" * 70)
                plot_order_vs_noise(noise_levels, va_means)
                print("=" * 70)
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

    # ========================================================================
    # TASK 5.2: Local Sampling in a Swarm
    # ========================================================================
    if config.get("task52", {}).get("active", False):
        import time

        from utils.mp_utils import (
            apply_mp_safety_env,
            resolve_pool_settings,
            run_pool_batches,
            set_low_priority,
        )

        t52 = config["task52"]
        mp_cfg = config.get("multiprocessing", {})  # global defaults

        # Parent-process safety (propagates to children)
        apply_mp_safety_env(blas_threads=str(mp_cfg.get("blas_threads", 1)))
        # task52 can still override if desired
        blas_override = t52.get("blas_threads")
        if blas_override is not None:
            apply_mp_safety_env(blas_threads=str(blas_override))

        SWARM_SIZES = t52["swarm_sizes"]
        SENSOR_RANGES = t52["sensor_ranges"]
        EXPERIMENTS_PER_CONFIG = int(t52["experiments_per_config"])

        cfg_base = deepcopy(config)
        cfg_base["rendering"] = t52.get("rendering", cfg_base["rendering"])
        cfg_base["max_timestep"] = t52.get("max_timestep", cfg_base["max_timestep"])
        cfg_base["save_trajectory"] = t52.get(
            "save_trajectory", cfg_base["save_trajectory"]
        )
        cfg_base["FPS"] = t52.get("FPS", cfg_base["FPS"])

        combos = [
            (N, r, cfg_base, EXPERIMENTS_PER_CONFIG)
            for N in SWARM_SIZES
            for r in SENSOR_RANGES
        ]
        total = len(combos)
        results = {}

        # Safety knobs from global multiprocessing config only
        workers, maxtasks, batch_size, cooldown = resolve_pool_settings(total, mp_cfg)

        print("\n" + "=" * 70)
        print("🤖 TASK 5.2: Local Sampling in a Swarm (multiprocessing)")
        print(
            f"Safety: workers={workers}, maxtasksperchild={maxtasks}, batch_size={batch_size}, cooldown={cooldown}s"
        )
        print("=" * 70)

        start = time.time()
        try:
            completed = 0
            for N, r, estimates in run_pool_batches(
                combos,
                _run_task52_config,
                processes=workers,
                maxtasksperchild=maxtasks,
                batch_size=batch_size,
                cooldown_seconds=cooldown,
                ctx="spawn",
                initializer=set_low_priority,
                unordered=True,
            ):
                results[(N, r)] = estimates
                completed += 1
                if estimates:
                    print(
                        f"[{completed}/{total}] N={N}, r={r:.2f} → {len(estimates)} runs, "
                        f"mean={np.mean(estimates):.4f}, std={np.std(estimates):.4f}",
                        flush=True,
                    )
        except KeyboardInterrupt:
            print(f"\n\n✗ Interrupted by user after {len(results)} configs")
            sys.exit(0)

        elapsed = time.time() - start
        print(f"\n✓ Completed {len(results)} configs in {elapsed / 60:.1f} min")

        if results:
            from utils.plot_sampling import (
                plot_sampling_results,
                print_sampling_summary,
            )

            plot_sampling_results(results, SWARM_SIZES, SENSOR_RANGES)
            print_sampling_summary(results, true_ratio=0.5)
