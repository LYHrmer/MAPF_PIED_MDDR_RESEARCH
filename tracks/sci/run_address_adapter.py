"""One explicitly authorized common-initial ADDRESS job; inspect performs no search.

Uses the existing group supervisor and common GridProblem final validator.
An immutable manifest is a proposal, never permission. Every attempted job owns
an exclusive output directory, including failure/timeout; no retries.
"""
import time
ENTERED_NS = time.monotonic_ns()
import argparse
import json
import math
import os
from pathlib import Path
import re
import resource
import subprocess
import sys

from run_repair_dev import digest, supervise, unpack, write_json
from address_backend import AUTHOR

HERE = Path(__file__).resolve().parent


def comparison_settings(config, job):
    """Explicit opt-in; old manifests never silently acquire a new policy."""
    protocol = config.get('comparison_protocol')
    if protocol is None:
        if 'seed_admission' in job or 'effort_mode' in job:
            raise ValueError('seed/effort settings require comparison protocol')
        return None
    if protocol != 'seed_admission_v1' or config.get('variant') != 'budget_guard':
        raise ValueError('unsupported seed comparison protocol')
    if config.get('attempt_trace', False) or config.get('phase_profile', False):
        raise ValueError('seed comparison uses matched unprofiled, untraced arms')
    policy, mode = job.get('seed_admission'), job.get('effort_mode')
    if policy not in ('all', 'positive_delay') or mode not in ('fixed_repairs', 'total_budget'):
        raise ValueError('explicit seed admission and effort mode required')
    iterations = job.get('iterations')
    if (type(iterations) is not int or
            (mode == 'fixed_repairs' and iterations < 1) or
            (mode == 'total_budget' and iterations != 0)):
        raise ValueError('repair cap must be positive for fixed work and zero for total budget')
    return policy, mode


def load(path, expected_sha):
    path = Path(path).resolve()
    raw = path.read_bytes()
    if digest(raw) != expected_sha:
        raise ValueError('manifest SHA mismatch')
    config = json.loads(raw)
    if config['schema'] != 'address_common_initial_dev_v1' or config['authorization'] != 'PENDING_USER':
        raise ValueError('proposal schema required; authorization is external')
    receipt_name = config.get('build_receipt', 'adapter_build_receipt.json')
    if not isinstance(receipt_name, str) or Path(receipt_name).name != receipt_name:
        raise ValueError('build receipt must be a local basename')
    variant = config.get('variant', 'base')
    scopes = {'base': 'ADDRESS_COMMON_INITIAL_ADAPTER_COMPILE_AND_HELP_ONLY',
              'loop_guard': 'ADDRESS_COMMON_INITIAL_LOOP_GUARD_COMPILE_AND_HELP_ONLY',
              'budget_guard': 'ADDRESS_COMMON_INITIAL_BUDGET_GUARD_COMPILE_AND_HELP_ONLY'}
    if variant not in scopes:
        raise ValueError('unreviewed runner variant')
    if type(config.get('attempt_trace', False)) is not bool:
        raise ValueError('attempt_trace must be boolean')
    if config.get('attempt_trace', False) and variant != 'budget_guard':
        raise ValueError('attempt trace requires the shared budget baseline')
    if type(config.get('phase_profile', False)) is not bool:
        raise ValueError('phase_profile must be boolean')
    if config.get('phase_profile', False) and (variant != 'budget_guard' or not config.get('attempt_trace', False)):
        raise ValueError('phase profile requires budget baseline with attempt trace')
    required = {'run_address_adapter.py', 'run_repair_dev.py', 'address_backend.py',
                'pp_repair.py', receipt_name}
    if not required <= config['code_sha256'].keys():
        raise ValueError('missing runtime/build receipt pins')
    for name, expected in config['code_sha256'].items():
        if Path(name).name != name or digest((HERE/name).read_bytes()) != expected:
            raise ValueError('changed adapter runtime: '+name)
    build_sources = config.get('build_source_sha256', {})
    if (config.get('attempt_trace', False) or config.get('comparison_protocol')) and not {
            'build_address_full.py', 'address_adapter.py', 'address_adapter_support.h',
            'address_loop_guard.py', 'address_budget.py', 'address_budget_support.h'} <= build_sources.keys():
        raise ValueError('missing diagnostic/comparison build source pins')
    for name, expected in build_sources.items():
        if Path(name).name != name or digest((HERE/name).read_bytes()) != expected:
            raise ValueError('changed build source: '+name)
    raw_inputs = (path.parent/config['input_file']).read_bytes()
    if digest(raw_inputs) != config['input_sha256']:
        raise ValueError('changed input bundle')
    binary = (HERE/config['binary']).resolve()
    binary_sha = digest(binary.read_bytes())
    if binary_sha != config['binary_sha256']:
        raise ValueError('changed adapter binary; no silent rebuild')
    receipt = json.loads((HERE/receipt_name).read_bytes())
    if (receipt.get('status') != 'COMPILED_HELP_ONLY'
        or receipt.get('scope') != scopes[variant]
        or receipt.get('author_commit') != AUTHOR or receipt.get('author_unchanged') is not True
        or receipt.get('solver_instance_constructed') is not False
        or receipt.get('scientific_search_executed') is not False
        or receipt.get('binary_sha256') != binary_sha):
        raise ValueError('build receipt does not certify this adapter binary and author identity')
    if variant == 'loop_guard' and receipt.get('extension') != 'loop_guard':
        raise ValueError('shared root bound missing from build receipt')
    if variant == 'budget_guard' and receipt.get('extension') != 'budget_guard':
        raise ValueError('shared budget extension missing from build receipt')
    if config.get('attempt_trace', False) or config.get('comparison_protocol'):
        if (receipt.get('extension_order') != ['address_loop_guard', 'address_budget']
            or receipt.get('script_sha256') != build_sources['build_address_full.py']
            or receipt.get('adapter_script_sha256') != build_sources['address_adapter.py']
            or any(receipt.get('extension_script_sha256', {}).get(name) != build_sources[name+'.py']
                   for name in ('address_loop_guard', 'address_budget'))
            or receipt.get('extension_sources', {}).get('address_budget', {}).get(
                'inc/address_budget_support.h', {}).get('sha256') != build_sources['address_budget_support.h']):
            raise ValueError('attempt-trace build receipt/source mismatch')
    if config.get('comparison_protocol'):
        if (receipt.get('seed_admission_policies') != ['all', 'positive_delay'] or
                receipt.get('effort_modes') != ['fixed_repairs', 'total_budget']):
            raise ValueError('binary lacks reviewed seed admission / effort capabilities')
    if config.get('retry') != 0:
        raise ValueError('zero retry required')
    limits = config['limits']
    for key in ('total_wall_s', 'worker_cpu_s', 'native_cpu_s', 'per_process_as_mib',
                'external_final_reserve_s', 'inner_final_reserve_s'):
        if type(limits[key]) not in (int, float) or not 0 < limits[key] <= 512:
            raise ValueError('invalid limit '+key)
    if not all(type(limits[key]) is int for key in ('worker_cpu_s', 'native_cpu_s', 'per_process_as_mib')):
        raise ValueError('integer resource limits required')
    if limits['external_final_reserve_s']+limits['inner_final_reserve_s'] >= limits['total_wall_s']:
        raise ValueError('reserves consume entire budget')
    if variant == 'budget_guard':
        reserve = limits.get('native_cpu_reserve_s')
        if type(reserve) not in (int, float) or not 0 < reserve < limits['native_cpu_s']:
            raise ValueError('native CPU reserve must be inside the hard limit')
    config['manifest_sha256'] = expected_sha
    bundle = json.loads(raw_inputs)
    ids = {case['id'] for case in bundle['cases']}
    jobs = config['jobs']
    if len({j['id'] for j in jobs}) != len(jobs):
        raise ValueError('duplicate job')
    for job in jobs:
        if job['case'] not in ids or not re.fullmatch(r'[A-Za-z0-9_-]+', job['id']):
            raise ValueError('unknown case or invalid job id')
        if any(type(job[key]) is not int for key in ('seed', 'iterations', 'top_k')):
            raise ValueError('integer solver settings required')
        settings = comparison_settings(config, job)
        if job['seed'] < 0 or (settings is None and job['iterations'] < 1) or job['top_k'] < 1:
            raise ValueError('invalid solver settings')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', config['batch_id']):
        raise ValueError('invalid batch id')
    return config, bundle, binary


def parse_paths(raw, problem):
    lines = raw.decode('ascii').splitlines()
    if len(lines) != len(problem.ids):
        raise ValueError('incomplete final robot set')
    paths = {}
    for native_id, line in enumerate(lines):
        prefix = 'Agent '+str(native_id)+':'
        if not line.startswith(prefix):
            raise ValueError('unexpected agent order')
        body = line[len(prefix):]
        if not re.fullmatch(r'(\([0-9]+,[0-9]+\)->)+', body):
            raise ValueError('malformed author output')
        coords = [(int(r), int(c)) for r, c in re.findall(r'\(([0-9]+),([0-9]+)\)->', body)]
        if any(r >= problem.rows or c >= problem.cols for r, c in coords):
            raise ValueError('coordinate outside map')
        paths[problem.ids[native_id]] = tuple(r*problem.cols+c for r, c in coords)
    problem.validate(paths)
    return paths


def command(binary, folder, job, count, cutoff, reserve):
    return [str(binary), '--map', str(folder/'map.txt'), '--agents', str(folder/'agents.txt'),
        '--agentNum', str(count), '--initialPaths', str(folder/'initial.txt'),
        '--outputPaths', str(folder/'final.paths'), '--adapterReceipt', str(folder/'native_receipt.json'),
        '--cutoffTime', str(cutoff), '--finalReserve', str(reserve), '--seed', str(job['seed']),
        '--maxIterations', str(job['iterations']), '--destroyStrategy', 'RandomWalk',
        '--algorithm', 'bernoulie', '--k', str(job['top_k']), '--replanAlgo', 'PP',
        '--neighborSize', '8', '--b', 'canonical', '--sipp', '1', '--screen', '0']


def verify_budget_receipt(native, config):
    """A cooperative stop may succeed only after complete final validation.

    The inner CPU value is absolute process CPU, not descendant CPU summed by
    the supervisor. It is a recorded admission check, not a hard-time proof.
    """
    if config.get('variant', 'base') != 'budget_guard':
        return
    limits = config['limits']
    if (native.get('budget_scope') != 'SHARED_WALL_PROCESS_CPU_WITH_FINAL_RESERVE'
        or native.get('cpu_limit_s') != limits['native_cpu_s']
        or native.get('cpu_reserve_s') != limits['native_cpu_reserve_s']
        or type(native.get('inner_cpu_s')) not in (int, float)
        or not 0 <= native['inner_cpu_s'] < limits['native_cpu_s']):
        raise ValueError('native shared CPU budget receipt mismatch')
    for name in ('global_deadline', 'preprocessing_fallback'):
        if type(native.get(name)) is not bool:
            raise ValueError('missing native budget state: '+name)
    for name in ('last_stage', 'termination', 'last_sipp_end'):
        if not isinstance(native.get(name), str) or not native[name]:
            raise ValueError('missing native termination field: '+name)
    for name in ('group_calls', 'sipp_calls', 'sipp_deadlines', 'repair_deadlines', 'rollbacks'):
        if type(native.get(name)) is not int or native[name] < 0:
            raise ValueError('invalid native budget counter: '+name)
    if native['sipp_deadlines'] > native['sipp_calls']:
        raise ValueError('more SIPP deadlines than calls')


def verify_seed_comparison(native, config, job):
    """Keep policy identity, partial work, and budget-limited quality separate."""
    settings = comparison_settings(config, job)
    if settings is None:
        return None
    policy, mode = settings
    cap = job['iterations'] if mode == 'fixed_repairs' else None
    if (native.get('effort_mode') != mode or native.get('repair_cap') != cap or
            (cap is not None and type(native.get('repair_cap')) is not int)):
        raise ValueError('native effort mode/cap differs from requested comparison')
    attempts = native.get('repair_attempts')
    if (type(attempts) is not int or attempts < 0 or
            (cap is not None and attempts > cap) or
            native.get('attempt_trace_rows') != 0):
        raise ValueError('invalid repair attempt count')
    if (attempts > native['group_calls'] or native['rollbacks'] > attempts or
            native.get('attempt_trace_enabled') is not False or
            any(type(native.get(k)) is not int or native[k] != 0
                for k in ('trace_io_wall_ns', 'trace_io_cpu_ns'))):
        raise ValueError('comparison repair/group/trace accounting mismatch')
    reason = native.get('loop_exit_reason')
    if reason not in ('REPAIR_CAP', 'GLOBAL_DEADLINE', 'STATIC_SOC_BOUND',
                      'PREPROCESS_FALLBACK', 'AUTHOR_TIME_LIMIT') or reason != native['termination']:
        raise ValueError('unknown or inconsistent comparison stop reason')
    resource = native.get('deadline_resource')
    if (resource not in ('NONE', 'WALL', 'CPU', 'WALL_AND_CPU') or
            native['global_deadline'] != (resource != 'NONE')):
        raise ValueError('comparison deadline resource mismatch')
    reached = native.get('static_soc_lower_bound_reached')
    if type(reached) is not bool:
        raise ValueError('missing explicit static-bound state')
    if ((reason == 'REPAIR_CAP' and (cap is None or attempts != cap or native['global_deadline'])) or
            (reason == 'GLOBAL_DEADLINE' and not native['global_deadline']) or
            (reason == 'STATIC_SOC_BOUND' and not reached) or
            (reason == 'PREPROCESS_FALLBACK') != native['preprocessing_fallback']):
        raise ValueError('comparison termination does not match work/budget state')
    admission = native.get('seed_admission', {})
    if (admission.get('schema') != 'ADDRESS_SEED_ADMISSION_V1' or
            admission.get('policy') != policy or
            admission.get('static_soc_lower_bound_reached') is not reached):
        raise ValueError('seed admission policy or static bound mismatch')
    counters = ('selection_calls', 'agents_checked', 'topk_candidates', 'filtered_zero_candidates',
                'retained_topk_candidates', 'empty_eligible_calls', 'deadline_calls', 'selected_calls')
    if any(type(admission.get(k)) is not int or admission[k] < 0 for k in counters):
        raise ValueError('invalid seed admission counter')
    if (admission['selection_calls'] != sum(admission[k] for k in
            ('empty_eligible_calls', 'deadline_calls', 'selected_calls')) or
            admission['selection_calls'] > native['group_calls'] or
            admission['topk_candidates'] != admission['filtered_zero_candidates']+admission['retained_topk_candidates'] or
            (policy == 'all' and any(admission[k] for k in
                ('agents_checked', 'filtered_zero_candidates', 'empty_eligible_calls')))):
        raise ValueError('seed admission accounting does not close')
    target_met = (attempts == cap and reason in ('REPAIR_CAP', 'STATIC_SOC_BOUND')) if cap is not None else None
    return {'schema': 'ADDRESS_SEED_COMPARISON_V1', 'seed_admission': admission,
            'effort_mode': mode, 'repair_target': cap, 'repair_attempts': attempts,
            'repair_target_met': target_met,
            'equal_work_timing_eligible': target_met if cap is not None else False,
            'stop_reason': reason, 'deadline_resource': resource,
            'final_quality_at_return': True,
            'same_seed_does_not_imply_same_neighborhood_sequence': True}


PHASE_NAMES = ('DRIVER_OTHER', 'PREPROCESS', 'LNS_OTHER', 'GROUP_OTHER', 'TOPK',
               'BETA', 'WALK', 'NEIGHBOR_PREPARE', 'REPAIR', 'POST_REPAIR', 'FINAL_CHECK_OUTPUT')


def verify_phase_profile(native, config):
    """Verify exclusive accounting. Sampled clock cost is never a total estimate."""
    if not config.get('phase_profile', False):
        if 'phase_profile' in native:
            raise ValueError('unexpected phase profile in unprofiled run')
        return None
    p = native.get('phase_profile')
    if not isinstance(p, dict) or p.get('schema') != 'ADDRESS_PHASE_PROFILE_V1':
        raise ValueError('missing phase profile')
    if (p.get('clock') != 'STEADY_WALL_NS' or p.get('window') != 'CONFIGURED_TO_FINISH_BEFORE_RECEIPT'
        or p.get('exclusive') is not True or p.get('includes_instrumentation') is not True):
        raise ValueError('phase accounting scope mismatch')
    def nonnegative(obj, names):
        for name in names:
            if type(obj.get(name)) is not int or obj[name] < 0:
                raise ValueError('invalid phase field '+name)
    nonnegative(p, ('window_wall_ns', 'accounted_wall_ns', 'residual_wall_ns'))
    phases = p.get('phases', {})
    if set(phases) != set(PHASE_NAMES):
        raise ValueError('phase names mismatch')
    for value in phases.values():
        nonnegative(value, ('wall_ns', 'scope_entries', 'expired_calls', 'expired_samples', 'expired_sampled_wall_ns'))
        if value['expired_samples'] > value['expired_calls']:
            raise ValueError('more sampled checks than calls')
        if value['expired_sampled_wall_ns'] > value['wall_ns']:
            raise ValueError('sampled check time outside owning phase')
    accounted = sum(value['wall_ns'] for value in phases.values())
    if (p['accounted_wall_ns'] != accounted or p['residual_wall_ns'] != 0
        or accounted != p['window_wall_ns']):
        raise ValueError('exclusive phase accounting does not close')
    native_wall = native.get('inner_wall_before_receipt_s')
    if type(native_wall) not in (float, int) or not math.isfinite(native_wall) or native_wall < 0:
        raise ValueError('invalid native wall duration')
    if p['window_wall_ns'] > round(native_wall*1e9)+1000:
        raise ValueError('profile window exceeds native lifetime')
    sample = p.get('expired_sampling', {})
    if sample.get('sampled') is not True or sample.get('stride') != 1024 or sample.get('extrapolated') is not False:
        raise ValueError('sampling scope mismatch')
    nonnegative(sample, ('calls', 'samples', 'sampled_wall_ns'))
    for total, per in (('calls', 'expired_calls'), ('samples', 'expired_samples'),
                       ('sampled_wall_ns', 'expired_sampled_wall_ns')):
        if sample[total] != sum(value[per] for value in phases.values()):
            raise ValueError('sample aggregate mismatch')
    if sample['samples'] != sample['calls']//1024:
        raise ValueError('sample stride count mismatch')
    counters = p.get('counters', {})
    nonnegative(counters, ('group_calls', 'groups_formed', 'groups_no_seed', 'groups_too_small',
                           'groups_deadline', 'seed_calls', 'walk_calls',
                           'seed_zero_delay_selected', 'seed_positive_delay_selected'))
    if (counters['group_calls'] != native['group_calls']
        or sum(counters[k] for k in ('groups_formed', 'groups_no_seed', 'groups_too_small', 'groups_deadline')) != counters['group_calls']
        or counters['groups_formed'] < native['attempt_trace_rows']):
        raise ValueError('group outcomes mismatch')
    if counters['seed_zero_delay_selected']+counters['seed_positive_delay_selected'] > counters['seed_calls']:
        raise ValueError('selected seed counts exceed calls')
    for phase, calls in (('GROUP_OTHER', counters['group_calls']), ('TOPK', counters['seed_calls']),
                         ('WALK', counters['walk_calls']), ('REPAIR', native['attempt_trace_rows'])):
        if phases[phase]['scope_entries'] != calls:
            raise ValueError('phase entry count disagrees with calls')
    return p


def verify_attempt_trace(raw, native, count):
    """Check recorded execution sites, not recoverability or search completeness.

    The optional baseline trace never runs blocker diagnostics. Zero records
    means no runPP was entered; group construction is outside this denominator.
    """
    rows = []
    if native.get('attempt_trace_enabled') is not True:
        raise ValueError('attempt trace was not enabled in native receipt')
    if raw and not raw.endswith(b'\n'):
        raise ValueError('partial attempt trace line')
    allowed = {'UNKNOWN', 'FOUND', 'DEADLINE', 'COST_STOP', 'EMPTY_UNCLASSIFIED',
               'START_BLOCKED', 'FOCAL_DRAINED_EMPTY'}
    counters = {}
    search_calls = rollbacks = 0
    late_normal = []
    def integer(value, minimum=0):
        return type(value) is int and value >= minimum
    for line in raw.splitlines():
        row = json.loads(line)
        order = row.get('order')
        returns = row.get('primary_returns')
        if (row.get('schema') != 'ADDRESS_ATTEMPT_V2'
            or type(row.get('attempt_id')) is not int or row['attempt_id'] != len(rows)+1
            or not isinstance(order, list) or not order or len(set(order)) != len(order)
            or any(not integer(a) or a >= count for a in order)
            or row.get('group_size') != len(order)
            or not isinstance(returns, list)
            or not integer(row.get('primary_calls')) or row['primary_calls'] != len(returns)
            or len(returns) > len(order)):
            raise ValueError('attempt trace identity or call count mismatch')
        for index, call in enumerate(returns):
            if (call.get('position_zero_based') != index or call.get('agent') != order[index]
                or call.get('stop') not in allowed
                or call.get('native_end') not in allowed
                or type(call.get('empty')) is not bool
                or not integer(call.get('path_cost'), -1)
                or (call['empty'] != (call['path_cost'] == -1))
                or not integer(call.get('wall_ns')) or not integer(call.get('cpu_ns'))):
                raise ValueError('invalid per-call attempt record')
        if row.get('primary_stop') not in allowed:
            raise ValueError('invalid primary stop class')
        for name in ('primary_complete', 'failed_agent_attempted', 'local_deadline_reached',
                     'global_deadline_reached', 'accepted'):
            if type(row.get(name)) is not bool:
                raise ValueError('missing attempt state: '+name)
        pos, agent = row.get('failed_position_zero_based'), row.get('failed_agent')
        if (not integer(pos, -1) or not integer(agent, -1)
            or (pos == -1 and agent != -1)
            or (pos >= 0 and (pos >= len(order) or agent != order[pos]))):
            raise ValueError('invalid failed position/agent')
        if row['primary_complete'] and (pos != -1 or row['primary_calls'] != len(order)):
            raise ValueError('complete primary has a failed agent or missing call')
        if row['failed_agent_attempted'] != (0 <= pos < len(returns)):
            raise ValueError('failed agent attempted flag disagrees with calls')
        if row.get('failure_site') not in {'BEFORE_CALL', 'RETURN', 'COST_BOUND', 'COMPLETE', 'FINAL_ADMISSION'}:
            raise ValueError('invalid failure site')
        if row.get('recovery_decision') != 'NONE':
            raise ValueError('recovery is outside this baseline diagnostic manifest')
        if row.get('blockers_checked') is not False or row.get('recoverability_established') is not False:
            raise ValueError('baseline trace cannot certify recovery diagnostics')
        for name in ('old_group_cost', 'final_group_cost', 'group_calls_so_far'):
            if not integer(row.get(name)):
                raise ValueError('invalid attempt cost/counter')
        if ((row['accepted'] and (not row['primary_complete']
                                 or row['final_group_cost'] > row['old_group_cost']))
            or (not row['accepted'] and row['final_group_cost'] != row['old_group_cost'])):
            raise ValueError('attempt acceptance or rollback cost mismatch')
        cost = row.get('cost', {})
        for name in ('primary_search_wall_ns', 'primary_search_cpu_ns', 'rollback_wall_ns',
                     'rollback_cpu_ns', 'attempt_wall_before_trace_ns', 'attempt_cpu_before_trace_ns'):
            if not integer(cost.get(name)):
                raise ValueError('invalid attempt timing: '+name)
        if (sum(c['wall_ns'] for c in returns) != cost['primary_search_wall_ns']
            or sum(c['cpu_ns'] for c in returns) != cost['primary_search_cpu_ns']):
            raise ValueError('per-call timing disagrees with search interval sum')
        stop = row['primary_stop']
        if (row['global_deadline_reached'] or row['local_deadline_reached']) and row['accepted']:
            raise ValueError('attempt accepted after its deadline')
        counters[stop] = counters.get(stop, 0)+1
        search_calls += len(returns)
        rollbacks += not row['accepted']
        # An observed late focal-empty return is only a diagnosis candidate.
        # Old-path conflicts and usable retained prefixes remain unexamined.
        if (stop == 'FOCAL_DRAINED_EMPTY' and pos >= len(order)//2
            and row['failed_agent_attempted'] and not row['global_deadline_reached']
            and not row['local_deadline_reached']):
            late_normal.append(row['attempt_id'])
        rows.append(row)
    if (native.get('attempt_trace_rows') != len(rows)
        or native.get('sipp_calls') != search_calls or native.get('rollbacks') != rollbacks):
        raise ValueError('trace/native attempt counters disagree')
    for name in ('trace_io_wall_ns', 'trace_io_cpu_ns'):
        if not integer(native.get(name)):
            raise ValueError('trace I/O cost missing')
    return {'schema': 'ADDRESS_ATTEMPT_DIAGNOSTIC_SUMMARY_V1',
            'attempts': len(rows), 'primary_search_calls': search_calls,
            'primary_stop_counts': counters, 'late_normal_empty_attempt_ids': late_normal,
            'blockers_checked': False, 'recoverability_established': False,
            'group_construction_in_attempt_denominator': False,
            'trace_io_wall_ns': native['trace_io_wall_ns'],
            'trace_io_cpu_ns': native['trace_io_cpu_ns']}


def worker(config, case, job, binary, folder, deadline_ns, command_factory=command):
    started, cpu = time.monotonic_ns(), time.process_time_ns()
    payload = {'scope': 'COMMON_INITIAL_ADDRESS_DEV_NOT_INDEPENDENT_PERFORMANCE', 'status': 'FAILED',
               'case': case['id'], 'job': job, 'stage_wall_ns': {},
               'manifest_sha256': config['manifest_sha256'], 'final_validated': False}
    def timed(name, function):
        before = time.monotonic_ns()
        try:
            return function()
        finally:
            payload['stage_wall_ns'][name] = time.monotonic_ns()-before
    process = None
    initial = None
    try:
        problem, initial = timed('initial_complete_validation', lambda: unpack(case))
        if len(initial) < 8 or job['top_k'] > len(initial):
            raise ValueError('author recommended config requires n>=8 and 1<=top_k<=n')
        payload.update({'model_key': problem.model_key,
                        'initial_soc': sum(len(p)-1 for p in initial.values())})
        def materialize():
            grid, agents = problem.author_files()
            for name, raw in (('map.txt', grid), ('agents.txt', agents)):
                with (folder/name).open('xb') as stream:
                    stream.write(raw)
            with (folder/'initial.txt').open('x') as stream:
                stream.write(str(len(initial))+'\n')
                for agent in problem.ids:
                    path = initial[agent]
                    stream.write(str(len(path))+' '+' '.join(map(str, path))+'\n')
        timed('common_initial_materialization', materialize)
        limits = config['limits']
        cutoff = (deadline_ns-time.monotonic_ns())/1e9-limits['external_final_reserve_s']
        if cutoff <= limits['inner_final_reserve_s']:
            raise TimeoutError('no budget for ADDRESS construction and final validation')
        cmd = command_factory(binary, folder, job, len(initial), cutoff, limits['inner_final_reserve_s'])
        if config.get('variant', 'base') == 'budget_guard':
            cmd += ['--cpuLimit', str(limits['native_cpu_s']),
                    '--cpuReserve', str(limits['native_cpu_reserve_s'])]
        if config.get('attempt_trace', False):
            cmd += ['--attemptTrace', str(folder/'attempts.jsonl')]
        if config.get('phase_profile', False):
            cmd += ['--phaseProfile', '1']
        settings = comparison_settings(config, job)
        if settings is not None:
            cmd += ['--seedAdmission', settings[0], '--effortMode', settings[1]]
        payload['native_command'] = cmd
        def native_limits():
            resource.setrlimit(resource.RLIMIT_CPU, (limits['native_cpu_s'],)*2)
            resource.setrlimit(resource.RLIMIT_AS, (limits['per_process_as_mib']*1024**2,)*2)
            resource.setrlimit(resource.RLIMIT_FSIZE, (16*1024**2,)*2)
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        def invoke():
            nonlocal process
            with (folder/'native.stdout.log').open('xb') as out, (folder/'native.stderr.log').open('xb') as err:
                # Inherit worker's supervised process group. No orphan escape.
                process = subprocess.Popen(cmd, stdout=out, stderr=err, preexec_fn=native_limits)
                code = process.wait(timeout=max(.001, (deadline_ns-time.monotonic_ns())/1e9))
                if code:
                    raise RuntimeError('native exited '+str(code))
        timed('native_launch_through_exit', invoke)
        def final_check():
            paths = parse_paths((folder/'final.paths').read_bytes(), problem)
            native = json.loads((folder/'native_receipt.json').read_bytes())
            soc = sum(len(p)-1 for p in paths.values())
            if (not native.get('initial_and_final_validated') or native['seed'] != job['seed']
                or native['initial_soc'] != payload['initial_soc'] or native['final_soc'] != soc
                or soc > payload['initial_soc']):
                raise ValueError('native / external full validation disagreement')
            verify_budget_receipt(native, config)
            comparison = verify_seed_comparison(native, config, job)
            if comparison is not None:
                payload['comparison_diagnostics'] = comparison
            phase = verify_phase_profile(native, config)
            if phase is not None:
                payload['phase_diagnostics'] = phase
            if config.get('attempt_trace', False):
                payload['attempt_diagnostics'] = verify_attempt_trace(
                    (folder/'attempts.jsonl').read_bytes(), native, len(problem.ids))
            payload.update({'final_paths': paths, 'final_soc': soc,
                            'final_makespan': max(len(p)-1 for p in paths.values()),
                            'final_validated': True, 'native_receipt': native})
        timed('output_parse_and_external_final_validation', final_check)
        if time.monotonic_ns() >= deadline_ns:
            raise TimeoutError('final validation exceeded total deadline')
        payload['status'] = 'COMPLETE'
    except Exception as error:
        payload['reason'] = type(error).__name__+': '+str(error)
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait()
        payload.update({'worker_before_result_io_wall_ns': time.monotonic_ns()-started,
                        'worker_cpu_ns': time.process_time_ns()-cpu,
                        'original_initial_retained': initial is not None})
        write_json(folder/'result.json', payload)
    return payload['status'] == 'COMPLETE' and time.monotonic_ns() < deadline_ns


def execute(args, config, bundle, binary):
    if not args.authorization_reference or len(args.authorization_reference.strip()) < 8:
        raise ValueError('actual user permission reference required; a flag is not permission')
    job = next(job for job in config['jobs'] if job['id'] == args.job)
    output = HERE/'results'/config['batch_id']/job['id']
    output.mkdir(parents=True, exist_ok=False)
    write_json(output/'attempt.json', {'job': job, 'status': 'CONSUMED_ONCE', 'retries': 0,
        'manifest_sha256': config['manifest_sha256'], 'authorization_reference': args.authorization_reference})
    # Includes this process import, manifest/hash checks, worker/native startup,
    # initial import, output, external final validation and artifact hashing.
    deadline = ENTERED_NS+int(config['limits']['total_wall_s']*1e9)
    remaining = (deadline-time.monotonic_ns())/1e9
    if remaining <= 0:
        write_json(output/'receipt.json', {'status': 'FAILED_OR_INCOMPLETE',
            'reason': 'deadline consumed before launch', 'retry_allowed': False})
        return 2
    cmd = [sys.executable, '-B', str(Path(__file__).resolve()), '_worker', '--manifest', str(args.manifest.resolve()),
           '--sha256', args.sha256, '--job', args.job, '--output', str(output), '--deadline-ns', str(deadline)]
    limits = config['limits']
    costs = supervise(cmd, output, wall_s=remaining, cpu_s=limits['worker_cpu_s'],
                      memory_mib=limits['per_process_as_mib'])
    payload = None
    try:
        payload = json.loads((output/'result.json').read_bytes())
    except (ValueError, OSError):
        pass
    artifacts = {str(p.relative_to(output)): {'sha256': digest(p.read_bytes()), 'bytes': p.stat().st_size}
                 for p in sorted(output.rglob('*')) if p.is_file()}
    total_ns = time.monotonic_ns()-ENTERED_NS
    accepted = (costs['exit_code'] == 0 and not costs['forced_cleanup'] and payload
                and payload.get('status') == 'COMPLETE' and payload.get('final_validated')
                and time.monotonic_ns() < deadline)
    own = resource.getrusage(resource.RUSAGE_SELF)
    write_json(output/'receipt.json', {'status': 'COMPLETE' if accepted else 'FAILED_OR_INCOMPLETE',
        'manifest_sha256': config['manifest_sha256'], 'job': job, 'costs': costs, 'artifacts': artifacts,
        'total_entry_through_output_validation_and_hash_ns': total_ns,
        'supervisor_self_cpu_s': own.ru_utime+own.ru_stime,
        'budget_scope': 'ENTRY_THROUGH_RESULT_OUTPUT_EXTERNAL_FINAL_CHECK_AND_ARTIFACT_HASH',
        'total_wall_is_success_admission_budget': True,
        'coordinator_io_is_not_preemptively_bounded_here': True,
        'audit_receipt_write_and_process_exit_excluded': True,
        'retry_allowed': False, 'independent_performance_result': False})
    print(json.dumps({'job': job['id'], 'status': 'COMPLETE' if accepted else 'FAILED_OR_INCOMPLETE'}))
    return 0 if accepted else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('inspect', 'run', '_worker'))
    parser.add_argument('--manifest', required=True, type=Path)
    parser.add_argument('--sha256', required=True)
    parser.add_argument('--job')
    parser.add_argument('--authorization-reference')
    parser.add_argument('--output', type=Path)
    parser.add_argument('--deadline-ns', type=int)
    args = parser.parse_args()
    config, bundle, binary = load(args.manifest, args.sha256)
    if args.mode == 'inspect':
        for job in config['jobs']:
            case = next(case for case in bundle['cases'] if case['id'] == job['case'])
            problem, paths = unpack(case)
            if len(paths) < 8 or job['top_k'] > len(paths):
                raise ValueError('invalid ADDRESS task domain')
            print(json.dumps({'job': job, 'initial_soc': sum(len(p)-1 for p in paths.values()),
                              'model_key': problem.model_key, 'search_executed': False}))
        return 0
    if args.mode == '_worker':
        job = next(job for job in config['jobs'] if job['id'] == args.job)
        case = next(case for case in bundle['cases'] if case['id'] == job['case'])
        return 0 if worker(config, case, job, binary, args.output, args.deadline_ns) else 2
    return execute(args, config, bundle, binary)


if __name__ == '__main__':
    raise SystemExit(main())
