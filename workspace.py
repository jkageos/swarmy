# =============================================================================
# created by:   Samer Al-Magazachi
# created on:   06/04/2021 -- 13/04/2022
# version:      0.9
# status:       prototype
# =============================================================================
import yaml

from swarmy.experiment import Experiment

### load the configuration file
with open("config.yaml", "r") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

## ============================================================================
## TASK 3.1: Single Robot Behaviors
## ============================================================================
# from agent.my_agent import MyAgent
# from controller.task31a_controller import CollisionAvoidanceController
# from controller.task31b_controller import WallFollowerController
# from controller.task31c_controller import VacuumCleanerController
# from controller.task31d_controller import LevyFlightController
# from sensors.bumper_sensor import BumperSensor
# from world.task31_world import Task31Environment

# # Choose which controller to test (uncomment one):
# agent_controller = [CollisionAvoidanceController]  # Task 3.1a
# agent_controller = [WallFollowerController]        # Task 3.1b
# agent_controller = [VacuumCleanerController]       # Task 3.1c
# agent_controller = [LevyFlightController]          # Task 3.1d

# # Add sensors
# agent_sensing = [BumperSensor]

# # Create and run experiment
# exp1 = Experiment(config, agent_controller, agent_sensing, Task31Environment, MyAgent)
# exp1.run(1)

## ============================================================================
## TASK 3.2: Potential Field Control
## ============================================================================
from agent.task32_agent import Task32Agent
from controller.task32a_controller import DirectGradientController
from controller.task32b_controller import IndirectGradientController
from world.task32_world import Task32Environment

# Choose which controller to test (uncomment one):
agent_controller = [DirectGradientController]  # Task 3.2a
# agent_controller = [IndirectGradientController]  # Task 3.2b

# No sensors needed for potential field navigation
agent_sensing = []

# Create and run experiment
exp1 = Experiment(
    config, agent_controller, agent_sensing, Task32Environment, Task32Agent
)
exp1.run(1)
