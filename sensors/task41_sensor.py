import numpy as np

from swarmy.perception import Perception


class ProximitySensor(Perception):
    """
    Sensor that detects nearby robots within a specified range.
    Returns the distance to the nearest robot, or -1 if no robot is nearby.
    """

    def __init__(self, agent, environment, config):
        super().__init__(agent, environment)
        self.agent = agent
        self.environment = environment
        self.config = config
        self.detection_range = config.get(
            "proximity_range", 80
        )  # Detection range in pixels

    def sensor(self):
        """
        Detect nearby robots within detection_range.

        Returns:
            distance (float): Distance to nearest robot, or -1 if no robot nearby

        Visualization:
            - Green circle: detection range
            - Red line: vector to nearest robot
        """
        robot_x, robot_y, robot_heading = self.agent.get_position()
        robot_pos = np.array([robot_x, robot_y])

        min_distance = float("inf")
        nearest_robot_pos = None

        # Check distance to all other robots
        for other_agent in self.environment.agentlist:
            if other_agent.unique_id == self.agent.unique_id:
                continue  # Skip self

            other_x, other_y, _ = other_agent.get_position()
            other_pos = np.array([other_x, other_y])

            distance = np.linalg.norm(robot_pos - other_pos)

            if distance < min_distance:
                min_distance = distance
                nearest_robot_pos = other_pos

        # Visualize detection range (optional, can be toggled)
        if self.config.get("rendering", 1) == 1:
            self.environment.add_dynamic_circle_object(
                [(0, 255, 0), (robot_x, robot_y), 2, self.detection_range]
            )

        # If robot found within range, visualize direction
        if min_distance <= self.detection_range and nearest_robot_pos is not None:
            if self.config.get("rendering", 1) == 1:
                self.environment.add_dynamic_line_object(
                    [
                        (255, 0, 0),
                        (robot_x, robot_y),
                        (nearest_robot_pos[0], nearest_robot_pos[1]),
                    ]
                )
            return min_distance
        else:
            return -1  # No robot detected
