"""Fixed C1 public-history mechanism diagnostic, never a launch API.

No source.sample, Plant, task session, author solver, new world, or training.
All original C1 evidence and source/protocol files remain frozen.
"""
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path
import sys
from copy import deepcopy
from dataclasses import replace

BASE = Path(__file__).resolve().parent
HOME = BASE.parents[2]
SOURCE = HOME/'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source'
TOOLS = HOME/'MAPF_QUERY_VALUE_FEASIBILITY/exploration/execution_feedback'
sys.path[:0] = [str(SOURCE), str(TOOLS)]

from interface import Box
from history_replay import recover_c1
from initial_pose_history import validate_c1, project_c1, intersect_x, propagate_translation_x, PRIOR_X


def check_frozen_inputs():
    anchors = {'COMPOSITION_CHECK.json': '3f90cdce55e24fb39ab6e9f177f55701c04cb933ed51182e0ae5dd8c9a30c2df',
               'COMPOSITION_MANIFEST.json': '0a597e5df118f2d8846fe918f9f4e18e0d7eaa17da6a805308128ffd2f038a99'}
    for name, digest in anchors.items():
        if hashlib.sha256((BASE/name).read_bytes()).hexdigest() != digest:
            raise ValueError('frozen C1 evidence changed: '+name)
    manifest = json.loads((BASE/'COMPOSITION_MANIFEST.json').read_text())
    for group, root in (('execution', BASE), ('source', SOURCE)):
        for name, digest in manifest['files'][group].items():
            if hashlib.sha256((root/name).read_bytes()).hexdigest() != digest:
                raise ValueError('frozen source/geometry input changed: '+name)


def suffix_diagnostic(boxes, progress_lower, bx):
    """Use the old C1 continuous enclosures, altering ONLY certified b_x.

    A's fixed suffix is A_2 northbound to y=1 and permanent A_3 HOLD. The
    current progress lower bound is the original legal y-bound expression.
    Every B box, including start wait and permanent goal, is checked.
    Scope validation and legal receiver admission are mandatory at the caller.
    """
    if not Q(0) <= progress_lower <= 1:
        raise ValueError('C1 northbound progress only')
    future = {}
    for name in ('A_2', 'A_3'):
        raw = tuple(Q(boxes[name][k]) for k in ('xmin', 'xmax', 'ymin', 'ymax'))
        if name == 'A_2':
            raw = (raw[0], raw[1], raw[2]+progress_lower, raw[3])
        future[name] = Box(*propagate_translation_x(raw, bx))
    others = {name: Box(*(Q(raw[k]) for k in ('xmin', 'xmax', 'ymin', 'ymax')))
              for name, raw in boxes.items() if name.startswith('B_')}
    blocking = [(a, b) for a, box in future.items() for b, other in others.items()
                if not box.separated(other)]
    return {'full_suffix_separated': not blocking, 'unresolved_pairs': blocking,
            'box_pair_checks': len(future)*len(others),
            'posterior_body_boxes': {name: [getattr(box, k) for k in ('xmin', 'xmax', 'ymin', 'ymax')]
                                     for name, box in future.items()},
            'overlap_is_collision': False, 'is_release_authorization': False}


def compare_existing_history():
    check_frozen_inputs()
    fixture = json.loads((BASE/'composition_fixture.json').read_text())
    evidence = json.loads((BASE/'COMPOSITION_CHECK.json').read_text())
    validate_c1(fixture, evidence['source_contract'])
    packets, replay = recover_c1(fixture, evidence)
    history = PRIOR_X
    results = []
    for packet, previous in zip(packets, evidence['decisions']):
        projected = project_c1(packet)
        history = intersect_x(history, projected['bx'])
        modes = {'prior': PRIOR_X, 'latest_packet': projected['bx'], 'history_intersection': history}
        comparisons = {mode: suffix_diagnostic(evidence['occupancy_boxes'], projected['reference_r'][0], bx)
                       for mode, bx in modes.items()}
        if comparisons['prior']['full_suffix_separated'] != previous['guard']['accepted']:
            raise AssertionError('frozen suffix representation changed')
        results.append({'capture': packet.capture, 'delivery': packet.delivery,
                        'single_packet_projection': projected, 'history_bx': history, 'comparisons': comparisons,
                        'frozen_SADG_decision': previous['adapted_SADG_can_start_B']})
    return {'status': 'C1_HISTORY_SUFFIX_DIAGNOSTIC', 'replay': replay, 'records': results,
            'new_source_captures': 0, 'task_session_calls': 0, 'world_runs': 0, 'training': 0}


def update_baselines(result):
    """Strong simple comparator: two scalar prefix bounds, not full replay.

    Replaying a prefix is only an independent equality check. Both proposed
    history and the strong comparator get the same sufficient statistic.
    """
    intervals, incremental = [], PRIOR_X
    replay_visits, incremental_updates = 0, 0
    records, previous_boxes, previous_safe = [], None, False
    reusable_true_certificates = 0
    for row in result['records']:
        interval = tuple(map(Q, row['single_packet_projection']['bx']))
        intervals.append(interval)
        incremental = intersect_x(incremental, interval)
        incremental_updates += 1
        replayed = PRIOR_X
        for value in intervals:
            replayed = intersect_x(replayed, value)
            replay_visits += 1
        assert replayed == incremental == tuple(map(Q, row['history_bx']))
        current = row['comparisons']['history_intersection']
        boxes = {name: tuple(map(Q, values)) for name, values in current['posterior_body_boxes'].items()}
        nested = previous_boxes is not None and set(boxes) == set(previous_boxes) and all(
            previous_boxes[n][0] <= b[0] <= b[1] <= previous_boxes[n][1]
            and previous_boxes[n][2] <= b[2] <= b[3] <= previous_boxes[n][3] for n, b in boxes.items())
        # With identical B, source, order, controller and scope, a VERIFIED
        # positive certificate may survive this inclusion. False/unresolved
        # never proves a smaller occupancy unsafe, so cannot block forever.
        reusable = previous_safe and nested
        reusable_true_certificates += bool(reusable)
        records.append({'delivery': row['delivery'], 'strong_prefix_interval': incremental,
                        'same_as_full_replay': replayed == incremental,
                        'future_boxes_subset_previous': nested,
                        'positive_certificate_reuse_possible': bool(reusable),
                        'negative_cache_reuse_allowed': False})
        previous_boxes, previous_safe = boxes, current['full_suffix_separated']
    return {'records': records, 'projection_evaluations_with_reuse': len(intervals),
            'diagnostic_full_prefix_interval_visits': replay_visits,
            'strong_simple_incremental_updates': incremental_updates,
            'candidate_incremental_updates': incremental_updates,
            'interval_scalar_storage': 2,
            'positive_certificate_reuse_opportunities': reusable_true_certificates,
            'candidate_advantage_over_strong_simple_update': False,
            'box_pair_checks_per_method': sum(r['comparisons']['prior']['box_pair_checks'] for r in result['records']),
            'missing_complete_task_cost': ['controller_and_source', 'B_feedback', 'both_final_ENDs',
                                           'full_execution_checks', 'process_wall_CPU_memory_and_final_IO'],
            'total_runtime_advantage': 'UNKNOWN'}


def boundary_audit():
    from history_replay import require_task_phase
    from protocol import Inbox
    fixture = json.loads((BASE/'composition_fixture.json').read_text())
    evidence = json.loads((BASE/'COMPOSITION_CHECK.json').read_text())
    packets, _ = recover_c1(fixture, evidence)
    packet = packets[0]
    rejected = []

    def reject(fn, reason):
        try:
            fn()
        except ValueError:
            rejected.append(reason)
        else:
            raise AssertionError('accepted invalid input: '+reason)

    wrong = deepcopy(evidence)
    wrong['same_information']['wire_sha256'] = '0'*64
    reject(lambda: recover_c1(fixture, wrong), 'wrong_public_digest')
    changed = deepcopy(fixture)
    changed['robots']['A']['actions'][-1:] = [['TURN', 1], ['TURN', 1], ['MOVE', '1'], ['HOLD', '0']]
    reject(lambda: recover_c1(changed, evidence), 'future_reentry_changes_whole_commitment')
    changed_b = deepcopy(fixture)
    changed_b['robots']['B']['actions'][0][1] = '1'
    reject(lambda: recover_c1(changed_b, evidence), 'B_path_not_part_of_frozen_problem')
    changed_contract = deepcopy(evidence['source_contract'])
    changed_contract['speed'] = '.6'
    reject(lambda: validate_c1(fixture, changed_contract), 'changed_speed_model')
    changed_fields = deepcopy(fixture)
    changed_fields['public_progress'][0]['pose_true'] = [0, 0, 0]
    reject(lambda: recover_c1(changed_fields, evidence), 'private_state_in_public_fixture')
    reject(lambda: require_task_phase(packet), 'C1_not_T1_phase_feedback')
    reject(lambda: Inbox(packet.binding).admit(packet, now=packet.capture), 'undelivered_message')
    reject(lambda: Inbox(packet.binding).admit(replace(packet, binding=replace(packet.binding, robot='B')),
                                              now=packet.delivery), 'foreign_binding')
    inbox = Inbox(packet.binding)
    inbox.admit(packet, now=packet.delivery)
    reject(lambda: inbox.admit(packet, now=packet.delivery), 'replayed_sequence')
    reject(lambda: project_c1(replace(packet, kind='END')), 'END_not_progress_projection')
    reject(lambda: project_c1(replace(packet, localization_bound='.001')), 'unqualified_smaller_localization_bound')
    reject(lambda: project_c1(replace(packet, observed_x='1.2')), 'inconsistent_projection_not_empty_safe')
    reject(lambda: project_c1(replace(packet, observed_x=1.0)), 'inexact_float_observation')
    reject(lambda: intersect_x((Q(0), Q('.01')), (Q('.02'), Q('.03'))), 'empty_history_not_safe')
    reject(lambda: propagate_translation_x((0, 1, 0, 1), ('-.03', '.03')), 'domain_widening_not_subset')
    first, second = map(project_c1, packets)
    history = intersect_x(first['bx'], second['bx'])
    assert history == first['bx'] and history != second['bx']
    assert first['by'] == second['by'] == (Q('-.01'), Q('.01'))
    assert first['delta'] == second['delta'] == (Q('-.002'), Q('.002'))
    assert first['localization_bound'] == second['localization_bound'] == Q('.01')
    # The gauge ambiguity remains: b_x+h and ell_x-h give the same observations.
    h = Q('.005')
    assert abs(h) <= Q('.009999') and history[0] <= h <= history[1]
    assert h+(-h) == 0
    propagated = {}
    for name, box in evidence['occupancy_boxes'].items():
        if name.startswith('A_'):
            old = tuple(Q(box[k]) for k in ('xmin', 'xmax', 'ymin', 'ymax'))
            new = propagate_translation_x(old, history)
            assert old[0] <= new[0] <= new[1] <= old[1] and new[2:] == old[2:]
            propagated[name] = new
    return {'rejected_boundaries': rejected, 'unchanged_by_delta_localization': True,
            'fixed_bias_gauge_not_removed': True, 'propagation_all_A_actions_and_HOLD': propagated,
            'five_millimetre_gauge_pair_remains_allowed': True}


def audit():
    result = compare_existing_history()
    baseline = update_baselines(result)
    boundaries = boundary_audit()
    decisions = {method: [r['comparisons'][method]['full_suffix_separated'] for r in result['records']]
                 for method in ('prior', 'latest_packet', 'history_intersection')}
    blockers = {method: [r['comparisons'][method]['unresolved_pairs'] for r in result['records']]
                for method in decisions}
    assert len({str(x) for x in decisions.values()}) == 1
    assert len({str(x) for x in blockers.values()}) == 1
    assert decisions['prior'] == [False, True]
    assert [r['frozen_SADG_decision'] for r in result['records']] == decisions['prior']
    assert baseline['positive_certificate_reuse_opportunities'] == 0
    paths = [Path(__file__), TOOLS/'history_replay.py', SOURCE/'initial_pose_history.py',
             BASE/'composition_fixture.json', BASE/'COMPOSITION_CHECK.json', BASE/'COMPOSITION_MANIFEST.json',
             BASE/'composition_constraints.py', BASE/'interface.py', SOURCE/'composition.py',
             TOOLS/'protocol.py', TOOLS/'timed_protocol.py']
    return {**result, 'status': 'FIXED_FIVE_ROUND_FEEDBACK_FEASIBILITY_PASS',
            'round_4_strong_baseline_and_cost': baseline, 'round_5_boundaries': boundaries,
            'decision_vectors': decisions, 'unchanged_blocking_pairs': blockers,
            'candidate_decision': 'STOP_C1_BX_PROJECTION_AS_INDEPENDENT_CONTRIBUTION',
            'reason': 'state_projection_shrinks_but_constraints_decisions_and_strong_simple_update_do_not_improve',
            'actual_task_performance': 'NOT_MEASURED', 'external_contribution': 'NOT_ESTABLISHED',
            'T1_raw_trace_gap': 'UNCHANGED', 'fresh_run_plan': 'NOT_PREPARED',
            'input_sha256': {str(p.resolve()): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}}


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    target = BASE/'FEEDBACK_FEASIBILITY.json'
    if args.write_result and target.exists():
        raise FileExistsError('frozen receipt already exists')
    try:
        result = audit()
    except Exception as exc:
        result = {'status': 'FEEDBACK_FEASIBILITY_FAILED', 'error': type(exc).__name__, 'detail': str(exc),
                  'scientific_runs': 0, 'training': 0}
        if args.write_result:
            with target.open('x') as output:
                json.dump(result, output, default=str, sort_keys=True); output.write('\n')
        raise
    if args.write_result:
        with target.open('x') as output:
            json.dump(result, output, default=str, sort_keys=True); output.write('\n')
    print(json.dumps({k: result[k] for k in ('status', 'decision_vectors', 'candidate_decision',
                                           'reason', 'actual_task_performance', 'T1_raw_trace_gap')}, default=str))
