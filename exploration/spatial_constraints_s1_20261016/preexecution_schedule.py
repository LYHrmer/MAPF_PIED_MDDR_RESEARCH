"""Declared pre-start orders, earliest schedules and conditional certificates.

Explicit starts insert finite WAITs into unchanged v2 primitives. A certificate
assumes one common, zero-jitter program epoch and immutable complete chains.
It does not confirm that commands were accepted, authorize motion, or supply END.
Imports have no scientific-run side effects. Calling consider() does perform
continuous interval checks and requires a separately authorized run budget.
"""
from copy import deepcopy
from dataclasses import dataclass, replace
from fractions import Fraction as Q
from itertools import combinations
from pathlib import Path
from time import perf_counter_ns, process_time_ns
import hashlib
import json

import composition
import interface
import protocol
import preexecution_order
import timed
import timed_constraints
import timed_protocol
from composition import Chain, contract, exact
from interface import Box
from preexecution_order import OrderContract
from timed import Anchor, Trajectory
from timed_constraints import Certificates
from timed_protocol import Costs


def _digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':'),
                                     default=str, allow_nan=False).encode()).hexdigest()


def _code_identity():
    modules = (composition, interface, protocol, preexecution_order,
               timed, timed_constraints, timed_protocol)
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


class _ActionWindowCertificates(Certificates):
    """Only the shared visits kernel; do not append C1's old END constraints."""
    def __init__(self, trajectories, budget):
        finite, intervals = {}, {}
        for robot, tr in trajectories.items():
            for index, action in enumerate(tr.chain.primitives[:-1]):
                name, begin = (robot, index), tr.offsets[index]
                finite[name], intervals[name] = name, (begin, begin+action.duration)
        self.problem = {'trajectories': trajectories, 'finite': finite, 'intervals': intervals}
        self.resolution, self.limit, self.cache = budget.resolution, budget.max_cells, {}
        self.operations = {'phase_cells': 0, 'time_cells': 0,
                           'phase_cache_hits': 0, 'time_checks': 0}


def _compile_order_contract(specs, declaration, mode, gap, budget, deadlines, audit):
    """Build both alternatives once, charging failures and cached visits alike.

    Window lags are sufficient conditions for a declared finite action pair.
    They are not a complete schedule certificate. Original task offsets are
    subtracted, but original task origins/initial parameters are never reset.
    Separated declared pairs retain END semantics as an explicit conservative
    fallback; this compiler never silently removes a caller's required order.
    """
    base = OrderContract(specs, declaration, separation_gap=gap)
    audit.update(status='BUILD_STARTED', mode=mode, base_contract_sha256=base.sha256, edges=[],
                 operations={'phase_cells': 0, 'time_cells': 0,
                             'phase_cache_hits': 0, 'time_checks': 0},
                 complete_schedule_safety_checked=False)
    if mode == 'END_TO_START':
        audit.update(status='BUILT_END_ORDER_CONTRACT', contract_sha256=base.sha256)
        return base
    if mode != 'WINDOW_START_LAGS':
        raise ValueError('unknown order mode')
    trajectories = {r: Trajectory(r, Chain.build(s)) for r, s in specs.items()}
    checker = _ActionWindowCertificates(trajectories, budget)
    # Keep a live counter reference so incomplete/failed builds remain charged.
    audit['operations'] = checker.operations
    boxes = {}
    for name, (r, i) in checker.problem['finite'].items():
        if _expired(deadlines):
            raise ValueError('time budget exhausted in action-window construction')
        boxes[name] = Box(*trajectories[r].action_box(i, *checker.problem['intervals'][name]))
    lags = {}
    for a, b in base.all_cross_edges:
        if _expired(deadlines):
            raise ValueError('time budget exhausted in cross-window construction')
        oa, ea = checker.problem['intervals'][a]
        ob, eb = checker.problem['intervals'][b]
        ba, bb = boxes[a], boxes[b]
        record = {'tail': a, 'head': b, 'kind': 'DECLARED_END_FALLBACK',
                  'fallback_reason': 'DISJOINT_FULL_OUTERS', 'windows': None}
        lag = ea-oa+gap
        if not ba.separated(bb):
            region = Box(max(ba.xmin, bb.xmin), min(ba.xmax, bb.xmax),
                         max(ba.ymin, bb.ymin), min(ba.ymax, bb.ymax))
            windows = []
            for name in (a, b):
                if _expired(deadlines):
                    raise ValueError('time budget exhausted before phase check')
                remaining = budget.max_cells-checker.operations['phase_cells']
                if (name, region) not in checker.cache and remaining <= 0:
                    raise ValueError('total cell budget exhausted in phase check')
                # visits charges the first over-limit cell, as pair does.
                checker.limit = max(0, remaining-1)
                windows.append(checker.visits(name, region))
                if _expired(deadlines):
                    raise ValueError('time budget exhausted after phase check')
            wa, wb = windows
            record.update(region=(region.xmin, region.xmax, region.ymin, region.ymax),
                          windows=windows, original_offsets=(oa, ob),
                          fallback_reason='EMPTY_VISIT_OUTER')
            if wa is not None and wb is not None:
                lag = (wa[1]-oa)-(wb[0]-ob)+gap
                record.update(kind='ROBUST_VISIT_WINDOW', fallback_reason=None)
        lags[(a, b)] = lag
        record['start_lag'] = lag
        audit['edges'].append(record)
    binding = {'specs_sha256': base.specs_sha256, 'declaration_sha256': _digest(declaration),
               'code_sha256': _code_identity(), 'resolution': budget.resolution,
               'gap': gap, 'edges': audit['edges']}
    proof_sha = _digest(binding)
    result = OrderContract(specs, declaration, separation_gap=gap,
                           cross_lags=lags, lag_provenance=proof_sha)
    audit.update(status='BUILT_CONDITIONAL_ACTION_WINDOWS', proof_sha256=proof_sha,
                 contract_sha256=result.sha256,
                 condition='ORIGINAL_V2_TASK_PARAMETERS_AND_UNCHANGED_STOPPED_PRIMITIVES',
                 interval_proof='CONTACT_IMPLIES_BOTH_BODIES_VISIT_FULL_OUTER_INTERSECTION',
                 uncertainty_domain='FROZEN_V2_NO_POSTERIOR_SHRINKAGE')
    return result


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
        pair_key = json.dumps((a, b), separators=(',', ':'))
        if _expired(deadlines):
            status = 'UNRESOLVED'
            records[pair_key] = {'status': 'UNRESOLVED', 'reason': 'TIME_BUDGET'}
            break
        remaining = budget.max_cells-checker.operations['time_cells']
        if remaining <= 0:
            status = 'UNRESOLVED'
            records[pair_key] = {'status': 'UNRESOLVED', 'reason': 'TOTAL_CELL_BUDGET'}
            break
        # Existing pair() charges its first over-budget cell. Reserve that
        # charge so the declared TOTAL ceiling cannot be exceeded.
        checker.limit = remaining-1
        record = checker.pair(a, anchors[a], b, anchors[b], now=Q(0))
        checked.add((a, b))
        records[pair_key] = record
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
    """Keep declared-order and geometry-certified pre-start proposals.

    No initial schedule is manufactured or assumed feasible by serializing
    robots. Earliest starts may be generated for explicit group directions.
    Groups are caller-declared, not automatically inferred maximal SADG groups.
    All rejected attempts are retained. There is no local-order selector or
    dispatch authority. Acyclic action graphs remain an adapter restriction.
    """
    def __init__(self, specs, world_bounds, budget, *, obstacles,
                 order_declaration, separation_gap, order_mode='WINDOW_START_LAGS'):
        if type(budget) is not ValidationBudget:
            raise ValueError('explicit immutable validation budget required')
        self._specs, self._world = deepcopy(specs), tuple(world_bounds)
        if not isinstance(obstacles, (list, tuple)):
            raise ValueError('explicit obstacle list required; no implicit obstacle-free map')
        self._obstacles = deepcopy(obstacles)
        if order_mode not in ('WINDOW_START_LAGS', 'END_TO_START'):
            raise ValueError('explicit window or END comparison mode required')
        self._declaration, self._gap = deepcopy(order_declaration), exact(separation_gap)
        if self._gap <= 0:
            raise ValueError('strict positive separation gap required')
        self._order_mode, self._order, self._order_audit = order_mode, None, None
        self._budget, self._incumbent, self._attempts = budget, None, []
        self._identity = _digest({'specs': self._specs, 'world': self._world,
                                  'obstacles': self._obstacles,
                                  'order_declaration': self._declaration,
                                  'order_mode': self._order_mode, 'separation_gap': self._gap,
                                  'source': contract(), 'budget': budget.__dict__})
        self._code = _code_identity()

    @property
    def incumbent(self):
        return deepcopy(self._incumbent)

    @property
    def attempts(self):
        return deepcopy(self._attempts)

    def consider(self, starts=None, *, directions, absolute_deadlines=None):
        costs, candidate, validation, reason = Costs(), None, None, None
        order_check, build_audit, phase_cells = None, {}, 0
        deadlines = (costs.wall_start+self._budget.wall_ns, costs.cpu_start+self._budget.cpu_ns)
        accepted, proposal_sha = False, None
        previous = self._incumbent
        try:
            with costs.measure('shared_order_windows_build_or_cache'):
                deadlines = _cap_deadlines(deadlines, absolute_deadlines)
                if _expired(deadlines):
                    raise ValueError('time budget exhausted before compilation')
                starts, directions = deepcopy(starts), deepcopy(directions)
                proposal_sha = _digest({'starts': starts, 'directions': directions})
                if _code_identity() != self._code:
                    raise ValueError('source/checker changed; new qualification required')
                if self._order is None:
                    order = _compile_order_contract(self._specs, self._declaration,
                                                    self._order_mode, self._gap, self._budget,
                                                    deadlines, build_audit)
                    if _expired(deadlines) or _code_identity() != self._code:
                        raise ValueError('expired/changed order construction; cache not installed')
                    self._order, self._order_audit = order, deepcopy(build_audit)
                else:
                    build_audit = {'status': 'SHARED_ORDER_CACHE_HIT',
                                   'contract_sha256': self._order.sha256,
                                   'operations': {'phase_cells': 0}}
                phase_cells = build_audit['operations']['phase_cells']
            with costs.measure('earliest_times_and_declared_order_validation'):
                if starts is None:
                    starts = self._order.earliest(directions)
                order_check = self._order.validate(starts, directions)
                if not order_check['action_graph_acyclic']:
                    raise ValueError('CURRENT_ACTION_GRAPH_CYCLE_OUTSIDE_ADAPTER; '
                                     'not a claim of temporal or all-arrangement infeasibility')
            with costs.measure('compile_complete_schedule'):
                if _expired(deadlines):
                    raise ValueError('time budget exhausted before schedule compilation')
                candidate = compile_schedule(self._specs, starts, self._world,
                                             obstacles=self._obstacles, horizon=self._budget.horizon)
            with costs.measure('final_complete_continuous_validation'):
                if _expired(deadlines):
                    raise ValueError('time budget exhausted before validation')
                remaining = self._budget.max_cells-phase_cells
                if remaining <= 0:
                    raise ValueError('total phase/time cell budget exhausted before final validation')
                validation = certify_schedule(candidate, replace(self._budget, max_cells=remaining),
                                              deadlines=deadlines)
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
                                  declared_orders=order_check, order_construction=self._order_audit,
                                  problem_admissibility='DECLARED_PRESTART_ORDERS_AND_CONDITIONAL_GEOMETRY',
                                  group_completeness='CALLER_DECLARED_NOT_SADG_MAXIMAL_GROUP_REPRODUCTION')
                    # Exact decimal/rational strings and independent owned data.
                    record = json.loads(json.dumps(record, default=str, sort_keys=True))
                    record['schedule_sha256'] = _digest(record)
                    if _expired(deadlines):
                        raise ValueError('time budget exhausted; candidate not installed')
                    self._incumbent, accepted = record, True
        except Exception as exc:
            reason = type(exc).__name__+': '+str(exc)
        report = {'accepted': accepted, 'reason': reason, 'validation': validation,
                  'declared_orders': order_check, 'order_build_or_cache': build_audit,
                  'proposal_sha256': proposal_sha, 'attempt_index': len(self._attempts),
                  'status': 'NEW_CONDITIONAL_PRESTART_INCUMBENT' if accepted else
                  'NO_CERTIFIED_INCUMBENT' if self._incumbent is None else 'RETAINED_INCUMBENT',
                  'candidate_sum_completion': None if candidate is None else str(candidate['sum_completion']),
                  'incumbent_sha256': None if self._incumbent is None else self._incumbent['schedule_sha256'],
                  'problem_admissibility': 'DECLARED_PRESTART_ORDERS_AND_CONDITIONAL_GEOMETRY' if accepted
                  else 'NO_NEW_ADMISSIBLE_CANDIDATE',
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
                               problem_admissibility='NO_NEW_ADMISSIBLE_CANDIDATE',
                               incumbent_sha256=None if previous is None else previous['schedule_sha256'])
        stored['costs'] = costs.finish()
        result['costs'] = deepcopy(stored['costs'])
        return result
