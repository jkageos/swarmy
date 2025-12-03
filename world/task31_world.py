import pygame

from swarmy.environment import Environment


class Task31Environment(Environment):
    def __init__(self, config):
        super().__init__(config)

    def add_static_rectangle_object(self):
        """
        Rectangular arena with 4 bounding walls and a few inner obstacles.
        """
        # Walls (5 px thick, inset by 5 px)
        self.staticRectList.append(
            ["BLACK", pygame.Rect(5, 5, self.width - 10, 5), 5]
        )  # top
        self.staticRectList.append(
            ["BLACK", pygame.Rect(5, self.height - 10, self.width - 10, 5), 5]
        )  # bottom
        self.staticRectList.append(
            ["BLACK", pygame.Rect(5, 5, 5, self.height - 10), 5]
        )  # left
        self.staticRectList.append(
            ["BLACK", pygame.Rect(self.width - 10, 5, 5, self.height - 10), 5]
        )  # right

        # Obstacles (thin rectangles)
        self.staticRectList.append(
            ["BLACK", pygame.Rect(self.width // 3, self.height // 3, 80, 10), 3]
        )
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(self.width // 2 + 60, self.height // 2 - 40, 10, 90),
                3,
            ]
        )
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(self.width // 4 + 30, self.height // 2 + 60, 120, 10),
                3,
            ]
        )

    def add_static_circle_object(self):
        """
        Optional circular obstacles (disabled by default).
        Example:
            self.staticCircList.append(['BLACK', (x, y), 3, radius])
        """
        # Uncomment to add circles:
        # self.staticCircList.append(['BLACK', (self.width//2, self.height//4), 3, 20])
        pass

    def set_background_color(self):
        self.displaySurface.fill(self.BACKGROUND_COLOR)
