"""Task-level v2 phase feedback. Reuses Binding, Costs and failure accounting.

Phase bounds are NEW local actual-input-clock feedback, explicitly costed and
given to both arms. They are not the central planned clock or private pose truth.
The trusted in-process source is not cryptographic sensor authentication.
"""
from dataclasses import asdict, dataclass
from fractions import Fraction as Q
import hashlib
import json

from protocol import Binding, Costs, exact, completion_summary

PROTOCOL = 'task_phase_interval_observation_END_v1'
CLOCK = 'v2_actual_input_shared_clock_nonpreemptive_v1'
FIELDS = {'capture', 'phase_lo', 'phase_hi', 'state', 'observed_x', 'observed_y', 'clock', 'completion_time'}


@dataclass(frozen=True)
class TaskPacket:
    binding: Binding
    seq: int
    capture: str
    delivery: str
    phase_lo: str
    phase_hi: str
    state: str
    observed_x: str
    observed_y: str
    completion_time: object = None
    kind: str = 'STATE'
    clock: str = CLOCK
    protocol: str = PROTOCOL
    localization_bound: str = '.01'

    def wire(self):
        return json.dumps(asdict(self), sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


class TaskProducer:
    def __init__(self, binding, *, delay='.1'):
        self.binding, self.delay = binding, exact(delay)
        if self.delay < 0:
            raise ValueError('negative transport delay')
        self.seq, self.last, self.ended = 0, Q(-1), False

    def capture(self, observation, *, now):
        if self.ended or set(observation) != FIELDS:
            raise ValueError('public schema only, no captures after END')
        t = exact(observation['capture'])
        if not self.last < t <= exact(now) or t < 0:
            raise ValueError('future/nonmonotone capture')
        packet = TaskPacket(self.binding, self.seq, str(t), str(t+self.delay),
                            observation['phase_lo'], observation['phase_hi'], observation['state'],
                            observation['observed_x'], observation['observed_y'],
                            completion_time=observation['completion_time'],
                            kind='END' if observation['state'] == 'DONE' else 'STATE', clock=observation['clock'])
        self.seq, self.last, self.ended = self.seq+1, t, packet.kind == 'END'
        return packet


class TaskInbox:
    def __init__(self, binding, duration):
        self.binding, self.duration = binding, exact(duration)
        self.last_seq, self.last_capture, self.last_now, self.ended = -1, Q(-1), Q(-1), False
        self.received_count, self.received_bytes = 0, 0
        self.previous = None

    def validate(self, p, *, now):
        if type(p) is not TaskPacket or p.binding != self.binding or self.ended:
            raise ValueError('foreign binding or post-END message')
        if p.protocol != PROTOCOL or p.clock != CLOCK or p.localization_bound != '.01':
            raise ValueError('unqualified clock/protocol/localization condition')
        if type(p.seq) is not int or p.seq <= self.last_seq:
            raise ValueError('replay/out-of-order packet')
        t, d, now = exact(p.capture), exact(p.delivery), exact(now)
        if not 0 <= t <= d <= now or t <= self.last_capture or now < self.last_now:
            raise ValueError('undelivered/stale capture or reversed receive clock')
        lo, hi = exact(p.phase_lo), exact(p.phase_hi)
        if not 0 <= lo <= hi <= self.duration or hi-lo > Q('.01'):
            raise ValueError('invalid local phase bound')
        if p.state == 'STOPPED':
            if (lo, hi, p.kind) != (0, 0, 'STATE'):
                raise ValueError('this protocol supports initial wait only')
        elif p.state == 'RUNNING':
            if p.kind != 'STATE':
                raise ValueError('moving END')
        elif p.state == 'DONE':
            if (lo, hi, p.kind) != (self.duration, self.duration, 'END'):
                raise ValueError('END must be a local completed chain event')
            if p.completion_time is None or not 0 <= exact(p.completion_time) <= t:
                raise ValueError('local physical completion time required')
        else:
            raise ValueError('unknown state')
        if p.state != 'DONE' and p.completion_time is not None:
            raise ValueError('completion attached to unfinished motion')
        exact(p.observed_x); exact(p.observed_y)
        if self.previous is not None and self.previous.state == 'RUNNING':
            elapsed = t-exact(self.previous.capture)
            prior_lo = min(self.duration, exact(self.previous.phase_lo)+elapsed)
            prior_hi = min(self.duration, exact(self.previous.phase_hi)+elapsed)
            if p.state == 'STOPPED' or hi < prior_lo or lo > prior_hi:
                raise ValueError('actual-input clock changed without a new commitment')
            if p.state == 'DONE' and not (exact(self.previous.capture)+self.duration-exact(self.previous.phase_hi)
                                          <= exact(p.completion_time)
                                          <= exact(self.previous.capture)+self.duration-exact(self.previous.phase_lo)):
                raise ValueError('completion conflicts with delivered actual clock')
        return p

    def admit(self, p, *, now):
        self.validate(p, now=now)
        self.last_seq, self.last_capture, self.last_now = p.seq, exact(p.capture), exact(now)
        self.ended, self.previous = p.kind == 'END', p
        self.received_count += 1
        self.received_bytes += len(p.wire())


def task_receipt(packets, *, task, robots, engine, completion, costs, horizon='40', status=None):
    if set(completion) != set(robots):
        raise ValueError('missing robot outcome')
    ends = {r: [] for r in robots}
    for p in packets:
        if p.binding.task != task or p.binding.robot not in ends:
            raise ValueError('foreign packet in receipt')
        if p.kind == 'END':
            ends[p.binding.robot].append(p.completion_time)
    for r in robots:
        if ends[r] != ([] if completion[r] is None else [completion[r]]):
            raise ValueError('completion must come from one delivered local END')
    complete = all(completion[r] is not None and len(ends[r]) == 1 for r in robots)
    if status is None:
        status = 'SUCCESS' if complete else 'INCOMPLETE'
    if status == 'SUCCESS' and not complete:
        raise ValueError('cannot hide incomplete task as success')
    if (costs['aggregation'] != 'OUTER_ENVELOPE_ONLY_DO_NOT_SUM_NESTED'
            or any(costs[k] < 0 for k in ('wall_ns', 'cpu_ns'))
            or any(s[k] > costs[k] for s in costs['segments'] for k in ('wall_ns', 'cpu_ns'))):
        raise ValueError('invalid cost envelope')
    result = completion_summary([{'task': task, 'arm': engine, 'status': status, 'completion': completion}],
                                robots=tuple(robots), horizon=horizon)[0]
    return {**result, 'messages': len(packets), 'bytes': sum(len(p.wire()) for p in packets),
            'public_wire_sha256': hashlib.sha256(b'\n'.join(p.wire() for p in packets)).hexdigest(),
            'costs': costs, 'safety_inferred_from_END': False,
            'total_process_cost': 'external runner receipt includes imports, final serialization and I/O; pending until executed'}
