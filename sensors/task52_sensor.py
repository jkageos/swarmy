import numpy as np

from swarmy.perception import Perception


class ColorSensor(Perception):
    """
    Counts black and total robots within sensing radius r (normalized [0,1]).
    Includes self in counts.
    """

    def __init__(self, agent, environment, config):
        super().__init__(agent, environment)
        self.agent = agent
        self.environment = environment
        self.config = config

        world_w = config["world_width"]
        world_h = config["world_height"]
        diag = float(np.hypot(world_w, world_h))
        self.range_px = float(config["sensor_range"]) * diag
        self.range_px_sq = self.range_px**2

    def sensor(self):
        ax, ay, _ = self.agent.get_position()
        pos = np.array([ax, ay], dtype=float)

        black = 1 if getattr(self.agent, "color", "white") == "black" else 0
        total = 1

        for other in self.environment.agentlist:
            if other.unique_id == self.agent.unique_id:
                continue
            ox, oy, _ = other.get_position()
            dx = ax - ox
            dy = ay - oy
            if dx * dx + dy * dy <= self.range_px_sq:
                total += 1
                if getattr(other, "color", "white") == "black":
                    black += 1

        if self.config.get("rendering", 1) == 1:
            self.environment.add_dynamic_circle_object(
                [
                    (0, 0, 0)
                    if getattr(self.agent, "color", "white") == "black"
                    else (200, 200, 200),
                    (int(pos[0]), int(pos[1])),
                    int(self.range_px),
                    1,
                ]
            )

        return (black, total)
