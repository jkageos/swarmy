# Task 3.1 & 3.2 - Single Robot Behaviors and Potential Field Control

This document provides instructions for running and visualizing the robot behavior experiments.

## Prerequisites

- Python 3.13+
- Required packages (install with `pip install pygame pyyaml numpy matplotlib scipy`)

## Task 3.1: Single Robot Behaviors

### How to Run

1. Open [`workspace.py`](workspace.py)
2. **Comment out** the Task 3.2 section (lines 40-58)
3. **Uncomment** the Task 3.1 section (lines 14-38)
4. Choose which controller to test by uncommenting one line:
   ```python
   agent_controller = [CollisionAvoidanceController]  # Task 3.1a
   # agent_controller = [WallFollowerController]      # Task 3.1b
   # agent_controller = [VacuumCleanerController]     # Task 3.1c
   # agent_controller = [LevyFlightController]        # Task 3.1d
   ```
5. Run the simulation:
   ```bash
   python workspace.py
   ```

### Subtasks

#### a) Collision Avoidance
- **Behavior**: Robot moves forward and backs up + turns when hitting obstacles
- **File**: [`controller/task31a_controller.py`](controller/task31a_controller.py)
- **Strategy**: Reactive behavior with random turn direction after collision

#### b) Wall Follower
- **Behavior**: Robot follows walls at a consistent distance without touching
- **File**: [`controller/task31b_controller.py`](controller/task31b_controller.py)
- **Strategy**: State machine (seeking → avoiding → following)

#### c) Vacuum Cleaner
- **Behavior**: Robot attempts to cover maximum area
- **File**: [`controller/task31c_controller.py`](controller/task31c_controller.py)
- **Strategy**: Combines spiral patterns with random bouncing

#### d) Lévy Flight
- **Behavior**: Exploratory behavior with varied movement lengths
- **File**: [`controller/task31d_controller.py`](controller/task31d_controller.py)
- **Strategy**: Power-law distributed movement segments

## Task 3.2: Potential Field Control

### How to Run

1. Open [`workspace.py`](workspace.py)
2. **Comment out** the Task 3.1 section (lines 14-38)
3. **Uncomment** the Task 3.2 section (lines 40-58)
4. Choose which controller to test:
   ```python
   agent_controller = [DirectGradientController]      # Task 3.2a
   # agent_controller = [IndirectGradientController]  # Task 3.2b
   ```
5. Run the simulation:
   ```bash
   python workspace.py
   ```

### Subtasks

#### a) Direct Gradient Control
- **File**: [`controller/task32a_controller.py`](controller/task32a_controller.py)
- **Equations**:
  - $v_x(t) = -\frac{\partial P}{\partial x}$
  - $v_y(t) = -\frac{\partial P}{\partial y}$
- **Parameters**:
  - `velocity_scale = 0.5`: Controls response to gradient
  - `max_velocity = 3.0`: Limits maximum speed
- **Characteristics**: Fast response, may oscillate near local minima

#### b) Indirect Gradient Control
- **File**: [`controller/task32b_controller.py`](controller/task32b_controller.py)
- **Equations**:
  - $v_x(t) = c \cdot v_x(t-\Delta t) - \frac{\partial P}{\partial x}$
  - $v_y(t) = c \cdot v_y(t-\Delta t) - \frac{\partial P}{\partial y}$
  - Then normalize: $\vec{v} \leftarrow \frac{\vec{v}}{|\vec{v}|}$
- **Parameters**:
  - `c = 0.95`: Discount factor (memory)
  - `acceleration_scale = 0.3`: Gradient influence
  - `max_velocity = 4.0`: Maximum speed
- **Characteristics**: Smooth trajectories with momentum, better obstacle avoidance

## Configuration

Edit [`config.yaml`](config.yaml) to adjust simulation parameters:

```yaml
FPS: 60                    # Simulation speed
max_timestep: 3000         # Duration
world_width: 800           # Arena width
world_height: 600          # Arena height
number_of_agents: 1        # Number of robots
default_velocity: 4        # Linear velocity
default_angle_velocity: 4  # Angular velocity
save_trajectory: 1         # Enable trajectory recording
rendering: 1               # Show visualization
```

## Output

- **Plots**: Saved to `plots/` directory
- **Console**: Statistics printed during and after simulation
- **Visual**: Real-time rendering in pygame window

## Parameter Tuning Guidelines

### Task 3.2a (Direct Gradient)
- Increase `velocity_scale` for faster descent (may oscillate)
- Decrease `velocity_scale` for smoother but slower movement
- Adjust `max_velocity` to control overall speed

### Task 3.2b (Indirect Gradient)
- `c` closer to 1.0: More memory, smoother paths
- `c` closer to 0.0: Less memory, more reactive
- Increase `acceleration_scale` for stronger gradient response
- Balance between `c` and `acceleration_scale` is key