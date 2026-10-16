"""Complete public task session with shared physical-time checks and author API.

This project adapter grants an immutable stopped-primitive batch. A future time
reservation is a logical certificate, never a fake physical COMPLETED status.
SADG optimizer/ROS semantics and original proofs are not inherited.
"""
from fractions import Fraction as Q
from copy import deepcopy

from composition import CONDITION
from timed import Anchor
from timed_constraints import Certificates
from timed_protocol import Binding, Costs, TaskPacket, TaskInbox, task_receipt


class AuthorTaskEvents:
    """AGPL-3.0-or-later common-problem adaptation of verified author classes."""
    def __init__(self, robots, author):
        self.Status = author['sadg.status'].Status
        Vertex, PlanTuple = author['sadg.vertex'].Vertex, author['mapf.plan_tuple'].PlanTuple
        Dependency = author['sadg.dependency'].Dependency
        self.motion, self.certificate = {}, {}
        for robot in robots:
            event = Vertex(robot+'_reservation', PlanTuple(0, 0, 0), 0)
            motion = Vertex(robot+'_task', [PlanTuple(0, 0, 0), PlanTuple(1, 0, 0)], 0)
            motion.add_dependency(Dependency(event, motion))
            self.motion[robot], self.certificate[robot] = motion, event

    def reserve(self, robot):
        self.certificate[robot].set_status(self.Status.COMPLETED)
        return self.motion[robot].can_execute()

    def feedback(self, robot, state):
        if state in ('RUNNING', 'DONE'):
            self.motion[robot].set_status(self.Status.COMPLETED if state == 'DONE' else self.Status.IN_PROGRESS)


class TaskSession:
    def __init__(self, problem, author, *, engine, costs=None):
        if engine not in ('guard', 'SADG_events'):
            raise ValueError('unregistered engine')
        self.problem, self.engine = deepcopy(problem), engine
        self._qualified_problem = deepcopy(problem)
        problem = self.problem
        self.costs = costs if costs is not None else Costs()
        with self.costs.measure('construct_space_time_constraints'):
            self.certificates = Certificates(problem)
        self.bindings = {r: Binding(problem['task'], r, r+'_TASK', CONDITION, problem['commitment'])
                         for r in problem['trajectories']}
        self.inboxes = {r: TaskInbox(self.bindings[r], tr.chain.duration) for r, tr in problem['trajectories'].items()}
        self.events = AuthorTaskEvents(self.bindings, author) if engine == 'SADG_events' else None
        self.latest, self.started, self.completion = {}, {}, dict.fromkeys(self.bindings)
        self.packets, self.decisions, self.commands = [], [], []

    def receive(self, packet, *, now):
        with self.costs.measure('feedback_validation_and_accounting'):
            self.check_commitment()
            if type(packet) is not TaskPacket:
                raise ValueError('typed public packet required')
            robot = packet.binding.robot
            if robot not in self.inboxes:
                raise ValueError('foreign robot')
            inbox = self.inboxes[robot]
            inbox.validate(packet, now=now)
            if packet.state != 'STOPPED' and (robot not in self.started or Q(packet.capture) < self.started[robot]):
                raise ValueError('motion/END before a granted command')
            if packet.state == 'STOPPED' and robot in self.started and Q(packet.capture) >= self.started[robot]:
                raise ValueError('committed controller unexpectedly stopped')
            tr = self.problem['trajectories'][robot]
            if robot in self.started and packet.state != 'STOPPED':
                # Consistency check only: commanded time NEVER substitutes for
                # a delivered actual-input ACK or a delivered completion event.
                expected = min(tr.chain.duration, Q(packet.capture)-self.started[robot])
                if not Q(packet.phase_lo) <= expected <= Q(packet.phase_hi):
                    raise ValueError('actual feedback violates committed zero-jitter input clock')
                if packet.kind == 'END' and Q(packet.completion_time) != self.started[robot]+tr.chain.duration:
                    raise ValueError('premature/shifted END violates committed braking duration')
            b = tr.box(Q(packet.phase_lo), Q(packet.phase_hi), body=False)
            x, y, loc = Q(packet.observed_x), Q(packet.observed_y), Q(packet.localization_bound)
            if not (b[0]-loc <= x <= b[1]+loc and b[2]-loc <= y <= b[3]+loc):
                raise ValueError('observation outside declared source and phase family')
            inbox.admit(packet, now=now)
            self.latest[robot] = packet
            self.packets.append(packet)
            if self.events:
                self.events.feedback(robot, packet.state)
            if packet.kind == 'END':
                self.completion[robot] = packet.completion_time

    def anchors(self, now):
        if set(self.latest) != set(self.bindings):
            raise ValueError('MISSING_PUBLIC_FEEDBACK')
        anchors = {}
        for robot, p in self.latest.items():
            # A delivered END supports the permanent goal forever under v2.
            if p.state != 'DONE' and Q(now)-Q(p.capture) > Q(self.problem['config']['feedback_ttl']):
                raise ValueError('STALE_FEEDBACK_NO_NEW_DISPATCH')
            if robot in self.started and p.state == 'STOPPED':
                raise ValueError('WAITING_FOR_ACTUAL_INPUT_ACK')
            anchors[robot] = Anchor(Q(p.capture), Q(p.phase_lo), Q(p.phase_hi), p.state == 'RUNNING',
                                     self.problem['trajectories'][robot].chain.duration)
        return anchors

    def authorize(self, robot, *, now, deadline=None):
        with self.costs.measure('update_and_release'):
            self.check_commitment()
            try:
                anchors = self.anchors(now)
            except ValueError as e:
                result = {'accepted': False, 'reason': str(e)}
            else:
                result = self.certificates.launch(robot, anchors, self.started, now=now, deadline=deadline)
            if result['accepted']:
                if result['commitment'] != self.problem['commitment']:
                    raise ValueError('reservation scope changed')
                if self.events and not self.events.reserve(robot):
                    raise ValueError('author dependency rejected valid reservation')
                self.started[robot] = Q(now)
                command = {'task': self.problem['task'], 'robot': robot, 'start': str(Q(now)),
                           'commitment': self.problem['commitment'], 'controller_policy': self.problem['config']['controller_commitment']}
                self.commands.append(command)
            self.decisions.append({'robot': robot, 'now': str(Q(now)), **result})
            return result

    def check_commitment(self):
        if self.problem != self._qualified_problem:
            raise ValueError('qualified trajectory/controller/geometry changed; new reservation required')

    def request_change(self, robot, *, action):
        # Includes braking: the fixed profile already brakes to zero at every
        # boundary. A new brake/pause/speed request needs a new joint reservation,
        # which is intentionally not implemented in this first finite contract.
        if robot in self.started and self.completion[robot] is None:
            raise ValueError('OUTSTANDING_RESERVATION: cannot '+action)
        raise ValueError('new controller contract required; no silent schedule mutation')

    def receipt(self, *, status=None):
        result = task_receipt(self.packets, task=self.problem['task'], robots=tuple(self.bindings),
                              engine=self.engine, completion=self.completion, costs=self.costs.finish(),
                              horizon=self.problem['config']['horizon'], status=status)
        return {**result, 'operations': dict(self.certificates.operations),
                'decisions': self.decisions, 'commands': self.commands,
                'constraint_count': len(self.certificates.constraints),
                'initial_wait': {r: str(t) for r, t in self.started.items()},
                'unresolved_is_collision': False,
                'coverage_basis': 'declared v2 shared-parameter family and continuous interval certificates'}
