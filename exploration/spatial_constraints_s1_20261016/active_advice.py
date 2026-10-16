"""Exploratory advice interface for two exact progress LPs, NOT a release gate.

Predictions are only row indices. Every accepted answer is recomputed and
certified on the current original rational coefficients; no learned safety.
"""
from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import combinations

from interface import q

OBJECTIVES = {'max_A': (Q(1), Q(0)), 'min_B': (Q(0), Q(-1))}


def tick(ops, key, amount=1):
    ops[key] = ops.get(key, 0)+amount


@dataclass(frozen=True)
class ProgressLP:
    lines: tuple

    def __post_init__(self):
        if (not isinstance(self.lines, tuple) or len(self.lines) != 8
                or any(not isinstance(row, tuple) or len(row) != 3
                       or any(not isinstance(x, Q) for x in row) for row in self.lines)):
            raise ValueError('immutable exact eight-row LP required')
        la, lb = self.lines[1][2], self.lines[3][2]
        expected = ((Q(-1), Q(0), Q(0)), (Q(1), Q(0), la),
                    (Q(0), Q(-1), Q(0)), (Q(0), Q(1), lb))
        if self.lines[:4] != expected or min(la, lb) <= 0:
            raise ValueError('first four rows must bound a positive progress rectangle')

    @classmethod
    def read(cls, rows, ops):
        lines = tuple(tuple(map(q, row)) for row in rows)
        tick(ops, 'normalized_coefficients', sum(map(len, lines)))
        if len(lines) != 8 or any(len(row) != 3 for row in lines):
            raise ValueError('exactly eight three-coefficient progress halfplanes required')
        return cls(lines)


def certify(lp, objective, basis, ops):
    """Exact primal/dual feasibility and zero gap for a proposed active pair."""
    if objective not in OBJECTIVES:
        raise ValueError('unsupported objective')
    tick(ops, 'basis_attempts')
    rejected = lambda reason: {'accepted': False, 'reason': reason}
    if (not isinstance(basis, (tuple, list)) or len(basis) != 2
            or any(type(i) is not int or i not in range(8) for i in basis)
            or basis[0] == basis[1]):
        return rejected('INVALID_ADVICE')
    i, j = basis
    a, b, r = lp.lines[i]
    d, e, s = lp.lines[j]
    tick(ops, 'determinants')
    determinant = a*e-b*d
    if not determinant:
        return rejected('PARALLEL_BASIS')
    cx, cy = OBJECTIVES[objective]
    li, lj = (cx*e-d*cy)/determinant, (a*cy-b*cx)/determinant
    tick(ops, 'dual_solves')
    tick(ops, 'dual_sign_checks', 2)
    if li < 0 or lj < 0:
        return rejected('NOT_DUAL_FEASIBLE')
    x, y = (r*e-b*s)/determinant, (a*s-r*d)/determinant
    tick(ops, 'primal_solves')
    for aa, bb, rr in lp.lines:
        tick(ops, 'primal_row_tests')
        if aa*x+bb*y > rr:
            return rejected('NOT_PRIMAL_FEASIBLE')
    tick(ops, 'dual_equalities', 2)
    tick(ops, 'gap_tests')
    value = cx*x+cy*y
    if a*li+d*lj != cx or b*li+e*lj != cy or r*li+s*lj != value:
        return rejected('CERTIFICATE_MISMATCH')
    return {'accepted': True, 'reason': 'EXACT_PRIMAL_DUAL_OPTIMUM',
            'basis': tuple(basis), 'point': (x, y), 'dual': (li, lj), 'value': value}


def clip(lp, ops):
    """Independent exact baseline: clip the initial rectangle by rows 4..7."""
    la, lb = lp.lines[1][2], lp.lines[3][2]
    polygon = [(Q(0), Q(0)), (la, Q(0)), (la, lb), (Q(0), lb)]
    for a, b, r in lp.lines[4:]:
        if not polygon:
            break
        distances = [a*x+b*y-r for x, y in polygon]
        tick(ops, 'clip_vertex_tests', len(polygon))
        output = []
        for k, current in enumerate(polygon):
            previous = polygon[k-1]
            before, after = distances[k-1], distances[k]
            if (before <= 0) != (after <= 0):
                t = before/(before-after)
                output.append(tuple(previous[j]+t*(current[j]-previous[j]) for j in (0, 1)))
                tick(ops, 'clip_intersections')
            if after <= 0:
                output.append(current)
        polygon = []
        for point in output:
            if not polygon or polygon[-1] != point:
                polygon.append(point)
        if len(polygon) > 1 and polygon[0] == polygon[-1]:
            polygon.pop()
    return polygon


def extrema(polygon, ops):
    if not polygon:
        return None
    result = {}
    for name, (cx, cy) in OBJECTIVES.items():
        tick(ops, 'objective_vertex_tests', len(polygon))
        point = max(polygon, key=lambda z: cx*z[0]+cy*z[1])
        result[name] = {'value': cx*point[0]+cy*point[1], 'point': point}
    return result


def basis_at(lp, objective, point, ops):
    """Recover advice for a future problem; all extraction work is charged."""
    active = []
    for i, (a, b, r) in enumerate(lp.lines):
        tick(ops, 'active_row_tests')
        if a*point[0]+b*point[1] == r:
            active.append(i)
    for pair in combinations(active, 2):
        cert = certify(lp, objective, pair, ops)
        if cert['accepted']:
            return cert['basis']
    raise ValueError('no nonparallel optimal basis for bounded nonempty LP')


def scan(lp, ops):
    """Nonlearning rule: fixed lexicographic basis order, dual check first."""
    answers = {}
    for objective in OBJECTIVES:
        for basis in combinations(range(8), 2):
            cert = certify(lp, objective, basis, ops)
            if cert['accepted']:
                answers[objective] = cert
                break
        if objective not in answers:
            return None
    return answers


def solve(lp, advice, ops, *, remember=False):
    """At most one proposal/objective; one shared exact fallback per problem.

    Advice values are untrusted indices. Missing/rejected advice never releases
    anything; exact clipping supplies the affected objective values instead.
    """
    if not isinstance(advice, dict) or any(k not in OBJECTIVES for k in advice):
        raise ValueError('advice must map registered objectives to index pairs')
    answers, rejected = {}, {}
    for objective in OBJECTIVES:
        if objective not in advice:
            rejected[objective] = 'NO_ADVICE'
            continue
        cert = certify(lp, objective, advice[objective], ops)
        if cert['accepted']:
            answers[objective] = {**cert, 'origin': 'VERIFIED_ADVICE'}
        else:
            rejected[objective] = cert['reason']
    if rejected:
        tick(ops, 'fallback_calls')
        polygon = clip(lp, ops)
        exact = extrema(polygon, ops)
        if exact is None:
            if answers:
                raise AssertionError('feasible certificate contradicts empty clipping result')
            return {'status': 'EMPTY_PROGRESS_POLYGON', 'answers': {}, 'rejections': rejected,
                    'is_release_authorization': False}
        for objective in rejected:
            answer = {**exact[objective], 'origin': 'EXACT_CLIP_FALLBACK', 'basis': None}
            if remember:
                answer['basis'] = basis_at(lp, objective, answer['point'], ops)
            answers[objective] = answer
    return {'status': 'EXACT_EXTREMA', 'answers': answers, 'rejections': rejected,
            'is_release_authorization': False}
