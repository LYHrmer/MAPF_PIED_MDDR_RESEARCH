"""Explicitly gated finite DEV run. Import/check-inputs NEVER runs a task.

Parent process measures each child through exit (imports, final logs and I/O
included). Inner Costs segments are diagnostics, never added to the envelope.
No existing run permission is accepted; a fresh plan-bound receipt is required.
"""
import argparse
from fractions import Fraction as Q
import hashlib
import heapq
import json
import math
import os
from pathlib import Path
import resource
import subprocess
import sys
import time
from itertools import combinations

BASE = Path(__file__).resolve().parent
HOME = BASE.parents[2]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def verify_inputs():
    from verify_composition import verify_pins, verify_new_pins
    old, c1 = verify_pins(), verify_new_pins()
    manifest = json.loads((BASE/'TIMED_MANIFEST.json').read_text())
    roots = {'execution': BASE, 'source': HOME/'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source',
             'tools': HOME/'MAPF_QUERY_VALUE_FEASIBILITY/exploration/execution_feedback'}
    if sha(BASE/'COMPOSITION_MANIFEST.json') != manifest['composition_manifest_sha256']:
        raise ValueError('frozen C1 manifest changed')
    count = 0
    for group, files in manifest['files'].items():
        for name, expected in files.items():
            path = (roots[group]/name).resolve()
            if not path.is_relative_to(roots[group]) or sha(path) != expected:
                raise ValueError('new input hash mismatch: '+group+'/'+name)
            count += 1
    return {'old': old, 'C1': c1, 'timed': count}


def load_components():
    verify_inputs()
    from verify_integration import module
    from author_events import load_author
    source = HOME/'MAPF_GAUSSIAN_FEASIBILITY/exploration/spatial_source'
    transport = HOME/'MAPF_QUERY_VALUE_FEASIBILITY/exploration/execution_feedback'
    module('composition', source/'composition.py')
    timed = module('timed', source/'timed.py')
    protocol = module('protocol', transport/'protocol.py')
    feedback = module('timed_protocol', transport/'timed_protocol.py')
    module('composition_constraints', BASE/'composition_constraints.py')
    constraints = module('timed_constraints', BASE/'timed_constraints.py')
    session = module('timed_session', BASE/'timed_session.py')
    author = load_author(HOME/'.cache/mapf_research/sadg-controller-c2626d9',
                         BASE.parent/'error_guidance/sadg_preflight_20261004_r16/SOURCE_ENVIRONMENT.json')
    return timed, protocol, feedback, constraints, session, author


def inputs():
    config = json.loads((BASE/'timed_fixture.json').read_text())
    if sha(BASE/config['base_fixture']) != config['base_sha256']:
        raise ValueError('C1 fixture identity changed')
    return json.loads((BASE/config['base_fixture']).read_text()), config


def dump(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, default=lambda x: str(x) if isinstance(x, Q) else x)


class Journal:
    def __init__(self, directory, limit):
        self.public = (directory/'public.jsonl').open('x')
        self.evaluation = (directory/'evaluation.jsonl').open('x')
        self.count, self.limit = 0, limit

    def write(self, value, *, evaluation=False):
        payload = dump(value)+'\n'
        self.count += len(payload.encode())
        if self.count > self.limit:
            raise ValueError('aggregate log output budget exceeded')
        file = self.evaluation if evaluation else self.public
        file.write(payload); file.flush()

    def close(self):
        self.public.close(); self.evaluation.close()


def rectangle_overlap_witness(a, b):
    """SAT interior witness at ONE evaluated instant; not continuous clearance.

    Return True only with >1e-8 m projection overlap on every unit normal.
    Floating near-contact cases remain unknown, never reported as safe.
    """
    minimum = float('inf')
    for polygon in (a, b):
        for i in (0, 1):
            p, q = polygon[i], polygon[i+1]
            dx, dy = q[0]-p[0], q[1]-p[1]
            norm = math.hypot(dx, dy)
            axis = (-dy/norm, dx/norm)
            pa = [x*axis[0]+y*axis[1] for x, y in a]
            pb = [x*axis[0]+y*axis[1] for x, y in b]
            gap = min(max(pa), max(pb))-max(min(pa), min(pb))
            if gap < -1e-8:
                return 'SEPARATED_AT_PROBE'
            minimum = min(minimum, gap)
    return 'NUMERICAL_INTERIOR_COLLISION_WITNESS' if minimum > 1e-8 else 'NEAR_CONTACT_UNRESOLVED'


def task_child(directory, size, engine):
    """Authorized scientific DEV entry; NEVER called by static verification."""
    timed, protocol, feedback, constraints, sessions, author = load_components()
    base, config = inputs()
    costs = protocol.Costs()
    journal = Journal(directory, config['run_budget']['output_bytes_per_child']-1048576)
    session = None
    outcome, failure = 'FAILED', None
    evaluation_count, coverage_violations, collision_witnesses, near_contacts = 0, 0, 0, 0
    try:
        with costs.measure('whole_task_after_imports'):
            with costs.measure('source_and_problem_construction'):
                problem = constraints.make_problem(base, config, size)
                session = sessions.TaskSession(problem, author, engine=engine, costs=costs)
                initial = tuple(map(float, config['initial_conditions']['all_robots']))
                plants = {r: timed.Plant(tr, initial) for r, tr in problem['trajectories'].items()}
                producers = {r: feedback.TaskProducer(session.bindings[r], delay=config['feedback_delay']) for r in plants}
            pending, serial = [], 0

            def enqueue(t, kind, robot, payload=None):
                nonlocal serial
                serial += 1
                heapq.heappush(pending, (Q(t), serial, kind, robot, payload))

            cadence, horizon = Q(config['periodic_capture_interval']), Q(config['horizon'])
            for robot in plants:
                t = Q(0)
                while t <= horizon:
                    enqueue(t, 'capture', robot)
                    t += cadence
            handled = 0
            while pending:
                now, _, kind, robot, payload = heapq.heappop(pending)
                if now > horizon:
                    break
                handled += 1
                if handled > config['run_budget']['max_events_per_child']:
                    raise ValueError('event budget exceeded')
                if kind == 'capture':
                    producer = producers[robot]
                    if producer.ended or producer.last == now:
                        continue
                    with costs.measure('actual_controller_and_sensor'):
                        observation = plants[robot].observe(now)
                        packet = producer.capture(observation, now=now)
                    with costs.measure('evaluation_only_truth_and_coverage'):
                        record = plants[robot].evaluate(now)
                        phase = plants[robot].clock.phase(now)
                        tr = problem['trajectories'][robot]
                        b = tr.box(phase, phase)
                        points = [tr.body_point(phase, initial, u) for u in ((-.3, -.1), (-.3, .1), (.3, -.1), (.3, .1))]
                        valid = all(float(b[0]) <= x <= float(b[1]) and float(b[2]) <= y <= float(b[3]) for x, y in points)
                        evaluation_count += 1
                        coverage_violations += int(not valid)
                        journal.write({'robot': robot, **record, 'body_contained_at_probe': valid}, evaluation=True)
                        if not valid:
                            raise ValueError('source coverage violation; retain failure')
                        corners = ((-.3, -.1), (.3, -.1), (.3, .1), (-.3, .1))
                        polygons = {r: [p.trajectory.body_point(p.clock.phase(now), initial, u) for u in corners]
                                    for r, p in plants.items()}
                        for ra, rb in combinations(plants, 2):
                            witness = rectangle_overlap_witness(polygons[ra], polygons[rb])
                            collision_witnesses += int(witness == 'NUMERICAL_INTERIOR_COLLISION_WITNESS')
                            near_contacts += int(witness == 'NEAR_CONTACT_UNRESOLVED')
                            journal.write({'physical_time': str(now), 'pair': [ra, rb], 'probe': witness}, evaluation=True)
                            if witness != 'SEPARATED_AT_PROBE':
                                raise ValueError('collision witness or unresolved numeric contact; retain failure')
                    with costs.measure('public_serialization_and_transport_log'):
                        journal.write({'event': 'capture', 'robot': robot, 'packet': json.loads(packet.wire())})
                        enqueue(packet.delivery, 'delivery', robot, packet)
                else:
                    session.receive(payload, now=now)
                    with costs.measure('delivery_log'):
                        journal.write({'event': 'delivery', 'robot': robot, 'time': str(now), 'seq': payload.seq})
                    # Stable priority and identical engine-independent proposals.
                    for candidate in plants:
                        if candidate in session.started:
                            continue
                        decision = session.authorize(candidate, now=now)
                        with costs.measure('decision_and_control_log'):
                            journal.write({'event': 'decision', 'robot': candidate, 'time': str(now), 'decision': decision})
                        if decision['accepted']:
                            with costs.measure('control_dispatch_shared_actual_clock'):
                                plants[candidate].clock.resume(now)
                                enqueue(now, 'capture', candidate)  # explicit actual-input ACK, delayed like all feedback
                                enqueue(now+problem['trajectories'][candidate].chain.duration, 'capture', candidate)
                    if all(t is not None for t in session.completion.values()):
                        outcome = 'SUCCESS'
                        break
            if outcome != 'SUCCESS':
                outcome = 'TIMEOUT'
    except Exception as exc:
        failure = type(exc).__name__+': '+str(exc)
    finally:
        journal.close()
    result = session.receipt(status=outcome) if session is not None else {'status': outcome, 'construction_failed': True}
    result.update(failure=failure, size=size, engine=engine, evaluation_probes=evaluation_count,
                  observed_coverage_violations=coverage_violations,
                  numerical_collision_witness_count=collision_witnesses, unresolved_contact_probe_count=near_contacts,
                  witness_count_scope='evaluated instants only; zero witnesses alone does not prove continuous clearance',
                  collision_measure='continuous allowed-family certificates; unresolved does not count as collision',
                  numerical_world_integrator=False, data_status='DEV_closed_form_execution_not_benchmark_evidence')
    payload = dump(result)+'\n'
    if len(payload.encode()) > 1048576:
        raise ValueError('result output budget exceeded')
    (directory/'result.json').write_text(payload)
    return 0 if outcome == 'SUCCESS' else 2


def validate_permission(path):
    receipt = json.loads(Path(path).read_text())
    if (set(receipt) != {'scope', 'approved_by_user', 'authorization_id', 'manifest_sha256', 'checklist_sha256'}
            or receipt['scope'] != 'T1_v2_four_children_once' or receipt['approved_by_user'] is not True
            or not isinstance(receipt['authorization_id'], str) or not receipt['authorization_id'].strip()
            or receipt['manifest_sha256'] != sha(BASE/'TIMED_MANIFEST.json')
            or receipt['checklist_sha256'] != sha(BASE/'TIMED_RUN_CHECKLIST.md')):
        raise ValueError('fresh explicit plan-bound authorization required')
    return receipt


def bounded_run(permission_path, output):
    verify_inputs()
    receipt = validate_permission(permission_path)
    _, config = inputs()
    output = Path(output).resolve()
    expected = BASE/'timed_run_once_20261016'
    if output != expected:
        raise ValueError('output must match the frozen checklist')
    # A one-use marker survives partial/failed runs. Never retry by deleting it.
    marker = BASE/('.timed_permission_consumed_'+receipt['manifest_sha256'])
    with marker.open('x') as stream:
        stream.write(dump(receipt)+'\n')
    output.mkdir(exist_ok=False)
    (output/'authorization.json').write_text(dump(receipt)+'\n')
    planned = [(n, e) for n in config['sizes'] for e in config['engines']]
    rows, outcomes, stop = [], {}, False
    budget = config['run_budget']
    if len(planned) != budget['children']:
        raise ValueError('child count differs from budget')
    for size, engine in planned:
        if stop:
            rows.append({'size': size, 'engine': engine, 'status': 'NOT_RUN_AFTER_STOP', 'failure_retained': True})
            continue
        directory = output/(str(size)+'_'+engine)
        directory.mkdir()
        args = [sys.executable, '-B', str(Path(__file__).resolve()), '--child', str(directory), '--size', str(size), '--engine', engine]

        def limits():
            resource.setrlimit(resource.RLIMIT_CPU, (budget['cpu_seconds_per_child'], budget['cpu_seconds_per_child']))
            resource.setrlimit(resource.RLIMIT_AS, (budget['address_space_bytes_per_child'], budget['address_space_bytes_per_child']))
            resource.setrlimit(resource.RLIMIT_FSIZE, (budget['output_bytes_per_child'], budget['output_bytes_per_child']))

        before = resource.getrusage(resource.RUSAGE_CHILDREN)
        started = time.perf_counter_ns()
        with (directory/'process.log').open('x') as log:
            child = subprocess.Popen(args, stdout=log, stderr=subprocess.STDOUT, preexec_fn=limits)
            timed_out = False
            try:
                code = child.wait(timeout=budget['wall_seconds_per_child'])
            except subprocess.TimeoutExpired:
                timed_out = True
                child.kill(); code = child.wait()
        wall = time.perf_counter_ns()-started
        after = resource.getrusage(resource.RUSAGE_CHILDREN)
        cpu = int(1e9*((after.ru_utime+after.ru_stime)-(before.ru_utime+before.ru_stime)))
        byte_count = sum(p.stat().st_size for p in directory.iterdir() if p.is_file())
        result_path = directory/'result.json'
        try:
            result = json.loads(result_path.read_text()) if result_path.exists() else {'status': 'PROCESS_FAILED_NO_RESULT'}
            if not isinstance(result, dict) or 'status' not in result:
                raise ValueError('result schema absent')
        except (ValueError, OSError) as exc:
            result = {'status': 'PROCESS_FAILED_INVALID_RESULT', 'failure': str(exc)}
        process_success = code == 0 and not timed_out and byte_count <= budget['output_bytes_per_child'] and result.get('success') is True
        if not process_success:
            result = {**result, 'success': False}
        outcomes[(size, engine)] = result
        row = {'size': size, 'engine': engine, 'status': result['status'], 'exit_code': code,
               'host_timeout': timed_out, 'total_process_wall_ns': wall, 'total_process_cpu_ns': cpu,
               'output_bytes': byte_count, 'failure_retained': not process_success,
               'process_success': process_success, 'output_budget_exceeded': byte_count > budget['output_bytes_per_child'],
               'cost_scope': 'spawn through child exit, including imports, final serialization and log I/O'}
        rows.append(row)
        stop = not process_success
    comparisons = []
    for size in config['sizes']:
        a, b = (outcomes.get((size, e)) for e in config['engines'])
        keys = ('completion', 'messages', 'bytes', 'public_wire_sha256', 'operations', 'constraint_count', 'initial_wait')
        paired = bool(a and b and a.get('success') and b.get('success'))
        comparisons.append({'size': size, 'both_success': paired,
                            'same_decisions_and_work': paired and all(a[k] == b[k] for k in keys),
                            'guarantee_increment': 'NONE_BY_SHARED_CERTIFICATE_CONSTRUCTION',
                            'cost_interpretation': 'single DEV pair; wrapper overhead/noise is not a constraint-algorithm speedup'})
    equal = all(p['both_success'] and p['same_decisions_and_work'] for p in comparisons)
    (output/'RUN_RECEIPT.json').write_text(dump({'authorization': receipt, 'rows': rows, 'retry': 0,
                                              'comparisons': comparisons,
                                              'decision': 'CLOSE_CURRENT_SAME_CERTIFICATE_CONTRIBUTION_CANDIDATE' if equal else 'STOP_AND_DIAGNOSE_NO_EXPANSION',
                                              'all_planned_children_retained': True})+'\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check-inputs', action='store_true')
    parser.add_argument('--execute', action='store_true')
    parser.add_argument('--permission')
    parser.add_argument('--output')
    parser.add_argument('--child', help=argparse.SUPPRESS)
    parser.add_argument('--size', type=int, choices=(2, 3))
    parser.add_argument('--engine', choices=('guard', 'SADG_events'))
    args = parser.parse_args()
    if args.check_inputs:
        print(dump({'pins': verify_inputs(), 'runtime_started': False}))
    elif args.child:
        directory = Path(args.child).resolve()
        parent = BASE/'timed_run_once_20261016'
        if directory.parent != parent or not (parent/'authorization.json').is_file():
            parser.error('internal child requires the authorized parent receipt')
        receipt = validate_permission(parent/'authorization.json')
        if not (BASE/('.timed_permission_consumed_'+receipt['manifest_sha256'])).is_file():
            parser.error('one-use marker absent')
        if directory.name != str(args.size)+'_'+str(args.engine):
            parser.error('child identity does not match predeclared output')
        with (directory/'CHILD_STARTED.json').open('x') as stream:
            stream.write(dump({'size': args.size, 'engine': args.engine, 'retry': 0})+'\n')
        sys.exit(task_child(directory, args.size, args.engine))
    elif args.execute:
        if not args.permission or not args.output:
            parser.error('--execute requires a new permission receipt and fixed output')
        bounded_run(args.permission, args.output)
    else:
        parser.print_help()
