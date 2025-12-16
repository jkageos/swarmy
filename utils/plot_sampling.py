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

    # Mean vs N for a few r
    fig1, ax1 = plt.subplots(figsize=(10, 6))
    pick_rs = [
        sensor_ranges[0],
        sensor_ranges[len(sensor_ranges) // 2],
        sensor_ranges[-1],
    ]
    for r in pick_rs:
        means = [stats.get((N, r), {}).get("mean", np.nan) for N in swarm_sizes]
        ax1.plot(swarm_sizes, means, "o-", label=f"r = {r:.2f}")
    ax1.axhline(0.5, color="red", linestyle="--", alpha=0.5, label="True ratio (0.5)")
    ax1.set_xlabel("Swarm Size N")
    ax1.set_ylabel("Mean Estimated Black Ratio")
    ax1.set_title("Task 5.2: Mean Estimate vs. Swarm Size")
    ax1.set_ylim(0, 1)
    ax1.grid(True, alpha=0.3)
    ax1.legend()
    fig1.tight_layout()
    p1 = plots_dir / "task52_mean_vs_swarm_size.png"
    fig1.savefig(p1, dpi=300, bbox_inches="tight")
    print(f"✓ Plot saved: {p1}")
    plt.close(fig1)

    # Std vs N
    fig2, ax2 = plt.subplots(figsize=(10, 6))
    for r in pick_rs:
        stds = [stats.get((N, r), {}).get("std", np.nan) for N in swarm_sizes]
        ax2.plot(swarm_sizes, stds, "o-", label=f"r = {r:.2f}")
    ax2.set_xlabel("Swarm Size N")
    ax2.set_ylabel("Standard Deviation of Estimate")
    ax2.set_title("Task 5.2: Estimation Uncertainty")
    ax2.grid(True, alpha=0.3)
    ax2.legend()
    fig2.tight_layout()
    p2 = plots_dir / "task52_std_vs_swarm_size.png"
    fig2.savefig(p2, dpi=300, bbox_inches="tight")
    print(f"✓ Plot saved: {p2}")
    plt.close(fig2)

    # Mean vs r for a few N
    fig3, ax3 = plt.subplots(figsize=(10, 6))
    pick_Ns = [swarm_sizes[0], swarm_sizes[len(swarm_sizes) // 2], swarm_sizes[-1]]
    for N in pick_Ns:
        means = [stats.get((N, r), {}).get("mean", np.nan) for r in sensor_ranges]
        ax3.plot(sensor_ranges, means, "o-", label=f"N = {N}")
    ax3.axhline(0.5, color="red", linestyle="--", alpha=0.5, label="True ratio (0.5)")
    ax3.set_xlabel("Sensor Range r")
    ax3.set_ylabel("Mean Estimated Black Ratio")
    ax3.set_title("Task 5.2: Mean Estimate vs. Sensor Range")
    ax3.set_ylim(0, 1)
    ax3.grid(True, alpha=0.3)
    ax3.legend()
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
