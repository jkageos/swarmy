from __future__ import annotations

import pygame

from swarmy.environment import Environment


class Task2World(Environment):
    """
    Bounded 2D world with internal walls and boundary walls.
    Space is a square from (0,0) to (world_width, world_height).
    Internal walls as per Fig. 1a description (scaled to world dimensions).
    """

    def __init__(self, config):
        super().__init__(config)

        # Read world dimensions from config
        self.width = float(config["world_width"])
        self.height = float(config["world_height"])

        # Kinematics limits (per frame at 60 FPS)
        self.max_speed = 5.0  # px/frame
        self.max_turn_rate = 5.0  # degrees/frame

    def add_static_rectangle_object(self):
        """Add boundary walls and internal walls"""
        wall_thickness = 5

        # Boundary walls (black)
        # Top wall
        self.staticRectList.append(
            ["BLACK", pygame.Rect(0, 0, self.width, wall_thickness), 0]
        )
        # Left wall
        self.staticRectList.append(
            ["BLACK", pygame.Rect(0, 0, wall_thickness, self.height), 0]
        )
        # Bottom wall
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(
                    0, self.height - wall_thickness, self.width, wall_thickness
                ),
                0,
            ]
        )
        # Right wall
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(
                    self.width - wall_thickness, 0, wall_thickness, self.height
                ),
                0,
            ]
        )

        # Internal walls (red) - based on Fig. 1a description
        # Wall 1: from (0, 0.4) to (0.3, 0.4) - horizontal wall
        wall1_y = int(0.4 * self.height)
        wall1_width = int(0.3 * self.width)
        self.staticRectList.append(
            ["RED", pygame.Rect(0, wall1_y, wall1_width, wall_thickness), 0]
        )

        # Wall 2: from (0.5, 0) to (0.5, 0.8) - vertical wall
        wall2_x = int(0.5 * self.width)
        wall2_height = int(0.8 * self.height)
        self.staticRectList.append(
            ["RED", pygame.Rect(wall2_x, 0, wall_thickness, wall2_height), 0]
        )

        # Wall 3: from (0.7, 0.6) to (1, 0.6) - horizontal wall
        wall3_x = int(0.7 * self.width)
        wall3_y = int(0.6 * self.height)
        wall3_width = int(0.3 * self.width)
        self.staticRectList.append(
            ["RED", pygame.Rect(wall3_x, wall3_y, wall3_width, wall_thickness), 0]
        )

    def add_static_circle_object(self):
        """No static circles in this world"""
        pass

    def set_background_color(self):
        """Set plain background"""
        self.displaySurface.fill(self.BACKGROUND_COLOR)

    def clamp_velocity(self, v: float) -> float:
        """Clamp linear velocity to max_speed"""
        return max(-self.max_speed, min(self.max_speed, v))

    def clamp_turn_rate(self, omega: float) -> float:
        """Clamp angular velocity to max_turn_rate"""
        return max(-self.max_turn_rate, min(self.max_turn_rate, omega))
