# =============================================================================
# created by:   Samer Al-Magazachi
# created on:   06/04/2021 -- 13/04/2022
# version:      0.9
# status:       prototype
# =============================================================================
import yaml

# from swarmy.experiment import Experiment

### load the configuration file, check the config.yaml file for more information and to change to your needs
with open("config.yaml", "r") as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

## Choose which task to run by uncommenting the appropriate section

# =============================================================================
# Task 1: Braitenberg vehicles with light sensors
# =============================================================================
# from agent.task1_agent import MyAgent
# from controller.task1_2_controller import BraitenbergController
# from sensors.bumper_sensor import BumperSensor
# from sensors.task1_2_sensor import DualLightSensor
# from world.task1_world import Task1World
#
# agent_controller = [BraitenbergController]
# agent_sensing = [BumperSensor, DualLightSensor]
# exp1 = Experiment(config, agent_controller, agent_sensing, Task1World, MyAgent)
# exp1.run(1)


# =============================================================================
# Task 2: Rule-based navigation with proximity sensors
# =============================================================================
# from agent.task2_agent import Task2Agent
# from controller.task2_controller import RuleBasedController
# from sensors.task2_sensor import ProximitySensor
# from world.task2_world import Task2World

# agent_controller = [RuleBasedController]
# agent_sensing = [ProximitySensor]
# exp1 = Experiment(config, agent_controller, agent_sensing, Task2World, Task2Agent)
# exp1.run(1)


# =============================================================================
# Task 4: Hill Climber Evolution for Robot Exploration
# =============================================================================
if __name__ == "__main__":
    from utils.hill_climber import run_hill_climber_experiment

    # Run hill climber evolution with multiple independent runs
    num_runs = 4

    # Set parallel=True to run experiments in parallel (faster on multi-core CPUs)
    # Set parallel=False for sequential execution (lower memory usage)
    results = run_hill_climber_experiment(config, num_runs=num_runs, parallel=True)

    print("\n✓ Hill climber experiment completed!")
    print(f"Best fitness achieved: {max(r['fitness'] for r in results)}")
