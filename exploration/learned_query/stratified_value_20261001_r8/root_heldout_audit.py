"""Root audit: recompute held-out outcomes and decisions without importing the runner."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter, defaultdict
import hashlib
import json

HERE = Path(__file__).resolve().parent


def read(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def midpoint(bound):
    return F(bound['lower'] + bound['upper'], 2 * bound['denominator'])


def main(here=HERE, model_path=None, expected_episodes=60, output_path=None):
    HERE = here
    model_path = model_path or HERE / 'MODELS_FROZEN_BEFORE_TEST.json'
    registration = read(HERE / 'REGISTRATION.json')
    model = read(model_path)
    for name, value in registration['frozen'].items():
        assert sha(HERE / name) == value, name
    worlds = [w for w in registration['worlds'] if w['split'] in ('test', 'scale')]
    rows = []
    for world in worlds:
        for policy in registration['policies']:
            receipt_path = HERE / 'runs' / (world['name'] + '__' + policy + '.receipt.json')
            receipt = read(receipt_path)
            for key in ('raw', 'planner', 'input'):
                assert sha(Path(receipt[key])) == receipt[key + '_sha256']
            assert receipt['binary_sha256'] == registration['binary_sha256']
            assert receipt['bridge_sha256'] == registration['bridge_sha256']
            row = dict(world=world['name'], split=world['split'], map=world['map_name'],
                       seed=world['seed'], shift=world['shift'], N=world['N'], policy=policy,
                       error=receipt['error'], receipt_sha256=sha(receipt_path))
            if receipt['error'] is not None:
                rows.append(row)
                continue
            tasks = {task['task']: (robot['agent'], tuple(task['goal']))
                     for robot in world['robots'] for task in robot['tasks']}
            first = {t['task'] for robot in world['robots'] for t in robot['tasks'][:4]}
            completed = {}
            served_by_agent = Counter()
            decisions = commits = calls = multi = multi_query = free_wait = 0
            used = 0
            query_bins = [0] * 4
            pending = None
            previous_time = F(0)
            summary = None
            for line in Path(receipt['raw']).open():
                event = json.loads(line)
                kind = event['event']
                if 'at' in event:
                    at = midpoint(event['at'])
                    assert previous_time <= at <= world['horizon']
                    previous_time = at
                if kind == 'task_service':
                    task, agent = event['task'], event['agent']
                    assert task not in completed
                    assert tasks[task] == (agent, tuple(event['goal']))
                    assert task == world['robots'][agent]['tasks'][served_by_agent[agent]]['task']
                    assert event['original_endpoint_at_rest'] and event['physical_footprint_inside_service_square']
                    served_by_agent[agent] += 1
                    completed[task] = at
                elif kind == 'actor_decision':
                    assert pending is None
                    decisions += 1
                    assert event['opportunity'] == decisions and event['policy'] == policy
                    assert event['remaining_capacity'] == receipt['capacity'] - used
                    candidates = event['candidates']
                    assert candidates
                    multi += len(candidates) > 1
                    for candidate in candidates:
                        features = list(map(F, candidate['features']))
                        if policy.startswith('paced_ridge_'):
                            name = policy.removeprefix('paced_')
                            coefficients = list(map(F, model['models'][name]['coefficients']))
                            if name == 'ridge_nohistory':
                                features[10:18] = [F(0)] * 8
                            score = coefficients[0] + sum(c * x for c, x in zip(coefficients[1:], features))
                            assert score == F(candidate['score'])
                    time_bin = min(3, int(at // 32))
                    allowance = 4 * (time_bin + 1) if policy.startswith('paced_') else receipt['capacity']
                    available = used < min(allowance, receipt['capacity'])
                    positive = [c for c in candidates if F(c['score']) > 0]
                    expected = min(positive, key=lambda c: (-F(c['score']), c['agent']))['move'] if available and positive else ''
                    assert event['selected'] == expected
                    if expected:
                        used += 1
                        query_bins[time_bin] += 1
                        multi_query += len(candidates) > 1
                        pending = expected
                    elif available:
                        free_wait += 1
                elif kind == 'certified_POSITION_committed':
                    assert event['move'] == pending
                    commits += 1
                    pending = None
                elif kind == 'planner_request':
                    calls += 1
                elif kind == 'joint_summary':
                    assert summary is None
                    summary = event
            assert pending is None and summary == receipt['summary']
            assert summary['served'] == len(completed)
            assert summary['queries'] == used == commits
            assert summary['official_plan_calls'] == calls
            fixed_flow = sum((completed.get(task, F(world['horizon'])) for task in first), F(0))
            row.update(served=len(completed), queries=used, query_bins=query_bins,
                       fixed_first4_time=str(fixed_flow), fixed_first4_tasks=len(first),
                       fixed_first4_completed=sum(t in completed for t in first),
                       multi_opportunities=multi, multi_queries=multi_query,
                       available_budget_WAIT=free_wait, deadlock=summary['deadlock'],
                       official_calls=calls)
            rows.append(row)
    assert len(rows) == expected_episodes
    pairs = []
    for world in worlds:
        group = {r['policy']: r for r in rows if r['world'] == world['name']}
        for reference in ('WAIT', 'paced_condition', 'paced_ridge_nohistory'):
            a, b = group['paced_ridge_history'], group[reference]
            if a['error'] is None and b['error'] is None:
                pairs.append(dict(world=world['name'], split=world['split'], map=world['map_name'],
                                  seed=world['seed'], shift=world['shift'], reference=reference,
                                  task_delta=a['served'] - b['served'],
                                  query_delta=a['queries'] - b['queries'],
                                  fixed_time_gain=str(F(b['fixed_first4_time']) - F(a['fixed_first4_time']))))
    totals = []
    for split in ('test', 'scale'):
        for policy in registration['policies']:
            group = [r for r in rows if r['split'] == split and r['policy'] == policy]
            good = [r for r in group if r['error'] is None]
            totals.append(dict(split=split, policy=policy, expected=len(group), successful=len(good),
                               errors=len(group)-len(good),
                               served=sum(r['served'] for r in good), queries=sum(r['queries'] for r in good),
                               deadlocks=sum(r['deadlock'] for r in good),
                               fixed_time=str(sum((F(r['fixed_first4_time']) for r in good), F(0)))))
    families = defaultdict(list)
    for pair in pairs:
        if pair['split'] == 'test':
            families[(pair['map'], pair['seed'], pair['reference'])].append(pair)
    family_effects = [dict(map=k[0], seed=k[1], reference=k[2], paired_conditions=len(v),
                           task_delta_sum=sum(p['task_delta'] for p in v),
                           fixed_time_gain_sum=str(sum((F(p['fixed_time_gain']) for p in v), F(0))))
                      for k, v in families.items()]
    result = dict(passed=True, implementation_imported=False, rows=rows, totals=totals,
                  paired_differences=pairs, family_effects=family_effects,
                  uncertainty='Four test map/task families, with IID/SHIFT paired; no 48-arm independent-sample inference.',
                  files=dict(registration=sha(HERE/'REGISTRATION.json'), model=sha(model_path)))
    (output_path or HERE/'ROOT_HELDOUT_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(passed=True, episodes=len(rows), totals=totals), indent=2))


if __name__ == '__main__':
    main()
