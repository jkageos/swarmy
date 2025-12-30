import math
import random

from swarmy.actuation import Actuation


class Task6Controller(Actuation):
    """
    Controller for swarm aggregation behavior.
    Regular agents: Random walk with attraction to neighbors.
    Anti-agents: Random walk with communication capability.
    """

    def __init__(self, agent, config):
        super().__init__(agent)
        self.agent = agent
        self.config = config
        self.init_pos = True

        self.linear_velocity = config.get("default_velocity", 2)
        self.angle_velocity = config.get("default_angle_velocity", 5)
        self.aggregation_range = config.get("task6_aggregation_range", 80)
        self.attraction_probability = config.get("task6_attraction_probability", 0.3)
        self.random_walk_probability = config.get("task6_random_walk_probability", 0.1)
        self.anti_agent_comm_range = config.get("task6_anti_agent_comm_range", 120)
        self.anti_agent_leave_threshold = config.get(
            "task6_anti_agent_leave_threshold", 2
        )

        # Boundary setup
        wall_thickness = 10
        robot_radius = 20
        margin = wall_thickness + robot_radius
        self.min_x = margin
        self.max_x = config["world_width"] - margin
        self.min_y = margin
        self.max_y = config["world_height"] - margin

    def is_near_boundary(self):
        """Check if agent is near world boundary."""
        x, y, _ = self.agent.get_position()
        tolerance = 15
        return (
            x <= self.min_x + tolerance
            or x >= self.max_x - tolerance
            or y <= self.min_y + tolerance
            or y >= self.max_y - tolerance
        )

    def find_nearby_agents(self):
        """
        Find agents within aggregation range.
        Returns list of nearby agents.
        """
        nearby = []
        ax, ay, _ = self.agent.get_position()

        agent_list = self.agent.environment.agentlist
        for other_agent in agent_list:
            if other_agent.unique_id == self.agent.unique_id:
                continue

            ox, oy, _ = other_agent.get_position()
            dist = math.sqrt((ax - ox) ** 2 + (ay - oy) ** 2)

            if dist < self.aggregation_range:
                nearby.append((other_agent, dist))

        return nearby

    def aggregate_towards_neighbors(self, nearby_agents):
        """
        Move towards the centroid of nearby agents.
        """
        if not nearby_agents:
            return

        # Calculate centroid of nearby agents
        cx = sum(agent.get_position()[0] for agent, _ in nearby_agents) / len(
            nearby_agents
        )
        cy = sum(agent.get_position()[1] for agent, _ in nearby_agents) / len(
            nearby_agents
        )

        ax, ay, heading = self.agent.get_position()

        # Calculate direction to centroid
        dx = cx - ax
        dy = cy - ay
        target_angle = math.degrees(math.atan2(dx, dy)) % 360

        # Gradually turn towards target
        current_heading = heading % 360
        angle_diff = (target_angle - current_heading) % 360

        if angle_diff > 180:
            angle_diff -= 360

        if angle_diff > 0:
            self.turn_left(min(self.angle_velocity * 2, abs(angle_diff)))
        elif angle_diff < 0:
            self.turn_right(min(self.angle_velocity * 2, abs(angle_diff)))

        # Move forward
        self.stepForward(self.linear_velocity)

    def send_leave_commands(self, agent_list):
        """
        Anti-agents send leave commands to nearby regular agents that are in clusters.
        Probability of sending command depends on cluster size.
        """
        if not self.agent.is_anti_agent:
            return

        ax, ay, _ = self.agent.get_position()

        for agent in agent_list:
            if agent.is_anti_agent:
                continue

            # Calculate distance to agent
            gx, gy, _ = agent.get_position()
            dist = ((ax - gx) ** 2 + (ay - gy) ** 2) ** 0.5

            # Check if within communication range
            if dist < self.anti_agent_comm_range:
                # Only send command if agent is in a cluster
                if (
                    agent.in_cluster
                    and agent.cluster_size >= self.anti_agent_leave_threshold
                ):
                    # Probability increases with cluster size
                    prob_send = min(0.9, 0.5 + (agent.cluster_size * 0.15))
                    if random.random() < prob_send:
                        agent.receive_leave_command()

    def controller(self):
        """
        Main control loop for aggregation behavior.
        """
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False

        # Get sensor data (bumper collision detection)
        sensor_data = self.agent.get_perception()
        bumper_hit = sensor_data[1] == 1 if len(sensor_data) > 1 else False
        boundary_hit = self.is_near_boundary()
        collision = bumper_hit or boundary_hit

        if collision:
            # Escape collision
            self.stepBackward(self.linear_velocity)
            self.turn_right(self.angle_velocity * random.randint(2, 4))
            return

        # Find nearby agents for aggregation
        nearby_agents = self.find_nearby_agents()
        self.agent.update_cluster_info(len(nearby_agents))

        # Anti-agents send leave commands
        if self.agent.is_anti_agent:
            agent_list = self.agent.environment.agentlist
            self.send_leave_commands(agent_list)

            # Anti-agents do random walk
            if random.random() < self.random_walk_probability:
                delta = random.randint(-2, 2) * self.angle_velocity
                if delta > 0:
                    self.turn_left(delta)
                elif delta < 0:
                    self.turn_right(-delta)

            self.stepForward(self.linear_velocity)
        else:
            # Regular agents: aggregate if neighbors present, else random walk
            if (
                nearby_agents
                and not self.agent.in_cluster
                and random.random() < self.attraction_probability
            ):
                self.aggregate_towards_neighbors(nearby_agents)
            else:
                # Random walk
                if random.random() < self.random_walk_probability:
                    delta = random.randint(-2, 2) * self.angle_velocity
                    if delta > 0:
                        self.turn_left(delta)
                    elif delta < 0:
                        self.turn_right(-delta)

                self.stepForward(self.linear_velocity)

        # Apply boundary constraints
        self.torus()

    def torus(self):
        """Apply boundary constraints (clamp to world bounds)."""
        x, y, ang = self.agent.get_position()
        cx = max(self.min_x, min(x, self.max_x))
        cy = max(self.min_y, min(y, self.max_y))
        if cx != x or cy != y:
            self.agent.set_position(cx, cy, ang)
