"""Successor adapter; frozen T1 source, packets and original evidence stay intact."""
from copy import deepcopy

from composition import CONDITION
from timed_constraints import Certificates, CertificateBudget
from interface import Box
from timed_session import TaskSession, AuthorTaskEvents
from timed_protocol import Binding, Costs, TaskInbox
from source_qualification import phase_segments, physical_windows, extreme_window, WindowBudget
from feedback_qualification import CausalClock


class EndpointCertificates(Certificates):
    """Shared engineering optimization; preserves every T1 compiled window."""
    def visits(self, name, region):
        key = (name, region)
        if key in self.cache:
            self.operations['phase_cache_hits'] += 1
            return self.cache[key]
        robot, index = self.problem['finite'][name]
        tr = self.problem['trajectories'][robot]
        lo, hi = self.problem['intervals'][name]
        try:
            result = extreme_window(lo, hi, lambda a, b: Box(*tr.action_box(index, a, b)).separated(region),
                                    resolution=self.resolution, max_nodes=self.limit)
        except WindowBudget as exc:
            self.operations['phase_cells'] += exc.nodes
            raise CertificateBudget(str(exc)) from exc
        self.operations['phase_cells'] += result['nodes']
        self.cache[key] = result['window']
        return result['window']


class CheckedSession(TaskSession):
    def __init__(self, problem, author, *, engine, costs=None, certificate_factory=Certificates):
        if engine not in ('guard', 'SADG_events'):
            raise ValueError('unregistered engine')
        self.problem, self._qualified_problem = deepcopy(problem), deepcopy(problem)
        problem = self.problem
        self.engine, self.costs = engine, costs if costs is not None else Costs()
        with self.costs.measure('construct_space_time_constraints'):
            self.source_phases = {r: phase_segments(t) for r, t in problem['trajectories'].items()}
            self.certificates = certificate_factory(problem)
        self.bindings = {r: Binding(problem['task'], r, r+'_TASK', CONDITION, problem['commitment'])
                         for r in problem['trajectories']}
        self.inboxes = {r: TaskInbox(self.bindings[r], t.chain.duration) for r, t in problem['trajectories'].items()}
        self.events = AuthorTaskEvents(self.bindings, author) if engine == 'SADG_events' else None
        self.latest, self.started, self.completion = {}, {}, dict.fromkeys(self.bindings)
        self.packets, self.decisions, self.commands = [], [], []
        self.causal_clock = CausalClock()

    def receive(self, packet, *, now):
        with self.costs.measure('global_causality'):
            stamp = self.causal_clock.validate(now)
            super().receive(packet, now=stamp)
            self.causal_clock.commit(stamp)  # rejected messages cannot poison the clock

    def authorize(self, robot, *, now, deadline=None):
        with self.costs.measure('global_causality'):
            stamp = self.causal_clock.validate(now, deliveries=(p.delivery for p in self.latest.values()))
            result = super().authorize(robot, now=stamp, deadline=deadline)
            self.causal_clock.commit(stamp)
            return result

    def remaining_modes(self, now):
        self.causal_clock.validate(now, deliveries=(p.delivery for p in self.latest.values()))
        anchors = self.anchors(now)
        return {r: physical_windows(self.problem['trajectories'][r], a, now) for r, a in anchors.items()}
