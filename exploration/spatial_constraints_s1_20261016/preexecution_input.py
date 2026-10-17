"""SHA-bound R16 complete-path DEV projections, with no solver/source imports.

load_r16_dev reads and validates the frozen four-agent source before selecting
two or three complete paths. It does not construct OrderContract, evaluate a
trajectory, check continuous occupancy, run a planner, or issue an END receipt.
The one-metre adaptation is explicit; source t is discrete order, never seconds.
There are no noise, scale, path-slice, or motion-parameter override arguments.
"""
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
import hashlib
import json
import re


STAGED_SHA256 = 'e24af3c1c95fe57f7512f5d3ed6826f3ec4007b27ddc69c879cea30624487f13'
MAP_SHA256 = 'c8b4344b62e77fb7dbe9029fc2173749f72631e7ce63a7a0b0d71d11a18ab656'
AUTHOR_COMMIT = 'c2626d996121a9d6c128844a167b917db24418ac'
ROBOT_IDS = ('agent0', 'agent1', 'agent2', 'agent3')
DIRECTIONS = ((1, 0), (0, 1), (-1, 0), (0, -1))
DATA_CLASS = 'R16_DERIVED_DEV_NOT_INDEPENDENT_TEST'


def _read_bound(path, expected):
    raw = path.read_bytes()
    if hashlib.sha256(raw).hexdigest() != expected:
        raise ValueError('frozen source SHA256 mismatch: '+str(path))
    return raw


def _frozen_map(raw):
    """Read only the SHA-verified author's exact block layout, not general YAML.

    The staged JSON contains resolution metadata but no obstacle list. This
    narrow parser avoids a new YAML dependency and rejects unconsumed content.
    """
    text = raw.decode('utf-8')
    header = re.fullmatch(
        r'agents:\n(.*?)map:\n  dimensions:\n  - (\d+)\n  - (\d+)\n'
        r'  obstacles:\n(.*)', text, flags=re.DOTALL)
    if header is None:
        raise ValueError('unexpected frozen author map layout')
    agent_text, width, height, obstacle_text = header.groups()
    agent_pattern = re.compile(
        r'- goal:\n  - (\d+)\n  - (\d+)\n  name: (agent\d+)\n'
        r'  start:\n  - (\d+)\n  - (\d+)\n')
    agent_matches = list(agent_pattern.finditer(agent_text))
    if ''.join(m.group(0) for m in agent_matches) != agent_text:
        raise ValueError('unconsumed author agent declaration')
    agents = {}
    for match in agent_matches:
        gx, gy, name, sx, sy = match.groups()
        if name in agents:
            raise ValueError('duplicate author agent')
        agents[name] = {'start': (int(sx), int(sy)), 'goal': (int(gx), int(gy))}
    obstacle_pattern = re.compile(r'  - - (\d+)\n    - (\d+)\n')
    obstacle_matches = list(obstacle_pattern.finditer(obstacle_text))
    if ''.join(m.group(0) for m in obstacle_matches) != obstacle_text:
        raise ValueError('unconsumed author obstacle declaration')
    blocked = tuple((int(m[1]), int(m[2])) for m in obstacle_matches)
    dimensions = int(width), int(height)
    if (set(agents) != set(ROBOT_IDS) or dimensions != (9, 9)
            or len(set(blocked)) != len(blocked)
            or any(not 0 <= p[j] < dimensions[j] for p in blocked for j in (0, 1))):
        raise ValueError('unexpected or invalid frozen map data')
    return agents, dimensions, blocked


def _selected_ids(selected):
    if not isinstance(selected, (list, tuple)) or len(selected) not in (2, 3):
        raise ValueError('explicit two/three distinct original robot IDs required')
    ids = []
    for item in selected:
        name = 'agent'+str(item) if type(item) is int else item
        if not isinstance(name, str) or name not in ROBOT_IDS or name in ids:
            raise ValueError('robot IDs must be distinct agent0..agent3 (or integers 0..3)')
        ids.append(name)
    return tuple(sorted(ids))


def _validate_paths(staged, agents, dimensions, blocked):
    if (not isinstance(staged, dict) or staged.get('name') != 'official_test_staged'
            or staged.get('data_class') != 'official_test_fixture'
            or not isinstance(staged.get('solution'), dict)):
        raise ValueError('unexpected frozen staged input identity')
    paths = staged['solution'].get('schedule')
    if not isinstance(paths, dict) or set(paths) != set(ROBOT_IDS):
        raise ValueError('all four complete source paths are required before projection')
    blocked = set(blocked)
    for robot, rows in paths.items():
        if not isinstance(rows, list) or len(rows) < 2:
            raise ValueError('missing complete path for '+robot)
        for index, row in enumerate(rows):
            if (not isinstance(row, dict) or set(row) != {'x', 'y', 't'}
                    or any(type(row[k]) is not int for k in ('x', 'y', 't'))
                    or row['t'] != index):
                raise ValueError('consecutive integer discrete visits required for '+robot)
            point = row['x'], row['y']
            if (point in blocked or any(not 0 <= point[j] < dimensions[j] for j in (0, 1))
                    or any(abs(point[j]) > 10 or abs(point[j]-agents[robot]['start'][j]) > 8
                           for j in (0, 1))):
                raise ValueError('path outside free cells or original v2 8m/10m domain')
            if index:
                step = row['x']-rows[index-1]['x'], row['y']-rows[index-1]['y']
                if step == (0, 0):
                    # R16 has none. Integer source t does not define physical
                    # WAIT seconds; a different input needs an explicit mapping.
                    raise ValueError('source WAIT has no declared physical mapping in frozen R16')
                if step not in DIRECTIONS:
                    raise ValueError('source path must use unmerged unit cardinal steps')
        if ((rows[0]['x'], rows[0]['y']) != agents[robot]['start']
                or (rows[-1]['x'], rows[-1]['y']) != agents[robot]['goal']):
            raise ValueError('cropped or changed source start/goal for '+robot)
    # Static source validity only: this is not continuous v2 collision checking.
    for index in range(max(len(rows) for rows in paths.values())):
        positions = {r: (rows[min(index, len(rows)-1)]['x'],
                         rows[min(index, len(rows)-1)]['y']) for r, rows in paths.items()}
        if len(set(positions.values())) != len(paths):
            raise ValueError('source discrete vertex conflict with terminal holds')
        if index:
            previous = {r: (rows[min(index-1, len(rows)-1)]['x'],
                            rows[min(index-1, len(rows)-1)]['y']) for r, rows in paths.items()}
            if any(previous[a] == positions[b] and previous[b] == positions[a]
                   for a, b in combinations(ROBOT_IDS, 2)):
                raise ValueError('source discrete head-on edge conflict')
    return paths


def _adapt_path(rows):
    first = rows[1]['x']-rows[0]['x'], rows[1]['y']-rows[0]['y']
    initial_heading = heading = DIRECTIONS.index(first)
    actions, trace = [], []

    def append(kind, argument, first_visit, last_visit, next_heading):
        a, b = rows[first_visit], rows[last_visit]
        index = len(actions)
        actions.append([kind, argument])
        trace.append({'primitive_index': index, 'kind': kind,
                      'start_vertex': [a['x'], a['y']], 'end_vertex': [b['x'], b['y']],
                      'source_step': first_visit if kind != 'HOLD' else None,
                      'source_time': a['t'], 'source_time_end': b['t'],
                      'source_visit_index': first_visit, 'source_visit_end_index': last_visit,
                      'heading_before': heading, 'heading_after': next_heading,
                      'source_time_unit': 'DISCRETE_ORDER_INDEX_NOT_SECONDS'})

    for index, (a, b) in enumerate(zip(rows, rows[1:])):
        direction = DIRECTIONS.index((b['x']-a['x'], b['y']-a['y']))
        change = (direction-heading) % 4
        if change == 2:
            raise ValueError('frozen R16 adapter has no declared half-turn mapping')
        if change:
            sign = 1 if change == 1 else -1
            append('TURN', sign, index, index, direction)
            heading = direction
        append('MOVE', '1', index, index+1, heading)
    append('HOLD', '0', len(rows)-1, len(rows)-1, heading)
    return {'origin': [str(rows[0]['x']), str(rows[0]['y'])],
            'heading': initial_heading, 'actions': actions}, trace


def load_r16_dev(selected_ids, *, r16_dir=None, author_dir=None):
    """Return specs/map and discrete provenance for a full 2/3-agent DEV task.

    Locations may change, bytes may not. specs/world_bounds/obstacles match
    compile_schedule's input schema. grid_paths and action_trace support a
    later explicit order declaration; this loader never infers safe groups.
    Original R16 contains no WAIT. Any scheduled WAIT is introduced separately
    at an original stopped boundary, without resetting task parameters.
    """
    selected = _selected_ids(selected_ids)
    root = (Path(r16_dir) if r16_dir is not None else
            Path(__file__).resolve().parent.parent/'error_guidance'/'sadg_preflight_20261004_r16')
    author = (Path(author_dir) if author_dir is not None else
              Path.home()/'.cache'/'mapf_research'/'sadg-controller-c2626d9')
    staged_path = root/'inputs'/'official_test_staged.json'
    map_path = author/'sadg_controller'/'data'/'ecbs'/'test.yaml'
    staged = json.loads(_read_bound(staged_path, STAGED_SHA256))
    agents, dimensions, blocked = _frozen_map(_read_bound(map_path, MAP_SHA256))
    paths = _validate_paths(staged, agents, dimensions, blocked)
    adapted = {robot: _adapt_path(paths[robot]) for robot in ROBOT_IDS}
    specs = {robot: adapted[robot][0] for robot in selected}
    trace = {robot: adapted[robot][1] for robot in selected}
    selected_paths = {r: [dict(row) for row in paths[r]] for r in selected}
    half = Q(1, 2)
    obstacles = [[str(Q(x)-half), str(Q(x)+half), str(Q(y)-half), str(Q(y)+half)]
                 for x, y in blocked]
    world = [str(-half), str(dimensions[0]-half), str(-half), str(dimensions[1]-half)]
    projections = {
        label: [{'id': 'r16_dev__'+'__'.join(ids), 'selected_ids': list(ids),
                 'data_class': DATA_CLASS, 'selection_basis': 'ALL_LEXICOGRAPHIC_SUBSETS'}
                for ids in combinations(ROBOT_IDS, count)]
        for label, count in (('two_robot', 2), ('three_robot', 3))}
    source = {
        'data_class': DATA_CLASS, 'author_url': 'https://github.com/alexberndt/sadg-controller',
        'author_commit': AUTHOR_COMMIT, 'license': 'AGPL-3.0',
        'staged_input': {'path': str(staged_path.resolve()), 'sha256': STAGED_SHA256},
        'author_map': {'path': str(map_path.resolve()), 'sha256': MAP_SHA256},
        'adapter_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'specs_sha256': hashlib.sha256(json.dumps(specs, sort_keys=True,
                                                  separators=(',', ':')).encode()).hexdigest(),
        'visit_mapping_sha256': hashlib.sha256(json.dumps(
            {'grid_paths': selected_paths, 'action_trace': trace}, sort_keys=True,
            separators=(',', ':')).encode()).hexdigest(),
        'selected_ids': list(selected), 'all_original_ids': list(ROBOT_IDS),
        'scale_metres_per_grid_unit': '1', 'coordinate_offsets': ['0', '0'],
        'original_scale_metadata_ignored': staged['dimensions'],
        'original_horizon_not_used_as_physical_time': staged['horizon'],
        'source_t_semantics': 'DISCRETE_ORDER_ONLY_NOT_SECONDS_OR_DEADLINES',
        'obstacle_semantics': 'CLOSED_UNIT_SQUARES_CENTERED_AT_ORIGINAL_BLOCKED_CELLS',
        'source_condition': 'joint_initial_se2_stopped_primitives_v2',
        'motion_mapping': 'EACH_GRID_EDGE_IS_OWN_STOPPED_1M_MOVE_QUARTER_TURNS_PERMANENT_HOLD',
        'uncertainty_mapping': 'ORIGINAL_TASK_INITIAL_PARAMETERS_NO_RESET_OR_OVERRIDES',
        'source_discrete_paths_validated': True, 'continuous_safety_checked': False,
        'group_admissibility': 'NOT_CHECKED', 'physical_END_received': False,
    }
    return {'specs': specs, 'world_bounds': world, 'obstacles': obstacles,
            'grid_paths': selected_paths,
            'action_trace': trace, 'source': source, 'all_projections': projections,
            'map_dimensions': list(dimensions), 'blocked_cells': [list(p) for p in blocked]}
