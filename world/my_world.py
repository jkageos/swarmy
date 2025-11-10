import numpy as np
import pygame

from swarmy.environment import Environment


class My_environment(Environment):
    def __init__(self, config):
        self.config = config
        super().__init__(config)
        self.light_dist = self.defineLight()

    def add_static_rectangle_object(self):
        """
        Add static rectangle object to the environment such as walls or obstacles.
        Example:
            self.staticRectList.append(color, pygame.Rect(x, y, width, height), border_width))
        Returns:
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

        # Add obstacles in the arena
        self.staticRectList.append(
            ["RED", pygame.Rect(150, 150, 60, 60), 0]
        )  # Square obstacle
        self.staticRectList.append(
            ["RED", pygame.Rect(300, 100, 40, 150), 0]
        )  # Vertical obstacle
        self.staticRectList.append(
            ["RED", pygame.Rect(100, 300, 150, 40), 0]
        )  # Horizontal obstacle
        self.staticRectList.append(
            ["RED", pygame.Rect(350, 300, 50, 50), 0]
        )  # Small square

    def add_static_circle_object(self):
        """
        Add static circle object to the environment such as sources or sinks.
        Example:
            self.staticCircList.append([color, position, border_width, radius])
        Returns:
        """
        self.staticCircList.append(
            [(200, 0, 0), (250, 250), 30, 0]
        )  # Central circular obstacle

    def set_background_color(self):
        """
        Set the background color of the environment.
        Example:
            self.displaySurface.fill(self.BACKGROUND_COLOR)
        Hint: It is possible to use the light distribution to set the background color.
        For displaying a light distribution you might find pygame.surfarray.make_surface and self.displaySurface.blit useful)
        Returns:
        """
        self.displaySurface.fill(self.BACKGROUND_COLOR)

    ###  LIGHT DISTRIBUTION ###

    def defineLight(self):
        """
        Define the light distribution of the environment.
        Returns: 3 dimensional light distribution tuple (x,y,light_intensity)

        """
        """ your implementation here"""
        pass
