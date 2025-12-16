import pygame

from swarmy.environment import Environment


class Task52Environment(Environment):
    """
    Unit square (scaled) with simple visual boundaries.
    """

    def __init__(self, config):
        super().__init__(config)

    def add_static_rectangle_object(self):
        t = 2
        self.staticRectList.append(["GRAY", pygame.Rect(0, 0, self.width, t), t])  # top
        self.staticRectList.append(
            ["GRAY", pygame.Rect(0, self.height - t, self.width, t), t]
        )  # bottom
        self.staticRectList.append(
            ["GRAY", pygame.Rect(0, 0, t, self.height), t]
        )  # left
        self.staticRectList.append(
            ["GRAY", pygame.Rect(self.width - t, 0, t, self.height), t]
        )  # right

    def add_static_circle_object(self):
        pass

    def set_background_color(self):
        self.displaySurface.fill(self.BACKGROUND_COLOR)
