"""Public observation transport for the S1 declared simulation contract.

No private-state input, nominal ETA release, sockets, query policy, or I/O.
Producer identity is an in-process binding, not network authentication.
"""
from dataclasses import asdict, dataclass
from fractions import Fraction as Q
import json
from contextlib import contextmanager
import hashlib
import time


def exact(value):
    if isinstance(value, (bool, float)):
        raise ValueError('exact rational text required')
    return Q(value)


@dataclass(frozen=True)
class Binding:
    task: str
    robot: str
    action: str
    condition: str
    commitment: str


@dataclass(frozen=True)
class Packet:
    binding: Binding
    seq: int
    capture: str
    delivery: str
    observed_x: str
    observed_y: str
    localization_bound: str = '.01'
    tracking_bound: str = '.03'
    kind: str = 'PROGRESS_BOUND'

    def wire(self):
        return json.dumps(asdict(self), sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


class Producer:
    def __init__(self, binding, delay='.1'):
        self.binding, self.delay = binding, exact(delay)
        if self.delay < 0:
            raise ValueError('negative delay')
        self.seq, self.last_capture, self.ended = 0, Q(-1), False

    def capture(self, observation, *, now, kind='PROGRESS_BOUND'):
        if self.ended or kind not in ('PROGRESS_BOUND', 'END'):
            raise ValueError('unsupported event or already ended action')
        if set(observation) != {'task', 'robot', 'action', 'condition', 'capture', 'observed_x', 'observed_y'}:
            raise ValueError('public observation schema only')
        if any(observation[k] != getattr(self.binding, k) for k in ('task', 'robot', 'action', 'condition')):
            raise ValueError('source binding mismatch')
        t = exact(observation['capture'])
        if not self.last_capture < t <= exact(now) or t < 0:
            raise ValueError('future or nonmonotone capture')
        exact(observation['observed_x']); exact(observation['observed_y'])
        result = Packet(self.binding, self.seq, str(t), str(t+self.delay),
                        observation['observed_x'], observation['observed_y'], kind=kind)
        self.seq += 1
        self.last_capture = t
        self.ended = kind == 'END'
        return result


class Inbox:
    """One receiver per arm; exactly the same packet bytes go to every arm."""
    def __init__(self, binding):
        self.binding, self.last_seq, self.last_capture = binding, -1, Q(-1)
        self.last_now = Q(-1)
        self.received_bytes = self.received_count = 0

    def admit(self, packet, *, now):
        if not isinstance(packet, Packet) or packet.binding != self.binding:
            raise ValueError('wrong public producer/binding')
        if packet.kind not in ('PROGRESS_BOUND', 'END') or type(packet.seq) is not int or packet.seq <= self.last_seq:
            raise ValueError('wrong kind or replay/out-of-order sequence')
        t, delivery = exact(packet.capture), exact(packet.delivery)
        if not 0 <= t <= delivery <= exact(now) or t <= self.last_capture or exact(now) < self.last_now:
            raise ValueError('undelivered or stale observation')
        if packet.localization_bound != '.01' or packet.tracking_bound != '.03':
            raise ValueError('unqualified smaller/different bounds')
        exact(packet.observed_x); exact(packet.observed_y)
        self.last_seq, self.last_capture = packet.seq, t
        self.last_now = exact(now)
        self.received_count += 1
        self.received_bytes += len(packet.wire())
        return {'task': packet.binding.task, 'condition': packet.binding.condition,
                'seq': packet.seq, 'capture': packet.capture, 'delivery': packet.delivery,
                'observed_x': packet.observed_x, 'localization_bound': packet.localization_bound,
                'tracking_bound': packet.tracking_bound, 'kind': packet.kind}


class Broadcast:
    def __init__(self):
        self.pending, self.now = [], Q(-1)

    def send(self, packet, *, now):
        if not exact(packet.capture) <= exact(now) <= exact(packet.delivery):
            raise ValueError('cannot enqueue before capture or after delivery')
        self.pending.append(packet)

    def deliver(self, now):
        now = exact(now)
        if now < self.now:
            raise ValueError('transport clock moved backwards')
        ready = sorted((p for p in self.pending if exact(p.delivery) <= now),
                       key=lambda p: (exact(p.delivery), p.binding.robot, p.seq))
        self.pending = [p for p in self.pending if exact(p.delivery) > now]
        self.now = now
        return tuple(ready)


def paired_identity(records):
    """Different arms may have different causal END times, never hidden inputs."""
    fields = {'task', 'source_sha256', 'paths_sha256', 'order_sha256', 'controller',
              'protocol', 'initial_state_sha256', 'A_progress_wire_sha256', 'units', 'safety_set'}
    if not records or any(set(row) != fields for row in records):
        raise ValueError('incomplete paired identity')
    if any(row != records[0] for row in records[1:]):
        raise ValueError('paired inputs or public information differ')
    return hashlib.sha256(json.dumps(records[0], sort_keys=True).encode()).hexdigest()


class Costs:
    """Nested segments are diagnostic; the outer envelope is the total."""
    def __init__(self):
        self.wall_start, self.cpu_start = time.perf_counter_ns(), time.process_time_ns()
        self.segments, self.depth = [], 0

    @contextmanager
    def measure(self, name):
        wall, cpu, depth = time.perf_counter_ns(), time.process_time_ns(), self.depth
        self.depth += 1
        try:
            yield
        finally:
            self.depth -= 1
            self.segments.append({'name': name, 'depth': depth,
                                  'wall_ns': time.perf_counter_ns()-wall,
                                  'cpu_ns': time.process_time_ns()-cpu})

    def finish(self):
        if self.depth:
            raise ValueError('cost segment still active')
        return {'wall_ns': time.perf_counter_ns()-self.wall_start,
                'cpu_ns': time.process_time_ns()-self.cpu_start,
                'segments': list(self.segments), 'aggregation': 'OUTER_ENVELOPE_ONLY_DO_NOT_SUM_NESTED'}


def completion_summary(rows, *, robots=('A', 'B'), horizon='20'):
    """All task records retained. Incomplete agents contribute the fixed horizon."""
    horizon = exact(horizon)
    if horizon <= 0 or not rows:
        raise ValueError('positive preregistered horizon and nonempty records required')
    results = []
    for row in rows:
        if set(row) != {'task', 'arm', 'status', 'completion'} or set(row['completion']) != set(robots):
            raise ValueError('missing task/agent record; do not silently omit failure')
        times = [None if row['completion'][r] is None else exact(row['completion'][r]) for r in robots]
        if any(t is not None and not 0 <= t <= horizon for t in times):
            raise ValueError('completion outside declared horizon')
        complete = row['status'] == 'SUCCESS' and all(t is not None for t in times)
        charged = [horizon if t is None else t for t in times]
        results.append({**row, 'success': complete, 'censored_sum_completion': str(sum(charged)),
                        'censored_makespan': str(max(charged)), 'failure_retained': not complete})
    return results


def public_receipt(packets, costs, *, task):
    """Complete S1 receive ledger; no evaluation truth or task-success inference."""
    counts = {(r, k): 0 for r in ('A', 'B') for k in ('PROGRESS_BOUND', 'END')}
    last = {}
    wire_bytes = 0
    for p in packets:
        if p.binding.task != task or (p.binding.robot, p.kind) not in counts:
            raise ValueError('receipt has foreign task/robot/event')
        key = p.binding.robot
        if type(p.seq) is not int or p.seq <= last.get(key, -1) or not 0 <= exact(p.capture) <= exact(p.delivery):
            raise ValueError('receipt has replay, bad sequence or clock')
        last[key] = p.seq
        counts[(key, p.kind)] += 1
        wire_bytes += len(p.wire())
    if counts != {('A', 'PROGRESS_BOUND'): 2, ('A', 'END'): 1, ('B', 'PROGRESS_BOUND'): 0, ('B', 'END'): 1}:
        raise ValueError('incomplete or expanded S1 message contract')
    if (set(costs) != {'wall_ns', 'cpu_ns', 'segments', 'aggregation'}
            or costs['aggregation'] != 'OUTER_ENVELOPE_ONLY_DO_NOT_SUM_NESTED'
            or any(type(costs[k]) is not int or costs[k] < 0 for k in ('wall_ns', 'cpu_ns'))):
        raise ValueError('incomplete cost envelope')
    if not isinstance(costs['segments'], list):
        raise ValueError('missing diagnostic cost segments')
    for segment in costs['segments']:
        if (set(segment) != {'name', 'depth', 'wall_ns', 'cpu_ns'}
                or any(type(segment[k]) is not int or segment[k] < 0 for k in ('depth', 'wall_ns', 'cpu_ns'))
                or any(segment[k] > costs[k] for k in ('wall_ns', 'cpu_ns'))):
            raise ValueError('cost segment outside outer envelope')
    progress = b'\n'.join(p.wire() for p in packets if p.kind == 'PROGRESS_BOUND')
    return {'task': task, 'messages': len(packets), 'wire_bytes': wire_bytes,
            'A_progress_wire_sha256': hashlib.sha256(progress).hexdigest(),
            'all_public_wire_sha256': hashlib.sha256(b'\n'.join(p.wire() for p in packets)).hexdigest(),
            'END_semantics': 'local_controller_event_not_zero_tracking_error',
            'costs': costs, 'success_or_safety_inferred_from_messages': False}
