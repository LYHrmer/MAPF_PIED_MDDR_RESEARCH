"""Whole-plan motion controls and objective acceptance; runs require user authority.

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
ACCEPTANCE_SCHEMA = 'thesis_motion_acceptance_v1'
INITIAL_CERTIFICATION_SCHEMA = 'thesis_initial_motion_certification_v1'
ADDRESS_CANDIDATE_COMMIT = 'f9c651ad0680679cf99a4973f722b65fd6f7aa97'
ACCEPTANCE_CASES = ('maze-32-32-2__s05__n32', 'random-32-32-10__s05__n32')
ACCEPTANCE_ARMS = ('full_recompute', 'primitive_lower_bound')
ACCEPTANCE_ARM_WALL_S = 20
ACCEPTANCE_ARM_OUTPUT_RESERVE_S = 2
ARMS = ('original', 'frozen_soc', 'turn_aware')
SCHEDULERS = ('global_barrier', 'local_dependency')
SCHEDULER_CASES = ('maze-32-32-2__s01__n16', 'random-32-32-10__s01__n16')
SCHEDULER_ARMS = tuple(a+'__'+s for a in ARMS for s in SCHEDULERS)
RUNTIME = {'compare_nominal_motion.py', 'nominal_motion.py', 'plan_selection.py',
           'inspect_sci_paths.py', 'export_frozen_trace.py', 'sci.lock.json',
           'shared.lock.json', 'plan_selection.lock.json'}
ACCEPTANCE_RUNTIME = {'compare_nominal_motion.py', 'nominal_motion.py', 'plan_selection.py',
    'export_frozen_trace.py', 'shared.lock.json', 'plan_selection.lock.json',
    'local_scheduler.py', 'motion_acceptance.lock.json'}
LIMITS = {'total_admission_wall_s': 60, 'final_artifact_reserve_s': 2,
          'worker_cpu_s': 45, 'worker_as_mib': 512, 'per_file_mib': 16,
          'outer_term_s': 62, 'outer_kill_after_s': 2}
INITIAL_CERTIFICATION_LIMITS = {'total_admission_wall_s': 26, 'final_artifact_reserve_s': 2,
    'worker_cpu_s': 24, 'worker_as_mib': 512, 'per_file_mib': 16,
    'outer_term_s': 28, 'outer_kill_after_s': 2}


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


def load_acceptance(config, repo):
    """Byte-only fixed ADDRESS input/output adapter; does not build a schedule."""
    initial_only = config['schema'] == INITIAL_CERTIFICATION_SCHEMA
    require(config['authorization'] == 'PENDING_USER'
            and config['limits'] == (INITIAL_CERTIFICATION_LIMITS if initial_only else LIMITS)
            and config['retries'] == 0
            and config['stop_batch_on_failure'] is True
            and config['sufficient_geometry_rejection_is_retained_result'] is True
            and config['old_authorization_reusable'] is False
            and all(config[k] is False for k in ('new_world', 'training', 'optimizer_search')),
            'fixed motion-acceptance budget and proposal scope required')
    require(config['candidate_sci_commit'] == ADDRESS_CANDIDATE_COMMIT
            and config['sci_commit'] == selection.SCI
            and config['source_family'] == ('FROZEN_ADDRESS_INITIAL_ONLY_NO_CANDIDATE_EVALUATION'
                                           if initial_only else 'FROZEN_ADDRESS_CANDIDATES_NO_NEW_SEARCH')
            and config['cases'] == list(ACCEPTANCE_CASES)
            and config['arms'] == (['initial_certification'] if initial_only else list(ACCEPTANCE_ARMS))
            and config['arm_evaluation_wall_s'] == ACCEPTANCE_ARM_WALL_S
            and config['arm_output_reserve_s'] == ACCEPTANCE_ARM_OUTPUT_RESERVE_S
            and config['candidate_order'] == ([] if initial_only else ['all', 'acceptance_eligible'])
            and config['initial_heading_quarters'] == 0
            and type(config['initial_heading_quarters']) is int,
            'fixed source, candidate order, motion arms and per-arm budget required')
    if initial_only:
        require(config['stage'] == 'INITIAL_CERTIFICATION_ONLY'
                and config['initial_certification_failure_stops_batch'] is True
                and config['candidate_evaluations_allowed'] == 0
                and config['maximum_external_total_wall_s'] == 60,
                'initial-only scope, strict certification stop and total guard required')
    require(re.fullmatch('[a-zA-Z0-9_-]+', config['batch_id']) is not None,
            'local batch id required')
    require(set(config['runtime_sha256']) == ACCEPTANCE_RUNTIME, 'incomplete acceptance runtime pins')
    for name, digest in config['runtime_sha256'].items():
        require(Path(name).name == name and sha((HERE/name).read_bytes()) == digest,
                'runtime/lock changed: '+name)
    motion.MotionModel(**config['motion_model'])
    exporter = selection._local('_motion_acceptance_export', 'export_frozen_trace.py')
    reader = exporter.load_reader(repo, read_json(HERE/'shared.lock.json'))
    lock = read_json(HERE/'motion_acceptance.lock.json')
    require(lock['schema'] == 'thesis_frozen_address_motion_candidates_v1'
            and lock['commit'] == ADDRESS_CANDIDATE_COMMIT and len(lock['entries']) == 10
            and lock['cases'] == list(ACCEPTANCE_CASES)
            and lock['candidate_order'] == ['all', 'acceptance_eligible']
            and all(p['commit'] == ADDRESS_CANDIDATE_COMMIT for p in lock['entries'].values()),
            'unexpected ADDRESS candidate lock')
    # Initial feasibility must not load or evaluate the frozen final candidates.
    selected_pins = {'inputs': lock['entries']['inputs']} if initial_only else lock['entries']
    blobs = {key: reader.read_blob(repo, pin) for key, pin in selected_pins.items()}
    require(sha(blobs['inputs']) == config['input_sha256'], 'frozen ADDRESS input SHA mismatch')
    inputs = json.loads(blobs['inputs'])
    summary = None if initial_only else json.loads(blobs['summary'])
    cases, sources = {}, {}
    for name in ACCEPTANCE_CASES:
        case = next(c for c in inputs['cases'] if c['id'] == name)
        if initial_only:
            cases[name] = case
            sources[name] = dict(initial_sci_commit=ADDRESS_CANDIDATE_COMMIT,
                input_pin=lock['entries']['inputs'], scope='INITIAL_PLAN_ONLY_NO_FINAL_CANDIDATES',
                source_protocol_deviation=lock['source_protocol_deviation'])
            continue
        candidates, costs = [], {}
        for mode in config['candidate_order']:
            job = name+'__seed0__'+mode
            result, receipt = (json.loads(blobs[job+suffix]) for suffix in ('_result', '_receipt'))
            row = next(r for r in summary['jobs'] if r['job'] == job)
            require(row['status'] == receipt['status'] == result['status'] == 'COMPLETE'
                    and result['final_validated'] is True and result['case'] == name
                    and receipt['manifest_sha256'] == result['manifest_sha256'] == summary['manifest_sha256']
                    and row['receipt_sha256'] == sha(blobs[job+'_receipt'])
                    and receipt['artifacts']['result.json']['sha256'] == sha(blobs[job+'_result']),
                    'frozen ADDRESS result/receipt identity mismatch')
            require(sum(len(p)-1 for p in result['final_paths'].values()) == result['final_soc']
                    and sum(len(p)-1 for p in case['paths'].values()) == result['initial_soc'],
                    'frozen ADDRESS path costs mismatch')
            candidates.append(dict(label=mode, paths=result['final_paths'],
                source_result=lock['entries'][job+'_result'], source_receipt=lock['entries'][job+'_receipt']))
            costs[mode] = receipt.get('costs', receipt.get('worker_costs'))
        cases[name] = case
        sources[name] = dict(candidates=candidates, prior_optimizer_costs_not_new_run=costs,
            candidate_sci_commit=ADDRESS_CANDIDATE_COMMIT,
            source_protocol_deviation=lock['source_protocol_deviation'],
            input_pin=lock['entries']['inputs'], summary_pin=lock['entries']['summary'])
    pin = config['supervisor_pin']
    require(pin['commit'] == selection.SCI and pin['path'] == 'tracks/sci/run_repair_dev.py',
            'unexpected fixed supervisor source')
    raw = reader.read_blob(repo, pin)
    supervisor = types.ModuleType('_motion_acceptance_fixed_supervisor')
    supervisor.__file__ = pin['commit']+':'+pin['path']
    exec(compile(raw, supervisor.__file__, 'exec'), supervisor.__dict__)
    return config, cases, sources, supervisor


def load(manifest, expected_sha, repo):
    raw = Path(manifest).read_bytes()
    require(sha(raw) == expected_sha, 'manifest SHA mismatch')
    config = json.loads(raw)
    if config.get('schema') in (ACCEPTANCE_SCHEMA, INITIAL_CERTIFICATION_SCHEMA):
        return load_acceptance(config, repo)
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


def evaluate_motion_candidates(problem, initial, candidates, model, headings, *, budget,
                               expired_exception, use_lower_bound):
    """One real transaction path, used by the scientific worker and fixtures."""
    selector = selection.MotionPlanSelector(problem, initial, model, headings,
        budget=budget, expired_exception=expired_exception)
    initial_snapshot = selector.snapshot()
    attempts, status = [], 'COMPLETE'
    for index, candidate in enumerate(candidates):
        result = selector.consider(candidate['paths'], label=candidate['label'],
                                   use_lower_bound=use_lower_bound)
        attempts.append(result)
        if result['status'] in ('BUDGET_CENSORED', 'IMPLEMENTATION_FAILED'):
            if result['status'] == 'IMPLEMENTATION_FAILED':
                status = 'FAILED'
            for later in candidates[index+1:]:
                attempts.append(dict(label=later['label'], status='NOT_ATTEMPTED_AFTER_STOP'))
            break
    final = selector.snapshot()
    return dict(status=status, initial=initial_snapshot, final=final, attempts=attempts,
        objective='EXACT_SUM_COMPLETION_TIMES_LOCAL_DEPENDENCY',
        selected_within_supplied_set_only=True, optimizer_called=False,
        budget_stage_wall_ns=dict(budget.stage_wall_ns), budget_stage_cpu_ns=dict(budget.stage_cpu_ns),
        cpu_budget_enforcement='OUTER_PROCESS_RLIMIT_ONLY_NOT_COOPERATIVE_SOFT_CPU',
        hard_realtime_claim=False, common_end_received=False)


def execute_acceptance_worker(config, case, source, output, repo, load_ns):
    """Fixed ADDRESS candidates, equal wall allowance per acceptance policy."""
    setup_start = time.monotonic_ns()
    modules = selection.load_fixed_sci_components(repo)
    Grid, Budget = modules['address_backend'].GridProblem, modules['pp_repair'].SharedBudget
    Expired = modules['pp_repair']._Expired
    problem = Grid(case['rows'], case['cols'], case['blocked'],
                   {int(a): tuple(p) for a, p in case['endpoints'].items()})
    initial = {int(a): tuple(p) for a, p in case['paths'].items()}
    candidates = [dict(label=c['label'], paths={int(a): tuple(p) for a, p in c['paths'].items()})
                  for c in source['candidates']]
    model = motion.MotionModel(**config['motion_model'])
    headings = {a: config['initial_heading_quarters'] for a in problem.ids}
    setup_ns = time.monotonic_ns()-setup_start
    rows, arm_io, status = [], {}, 'COMPLETE'
    for arm in ACCEPTANCE_ARMS:
        if status != 'COMPLETE':
            rows.append(dict(arm=arm, status='NOT_RUN_AFTER_HARD_FAILURE'))
            continue
        started, cpu = time.monotonic_ns(), time.process_time_ns()
        budget = Budget(started+config['arm_evaluation_wall_s']*10**9, 0)
        try:
            # All construction, initial certification, candidate checks and
            # commit polls share this one absolute deadline for the arm.
            value = evaluate_motion_candidates(problem, initial, candidates, model, headings,
                budget=budget, expired_exception=Expired,
                use_lower_bound=arm == 'primitive_lower_bound')
        except (Expired, TimeoutError) as error:
            value = dict(status='FAILED', final=None, attempts=[],
                reason=dict(kind='INITIAL_NOT_CERTIFIED_BEFORE_DEADLINE', detail=str(error)))
        except Exception as error:
            value = dict(status='FAILED', final=None, attempts=[],
                reason=dict(kind='INITIAL_CERTIFICATION_FAILED', detail=type(error).__name__+': '+str(error)))
        value.update(arm=arm, evaluation_wall_ns=time.monotonic_ns()-started,
            evaluation_cpu_ns=time.process_time_ns()-cpu,
            budget_stage_wall_ns=dict(budget.stage_wall_ns), budget_stage_cpu_ns=dict(budget.stage_cpu_ns))
        io_start = time.monotonic_ns()
        write_json(output/('arm_'+arm+'.json'), value)
        arm_io[arm] = time.monotonic_ns()-io_start
        admitted = time.monotonic_ns()-started <= (
            config['arm_evaluation_wall_s']+config['arm_output_reserve_s'])*10**9
        row = dict(arm=arm, status=value['status'] if admitted else 'FAILED',
            arm_output_within_reserve=admitted, attempts=value['attempts'],
            initial_objective_exact_s=value.get('initial', {}).get('objective_exact_s'),
            final_objective_exact_s=(value['final']['objective_exact_s'] if value.get('final') else None),
            final_paths_sha256=(value['final']['paths_sha256'] if value.get('final') else None),
            complete_certified_incumbent_retained=value.get('final') is not None,
            evaluation_wall_ns=value['evaluation_wall_ns'], evaluation_cpu_ns=value['evaluation_cpu_ns'],
            arm_entry_through_output_ns=time.monotonic_ns()-started,
            budget_stage_wall_ns=value['budget_stage_wall_ns'],
            budget_stage_cpu_ns=value['budget_stage_cpu_ns'])
        if value.get('reason'):
            row['reason'] = value['reason']
        rows.append(row)
        if row['status'] != 'COMPLETE':
            status = 'FAILED'
    result = dict(status=status, case=case['id'], rows=rows,
        manifest_sha256=config['manifest_sha256'], candidate_provenance=source,
        validator_budget_supervisor_commit=selection.SCI,
        candidate_sci_commit=ADDRESS_CANDIDATE_COMMIT,
        source_family='FROZEN_ADDRESS_CANDIDATES_NO_NEW_SEARCH',
        optimizer_called=False, v2_applied=False, common_end_received=False,
        load_and_pinned_evidence_validation_ns=load_ns, validator_import_and_problem_setup_ns=setup_ns,
        arm_serialization_and_fsync_ns=arm_io,
        worker_entry_through_before_result_write_ns=time.monotonic_ns()-ENTERED_NS,
        accounting='Each arm includes its own initial certificate and transaction work. Common fixed-source load/setup, output, hashing and process supervision are charged in the case total. Nested stage costs are not additive. Previous optimizer costs are provenance only.',
        scope='SOFTWARE_IMPLEMENTED_SUPPLIED_CANDIDATE_ACCEPTANCE_NOT_END_TO_END_ADDRESS_SEARCH')
    write_json(output/'result.json', result)


def execute_initial_certification_worker(config, case, source, output, repo, load_ns,
                                         case_deadline_ns):
    """Only certify the supplied initial plan; no candidate access or selection."""
    setup_started, setup_cpu = time.monotonic_ns(), time.process_time_ns()
    budget, snapshot, failure = None, None, None
    Expired, current_stage = TimeoutError, 'FIXED_COMPONENTS_AND_PROBLEM_SETUP'
    evaluation_started = evaluation_cpu = None
    setup_ns = setup_cpu_ns = 0
    evaluation_ns = evaluation_cpu_ns = 0
    deadline_ns, available_ns = None, None
    try:
        require(type(case_deadline_ns) is int and case_deadline_ns > 0,
                'the parent absolute admission deadline is required')
        require('candidates' not in source, 'initial-only worker must not receive candidate plans')
        modules = selection.load_fixed_sci_components(repo)
        Grid, Budget = modules['address_backend'].GridProblem, modules['pp_repair'].SharedBudget
        Expired = modules['pp_repair']._Expired
        problem = Grid(case['rows'], case['cols'], case['blocked'],
                       {int(a): tuple(p) for a, p in case['endpoints'].items()})
        initial = {int(a): tuple(p) for a, p in case['paths'].items()}
        model = motion.MotionModel(**config['motion_model'])
        headings = {a: config['initial_heading_quarters'] for a in problem.ids}
        setup_ns, setup_cpu_ns = time.monotonic_ns()-setup_started, time.process_time_ns()-setup_cpu
        current_stage = 'INITIAL_CERTIFICATION_TRANSACTION'
        evaluation_started, evaluation_cpu = time.monotonic_ns(), time.process_time_ns()
        # Preserve 2s worker output and 2s parent validation/hash. Slow setup can
        # only REDUCE the initial transaction's <=20s, never enlarge it.
        deadline_ns = min(evaluation_started+config['arm_evaluation_wall_s']*10**9,
            case_deadline_ns-(config['arm_output_reserve_s']+
                              config['limits']['final_artifact_reserve_s'])*10**9)
        available_ns = max(0, deadline_ns-evaluation_started)
        budget = Budget(deadline_ns, 0)
        selector = selection.MotionPlanSelector(problem, initial, model, headings,
            budget=budget, expired_exception=Expired)
        evaluation_ns = time.monotonic_ns()-evaluation_started
        evaluation_cpu_ns = time.process_time_ns()-evaluation_cpu
        current_stage = 'CERTIFIED_STATE_EXPORT'
        snapshot = selector.snapshot()
    except Exception as error:
        if evaluation_started is not None:
            evaluation_ns = time.monotonic_ns()-evaluation_started
            evaluation_cpu_ns = time.process_time_ns()-evaluation_cpu
        else:
            setup_ns = time.monotonic_ns()-setup_started
            setup_cpu_ns = time.process_time_ns()-setup_cpu
        certificate_reason = getattr(error, 'reason', None)
        expected_noncertificate = (isinstance(error, selection.InitialMotionCertificationError)
            and isinstance(certificate_reason, dict)
            and certificate_reason.get('kind', '').startswith(('DEPENDENCY_', 'CIRCLE_')))
        kind = ('INITIAL_BUDGET_CENSORED' if isinstance(error, (Expired, TimeoutError))
                else 'INITIAL_CERTIFICATE_NOT_ESTABLISHED' if expected_noncertificate
                else 'IMPLEMENTATION_FAILED')
        failure = dict(kind=kind, stage=current_stage, detail=type(error).__name__+': '+str(error),
                       certificate_reason=certificate_reason,
                       first_failed_motion_stage=getattr(budget, 'motion_first_failed_stage', None),
                       certified_fallback_available=False)
    stage_wall = {} if budget is None else dict(budget.stage_wall_ns)
    stage_cpu = {} if budget is None else dict(budget.stage_cpu_ns)
    value = dict(status='COMPLETE' if snapshot is not None else 'FAILED',
        diagnostic_completed=True, initial_certified=snapshot is not None,
        certified_initial=snapshot, failure=failure, candidate_evaluations=0, new_search_calls=0,
        initial_evaluation_wall_ns=evaluation_ns, initial_evaluation_cpu_ns=evaluation_cpu_ns,
        configured_initial_evaluation_limit_ns=config['arm_evaluation_wall_s']*10**9,
        actual_initial_available_ns=available_ns, initial_deadline_ns=deadline_ns,
        parent_admission_deadline_ns=case_deadline_ns,
        stage_wall_ns=stage_wall, stage_cpu_ns=stage_cpu,
        validator_import_and_problem_setup_ns=setup_ns, validator_import_and_problem_setup_cpu_ns=setup_cpu_ns,
        cpu_budget_enforcement='OUTER_PROCESS_RLIMIT_ONLY', hard_realtime_claim=False,
        common_end_received=False, scope='INITIAL_CERTIFICATION_BUDGET_FEASIBILITY_ONLY')
    io_started = time.monotonic_ns()
    write_json(output/'initial_certification.json', value)
    io_ns = time.monotonic_ns()-io_started
    within_worker_tail = type(case_deadline_ns) is int and time.monotonic_ns() <= (
        case_deadline_ns-config['limits']['final_artifact_reserve_s']*10**9)
    row = dict(arm='initial_certification', status=value['status'] if within_worker_tail else 'FAILED',
        diagnostic_completed=True, initial_certified=value['initial_certified'], failure=failure,
        output_within_worker_tail=within_worker_tail, candidate_evaluations=0, new_search_calls=0,
        initial_evaluation_wall_ns=evaluation_ns, initial_evaluation_cpu_ns=evaluation_cpu_ns,
        actual_initial_available_ns=available_ns,
        exact_objective_s=None if snapshot is None else snapshot['objective_exact_s'],
        certified_paths_sha256=None if snapshot is None else snapshot['paths_sha256'],
        stage_wall_ns=stage_wall, stage_cpu_ns=stage_cpu)
    result = dict(status=row['status'], case=case['id'], rows=[row],
        manifest_sha256=config['manifest_sha256'], initial_provenance=source,
        diagnostic_completed=True, initial_certified=row['initial_certified'],
        candidate_evaluations=0, optimizer_called=False, new_search_calls=0, v2_applied=False,
        performance_comparison=False, following_gain_comparison_authorized=False,
        load_and_pinned_evidence_validation_ns=load_ns, validator_import_and_problem_setup_ns=setup_ns,
        initial_artifact_serialization_and_fsync_ns=io_ns,
        worker_entry_through_before_result_write_ns=time.monotonic_ns()-ENTERED_NS,
        parent_admission_deadline_ns=case_deadline_ns,
        scope='INITIAL_CERTIFICATION_BUDGET_FEASIBILITY_ONLY',
        accounting='Input/Git/import/problem setup is charged in case total, outside the <=20s initial selector transaction. Selector snapshot/construction/full certification/private-state serialization shares one absolute deadline. Detached certificate export, result IO and hashes use the reserved tail. Nested costs are not additive.')
    write_json(output/'result.json', result)


def execute_worker(config, case, source, output, repo, load_ns, *, case_deadline_ns=None):
    if config.get('schema') == INITIAL_CERTIFICATION_SCHEMA:
        return execute_initial_certification_worker(config, case, source, output, repo, load_ns,
                                                    case_deadline_ns)
    if config.get('schema') == ACCEPTANCE_SCHEMA:
        return execute_acceptance_worker(config, case, source, output, repo, load_ns)
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
    if config['schema'] == INITIAL_CERTIFICATION_SCHEMA:
        command += ['--case-deadline-ns',
                    str(ENTERED_NS+config['limits']['total_admission_wall_s']*10**9)]
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
    receipt = {'status': status, 'case': args.case,
        'manifest_sha256': args.sha256, 'artifacts': artifacts, 'worker_costs': costs,
        'entry_through_import_input_validation_output_and_hash_ns': elapsed,
        'supervisor_self_cpu_s': usage.ru_utime+usage.ru_stime,
        'accounting': 'Total includes Git reads, imports, selection, all geometry/construction, metric checks, result serialization, fsync, artifact hashes, and supervisor wait. Administrative receipt write and final process exit excluded. Nested times are not additive. Prior SCI optimization cost is source metadata, not this motion-adaptation cost.',
        'retry_allowed': False, 'new_scientific_motion_comparison': True}
    if config['schema'] == INITIAL_CERTIFICATION_SCHEMA:
        receipt.update(new_scientific_motion_comparison=False,
            new_scientific_initial_certification=True,
            diagnostic_completed=bool(payload and payload.get('diagnostic_completed')),
            initial_certified=bool(payload and payload.get('initial_certified')),
            candidate_evaluations=0, following_gain_comparison_authorized=False,
            initial_budget_feasible_at_this_observation=accepted,
            any_initial_certification_failure_stops_batch=True)
    write_json(output/'receipt.json', receipt)
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
    parser.add_argument('--case-deadline-ns', type=int)
    args = parser.parse_args()
    started = time.monotonic_ns()
    config, cases, results, supervisor = load(args.manifest, args.sha256, HERE.parents[1])
    config['manifest_sha256'] = args.sha256
    load_ns = time.monotonic_ns()-started
    if args.mode == 'inspect':
        value = {'status': 'FROZEN_BYTES_VALIDATED_NO_MOTION_COMPARISON',
                 'cases': config['cases'], 'sci_commit': selection.SCI,
                 'motion_model': config['motion_model'], 'authorization': 'PENDING_USER'}
        if config['schema'] in (ACCEPTANCE_SCHEMA, INITIAL_CERTIFICATION_SCHEMA):
            value.update(candidate_sci_commit=config['candidate_sci_commit'],
                initial_motion_certification_cost='UNKNOWN',
                status='PINNED_ADDRESS_INPUT_INTERFACE_ONLY_NO_MOTION_COMPARISON')
        if config['schema'] == INITIAL_CERTIFICATION_SCHEMA:
            value.update(stage='INITIAL_CERTIFICATION_ONLY', candidate_evaluations=0,
                         status='PINNED_INITIAL_INPUT_ONLY_NO_CERTIFICATION_OR_SEARCH')
        print(json.dumps(value))
        return 0
    if args.mode == '_worker':
        execute_worker(config, cases[args.case], results[args.case], args.output, HERE.parents[1], load_ns,
                       case_deadline_ns=args.case_deadline_ns)
        return 0
    return run(args, config, cases, results, supervisor)


if __name__ == '__main__':
    raise SystemExit(main())
