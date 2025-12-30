"""
Analysis utilities for Task 6 anti-agent experiments
"""

import math
from pathlib import Path
from typing import Dict, List

import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend
import matplotlib.pyplot as plt
import numpy as np


def detect_clusters(agent_list, cluster_distance=100):
    """
    Detect clusters using distance-based clustering.
    Returns list of cluster sizes, sorted in descending order.

    Args:
        agent_list: List of all agents
        cluster_distance: Maximum distance between agents in a cluster

    Returns:
        List of cluster sizes, sorted in descending order
    """
    visited = set()
    clusters = []

    for agent in agent_list:
        if agent.unique_id in visited:
            continue

        # BFS to find connected agents
        cluster = set()
        queue = [agent]

        while queue:
            current = queue.pop(0)
            if current.unique_id in visited:
                continue

            visited.add(current.unique_id)
            cluster.add(current.unique_id)

            cx, cy, _ = current.get_position()

            # Find neighbors within cluster_distance
            for other in agent_list:
                if other.unique_id in visited:
                    continue

                ox, oy, _ = other.get_position()
                dist = math.sqrt((cx - ox) ** 2 + (cy - oy) ** 2)

                if dist < cluster_distance:
                    queue.append(other)

        if cluster:
            clusters.append(len(cluster))

    return sorted(clusters, reverse=True)


def compute_clustering_metrics(agent_list, cluster_distance=100):
    """
    Compute various clustering metrics.

    Returns:
        Dictionary with metrics: max_cluster, num_clusters, avg_cluster_size, etc.
    """
    clusters = detect_clusters(agent_list, cluster_distance)

    if not clusters:
        return {
            "max_cluster": 0,
            "num_clusters": 0,
            "avg_cluster_size": 0,
            "total_agents": len(agent_list),
            "clustered_agents": 0,
            "cluster_distribution": [],
        }

    return {
        "max_cluster": clusters[0],
        "num_clusters": len(clusters),
        "avg_cluster_size": np.mean(clusters),
        "total_agents": len(agent_list),
        "clustered_agents": sum(clusters),
        "cluster_distribution": clusters,
    }


def plot_task6_results(
    results: List[Dict], output_filename="task6_anti_agent_results.png"
):
    """
    Plot the effect of anti-agent percentage on clustering performance.

    Args:
        results: List of result dictionaries from experiments
        output_filename: Name of output plot file
    """
    if not results:
        print("⚠️  No results to plot!")
        return

    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

    # Extract data
    percentages = [r["anti_agent_percentage"] for r in results]
    max_clusters = [r["avg_max_cluster_size"] for r in results]
    std_devs = [r.get("std_max_cluster_size", 0) for r in results]

    # Create figure with multiple subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

    # Plot 1: Max cluster size with error bars
    ax1.errorbar(
        percentages,
        max_clusters,
        yerr=std_devs,
        marker="o",
        markersize=8,
        linewidth=2,
        capsize=5,
        capthick=2,
        color="steelblue",
        label="Max Cluster Size",
    )

    ax1.set_xlabel("Anti-Agent Percentage (%)", fontsize=12, fontweight="bold")
    ax1.set_ylabel("Average Max Cluster Size", fontsize=12, fontweight="bold")
    ax1.set_title(
        "Task 6: Effect of Anti-Agents on Swarm Aggregation",
        fontsize=14,
        fontweight="bold",
    )
    ax1.grid(True, alpha=0.3)
    ax1.legend(fontsize=11)

    # Add annotation
    num_runs = (
        len(results[0]["max_cluster_sizes"])
        if results and results[0].get("max_cluster_sizes")
        else 0
    )
    ax1.text(
        0.02,
        0.98,
        f"Runs per config: {num_runs}\nError bars: ±1 std dev",
        transform=ax1.transAxes,
        fontsize=10,
        verticalalignment="top",
        bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8),
    )

    # Plot 2: Relative performance (normalized to baseline)
    if results and len(results) > 0:
        baseline = results[0]["avg_max_cluster_size"]
        if baseline > 0:
            relative_performance = [
                (r["avg_max_cluster_size"] / baseline) * 100 for r in results
            ]
            relative_std = [
                (r.get("std_max_cluster_size", 0) / baseline) * 100 for r in results
            ]

            ax2.errorbar(
                percentages,
                relative_performance,
                yerr=relative_std,
                marker="s",
                markersize=8,
                linewidth=2,
                capsize=5,
                capthick=2,
                color="darkgreen",
                label="Relative Performance",
            )

            ax2.axhline(
                100, color="red", linestyle="--", alpha=0.5, label="Baseline (0% anti)"
            )
            ax2.set_xlabel("Anti-Agent Percentage (%)", fontsize=12, fontweight="bold")
            ax2.set_ylabel("Relative Performance (%)", fontsize=12, fontweight="bold")
            ax2.set_title(
                "Task 6: Relative Clustering Performance",
                fontsize=14,
                fontweight="bold",
            )
            ax2.grid(True, alpha=0.3)
            ax2.legend(fontsize=11)

            # Highlight optimal percentage
            best_idx = np.argmax(relative_performance)
            best_pct = percentages[best_idx]
            best_val = relative_performance[best_idx]
            ax2.plot(
                best_pct, best_val, "r*", markersize=20, label=f"Best: {best_pct}%"
            )

            ax2.text(
                0.02,
                0.02,
                f"Optimal: {best_pct}% anti-agents\nPerformance: {best_val:.1f}%",
                transform=ax2.transAxes,
                fontsize=10,
                verticalalignment="bottom",
                bbox=dict(boxstyle="round", facecolor="lightgreen", alpha=0.8),
            )

    plt.tight_layout()

    output_path = plots_dir / output_filename
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Task 6 results plot saved to: {output_path}")

    plt.close()


def plot_cluster_distribution(results: List[Dict]):
    """
    Plot cluster size distribution for different anti-agent percentages.

    Args:
        results: List of result dictionaries from experiments
    """
    if not results:
        print("⚠️  No results to plot!")
        return

    plots_dir = Path("plots")
    plots_dir.mkdir(exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 6))

    # Plot box plots for each percentage
    percentages = [r["anti_agent_percentage"] for r in results]
    cluster_data = [r["max_cluster_sizes"] for r in results]

    positions = list(range(len(percentages)))
    bp = ax.boxplot(
        cluster_data,
        positions=positions,
        widths=0.6,
        patch_artist=True,
        showmeans=True,
        meanline=True,
    )

    # Color boxes
    for patch in bp["boxes"]:
        patch.set_facecolor("lightblue")
        patch.set_alpha(0.7)

    ax.set_xticks(positions)
    ax.set_xticklabels([f"{p}%" for p in percentages])
    ax.set_xlabel("Anti-Agent Percentage", fontsize=12, fontweight="bold")
    ax.set_ylabel("Max Cluster Size", fontsize=12, fontweight="bold")
    ax.set_title(
        "Task 6: Distribution of Max Cluster Sizes", fontsize=14, fontweight="bold"
    )
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()

    output_path = plots_dir / "task6_cluster_distribution.png"
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    print(f"✓ Task 6 distribution plot saved to: {output_path}")

    plt.close()


def print_task6_summary(results: List[Dict]):
    """
    Print a summary table of Task 6 results.

    Args:
        results: List of result dictionaries from experiments
    """
    if not results:
        print("⚠️  No results to summarize!")
        return

    print("\n" + "=" * 90)
    print("TASK 6: ANTI-AGENT SWARM AGGREGATION - RESULTS SUMMARY")
    print("=" * 90)
    print(
        f"{'Anti-Agents %':<20} {'Max Cluster (mean)':<25} {'Std Dev':<15} {'Improvement':<15} {'Runs':<10}"
    )
    print("-" * 90)

    baseline = None
    for result in results:
        pct = result["anti_agent_percentage"]
        mean_val = result["avg_max_cluster_size"]
        std_val = result.get("std_max_cluster_size", 0)
        num_runs = len(result.get("max_cluster_sizes", []))

        if baseline is None:
            baseline = mean_val
            improvement = "—"
        else:
            diff = mean_val - baseline
            pct_change = ((mean_val - baseline) / baseline * 100) if baseline > 0 else 0
            improvement = f"{diff:+.2f} ({pct_change:+.1f}%)"

        print(
            f"{pct:<20.1f} {mean_val:<25.2f} {std_val:<15.2f} {improvement:<15} {num_runs:<10}"
        )

    print("=" * 90)
    print()

    # Find best configuration
    best_result = max(results, key=lambda r: r["avg_max_cluster_size"])
    baseline_result = results[0]

    print(
        f"✓ Best performance: {best_result['anti_agent_percentage']:.1f}% anti-agents"
    )
    print(
        f"  Max cluster size: {best_result['avg_max_cluster_size']:.2f} ± {best_result.get('std_max_cluster_size', 0):.2f}"
    )

    if baseline_result["avg_max_cluster_size"] > 0:
        improvement = (
            (
                best_result["avg_max_cluster_size"]
                - baseline_result["avg_max_cluster_size"]
            )
            / baseline_result["avg_max_cluster_size"]
            * 100
        )
        print(f"  Improvement over baseline: {improvement:+.1f}%")

    # Check if anti-agents help or hurt
    if best_result["anti_agent_percentage"] == 0:
        print("\n⚠️  WARNING: Pure aggregation (0% anti-agents) performed best!")
        print(
            "     This suggests anti-agents may be hindering aggregation with current parameters."
        )
    else:
        print(
            f"\n✓ Anti-agents improved clustering! Optimal percentage: {best_result['anti_agent_percentage']:.1f}%"
        )

    print()
