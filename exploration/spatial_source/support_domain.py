"""Whole-task MOVE geometry for a shared analytic support comparator.

This describes the original v2 prior, not a feedback-conditioned joint set.
For every body point: o + b + R(delta) (d + e*x + u).
The SAME task b/delta rotates cumulative displacement and the body through
every action. A descriptor is geometry, not a clock observation or release.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
import hashlib
import json

from composition import Chain, CONDITION, CONTROLLER, DIRECTIONS, H, exact


@dataclass(frozen=True)
class MoveDomain:
    task_parameters: str
    index: int
    origin: tuple
    displacement: tuple
    forward: tuple
    lateral: tuple
    translation_half: tuple
    length: Q
    offset: Q
    heading_half: Q = H
    body_half: tuple = (Q('.3'), Q('.1'))
    condition: str = CONDITION
    controller: str = CONTROLLER

    @property
    def rotated_vertex_coefficients(self):
        """Four d+u vectors at x=0; not independently uncertain vertices."""
        return tuple(tuple(self.displacement[j] + a*self.forward[j] + b*self.lateral[j]
                           for j in (0, 1))
                     for a in (-self.body_half[0], self.body_half[0])
                     for b in (-self.body_half[1], self.body_half[1]))


def move_domain(chain, index):
    if type(chain) is not Chain or type(index) is not int or not 0 <= index < len(chain.primitives):
        raise ValueError('qualified complete v2 Chain and valid action index required')
    action = chain.primitives[index]
    if action.kind != 'MOVE':
        raise ValueError('MOVE-only descriptor; TURN/WAIT/HOLD require their own continuous geometry')
    # Include the complete chain, including waiting and terminal occupancy.
    # Same chain => same parameter family for all actions; this is not a robot ID.
    payload = {'origin': chain.origin, 'heading': chain.heading,
               'actions': [(a.kind, a.start, a.end, a.heading, a.next_heading,
                            a.duration, a.turn) for a in chain.primitives],
               'condition': CONDITION, 'controller': CONTROLLER}
    family = hashlib.sha256(json.dumps(payload, default=str, sort_keys=True).encode()).hexdigest()
    forward = DIRECTIONS[action.heading]
    return MoveDomain(
        family, index, chain.origin,
        tuple(action.start[j]-chain.origin[j] for j in (0, 1)),
        forward, DIRECTIONS[(action.heading+1) % 4],
        (Q('.02'), Q('.01')) if chain.heading % 2 == 0 else (Q('.01'), Q('.02')),
        sum((action.end[j]-action.start[j])*forward[j] for j in (0, 1)),
        sum((a.duration for a in chain.primitives[:index]), Q(0)))


def rank_condition(a, b):
    """Independent original heading boxes, including delta_A=delta_B=0.

    For nominally perpendicular cardinal directions, |det M|=|cos(da-db)|
    >= 1-(2H)^2/2. For nominally parallel directions the domain contains an
    exactly singular matrix. Do not invert it by adding a numerical epsilon.
    """
    if a.heading_half != H or b.heading_half != H:
        raise ValueError('heading domain changed; requalify the source')
    det = a.forward[0]*b.forward[1]-a.forward[1]*b.forward[0]
    if det == 0:
        return {'status': 'SINGULAR_INCLUDED', 'det_abs_lower': Q(0)}
    return {'status': 'UNIFORMLY_INVERTIBLE', 'det_abs_lower': 1-2*H*H}


def affine_inverse_condition(a, b, *, max_a, min_b):
    """Check sufficient conditions on an ALREADY CERTIFIED outer progress set.

    tau_A(x) <= 1/4+2x for x <= length_A-1/8;
    tau_B(y) >= 1/4+2y for y >= 1/8. The constants cancel.
    This function does not establish the provenance/coverage of the supplied
    extrema. The consumer must bind them to a verified outer-set certificate.
    """
    max_a, min_b = exact(max_a), exact(min_b)
    if not 0 <= max_a <= a.length or not 0 <= min_b <= b.length:
        raise ValueError('progress extrema outside the declared MOVE domain')
    missing = []
    if max_a > a.length-Q(1, 8):
        missing.append('A_BRAKING_NOT_EXCLUDED')
    if min_b < Q(1, 8):
        missing.append('B_ACCELERATION_NOT_EXCLUDED')
    return {'qualified': not missing, 'reasons': missing,
            'offset_A_minus_B': a.offset-b.offset,
            'requires_certified_outer_progress_set': True}
