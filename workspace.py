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

# Use the Task 1.2 implementations (Braitenberg vehicles)
from agent.task1_agent import MyAgent
from controller.task1_2_controller import BraitenbergController
from sensors.bumper_sensor import BumperSensor
from sensors.task1_2_sensor import DualLightSensor
from world.task1_world import Task1World

# add your controller, if you have more than one controller, add them to the list and specify the percentage of robots that should use this controller in the config.yaml file
agent_controller = [BraitenbergController]
# add your sensors, if you have more than one sensor, add them to the list all sensors are added to each robot
agent_sensing = [BumperSensor, DualLightSensor]

exp1 = Experiment(config, agent_controller, agent_sensing, Task1World, MyAgent)

exp1.run(1)
