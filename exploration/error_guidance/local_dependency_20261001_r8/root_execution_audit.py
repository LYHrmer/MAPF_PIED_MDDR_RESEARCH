"""Independent event-order, original type-2 dependency and FIFO outcome audit."""
from collections import defaultdict, deque
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
RAW = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence') / HERE.name / 'runs'


def load(path):
    return json.loads(path.read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def audit(spec):
    folder = RAW / spec['id']
    receipt = load(folder / 'receipt.json')
    assert receipt['spec'] == spec
    for filename, value in receipt['files'].items():
        assert sha(folder / filename) == value
    result = {k: spec[k] for k in ('id', 'split', 'map', 'seed', 'condition', 'execution', 'policy')}
    result['error'] = receipt['error']
    if receipt['error'] is not None:
        return result
    environment = load(HERE / 'inputs' / spec['input_id'] / 'environment.json')
    fifo = environment['FIFO_goals']
    waiting = defaultdict(deque)
    nodes, actual_nodes, incoming, ended = {}, {}, defaultdict(set), {}
    admitted, first_control = {}, {}
    services = defaultdict(list)
    batch_nodes = []
    dependency_checks = early_step2 = step2_total = midpoint_services = 0
    last_sequence = -1
    for line in (folder / 'events.jsonl').open():
        event = json.loads(line)
        assert event['sequence'] == last_sequence + 1
        last_sequence = event['sequence']
        kind, tick = event['kind'], event['tick']
        if kind == 'parsed':
            assert all(k in ended for k in batch_nodes), 'in-flight batch replaced'
            assert not any(waiting.values())
            batch_nodes = []
            pid = event['proposal_id']
            plans = event['actions']
            for agent, plan in enumerate(plans):
                for index, action in enumerate(plan):
                    key = (pid, agent, index)
                    nodes[key] = action
                    waiting[agent].append(key)
                    batch_nodes.append(key)
            # Match the author's ordered if/else-if construction exactly.
            # Every previous batch is already ACKed, so no old/new live edge remains.
            for agent, plan in enumerate(plans):
                for index, action in enumerate(plan):
                    for other in range(agent + 1, len(plans)):
                        for other_index, other_action in enumerate(plans[other]):
                            left, right = (pid, agent, index), (pid, other, other_index)
                            if action['start'] == other_action['goal'] and action['time'] <= other_action['time']:
                                incoming[right].add(left)
                            elif other_action['start'] == action['goal'] and other_action['time'] <= action['time']:
                                incoming[left].add(right)
        elif kind == 'admit':
            agent = int(event['robot'])
            for action in event['actions']:
                key = waiting[agent].popleft()
                expected = nodes[key]
                assert [action[3], action[4], action[5], action[2], action[6]] == [expected[k] for k in ('type', 'start', 'goal', 'orientation', 'task_id')]
                for predecessor in incoming[key]:
                    assert predecessor in ended, ('missing predecessor ACK', key, predecessor)
                    assert ended[predecessor]['sequence'] < event['sequence']
                    dependency_checks += 1
                if expected['time'] >= 1:
                    step2_total += 1
                    unfinished_step1 = [k for k in batch_nodes if nodes[k]['time'] < 1 and k not in ended]
                    if spec['execution'] == 'global':
                        assert not unfinished_step1, ('global gate violation', key)
                    early_step2 += bool(unfinished_step1)
                actual = (agent, action[1])
                assert actual not in actual_nodes
                actual_nodes[actual] = key
                admitted[key] = dict(tick=tick, sequence=event['sequence'])
        elif kind == 'control' and event['control']['nodes']:
            agent = int(event['robot'])
            key = actual_nodes[(agent, event['control']['nodes'][0])]
            if key not in first_control:
                first_control[key] = dict(tick=tick, sequence=event['sequence'])
                # Original type-1 queue order applies to execution, not early enqueue.
                previous = (key[0], key[1], key[2]-1)
                assert previous not in nodes or previous in ended
        elif kind == 'end':
            actual = (int(event['robot']), event['node'])
            key = actual_nodes[actual]
            assert event['accepted'] and key not in ended
            assert key in first_control
            ended[key] = dict(tick=tick, sequence=event['sequence'])
            if event['task']:
                agent = actual[0]
                goal = int(event['goal'][1]) * spec['cols'] + int(event['goal'][0])
                assert goal == fifo[agent][len(services[agent])], 'not the registered next FIFO task'
                assert event['task_id'] not in {s['task'] for ss in services.values() for s in ss}
                services[agent].append(dict(task=event['task_id'], tick=tick, goal=goal))
                midpoint_services += nodes[key]['time'] < 1
        elif kind == 'horizon':
            assert tick == spec['horizon_ticks'] == receipt['true_horizon_tick']
    first10 = sum(sum(s['tick'] for s in services[a][:10]) +
                  (10-min(10, len(services[a]))) * spec['horizon_ticks'] for a in range(spec['N']))
    result.update(served=sum(map(len, services.values())), fixed_first10_ticks=first10,
                  type2_predecessor_ACK_checks=dependency_checks, step2_admitted=step2_total,
                  step2_admitted_before_other_step1_END=early_step2,
                  service_at_step1=midpoint_services, parsed=len(nodes), ended=len(ended),
                  services=dict(services), receipt_sha256=sha(folder/'receipt.json'))
    if spec['split'] == 'mechanical':
        result['first_batch'] = [dict(agent=k[1], index=k[2], action=nodes[k],
                                      admit=admitted.get(k), first_control=first_control.get(k), end=ended.get(k))
                                 for k in nodes if k[0] == 0]
    return result


def main():
    specs = load(HERE/'runs.json')['runs']
    rows = [audit(spec) for spec in specs]
    assert len(rows) == 52
    totals = []
    for execution in ('global', 'local'):
        for policy in ('hm', 'history', 'learned'):
            group = [r for r in rows if r['split']=='test' and r['execution']==execution and r['policy']==policy]
            good = [r for r in group if r['error'] is None]
            totals.append(dict(execution=execution, policy=policy, expected=len(group), success=len(good),
                               served=sum(r['served'] for r in good),
                               fixed_first10_ticks=sum(r['fixed_first10_ticks'] for r in good)))
    pairs = []
    index = {(r['map'], r['seed'], r['condition'], r['execution'], r['policy']): r
             for r in rows if r['split']=='test'}
    for key, row in index.items():
        if key[4] != 'learned':
            continue
        for reference in ('hm', 'history'):
            other = index[(*key[:4], reference)]
            if row['error'] is None and other['error'] is None:
                pairs.append(dict(map=key[0], seed=key[1], condition=key[2], execution=key[3], reference=reference,
                                  task_delta=row['served']-other['served'],
                                  fixed_first10_gain_ticks=other['fixed_first10_ticks']-row['fixed_first10_ticks']))
    report = dict(passed=True, implementation_imported=False, rows=rows, totals=totals, pairs=pairs,
                  interpretation='Author ADG type-2 edges plus normal ACK verified. Global is an internal extra-gate ablation; local is buffered asynchrony. Four map/task families, no 48-arm independence claim.')
    (HERE/'ROOT_EXECUTION_AUDIT.json').write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps(dict(passed=True, episodes=len(rows), totals=totals), indent=2))


if __name__ == '__main__':
    main()
