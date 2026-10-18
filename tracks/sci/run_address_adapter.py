"""One explicitly authorized common-initial ADDRESS job; inspect performs no search.

Uses the existing group supervisor and common GridProblem final validator.
An immutable manifest is a proposal, never permission. Every attempted job owns
an exclusive output directory, including failure/timeout; no retries.
"""
import time
ENTERED_NS = time.monotonic_ns()
import argparse
import json
import os
from pathlib import Path
import re
import resource
import subprocess
import sys

from run_repair_dev import digest, supervise, unpack, write_json
from address_backend import AUTHOR

HERE = Path(__file__).resolve().parent


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
    required = {'run_address_adapter.py', 'run_repair_dev.py', 'address_backend.py',
                'pp_repair.py', receipt_name}
    if not required <= config['code_sha256'].keys():
        raise ValueError('missing runtime/build receipt pins')
    for name, expected in config['code_sha256'].items():
        if Path(name).name != name or digest((HERE/name).read_bytes()) != expected:
            raise ValueError('changed adapter runtime: '+name)
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
        if job['seed'] < 0 or job['iterations'] < 1 or job['top_k'] < 1:
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
