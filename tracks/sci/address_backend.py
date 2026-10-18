"""Actual ADDRESS-SIPP callback and common discrete validator for pp_repair.

Importing this module does not run a solver. NativeBackend construction does:
it belongs inside an explicitly authorized case and its outer process budget.
"""
import hashlib
import json
import os
from pathlib import Path
import resource
import select
import signal
import subprocess
import time
from types import MappingProxyType

from pp_repair import SearchReply, SearchStatus

AUTHOR = 'b3d35c431ce03834f95e834d87986f2f341394a1'
MAX_TIMESTEP = (2**31 - 1) // 2
MAX_FRAME = 16 * 1024 * 1024


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def integer(value, low=0, high=MAX_TIMESTEP):
    if type(value) is not int or not low <= value < high:
        raise ValueError('integer outside declared domain')
    return value


class GridProblem:
    """Unit-time, unit-cost four-neighbor grid; wait allowed, goals held forever."""
    def __init__(self, rows, cols, blocked, endpoints):
        self.rows, self.cols = integer(rows, 1), integer(cols, 1)
        if rows * cols > 1_000_000:
            raise ValueError('adapter limit: at most 1000000 cells')
        self.blocked = frozenset(integer(v, 0, rows * cols) for v in blocked)
        if not endpoints or len(endpoints) > 10_000:
            raise ValueError('adapter requires 1..10000 agents')
        normalized = {}
        for agent, pair in endpoints.items():
            integer(agent)
            if len(pair) != 2:
                raise ValueError('start/goal pair required')
            start, goal = (integer(v, 0, rows * cols) for v in pair)
            if start in self.blocked or goal in self.blocked:
                raise ValueError('blocked endpoint')
            normalized[agent] = (start, goal)
        if len({v[0] for v in normalized.values()}) != len(normalized):
            raise ValueError('start vertex conflict')
        if len({v[1] for v in normalized.values()}) != len(normalized):
            raise ValueError('permanent goal conflict')
        self.endpoints = MappingProxyType(normalized)
        self.ids = tuple(sorted(normalized))
        self.native_ids = {agent: index for index, agent in enumerate(self.ids)}
        self.model_key = sha(canonical({'rows': rows, 'cols': cols, 'blocked': sorted(self.blocked),
            'endpoints': sorted(normalized.items()), 'semantics': '4NEIGHBOR_UNIT_WAIT_VERTEX_SWAP_GOAL_HOLD_V1'}))

    def validate(self, paths, *, complete=True):
        if (complete and set(paths) != set(self.ids)) or not set(paths) <= set(self.ids):
            raise ValueError('robot set does not match the declared problem')
        for a, path in paths.items():
            if not path or len(path) > 1_000_000:
                raise ValueError('adapter requires 1..1000000 vertices per path')
            if (path[0], path[-1]) != self.endpoints[a]:
                raise ValueError('path endpoints changed')
            for t, v in enumerate(path):
                integer(v, 0, self.rows * self.cols)
                if v in self.blocked:
                    raise ValueError('path enters obstacle')
                if t:
                    before = path[t - 1]
                    distance = abs(v // self.cols - before // self.cols) + abs(v % self.cols - before % self.cols)
                    if distance > 1:
                        raise ValueError('nonlocal/diagonal grid move')
        for t in range(max(map(len, paths.values()), default=0)):
            occupied, edges = {}, set()
            for a, path in paths.items():
                v = path[min(t, len(path) - 1)]
                if v in occupied:
                    raise ValueError('vertex/goal-hold conflict')
                occupied[v] = a
                if t:
                    u = path[min(t - 1, len(path) - 1)]
                    if (v, u) in edges:
                        raise ValueError('opposite-edge conflict')
                    edges.add((u, v))
        return True

    def author_files(self):
        # Exactly the author's custom format. Not MovingAI seconds/metres.
        grid = str(self.rows) + ',' + str(self.cols) + '\n'
        grid += ''.join(''.join('@' if r * self.cols + c in self.blocked else '.'
                                for c in range(self.cols)) + '\n' for r in range(self.rows))
        agents = str(len(self.ids)) + '\n'
        for a in self.ids:
            s, g = self.endpoints[a]
            agents += ','.join(map(str, (s // self.cols, s % self.cols, g // self.cols, g % self.cols))) + '\n'
        return grid.encode(), agents.encode()


class NativeBackend:
    """One persistent author process per arm, with reused author h tables.

    No retry/restart. Outer case timing must cover this constructor, repair,
    close(), final serialization and I/O. The child CPU/AS limits and RPC wall
    deadline do not replace a hard supervisor for the entire Python process.
    """
    def __init__(self, problem, incumbent_paths, binary, build_receipt, session_dir,
                 budget, *, seed, cpu_seconds=45, memory_mib=512):
        self.problem, self.budget = problem, budget
        self.seed = integer(seed)
        integer(cpu_seconds, 1)
        integer(memory_mib, 64)
        self.proc, self.log, self.seq = None, None, 0
        self.buffer = bytearray()
        self.cache = {'model_key': problem.model_key, 'scope': 'AUTHOR_H_TABLES_NO_PATH_RESULT_CACHE'}
        self.records, self.child_usage = [], None
        self.lower_bounds = None
        try:
            budget.check()
            if budget.clock_ns is not time.monotonic_ns:
                raise ValueError('native deadline requires the real monotonic clock')
            problem.validate(incumbent_paths)
            self.initial_sha256 = sha(canonical(sorted(incumbent_paths.items())))
            binary = Path(binary).resolve()
            receipt = json.loads(Path(build_receipt).read_bytes())
            if (receipt['author_commit'] != AUTHOR or receipt['exit_code'] != 0
                    or receipt['scope'] != 'COMPILE_AND_DESCRIBE_ONLY_NO_INSTANCE_OR_SEARCH'
                    or receipt['describe']['protocol'] != 'address_sipp_bridge_v1'
                    or receipt['describe']['solver_called'] is not False
                    or receipt['binary_sha256'] != sha(binary.read_bytes())
                    or receipt['bridge_sha256'] != sha(Path(__file__).with_name('address_sipp_bridge.cpp').read_bytes())):
                raise ValueError('unqualified or changed backend build')
            self.build_receipt_sha256 = sha(Path(build_receipt).read_bytes())
            folder = Path(session_dir).resolve()
            folder.mkdir(parents=True, exist_ok=False)
            map_raw, agents_raw = problem.author_files()
            (folder / 'map.txt').write_bytes(map_raw)
            (folder / 'agents.txt').write_bytes(agents_raw)
            self.input_sha256 = {'map': sha(map_raw), 'agents': sha(agents_raw)}
            self.log = (folder / 'native.stderr.log').open('wb')
            def limits():
                resource.setrlimit(resource.RLIMIT_CPU, (cpu_seconds, cpu_seconds))
                resource.setrlimit(resource.RLIMIT_AS, (memory_mib * 1024**2,) * 2)
                resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            self.proc = subprocess.Popen([str(binary), '--serve'], stdin=subprocess.PIPE,
                stdout=subprocess.PIPE, stderr=self.log, start_new_session=True, preexec_fn=limits)
            os.set_blocking(self.proc.stdin.fileno(), False)
            os.set_blocking(self.proc.stdout.fileno(), False)
            answer = self._rpc({'op': 'init', 'map_file': str(folder / 'map.txt'),
                                'agents_file': str(folder / 'agents.txt'), 'seed': self.seed})
            if answer['status'] != 'READY' or answer['base_length_max'] != MAX_TIMESTEP:
                raise ValueError('author initialization failed: ' + str(answer))
            lower = answer['lower_bounds']
            if len(lower) != len(problem.ids):
                raise ValueError('lower-bound coverage mismatch')
            self.lower_bounds = {a: integer(h) for a, h in zip(problem.ids, lower)}
            if any(self.lower_bounds[a] > len(incumbent_paths[a]) - 1 for a in problem.ids):
                raise ValueError('author h contradicts the validated incumbent')
            budget.check()
        except Exception:
            self.close()
            raise

    def _remaining(self):
        remaining = (self.budget.deadline_ns - time.monotonic_ns()) / 1e9
        if remaining <= 0:
            raise TimeoutError('native RPC deadline reached')
        return remaining

    def _rpc(self, request):
        request = dict(request, seq=self.seq)
        self.seq += 1
        wire = canonical(request) + b'\n'
        if len(wire) > MAX_FRAME or self.proc is None:
            raise ValueError('native RPC unavailable or request exceeds frame limit')
        entry = {'request_sha256': sha(wire), 'request_bytes': len(wire), 'op': request['op'],
                 'status': 'PENDING'}
        self.records.append(entry)
        started = time.monotonic_ns()
        try:
            view = memoryview(wire)
            while view:
                _, writable, _ = select.select([], [self.proc.stdin.fileno()], [], self._remaining())
                if not writable:
                    raise TimeoutError('native request write timeout')
                view = view[os.write(self.proc.stdin.fileno(), view):]
            while b'\n' not in self.buffer:
                readable, _, _ = select.select([self.proc.stdout.fileno()], [], [], self._remaining())
                if not readable:
                    raise TimeoutError('native response timeout')
                chunk = os.read(self.proc.stdout.fileno(), 65536)
                if not chunk:
                    raise RuntimeError('native process exited before a complete response')
                self.buffer.extend(chunk)
                if len(self.buffer) > MAX_FRAME:
                    raise ValueError('native response exceeds frame limit')
            raw, _, tail = self.buffer.partition(b'\n')
            self.buffer = bytearray(tail)
            answer = json.loads(raw)
            if answer['seq'] != request['seq'] or answer['author_commit'] != AUTHOR:
                raise ValueError('native response identity mismatch')
            self._remaining()
            entry.update({'response_sha256': sha(raw + b'\n'), 'response_bytes': len(raw) + 1,
                          'status': answer['status'], 'response': answer})
            return answer
        except Exception as error:
            entry.update({'status': 'TIMEOUT' if isinstance(error, TimeoutError) else 'FAILED',
                          'reason': type(error).__name__ + ': ' + str(error)})
            self.close()
            raise
        finally:
            entry['wall_ns'] = time.monotonic_ns() - started

    def search(self, request):
        if (request.budget is not self.budget or request.shared_cache is not self.cache
                or request.model_key != self.problem.model_key
                or (request.start, request.goal) != self.problem.endpoints[request.agent]):
            raise ValueError('backend request does not match its model/budget/cache')
        if set(request.fixed_paths) & set(request.prefix_paths):
            raise ValueError('fixed/prefix overlap')
        order = tuple(request.order)
        if (not order or len(set(order)) != len(order)
                or not set(order) <= set(self.problem.ids) or request.agent not in order
                or set(request.fixed_paths) != set(self.problem.ids) - set(order)
                or set(request.prefix_paths) != set(order[:order.index(request.agent)])):
            raise ValueError('fixed/prefix paths do not cover the declared PP request')
        paths = {**request.fixed_paths, **request.prefix_paths}
        self.problem.validate(paths, complete=False)
        if request.max_cost is not None:
            integer(request.max_cost)
        # Same RNG seed for identical geometry/order/prefix across the two cap policies.
        seed_key = (self.seed, request.agent, request.order, sorted(paths.items()))
        seed = int(sha(canonical(seed_key))[:8], 16) % MAX_TIMESTEP
        answer = self._rpc({'op': 'search', 'agent': self.problem.native_ids[request.agent],
            'seed': seed, 'max_cost': request.max_cost,
            'fixed_paths': [{'agent': self.problem.native_ids[a], 'path': p} for a, p in sorted(paths.items())]})
        if answer['status'] == 'FOUND':
            candidate = tuple(answer['path'])
            self.problem.validate({**paths, request.agent: candidate}, complete=False)
            expected_cap = MAX_TIMESTEP if request.max_cost is None else request.max_cost
            if (answer['effective_max_cost'] != expected_cap
                    or (request.max_cost is not None and len(candidate) - 1 > request.max_cost)):
                raise ValueError('native cost cap mismatch')
            if answer['num_collisions'] != 0:
                raise ValueError('native returned a colliding path')
            return SearchReply(SearchStatus.FOUND, candidate)
        # Empty author return alone is not promoted to a verified exhaustive-search
        # certificate. Retain and censor until that backend qualification is done.
        if answer['status'] not in ('EMPTY_CAPPED', 'EMPTY_BASE_LIMIT'):
            self.close()  # An exception may leave author search state incomplete.
        return SearchReply(SearchStatus.FAILED, reason='native ' + answer['status'] + ': ' + answer.get('reason', 'empty/unknown search result'))

    def validate(self, request):
        if (request.model_key != self.problem.model_key or request.budget is not self.budget
                or request.shared_cache is not self.cache):
            raise ValueError('validator identity mismatch')
        return self.problem.validate(request.paths)

    def close(self):
        """Terminate/reap exactly this child; preserve stderr and CPU/RSS accounting."""
        if self.proc is not None:
            process, self.proc = self.proc, None
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            until = time.monotonic() + 0.25
            while True:
                try:
                    pid, status, usage = os.wait4(process.pid, os.WNOHANG)
                except ChildProcessError:
                    self.child_usage = {'status': 'UNAVAILABLE_ALREADY_REAPED'}
                    break
                if pid:
                    break
                if time.monotonic() >= until:
                    try:
                        os.killpg(process.pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass
                    pid, status, usage = os.wait4(process.pid, 0)
                    break
                time.sleep(0.005)
            if self.child_usage is None:
                process.returncode = os.waitstatus_to_exitcode(status)
                self.child_usage = {'exit_code': process.returncode, 'user_s': usage.ru_utime,
                                    'system_s': usage.ru_stime, 'maxrss_kib': usage.ru_maxrss}
            process.stdin.close()
            process.stdout.close()
        if self.log is not None:
            self.log.close()
            self.log = None
