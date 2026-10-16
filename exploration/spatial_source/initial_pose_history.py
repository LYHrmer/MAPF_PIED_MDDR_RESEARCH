"""C1-only public-history feasibility diagnostic, not a general estimator.

Keep the original task b, delta and localization bounds. No phase is invented,
no fixed-bias cancellation is assumed, and no controller/source is evaluated.
"""
from fractions import Fraction as Q

from composition import CONDITION, H, contract, exact

PRIOR_X = (Q('-.02'), Q('.02'))


def validate_c1(fixture, source_contract):
    expected = {'origin': ['-1', '0'], 'heading': 0,
                'actions': [['MOVE', '2'], ['TURN', 1], ['MOVE', '1'], ['HOLD', '0']]}
    if (fixture['condition'] != CONDITION or fixture['robots']['A'] != expected
            or source_contract != contract()):
        raise ValueError('this projection requires the frozen C1 task/source')


def intersect_x(a, b):
    a, b = tuple(map(exact, a)), tuple(map(exact, b))
    if len(a) != 2 or len(b) != 2 or a[0] > a[1] or b[0] > b[1]:
        raise ValueError('invalid interval')
    lo, hi = max(a[0], b[0]), min(a[1], b[1])
    if lo > hi:
        raise ValueError('inconsistent public history; never an empty-safe state')
    return lo, hi


def project_c1(admitted_packet):
    """Necessary task-initial b_x interval from one already-admitted C1 packet.

    For the northbound A_2, d=(2,r), 0<=r<=1. Old certified y tracking
    projection .03 and localization .01 bound r. With |delta|<=H,
      b_x = z_x - 1 - ell_x + 2*(1-cos(delta)) + r*sin(delta).
    Hence 2*(1-cos(delta)) in [0,H^2], |r*sin(delta)|<=r_hi*H.
    This is an OUTER projection. It does not identify b or remove ell.
    """
    p = admitted_packet
    if (p.binding.robot != 'A' or p.binding.action != 'A_2' or p.binding.condition != CONDITION
            or p.kind != 'PROGRESS_BOUND' or p.localization_bound != '.01' or p.tracking_bound != '.03'):
        raise ValueError('unqualified admitted C1 action/bounds')
    x, y = exact(p.observed_x), exact(p.observed_y)
    loc, tracking = exact(p.localization_bound), exact(p.tracking_bound)
    rlo, rhi = max(Q(0), y-loc-tracking), min(Q(1), y+loc+tracking)
    if rlo > rhi:
        raise ValueError('no reference position in bound action')
    bx = intersect_x(PRIOR_X, (x-1-loc-rhi*H, x-1+loc+H*H+rhi*H))
    return {'bx': bx, 'reference_r': (rlo, rhi),
            'by': (Q('-.01'), Q('.01')), 'delta': (-H, H),
            'localization_bound': loc, 'task_parameter_not_waypoint_reset': True}


def propagate_translation_x(old_box, bx):
    """Same b_x enters every body/turn/HOLD point additively with coefficient 1.

    The frozen C1 enclosure explicitly adds +/- .02 to x. Replacing only that
    term is conservative for the intersection's b_x outer projection; all
    heading/body/time and b_y/delta terms remain untouched.
    """
    old_box, bx = tuple(map(exact, old_box)), tuple(map(exact, bx))
    if (len(old_box) != 4 or len(bx) != 2 or bx != intersect_x(PRIOR_X, bx)
            or old_box[0] > old_box[1] or old_box[2] > old_box[3]):
        raise ValueError('unqualified prior box or posterior')
    result = (old_box[0]+Q('.02')+bx[0], old_box[1]-Q('.02')+bx[1], old_box[2], old_box[3])
    if result[0] > result[1]:
        raise ValueError('inconsistent propagation')
    return result
