import math

from swarmy.perception import Perception


class DualLightSensor(Perception):
    """
    Dual light sensors positioned at front-left and front-right of the robot.
    Returns a tuple (left_intensity, right_intensity).
    """

    def __init__(self, agent, environment, config):
        super().__init__(agent, environment)
        self.agent = agent
        self.environment = environment
        self.config = config
        self.sensor_offset = config.get("sensor_offset", 15.0)
        self.sensor_angle = config.get("sensor_angle", 45.0)

    def sensor(self) -> tuple[float, float]:
        """
        Calculate positions of left and right sensors based on robot position and heading.
        Returns: (left_intensity, right_intensity)
        """
        x, y, gamma = self.agent.get_position()

        # Convert heading to radians
        heading_rad = math.radians(gamma)

        # Calculate left sensor position (front-left)
        left_angle = heading_rad + math.radians(self.sensor_angle)
        left_x = x + self.sensor_offset * math.cos(left_angle)
        left_y = y + self.sensor_offset * math.sin(left_angle)

        # Calculate right sensor position (front-right)
        right_angle = heading_rad - math.radians(self.sensor_angle)
        right_x = x + self.sensor_offset * math.cos(right_angle)
        right_y = y + self.sensor_offset * math.sin(right_angle)

        # Wrap sensor positions on torus
        left_pos = self.environment.wrap_position((left_x, left_y))
        right_pos = self.environment.wrap_position((right_x, right_y))

        # Get light intensities at sensor positions
        left_intensity = float(self.environment.light_intensity_at(left_pos))
        right_intensity = float(self.environment.light_intensity_at(right_pos))

        print(f"Left sensor pos: {left_pos}, intensity: {left_intensity}")
        print(f"Right sensor pos: {right_pos}, intensity: {right_intensity}")

        return (left_intensity, right_intensity)
