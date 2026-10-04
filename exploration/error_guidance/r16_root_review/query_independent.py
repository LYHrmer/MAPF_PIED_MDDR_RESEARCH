"""Independent raw-event checks for the newly registered STOP tails.

Does not import the candidate runner/auditor/model. Does not read TEST traces.
The finite C/LD/STOP envelope is an offline diagnostic, never a baseline.
"""
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
QUERY = Path('/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query')
OLD = QUERY / 'late_budget_choice_20261004_r13'
NEW = QUERY / 'stop_value_20261004_r16'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def load(path):
    return json.loads(Path(path).read_text())


def interval(x):
    return F(x['lower'], x['denominator']), F(x['upper'], x['denominator'])


def canonical(x):
    return json.dumps(x, sort_keys=True, separators=(',', ':')).encode()


def normalize(row):
    return {k: v for k, v in row.items() if k not in ('policy', 'native_checks')}


def events(receipt):
    assert receipt['error'] is None
    for k in ('raw', 'planner', 'input'):
        assert sha(receipt[k]) == receipt[k + '_sha256'], (receipt['world'], k)
    return [json.loads(s) for s in Path(receipt['raw']).read_text().splitlines()]


def outcomes(rows, world, policy):
    assert world['split'] in ('train', 'calibration'), 'TEST is outside this audit'
    ends = [r for r in rows if r['event'] == 'joint_summary']
    assert len(ends) == 1
    end = ends[0]
    assert end['status'] == 'passed' and not end['deadlock']
    assert interval(end['last_clock']) == (F(world['horizon']),) * 2
    assert end['production_COST'] is False
    tasks = {r['agent']: r['tasks'] for r in world['robots']}
    counts = Counter()
    service = {}
    for r in rows:
        if r['event'] != 'task_service':
            continue
        a = r['agent']
        expected = tasks[a][counts[a]]
        assert r['task'] == expected['task'] and r['goal'] == expected['goal']
        assert r['original_endpoint_at_rest'] and r['physical_footprint_inside_service_square']
        assert (a, r['task']) not in service
        t = interval(r['at'])
        assert 0 <= t[0] <= t[1] <= world['horizon']
        service[a, r['task']] = t
        counts[a] += 1
    assert sum(counts.values()) == end['served']
    decisions = [r for r in rows if r['event'] == 'actor_decision']
    for r in decisions:
        for k in ('private_progress_input', 'regime_input', 'future_head_input'):
            assert r[k] is False
    queries = sum(r['selected_kind'] == 'QUERY' for r in decisions)
    assert queries == end['queries'] <= world['budget']
    total = [F(0), F(0)]
    for a, fifo in tasks.items():
        for task in fifo[:4]:
            t = service.get((a, task['task']), (F(world['horizon']),) * 2)
            total[0] += t[0]
            total[1] += t[1]
    return dict(world=world['name'], family=world['family_key'], split=world['split'],
                budget=world['budget'], policy=policy, tasks=sum(counts.values()),
                queries=queries, time_low=str(total[0]), time_high=str(total[1]),
                services_sha256=hashlib.sha256(canonical(sorted(
                    (a, t, str(v[0]), str(v[1])) for (a, t), v in service.items()))).hexdigest())


def stop_contract(rows, baseline):
    gate_at = [i for i, r in enumerate(rows) if r['event'] == 'macro_choice']
    old_gate_at = [i for i, r in enumerate(baseline) if r['event'] == 'macro_choice']
    assert len(gate_at) == len(old_gate_at) == 1
    i, j = gate_at[0], old_gate_at[0]
    assert [normalize(r) for r in rows[:i]] == [normalize(r) for r in baseline[:j]], 'prefix mismatch'
    gate, old_gate = rows[i], baseline[j]
    for k in ('at', 'opportunity', 'initial_capacity', 'remaining_capacity', 'spent',
              'target_agent', 'target_move', 'feature_schema', 'features'):
        assert gate[k] == old_gate[k], ('gate mismatch', k)
    assert gate['selected_option'] == 'STOP' and old_gate['selected_option'] == 'C'
    assert gate['spent'] >= gate['initial_capacity'] // 2
    assert gate['remaining_capacity'] > 0
    before_queries = sum(r['event'] == 'actor_decision' and r['selected_kind'] == 'QUERY' for r in rows[:i])
    assert before_queries == gate['spent']
    assert not any(r['event'] == 'certified_POSITION_committed' for r in rows[i+1:])
    for r in rows[i+1:]:
        if r['event'] == 'actor_decision':
            assert r['selected_kind'] == 'WAIT', 'STOP acquired information or skipped an occurrence'
            assert r['remaining_capacity'] == gate['remaining_capacity']
    return dict(prefix_events=i, gate_at=gate['at'], features=gate['features'],
                queries_before_gate=before_queries,
                normal_END_after_gate=sum(r['event'] == 'public_END_delivered' for r in rows[i+1:]),
                task_services_after_gate=sum(r['event'] == 'task_service' for r in rows[i+1:]))


def totals(rows):
    return dict(contexts=len(rows), families=len({r['family'] for r in rows}),
                tasks=sum(r['tasks'] for r in rows), queries=sum(r['queries'] for r in rows),
                time_low=str(sum((F(r['time_low']) for r in rows), F(0))),
                time_high=str(sum((F(r['time_high']) for r in rows), F(0))))


def main():
    world_by_name = {w['name']: w for w in load(OLD/'REGISTRATION.json')['worlds']
                     if w['split'] in ('train', 'calibration')}
    receipts = sorted((NEW/'runs').glob('*__macro_STOP.receipt.json'))
    assert len(receipts) == 27, ('expected 24 TRAIN and 3 new CAL STOP tails', len(receipts))
    paired, all_rows, pins = [], [], {}
    negative_rejected = []
    for path in receipts:
        e = load(path)
        world = world_by_name[e['world']]
        assert e['native_source_sha256'] == sha(NEW/'joint_history_native.cpp')
        assert e['binary_sha256'] == sha(NEW/'build/joint_history_native')
        assert e['registration_sha256'] == sha(NEW/'REGISTRATION.json')
        base_path = OLD/'runs'/(e['world']+'__macro_C.receipt.json')
        base = load(base_path)
        assert e['input_sha256'] == base['input_sha256']
        for k in ('bridge_sha256', 'config_sha256'):
            assert e[k] == base[k]
        current, prior = events(e), events(base)
        contract = stop_contract(current, prior)
        c, stop = outcomes(prior, world, 'C'), outcomes(current, world, 'STOP')
        low = F(c['time_low']) - F(stop['time_high'])
        high = F(c['time_high']) - F(stop['time_low'])
        paired.append(dict(world=world['name'], split=world['split'], budget=world['budget'],
                           task_delta=stop['tasks']-c['tasks'], time_saved_low=str(low),
                           time_saved_high=str(high), queries_saved=c['queries']-stop['queries'], **contract))
        ld_path = OLD/'runs'/(e['world']+'__macro_LD.receipt.json')
        ld_receipt = load(ld_path)
        assert ld_receipt['input_sha256'] == base['input_sha256']
        ld = outcomes(events(ld_receipt), world, 'LD')
        all_rows.extend((c, stop, ld))
        for p in (path, base_path, ld_path):
            pins[str(p)] = sha(p)
        if not negative_rejected:
            corrupted = json.loads(json.dumps(current))
            gate_index = next(i for i,r in enumerate(corrupted) if r['event']=='macro_choice')
            tail_index = next(i for i in range(gate_index+1,len(corrupted)) if corrupted[i]['event']=='actor_decision')
            corrupted[tail_index]['selected_kind'] = 'QUERY'
            try:
                stop_contract(corrupted, prior)
            except AssertionError:
                negative_rejected.append('forbidden_QUERY_after_STOP')
            assert negative_rejected
    summary = {}
    for split in sorted({r['split'] for r in all_rows}):
        group = [r for r in all_rows if r['split'] == split]
        fixed = {p: totals([r for r in group if r['policy'] == p]) for p in ('C','LD','STOP')}
        by_world = defaultdict(list)
        for row in group:
            by_world[row['world']].append(row)
        # The midpoint is a deterministic diagnostic tie-break, not significance.
        choice = [max(rs, key=lambda r:(r['tasks'], -(F(r['time_low'])+F(r['time_high'])),
                                       -r['queries'], -('C','LD','STOP').index(r['policy'])))
                  for rs in by_world.values()]
        upper = totals(choice)
        summary[split] = dict(fixed=fixed, finite_three_tail_oracle=upper,
                              oracle_task_gap_to_best_fixed=upper['tasks']-max(x['tasks'] for x in fixed.values()),
                              selected_options=dict(Counter(r['policy'] for r in choice)))
    result = dict(passed=True, STOP_episodes=len(receipts), raw_trajectories_checked=len(all_rows),
                  CAL_native_subset_only=True, CAL_semantic_aliases_audited_in='QUERY_CAL_MODEL_INDEPENDENT.json',
                  old_TEST_traces_read=0, negative_controls_rejected=negative_rejected,
                  outcomes=all_rows, pairs=paired, summary=summary, receipt_pins=pins,
                  scope='TRAIN/CAL development; paired budgets within families; query counts not production cost; '
                        'time is fixed first-four-task restricted completion sum; oracle is retrospective only; '
                        'CAL summary here covers only the 3 native B8 tails, not the full 6-context CAL; '
                        'no new solver or simulation calls; physical geometry audited separately')
    (HERE/'QUERY_INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':True,'STOP_episodes':len(receipts),'summary':summary},indent=2))


if __name__ == '__main__':
    main()
