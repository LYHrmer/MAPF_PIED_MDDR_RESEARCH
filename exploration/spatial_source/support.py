"""Exploratory rational support bounds for the unchanged v2 trajectory family.

One task delta rotates displacement AND body. TURN uses the frozen enclosure.
No sampling, floating trigonometry, controller, observation or source change.
"""
from dataclasses import dataclass, field
from fractions import Fraction as Q

from composition import H, RESERVE, DIRECTIONS, exact
from timed import Trajectory, distance

AXES = ((1, 0), (-1, 0), (0, 1), (0, -1))


def rotation_upper(a, b):
    """Upper bound max(a*cos(delta)+b*sin(delta)), |delta| <= H.

    cos = 1-delta**2/2 + e, 0 <= e <= H**4/24;
    |sin-delta| <= H**3/6. Maximize the quadratic exactly.
    """
    a, b = exact(a), exact(b)
    quadratic = a-a*H*H/2+abs(b)*H
    if a > 0 and abs(b) <= a*H:
        quadratic = a+b*b/(2*a)
    return quadratic+max(a, Q(0))*H**4/24+abs(b)*H**3/6


@dataclass(frozen=True)
class JointTrajectory(Trajectory):
    operations: dict = field(default_factory=lambda: dict(
        old_box_calls=0, joint_box_calls=0, turn_fallbacks=0,
        support_requests=0, support_cache_hits=0, quadratic_bounds=0),
        compare=False, repr=False)
    _supports: dict = field(default_factory=dict, compare=False, repr=False)

    def point_support(self, point, heading, normal, *, body=True):
        """Whole initial-parameter domain at one reference position/heading."""
        point, normal = tuple(map(exact, point)), tuple(map(exact, normal))
        if len(point) != 2 or len(normal) != 2 or not any(normal):
            raise ValueError('two coordinates and a nonzero normal required')
        if type(heading) is not int or heading not in range(4):
            raise ValueError('cardinal heading required')
        self.chain.error_box(point, point)
        key = (point, heading % 2, normal, body)
        self.operations['support_requests'] += 1
        if key in self._supports:
            self.operations['support_cache_hits'] += 1
            return self._supports[key]
        hx, hy = (Q('.3'), Q('.1')) if heading % 2 == 0 else (Q('.1'), Q('.3'))
        vertices = [(x, y) for x in (-hx, hx) for y in (-hy, hy)] if body else [(Q(0), Q(0))]
        nx, ny = normal
        dx, dy = (point[j]-self.chain.origin[j] for j in (0, 1))
        bounds = []
        for ux, uy in vertices:
            x, y = dx+ux, dy+uy
            bounds.append(rotation_upper(nx*x+ny*y, ny*x-nx*y))
            self.operations['quadratic_bounds'] += 1
        bx, by = (Q('.02'), Q('.01')) if self.chain.heading % 2 == 0 else (Q('.01'), Q('.02'))
        result = (nx*self.chain.origin[0]+ny*self.chain.origin[1]
                  +bx*abs(nx)+by*abs(ny)+max(bounds)
                  +RESERVE*(abs(nx)+abs(ny)))
        self._supports[key] = result
        return result

    def action_box(self, index, phase_lo, phase_hi, *, body=True):
        self.operations['old_box_calls'] += 1
        old = super().action_box(index, phase_lo, phase_hi, body=body)
        if old is None:
            return None
        action, start = self.chain.primitives[index], self.offsets[index]
        if action.kind == 'TURN':
            self.operations['turn_fallbacks'] += 1
            return old
        self.operations['joint_box_calls'] += 1
        end = start+action.duration if action.duration is not None else self.chain.duration
        lo, hi = max(start, exact(phase_lo)), min(end, exact(phase_hi))
        points = [action.start]
        if action.kind == 'MOVE':
            length = sum(abs(action.end[j]-action.start[j]) for j in (0, 1))
            direction = DIRECTIONS[action.heading]
            points = [tuple(action.start[j]+direction[j]*distance(t-start, length)
                            for j in (0, 1)) for t in (lo, hi)]
        support = [max(self.point_support(p, action.heading, n, body=body) for p in points) for n in AXES]
        joint = (-support[1], support[0], -support[3], support[2])
        result = (max(old[0], joint[0]), min(old[1], joint[1]),
                  max(old[2], joint[2]), min(old[3], joint[3]))
        if result[0] > result[1] or result[2] > result[3]:
            raise ValueError('inconsistent certified enclosures')
        return result

    def move_chords(self, index):
        """Affine upper supports in distance, by convexity of exact support.

        Returns length and (normal, intercept, slope). Numerical upper bounds
        at both endpoints suffice; their interpolation covers the exact convex
        support throughout the action. No reset to a waypoint-local error set.
        """
        a = self.chain.primitives[index]
        if a.kind != 'MOVE':
            raise ValueError('affine progress adapter is MOVE-only')
        length = sum(abs(a.end[j]-a.start[j]) for j in (0, 1))
        lines = []
        for n in AXES:
            left = self.point_support(a.start, a.heading, n)
            right = self.point_support(a.end, a.heading, n)
            lines.append((n, left, (right-left)/length))
        return length, tuple(lines)
