"""Joint phase upper bound on frozen progress polygons; no release authority.

Exploratory analytical comparator for the declared v2 stopped trapezoid only.
The command-line entry reads frozen coefficients, never constructs trajectories
or invokes controllers. It preserves failures and refuses receipt overwrite.
"""
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

from active_advice import ProgressLP, clip, extrema, tick
from interface import q

CONTROLLER = 'ideal_feedforward_stopped_v05_a1_pivot_w05_alpha1_v2'
BASE = Path(__file__).resolve().parent


def joint_upper(lines, offset, *, controller, operations):
    """Bound offset + tau_A(x) - tau_B(y) on the SAME progress polygon.

    tau_A(x) <= 1/4+2x when x <= L_A-1/8 (accel or cruise).
    tau_B(y) >= 1/4+2y when y >= 1/8 (cruise or brake).
    Thus the joint linear objective is an upper bound throughout the polygon,
    even when some points are not in cruise. Otherwise return explicit fallback.
    Empty polygon is geometric separation under the caller's support contract,
    never a claim that all task arrangements are infeasible.
    """
    if controller != CONTROLLER:
        raise ValueError('unqualified speed/acceleration/controller')
    offset = q(offset)
    lp = ProgressLP.read(lines, operations)
    la, lb = lp.lines[1][2], lp.lines[3][2]
    if not all(Q(1, 4) <= length <= 3 for length in (la, lb)):
        raise ValueError('length outside v2 MOVE domain')
    polygon = clip(lp, operations)
    common = {'is_release_authorization': False, 'upper': None}
    extremes = extrema(polygon, operations)
    if extremes is None:
        return {**common, 'status': 'EMPTY_PROGRESS_POLYGON'}
    max_a, min_b = extremes['max_A']['value'], -extremes['min_B']['value']
    eligibility = {'max_a': max_a, 'min_b': min_b,
                   'A_excludes_braking': max_a <= la-Q(1, 8),
                   'B_excludes_acceleration': min_b >= Q(1, 8)}
    tick(operations, 'inverse_domain_checks', 2)
    if not eligibility['A_excludes_braking'] or not eligibility['B_excludes_acceleration']:
        return {**common, 'status': 'FALLBACK_INVERSE_DOMAIN', **eligibility}
    tick(operations, 'joint_objective_vertex_tests', len(polygon))
    point = max(polygon, key=lambda z: z[0]-z[1])
    value = point[0]-point[1]
    attained = Q(1, 8) <= point[0] and point[1] <= lb-Q(1, 8)
    return {**common, **eligibility, 'status': 'JOINT_ONE_SIDED_INVERSE_BOUND',
            'upper': offset+2*value, 'maximizer': point,
            'linear_max': value, 'attained_in_progress_relaxation': attained,
            'collision_witness': False}


def frozen_audit():
    """One fixed algebraic audit, with existing cases and domain counterexamples."""
    path = BASE/'SUPPORT_CHECK.json'
    support = json.loads(path.read_text())
    for name, digest in support['input_sha256'].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest() != digest:
            raise ValueError('frozen support input changed: '+name)
    fixture_path = BASE/'composition_fixture.json'
    fixture = json.loads(fixture_path.read_text())
    offsets = {}
    for robot, spec in fixture['robots'].items():
        phase = Q(0)
        for i, (kind, parameter) in enumerate(spec['actions']):
            offsets[robot+'_'+str(i)] = phase
            if kind == 'MOVE':
                phase += 2*q(parameter)+Q(1, 2)
            elif kind == 'TURN':
                phase += 4
            elif kind != 'HOLD':
                raise ValueError('fixture changed: unsupported action')
    records, operations = [], {}
    for row in support['records']:
        prior = row['pair_analytic']
        pair = (row['tail'], row['head'])
        result = {'status': 'FALLBACK_NON_MOVE', 'upper': None}
        if 'lines' in prior:
            offset = offsets[pair[0]]-offsets[pair[1]]
            result = joint_upper(prior['lines'], offset, controller=CONTROLLER, operations=operations)
            vertices = [tuple(map(q, p)) for p in prior['vertices']]
            if result['upper'] is not None:
                assert result['linear_max'] == max(x-y for x, y in vertices)
                assert result['upper'] <= q(prior['upper'])
                assert result['attained_in_progress_relaxation']
        refined = q(row['pair_refined_upper'])
        if result['upper'] is not None:
            refined = min(refined, result['upper'])
        records.append({'tail': pair[0], 'head': pair[1], 'joint': result,
                        'previous_upper': row['pair_refined_upper'], 'refined_upper': refined})
    # Necessary counterchecks of the one-sided proof, not new MAPF scenarios.
    square = [(-1, 0, 0), (1, 0, 1), (0, -1, 0), (0, 1, 1),
              (1, 0, 1), (0, 1, 1), (-1, 0, 0), (0, -1, 0)]
    assert joint_upper(square, 0, controller=CONTROLLER, operations={})['status'] == 'FALLBACK_INVERSE_DOMAIN'
    permitted = square.copy()
    permitted[4], permitted[5] = (1, 0, Q(7, 8)), (0, -1, Q(-1, 8))
    bound = joint_upper(permitted, 0, controller=CONTROLLER, operations={})
    assert bound['upper'] == Q(3, 2) and not bound['is_release_authorization']
    empty = square.copy()
    empty[4] = (1, 0, -1)
    assert joint_upper(empty, 0, controller=CONTROLLER, operations={})['status'] == 'EMPTY_PROGRESS_POLYGON'
    try:
        joint_upper(permitted, 0, controller='changed_speed', operations={})
    except ValueError:
        pass
    else:
        raise AssertionError('changed controller accepted')
    # At A's brake endpoint and B's accel origin, the affine substitution fails:
    # tau_A(1)=5/2 > 9/4, tau_B(0)=0 < 1/4. Domain fallback is indispensable.
    assert Q(5, 2) > Q(1, 4)+2 and 0 < Q(1, 4)
    old = q(support['ordered_upper_bounds']['pair_analytic'])
    original_order = Q('4.5')-Q('6.06')
    upper = max(original_order, *(r['refined_upper'] for r in records))
    assert len(records) == 11 and upper < old
    tightened = [r for r in records if r['refined_upper'] < q(r['previous_upper'])]
    assert [(r['tail'], r['head']) for r in tightened] == [('A_0', 'B_0'), ('A_2', 'B_2')]
    t = json.loads((BASE/'TIMED_CHECK.json').read_text())
    public = t['fixed_public_sessions']
    assert all(q(s['initial_wait']['B']) == Q('9.45') for s in public)
    # This is a slack diagnostic at the EXISTING delivery; never retroactive dispatch.
    config = json.loads((BASE/'timed_fixture.json').read_text())
    capture = q(config['static_progress_capture'])
    start = q(public[0]['initial_wait']['A'])
    phase_lo = capture-start-q(config['phase_half_width'])
    feedback_anchor_upper = capture-phase_lo
    deadline_bound = feedback_anchor_upper+upper+Q('0.000001')
    assert deadline_bound < Q('9.45')
    paths = [Path(__file__), BASE/'active_advice.py', BASE/'interface.py', path,
             fixture_path, BASE/'TIMED_CHECK.json', BASE/'timed_fixture.json', BASE/'verify_timed.py']
    return {'status': 'FIXED_JOINT_PHASE_AUDIT_PASS', 'records': records,
            'operations': operations, 'old_ordered_upper': old, 'joint_ordered_upper': upper,
            'tightening_seconds': old-upper, 'original_order_lower': original_order,
            'bound_at_existing_delivery': deadline_bound, 'existing_delivery': '9.45',
            'anchor_basis': 'algebraic reconstruction of frozen message fixture; not a replayed packet',
            'fixed_public_outcomes_reused': public,
            'independent_task_evidence': False, 'feedback_update_implemented': False,
            'external_baseline_advantage': 'UNKNOWN', 'whole_cost_advantage': 'UNKNOWN',
            'runtime_integration': False, 'new_release_benefit': False,
            'scientific_runs': 0, 'training': 0, 'world_steps': 0, 'task_session_calls': 0,
            'input_sha256': {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    try:
        result = frozen_audit()
    except Exception as exc:
        result = {'status': 'FIXED_JOINT_PHASE_AUDIT_FAILED', 'error': type(exc).__name__, 'detail': str(exc)}
        if args.write_result:
            with (BASE/'JOINT_PHASE_CHECK.json').open('x') as f:
                json.dump(result, f, default=str, sort_keys=True)
                f.write('\n')
        raise
    if args.write_result:
        with (BASE/'JOINT_PHASE_CHECK.json').open('x') as f:
            json.dump(result, f, default=str, sort_keys=True)
            f.write('\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('records', 'fixed_public_outcomes_reused', 'input_sha256')}, default=str))
