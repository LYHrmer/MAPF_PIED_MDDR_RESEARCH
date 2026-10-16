"""Physical-time extension of frozen v2; public tubes never consume true state.

For ONE task parameter z=(b,delta) and body point u, the exact family is
 p0 + b + R(delta) [p_ref(phase(t))-p0 + R(theta_ref(phase(t)))u].
The same delta rotates the displacement and body, at all times/actions.
Rational boxes below are outer projections of this family, not new draws of z.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
import math

from composition import Chain, DIRECTIONS, H, RESERVE, exact

CLOCK_CONTRACT = 'v2_actual_input_shared_clock_nonpreemptive_v1'
PHASE_ERROR = Q('.005')


def hull(boxes):
    if not boxes:
        raise ValueError('empty phase domain')
    return (min(b[0] for b in boxes), max(b[1] for b in boxes),
            min(b[2] for b in boxes), max(b[3] for b in boxes))


def distance(t, length):
    """Exact monotone stopped trapezoid, including the braking interval."""
    end = 2*length+Q('.5')
    t = max(Q(0), min(t, end))
    if t < Q('.5'):
        return t*t/2
    if t <= end-Q('.5'):
        return (t-Q('.25'))/2
    return length-(end-t)**2/2


@dataclass(frozen=True)
class Trajectory:
    robot: str
    chain: Chain

    @property
    def offsets(self):
        offsets, t = [], Q(0)
        for a in self.chain.primitives:
            offsets.append(t)
            if a.duration is not None:
                t += a.duration
        return tuple(offsets)

    def action_box(self, index, phase_lo, phase_hi, *, body=True):
        """Whole continuous phase interval, no sample-based coverage argument."""
        phase_lo, phase_hi = exact(phase_lo), exact(phase_hi)
        if phase_lo > phase_hi:
            raise ValueError('inverted phase interval')
        a, offset = self.chain.primitives[index], self.offsets[index]
        end = offset+a.duration if a.duration is not None else self.chain.duration
        lo, hi = max(offset, phase_lo), min(end, phase_hi)
        if lo > hi:
            return None
        p, q = a.start, a.end
        if a.kind == 'MOVE':
            length = sum(abs(q[j]-p[j]) for j in (0, 1))
            direction = DIRECTIONS[a.heading]
            p, q = (tuple(a.start[j]+direction[j]*distance(t-offset, length) for j in (0, 1))
                    for t in (lo, hi))
        else:
            p = q = a.start
        # Reuse the v2 task-origin domain/condition validation.
        self.chain.error_box(p, q)
        bx, by = (Q('.02'), Q('.01')) if self.chain.heading % 2 == 0 else (Q('.01'), Q('.02'))
        dx = max(abs(x[0]-self.chain.origin[0]) for x in (p, q))
        dy = max(abs(x[1]-self.chain.origin[1]) for x in (p, q))
        if a.kind == 'TURN':
            # Full-circle body outer bound is intentional; orientation-time
            # correlation remains in the family, but is relaxed in this projection.
            hx = hy = Q('.32') if body else Q(0)
            ex, ey = bx+dx*H*H/2+dy*H, by+dx*H+dy*H*H/2
        else:
            hx, hy = (Q('.3'), Q('.1')) if a.heading % 2 == 0 else (Q('.1'), Q('.3'))
            if not body:
                hx = hy = Q(0)
            # Apply the SAME small rotation to d + rotated body point.
            ex = bx+(dx+hx)*H*H/2+(dy+hy)*H
            ey = by+(dx+hx)*H+(dy+hy)*H*H/2
        return (min(p[0], q[0])-hx-ex-RESERVE, max(p[0], q[0])+hx+ex+RESERVE,
                min(p[1], q[1])-hy-ey-RESERVE, max(p[1], q[1])+hy+ey+RESERVE)

    def box(self, phase_lo, phase_hi, *, body=True):
        lo, hi = exact(phase_lo), exact(phase_hi)
        if lo > hi or lo < 0 or hi > self.chain.duration:
            raise ValueError('phase interval outside complete task')
        boxes = [self.action_box(i, lo, hi, body=body) for i in range(len(self.chain.primitives))]
        return hull([b for b in boxes if b is not None])

    def body_point(self, phase, initial, local_point):
        """Evaluation/witness helper only; initial is NEVER a guard input."""
        if len(local_point) != 2 or abs(local_point[0]) > .3 or abs(local_point[1]) > .1:
            raise ValueError('point outside body')
        record = self.chain.sample(float(phase), initial)['evaluation']
        theta = record['pose_true'][2]  # already theta_ref + the shared delta
        c, s = math.cos(theta), math.sin(theta)
        u, v = local_point
        return record['pose_true'][0]+c*u-s*v, record['pose_true'][1]+s*u+c*v


@dataclass(frozen=True)
class Anchor:
    capture: Q
    low: Q
    high: Q
    moving: bool
    duration: Q

    def __post_init__(self):
        if any(not isinstance(x, Q) for x in (self.capture, self.low, self.high, self.duration)):
            raise ValueError('exact physical-time anchor required')
        if not 0 <= self.low <= self.high <= self.duration or self.capture < 0:
            raise ValueError('invalid feedback phase interval')

    def phases(self, t0, t1):
        t0, t1 = exact(t0), exact(t1)
        if t0 > t1 or t0 < self.capture:
            raise ValueError('future physical interval required')
        if not self.moving:
            return self.low, self.high
        return min(self.duration, self.low+t0-self.capture), min(self.duration, self.high+t1-self.capture)

    def finish_upper(self):
        if not self.moving and self.low != self.duration:
            return None
        return self.capture+self.duration-self.low


class SharedClock:
    """One clock drives actual inputs AND reference, including pause/resume.

    A committed moving chain cannot be changed. Unreserved pause is supported
    only at a stopped primitive boundary; no emergency-braking claim is made.
    """
    def __init__(self, trajectory):
        self.trajectory = trajectory
        self.at, self.saved, self.running, self.locked = Q(0), Q(0), False, False
        self.completed = None

    def phase(self, now):
        now = exact(now)
        if now < self.at:
            raise ValueError('clock reversal')
        return min(self.trajectory.chain.duration, self.saved+(now-self.at if self.running else 0))

    def resume(self, now, *, commit=True):
        phase = self.phase(now)
        if self.running or phase not in self.trajectory.offsets or phase == self.trajectory.chain.duration:
            raise ValueError('resume requires a stopped boundary')
        self.at, self.saved, self.running, self.locked = exact(now), phase, True, commit

    def pause(self, now):
        phase = self.phase(now)
        if self.locked and phase < self.trajectory.chain.duration:
            raise ValueError('cannot change an outstanding time reservation')
        if phase not in self.trajectory.offsets:
            raise ValueError('moving stop would omit braking; unqualified')
        if phase == self.trajectory.chain.duration and self.running:
            self.completed = self.at+self.trajectory.chain.duration-self.saved
        self.at, self.saved, self.running = exact(now), phase, False

    def end_time(self, now):
        if self.phase(now) != self.trajectory.chain.duration:
            return None
        return self.at+self.trajectory.chain.duration-self.saved if self.running else self.completed


class Plant:
    """Closed-form source endpoint; evaluation and public feedback are separate."""
    def __init__(self, trajectory, initial=(0., 0., 0., 0., 0.)):
        trajectory.chain.sample(0, initial)  # validate private task parameters once
        self.trajectory, self._initial = trajectory, tuple(initial)
        self.clock = SharedClock(trajectory)

    def evaluate(self, now):
        phase = self.clock.phase(now)
        result = self.trajectory.chain.sample(float(phase), self._initial)
        result['evaluation'].update(physical_time=str(exact(now)), controller_phase=str(phase),
                                    shared_clock=CLOCK_CONTRACT)
        if not self.clock.running:
            result['evaluation']['control'] = {'v_cmd': 0., 'omega_cmd': 0.}
        return result

    def observe(self, now):
        phase, duration = self.clock.phase(now), self.trajectory.chain.duration
        done = phase == duration
        state = 'DONE' if done else 'RUNNING' if self.clock.running else 'STOPPED'
        low, high = (phase, phase) if state != 'RUNNING' else (max(Q(0), phase-PHASE_ERROR), min(duration, phase+PHASE_ERROR))
        record = self.evaluate(now)
        xy = [format(x, '.12g') for x in record['observation']]
        truth = record['evaluation']['pose_true']
        if any(abs(Q(xy[j])-Q(truth[j])) > Q('.01') for j in (0, 1)):
            raise ValueError('serialized observation exceeds localization budget')
        return {'capture': str(exact(now)), 'phase_lo': str(low), 'phase_hi': str(high),
                'state': state, 'observed_x': xy[0], 'observed_y': xy[1],
                'clock': CLOCK_CONTRACT,
                'completion_time': str(self.clock.end_time(now)) if done else None}
