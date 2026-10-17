"""Declared atomic cross orders, before any action is committed.

Groups are supplied explicitly, not discovered maximal SADG groups. Earliest
times solve declared difference constraints; neither acyclicity nor this contract proves
continuous safety, obstacle clearance, joint dispatch, or delivered final END.
Import has no graph/optimizer/certificate execution or filesystem writes.
"""
from copy import deepcopy
from dataclasses import dataclass
from fractions import Fraction as Q
from pathlib import Path
import hashlib
import heapq
import json

import composition
from composition import Chain, contract, exact

SCHEMA = 'preexecution_atomic_end_start_v1'
PRE_START = 'PRE_START_NO_ACTION_COMMITTED'


def _canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), default=str, allow_nan=False)


def _sha(value):
    return hashlib.sha256(_canonical(value).encode()).hexdigest()


def _source_identity():
    return _sha({'source': contract(),
                 'composition_sha256': hashlib.sha256(Path(composition.__file__).read_bytes()).hexdigest(),
                 'order_code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest()})


@dataclass(frozen=True, init=False)
class OrderContract:
    """Immutable declaration and primitive durations; public results are copies.

    declaration = {'schema': SCHEMA, 'fixed_edges': [edge, ...], 'groups': [
        {'id': 'g0', 'forward_edges': [edge, ...], 'reverse_edges': [edge, ...],
         'initial': 'forward', 'switchable': True}, ...]}
    edge = ((robot, original_finite_primitive_index), (robot, index)).
    Both complete group alternatives must be explicit and nonempty. They may
    contain different endpoint pairs; completeness relative to geometry is not
    inferred. Fixed edges and different groups cannot own the same unordered
    endpoint pair, except in explicit clause_lags mode. There, different clauses
    may project to the same pair; only selected directions contribute weights.
    clause_lags = {'fixed': {edge: lag, ...}, 'groups': {
        'g0': {'forward': {edge: lag, ...}, 'reverse': {edge: lag, ...}}, ...}}
    Shared nodes are allowed; resulting cycles are checked.
    phase is a static precondition, not evidence from delivered execution feedback.
    """
    _durations: tuple
    _fixed: tuple
    _groups: tuple
    _gap: Q
    _source: str
    _specs_sha: str
    _sha: str
    _cross_lags: tuple
    _clause_lags: tuple
    _semantics: str
    _provenance: object

    def __init__(self, specs, declaration, *, separation_gap, phase=PRE_START,
                 cross_lags=None, lag_provenance=None, clause_lags=None):
        if phase != PRE_START:
            raise ValueError('only PRE_START_NO_ACTION_COMMITTED is supported')
        if cross_lags is not None and clause_lags is not None:
            raise ValueError('cross_lags and clause_lags are mutually exclusive')
        gap = exact(separation_gap)
        if gap <= 0:
            raise ValueError('positive exact END-to-START separation_gap required')
        specs, declaration = deepcopy(specs), deepcopy(declaration)
        if (not isinstance(specs, dict) or not 2 <= len(specs) <= 3
                or any(not isinstance(r, str) or not r for r in specs)):
            raise ValueError('complete named two/three-robot source specs required')
        durations = tuple((r, tuple(a.duration for a in Chain.build(specs[r]).primitives[:-1]))
                          for r in sorted(specs))
        lengths = {r: len(ds) for r, ds in durations}
        if (not isinstance(declaration, dict)
                or set(declaration) != {'schema', 'fixed_edges', 'groups'}
                or declaration['schema'] != SCHEMA
                or not isinstance(declaration['groups'], (list, tuple))):
            raise ValueError('explicit atomic order declaration schema required')

        def endpoint(value):
            if (not isinstance(value, (list, tuple)) or len(value) != 2
                    or not isinstance(value[0], str) or value[0] not in lengths
                    or type(value[1]) is not int or not 0 <= value[1] < lengths[value[0]]):
                raise ValueError('edge endpoint must name an original finite primitive')
            return tuple(value)

        def edges(values, *, nonempty=False):
            if not isinstance(values, (list, tuple)) or (nonempty and not values):
                raise ValueError('explicit complete edge list required')
            result, pairs = [], set()
            for item in values:
                if not isinstance(item, (list, tuple)) or len(item) != 2:
                    raise ValueError('two endpoints per edge required')
                edge = endpoint(item[0]), endpoint(item[1])
                if edge[0][0] == edge[1][0]:
                    raise ValueError('declared cross edges must connect different robots')
                key = edge if clause_lags is not None else frozenset(edge)
                if key in pairs:
                    raise ValueError('duplicate/conflicting endpoint pair in one alternative')
                pairs.add(key)
                result.append(edge)
            return tuple(sorted(result))

        fixed = edges(declaration['fixed_edges'])
        owners = {frozenset(e): ('fixed',) for e in fixed}
        groups, ids = [], set()
        for group in declaration['groups']:
            if (not isinstance(group, dict)
                    or set(group) != {'id', 'forward_edges', 'reverse_edges', 'initial', 'switchable'}
                    or not isinstance(group['id'], str) or not group['id'] or group['id'] in ids
                    or group['initial'] not in ('forward', 'reverse')
                    or type(group['switchable']) is not bool):
                raise ValueError('malformed/duplicate atomic group declaration')
            name = group['id']
            forward = edges(group['forward_edges'], nonempty=True)
            reverse = edges(group['reverse_edges'], nonempty=True)
            if set(forward) & set(reverse):
                raise ValueError('common directed edges belong in fixed_edges, not both alternatives')
            for edge in forward+reverse:
                key, owner = frozenset(edge), ('group', name)
                if clause_lags is None and key in owners and owners[key] != owner:
                    raise ValueError('edge pair has multiple fixed/group owners')
                owners[key] = owner
            ids.add(name)
            groups.append((name, forward, reverse, group['initial'], group['switchable']))
        all_cross = set(fixed)
        for _, forward, reverse, _, _ in groups:
            all_cross.update(forward+reverse)
        semantics, lags, clauses, provenance = 'END_TO_START', (), (), None
        if clause_lags is not None:
            if (not isinstance(clause_lags, dict) or set(clause_lags) != {'fixed', 'groups'}
                    or not isinstance(clause_lags['groups'], dict)
                    or set(clause_lags['groups']) != ids
                    or not isinstance(lag_provenance, str) or not lag_provenance.strip()):
                raise ValueError('all fixed/group clauses and nonempty provenance required')

            def weighted(values, declared):
                if not isinstance(values, dict):
                    raise ValueError('each clause alternative needs an explicit edge-to-lag map')
                result = {}
                for edge, value in values.items():
                    if not isinstance(edge, (list, tuple)) or len(edge) != 2:
                        raise ValueError('two endpoints per weighted clause required')
                    normalized = endpoint(edge[0]), endpoint(edge[1])
                    if normalized in result:
                        raise ValueError('duplicate normalized weighted clause')
                    result[normalized] = exact(value)
                if set(result) != set(declared):
                    raise ValueError('clause lags must cover all and only their declared edges')
                return tuple(sorted(result.items()))

            records = [('fixed', None, None, edge, lag)
                       for edge, lag in weighted(clause_lags['fixed'], fixed)]
            for name, forward, reverse, _, _ in sorted(groups):
                alternatives = clause_lags['groups'][name]
                if (not isinstance(alternatives, dict)
                        or set(alternatives) != {'forward', 'reverse'}):
                    raise ValueError('exactly forward/reverse clause alternatives required')
                for direction, declared in (('forward', forward), ('reverse', reverse)):
                    records.extend(('group', name, direction, edge, lag)
                                   for edge, lag in weighted(alternatives[direction], declared))
            clauses = tuple(records)
            semantics, provenance = 'WINDOW_CLAUSE_LAGS', lag_provenance
        elif cross_lags is None:
            if lag_provenance is not None:
                raise ValueError('lag provenance without explicit cross_lags or clause_lags')
        else:
            if (not isinstance(cross_lags, dict) or set(cross_lags) != all_cross
                    or not isinstance(lag_provenance, str) or not lag_provenance.strip()):
                raise ValueError('all and only declared cross edges need explicit lags and provenance')
            lags = tuple(sorted(((endpoint(edge[0]), endpoint(edge[1])), exact(value))
                                for edge, value in cross_lags.items()))
            semantics, provenance = 'WINDOW_START_LAGS', lag_provenance
        source, specs_sha = _source_identity(), _sha(specs)
        values = {'_durations': durations, '_fixed': fixed, '_groups': tuple(sorted(groups)),
                  '_gap': gap, '_source': source, '_specs_sha': specs_sha,
                  '_cross_lags': lags, '_clause_lags': clauses,
                  '_semantics': semantics, '_provenance': provenance,
                  '_sha': _sha({'schema': SCHEMA, 'specs_sha256': specs_sha,
                                'source_sha256': source, 'declaration': declaration,
                                'separation_gap': gap, 'phase': phase,
                                'cross_lags': lags, 'clause_lags': clauses,
                                'semantics': semantics, 'lag_provenance': provenance})}
        for name, value in values.items():
            object.__setattr__(self, name, value)

    @property
    def sha256(self):
        return self._sha

    @property
    def specs_sha256(self):
        return self._specs_sha

    @property
    def initial_directions(self):
        return {g[0]: g[3] for g in self._groups}

    @property
    def all_cross_edges(self):
        """All declared directed alternatives, independent of selected directions."""
        edges = set(self._fixed)
        for _, forward, reverse, _, _ in self._groups:
            edges.update(forward+reverse)
        return tuple(sorted(edges))

    @property
    def semantics(self):
        return self._semantics

    def _selected(self, directions):
        if _source_identity() != self._source:
            raise ValueError('source/order implementation changed; contract requires rebuilding')
        if not isinstance(directions, dict) or set(directions) != {g[0] for g in self._groups}:
            raise ValueError('every group, including locked groups, requires exactly one direction')
        result = list(self._fixed)
        for name, forward, reverse, initial, switchable in self._groups:
            choice = directions[name]
            if choice not in ('forward', 'reverse'):
                raise ValueError('unknown group direction')
            if not switchable and choice != initial:
                raise ValueError('locked group direction changed')
            result.extend(forward if choice == 'forward' else reverse)
        return tuple(result)

    def _active_clauses(self, directions):
        """Caller has validated directions through _selected; retain duplicates."""
        return tuple(clause for clause in self._clause_lags
                     if clause[0] == 'fixed' or directions[clause[1]] == clause[2])

    def _graph(self, directions):
        selected = self._selected(directions)
        duration = {(r, i): value for r, ds in self._durations for i, value in enumerate(ds)}
        edges = [((r, i), (r, i+1), ds[i])
                 for r, ds in self._durations for i in range(len(ds)-1)]
        if self._semantics == 'WINDOW_CLAUSE_LAGS':
            # Duplicated projected edges remain separate selected constraints.
            # A max across all directions here would activate unselected clauses.
            edges += [(edge[0], edge[1], lag)
                      for _, _, _, edge, lag in self._active_clauses(directions)]
        else:
            lags = dict(self._cross_lags)
            edges += [(a, b, lags[(a, b)] if self._semantics == 'WINDOW_START_LAGS'
                       else duration[a]+self._gap) for a, b in selected]
        return duration, tuple(edges), selected

    @staticmethod
    def _acyclic(duration, edges):
        degree, outgoing = dict.fromkeys(duration, 0), {n: [] for n in duration}
        for a, b, lag in edges:
            degree[b] += 1
            outgoing[a].append(b)
        ready = [n for n in duration if degree[n] == 0]
        heapq.heapify(ready)
        visited = 0
        while ready:
            a = heapq.heappop(ready)
            visited += 1
            for b in sorted(outgoing[a]):
                degree[b] -= 1
                if degree[b] == 0:
                    heapq.heappush(ready, b)
        return visited == len(duration)

    def earliest(self, directions):
        """Longest-path Bellman-Ford; negative/zero cycles need not be infeasible.

        Explicit raw window lags already contain the declared separation gap.
        Provenance is bound, not independently certified here: the caller must
        derive these lags from the common continuous source/geometry kernel.
        """
        duration, edges, _ = self._graph(directions)
        times = dict.fromkeys(duration, Q(0))
        for _ in range(len(duration)):
            changed = False
            for a, b, lag in edges:
                if times[b] < times[a]+lag:
                    times[b], changed = times[a]+lag, True
            if not changed:
                break
        else:
            if duration:
                raise ValueError('CURRENT_DIRECTION_POSITIVE_TIME_CYCLE: other assignments untested')
        return {r: [times[(r, i)] for i in range(len(ds))] for r, ds in self._durations}

    def validate(self, starts, directions):
        """Verify all original action orders and every selected/fixed cross edge.

        Success is time/order admissibility only, under the declared pre-start
        scope. It does not establish that this is the full map conflict graph.
        """
        duration, edges, selected = self._graph(directions)
        if not isinstance(starts, dict) or set(starts) != {r for r, _ in self._durations}:
            raise ValueError('complete start-time mapping required')
        times = {}
        for r, ds in self._durations:
            if not isinstance(starts[r], (list, tuple)) or len(starts[r]) != len(ds):
                raise ValueError('one exact start per original finite primitive required')
            for i, value in enumerate(starts[r]):
                start = exact(value)
                if start < 0:
                    raise ValueError('negative action start')
                times[(r, i)] = start
        for a, b, lag in edges:
            if times[b] < times[a]+lag:
                raise ValueError('declared cross-time/own-action order violated: '+repr((a, b)))
        result = {'valid': True, 'contract_sha256': self.sha256, 'specs_sha256': self.specs_sha256,
                  'directions': dict(directions), 'selected_edges': selected,
                  'semantics': self._semantics, 'separation_gap': str(self._gap),
                  'lag_provenance': self._provenance, 'window_provenance_certified_here': False,
                  'action_graph_acyclic': self._acyclic(duration, edges),
                  'phase': PRE_START, 'spatial_safety_checked': False,
                  'group_completeness': 'DECLARED_NOT_AUTOMATICALLY_INFERRED_FROM_GEOMETRY',
                  'dispatch_authorized': False, 'physical_END_received': False}
        if self._semantics == 'WINDOW_CLAUSE_LAGS':
            result['selected_clauses'] = tuple(
                {'scope': scope, 'group': name, 'direction': direction,
                 'tail': edge[0], 'head': edge[1], 'start_lag': lag,
                 'lag_provenance': self._provenance}
                for scope, name, direction, edge, lag in self._active_clauses(directions))
        return result
