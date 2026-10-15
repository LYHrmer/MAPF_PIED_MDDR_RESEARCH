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
                            (.02, .01, .002, .01, .01)):
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
                or len(self.start) != 2 or not all(math.isfinite(x) for x in self.start)):
            raise ValueError('unsupported controller/mode/initial condition')

    @property
    def duration(self):
        return self.length/self.speed + self.speed/self.acceleration

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
        evaluation = {'task': self.task, 'robot': self.robot, 'physical_time': now,
                      'reference_phase': s, 'pose_ref': ref, 'pose_true': truth,
                      'pose_observed': observed, 'control': {'v_cmd': v, 'omega_cmd': 0.},
                      'speed': v, 'mode': mode, 'controller': CONTROLLER, 'condition': CONDITION,
                      'tracking_error': [truth[i]-ref[i] for i in range(3)],
                      'localization_error': [observed[i]-truth[i] for i in (0, 1)]}
        return {'sensor': sensor, 'evaluation': evaluation}
