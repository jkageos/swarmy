import math

import pygame

from swarmy.perception import Perception

# Reused across all agents per frame
_SPATIAL_GRID = {}
_SPATIAL_FRAME_AGENTLIST_ID = None  # tracks the list object identity for one frame


class BumperSensor(Perception):
    def __init__(self, agent, environment, config):
        super().__init__(agent, environment)
        self.agent = agent
        self.environment = environment
        self.config = config

        # Tunables
        self.collision_distance_threshold = 60
        self.cell_size = self.config.get("spatial_cell_size", 80)
        self.draw_bumpers = self.config.get("draw_bumpers", 1)

        # Precompute statics (never change)
        self._static_rects = [r[1] for r in self.environment.get_static_rect_list()]
        self._static_circles = [
            (c[1][0], c[1][1], c[2]) for c in self.environment.get_static_circ_list()
        ]

    def _build_spatial_grid_if_new_frame(self):
        """
        Build the spatial grid once per frame for all agents.
        We detect a new frame by a new agent_object_list instance created in Experiment.run().
        """
        global _SPATIAL_GRID, _SPATIAL_FRAME_AGENTLIST_ID
        agent_list_obj = self.environment.get_agent_object()
        cur_id = id(agent_list_obj)
        if _SPATIAL_FRAME_AGENTLIST_ID == cur_id:
            return  # already built for this frame

        # new frame: rebuild
        _SPATIAL_GRID = {}
        for rect in agent_list_obj:
            cx = rect.centerx // self.cell_size
            cy = rect.centery // self.cell_size
            _SPATIAL_GRID.setdefault((cx, cy), []).append(rect)

        _SPATIAL_FRAME_AGENTLIST_ID = cur_id

    def sensor(self):
        # Build grid once per frame
        self._build_spatial_grid_if_new_frame()

        rx, ry, heading = self.agent.get_position()

        # Precompute bumper endpoints (front + rear bars)
        def endpoint(base_angle, offset_angle, dist):
            ang = math.radians(base_angle + offset_angle)
            return (rx + math.sin(ang) * dist, ry + math.cos(ang) * dist)

        front_l = endpoint(heading, +40, 35)
        front_r = endpoint(heading, -40, 35)
        rear_l = endpoint(heading + 180, +40, 35)
        rear_r = endpoint(heading + 180, -40, 35)

        if self.draw_bumpers:
            self.environment.add_dynamic_line_object([(255, 0, 0), front_l, front_r])
            self.environment.add_dynamic_line_object([(255, 165, 0), rear_l, rear_r])

        # Fast distance pruning for static circles (squared distance, no sqrt)
        rr_margin = 40  # robot radius + safety
        rr_margin_sq = rr_margin * rr_margin
        rx_f = float(rx)
        ry_f = float(ry)
        for cx, cy, rad in self._static_circles:
            dx = rx_f - float(cx)
            dy = ry_f - float(cy)
            if dx * dx + dy * dy < float(rad + rr_margin) ** 2:
                return 1

        # Collect nearby rectangles via spatial hash (neighbors)
        cx = int(rx // self.cell_size)
        cy = int(ry // self.cell_size)
        nearby_rects = []
        for ox in (-1, 0, 1):
            for oy in (-1, 0, 1):
                cell = (cx + ox, cy + oy)
                rects = _SPATIAL_GRID.get(cell)
                if rects:
                    nearby_rects.extend(rects)

        # Include static rects (walls + static obstacles); few in number
        nearby_rects.extend(self._static_rects)

        # Line-line intersection helpers
        def line_intersects_line(p1, p2, p3, p4):
            x1, y1 = p1
            x2, y2 = p2
            x3, y3 = p3
            x4, y4 = p4
            denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
            if abs(denom) < 1e-9:
                return False
            t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / denom
            u = -((x1 - x2) * (y1 - y3) - (y1 - y2) * (x1 - x3)) / denom
            return 0 <= t <= 1 and 0 <= u <= 1

        def rect_edges(rect):
            l, r, t, b = rect.left, rect.right, rect.top, rect.bottom
            return [
                ((l, t), (r, t)),
                ((r, t), (r, b)),
                ((r, b), (l, b)),
                ((l, b), (l, t)),
            ]

        # Early AABB distance pruning for rects
        reach_sq = (35 + 15) ** 2  # bumper reach + half body
        rx_i, ry_i = int(rx), int(ry)
        for rect in nearby_rects:
            dx = rect.centerx - rx_i
            dy = rect.centery - ry_i
            if dx * dx + dy * dy > reach_sq:
                continue
            for e1, e2 in rect_edges(rect):
                if line_intersects_line(
                    front_l, front_r, e1, e2
                ) or line_intersects_line(rear_l, rear_r, e1, e2):
                    return 1

        return 0
