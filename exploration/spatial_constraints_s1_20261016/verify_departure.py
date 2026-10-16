"""Fixed analytic projection checks; no task session, plant or world calls."""
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

from interface import Box
from departure_constraints import relative_hull, union_closed, ProjectionBudget
from run_timed import BASE, HOME, inputs, verify_inputs, dump
from verify_qualified import verify_qualification_pins
from verify_integration import module


def check():
    checks = []

    def need(value, name):
        if not value:
            raise AssertionError(name)
        checks.append(name)

    def fails(call, error, name):
        try:
            call()
        except error:
            checks.append(name)
        else:
            raise AssertionError(name)

    # Independent finite leaf-grid enumeration; no tree traversal reused.
    def oracle(a, b):
        possible = []
        for i in range(4):
            for j in range(4):
                lo, hi, low, high = Q(i, 4), Q(i+1, 4), Q(j, 4), Q(j+1, 4)
                if not a(lo, hi).separated(b(low, high)):
                    possible.append((lo-high, hi-low))
        return None if not possible else (min(x[0] for x in possible), max(x[1] for x in possible))

    point = lambda lo, hi: Box(Q(0), Q(0), Q(0), Q(0))
    far = lambda lo, hi: Box(Q(2), Q(2), Q(0), Q(0))
    line = lambda lo, hi: Box(lo, hi, Q(0), Q(0))
    shifted = lambda lo, hi: Box(lo+1, hi+1, Q(0), Q(0))

    def parabola(lo, hi):
        a, b = lo*(1-lo), hi*(1-hi)
        return Box(min(a, b), Q(1, 4) if lo <= Q(1, 2) <= hi else max(a, b), Q(0), Q(0))

    level = lambda lo, hi: Box(Q(1, 8), Q(1, 8), Q(0), Q(0))
    for name, a, b in [('all_possible', point, point), ('empty', point, far),
                       ('contact_and_sign', line, shifted), ('nonmonotone', parabola, level)]:
        result = relative_hull((0, 1), (0, 1), a, b, resolution=Q(1, 4), max_cells=31)
        need(result['window'] == oracle(a, b), name+'_matches_independent_grid')
        need(not result['overlap_is_collision'], name+'_not_collision_claim')
    exact = relative_hull((2, 2), (0, 0), point, point, resolution=1, max_cells=1)
    need(exact['window'] == (2, 2), 'relative_start_sign_and_zero_width_domain')
    need(union_closed([(0, 1), (1, 2), (3, 4)]) == ((0, 2), (3, 4)),
         'closed_contact_merged_but_gap_retained')
    fails(lambda: relative_hull((0, 1), (0, 1), point, point, resolution=Q(1, 4), max_cells=1),
          ProjectionBudget, 'no_partial_output_at_budget')
    fails(lambda: relative_hull((0., 1), (0, 1), point, point, resolution=1, max_cells=2),
          ValueError, 'no_inexact_domains')

    pins = {'frozen': verify_inputs(), 'qualification': verify_qualification_pins()}
    source = HOME/'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source'
    module('composition', source/'composition.py')
    module('timed', source/'timed.py')
    module('composition_constraints', BASE/'composition_constraints.py')
    constraints = module('timed_constraints', BASE/'timed_constraints.py')
    base, config = inputs()
    problem = constraints.make_problem(base, config, 2)
    frozen = json.loads((BASE/'TIMED_CHECK.json').read_text())
    previous = {(e['tail'], e['head']): Q(e['exit'])-Q(e['entry'])
                for e in frozen['constructed_constraints'] if e['kind'] == 'SPATIAL_PASSAGE'}
    pairs = problem['graph']['new_or_retained']
    need(len(pairs) == len(previous) == 11, 'same_eleven_frozen_action_pairs')
    # This eligibility is the reason finite phase domains cover all collisions
    # in THIS fixture: starts/terminal holds are globally separated already.
    for name, box in problem['boxes'].items():
        if name in problem['finite']:
            continue
        for other, obox in problem['boxes'].items():
            if name.split('_')[0] != other.split('_')[0]:
                need(box.separated(obox), 'permanent_or_initial_wait_clear_'+name+'_'+other)
    records = []
    for tail, head in pairs:
        ra, ia = problem['finite'][tail]
        rb, ib = problem['finite'][head]
        need((ra, rb) == ('A', 'B'), 'frozen_serial_direction_'+tail+'_'+head)
        ta, tb = problem['trajectories'][ra], problem['trajectories'][rb]
        result = relative_hull(problem['intervals'][tail], problem['intervals'][head],
                               lambda lo, hi: Box(*ta.action_box(ia, lo, hi)),
                               lambda lo, hi: Box(*tb.action_box(ib, lo, hi)),
                               resolution=Q(config['phase_resolution']),
                               max_cells=config['certificate_max_cells'])
        window = result['window']
        need(window is None or window[1] <= previous[tail, head],
             'no_larger_ordered_upper_'+tail+'_'+head)
        records.append({'tail': tail, 'head': head, **result,
                        'old_ordered_upper': previous[tail, head],
                        'upper_reduction': None if window is None else previous[tail, head]-window[1]})
    merged = union_closed(r['window'] for r in records if r['window'] is not None)
    old_upper = max(previous.values())
    new_upper = max(hi for lo, hi in merged)
    original_lower = max(Q(e['exit'])-Q(e['entry']) for e in frozen['constructed_constraints']
                         if e['kind'] == 'EXISTING_ORDER')
    witness = (new_upper+old_upper)/2 if new_upper < old_upper else None
    if witness is not None:
        need(new_upper < witness < old_upper and witness > original_lower,
             'strict_geometry_only_schedule_preserves_original_END_order')
    # Existing late feedback only, without manufacturing a new earlier packet.
    delta_now = (Q('9.45')-Q('.105'), Q('9.45')-Q('.095'))
    need(delta_now[0] > max(new_upper, old_upper), 'existing_9_45_feedback_still_no_release_difference')
    aggregate = {key: sum(r['operations'][key] for r in records)
                 for key in records[0]['operations'] if key != 'max_heap'}
    aggregate['max_heap_per_pair'] = max(r['operations']['max_heap'] for r in records)
    sources = [BASE/n for n in ('composition_fixture.json', 'timed_fixture.json', 'TIMED_CHECK.json',
                               'QUALIFICATION_CHECK.json', 'departure_constraints.py', 'verify_departure.py')]
    sources += [source/'composition.py', source/'timed.py']
    return {'status': 'STATIC_PROJECTION_CHECK_PASS', 'scope': 'fixed C1 analytic geometry; no autonomous task',
            'checks': checks, 'records': records, 'forbidden_outer_union': merged,
            'old_ordered_upper': old_upper, 'new_ordered_upper': new_upper,
            'upper_reduction': old_upper-new_upper, 'original_END_order_lower': original_lower,
            'geometry_only_relative_start_witness': witness,
            'witness_is_public_feedback_release': False,
            'same_9_45_fixed_feedback_release': True,
            'operations': aggregate, 'old_endpoint_box_evaluations': 446,
            'whole_process_cost_advantage': 'UNKNOWN_NOT_BENCHMARKED',
            'external_baseline_advantage': 'NOT_ESTABLISHED_CTC_STYLE_ADAPTATION',
            'successor_run_gate': 'NOT_PASSED', 'input_pins_reused': pins,
            'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
            'scientific_runs': 0, 'world_steps': 0, 'training': 0, 'task_session_calls': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    try:
        receipt = check()
    except Exception as exc:
        receipt = {'status': 'STATIC_PROJECTION_CHECK_FAILED', 'error': type(exc).__name__,
                   'detail': str(exc), 'scientific_runs': 0, 'task_session_calls': 0}
        if isinstance(exc, ProjectionBudget):
            receipt['operations'] = exc.operations
        if args.write_result:
            with (BASE/'DEPARTURE_CHECK.json').open('x') as f:
                f.write(dump(receipt)+'\n')
        print(dump(receipt))
        raise
    if args.write_result:
        with (BASE/'DEPARTURE_CHECK.json').open('x') as f:
            f.write(dump(receipt)+'\n')
    print(dump({k: v for k, v in receipt.items() if k not in ('records', 'checks', 'input_sha256')}))
