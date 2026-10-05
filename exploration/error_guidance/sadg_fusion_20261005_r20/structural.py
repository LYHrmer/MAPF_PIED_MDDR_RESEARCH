"""Public current-graph opportunity features and an explicit STOP query rule."""
from collections import defaultdict
import heapq
import math


def structural_features(graph, agents):
    vertices = {v["uid"]: v for v in graph["vertices"]}
    edges = list(graph["type1"])
    boundaries = []
    for group in graph["groups"]:
        edges.extend(d["active"] for d in group["dependencies"])
        if group["switchable"] and group["within_horizon"]:
            # Both candidate heads must remain STAGED. This explicit public
            # recheck cannot grant permission the common author guard withheld.
            if not all(d["reverse"] is not None and all(vertices[d[k][1]]["status"] == "STAGED"
                for k in ("forward", "reverse")) for d in group["dependencies"]):
                raise ValueError("public switchable flag violates all-head commitment")
            tails = {d[k][0] for d in group["dependencies"] for k in ("forward", "reverse")}
            boundaries.append((group["uid"], tails))
    outgoing = defaultdict(list)
    for tail, head in edges:
        if vertices[head]["status"] != "COMPLETED" and vertices[tail]["status"] != "COMPLETED":
            outgoing[tail].append(head)
    blocked = {a["current_vertex"]: a["agent_id"] for a in agents if a["blocked"]}
    result = {}
    for agent in agents:
        source = agent["current_vertex"]
        distances = {}
        if source is not None:
            v = vertices[source]
            initial = v["duration"] * (1-v["progress"]) if v["status"] == "IN_PROGRESS" else v["duration"]
            distances[source] = initial
            queue = [(initial, source)]
            while queue:
                distance, uid = heapq.heappop(queue)
                if distance != distances[uid]:
                    continue
                for target in outgoing[uid]:
                    proposed = distance + vertices[target]["duration"]
                    if proposed < distances.get(target, math.inf):
                        distances[target] = proposed
                        heapq.heappush(queue, (proposed, target))
        reached = [(group, min(distances[t] for t in tails if t in distances))
            for group, tails in boundaries if any(t in distances for t in tails)]
        frontier = sorted({aid for uid, aid in blocked.items() if uid in distances and aid != agent["agent_id"]})
        direct = sorted({blocked[uid] for uid in outgoing[source] if uid in blocked and blocked[uid] != agent["agent_id"]})
        result[agent["agent_id"]] = dict(
            legal_boundary_group_count=len(reached),
            legal_boundary_group_ids=sorted(g for g, _ in reached),
            boundary_path_time_min=min((distance for _, distance in reached), default=None),
            blocked_frontier_count=len(frontier), blocked_frontier_agents=frontier,
            direct_blocked_frontier_count=len(direct),
            structural_eligible=bool(agent["query_eligible"] and (reached or frontier)))
    return result


class StructuralStopPolicy:
    """History uncertainty × reachable legal/blocking structure, else STOP.

    Public path time is a shortest-path estimate ignoring AND dependencies,
    not a true ETA or safety deadline. There is no fitted value threshold.
    """
    name = "structural_history_stop"

    @staticmethod
    def score(agent, period):
        if not agent["structural_eligible"]:
            return 0.
        expected = max(1e-9, agent["nominal_duration"]*agent["history_ratio"])
        age = agent["elapsed"] if agent["last_measurement_age"] is None else agent["last_measurement_age"]
        uncertainty = agent["history_cv"] + max(0., agent["elapsed"]/expected-1.) + age/expected
        impact = agent["legal_boundary_group_count"] + agent["blocked_frontier_count"]
        distance = agent["boundary_path_time_min"]
        urgency = 1. if distance is None else 1./(1.+distance/max(period, 1e-9))
        return uncertainty*impact*urgency

    def __call__(self, snapshot):
        scored = [(self.score(a, snapshot["solve_period"]), a["agent_id"]) for a in snapshot["agents"]]
        scored.sort(key=lambda row: (-row[0], row[1]))
        return [aid for score, aid in scored[:snapshot["max_queries"]] if score > 0.]
