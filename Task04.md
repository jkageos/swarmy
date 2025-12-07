# Task 4.1 & 4.2 - Swarm Behaviors and Flocking Analysis

This document provides instructions for running and analyzing the swarm robotics experiments.

## Prerequisites

- Python 3.13+
- Required packages (install with `pip install -r requirements.txt`)

### Install Dependencies

```bash
pip install pygame pyyaml numpy matplotlib scipy
```

Or using the included dependency file:

```bash
pip install -e .
```

## Quick Start

### Task 4.1: Swarm Aggregation

**Goal**: Robots detect nearby swarm members and aggregate into clusters.

#### How to Run

1. Open [`workspace.py`](workspace.py)
2. **Comment out** the Task 4.2b section (lines 145-225)
3. **Uncomment** the Task 4.1 section (lines 89-103):
   ```python
   from agent.task41_agent import Task41Agent
   from controller.task41_controller import AggregationController
   from sensors.task41_sensor import ProximitySensor
   from world.task41_world import Task41Environment

   agent_controller = [AggregationController]
   agent_sensing = [ProximitySensor]

   exp1 = Experiment(
       config, agent_controller, agent_sensing, Task41Environment, Task41Agent
   )
   exp1.run(1)
   ```

4. Run the simulation:
   ```bash
   python workspace.py
   ```

#### Configuration

Edit [`config.yaml`](config.yaml) to adjust parameters:

```yaml
number_of_agents: 20              # Number of robots in the swarm
proximity_range: 80               # Detection range (pixels)
aggregation_waiting_time: 80      # Frames to wait when stopped
aggregation_cooldown: 30          # Frames to move after waking up
default_velocity: 3               # Movement speed
default_angle_velocity: 3         # Rotation speed
max_timestep: 6000                # Simulation duration
```

#### Behavior

The aggregation controller uses a **state machine** with three states:

| State | Behavior | Condition |
|-------|----------|-----------|
| **moving** | Robot explores freely with random walk | Active until neighbor detected |
| **stopped** | Robot stays still | Duration: `aggregation_waiting_time` frames |
| **cooldown** | Robot wakes up and moves | Duration: `aggregation_cooldown` frames |

**Strategy**: When a robot detects nearby robots, it stops to encourage clustering. After waiting, it moves again with reduced sensitivity to avoid immediate re-triggering.

#### Output

- Real-time visualization in pygame window
- Robot trajectories logged (if `save_trajectory: 1`)
- Console output: Path length and clustering statistics

---

### Task 4.2a: Reynolds Flocking in Toroidal Space

**Goal**: Implement classic Reynolds flocking with three forces (separation, alignment, cohesion).

#### How to Run

1. Open [`workspace.py`](workspace.py)
2. **Comment out** the Task 4.2b section (lines 145-225)
3. **Uncomment** the Task 4.2a section (lines 106-119):
   ```python
   from agent.task42_agent import Task42Agent
   from controller.task42_controller import FlockingController
   from sensors.task42_sensor import FlockingSensor
   from world.task42_world import Task42Environment

   agent_controller = [FlockingController]
   agent_sensing = [FlockingSensor]

   exp1 = Experiment(
       config, agent_controller, agent_sensing, Task42Environment, Task42Agent
   )
   exp1.run(1)
   ```

4. Run the simulation:
   ```bash
   python workspace.py
   ```

#### Configuration

Edit [`config.yaml`](config.yaml):

```yaml
number_of_agents: 20              # Swarm size
separation_radius: 50.0           # Min distance threshold
alignment_radius: 80.0            # Velocity matching range
cohesion_radius: 100.0            # Attraction range
separation_weight: 5.0            # Separation force strength (↑ = stronger repulsion)
alignment_weight: 1.0             # Alignment force strength
cohesion_weight: 0.02             # Cohesion force strength (↓ = looser flock)
flock_speed: 3.0                  # Desired velocity magnitude
max_sensing_radius: 120.0         # Max neighbor detection range
min_separation_distance: 35.0     # Emergency separation threshold
show_velocity: False              # Debug visualization of forces
max_timestep: 6000                # Simulation duration
```

#### Flocking Forces

The controller implements Reynolds' three rules:

$$\vec{F}_{total} = w_s \cdot \vec{F}_{sep} + w_a \cdot \vec{F}_{align} + w_c \cdot \vec{F}_{coh}$$

1. **Separation** ($\vec{F}_{sep}$): Avoid crowding neighbors
   - Active for $d < r_s$ (separation radius)
   - Strength: Inverse-square law with emergency boost

2. **Alignment** ($\vec{F}_{align}$): Match velocity of neighbors
   - Active for $d < r_a$ (alignment radius)
   - Strength: Proportional to velocity difference

3. **Cohesion** ($\vec{F}_{coh}$): Steer towards center of neighbors
   - Active for $d < r_c$ (cohesion radius)
   - Strength: Proportional to distance to center

#### Special Features

- **Toroidal space**: Robots wrap around edges (no walls)
- **Emergency separation**: Critical response if robots get too close
- **Danger zone detection**: Disables other forces if in critical proximity
- **Periodic boundaries**: Smooth wrapping without collisions

#### Output

- Real-time visualization (optional)
- Robot velocity vectors (if `show_velocity: True`)
- Console output: Simulation progress

---

### Task 4.2b: Order Parameter Analysis (Phase Transition)

**Goal**: Measure how heading noise affects flock coherence.

#### How to Run

1. Open [`workspace.py`](workspace.py) - Task 4.2b section is already active
2. Optionally adjust configuration in [`config.yaml`](config.yaml)
3. Run the simulation:
   ```bash
   python workspace.py
   ```

The script will automatically:
- Run 33 simulations (11 noise levels × 3 runs each)
- Compute order parameter for each run
- Generate statistics and plot

#### What is Order Parameter?

The **order parameter** $v_a$ measures global alignment of the swarm:

$$v_a = \frac{1}{N}\left\lvert\sum_{i=1}^N \hat{v}_i\right\rvert$$

where $\hat{v}_i$ is the normalized velocity of agent $i$.

- **$v_a = 1.0$**: Perfect alignment (all robots moving same direction)
- **$v_a = 0.5$**: Partial coherence (swarm is partially ordered)
- **$v_a = 0.0$**: Complete disorder (random motion)

#### Phase Transition

The sweep reveals the **order-disorder transition**:

$$v_a(\eta) = \begin{cases}
\text{high} (~0.8\text{-}0.9) & \eta \ll \eta_c \text{ (ordered phase)} \\
\text{transition region} & \eta \approx \eta_c \text{ (critical point)} \\
\text{low} (~0.1\text{-}0.3) & \eta \gg \eta_c \text{ (disordered phase)}
\end{cases}$$

#### Configuration for Task 4.2b

```yaml
number_of_agents: 20              # Swarm size
max_timestep: 4000                # Time per simulation
separation_weight: 5.0            # Strong separation
alignment_weight: 1.0
cohesion_weight: 0.02             # Weak cohesion (allows transition)
heading_noise: 0.0                # Overridden by workspace.py
rendering: 0                      # No visualization (faster)
```

**Noise sweep parameters** (in `workspace.py`):

```python
noise_levels = np.linspace(0, 1.0, 11)  # 11 noise levels: 0.0 → 1.0
runs_per_noise = 3                       # 3 runs per level for statistics
```

#### Output

The script generates:

1. **Console output**:
   ```
   Noise intensity η = 0.00:
   --------------------------------------------------
   Run 1/3... va = 0.9997
   Run 2/3... va = 0.9706
   Run 3/3... va = 0.9998
   Average: 0.9900 ± 0.0137
   ...
   ```

2. **Plot**: `plots/task42_order_parameter.png`
   - X-axis: Noise intensity $\eta$ (radians)
   - Y-axis: Order parameter $v_a$
   - Shows phase transition curve

3. **Summary statistics**:
   ```
   Maximum order parameter: 0.9991 at η = 0.10
   Minimum order parameter: 0.6284 at η = 1.00
   Largest drop in order: Δva = 0.2619 between η = 0.90 and η = 1.00
   Potential phase transition region: η ≈ 0.90
   ```

#### Interpreting Results

- **Expected behavior**: $v_a$ decreases monotonically with noise
- **Sharp transition**: Indicates a critical point ($\eta_c$)
- **Smooth transition**: Suggests crossover behavior
- **High variance**: Small swarms (N=20) have stochastic fluctuations

#### Parameter Tuning

To improve results:

| Goal | Change | Effect |
|------|--------|--------|
| Clearer transition | ↓ `cohesion_weight` | Looser flocking, easier to break up |
| Lower base order | ↑ `separation_weight` | Stronger repulsion |
| Smoother curves | ↑ `max_timestep` | Longer equilibration time |
| Less variance | ↑ `runs_per_noise` | Better statistics (slower) |
| Different transition point | Adjust all weights | Shift critical noise level |

---

## File Structure

```
Task 4.1 & 4.2 Files:
├── workspace.py                           # Main execution script
├── config.yaml                            # Configuration parameters
├── agent/
│   ├── task41_agent.py                   # Aggregation agent
│   └── task42_agent.py                   # Flocking agent
├── controller/
│   ├── task41_controller.py              # Aggregation behavior
│   └── task42_controller.py              # Flocking behavior
├── sensors/
│   ├── task41_sensor.py                  # Proximity sensor
│   └── task42_sensor.py                  # Flocking sensor (neighbors)
├── world/
│   ├── task41_world.py                   # Rectangular arena
│   └── task42_world.py                   # Toroidal arena
├── utils/
│   └── plot_flocking.py                  # Order parameter plotting
└── swarmy/                                # Core simulator
    ├── experiment.py
    ├── environment.py
    ├── agent.py
    ├── actuation.py
    ├── perception.py
    ├── processing.py
    └── body.py
```

---

## Troubleshooting

### Task 4.1: Robots not aggregating

- ↑ Increase `aggregation_waiting_time` (robots wait longer)
- ↓ Decrease `proximity_range` (make detection more selective)
- ↑ Increase `number_of_agents` (more robots = higher encounter rate)

### Task 4.2a: Flock breaks apart

- ↑ Increase `cohesion_weight` (stronger attraction)
- ↓ Decrease `separation_weight` (reduce repulsion)
- ↓ Decrease `heading_noise` (less random perturbation)

### Task 4.2b: High variance in order parameter

- ↑ Increase `max_timestep` (longer equilibration)
- ↑ Increase `runs_per_noise` (more samples per level)
- ↑ Increase `number_of_agents` (larger swarm, less stochastic noise)

### Simulation too slow

- Set `rendering: 0` in config.yaml (no visualization)
- Reduce `max_timestep` (shorter runs)
- Reduce `number_of_agents` (fewer robots)
- Reduce `runs_per_noise` in workspace.py (fewer noise levels)

---

## Expected Results

### Task 4.1: Aggregation
- Robots form clusters within ~2000 timesteps
- Multiple aggregation sites may appear
- Trajectories show exploratory phase → aggregation phase

### Task 4.2a: Flocking
- Synchronized motion within ~1000 timesteps
- Smooth collective rotation and translation
- High order parameter (~0.9+)

### Task 4.2b: Phase Transition
- **No noise** ($\eta = 0$): $v_a \approx 0.99$ (perfectly ordered)
- **Low noise** ($\eta < 0.3$): $v_a \approx 0.95$ (strongly ordered)
- **Medium noise** ($\eta \approx 0.5$): $v_a \approx 0.5$ (transition region)
- **High noise** ($\eta > 0.8$): $v_a \approx 0.1\text{-}0.3$ (disordered)

Critical point typically near $\eta_c \approx 0.5\text{-}0.7$ (depends on parameters).

---

## References

- **Reynolds Flocking**: C. W. Reynolds, "Flocks, Herds, and Schools: A Distributed Behavioral Model," *SIGGRAPH*, 1987
- **Order Parameter**: Vicsek et al., "Novel type of phase transition in a system of self-driven particles," *Physical Review Letters*, 1995
- **Toroidal Space**: Common in swarm robotics to eliminate boundary effects

---

## Citation

Based on the Swarmy simulator by Samer Al-Magazachi.