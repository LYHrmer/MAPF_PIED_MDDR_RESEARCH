"""Small SHA-bound R16 input projection for the existing motion comparison runner.

Prepare/load perform static discrete checks only. The explicit worker is a new
scientific comparison; it must run under a newly authorized finite manifest.
"""
from fractions import Fraction as Q
import json
from pathlib import Path
import sys
import tempfile
import time
import types

import export_frozen_trace as frozen
import plan_selection as selection
import v2_motion as v2

HERE = Path(__file__).resolve().parent
ARMS = ['zero_initial_pose_error', 'propagated_initial_pose_error']
CASES = ['r16_ids13', 'r16_ids013']
LIMITS = {'total_admission_wall_s': 15, 'final_artifact_reserve_s': 1,
          'worker_cpu_s': 10, 'worker_as_mib': 512, 'per_file_mib': 16,
          'outer_term_s': 20, 'outer_kill_after_s': 2}
RUNTIME = {'compare_nominal_motion.py', 'nominal_motion.py', 'v2_motion.py', 'v2_motion_inputs.py',
           'plan_selection.py', 'export_frozen_trace.py', 'shared.lock.json', 'plan_selection.lock.json'}


def module(reader, repo, pin, name):
    raw = reader.read_blob(repo, pin)
    result = types.ModuleType(name)
    result.__file__ = pin['commit']+':'+pin['path']
    previous = sys.modules.get(name)
    sys.modules[name] = result
    try:
        exec(compile(raw, result.__file__, 'exec'), result.__dict__)
    finally:
        if previous is None:
            sys.modules.pop(name, None)
        else:
            sys.modules[name] = previous
    return result


def reader_and_pins(repo):
    lock = json.loads((HERE/'shared.lock.json').read_bytes())
    reader = frozen.load_reader(repo, lock)
    manifest = json.loads(reader.read_blob(repo, lock['manifest']))
    return reader, {name: manifest['modules'][name] for name in ('preexecution_input', 'composition')}


def check_source_contract(contract):
    expected = {'condition': 'joint_initial_se2_stopped_primitives_v2',
                'model': 'ideal_unicycle_identical_reference_actual_inputs',
                'task_initial_local_box': ['.02', '.01', '.002'], 'body_half': ['.3', '.1'],
                'speed': '.5', 'acceleration': '1', 'omega': '.5', 'alpha': '1',
                'move_length': ['.25', '3'], 'turn_slot_seconds': '4',
                'reference_displacement_axis_limit': '8', 'reference_coordinate_limit': '10',
                'stop_at_each_action_boundary': True, 'hold_drift': '0'}
    if any(contract.get(k) != value for k, value in expected.items()):
        raise ValueError('source v2 contract changed')
    checks = ((v2.SPEED_M_S, contract['speed']), (v2.ACCEL_M_S2, contract['acceleration']),
              (v2.DECEL_M_S2, contract['acceleration']), (v2.TURN_SPEED_RAD_S, contract['omega']),
              (v2.TURN_ACCEL_RAD_S2, contract['alpha']), (v2.TURN_DECEL_RAD_S2, contract['alpha']),
              (v2.TURN_QUARTER_SLOT_S, contract['turn_slot_seconds']),
              (v2.INITIAL_HEADING_BOUND_RAD, contract['task_initial_local_box'][2]),
              (v2.INITIAL_POSE_BOUND_X_M, contract['task_initial_local_box'][0]),
              (v2.INITIAL_POSE_BOUND_Y_M, contract['task_initial_local_box'][1]),
              (v2.NUMERIC_MARGIN_M, contract['numerical_reserve']),
              (v2.BODY_LENGTH_M/2, contract['body_half'][0]),
              (v2.BODY_WIDTH_M/2, contract['body_half'][1]))
    if any(actual != Q(expected) for actual, expected in checks):
        raise ValueError('motion adapter does not match pinned source parameters')


def load_r16_projection(reader, repo, pin, selected, r16):
    # The frozen adapter hashes its own __file__. Materialize only these verified
    # small source bytes temporarily, never point it at a mutable worktree HEAD.
    with tempfile.TemporaryDirectory(prefix='thesis-v2-input-') as directory:
        path = Path(directory)/'preexecution_input.py'
        path.write_bytes(reader.read_blob(repo, pin))
        adapter = module(reader, repo, pin, '_thesis_fixed_r16_input')
        adapter.__file__ = str(path)
        return adapter.load_r16_dev(selected, r16_dir=r16)


def prepare():
    """No trajectory construction: read, project and qualify complete paths."""
    from compare_nominal_motion import write_json, sha
    repo = HERE.parents[1]
    target = HERE/'config'/'v2_motion_pair_v1_manifest.json'
    inputs_path = HERE/'config'/'v2_motion_pair_v1_inputs.json'
    if target.exists() or inputs_path.exists() or (HERE/'results'/'v2_motion_pair_v1').exists():
        raise FileExistsError('preserve proposal/attempts; no automatic regeneration')
    reader, pins = reader_and_pins(repo)
    source = module(reader, repo, pins['composition'], '_thesis_fixed_v2_source')
    check_source_contract(source.contract())  # Does not build Chain or Plant.
    Grid = selection.load_grid_problem(repo)
    r16 = Path('/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/sadg_preflight_20261004_r16')
    cases = []
    for name, selected in zip(CASES, ((1, 3), (0, 1, 3))):
        old = load_r16_projection(reader, repo, pins['preexecution_input'], selected, r16)
        cols, rows = old['map_dimensions']
        # A common translation, not reflection: reference (x,y) -> (x,y-8).
        # Grid row=8-y and nominal y=-row preserve E/N/W/S and all displacements.
        paths = {int(agent[5:]): [(rows-1-p['y'])*cols+p['x'] for p in path]
                 for agent, path in old['grid_paths'].items()}
        endpoints = {agent: [path[0], path[-1]] for agent, path in paths.items()}
        blocked = [(rows-1-y)*cols+x for x, y in old['blocked_cells']]
        problem = Grid(rows, cols, blocked, endpoints)
        qualification = v2.static_qualification(problem, paths)
        if not qualification['qualified']:
            raise ValueError('preselected complete R16 path fails v2 static bounds')
        # The frozen input adapter chooses the first edge direction as initial
        # heading. Preserve it explicitly rather than changing it between arms.
        headings = {int(agent[5:]): old['specs'][agent]['heading'] for agent in old['specs']}
        cases.append({'id': name, 'rows': rows, 'cols': cols, 'blocked': blocked,
            'paths': paths, 'endpoints': endpoints, 'initial_headings': headings,
            'static_qualification': qualification, 'source': old['source'],
            'coordinate_translation_m': ['0', str(-(rows-1))],
            'data_class': 'RELATED_R16_DEV_PROJECTIONS_NOT_INDEPENDENT_TASKS',
            'continuous_comparison_executed': False})
    bundle = {'cases': cases, 'source_pins': pins, 'source_contract': source.contract(),
              'generator_sha256': sha(Path(__file__).read_bytes()),
              'motion_compared': False, 'new_initial_search': False}
    write_json(inputs_path, bundle)
    old_manifest = json.loads((HERE/'config'/'nominal_motion_v1_manifest.json').read_bytes())
    config = {'schema': 'thesis_v2_pair_v1', 'batch_id': 'v2_motion_pair_v1',
        'authorization': 'PENDING_USER', 'cases': CASES, 'arms': ARMS, 'limits': LIMITS,
        'runtime_sha256': {name: sha((HERE/name).read_bytes()) for name in RUNTIME},
        'input_file': inputs_path.name, 'input_sha256': sha(inputs_path.read_bytes()),
        'source_pins': pins, 'supervisor_pin': old_manifest['supervisor_pin'],
        'sci_commit': selection.SCI, 'motion_model': v2.V2_MODEL.record(),
        'retries': 0, 'stop_batch_on_failure': True,
        'sufficient_geometry_rejection_is_retained_result': True,
        'new_world': False, 'training': False, 'optimizer_search': False,
        'physical_END': False, 'previous_authorization_reusable': False}
    write_json(target, config)
    load_pair(config, repo)
    print(json.dumps({'manifest_sha256': sha(target.read_bytes()), 'input_sha256': config['input_sha256'],
                      'cases': CASES, 'motion_compared': False}))


def load_pair(config, repo):
    from compare_nominal_motion import require, sha
    require(config['authorization'] == 'PENDING_USER' and config['cases'] == CASES
            and config['arms'] == ARMS and config['limits'] == LIMITS and config['retries'] == 0,
            'fixed proposal cases/arms/budget required')
    require(config['stop_batch_on_failure'] is True and
            config['sufficient_geometry_rejection_is_retained_result'] is True and
            all(config[k] is False for k in ('new_world', 'training', 'optimizer_search', 'physical_END',
                                            'previous_authorization_reusable')), 'scope/stop flags changed')
    require(set(config['runtime_sha256']) == RUNTIME, 'runtime pin closure mismatch')
    for name, expected in config['runtime_sha256'].items():
        require(sha((HERE/name).read_bytes()) == expected, 'changed runtime '+name)
    require(Path(config['input_file']).name == config['input_file'], 'local input basename required')
    raw = (HERE/'config'/config['input_file']).read_bytes()
    require(sha(raw) == config['input_sha256'], 'changed complete paths')
    bundle = json.loads(raw)
    reader, pins = reader_and_pins(repo)
    require(config['source_pins'] == bundle['source_pins'] == pins, 'fixed source pins changed')
    source = module(reader, repo, pins['composition'], '_thesis_fixed_v2_source')
    require(bundle['source_contract'] == source.contract(), 'source contract record changed')
    check_source_contract(source.contract())
    require(config['motion_model'] == v2.V2_MODEL.record() and config['sci_commit'] == selection.SCI,
            'model or validator version changed')
    cases = {case['id']: case for case in bundle['cases']}
    require(list(cases) == CASES, 'case order/coverage mismatch')
    Grid = selection.load_grid_problem(repo)
    for case in cases.values():
        problem = Grid(case['rows'], case['cols'], case['blocked'],
                       {int(a): tuple(p) for a, p in case['endpoints'].items()})
        qualification = v2.static_qualification(problem, {int(a): tuple(p) for a, p in case['paths'].items()})
        require(qualification == case['static_qualification'] and qualification['qualified'],
                'static eligibility changed')
    pin = config['supervisor_pin']
    require(pin['commit'] == selection.SCI and pin['path'] == 'tracks/sci/run_repair_dev.py',
            'unexpected supervisor version')
    supervisor = module(reader, repo, pin, '_thesis_v2_fixed_supervisor')
    return config, cases, cases, supervisor


def execute_pair_worker(config, case, source, output, repo, load_ns, entered_ns):
    from compare_nominal_motion import motion_metrics, require, write_json
    started = time.monotonic_ns()
    Grid = selection.load_grid_problem(repo)
    problem = Grid(case['rows'], case['cols'], case['blocked'],
                   {int(a): tuple(p) for a, p in case['endpoints'].items()})
    paths = {int(a): tuple(p) for a, p in case['paths'].items()}
    headings = {int(a): h for a, h in case['initial_headings'].items()}
    setup_ns = time.monotonic_ns()-started
    started = time.monotonic_ns()
    pair = v2.compile_v2_pair(problem, paths, headings)
    pair_ns = time.monotonic_ns()-started
    require(pair['status'] in ('CERTIFIED_V2_PAIR', 'SUFFICIENT_SEPARATION_NOT_ESTABLISHED'),
            'invalid pair construction: '+str(pair.get('reason')))
    rows, io_ns = [], {}
    for arm in ARMS:
        answer = pair['arms'][arm]
        metrics = motion_metrics(answer)
        if answer['certified_nominal_reference']:
            metrics['feasibility'] = ('CERTIFIED_ZERO_ERROR_REFERENCE' if arm == ARMS[0]
                                      else 'CERTIFIED_INITIAL_POSE_ENCLOSURE')
        row = {'arm': arm, 'metrics': metrics, 'motion': answer}
        started = time.monotonic_ns()
        write_json(output/('arm_'+arm+'.json'), row)
        io_ns[arm] = time.monotonic_ns()-started
        row.pop('motion')
        rows.append(row)
    pair.pop('arms')
    value = {'status': 'COMPLETE', 'case': case['id'], 'rows': rows, 'pair': pair,
        'manifest_sha256': config['manifest_sha256'], 'input_provenance': case['source'],
        'coordinate_translation_m': case['coordinate_translation_m'],
        'data_class': case['data_class'], 'sci_validator_commit': selection.SCI,
        'common_end_received': False, 'optimizer_called': False,
        'load_and_static_evidence_validation_ns': load_ns,
        'validator_and_problem_setup_ns': setup_ns,
        'pair_qualification_construction_and_all_checks_ns': pair_ns,
        'arm_serialization_and_fsync_ns': io_ns,
        'worker_entry_before_result_write_ns': time.monotonic_ns()-entered_ns}
    write_json(output/'result.json', value)


if __name__ == '__main__':
    prepare()
