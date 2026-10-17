"""One-use manifest-bound four-case closed-form DEV driver.

Public entry: --manifest PATH --case all --permission PATH. A permission JSON
records real user authorization; creating one is not itself authorization.
This file is independent of the frozen T1/G2c runners and permissions. Imports
here are standard-library only; scientific imports occur inside the authorized,
resource-limited child. Never import/run this file as a static verification.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import heapq
import json
import os
from pathlib import Path
import resource
import secrets
import selectors
import signal
import subprocess
import sys
import time


BASE = Path(__file__).resolve().parent
SCHEMA = 'preexecution_dev_manifest_v1'
SCOPE = 'R16_TWO_TASKS_TWO_ARMS_CLOSED_FORM_DEV_ONCE'
CASES = {
    'ids13_initial': {'selected_ids': [1, 3], 'arm': 'initial'},
    'ids13_enumerate': {'selected_ids': [1, 3], 'arm': 'enumerate'},
    'ids013_initial': {'selected_ids': [0, 1, 3], 'arm': 'initial'},
    'ids013_enumerate': {'selected_ids': [0, 1, 3], 'arm': 'enumerate'},
}
PARAMETERS = {
    'resolution': '1/64', 'separation_gap': '1/20', 'plan_horizon': '120',
    'epoch': '1', 'task_horizon': '121', 'feedback_delay': '.1', 'feedback_ttl': '1',
    'capture_interval': '1', 'pair_crosscheck': True,
    'initial': ['.01', '-.005', '.001', '.005', '-.005'],
}
BUDGET_CEILINGS = {
    'wall_seconds': 60, 'cpu_seconds': 45, 'address_space_bytes': 536870912,
    'optimizer_wall_seconds': 40, 'optimizer_cpu_seconds': 30,
    'output_bytes': 16777216, 'max_groups': 6, 'max_proposals': 64,
    'max_group_pair_checks': 10000, 'max_group_link_checks': 10000,
    'max_cells_per_proposal': 200000, 'max_cells_total': 200000, 'max_events': 2000,
}
REQUIRED_CODE = {
    'execution': ('preexecution_driver.py', 'preexecution_input.py', 'preexecution_order.py',
                  'preexecution_schedule.py', 'preexecution_session.py', 'interface.py',
                  'timed_constraints.py', 'composition_constraints.py'),
    'source': ('composition.py', 'timed.py'),
    'tools': ('protocol.py', 'timed_protocol.py'),
}
LOG_LIMIT = 262144
RESULT_LIMIT = 2097152
FINAL_WALL_RESERVE = 2
FINAL_CPU_RESERVE = 1


def _dump(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), default=str, allow_nan=False)


def _sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _write_new(path, value, *, limit=None):
    raw = (_dump(value)+'\n').encode()
    if limit is not None and len(raw) > limit:
        raise ValueError('artifact byte budget exceeded: '+str(path))
    with Path(path).open('xb') as stream:
        stream.write(raw)
        stream.flush()
        os.fsync(stream.fileno())


def _absolute(value):
    if not isinstance(value, str) or not Path(value).is_absolute():
        raise ValueError('manifest paths must be explicit absolute paths')
    return Path(value).resolve()


def _load_manifest(path, permission_path):
    path = _absolute(str(Path(path).resolve()))
    raw = path.read_bytes()
    manifest_sha = hashlib.sha256(raw).hexdigest()
    manifest = json.loads(raw)
    fields = {'schema', 'scope', 'checklist_path', 'output_root', 'files', 'source_roots',
              'r16_dir', 'author_dir', 'cases', 'parameters', 'budget'}
    if (not isinstance(manifest, dict) or set(manifest) != fields
            or manifest['schema'] != SCHEMA or manifest['scope'] != SCOPE
            or manifest['cases'] != CASES or manifest['parameters'] != PARAMETERS):
        raise ValueError('manifest schema/cases/shared parameters differ from this finite DEV scope')
    if any(type(i) is not int for c in manifest['cases'].values() for i in c['selected_ids']):
        raise ValueError('original integer robot IDs required')
    budget = manifest['budget']
    if (not isinstance(budget, dict) or set(budget) != set(BUDGET_CEILINGS)
            or any(type(budget[k]) is not int or not 0 < budget[k] <= maximum
                   for k, maximum in BUDGET_CEILINGS.items())
            or budget['output_bytes'] <= RESULT_LIMIT+LOG_LIMIT+65536
            or budget['wall_seconds'] <= FINAL_WALL_RESERVE
            or budget['cpu_seconds'] <= FINAL_CPU_RESERVE
            or budget['optimizer_wall_seconds'] >= budget['wall_seconds']-FINAL_WALL_RESERVE
            or budget['optimizer_cpu_seconds'] >= budget['cpu_seconds']-FINAL_CPU_RESERVE):
        raise ValueError('explicit positive budgets within frozen hard ceilings required')
    if not isinstance(manifest['source_roots'], dict) or set(manifest['source_roots']) != set(REQUIRED_CODE):
        raise ValueError('execution/source/tools roots required')
    roots = {k: _absolute(v) for k, v in manifest['source_roots'].items()}
    if roots['execution'] != BASE:
        raise ValueError('execution root must contain this exact driver')
    required = {str(roots[root]/name) for root, names in REQUIRED_CODE.items() for name in names}
    required.update((str(_absolute(manifest['r16_dir'])/'inputs'/'official_test_staged.json'),
                     str(_absolute(manifest['author_dir'])/'sadg_controller'/'data'/'ecbs'/'test.yaml')))
    files = manifest['files']
    if not isinstance(files, dict) or not required <= set(files):
        raise ValueError('manifest omits driver/project dependency/input SHA bindings')
    for filename, expected in files.items():
        p = _absolute(filename)
        if (str(p) != filename or not isinstance(expected, str) or len(expected) != 64
                or any(c not in '0123456789abcdef' for c in expected) or _sha(p) != expected):
            raise ValueError('manifest file SHA mismatch: '+filename)
    checklist = _absolute(manifest['checklist_path'])
    _absolute(manifest['output_root'])
    permission = json.loads(Path(permission_path).read_bytes())
    if (not isinstance(permission, dict)
            or set(permission) != {'scope', 'approved_by_user', 'authorization_id',
                                   'manifest_sha256', 'checklist_sha256'}
            or permission['scope'] != SCOPE or permission['approved_by_user'] is not True
            or not isinstance(permission['authorization_id'], str) or not permission['authorization_id'].strip()
            or permission['manifest_sha256'] != manifest_sha
            or permission['checklist_sha256'] != _sha(checklist)):
        raise ValueError('fresh real-user authorization must bind this manifest AND checklist')
    return manifest, manifest_sha, permission


class Journal:
    def __init__(self, directory, limit):
        self.path, self.limit, self.written = directory/'events.ndjson', limit, 0
        self.stream = self.path.open('xb')

    def write(self, event, **values):
        raw = (_dump({'event': event, **values})+'\n').encode()
        if self.written+len(raw) > self.limit:
            raise ValueError('combined journal output budget exhausted')
        self.stream.write(raw)
        self.stream.flush()
        self.written += len(raw)

    def close(self):
        self.stream.flush()
        os.fsync(self.stream.fileno())
        self.stream.close()


def _worker_capability(args, manifest_sha, permission):
    if args.cap_fd is None or args.cap_fd < 3:
        raise ValueError('worker requires a parent-inherited one-use capability pipe')
    try:
        raw = os.read(args.cap_fd, 8193)
    finally:
        os.close(args.cap_fd)
    if len(raw) > 8192:
        raise ValueError('invalid worker capability length')
    cap = json.loads(raw)
    root = Path(args.run_dir).resolve()
    context = json.loads((root/'RUN_CONTEXT.json').read_bytes())
    if (set(cap) != {'case', 'manifest_sha256', 'parent_pid', 'nonce', 'output_root'}
            or cap['case'] != args.case or cap['manifest_sha256'] != manifest_sha
            or cap['parent_pid'] != os.getppid() or context['parent_pid'] != os.getppid()
            or cap['output_root'] != str(root) or context['manifest_sha256'] != manifest_sha
            or context['authorization_id'] != permission['authorization_id']
            or hashlib.sha256(cap['nonce'].encode()).hexdigest() != context['capability_hashes'][args.case]
            or not (BASE/('.preexecution_dev_consumed_'+manifest_sha)).is_file()):
        raise ValueError('worker is not the authorized direct child of this active batch')
    directory = root/args.case
    _write_new(directory/'CHILD_STARTED.json', {'case': args.case, 'manifest_sha256': manifest_sha,
                                               'pid': os.getpid(), 'retry': 0}, limit=65536)
    return directory


def _run_worker(args):
    manifest, manifest_sha, permission = _load_manifest(args.manifest, args.permission)
    if args.case not in CASES or Path(args.run_dir).resolve() != _absolute(manifest['output_root']):
        raise ValueError('worker case/output differs from manifest')
    directory = _worker_capability(args, manifest_sha, permission)
    budget, params, case = manifest['budget'], manifest['parameters'], CASES[args.case]
    started = time.perf_counter_ns()
    deadlines = (started+(budget['wall_seconds']-FINAL_WALL_RESERVE)*1000000000,
                 (budget['cpu_seconds']-FINAL_CPU_RESERVE)*1000000000)
    optimizer_deadlines = (started+budget['optimizer_wall_seconds']*1000000000,
                           budget['optimizer_cpu_seconds']*1000000000)
    journal = Journal(directory, budget['output_bytes']-RESULT_LIMIT-LOG_LIMIT-65536)
    result = {'case': args.case, 'arm': case['arm'], 'selected_ids': case['selected_ids'],
              'manifest_sha256': manifest_sha, 'status': 'FAILED', 'success': False,
              'failure_retained': True, 'retry': 0, 'attempts': [], 'source': None,
              'session_receipt': None, 'incumbent': None,
              'optimization_status': 'NOT_STARTED', 'optimization_stop': None, 'failure': None,
              'collision_observations': 'NOT_MEASURED', 'coverage_observations': 'NOT_MEASURED',
              'safety_scope': 'CONDITIONAL_CONTINUOUS_ALLOWED_FAMILY_CERTIFICATE_SEPARATE_FROM_OBSERVATION',
              'data_status': 'CLOSED_FORM_FUNCTIONAL_DEV_NOT_WORLD_OR_INDEPENDENT_PERFORMANCE',
              'initial_definition': params['initial'], 'initial_scope': 'FIXED_DECLARED_DEV_NOT_LIMO_DATA'}
    manager, session, costs = None, None, None
    used_cells, evaluated, certified = 0, 0, 0

    def check_deadline():
        if time.perf_counter_ns() >= deadlines[0] or time.process_time_ns() >= deadlines[1]:
            raise ValueError('total worker wall/CPU scientific budget exhausted; no retry')

    try:
        sys.path[:0] = [manifest['source_roots'][key] for key in ('execution', 'source', 'tools')]
        from preexecution_input import load_r16_dev
        from preexecution_schedule import ScheduleIncumbent, ValidationBudget, build_local_groups
        from preexecution_session import JointTaskSession
        from composition import Chain
        from timed import Plant, Trajectory
        from protocol import Costs
        costs = Costs()
        with costs.measure('input_and_complete_group_construction'):
            task = load_r16_dev(case['selected_ids'], r16_dir=manifest['r16_dir'],
                                author_dir=manifest['author_dir'])
            result['source'] = task['source']
            journal.write('input', source=task['source'], grid_paths=task['grid_paths'])
            check_deadline()
            catalog = build_local_groups(task, max_pair_checks=budget['max_group_pair_checks'],
                                         max_link_checks=budget['max_group_link_checks'], deadlines=optimizer_deadlines)
            payload = catalog.payload
            group_ids = sorted(g['id'] for g in payload['groups'])
            initial = {g['id']: g['initial'] for g in payload['groups']}
            result['group_count'] = len(group_ids)
            result['catalog_sha256'] = catalog.sha256
            journal.write('catalog', sha256=catalog.sha256, payload=payload)
            if len(group_ids) > budget['max_groups']:
                raise ValueError('max_groups exceeded; do not discard groups to fit budget')
            total_assignments = 1 << len(group_ids)
            result['declared_direction_assignments'] = total_assignments
            vb = ValidationBudget(resolution=Q(params['resolution']),
                                  max_cells=budget['max_cells_per_proposal'],
                                  horizon=Q(params['plan_horizon']),
                                  wall_ns=budget['wall_seconds']*1000000000,
                                  cpu_ns=budget['cpu_seconds']*1000000000)
            manager = ScheduleIncumbent(task['specs'], task['world_bounds'], vb,
                                        obstacles=task['obstacles'], separation_gap=params['separation_gap'],
                                        local_groups=catalog, order_mode='WINDOW_START_LAGS',
                                        pair_crosscheck=params['pair_crosscheck'])
        masks = range(1 if case['arm'] == 'initial' else total_assignments)
        result['planned_proposals'] = len(masks)
        for mask in masks:
            check_deadline()
            remaining = budget['max_cells_total']-used_cells
            stop = ('OPTIMIZER_TIME_BUDGET' if time.perf_counter_ns() >= optimizer_deadlines[0]
                    or time.process_time_ns() >= optimizer_deadlines[1] else
                    'PROPOSAL_BUDGET' if evaluated >= budget['max_proposals'] else
                    'TOTAL_CELL_BUDGET' if remaining <= 0 else None)
            if stop is not None:
                if manager.incumbent is None:
                    raise ValueError('INITIAL_NOT_CERTIFIED: '+stop)
                result['optimization_stop'] = stop
                journal.write('optimization_budget_stop', reason=stop, next_mask=mask)
                break
            # Each assignment is derived from the same original direction
            # vector. The best incumbent never changes candidate generation.
            directions = {name: ('reverse' if initial[name] == 'forward' else 'forward')
                          if mask & (1 << i) else initial[name] for i, name in enumerate(group_ids)}
            with costs.measure('complete_direction_proposal'):
                report = manager.consider(directions=directions, absolute_deadlines=optimizer_deadlines,
                                          max_cells=min(remaining, budget['max_cells_per_proposal']))
            evaluated += 1
            journal.write('proposal', mask=mask, directions=directions, report=report)
            operations = report.get('operations')
            if (not isinstance(operations, dict)
                    or any(type(operations.get(k)) is not int or operations[k] < 0
                           for k in ('phase_cells', 'time_cells'))):
                raise ValueError('proposal must expose nonnegative per-call phase/time cell deltas')
            used_cells += operations['phase_cells']+operations['time_cells']
            reason = report.get('reason')
            is_certified = (report.get('validation') or {}).get('status') == 'CERTIFIED_CONDITIONAL_GEOMETRY'
            is_certified = is_certified and reason in (None, 'NO_STRICT_SUM_COMPLETION_IMPROVEMENT')
            certified += int(is_certified)
            result['attempts'].append({'mask': mask, 'directions': directions,
                                       'certified': is_certified, 'accepted': report.get('accepted'),
                                       'reason': reason, 'operations': operations,
                                       'sum_completion': report.get('candidate_sum_completion')})
            if used_cells > budget['max_cells_total']:
                raise ValueError('total cell budget exceeded; preserve overrun and stop batch')
            if mask == 0:
                if not is_certified or manager.incumbent is None:
                    raise ValueError('INITIAL_NOT_CERTIFIED; no enumeration or task execution')
                result['initial_incumbent_sha256'] = manager.incumbent['schedule_sha256']
                result['initial_sum_completion'] = manager.incumbent['sum_completion']
            elif not is_certified:
                text = str(reason)
                pair = (report.get('validation') or {}).get('pair_crosscheck')
                pair_rows = [] if not isinstance(pair, dict) else list(pair.get('pairs', {}).values())
                pair_budget = isinstance(pair, dict) and (
                    any(s in str(pair.get('reason')).lower() for s in ('budget', 'cells'))
                    or any(row.get('expired_after_pair') or
                           'budget' in str(row.get('reason')).lower() for row in pair_rows))
                if (isinstance(pair, dict) and pair.get('status') != 'CERTIFIED_CONDITIONAL_GEOMETRY'
                        and not pair_budget):
                    raise ValueError('PAIR_CROSSCHECK_UNRESOLVED_OR_INCONSISTENT; no collision conclusion')
                budget_stop = (any(s in text.lower() for s in ('budget', 'deadline', 'expired', 'time exhausted'))
                               or time.perf_counter_ns() >= optimizer_deadlines[0]
                               or time.process_time_ns() >= optimizer_deadlines[1]
                               or used_cells >= budget['max_cells_total']
                               or pair_budget)
                if budget_stop:
                    result['optimization_stop'] = 'PROPOSAL_RESOURCE_LIMIT_KEEP_CERTIFIED_INCUMBENT'
                    journal.write('optimization_budget_stop', reason=reason, next_mask=mask+1)
                    break
                # A proved positive time cycle rejects only this direction.
                # Other resolution failures retain best-certified status; they
                # are never promoted to a collision or global infeasibility.
                expected = any(s in text for s in ('CURRENT_DIRECTION_POSITIVE_TIME_CYCLE',
                                                   'UNRESOLVED', 'horizon exceeded',
                                                   'continuous outer occupancy'))
                if not expected:
                    raise ValueError('proposal failed outside declared rejection cases: '+text)
            check_deadline()
        result['not_evaluated_masks'] = list(range(evaluated, len(masks)))
        result['optimization_status'] = (
            'FIXED_INITIAL_DIRECTIONS_CERTIFIED' if case['arm'] == 'initial' else
            'MINIMUM_OVER_ALL_EARLIEST_SCHEDULES_IN_FIXED_CONSERVATIVE_ABSTRACTION'
            if evaluated == total_assignments and certified == total_assignments else
            'BEST_CERTIFIED_ONLY_UNRESOLVED_OR_REJECTED_ASSIGNMENTS_RETAINED')
        plan = manager.incumbent
        result['incumbent'] = plan
        check_deadline()
        with costs.measure('qualified_plants_and_joint_session_construction'):
            initial_state = tuple(float(x) for x in params['initial'])
            plants = {r: Plant(Trajectory(r, Chain.build(spec)), initial_state)
                      for r, spec in plan['scheduled_specs'].items()}
            session = JointTaskSession(manager, plants, task='R16_DEV_'+'_'.join(map(str, case['selected_ids'])),
                                       epoch=params['epoch'], horizon=params['task_horizon'],
                                       feedback_delay=params['feedback_delay'], feedback_ttl=params['feedback_ttl'],
                                       engine=case['arm'], costs=costs)
        pending, serial, handled, completed = [], 0, 0, set()

        def enqueue(t, priority, kind, value=None):
            nonlocal serial
            serial += 1
            heapq.heappush(pending, (Q(t), priority, serial, kind, value))

        def packet_events(packets):
            for packet in packets:
                journal.write('capture', packet=json.loads(packet.wire()))
                enqueue(packet.delivery, 0, 'delivery', packet)

        packet_events(session.prepare('0'))
        handled += 1
        epoch, horizon, interval = Q(params['epoch']), Q(params['task_horizon']), Q(params['capture_interval'])
        enqueue(epoch, 1, 'launch')
        capture_times = {epoch, horizon}
        t = epoch
        while t <= horizon:
            capture_times.add(t)
            t += interval
        # These are capture requests, never a completion inference. The local
        # source must actually emit END, which must then be delivered/admitted.
        capture_times.update(epoch+p.trajectory.chain.duration for p in plants.values())
        for t in sorted(capture_times):
            enqueue(t, 2, 'capture')
        while pending and len(completed) != len(plants):
            check_deadline()
            now, _, _, kind, payload = heapq.heappop(pending)
            handled += 1
            if handled > budget['max_events']:
                raise ValueError('complete-session event budget exhausted')
            if kind == 'launch':
                decision = session.launch(now)
                journal.write('joint_launch', now=now, decision=decision)
            elif kind == 'capture':
                packet_events(session.capture(now))
            else:
                session.receive(payload, now=now)
                journal.write('delivery', now=now, robot=payload.binding.robot, seq=payload.seq, kind=payload.kind)
                if payload.kind == 'END':
                    completed.add(payload.binding.robot)
        result['handled_events'] = handled
        if len(completed) != len(plants):
            raise ValueError('missing delivered public END at declared task/delivery horizon')
        check_deadline()
    except Exception as exc:
        result['failure'] = type(exc).__name__+': '+str(exc)
        try:
            journal.write('failure', reason=result['failure'], evaluated=evaluated, used_cells=used_cells)
        except Exception as log_exc:
            result['failure_log_error'] = type(log_exc).__name__+': '+str(log_exc)
    finally:
        if session is not None:
            try:
                # Costs.finish() rejects active nested segments. No outer
                # measure context surrounds receipt(), including on failure.
                result['session_receipt'] = session.receipt()
                for row in session.evaluation_records:
                    journal.write('evaluation_only', data=row)
            except Exception as exc:
                result['receipt_or_evaluation_error'] = type(exc).__name__+': '+str(exc)
                result['failure'] = result['failure'] or result['receipt_or_evaluation_error']
        result['evaluated_assignments'], result['certified_assignments'] = evaluated, certified
        result['used_phase_plus_time_cells'] = used_cells
        if manager is not None:
            result['incumbent'] = manager.incumbent
        if result['failure'] is not None:
            result['optimization_status'] = 'BEST_CERTIFIED_ONLY_STOPPED_ON_FAILURE' if result['incumbent'] else 'NO_CERTIFIED_INITIAL'
        receipt = result['session_receipt']
        success = result['failure'] is None and receipt is not None and receipt.get('success') is True
        result.update(status='SUCCESS' if success else 'FAILED', success=success, failure_retained=not success,
                      all_candidate_failures_retained=True, completion=None if receipt is None else receipt['completion'],
                      soft_finalize_reserve={'wall_seconds': FINAL_WALL_RESERVE, 'cpu_seconds': FINAL_CPU_RESERVE})
        if costs is not None:
            result['in_process_costs'] = costs.finish()
        journal.close()
        result['journal'] = {'path': journal.path.name, 'bytes': journal.written, 'sha256': _sha(journal.path)}
        result['worker_peak_rss_kib'] = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        result['cost_scope'] = 'PARENT_SPAWN_THROUGH_EXIT_INCLUDES_IMPORTS_FINAL_SERIALIZATION_AND_IO'
        _write_new(directory/'result.json', result, limit=RESULT_LIMIT)
    return 0 if result['success'] else 2


def _run_child(manifest, manifest_path, manifest_sha, root, case, nonce):
    directory, budget = root/case, manifest['budget']
    directory.mkdir()
    read_fd, write_fd = os.pipe()
    cap = {'case': case, 'manifest_sha256': manifest_sha, 'parent_pid': os.getpid(),
           'nonce': nonce, 'output_root': str(root)}
    try:
        os.write(write_fd, _dump(cap).encode())
    finally:
        os.close(write_fd)
    args = [sys.executable, '-I', '-B', str(Path(__file__).resolve()), '--worker',
            '--manifest', str(manifest_path), '--permission', str(root/'authorization.json'),
            '--case', case, '--run-dir', str(root), '--cap-fd', str(read_fd)]

    def limits():
        resource.setrlimit(resource.RLIMIT_CPU, (budget['cpu_seconds'], budget['cpu_seconds']))
        resource.setrlimit(resource.RLIMIT_AS, (budget['address_space_bytes'], budget['address_space_bytes']))
        resource.setrlimit(resource.RLIMIT_FSIZE, (budget['output_bytes'], budget['output_bytes']))
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))

    before = resource.getrusage(resource.RUSAGE_CHILDREN)
    start = time.perf_counter_ns()
    child, reason, exit_code, logged = None, None, None, 0
    try:
        child = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                 pass_fds=(read_fd,), preexec_fn=limits, start_new_session=True)
        os.close(read_fd)
        read_fd = None
        sel = selectors.DefaultSelector()
        sel.register(child.stdout, selectors.EVENT_READ)
        with (directory/'process.log').open('xb') as log:
            while sel.get_map():
                if time.perf_counter_ns()-start >= budget['wall_seconds']*1000000000 and reason is None:
                    reason = 'HOST_WALL_TIMEOUT'
                    os.killpg(child.pid, signal.SIGKILL)
                for key, _ in sel.select(timeout=.05):
                    raw = os.read(key.fileobj.fileno(), 65536)
                    if not raw:
                        sel.unregister(key.fileobj)
                        continue
                    available = max(0, LOG_LIMIT-logged)
                    log.write(raw[:available])
                    logged += min(len(raw), available)
                    if len(raw) > available and reason is None:
                        reason = 'PROCESS_LOG_BUDGET_EXCEEDED'
                        os.killpg(child.pid, signal.SIGKILL)
            remaining = max(.001, budget['wall_seconds']-(time.perf_counter_ns()-start)/1000000000)
            try:
                exit_code = child.wait(timeout=remaining)
            except subprocess.TimeoutExpired:
                reason = reason or 'HOST_WALL_TIMEOUT_AFTER_STDOUT_CLOSED'
                os.killpg(child.pid, signal.SIGKILL)
                exit_code = child.wait()
            log.flush()
            os.fsync(log.fileno())
        sel.close()
    except Exception as exc:
        reason = reason or type(exc).__name__+': '+str(exc)
        if child is not None:
            if child.poll() is None:
                os.killpg(child.pid, signal.SIGKILL)
            exit_code = child.wait()
    finally:
        if read_fd is not None:
            os.close(read_fd)
    wall = time.perf_counter_ns()-start
    after = resource.getrusage(resource.RUSAGE_CHILDREN)
    cpu = int(1000000000*((after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime)))
    output_bytes = sum(p.stat().st_size for p in directory.iterdir() if p.is_file())
    try:
        result = json.loads((directory/'result.json').read_bytes())
        if not isinstance(result, dict) or result.get('case') != case or result.get('manifest_sha256') != manifest_sha:
            raise ValueError('child result identity mismatch')
    except Exception as exc:
        result = {'status': 'NO_VALID_CHILD_RESULT', 'success': False,
                  'failure': type(exc).__name__+': '+str(exc)}
    success = (reason is None and exit_code == 0 and result.get('success') is True
               and output_bytes <= budget['output_bytes']
               and wall <= budget['wall_seconds']*1000000000 and cpu <= budget['cpu_seconds']*1000000000)
    return {'case': case, 'status': result['status'], 'success': success, 'failure_retained': not success,
            'supervisor_failure': reason, 'exit_code': exit_code, 'output_bytes': output_bytes,
            'total_process_wall_ns': wall, 'total_process_cpu_ns': cpu,
            'output_budget_exceeded': output_bytes > budget['output_bytes'],
            'cost_scope': 'SPAWN_THROUGH_EXIT_IMPORTS_CONSTRUCTION_FINAL_SERIALIZATION_LOG_IO',
            'result': result}


def _run_batch(args):
    manifest, manifest_sha, permission = _load_manifest(args.manifest, args.permission)
    root = _absolute(manifest['output_root'])
    if root.exists():
        raise ValueError('exclusive output directory already exists; never overwrite or retry')
    marker = BASE/('.preexecution_dev_consumed_'+manifest_sha)
    _write_new(marker, {'authorization': permission, 'output_root': str(root),
                        'case_order': list(CASES), 'retry': 0}, limit=65536)
    root.mkdir()
    _write_new(root/'authorization.json', permission, limit=65536)
    nonces = {case: secrets.token_hex(32) for case in CASES}
    _write_new(root/'RUN_CONTEXT.json', {
        'manifest_sha256': manifest_sha, 'authorization_id': permission['authorization_id'],
        'parent_pid': os.getpid(), 'case_order': list(CASES),
        'capability_hashes': {case: hashlib.sha256(nonce.encode()).hexdigest() for case, nonce in nonces.items()},
    }, limit=65536)
    (root/'manifest.json').write_bytes(Path(args.manifest).read_bytes())
    rows, stopped = [], False
    try:
        for case in CASES:
            if stopped:
                rows.append({'case': case, 'status': 'NOT_RUN_AFTER_STOP', 'success': False, 'failure_retained': True})
                continue
            row = _run_child(manifest, Path(args.manifest).resolve(), manifest_sha, root, case, nonces[case])
            rows.append(row)
            stopped = not row['success']
    except Exception as exc:
        rows.append({'case': list(CASES)[len(rows)], 'status': 'PARENT_EXCEPTION', 'success': False,
                     'failure_retained': True, 'failure': type(exc).__name__+': '+str(exc)})
        rows.extend({'case': c, 'status': 'NOT_RUN_AFTER_STOP', 'success': False, 'failure_retained': True}
                    for c in list(CASES)[len(rows):])
    receipt = {'manifest_sha256': manifest_sha, 'authorization': permission, 'rows': rows,
               'case_order': list(CASES), 'retry': 0, 'planned_count': 4,
               'success': len(rows) == 4 and all(r['success'] for r in rows),
               'failed_or_unrun_cases_excluded': 0,
               'comparison_scope': 'INITIAL_VS_ENUMERATION_FUNCTIONAL_DEV_NO_LEARNING_OR_SPEEDUP_CLAIM',
               'common_pair_crosscheck': True, 'automatic_budget_relaxation': False}
    _write_new(root/'RUN_RECEIPT.json', receipt, limit=4*RESULT_LIMIT+65536)
    print(_dump({'output_root': str(root), 'success': receipt['success'], 'cases': [(r['case'], r['status']) for r in rows]}))
    return 0 if receipt['success'] else 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True)
    parser.add_argument('--permission', required=True)
    parser.add_argument('--case', required=True, choices=('all',)+tuple(CASES))
    parser.add_argument('--worker', action='store_true', help=argparse.SUPPRESS)
    parser.add_argument('--run-dir', help=argparse.SUPPRESS)
    parser.add_argument('--cap-fd', type=int, help=argparse.SUPPRESS)
    args = parser.parse_args()
    if args.worker:
        if args.case == 'all' or not args.run_dir:
            parser.error('internal worker requires one case and parent capability')
        return _run_worker(args)
    if args.case != 'all' or args.run_dir is not None or args.cap_fd is not None:
        parser.error('public entry permits only --case all; stopped batches cannot continue')
    return _run_batch(args)


if __name__ == '__main__':
    sys.exit(main())
