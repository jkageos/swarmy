# Task 6 – Swarm Aggregation with Anti-Agents

This document provides instructions for running and analyzing swarm clustering experiments with disruption from anti-agents.

## Prerequisites

- Python 3.13+
- `uv` package manager installed ([uv docs](https://docs.astral.sh/uv/))

### Install Dependencies

Using `uv`:

```bash
# Sync project dependencies (creates .venv automatically)
uv sync

# Or install directly without venv
uv pip install pygame pyyaml numpy matplotlib scipy psutil
```

The project's `pyproject.toml` specifies all required packages.

---

## Environment Setup

### Option 1: Using `uv` with Virtual Environment (Recommended)

```bash
# Create and activate virtual environment
uv venv .venv

# On Windows PowerShell:
.venv\Scripts\Activate.ps1

# On Windows CMD:
.venv\Scripts\activate.bat

# On macOS/Linux:
source .venv/bin/activate

# Sync dependencies
uv sync
```

### Option 2: Using `uv` without Virtual Environment

```bash
# Install globally to uv's managed Python
uv pip install -r pyproject.toml
```

### Verify Installation

```bash
# Check Python version
python --version  # Should be 3.13+

# Check key packages
python -c "import pygame, numpy, matplotlib; print('✓ All packages installed')"
```

---

## Quick Start

### Run Task 6

1. **Configure parameters** in [`config.yaml`](config.yaml):

   ```yaml
   task6:
     active: true
     rendering: 0 # No visualization (faster)
     max_timestep: 5000 # Duration per experiment
     save_trajectory: 0

     # Experiment sweep
     use_multiprocessing: true # Recommended for speed
     anti_agent_percentages: [0, 2, 5, 10, 15, 20, 30]
     runs_per_percentage: 100 # Total runs: 700
     cluster_distance: 100 # Distance threshold
   ```

2. **Run the experiment**:

   ```bash
   # Using uv directly
   uv run python workspace.py

   # Or activate venv first, then run
   python workspace.py
   ```

3. **Monitor progress** in console:

   ```
   🤖 TASK 6: Swarm Aggregation with Anti-Agents
      (Multiprocessing ENABLED for faster execution)
   ======================================================================
   Multiprocessing: workers=6, batch_size=6, maxtasksperchild=5
   Total configurations: 7
   Runs per config: 100
   Total experiments: 700
   ======================================================================
   [1/700] 0% anti-agents → max_cluster = 15
   [2/700] 0% anti-agents → max_cluster = 13
   ...
   ✓ Completed 700 runs in 4.3 min
   ```

4. **View results**:
   - Plots saved to `plots/`:
     - `task6_anti_agent_results.png` (main results with error bars)
     - `task6_cluster_distribution.png` (box plot distribution)
   - Summary printed to console

---

## Configuration

### Global Parameters

Edit [`config.yaml`](config.yaml):

```yaml
# Simulation parameters
FPS: 60
max_timestep: 6000

# World parameters
world_width: 800
world_height: 800
background_color: [255, 255, 255]

# Swarm parameters
number_of_agents: 50 # Total agents (regular + anti)
default_velocity: 2 # Movement speed
default_angle_velocity: 3 # Rotation speed
```

### Task 6 Specific Parameters

```yaml
# Aggregation behavior
task6_aggregation_range: 100 # Detection range for neighbors
task6_attraction_probability: 0.3 # Probability to move toward neighbor
task6_random_walk_probability: 0.1 # Probability to move randomly

# Anti-agent behavior
task6_anti_agent_comm_range: 120 # Range to send leave commands
task6_anti_agent_leave_threshold: 2 # Minimum cluster size to target

# Task 6 run controls
task6:
  active: true
  rendering: 0 # 0=headless, 1=visualization
  max_timestep: 5000
  save_trajectory: 0
  use_multiprocessing: true

  # Sweep configuration
  anti_agent_percentages: [0, 2, 5, 10, 15, 20, 30]
  runs_per_percentage: 100
  cluster_distance: 100
```

### Multiprocessing Configuration

```yaml
multiprocessing:
  max_cpu_utilization: 0.5 # Use up to 50% of CPU cores
  max_workers: 6 # Hard cap at 6 workers
  blas_threads: 1 # Single-threaded BLAS
  maxtasksperchild: 5 # Recycle workers every 5 tasks
  batch_size: 6 # Process 6 configs per batch
  cooldown_seconds: 2.0 # Pause between batches
```

---