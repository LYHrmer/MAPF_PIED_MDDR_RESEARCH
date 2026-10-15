"""Exploratory continuous-occupancy / release interface, not an author solver.

Exact rational certificates for axis-aligned straight primitives and a
conservative full-rotation bound. Overlap means potential conflict, not a
collision proof. No simulator, training, solver invocation or I/O on import.
"""
from dataclasses import dataclass
from fractions import Fraction as Q


def q(value):
    if isinstance(value, float) or isinstance(value, bool):
        raise ValueError('use exact decimal text or integers')
    return Q(value)


@dataclass(frozen=True)
class Box:
    xmin: Q
    xmax: Q
    ymin: Q
    ymax: Q

    def __post_init__(self):
        if self.xmin > self.xmax or self.ymin > self.ymax:
            raise ValueError('inverted box')

    def separated(self, other):
        # Closed occupancies: touching is not accepted.
        return (self.xmax < other.xmin or other.xmax < self.xmin
                or self.ymax < other.ymin or other.ymax < self.ymin)


def sweep(start, end, half):
    """Continuous segment + rectangle. Axis aligned only; includes endpoints."""
    x0, y0 = map(q, start)
    x1, y1 = map(q, end)
    hx, hy = map(q, half)
    if hx < 0 or hy < 0 or (x0 != x1 and y0 != y1):
        raise ValueError('unsupported motion or negative extent')
    return Box(min(x0, x1)-hx, max(x0, x1)+hx,
               min(y0, y1)-hy, max(y0, y1)+hy)


def turn_sweep(center, body_radius, position_radius, half_length, half_width):
    """Contains every intermediate body heading, not just turn endpoints."""
    r, e, a, b = map(q, (body_radius, position_radius, half_length, half_width))
    if min(r, e, a, b) < 0 or r*r < a*a+b*b:
        raise ValueError('invalid full-rotation outer bound')
    return sweep(center, center, (r+e, r+e))


def conflicts(occupancies):
    """All cross-robot primitive sweeps, including WAIT and GOAL_HOLD."""
    found = []
    for i, (name, robot, box) in enumerate(occupancies):
        for name2, robot2, box2 in occupancies[i+1:]:
            if robot != robot2 and not box.separated(box2):
                found.append((name, name2))
    return found


def dag(nodes, edges):
    remaining = set(nodes)
    if any(a not in remaining or b not in remaining for a, b in edges):
        raise ValueError('edge endpoint not declared')
    order = []
    while remaining:
        ready = sorted(n for n in remaining
                       if not any(b == n and a in remaining for a, b in edges))
        if not ready:
            return {'feasible': False, 'reason': 'CURRENT_ARRANGEMENT_CYCLE',
                    'remaining': sorted(remaining)}
        order.extend(ready)
        remaining.difference_update(ready)
    return {'feasible': True, 'order': order}


def add_conflicts(nodes, existing, new_pairs, ranks):
    """Preserve existing reachability; otherwise frozen rank, then cycle check."""
    edges = list(existing)

    def reaches(a, b):
        seen, todo = set(), [a]
        while todo:
            n = todo.pop()
            if n == b:
                return True
            if n not in seen:
                seen.add(n)
                todo.extend(v for u, v in edges if u == n)
        return False

    # Determine every orientation from the ORIGINAL relations, not insertion order.
    additions = []
    for a, b in sorted(new_pairs):
        if reaches(a, b):
            edge = (a, b)
        elif reaches(b, a):
            edge = (b, a)
        else:
            if ranks[a] == ranks[b]:
                raise ValueError('priority ranks must be total')
            edge = (a, b) if ranks[a] < ranks[b] else (b, a)
        additions.append(edge)
    edges.extend(e for e in additions if e not in edges)
    return {'edges': edges, 'new_or_retained': additions, **dag(nodes, edges)}


def temporal_feasible(nodes, lower_constraints):
    """Difference constraints t[v] >= t[u]+lag; positive cycle is infeasible.

    Deadlines/equalities use reverse edges to the common clock-origin node.
    This is a feasibility check, not a performance optimizer.
    """
    d = dict.fromkeys(nodes, Q(0))
    for iteration in range(len(d)):
        changed = False
        for u, v, lag in lower_constraints:
            if u not in d or v not in d:
                raise ValueError('undeclared time node')
            candidate = d[u]+q(lag)
            if d[v] < candidate:
                d[v], changed = candidate, True
        if not changed:
            return True
    return False


def release(packet, *, now, task, condition, half_a, occupied_b, suffix, end):
    """Consume a delivered observation and a bound, never private truth or ETA.

    suffix is the COMPLETE allowed eastward reference suffix, including its
    permanent terminal hold. Full-suffix separation tolerates arbitrary B
    delays. Caller must enforce the same suffix commitment after dispatch.
    This checker does not authenticate transport or implement robot control.
    """
    fields = {'task', 'condition', 'seq', 'capture', 'delivery', 'observed_x',
              'localization_bound', 'tracking_bound', 'kind'}
    if set(packet) != fields or packet['kind'] != 'PROGRESS_BOUND':
        return {'accepted': False, 'reason': 'WRONG_MESSAGE_SCHEMA'}
    if packet['task'] != task or packet['condition'] != condition or packet['seq'] < 0:
        return {'accepted': False, 'reason': 'BINDING_MISMATCH'}
    capture, delivery, current = map(q, (packet['capture'], packet['delivery'], now))
    if capture < 0 or not capture <= delivery <= current:
        return {'accepted': False, 'reason': 'NOT_LEGALLY_DELIVERED'}
    loc, track = map(q, (packet['localization_bound'], packet['tracking_bound']))
    # Fixed source contract, not caller-selected smaller bounds.
    if loc != q('.01') or track != q('.03'):
        return {'accepted': False, 'reason': 'BOUND_CONDITION_MISMATCH'}
    lower = q(packet['observed_x'])-loc-track
    if not suffix or tuple(map(q, suffix[0][0])) != (lower, Q(0)):
        return {'accepted': False, 'reason': 'SUFFIX_NOT_BOUND_TO_PROGRESS'}
    previous = (lower, Q(0))
    for a, b in suffix:
        a, b = tuple(map(q, a)), tuple(map(q, b))
        if a != previous or a[1] != 0 or b[1] != 0 or b[0] < a[0]:
            return {'accepted': False, 'reason': 'REENTRY_OR_UNSUPPORTED_SUFFIX'}
        if not sweep(a, b, half_a).separated(occupied_b):
            return {'accepted': False, 'reason': 'FUTURE_OCCUPANCY_OVERLAP'}
        previous = b
    if previous != tuple(map(q, end)) or suffix[-1][0] != suffix[-1][1]:
        return {'accepted': False, 'reason': 'MISSING_PERMANENT_GOAL_HOLD'}
    return {'accepted': True, 'progress_lower': str(lower),
            'coverage': 'ALL_ALLOWED_SUFFIX_AND_PERMANENT_HOLD'}


def trapezoid_duration(length, speed, acceleration):
    length, speed, acceleration = map(q, (length, speed, acceleration))
    if min(length, speed, acceleration) <= 0 or length < speed*speed/acceleration:
        raise ValueError('only nondegenerate trapezoid supported')
    return length/speed+speed/acceleration


def cruise_arrival(distance, length, speed, acceleration):
    """Analytic feasible schedule only. NEVER used by release()."""
    d, length, v, a = map(q, (distance, length, speed, acceleration))
    ramp_distance = v*v/(2*a)
    if not ramp_distance <= d <= length-ramp_distance:
        raise ValueError('event outside cruise segment')
    return v/a+(d-ramp_distance)/v
