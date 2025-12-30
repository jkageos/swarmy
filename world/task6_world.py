import pygame

from swarmy.environment import Environment


class Task6Environment(Environment):
    """
    Environment for swarm aggregation task with anti-agents.
    Provides an empty arena with walls for robots to aggregate.
    """

    def __init__(self, config):
        self.config = config
        super().__init__(config)

    def add_static_rectangle_object(self):
        """
        Add boundary walls to the environment.
        """
        # Boundary walls
        self.staticRectList.append(
            ["BLACK", pygame.Rect(5, 5, self.config["world_width"] - 10, 5), 5]
        )
        self.staticRectList.append(
            ["BLACK", pygame.Rect(5, 5, 5, self.config["world_height"] - 10), 5]
        )
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(
                    5,
                    self.config["world_height"] - 10,
                    self.config["world_width"] - 10,
                    5,
                ),
                5,
            ]
        )
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(
                    self.config["world_width"] - 10,
                    5,
                    5,
                    self.config["world_height"] - 10,
                ),
                5,
            ]
        )

    def add_static_circle_object(self):
        """
        No static circles for aggregation task.
        """
        pass

    def set_background_color(self):
        """
        Set the background to white.
        """
        self.displaySurface.fill((255, 255, 255))
