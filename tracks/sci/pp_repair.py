"""Budgeted PP repair transaction; a solver callback supplies all path search.

Discrete unit-cost MAPF only. The lower-bound rule is classical, not a novelty
claim. Pruning is conditional on this order and its already fixed prefix.
No map, benchmark, world, training, or research executor is imported here.
"""

from dataclasses import dataclass, field
from enum import Enum
from hashlib import sha256
import json
from threading import Lock
from time import monotonic_ns, process_time_ns
from types import MappingProxyType
from typing import Callable, Mapping, Optional, Tuple


Path = Tuple[int, ...]


def _integer(value, name):
    if type(value) is not int or value < 0:
        raise ValueError(name + " must be a nonnegative integer")
    return value


def _paths(paths):
    result = {}
    for agent, path in paths.items():
        _integer(agent, "agent")
        path = tuple(path)
        if not path:
            raise ValueError("paths must include start and goal")
        for vertex in path:
            _integer(vertex, "vertex")
        result[agent] = path
    return MappingProxyType(result)


def _digest(value):
    return sha256(json.dumps(value, separators=(",", ":")).encode()).hexdigest()


def _path_digest(paths):
    return _digest(sorted(paths.items()))


@dataclass(frozen=True)
class Snapshot:
    version: int
    paths: Mapping[int, Path]
    sha256: str


class Incumbent:
    """Caller supplies a validated initial plan; replacement is compare-and-swap.

    The host/callbacks are trusted code. This is an in-process transaction, not
    isolation from malicious callbacks or an atomic network robot launch.
    """

    def __init__(self, paths):
        paths = _paths(paths)
        self._snapshot = Snapshot(0, paths, _path_digest(paths))
        self._lock = Lock()

    def snapshot(self):
        with self._lock:
            return self._snapshot

    def _commit(self, expected, paths, budget):
        paths = _paths(paths)
        digest = _path_digest(paths)
        with self._lock:
            budget.check()
            if self._snapshot is not expected:
                return False
            self._snapshot = Snapshot(expected.version + 1, paths, digest)
            return True


class SearchStatus(str, Enum):
    FOUND = "FOUND"
    EXHAUSTED_WITHIN_CAP = "EXHAUSTED_WITHIN_CAP"
    INFEASIBLE = "INFEASIBLE"  # complete search without a cost cap
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"


class RepairStatus(str, Enum):
    ACCEPTED = "ACCEPTED"
    NO_IMPROVEMENT = "NO_IMPROVEMENT"
    INFEASIBLE = "INFEASIBLE"
    TIMEOUT = "TIMEOUT"
    FAILED = "FAILED"
    STALE = "STALE_INCUMBENT"


class Policy(str, Enum):
    ORIGINAL_PREFIX = "ORIGINAL_PREFIX"
    REMAINING_BOUND = "REMAINING_BOUND"


class _Expired(Exception):
    pass


@dataclass
class SharedBudget:
    """One absolute deadline/call allowance across repairs, including failures.

    Callbacks must cooperate or run behind a process supervisor: checking the
    clock after a callback prevents late acceptance, but cannot preempt it.
    Cache work inside a callback is included in that callback's charged time.
    Construction/import/serialization outside repair() need an outer timer.
    """

    deadline_ns: int
    max_search_calls: int
    clock_ns: Callable[[], int] = monotonic_ns
    cpu_clock_ns: Callable[[], int] = process_time_ns
    search_calls: int = field(default=0, init=False)
    stage_wall_ns: dict = field(default_factory=dict, init=False)
    stage_cpu_ns: dict = field(default_factory=dict, init=False)

    def __post_init__(self):
        _integer(self.deadline_ns, "deadline_ns")
        _integer(self.max_search_calls, "max_search_calls")

    def check(self):
        if self.clock_ns() >= self.deadline_ns:
            raise _Expired("absolute deadline reached")

    def reserve_search(self):
        self.check()
        if self.search_calls >= self.max_search_calls:
            raise _Expired("shared search-call budget exhausted")
        self.search_calls += 1

    def measure(self, stage, callback, *, check_after=True):
        wall, cpu = self.clock_ns(), self.cpu_clock_ns()
        try:
            self.check()
            value = callback()
            if check_after:
                self.check()
            return value
        finally:
            self.stage_wall_ns[stage] = self.stage_wall_ns.get(stage, 0) + self.clock_ns() - wall
            self.stage_cpu_ns[stage] = self.stage_cpu_ns.get(stage, 0) + self.cpu_clock_ns() - cpu


@dataclass(frozen=True)
class SearchRequest:
    agent: int
    start: int
    goal: int
    max_cost: Optional[int]
    fixed_paths: Mapping[int, Path]
    prefix_paths: Mapping[int, Path]
    order: Tuple[int, ...]
    model_key: str
    constraint_key: str
    budget: SharedBudget
    shared_cache: object


@dataclass(frozen=True)
class SearchReply:
    status: SearchStatus
    path: Path = ()
    reason: str = ""


@dataclass(frozen=True)
class ValidationRequest:
    paths: Mapping[int, Path]
    changed_agents: Tuple[int, ...]
    model_key: str
    budget: SharedBudget
    shared_cache: object


@dataclass(frozen=True)
class RepairResult:
    status: RepairStatus
    reason: str
    before: Snapshot
    after: Snapshot
    order: Tuple[int, ...]
    old_cost: Optional[int]
    candidate_cost: Optional[int]
    completed_agents: int
    search_calls: int
    wall_ns: int
    cpu_ns: int
    # None denotes censored/error/stale, never a success/failure training label.
    improvement_label: Optional[bool]
    scope: str = "THIS_ORDER_AND_ALREADY_FIXED_PREFIX_ONLY"


def repair(incumbent, order, lower_bounds, *, model_key, search, validate,
           budget, shared_cache, policy=Policy.REMAINING_BOUND):
    """Propose a complete PP repair and commit only a verified strict improvement.

    lower_bounds[a] must be an admissible integer path-cost bound for the exact
    same static map/start/goal/model. Merely being <= the incumbent is insufficient
    evidence; the backend owns this precondition and should reuse its shared h.
    `validate` is the same complete map/vertex/edge/goal-hold checker for both
    policies and must return exactly True; it is not replaced by path-length tests.
    EXHAUSTED_WITHIN_CAP is allowed only after exhaustive search for this request.
    A deadline, exception, or partial search must return TIMEOUT/FAILED instead.
    """
    wall, cpu = budget.clock_ns(), budget.cpu_clock_ns()
    before = incumbent.snapshot()
    calls_before = budget.search_calls
    selected, old_cost, candidate_cost, completed = (), None, None, 0

    def finish(status, reason):
        label = {RepairStatus.ACCEPTED: True, RepairStatus.NO_IMPROVEMENT: False,
                 RepairStatus.INFEASIBLE: False}.get(status)
        return RepairResult(status, reason, before, incumbent.snapshot(), selected,
                            old_cost, candidate_cost, completed,
                            budget.search_calls - calls_before,
                            budget.clock_ns() - wall, budget.cpu_clock_ns() - cpu, label)

    try:
        def prepare():
            if not isinstance(policy, Policy):
                raise ValueError("policy must be a Policy")
            if not isinstance(model_key, str) or not model_key:
                raise ValueError("model_key must identify the common map and semantics")
            selected = tuple(order)
            if not selected or len(set(selected)) != len(selected):
                raise ValueError("order must be a nonempty unique agent sequence")
            for agent in selected:
                _integer(agent, "agent")
                if agent not in before.paths:
                    raise ValueError("unknown selected agent")
                _integer(lower_bounds[agent], "lower_bound")
                if lower_bounds[agent] > len(before.paths[agent]) - 1:
                    raise ValueError("lower bound contradicts the validated incumbent")
            fixed = MappingProxyType({a: p for a, p in before.paths.items() if a not in selected})
            return selected, fixed, _path_digest(fixed), {a: lower_bounds[a] for a in selected}

        selected, fixed, fixed_key, bounds = budget.measure("prepare", prepare)
        old_cost = sum(len(before.paths[a]) - 1 for a in selected)
        target = old_cost - 1
        prefix, prefix_cost = {}, 0
        remaining_lb = sum(bounds.values())
        prefix_hash = sha256()
        for index, agent in enumerate(selected):
            budget.check()
            if policy is Policy.REMAINING_BOUND:
                if prefix_cost + remaining_lb > target:
                    return finish(RepairStatus.NO_IMPROVEMENT, "remaining lower bound exceeds strict target")
                cap = target - prefix_cost - (remaining_lb - bounds[agent])
            else:
                # Author-style control: no new per-agent length cap; stop when
                # the already realized prefix alone cannot strictly improve.
                if prefix_cost > target:
                    return finish(RepairStatus.NO_IMPROVEMENT, "realized prefix exceeds strict target")
                cap = None
            request = SearchRequest(
                agent, before.paths[agent][0], before.paths[agent][-1], cap,
                fixed, MappingProxyType(dict(prefix)), selected, model_key,
                _digest((model_key, fixed_key, prefix_hash.hexdigest(), agent, cap)),
                budget, shared_cache)
            budget.reserve_search()
            reply = budget.measure("search", lambda: search(request))
            if not isinstance(reply, SearchReply) or not isinstance(reply.status, SearchStatus):
                raise ValueError("backend returned an invalid SearchReply")
            if reply.status is SearchStatus.TIMEOUT:
                return finish(RepairStatus.TIMEOUT, reply.reason or "backend timeout")
            if reply.status is SearchStatus.FAILED:
                return finish(RepairStatus.FAILED, reply.reason or "backend failure")
            if reply.status is SearchStatus.EXHAUSTED_WITHIN_CAP:
                if cap is None:
                    raise ValueError("exhausted-within-cap requires an actual cost cap")
                return finish(RepairStatus.NO_IMPROVEMENT, "complete search exhausted the current improvement cap")
            if reply.status is SearchStatus.INFEASIBLE:
                if cap is not None:
                    raise ValueError("capped search cannot declare unrestricted infeasibility")
                return finish(RepairStatus.INFEASIBLE, "complete unrestricted search found no continuation")
            path = tuple(reply.path)
            _paths({agent: path})
            cost = len(path) - 1
            if path[0] != request.start or path[-1] != request.goal:
                raise ValueError("backend changed the agent's start or goal")
            if cost < bounds[agent]:
                raise ValueError("backend path contradicts the supplied lower bound")
            if cap is not None and cost > cap:
                raise ValueError("backend path exceeds its cost cap")
            prefix[agent] = path
            prefix_hash.update(json.dumps((agent, path), separators=(",", ":")).encode())
            prefix_cost += cost
            remaining_lb -= bounds[agent]
            completed = index + 1
        candidate_cost = prefix_cost
        if candidate_cost >= old_cost:
            return finish(RepairStatus.NO_IMPROVEMENT, "complete repair is not a strict improvement")
        candidate = MappingProxyType({**fixed, **prefix})
        verdict = budget.measure("validate", lambda: validate(
            ValidationRequest(candidate, selected, model_key, budget, shared_cache)))
        if verdict is not True:
            return finish(RepairStatus.FAILED, "common complete-plan validator did not return True")
        # _commit checks the same deadline under the lock immediately before
        # replacement. Never turn an already committed plan into a timeout.
        accepted = budget.measure("commit", lambda: incumbent._commit(before, candidate, budget),
                                  check_after=False)
        if not accepted:
            return finish(RepairStatus.STALE, "incumbent changed while repair was in flight")
        return finish(RepairStatus.ACCEPTED, "complete strict improvement accepted")
    except (_Expired, TimeoutError) as exc:
        return finish(RepairStatus.TIMEOUT, str(exc))
    except Exception as exc:
        return finish(RepairStatus.FAILED, type(exc).__name__ + ": " + str(exc))
