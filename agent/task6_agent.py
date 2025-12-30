import random

import pygame

from swarmy.agent import Agent


class Task6Agent(Agent):
    """
    Agent for swarm aggregation with support for anti-agents.
    Regular agents aggregate together, while anti-agents can command them to leave clusters.
    """

    def __init__(self, environment, controller, sensor, config):
        super().__init__(environment, controller, sensor, config)
        self.environment = environment
        self.trajectory = []
        self.is_anti_agent = False
        self.in_cluster = False
        self.cluster_id = None
        self.cluster_size = 0
        self.last_position = None

    def initial_position(self):
        """
        Spawn agent at random position avoiding obstacles.
        """
        wall_offset = 10
        robot_radius = 20
        margin = wall_offset + robot_radius
        max_attempts = 100

        for attempt in range(max_attempts):
            x = random.randint(margin, self.config["world_width"] - margin)
            y = random.randint(margin, self.config["world_height"] - margin)
            gamma = random.randint(0, 360)

            collision_detected = False

            # Check against static rectangles (obstacles)
            for rect_obj in self.environment.get_static_rect_list():
                if rect_obj[2] == 5:  # Wall has border_width = 5
                    continue
                test_rect = pygame.Rect(x - 20, y - 20, 40, 40)
                if test_rect.colliderect(rect_obj[1]):
                    collision_detected = True
                    break

            # Check against static circles
            if not collision_detected:
                for circ_obj in self.environment.get_static_circ_list():
                    circle_center = pygame.Vector2(circ_obj[1])
                    circle_radius = circ_obj[2]
                    spawn_pos = pygame.Vector2(x, y)
                    dist = spawn_pos.distance_to(circle_center)
                    if dist < (circle_radius + 25):
                        collision_detected = True
                        break

            # Check against other agents
            if not collision_detected:
                for agent_rect in self.environment.get_agent_object():
                    test_rect = pygame.Rect(x - 20, y - 20, 40, 40)
                    if test_rect.colliderect(agent_rect):
                        collision_detected = True
                        break

            if not collision_detected:
                self.actuation.position[0] = x
                self.actuation.position[1] = y
                self.actuation.angle = gamma
                self.set_position(x, y, gamma)
                self.last_position = (x, y)
                return

        # Fallback: center position
        x = self.config["world_width"] // 2
        y = self.config["world_height"] // 2
        gamma = random.randint(0, 360)
        self.actuation.position[0] = x
        self.actuation.position[1] = y
        self.actuation.angle = gamma
        self.set_position(x, y, gamma)
        self.last_position = (x, y)

    def assign_controller_and_sensors(self):
        """
        Already handled in __init__ by parent class.
        """
        pass

    def save_information(self, final_save=False):
        """
        Save trajectory and cluster information.
        """
        if final_save and self.trajectory:
            print(f"Agent {self.unique_id} trajectory length: {len(self.trajectory)}")

    def update_cluster_info(self, neighbors_count):
        """
        Update cluster membership based on neighbor count.
        """
        self.cluster_size = neighbors_count
        self.in_cluster = neighbors_count > 0

    def receive_leave_command(self):
        """
        Handle command from anti-agent to leave cluster.
        """
        self.in_cluster = False
        self.cluster_id = None
        self.cluster_size = 0
