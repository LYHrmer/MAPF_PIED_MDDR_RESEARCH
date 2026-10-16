"""Exploratory v2 source contract: shared initial error through stopped actions.

This is a declared ideal unicycle, not fitted robot data. The invariant is
  p_true = p0 + b + R(delta) (p_ref-p0), theta_true = theta_ref + delta.
Actual/reference inputs are identical. No slip, input error or hold drift.
The old v1 initial-set failure remains valid; no old file/condition is changed.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
import math

CONDITION = 'joint_initial_se2_stopped_primitives_v2'
CONTROLLER = 'ideal_feedforward_stopped_v05_a1_pivot_w05_alpha1_v2'
H = Q('.002')
RESERVE = Q('.000001')
DIRECTIONS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def exact(x):
    if isinstance(x, (float, bool)):
        raise ValueError('exact rational input required')
    return Q(x)


def contract():
    return {'condition': CONDITION, 'controller': CONTROLLER,
            'model': 'ideal_unicycle_identical_reference_actual_inputs',
            'units': 'metre_second_radian', 'body_half': ['.3', '.1'],
            'task_initial_local_box': ['.02', '.01', '.002'],
            'speed': '.5', 'acceleration': '1', 'omega': '.5', 'alpha': '1',
            'move_length': ['.25', '3'], 'turn_slot_seconds': '4',
            'reference_displacement_axis_limit': '8', 'reference_coordinate_limit': '10',
            'localization_physical_axis_bound': '.009999', 'numerical_reserve': str(RESERVE),
            'stop_at_each_action_boundary': True, 'hold_drift': '0',
            'scope': 'whole declared chain including permanent terminal hold; no learning claim'}


@dataclass(frozen=True)
class Primitive:
    kind: str
    start: tuple
    end: tuple
    heading: int
    next_heading: int
    duration: object
    turn: int = 0


@dataclass(frozen=True)
class Chain:
    origin: tuple
    heading: int
    primitives: tuple

    def __post_init__(self):
        if not isinstance(self.origin, tuple) or not isinstance(self.primitives, tuple):
            raise ValueError('immutable chain containers required')
        if type(self.heading) is not int or self.heading not in range(4):
            raise ValueError('cardinal initial heading required')
        if len(self.origin) != 2 or any(not isinstance(x, Q) for x in self.origin):
            raise ValueError('exact origin required')
        if not self.primitives or self.primitives[-1].kind != 'HOLD':
            raise ValueError('complete chain with permanent hold required')
        p, heading = self.origin, self.heading
        for i, a in enumerate(self.primitives):
            if a.start != p or a.heading != heading:
                raise ValueError('disconnected action boundary')
            if a.kind == 'MOVE':
                u = DIRECTIONS[heading]
                length = sum((a.end[j]-p[j])*u[j] for j in (0, 1))
                if (not Q('.25') <= length <= 3 or a.end != tuple(p[j]+u[j]*length for j in (0, 1))
                        or a.next_heading != heading or a.turn != 0 or a.duration != 2*length+Q('.5')):
                    raise ValueError('unqualified move')
            elif a.kind == 'TURN':
                if (a.turn not in (-1, 1) or a.next_heading != (heading+a.turn) % 4
                        or a.start != a.end or a.duration != 4):
                    raise ValueError('unqualified stopped quarter turn')
            elif a.kind in ('WAIT', 'HOLD'):
                if a.start != a.end or a.next_heading != heading or a.turn != 0:
                    raise ValueError('nonstationary hold')
                if a.kind == 'HOLD' and (i != len(self.primitives)-1 or a.duration is not None):
                    raise ValueError('permanent hold must be terminal')
                if a.kind == 'WAIT' and (not isinstance(a.duration, Q) or a.duration < 0):
                    raise ValueError('invalid finite wait')
            else:
                raise ValueError('unknown mode')
            self.error_box(a.start, a.end)
            p, heading = a.end, a.next_heading

    @classmethod
    def build(cls, spec, *, controller=CONTROLLER, speed='.5', acceleration='1',
              drift='0', initial_speed='0', initial_omega='0'):
        if (controller != CONTROLLER or exact(speed) != Q('.5') or exact(acceleration) != 1
                or any(exact(x) != 0 for x in (drift, initial_speed, initial_omega))):
            raise ValueError('new dynamics/controller condition requires requalification')
        if set(spec) != {'origin', 'heading', 'actions'}:
            raise ValueError('explicit source schema required')
        p, heading = tuple(map(exact, spec['origin'])), spec['heading']
        if type(heading) is not int or heading not in range(4):
            raise ValueError('cardinal heading required')
        primitives = []
        for kind, arg in spec['actions']:
            next_heading, end, turn = heading, p, 0
            if kind == 'MOVE':
                length = exact(arg)
                end = tuple(p[j]+DIRECTIONS[heading][j]*length for j in (0, 1))
                duration = 2*length+Q('.5')
            elif kind == 'TURN':
                if type(arg) is not int or arg not in (-1, 1):
                    raise ValueError('quarter turn sign required')
                turn, next_heading, duration = arg, (heading+arg) % 4, Q(4)
            elif kind == 'WAIT':
                duration = exact(arg)
            elif kind == 'HOLD':
                if exact(arg) != 0:
                    raise ValueError('permanent hold takes zero input')
                duration = None
            else:
                raise ValueError('unsupported mode')
            primitives.append(Primitive(kind, p, end, heading, next_heading, duration, turn))
            p, heading = end, next_heading
        return cls(tuple(map(exact, spec['origin'])), spec['heading'], tuple(primitives))

    def error_box(self, start, end):
        """Whole axis-aligned interval, exact rational inequality, not samples.

        Shared b/delta remain latent task constants. Projecting their joint set
        to a box does not replace that set at the next action boundary.
        """
        if len(start) != 2 or len(end) != 2:
            raise ValueError('two coordinates required')
        if any(not isinstance(x, Q) for x in (*start, *end)):
            raise ValueError('exact points required')
        if start[0] != end[0] and start[1] != end[1]:
            raise ValueError('axis-aligned reference interval required')
        d = [max(abs(start[j]-self.origin[j]), abs(end[j]-self.origin[j])) for j in (0, 1)]
        if max(d) > 8 or max(map(abs, (*start, *end))) > 10:
            raise ValueError('outside declared reference domain')
        bx, by = (Q('.02'), Q('.01')) if self.heading % 2 == 0 else (Q('.01'), Q('.02'))
        return bx+d[0]*H*H/2+d[1]*H, by+d[0]*H+d[1]*H*H/2

    @property
    def duration(self):
        return sum(a.duration for a in self.primitives if a.duration is not None)

    def reference(self, now):
        """Closed-form controller evaluation, not a time-step simulator."""
        t = float(now)
        if not math.isfinite(t) or t < 0:
            raise ValueError('nonnegative finite physical time required')
        turns = 0
        for index, a in enumerate(self.primitives):
            if a.duration is not None and t >= float(a.duration):
                t -= float(a.duration)
                turns += a.turn
                continue
            # Retain unwrapped heading across quarter-turn boundaries. Geometry
            # uses the equivalent cardinal residue; the reference log stays continuous.
            theta, v, omega = (self.heading+turns)*math.pi/2, 0., 0.
            point = list(map(float, a.start))
            mode = a.kind
            if a.kind == 'MOVE':
                length = float(sum(abs(a.end[j]-a.start[j]) for j in (0, 1)))
                s, v, mode = trapezoid(t, length)
                point = [point[j]+DIRECTIONS[a.heading][j]*s for j in (0, 1)]
            elif a.kind == 'TURN':
                angle, w, mode = trapezoid(t, math.pi/2)
                theta += a.turn*angle
                omega = a.turn*w
                mode = 'TURN_'+mode
            return {'action_index': index, 'pose_ref': point+[theta],
                    'control': {'v_cmd': v, 'omega_cmd': omega}, 'mode': mode}
        raise AssertionError('terminal hold missing')

    def sample(self, now, initial=(0., 0., 0., 0., 0.)):
        """Evaluation only; no private state is an input to the compiler/guard."""
        if len(initial) != 5 or any(not math.isfinite(x) or abs(x) > limit
                                  for x, limit in zip(initial, (.02, .01, .002, .009999, .009999))):
            raise ValueError('initial state outside task condition')
        r = self.reference(now)
        along, cross, delta, loc_x, loc_y = initial
        u, w = DIRECTIONS[self.heading], DIRECTIONS[(self.heading+1) % 4]
        b = [along*u[j]+cross*w[j] for j in (0, 1)]
        d = [r['pose_ref'][j]-float(self.origin[j]) for j in (0, 1)]
        c, s = math.cos(delta), math.sin(delta)
        rotated = [c*d[0]-s*d[1], s*d[0]+c*d[1]]
        truth = [float(self.origin[j])+b[j]+rotated[j] for j in (0, 1)]+[r['pose_ref'][2]+delta]
        observation = [truth[0]+loc_x, truth[1]+loc_y]
        return {'evaluation': {**r, 'physical_time': float(now), 'pose_true': truth,
                               'tracking_error': [truth[j]-r['pose_ref'][j] for j in range(3)],
                               'localization_error': [loc_x, loc_y]},
                'observation': observation}


def trapezoid(t, length):
    """v_max=.5, acceleration=1; also omega/alpha for a stopped pivot."""
    duration = 2*length+.5
    if t < .5:
        return .5*t*t, t, 'ACCEL'
    if t <= duration-.5:
        return .5*(t-.25), .5, 'CRUISE'
    if t < duration:
        left = duration-t
        return length-.5*left*left, left, 'BRAKE'
    return length, 0., 'STOPPED'
