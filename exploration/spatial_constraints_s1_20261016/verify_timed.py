"""Fixed source/interval/message fixtures only. Never calls task_child/world loop."""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction as Q
import json
import math

from run_timed import BASE, load_components, inputs, dump, verify_inputs, rectangle_overlap_witness
from interface import Box, temporal_feasible, dag


def check():
    timed, protocol, feedback, constraints, sessions, author = load_components()
    base, config = inputs()
    passed, summaries = [], []

    def need(value, name):
        if not value:
            raise AssertionError(name)
        passed.append(name)

    def rejects(fn, name):
        try:
            fn()
        except ValueError:
            passed.append(name)
        else:
            raise AssertionError(name)

    problem = constraints.make_problem(base, config, 2)
    tr = problem['trajectories']['A']
    initial = (.02, -.01, .002, .009999, -.009999)
    # Exact shared-parameter body family, including an interior turn attitude.
    p = tr.chain.sample(5.5, initial)['evaluation']
    theta, delta = p['pose_ref'][2], initial[2]
    u = (.3, .1)
    w = [p['pose_ref'][j]-float(tr.chain.origin[j]) for j in (0, 1)]
    w[0] += math.cos(theta)*u[0]-math.sin(theta)*u[1]
    w[1] += math.sin(theta)*u[0]+math.cos(theta)*u[1]
    expected = [float(tr.chain.origin[0])+initial[0]+math.cos(delta)*w[0]-math.sin(delta)*w[1],
                float(tr.chain.origin[1])+initial[1]+math.sin(delta)*w[0]+math.cos(delta)*w[1]]
    need(max(abs(a-b) for a, b in zip(expected, tr.body_point(Q('5.5'), initial, u))) < 1e-12,
         'one_shared_delta_rotates_displacement_and_body')
    for lo, hi in [(Q(0), Q('.5')), (Q('3.9'), Q('4.5')), (Q('4.5'), Q('8.5')), (Q('10.5'), Q(11))]:
        b = tr.box(lo, hi)
        # These fixed probes only check implementation; interval inequalities
        # supply coverage between probes and for every allowed initial parameter.
        points = [tr.body_point(t, initial, c) for t in (lo, (lo+hi)/2, hi)
                  for c in ((-.3, -.1), (-.3, .1), (.3, -.1), (.3, .1))]
        need(all(float(b[0]) <= x <= float(b[1]) and float(b[2]) <= y <= float(b[3]) for x, y in points),
             'continuous_enclosure_probe_'+str(lo)+'_'+str(hi))
    need(timed.distance(Q('4.25'), Q(2)) == Q('1.96875') and timed.distance(Q('4.5'), Q(2)) == 2,
         'braking_tail_kept_in_exact_motion_profile')
    clock = timed.SharedClock(tr)
    clock.resume('0', commit=False)
    rejects(lambda: clock.pause('.25'), 'moving_pause_rejected_requires_braking')
    clock.pause('4.5')
    need(clock.phase('9') == Q('4.5'), 'common_pause_freezes_reference_and_actual_phase')
    clock.resume('9')
    need(clock.phase('10') == Q('5.5'), 'common_resume_preserves_accumulated_phase')
    rejects(lambda: clock.pause('13'), 'outstanding_reservation_prevents_extra_wait')
    a = timed.Anchor(Q(1), Q('.8'), Q('.81'), True, Q(11))
    need(a.phases(Q(2), Q('2.2')) == (Q('1.8'), Q('2.01')), 'physical_time_propagates_delivered_phase_interval')
    rejects(lambda: a.phases(Q('.9'), Q(2)), 'cannot_use_anchor_before_capture')
    same = timed.Anchor(Q(0), Q(0), Q(0), False, Q(11))
    checker = constraints.Certificates(problem)
    need(checker.pair('A', same, 'A', same, now=0)['status'] == 'UNRESOLVED', 'outer_overlap_not_reported_as_collision')
    need(dag(['a', 'b'], [('a', 'b')])['feasible'] and
         not temporal_feasible(['z', 'a', 'b'], [('z', 'a', 0), ('a', 'b', 2), ('b', 'z', -1)]),
         'DAG_and_time_feasibility_remain_distinct')
    square = [(0, 0), (1, 0), (1, 1), (0, 1)]
    need(rectangle_overlap_witness(square, square) == 'NUMERICAL_INTERIOR_COLLISION_WITNESS' and
         rectangle_overlap_witness(square, [(x+2, y) for x, y in square]) == 'SEPARATED_AT_PROBE' and
         rectangle_overlap_witness(square, [(x+1, y) for x, y in square]) == 'NEAR_CONTACT_UNRESOLVED',
         'collision_witness_separated_from_outer_overlap_and_contact_uncertainty')

    # Complete fixed public task fixtures, not adaptive simulation/batch runs.
    for size in (2, 3):
        per_size = []
        for engine in config['engines']:
            costs = protocol.Costs()
            with costs.measure('static_complete_message_fixture'):
                problem = constraints.make_problem(base, config, size)
                s = sessions.TaskSession(problem, author, engine=engine, costs=costs)
                plants = {r: timed.Plant(t, initial) for r, t in problem['trajectories'].items()}
                producers = {r: feedback.TaskProducer(s.bindings[r]) for r in plants}

                def send(robot, capture):
                    with costs.measure('static_controller_sensor_wire_and_delivery'):
                        ob = plants[robot].observe(capture)
                        packet = producers[robot].capture(ob, now=capture)
                        s.receive(packet, now=packet.delivery)
                        return packet

                need(not s.authorize('A', now=0)['accepted'], str(size)+engine+'_planned_clock_alone_cannot_start')
                for robot in plants:
                    send(robot, '0')
                need(s.authorize('A', now='.1')['accepted'], str(size)+engine+'_initial_waits_certified_before_command')
                plants['A'].clock.resume('.1')
                need(not s.authorize('B', now='.1')['accepted'], str(size)+engine+'_command_is_not_actual_input_ack')
                ack = send('A', '.1')
                premature = replace(ack, seq=ack.seq+1, capture='.2', delivery='.3', phase_lo='11', phase_hi='11',
                                    state='DONE', kind='END', completion_time='.2')
                rejects(lambda: s.receive(premature, now='.3'), str(size)+engine+'_premature_END_rejected')
                need(not s.authorize('B', now='.2')['accepted'], str(size)+engine+'_too_early_time_window_rejected')
                rejects(lambda: s.request_change('A', action='pause_or_speed_change'), str(size)+engine+'_committed_profile_immutable')
                if size == 3:
                    need(s.authorize('C', now='.2')['accepted'], engine+'_third_independent_robot_dispatch')
                    plants['C'].clock.resume('.2')
                    send('C', '.2')
                    send('C', '1.7')
                for robot in ('A', 'B'):
                    send(robot, config['static_progress_capture'])
                anchors = s.anchors(Q('9.45'))
                # Same geometry and feedback; retaining time can avoid a whole-
                # suffix spatial mutex, but BOTH fair engines receive this ability.
                full_a = Box(*problem['trajectories']['A'].box(anchors['A'].phases(Q('9.45'), Q('9.45'))[0], Q(11)))
                full_b = Box(*problem['trajectories']['B'].box(Q(0), problem['trajectories']['B'].chain.duration))
                need(not full_a.separated(full_b), str(size)+engine+'_spatial_union_loses_time_separation')
                need(not s.authorize('B', now='9.45', deadline='10')['accepted'], str(size)+engine+'_deadline_cannot_shorten_braking_chain')
                grant = s.authorize('B', now='9.45')
                need(grant['accepted'], str(size)+engine+'_physical_time_reservation_passes')
                if s.events:
                    need(s.events.motion['A'].get_status() == s.events.Status.IN_PROGRESS,
                         str(size)+'_future_reservation_not_fake_physical_END')
                plants['B'].clock.resume('9.45')
                bp = send('B', '9.45')
                rejects(lambda: s.receive(bp, now=bp.delivery), str(size)+engine+'_replayed_packet_rejected')
                send('A', '11.1')
                send('B', '23.67')
                need(all(x is not None for x in s.completion.values()), str(size)+engine+'_all_actual_END_events_delivered')
            receipt = s.receipt()
            need(receipt['success'], str(size)+engine+'_complete_receipt_retains_real_completion_times')
            need(receipt['costs']['wall_ns'] >= max(x['wall_ns'] for x in receipt['costs']['segments']),
                 str(size)+engine+'_costs_use_outer_envelope')
            per_size.append({'size': size, 'engine': engine, 'completion': receipt['completion'],
                             'messages': receipt['messages'], 'bytes': receipt['bytes'],
                             'public_wire_sha256': receipt['public_wire_sha256'],
                             'operations': receipt['operations'], 'constraints': receipt['constraint_count'],
                             'censored_sum_completion': receipt['censored_sum_completion'],
                             'censored_makespan': receipt['censored_makespan'],
                             'initial_wait': receipt['initial_wait']})
        left, right = per_size
        need(all(left[k] == right[k] for k in ('completion', 'messages', 'bytes', 'public_wire_sha256', 'operations', 'constraints')),
             str(size)+'_same_information_certificate_and_work_counts')
        summaries.extend(per_size)

    # Invalid feedback is checked before mutation, with no private-state channel.
    problem = constraints.make_problem(base, config, 2)
    s = sessions.TaskSession(problem, author, engine='guard')
    plant = timed.Plant(problem['trajectories']['A'], initial)
    producer = feedback.TaskProducer(s.bindings['A'])
    ob = plant.observe('0')
    rejects(lambda: producer.capture({**ob, 'pose_true': [0, 0, 0]}, now=0), 'private_truth_schema_rejected')
    p = producer.capture(ob, now=0)
    rejects(lambda: s.receive(p, now=0), 'undelivered_phase_feedback_rejected')
    rejects(lambda: s.receive(replace(p, binding=replace(p.binding, commitment='new')), now='.1'), 'changed_commitment_rejected')
    rejects(lambda: s.receive(replace(p, observed_x='100'), now='.1'), 'observation_must_match_source_phase_family')
    rejects(lambda: s.receive(replace(p, clock='planned_clock'), now='.1'), 'nominal_clock_not_actual_input_feedback')
    s.receive(p, now='.1')
    missing = s.receipt()
    need(not missing['success'] and missing['failure_retained'] and missing['censored_sum_completion'] == '80',
         'missing_END_tasks_retained_in_failure_metrics')
    for robot in ('B',):
        bplant = timed.Plant(problem['trajectories'][robot])
        packet = feedback.TaskProducer(s.bindings[robot]).capture(bplant.observe(0), now=0)
        s.receive(packet, now='.1')
    need(not s.authorize('A', now='2')['accepted'], 'stale_state_prevents_new_dispatch')
    s.problem['config']['feedback_ttl'] = '100'
    rejects(lambda: s.authorize('A', now='2'), 'in_place_condition_mutation_invalidates_commitment')
    plant.clock.resume('.1')
    late = plant.observe('12')
    need(late['completion_time'] == '111/10' and late['capture'] == '12', 'completion_capture_and_delivery_are_distinct')
    bad = deepcopy(base); bad['robots']['A']['actions'] = [['MOVE', '2'], ['HOLD', '0']]
    rejects(lambda: constraints.make_problem(bad, config, 2), 'permanent_goal_overlap_not_hidden_by_finite_time_horizon')
    bad = deepcopy(base); bad['existing_passage_order'].append(['B_2', 'A_0'])
    rejects(lambda: constraints.make_problem(bad, config, 2), 'existing_cycle_rejected_without_claiming_all_arrangements_impossible')
    bad_config = deepcopy(config); bad_config['dispatch_delay'] = '.1'
    rejects(lambda: constraints.make_problem(base, bad_config, 2), 'new_dispatch_latency_requires_new_phase_contract')
    old = json.loads((BASE/'COMPOSITION_CHECK.json').read_text())
    need([x['guard']['accepted'] for x in old['decisions']] == [False, True] and old['same_information']['messages_per_arm'] == 2,
         'frozen_C1_negative_result_preserved')
    need(not (BASE/'timed_run_once_20261016').exists(), 'scientific_runtime_not_created')
    return {'status': 'STATIC_TIME_INTERFACE_PASS', 'check_count': len(passed), 'checks': passed,
            'fixed_public_sessions': summaries, 'world_runs': 0, 'task_child_calls': 0, 'training': 0,
            'scope': 'fixed closed-form source/interval/public-message fixtures, not independent task experiments',
            'constructed_constraints': checker.constraints,
            'increment': {'conservatism_vs_shared_strong_adapter': 'NO_EXTRA_CHOICE_IN_FIXED_FIXTURES',
                          'construction_update_operation_counts': 'IDENTICAL_SHARED_ALGORITHM',
                          'total_process_cost': 'NOT_MEASURED_UNTIL_AUTHORIZED_RUN',
                          'guarantee_vs_shared_strong_adapter': 'SAME_SUFFICIENT_CONDITIONS_NO_NEW_GUARANTEE'},
            'input_pins': verify_inputs()}


if __name__ == '__main__':
    import sys
    result = check()
    if sys.argv[1:] == ['--write-result']:
        (BASE/'TIMED_CHECK.json').write_text(dump(result)+'\n')
        print(dump({k: result[k] for k in ('status', 'check_count', 'fixed_public_sessions', 'increment', 'input_pins')}))
    elif not sys.argv[1:]:
        print(dump(result))
    else:
        raise ValueError('only --write-result is supported')
