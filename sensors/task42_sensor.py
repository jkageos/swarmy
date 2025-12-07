import numpy as np

from swarmy.perception import Perception


class FlockingSensor(Perception):
    """
    Sensor that detects neighboring robots within a specified range.
    Returns positions and velocities of neighbors for flocking computation.
    """

    def __init__(self, agent, environment, config):
        super().__init__(agent, environment)
        self.agent = agent
        self.environment = environment
        self.config = config
        self.max_sensing_radius = config.get("max_sensing_radius", 100)

    def sensor(self):
        """
        Detect neighboring robots and return their relative positions and velocities.

        Returns:
            neighbors: List of (relative_pos, neighbor_velocity, distance)
        """
        robot_x, robot_y, robot_heading = self.agent.get_position()
        robot_pos = np.array([robot_x, robot_y])

        neighbors = []

        # Check all other robots
        for other_agent in self.environment.agentlist:
            if other_agent.unique_id == self.agent.unique_id:
                continue  # Skip self

            other_x, other_y, _ = other_agent.get_position()
            other_pos = np.array([other_x, other_y])

            # Get neighbor velocity
            if hasattr(other_agent.actuation, "velocity"):
                other_vel = np.array(other_agent.actuation.velocity)
            else:
                other_vel = np.array([0.0, 0.0])

            # Compute relative position in toroidal space
            delta = other_pos - robot_pos
            delta[0] = (
                (delta[0] + self.environment.width / 2) % self.environment.width
            ) - self.environment.width / 2
            delta[1] = (
                (delta[1] + self.environment.height / 2) % self.environment.height
            ) - self.environment.height / 2

            distance = np.linalg.norm(delta)

            # Include neighbor if within sensing radius
            if distance > 0 and distance <= self.max_sensing_radius:
                neighbors.append((delta, other_vel, distance))

        # Visualize sensing range (convert to integers for pygame)
        if self.config.get("rendering", 1) == 1:
            self.environment.add_dynamic_circle_object(
                [
                    (0, 200, 200),
                    (int(robot_x), int(robot_y)),
                    2,
                    int(self.max_sensing_radius),
                ]
            )

        return neighbors
