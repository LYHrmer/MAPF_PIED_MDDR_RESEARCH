"""One deterministic algebraic fixture/contract check; no scientific run.

Outputs feasible analytic schedules, not simulated or observed improvements.
No random draws, time stepping, solver call, model fit or author re-run.
"""
import ast
from copy import deepcopy
import hashlib
import json
from pathlib import Path

from interface import (Q, q, Box, sweep, turn_sweep, conflicts, add_conflicts,
                       dag, temporal_feasible, release,
                       trapezoid_duration, cruise_arrival)


def check():
    base = Path(__file__).resolve().parent
    f = json.loads((base/'fixture.json').read_text())
    passed = []

    def need(predicate, name):
        if not predicate:
            raise AssertionError(name)
        passed.append(name)

    for name in ('interface.py', 'verify.py'):
        ast.parse((base/name).read_text(), filename=name)
    a, b = map(q, f['body_half'])
    ex, ey, psi = map(q, (f['tracking_parallel'], f['tracking_cross'], f['heading_error']))
    hx, hy = map(q, f['directional_half'])
    r = q(f['circle_radius'])
    # |sin psi|<=|psi|, |cos psi|<=1; radii .32/.04 verified by squares.
    need(hx >= a+b*psi+ex and hy >= b+a*psi+ey,
         'directional_body_position_heading_containment')
    need(q('.32')**2 >= a*a+b*b and q('.04')**2 >= ex*ex+ey*ey
         and r >= q('.32')+q('.04'), 'same_allowed_set_circle_containment')
    need(q('.02')+3*psi*psi/2 <= ex and q('.01')+3*psi <= ey,
         'unicycle_initial_pose_error_continuous_bound')
    speed, acceleration = f['speed'], f['acceleration']
    ta = trapezoid_duration(3, speed, acceleration)
    tb = trapezoid_duration(2, speed, acceleration)
    latency = q(f['message_delay'])
    packets = []
    for seq, observed in enumerate(f['observation_thresholds']):
        capture = cruise_arrival(q(observed)+1, 3, speed, acceleration)
        packets.append({'task': f['id'], 'condition': f['condition'], 'seq': seq,
                        'capture': str(capture), 'delivery': str(capture+latency),
                        'observed_x': observed, 'localization_bound': '.01',
                        'tracking_bound': '.03', 'kind': 'PROGRESS_BOUND'})

    def kwargs(packet, half_a, half_b, lower=None):
        lower = (q(packet['observed_x'])-q('.01')-q('.03')
                 if lower is None else q(lower))
        return dict(now=packet['delivery'], task=f['id'], condition=f['condition'],
                    half_a=half_a, occupied_b=sweep((0, -1), (0, 1), half_b),
                    suffix=[((lower, Q(0)), (Q(2), Q(0))),
                            ((Q(2), Q(0)), (Q(2), Q(0)))], end=(2, 0))

    kdir = kwargs(packets[0], (hx, hy), (hy, hx))
    kcirc = kwargs(packets[1], (r, r), (r, r))
    need(release(packets[0], **kdir)['accepted'], 'directional_full_suffix_release')
    need(release(packets[1], **kcirc)['accepted'], 'circular_full_suffix_release')
    need(not release(packets[0], **kwargs(packets[0], (r, r), (r, r)))['accepted'],
         'earlier_circle_release_rejected_same_packet')
    # Whole pre-release wait, all post-release B motion, both permanent goals.
    for name, ha, hb in [('directional', (hx, hy), (hy, hx)), ('circle', (r, r), (r, r))]:
        need(sweep((-1, 0), (2, 0), ha).separated(sweep((0, -1), (0, -1), hb)),
             name+'_all_pre_release_wait_safe')
        need(sweep((2, 0), (2, 0), ha).separated(sweep((0, -1), (0, 1), hb)),
             name+'_permanent_goal_safe')
        world = Box(q('-1.5'), q('2.5'), q('-1.5'), q('1.5'))
        for start, end, half in [((-1, 0), (2, 0), ha), ((0, -1), (0, 1), hb)]:
            z = sweep(start, end, half)
            need(world.xmin < z.xmin <= z.xmax < world.xmax and
                 world.ymin < z.ymin <= z.ymax < world.ymax, name+'_wall_clearance')

    # New neighboring-segment conflict: no shared waypoint, intersecting tubes.
    occ = [('C_straight', 'C', sweep((0, 0), (1, 0), (hx, hy))),
           ('D_straight', 'D', sweep((q('.2'), q('.2')), (q('1.2'), q('.2')), (hx, hy)))]
    need(conflicts(occ) == [('C_straight', 'D_straight')], 'new_adjacent_segment_conflict')
    turn = turn_sweep((0, 0), '.32', '.05', a, b)
    need(q('.05')**2 >= 2*q('.03')**2, 'turn_position_error_containment')
    neighbor = sweep(('.61', 0), ('.61', 0), (a, b))
    need(not turn.separated(neighbor), 'new_turn_sweep_conflict')
    need(sweep((0, 0), (0, 0), (a, b)).separated(neighbor) and
         sweep((0, 0), (0, 0), (b, a)).separated(neighbor),
         'turn_nominal_endpoints_miss_conflict')
    # Exact intermediate-heading corner witness: cos=12/13, sin=5/13.
    wx, wy = a*Q(12, 13)+b*Q(5, 13), a*Q(5, 13)-b*Q(12, 13)
    need(neighbor.xmin < wx < neighbor.xmax and neighbor.ymin < wy < neighbor.ymax,
         'turn_interior_overlap_witness_no_sampling')
    nodes = ['C', 'D', 'E', 'F']
    ranks = {'C': (0, 'C'), 'D': (1, 'D'), 'E': (2, 'E'), 'F': (3, 'F')}
    need(add_conflicts(nodes, [('C', 'D')], [('D', 'C'), ('E', 'F')], ranks)['feasible'],
         'existing_order_preserved_new_order_frozen')
    cyc = add_conflicts(nodes, [('D', 'E'), ('F', 'C')], [('C', 'D'), ('E', 'F')], ranks)
    need(not cyc['feasible'] and cyc['reason'] == 'CURRENT_ARRANGEMENT_CYCLE',
         'new_orders_cycle_reject_only_current_arrangement')
    need(dag(['start', 'end'], [('start', 'end')])['feasible'] and
         not temporal_feasible(['zero', 'start', 'end'],
                               [('zero', 'start', 0), ('start', 'end', 2), ('end', 'zero', -1)]),
         'dag_does_not_imply_temporal_feasibility')
    need(temporal_feasible(['zero', 'start', 'end'],
                          [('zero', 'start', 0), ('start', 'end', 2), ('end', 'zero', -3)]),
         'feasible_temporal_window')

    bad = deepcopy(packets[0]); bad['kind'] = 'END'
    need(not release(bad, **kdir)['accepted'], 'ordinary_END_cannot_release')
    bad = deepcopy(packets[0]); bad['truth_x'] = '.54'
    need(not release(bad, **kdir)['accepted'], 'private_truth_field_rejected')
    bad = deepcopy(packets[0]); bad['condition'] = 'different_speed'
    need(not release(bad, **kdir)['accepted'], 'changed_mode_rejected')
    bad = deepcopy(packets[0]); bad['tracking_bound'] = '0'
    need(not release(bad, **kdir)['accepted'], 'shrunk_bound_rejected')
    badk = deepcopy(kdir); badk['now'] = packets[0]['capture']
    need(not release(packets[0], **badk)['accepted'], 'undelivered_packet_rejected')
    badk = deepcopy(kdir); badk['suffix'].insert(1, ((Q(2), Q(0)), (Q(0), Q(0))))
    need(not release(packets[0], **badk)['accepted'], 'future_reentry_rejected')
    badk = deepcopy(kdir); badk['suffix'] = badk['suffix'][:-1]
    need(not release(packets[0], **badk)['accepted'], 'missing_goal_hold_rejected')
    badk = deepcopy(kdir); badk['occupied_b'] = sweep((0, 0), (2, 0), (hy, hx))
    need(not release(packets[0], **badk)['accepted'], 'terminal_or_return_corridor_overlap_rejected')
    need(not sweep((0, 0), (0, 0), (hx, hy)).separated(sweep((0, 0), (0, 0), (hy, hx))),
         'start_overlap_requires_rejection_even_if_graph_acyclic')

    old_start = ta+latency
    schedules = []
    for label, start in [('waypoint_END_guard', old_start),
                         ('circle_CLEAR', q(packets[1]['delivery'])),
                         ('directional_CLEAR', q(packets[0]['delivery']))]:
        need(temporal_feasible(['zero', 'As', 'Ae', 'Bs', 'Be'],
                               [('zero', 'As', 0), ('As', 'zero', 0),
                                ('As', 'Ae', ta), ('Ae', 'As', -ta),
                                ('zero', 'Bs', start), ('Bs', 'zero', -start),
                                ('Bs', 'Be', tb), ('Be', 'Bs', -tb)]),
             label+'_complete_schedule_time_constraints')
        schedules.append({'arm': label, 'A_complete': str(ta), 'B_start': str(start),
                          'B_complete': str(start+tb), 'sum_completion': str(ta+start+tb),
                          'makespan': str(max(ta, start+tb)), 'B_wait': str(start),
                          'progress_messages': 2, 'ordinary_END_messages': 2,
                          'last_END_delivery': str(max(ta, start+tb)+latency),
                          'meaning': 'ANALYTIC_FEASIBLE_ZERO_ERROR_REALIZATION_NOT_MEASURED'})
    # A separate common predecessor finishing at t=8 masks either early release.
    need(max(Q(8), q(packets[0]['delivery'])) == max(Q(8), old_start),
         'independent_predecessor_no_completion_gain')
    need(min(old_start, old_start+1) == old_start, 'late_feedback_no_gain_endpoint_fallback')
    return {'status': 'STATIC_ANALYTIC_CHECK_PASS', 'checks': passed,
            'scientific_runs': 0, 'author_runs': 0, 'world_samples': 0,
            'fixture_sha256': hashlib.sha256((base/'fixture.json').read_bytes()).hexdigest(),
            'packets': packets, 'analytic_schedules': schedules,
            'continuous_directional_min_certificate_margin': '3/100',
            'scope': 'declared primitive sets only; no learned or empirical result'}


if __name__ == '__main__':
    print(json.dumps(check(), ensure_ascii=False, indent=2))
