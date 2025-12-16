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

1. Open [`config.yaml`](config.yaml)
2. Set `task41.active: true` and ensure other tasks are set to `false`:
   ```yaml
   task41:
     active: true
     rendering: 1
     max_timestep: 4000
     save_trajectory: 0
   ```
3. Run the simulation:
   ```bash
   python workspace.py
   ```

#### Configuration

Edit [`config.yaml`](config.yaml) to adjust parameters:

**Global Aggregation Parameters** (used by controller):
```yaml
number_of_agents: 20              # Number of robots in the swarm
proximity_range: 80               # Detection range (pixels)
aggregation_waiting_time: 80      # Frames to wait when stopped
aggregation_cooldown: 40          # Frames to move after waking up
default_velocity: 3               # Movement speed
default_angle_velocity: 3         # Rotation speed
```

**Task 4.1 Run Controls**:
```yaml
task41:
  active: false                   # Toggle this task on/off
  rendering: 1                    # Override global rendering
  max_timestep: 4000              # Simulation duration
  save_trajectory: 0              # Trajectory recording
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

- Real-time visualization in pygame window (if `rendering: 1`)
- Robot trajectories logged (if `save_trajectory: 1`)
- Console output: Path length and clustering statistics

---

### Task 4.2a: Reynolds Flocking in Toroidal Space

**Goal**: Implement classic Reynolds flocking with three forces (separation, alignment, cohesion).

#### How to Run

1. Open [`config.yaml`](config.yaml)
2. Set `task42a.active: true` and ensure other tasks are set to `false`:
   ```yaml
   task42a:
     active: true
     rendering: 1
     max_timestep: 3000
     save_trajectory: 0
   ```
3. Run the simulation:
   ```bash
   python workspace.py
   ```

#### Configuration

Edit [`config.yaml`](config.yaml):

**Global Flocking Parameters** (used by controller):
```yaml
number_of_agents: 20              # Swarm size
separation_radius: 50.0           # Min distance threshold
alignment_radius: 80.0            # Velocity matching range
cohesion_radius: 100.0            # Attraction range
separation_weight: 5.0            # Separation force strength (↑ = stronger repulsion)
alignment_weight: 1.0             # Alignment force strength
cohesion_weight: 0.02             # Cohesion force strength (↓ = looser flock)
flock_speed: 3.0                  # Desired velocity magnitude
heading_noise: 0.0                # Random angular perturbation (radians)
max_sensing_radius: 120.0         # Max neighbor detection range
min_separation_distance: 35.0     # Emergency separation threshold
show_velocity: False              # Debug visualization of forces
```

**Task 4.2a Run Controls**:
```yaml
task42a:
  active: false                   # Toggle this task on/off
  rendering: 1                    # Override global rendering
  max_timestep: 3000              # Simulation duration
  save_trajectory: 0              # Trajectory recording
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

- Real-time visualization (if `rendering: 1`)
- Robot velocity vectors (if `show_velocity: True`)
- Console output: Simulation progress

---

### Task 4.2b: Order Parameter Analysis (Phase Transition)

**Goal**: Measure how heading noise affects flock coherence.

#### How to Run

1. Open [`config.yaml`](config.yaml)
2. Set `task42b.active: true` and ensure other tasks are set to `false`:
   ```yaml
   task42b:
     active: true
     rendering: 0                      # No visualization (faster)
     max_timestep: 3000                # Time per simulation
     save_trajectory: 0
     noise_levels: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
     runs_per_noise: 3                 # Runs per noise level
   ```
3. Run the simulation:
   ```bash
   python workspace.py
   ```

The script will automatically:
- Run simulations for each noise level (default: 11 levels × 3 runs = 33 simulations)
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

**Global Flocking Parameters** (same as Task 4.2a):
```yaml
number_of_agents: 20              # Swarm size
separation_weight: 5.0            # Strong separation
alignment_weight: 1.0
cohesion_weight: 0.02             # Weak cohesion (allows transition)
heading_noise: 0.0                # Overridden by task42b sweep
```

**Task 4.2b Sweep Parameters**:
```yaml
task42b:
  active: false                   # Toggle this task on/off
  rendering: 0                    # No visualization (faster)
  max_timestep: 3000              # Time per simulation
  save_trajectory: 0
  noise_levels: [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
  runs_per_noise: 3               # Runs per noise level for statistics
```

#### Output

The script generates:

1. **Console output**:
   ```
   TASK 4.2b: Flocking with Heading Noise
   
   Noise intensity η = 0.00:
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

3. **Summary statistics** (in console):
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

To improve results, edit [`config.yaml`](config.yaml):

| Goal | Change | Effect |
|------|--------|--------|
| Clearer transition | ↓ `cohesion_weight` | Looser flocking, easier to break up |
| Lower base order | ↑ `separation_weight` | Stronger repulsion |
| Smoother curves | ↑ `task42b.max_timestep` | Longer equilibration time |
| Less variance | ↑ `task42b.runs_per_noise` | Better statistics (slower) |
| More noise levels | Modify `task42b.noise_levels` | Finer resolution |
| Different transition point | Adjust all weights | Shift critical noise level |

**Example: Finer noise sweep**:
```yaml
task42b:
  noise_levels: [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 
                 0.55, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9, 0.95, 1.0]
  runs_per_noise: 5  # More runs for better statistics
```

---

## File Structure

```
Task 4.1 & 4.2 Files:
├── workspace.py                           # Main execution script (reads config)
├── config.yaml                            # All configuration parameters
├── Task04.md                              # This documentation
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
├── plots/                                 # Generated plots
│   ├── task42_order_parameter.png
│   └── task42_trajectories.png
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

**Symptoms**: Robots never stop, no clusters form

**Solutions**:
- ↑ Increase `aggregation_waiting_time` (robots wait longer)
- ↑ Increase `proximity_range` (detect neighbors from farther away)
- ↑ Increase `number_of_agents` (more robots = higher encounter rate)
- ↓ Decrease `default_velocity` (slower movement = more time to detect)

### Task 4.2a: Flock breaks apart

**Symptoms**: Robots scatter instead of forming cohesive group

**Solutions**:
- ↑ Increase `cohesion_weight` (stronger attraction to center)
- ↓ Decrease `separation_weight` (reduce repulsion)
- ↓ Decrease `heading_noise` (less random perturbation)
- ↑ Increase `alignment_weight` (stronger velocity matching)
- ↑ Increase `cohesion_radius` (wider attraction range)

### Task 4.2a: Robots collide too much

**Symptoms**: Robots overlap, chaotic movement

**Solutions**:
- ↑ Increase `separation_weight` (stronger repulsion)
- ↓ Decrease `separation_radius` (repel only when very close)
- ↑ Increase `min_separation_distance` (emergency separation threshold)
- ↓ Decrease `flock_speed` (slower = more control)

### Task 4.2b: High variance in order parameter

**Symptoms**: Order parameter jumps around, unclear transition

**Solutions**:
- ↑ Increase `task42b.max_timestep` (longer equilibration, steady state)
- ↑ Increase `task42b.runs_per_noise` (more samples = smoother curve)
- ↑ Increase `number_of_agents` (larger swarm, less stochastic noise)
- Adjust flocking weights for clearer transition

### Task 4.2b: No clear phase transition

**Symptoms**: Order parameter decreases linearly, no critical point

**Solutions**:
- ↓ Decrease `cohesion_weight` (make flock easier to break up)
- ↑ Increase `separation_weight` (create competition with alignment)
- Modify `task42b.noise_levels` to focus on specific range
- Increase swarm size (`number_of_agents`)

### Simulation too slow

**Symptoms**: Long runtime, especially for Task 4.2b

**Solutions**:
- Set `rendering: 0` in task-specific config (no visualization)
- ↓ Reduce `max_timestep` (shorter runs, may not reach equilibrium)
- ↓ Reduce `number_of_agents` (fewer robots, but changes dynamics)
- ↓ Reduce `task42b.runs_per_noise` (fewer samples, more variance)
- ↓ Reduce number of noise levels in `task42b.noise_levels`

### Plots not generated

**Symptoms**: No files in `plots/` directory

**Solutions**:
- Ensure simulation completes (check console for errors)
- Check that `matplotlib` is installed
- For Task 4.2b, at least one run must complete successfully

---

## Expected Results

### Task 4.1: Aggregation
- **Time to cluster**: ~1500-3000 timesteps (depends on density)
- **Number of clusters**: 1-3 (depends on initial distribution)
- **Cluster stability**: Robots remain aggregated once stopped
- **Trajectories**: Exploratory random walk → stationary aggregation

### Task 4.2a: Flocking
- **Time to synchronize**: ~500-1500 timesteps
- **Movement pattern**: Smooth collective rotation and translation
- **Order parameter**: High (~0.9-0.99) once synchronized
- **Visual**: Cohesive group moving as a unit

### Task 4.2b: Phase Transition

With default parameters (`cohesion_weight: 0.02`, `separation_weight: 5.0`):

- **No noise** ($\eta = 0.0$): $v_a \approx 0.99$ (perfectly ordered)
- **Low noise** ($\eta < 0.3$): $v_a \approx 0.90-0.95$ (strongly ordered)
- **Medium noise** ($\eta \approx 0.5$): $v_a \approx 0.5-0.7$ (transition region)
- **High noise** ($\eta > 0.8$): $v_a \approx 0.1-0.3$ (disordered)

**Critical point**: Typically near $\eta_c \approx 0.5\text{-}0.7$ (depends on weights)

**Expected plot shape**:
- Steep descent from high order
- Smooth transition (small swarms don't show sharp critical point)
- Plateau at low order for high noise

---

## Advanced Configuration

### Running Multiple Tasks Sequentially

Edit [`config.yaml`](config.yaml) to switch between tasks without modifying Python code:

```yaml
# Run Task 4.1 first
task41:
  active: true
task42a:
  active: false
task42b:
  active: false
```

Then change to:

```yaml
# Run Task 4.2b after
task41:
  active: false
task42a:
  active: false
task42b:
  active: true
```

### Custom Flocking Weights

Experiment with different force balances in [`config.yaml`](config.yaml):

**Tight flock** (stay close):
```yaml
separation_weight: 2.0    # Weak repulsion
alignment_weight: 1.5     # Strong alignment
cohesion_weight: 0.05     # Strong attraction
```

**Loose flock** (spread out):
```yaml
separation_weight: 8.0    # Strong repulsion
alignment_weight: 0.5     # Weak alignment
cohesion_weight: 0.01     # Weak attraction
```

**Milling behavior** (circular motion):
```yaml
separation_weight: 3.0
alignment_weight: 2.0     # Dominant force
cohesion_weight: 0.01
```

### Custom Noise Sweep

Focus on specific noise range in [`config.yaml`](config.yaml):

**Around critical point** (0.4-0.8):
```yaml
task42b:
  noise_levels: [0.4, 0.45, 0.5, 0.55, 0.6, 0.65, 0.7, 0.75, 0.8]
  runs_per_noise: 5
```

**Coarse sweep** (faster):
```yaml
task42b:
  noise_levels: [0.0, 0.25, 0.5, 0.75, 1.0]
  runs_per_noise: 2
```

---

## References

- **Reynolds Flocking**: C. W. Reynolds, "Flocks, Herds, and Schools: A Distributed Behavioral Model," *SIGGRAPH*, 1987
- **Order Parameter**: Vicsek et al., "Novel type of phase transition in a system of self-driven particles," *Physical Review Letters*, 1995
- **Toroidal Space**: Common in swarm robotics to eliminate boundary effects
- **Aggregation**: Widely used in swarm robotics for self-assembly and clustering

---

## Citation

Based on the Swarmy simulator by Samer Al-Magazachi.