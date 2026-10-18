"""Offline geometry of pinned SCI plans; no optimizer, dynamics or simulation.

Quarter-turns describe a forward-facing grid-edge direction sequence. They are
not measured robot rotations, motion durations or a continuous-safety proof.
"""
import hashlib
import importlib.util
import json
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCI = '535ee1adf3135ab79565e0b3aa5d189348fe7ab2'


def require(condition, reason):
    if not condition:
        raise ValueError(reason)


def quarter_distance(a, b):
    return min((a-b) % 4, (b-a) % 4)


def path_shape(path, rows, cols, blocked=()):
    require(isinstance(path, list) and path, 'nonempty recorded path required')
    obstacles = set(blocked)
    require(all(type(v) is int and 0 <= v < rows*cols and v not in obstacles for v in path),
            'invalid path vertex')
    moves, waits, turns, first, last = 0, 0, 0, None, None
    for old, new in zip(path, path[1:]):
        if old == new:
            waits += 1
            continue
        edge = (new % cols-old % cols, new // cols-old // cols)
        directions = {(1, 0): 0, (0, 1): 1, (-1, 0): 2, (0, -1): 3}
        require(edge in directions, 'non-four-neighbor recorded move')
        heading = directions[edge]
        moves += 1
        if first is None:
            first = heading
        if last is not None:
            turns += quarter_distance(last, heading)
        last = heading  # Waiting does not invent a new edge direction.
    return {'moves': moves, 'waits': waits, 'internal_quarter_turns': turns,
            'first_direction': first, 'last_direction': last}


def compare(case, result):
    require(result['status'] == 'COMPLETE' and result['final_validated'] is True,
            'completed, validated SCI output required')
    initial, final = case['paths'], result['final_paths']
    require(set(initial) == set(final) == set(case['endpoints']), 'robot coverage mismatch')
    names = ('moves', 'waits', 'internal_quarter_turns')
    before, after = ({k: 0 for k in names} for _ in range(2))
    boundary_bound, changed, agents = 0, [], []
    for agent in sorted(initial, key=int):
        old, new = initial[agent], final[agent]
        start, goal = case['endpoints'][agent]
        require(old[0] == new[0] == start and old[-1] == new[-1] == goal, 'endpoints changed')
        a = path_shape(old, case['rows'], case['cols'], case['blocked'])
        b = path_shape(new, case['rows'], case['cols'], case['blocked'])
        for k in names:
            before[k] += a[k]
            after[k] += b[k]
        if boundary_bound is not None:
            if any(x is None for x in (a['first_direction'], a['last_direction'],
                                       b['first_direction'], b['last_direction'])):
                boundary_bound = None  # No heading inferred for a stationary path.
            else:
                boundary_bound += (quarter_distance(a['first_direction'], b['first_direction'])
                                   + quarter_distance(a['last_direction'], b['last_direction']))
        if old != new:
            changed.append({'agent': int(agent), 'old_cost': len(old)-1, 'new_cost': len(new)-1})
        category = ('unchanged' if old == new else 'equal_cost_reroute' if len(old) == len(new)
                    else 'shorter' if len(new) < len(old) else 'longer')
        start_x, start_y = start % case['cols'], start // case['cols']
        displacement = lambda path: {
            'x': max(abs(v % case['cols']-start_x) for v in path),
            'y': max(abs(v // case['cols']-start_y) for v in path)}
        agents.append({'agent': int(agent), 'category': category,
                       'old_cost': len(old)-1, 'new_cost': len(new)-1,
                       'before': a, 'after': b, 'delta': {k: b[k]-a[k] for k in names},
                       'max_relative_axis_displacement_cells': {
                           'before': displacement(old), 'after': displacement(new)}})
    require(before['moves']+before['waits'] == result['initial_soc']
            and after['moves']+after['waits'] == result['final_soc'], 'SOC decomposition mismatch')
    delta = {k: after[k]-before[k] for k in names}
    turn_delta = delta['internal_quarter_turns']
    groups = {}
    for category in ('unchanged', 'equal_cost_reroute', 'shorter', 'longer'):
        group = [a for a in agents if a['category'] == category]
        groups[category] = {'count': len(group), 'agents': [a['agent'] for a in group],
                           'soc_delta': sum(a['new_cost']-a['old_cost'] for a in group),
                           'delta': {k: sum(a['delta'][k] for a in group) for k in names}}
    extents = {phase: {axis: max(a['max_relative_axis_displacement_cells'][phase][axis]
                                for a in agents) for axis in ('x', 'y')}
               for phase in ('before', 'after')}
    scales = {}
    for phase, axes in extents.items():
        largest = max(axes.values())
        upper = Fraction(8, largest) if largest else None
        scales[phase] = {'lower_m_per_cell': '1/4',
                         'upper_m_per_cell_from_axis_bound': str(upper) if upper is not None else None,
                         'necessary_interval_nonempty': upper is None or upper >= Fraction(1, 4),
                         'assumption': 'Every moving grid edge is one original v2 MOVE, all with one common scale. This tests only the 0.25 m minimum MOVE and 8 m task-relative axis bound.'}
    return {'case': case['id'], 'initial_soc': result['initial_soc'], 'final_soc': result['final_soc'],
            'before': before, 'after': after, 'delta': delta, 'changed_paths': changed,
            'per_agent': agents, 'path_change_groups': groups,
            'max_relative_axis_displacement_cells': extents,
            'v2_one_edge_per_move_necessary_scale_interval': scales,
            'v2_displacement_screen_at_hypothetical_1m_cell': {
                phase: 'FAIL_NECESSARY_AXIS_BOUND' if max(extents[phase].values()) > 8
                else 'AXIS_BOUND_ONLY_NOT_FULL_QUALIFICATION' for phase in extents},
            'boundary_heading_difference_bound_quarters': boundary_bound,
            'total_direction_rotation_delta_interval_quarters': None if boundary_bound is None else
                [turn_delta-boundary_bound, turn_delta+boundary_bound],
            'interpretation': 'Geometry only. Interval allows arbitrary common initial/final headings and shortest heading changes while facing each edge. Reverse driving, smooth dynamics, overlapping turn/wait and multi-robot retiming are not evaluated.'}


def analyze(repo):
    # Reuse the existing fixed Git reader bootstrap; no SCI runtime import.
    spec = importlib.util.spec_from_file_location('_trace_export', HERE/'export_frozen_trace.py')
    exporter = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(exporter)
    reader = exporter.load_reader(repo, json.loads((HERE/'shared.lock.json').read_bytes()))
    lock_raw = (HERE/'sci.lock.json').read_bytes()
    lock = json.loads(lock_raw)
    require(lock['schema'] == 'thesis_sci_path_audit_v1' and lock['commit'] == SCI
            and len(lock['entries']) == 14, 'unexpected SCI evidence lock')
    require(all(pin['commit'] == SCI for pin in lock['entries'].values()), 'mixed SCI commits')
    source_pin = lock['source_contract']
    require(source_pin['commit'] == '16b1ee089be20cafaf4818c3dbb7b259659b021d'
            and source_pin['path'] == 'exploration/spatial_source/COMPOSITION.md',
            'unexpected v2 source contract')
    source_contract = reader.read_blob(repo, source_pin).decode('utf-8')
    require('每个 MOVE 长 .25–3 m' in source_contract
            and '参考相对初点每轴位移≤8 m' in source_contract,
            'declared v2 screening constants do not match the fixed contract')
    raw = {key: reader.read_blob(repo, pin) for key, pin in lock['entries'].items()}
    inputs = json.loads(raw['inputs'])
    summary = json.loads(raw['summary'])
    require(summary['input_sha256'] == hashlib.sha256(raw['inputs']).hexdigest(), 'input identity mismatch')
    rows = []
    for row in summary['rows']:
        job = row['job']['id']
        receipt = json.loads(raw[job+'_receipt'])
        result_raw = raw[job+'_result']
        result = json.loads(result_raw)
        require(receipt['status'] == row['status'] == 'COMPLETE'
                and receipt['job'] == row['job'], 'job/receipt mismatch')
        require(receipt['artifacts']['result.json']['sha256'] == hashlib.sha256(result_raw).hexdigest()
                and row['receipt_sha256'] == hashlib.sha256(raw[job+'_receipt']).hexdigest(),
                'result/receipt hash mismatch')
        case = next(c for c in inputs['cases'] if c['id'] == row['job']['case'])
        require(result['case'] == case['id']
                and result['manifest_sha256'] == summary['manifest_sha256'], 'result identity mismatch')
        rows.append(compare(case, result))
    require(len(rows) == 6, 'six consumed tasks required')
    return {'scope': 'OFFLINE_GEOMETRY_OF_EXISTING_SCI_PLANS', 'new_experiment': False,
            'sci_commit': SCI, 'lock_sha256': hashlib.sha256(lock_raw).hexdigest(),
            'v2_source_contract': source_pin, 'v2_source_model_imported': False,
            'generator_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), 'rows': rows,
            'physical_duration_or_safety_verified': False,
            'boundary_argument': 'For circle distance d and a common boundary heading h, |d(h,u)-d(h,v)| <= d(u,v). Apply at both ends of each moving path and sum. This is a direction-sequence bound, not a vehicle dynamics guarantee.'}


def analyze_details(repo):
    value = analyze(repo)
    # Keep the previous geometry artifact byte-for-byte; this is a finer audit
    # of the same fixed inputs and outputs, never a new optimization run.
    value['scope'] = 'OFFLINE_EQUAL_COST_AND_DISPLACEMENT_AUDIT'
    value['map_scale_metres_per_cell'] = None
    value['displacement_screen_limit'] = ('Only a necessary v2 axis-displacement condition at a hypothetical '
        '1 m/cell scale; no map scale is selected, no automatic scaling or v2 extension. '
        'Primitive lengths/speeds, absolute coordinates, body clearance, synchronous actual '
        'inputs, shared task initial pose and zero wait drift remain unchecked.')
    return value


if __name__ == '__main__':
    value = analyze_details(HERE.parents[1])
    output = HERE/'derived/sci_equal_cost_structure.json'
    with output.open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True)
        stream.write('\n')
    print(json.dumps({'output': str(output), 'sha256': hashlib.sha256(output.read_bytes()).hexdigest(),
                      'cases': len(value['rows']), 'new_experiment': False}))
