# =============================================================================
# created by:   Samer Al-Magazachi
# created on:   06/04/2021 -- 13/04/2022
# version:      0.9
# status:       prototype
# =============================================================================
import yaml

from swarmy.experiment import Experiment

### load the configuration file, check the config.yaml file for more information and to change to your needs
with open("config.yaml", "r") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)
## Import your implementation of the controller, sensor, environment and agent

# Task 2: Rule-based navigation with proximity sensors
from agent.task2_agent import Task2Agent
from controller.task2_controller import RuleBasedController
from sensors.task2_sensor import ProximitySensor
from world.task2_world import Task2World

# add your controller
agent_controller = [RuleBasedController]
# add your sensors
agent_sensing = [ProximitySensor]

exp1 = Experiment(config, agent_controller, agent_sensing, Task2World, Task2Agent)

exp1.run(1)
