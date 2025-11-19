import math

from swarmy.perception import Perception


class ProximitySensor(Perception):
    """
    Three proximity sensors (left, front, right) that detect distance to walls.
    Sensor range is ~15% of world width.
    Returns (1 - d/r) if obstacle detected at distance d within range r, else 0.
    """

    def __init__(self, agent, environment, config):
        super().__init__(agent, environment)
        self.agent = agent
        self.environment = environment
        self.config = config

        # Sensor range: 15% of world width
        self.sensor_range = int(0.15 * config["world_width"])

        # Sensor angles relative to robot heading
        self.sensor_angles = {
            "left": 45.0,  # front-left
            "front": 0.0,  # straight ahead
            "right": -45.0,  # front-right
        }

    def sensor(self) -> tuple[float, float, float]:
        """
        Calculate proximity sensor readings for left, front, and right sensors.
        Returns: (left_value, front_value, right_value)
        Each value is in range [0, 1] where 0 = no obstacle, 1 = obstacle very close
        """
        x, y, gamma = self.agent.get_position()

        # Calculate sensor readings for each direction
        left_value = self._ray_trace(x, y, gamma + self.sensor_angles["left"])
        front_value = self._ray_trace(x, y, gamma + self.sensor_angles["front"])
        right_value = self._ray_trace(x, y, gamma + self.sensor_angles["right"])

        # Optional: Visualize sensors
        if self.config.get("draw_proximity_sensors", 1):
            self._visualize_sensor(
                x, y, gamma + self.sensor_angles["left"], left_value, (0, 255, 0)
            )
            self._visualize_sensor(
                x, y, gamma + self.sensor_angles["front"], front_value, (0, 0, 255)
            )
            self._visualize_sensor(
                x, y, gamma + self.sensor_angles["right"], right_value, (255, 0, 0)
            )

        return (left_value, front_value, right_value)

    def _ray_trace(self, start_x: float, start_y: float, angle_deg: float) -> float:
        """
        Trace a ray from robot position in given direction.
        Returns sensor value (1 - d/r) if obstacle found, else 0.
        """
        # Convert angle to radians
        angle_rad = math.radians(angle_deg)

        # Direction vector
        dx = math.sin(angle_rad)
        dy = math.cos(angle_rad)

        # Sample along the ray at small increments
        step_size = 2  # pixels per step
        num_steps = int(self.sensor_range / step_size)

        for i in range(1, num_steps + 1):
            # Current point along ray
            test_x = start_x + dx * i * step_size
            test_y = start_y + dy * i * step_size

            # Check collision with all static rectangles (walls)
            for wall in self.environment.get_static_rect_list():
                wall_rect = wall[1]  # pygame.Rect object

                if wall_rect.collidepoint(int(test_x), int(test_y)):
                    # Calculate distance to obstacle
                    distance = i * step_size
                    # Return sensor value: 1 - d/r
                    return 1.0 - (distance / self.sensor_range)

        # No obstacle detected within range
        return 0.0

    def _visualize_sensor(
        self, x: float, y: float, angle_deg: float, sensor_value: float, color: tuple
    ):
        """Draw sensor beam for visualization"""
        angle_rad = math.radians(angle_deg)

        # End point of sensor beam
        beam_length = (
            self.sensor_range * (1.0 - sensor_value)
            if sensor_value > 0
            else self.sensor_range
        )
        end_x = x + math.sin(angle_rad) * beam_length
        end_y = y + math.cos(angle_rad) * beam_length

        # Color intensity based on sensor value
        if sensor_value > 0:
            # Brighter color when obstacle detected
            intensity = int(255 * sensor_value)
            draw_color = tuple(
                min(255, c + intensity) if c > 0 else intensity for c in color
            )
        else:
            draw_color = tuple(c // 3 for c in color)  # Dimmer when no obstacle

        self.environment.add_dynamic_line_object([draw_color, (x, y), (end_x, end_y)])
