"""Qualification helpers layered over frozen v2, without new source parameters."""
from fractions import Fraction as Q


def phase_segments(trajectory):
    """Exact finite controller phases plus permanent HOLD, no waypoint reset.

    TURN keeps its complete four-second slot: no rational approximation to pi
    is substituted for its true acceleration/braking switch times.
    """
    result = []
    for index, (action, start) in enumerate(zip(trajectory.chain.primitives, trajectory.offsets)):
        if action.kind == 'HOLD':
            result.append((index, 'PERMANENT_HOLD', start, None))
        elif action.kind == 'MOVE':
            end = start+action.duration
            points = (start, start+Q('.5'), end-Q('.5'), end)
            for mode, lo, hi in zip(('ACCEL', 'CRUISE', 'BRAKE'), points, points[1:]):
                if hi > lo:
                    result.append((index, mode, lo, hi))
        else:
            result.append((index, action.kind, start, start+action.duration))
    finite = [x for x in result if x[3] is not None]
    if (not finite or finite[0][2] != 0 or finite[-1][3] != trajectory.chain.duration
            or any(a[3] != b[2] for a, b in zip(finite, finite[1:]))
            or result[-1][1] != 'PERMANENT_HOLD'):
        raise ValueError('controller phases must cover the complete chain and permanent goal')
    return tuple(result)


def physical_windows(trajectory, anchor, now):
    """Possible physical-time windows implied by delivered phase bounds.

    Windows may overlap because phase is uncertain. They are NOT a new
    collision test, and do not replace the continuous trajectory-family box.
    """
    now = Q(now)
    anchor.phases(now, now)  # reject retrospective use
    if not anchor.moving:
        return ({'mode': 'CONFIRMED_STATIONARY', 'start': now, 'end': None,
                 'phase': (anchor.low, anchor.high)},)
    result = []
    for index, mode, lo, hi in phase_segments(trajectory):
        end = None if hi is None else anchor.capture+hi-anchor.low
        if end is not None and end < now:
            continue
        result.append({'action': index, 'mode': mode,
                       'start': max(now, anchor.capture+lo-anchor.high), 'end': end})
    return tuple(result)
