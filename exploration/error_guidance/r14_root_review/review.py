"""Root-owned exact checks of new views, without importing the candidate adapter."""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import copy
import gzip
import hashlib
import json
import math
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
P = HERE.parent / 'position_search_bridge_20261004_r14'
OLD = HERE.parent / 'gses_online_adoption_20261004_r13'
REVIEW = HERE.parent / 'r13_root_review'
sys.path.insert(0, str(REVIEW))
from audit_online import decode, validate_graph, family


def read(p):
    return json.loads(p.read_text())


def packed(p):
    return json.loads(gzip.decompress(p.read_bytes()))


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def digest(v):
    return hashlib.sha256(json.dumps(v, sort_keys=True, separators=(',', ':')).encode()).hexdigest()


def normalize(v):
    if isinstance(v, float):
        assert v.is_integer()
        return int(v)
    if isinstance(v, list):
        return [normalize(x) for x in v]
    if isinstance(v, dict):
        return {k: normalize(x) for k, x in v.items()}
    return v


def graph_hash(g):
    g = normalize(copy.deepcopy(g))
    for k in ('type1', 'type2'):
        g[k].sort()
    return digest(g)


def lift(old, inp, selected):
    validate_graph(selected)
    for key in ('paths', 'offsets', 'current', 'type1'):
        assert selected[key] == inp[key]
    assert Counter(map(family, selected['type2'])) == Counter(map(family, inp['type2']))
    directions = {family(e): e for e in selected['type2']}
    full = copy.deepcopy(old)
    full['type2'] = sorted(directions.get(family(e), e) for e in old['type2'])
    validate_graph(full)
    return full


def independently_derive(base, snap, observation):
    graph = base['solver_graph']
    ids = [(a, s) for a, path in enumerate(graph['paths']) for s in range(len(path))]
    at = F(base['public_at'])
    active = []
    for c in base['active_commitments']:
        a, s = c['agent'], c['from_state']
        start, = [e for e in base['observed_events'] if e['kind'] == 'MOVE_START'
                  and e['agent'] == a and e['from_state'] == s]
        age = at - F(start['t'])
        origin, dest = tuple(c['origin']), tuple(c['destination'])
        cells = {tuple(cell) for cell in base['physical_cells'][a]}
        low, high = {(True, False): (F(0), F(2, 5)),
                     (True, True): (F(2, 5), F(3, 5)),
                     (False, True): (F(3, 5), F(1))}[origin in cells, dest in cells]
        speed = F(1)
        for e in base['observed_events']:
            if e['seq'] < start['seq'] or e['agent'] != a:
                continue
            if e['kind'] == 'CELL_ENTER' and tuple(e['cell']) == dest:
                speed = F(2, 5) / (F(e['t']) - F(start['t']))
            elif e['kind'] == 'CELL_EXIT' and tuple(e['cell']) == origin:
                speed = F(3, 5) / (F(e['t']) - F(start['t']))
        alpha = max(low, min(high, age * speed))
        releases = sum(ids[u] == (a, s + 1) for u, _, _ in graph['type2'])
        active.append({'agent': a, 'state': s, 'age': age, 'alpha': alpha,
                       'releases': releases, 'commitment': c, 'start': start['t']})
    selected = min(active, key=lambda r: (-r['releases'], r['agent'], r['state'])) if active else None
    public_graph, position_graph = copy.deepcopy(graph), copy.deepcopy(graph)
    if selected:
        request = observation['request']
        a, s = selected['agent'], selected['state']
        c = selected['commitment']
        assert request == {'domain': 'r14_affine_simulated_position_v1',
                           'public_base_sha256': digest(base), 'captured_at': base['public_at'],
                           'agent': a, 'from_state': s, 'to_state': s + 1,
                           'origin': c['origin'], 'destination': c['destination'],
                           'move_started_at': selected['start'], 'request_count': 1}
        body, receipt = observation['body'], observation['receipt']
        assert receipt['request_sha256'] == digest(request)
        assert receipt['body_sha256'] == digest(body)
        assert observation['trusted_receipt_sha256'] == digest(receipt)
        assert receipt['production_cost'] is None and body['production_cost'] is None
        assert body['source'] == receipt['source'] == 'synthetic_position_measurement'
        assert body['request'] == request and body['request_count'] == 1
        assert body['captured_at'] == body['delivered_at'] == str(at)
        pieces = [e for e in snap['segments'] if e['agent'] == a and F(e['t0']) <= at <= F(e['t1'])]
        segment = pieces[-1]
        ratio = (at - F(segment['t0'])) / (F(segment['t1']) - F(segment['t0']))
        point = [F(x) + ratio * (F(y) - F(x)) for x, y in zip(segment['p0'], segment['p1'])]
        assert point == list(map(F, body['position']))
        measured_alpha = sum((p - x) * (y - x) for p, x, y in zip(point, c['origin'], c['destination']))
        assert measured_alpha == F(body['progress_lower']) == F(body['progress_upper'])
    else:
        assert observation is None
    changes = []
    for row in active:
        a, s, age = row['agent'], row['state'], row['age']
        alphas = [row['alpha'], measured_alpha if selected and a == selected['agent'] else row['alpha']]
        weights = []
        for output, alpha in zip([public_graph, position_graph], alphas):
            weight = max(1, math.ceil(age * (1 - alpha) / alpha)) if age > 0 and alpha > 0 else 1
            edge, = [e for e in output['type1'] if e[0] == graph['offsets'][a] + s]
            edge[2] = weight
            weights.append(weight)
        if selected and a == selected['agent']:
            changes.append({'agent': a, 'public_alpha': str(alphas[0]), 'measured_alpha': str(alphas[1]),
                            'public_weight': weights[0], 'position_weight': weights[1]})
    return public_graph, position_graph, changes


def views():
    records = []
    kinds = {'INITIAL', 'INITIAL_READY', 'TURN_START', 'TURN_END', 'MOVE_START', 'CELL_ENTER',
             'CELL_EXIT', 'ARRIVE', 'STATION_START', 'STATION_END', 'GOAL_COMPLETE'}
    for spec in read(OLD / 'REGISTRATION.json')['runs']:
        context = spec['id']
        checkpoint = OLD / 'raw' / (context + '__checkpoint.json.gz')
        snap = decode(packed(checkpoint))
        old_public = read(OLD / 'public' / (context + '.json'))
        base = read(P / 'public' / (context + '.json'))
        expected = copy.deepcopy(old_public)
        expected['observed_events'] = [e for e in snap['events'] if e['kind'] in kinds and F(e['t']) <= snap['t']]
        expected['schema'] = 'r14_public_base_v1'
        assert base == expected
        observation = read(P / 'evidence' / (context + '.json'))
        if observation:
            assert observation['receipt']['checkpoint_sha256'] == sha(checkpoint)
        public_graph, position_graph, changes = independently_derive(base, snap, observation)
        for option, graph in [('public', public_graph), ('position', position_graph)]:
            view = read(P / 'views' / (context + '__' + option + '.json'))
            assert graph == view['solver_graph']
            assert view['public_base_sha256'] == digest(base)
            assert view['evidence_sha256'] == (digest(observation['body']) if option == 'position' and observation else None)
        records.append({'context': context, 'changes': changes,
                        'paid_graph_differs': public_graph != position_graph,
                        'public_graph_differs_from_R13': public_graph != old_public['solver_graph']})
    return records


def results():
    reg = read(P / 'REGISTRATION.json')
    rows = read(P / 'RESULTS.json')
    assert len(rows) == 36 and len({r['id'] for r in rows}) == 36
    old_rows = {r['id']: r for r in read(OLD / 'RESULTS.json')}
    previous_audit = read(REVIEW / 'ROOT_ONLINE_AUDIT.json')
    assert previous_audit['passed'] and len(previous_audit['checks']) == 36
    audited = {r['id']: r['raw_sha256'] for r in previous_audit['checks']}
    context_cache, checked_raw, records = {}, set(), []
    for r in rows:
        cid = r['context']
        if cid not in context_cache:
            checkpoint = OLD / 'raw' / (cid + '__checkpoint.json.gz')
            snap = decode(packed(checkpoint))
            context_cache[cid] = (snap, sha(checkpoint))
        snap, checkpoint_sha = context_cache[cid]
        assert r['checkpoint_sha256'] == checkpoint_sha
        old = snap['g']
        for label in ('public_base', 'search_view', 'evidence'):
            if r[label]:
                assert sha(Path(r[label]['path'])) == r[label]['sha256']
        if r['option'] == 'keep':
            assert r['status'] == 'Control' and r['call_reference'] is None
            full = old
        else:
            view = read(Path(r['search_view']['path']))
            call = r['call_reference']
            assert sha(Path(call['reply'])) == call['reply_sha256']
            reply = read(Path(call['reply']))
            assert reply['input_graph'] == view['solver_graph'] and reply['method'] == 'GSES'
            assert reply['status'] == r['status'] == 'Succ'
            assert graph_hash(reply['selected_graph']) == r['candidate_graph_sha256']
            full = lift(old, view['solver_graph'], reply['selected_graph'])
            identity = {'canonical_input_sha256': graph_hash(view['solver_graph']), 'method': 'GSES',
                        'config': reg['config'], 'binary_sha256': reg['binary_sha256'],
                        'author_sources_sha256': reg['author_sources_sha256'],
                        'author_binding_sha256': reg['author_binding_sha256'],
                        'adapter_sha256': reg['adapter_sha256']}
            assert digest(identity) == r['solver_key']
            receipt = read(Path(call['receipt']))
            assert receipt['returncode'] == 0
            assert receipt['command'][2] == reg['binary'] and receipt['command'][4] == 'GSES'
            if r['call_source'] == 'new':
                assert receipt['identity'] == identity
                assert receipt['started_unix_ns'] > reg['frozen_unix_ns']
                attempt = read(Path(call['receipt']).parent / 'FIRST_ATTEMPT.json')
                assert attempt['solver_key'] == r['solver_key'] and attempt['first_attempt'] == 1
                assert sha(Path(receipt['command'][3])) == receipt['input_file_sha256']
        guard = read(P / 'guards' / (r['id'] + '.json'))
        assert guard['actual_full_graph'] == full and graph_hash(full) == r['adopted_graph_sha256']
        ids = [(a, s) for a, path in enumerate(old['paths']) for s in range(len(path))]
        protected = [(a, s) for a, agent in enumerate(snap['ag']) for s in range(old['current'][a], agent['state'])]
        protected += [(a, agent['state']) for a, agent in enumerate(snap['ag']) if 'active' in agent]
        for a, s in protected:
            target = old['offsets'][a] + s + 1
            assert sorted(e for e in full['type2'] if e[1] == target) == sorted(e for e in old['type2'] if e[1] == target)
        for e in old['type2']:
            a, s = ids[e[0]]
            if s <= snap['ag'][a]['state']:
                assert e in full['type2']
        continuation = r['continuation_source']
        assert continuation['source'] == 'reused_R13', 'New trajectory needs fresh event/geometry audit'
        previous = old_rows[continuation['reference_id']]
        assert previous['spec']['id'] == cid
        if previous['method'] == 'original':
            previous_full = old
        else:
            previous_reply = read(OLD / 'calls' / previous['id'] / 'author_reply.json')
            previous_full = lift(old, previous_reply['input_graph'], previous_reply['selected_graph'])
        assert previous_full == full
        assert continuation['raw_sha256'] == previous['raw_sha256'] == audited[previous['id']]
        raw = Path(continuation['raw'])
        assert raw == OLD / previous['raw'] and continuation['packed_sha256'] == previous['packed_sha256']
        if raw not in checked_raw:
            assert sha(raw) == previous['packed_sha256']
            checked_raw.add(raw)
        for k in ('sum_completion_time', 'makespan'):
            assert r[k] == continuation[k] == previous[k]
        ckey = digest({'checkpoint_packed_sha256': checkpoint_sha,
                       'adopted_full_graph_sha256': graph_hash(full),
                       'executor_sha256': reg['executor_sha256'], 'guard_sha256': reg['guard_sha256'],
                       'semantics': 'R11 affine exact event executor + R13 guarded graph adoption'})
        assert ckey == r['continuation_key']
        records.append({'id': r['id'], 'solver_key': r['solver_key'], 'call_source': r['call_source'],
                        'continuation_reference': previous['id'], 'reused_independent_audit': True})
    index = {(r['context'], r['option']): r for r in rows}
    for cid in context_cache:
        public, paid = index[cid, 'public'], index[cid, 'position']
        assert public['adopted_graph_sha256'] == paid['adopted_graph_sha256']
        assert public['continuation_key'] == paid['continuation_key']
    new_calls = list((P / 'calls').glob('*/receipt.json'))
    assert len(new_calls) == 1 and not list((P / 'raw').glob('*.json.gz'))
    return {'passed': True, 'rows': len(records), 'new_solver_calls': len(new_calls),
            'new_physical_continuations': 0, 'reused_unique_audited_trajectories': len(checked_raw),
            'position_execution_changes': 0, 'prior_independent_audit_sha256': sha(REVIEW / 'ROOT_ONLINE_AUDIT.json'),
            'records': records}


if __name__ == '__main__':
    if '--results' in sys.argv:
        result = results()
        name = 'ROOT_RESULT_AUDIT.json'
    else:
        result = {'passed': True, 'candidate_implementation_imported': False,
                  'native_runs': 0, 'solver_calls': 0, 'views': views()}
        name = 'ROOT_VIEW_AUDIT.json'
    (HERE / name).write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items() if k not in ('views', 'records')}))
