from __future__ import annotations

import math
from typing import Tuple

import pygame

from swarmy.environment import Environment


class Task1World(Environment):
    """
    Toroidal 2D world with a single cone-shaped light source and helper kinematics.
    Space wraps like Pac-Man: what exits left re-enters right, etc.
    """

    def __init__(self, config):
        super().__init__(config)

        # Read world dimensions from config
        self.width = float(config["world_width"])
        self.height = float(config["world_height"])

        # Light source at center
        self.light_pos = (self.width * 0.5, self.height * 0.5)
        self.light_max_intensity = 1.0
        self.light_radius = min(self.width, self.height) * 0.4

        # Kinematics limits (per frame at 60 FPS)
        self.max_speed = 5.0  # px/frame (reasonable for 60 FPS)
        self.max_turn_rate = 5.0  # degrees/frame

    def add_static_rectangle_object(self):
        """No walls on a torus - override to prevent boundary walls"""
        pass

    def add_static_circle_object(self):
        """Add visual marker for light source center"""
        # Optionally add a visual marker at the light source
        pass

    def set_background_color(self):
        """Draw the light field gradient as background"""
        # Fill with base color
        self.displaySurface.fill(self.BACKGROUND_COLOR)

        # Draw light source visualization
        self._draw_light_field()

    def _draw_light_field(self):
        """Visualize the cone-shaped light field"""
        lx, ly = self.light_pos
        radius = int(self.light_radius)

        # Draw concentric circles showing light intensity gradient
        for r in range(radius, 0, -20):
            intensity = max(
                0.0, self.light_max_intensity * (1.0 - r / self.light_radius)
            )
            # Color gradient: darker at edges, lighter/yellow at center
            gray = int(255 * (1 - intensity * 0.5))  # Lighter = more intense
            color = (255, gray, gray)  # Yellowish to white gradient
            pygame.draw.circle(self.displaySurface, color, (int(lx), int(ly)), r, 2)

        # Draw light source center
        pygame.draw.circle(self.displaySurface, (255, 255, 0), (int(lx), int(ly)), 8)

    # --------- Geometry on a torus ---------

    def _torus_delta(self, a: float, b: float, size: float) -> float:
        """Calculate shortest delta on a torus (wrapping)"""
        d = a - b
        if abs(d) > size * 0.5:
            if d > 0:
                d -= size
            else:
                d += size
        return d

    def torus_distance(self, p: Tuple[float, float], q: Tuple[float, float]) -> float:
        """Calculate Euclidean distance on torus (shortest path)"""
        dx = self._torus_delta(p[0], q[0], self.width)
        dy = self._torus_delta(p[1], q[1], self.height)
        return math.hypot(dx, dy)

    def wrap_position(self, pos: Tuple[float, float]) -> Tuple[float, float]:
        """Wrap position to torus (Pac-Man wrapping)"""
        x = pos[0] % self.width
        y = pos[1] % self.height
        return (x, y)

    # --------- Light field ---------

    def light_intensity_at(self, pos: Tuple[float, float]) -> float:
        """
        Cone-shaped intensity: I(p) = max(0, I_max * (1 - d(p,s)/R))
        where d is toroidal distance from light source.

        Returns:
            float: Light intensity in range [0.0, 1.0]
        """
        d = self.torus_distance(pos, self.light_pos)
        if d >= self.light_radius:
            return 0.0
        return max(0.0, self.light_max_intensity * (1.0 - d / self.light_radius))

    # --------- Kinematics helpers ---------

    def clamp_velocity(self, v: float) -> float:
        """Clamp linear velocity to max_speed"""
        return max(-self.max_speed, min(self.max_speed, v))

    def clamp_turn_rate(self, omega: float) -> float:
        """Clamp angular velocity to max_turn_rate"""
        return max(-self.max_turn_rate, min(self.max_turn_rate, omega))
