"""
Local sampling analysis and visualization for Task 5.2
"""

import matplotlib

matplotlib.use("Agg")  # headless backend to avoid Tk iconphoto issues
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


def plot_sampling_results(results, swarm_sizes, sensor_ranges):
    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

    stats = {}
    for (N, r), vals in results.items():
        arr = np.array(vals, dtype=float)
        stats[(N, r)] = {"mean": float(np.mean(arr)), "std": float(np.std(arr))}

    # Mean vs N (plot all sensor ranges)
    fig1, ax1 = plt.subplots(figsize=(10, 6))

    all_means_n = []
    for r in sensor_ranges:
        means = [stats.get((N, r), {}).get("mean", np.nan) for N in swarm_sizes]
        all_means_n.extend([m for m in means if not np.isnan(m)])
        ax1.plot(swarm_sizes, means, "o-", label=f"r = {r:.2f}")

    ax1.axhline(0.5, color="red", linestyle="--", alpha=0.5, label="True ratio (0.5)")
    ax1.set_xlabel("Swarm Size N")
    ax1.set_ylabel("Mean Estimated Black Ratio")
    ax1.set_title("Task 5.2: Mean Estimate vs. Swarm Size")

    # Tight y-axis (barely visible min/max)
    if all_means_n:
        y_min_val = float(np.nanmin(all_means_n))
        y_max_val = float(np.nanmax(all_means_n))
        span = max(1e-12, y_max_val - y_min_val)
        pad = max(0.001, 0.005 * span)
        y0 = max(0.0, y_min_val - pad)
        y1 = min(1.0, y_max_val + pad)
        if y1 - y0 < 2 * 0.001:  # guard nearly-constant case
            c = 0.5 * (y_min_val + y_max_val)
            y0 = max(0.0, c - 0.001)
            y1 = min(1.0, c + 0.001)
        ax1.set_ylim(y0, y1)
    else:
        ax1.set_ylim(0, 1)

    # Tight x-axis
    x_margin = max(1, (max(swarm_sizes) - min(swarm_sizes)) * 0.01)
    ax1.set_xlim(min(swarm_sizes) - x_margin, max(swarm_sizes) + x_margin)

    ax1.grid(True, alpha=0.3)
    ax1.legend(ncol=2)
    fig1.tight_layout()
    p1 = plots_dir / "task52_mean_vs_swarm_size.png"
    fig1.savefig(p1, dpi=300, bbox_inches="tight")
    print(f"✓ Plot saved: {p1}")
    plt.close(fig1)

    # Std vs N (plot all sensor ranges)
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    all_stds = []
    for r in sensor_ranges:
        stds = [stats.get((N, r), {}).get("std", np.nan) for N in swarm_sizes]
        all_stds.extend([s for s in stds if not np.isnan(s)])
        ax2.plot(swarm_sizes, stds, "o-", label=f"r = {r:.2f}")

    ax2.set_xlabel("Swarm Size N")
    ax2.set_ylabel("Standard Deviation of Estimate")
    ax2.set_title("Task 5.2: Estimation Uncertainty")

    # Tight y-axis (unchanged for std)
    if all_stds:
        max_std = float(np.nanmax(all_stds))
        pad = max(0.002, 0.02 * max_std)
        ax2.set_ylim(0, max_std + pad)
    else:
        ax2.set_ylim(0, 0.5)

    # Tight x-axis
    ax2.set_xlim(min(swarm_sizes) - x_margin, max(swarm_sizes) + x_margin)

    ax2.grid(True, alpha=0.3)
    ax2.legend(ncol=2)
    fig2.tight_layout()
    p2 = plots_dir / "task52_std_vs_swarm_size.png"
    fig2.savefig(p2, dpi=300, bbox_inches="tight")
    print(f"✓ Plot saved: {p2}")
    plt.close(fig2)

    # Mean vs r (plot all swarm sizes)
    fig3, ax3 = plt.subplots(figsize=(10, 6))

    all_means_r = []
    for N in swarm_sizes:
        means = [stats.get((N, r), {}).get("mean", np.nan) for r in sensor_ranges]
        all_means_r.extend([m for m in means if not np.isnan(m)])
        ax3.plot(sensor_ranges, means, "o-", label=f"N = {N}")

    ax3.axhline(0.5, color="red", linestyle="--", alpha=0.5, label="True ratio (0.5)")
    ax3.set_xlabel("Sensor Range r")
    ax3.set_ylabel("Mean Estimated Black Ratio")
    ax3.set_title("Task 5.2: Mean Estimate vs. Sensor Range")

    # Tight y-axis (barely visible min/max)
    if all_means_r:
        y_min_val = float(np.nanmin(all_means_r))
        y_max_val = float(np.nanmax(all_means_r))
        span = max(1e-12, y_max_val - y_min_val)
        pad = max(0.001, 0.005 * span)
        y0 = max(0.0, y_min_val - pad)
        y1 = min(1.0, y_max_val + pad)
        if y1 - y0 < 2 * 0.001:
            c = 0.5 * (y_min_val + y_max_val)
            y0 = max(0.0, c - 0.001)
            y1 = min(1.0, c + 0.001)
        ax3.set_ylim(y0, y1)
    else:
        ax3.set_ylim(0, 1)

    # Tight x-axis
    r_margin = max(0.001, (max(sensor_ranges) - min(sensor_ranges)) * 0.01)
    ax3.set_xlim(min(sensor_ranges) - r_margin, max(sensor_ranges) + r_margin)

    ax3.grid(True, alpha=0.3)
    ax3.legend(ncol=2)
    fig3.tight_layout()
    p3 = plots_dir / "task52_mean_vs_sensor_range.png"
    fig3.savefig(p3, dpi=300, bbox_inches="tight")
    print(f"✓ Plot saved: {p3}")
    plt.close(fig3)


def print_sampling_summary(results, true_ratio=0.5):
    all_vals = []
    for v in results.values():
        all_vals.extend(v)
    arr = np.array(all_vals, dtype=float)

    print("\n" + "=" * 70)
    print("LOCAL SAMPLING SUMMARY")
    print("=" * 70)
    print(f"  True black ratio: {true_ratio:.4f}")
    print(f"  Mean estimate: {float(np.mean(arr)):.4f}")
    print(f"  Std deviation: {float(np.std(arr)):.4f}")
    print(f"  Total experiments: {len(arr)}")
