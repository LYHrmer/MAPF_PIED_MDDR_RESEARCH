"""Fixed certificate preflight using only frozen coefficients; no learning run."""
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

from active_advice import ProgressLP, OBJECTIVES, certify, clip, extrema, basis_at, scan, solve, tick

BASE = Path(__file__).resolve().parent


def wire(value):
    return json.dumps(value, sort_keys=True, default=str, separators=(',', ':'))


def check():
    checks = []

    def need(condition, name):
        if not condition:
            raise AssertionError(name)
        checks.append(name)

    def fails(call, name):
        try:
            call()
        except ValueError:
            checks.append(name)
        else:
            raise AssertionError(name)

    receipt_path = BASE/'SUPPORT_CHECK.json'
    previous = json.loads(receipt_path.read_text())
    for path, digest in previous['input_sha256'].items():
        need(hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest,
             'frozen_support_input_unchanged_'+path)
    records = [r for r in previous['records'] if 'lines' in r['pair_analytic']]
    need(len(records) == 5, 'only_five_frozen_MOVE_polygons')

    # Fixed algebraic unit inputs, not new trajectories or statistical samples.
    square = [(-1, 0, 0), (1, 0, 1), (0, -1, 0), (0, 1, 1),
              (1, 0, 1), (0, 1, 1), (-1, 0, 0), (0, -1, 0)]
    unit = ProgressLP.read(square, {})
    need(certify(unit, 'max_A', (1, 3), {})['accepted'], 'exact_square_certificate')
    need(certify(unit, 'max_A', (0, 2), {})['reason'] == 'NOT_DUAL_FEASIBLE',
         'feasible_but_nonoptimal_point_rejected')
    need(certify(unit, 'max_A', (0, 1), {})['reason'] == 'PARALLEL_BASIS', 'parallel_advice_rejected')
    for malformed in [None, (1,), (1, 1), (-1, 3), (1, 8), (True, 3), (1., 3), '13']:
        need(not certify(unit, 'max_A', malformed, {})['accepted'], 'malformed_advice_'+repr(malformed))
    changed = list(square)
    changed[4] = (1, 0, Q(1, 2))
    stale = ProgressLP.read(changed, {})
    need(certify(stale, 'max_A', (1, 3), {})['reason'] == 'NOT_PRIMAL_FEASIBLE',
         'old_basis_recomputed_against_changed_coefficients')
    repaired = solve(stale, {'max_A': (1, 3), 'min_B': (0, 1)}, {})
    need(repaired['answers']['max_A']['value'] == Q(1, 2)
         and repaired['answers']['min_B']['value'] == 0, 'invalid_advice_exact_fallback')
    need(not repaired['is_release_authorization'], 'LP_certificate_never_releases_robot')
    empty_rows = list(square)
    empty_rows[4] = (1, 0, -1)
    empty = solve(ProgressLP.read(empty_rows, {}), {}, {})
    need(empty['status'] == 'EMPTY_PROGRESS_POLYGON', 'empty_progress_arrangement_reported')
    point_rows = list(square)
    point_rows[4], point_rows[5] = (1, 0, 0), (0, 1, 0)
    point = solve(ProgressLP.read(point_rows, {}), {}, {}, remember=True)
    need(all(a['value'] == 0 and a['basis'] is not None for a in point['answers'].values()),
         'degenerate_point_has_exact_extrema_and_certificate')
    inexact = list(square)
    inexact[4] = (1, 0, 1.)
    fails(lambda: ProgressLP.read(inexact, {}), 'floating_coefficients_rejected')
    fails(lambda: ProgressLP(tuple(square)), 'constructor_cannot_bypass_exact_contract')
    fails(lambda: solve(unit, {'predicted_release_time': 0}, {}), 'answer_or_release_not_an_advice_field')

    names = ('rectangle_clip', 'dual_first_scan', 'previous_basis', 'perfect_advice')
    costs = {name: {} for name in names}
    teacher_costs, prior_basis, results = {}, {}, []
    for row in records:
        frozen = row['pair_analytic']
        vertices = [tuple(map(Q, z)) for z in frozen['vertices']]
        expected = {'max_A': Q(frozen['max_a']), 'min_B': -Q(frozen['min_b'])}
        label_lp = ProgressLP.read(frozen['lines'], teacher_costs)
        labels = {}
        for objective, c in OBJECTIVES.items():
            point = max(vertices, key=lambda z: c[0]*z[0]+c[1]*z[1])
            labels[objective] = basis_at(label_lp, objective, point, teacher_costs)
        outputs = {}
        for method in names:
            ops = costs[method]
            lp = ProgressLP.read(frozen['lines'], ops)
            if method == 'rectangle_clip':
                answer = extrema(clip(lp, ops), ops)
                outputs[method] = {'values': {k: v['value'] for k, v in answer.items()}}
            elif method == 'dual_first_scan':
                answer = scan(lp, ops)
                outputs[method] = {'values': {k: v['value'] for k, v in answer.items()}}
            else:
                if method == 'previous_basis':
                    tick(ops, 'cache_lookups', 2)
                    suggestions = dict(prior_basis)
                else:
                    suggestions = labels  # diagnostic perfect advice, no learned model
                answer = solve(lp, suggestions, ops, remember=(method == 'previous_basis'))
                need(answer['status'] == 'EXACT_EXTREMA', 'bounded_frozen_problem_solved_'+method+row['tail']+row['head'])
                outputs[method] = {'values': {k: v['value'] for k, v in answer['answers'].items()},
                                   'origins': {k: v['origin'] for k, v in answer['answers'].items()},
                                   'rejections': answer['rejections']}
                if method == 'previous_basis':
                    prior_basis = {k: v['basis'] for k, v in answer['answers'].items()}
                    tick(ops, 'cache_stores', 2)
            need(outputs[method]['values'] == expected, 'exact_frozen_values_'+method+row['tail']+row['head'])
        results.append({'tail': row['tail'], 'head': row['head'], 'perfect_labels': labels,
                        'expected': expected, 'methods': outputs,
                        'original_inverse_status': frozen['status']})
    need(costs['perfect_advice'].get('fallback_calls', 0) == 0, 'perfect_advice_all_ten_certified')
    old_operations = {}
    for row in records:
        for key, value in row['pair_analytic']['operations'].items():
            old_operations[key] = old_operations.get(key, 0)+value
    hits = sum(origin == 'VERIFIED_ADVICE' for row in results
               for origin in row['methods']['previous_basis']['origins'].values())
    paths = [BASE/n for n in ('active_advice.py', 'verify_advice.py', 'SUPPORT_CHECK.json', 'interface.py')]
    return {'status': 'STATIC_ADVICE_CHECK_PASS', 'checks': checks, 'records': results,
            'operations': costs, 'frozen_vertex_enumeration_operations': old_operations,
            'perfect_label_extraction_operations_excluded_from_oracle': teacher_costs,
            'previous_basis_verified_hits_of_ten': hits,
            'all_ten_objective_values_equal': True,
            'source_support_and_legacy_fallback_work_unchanged': True,
            'network_inference_cost_assumed_zero_only_for_oracle': True,
            'no_claim_of_wall_CPU_speedup': True, 'training_gate': 'NOT_PASSED',
            'gate_reason': 'NO_COMPLETE_COST_OR_EXTERNAL_BASELINE_ADVANTAGE_EVIDENCE',
            'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'scientific_runs': 0, 'world_steps': 0, 'training': 0, 'task_session_calls': 0,
            'new_geometry_constructions': 0, 'new_task_samples': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    try:
        receipt = check()
    except Exception as exc:
        receipt = {'status': 'STATIC_ADVICE_CHECK_FAILED', 'error': type(exc).__name__,
                   'detail': str(exc), 'scientific_runs': 0, 'training': 0}
        if args.write_result:
            with (BASE/'ADVICE_CHECK.json').open('x') as f:
                f.write(wire(receipt)+'\n')
        print(wire(receipt))
        raise
    if args.write_result:
        with (BASE/'ADVICE_CHECK.json').open('x') as f:
            f.write(wire(receipt)+'\n')
    print(wire({k: v for k, v in receipt.items() if k not in ('checks', 'records', 'input_sha256')}))
