"""Three whole-plan motion controls; scientific runs require separate user authority.

Inspect checks frozen bytes only. Run consumes one exclusive case directory and
uses the existing fixed SCI supervisor; no solver, training or world is started.
"""
import time
ENTERED_NS = time.monotonic_ns()
import argparse
import hashlib
import json
from pathlib import Path
import resource
import re
import sys
import types

import nominal_motion as motion
import plan_selection as selection

HERE = Path(__file__).resolve().parent
SCHEMA = 'thesis_nominal_comparison_v1'
SCHEDULER_SCHEMA = 'thesis_scheduler_comparison_v1'
ARMS = ('original', 'frozen_soc', 'turn_aware')
SCHEDULERS = ('global_barrier', 'local_dependency')
SCHEDULER_CASES = ('maze-32-32-2__s01__n16', 'random-32-32-10__s01__n16')
SCHEDULER_ARMS = tuple(a+'__'+s for a in ARMS for s in SCHEDULERS)
RUNTIME = {'compare_nominal_motion.py', 'nominal_motion.py', 'plan_selection.py',
           'inspect_sci_paths.py', 'export_frozen_trace.py', 'sci.lock.json',
           'shared.lock.json', 'plan_selection.lock.json'}
LIMITS = {'total_admission_wall_s': 60, 'final_artifact_reserve_s': 2,
          'worker_cpu_s': 45, 'worker_as_mib': 512, 'per_file_mib': 16,
          'outer_term_s': 62, 'outer_kill_after_s': 2}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_bytes())


def write_json(path, value):
    # The fixed supervisor owns identical exclusive/fsync output semantics.
    import os
    with Path(path).open('x') as stream:
        json.dump(value, stream, indent=2, sort_keys=True, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def load(manifest, expected_sha, repo):
    raw = Path(manifest).read_bytes()
    require(sha(raw) == expected_sha, 'manifest SHA mismatch')
    config = json.loads(raw)
    if config.get('schema') == 'thesis_v2_pair_v1':
        from v2_motion_inputs import load_pair
        return load_pair(config, repo)
    scheduler_comparison = config.get('schema') == SCHEDULER_SCHEMA
    require(config['schema'] in (SCHEMA, SCHEDULER_SCHEMA) and config['authorization'] == 'PENDING_USER',
            'manifest is a proposal, not an authorization')
    require(set(config['runtime_sha256']) == (RUNTIME | {'local_scheduler.py'} if scheduler_comparison else RUNTIME),
            'incomplete runtime/lock pin set')
    require(config['limits'] == LIMITS and config['retries'] == 0
            and config['stop_batch_on_failure'] is True
            and config['sufficient_geometry_rejection_is_retained_result'] is True
            and all(config[k] is False for k in ('new_world', 'training', 'optimizer_search')),
            'fixed budget, zero retry, fail-stop and scope flags required')
    require(re.fullmatch('[a-zA-Z0-9_-]+', config['batch_id']) is not None
            and len(config['cases']) == len(set(config['cases'])) == (2 if scheduler_comparison else 6)
            and all(re.fullmatch('[a-zA-Z0-9_-]+', name) is not None for name in config['cases']),
            'local case and batch IDs required')
    require(config['sci_commit'] == selection.SCI
            and config['source_family'] == 'repair_residual_v1_remaining_bound_NOT_FULL_ADDRESS',
            'unexpected optimizer provenance')
    for name, digest in config['runtime_sha256'].items():
        require(Path(name).name == name and sha((HERE/name).read_bytes()) == digest,
                'runtime/lock changed: '+name)
    require(config['arms'] == list(SCHEDULER_ARMS if scheduler_comparison else ARMS)
            and type(config['initial_heading_quarters']) is int and config['initial_heading_quarters'] == 0,
            'fixed three arms and common initial east heading required')
    if scheduler_comparison:
        from local_scheduler import PAIR_MAX_DEPTH, PAIR_MAX_BOXES
        require(tuple(config['cases']) == SCHEDULER_CASES
                and config['schedulers'] == list(SCHEDULERS)
                and config['old_authorization_reusable'] is False
                and config['error_model_applied'] is False
                and config['author_sadg_reproduction'] is False
                and config['primitive_timing'] == 'RATIONAL_REST_TO_REST_COMMON_TO_BOTH_SCHEDULERS',
                'fixed scheduler scope or selected complete cases changed')
        require(config['checker_policy'] == dict(pair_max_depth=PAIR_MAX_DEPTH,
                pair_max_boxes=PAIR_MAX_BOXES, arithmetic='EXACT_RATIONAL_MONOTONE_INTERVAL_ENCLOSURES'),
                'continuous interval proof policy changed')
    motion.MotionModel(**config['motion_model'])
    exporter = selection._local('_motion_frozen_export', 'export_frozen_trace.py')
    reader = exporter.load_reader(repo, read_json(HERE/'shared.lock.json'))
    lock = read_json(HERE/'sci.lock.json')
    require(lock['commit'] == selection.SCI and len(lock['entries']) == 14,
            'six fixed old SCI tasks required')
    require(all(pin['commit'] == selection.SCI for pin in lock['entries'].values()),
            'mixed optimizer result versions')
    blobs = {key: reader.read_blob(repo, pin) for key, pin in lock['entries'].items()}
    require(sha(blobs['inputs']) == config['input_sha256'], 'input identity mismatch')
    inputs, summary = json.loads(blobs['inputs']), json.loads(blobs['summary'])
    require(summary['input_sha256'] == config['input_sha256'], 'summary input mismatch')
    cases, results = {}, {}
    for row in summary['rows']:
        job = row['job']['id']
        receipt = json.loads(blobs[job+'_receipt'])
        result = json.loads(blobs[job+'_result'])
        require(row['status'] == receipt['status'] == result['status'] == 'COMPLETE'
                and result['final_validated'] is True and receipt['job'] == row['job'],
                'incomplete or mismatched frozen result')
        require(row['receipt_sha256'] == sha(blobs[job+'_receipt'])
                and receipt['artifacts']['result.json']['sha256'] == sha(blobs[job+'_result']),
                'frozen receipt/result digest mismatch')
        case = next(c for c in inputs['cases'] if c['id'] == row['job']['case'])
        require(result['case'] == case['id']
                and result['manifest_sha256'] == summary['manifest_sha256'], 'result identity mismatch')
        require(case['id'] not in cases, 'duplicate case result')
        result['_frozen_provenance'] = {'inputs': lock['entries']['inputs'],
            'summary': lock['entries']['summary'], 'result': lock['entries'][job+'_result'],
            'receipt': lock['entries'][job+'_receipt'], 'source_job': row['job']}
        result['_prior_optimizer_costs'] = {key: receipt[key] for key in
            ('costs', 'supervisor_entry_through_artifact_hash_ns', 'supervisor_self_cpu_s', 'accounting_note')}
        cases[case['id']], results[case['id']] = case, result
    require(len(cases) == 6, 'frozen source case coverage changed')
    if scheduler_comparison:
        require(all(name in cases for name in SCHEDULER_CASES), 'missing frozen scheduler case')
        cases = {name: cases[name] for name in SCHEDULER_CASES}
        results = {name: results[name] for name in SCHEDULER_CASES}
    else:
        require(list(cases) == config['cases'], 'case order/coverage changed')
    pin = config['supervisor_pin']
    require(pin['commit'] == selection.SCI and pin['path'] == 'tracks/sci/run_repair_dev.py',
            'unexpected supervisor source')
    raw_supervisor = reader.read_blob(repo, pin)
    supervisor = types.ModuleType('_motion_fixed_supervisor')
    supervisor.__file__ = pin['commit']+':'+pin['path']
    exec(compile(raw_supervisor, supervisor.__file__, 'exec'), supervisor.__dict__)
    return config, cases, results, supervisor


def motion_metrics(answer):
    """Wait only before actual reference completion; permanent holds excluded."""
    if not answer['certified_nominal_reference']:
        dependency_failure = answer['reason']['kind'].startswith('DEPENDENCY_')
        require(answer['reason']['kind'].startswith('CIRCLE_') or dependency_failure,
                'invalid motion input or schedule: '+str(answer['reason']))
        return {'feasibility': ('LOCAL_CONSTRUCTION_NOT_ESTABLISHED' if dependency_failure
                                else 'SUFFICIENT_SEPARATION_NOT_ESTABLISHED'),
                'collision_claim': False, 'completion_sum_s': None, 'makespan_s': None,
                'wait_sum_s': None, 'reason': answer['reason']}
    schedule = answer['schedule']
    totals = dict(turn_s=0.0, move_s=0.0, wait_sum_s=0.0,
                  turn_barrier_wait_s=0.0, discrete_wait_slot_s=0.0, turn_slot_padding_wait_s=0.0,
                  local_dependency_wait_s=0.0)
    per_agent = {}
    for agent, actions in schedule['agents'].items():
        total, wait = 0.0, 0.0
        for action in actions:
            if action['kind'] == 'GOAL_HOLD':
                require(action['end_s'] is None, 'terminal hold must be permanent')
                continue
            duration = action['end_s']-action['start_s']
            total += duration
            if action['kind'] == 'WAIT':
                wait += duration
                totals['wait_sum_s'] += duration
                key = {'TURN_BARRIER': 'turn_barrier_wait_s',
                       'LOCAL_DEPENDENCY': 'local_dependency_wait_s',
                       'TURN_SLOT_PADDING': 'turn_slot_padding_wait_s',
                       'DISCRETE_WAIT_SLOT': 'discrete_wait_slot_s'}[action['reason']]
                totals[key] += duration
            else:
                totals[{'MOVE': 'move_s', 'TURN': 'turn_s'}[action['kind']]] += duration
        require(abs(total-schedule['completion_s'][agent]) <= 1e-8*max(1.0, total),
                'action/completion partition mismatch')
        per_agent[agent] = {'completion_s': schedule['completion_s'][agent], 'wait_s': wait}
    return {'feasibility': 'CERTIFIED_NOMINAL_REFERENCE', 'collision_claim': False,
            'completion_sum_s': schedule['completion_sum_s'], 'makespan_s': schedule['makespan_s'],
            **totals, 'per_agent': per_agent,
            'permanent_goal_hold_count': len(per_agent), 'goal_hold_in_wait_sum': False}


def compare_plans(problem, initial, optimized, model, headings, emit=None, *, scheduler_comparison=False):
    """No search; frozen optimized plan stays intact even on equal SOC.

    Turn-aware chooses among the two whole plans and one simultaneous retention
    proposal using existing complete checks. It is a control, not turn-optimal
    replanning. It does not select according to the measured motion outcome.
    """
    started = time.monotonic_ns()
    problem.validate(initial, complete=True)
    problem.validate(optimized, complete=True)
    common_validation_ns = time.monotonic_ns()-started
    rows = []
    for arm in ARMS:
        started = time.monotonic_ns()
        if arm == 'turn_aware':
            selected = selection.select_complete_plan(problem, initial, optimized, rule='turn_aware')
            paths = selected.pop('paths')
        else:
            paths = initial if arm == 'original' else optimized
            selected = {'selected': 'incumbent' if arm == 'original' else 'frozen_proposal',
                        'rule': arm, 'search_calls': 0}
        selection_ns = time.monotonic_ns()-started
        for scheduler in (SCHEDULERS if scheduler_comparison else (None,)):
            started = time.monotonic_ns()
            if scheduler_comparison:
                import local_scheduler
                answer = local_scheduler.compile_schedule(problem, paths, model, headings, scheduler)
            else:
                answer = motion.compile_motion(problem, paths, model, headings)
            construction_and_validation_ns = time.monotonic_ns()-started
            started = time.monotonic_ns()
            metrics = motion_metrics(answer)
            row = {'arm': arm+'__'+scheduler if scheduler_comparison else arm,
                   'selection': selected, 'soc': sum(len(p)-1 for p in paths.values()),
                   'grid_makespan': max(len(p)-1 for p in paths.values()), 'metrics': metrics,
                   'motion': answer, 'stage_wall_ns': {
                       'whole_plan_selection': selection_ns if scheduler in (None, SCHEDULERS[0]) else 0,
                       'complete_discrete_and_continuous_checks_and_schedule': construction_and_validation_ns,
                       'metric_validation': time.monotonic_ns()-started}}
            if scheduler_comparison:
                row.update(path_arm=arm, scheduler=scheduler,
                    complete_paths_sha256=sha(json.dumps({str(a): list(p) for a, p in paths.items()},
                                                         sort_keys=True, separators=(',', ':')).encode()),
                    selection_cost_shared_by_scheduler_pair=True)
            rows.append(row)
            if emit is not None:
                emit(row)
    return {'status': 'COMPLETE', 'rows': rows,
            'common_initial_and_optimized_validation_ns': common_validation_ns,
            'comparison_scope': ('FIXED_PATH_GLOBAL_VS_CONSERVATIVE_LOCAL_DEPENDENCY'
                                  if scheduler_comparison else 'NOMINAL_SHARED_PHASE_BARRIER_CONTROL'),
            'independent_performance_experiment': False, 'optimizer_called': False,
            'v2_applied': False, 'learning_used': False,
            'limits': ['Global barriers add conservative waiting; no optimal scheduling claim.',
                       *(['Both schedulers use a new common rational primitive timing; do not subtract old 18-arm seconds.',
                          'Local sweep serialization may cycle or be more conservative; other schedules may exist.',
                          'This project fixed-order control is not a full SADG reproduction or feedback execution.']
                         if scheduler_comparison else []),
                       'Circle separation failure is inconclusive about rectangular-body collision.',
                       'Motion parameters are synthetic declarations, not measured LIMO parameters.',
                       'No unmodeled per-robot timing delays, tracking disturbance or feedback controller.']}


def execute_worker(config, case, source, output, repo, load_ns):
    if config.get('schema') == 'thesis_v2_pair_v1':
        from v2_motion_inputs import execute_pair_worker
        return execute_pair_worker(config, case, source, output, repo, load_ns, ENTERED_NS)
    started = time.monotonic_ns()
    Grid = selection.load_grid_problem(repo)
    endpoints = {int(a): tuple(p) for a, p in case['endpoints'].items()}
    problem = Grid(case['rows'], case['cols'], case['blocked'], endpoints)
    initial = {int(a): tuple(p) for a, p in case['paths'].items()}
    optimized = {int(a): tuple(p) for a, p in source['final_paths'].items()}
    require(sum(len(p)-1 for p in initial.values()) == source['initial_soc']
            and sum(len(p)-1 for p in optimized.values()) == source['final_soc'], 'source SOC mismatch')
    model = motion.MotionModel(**config['motion_model'])
    headings = {agent: config['initial_heading_quarters'] for agent in problem.ids}
    setup_ns = time.monotonic_ns()-started
    arm_io_ns = {}
    def emit(row):
        started = time.monotonic_ns()
        write_json(output/('arm_'+row['arm']+'.json'), row)
        arm_io_ns[row['arm']] = time.monotonic_ns()-started
    value = compare_plans(problem, initial, optimized, model, headings, emit=emit,
                          scheduler_comparison=config.get('schema') == SCHEDULER_SCHEMA)
    # Each full reference is already saved; keep the task summary small.
    for row in value['rows']:
        row.pop('motion')
    value.update({'case': case['id'], 'sci_commit': selection.SCI,
                  'source_family': 'repair_residual_v1_remaining_bound_NOT_FULL_ADDRESS',
                  'input_provenance': source['_frozen_provenance'],
                  'prior_optimizer_costs_not_new_run': source['_prior_optimizer_costs'],
                  'arm_serialization_and_fsync_ns': arm_io_ns,
                  'manifest_sha256': config['manifest_sha256'], 'motion_model': model.record(),
                  'initial_headings_quarters': headings,
                  'load_and_pinned_evidence_validation_ns': load_ns,
                  'validator_import_and_problem_setup_ns': setup_ns,
                  'worker_entry_through_before_result_write_ns': time.monotonic_ns()-ENTERED_NS})
    write_json(output/'result.json', value)


def run(args, config, cases, results, supervisor):
    require(args.case in config['cases'], 'unknown case')
    require(args.authorization_reference and len(args.authorization_reference.strip()) >= 8,
            'record actual user authority; a file or flag cannot grant it')
    batch = HERE/'results'/config['batch_id']
    # Previous attempts must be complete; an incomplete/missing result stops the
    # batch and no later command may silently skip or retry it.
    for case in config['cases'][:config['cases'].index(args.case)]:
        prior = read_json(batch/case/'receipt.json')
        require(prior['status'] == 'COMPLETE' and prior['manifest_sha256'] == args.sha256,
                'earlier case failed or is incomplete: batch stopped')
    output = batch/args.case
    output.mkdir(parents=True, exist_ok=False)
    write_json(output/'attempt.json', {'case': args.case, 'status': 'CONSUMED_ONCE',
        'manifest_sha256': args.sha256, 'authorization_reference': args.authorization_reference,
        'retry_allowed': False})
    remaining = config['limits']['total_admission_wall_s']-(time.monotonic_ns()-ENTERED_NS)/1e9
    require(remaining > config['limits']['final_artifact_reserve_s'], 'preflight exhausted admission budget')
    command = [sys.executable, '-B', str(Path(__file__).resolve()), '_worker',
               '--manifest', str(Path(args.manifest).resolve()), '--sha256', args.sha256,
               '--case', args.case, '--output', str(output)]
    costs = supervisor.supervise(command, output,
        wall_s=remaining-config['limits']['final_artifact_reserve_s'],
        cpu_s=config['limits']['worker_cpu_s'], memory_mib=config['limits']['worker_as_mib'])
    artifacts = {p.name: {'sha256': sha(p.read_bytes()), 'bytes': p.stat().st_size}
                 for p in sorted(output.iterdir()) if p.is_file()}
    payload = None
    try:
        payload = read_json(output/'result.json')
    except (ValueError, OSError):
        pass
    elapsed = time.monotonic_ns()-ENTERED_NS
    accepted = (costs['exit_code'] == 0 and not costs['forced_cleanup']
        and payload is not None and payload.get('status') == 'COMPLETE'
        and payload.get('manifest_sha256') == args.sha256 and payload.get('case') == args.case
        and [row['arm'] for row in payload.get('rows', [])] == config['arms']
        and elapsed <= config['limits']['total_admission_wall_s']*1e9)
    usage = resource.getrusage(resource.RUSAGE_SELF)
    status = 'COMPLETE' if accepted else 'FAILED_OR_INCOMPLETE'
    write_json(output/'receipt.json', {'status': status, 'case': args.case,
        'manifest_sha256': args.sha256, 'artifacts': artifacts, 'worker_costs': costs,
        'entry_through_import_input_validation_output_and_hash_ns': elapsed,
        'supervisor_self_cpu_s': usage.ru_utime+usage.ru_stime,
        'accounting': 'Total includes Git reads, imports, selection, all geometry/construction, metric checks, result serialization, fsync, artifact hashes, and supervisor wait. Administrative receipt write and final process exit excluded. Nested times are not additive. Prior SCI optimization cost is source metadata, not this motion-adaptation cost.',
        'retry_allowed': False, 'new_scientific_motion_comparison': True})
    print(json.dumps({'case': args.case, 'status': status, 'output': str(output)}))
    return 0 if accepted else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('inspect', 'run', '_worker'))
    parser.add_argument('--manifest', type=Path, required=True)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--case')
    parser.add_argument('--authorization-reference')
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    started = time.monotonic_ns()
    config, cases, results, supervisor = load(args.manifest, args.sha256, HERE.parents[1])
    config['manifest_sha256'] = args.sha256
    load_ns = time.monotonic_ns()-started
    if args.mode == 'inspect':
        print(json.dumps({'status': 'FROZEN_BYTES_VALIDATED_NO_MOTION_COMPARISON',
                          'cases': config['cases'], 'sci_commit': selection.SCI,
                          'motion_model': config['motion_model'], 'authorization': 'PENDING_USER'}))
        return 0
    if args.mode == '_worker':
        execute_worker(config, cases[args.case], results[args.case], args.output, HERE.parents[1], load_ns)
        return 0
    return run(args, config, cases, results, supervisor)


if __name__ == '__main__':
    raise SystemExit(main())
