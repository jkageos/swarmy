import numpy as np
import pygame
from scipy.ndimage import gaussian_filter

from swarmy.environment import Environment


class Task32Environment(Environment):
    def __init__(self, config):
        super().__init__(config)
        self.potential_field = None
        self.generate_potential_field()

    def generate_potential_field(self):
        """Generate potential field: HIGH on LEFT (yellow), LOW on RIGHT (purple)"""
        self.potential_field = np.zeros((self.width, self.height))

        # 1. Base potential: Strong linear gradient from left to right
        for i in range(self.width):
            for j in range(self.height):
                x_normalized = i / self.width
                # Linear: 1.0 on far left, 0.0 on far right
                self.potential_field[i, j] = 1.0 - x_normalized

        # 2. Add 12 well-separated Gaussian obstacle peaks in a grid pattern
        # Divide arena into 4 columns x 3 rows = 12 positions
        num_cols = 4
        num_rows = 3

        # Calculate spacing to maximize separation
        col_spacing = self.width * 0.7 / (num_cols - 1)  # Use 70% of width
        row_spacing = self.height * 0.6 / (num_rows - 1)  # Use 60% of height

        # Starting offsets (centered)
        start_x = self.width * 0.2
        start_y = self.height * 0.2

        np.random.seed(42)  # For reproducibility

        for row in range(num_rows):
            for col in range(num_cols):
                # Base position on grid
                obs_x = start_x + col * col_spacing
                obs_y = start_y + row * row_spacing

                # Add small random jitter to avoid perfect grid
                obs_x += np.random.uniform(-30, 30)
                obs_y += np.random.uniform(-30, 30)

                # Varying obstacle sizes for visual interest
                amplitude = np.random.uniform(0.15, 0.30)
                sigma = np.random.uniform(25, 40)

                for i in range(self.width):
                    for j in range(self.height):
                        # Gaussian bump: e^(-(distance²)/(2σ²))
                        dist_sq = (i - obs_x) ** 2 + (j - obs_y) ** 2
                        gaussian = amplitude * np.exp(-dist_sq / (2 * sigma**2))
                        self.potential_field[i, j] += gaussian

        # 3. HIGH POTENTIAL WALLS at top and bottom borders (repel robot)
        border_width = 60
        border_strength = 0.8  # Strong repulsion

        for i in range(self.width):
            for j in range(self.height):
                # Top border (ADD potential = create wall)
                if j < border_width:
                    distance = (border_width - j) / border_width
                    self.potential_field[i, j] += border_strength * (distance**2)

                # Bottom border (ADD potential = create wall)
                if self.height - j - 1 < border_width:
                    distance = (border_width - (self.height - j - 1)) / border_width
                    self.potential_field[i, j] += border_strength * (distance**2)

        # 4. Ensure non-negative values
        self.potential_field = np.maximum(self.potential_field, 0)

        # 5. Smooth the entire field with Gaussian filter for extra smoothness
        self.potential_field = gaussian_filter(self.potential_field, sigma=2)

    def get_potential_value(self, x, y):
        """Get potential value at position (x, y)"""
        if self.potential_field is None:
            return 0.0
        i = int(np.clip(x, 0, self.width - 1))
        j = int(np.clip(y, 0, self.height - 1))
        return self.potential_field[i, j]

    def get_gradient(self, x, y):
        """
        Calculate gradient at position (x, y)
        Returns: (grad_x, grad_y)

        Gradient points UPHILL (increasing potential).
        Robot moves DOWNHILL (opposite to gradient).
        """
        if self.potential_field is None:
            return 0.0, 0.0

        i = int(np.clip(x, 1, self.width - 2))
        j = int(np.clip(y, 1, self.height - 2))

        # Central difference approximation
        grad_x = (self.potential_field[i + 1, j] - self.potential_field[i - 1, j]) / 2
        grad_y = (self.potential_field[i, j + 1] - self.potential_field[i, j - 1]) / 2

        return grad_x, grad_y

    def add_static_rectangle_object(self):
        """Physical walls for visualization"""
        wall_thickness = 3
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(5, 5, self.width - 10, wall_thickness),
                wall_thickness,
            ]
        )  # top
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(
                    5, self.height - 5 - wall_thickness, self.width - 10, wall_thickness
                ),
                wall_thickness,
            ]
        )  # bottom
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(5, 5, wall_thickness, self.height - 10),
                wall_thickness,
            ]
        )  # left
        self.staticRectList.append(
            [
                "BLACK",
                pygame.Rect(
                    self.width - 5 - wall_thickness, 5, wall_thickness, self.height - 10
                ),
                wall_thickness,
            ]
        )  # right

    def add_static_circle_object(self):
        """No static circles needed"""
        pass

    def set_background_color(self):
        """Display the potential field as background heatmap matching reference image"""
        if self.potential_field is None:
            self.displaySurface.fill(self.BACKGROUND_COLOR)
            return

        # Normalize potential field for visualization
        min_val = np.min(self.potential_field)
        max_val = np.max(self.potential_field)

        if max_val - min_val > 0:
            normalized = (
                (self.potential_field - min_val) / (max_val - min_val) * 255
            ).astype(int)
        else:
            normalized = np.zeros_like(self.potential_field, dtype=int)

        # FIXED COLOR MAPPING: Make high values BRIGHT ORANGE/YELLOW
        # Low potential (right) = DARK PURPLE/BLUE
        # High potential (left) = BRIGHT ORANGE/YELLOW
        for i in range(0, self.width, 4):
            for j in range(0, self.height, 4):
                value = normalized[i, j]

                if value < 85:
                    # Very low potential: DARK BLUE/PURPLE (right side)
                    r = 10
                    g = 0
                    b = int(50 + value * 0.8)
                elif value < 170:
                    # Medium potential: PURPLE to MAGENTA
                    t = (value - 85) / 85.0
                    r = int(10 + t * 170)
                    g = int(0 + t * 50)
                    b = int(120 + t * 135)
                else:
                    # High potential: BRIGHT ORANGE/YELLOW (left side + obstacles)
                    t = (value - 170) / 85.0
                    r = int(180 + t * 75)  # 180 → 255 (bright red)
                    g = int(50 + t * 165)  # 50 → 215 (yellow)
                    b = int(255 - t * 255)  # 255 → 0 (no blue)

                pygame.draw.rect(
                    self.displaySurface, (r, g, b), pygame.Rect(i, j, 4, 4)
                )
