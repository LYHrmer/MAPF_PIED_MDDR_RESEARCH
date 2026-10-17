"""Conditional TURN/MOVE time elimination; no collision or release solver.

For a convex pivot body containing a radius-r disk and contained in radius R,
the longitudinal extrema of its intersection with a transverse strip containing
the pivot are R**2/r-Lipschitz in angle.  With contact in the MOVE cruise phase,
omega*R**2 <= r*v implies max(t_turn - tau_move(entry)) occurs at TURN END.

This prototype only qualifies a complete, unchanged v2 chain pair and returns
the exact boundary subproblem.  It does not evaluate poses, search contacts,
run a controller, tighten the allowed initial set, or authorize a release.
Proof and comparator contract: main/SPACE_TIME_INTERFACE_PLAN_20261016.md.
"""
from dataclasses import dataclass
from fractions import Fraction as Q

from composition import Chain, CONTROLLER, H, contract
from support_domain import move_domain


@dataclass(frozen=True)
class BoundaryProblem:
    # Retain the actual complete chains, not independent per-action error boxes.
    # These references are not robot IDs and must not replace the caller's IDs.
    turn_chain: Chain
    move_chain: Chain
    turn_index: int
    move_index: int
    turn_local_time: Q
    turn_phase: Q
    turn_heading: int
    offset_difference: Q
    move_entry_outer: tuple
    transverse_center_bound: Q
    contact_rate_bound: Q
    is_release_authorization: bool = False


def reduce_turn_incoming_move(turn_chain, turn_index, move_chain, move_index):
    """Return a boundary subproblem or a reason for the common fallback.

    Only the original v2 prior and fixed nonpreemptive physical-time offsets
    are covered.  Feedback domains/offset changes require caller revalidation.
    The remaining exact endpoint contact geometry is a SHARED solver service;
    a full-circle TURN box, a nominal pose, or a zero-length fake MOVE will not do.
    """
    for chain, index in ((turn_chain, turn_index), (move_chain, move_index)):
        if type(chain) is not Chain or type(index) is not int or not 0 <= index < len(chain.primitives):
            raise ValueError('qualified complete v2 Chain and valid action index required')
    declared = contract()
    expected = {'condition': 'joint_initial_se2_stopped_primitives_v2',
                'controller': 'ideal_feedforward_stopped_v05_a1_pivot_w05_alpha1_v2',
                'model': 'ideal_unicycle_identical_reference_actual_inputs',
                'body_half': ['.3', '.1'], 'speed': '.5', 'omega': '.5',
                'acceleration': '1', 'alpha': '1', 'turn_slot_seconds': '4',
                'task_initial_local_box': ['.02', '.01', '.002'],
                'reference_displacement_axis_limit': '8', 'reference_coordinate_limit': '10',
                'stop_at_each_action_boundary': True, 'hold_drift': '0'}
    if any(declared.get(k) != v for k, v in expected.items()) or H != Q('.002'):
        return None, 'SOURCE_CONDITION_CHANGED'
    turn = turn_chain.primitives[turn_index]
    move = move_chain.primitives[move_index]
    if turn.kind != 'TURN' or move.kind != 'MOVE':
        return None, 'REQUIRES_TURN_AND_MOVE'
    if turn.start != move.end:
        return None, 'NOMINAL_PIVOT_NOT_MOVE_END'

    # At the common nominal vertex, first bound the relative center error in
    # world axes, then rotate into B's ACTUAL MOVE frame.  A and B retain their
    # own task delta; each delta also rotates that vehicle's body.
    ea = turn_chain.error_box(turn.start, turn.end)
    eb = move_chain.error_box(move.end, move.end)
    error = max(ea[j]+eb[j] for j in (0, 1)) * (1+H)
    half_length, half_width = Q('.3'), Q('.1')
    inner_radius, radius_squared, radius_outer = Q('.1'), Q('.10'), Q('.32')
    speed, angular_speed = Q('.5'), Q('.5')
    if error > half_width:
        return None, 'TRANSVERSE_STRIP_MAY_EXCLUDE_PIVOT'
    domain = move_domain(move_chain, move_index)
    # Strip contains the origin: its lower longitudinal extreme is in [-R,-r].
    entry = (domain.length-error-half_length-radius_outer,
             domain.length+error-half_length-inner_radius)
    if entry[0] < Q(1, 8) or entry[1] > domain.length-Q(1, 8):
        return None, 'FIRST_CONTACT_NOT_PROVED_IN_CRUISE'
    rate = angular_speed*radius_squared/inner_radius
    if rate > speed:
        return None, 'CONTACT_RATE_EXCEEDS_MOVE_SPEED'
    offset = sum((a.duration for a in turn_chain.primitives[:turn_index]), Q(0))
    return BoundaryProblem(turn_chain, move_chain, turn_index, move_index,
                           turn.duration, offset+turn.duration, turn.next_heading,
                           offset-domain.offset, entry, error, rate), 'ENDPOINT_REDUCTION'


def static_r16_check():
    """Read one pinned old input and check algebraic qualifications, not tasks.

    Returns counts of candidate action pairs, not independent experiments or
    requests surviving all strong-baseline/global pruning. No scientific run.
    """
    import ast
    from collections import Counter
    from dataclasses import asdict
    import hashlib
    import json
    from pathlib import Path

    root = Path(__file__).resolve().parents[2]
    source = Path(__file__).resolve().parents[3]/'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source'
    old = root/'exploration/error_guidance/sadg_preflight_20261004_r16'
    staged = old/'inputs/official_test_staged.json'
    yaml = old/'official_ecbs_solution.yaml'
    pins = {staged: 'e24af3c1c95fe57f7512f5d3ed6826f3ec4007b27ddc69c879cea30624487f13',
            yaml: '0308cf1d1b11f777d2639cdac7b1ebcccd1221724b12226392fd41972c950975',
            source/'composition.py': 'e294be82cc6277fac462f61450685820f2d9f1b2c49f1c07c814f7abe4f08453'}
    for path, sha in pins.items():
        assert hashlib.sha256(path.read_bytes()).hexdigest() == sha, str(path)
    ast.parse(Path(__file__).read_text())
    schedule = json.loads(staged.read_text())['solution']['schedule']
    chains, vertices, arrivals = {}, {}, {}
    directions = ((1, 0), (0, 1), (-1, 0), (0, -1))
    for robot, path in schedule.items():
        points = [tuple(row[k] for k in ('x', 'y')) for row in path]
        headings = []
        for p, q in zip(points, points[1:]):
            headings.append(directions.index((q[0]-p[0], q[1]-p[1])))
        actions, heading = [], headings[0]
        for h in headings:
            if h != heading:
                delta = (h-heading) % 4
                assert delta in (1, 3), 'only original quarter turns qualified'
                actions.append(['TURN', 1 if delta == 1 else -1])
            actions.append(['MOVE', '1'])
            heading = h
        actions.append(['HOLD', '0'])
        chains[robot] = Chain.build({'origin': points[0], 'heading': headings[0], 'actions': actions})
        arrivals[robot] = {p: row['t'] for p, row in zip(points, path)}
        assert len(arrivals[robot]) == len(points), 'this static order screen assumes no revisits'
        t, events = Q(0), []
        for action in chains[robot].primitives:
            events.append((action.start, t))
            if action.duration is not None:
                t += action.duration
                events.append((action.end, t))
        vertices[robot] = events

    records, rejected = [], Counter()
    for a, ca in chains.items():
        for b, cb in chains.items():
            if a == b:
                continue
            # A legitimate analytic lower witness: zero allowed errors, actual
            # body centers coincident at two STOPPED boundary phases. It is not
            # a feasible schedule, an observed collision, or an execution result.
            lower = max((ta-tb for pa, ta in vertices[a] for pb, tb in vertices[b] if pa == pb), default=None)
            for i, turn in enumerate(ca.primitives):
                if turn.kind != 'TURN':
                    continue
                for j, move in enumerate(cb.primitives):
                    if move.kind != 'MOVE':
                        continue
                    reduction, status = reduce_turn_incoming_move(ca, i, cb, j)
                    if reduction is None:
                        rejected[status] += 1
                        continue
                    row = {k: v for k, v in asdict(reduction).items() if not k.endswith('_chain')}
                    upper = reduction.offset_difference+turn.duration
                    row.update(A=a, B=b, vertex=turn.start,
                               old_grid_A_before_B=arrivals[a][turn.start] < arrivals[b][turn.start],
                               trivial_time_upper=upper, boundary_contact_lower=lower,
                               pruned_by_boundary_contact=lower is not None and upper <= lower)
                    records.append(row)
    assert len(records) == 5
    assert sum(r['pruned_by_boundary_contact'] for r in records) == 1
    assert sum(r['old_grid_A_before_B'] and not r['pruned_by_boundary_contact'] for r in records) == 3

    # No fabricated positive scene: negative checks use types, the same input's
    # nonincident pairs, and an existing wrong-index boundary from that input.
    assert reduce_turn_incoming_move(chains['agent1'], 0, chains['agent0'], 0)[1] == 'REQUIRES_TURN_AND_MOVE'
    assert rejected['NOMINAL_PIVOT_NOT_MOVE_END'] > 0
    try:
        reduce_turn_incoming_move(chains['agent1'], True, chains['agent0'], 0)
    except ValueError:
        pass
    else:
        raise AssertionError('bool action index accepted')

    e0 = Q('.04')+16*H+8*H*H
    e = e0*(1+H)
    qlo, qhi = 1-e-Q('.3')-Q('.32'), 1+e-Q('.3')-Q('.1')
    assert e < Q('.1') and Q(1, 8) < qlo < qhi < Q(7, 8)
    assert Q('.5')*Q('.10')/Q('.1') == Q('.5')
    return {'status': 'STATIC_QUALIFICATION_ONLY', 'rule': 'TURN_END_CONTACT_RATE',
            'source_pins': {str(p): sha for p, sha in pins.items()},
            'prototype_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            'scale': 'explicit common-problem adaptation: 1 metre/grid edge; author resolution 2.5 is not reproduced',
            'controller': CONTROLLER, 'model': 'original v2 task-initial pose prior; no new source',
            'counts': {'robots': len(chains), 'moves': 24, 'turns': 6,
                       'qualified_incoming_pairs': len(records), 'after_trivial_boundary_prune': 4,
                       'also_matching_old_vertex_order': 3},
            'uniform_original_v2_bounds': {'relative_world_axis': e0, 'relative_actual_move_axis': e,
                                         'unit_move_entry': [qlo, qhi], 'rate': Q('.5')},
            'qualified_pairs': records, 'fallback_counts': dict(rejected),
            'not_established': ['exact endpoint solver integration', 'survival after all G0 fast paths/global pruning',
                                'full task timing/start-wait/terminal-hold feasibility',
                                'same-model baseline cost difference', 'independent novelty or full acceleration'],
            'scientific_runs': 0, 'pose_or_controller_calls': 0, 'root_solves': 0,
            'is_release_authorization': False}


if __name__ == '__main__':
    import argparse
    import json
    from pathlib import Path
    parser = argparse.ArgumentParser(description='Static old-input qualification; no scientific solver/session.')
    parser.add_argument('--static-check', action='store_true', required=True)
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    result = static_r16_check()
    if args.write_result:
        output = Path(__file__).with_name('TURN_ENDPOINT_CHECK.json')
        if output.exists():
            raise SystemExit('refuse to overwrite an existing evidence record')
        output.write_text(json.dumps(result, default=str, ensure_ascii=False, indent=2)+'\n')
    print(json.dumps({'status': result['status'], 'counts': result['counts'], 'scientific_runs': 0}, ensure_ascii=False))
