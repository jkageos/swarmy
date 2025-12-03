"""
Potential field visualization utility for Task 3.2
Automatically generates diagrams after simulation
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_task32_trajectory(controller_name, trajectory, potential_field, width, height):
    """
    Generate potential field plot with trajectory overlay for Task 3.2.

    Args:
        controller_name: Name of the controller (e.g., "DirectGradient")
        trajectory: List of (x, y) positions
        potential_field: 2D numpy array of potential values
        width: Environment width
        height: Environment height
    """
    # Create plots directory
    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Subplot 1: Potential field heatmap
    plot_potential_heatmap(ax1, potential_field, width, height)

    # Subplot 2: Trajectory on potential field
    plot_trajectory_on_field(
        ax2, potential_field, trajectory, width, height, controller_name
    )

    plt.tight_layout()

    # Save figure
    output_path = plots_dir / f"task32_{controller_name.lower()}.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Task 3.2 potential field plot saved to: {output_path}")

    plt.close()


def plot_potential_heatmap(ax, potential_field, width, height):
    """Plot potential field as heatmap"""
    im = ax.imshow(
        potential_field.T,
        extent=(0, width, height, 0),  # Changed to tuple
        cmap="RdYlBu_r",
        aspect="auto",
        origin="upper",
    )
    ax.set_title("Potential Field Distribution", fontsize=12, fontweight="bold")
    ax.set_xlabel("X Position (pixels)")
    ax.set_ylabel("Y Position (pixels)")

    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label("Potential Value", rotation=270, labelpad=20)

    # Add labels
    ax.text(
        50,
        50,
        "HIGH\nPOTENTIAL",
        fontsize=10,
        color="white",
        bbox=dict(boxstyle="round", facecolor="red", alpha=0.7),
    )
    ax.text(
        width - 100,
        height - 50,
        "LOW\nPOTENTIAL",
        fontsize=10,
        color="black",
        bbox=dict(boxstyle="round", facecolor="blue", alpha=0.7),
    )


def plot_trajectory_on_field(
    ax, potential_field, trajectory, width, height, controller_name
):
    """Plot trajectory overlaid on potential field"""
    # Background
    ax.imshow(
        potential_field.T,
        extent=(0, width, height, 0),  # Changed to tuple
        cmap="RdYlBu_r",
        aspect="auto",
        origin="upper",
        alpha=0.5,
    )

    # Plot trajectory if available
    if trajectory and len(trajectory) > 0:
        trajectory_array = np.array(trajectory)

        # Trajectory line
        ax.plot(
            trajectory_array[:, 0],
            trajectory_array[:, 1],
            "lime",
            linewidth=2,
            label="Robot trajectory",
            zorder=5,
        )
        ax.plot(
            trajectory_array[0, 0],
            trajectory_array[0, 1],
            "go",
            markersize=12,
            label="Start",
            zorder=6,
        )
        ax.plot(
            trajectory_array[-1, 0],
            trajectory_array[-1, 1],
            "ro",
            markersize=12,
            label="End",
            zorder=6,
        )

        # Calculate statistics
        start_x, start_y = trajectory_array[0]
        end_x, end_y = trajectory_array[-1]
        start_pot = potential_field[int(start_x), int(start_y)]
        end_pot = potential_field[int(end_x), int(end_y)]

        # Add statistics
        stats_text = (
            f"Potential descent: {start_pot - end_pot:.1f}\n"
            f"Path length: {len(trajectory)} steps\n"
            f"Start: {start_pot:.1f} → End: {end_pot:.1f}"
        )

        ax.text(
            0.02,
            0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
        )

    ax.set_title(f"Task 3.2: {controller_name} Control", fontsize=12, fontweight="bold")
    ax.set_xlabel("X Position (pixels)")
    ax.set_ylabel("Y Position (pixels)")
    ax.legend(loc="upper right")


def plot_gradient_field(potential_field, width, height):
    """
    Generate gradient vector field visualization (optional, for analysis)

    Args:
        potential_field: 2D numpy array
        width: Environment width
        height: Environment height
    """
    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 8))

    # Sample gradient vectors
    step = 40
    X, Y = np.meshgrid(
        range(step, width - step, step), range(step, height - step, step)
    )

    U = np.zeros_like(X, dtype=float)
    V = np.zeros_like(Y, dtype=float)

    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            grad_x, grad_y = get_gradient(
                potential_field, X[i, j], Y[i, j], width, height
            )
            U[i, j] = -grad_x
            V[i, j] = -grad_y

    # Background
    ax.imshow(
        potential_field.T,
        extent=(0, width, height, 0),  # Changed to tuple
        cmap="RdYlBu_r",
        aspect="auto",
        origin="upper",
        alpha=0.4,
    )

    # Gradient vectors
    ax.quiver(X, Y, U, V, color="black", alpha=0.6, scale=800)

    ax.set_title(
        "Gradient Vector Field (descent direction)", fontsize=12, fontweight="bold"
    )
    ax.set_xlabel("X Position (pixels)")
    ax.set_ylabel("Y Position (pixels)")

    plt.tight_layout()

    output_path = plots_dir / "task32_gradient_field.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Gradient field plot saved to: {output_path}")

    plt.close()


def get_gradient(potential_field, x, y, width, height):
    """Calculate gradient at position (x, y)"""
    i = int(np.clip(x, 1, width - 2))
    j = int(np.clip(y, 1, height - 2))

    grad_x = potential_field[i, j] - potential_field[i + 1, j]
    grad_y = potential_field[i, j] - potential_field[i, j + 1]

    return grad_x, grad_y
