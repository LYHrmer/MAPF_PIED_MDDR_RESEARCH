"""Conditional schedule GEOMETRY certificates; no dispatcher or optimizer.

Explicit starts insert finite WAITs into unchanged v2 primitives. A certificate
assumes one common, zero-jitter program epoch and immutable complete chains.
It does not confirm that commands were accepted, authorize motion, or supply END.
Imports have no scientific-run side effects. Calling consider() does perform
continuous interval checks and requires a separately authorized run budget.
"""
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from time import perf_counter_ns, process_time_ns
import hashlib
import json

import composition
import interface
import protocol
import timed
import timed_constraints
import timed_protocol
from composition import Chain, contract, exact
from interface import Box
from timed import Anchor, Trajectory
from timed_constraints import Certificates
from timed_protocol import Costs


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     default=str, allow_nan=False).encode()).hexdigest()


def _code_identity():
    modules = (composition, interface, protocol, timed, timed_constraints, timed_protocol)
    paths = {m.__name__: Path(m.__file__) for m in modules}
    paths['preexecution_schedule'] = Path(__file__)
    return {name: hashlib.sha256(path.read_bytes()).hexdigest()
            for name, path in paths.items()}


@dataclass(frozen=True)
class ValidationBudget:
    """Per-proposal ceilings; a complete optimizer needs its own total budget."""
    resolution: Q
    max_cells: int
    horizon: Q
    wall_ns: int
    cpu_ns: int

    def __post_init__(self):
        if (not isinstance(self.resolution, Q) or self.resolution <= 0
                or type(self.max_cells) is not int or self.max_cells < 1
                or not isinstance(self.horizon, Q) or self.horizon <= 0
                or any(type(x) is not int or x <= 0 for x in (self.wall_ns, self.cpu_ns))):
            raise ValueError('exact positive resolution/horizon and total cell budget required')


def _expired(deadlines):
    return perf_counter_ns() >= deadlines[0] or process_time_ns() >= deadlines[1]


def _cap_deadlines(local, external):
    if external is None:
        return local
    if len(external) != 2 or any(type(x) is not int or x <= 0 for x in external):
        raise ValueError('absolute monotonic wall/CPU nanosecond deadlines required')
    return tuple(min(a, b) for a, b in zip(local, external))


def compile_schedule(specs, starts, world_bounds, *, obstacles, horizon):
    """Starts name EVERY original finite primitive, including original WAITs.

    Keys are robot IDs; each value is a sequence of exact start times relative
    to common epoch zero. Gaps add WAITs only at stopped boundaries. Original
    finite actions and the terminal HOLD are retained, including all durations.
    """
    if not isinstance(specs, dict) or not 2 <= len(specs) <= 3:
        raise ValueError('this prototype accepts complete two/three-robot tasks')
    if set(starts) != set(specs) or any(not isinstance(r, str) or not r for r in specs):
        raise ValueError('one complete start-time vector per named robot required')
    xmin, xmax, ymin, ymax = map(exact, world_bounds)
    world = Box(xmin, xmax, ymin, ymax)
    if (not isinstance(obstacles, (list, tuple))
            or any(not isinstance(b, (list, tuple)) or len(b) != 4 for b in obstacles)):
        raise ValueError('explicit closed axis-aligned obstacle rectangles required; [] is allowed')
    blocked = tuple(Box(*map(exact, bounds)) for bounds in obstacles)
    horizon = exact(horizon)
    plans, trajectories, mapping, normalized = {}, {}, {}, {}
    for robot in sorted(specs):
        original = Chain.build(specs[robot])
        finite = original.primitives[:-1]
        supplied = starts[robot]
        if not isinstance(supplied, (list, tuple)) or len(supplied) != len(finite):
            raise ValueError('missing/extra finite action start for '+robot)
        times = tuple(exact(s) for s in supplied)
        actions, indices, cursor = [], [], Q(0)
        for index, (action, start) in enumerate(zip(finite, times)):
            if start < cursor:
                raise ValueError('overlapping/reversed own actions for '+robot)
            if start > cursor:
                actions.append(['WAIT', str(start-cursor)])
            indices.append(len(actions))
            actions.append(deepcopy(specs[robot]['actions'][index]))
            cursor = start+action.duration
        actions.append(deepcopy(specs[robot]['actions'][-1]))
        spec = {'origin': deepcopy(specs[robot]['origin']),
                'heading': specs[robot]['heading'], 'actions': actions}
        scheduled = Chain.build(spec)
        if scheduled.duration != cursor or cursor > horizon:
            raise ValueError('incomplete schedule or declared horizon exceeded')
        if any(scheduled.primitives[j] != a for j, a in zip(indices, finite)):
            raise ValueError('original motion/controller primitive changed')
        if scheduled.primitives[-1] != original.primitives[-1]:
            raise ValueError('terminal HOLD changed')
        tr = Trajectory(robot, scheduled)
        box = Box(*tr.box(Q(0), scheduled.duration))
        if (box.xmin < world.xmin or box.xmax > world.xmax
                or box.ymin < world.ymin or box.ymax > world.ymax):
            raise ValueError('complete continuous outer occupancy not certified inside world')
        for index, (action, begin) in enumerate(zip(scheduled.primitives, tr.offsets)):
            end = begin+(action.duration or 0)
            occupied = Box(*tr.action_box(index, begin, end))
            if any(not occupied.separated(obstacle) for obstacle in blocked):
                raise ValueError('static obstacle separation UNRESOLVED; outer overlap is not collision')
        plans[robot], trajectories[robot] = spec, tr
        mapping[robot], normalized[robot] = indices, tuple(map(str, times))
    return {'scheduled_specs': plans, 'trajectories': trajectories,
            'original_to_scheduled': mapping, 'starts': normalized,
            'static_obstacles_checked': True,
            'obstacle_scope': 'EXPLICIT_CLOSED_AXIS_ALIGNED_RECTANGLES_ONLY',
            'obstacles': [tuple(map(str, (b.xmin, b.xmax, b.ymin, b.ymax))) for b in blocked],
            'sum_completion': sum(t.chain.duration for t in trajectories.values()),
            'makespan': max(t.chain.duration for t in trajectories.values())}


class _FullScheduleCertificates(Certificates):
    """Reuse pair() verbatim; bypass C1's policy-specific launch constructor."""
    def __init__(self, trajectories, budget):
        self.problem = {'trajectories': trajectories}
        self.resolution, self.limit = budget.resolution, budget.max_cells
        self.operations = {'phase_cells': 0, 'time_cells': 0,
                           'phase_cache_hits': 0, 'time_checks': 0}


def certify_schedule(compiled, budget, *, deadlines=None):
    """All unordered robot pairs, [0,last finish] and permanent terminal tails.

    Planned anchors are used only in this conditional offline proof. They are
    not legal feedback anchors and MUST NOT be forwarded to a release gate.
    Time checks occur between pair calls, not inside the frozen kernel. A future
    external process supervisor must enforce hard wall/CPU limits.
    """
    trajectories = compiled['trajectories']
    if (compiled.get('static_obstacles_checked') is not True
            or type(budget) is not ValidationBudget or not 2 <= len(trajectories) <= 3
            or any(type(t) is not Trajectory or t.robot != r or t.chain.duration > budget.horizon
                   for r, t in trajectories.items())):
        raise ValueError('complete compiled two/three-robot schedule and budget required')
    deadlines = _cap_deadlines((perf_counter_ns()+budget.wall_ns, process_time_ns()+budget.cpu_ns), deadlines)
    checker = _FullScheduleCertificates(trajectories, budget)
    anchors = {r: Anchor(Q(0), Q(0), Q(0), True, t.chain.duration)
               for r, t in trajectories.items()}
    records, checked = {}, set()
    pairs = tuple(combinations(sorted(trajectories), 2))
    status = 'CERTIFIED_CONDITIONAL_GEOMETRY'
    for a, b in pairs:
        if _expired(deadlines):
            status = 'UNRESOLVED'
            records[a+'|'+b] = {'status': 'UNRESOLVED', 'reason': 'TIME_BUDGET'}
            break
        remaining = budget.max_cells-checker.operations['time_cells']
        if remaining <= 0:
            status = 'UNRESOLVED'
            records[a+'|'+b] = {'status': 'UNRESOLVED', 'reason': 'TOTAL_CELL_BUDGET'}
            break
        # Existing pair() charges its first over-budget cell. Reserve that
        # charge so the declared TOTAL ceiling cannot be exceeded.
        checker.limit = remaining-1
        record = checker.pair(a, anchors[a], b, anchors[b], now=Q(0))
        checked.add((a, b))
        records[a+'|'+b] = record
        if _expired(deadlines):
            record['expired_after_pair'] = True
            status = 'UNRESOLVED'
            break
        if record['status'] != 'CERTIFIED_SEPARATED':
            status = 'UNRESOLVED'
            break
    coverage = 'ALL_TASK_SHARED_INITIAL_PARAMETERS_CONTINUOUS_TIME_AND_HOLDS'
    return {'status': status, 'pairs': records, 'operations': dict(checker.operations),
            'unchecked_pairs': [p for p in pairs if p not in checked],
            'coverage_requested': coverage,
            'coverage_certified': coverage if status == 'CERTIFIED_CONDITIONAL_GEOMETRY' else None,
            'problem_admissibility': 'NOT_CHECKED_NO_SWITCH_GROUP_CONTRACT',
            'condition': 'COMMON_ZERO_JITTER_EPOCH_IMMUTABLE_V2_CHAINS',
            'overlap_is_collision': False, 'is_dispatch_authorization': False,
            'physical_END_received': False}


class ScheduleIncumbent:
    """Keep geometry-certified proposals; task admissibility is NOT checked.

    No initial schedule is manufactured or assumed feasible by serializing
    robots. Callers/optimizers must supply complete starts. All rejected
    attempts are retained, but there is no optimizer or local-order selector.
    """
    def __init__(self, specs, world_bounds, budget, *, obstacles):
        if type(budget) is not ValidationBudget:
            raise ValueError('explicit immutable validation budget required')
        self._specs, self._world = deepcopy(specs), tuple(world_bounds)
        if not isinstance(obstacles, (list, tuple)):
            raise ValueError('explicit obstacle list required; no implicit obstacle-free map')
        self._obstacles = deepcopy(obstacles)
        self._budget, self._incumbent, self._attempts = budget, None, []
        self._identity = _digest({'specs': self._specs, 'world': self._world,
                                  'obstacles': self._obstacles,
                                  'source': contract(), 'budget': budget.__dict__})
        self._code = _code_identity()

    @property
    def incumbent(self):
        return deepcopy(self._incumbent)

    @property
    def attempts(self):
        return deepcopy(self._attempts)

    def consider(self, starts, *, absolute_deadlines=None):
        costs, candidate, validation, reason = Costs(), None, None, None
        deadlines = (costs.wall_start+self._budget.wall_ns, costs.cpu_start+self._budget.cpu_ns)
        accepted, proposal_sha = False, None
        previous = self._incumbent
        try:
            with costs.measure('compile_complete_schedule'):
                deadlines = _cap_deadlines(deadlines, absolute_deadlines)
                if _expired(deadlines):
                    raise ValueError('time budget exhausted before compilation')
                starts = deepcopy(starts)
                proposal_sha = _digest(starts)
                if _code_identity() != self._code:
                    raise ValueError('source/checker changed; new qualification required')
                candidate = compile_schedule(self._specs, starts, self._world,
                                             obstacles=self._obstacles, horizon=self._budget.horizon)
            with costs.measure('final_complete_continuous_validation'):
                if _expired(deadlines):
                    raise ValueError('time budget exhausted before validation')
                validation = certify_schedule(candidate, self._budget, deadlines=deadlines)
                if _code_identity() != self._code:
                    raise ValueError('source/checker changed during validation')
            with costs.measure('incumbent_comparison_and_artifact'):
                if validation['status'] != 'CERTIFIED_CONDITIONAL_GEOMETRY':
                    reason = 'CONTINUOUS_CERTIFICATE_UNRESOLVED'
                elif (self._incumbent is not None and candidate['sum_completion']
                      >= Q(self._incumbent['sum_completion'])):
                    reason = 'NO_STRICT_SUM_COMPLETION_IMPROVEMENT'
                else:
                    record = {k: v for k, v in candidate.items() if k != 'trajectories'}
                    record.update(validation=validation, input_sha256=self._identity,
                                  code_sha256=self._code, execution_status='NOT_EXECUTED',
                                  problem_admissibility='NOT_CHECKED_NO_SWITCH_GROUP_CONTRACT')
                    # Exact decimal/rational strings and independent owned data.
                    record = json.loads(json.dumps(record, default=str, sort_keys=True))
                    record['schedule_sha256'] = _digest(record)
                    if _expired(deadlines):
                        raise ValueError('time budget exhausted; candidate not installed')
                    self._incumbent, accepted = record, True
        except Exception as exc:
            reason = type(exc).__name__+': '+str(exc)
        report = {'accepted': accepted, 'reason': reason, 'validation': validation,
                  'proposal_sha256': proposal_sha, 'attempt_index': len(self._attempts),
                  'status': 'NEW_GEOMETRY_CERTIFIED_INCUMBENT' if accepted else
                  'NO_CERTIFIED_INCUMBENT' if self._incumbent is None else 'RETAINED_INCUMBENT',
                  'candidate_sum_completion': None if candidate is None else str(candidate['sum_completion']),
                  'incumbent_sha256': None if self._incumbent is None else self._incumbent['schedule_sha256'],
                  'problem_admissibility': 'NOT_CHECKED_NO_SWITCH_GROUP_CONTRACT',
                  'execution_interface': 'NOT_CONNECTED_NO_ATOMIC_JOINT_START_OR_END',
                  'hard_time_limit': 'EXTERNAL_SUPERVISOR_REQUIRED_NOT_ENFORCED_INSIDE_PAIR',
                  'budget_scope': 'PER_PROPOSAL_CAPPED_BY_OPTIONAL_CALLER_DEADLINES_TOTAL_OPTIMIZER_BUDGET_EXTERNAL',
                  'cost_scope': 'IN_PROCESS_INCLUDING_LEDGER_FINAL_TIMING_METADATA_AND_EXTERNAL_PROCESS_PENDING'}
        with costs.measure('attempt_copy_and_ledger'):
            stored, result = deepcopy(report), deepcopy(report)
            self._attempts.append(stored)
            if accepted and _expired(deadlines):
                self._incumbent = previous
                for row in (stored, result):
                    row.update(accepted=False, reason='TIME_BUDGET_AFTER_LEDGER',
                               status='NO_CERTIFIED_INCUMBENT' if previous is None else 'RETAINED_INCUMBENT',
                               incumbent_sha256=None if previous is None else previous['schedule_sha256'])
        stored['costs'] = costs.finish()
        result['costs'] = deepcopy(stored['costs'])
        return result
