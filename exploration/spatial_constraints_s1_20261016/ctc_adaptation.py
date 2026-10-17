"""CTC-style relative-start elimination on the frozen v2 support relaxation.

Project implementation of a common-model comparator, NOT the PSIPP/CTC author
solver. The author disk kernel is only inspected and pinned. This file supplies
exact half-plane elimination for uncertain-body supports, with the same inverse
phase restrictions and frozen fallback as joint_phase.py. No release API,
controller, world, new task, or performance benchmark is invoked.
"""
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

from active_advice import ProgressLP, tick
from interface import q

BASE = Path(__file__).resolve().parent
CONTROLLER = 'ideal_feedforward_stopped_v05_a1_pivot_w05_alpha1_v2'
AUTHOR_COMMIT = '43634ec3d1d231ccfeabbefd8384273292a06e86'
AUTHOR_CACHE = Path.home()/'.cache/mapf_research/psipp-ctc-43634ec'
AUTHOR_BLOBS = {
    'src/base/geometry_2D.hpp': 'ac2d246a327bca749581cdcc8ebf1a47d608b1e2',
    'src/base/problem_with_explicit_collisions.hpp': '2d03601b7f3624d0c10337b8215f74b2a56818bf',
    'LICENSE': '1ee6653affb2f464bac57c55ab42a9846d458b16',
}
PINS = {
    'SUPPORT_CHECK.json': '2abdd3448f6820a253782b4c09a3f51a78764c1ce8bcb009112c37b671cb3b4c',
    'JOINT_PHASE_CHECK.json': 'e3b23415c067bab855db800c6367ed905131c14698bb12a77e96e7b2ff43c680',
    'composition_fixture.json': '21505bab2eceb3b86c311bf870d8c70b3c81621ff194466b3be25fc62681d68a',
    'active_advice.py': '35923de43d2e82a9bc76fec1be18776d49315b64311c1a1e93db76bb14a08455',
    'interface.py': '986aeee580e4cd724b6790c0d0b187a7901c8a6764d79c268b9a5d8fedb1e89c',
}


def project(lp, objective, operations):
    """Exact closed interval of z=u*x+v*y over a bounded progress polygon.

    Rewrite every row as e*w+d*z<=c and eliminate w by Fourier--Motzkin.
    Every lower bound on w must be <= every upper bound. No vertex enumeration
    or candidate optimizer is used. Empty and singleton projections differ.
    """
    u, v = map(q, objective)
    if not (u or v):
        raise ValueError('nonzero objective required')
    rows = [(a-b*u/v, b/v, c) if v else (b, a/u, c)
            for a, b, c in lp.lines]
    tick(operations, 'projections')
    tick(operations, 'row_transformations', len(rows))
    positive = [r for r in rows if r[0] > 0]
    negative = [r for r in rows if r[0] < 0]
    reduced = [(d, c) for e, d, c in rows if not e]
    tick(operations, 'eliminated_bound_pairs', len(positive)*len(negative))
    for ep, dp, cp in positive:
        for en, dn, cn in negative:
            reduced.append((dp*(-en)+dn*ep, cp*(-en)+cn*ep))
    lower, upper = None, None
    for d, c in reduced:
        tick(operations, 'projected_inequality_tests')
        if not d:
            if c < 0:
                return None
        elif d > 0:
            value = c/d
            upper = value if upper is None else min(upper, value)
        else:
            value = c/d
            lower = value if lower is None else max(lower, value)
    if lower is None or upper is None:
        raise ValueError('bounded progress domain lost')
    if lower > upper:
        return None

    def preimage(z):
        lo, hi = None, None
        for e, d, c in rows:
            tick(operations, 'preimage_bound_tests')
            if e > 0:
                value = (c-d*z)/e
                hi = value if hi is None else min(hi, value)
            elif e < 0:
                value = (c-d*z)/e
                lo = value if lo is None else max(lo, value)
            elif d*z > c:
                raise AssertionError('infeasible projected endpoint')
        if lo is None or hi is None or lo > hi:
            raise AssertionError('missing endpoint preimage')
        point = (lo, (z-u*lo)/v) if v else (z/u, lo)
        for a, b, c in lp.lines:
            tick(operations, 'preimage_row_tests')
            if a*point[0]+b*point[1] > c:
                raise AssertionError('preimage outside polygon')
        if u*point[0]+v*point[1] != z:
            raise AssertionError('preimage objective mismatch')
        return point

    return {'lower': lower, 'upper': upper,
            'lower_preimage': preimage(lower), 'upper_preimage': preimage(upper)}


def ctc_upper(lines, offset, *, controller, operations):
    """Adapt CTC relative-start projection to the same v2 one-sided inverse.

    Author EE intervals use s=start_A-start_B, opposite our Delta convention.
    In cruise, local s=2*(y-x); Delta=offset-s. Outside cruise, under the tested
    domain, tau_A(x)<=1/4+2*x and tau_B(y)>=1/4+2*y, so this remains an UPPER
    bound on Delta. The projected lower endpoint is not an exact physical CTC
    lower endpoint. Non-MOVE and unqualified inverse domains need old fallback.
    """
    if controller != CONTROLLER:
        raise ValueError('unqualified motion controller')
    offset = q(offset)
    lp = ProgressLP.read(lines, operations)
    la, lb = lp.lines[1][2], lp.lines[3][2]
    if not all(Q(1, 4) <= length <= 3 for length in (la, lb)):
        raise ValueError('MOVE length outside v2')
    common = {'upper': None, 'is_release_authorization': False,
              'collision_witness': False}
    x = project(lp, (1, 0), operations)
    if x is None:
        return {**common, 'status': 'EMPTY_PROGRESS_POLYGON'}
    y = project(lp, (0, 1), operations)
    if y is None:
        raise AssertionError('coordinate projections disagree on feasibility')
    tick(operations, 'inverse_domain_checks', 2)
    if x['upper'] > la-Q(1, 8) or y['lower'] < Q(1, 8):
        return {**common, 'status': 'FALLBACK_INVERSE_DOMAIN'}
    relative = project(lp, (-2, 2), operations)
    point = relative['lower_preimage']
    return {**common, 'status': 'CTC_STYLE_ONE_SIDED_UPPER',
            'upper': offset-relative['lower'], 'relative_affine_projection': relative,
            'max_a': x['upper'], 'min_b': y['lower'],
            'attained_in_progress_relaxation': Q(1, 8) <= point[0] <= la-Q(1, 8)
                and Q(1, 8) <= point[1] <= lb-Q(1, 8)}


def boundary_checks():
    """Finite algebraic counterchecks, not additional MAPF task samples."""
    square = [(-1, 0, 0), (1, 0, 1), (0, -1, 0), (0, 1, 1),
              (1, 0, 1), (0, 1, 1), (-1, 0, 0), (0, -1, 0)]
    lp = ProgressLP.read(square, {})
    a = project(lp, (-2, 2), {})
    assert (a['lower'], a['upper']) == (-2, 2)
    triangle = square.copy()
    triangle[4] = (1, 1, 1)
    b = project(ProgressLP.read(triangle, {}), (1, 1), {})
    assert (b['lower'], b['upper']) == (0, 1)
    empty = square.copy()
    empty[4] = (1, 0, -1)
    assert project(ProgressLP.read(empty, {}), (1, -1), {}) is None
    contact = square.copy()
    contact[4], contact[5] = (1, -1, 0), (-1, 1, 0)
    c = project(ProgressLP.read(contact, {}), (1, -1), {})
    assert c['lower'] == c['upper'] == 0
    assert ctc_upper(square, 0, controller=CONTROLLER, operations={})['status'] == 'FALLBACK_INVERSE_DOMAIN'
    eligible = square.copy()
    eligible[4], eligible[5] = (1, 0, Q(7, 8)), (0, -1, -Q(1, 8))
    assert ctc_upper(eligible, 3, controller=CONTROLLER, operations={})['upper'] == Q(9, 2)
    for rows, controller in ((eligible, 'changed_speed'),
                             ([tuple(float(v) for v in r) for r in eligible], CONTROLLER)):
        try:
            ctc_upper(rows, 0, controller=controller, operations={})
        except ValueError:
            pass
        else:
            raise AssertionError('unsupported input accepted')
    return ['rectangle_projection', 'coupled_triangle', 'empty_not_safe_release',
            'closed_singleton_retained', 'inverse_domain_fallback',
            'offset_and_relative_start_sign', 'changed_speed_rejected', 'float_rejected']


def frozen_audit():
    inputs = {}
    for name, expected in PINS.items():
        path = BASE/name
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != expected:
            raise ValueError('frozen input changed: '+name)
        inputs[str(path)] = digest
    support = json.loads((BASE/'SUPPORT_CHECK.json').read_text())
    joint = json.loads((BASE/'JOINT_PHASE_CHECK.json').read_text())
    for report in (support, joint):
        for name, expected in report['input_sha256'].items():
            digest = hashlib.sha256(Path(name).read_bytes()).hexdigest()
            if digest != expected:
                raise ValueError('frozen transitive input changed: '+name)
            inputs[name] = digest
    authors = []
    for name, expected in AUTHOR_BLOBS.items():
        raw = (AUTHOR_CACHE/name).read_bytes()
        actual = hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()
        if actual != expected:
            raise ValueError('author source differs from prior fixed audit: '+name)
        authors.append({'path': name, 'git_blob_sha1': actual,
                        'sha256': hashlib.sha256(raw).hexdigest(),
                        'url': 'https://raw.githubusercontent.com/omron-sinicx/PSIPP-CTC/'
                               +AUTHOR_COMMIT+'/'+name})
    fixture = json.loads((BASE/'composition_fixture.json').read_text())
    offsets = {}
    for robot, spec in fixture['robots'].items():
        offset = Q(0)
        for index, (kind, parameter) in enumerate(spec['actions']):
            offsets[robot+'_'+str(index)] = offset
            if kind == 'MOVE':
                offset += 2*q(parameter)+Q(1, 2)
            elif kind == 'TURN':
                offset += 4
            elif kind != 'HOLD':
                raise ValueError('frozen fixture action changed')
    expected = {(r['tail'], r['head']): r for r in joint['records']}
    records, operations = [], {}
    for row in support['records']:
        pair = (row['tail'], row['head'])
        result = {'status': 'FALLBACK_NON_MOVE', 'upper': None}
        geometry = row['pair_analytic']
        if 'lines' in geometry:
            result = ctc_upper(geometry['lines'], offsets[pair[0]]-offsets[pair[1]],
                               controller=CONTROLLER, operations=operations)
        # Inputs to this algorithm are coefficients and old fallback only.
        # Candidate records and vertices are used solely as independent checks.
        prior = q(row['pair_refined_upper'])
        upper = prior if result['upper'] is None else min(prior, result['upper'])
        candidate = expected[pair]
        assert upper == q(candidate['refined_upper'])
        if result['upper'] is not None:
            assert result['upper'] == q(candidate['joint']['upper'])
            assert result['attained_in_progress_relaxation']
            vertices = [tuple(map(q, p)) for p in geometry['vertices']]
            projected = result['relative_affine_projection']
            assert projected['lower'] == min(2*(y-x) for x, y in vertices)
            assert projected['upper'] == max(2*(y-x) for x, y in vertices)
        else:
            assert result['status'] == candidate['joint']['status']
        records.append({'tail': pair[0], 'head': pair[1], 'adaptation': result,
                        'shared_fallback_upper': prior, 'adapted_upper': upper,
                        'candidate_upper': q(candidate['refined_upper']), 'equal': True})
    assert len(records) == 11 and len(expected) == 11
    original_order = Q('4.5')-Q('6.06')
    ordered = max(original_order, *(r['adapted_upper'] for r in records))
    assert ordered == q(joint['joint_ordered_upper'])
    assert sum(r['adaptation']['upper'] is not None for r in records) == 2
    inputs[str(Path(__file__).resolve())] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    return {
        'status': 'FIXED_CTC_ADAPTATION_STATIC_PASS', 'records': records,
        'scope': 'right-hand ordered safe ray on frozen C1 supports, not full exact forbidden sets',
        'method_identity': 'project CTC-style half-plane adaptation, not original author execution',
        'author_sources': authors, 'author_commit': AUTHOR_COMMIT, 'author_license': 'MIT',
        'boundary_checks': boundary_checks(), 'adaptation_operations': operations,
        'candidate_operations_reused': joint['operations'],
        'original_order_lower': original_order, 'ordered_upper': ordered,
        'all_eleven_bounds_equal': True, 'source_supports_and_fallback_shared': True,
        'shared_fallback_pairs': 9, 'independent_projection_pairs': 2,
        'whole_task_cost': 'NOT_MEASURED', 'cost_advantage': 'NOT_ESTABLISHED',
        'extra_guarantee': 'NONE_ESTABLISHED_UNDER_COMMON_CONDITIONS',
        'feedback_release': 'prior fixed-message negative results reused, no session called',
        'is_release_authorization': False, 'independent_scientific_validation': False,
        'remaining_external_gap': 'full original-system execution and general robust constructor comparison',
        'decision': 'STOP_JOINT_AFFINE_PROJECTION_AS_INDEPENDENT_TIGHTNESS_CONTRIBUTION',
        'successor_run_plan_prepared': False, 'scientific_runs': 0,
        'author_code_calls': 0, 'task_session_calls': 0, 'training_runs': 0,
        'input_sha256': inputs,
    }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    output = BASE/'CTC_ADAPTATION_CHECK.json'
    # Refuse before computation, including when a prior attempt failed.
    if args.write_result and output.exists():
        raise FileExistsError('preserve existing receipt: '+str(output))
    try:
        result = frozen_audit()
    except Exception as exc:
        if args.write_result:
            with output.open('x') as f:
                json.dump({'status': 'FIXED_CTC_ADAPTATION_STATIC_FAILED',
                           'error': type(exc).__name__, 'detail': str(exc)}, f)
                f.write('\n')
        raise
    if args.write_result:
        with output.open('x') as f:
            json.dump(result, f, default=str, sort_keys=True, indent=2)
            f.write('\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('records', 'input_sha256', 'author_sources')}, default=str))
