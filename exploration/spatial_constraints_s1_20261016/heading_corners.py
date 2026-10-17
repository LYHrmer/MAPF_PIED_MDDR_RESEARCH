"""Prototype: four-heading-corner maximum of the relaxed MOVE support.

The proof is in HEADING_CORNER_RULE.md. This is a finite algebraic operator,
not a forbidden-set solver or a release gate. It has NOT been run on tasks.
The original independent pose boxes are essential. A feedback-conditioned
joint domain cannot be passed as though it were the original prior.
"""
from fractions import Fraction as Q
from math import factorial

import sympy as sp

from composition import CONDITION, CONTROLLER, DIRECTIONS, H
from support_domain import MoveDomain, rank_condition
from support_scope import rational_range


ORIGINAL_PRIOR = 'v2_original_independent_pose_boxes'


def half_angle_endpoint(order=1):
    """Exact rational enclosure of tan(H/2), by alternating Taylor bounds.

    order changes arithmetic enclosure, never the physical heading prior.
    No search or floating trigonometric evaluation is performed.
    """
    if type(order) is not int or not 1 <= order <= 8:
        raise ValueError('arithmetic order must be an integer in [1, 8]')
    z = H/2
    sin_lo = sum(((-1)**j*z**(2*j+1)/factorial(2*j+1)
                  for j in range(2*order)), Q(0))
    sin_hi = sin_lo+z**(4*order+1)/factorial(4*order+1)
    cos_lo = sum(((-1)**j*z**(2*j)/factorial(2*j)
                  for j in range(2*order)), Q(0))
    cos_hi = cos_lo+z**(4*order)/factorial(4*order)
    if not 0 < cos_lo <= cos_hi or not 0 < sin_lo <= sin_hi:
        raise ValueError('Taylor qualification failed')
    return sin_lo/cos_hi, sin_hi/cos_lo


def absolute_range(bounds):
    lo, hi = bounds
    return (Q(0) if lo <= 0 <= hi else min(abs(lo), abs(hi)),
            max(abs(lo), abs(hi)))


def corner_support(a, b, *, allowed_set_kind, arithmetic_order=1):
    """Enclose max V over the original heading box using four exact corners.

    V maximizes x-y with the finite progress rectangle RELAXED. The lower
    endpoint returned here is NOT a lower bound on a physical contact time.
    Callers must bind descriptors to qualified complete chains and the
    original prior; this function does not authenticate incoming feedback.
    Existing successful shared fast paths should bypass this extra work.
    """
    work = dict(symbolic_derivatives=0, rational_enclosures=0,
                polynomial_terms=0, heading_corners_evaluated=0,
                heading_bisections=0)
    result = {'operations': work, 'progress_rectangle_relaxed': True,
              'lower_bound_kind': 'RELAXED_SUPPORT_ONLY_NOT_CONTACT',
              'contact_witness_verified': False,
              'inverse_time_qualified': False,
              'is_release_authorization': False,
              'independent_novelty_established': False}
    if allowed_set_kind != ORIGINAL_PRIOR:
        return {**result, 'status': 'FALLBACK_NONPRODUCT_OR_CHANGED_PRIOR'}
    for domain in (a, b):
        if type(domain) is not MoveDomain:
            raise ValueError('qualified MOVE descriptors required')
        if (domain.condition != CONDITION or domain.controller != CONTROLLER
                or domain.heading_half != H
                or domain.forward not in DIRECTIONS
                or domain.lateral != (-domain.forward[1], domain.forward[0])
                or domain.body_half != (Q('.3'), Q('.1'))
                or domain.translation_half not in
                ((Q('.02'), Q('.01')), (Q('.01'), Q('.02')))):
            raise ValueError('descriptor outside the frozen v2 source')
    rank = rank_condition(a, b)
    result['rank'] = rank
    if rank['status'] != 'UNIFORMLY_INVERTIBLE':
        return {**result, 'status': 'FALLBACK_SINGULAR_INCLUDED'}

    ta, tb = variables = sp.symbols('ta tb', real=True)
    rotations = [sp.Matrix([[(1-t*t)/(1+t*t), -2*t/(1+t*t)],
                            [2*t/(1+t*t), (1-t*t)/(1+t*t)]])
                 for t in variables]
    ra, rb = rotations
    ea, eb = ra*sp.Matrix(a.forward), rb*sp.Matrix(b.forward)
    wa, wb = ra*sp.Matrix(a.lateral), rb*sp.Matrix(b.lateral)
    matrix = sp.Matrix.hstack(ea, -eb)
    normal = (matrix.T.inv()*sp.Matrix([1, -1])).applyfunc(sp.cancel)
    r0 = (sp.Matrix(a.origin)-sp.Matrix(b.origin)
          + ra*sp.Matrix(a.displacement)-rb*sp.Matrix(b.displacement))
    # Same six support terms as the frozen common kernel. Absolute-value
    # enclosures allow sign changes; no new outer geometry is introduced.
    terms = ((a.body_half[0], normal.dot(ea)),
             (a.body_half[1], normal.dot(wa)),
             (b.body_half[0], normal.dot(eb)),
             (b.body_half[1], normal.dot(wb)),
             (a.translation_half[0]+b.translation_half[0], normal[0]),
             (a.translation_half[1]+b.translation_half[1], normal[1]))
    endpoint = half_angle_endpoint(arithmetic_order)
    rows = []
    for sign_a, sign_b in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        boxes = tuple(endpoint if s > 0 else (-endpoint[1], -endpoint[0])
                      for s in (sign_a, sign_b))
        shift = rational_range(-normal.dot(r0), variables, boxes, work)
        if shift is None:
            return {**result, 'status': 'FALLBACK_ARITHMETIC_DENOMINATOR',
                    'corner_rows': rows}
        lo, hi = shift
        for extent, expression in terms:
            bounds = rational_range(expression, variables, boxes, work)
            if bounds is None:
                return {**result, 'status': 'FALLBACK_ARITHMETIC_DENOMINATOR',
                        'corner_rows': rows}
            lower, upper = absolute_range(bounds)
            lo, hi = lo+extent*lower, hi+extent*upper
        rows.append({'heading': (sign_a*H, sign_b*H),
                     'relaxed_support_enclosure': (lo, hi)})
        work['heading_corners_evaluated'] += 1
    return {**result, 'status': 'FOUR_CORNER_RELAXED_SUPPORT',
            'corner_rows': rows,
            'max_relaxed_progress_enclosure':
            (max(row['relaxed_support_enclosure'][0] for row in rows),
             max(row['relaxed_support_enclosure'][1] for row in rows)),
            'arithmetic_order': arithmetic_order}
