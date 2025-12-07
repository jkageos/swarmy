import pygame

from swarmy.environment import Environment


class Task41Environment(Environment):
    """
    Simple rectangular arena for swarm aggregation task.
    Open arena with walls to contain the robots.
    """

    def __init__(self, config):
        super().__init__(config)

    def add_static_rectangle_object(self):
        """
        Add boundary walls for the arena.
        """
        wall_thickness = 5

        # Top wall
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(5, 5, self.width - 10, wall_thickness),
                wall_thickness,
            ]
        )
        # Bottom wall
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(5, self.height - 10, self.width - 10, wall_thickness),
                wall_thickness,
            ]
        )
        # Left wall
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(5, 5, wall_thickness, self.height - 10),
                wall_thickness,
            ]
        )
        # Right wall
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(self.width - 10, 5, wall_thickness, self.height - 10),
                wall_thickness,
            ]
        )

    def add_static_circle_object(self):
        """
        No static circles needed for this task.
        """
        pass

    def set_background_color(self):
        """
        Simple white background.
        """
        self.displaySurface.fill(self.BACKGROUND_COLOR)
