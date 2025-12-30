from swarmy.perception import Perception


class Task6Sensor(Perception):
    """
    Simple bumper sensor for Task 6 collision detection.
    Returns [sensor_id, collision_flag] where collision_flag is 1 if collision detected.
    """

    def __init__(self, agent, environment, config):
        super().__init__(agent, environment)
        self.agent = agent
        self.environment = environment
        self.config = config

    def sensor(self):
        """
        Detect collisions with walls and other agents.
        Returns [sensor_id, collision_value]
        """
        collision = 0

        # Get agent's position and create bounding box
        x, y, _ = self.agent.get_position()
        agent_rect = self.agent.body.rect
        agent_rect.centerx = x
        agent_rect.centery = y

        # Check collision with static rectangles (walls)
        for rect_obj in self.environment.get_static_rect_list():
            # Skip walls with border_width = 5 (they are just visual boundaries)
            if rect_obj[2] == 5:
                continue
            if agent_rect.colliderect(rect_obj[1]):
                collision = 1
                break

        # Check collision with static circles (if any)
        if collision == 0:
            for circle_obj in self.environment.get_static_circ_list():
                circle_center = circle_obj[1]
                circle_radius = circle_obj[2]
                # Calculate distance from agent center to circle center
                dx = x - circle_center[0]
                dy = y - circle_center[1]
                distance = (dx * dx + dy * dy) ** 0.5
                if distance < (circle_radius + agent_rect.width / 2):
                    collision = 1
                    break

        # Check collision with other agents
        if collision == 0:
            for other_rect in self.environment.get_agent_object():
                # Skip self
                if agent_rect.colliderect(other_rect) and other_rect != agent_rect:
                    collision = 1
                    break

        return [6, collision]  # sensor_id=6 for Task 6
