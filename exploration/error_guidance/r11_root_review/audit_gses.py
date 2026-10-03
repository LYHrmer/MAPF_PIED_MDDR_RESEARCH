"""Independent graph/event/geometry audit; imports no candidate execution code."""
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import argparse
import copy
import gzip
import hashlib
import json
from exact_segments import audit as geometry_audit, self_check

ROOT = Path(__file__).resolve().parent
P = ROOT.parent / 'gses_primitive_20261003_r11'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def event_audit(data, author):
    g = data['graph']
    assert g == author['graph'], 'Changed author graph'
    paths, state = g['paths'], g['current'].copy()
    n = len(paths)
    ids = [(a, s) for a, path in enumerate(paths) for s in range(len(path))]
    deps = defaultdict(list)
    weights = {}
    for u, v, w in g['type1']:
        a, s = ids[u]
        assert ids[v] == (a, s + 1)
        weights[a, s] = F(w)
    for u, v, w in g['type2']:
        a, s = ids[u]
        b, t = ids[v]
        assert w == 1 and a != b and s >= 1 and paths[a][s - 1][0] == paths[b][t][0]
        deps[b, t].append((a, s))
    initial_delay = [weights.get((a, s), F(1)) - 1 for a, s in enumerate(state)]
    active, occupied, reservations, edges = {}, {}, {}, {}
    started, completed, turning, station = set(), {}, {}, {}
    moves = 0
    arrivals = defaultdict(list)
    segment_moves = defaultdict(dict)
    for s in data['segments']:
        kind, a = s['kind'], s['agent']
        p, z = tuple(map(F, s['p0'])), tuple(map(F, s['p1']))
        assert F(s['t1']) > F(s['t0'])
        if kind in ['MOVE_HALF1', 'MOVE_HALF2', 'MIDPOINT_PAUSE']:
            key = a, s['from_state'], s['to_state']
            assert kind not in segment_moves[key]
            segment_moves[key][kind] = s
        else:
            assert kind in ['INITIAL_HOLD', 'WAIT', 'TURN', 'STATION', 'GOAL_HOLD']
            assert p == z == tuple(map(F, paths[a][s['from_state']][0]))
            assert s['from_state'] == s['to_state']
            if kind == 'TURN':
                assert data['profile'] != 'author_unit' and F(s['t1']) - F(s['t0']) == F(1, 4)
                assert (s['yaw1'] - s['yaw0']) % 4 in [1, 3]
            if kind == 'STATION':
                assert data['profile'] != 'author_unit' and F(s['t1']) - F(s['t0']) == F(1, 2)
            if kind == 'INITIAL_HOLD':
                assert F(s['t0']) == 0 and F(s['t1']) == initial_delay[a]
    previous = F(0)
    for seq, e in enumerate(data['events']):
        assert e['seq'] == seq
        t, a, kind = F(e['t']), e['agent'], e['kind']
        assert 0 <= a < n and previous <= t <= F(data['makespan'])
        previous = t
        if kind == 'INITIAL':
            assert t == 0 and a not in started and e['state'] == state[a]
            cell = tuple(e['cell'])
            assert cell == tuple(paths[a][state[a]][0]) and cell not in reservations
            started.add(a); reservations[cell] = a; occupied[a] = {cell}
            if state[a] == len(paths[a]) - 1:
                completed[a] = F(0)
        elif kind == 'MOVE_START':
            assert a in started and a not in active and a not in turning and a not in station and a not in completed
            assert e['from_state'] == state[a] and e['to_state'] == state[a] + 1
            assert t >= initial_delay[a]
            origin, dest = tuple(e['origin']), tuple(e['destination'])
            assert origin == tuple(paths[a][state[a]][0]) and dest == tuple(paths[a][state[a] + 1][0])
            assert occupied[a] == {origin} and reservations[origin] == a
            required = deps[a, state[a] + 1]
            assert sorted(map(tuple, e['dependencies'])) == sorted(required)
            assert all(state[b] >= s for b, s in required), 'Uncompleted author dependency'
            duration = F(3, 2) if data['profile'] == 'axis_slow' and origin[1] != dest[1] else F(1)
            pause = F(3, 4) if data['profile'] == 'midpoint_pause' and (a + state[a]) % 11 == 0 else F(0)
            key = a, state[a], state[a] + 1
            parts = segment_moves.pop(key)
            assert set(parts) == ({'MOVE_HALF1', 'MOVE_HALF2', 'MIDPOINT_PAUSE'} if pause else {'MOVE_HALF1', 'MOVE_HALF2'})
            mid = tuple((F(x) + F(y)) / 2 for x, y in zip(origin, dest))
            for name, t0, t1, p0, p1 in [('MOVE_HALF1', t, t + duration / 2, origin, mid),
                                         ('MOVE_HALF2', t + duration / 2 + pause, t + duration + pause, mid, dest)]:
                s = parts[name]
                assert (F(s['t0']), F(s['t1']), tuple(map(F, s['p0'])), tuple(map(F, s['p1']))) == (t0, t1, tuple(map(F, p0)), tuple(map(F, p1)))
            if pause:
                s = parts['MIDPOINT_PAUSE']
                assert (F(s['t0']), F(s['t1'])) == (t + duration / 2, t + duration / 2 + pause)
                assert tuple(map(F, s['p0'])) == tuple(map(F, s['p1'])) == mid
            active[a] = {'s': state[a], 't': t, 'd': duration, 'pause': pause, 'origin': origin, 'dest': dest,
                         'entered': False, 'half': False, 'exited': False, 'released': False, 'edge_released': False}
            moves += 1
        elif kind == 'RESERVE_DESTINATION':
            m = active[a]; cell = tuple(e['cell'])
            assert t == m['t'] and cell == m['dest'] and cell not in reservations
            reservations[cell] = a
        elif kind == 'RESERVE_EDGE':
            m = active[a]; edge = tuple(sorted(map(tuple, e['edge'])))
            assert t == m['t'] and edge == tuple(sorted([m['origin'], m['dest']])) and edge not in edges
            edges[edge] = a
        elif kind == 'CELL_ENTER':
            m = active[a]; cell = tuple(e['cell'])
            assert t == m['t'] + m['d'] * F(2, 5) and cell == m['dest'] and e['state'] == state[a]
            assert reservations[cell] == a and cell not in occupied[a] and not m['entered']
            occupied[a].add(cell); m['entered'] = True
        elif kind in ['HALF_END', 'MIDPOINT_RESUME']:
            m = active[a]
            assert e['state'] == state[a] == m['s'] and e['to_state'] == state[a] + 1
            assert occupied[a] == {m['origin'], m['dest']}
            assert t == m['t'] + m['d'] / 2 + (m['pause'] if kind == 'MIDPOINT_RESUME' else 0)
            if kind == 'HALF_END':
                assert not m['half']; m['half'] = True
            else:
                assert m['pause'] > 0 and m['half']
        elif kind == 'CELL_EXIT':
            m = active[a]; cell = tuple(e['cell'])
            assert t == m['t'] + m['d'] * F(3, 5) + m['pause'], 'Source released before full disc exit'
            assert cell == m['origin'] and occupied[a] == {m['origin'], m['dest']} and m['half'] and not m['exited']
            occupied[a].remove(cell); m['exited'] = True
        elif kind == 'RELEASE_SOURCE':
            m = active[a]; cell = tuple(e['cell'])
            assert t == m['t'] + m['d'] * F(3, 5) + m['pause'] and m['exited'] and not m['released']
            assert cell == m['origin'] and reservations[cell] == a
            del reservations[cell]; m['released'] = True
        elif kind == 'RELEASE_EDGE':
            m = active[a]; edge = tuple(sorted(map(tuple, e['edge'])))
            assert t == m['t'] + m['d'] + m['pause'] and edges[edge] == a and not m['edge_released']
            del edges[edge]; m['edge_released'] = True
        elif kind == 'ARRIVE':
            m = active[a]
            assert t == m['t'] + m['d'] + m['pause'] and m['entered'] and m['half'] and m['released'] and m['edge_released']
            assert e['from_state'] == state[a] and e['to_state'] == state[a] + 1 and tuple(e['cell']) == m['dest']
            assert occupied[a] == {m['dest']} and reservations[m['dest']] == a
            state[a] += 1; arrivals[a].append((t, state[a])); del active[a]
        elif kind == 'TURN_START':
            assert a not in active and a not in station and a not in turning
            assert occupied[a] == {tuple(e['cell'])} and reservations[tuple(e['cell'])] == a
            turning[a] = t, e['quarters']
        elif kind == 'TURN_END':
            start, quarters = turning.pop(a)
            assert t - start == F(quarters, 4) and occupied[a] == {tuple(e['cell'])}
        elif kind == 'STATION_START':
            assert a not in active and a not in turning and a not in station and data['profile'] != 'author_unit'
            assert e['state'] == state[a] and occupied[a] == {tuple(e['cell'])} and reservations[tuple(e['cell'])] == a
            station[a] = t
        elif kind == 'STATION_END':
            assert t - station.pop(a) == F(1, 2) and occupied[a] == {tuple(e['cell'])}
        elif kind == 'GOAL_COMPLETE':
            assert state[a] == len(paths[a]) - 1 and a not in completed and a not in active and a not in station
            completed[a] = t
        elif kind == 'INITIAL_READY':
            assert t == initial_delay[a] and state[a] == g['current'][a]
        else:
            raise AssertionError(('Unknown event', kind))
    assert not any([active, edges, turning, station, segment_moves])
    assert set(completed) == set(range(n)) and started == set(range(n))
    assert all(state[a] == len(paths[a]) - 1 and occupied[a] == {tuple(paths[a][-1][0])} for a in range(n))
    assert len(reservations) == n
    assert {str(a): str(t) for a, t in completed.items()} == data['completion_times']
    assert max(completed.values()) == F(data['makespan']) and sum(completed.values(), F(0)) == F(data['sum_completion_time'])
    if data['profile'] == 'author_unit':
        indices = [0] * n
        states = g['current'].copy()
        assert F(data['makespan']) == author['ticks'] and F(data['sum_completion_time']) == author['cost']
        for t, recorded in enumerate(author['states']):
            for a in range(n):
                while indices[a] < len(arrivals[a]) and arrivals[a][indices[a]][0] <= t:
                    states[a] = arrivals[a][indices[a]][1]; indices[a] += 1
            assert states == recorded, ('Author integer state mismatch', t)
    return {'passed': True, 'moves': moves, 'events': len(data['events']), 'original_graph_unchanged': True,
            'author_unit_full_state_match': data['profile'] == 'author_unit', 'exact_completion_sum': data['sum_completion_time']}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    results = [r for path in sorted(P.glob('RESULTS_attempt*.json')) for r in json.loads(path.read_text())]
    registered = json.loads((P / 'REGISTRATION.json').read_text())['runs']
    assert len({r['spec']['id'] for r in results}) == len(results)
    if not args.limit:
        assert {r['spec']['id'] for r in results} == {r['id'] for r in registered}
    if args.limit:
        results = results[:args.limit]
    checks = []
    first = None
    for row in results:
        assert row['error'] is None
        path = P / row['raw']; assert sha(path) == row['raw_sha256']
        raw = gzip.decompress(path.read_bytes())
        assert hashlib.sha256(raw).hexdigest() == row['uncompressed_sha256']
        data = json.loads(raw)
        author = json.loads(gzip.decompress(Path(row['spec']['source']).read_bytes()))[row['spec']['part']]
        if first is None:
            first = data, author
        events = event_audit(data, author)
        geometry = geometry_audit(data['segments'], data['makespan'], data['agents'], data['radius'])
        checks.append({'id': row['spec']['id'], 'raw_sha256': row['raw_sha256'], 'events': events, 'geometry': geometry})
        print(row['spec']['id'], 'PASS', geometry['exact_pairs_checked'], flush=True)
    event_negatives = []
    for mutation in ['half_move_falsely_advances_state', 'source_exit_at_midpoint']:
        data, author = copy.deepcopy(first)
        if mutation == 'half_move_falsely_advances_state':
            e = next(e for e in data['events'] if e['kind'] == 'HALF_END')
            e['state'] = e['to_state']
        else:
            e = next(e for e in data['events'] if e['kind'] == 'CELL_EXIT')
            e['t'] = str(F(e['t']) - F(1, 10))
            data['events'].sort(key=lambda e: (F(e['t']), e['seq']))
            for seq, event in enumerate(data['events']):
                event['seq'] = seq
        try:
            event_audit(data, author)
        except AssertionError as error:
            event_negatives.append({'mutation': mutation, 'rejected': True, 'reason': str(error)})
        else:
            raise AssertionError('Accepted broken events: ' + mutation)
    output = {'passed': True, 'candidate_executor_imports': False, 'partial': bool(args.limit), 'runs': len(checks),
              'auditor_sha256': sha(Path(__file__)), 'geometry_sha256': sha(ROOT / 'exact_segments.py'),
              'geometry_negative_controls': self_check(), 'event_negative_controls': event_negatives, 'checks': checks}
    name = 'ROOT_GSES_PILOT.json' if args.limit else 'ROOT_GSES_EXECUTION.json'
    (ROOT / name).write_text(json.dumps(output, indent=2) + '\n')


if __name__ == '__main__':
    main()
