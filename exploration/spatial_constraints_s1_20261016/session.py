"""Public-input fixed-order session, integrating S1 guard and source contract.

Exploratory adaptation. No truth input, plant stepping, optimizer, or training.
"""
from copy import deepcopy
import hashlib
import json

from author_events import FixedOrderEvents
from interface import Box, q, release, sweep


class Session:
    def __init__(self, fixture, source, feedback, author, *, geometry, engine):
        if geometry not in ('directional', 'circle') or engine not in ('guard', 'SADG_events', 'endpoint'):
            raise ValueError('unsupported geometry/engine')
        self.fixture = deepcopy(fixture)
        self.contract = source.admit_fixture(self.fixture)
        self.geometry, self.engine, self.feedback = geometry, engine, feedback
        a, b = map(q, self.contract['body_half'])
        ex, ey = map(q, self.contract['tracking_half'])
        psi = q(self.contract['heading_bound'])
        bound = source.bounds()
        if bound['parallel'] > ex or bound['cross'] > ey:
            raise ValueError('source window does not fit occupancy')
        if geometry == 'directional':
            self.half = tuple(map(q, self.fixture['directional_half']))
            if self.half[0] < a+b*psi+ex or self.half[1] < b+a*psi+ey:
                raise ValueError('directional footprint omits permitted body/error')
        else:
            r = q(self.fixture['circle_radius'])
            # Explicit circle bounds on body and position residual.
            if r < q('.32')+q('.04') or q('.32')**2 < a*a+b*b or q('.04')**2 < ex*ex+ey*ey:
                raise ValueError('circle omits permitted body/error')
            self.half = (r, r)
        self.b_box = sweep((0, -1), (0, 1), self.half[::-1])
        if not sweep((-1, 0), (2, 0), self.half).separated(sweep((0, -1), (0, -1), self.half[::-1])):
            raise ValueError('unsafe complete initial wait')
        if not sweep((2, 0), (2, 0), self.half).separated(self.b_box):
            raise ValueError('unsafe permanent goal occupancy')
        world = Box(q('-1.5'), q('2.5'), q('-1.5'), q('1.5'))
        for box in (sweep((-1, 0), (2, 0), self.half), self.b_box):
            if not (world.xmin < box.xmin <= box.xmax < world.xmax
                    and world.ymin < box.ymin <= box.ymax < world.ymax):
                raise ValueError('full motion occupancy reaches wall')
        self.bindings = {r: feedback.Binding(self.fixture['id'], r, r+'_move', self.fixture['condition'],
                                            self.contract['suffix_commitment'] if r == 'A' else 'B_north_to_1_permanent_hold_v1')
                         for r in ('A', 'B')}
        self.inboxes = {r: feedback.Inbox(binding) for r,binding in self.bindings.items()}
        self.graph = FixedOrderEvents(author) if engine == 'SADG_events' else None
        self.started_at, self.ended, self.packets, self.last_time = None, set(), [], q(-1)
        self.contract_sha256 = self.digest()

    def digest(self):
        return hashlib.sha256(json.dumps({'fixture': self.fixture, 'contract': self.contract}, sort_keys=True).encode()).hexdigest()

    def receive(self, packet, *, now):
        # A post-release contract change is a fault, never a new legal decision.
        if self.digest() != self.contract_sha256:
            raise ValueError('committed source/path/occupancy contract mutated')
        now = q(now)
        if now < self.last_time:
            raise ValueError('session time reversal')
        robot = packet.binding.robot
        if robot not in self.inboxes or robot in self.ended:
            raise ValueError('foreign robot or message after END')
        if robot == 'B' and (packet.kind != 'END' or self.started_at is None or q(packet.capture) < self.started_at):
            raise ValueError('B cannot report completion before dispatch')
        public = self.inboxes[robot].admit(packet, now=now)
        self.last_time = now
        self.packets.append(packet)
        if packet.kind == 'END':
            self.ended.add(robot)
            if robot == 'A' and self.graph:
                self.graph.a_motion.set_status(self.graph.Status.COMPLETED)
        if robot != 'A' or (self.engine == 'endpoint' and packet.kind != 'END'):
            return self.started_at
        # END is useful only together with its separately bound observation and
        # this full-suffix guard. The event itself is never the spatial evidence.
        observation = {**public, 'kind': 'PROGRESS_BOUND'}
        lower = q(observation['observed_x'])-q('.01')-q('.03')
        if lower > 2:
            raise ValueError('observation inconsistent with committed reference endpoint')
        cert = release(observation, now=now, task=self.fixture['id'], condition=self.fixture['condition'],
                       half_a=self.half, occupied_b=self.b_box,
                       suffix=[((lower, 0), (2, 0)), ((2, 0), (2, 0))], end=(2, 0))
        eligible = self.graph.apply_certificate(cert) if self.graph else cert['accepted']
        if eligible and self.started_at is None:
            self.started_at = now
        return self.started_at
