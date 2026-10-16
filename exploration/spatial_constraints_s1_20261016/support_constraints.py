"""Analytic MOVE upper bounds; exploratory standard half-plane adaptation.

Geometry only, not a release gate. Unsupported inverse phases return fallback.
All times retain chain offsets, acceleration/braking and original precedence.
"""
from fractions import Fraction as Q
from itertools import combinations
from interface import q


def bounded_vertices(lines):
    """Vertices of a bounded 2-D intersection ax+by<=c (caller adds box)."""
    lines = [tuple(map(q, row)) for row in lines]
    if any(len(row) != 3 for row in lines):
        raise ValueError('three exact coefficients required')
    vertices, solves, tests = set(), 0, 0
    for first, second in combinations(lines, 2):
        a, b, c = first
        d, e, f = second
        det = a*e-b*d
        if det == 0:
            continue
        solves += 1
        x, y = (c*e-b*f)/det, (a*f-c*d)/det
        feasible = True
        for aa, bb, cc in lines:
            tests += 1
            if aa*x+bb*y > cc:
                feasible = False
                break
        if feasible:
            vertices.add((x, y))
    return sorted(vertices), {'line_intersections': solves, 'halfplane_tests': tests}


def cruise_upper(ta, ia, tb, ib, max_a, min_b, la, lb):
    """Monotone inverse allows independent progress extrema as outer bound.

    A cruise inverse is used only at the extrema, not assumed for the complete
    possible-contact set. Other points cannot yield a larger phase difference.
    """
    if not (Q(1, 8) <= max_a <= la-Q(1, 8) and Q(1, 8) <= min_b <= lb-Q(1, 8)):
        return None
    return ta.offsets[ia]-tb.offsets[ib]+2*(max_a-min_b)


def pair_upper(ta, ia, tb, ib):
    """Collision implies support(A-B,n)>=0 for every selected axis.

    Chords replace exact supports from above, hence all collisions lie in the
    resulting progress polygon. Its overlap is not a collision conclusion.
    """
    if ta.chain.primitives[ia].kind != 'MOVE' or tb.chain.primitives[ib].kind != 'MOVE':
        return {'status': 'FALLBACK_NON_MOVE', 'upper': None, 'operations': {}}
    la, ca = ta.move_chords(ia)
    lb, cb = tb.move_chords(ib)
    opposing = {n: (intercept, slope) for n, intercept, slope in cb}
    lines = [(Q(-1), Q(0), Q(0)), (Q(1), Q(0), la),
             (Q(0), Q(-1), Q(0)), (Q(0), Q(1), lb)]
    for n, aa, ab in ca:
        ba, bb = opposing[(-n[0], -n[1])]
        lines.append((-ab, -bb, aa+ba))
    vertices, operations = bounded_vertices(lines)
    if not vertices:
        return {'status': 'CERTIFIED_EMPTY', 'upper': None, 'lines': lines,
                'vertices': vertices, 'operations': operations}
    max_a, min_b = max(x for x, y in vertices), min(y for x, y in vertices)
    upper = cruise_upper(ta, ia, tb, ib, max_a, min_b, la, lb)
    return {'status': 'CRUISE_EXTREMA_BOUND' if upper is not None else 'FALLBACK_INVERSE_PHASE',
            'upper': upper, 'max_a': max_a, 'min_b': min_b,
            'lines': lines, 'vertices': vertices, 'operations': operations}


def region_upper(ta, ia, tb, ib, region):
    """Strong first/last-region adaptation, same supports, no dyadic rounding."""
    if ta.chain.primitives[ia].kind != 'MOVE' or tb.chain.primitives[ib].kind != 'MOVE':
        return {'status': 'FALLBACK_NON_MOVE', 'upper': None, 'operations': {}}
    region_support = {(1, 0): region.xmax, (-1, 0): -region.xmin,
                      (0, 1): region.ymax, (0, -1): -region.ymin}
    spans, lengths, tests = [], [], 0
    for tr, index in ((ta, ia), (tb, ib)):
        length, chords = tr.move_chords(index)
        lo, hi = Q(0), length
        for n, intercept, slope in chords:
            tests += 1
            intercept += region_support[(-n[0], -n[1])]
            if slope > 0:
                lo = max(lo, -intercept/slope)
            elif slope < 0:
                hi = min(hi, -intercept/slope)
            elif intercept < 0:
                return {'status': 'CERTIFIED_EMPTY', 'upper': None,
                        'operations': {'linear_tests': tests}}
        if lo > hi:
            return {'status': 'CERTIFIED_EMPTY', 'upper': None,
                    'operations': {'linear_tests': tests}}
        spans.append((lo, hi))
        lengths.append(length)
    upper = cruise_upper(ta, ia, tb, ib, spans[0][1], spans[1][0], *lengths)
    return {'status': 'CRUISE_EXTREMA_BOUND' if upper is not None else 'FALLBACK_INVERSE_PHASE',
            'upper': upper, 'spans': spans, 'operations': {'linear_tests': tests}}
