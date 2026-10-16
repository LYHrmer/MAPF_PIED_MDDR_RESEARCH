"""Three staged STATIC checks; never calls T1 task_child or an adaptive task loop."""
import argparse
import json
import hashlib
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q

from run_timed import BASE, HOME, inputs, load_components, dump


def verify_qualification_pins():
    manifest = json.loads((BASE/'QUALIFICATION_MANIFEST.json').read_text())
    sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
    if sha(BASE/'TIMED_MANIFEST.json') != manifest['frozen_T1_manifest_sha256']:
        raise ValueError('frozen T1 identity changed')
    roots = {'execution': BASE,
             'source': HOME/'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source',
             'tools': HOME/'MAPF_QUERY_VALUE_FEASIBILITY/exploration/execution_feedback'}
    count = 0
    for group, files in manifest['files'].items():
        for name, expected in files.items():
            path = (roots[group]/name).resolve()
            if not path.is_relative_to(roots[group]) or sha(path) != expected:
                raise ValueError('successor input changed: '+group+'/'+name)
            count += 1
    return count


def check(round_number):
    pin_count = verify_qualification_pins() if round_number == 3 else None
    timed, protocol, feedback, constraints, sessions, author = load_components()
    from verify_integration import module
    source = module('source_qualification', HOME/'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source/qualification.py')
    transport = module('feedback_qualification', HOME/'MAPF_QUERY_VALUE_FEASIBILITY/exploration/execution_feedback/qualification.py')
    successor = module('qualified_session', BASE/'qualified_session.py')
    base, config = inputs()
    problem = constraints.make_problem(base, config, 2)
    checks, evidence = [], {}

    def need(value, name):
        if not value:
            raise AssertionError(name)
        checks.append(name)

    def rejects(call, name):
        try:
            call()
        except ValueError:
            checks.append(name)
        else:
            raise AssertionError(name)

    tr = problem['trajectories']['A']
    parts = source.phase_segments(tr)
    need(parts[0][2] == 0 and parts[-1] == (3, 'PERMANENT_HOLD', Q(11), None), 'phase_partition_keeps_task_origin_and_permanent_hold')
    need(sum(hi-lo for _, _, lo, hi in parts if hi is not None) == 11, 'finite_phases_cover_full_duration_without_gap')
    need((0, 'BRAKE', Q(4), Q('4.5')) in parts, 'braking_interval_explicit')
    anchor = timed.Anchor(Q(1), Q('.8'), Q('.81'), True, Q(11))
    windows = source.physical_windows(tr, anchor, Q(2))
    need(windows[-1]['start'] == Q('11.19') and windows[-1]['end'] is None, 'goal_window_keeps_phase_uncertainty_and_infinite_tail')
    rejects(lambda: source.physical_windows(tr, anchor, Q(0)), 'source_windows_reject_time_before_feedback_capture')
    clock = transport.CausalClock()
    rejects(lambda: clock.validate(0, deliveries=('.1',)), 'public_delivery_required_at_decision_time')
    clock.commit('.1')
    rejects(lambda: clock.validate(0), 'one_clock_rejects_cross_robot_retrospection')
    need(clock.frontier == Q('.1'), 'failed_validation_does_not_change_frontier')

    def stopped_messages(s):
        for r, t in problem['trajectories'].items():
            plant = timed.Plant(t)
            packet = feedback.TaskProducer(s.bindings[r]).capture(plant.observe(0), now=0)
            s.receive(packet, now=packet.delivery)

    # Preserve the old bug as a concrete regression witness, not a simulation.
    old = sessions.TaskSession(problem, author, engine='guard')
    stopped_messages(old)
    witness = old.authorize('A', now=0)
    need(witness['accepted'], 'frozen_T1_retrospective_dispatch_counterexample_reproduced')
    evidence['T1_counterexample'] = {'all_feedback_delivered_at': '.1', 'requested_launch_at': '0',
                                     'old_accepted': witness['accepted'], 'meaning': 'API causality defect; not an observed physical collision'}
    for engine in config['engines']:
        new = successor.CheckedSession(problem, author, engine=engine)
        stopped_messages(new)
        rejects(lambda: new.authorize('A', now=0), engine+'_retrospective_dispatch_rejected')
        need(not new.started and not new.commands, engine+'_rejected_request_has_no_control_side_effect')
        need(new.authorize('A', now='.1')['accepted'], engine+'_normal_forward_dispatch_preserved')
    if round_number >= 2:
        # Independently enumerated four-leaf outcomes, including disconnected
        # allowed leaves and an empty region. No trajectory sampling proof.
        for mask in range(16):
            leaves = [i for i in range(4) if mask & (1 << i)]
            clear = lambda lo, hi: not any(Q(i) < hi and Q(i+1) > lo for i in leaves)
            found = source.extreme_window(0, 4, clear, resolution=1, max_nodes=7)
            expected = None if not leaves else (Q(min(leaves)), Q(max(leaves)+1))
            need(found['window'] == expected, 'extremal_tree_mask_'+str(mask))
            need(found['nodes'] <= 7, 'memoized_search_does_not_exceed_full_tree_'+str(mask))
        rejects(lambda: source.extreme_window(0, 4, lambda a, b: False, resolution=1, max_nodes=1),
                'budget_exhaustion_never_returns_partial_window')
        reference, candidate = constraints.Certificates(problem), successor.EndpointCertificates(problem)
        need(reference.constraints == candidate.constraints, 'all_twelve_C1_constraints_exactly_equal')
        need(reference.cache == candidate.cache, 'all_twenty_two_action_region_windows_exactly_equal')
        left = {'commitment': problem['commitment'], 'constraints': reference.constraints,
                'phase_cells': reference.operations['phase_cells']}
        right = {**left, 'phase_cells': candidate.operations['phase_cells']}
        comparison = transport.construction_comparison(left, right)
        need(comparison['saved_phase_cells'] > 0 and not comparison['runtime_speedup_claim_allowed'],
             'fewer_enclosure_evaluations_do_not_assert_measured_runtime_speedup')
        rejects(lambda: transport.construction_comparison(left, {**right, 'commitment': 'foreign'}),
                'different_motion_inputs_cannot_form_speedup_pair')
        rejects(lambda: transport.construction_comparison(left, {**right, 'constraints': []}),
                'different_output_windows_cannot_form_exact_optimization_pair')
        evidence['construction'] = comparison
        evidence['construction']['query_count'] = len(reference.cache)
    if round_number >= 3:
        hold = source.terminal_hold_certificate(tr, anchor, Q(2))
        need(hold['valid_from'] == Q('11.2') and not hold['is_physical_END_confirmation'],
             'all_phase_realizations_must_finish_before_permanent_tail_certificate')
        still = timed.Anchor(Q(0), Q(0), Q(0), False, Q(11))
        need(source.terminal_hold_certificate(tr, still, Q(2)) is None, 'initial_wait_cannot_be_relabelled_as_goal_hold')
        wrong = timed.Anchor(Q(0), Q(0), Q(0), False, Q(12))
        rejects(lambda: source.terminal_hold_certificate(tr, wrong, Q(2)), 'feedback_duration_bound_to_trajectory')
        # A receipt without END may only report missing terminal evidence.
        empty = successor.CheckedSession(problem, author, engine='guard')
        need(all(v is None for v in empty.receipt()['terminal_geometry_after_delivered_END'].values()),
             'no_private_truth_or_nominal_time_fills_missing_END')
        # Per-robot packet validation can pass while the global frontier is past it.
        causal = successor.CheckedSession(problem, author, engine='guard')
        stopped_messages(causal)
        causal.authorize('A', now='.1')
        causal.authorize('B', now='.3')  # no ACK: denied, but this event happened
        packet = feedback.TaskProducer(causal.bindings['B']).capture(timed.Plant(problem['trajectories']['B']).observe('.1'), now='.1')
        packet = replace(packet, seq=1)
        causal.inboxes['B'].validate(packet, now='.2')
        rejects(lambda: causal.receive(packet, now='.2'), 'cross_robot_receive_frontier_cannot_go_backwards')
        need(len(causal.packets) == 2, 'failed_cross_robot_receive_retains_previous_public_state')

        receipts, planned, pairs = [], [], []
        initial = tuple(map(float, config['initial_conditions']['all_robots']))
        for size in config['sizes']:
            pair = []
            for engine in config['engines']:
                p = constraints.make_problem(base, config, size)
                s = successor.CheckedSession(p, author, engine=engine)
                plants = {r: timed.Plant(t, initial) for r, t in p['trajectories'].items()}
                producers = {r: feedback.TaskProducer(s.bindings[r]) for r in plants}

                def send(robot, capture):
                    with s.costs.measure('fixed_controller_sensor_public_message'):
                        packet = producers[robot].capture(plants[robot].observe(capture), now=capture)
                        s.receive(packet, now=packet.delivery)

                for r in plants:
                    send(r, '0')
                need(s.authorize('A', now='.1')['accepted'], str(size)+engine+'_first_chain_still_qualified')
                plants['A'].clock.resume('.1')
                send('A', '.1')
                need(not s.authorize('B', now='.2')['accepted'], str(size)+engine+'_early_release_still_rejected')
                if size == 3:
                    need(s.authorize('C', now='.2')['accepted'], engine+'_independent_third_chain_qualified')
                    plants['C'].clock.resume('.2')
                    send('C', '.2'); send('C', '1.7')
                for r in ('A', 'B'):
                    send(r, config['static_progress_capture'])
                need(not s.authorize('B', now='9.45', deadline='10')['accepted'], str(size)+engine+'_short_deadline_still_infeasible')
                need(s.authorize('B', now='9.45')['accepted'], str(size)+engine+'_unchanged_fixed_time_release')
                plants['B'].clock.resume('9.45')
                send('B', '9.45'); send('A', '11.1'); send('B', '23.67')
                result = s.receipt()
                need(result['success'] and all(result['terminal_geometry_after_delivered_END'].values()),
                     str(size)+engine+'_all_END_and_permanent_geometry_present')
                need(result['operations']['phase_cells'] == 446, str(size)+engine+'_endpoint_compiler_used_in_complete_session')
                need(result['costs']['aggregation'] == 'OUTER_ENVELOPE_ONLY_DO_NOT_SUM_NESTED' and
                     any(x['name'] == 'final_source_and_constraint_audit' for x in result['costs']['segments']),
                     str(size)+engine+'_final_source_audit_cost_included')
                pair.append(result); receipts.append(result)
                planned.append({'task': result['task'], 'arm': engine, 'robots': list(plants)})
            audit = transport.fixed_session_comparison(*pair)
            need(all(audit[k] for k in ('both_success', 'same_launches', 'same_completion', 'same_core_work')),
                 str(size)+'_optimized_strong_adapter_preserves_negative_result')
            need(not audit['new_relative_guarantee'] and audit['total_process_cost_status'] == 'UNKNOWN_NOT_MEASURED',
                 str(size)+'_neither_new_guarantee_nor_runtime_gain_invented')
            pairs.append({'size': size, **audit, 'completion': pair[0]['completion'],
                          'messages_per_arm': pair[0]['messages'], 'bytes_per_arm': pair[0]['bytes'],
                          'constraint_signature': pair[0]['constraint_signature'],
                          'operations_per_arm': pair[0]['operations']})
        ledger = transport.task_ledger(planned, receipts, horizon=config['horizon'])
        need(ledger['planned_count'] == 4 and ledger['success_count'] == 4, 'four_fixed_message_fixtures_accounted_for')
        negative = deepcopy(receipts[:1])
        negative[0]['success'], negative[0]['status'] = False, 'FAILED'
        failures = transport.task_ledger(planned[:2], negative, horizon=config['horizon'])
        need(failures['failure_or_missing_count'] == 2 and failures['failed_rows_excluded'] == 0,
             'failure_and_absent_result_both_retained')
        need(all(r['penalized_sum_completion'] == '120' for r in failures['rows']),
             'failure_with_END_cannot_outscore_success_via_small_completion_sum')
        bad = deepcopy(receipts[0]); bad['completion']['A'] = None
        rejects(lambda: transport.task_ledger(planned[:1], [bad], horizon=config['horizon']), 'missing_completion_cannot_be_success')
        rejects(lambda: transport.task_ledger(planned[:1], [receipts[0], receipts[0]], horizon=config['horizon']), 'duplicate_results_not_silently_dropped')
        bad = deepcopy(receipts[1]); bad['public_wire_sha256'] = 'foreign'
        rejects(lambda: transport.fixed_session_comparison(receipts[0], bad), 'different_feedback_stream_not_same_information')
        evidence.update(fixed_session_pairs=pairs, fixed_fixture_ledger=ledger, failure_fixture_ledger=failures,
                        scientific_decision={'shared_event_wiring_candidate': 'CLOSED_AS_INDEPENDENT_CONTRIBUTION',
                                             'endpoint_optimization': 'ENGINEERING_RESULT_NO_NOVELTY_CLAIM',
                                             'total_runtime': 'UNKNOWN', 'next_scientific_run': 'NOT_AUTHORIZED'})
    return {'status': 'PASS', 'round': round_number, 'check_count': len(checks), 'checks': checks,
            'evidence': evidence, 'successor_input_pins': pin_count,
            'scientific_runs': 0, 'world_steps': 0, 'training': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round', type=int, choices=(1, 2, 3), required=True)
    args = parser.parse_args()
    result = check(args.round)
    (BASE/'QUALIFICATION_CHECK.json').write_text(dump(result)+'\n')
    print(dump(result))
