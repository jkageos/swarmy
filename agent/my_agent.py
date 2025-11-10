import random

import pygame

from swarmy.agent import Agent


class MyAgent(Agent):
    def __init__(self, environment, controller, sensor, config):
        super().__init__(environment, controller, sensor, config)

        self.environment = environment
        self.trajectory = []

    def initial_position(self):
        """
        Define the initial position of the agent.
        Ensures robots spawn in valid positions, not inside obstacles or other robots.
        """
        # Account for wall thickness (5 pixels) and robot bounding box (~30 pixels radius)
        wall_offset = 10  # Wall thickness
        robot_radius = 20  # Safe margin for robot size
        margin = wall_offset + robot_radius

        max_attempts = 100  # Prevent infinite loop

        for attempt in range(max_attempts):
            # Generate random position within safe bounds
            x = random.randint(margin, self.config["world_width"] - margin)
            y = random.randint(margin, self.config["world_height"] - margin)
            gamma = random.randint(0, 360)

            # Check if position collides with static obstacles
            collision_detected = False

            # Check against static rectangles (obstacles)
            for rect_obj in self.environment.get_static_rect_list():
                # Skip walls (the first 4 rectangles are walls)
                if rect_obj[2] == 5:  # Wall has border_width = 5
                    continue

                # Create a test rectangle at spawn position
                test_rect = pygame.Rect(x - 20, y - 20, 40, 40)  # Robot size
                if test_rect.colliderect(rect_obj[1]):
                    collision_detected = True
                    break

            # Check against static circles
            if not collision_detected:
                for circ_obj in self.environment.get_static_circ_list():
                    circle_center = pygame.Vector2(circ_obj[1])
                    circle_radius = circ_obj[2]
                    spawn_pos = pygame.Vector2(x, y)

                    # Check distance
                    dist = spawn_pos.distance_to(circle_center)
                    if dist < (circle_radius + 25):  # 25 = robot radius + margin
                        collision_detected = True
                        break

            # Check against other agents
            if not collision_detected:
                for agent_rect in self.environment.get_agent_object():
                    test_rect = pygame.Rect(x - 20, y - 20, 40, 40)
                    if test_rect.colliderect(agent_rect):
                        collision_detected = True
                        break

            # If no collision, use this position
            if not collision_detected:
                self.actuation.position[0] = x
                self.actuation.position[1] = y
                self.actuation.angle = gamma
                self.set_position(x, y, gamma)
                return

        # Fallback: if can't find free spot, place in center (should rarely happen)
        print(
            f"Warning: Could not find free spawn position after {max_attempts} attempts"
        )
        x = self.config["world_width"] // 2
        y = self.config["world_height"] // 2
        gamma = random.randint(0, 360)
        self.actuation.position[0] = x
        self.actuation.position[1] = y
        self.actuation.angle = gamma
        self.set_position(x, y, gamma)

    def save_information(self):
        """
        Save information of the agent, e.g. trajectory or the environmental plot.
        Hint:
        - Use pygame.draw.lines() to draw the trajectory of the robot and access the surface of the environment with self.environment.displaySurface
        - pygame allows to save an image of the current environment
        """
        print("Save information not implemented, check my_agent.py")
        """ your implementation here """

        pass
