"""
Data persistence utilities for saving and loading simulation results
"""

import pickle
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def save_task52_results(
    results: Dict[Tuple[int, float], List[float]],
    swarm_sizes: List[int],
    sensor_ranges: List[float],
    filename: str = "task52_results.pkl",
) -> Path:
    """
    Save Task 5.2 experimental results to disk.

    Args:
        results: Dictionary mapping (N, r) -> list of estimates
        swarm_sizes: List of swarm sizes tested
        sensor_ranges: List of sensor ranges tested
        filename: Output filename (default: task52_results.pkl)

    Returns:
        Path to saved file
    """
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)

    data = {
        "results": dict(results),  # Convert defaultdict to regular dict
        "swarm_sizes": swarm_sizes,
        "sensor_ranges": sensor_ranges,
        "metadata": {
            "total_experiments": sum(len(v) for v in results.values()),
            "num_configs": len(results),
            "experiments_per_config": len(next(iter(results.values())))
            if results
            else 0,
        },
    }

    filepath = data_dir / filename
    with open(filepath, "wb") as f:
        pickle.dump(data, f)

    print(f"\n✓ Results saved to: {filepath}")
    print(f"  - {data['metadata']['num_configs']} configurations")
    print(f"  - {data['metadata']['total_experiments']} total experiments")

    return filepath


def load_task52_results(
    filename: str = "task52_results.pkl",
) -> Optional[Tuple[Dict, List[int], List[float]]]:
    """
    Load Task 5.2 experimental results from disk.

    Args:
        filename: Input filename (default: task52_results.pkl)

    Returns:
        Tuple of (results, swarm_sizes, sensor_ranges) or None if file doesn't exist
    """
    filepath = Path("data") / filename

    if not filepath.exists():
        return None

    with open(filepath, "rb") as f:
        data = pickle.load(f)

    print(f"\n✓ Loaded results from: {filepath}")
    print(f"  - {data['metadata']['num_configs']} configurations")
    print(f"  - {data['metadata']['total_experiments']} total experiments")

    return data["results"], data["swarm_sizes"], data["sensor_ranges"]


def clear_task52_cache(filename: str = "task52_results.pkl") -> bool:
    """
    Delete cached Task 5.2 results.

    Args:
        filename: Cache filename to delete

    Returns:
        True if file was deleted, False if it didn't exist
    """
    filepath = Path("data") / filename

    if filepath.exists():
        filepath.unlink()
        print(f"✓ Deleted cache: {filepath}")
        return True
    else:
        print(f"⚠ Cache not found: {filepath}")
        return False
