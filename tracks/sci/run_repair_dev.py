"""Inspect frozen repair inputs, or execute ONE explicitly authorized DEV arm.

Import/inspect never constructs the native solver. The run command consumes its
exclusive output directory even on failure; no automatic retries or tuning.
"""
import time

ENTERED_NS = time.monotonic_ns()
import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import resource
import signal
import subprocess
import sys

HERE = Path(__file__).resolve().parent


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def write_json(path, value):
    # Exclusive writes preserve failed/partial attempts rather than overwriting.
    with Path(path).open('x') as stream:
        json.dump(value, stream, sort_keys=True, indent=2, allow_nan=False)
        stream.write('\n')
        stream.flush()
        os.fsync(stream.fileno())


def load(manifest, expected_sha):
    manifest = Path(manifest).resolve()
    raw = manifest.read_bytes()
    if digest(raw) != expected_sha:
        raise ValueError('manifest SHA mismatch')
    config = json.loads(raw)
    if config['schema'] != 'repair_dev_v1' or config['authorization'] != 'PENDING_USER':
        raise ValueError('this configuration is a proposal, never an authorization')
    for name, expected in config['code_sha256'].items():
        if Path(name).name != name or digest((HERE / name).read_bytes()) != expected:
            raise ValueError('changed runtime file: ' + name)
    inputs = (manifest.parent / config['input_file']).read_bytes()
    if digest(inputs) != config['input_sha256']:
        raise ValueError('input bundle changed')
    build = json.loads((HERE / 'build_receipt.json').read_bytes())
    binary = HERE / config['binary']
    if digest(binary.read_bytes()) != build['binary_sha256']:
        raise ValueError('compiled binary changed/missing; do not silently rebuild')
    config['manifest_sha256'] = expected_sha
    return config, json.loads(inputs), binary.resolve()


def unpack(case):
    from address_backend import GridProblem
    paths = {int(a): tuple(p) for a, p in case['paths'].items()}
    endpoints = {int(a): tuple(p) for a, p in case['endpoints'].items()}
    problem = GridProblem(case['rows'], case['cols'], case['blocked'], endpoints)
    problem.validate(paths)
    for order in case['orders']:
        if not order or len(set(order)) != len(order) or not set(order) <= set(paths):
            raise ValueError('invalid fixed neighborhood/order')
    return problem, paths


def inspect_inputs(config, bundle):
    result = []
    for case in bundle['cases']:
        problem, paths = unpack(case)
        result.append({'id': case['id'], 'model_key': problem.model_key,
                       'robots': len(paths), 'initial_soc': sum(len(p)-1 for p in paths.values()),
                       'makespan': max(len(p)-1 for p in paths.values()),
                       'fixed_orders': case['orders'], 'status': 'EXISTING_PATHS_VALIDATED_NO_SEARCH'})
    ids = {case['id'] for case in bundle['cases']}
    if any(job['case'] not in ids for job in config['jobs']):
        raise ValueError('job refers to unknown input')
    return result


def worker(config, case, policy, binary, output, deadline_ns, backend_factory=None):
    from address_backend import NativeBackend
    from pp_repair import Incumbent, Policy, RepairStatus, SharedBudget, repair
    backend_factory = backend_factory or NativeBackend
    started, cpu = time.monotonic_ns(), time.process_time_ns()
    problem, initial = unpack(case)
    store = Incumbent(initial)
    budget = SharedBudget(deadline_ns, config['limits']['search_calls'])
    backend, results = None, []
    payload = {'scope': 'EXISTING_TASK_DEV_NOT_INDEPENDENT_PERFORMANCE',
               'status': 'FAILED', 'case': case['id'], 'policy': policy,
               'manifest_sha256': config['manifest_sha256'],
               'initial_soc': sum(len(p)-1 for p in initial.values()),
               'model_key': problem.model_key, 'attempts': results}
    # Allocate first so even __init__ failure keeps its RPC/child-cost fields.
    backend = backend_factory.__new__(backend_factory)
    try:
        backend_factory.__init__(backend, problem, initial, binary, HERE / 'build_receipt.json',
            output / 'native', budget, seed=case['seed'], supervised=True,
            cpu_seconds=config['limits']['native_cpu_s'],
            memory_mib=config['limits']['per_process_as_mib'])
        payload['lower_bounds'] = backend.lower_bounds
        payload['bootstrap_through_native_ready_ns'] = time.monotonic_ns()-started
        for order in case['orders']:
            before_rpc = len(backend.records)
            result = repair(store, order, backend.lower_bounds,
                model_key=problem.model_key, search=backend.search, validate=backend.validate,
                budget=budget, shared_cache=backend.cache, policy=Policy(policy))
            record = {key: value for key, value in vars(result).items() if key not in ('before', 'after')}
            record.update({'before_sha256': result.before.sha256, 'after_sha256': result.after.sha256,
                           'rpc_indices': [before_rpc, len(backend.records)]})
            results.append(record)
            # Incomplete/unknown output is not a reward label or a reason to retry.
            if result.status in (RepairStatus.TIMEOUT, RepairStatus.FAILED, RepairStatus.STALE):
                payload['status'] = result.status.value
                break
        else:
            payload['status'] = 'COMPLETE'
        budget.measure('final_complete_validation', lambda: problem.validate(store.snapshot().paths))
        payload['final_validated'] = True
    except Exception as error:
        payload['status'] = 'FAILED'
        payload['reason'] = type(error).__name__ + ': ' + str(error)
    finally:
        if backend is not None and hasattr(backend, 'proc'):
            backend.close()
        final = store.snapshot()
        payload.update({'final_paths': dict(final.paths), 'final_sha256': final.sha256,
            'final_soc': sum(len(p)-1 for p in final.paths.values()),
            'final_makespan': max(len(p)-1 for p in final.paths.values()),
            'search_calls': budget.search_calls, 'stage_wall_ns': budget.stage_wall_ns,
            'stage_python_cpu_ns': budget.stage_cpu_ns,
            'rpc': getattr(backend, 'records', []), 'native_usage': getattr(backend, 'child_usage', None),
            'host_callback_costs': backend.accounting() if hasattr(backend, 'accounting') else None,
            'worker_before_write_wall_ns': time.monotonic_ns()-started,
            'worker_python_cpu_ns': time.process_time_ns()-cpu})
        write_json(output / 'result.json', payload)
    return payload['status'] == 'COMPLETE'


def supervise(command, folder, *, wall_s, cpu_s, memory_mib):
    """Fresh process only: own case group + Linux subreaper; reap orphan CPU too.

    RUSAGE_CHILDREN includes waited descendants; do not add native_usage again.
    maxrss is largest child RSS, not simultaneous tree memory.
    """
    libc = ctypes.CDLL(None, use_errno=True)
    if libc.prctl(36, 1, 0, 0, 0) != 0:  # PR_SET_CHILD_SUBREAPER
        raise OSError(ctypes.get_errno(), 'cannot enable Linux child subreaper')
    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    started = time.monotonic_ns()
    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (cpu_s, cpu_s))
        resource.setrlimit(resource.RLIMIT_AS, (memory_mib*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_FSIZE, (16*1024**2,)*2)
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
    with (folder/'worker.stdout.log').open('xb') as stdout, (folder/'worker.stderr.log').open('xb') as stderr:
        process = subprocess.Popen(command, stdout=stdout, stderr=stderr, start_new_session=True,
                                   preexec_fn=limits)
        deadline = started + int(wall_s*1e9)
        reaped, killed, worker_done, interruption = [], False, False, None
        def reap(pid, status, usage):
            nonlocal worker_done
            if pid:
                code = os.waitstatus_to_exitcode(status)
                reaped.append({'pid': pid, 'exit_code': code, 'user_s': usage.ru_utime,
                               'system_s': usage.ru_stime, 'maxrss_kib': usage.ru_maxrss})
                if pid == process.pid:
                    process.returncode, worker_done = code, True
        def kill_group():
            nonlocal killed
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            killed = True
        def interrupted(signum, frame):
            raise InterruptedError('supervisor signal ' + str(signum))
        previous = {sig: signal.signal(sig, interrupted) for sig in (signal.SIGTERM, signal.SIGINT)}
        try:
            while True:
                try:
                    pid, status, usage = os.wait4(-1, os.WNOHANG)
                except ChildProcessError:
                    break
                if pid:
                    reap(pid, status, usage)
                    continue
                if not killed and (time.monotonic_ns() >= deadline or worker_done):
                    # A returned worker must not leave its native child behind.
                    kill_group()
                time.sleep(0.01)
        except BaseException as error:
            interruption = type(error).__name__ + ': ' + str(error)
            kill_group()
            while True:
                try:
                    reap(*os.wait4(-1, 0))
                except ChildProcessError:
                    break
        finally:
            for sig, handler in previous.items():
                signal.signal(sig, handler)
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    return {'scope': 'WORKER_IMPORT_TO_EXIT_INCLUDING_RESULT_IO_AND_WAITED_NATIVE',
            'wall_ns': time.monotonic_ns()-started, 'exit_code': process.returncode,
            'forced_cleanup': killed, 'interruption': interruption, 'reaped': reaped,
            'all_descendant_user_s': after.ru_utime-before.ru_utime,
            'all_descendant_system_s': after.ru_stime-before.ru_stime,
            'largest_child_maxrss_kib': max((r['maxrss_kib'] for r in reaped), default=0)}


def execute(args, config, bundle, binary):
    if not args.authorization_reference or len(args.authorization_reference.strip()) < 8:
        raise ValueError('record the real user authorization; a file/flag cannot grant it')
    jobs = {job['id']: job for job in config['jobs']}
    job = jobs[args.job]
    case = next(case for case in bundle['cases'] if case['id'] == job['case'])
    output = HERE / 'results' / config['batch_id'] / job['id']
    output.mkdir(parents=True, exist_ok=False)  # Consumption begins before any solver.
    write_json(output/'attempt.json', {'status': 'CONSUMED_ONCE', 'job': job,
        'authorization_reference': args.authorization_reference,
        'manifest_sha256': config['manifest_sha256'], 'retries': 0})
    # Deadline starts before worker import and its input/initial-state checks.
    deadline = time.monotonic_ns() + int(config['limits']['algorithm_wall_s']*1e9)
    command = [sys.executable, '-B', str(Path(__file__).resolve()), '_worker',
               '--manifest', str(Path(args.manifest).resolve()), '--sha256', args.sha256,
               '--job', args.job, '--output', str(output), '--deadline-ns', str(deadline)]
    costs = supervise(command, output, wall_s=config['limits']['case_wall_s'],
        cpu_s=config['limits']['worker_cpu_s'], memory_mib=config['limits']['per_process_as_mib'])
    files = {str(p.relative_to(output)): {'sha256': digest(p.read_bytes()), 'bytes': p.stat().st_size}
             for p in sorted(output.rglob('*')) if p.is_file()}
    payload = None
    if (output/'result.json').exists():
        try:
            payload = json.loads((output/'result.json').read_bytes())
        except (ValueError, OSError):
            pass  # Partial output is retained, never made into success.
    accepted = (costs['exit_code'] == 0 and not costs['forced_cleanup']
                and payload is not None and payload.get('status') == 'COMPLETE'
                and payload.get('final_validated') is True)
    own = resource.getrusage(resource.RUSAGE_SELF)
    write_json(output/'receipt.json', {'status': 'COMPLETE' if accepted else 'FAILED_OR_INCOMPLETE',
        'job': job, 'manifest_sha256': config['manifest_sha256'], 'costs': costs, 'artifacts': files,
        'supervisor_entry_through_artifact_hash_ns': time.monotonic_ns()-ENTERED_NS,
        'supervisor_self_cpu_s': own.ru_utime+own.ru_stime,
        'accounting_note': 'worker wall includes imports and all result writes; supervisor bookkeeping separate; its final receipt write/exit excluded from its self-timer',
        'independent_performance_result': False, 'retry_allowed': False})
    print(json.dumps({'job': args.job, 'status': 'COMPLETE' if accepted else 'FAILED_OR_INCOMPLETE',
                      'output': str(output)}))
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
        print(json.dumps(inspect_inputs(config, bundle), indent=2))
        return 0
    if args.mode == '_worker':
        job = next(job for job in config['jobs'] if job['id'] == args.job)
        case = next(case for case in bundle['cases'] if case['id'] == job['case'])
        return 0 if worker(config, case, job['policy'], binary, args.output, args.deadline_ns) else 2
    return execute(args, config, bundle, binary)


if __name__ == '__main__':
    raise SystemExit(main())
