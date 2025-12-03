"""
Trajectory visualization utility for Task 3.1
Automatically generates characteristic diagrams after simulation
"""

from pathlib import Path

import matplotlib.patches as patches
import matplotlib.pyplot as plt
import numpy as np


def plot_task31_trajectory(controller_name, trajectory, arena_width, arena_height):
    """
    Generate trajectory plot for a specific Task 3.1 behavior.

    Args:
        controller_name: Name of the controller (e.g., "CollisionAvoidance")
        trajectory: List of (x, y) positions
        arena_width: Width of the arena
        arena_height: Height of the arena
    """
    # Create plots directory
    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Setup arena
    ax.set_xlim(0, arena_width)
    ax.set_ylim(0, arena_height)
    ax.set_aspect("equal")
    ax.set_title(
        f"Task 3.1: {controller_name} Behavior", fontsize=14, fontweight="bold"
    )
    ax.set_xlabel("X Position (pixels)")
    ax.set_ylabel("Y Position (pixels)")
    ax.grid(True, alpha=0.3)

    # Draw walls
    wall_rect = patches.Rectangle(
        (5, 5),
        arena_width - 10,
        arena_height - 10,
        linewidth=3,
        edgecolor="black",
        facecolor="none",
    )
    ax.add_patch(wall_rect)

    # Draw obstacles
    obstacles = [
        patches.Rectangle(
            (arena_width // 3, arena_height // 3),
            80,
            10,
            facecolor="gray",
            edgecolor="black",
            alpha=0.7,
        ),
        patches.Rectangle(
            (arena_width // 2 + 60, arena_height // 2 - 40),
            10,
            90,
            facecolor="gray",
            edgecolor="black",
            alpha=0.7,
        ),
        patches.Rectangle(
            (arena_width // 4 + 30, arena_height // 2 + 60),
            120,
            10,
            facecolor="gray",
            edgecolor="black",
            alpha=0.7,
        ),
    ]
    for obs in obstacles:
        ax.add_patch(obs)

    # Plot trajectory if available
    if trajectory and len(trajectory) > 0:
        trajectory_array = np.array(trajectory)

        # Draw trajectory line
        ax.plot(
            trajectory_array[:, 0],
            trajectory_array[:, 1],
            "b-",
            linewidth=1.5,
            alpha=0.6,
            label="Robot path",
        )

        # Mark start and end
        ax.plot(
            trajectory_array[0, 0],
            trajectory_array[0, 1],
            "go",
            markersize=12,
            label="Start",
            zorder=5,
        )
        ax.plot(
            trajectory_array[-1, 0],
            trajectory_array[-1, 1],
            "ro",
            markersize=12,
            label="End",
            zorder=5,
        )

        # Add statistics
        path_length = len(trajectory)
        coverage = estimate_coverage(trajectory_array, arena_width, arena_height)

        stats_text = f"Path length: {path_length} steps\nArea coverage: {coverage:.1f}%"
        ax.text(
            0.02,
            0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=10,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

    ax.legend(loc="upper right")

    plt.tight_layout()

    # Save figure
    output_path = plots_dir / f"task31_{controller_name.lower()}.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Task 3.1 trajectory plot saved to: {output_path}")

    plt.close()


def estimate_coverage(trajectory, width, height, grid_size=20):
    """
    Estimate percentage of arena covered by robot trajectory

    Args:
        trajectory: Nx2 array of positions
        width: Arena width
        height: Arena height
        grid_size: Size of grid cells for coverage estimation
    """
    # Create grid
    grid_x = width // grid_size
    grid_y = height // grid_size
    visited = np.zeros((grid_x, grid_y), dtype=bool)

    # Mark visited cells
    for x, y in trajectory:
        grid_i = int(np.clip(x / grid_size, 0, grid_x - 1))
        grid_j = int(np.clip(y / grid_size, 0, grid_y - 1))
        visited[grid_i, grid_j] = True

    # Calculate coverage percentage
    total_cells = grid_x * grid_y
    visited_cells = np.sum(visited)
    coverage = (visited_cells / total_cells) * 100

    return coverage
