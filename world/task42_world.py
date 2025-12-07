import pygame

from swarmy.environment import Environment


class Task42Environment(Environment):
    """
    Toroidal environment for flocking task.
    Periodic boundary conditions: robots wrap around edges.
    """

    def __init__(self, config):
        super().__init__(config)

    def add_static_rectangle_object(self):
        """
        No walls in toroidal space - robots wrap around instead.
        Optional: Draw boundary lines for visualization only (no collision).
        """
        # Draw boundary lines (visual only, not physical barriers)
        wall_thickness = 2
        self.staticRectList.append(
            [
                "GRAY",
                pygame.Rect(0, 0, self.width, wall_thickness),
                wall_thickness,
            ]
        )  # top
        self.staticRectList.append(
            [
                "GRAY",
                pygame.Rect(
                    0, self.height - wall_thickness, self.width, wall_thickness
                ),
                wall_thickness,
            ]
        )  # bottom
        self.staticRectList.append(
            [
                "GRAY",
                pygame.Rect(0, 0, wall_thickness, self.height),
                wall_thickness,
            ]
        )  # left
        self.staticRectList.append(
            [
                "GRAY",
                pygame.Rect(
                    self.width - wall_thickness, 0, wall_thickness, self.height
                ),
                wall_thickness,
            ]
        )  # right

    def add_static_circle_object(self):
        """
        No static circles in this task.
        """
        pass

    def set_background_color(self):
        """
        Simple white background.
        """
        self.displaySurface.fill(self.BACKGROUND_COLOR)
