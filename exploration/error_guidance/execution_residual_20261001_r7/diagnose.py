"""Read-only R6c action-state accounting; observations never feed a predictor."""
from pathlib import Path
from collections import Counter
import csv, hashlib, json, math

HERE = Path(__file__).resolve().parent
PARENT = HERE.parent / 'published_continuous_execution_20261001_r6c'
RAW = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence') / PARENT.name
CATEGORIES = ['move_control', 'turn_control', 'station_control', 'active_pause',
              'dependency_wait', 'dispatch_wait', 'joint_barrier_idle',
              'physical_settling', 'planner_boundary_idle']

def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()

def classify(spec):
    n, horizon = spec['N'], spec['horizon_ticks']
    nodes = [[] for _ in range(n)]
    finished, admitted, obs, wheel_seen = set(), set(), {}, set()
    counts = [Counter() for _ in range(n)]
    lengths = [Counter() for _ in range(n)]
    last_tick, expected_seq, proposal = -1, 0, None
    path = RAW / 'runs' / spec['id'] / 'events.jsonl'
    with path.open() as f:
        for line in f:
            e = json.loads(line); kind = e['kind']; tick = e['tick']
            assert e['sequence'] == expected_seq and tick >= last_tick
            expected_seq += 1; last_tick = tick
            if kind == 'proposal':
                proposal = e['proposal']
                assert all(len(p) == 2 and [x[2] for x in p] == [0, 1] for p in proposal['plan'])
            elif kind == 'parsed':
                assert proposal['proposal_id'] == e['proposal_id']
                assert all((a, j) in finished for a in range(n) for j in range(len(nodes[a])))
                offsets = [len(v) for v in nodes]
                new = e['actions']
                # All parsed actions inherit previous grid-step time=0 in
                # the unchanged one-step parser (including turns/services).
                for a, seq in enumerate(new):
                    nodes[a].extend(dict(x, deps=[]) for x in seq)
                for a in range(n):
                    for b in range(a + 1, n):
                        for j, x in enumerate(new[a]):
                            for k, y in enumerate(new[b]):
                                if x['start'] == y['goal']:
                                    nodes[b][offsets[b]+k]['deps'].append((a, offsets[a]+j))
                                elif y['start'] == x['goal']:
                                    nodes[a][offsets[a]+j]['deps'].append((b, offsets[b]+k))
            elif kind == 'admit':
                a = int(e['robot'])
                for x in e['actions']:
                    key = (a, x[1]); node = nodes[a][x[1]]
                    assert key not in admitted and all(tuple(d) in finished for d in node['deps'])
                    assert x[3] == node['type'] and x[4] == node['start'] and x[5] == node['goal']
                    admitted.add(key)
                    if x[3] == 'M': lengths[a]['admitted_path_m'] += math.dist(x[4], x[5])
                    if x[3] == 'T': lengths[a]['admitted_quarter_turns'] += 1
            elif kind == 'end':
                a = int(e['robot']); key = (a, e['node'])
                assert e['accepted'] and key in admitted and key not in finished
                finished.add(key); node = nodes[a][key[1]]
                if node['type'] == 'M': lengths[a]['acknowledged_path_m'] += math.dist(node['start'], node['goal'])
                if node['type'] == 'T': lengths[a]['acknowledged_quarter_turns'] += 1
                if e['task']: lengths[a]['normal_station_END'] += 1
            elif kind == 'observation':
                a = int(e['robot']); o = e['observation']; obs[a] = o
                assert o['tick'] == tick
                lengths[a]['sampled_center_distance_m'] += o['displacement_m']
            elif kind == 'control' and e['control']['phase'] == 'wheel_command':
                a = int(e['robot']); c = e['control']; key = (a, tick)
                assert key not in wheel_seen and 0 <= tick < horizon
                wheel_seen.add(key)
                if c['paused']: category = 'active_pause'
                elif c['type'] in [0, 1, 3]:
                    category = {0:'move_control', 1:'turn_control', 3:'station_control'}[c['type']]
                else:
                    pending = [j for j in range(len(nodes[a])) if (a, j) not in finished]
                    if pending:
                        first = nodes[a][pending[0]]
                        category = 'dependency_wait' if any(tuple(d) not in finished for d in first['deps']) else 'dispatch_wait'
                    elif not obs[a]['idle']: category = 'physical_settling'
                    elif any((b, j) not in finished for b in range(n) for j in range(len(nodes[b]))):
                        category = 'joint_barrier_idle'
                    else: category = 'planner_boundary_idle'
                counts[a][category] += 1
    assert last_tick == horizon and len(wheel_seen) == n * horizon
    result = []
    for a in range(n):
        assert sum(counts[a].values()) == horizon
        result.append({'run':spec['id'], 'agent':a, **{k:counts[a][k] for k in CATEGORIES},
                       **lengths[a], 'total_ticks':horizon})
    return {'spec':spec, 'event_sha256':sha(path), 'event_count':expected_seq,
            'agent_ticks':n*horizon, 'counts':dict(sum(counts, Counter())),
            'conservation_passed':True, 'per_agent':result}

def main():
    runs = []
    for spec in json.loads((PARENT/'runs.json').read_text())['runs']:
        result = classify(spec); runs.append(result)
        print(spec['id'], result['counts'], flush=True)
    (HERE/'r6_diagnosis.json').write_text(json.dumps({'runs':runs, 'script_sha256':sha(__file__),
        'category_semantics':'one last wheel-command state per robot/tick; sampled center travel is auxiliary, not body speed or actor input',
        'dependency_reconstruction':'unchanged one-step parser time=0 and original ADG type-2 geometric rules; every actual admission checked'}, indent=2)+'\n')
    fields = ['run','agent',*CATEGORIES,'admitted_path_m','admitted_quarter_turns','acknowledged_path_m',
              'acknowledged_quarter_turns','normal_station_END','sampled_center_distance_m','total_ticks']
    with (HERE/'r6_agent_tick_accounting.csv').open('w') as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for run in runs:
            for row in run['per_agent']:w.writerow(row)
    sums = Counter()
    for run in runs: sums.update(run['counts'])
    print('TOTAL',sum(sums.values()),dict(sums),flush=True)

if __name__ == '__main__': main()
