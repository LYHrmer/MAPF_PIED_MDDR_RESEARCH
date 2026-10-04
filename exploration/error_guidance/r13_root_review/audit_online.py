"""Independent online adoption audit; imports only independently adapted R11 auditor."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
import argparse, copy, gzip, hashlib, json, math
from event_core import event_audit
from exact_segments import audit as geometry_audit, self_check

ROOT = Path(__file__).resolve().parent
P = ROOT.parent / 'gses_online_adoption_20261004_r13'

def sha(raw): return hashlib.sha256(raw).hexdigest()
def canonical(x): return sha(json.dumps(x, sort_keys=True, separators=(',', ':')).encode())
def read(path): return json.loads(path.read_text())
def packed(path): return json.loads(gzip.decompress(path.read_bytes()))
def family(e): return min(tuple(e[:2]), (e[1] + 1, e[0] - 1))

def decode(v):
    if isinstance(v, list): return [decode(x) for x in v]
    if not isinstance(v, dict): return v
    assert len(v) == 1
    kind, value = next(iter(v.items()))
    if kind == '$fraction': return F(value)
    if kind == '$tuple': return tuple(map(decode, value))
    if kind == '$set': return set(map(decode, value))
    assert kind == '$dict'
    return {decode(k): decode(x) for k, x in value}

def validate_graph(g):
    ids = [(a, s) for a, path in enumerate(g['paths']) for s in range(len(path))]
    assert g['offsets'] == [sum(map(len, g['paths'][:a])) for a in range(len(g['paths']))]
    out, indegree = defaultdict(list), [0] * len(ids)
    for u, v, w in g['type1']:
        assert 0 <= u < len(ids) and 0 <= v < len(ids)
        a, s = ids[u]
        assert ids[v] == (a, s + 1) and w >= 1 and F(w).denominator == 1
    for u, v, w in g['type2']:
        assert 0 <= u < len(ids) and 0 <= v < len(ids)
        a, s = ids[u]; b, t = ids[v]
        assert a != b and s >= 1 and w == 1
        assert g['paths'][a][s - 1][0] == g['paths'][b][t][0]
    for u, v, w in g['type1'] + g['type2']:
        out[u].append(v); indegree[v] += 1
    queue = [u for u, d in enumerate(indegree) if not d]; count = 0
    while queue:
        u = queue.pop(); count += 1
        for v in out[u]:
            indegree[v] -= 1
            if not indegree[v]: queue.append(v)
    assert count == len(ids), 'Cyclic dependency graph'
    assert len(set(map(family, g['type2']))) == len(g['type2'])
    return ids

def boundary_checker(data, pub, snap, reply):
    old, new = data['graph'], data['final_graph']
    ids = validate_graph(old); validate_graph(new)
    at = F(pub['public_at']); boundary = len(snap['events'])
    assert snap['t'] == at and data['events'][:boundary] == snap['events']
    # Active segments were already committed before the solver call.
    assert data['segments'][:len(snap['segments'])] == snap['segments']
    assert set(pub) == {'public_at', 'arrived_states', 'active_commitments', 'phases',
                        'physical_cells', 'reservations', 'edge_reservations', 'nominal_contract', 'solver_graph'}
    assert all(F(e['t']) <= at for e in data['events'][:boundary])
    assert all(F(e['t']) > at for e in data['events'][boundary:]), 'Checkpoint not after same-time scheduling'
    for key in ['paths', 'current', 'offsets', 'type1']: assert old[key] == new[key]
    assert Counter(map(family, old['type2'])) == Counter(map(family, new['type2']))

    def check(state, active, occupied, reservations, edges, turning, station, completed):
        assert state == pub['arrived_states']
        commitments = [{'agent': a, 'from_state': m['s'], 'to_state': m['s'] + 1,
                        'origin': list(m['origin']), 'destination': list(m['dest'])} for a, m in sorted(active.items())]
        assert commitments == pub['active_commitments']
        assert [[list(cell) for cell in sorted(occupied[a])] for a in range(len(state))] == pub['physical_cells']
        assert [[list(cell), a] for cell, a in sorted(reservations.items())] == pub['reservations']
        assert [[[list(c) for c in edge], a] for edge, a in sorted(edges.items())] == pub['edge_reservations']
        weights = {ids[u]: F(w) for u, v, w in old['type1']}
        for a, phase in enumerate(pub['phases']):
            expected = 'move' if a in active else 'turn' if a in turning else 'station' if a in station else 'done' if a in completed else None
            if expected: assert phase == expected
            else:
                initial = state[a] == old['current'][a] and at < weights.get((a, state[a]), F(1)) - 1
                assert (phase == 'initial') == initial
                assert phase in {'initial', 'ready', 'need_turn'}
        inp = copy.deepcopy(old); inp['current'] = state.copy(); inp['type1'] = []
        for a, path in enumerate(old['paths']):
            for s in range(state[a], len(path) - 1):
                delay = max(0, math.ceil(weights[a, s] - 1 - at)) if s == state[a] and pub['phases'][a] == 'initial' else 0
                inp['type1'].append([old['offsets'][a] + s, old['offsets'][a] + s + 1, 1 + delay])
        inp['type2'] = sorted(e for e in old['type2'] if ids[e[0]][1] > state[ids[e[0]][0]])
        for u, v, w in inp['type2']: assert ids[v][1] > state[ids[v][0]]
        inp['type1'].sort(); assert pub['solver_graph'] == inp
        validate_graph(inp)
        protected = [(a, s) for a in range(len(state)) for s in range(old['current'][a], state[a])]
        protected += [(a, state[a]) for a in active]
        for a, s in protected:
            vertex = old['offsets'][a] + s + 1
            assert sorted(e for e in old['type2'] if e[1] == vertex) == sorted(e for e in new['type2'] if e[1] == vertex), 'Changed committed transition'
        assert all(e in new['type2'] for e in old['type2'] if ids[e[0]][1] <= state[ids[e[0]][0]])
        adoption = data['adoption']
        if adoption is None:
            assert old == new
        else:
            assert reply is not None and reply['status'] == 'Succ'
            assert reply['input_graph'] == inp
            selected = reply['selected_graph']; validate_graph(selected)
            for key in ['paths', 'current', 'offsets', 'type1']: assert selected[key] == inp[key]
            assert Counter(map(family, selected['type2'])) == Counter(map(family, inp['type2']))
            orientations = {family(e): e for e in selected['type2']}
            expected = copy.deepcopy(old)
            expected['type2'] = sorted(orientations.get(family(e), e) for e in old['type2'])
            assert new == expected == adoption['graph']
            assert sorted(protected) == sorted(map(tuple, adoption['protected_transitions']))
            assert adoption['active_count'] == len(active) and adoption['event_seq'] == boundary and F(adoption['at']) == at
            assert adoption['initial_graph_sha256'] == canonical(old) and adoption['adopted_graph_sha256'] == canonical(new)
            assert adoption['removed_type2'] == sorted(e for e in old['type2'] if e not in new['type2'])
            assert adoption['added_type2'] == sorted(e for e in new['type2'] if e not in old['type2'])
            assert adoption['changed'] == (old != new)
    return boundary, check

def audit_row(row, geometry=True, override=None, public_override=None):
    raw = gzip.decompress((P / row['raw']).read_bytes())
    assert sha(raw) == row['raw_sha256'] and sha((P / row['raw']).read_bytes()) == row['packed_sha256']
    data = json.loads(raw) if override is None else override
    source = Path(row['spec']['source']); assert sha(source.read_bytes()) == row['spec']['sha256']
    author = packed(source)['original']
    pub = read(P / 'public' / (row['spec']['id'] + '.json')) if public_override is None else public_override
    snap = decode(packed(P / 'raw' / (row['spec']['id'] + '__checkpoint.json.gz')))
    assert snap['g'] == author['graph'] == data['graph']
    reply = None
    if row['method'] != 'original':
        receipt = read(P / row['receipt']); assert receipt['returncode'] == 0
        reply = read((P / row['receipt']).parent / 'author_reply.json')
        assert reply['method'] == row['method'] and row['public_sha256'] == sha((P / 'public' / (row['spec']['id'] + '.json')).read_bytes())
    boundary, callback = boundary_checker(data, pub, snap, reply)
    events = event_audit(data, author, boundary, callback)
    geom = geometry_audit(data['segments'], data['makespan'], data['agents'], data['radius']) if geometry else None
    return {'id': row['id'], 'raw_sha256': row['raw_sha256'], 'events': events, 'geometry': geom,
            'boundary': boundary, 'sum_completion_time': data['sum_completion_time'], 'makespan': data['makespan']}

def main():
    parser = argparse.ArgumentParser(); parser.add_argument('--limit', type=int); args = parser.parse_args()
    rows = read(P / 'RESULTS.json'); reg = read(P / 'REGISTRATION.json')
    assert len({r['id'] for r in rows}) == len(rows)
    assert {r['id'] for r in rows} == {r['id'] + '__' + m for r in reg['runs'] for m in ['original', 'GSES', 'Improved_GSES']}
    checks = []
    for r in (rows[:args.limit] if args.limit else rows):
        checks.append(audit_row(r)); print(r['id'], 'PASS', flush=True)
    exemplar = next(r for r in rows if r.get('changed'))
    negatives = []
    for name in ['wrong_graph_at_switch', 'future_input_field', 'half_as_arrival', 'wrong_public_state', 'active_commitment_removed']:
        data = packed(P / exemplar['raw']); pub = read(P / 'public' / (exemplar['spec']['id'] + '.json'))
        if name == 'wrong_graph_at_switch': data['final_graph'] = data['graph']
        elif name == 'future_input_field': pub['future_profile'] = data['profile']
        elif name == 'half_as_arrival':
            e = next(e for e in data['events'] if e['kind'] == 'HALF_END'); e['state'] = e['to_state']
        elif name == 'wrong_public_state': pub['arrived_states'][0] += 1
        else: pub['active_commitments'].pop()
        try: audit_row(exemplar, geometry=False, override=data, public_override=pub)
        except AssertionError as exc: negatives.append({'name': name, 'rejected': True, 'reason': str(exc)})
        else: raise AssertionError('Accepted mutation ' + name)
    output = {'passed': True, 'partial': bool(args.limit), 'runs': len(checks), 'candidate_imports': False,
              'auditor_sha256': sha(Path(__file__).read_bytes()), 'event_core_sha256': sha((ROOT / 'event_core.py').read_bytes()),
              'geometry_sha256': sha((ROOT / 'exact_segments.py').read_bytes()),
              'negative_controls': negatives, 'geometry_negative_controls': self_check(), 'checks': checks}
    name = 'ROOT_ONLINE_PILOT.json' if args.limit else 'ROOT_ONLINE_AUDIT.json'
    (ROOT / name).write_text(json.dumps(output, indent=2) + '\n')

if __name__ == '__main__': main()
