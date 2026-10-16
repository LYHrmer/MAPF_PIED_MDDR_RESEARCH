"""Physical-time certificates shared by both engines; no collision from overlap.

Continuous interval subdivision yields SEPARATED or UNRESOLVED. Each interval
box encloses the shared-parameter trajectory family. Refinement never redraws
initial error, and never converts sample clearance into a continuous proof.
"""
from copy import deepcopy
from fractions import Fraction as Q
from itertools import combinations

from composition import Chain, contract
from composition_constraints import compile_case, digest
from interface import Box, conflicts, add_conflicts, temporal_feasible
from timed import Trajectory, Anchor, PHASE_ERROR


class CertificateBudget(ValueError):
    pass


def make_problem(base, config, size):
    if (Q(config['phase_half_width']) != PHASE_ERROR or Q(config['dispatch_delay']) != 0
            or config['controller_commitment'] != 'synchronous_actual_inputs_nonpreemptive_chain_to_goal'
            or Q(config['feedback_delay']) < 0 or Q(config['feedback_ttl']) <= 0
            or Q(config['periodic_capture_interval']) <= 0):
        raise ValueError('unqualified clock/controller/feedback contract')
    if size not in (2, 3) or size not in config['sizes']:
        raise ValueError('only predeclared two/three-robot tasks')
    # Preserve all original C1 qualification, including starts, goals and order.
    old = compile_case(base)
    if not old['feasible']:
        raise ValueError('C1 source arrangement not qualified')
    specs = deepcopy(base['robots'])
    if size == 3:
        specs['C'] = deepcopy(config['third_robot'])
    trajectories = {r: Trajectory(r, Chain.build(s)) for r, s in specs.items()}
    entries, finite, ranks, existing, intervals = [], {}, {}, [], {}
    for rank, (r, tr) in enumerate(trajectories.items()):
        entries.append((r+'_START_WAIT', r, Box(*tr.box(Q(0), Q(0)))))
        previous = None
        for i, (a, begin) in enumerate(zip(tr.chain.primitives, tr.offsets)):
            end = begin+(a.duration or 0)
            name = f'{r}_{i}'
            entries.append((name, r, Box(*tr.action_box(i, begin, end))))
            if a.kind != 'HOLD':
                finite[name], ranks[name], intervals[name] = (r, i), (rank, i), (begin, end)
                if previous is not None:
                    existing.append((previous, name))
                previous = name
    existing += [tuple(e) for e in base['existing_passage_order']]
    pairs = conflicts(entries)
    special = [(u, v) for u, v in pairs if u not in finite or v not in finite]
    graph = add_conflicts(finite, existing, [(u, v) for u, v in pairs if u in finite and v in finite], ranks)
    bounds = tuple(map(Q, base['world_bounds']))
    outside = [n for n, _, b in entries if b.xmin < bounds[0] or b.xmax > bounds[1] or b.ymin < bounds[2] or b.ymax > bounds[3]]
    if special or outside or not graph['feasible']:
        raise ValueError('CURRENT_ARRANGEMENT_UNQUALIFIED: '+str((special, outside, graph['feasible'])))
    return {'trajectories': trajectories, 'boxes': {n: b for n, _, b in entries},
            'finite': finite, 'intervals': intervals, 'graph': graph,
            'existing_cross': [tuple(e) for e in base['existing_passage_order']],
            'task': config['task']+'_'+str(size), 'config': deepcopy(config),
            'commitment': digest({'specs': specs, 'source': contract(), 'config': config,
                                   'geometry': 'joint_rotation_time_interval_outer_v1', 'old_order': base['existing_passage_order']})}


class Certificates:
    def __init__(self, problem):
        self.problem = problem
        self.resolution = Q(problem['config']['phase_resolution'])
        self.limit = problem['config']['certificate_max_cells']
        if self.resolution <= 0 or type(self.limit) is not int or self.limit <= 0:
            raise ValueError('positive frozen interval budget required')
        self.cache = {}
        self.operations = {'phase_cells': 0, 'time_cells': 0, 'phase_cache_hits': 0, 'time_checks': 0}
        self.constraints = []
        for tail, head in problem['graph']['new_or_retained']:
            a, b = problem['boxes'][tail], problem['boxes'][head]
            region = Box(max(a.xmin, b.xmin), min(a.xmax, b.xmax), max(a.ymin, b.ymin), min(a.ymax, b.ymax))
            ta, tb = self.visits(tail, region), self.visits(head, region)
            if ta is not None and tb is not None:
                self.constraints.append({'tail': tail, 'head': head, 'exit': ta[1], 'entry': tb[0], 'kind': 'SPATIAL_PASSAGE'})
        # Stronger END-to-START interpretation of old explicit relations is
        # preserved; new geometry never erases an existing precedence.
        for tail, head in problem['existing_cross']:
            self.constraints.append({'tail': tail, 'head': head,
                                     'exit': problem['intervals'][tail][1],
                                     'entry': problem['intervals'][head][0], 'kind': 'EXISTING_ORDER'})

    def visits(self, name, region):
        key = (name, region)
        # Box in frozen interface is hashable (frozen dataclass).
        if key in self.cache:
            self.operations['phase_cache_hits'] += 1
            return self.cache[key]
        robot, index = self.problem['finite'][name]
        tr = self.problem['trajectories'][robot]
        begin, end = self.problem['intervals'][name]
        pending, possible, count = [(begin, end)], [], 0
        while pending:
            lo, hi = pending.pop()
            count += 1; self.operations['phase_cells'] += 1
            if count > self.limit:
                raise CertificateBudget('phase interval budget; no collision conclusion')
            if Box(*tr.action_box(index, lo, hi)).separated(region):
                continue
            if hi-lo <= self.resolution:
                possible.append((lo, hi))
            else:
                middle = (lo+hi)/2
                pending += [(lo, middle), (middle, hi)]
        result = None if not possible else (min(p[0] for p in possible), max(p[1] for p in possible))
        self.cache[key] = result
        return result

    def pair(self, ra, aa, rb, ab, *, now):
        """Check all common physical times through both terminal holds."""
        now = Q(now)
        finishes = [a.finish_upper() for a in (aa, ab)]
        finish = max([now]+[t for t in finishes if t is not None])
        pending, unresolved, count = [(now, finish)], [], 0
        self.operations['time_checks'] += 1
        while pending:
            lo, hi = pending.pop()
            count += 1; self.operations['time_cells'] += 1
            if count > self.limit:
                return {'status': 'UNRESOLVED', 'reason': 'INTERVAL_BUDGET', 'cells': count}
            ba = Box(*self.problem['trajectories'][ra].box(*aa.phases(lo, hi)))
            bb = Box(*self.problem['trajectories'][rb].box(*ab.phases(lo, hi)))
            if ba.separated(bb):
                continue
            if hi-lo <= self.resolution:
                unresolved.append([str(lo), str(hi)])
            else:
                mid = (lo+hi)/2
                pending += [(lo, mid), (mid, hi)]
        # At finish, moving agents are in permanent HOLD; stationary initial
        # waits remain unchanged. Thus the last checked slice covers all later t.
        return {'status': 'UNRESOLVED' if unresolved else 'CERTIFIED_SEPARATED',
                'unresolved_physical_intervals': unresolved, 'cells': count,
                'tail': 'PERMANENT_HOLDS_OR_UNDISPATCHED_ZERO_INPUT_WAITS'}

    def launch(self, robot, anchors, launched, *, now, deadline=None):
        now = Q(now)
        if robot in launched or set(anchors) != set(self.problem['trajectories']):
            raise ValueError('fresh feedback from every robot required; no relaunch')
        if anchors[robot].moving or anchors[robot].low != 0 or anchors[robot].high != 0:
            raise ValueError('launch requires confirmed initial stopped state')
        duration = self.problem['trajectories'][robot].chain.duration
        candidate = {**anchors, robot: Anchor(now, Q(0), Q(0), True, duration)}
        temporal = [('zero', 'launch', now), ('launch', 'zero', -now)]
        nodes = ['zero', 'launch']
        # Every scheduled acceleration and braking interval keeps its original
        # duration. Whole stopped primitives are immutable after this reservation.
        for i, (offset, a) in enumerate(zip(self.problem['trajectories'][robot].offsets,
                                           self.problem['trajectories'][robot].chain.primitives)):
            name = 'action_'+str(i)
            nodes.append(name)
            temporal += [('launch', name, offset), (name, 'launch', -offset)]
        if deadline is not None:
            temporal.append(('action_'+str(len(nodes)-3), 'zero', -Q(deadline)))
        records = []
        for edge in self.constraints:
            tail, head = edge['tail'].split('_')[0], edge['head'].split('_')[0]
            if head != robot and tail != robot:
                continue  # previously authorized immutable reservations stay valid
            if head == robot:
                if tail not in launched:
                    return {'accepted': False, 'reason': 'PREDECESSOR_NOT_COMMITTED'}
                anchor = candidate[tail]
                latest = anchor.capture if not anchor.moving else anchor.capture+edge['exit']-anchor.low
                lower = latest-edge['entry']+Q('.000001')
                temporal.append(('zero', 'launch', lower))
                records.append({**edge, 'required_launch_lower': lower})
            elif head in launched:
                # Earlier robot cannot be inserted into an already granted later
                # batch under this first implementation. No implicit reordering.
                return {'accepted': False, 'reason': 'ALREADY_COMMITTED_SUCCESSOR'}
        if not temporal_feasible(nodes, temporal):
            return {'accepted': False, 'reason': 'CANDIDATE_TIME_WINDOW_INFEASIBLE', 'orders': records}
        pairs = {}
        for ra, rb in combinations(candidate, 2):
            pairs[ra+'_'+rb] = self.pair(ra, candidate[ra], rb, candidate[rb], now=now)
        valid = all(v['status'] == 'CERTIFIED_SEPARATED' for v in pairs.values())
        return {'accepted': valid, 'reason': 'TIME_AND_OCCUPANCY_CERTIFIED' if valid else 'CONTINUOUS_SEPARATION_UNRESOLVED',
                'pairs': pairs, 'orders': records, 'time_feasible': True,
                'commitment': self.problem['commitment'], 'launch': str(now),
                'coverage': 'SHARED_TASK_PARAMETERS_ALL_PHYSICAL_TIMES_THROUGH_PERMANENT_HOLDS',
                'collision_inferred_from_overlap': False}
