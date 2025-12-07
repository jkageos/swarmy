"""
Flocking analysis and visualization utilities for Task 4.2
"""

from pathlib import Path

import numpy as np


def compute_order_parameter(agentlist):
    """
    Compute global order parameter (average normalized velocity).

    Args:
        agentlist: List of agents in the swarm

    Returns:
        va: Order parameter (float between 0 and 1)
    """
    if not agentlist or len(agentlist) == 0:
        return 0.0

    velocities = []
    for agent in agentlist:
        if hasattr(agent.actuation, "velocity"):
            velocities.append(agent.actuation.velocity)

    if not velocities:
        return 0.0

    velocities = np.array(velocities)

    # Normalize each velocity to unit vector
    v_norm = np.linalg.norm(velocities, axis=1, keepdims=True)
    v_norm = np.where(v_norm == 0, 1, v_norm)  # Avoid division by zero
    v_hat = velocities / v_norm

    # Compute mean of normalized vectors
    mean_vec = v_hat.mean(axis=0)
    va = np.linalg.norm(mean_vec)

    return float(va)


def compute_and_plot_order_parameter(agentlist, config):
    """
    Compute and plot the final order parameter for a simulation.

    Args:
        agentlist: List of agents
        config: Configuration dictionary
    """
    va = compute_order_parameter(agentlist)

    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

    eta = config.get("heading_noise", 0.0)

    print(f"✓ Final order parameter (η={eta:.2f}): {va:.4f}")

    return va


def plot_order_vs_noise(noise_levels, va_values):
    """
    Plot order parameter as function of noise intensity.

    Args:
        noise_levels: Array of noise intensities
        va_values: Array of corresponding order parameters (averaged over runs)
    """
    # MOVED IMPORT HERE: Only import matplotlib when plotting
    import matplotlib.pyplot as plt

    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 6))

    ax.plot(
        noise_levels,
        va_values,
        "o-",
        linewidth=2,
        markersize=8,
        color="steelblue",
        label="Order parameter",
    )

    ax.set_xlabel("Noise Intensity η (radians)", fontsize=12)
    ax.set_ylabel("Order Parameter $v_a$", fontsize=12)
    ax.set_title(
        "Flocking Order Parameter vs. Heading Noise", fontsize=14, fontweight="bold"
    )
    ax.grid(True, alpha=0.3)
    ax.set_ylim(0, 1.05)
    ax.legend(fontsize=11)

    # Add annotations
    ax.text(
        0.02,
        0.98,
        f"N = {len(noise_levels)} noise levels\nMultiple runs averaged",
        transform=ax.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    plt.tight_layout()

    output_path = plots_dir / "task42_order_parameter.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Order parameter plot saved to: {output_path}")

    plt.close()


def plot_flocking_trajectories(agentlist, world_width, world_height):
    """
    Plot trajectories of all agents in the swarm.

    Args:
        agentlist: List of agents
        world_width: Width of arena
        world_height: Height of arena
    """
    # MOVED IMPORT HERE: Only import matplotlib when plotting
    import matplotlib.pyplot as plt

    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 10))

    # Plot trajectories for a subset of robots (for clarity)
    num_to_plot = min(5, len(agentlist))
    colors = plt.colormaps["tab10"](np.linspace(0, 1, num_to_plot))

    for idx in range(num_to_plot):
        agent = agentlist[idx]
        if (
            hasattr(agent.actuation, "trajectory")
            and len(agent.actuation.trajectory) > 10
        ):
            traj = np.array(agent.actuation.trajectory)
            ax.plot(
                traj[:, 0],
                traj[:, 1],
                "-",
                color=colors[idx],
                alpha=0.6,
                linewidth=1,
                label=f"Robot {agent.unique_id}",
            )
            ax.plot(
                traj[0, 0],
                traj[0, 1],
                "o",
                color=colors[idx],
                markersize=8,
                zorder=5,
            )

    # Draw arena boundary (visual reference only)
    ax.plot(
        [0, world_width, world_width, 0, 0],
        [0, 0, world_height, world_height, 0],
        "k--",
        linewidth=1,
        alpha=0.5,
    )

    ax.set_xlim(-50, world_width + 50)
    ax.set_ylim(-50, world_height + 50)
    ax.set_aspect("equal")
    ax.set_xlabel("X Position (pixels)", fontsize=11)
    ax.set_ylabel("Y Position (pixels)", fontsize=11)
    ax.set_title(
        "Flocking Trajectories (Toroidal Space)", fontsize=13, fontweight="bold"
    )
    ax.legend(loc="upper right", fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()

    output_path = plots_dir / "task42_trajectories.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Trajectories plot saved to: {output_path}")

    plt.close()
