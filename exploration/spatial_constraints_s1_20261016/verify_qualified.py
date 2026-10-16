"""Three staged STATIC checks; never calls T1 task_child or an adaptive task loop."""
import argparse
import json
from fractions import Fraction as Q

from run_timed import BASE, HOME, inputs, load_components, dump


def check(round_number):
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
    return {'status': 'PASS', 'round': round_number, 'check_count': len(checks), 'checks': checks,
            'evidence': evidence, 'scientific_runs': 0, 'world_steps': 0, 'training': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--round', type=int, choices=(1, 2, 3), required=True)
    args = parser.parse_args()
    result = check(args.round)
    (BASE/'QUALIFICATION_CHECK.json').write_text(dump(result)+'\n')
    print(dump(result))
