"""
Plotting utilities for trajectory visualization and analysis.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # set backend before importing pyplot
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.collections import LineCollection
from matplotlib.patches import Circle, Rectangle


def plot_trajectory(
    trajectory, agent_id, config, light_source=None, walls=None, save_path="plots"
):
    """
    Plot a single agent's trajectory on the toroidal world.

    Args:
        trajectory (list): List of (x, y, gamma) tuples
        agent_id (int): Unique identifier for the agent
        config (dict): Configuration dictionary with world dimensions
        light_source (tuple): Optional (x, y, radius) for light source visualization
        walls (list): Optional list of wall rectangles from environment
        save_path (str): Directory to save the plot
    """
    if not trajectory:
        print(f"Agent {agent_id}: No trajectory data to plot")
        return

    # Create output directory
    Path(save_path).mkdir(parents=True, exist_ok=True)

    # Extract x, y coordinates
    x_coords = [pos[0] for pos in trajectory]
    y_coords = [pos[1] for pos in trajectory]

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Draw walls/obstacles first (so they're in the background)
    if walls:
        for wall_data in walls:
            color_name = wall_data[0]
            rect = wall_data[1]  # pygame.Rect object

            # Convert color names to matplotlib colors
            if color_name == "BLACK":
                mpl_color = "black"
            elif color_name == "RED":
                mpl_color = "red"
            else:
                mpl_color = "gray"

            # Draw rectangle
            patch = Rectangle(
                (rect.x, rect.y),
                rect.width,
                rect.height,
                linewidth=1,
                edgecolor=mpl_color,
                facecolor=mpl_color,
                alpha=0.7,
            )
            ax.add_patch(patch)

    if len(trajectory) >= 2:
        # Ensure float dtype and proper shape (N-1, 2, 2)
        points = np.column_stack((x_coords, y_coords)).astype(float)
        segments = np.stack([points[:-1], points[1:]], axis=1)

        # Convert to a Python list to satisfy static type checkers
        lc = LineCollection(segments.tolist(), cmap="viridis", linewidth=2)
        lc.set_array(np.linspace(0, 1, len(segments)))
        ax.add_collection(lc)
        plt.colorbar(lc, ax=ax, label="Time (normalized)")
    else:
        ax.plot(
            x_coords, y_coords, "o", color="tab:blue", markersize=6, label="Position"
        )

    # Mark start and end positions
    ax.plot(x_coords[0], y_coords[0], "go", markersize=10, label="Start", zorder=5)
    ax.plot(x_coords[-1], y_coords[-1], "ro", markersize=10, label="End", zorder=5)

    # Draw light source if provided
    if light_source:
        lx, ly, radius = light_source
        circle = Circle(
            (lx, ly), radius, color="yellow", alpha=0.3, label="Light field"
        )
        ax.add_patch(circle)
        ax.plot(lx, ly, "y*", markersize=15, label="Light source", zorder=6)

    # Set limits and labels
    ax.set_xlim(0, config["world_width"])
    ax.set_ylim(0, config["world_height"])
    ax.set_xlabel("X Position (pixels)", fontsize=12)
    ax.set_ylabel("Y Position (pixels)", fontsize=12)

    world_type = "Bounded World with Walls" if walls else "Toroidal World"
    ax.set_title(
        f"Agent {agent_id} Trajectory ({world_type})\n{len(trajectory)} timesteps",
        fontsize=14,
    )
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal")

    # Save figure
    filename = f"{save_path}/trajectory_agent_{agent_id}.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    print(f"Saved trajectory plot: {filename}")
    plt.close()


def plot_light_distribution(config, world, save_path="plots"):
    """
    Plot the light intensity distribution in the world.

    Args:
        config (dict): Configuration dictionary
        world (Environment): World/environment instance with light_intensity_at method
        save_path (str): Directory to save the plot
    """
    Path(save_path).mkdir(parents=True, exist_ok=True)

    width = config["world_width"]
    height = config["world_height"]

    # Create grid
    resolution = 5  # Sample every 5 pixels for performance
    x = np.arange(0, width, resolution)
    y = np.arange(0, height, resolution)
    X, Y = np.meshgrid(x, y)

    # Calculate light intensity at each point
    Z = np.zeros_like(X, dtype=float)
    for i in range(X.shape[0]):
        for j in range(X.shape[1]):
            Z[i, j] = world.light_intensity_at((X[i, j], Y[i, j]))

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot heatmap
    contour = ax.contourf(X, Y, Z, levels=20, cmap="hot")

    # Mark light source
    if hasattr(world, "light_pos"):
        lx, ly = world.light_pos
        ax.plot(lx, ly, "y*", markersize=20, label="Light source", zorder=5)

        # Draw light radius
        if hasattr(world, "light_radius"):
            circle = Circle(
                (lx, ly),
                world.light_radius,
                color="white",
                fill=False,
                linestyle="--",
                linewidth=2,
                label="Light radius",
            )
            ax.add_patch(circle)

    # Labels and title
    ax.set_xlabel("X Position (pixels)", fontsize=12)
    ax.set_ylabel("Y Position (pixels)", fontsize=12)
    ax.set_title("Light Intensity Distribution (Cone-shaped on Torus)", fontsize=14)
    ax.legend(loc="upper right")

    # Colorbar
    plt.colorbar(contour, ax=ax, label="Light Intensity")

    # Save
    filename = f"{save_path}/light_distribution.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    print(f"Saved light distribution plot: {filename}")
    plt.close()


def plot_all_trajectories(
    agent_list, config, light_source=None, walls=None, save_path="plots"
):
    """
    Plot all agent trajectories on a single figure.

    Args:
        agent_list (list): List of agent objects with trajectory attribute
        config (dict): Configuration dictionary
        light_source (tuple): Optional (x, y, radius) for light source
        walls (list): Optional list of wall rectangles from environment
        save_path (str): Directory to save the plot
    """
    Path(save_path).mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 9))

    # Draw walls/obstacles first (background layer)
    if walls:
        for wall_data in walls:
            color_name = wall_data[0]
            rect = wall_data[1]  # pygame.Rect object

            # Convert color names to matplotlib colors
            if color_name == "BLACK":
                mpl_color = "black"
            elif color_name == "RED":
                mpl_color = "red"
            else:
                mpl_color = "gray"

            # Draw rectangle
            patch = Rectangle(
                (rect.x, rect.y),
                rect.width,
                rect.height,
                linewidth=1,
                edgecolor=mpl_color,
                facecolor=mpl_color,
                alpha=0.7,
            )
            ax.add_patch(patch)

    # Replace attribute access with get_cmap to satisfy type checkers and older Matplotlib
    cmap = plt.cm.get_cmap(
        "tab10"
    )  # or: plt.cm.get_cmap("tab20") for more distinct colors

    for idx, agent in enumerate(agent_list):
        if not agent.trajectory:
            continue

        x_coords = [pos[0] for pos in agent.trajectory]
        y_coords = [pos[1] for pos in agent.trajectory]

        color = cmap(idx % cmap.N)

        # Plot trajectory
        ax.plot(
            x_coords,
            y_coords,
            color=color,
            alpha=0.7,
            linewidth=1.5,
            label=f"Agent {agent.unique_id}",
        )

        # Mark start
        ax.plot(
            x_coords[0],
            y_coords[0],
            "o",
            color=color,
            markersize=8,
            markeredgecolor="black",
            markeredgewidth=1,
        )

    # Draw light source
    if light_source:
        lx, ly, radius = light_source
        circle = Circle((lx, ly), radius, color="yellow", alpha=0.2)
        ax.add_patch(circle)
        ax.plot(lx, ly, "y*", markersize=20, label="Light source", zorder=10)

    # Set limits and labels
    ax.set_xlim(0, config["world_width"])
    ax.set_ylim(0, config["world_height"])
    ax.set_xlabel("X Position (pixels)", fontsize=12)
    ax.set_ylabel("Y Position (pixels)", fontsize=12)

    world_type = "Bounded World with Walls" if walls else "Toroidal World"
    ax.set_title(f"All Agent Trajectories ({world_type})", fontsize=14)
    ax.legend(loc="upper right", fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal")

    # Save
    filename = f"{save_path}/all_trajectories.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    print(f"Saved combined trajectory plot: {filename}")
    plt.close()


def plot_task4_trajectory(
    trajectory, agent_id, run_id, config, walls=None, save_path="plots/task4"
):
    """
    Plot a single agent's trajectory for Task 4, including run index in filename and title.

    Args:
        trajectory (list): List of (x, y, gamma) tuples
        agent_id (int): Unique identifier for the agent
        run_id (int): Run index
        config (dict): Configuration dictionary with world dimensions
        walls (list): Optional list of wall rectangles from environment
        save_path (str): Directory to save the plot
    """
    if not trajectory:
        print(f"Agent {agent_id}, Run {run_id}: No trajectory data to plot")
        return

    from pathlib import Path

    import matplotlib.pyplot as plt
    import numpy as np
    from matplotlib.collections import LineCollection
    from matplotlib.patches import Rectangle

    Path(save_path).mkdir(parents=True, exist_ok=True)

    x_coords = [pos[0] for pos in trajectory]
    y_coords = [pos[1] for pos in trajectory]

    fig, ax = plt.subplots(figsize=(10, 8))

    if walls:
        for wall_data in walls:
            color_name = wall_data[0]
            rect = wall_data[1]
            mpl_color = "black" if color_name == "BLACK" else "red"
            patch = Rectangle(
                (rect.x, rect.y),
                rect.width,
                rect.height,
                linewidth=1,
                edgecolor=mpl_color,
                facecolor=mpl_color,
                alpha=0.7,
            )
            ax.add_patch(patch)

    if len(trajectory) >= 2:
        points = np.column_stack((x_coords, y_coords)).astype(float)
        segments = np.stack([points[:-1], points[1:]], axis=1)
        lc = LineCollection(segments.tolist(), cmap="viridis", linewidth=2)
        lc.set_array(np.linspace(0, 1, len(segments)))
        ax.add_collection(lc)
        plt.colorbar(lc, ax=ax, label="Time (normalized)")
    else:
        ax.plot(
            x_coords, y_coords, "o", color="tab:blue", markersize=6, label="Position"
        )

    ax.plot(x_coords[0], y_coords[0], "go", markersize=10, label="Start", zorder=5)
    ax.plot(x_coords[-1], y_coords[-1], "ro", markersize=10, label="End", zorder=5)

    ax.set_xlim(0, config["world_width"])
    ax.set_ylim(0, config["world_height"])
    ax.set_xlabel("X Position (pixels)", fontsize=12)
    ax.set_ylabel("Y Position (pixels)", fontsize=12)

    ax.set_title(
        f"Task 4 Agent {agent_id} Trajectory (Run {run_id})\n{len(trajectory)} timesteps",
        fontsize=14,
    )
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)
    ax.set_aspect("equal")

    filename = f"{save_path}/trajectory_agent_{agent_id}_run_{run_id}.png"
    plt.savefig(filename, dpi=150, bbox_inches="tight")
    print(f"Saved trajectory plot: {filename}")
    plt.close()
