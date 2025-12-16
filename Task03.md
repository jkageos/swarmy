# Task 3.1 & 3.2 - Single Robot Behaviors and Potential Field Control

This document provides instructions for running and visualizing the robot behavior experiments.

## Prerequisites

- Python 3.13+
- Required packages (install with `pip install pygame pyyaml numpy matplotlib scipy`)

## Task 3.1: Single Robot Behaviors

### How to Run

1. Open [`config.yaml`](config.yaml)
2. Set `task31.active: true` and ensure other tasks are set to `false`
3. Choose which controller to test by setting `task31.controller`:
   ```yaml
   task31:
     active: true
     controller: collision_avoidance  # or: wall_follower | vacuum_cleaner | levy_flight
     rendering: 1
     max_timestep: 3000
     save_trajectory: 1
   ```
4. Run the simulation:
   ```bash
   python workspace.py
   ```

### Subtasks

#### a) Collision Avoidance
- **Behavior**: Robot moves forward and backs up + turns when hitting obstacles
- **File**: [`controller/task31a_controller.py`](controller/task31a_controller.py)
- **Strategy**: Reactive behavior with random turn direction after collision
- **Config**: `controller: collision_avoidance`

#### b) Wall Follower
- **Behavior**: Robot follows walls at a consistent distance without touching
- **File**: [`controller/task31b_controller.py`](controller/task31b_controller.py)
- **Strategy**: State machine (seeking → avoiding → following)
- **Config**: `controller: wall_follower`

#### c) Vacuum Cleaner
- **Behavior**: Robot attempts to cover maximum area
- **File**: [`controller/task31c_controller.py`](controller/task31c_controller.py)
- **Strategy**: Combines spiral patterns with random bouncing
- **Config**: `controller: vacuum_cleaner`

#### d) Lévy Flight
- **Behavior**: Exploratory behavior with varied movement lengths
- **File**: [`controller/task31d_controller.py`](controller/task31d_controller.py)
- **Strategy**: Power-law distributed movement segments
- **Config**: `controller: levy_flight`

## Task 3.2: Potential Field Control

### How to Run

1. Open [`config.yaml`](config.yaml)
2. Set `task32.active: true` and ensure other tasks are set to `false`
3. Choose which controller to test by setting `task32.controller`:
   ```yaml
   task32:
     active: true
     controller: direct_gradient  # or: indirect_gradient
     rendering: 1
     max_timestep: 2000
     save_trajectory: 0
     # Controller parameters
     dt: 1.0
     direct_velocity_scale: 5000.0
     direct_max_velocity: 10.0
     indirect_c: 0.95
     indirect_acceleration_scale: 1000.0
     indirect_max_velocity: 10.0
   ```
4. Run the simulation:
   ```bash
   python workspace.py
   ```

### Subtasks

#### a) Direct Gradient Control
- **File**: [`controller/task32a_controller.py`](controller/task32a_controller.py)
- **Config**: `controller: direct_gradient`
- **Equations**:
  - $v_x(t) = -\frac{\partial P}{\partial x} \times \text{scale}$
  - $v_y(t) = -\frac{\partial P}{\partial y} \times \text{scale}$
- **Parameters** (in [`config.yaml`](config.yaml) under `task32`):
  - `dt`: Time step (default: 1.0)
  - `direct_velocity_scale`: Controls response to gradient (default: 5000.0)
  - `direct_max_velocity`: Limits maximum speed (default: 10.0)
- **Characteristics**: Fast response, may oscillate near local minima

#### b) Indirect Gradient Control
- **File**: [`controller/task32b_controller.py`](controller/task32b_controller.py)
- **Config**: `controller: indirect_gradient`
- **Equations**:
  - $v_x(t) = c \cdot v_x(t-\Delta t) - \frac{\partial P}{\partial x} \times \text{scale}$
  - $v_y(t) = c \cdot v_y(t-\Delta t) - \frac{\partial P}{\partial y} \times \text{scale}$
  - Then normalize: $\vec{v} \leftarrow \frac{\vec{v}}{|\vec{v}|} \times v_{max}$
- **Parameters** (in [`config.yaml`](config.yaml) under `task32`):
  - `dt`: Time step (default: 1.0)
  - `indirect_c`: Discount factor / memory (default: 0.95)
  - `indirect_acceleration_scale`: Gradient influence (default: 1000.0)
  - `indirect_max_velocity`: Maximum speed (default: 10.0)
- **Characteristics**: Smooth trajectories with momentum, better obstacle avoidance

## Configuration

All parameters are centralized in [`config.yaml`](config.yaml):

### Global Parameters (used by all tasks)
```yaml
FPS: 60                    # Simulation speed
world_width: 1000          # Arena width
world_height: 800          # Arena height
number_of_agents: 1        # Number of robots (Task 3 uses single robot)
default_velocity: 3        # Linear velocity
default_angle_velocity: 3  # Angular velocity
rendering: 1               # Show visualization (global default)
```

### Task 3.1 Specific
```yaml
task31:
  active: false                    # Toggle this task on/off
  rendering: 1                     # Override global rendering
  max_timestep: 3000               # Simulation duration
  save_trajectory: 1               # Enable trajectory recording
  controller: collision_avoidance  # Which behavior to run
```

### Task 3.2 Specific
```yaml
task32:
  active: false              # Toggle this task on/off
  rendering: 1               # Override global rendering
  max_timestep: 2000         # Simulation duration
  save_trajectory: 0         # Trajectory recording
  controller: direct_gradient # Which controller to run
  # Direct gradient parameters
  dt: 1.0
  direct_velocity_scale: 5000.0
  direct_max_velocity: 10.0
  # Indirect gradient parameters
  indirect_c: 0.95
  indirect_acceleration_scale: 1000.0
  indirect_max_velocity: 10.0
```

## Output

- **Plots**: Saved to `plots/` directory
  - Task 3.1: `task31_<controller>.png` (trajectory with coverage statistics)
  - Task 3.2: `task32_<controller>.png` (trajectory with potential field heatmap)
  - Task 3.2: `task32_gradient_field.png` (gradient vector field visualization)
- **Console**: Statistics printed during and after simulation
  - Task 3.1: Path length, area coverage percentage
  - Task 3.2: Start/end potential, potential descent, trajectory steps
- **Visual**: Real-time rendering in pygame window (if `rendering: 1`)

## Parameter Tuning Guidelines

### Task 3.1: Single Robot Behaviors

**Collision Avoidance**:
- Increase `default_velocity` for faster exploration
- Increase `default_angle_velocity` for sharper turns

**Wall Follower**:
- Adjust velocities to control following smoothness
- Behavior is mostly algorithmic (state machine)

**Vacuum Cleaner**:
- Increase `max_timestep` to see better coverage
- Coverage depends on spiral size (hardcoded in controller)

**Lévy Flight**:
- Exploration pattern is stochastic
- Increase `max_timestep` for more variation

### Task 3.2: Potential Field Control

**Direct Gradient (`task32.direct_*`)**:
- ↑ `direct_velocity_scale`: Faster descent, may oscillate near minima
- ↓ `direct_velocity_scale`: Smoother but slower movement
- ↑ `direct_max_velocity`: Higher top speed
- ↓ `dt`: Smaller time steps (more precise, slower simulation)

**Indirect Gradient (`task32.indirect_*`)**:
- `indirect_c` closer to 1.0: More memory, smoother paths, may overshoot
- `indirect_c` closer to 0.0: Less memory, more reactive, faster convergence
- ↑ `indirect_acceleration_scale`: Stronger gradient response
- ↑ `indirect_max_velocity`: Higher top speed
- **Balance**: `c` and `acceleration_scale` must be tuned together
  - High `c` + low `acceleration_scale`: Very smooth, slow convergence
  - Low `c` + high `acceleration_scale`: Reactive, may oscillate

### Recommended Starting Points

| Goal | `direct_velocity_scale` | `indirect_c` | `indirect_acceleration_scale` |
|------|------------------------|--------------|-------------------------------|
| Fast descent | 8000.0 | 0.90 | 1500.0 |
| Smooth path | 3000.0 | 0.98 | 500.0 |
| Balanced | 5000.0 | 0.95 | 1000.0 |

## Troubleshooting

### Robot doesn't move (Task 3.2)
- Check that potential field has gradient (visualize with `task32_gradient_field.png`)
- Increase `velocity_scale` or `acceleration_scale`
- Ensure robot starts at high potential (left side of arena)

### Robot oscillates near goal (Task 3.2)
- Decrease `velocity_scale` or `acceleration_scale`
- Increase `c` (indirect gradient only) for more damping
- Decrease `max_velocity` to prevent overshooting

### Trajectory plot not generated (Task 3.1)
- Set `save_trajectory: 1` in `task31` section
- Ensure simulation completes (check console for errors)

### Visualization too slow
- Set `rendering: 0` in task-specific section
- Reduce `FPS` (but plot generation doesn't need rendering)

## Expected Results

### Task 3.1

**Collision Avoidance**:
- Random walk behavior with obstacle bouncing
- Coverage: ~30-50% of arena (depends on obstacles)
- Trajectory: Irregular path with sharp direction changes

**Wall Follower**:
- Robot traces perimeter and some obstacles
- Coverage: ~20-40% (mostly along walls)
- Trajectory: Smooth curves along boundaries

**Vacuum Cleaner**:
- Systematic spiral coverage attempts
- Coverage: ~50-70% (best coverage)
- Trajectory: Mix of spirals and bounces

**Lévy Flight**:
- Mix of short and long straight segments
- Coverage: ~40-60% (efficient exploration)
- Trajectory: Power-law distributed movement lengths

### Task 3.2

**Direct Gradient**:
- Robot descends from high potential (yellow/left) to low potential (purple/right)
- Trajectory: Relatively direct path with some oscillations near obstacles
- Potential descent: ~0.6-0.8 (depends on obstacle encounters)
- Steps: ~800-1500 (depends on `velocity_scale`)

**Indirect Gradient**:
- Robot descends smoothly with momentum
- Trajectory: Smooth curves, better obstacle avoidance
- Potential descent: ~0.6-0.8
- Steps: ~1000-2000 (smoother = more steps)

## File Structure

```
Task 3.1 & 3.2 Files:
├── workspace.py                           # Main execution script
├── config.yaml                            # All configuration parameters
├── Task03.md                              # This documentation
├── agent/
│   ├── my_agent.py                       # Task 3.1 agent
│   └── task32_agent.py                   # Task 3.2 agent
├── controller/
│   ├── task31a_controller.py             # Collision avoidance
│   ├── task31b_controller.py             # Wall follower
│   ├── task31c_controller.py             # Vacuum cleaner
│   ├── task31d_controller.py             # Lévy flight
│   ├── task32a_controller.py             # Direct gradient
│   └── task32b_controller.py             # Indirect gradient
├── sensors/
│   └── bumper_sensor.py                  # Collision detection (Task 3.1)
├── world/
│   ├── task31_world.py                   # Rectangular arena with obstacles
│   └── task32_world.py                   # Potential field environment
├── utils/
│   ├── plot_trajectories.py              # Task 3.1 visualization
│   └── plot_potential_field.py           # Task 3.2 visualization
└── plots/                                 # Generated plots
    ├── task31_*.png
    ├── task32_*.png
    └── task32_gradient_field.png
```

## Running Multiple Tasks

To switch between tasks, edit [`config.yaml`](config.yaml):

```yaml
# Run Task 3.1 Collision Avoidance
task31:
  active: true
  controller: collision_avoidance
task32:
  active: false

# Then switch to Task 3.2 Direct Gradient
task31:
  active: false
task32:
  active: true
  controller: direct_gradient
```

No need to edit [`workspace.py`](workspace.py) - all task selection is done via config!

## Advanced Usage

### Custom Potential Field (Task 3.2)

Edit [`world/task32_world.py`](world/task32_world.py) → `generate_potential_field()`:
- Modify base gradient slope
- Add/remove obstacle bumps
- Adjust border repulsion

### Custom Arena (Task 3.1)

Edit [`world/task31_world.py`](world/task31_world.py) → `add_static_rectangle_object()`:
- Add more obstacles
- Change arena dimensions
- Add circular obstacles in `add_static_circle_object()`

## Citation

Based on the Swarmy simulator by Samer Al-Magazachi.