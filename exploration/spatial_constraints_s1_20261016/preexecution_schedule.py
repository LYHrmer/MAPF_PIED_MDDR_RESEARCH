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
import preexecution_input
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
    modules = (composition, interface, protocol, preexecution_order, preexecution_input,
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


@dataclass(frozen=True)
class LocalGroupCatalog:
    """Owned, immutable DEV contact-token abstraction, not SADG maximal groups."""
    specs_sha256: str
    payload_json: str
    code_json: str

    @property
    def payload(self):
        return json.loads(self.payload_json)

    @property
    def sha256(self):
        return _digest((self.specs_sha256, self.payload_json, self.code_json))

    def validate_for(self, specs):
        if self.specs_sha256 != _digest(specs) or json.loads(self.code_json) != _code_identity():
            raise ValueError('group catalog input/source changed; rebuild required')


def _intersection(a, b):
    if a.separated(b):
        return None
    return Box(max(a.xmin, b.xmin), min(a.xmax, b.xmax),
               max(a.ymin, b.ymin), min(a.ymax, b.ymax))


def _project_token_order(tail, head, sizes):
    """Project token exit-before-entry onto original finite start variables.

    D_k spans END(k-1)..START(k), D_0 begins at zero, D_N ends at infinity.
    None means this direction cannot be represented by this sufficient ordering.
    Numerical lags are compiled separately with the common visits kernel.
    """
    ra, ka, ia = tail
    rb, kb, ib = head
    if (ka == 'D' and ia == sizes[ra]) or (kb == 'D' and ib == 0):
        return None
    return (ra, ia), (rb, ib if kb == 'A' else ib-1)


def build_local_groups(task, *, max_pair_checks, max_link_checks, deadlines):
    """R16 DEV: local components in complete action/dwell contact-token space.

    Dwell tokens include EVERY stopped boundary, initial wait and permanent goal.
    Links require consecutive original phase domains and a possible common
    boundary contact, not merely aliased schedule variables. Outer overlap only
    constructs a conservative candidate abstraction, never a collision verdict.
    Conflicting old directions reject this abstraction, not the physical task.
    Calling this geometry constructor is deferred to a separately authorized run.
    """
    if any(type(n) is not int or n < 1 for n in (max_pair_checks, max_link_checks)):
        raise ValueError('explicit positive group construction limits required')
    if not isinstance(deadlines, (tuple, list)) or len(deadlines) != 2:
        raise ValueError('absolute wall/CPU construction deadlines required')
    deadlines = _cap_deadlines(deadlines, deadlines)
    code = _code_identity()
    task = deepcopy(task)
    specs, traces, paths = task['specs'], task['action_trace'], task['grid_paths']
    if (not 2 <= len(specs) <= 3 or set(traces) != set(specs) or set(paths) != set(specs)
            or task['source']['data_class'] != 'R16_DERIVED_DEV_NOT_INDEPENDENT_TEST'
            or task['source']['specs_sha256'] != _digest(specs)
            or task['source']['visit_mapping_sha256'] != _digest(
                {'grid_paths': paths, 'action_trace': traces})):
        raise ValueError('complete hash-bound R16 DEV adaptation required')
    trajectories = {r: Trajectory(r, Chain.build(s)) for r, s in specs.items()}
    tokens, sizes = {}, {}
    stats = {'pair_checks': 0, 'boundary_link_checks': 0, 'potential_token_pairs': 0}

    def budget():
        if _expired(deadlines):
            raise ValueError('group construction deadline; no task infeasibility conclusion')

    for r, tr in trajectories.items():
        budget()
        finite = len(tr.chain.primitives)-1
        sizes[r] = finite
        if finite < 1 or len(traces[r]) != finite+1:
            raise ValueError('nonempty complete finite chain and HOLD trace required')
        rows = paths[r]
        if any(type(row[k]) is not int or row['t'] != j
               for j, row in enumerate(rows) for k in ('x', 'y', 't')):
            raise ValueError('original integer visit order required')
        visit_cursor = 0
        for i, (a, trace) in enumerate(zip(tr.chain.primitives, traces[r])):
            budget()
            u, v = trace['source_visit_index'], trace['source_visit_end_index']
            if (type(u) is not int or type(v) is not int or not 0 <= u <= v < len(rows)
                    or u != visit_cursor
                    or trace['primitive_index'] != i or trace['kind'] != a.kind
                    or tuple(trace['start_vertex']) != a.start or tuple(trace['end_vertex']) != a.end
                    or (rows[u]['x'], rows[u]['y']) != a.start
                    or (rows[v]['x'], rows[v]['y']) != a.end
                    or trace['source_time'] != rows[u]['t']
                    or trace['source_time_end'] != rows[v]['t']):
                raise ValueError('primitive/visit provenance mismatch')
            if a.kind == 'MOVE' and (v != u+1 or sum(abs(a.end[j]-a.start[j]) for j in (0, 1)) != 1):
                raise ValueError('this local grouping is qualified only for unit grid MOVEs')
            if a.kind != 'MOVE' and u != v:
                raise ValueError('stationary primitive changed discrete visit')
            visit_cursor = v
            if i == finite:
                if a.kind != 'HOLD' or v != len(rows)-1:
                    raise ValueError('complete permanent goal trace required')
                continue
            begin, end = tr.offsets[i], tr.offsets[i]+a.duration
            tokens[(r, 'A', i)] = {'slot': 2*i+1, 'phase': (begin, end),
                                   'visits': {a.start: rows[u]['t'], a.end: rows[v]['t']},
                                   'box': Box(*tr.action_box(i, begin, end))}
        for k in range(finite+1):
            t = tr.offsets[k]
            trace, a = traces[r][k], tr.chain.primitives[k]
            tokens[(r, 'D', k)] = {'slot': 2*k, 'phase': (t, t),
                                   'visits': {a.start: trace['source_time']},
                                   'box': Box(*tr.box(t, t))}

    groups, fixed_members, component_records = [], [], []
    for ra, rb in combinations(sorted(specs), 2):
        cells = {}
        for a, ta in tokens.items():
            if a[0] != ra:
                continue
            for b, tb in tokens.items():
                if b[0] != rb:
                    continue
                budget()
                stats['pair_checks'] += 1
                if stats['pair_checks'] > max_pair_checks:
                    raise ValueError('group pair-check limit; construction unresolved')
                region = _intersection(ta['box'], tb['box'])
                if region is None:
                    continue
                vertices = set(ta['visits']) & set(tb['visits'])
                if not vertices:
                    raise ValueError('CURRENT_TOKEN_ABSTRACTION_UNSUPPORTED_NONVERTEX_CONTACT')
                orders = {1 if ta['visits'][p] < tb['visits'][p] else -1
                          if ta['visits'][p] > tb['visits'][p] else 0 for p in vertices}
                if len(orders) != 1 or 0 in orders:
                    raise ValueError('CURRENT_TOKEN_ABSTRACTION_UNSUPPORTED_MIXED_OR_TIED_SOURCE_ORDER')
                cells[(ta['slot'], tb['slot'])] = (a, b, region, next(iter(orders)))
        stats['potential_token_pairs'] += len(cells)
        parent = {c: c for c in cells}

        def root(c):
            while parent[c] != c:
                c = parent[c]
            return c

        def boundary_box(x, y):
            tx, ty = tokens[x], tokens[y]
            lo = max(tx['phase'][0], ty['phase'][0])
            hi = min(tx['phase'][1], ty['phase'][1])
            if lo > hi:
                return None
            tr = trajectories[x[0]]
            bx = tx['box'] if x[1] == 'D' else Box(*tr.action_box(x[2], lo, hi))
            by = ty['box'] if y[1] == 'D' else Box(*tr.action_box(y[2], lo, hi))
            return _intersection(bx, by)

        for c, (a, b, region, direction) in cells.items():
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    d = c[0]+di, c[1]+dj
                    if d not in cells or d <= c:
                        continue
                    budget()
                    stats['boundary_link_checks'] += 1
                    if stats['boundary_link_checks'] > max_link_checks:
                        raise ValueError('group boundary-link limit; construction unresolved')
                    aa, bb, _, _ = cells[d]
                    ba, bbb = boundary_box(a, aa), boundary_box(b, bb)
                    if ba is not None and bbb is not None and not ba.separated(bbb):
                        parent[root(d)] = root(c)
        components = {}
        for c in sorted(cells):
            components.setdefault(root(c), []).append(cells[c])
        for values in components.values():
            directions = {v[3] for v in values}
            if len(directions) != 1:
                raise ValueError('CURRENT_TOKEN_GROUP_ABSTRACTION_UNSUPPORTED_MIXED_OLD_ORDER')
            forward = tuple((v[0], v[1]) for v in values)
            reverse = tuple((b, a) for a, b in forward)
            possible = {label: all(_project_token_order(a, b, sizes) is not None for a, b in members)
                        for label, members in (('forward', forward), ('reverse', reverse))}
            initial = 'forward' if next(iter(directions)) == 1 else 'reverse'
            if not possible[initial]:
                raise ValueError('CURRENT_TOKEN_GROUP_ABSTRACTION_UNSUPPORTED_ENDPOINT_ORDER')
            name = 'component_'+_digest(forward)
            record = {'id': name, 'robots': (ra, rb), 'initial': initial,
                      'member_count': len(forward), 'directions_supported': possible,
                      'members': forward}
            component_records.append(record)
            if all(possible.values()):
                groups.append({'id': name, 'initial': initial,
                               'forward': forward, 'reverse': reverse})
            else:
                fixed_members.extend(forward if initial == 'forward' else reverse)
    budget()
    payload = {'groups': groups, 'fixed_members': fixed_members, 'sizes': sizes,
               'components': component_records, 'construction_operations': stats,
               'source': task['source'],
               'scope': 'CONSERVATIVE_COMMON_BOUNDARY_CONTACT_COMPONENTS_NOT_SADG_MAXIMAL_GROUPS',
               'complete_continuous_safety_checked': False, 'task_execution_performed': False,
               'dwell_scope': 'ALL_BOUNDARIES_INITIAL_WAIT_AND_PERMANENT_GOAL'}
    if _code_identity() != code:
        raise ValueError('source changed during group construction')
    catalog = LocalGroupCatalog(_digest(specs), json.dumps(payload, sort_keys=True, default=str),
                                json.dumps(code, sort_keys=True))
    budget()
    return catalog


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


def _compile_local_contract(specs, catalog, mode, gap, budget, deadlines, audit):
    """Action/dwell exit-entry clauses; never merge groups through time aliases."""
    catalog.validate_for(specs)
    payload = catalog.payload
    trajectories = {r: Trajectory(r, Chain.build(s)) for r, s in specs.items()}
    checker = _ActionWindowCertificates(trajectories, budget)
    sizes = {r: len(tr.chain.primitives)-1 for r, tr in trajectories.items()}
    if sizes != payload['sizes']:
        raise ValueError('catalog primitive counts changed')
    audit.update(status='BUILD_STARTED', mode=mode, catalog_sha256=catalog.sha256,
                 operations=checker.operations, clauses=[], complete_schedule_safety_checked=False)

    def token_box(token):
        r, kind, k = token
        tr = trajectories[r]
        if kind == 'D':
            return Box(*tr.box(tr.offsets[k], tr.offsets[k]))
        return Box(*tr.action_box(k, *checker.problem['intervals'][(r, k)]))

    def relative_window(token, region):
        r, kind, k = token
        if kind == 'D':
            return None, 'DWELL_VARIABLE_ENDPOINTS'
        begin, end = checker.problem['intervals'][(r, k)]
        if mode == 'END_TO_START':
            return (Q(0), end-begin), 'FULL_ACTION_INTERNAL_ABLATION'
        if _expired(deadlines):
            raise ValueError('time exhausted before token visit check')
        remaining = budget.max_cells-checker.operations['phase_cells']
        if ((r, k), region) not in checker.cache and remaining <= 0:
            raise ValueError('total cell budget exhausted in token visit check')
        checker.limit = max(0, remaining-1)
        result = checker.visits((r, k), region)
        if _expired(deadlines):
            raise ValueError('time exhausted after token visit check')
        if result is None:
            # Retain an explicit conservative order; do not silently discard a
            # member already used to define the source-order group abstraction.
            return (Q(0), end-begin), 'EMPTY_VISIT_FULL_ACTION_FALLBACK'
        return (result[0]-begin, result[1]-begin), 'ROBUST_VISIT_WINDOW'

    def compile_members(members, scope, group, direction):
        result = {}
        for tail, head in members:
            if _expired(deadlines):
                raise ValueError('time exhausted during token clause compilation')
            tail, head = tuple(tail), tuple(head)
            edge = _project_token_order(tail, head, sizes)
            if edge is None:
                raise ValueError('unsupported endpoint direction in catalog')
            region = _intersection(token_box(tail), token_box(head))
            if region is None:
                raise ValueError('catalog contact member no longer matches source')
            wa, kind_a = relative_window(tail, region)
            wb, kind_b = relative_window(head, region)
            exit_offset = Q(0) if tail[1] == 'D' else wa[1]
            entry_offset = (trajectories[head[0]].chain.primitives[head[2]-1].duration
                            if head[1] == 'D' else wb[0])
            lag = exit_offset-entry_offset+gap
            result[edge] = max(result[edge], lag) if edge in result else lag
            audit['clauses'].append({'scope': scope, 'group': group, 'direction': direction,
                                     'tail_token': tail, 'head_token': head, 'time_edge': edge,
                                     'start_lag': lag, 'tail_window': wa, 'head_window': wb,
                                     'window_kinds': (kind_a, kind_b),
                                     'region': (region.xmin, region.xmax, region.ymin, region.ymax)})
        return result

    fixed = compile_members(payload['fixed_members'], 'fixed', None, None)
    declarations, group_lags = [], {}
    for group in payload['groups']:
        name = group['id']
        forward = compile_members(group['forward'], 'group', name, 'forward')
        reverse = compile_members(group['reverse'], 'group', name, 'reverse')
        declarations.append({'id': name, 'initial': group['initial'], 'switchable': True,
                             'forward_edges': sorted(forward), 'reverse_edges': sorted(reverse)})
        group_lags[name] = {'forward': forward, 'reverse': reverse}
    declaration = {'schema': preexecution_order.SCHEMA, 'fixed_edges': sorted(fixed),
                   'groups': declarations}
    proof_sha = _digest({'catalog': catalog.sha256, 'mode': mode, 'gap': gap,
                         'resolution': budget.resolution, 'clauses': audit['clauses'],
                         'code': _code_identity()})
    result = OrderContract(specs, declaration, separation_gap=gap,
                           clause_lags={'fixed': fixed, 'groups': group_lags},
                           lag_provenance=proof_sha)
    audit.update(status='BUILT_ACTION_DWELL_WINDOW_CLAUSES', proof_sha256=proof_sha,
                 contract_sha256=result.sha256,
                 aggregation='MAX_WITHIN_SAME_ALTERNATIVE_ONLY_OTHER_GROUPS_REMAIN_INDEPENDENT',
                 dwell_scope=payload['dwell_scope'], group_scope=payload['scope'],
                 uncertainty_domain='FROZEN_V2_NO_POSTERIOR_SHRINKAGE')
    return result


def _compile_order_contract(specs, declaration, mode, gap, budget, deadlines, audit, catalog=None):
    """Build both alternatives once, charging failures and cached visits alike.

    Window lags are sufficient conditions for a declared finite action pair.
    They are not a complete schedule certificate. Original task offsets are
    subtracted, but original task origins/initial parameters are never reset.
    Separated declared pairs retain END semantics as an explicit conservative
    fallback; this compiler never silently removes a caller's required order.
    """
    if catalog is not None:
        return _compile_local_contract(specs, catalog, mode, gap, budget, deadlines, audit)
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
    dispatch authority. Manual declarations retain the legacy DAG restriction;
    trusted action/dwell catalogs use exact physical exit/entry times instead.
    """
    def __init__(self, specs, world_bounds, budget, *, obstacles,
                 separation_gap, order_declaration=None, local_groups=None,
                 order_mode='WINDOW_START_LAGS'):
        if type(budget) is not ValidationBudget:
            raise ValueError('explicit immutable validation budget required')
        self._specs, self._world = deepcopy(specs), tuple(world_bounds)
        if not isinstance(obstacles, (list, tuple)):
            raise ValueError('explicit obstacle list required; no implicit obstacle-free map')
        self._obstacles = deepcopy(obstacles)
        if order_mode not in ('WINDOW_START_LAGS', 'END_TO_START'):
            raise ValueError('explicit window or END comparison mode required')
        if (order_declaration is None) == (local_groups is None):
            raise ValueError('provide exactly one explicit declaration or local group catalog')
        if local_groups is not None:
            if type(local_groups) is not LocalGroupCatalog:
                raise ValueError('typed source-bound local group catalog required')
            local_groups.validate_for(specs)
        self._catalog = local_groups
        self._declaration, self._gap = deepcopy(order_declaration), exact(separation_gap)
        if self._gap <= 0:
            raise ValueError('strict positive separation gap required')
        self._order_mode, self._order, self._order_audit = order_mode, None, None
        self._budget, self._incumbent, self._attempts = budget, None, []
        self._identity = _digest({'specs': self._specs, 'world': self._world,
                                  'obstacles': self._obstacles,
                                  'order_declaration': self._declaration,
                                  'group_catalog': None if local_groups is None else local_groups.sha256,
                                  'order_mode': self._order_mode, 'separation_gap': self._gap,
                                  'source': contract(), 'budget': budget.__dict__})
        self._code = _code_identity()

    @property
    def incumbent(self):
        return deepcopy(self._incumbent)

    @property
    def attempts(self):
        return deepcopy(self._attempts)

    def consider(self, starts=None, *, directions=None, absolute_deadlines=None):
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
                                                    deadlines, build_audit, self._catalog)
                    if _expired(deadlines) or _code_identity() != self._code:
                        raise ValueError('expired/changed order construction; cache not installed')
                    self._order, self._order_audit = order, deepcopy(build_audit)
                else:
                    build_audit = {'status': 'SHARED_ORDER_CACHE_HIT',
                                   'contract_sha256': self._order.sha256,
                                   'operations': {'phase_cells': 0}}
                phase_cells = build_audit['operations']['phase_cells']
            with costs.measure('earliest_times_and_declared_order_validation'):
                if directions is None:
                    directions = self._order.initial_directions
                if starts is None:
                    starts = self._order.earliest(directions)
                order_check = self._order.validate(starts, directions)
                if self._catalog is not None:
                    self._catalog.validate_for(self._specs)
                    order_check['physical_event_order'] = 'PHYSICAL_EXIT_ENTRY_ORDERS_VERIFIED_BY_EXACT_TIMES'
                    order_check['group_catalog_sha256'] = self._catalog.sha256
                elif not order_check['action_graph_acyclic']:
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
                                  group_completeness='CALLER_DECLARED_NOT_SADG_MAXIMAL_GROUP_REPRODUCTION'
                                  if self._catalog is None else self._catalog.payload['scope'],
                                  group_catalog_sha256=None if self._catalog is None else self._catalog.sha256)
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
                  'execution_interface': 'SEPARATE_JOINT_SESSION_REQUIRED_NOT_EXECUTED_BY_CONSIDER',
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
