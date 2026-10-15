"""Public observation transport for the S1 declared simulation contract.

No private-state input, nominal ETA release, sockets, query policy, or I/O.
Producer identity is an in-process binding, not network authentication.
"""
from dataclasses import asdict, dataclass
from fractions import Fraction as Q
import json


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
        self.seq, self.last_capture = 0, Q(-1)

    def capture(self, observation, *, now):
        if set(observation) != {'task', 'robot', 'action', 'condition', 'capture', 'observed_x', 'observed_y'}:
            raise ValueError('public observation schema only')
        if any(observation[k] != getattr(self.binding, k) for k in ('task', 'robot', 'action', 'condition')):
            raise ValueError('source binding mismatch')
        t = exact(observation['capture'])
        if not self.last_capture < t <= exact(now) or t < 0:
            raise ValueError('future or nonmonotone capture')
        exact(observation['observed_x']); exact(observation['observed_y'])
        result = Packet(self.binding, self.seq, str(t), str(t+self.delay),
                        observation['observed_x'], observation['observed_y'])
        self.seq += 1
        self.last_capture = t
        return result


class Inbox:
    """One receiver per arm; exactly the same packet bytes go to every arm."""
    def __init__(self, binding):
        self.binding, self.last_seq, self.last_capture = binding, -1, Q(-1)
        self.received_bytes = self.received_count = 0

    def admit(self, packet, *, now):
        if not isinstance(packet, Packet) or packet.binding != self.binding:
            raise ValueError('wrong public producer/binding')
        if packet.kind != 'PROGRESS_BOUND' or type(packet.seq) is not int or packet.seq <= self.last_seq:
            raise ValueError('wrong kind or replay/out-of-order sequence')
        t, delivery = exact(packet.capture), exact(packet.delivery)
        if not 0 <= t <= delivery <= exact(now) or t <= self.last_capture:
            raise ValueError('undelivered or stale observation')
        if packet.localization_bound != '.01' or packet.tracking_bound != '.03':
            raise ValueError('unqualified smaller/different bounds')
        exact(packet.observed_x); exact(packet.observed_y)
        self.last_seq, self.last_capture = packet.seq, t
        self.received_count += 1
        self.received_bytes += len(packet.wire())
        return {'task': packet.binding.task, 'condition': packet.binding.condition,
                'seq': packet.seq, 'capture': packet.capture, 'delivery': packet.delivery,
                'observed_x': packet.observed_x, 'localization_bound': packet.localization_bound,
                'tracking_bound': packet.tracking_bound, 'kind': packet.kind}
