"""Declared ideal-unicycle source, SI units; no LIMO calibration or randomness.

Closed-form samples are for source/interface qualification. Continuous bounds
come from inequalities, never from the extrema of sampled points.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
import math

CONDITION = 'straight_trapezoid_v05_a1_length_le3_v1'
CONTROLLER = 'ideal_feedforward_trapezoid_v1'
COMMITMENT = 'A_east_to_2_permanent_hold_v1'
LOC_BIAS_MAX = .009999  # Remaining 1e-6 m covers numeric/serialization budget.


def public_contract():
    """Public admissible set, not the actual initial error or private state."""
    return {'schema': 'declared_unicycle_source_v1', 'condition': CONDITION,
            'controller': CONTROLLER, 'units': ['m', 's', 'rad'],
            'speed': '.5', 'acceleration': '1', 'body_half': ['.3', '.1'],
            'initial_half': ['.02', '.01', '.002'], 'length_range': ['.25', '3'],
            'tracking_half': ['.03', '.02'], 'heading_bound': '.002',
            'localization_bound': '.01', 'localization_bias_max': '.009999',
            'numeric_localization_reserve': '.000001', 'coordinate_limit': '10',
            'suffix_commitment': COMMITMENT, 'hold': 'zero_input_no_drift_permanent',
            'risk': 'DECLARED_HARD_SET_NOT_EMPIRICAL_OR_GAUSSIAN'}


def admit_fixture(fixture):
    """Bind S1 geometry and modes to this source before starting any task."""
    c = public_contract()
    if (fixture['condition'] != CONDITION or fixture['units'] != {'length': 'm', 'time': 's', 'angle': 'rad'}
            or fixture['speed'] != c['speed'] or fixture['acceleration'] != c['acceleration']
            or fixture['body_half'] != c['body_half'] or fixture['heading_error'] != c['heading_bound']
            or fixture['localization_bound'] != c['localization_bound']
            or fixture['tracking_parallel'] != c['tracking_half'][0]
            or fixture['tracking_cross'] != c['tracking_half'][1]
            or fixture['A_path'] != [['-1', '0'], ['0', '0'], ['2', '0']]
            or fixture['B_path'] != [['0', '-1'], ['0', '0'], ['0', '1']]
            or fixture['existing_order'] != 'A_BEFORE_B'):
        raise ValueError('fixture differs from qualified source/commitment')
    return c


@dataclass(frozen=True)
class Envelope:
    """Local reference-axis half widths; never an empirical maximum."""
    along: Q
    cross: Q
    heading: Q

    def __post_init__(self):
        if any(not isinstance(x, Q) for x in (self.along, self.cross, self.heading)):
            raise ValueError('exact rational extents required')
        if min(self.along, self.cross, self.heading) < 0:
            raise ValueError('negative uncertainty extent')


def propagate_straight(initial, length):
    length = Q(length)
    if not Q('.25') <= length <= 3 or not admits_straight(initial):
        raise ValueError('new straight primitive outside admitted initial set')
    return Envelope(initial.along+length*initial.heading**2/2,
                    initial.cross+length*initial.heading, initial.heading)


def admits_straight(initial):
    return (initial.along <= Q('.02') and initial.cross <= Q('.01')
            and initial.heading <= Q('.002'))


def stopped_quarter_turn(initial, *, speed='0', omega='0'):
    if (Q(speed) != 0 or Q(omega) != 0 or max(initial.along, initial.cross) > Q('.03')
            or initial.heading > Q('.002')):
        raise ValueError('turn requires stopped state in the declared position set')
    # Position does not move under the declared ideal pivot controller. Express
    # the same error in the new local axes; do not reset it at the waypoint.
    return Envelope(initial.cross, initial.along, initial.heading)


def permanent_hold(initial, *, drift='0'):
    if Q(drift) != 0:
        raise ValueError('nonzero indefinite drift has no finite declared hold bound')
    return initial


def bounds(length='3', heading='.002'):
    length, heading = Q(length), Q(heading)
    if not 0 < length <= 3 or not 0 <= heading <= Q('.002'):
        raise ValueError('outside declared primitive condition')
    # |sin psi| <= |psi|; 1-cos psi <= psi^2/2 over the entire primitive.
    return {'parallel': Q('.02') + length*heading*heading/2,
            'cross': Q('.01') + length*heading,
            'heading': heading}


@dataclass(frozen=True)
class Initial:
    along: float = 0.
    cross: float = 0.
    heading: float = 0.
    loc_x: float = 0.
    loc_y: float = 0.

    def __post_init__(self):
        for v, limit in zip((self.along, self.cross, self.heading, self.loc_x, self.loc_y),
                            (.02, .01, .002, LOC_BIAS_MAX, LOC_BIAS_MAX)):
            if not math.isfinite(v) or abs(v) > limit:
                raise ValueError('initial condition outside source contract')


@dataclass(frozen=True)
class Straight:
    task: str
    robot: str
    start: tuple
    axis: str
    length: float
    start_time: float = 0.
    initial: Initial = Initial()
    speed: float = .5
    acceleration: float = 1.

    def __post_init__(self):
        if (self.axis not in ('E', 'N') or not .25 <= self.length <= 3
                or self.speed != .5 or self.acceleration != 1.
                or not math.isfinite(self.start_time) or self.start_time < 0
                or len(self.start) != 2 or not all(math.isfinite(x) and abs(x)+self.length+.1 <= 10 for x in self.start)):
            raise ValueError('unsupported controller/mode/initial condition')

    @property
    def duration(self):
        return self.length/self.speed + self.speed/self.acceleration

    def observation(self, now, *, kind='PROGRESS_BOUND'):
        record = self.sample(now)
        if kind not in ('PROGRESS_BOUND', 'END') or (kind == 'END' and record['evaluation']['mode'] != 'GOAL_HOLD'):
            raise ValueError('local controller has not completed the action')
        return record['sensor']

    def sample(self, now):
        if not math.isfinite(now) or now < 0:
            raise ValueError('invalid physical time')
        t, ramp = now-self.start_time, self.speed/self.acceleration
        if t <= 0:
            s, v, mode = 0., 0., 'WAIT'
        elif t < ramp:
            s, v, mode = .5*self.acceleration*t*t, self.acceleration*t, 'ACCEL'
        elif t <= self.duration-ramp:
            s, v, mode = self.speed*(t-ramp/2), self.speed, 'STRAIGHT'
        elif t < self.duration:
            left = self.duration-t
            s, v, mode = self.length-.5*self.acceleration*left*left, self.acceleration*left, 'BRAKE'
        else:
            s, v, mode = self.length, 0., 'GOAL_HOLD'
        u, w, theta = ((1., 0.), (0., 1.), 0.) if self.axis == 'E' else ((0., 1.), (-1., 0.), math.pi/2)
        ini = self.initial
        along = ini.along+s*math.cos(ini.heading)
        cross = ini.cross+s*math.sin(ini.heading)
        ref = [self.start[i]+s*u[i] for i in (0, 1)] + [theta]
        truth = [self.start[i]+along*u[i]+cross*w[i] for i in (0, 1)] + [theta+ini.heading]
        observed = [truth[0]+ini.loc_x, truth[1]+ini.loc_y]
        sensor = {'task': self.task, 'robot': self.robot, 'action': self.robot+'_move',
                  'condition': CONDITION, 'capture': format(now, '.12g'),
                  'observed_x': format(observed[0], '.12g'), 'observed_y': format(observed[1], '.12g')}
        # Check the *serialized* observation against represented truth. Numeric
        # reserve is explicit; the hard tracking proof still comes from bounds().
        if any(abs(Q(sensor[k])-Q(truth[i])) > Q('.01') for i,k in enumerate(('observed_x', 'observed_y'))):
            raise ValueError('serialized localization violated declared numeric budget')
        evaluation = {'task': self.task, 'robot': self.robot, 'physical_time': now,
                      'reference_phase': s, 'pose_ref': ref, 'pose_true': truth,
                      'pose_observed': observed, 'control': {'v_cmd': v, 'omega_cmd': 0.},
                      'speed': v, 'mode': mode, 'controller': CONTROLLER, 'condition': CONDITION,
                      'tracking_error': [truth[i]-ref[i] for i in range(3)],
                      'localization_error': [observed[i]-truth[i] for i in (0, 1)]}
        return {'sensor': sensor, 'evaluation': evaluation}
