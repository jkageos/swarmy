from swarmy.actuation import Actuation


class SamplingController(Actuation):
    """
    Local sampling: each agent senses neighbors and stores the local estimate.
    No movement is required for the sampling step.
    """

    def __init__(self, agent, config):
        super().__init__(agent)
        self.config = config
        self.init_pos = True
        self.local_estimate = 0.0

    def controller(self):
        if self.init_pos:
            self.agent.initial_position()
            self.init_pos = False

        # sensor() returns (black_count, total_count)
        sensor_data = self.agent.get_perception()
        black, total = sensor_data[1]
        if total > 0:
            self.local_estimate = black / total
        else:
            self.local_estimate = 0.0

        # store on agent for aggregation later
        self.agent.local_estimate = self.local_estimate

    def torus(self):
        pass
