"""Reconstruct two saved SADG suffixes without the candidate event adapter.

No physical execution or author optimizer calls. Exact rational continuous
point-distance audit includes all waiting and goal occupancy segments.
"""
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'sadg_preflight_20261004_r16'


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def q(x):
    return F(str(x))


def audit(name):
    gp = BASE / 'cases' / name / 'graph_after.json'
    sp = BASE / 'suffix' / (name + '.json')
    graph, suffix = load(gp), load(sp)
    assert suffix['source_graph_sha256'] == sha(gp)
    vertices = {v['uid']: v for v in graph['vertices']}
    edges = graph['type1'] + [d['active'] for g in graph['groups'] for d in g['dependencies']]
    before = defaultdict(set)
    for a, b in edges:
        assert a in vertices and b in vertices
        before[b].add(a)
    true_progress = {'agent0': F(1, 4), 'agent1': F(1, 2)}
    assert {a:q(p) for a,p in suffix['true_progress'].items()} == true_progress
    # Max-plus earliest event schedule, independently reconstructed from edges.
    start, finish = {}, {}
    pending = set(vertices)
    while pending:
        ready = sorted(v for v in pending if before[v] <= finish.keys())
        assert ready, 'dependency cycle'
        for uid in ready:
            v = vertices[uid]
            if v['status'] == 'COMPLETED':
                finish[uid] = F(0)
            elif v['status'] == 'IN_PROGRESS':
                assert all(finish[p] == 0 for p in before[uid])
                start[uid] = F(0)
                finish[uid] = 1 - true_progress[v['agent']]
            else:
                assert v['status'] == 'STAGED'
                start[uid] = max((finish[p] for p in before[uid]), default=F(0))
                # The paired real plant uses duration 1, independently of estimates.
                finish[uid] = start[uid] + 1
            pending.remove(uid)
    started, completed = set(), set()
    event_times = [q(e['t']) for e in suffix['events']]
    assert event_times == sorted(event_times)
    for e in suffix['events']:
        uid, kind, t = e['vertex'], e['kind'], q(e['t'])
        assert e['agent'] == vertices[uid]['agent']
        if kind in ('START', 'RESUME_COMMITTED'):
            assert uid not in started and t == start[uid]
            started.add(uid)
            if kind == 'START':
                assert all(finish[p] <= t for p in before[uid])
                assert set(e['active_dependency_tails']) == {
                    a for a,b in edges if b == uid and vertices[a]['agent'] != vertices[uid]['agent']}
            else:
                assert vertices[uid]['status'] == 'IN_PROGRESS'
                assert q(e['remaining']) == finish[uid]
        elif kind == 'COMPLETE':
            assert uid in started and uid not in completed and t == finish[uid]
            completed.add(uid)
        else:
            raise AssertionError(kind)
    remaining = {uid for uid,v in vertices.items() if v['status'] != 'COMPLETED'}
    assert started == completed == remaining
    end = {a:max(t for uid,t in finish.items() if vertices[uid]['agent']==a) for a in true_progress}
    makespan = max(end.values())
    assert {a:q(t) for a,t in suffix['completion_times'].items()} == end
    assert q(suffix['sum_completion_time']) == sum(end.values())
    assert q(suffix['makespan']) == makespan
    segments = defaultdict(list)
    for s in suffix['segments']:
        row = dict(s, t0=q(s['t0']), t1=q(s['t1']), p0=list(map(q,s['p0'])), p1=list(map(q,s['p1'])))
        assert row['t0'] < row['t1']
        v = vertices[s['vertex']]
        assert s['agent'] == v['agent']
        p0 = list(map(q,v['path_tuples'][0][:2]))
        p1 = list(map(q,v['path_tuples'][-1][:2]))
        if s['kind'] in ('MOVE', 'COMMITTED_REMAINDER'):
            assert row['t0'] == start[v['uid']] and row['t1'] == finish[v['uid']]
            if s['kind'] == 'COMMITTED_REMAINDER':
                p0 = [a+true_progress[v['agent']]*(b-a) for a,b in zip(p0,p1)]
            assert row['p0'] == p0 and row['p1'] == p1
            assert sum((b-a)**2 for a,b in zip(p0,p1)) == 4*(row['t1']-row['t0'])**2
        else:
            assert s['kind'] in ('WAIT', 'GOAL_HOLD') and row['p0'] == row['p1']
        segments[s['agent']].append(row)
    for a, seq in segments.items():
        seq.sort(key=lambda s:s['t0'])
        assert seq[0]['t0'] == 0 and seq[-1]['t1'] == makespan
        for left,right in zip(seq,seq[1:]):
            assert left['t1'] == right['t0'] and left['p1'] == right['p0'], 'gap or teleport'
    distances, overlaps = [], 0
    for a in segments['agent0']:
        for b in segments['agent1']:
            lo, hi = max(a['t0'],b['t0']), min(a['t1'],b['t1'])
            if hi < lo:
                continue
            overlaps += 1
            va = [(y-x)/(a['t1']-a['t0']) for x,y in zip(a['p0'],a['p1'])]
            vb = [(y-x)/(b['t1']-b['t0']) for x,y in zip(b['p0'],b['p1'])]
            rel = [x+u*(lo-a['t0'])-y-v*(lo-b['t0']) for x,u,y,v in zip(a['p0'],va,b['p0'],vb)]
            vel = [u-v for u,v in zip(va,vb)]
            vv = sum(v*v for v in vel)
            at = min(hi-lo,max(F(0),-sum(x*v for x,v in zip(rel,vel))/vv)) if vv else F(0)
            distances.append(sum((x+v*at)**2 for x,v in zip(rel,vel)))
    assert min(distances) == 4 and suffix['collision_audit']['collisions'] == []
    return dict(case=name, passed=True, graph_sha256=sha(gp), suffix_sha256=sha(sp),
                completion={a:str(t) for a,t in end.items()}, sum_completion=str(sum(end.values())),
                makespan=str(makespan), minimum_point_distance_squared=str(min(distances)),
                overlaps_including_closed_endpoints=overlaps, complete_events=len(completed),
                all_wait_and_goal_occupancy_covered=True)


def main():
    rows = [audit(n) for n in ('mini_public_elapsed','mini_measured')]
    result = dict(passed=True, cases=rows, new_author_solver_calls=0, new_physical_episodes=0,
                  scope='Paired synthetic event adapter, fixed true plant, point geometry; '
                        'not paid sensing, ROS control, or finite-footprint safety. '
                        'Strong history adopts the same graph as measured, so this does not establish extra measurement value.')
    (HERE/'SUFFIX_INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
