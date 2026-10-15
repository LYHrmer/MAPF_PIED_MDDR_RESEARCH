"""Contract checks with closed-form probes; no world stepping or optimization."""
from dataclasses import replace
import importlib.util
import json
from pathlib import Path
import sys

from author_events import FixedOrderEvents, load_author
from interface import q, release, sweep

BASE = Path(__file__).resolve().parent
HOME = BASE.parents[2]


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    result = importlib.util.module_from_spec(spec)
    sys.modules[name] = result
    spec.loader.exec_module(result)
    return result


def dependencies():
    source = module('spatial_source', HOME/'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source/model.py')
    feedback = module('execution_feedback', HOME/'MAPF_QUERY_VALUE_FEASIBILITY/exploration/execution_feedback/protocol.py')
    author = load_author(HOME/'.cache/mapf_research/sadg-controller-c2626d9',
                         BASE.parent/'error_guidance/sadg_preflight_20261004_r16/SOURCE_ENVIRONMENT.json')
    return source, feedback, author


def certificate(packet, fixture, *, geometry='directional', suffix=None):
    lower = q(packet['observed_x'])-q('.01')-q('.03')
    half = ('.34', '.13') if geometry == 'directional' else ('.36', '.36')
    half_b = half[::-1]
    return release(packet, now=packet['delivery'], task=fixture['id'], condition=fixture['condition'],
                   half_a=half, occupied_b=sweep((0, -1), (0, 1), half_b),
                   suffix=suffix if suffix is not None else [((lower, 0), (2, 0)), ((2, 0), (2, 0))], end=(2, 0))


def check():
    source, feedback, author = dependencies()
    fixture = json.loads((BASE/'fixture.json').read_text())
    passed = []

    def need(test, name):
        if not test:
            raise AssertionError(name)
        passed.append(name)

    def rejects(fn, name):
        try:
            fn()
        except ValueError:
            passed.append(name)
        else:
            raise AssertionError(name)

    bound = source.bounds()
    need(bound['parallel'] == q('.020006') and bound['cross'] == q('.016'), 'analytic_source_bound_matches_S1')
    a = source.Straight(fixture['id'], 'A', (-1, 0), 'E', 3.)
    samples = [a.sample(t) for t in (0., .25, 3.33, 6.25, 8.)]
    need([s['evaluation']['mode'] for s in samples] == ['WAIT', 'ACCEL', 'STRAIGHT', 'BRAKE', 'GOAL_HOLD'],
         'reference_acceleration_braking_wait_hold_connected')
    need(q(samples[2]['sensor']['observed_x']) == q('.54'), 'closed_form_probe_reproduces_public_observation')
    shifted = source.Straight(fixture['id'], 'A', (-1, 0), 'E', 3., initial=source.Initial(.02, .01, .002, .01, -.01))
    rec = shifted.sample(8.)
    need(abs(rec['evaluation']['tracking_error'][1]) > .01 and
         abs(rec['evaluation']['localization_error'][0]-.01) < 1e-12,
         'tracking_and_localization_separated_after_hold')
    rejects(lambda: source.Straight(fixture['id'], 'A', (-1, 0), 'E', 3., speed=.6), 'changed_speed_not_silently_admitted')
    binding = feedback.Binding(fixture['id'], 'A', 'A_move', fixture['condition'], source.COMMITMENT)
    producer = feedback.Producer(binding)
    packet = producer.capture(samples[2]['sensor'], now='3.33')
    rejects(lambda: feedback.Producer(binding).capture({**samples[2]['sensor'], 'pose_true': [0, 0, 0]}, now='3.33'),
            'private_truth_extra_field_rejected')
    inbox = feedback.Inbox(binding)
    rejects(lambda: inbox.admit(packet, now='3.33'), 'capture_does_not_equal_delivery')
    public = inbox.admit(packet, now='3.43')
    rejects(lambda: inbox.admit(packet, now='3.43'), 'replayed_progress_rejected')
    rejects(lambda: feedback.Inbox(binding).admit(replace(packet, tracking_bound='.02'), now='3.43'),
            'caller_cannot_shrink_bound')
    need(b'pose_true' not in packet.wire() and b'pose_ref' not in packet.wire(), 'wire_contains_public_observation_only')
    graph = FixedOrderEvents(author)
    need(not graph.b_motion.can_execute(), 'author_dependency_initially_blocks_B')
    cert = certificate(public, fixture)
    need(cert['accepted'] and graph.apply_certificate(cert), 'same_certificate_enables_author_dependency')
    need(graph.a_motion.get_status() == graph.Status.IN_PROGRESS, 'CLEAR_does_not_complete_physical_A')
    need(inbox.received_count == 1 and inbox.received_bytes == len(packet.wire()), 'feedback_count_and_wire_bytes_recorded')

    # Round 2: composition conditions and a same-information event baseline.
    env = source.Envelope(q('.02'), q('.01'), q('.002'))
    after = source.stopped_quarter_turn(source.propagate_straight(env, '3'))
    need(not source.admits_straight(after), 'quarter_turn_does_not_reset_cross_track_error')
    rejects(lambda: source.propagate_straight(after, '2'), 'unsupported_next_primitive_rejected')
    rejects(lambda: source.stopped_quarter_turn(env, speed='.1'), 'moving_pivot_rejected')
    need(source.permanent_hold(env) == env, 'hold_keeps_full_residual')
    rejects(lambda: source.permanent_hold(env, drift='.001'), 'unbounded_indefinite_drift_rejected')

    producer = feedback.Producer(binding)
    packets = [producer.capture(a.sample(float(t))['sensor'], now=t) for t in ('3.33', '3.83')]
    end_packet = producer.capture(a.sample(6.5)['sensor'], now='6.5', kind='END')
    rejects(lambda: producer.capture(a.sample(7.)['sensor'], now='7'), 'no_capture_after_action_END')
    ordinary = feedback.Inbox(binding).admit(end_packet, now='6.6')
    need(not certificate(ordinary, fixture)['accepted'], 'ordinary_END_alone_cannot_release')
    bus = feedback.Broadcast()
    bus.send(packets[0], now=packets[0].capture)
    need(not bus.deliver('3.33'), 'queue_hides_undelivered_packet')
    need(bus.deliver('3.43') == (packets[0],), 'queue_delivers_identical_packet_object')
    rejects(lambda: bus.deliver('3.42'), 'transport_clock_reversal_rejected')
    equality = []
    for geometry, expected in [('directional', '3.43'), ('circle', '3.93')]:
        own_inbox, author_inbox = feedback.Inbox(binding), feedback.Inbox(binding)
        graph, custom_started, first = FixedOrderEvents(author), False, None
        for packet in packets:
            own = certificate(own_inbox.admit(packet, now=packet.delivery), fixture, geometry=geometry)
            other = certificate(author_inbox.admit(packet, now=packet.delivery), fixture, geometry=geometry)
            custom_started = custom_started or own['accepted']
            eligible = graph.apply_certificate(other)
            need(custom_started == eligible, geometry+'_same_event_release_'+str(packet.seq))
            if eligible and first is None:
                first = q(packet.delivery)
        need(first == q(expected), geometry+'_same_information_first_release')
        need((own_inbox.received_count, own_inbox.received_bytes) ==
             (author_inbox.received_count, author_inbox.received_bytes), geometry+'_equal_feedback_cost_units')
        equality.append({'geometry': geometry, 'custom_release': str(first), 'adapted_SADG_release': str(first),
                         'meaning': 'API_contract_fixture_not_world_benchmark'})
    bad_suffix = [((q('.5'), 0), (2, 0)), ((2, 0), (0, 0)), ((0, 0), (0, 0))]
    graph = FixedOrderEvents(author)
    public = feedback.Inbox(binding).admit(packets[0], now='3.43')
    need(not graph.apply_certificate(certificate(public, fixture, suffix=bad_suffix)), 'reentry_blocks_author_adapter_too')
    wrong = replace(packets[0], binding=replace(binding, commitment='A_may_return'))
    rejects(lambda: feedback.Inbox(binding).admit(wrong, now='3.43'), 'commitment_change_rejected_before_graph')
    common = dict(task=fixture['id'], source_sha256='fixture', paths_sha256='fixed', order_sha256='A_before_B',
                  controller=source.CONTROLLER, protocol='public_progress_and_observed_END_v1',
                  initial_state_sha256='zero_error_probe', A_progress_wire_sha256='same_bytes', units='m_s_rad',
                  safety_set='same_declared_hard_initial_set')
    need(bool(feedback.paired_identity([common, dict(common)])), 'same_information_pair_identity_accepted')
    rejects(lambda: feedback.paired_identity([common, {**common, 'controller': 'different'}]), 'unequal_controller_pair_rejected')
    summary = feedback.completion_summary([
        {'task': 'synthetic_unit', 'arm': 'success', 'status': 'SUCCESS', 'completion': {'A': '6.5', 'B': '7.93'}},
        {'task': 'synthetic_unit', 'arm': 'timeout', 'status': 'TIMEOUT', 'completion': {'A': '6.5', 'B': None}}])
    need(len(summary) == 2 and summary[1]['failure_retained'] and q(summary[1]['censored_sum_completion']) == q('26.5'),
         'failed_task_remains_in_censored_metric')
    costs = feedback.Costs()
    with costs.measure('outer'):
        with costs.measure('inner'):
            pass
    measured = costs.finish()
    need(measured['wall_ns'] >= measured['segments'][-1]['wall_ns'] and
         [s['depth'] for s in measured['segments']] == [1, 0], 'nested_costs_not_added_twice')
    return {'status': 'INTERFACE_CHECK_PASS', 'round': 2, 'checks': passed,
            'check_count': len(passed), 'scientific_batches': 0, 'optimizer_calls': 0,
            'world_time_steps': 0, 'closed_form_source_probes': 10,
            'same_information_pairs': equality,
            'author_api': 'unmodified Vertex/Dependency/Status, fixed order, virtual certificate event',
            'interpretation': 'same certificate yields same release; no independent scheduling novelty established'}


if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False, indent=2))
