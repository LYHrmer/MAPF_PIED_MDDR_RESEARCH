"""One fixed static qualification of support geometry and analytic MOVE bounds.

No task session, new feedback, simulation, author planner or scientific run.
"""
import argparse
import hashlib
import json
from fractions import Fraction as Q
from pathlib import Path

from interface import Box
from run_timed import BASE, HOME, inputs, verify_inputs, dump
from verify_qualified import verify_qualification_pins
from verify_integration import module
from departure_constraints import relative_hull
from support_constraints import bounded_vertices, pair_upper, region_upper, cruise_upper


def check():
    checks = []

    def need(value, label):
        if not value:
            raise AssertionError(label)
        checks.append(label)

    pins = {'frozen': verify_inputs(), 'qualification': verify_qualification_pins()}
    source = HOME/'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source'
    composition = module('composition', source/'composition.py')
    module('timed', source/'timed.py')
    support = module('support', source/'support.py')
    module('composition_constraints', BASE/'composition_constraints.py')
    constraints = module('timed_constraints', BASE/'timed_constraints.py')
    frozen = json.loads((BASE/'DEPARTURE_CHECK.json').read_text())
    for path, digest in frozen['input_sha256'].items():
        need(hashlib.sha256(Path(path).read_bytes()).hexdigest() == digest,
             'prior_departure_input_unchanged_'+path)
    base, config = inputs()
    problem = constraints.make_problem(base, config, 2)
    old = {(r['tail'], r['head']): r for r in frozen['records']}
    h = composition.H
    need(support.rotation_upper(1, 0) == 1+h**4/24, 'concave_interior_rotation_extremum')
    need(support.rotation_upper(-1, 0) == -1+h*h/2, 'convex_endpoint_rotation_extremum')
    need(support.rotation_upper(0, 1) == h+h**3/6, 'linear_rotation_extremum')
    need(support.rotation_upper(1, h/2) == 1+h*h/8+h**4/24+h**4/12,
         'nonzero_stationary_rotation_extremum')
    try:
        support.rotation_upper(1., 0)
    except ValueError:
        checks.append('float_rotation_rejected')
    else:
        raise AssertionError('float rotation accepted')

    square = [(-1, 0, 0), (1, 0, 1), (0, -1, 0), (0, 1, 1)]
    v, _ = bounded_vertices(square)
    need(set(v) == {(0, 0), (0, 1), (1, 0), (1, 1)}, 'exact_square_vertices')
    v, _ = bounded_vertices(square+[(1, 1, 1)])
    need(set(v) == {(0, 0), (0, 1), (1, 0)}, 'clipped_polygon_vertices')
    need(not bounded_vertices(square+[(1, 0, -1)])[0], 'empty_bounded_polygon')
    need(bounded_vertices(square+[(1, 1, 0)])[0] == [(0, 0)], 'degenerate_point_retained')

    # Finite regression points use higher-order rational trig enclosures. The
    # continuous proof is the quadratic remainder + convex support argument.
    def trig(delta):
        x = abs(delta)
        sl = x-x**3/6+x**5/120-x**7/5040
        su = x-x**3/6+x**5/120
        cl = 1-x*x/2+x**4/24-x**6/720
        cu = cl+x**8/40320
        return ((sl, su) if delta >= 0 else (-su, -sl)), (cl, cu)

    regression = {r: support.JointTrajectory(r, t.chain) for r, t in problem['trajectories'].items()}
    for r, tr in regression.items():
        for index, action in enumerate(tr.chain.primitives):
            begin = tr.offsets[index]
            end = begin+(action.duration or 0)
            box = tr.action_box(index, begin, end)
            coarse = problem['trajectories'][r].action_box(index, begin, end)
            need(box[0] >= coarse[0] and box[1] <= coarse[1] and box[2] >= coarse[2]
                 and box[3] <= coarse[3], 'never_looser_'+r+str(index))
            if action.kind == 'TURN':
                need(box == coarse, 'frozen_continuous_turn_'+r+str(index))
                continue
            hx, hy = (Q('.3'), Q('.1')) if action.heading % 2 == 0 else (Q('.1'), Q('.3'))
            bx, by = (Q('.02'), Q('.01')) if tr.chain.heading % 2 == 0 else (Q('.01'), Q('.02'))
            for point in (action.start, action.end):
                for ux in (-hx, hx):
                    for uy in (-hy, hy):
                        x, y = point[0]-tr.chain.origin[0]+ux, point[1]-tr.chain.origin[1]+uy
                        for delta in (-h, Q(0), h):
                            sine, cosine = trig(delta)
                            xs = [x*c-y*s for c in cosine for s in sine]
                            ys = [x*s+y*c for c in cosine for s in sine]
                            need(box[0] <= tr.chain.origin[0]-bx+min(xs)
                                 and tr.chain.origin[0]+bx+max(xs) <= box[1]
                                 and box[2] <= tr.chain.origin[1]-by+min(ys)
                                 and tr.chain.origin[1]+by+max(ys) <= box[3],
                                 'rational_body_vertex_'+r+str(index)+str((point, ux, uy, delta)))
    a, b = regression['A'], regression['B']
    need(a.action_box(2, Q('8.5'), Q('8.5'))[3] > Q('.314'), 'two_metre_prefix_not_reset_at_turn')
    need(cruise_upper(a, 0, b, 0, Q(2), Q(0), Q(2), Q('.78')) is None,
         'noncruise_inverse_must_fallback')

    def fresh():
        return {r: support.JointTrajectory(r, t.chain) for r, t in problem['trajectories'].items()}

    tree, pair, region = fresh(), fresh(), fresh()
    records = []
    for tail, head in problem['graph']['new_or_retained']:
        ra, ia = problem['finite'][tail]
        rb, ib = problem['finite'][head]
        prior = old[tail, head]
        projected = relative_hull(problem['intervals'][tail], problem['intervals'][head],
                                 lambda lo, hi: Box(*tree[ra].action_box(ia, lo, hi)),
                                 lambda lo, hi: Box(*tree[rb].action_box(ib, lo, hi)),
                                 resolution=Q(config['phase_resolution']),
                                 max_cells=config['certificate_max_cells'])
        need(projected['window'] is None or projected['window'][1] <= Q(prior['window'][1]),
             'no_looser_pair_upper_'+tail+head)
        coupled = pair_upper(pair[ra], ia, pair[rb], ib)
        ba = Box(*region[ra].action_box(ia, *problem['intervals'][tail]))
        bb = Box(*region[rb].action_box(ib, *problem['intervals'][head]))
        if ba.separated(bb):
            independent = {'status': 'CERTIFIED_EMPTY', 'upper': None, 'operations': {}}
        else:
            common = Box(max(ba.xmin, bb.xmin), min(ba.xmax, bb.xmax),
                         max(ba.ymin, bb.ymin), min(ba.ymax, bb.ymax))
            independent = region_upper(region[ra], ia, region[rb], ib, common)
        old_upper = Q(prior['window'][1])
        # These are added refinements of the frozen construction, not a claim
        # that its construction cost disappears from a complete implementation.
        pair_final = min(old_upper, coupled['upper']) if coupled['upper'] is not None else old_upper
        region_final = min(old_upper, independent['upper']) if independent['upper'] is not None else old_upper
        if coupled['status'] == 'CERTIFIED_EMPTY':
            pair_final = None
        if independent['status'] == 'CERTIFIED_EMPTY':
            region_final = None
        records.append({'tail': tail, 'head': head, 'old_upper': old_upper,
                        'joint_tree': projected, 'pair_analytic': coupled,
                        'region_analytic': independent, 'pair_refined_upper': pair_final,
                        'region_refined_upper': region_final})
    old_upper = Q(frozen['new_ordered_upper'])
    order = Q(frozen['original_END_order_lower'])
    bounds = {'old': max(order, old_upper),
              'joint_tree': max([order]+[r['joint_tree']['window'][1] for r in records
                                        if r['joint_tree']['window'] is not None]),
              'pair_analytic': max([order]+[r['pair_refined_upper'] for r in records
                                            if r['pair_refined_upper'] is not None]),
              'region_analytic': max([order]+[r['region_refined_upper'] for r in records
                                              if r['region_refined_upper'] is not None])}
    improved = min(bounds.values())
    witness = (improved+old_upper)/2 if improved < old_upper else None
    if witness is not None:
        need(witness > order and improved < witness < old_upper, 'strict_safe_ray_geometry_witness')
    # The existing received packet yields this interval, NOT an earlier packet.
    need(Q('9.345') > max(bounds.values()), 'existing_feedback_still_equal_at_9_45')
    for name in ('joint_tree', 'pair_analytic', 'region_analytic'):
        need(bounds[name] >= Q(80999801, 46875000), 'retains_prior_collision_lower_bound_'+name)
    paths = [source/n for n in ('composition.py', 'timed.py', 'support.py')]
    paths += [BASE/n for n in ('support_constraints.py', 'verify_support.py', 'DEPARTURE_CHECK.json',
                              'departure_constraints.py', 'composition_fixture.json', 'timed_fixture.json')]
    return {'status': 'STATIC_SUPPORT_CHECK_PASS', 'records': records, 'checks': checks,
            'ordered_upper_bounds': bounds, 'geometric_safe_ray_witness': witness,
            'witness_is_feedback_release': False, 'same_fixed_feedback_release': True,
            'source_operations': {name: {r: dict(tr.operations) for r, tr in arm.items()}
                                  for name, arm in [('joint_tree', tree), ('pair_analytic', pair), ('region_analytic', region)]},
            'frozen_construction_work_not_removed': frozen['operations'],
            'whole_process_cost_advantage': 'UNKNOWN_NOT_BENCHMARKED',
            'external_baseline_advantage': 'NOT_ESTABLISHED_STANDARD_SUPPORT_HALFPLANE_ADAPTATION',
            'successor_run_gate': 'NOT_PASSED', 'input_pins_reused': pins,
            'input_sha256': {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},
            'scientific_runs': 0, 'world_steps': 0, 'training': 0, 'task_session_calls': 0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--write-result', action='store_true')
    args = parser.parse_args()
    try:
        receipt = check()
    except Exception as exc:
        receipt = {'status': 'STATIC_SUPPORT_CHECK_FAILED', 'error': type(exc).__name__,
                   'detail': str(exc), 'scientific_runs': 0, 'task_session_calls': 0}
        if args.write_result:
            with (BASE/'SUPPORT_CHECK.json').open('x') as f:
                f.write(dump(receipt)+'\n')
        print(dump(receipt))
        raise
    if args.write_result:
        with (BASE/'SUPPORT_CHECK.json').open('x') as f:
            f.write(dump(receipt)+'\n')
    print(dump({k: v for k, v in receipt.items() if k not in ('records', 'checks', 'input_sha256')}))
