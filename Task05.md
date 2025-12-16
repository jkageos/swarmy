# Task 5.2 – Local Sampling (Run Instructions)

## Environment Setup
- Python 3.13+
- Install dependencies:
  ```bash
  pip install -e .
  # or
  pip install pygame pyyaml numpy matplotlib scipy
  ```

## Run Experiments
- Execute Task 5.2 sweep from the workspace:
  ```bash
  python workspace.py
  ```
- Outputs:
  - Plots in `plots/`:
    - `task52_mean_vs_swarm_size.png`
    - `task52_std_vs_swarm_size.png`
    - `task52_mean_vs_sensor_range.png`
  - Console summary with mean/std across all runs.

## Adjust Parameters
- Edit in `workspace.py` (Task 5.2 section):
  - `SWARM_SIZES` (e.g., `[2, 5, 10, ... , 200]`)
  - `SENSOR_RANGES` (e.g., `[0.02, 0.5]`)
  - `EXPERIMENTS_PER_CONFIG` (default `1000`)

Tip: For faster tests, lower `EXPERIMENTS_PER_CONFIG` and use fewer `SWARM_SIZES`/`SENSOR_RANGES`.