"""Conditional support theorem for v2 MOVE pairs, without a search tree.

Build the full same-delta Minkowski support from source descriptors; prove
support signs and monotonicity by exact rational polynomial enclosures.
No sampling, floating trigonometry, witness search, optimizer or controller.
This standard shared analytic preprocessing is NOT an exclusive algorithm.
"""
from fractions import Fraction as Q
import sympy as sp

from support_domain import rank_condition


def mul(a, b):
    products = [x*y for x in a for y in b]
    return min(products), max(products)


def power(interval, exponent):
    lo, hi = interval
    if exponent == 0:
        return Q(1), Q(1)
    if exponent % 2:
        return lo**exponent, hi**exponent
    return (Q(0) if lo <= 0 <= hi else min(lo**exponent, hi**exponent),
            max(lo**exponent, hi**exponent))


def polynomial_range(expression, variables, boxes, work):
    lower = upper = Q(0)
    for exponents, coefficient in sp.Poly(expression, *variables).terms():
        term = (Q(coefficient), Q(coefficient))
        for box, degree in zip(boxes, exponents):
            term = mul(term, power(box, degree))
        lower, upper = lower+term[0], upper+term[1]
        work['polynomial_terms'] += 1
    return lower, upper


def rational_range(expression, variables, boxes, work):
    """Outward exact enclosure; dependency loss causes fallback, never success."""
    work['rational_enclosures'] += 1
    numerator, denominator = sp.fraction(sp.cancel(expression))
    a = polynomial_range(numerator, variables, boxes, work)
    b = polynomial_range(denominator, variables, boxes, work)
    if b[0] <= 0 <= b[1]:
        return None
    return mul(a, (1/b[1], 1/b[0]))


def fixed_sign(interval):
    if interval is None:
        return None
    lo, hi = interval
    if lo == hi == 0:
        return 0
    if lo >= 0:
        return 1
    if hi <= 0:
        return -1
    return None


def support_scope(a, b):
    """An upper bound on max(x-y), relaxing the finite progress rectangle.

    Collision => r0+M(x,y) in Z => x-y <= h_Z(n)-n.r0,
    where n=M^{-T}(1,-1). A monotone relaxed value need not be attained in
    the action domains. An exact endpoint additionally needs inverse-time
    qualification and an admissible full-body contact witness.
    """
    work = dict(symbolic_derivatives=0, rational_enclosures=0, polynomial_terms=0)
    result = {'rank': rank_condition(a, b), 'operations': work,
              'progress_rectangle_relaxed': True, 'contact_witness_verified': False,
              'is_release_authorization': False, 'exclusive_baseline_advantage': False}
    if result['rank']['status'] != 'UNIFORMLY_INVERTIBLE':
        return {**result, 'status': 'FALLBACK_SINGULAR_INCLUDED'}
    ta, tb = variables = sp.symbols('ta tb', real=True)
    h = a.heading_half
    # t=tan(delta/2), |t| <= (H/2)/(1-(H/2)^2/2), by sin z<=z, cos z>=1-z²/2.
    z = h/2
    radius = z/(1-z*z/2)
    boxes = ((-radius, radius), (-radius, radius))
    rotations = [sp.Matrix([[(1-t*t)/(1+t*t), -2*t/(1+t*t)],
                            [2*t/(1+t*t), (1-t*t)/(1+t*t)]]) for t in variables]
    ra, rb = rotations
    ea, eb = ra*sp.Matrix(a.forward), rb*sp.Matrix(b.forward)
    wa, wb = ra*sp.Matrix(a.lateral), rb*sp.Matrix(b.lateral)
    matrix = sp.Matrix.hstack(ea, -eb)
    normal = (matrix.T.inv()*sp.Matrix([1, -1])).applyfunc(sp.cancel)
    r0 = (sp.Matrix(a.origin)-sp.Matrix(b.origin)
          + ra*sp.Matrix(a.displacement)-rb*sp.Matrix(b.displacement))
    supports = ((a.body_half[0], normal.dot(ea)), (a.body_half[1], normal.dot(wa)),
                (b.body_half[0], normal.dot(eb)), (b.body_half[1], normal.dot(wb)),
                (a.translation_half[0]+b.translation_half[0], normal[0]),
                (a.translation_half[1]+b.translation_half[1], normal[1]))
    terms, sign_bounds = [], []
    for extent, expression in supports:
        bound = rational_range(expression, variables, boxes, work)
        sign = fixed_sign(bound)
        sign_bounds.append(bound)
        if sign is None:
            return {**result, 'status': 'FALLBACK_SUPPORT_SIGN', 'support_bounds': sign_bounds}
        terms.append(extent*sign*expression)
    value = sp.cancel(sum(terms)-normal.dot(r0))
    derivatives, signs = [], []
    for variable in variables:
        # d t / d delta = (1+t²)/2 > 0: half-angle and physical-angle signs agree.
        derivative = sp.cancel(sp.diff(value, variable))
        work['symbolic_derivatives'] += 1
        bound = rational_range(derivative, variables, boxes, work)
        derivatives.append(bound)
        signs.append(fixed_sign(bound))
    result.update(support_bounds=sign_bounds, half_angle_derivative_bounds=derivatives,
                  relaxed_progress_support=str(sp.factor(value)), half_angle_radius=radius)
    if any(sign is None for sign in signs):
        return {**result, 'status': 'FALLBACK_MONOTONICITY_UNRESOLVED'}
    # Enclose the actual corner tan(+/-H/2), not a point outside the true prior.
    t_lo, t_hi = z-z**3/6, radius
    corner_boxes = tuple((t_lo, t_hi) if s > 0 else (-t_hi, -t_lo) for s in signs)
    enclosure = rational_range(value, variables, corner_boxes, work)
    if enclosure is None:
        return {**result, 'status': 'FALLBACK_CORNER_DENOMINATOR'}
    return {**result, 'status': 'MONOTONE_RELAXED_SUPPORT',
            'maximizing_heading_corner': [h if s > 0 else -h for s in signs],
            'max_relaxed_progress_enclosure': enclosure,
            'finite_progress_attainment': 'REQUIRES_SEPARATE_CONTACT_CERTIFICATE'}
