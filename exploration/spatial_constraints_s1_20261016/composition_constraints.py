"""C1 exploration: continuous occupancy compilation and same-information gate.

The compiler below is project code, NOT the original SADG compiler. Its output
is offered identically to the guard and to unmodified SADG event primitives.
No author optimizer/world execution, switching, or completeness claim.
"""
from fractions import Fraction as Q
from copy import deepcopy
import hashlib
import json

from composition import Chain, CONDITION, H, RESERVE, DIRECTIONS, contract
from interface import Box, sweep, conflicts, add_conflicts


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def occupancy(chain, action, *, start=None):
    start = action.start if start is None else start
    ex, ey = chain.error_box(start, action.end)
    if action.kind == 'TURN':
        # .32^2 > .3^2+.1^2: contains ALL intermediate headings and errors.
        hx = hy = Q('.32')
    elif action.heading % 2 == 0:
        hx, hy = Q('.3')+Q('.1')*H, Q('.1')+Q('.3')*H
    else:
        hx, hy = Q('.1')+Q('.3')*H, Q('.3')+Q('.1')*H
    return sweep(start, action.end, (hx+ex+RESERVE, hy+ey+RESERVE))


def initial_wait(chain):
    from composition import Primitive
    return occupancy(chain, Primitive('WAIT', chain.origin, chain.origin,
                                     chain.heading, chain.heading, Q(0)))


def compile_case(fixture):
    """Frozen C1 two-robot A-before-B policy. Reject unsupported arrangements.

    'order_edges' express passage order, NOT unconditional END-to-START lags.
    Every spatial edge has a CLEAR event. C1 conservatively gates all of B's
    launch on a full-A-suffix / full-B-corridor certificate covering those events.
    Overlaps involving start wait or permanent goal are reported, never hidden
    by inventing a finite completion event for indefinite occupancy.
    """
    if (fixture['condition'] != CONDITION or fixture['units'] != 'metre_second_radian'
            or fixture['rank_rule'] != 'robot_priority_then_action_index'
            or fixture['robot_priority'] != ['A', 'B'] or set(fixture['robots']) != {'A', 'B'}):
        raise ValueError('unsupported problem contract')
    chains = {r: Chain.build(spec) for r, spec in fixture['robots'].items()}
    entries, finite, ranks, chain_edges = [], {}, {}, []
    for r, chain in chains.items():
        entries.append((r+'_START_WAIT', r, initial_wait(chain)))
        previous = None
        for i, a in enumerate(chain.primitives):
            name = f'{r}_{i}'
            entries.append((name, r, occupancy(chain, a)))
            if a.kind != 'HOLD':
                finite[name], ranks[name] = a, (fixture['robot_priority'].index(r), i)
                if previous is not None:
                    chain_edges.append((previous, name))
                previous = name
    box_by_name = {n: b for n, _, b in entries}
    pairs = conflicts(entries)
    finite_pairs = [(a, b) for a, b in pairs if a in finite and b in finite]
    special = [(a, b) for a, b in pairs if a not in finite or b not in finite]
    existing = chain_edges+[tuple(e) for e in fixture['existing_passage_order']]
    graph = add_conflicts(finite, existing, finite_pairs, ranks)
    xmin, xmax, ymin, ymax = map(Q, fixture['world_bounds'])
    outside = [n for n, _, b in entries if b.xmin < xmin or b.xmax > xmax or b.ymin < ymin or b.ymax > ymax]
    reasons = []
    if special:
        reasons.append('CURRENT_POLICY_START_WAIT_OR_PERMANENT_GOAL_CONFLICT')
    if outside:
        reasons.append('OCCUPANCY_OUTSIDE_WORLD')
    if not graph['feasible']:
        reasons.append('CURRENT_ARRANGEMENT_CYCLE')
    if any(a.startswith('B_') and b.startswith('A_') for a, b in graph['edges']):
        reasons.append('CURRENT_A_BEFORE_B_GATE_UNSUPPORTED')
    # Exact point equality is only a diagnostic of the raw compiler's abstraction;
    # this is NOT an execution of compile_sadg on off-grid continuous paths.
    shared_points = set([chains['A'].origin]+[a.end for a in chains['A'].primitives]) & set(
        [chains['B'].origin]+[a.end for a in chains['B'].primitives])
    return {'chains': chains, 'finite': finite, 'boxes': box_by_name,
            'pairs': pairs, 'finite_pairs': finite_pairs, 'special_pairs': special,
            'existing': existing, 'graph': graph, 'outside': outside,
            'feasible': not reasons, 'reasons': reasons,
            'shared_waypoints': sorted(shared_points),
            'commitment': digest({'fixture': fixture, 'source': contract()}),
            'fixture': fixture}


class SuffixGate:
    """Reuse legal transport; consume BOTH coordinates only after Inbox admission.

    This fixed C1 adapter accepts progress only from A's last northbound MOVE.
    Earlier turns are complete according to the trusted local action binding.
    Remaining turns/returns are INCLUDED in the suffix. Ordinary END is rejected.
    The old .03 tracking field is accepted only after verifying that it bounds
    this action's northward reference projection in the NEW source condition.
    """
    def __init__(self, compiled, protocol, *, action_index=2):
        if not compiled['feasible']:
            raise ValueError('current arrangement not qualified')
        self.compiled, self.index = deepcopy(compiled), action_index
        chain = compiled['chains']['A']
        a = chain.primitives[action_index]
        if a.kind != 'MOVE' or a.heading != 1:
            raise ValueError('C1 northbound progress interface only')
        if chain.error_box(a.start, a.end)[1]+RESERVE > Q('.03'):
            raise ValueError('legacy wire bound insufficient for this projected action')
        self.binding = protocol.Binding(compiled['fixture']['task'], 'A', f'A_{action_index}',
                                        CONDITION, compiled['commitment'])
        self.inbox = protocol.Inbox(self.binding)

    def receive(self, packet, *, now):
        if digest({'fixture': self.compiled['fixture'], 'source': contract()}) != self.compiled['commitment']:
            raise ValueError('source or complete suffix contract changed')
        self.inbox.admit(packet, now=now)
        if packet.kind != 'PROGRESS_BOUND':
            return {'accepted': False, 'reason': 'END_ALONE_IS_NOT_CLEAR'}
        chain = self.compiled['chains']['A']
        a = chain.primitives[self.index]
        # Use public observed y. Reference/true position is not available here.
        lower = Q(packet.observed_y)-Q(packet.localization_bound)-Q(packet.tracking_bound)
        upper = Q(packet.observed_y)+Q(packet.localization_bound)+Q(packet.tracking_bound)
        if lower > a.end[1] or upper < a.start[1]:
            return {'accepted': False, 'reason': 'OBSERVATION_OUTSIDE_BOUND_ACTION'}
        lower = max(a.start[1], lower)
        remainder = [occupancy(chain, a, start=(a.start[0], lower))]
        remainder += [occupancy(chain, p) for p in chain.primitives[self.index+1:]]
        # Includes B WAIT, accelerations, turns, braking, arbitrary stopped waits,
        # terminal hold, and A's complete future including any re-entry.
        other = [b for n, b in self.compiled['boxes'].items() if n.startswith('B_')]
        accepted = all(x.separated(y) for x in remainder for y in other)
        return {'accepted': accepted, 'reason': 'FULL_SUFFIX_SEPARATED' if accepted else 'FUTURE_OCCUPANCY_OVERLAP',
                'progress_lower': str(lower), 'commitment': self.compiled['commitment'],
                'coverage': 'ALL_ALLOWED_SUFFIX_AND_PERMANENT_HOLD' if accepted else None}


class AuthorCompiledGate:
    """AGPL-3.0-or-later project adaptation using verified author event classes.

    Shared compiler/geometry/feedback/certificate are the same as SuffixGate.
    No authorship claim for these spatial events; no optimizer invocation.
    """
    def __init__(self, compiled, author):
        if not compiled['feasible']:
            raise ValueError('cannot dispatch an unqualified arrangement')
        self.compiled = deepcopy(compiled)
        self.Status = author['sadg.status'].Status
        Vertex = author['sadg.vertex'].Vertex
        PlanTuple = author['mapf.plan_tuple'].PlanTuple
        Dependency = author['sadg.dependency'].Dependency
        self.nodes = {}
        for name, a in compiled['finite'].items():
            # Spatial coordinates are adapter metadata; author fixed 2 m/s
            # expected-time calculation is NOT used as our dynamics or duration.
            self.nodes[name] = Vertex(name, [PlanTuple(float(a.start[0]), float(a.start[1]), 0),
                                             PlanTuple(float(a.end[0]), float(a.end[1]), 0)], 0)
        for chain in ('A', 'B'):
            names = [n for n in self.nodes if n.startswith(chain+'_')]
            for u, v in zip(names, names[1:]):
                self.nodes[v].add_dependency(Dependency(self.nodes[u], self.nodes[v]))
        self.events = []
        for i, (a, b) in enumerate(compiled['graph']['new_or_retained']):
            if not (a.startswith('A_') and b.startswith('B_')):
                raise ValueError('current shared gate preserves A-before-B only')
            event = Vertex(f'CLEAR_{a}_{b}', PlanTuple(0, 0, 0), i)
            self.events.append(event)
            self.nodes[b].add_dependency(Dependency(event, self.nodes[b]))
            # Conservative common launch policy is explicit, not baseline handicap.
            if b != 'B_0':
                self.nodes['B_0'].add_dependency(Dependency(event, self.nodes['B_0']))
        # Preserve preexisting cross-robot passage constraints even if geometry
        # happens not to flag them in another diagnostic fixture.
        for u, v in compiled['existing']:
            if u[0] != v[0]:
                self.nodes[v].add_dependency(Dependency(self.nodes[u], self.nodes[v]))

    def bind_local_action(self, index):
        # The same trusted local progress binding used by the guard confirms
        # prior stopped actions ended. No ETA or true-state input is used.
        for name, vertex in self.nodes.items():
            if name.startswith('A_'):
                i = int(name.split('_')[1])
                vertex.set_status(self.Status.COMPLETED if i < index else
                                  self.Status.IN_PROGRESS if i == index else self.Status.STAGED)

    def apply(self, certificate):
        if (certificate.get('accepted') is True
                and certificate.get('commitment') == self.compiled['commitment']
                and certificate.get('coverage') == 'ALL_ALLOWED_SUFFIX_AND_PERMANENT_HOLD'):
            for event in self.events:
                event.set_status(self.Status.COMPLETED)
        return self.nodes['B_0'].can_execute()
