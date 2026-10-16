"""One fixed analytic interface case; no optimizer, world steps or training.

All probes are unit/contract checks. Continuous coverage follows the stated
invariant and interval inequalities, not dense sampling or empirical maxima.
"""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
import hashlib
import json
from pathlib import Path
import sys

from verify_integration import BASE, HOME, module, verify_pins, dependencies
from interface import dag, temporal_feasible


def verify_new_pins():
    manifest = json.loads((BASE/'COMPOSITION_MANIFEST.json').read_text())
    if hashlib.sha256((BASE/'INTEGRATION_MANIFEST.json').read_bytes()).hexdigest() != manifest['old_manifest_sha256']:
        raise ValueError('old frozen integration manifest changed')
    count = 0
    for group, root in [('execution', BASE), ('source', HOME/'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source')]:
        for name, expected in manifest['files'][group].items():
            path = (root/name).resolve()
            if not path.is_relative_to(root.resolve()) or hashlib.sha256(path.read_bytes()).hexdigest() != expected:
                raise ValueError('composition input changed: '+group+'/'+name)
            count += 1
    return count


def check():
    old, feedback, author = dependencies()
    source = module('composition', HOME/'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source/composition.py')
    compiler = module('composition_constraints', BASE/'composition_constraints.py')
    fixture = json.loads((BASE/'composition_fixture.json').read_text())
    passed = []

    def need(condition, name):
        if not condition:
            raise AssertionError(name)
        passed.append(name)

    def rejects(fn, name):
        try:
            fn()
        except ValueError:
            passed.append(name)
        else:
            raise AssertionError(name)

    problem = compiler.compile_case(fixture)
    need(problem['feasible'], 'whole_chain_start_wait_goal_and_world_qualified')
    need(problem['shared_waypoints'] == [], 'no_shared_waypoints_diagnostic_not_author_run')
    need(('A_0', 'B_2') in problem['finite_pairs'], 'adjacent_straights_add_spatial_conflict')
    need(any(problem['finite'][u].kind == 'TURN' or problem['finite'][v].kind == 'TURN'
             for u, v in problem['finite_pairs']), 'continuous_turn_sweeps_add_conflicts')
    need(all(e in problem['graph']['edges'] for e in problem['existing']), 'existing_passage_and_action_order_preserved')
    need(all(u.startswith('A_') and v.startswith('B_') for u, v in problem['graph']['new_or_retained']),
         'predeclared_rank_applied_to_all_new_conflicts')
    need(problem['graph']['feasible'], 'order_graph_acyclic_is_only_one_gate')
    need(not problem['special_pairs'], 'indefinite_occupancy_not_given_fake_completion')

    old_env = old.Envelope(Q('.02'), Q('.01'), Q('.002'))
    old_after = old.stopped_quarter_turn(old.propagate_straight(old_env, '3'))
    rejects(lambda: old.propagate_straight(old_after, '1'), 'old_v1_failure_preserved')
    spec = {'origin': ['0', '0'], 'heading': 0,
            'actions': [['MOVE', '3'], ['TURN', 1], ['WAIT', '2'], ['MOVE', '1'], ['HOLD', '0']]}
    chain = source.Chain.build(spec)
    at_turn = chain.error_box(chain.primitives[1].start, chain.primitives[1].end)
    need(at_turn[0] == Q('.020006') and at_turn[1] == Q('.016'), 'same_global_error_carried_through_turn')
    need(at_turn[0] > Q('.01'), 'next_local_cross_bound_is_not_reset_to_old_initial_box')
    end = chain.primitives[-1].end
    need(chain.error_box(end, end) == (Q('.022006'), Q('.016002')), 'composed_window_bound_derived_from_task_initial_set')
    for kwargs, name in [({'controller': 'feedback_controller'}, 'changed_controller'),
                         ({'speed': '.6'}, 'changed_speed'), ({'acceleration': '.5'}, 'changed_acceleration'),
                         ({'drift': '.001'}, 'nonzero_hold_drift'), ({'initial_speed': '.1'}, 'moving_pivot'),
                         ({'initial_omega': '.1'}, 'moving_angular_initial_state')]:
        rejects(lambda k=kwargs: source.Chain.build(spec, **k), name+'_requires_new_qualification')
    bad = deepcopy(spec); bad['actions'].append(['MOVE', '1'])
    rejects(lambda: source.Chain.build(bad), 'post_permanent_hold_action_rejected')
    far = deepcopy(spec); far['actions'] = [['MOVE', '3']]*3+[['HOLD', '0']]
    rejects(lambda: source.Chain.build(far), 'reference_domain_escape_rejected')
    missing = deepcopy(spec); missing['actions'].pop()
    rejects(lambda: source.Chain.build(missing), 'missing_terminal_hold_rejected')
    bad_float = deepcopy(spec); bad_float['actions'][0][1] = 3.
    rejects(lambda: source.Chain.build(bad_float), 'inexact_certificate_input_rejected')

    # The same latent heading bias, not independent interval resets, closes a loop.
    loop = source.Chain.build({'origin': ['0', '0'], 'heading': 0,
        'actions': [['MOVE', '1'], ['TURN', 1]]*4+[['HOLD', '0']]})
    need(loop.primitives[-1].end == loop.origin and loop.error_box(loop.origin, loop.origin) == (Q('.02'), Q('.01')),
         'closed_loop_returns_to_initial_position_error_set')
    need(loop.reference(float(loop.duration))['pose_ref'][2] > 6.28,
         'reference_heading_is_unwrapped_across_full_rotation')
    probes = [(chain, t) for t in (0, .25, 6.25, 7, 9, 11.5, 13, 15, 100)]
    probes += [(loop, float(loop.duration)+1)]
    for c, t in probes:
        record = c.sample(t, (.02, -.01, .002, .009999, -.009999))
        r = record['evaluation']
        action = c.primitives[r['action_index']]
        bounds = c.error_box(action.start, action.end)
        need(all(abs(r['tracking_error'][j]) <= float(bounds[j]+source.RESERVE) for j in (0, 1)),
             'closed_form_invariant_probe_'+str(len(passed)))
    held1, held2 = chain.sample(20, (.02, -.01, .002, 0., 0.)), chain.sample(100, (.02, -.01, .002, 0., 0.))
    need(held1['evaluation']['pose_true'] == held2['evaluation']['pose_true'], 'indefinite_zero_input_hold_keeps_residual')
    turn = chain.sample(7.5)['evaluation']
    need(turn['control']['v_cmd'] == 0 and abs(turn['control']['omega_cmd']) <= .5,
         'stopped_turn_has_separate_angular_controller')

    guards = [compiler.SuffixGate(problem, feedback) for _ in range(2)]
    graph = compiler.AuthorCompiledGate(problem, author)
    need(not graph.nodes['B_0'].can_execute(), 'author_event_graph_blocks_unconfirmed_spatial_conflicts')
    producer = feedback.Producer(guards[0].binding)
    packets = []
    for row in fixture['public_progress']:
        sensor = {k: row[k] for k in ('action', 'capture', 'observed_x', 'observed_y')}
        sensor.update(task=fixture['task'], robot='A', condition=source.CONDITION)
        packets.append(producer.capture(sensor, now=row['capture']))
        probe = problem['chains']['A'].sample(float(row['capture']))
        need(all(abs(probe['observation'][j]-float(row[k])) < 1e-12
                 for j, k in enumerate(('observed_x', 'observed_y'))), 'public_packet_has_allowed_zero_error_realization_'+row['capture'])
        need(probe['evaluation']['action_index'] == 2, 'local_action_binding_matches_controller_'+row['capture'])
    rejects(lambda: compiler.SuffixGate(problem, feedback).receive(packets[0], now=packets[0].capture),
            'capture_not_delivered_progress')
    rejects(lambda: compiler.SuffixGate(problem, feedback).receive(replace(packets[0], binding=replace(packets[0].binding, commitment='changed')), now=packets[0].delivery),
            'wrong_full_chain_commitment_rejected')
    rejects(lambda: compiler.SuffixGate(problem, feedback).receive(replace(packets[0], tracking_bound='.01'), now=packets[0].delivery),
            'caller_cannot_shrink_projection_bound')
    ordinary = compiler.SuffixGate(problem, feedback).receive(replace(packets[0], kind='END'), now=packets[0].delivery)
    need(not ordinary['accepted'], 'ordinary_END_never_completes_CLEAR_event')
    decisions = []
    for p in packets:
        own, other = [g.receive(p, now=p.delivery) for g in guards]
        graph.bind_local_action(2)
        allowed = graph.apply(other)
        need(own == other and allowed == own['accepted'], 'same_information_author_gate_equality_'+str(p.seq))
        need(graph.nodes['A_2'].get_status() == graph.Status.IN_PROGRESS, 'CLEAR_is_not_physical_END_'+str(p.seq))
        decisions.append({'delivery': p.delivery, 'guard': own, 'adapted_SADG_can_start_B': allowed})
    need([d['guard']['accepted'] for d in decisions] == [False, True], 'frozen_early_reject_later_release_case')
    need(guards[0].inbox.received_bytes == guards[1].inbox.received_bytes,
         'equal_public_message_bytes_not_free_feedback')
    rejects(lambda: guards[0].receive(packets[-1], now=packets[-1].delivery), 'replayed_progress_rejected')
    changed_guard = compiler.SuffixGate(problem, feedback)
    changed_guard.compiled['fixture']['robots']['A']['actions'][0][1] = '3'
    rejects(lambda: changed_guard.receive(packets[0], now=packets[0].delivery), 'changed_complete_suffix_contract_rejected')
    need(b'pose_true' not in b''.join(p.wire() for p in packets), 'no_private_truth_in_release_input')

    # Same pose/progress but a future return: full suffix must prevent release.
    returning = deepcopy(fixture)
    returning['robots']['A']['actions'] = returning['robots']['A']['actions'][:-1]+[
        ['TURN', 1], ['TURN', 1], ['MOVE', '1'], ['TURN', 1], ['MOVE', '.5'], ['HOLD', '0']]
    # Its final goal (1.5,0) is away from B; rejection is due to intermediate re-entry.
    ret_problem = compiler.compile_case(returning)
    need(ret_problem['feasible'], 'returning_suffix_has_no_start_or_terminal_shortcut_rejection')
    ret_gate = compiler.SuffixGate(ret_problem, feedback)
    ret_packet = replace(packets[-1], binding=ret_gate.binding)
    ret_certificate = ret_gate.receive(ret_packet, now=ret_packet.delivery)
    need(not ret_certificate['accepted'], 'future_reentry_blocks_release_despite_same_observation')
    ret_graph = compiler.AuthorCompiledGate(ret_problem, author)
    ret_graph.bind_local_action(2)
    need(not ret_graph.apply(ret_certificate), 'future_reentry_blocks_adapted_author_graph_too')
    permanent = deepcopy(fixture)
    permanent['robots']['A']['actions'] = [['MOVE', '2'], ['HOLD', '0']]
    terminal_problem = compiler.compile_case(permanent)
    need(not terminal_problem['feasible'] and bool(terminal_problem['special_pairs']), 'permanent_goal_conflict_not_finite_END_edge')
    rejects(lambda: compiler.SuffixGate(terminal_problem, feedback), 'unqualified_goal_arrangement_cannot_dispatch')
    cyclic = deepcopy(fixture)
    cyclic['existing_passage_order'] += [['B_2', 'A_0']]
    need(not compiler.compile_case(cyclic)['graph']['feasible'], 'current_order_cycle_reported_without_global_impossibility_claim')
    need(dag(['a', 'b'], [('a', 'b')])['feasible'] and
         not temporal_feasible(['z', 'a', 'b'], [('z', 'a', '0'), ('a', 'b', '2'), ('b', 'z', '-1')]),
         'acyclic_order_does_not_imply_feasible_time_window')

    release = Q(packets[-1].delivery)
    da, db = (problem['chains'][r].duration for r in ('A', 'B'))
    # Timeline is an allowed zero-error closed-form witness. It is not a world run
    # and scheduled/nominal time is never an input to the release test.
    lags = [('z', 'a0', 0), ('a0', 'a_end', da), ('a_end', 'z', -da),
            ('z', 'clear', release), ('clear', 'z', -release),
            ('clear', 'b0', 0), ('b0', 'clear', 0), ('b0', 'b_end', db),
            ('b_end', 'b0', -db)]
    need(temporal_feasible(['z', 'a0', 'a_end', 'clear', 'b0', 'b_end'], lags), 'analytic_allowed_schedule_has_consistent_time_constraints')
    need(problem['chains']['A'].reference(float(release))['action_index'] == 2 and release < da,
         'allowed_witness_overlaps_A_final_motion_without_completing_it')
    return {'status': 'ANALYTIC_INTERFACE_CHECK_PASS', 'checks': passed, 'check_count': len(passed),
            'scope': 'exploratory_fixed_case_not_world_or_author_optimizer_results',
            'source_condition': source.CONDITION, 'source_contract': source.contract(),
            'spatial_pairs': problem['pairs'], 'existing_order_edges': problem['existing'],
            'compiled_order_edges': problem['graph']['edges'], 'shared_waypoints': problem['shared_waypoints'],
            'occupancy_boxes': {n: {k: str(getattr(b, k)) for k in ('xmin', 'xmax', 'ymin', 'ymax')}
                                for n, b in problem['boxes'].items()},
            'decisions': decisions,
            'same_information': {'messages_per_arm': len(packets), 'bytes_per_arm': guards[0].inbox.received_bytes,
                                 'wire_sha256': hashlib.sha256(b'\n'.join(p.wire() for p in packets)).hexdigest(),
                                 'scheduler_increment': 'ZERO_FOR_SHARED_COMPILER_AND_CERTIFICATES_BY_REPRESENTATION'},
            'analytic_witness': {'A_completion': str(da), 'B_duration': str(db),
                                  'B_start': str(release), 'B_completion': str(release+db),
                                  'sum_completion': str(da+release+db), 'makespan': str(release+db),
                                  'not_a_measured_execution_result': True},
            'world_steps': 0, 'optimizer_calls': 0, 'training': 0, 'scientific_batches': 0,
            'continuous_coverage_basis': 'joint_initial_SE2_invariant_plus_exact_interval_enclosures; probes_are_not_proof',
            'remaining': ['full controller/feedback execution session', 'world continuous safety and all online costs',
                          'independent contribution beyond same-information spatial SADG adaptation']}


if __name__ == '__main__':
    pins, new_pins = verify_pins(), verify_new_pins()
    result = {**check(), 'old_pins_verified': pins, 'new_pins_verified': new_pins}
    payload = json.dumps(result, indent=2, ensure_ascii=False)+'\n'
    if sys.argv[1:]:
        if sys.argv[1:] != ['--write-result']:
            raise ValueError('only --write-result is supported')
        (BASE/'COMPOSITION_CHECK.json').write_text(payload)
        print(json.dumps({k: result[k] for k in ('status', 'check_count', 'spatial_pairs', 'same_information', 'analytic_witness')}, indent=2))
    else:
        print(payload)
