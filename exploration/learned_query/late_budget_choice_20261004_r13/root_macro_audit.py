"""Independent raw macro/selection/value audit; no candidate-module imports."""
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import argparse
import hashlib
import json

P = Path(__file__).resolve().parent
OPTIONS = ['C', 'LD']
LEARNED = {'full', 'no_history_prob'}
BUDGET_SLOTS = {20, 22, 23}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def bounds(at):
    return F(at['lower'], at['denominator']), F(at['upper'], at['denominator'])


def condition(c):
    return sum((F(c['probability']) / (v['remaining_route_items'] * v['owners'])
                for v in c['claims']), F(0))


def top(candidates):
    return min(candidates, key=lambda c: (-condition(c), c['agent'], c['move']))


def coefficients(text):
    out = defaultdict(list)
    for line in text.splitlines():
        fields = line.split()
        if fields[0] == 'M':
            assert len(fields) == 4
            out[fields[1]].append(F(int(fields[2]), int(fields[3])))
    return dict(out)


def check_gate(gate, decision, policy, budget, params, n):
    assert gate['opportunity'] == decision['opportunity']
    assert gate['at'] == decision['at']
    assert gate['policy'] == policy and gate['initial_capacity'] == budget
    candidates = decision['candidates']; target = top(candidates)
    remaining = decision['remaining_capacity']
    assert 0 < remaining <= budget - budget // 2
    assert gate['remaining_capacity'] == remaining and gate['spent'] == budget - remaining
    assert (gate['target_agent'], gate['target_move']) == (target['agent'], target['move'])
    assert gate['feature_schema'] == 'late_target10_v1' and n == 16
    f = list(map(F, target['features'])); claims = target['claims']
    inverse = sum((F(1, c['remaining_route_items'] * c['owners']) for c in claims), F(0))
    assert f[10] == F(target['probability'])
    features = [f[10], f[0], f[18], inverse, F(min(c['remaining_route_items'] for c in claims), 64),
                F(len(claims), 15), F(len(candidates) - 1, 15), F(remaining, 16), 1 - f[21], f[10] * inverse]
    assert features == list(map(F, gate['features']))
    scores = [{'option': k, 'tasks': F(0), 'time': F(0), 'total': F(0)} for k in OPTIONS]
    margin, infinite, chosen = F(0), False, 'C'
    if policy in LEARNED:
        threshold = params['shared_margin']
        assert len(threshold) == 2 and threshold[0] in {F(0), F(1)} and threshold[1] >= 0
        infinite, margin = bool(threshold[0]), threshold[1]
        masked = {0, 9} if policy == 'no_history_prob' else set()
        for head in ['tasks', 'time']:
            coefs = params[policy + '_LD_' + head]
            assert len(coefs) == 11 and all(coefs[i + 1] == 0 for i in masked)
            scores[1][head] = coefs[0] + sum((coefs[i + 1] * x for i, x in enumerate(features) if i not in masked), F(0))
        scores[1]['total'] = scores[1]['tasks'] + scores[1]['time']
        if not infinite and scores[1]['total'] > margin: chosen = 'LD'
    elif policy in {'alwaysLD', 'macro_LD'}: chosen = 'LD'
    elif policy == 'budget_lookup':
        value = params['budget_lookup_' + str(budget)]
        assert len(value) == 1 and value[0] in {F(0), F(1)}
        chosen = OPTIONS[int(value[0])]
    else: assert policy in {'condition', 'macro_C'}
    assert gate['selected_option'] == chosen
    assert gate['learned'] == (policy in LEARNED)
    assert gate['inference_calls'] == int(policy in LEARNED)
    assert gate['inference_ns'] >= 0
    if policy not in LEARNED: assert gate['inference_ns'] == 0
    assert gate['margin_infinite'] == infinite and F(gate['margin']) == margin
    assert len(gate['scores']) == 2
    for expected, actual in zip(scores, gate['scores']):
        assert expected['option'] == actual['option']
        assert all(expected[k] == F(actual[k]) for k in ['tasks', 'time', 'total'])
    return chosen, features


def audit(world, receipt_path):
    receipt = json.loads(receipt_path.read_text())
    assert receipt['error'] is None and receipt['world'] == world['name']
    budget, policy = world['budget'], receipt['policy']
    assert receipt['capacity'] == budget and budget in {8, 16}
    raw = Path(receipt['raw']).read_bytes()
    inp = Path(receipt['input']).read_bytes()
    assert digest(raw) == receipt['raw_sha256'] and digest(inp) == receipt['input_sha256']
    params = coefficients(inp.decode())
    robots = {r['agent']: r for r in world['robots']}
    heads = {a: r['tasks'][0]['task'] for a, r in robots.items()}
    head_indices = {a: 0 for a in robots}
    services, parent, last_end = {}, {}, {}
    queried, skipped, end_seen = set(), set(), set()
    gate, features, macro, anchor = None, None, 'W' if policy == 'WAIT' else '', None
    gate_checked = False
    stage, decisions, interventions, skips = 0, 0, [], 0
    prefix_hash, control_hash = hashlib.sha256(), hashlib.sha256()
    for line in raw.splitlines():
        e = json.loads(line)
        kind = e['event']
        if kind != 'macro_choice':
            normalized = dict(e)
            normalized.pop('policy', None)
            if kind == 'joint_summary':
                # Coefficient validation adds implementation checks even when
                # the learned selector chooses the identical physical macro.
                normalized.pop('native_checks', None)
            normalized_line = json.dumps(normalized, sort_keys=True, separators=(',', ':')).encode() + b'\n'
            control_hash.update(normalized_line)
            if gate is None:
                prefix_hash.update(normalized_line)
        if kind == 'macro_choice':
            assert gate is None and policy != 'WAIT' and budget // 2 <= len(queried) < budget
            gate = e
        elif kind == 'task_service':
            a, task = e['agent'], e['task']
            assert heads[a] == task and task not in services
            assert e['original_endpoint_at_rest'] and e['physical_footprint_inside_service_square']
            services[task] = bounds(e['at'])
        elif kind == 'public_END_delivered':
            identity = e['agent'], e['move']
            assert identity not in end_seen
            end_seen.add(identity)
            last_end[e['agent']] = e['at']
            skipped.discard(identity)
        elif kind == 'public_head_revealed':
            a, task = e['agent'], e['task']
            assert e['previous_service_and_END'] and heads[a] in services and last_end[a] == e['at']
            head_indices[a] += 1
            assert robots[a]['tasks'][head_indices[a]]['task'] == task and task not in parent
            parent[task] = heads[a]
            heads[a] = task
        elif kind == 'actor_decision':
            if not gate_checked and policy != 'WAIT':
                eligible_gate = budget // 2 <= len(queried) < budget
                assert (gate is not None) == eligible_gate, 'Gate is not at first legal late opportunity'
                if eligible_gate:
                    macro, features = check_gate(gate, e, policy, budget, params, world['N'])
                    gate_checked = True
            decisions += 1
            assert e['opportunity'] == decisions and e['policy'] == policy
            assert e['macro'] == macro and e['initial_capacity'] == budget
            assert e['remaining_capacity'] == budget - len(queried)
            assert e['head_lineage_count'] == len(parent)
            assert not any(e[k] for k in ['private_progress_input', 'regime_input', 'future_head_input'])
            candidates = e['candidates']
            assert candidates
            for c in candidates:
                identity = c['agent'], c['move']
                assert identity not in skipped and identity not in queried
                assert all(cl['task'] in heads.values() for cl in c['claims'])
            index, eligible, target = 0, [], None
            if stage == 0 and macro == 'LD' and e['remaining_capacity'] > 0:
                if len(queried) >= budget // 2:
                    target = top(candidates)
                    stage = index = 1
                    anchor = target['agent'], target['move'], {cl['task'] for cl in target['claims']}
            elif stage == 1 and macro == 'LD' and e['remaining_capacity'] > 0:
                eligible = [c for c in candidates if (c['agent'], c['move']) != anchor[:2]]
                if eligible:
                    target = top(eligible)
                    stage = index = 2
            mode = 'force_SKIP' + str(target['agent']) if target else 'WAIT' if macro == 'W' else 'condition'
            assert e['decision_mode'] == mode
            assert e['pair_stage'] == stage and e['intervention_index'] == index
            assert e['second_eligible'] == [c['move'] for c in eligible]
            if anchor:
                assert (e['anchor_agent'], e['anchor_move'], set(e['anchor_tasks'])) == anchor
            else:
                assert e['anchor_agent'] == 1000 and e['anchor_move'] == '' and e['anchor_tasks'] == []
            choices = []
            for c in candidates:
                query_score = condition(c) if mode == 'condition' else F(0)
                skip_score = F(int(target is not None and c['agent'] == target['agent']))
                assert F(c['score']) == query_score and F(c['skip_score']) == skip_score
                for rank, kind_action, score in [(0, 'QUERY', query_score), (1, 'SKIP', skip_score)]:
                    if score > 0 and e['remaining_capacity'] > 0:
                        choices.append((-score, rank, c['agent'], c['move'], kind_action))
            choice = min(choices) if choices else None
            assert (e['selected_kind'], e['selected']) == ((choice[-1], choice[3]) if choice else ('WAIT', ''))
            if choice:
                identity = choice[2], choice[3]
                if choice[-1] == 'QUERY':
                    queried.add(identity)
                else:
                    assert identity not in skipped
                    skipped.add(identity)
                    skips += 1
            if index:
                interventions.append({'index': index, 'opportunity': e['opportunity'], 'at': e['at'],
                                      'remaining': e['remaining_capacity'], 'agent': target['agent'], 'move': target['move']})
    assert (gate is not None) == gate_checked
    assert policy != 'WAIT' or gate is None
    assert len(queried) <= budget
    assert len(queried) == receipt['summary']['queries'] and len(services) == receipt['summary']['served']
    fixed = [t['task'] for r in world['robots'] for t in r['tasks'][:4]]
    low = sum((services.get(t, (F(world['horizon']),) * 2)[0] for t in fixed), F(0))
    high = sum((services.get(t, (F(world['horizon']),) * 2)[1] for t in fixed), F(0))
    return {'world': world['name'], 'family': world.get('family_key', world.get('family', world['name'])),
            'split': world['split'], 'budget': budget, 'policy': policy, 'macro': macro or 'C',
            'tasks': len(services), 'time_low': str(low), 'time_high': str(high),
            'queries': len(queried), 'decisions': decisions, 'skips': skips,
            'interventions': interventions, 'gate': gate, 'features': list(map(str, features)) if features else None,
            'prefix_sha256': prefix_hash.hexdigest(), 'control_sha256': control_hash.hexdigest(),
            'service_sha256': digest(json.dumps([(task, str(v[0]), str(v[1])) for task, v in sorted(services.items())]).encode()),
            'queried_occurrences_sha256': digest(json.dumps(sorted(queried)).encode()),
            'raw_sha256': receipt['raw_sha256']}


def cross_checks(rows):
    same_world, families, same_macro = defaultdict(list), defaultdict(list), defaultdict(list)
    for r in rows:
        if r['policy'] != 'WAIT': same_world[r['world']].append(r)
        families[r['family']].append(r)
        same_macro[r['world'], r['macro']].append(r)
    for key, group in same_world.items():
        assert len({r['prefix_sha256'] for r in group}) == 1, ('prefix', key)
        assert len({tuple(r['features']) if r['features'] else None for r in group}) == 1, ('features', key)
    for key, group in same_macro.items():
        assert len({r['control_sha256'] for r in group}) == 1, ('same-macro trace', key)
    return {'world_groups': len(same_world), 'family_groups': len(families),
            'same_macro_groups_with_controls': sum(len(g) > 1 for g in same_macro.values()),
            'nonWAIT_pregate_prefixes_match': True, 'same_macro_full_trajectories_match': True,
            'cross_budget_prefix_equality_required': False}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--partial', action='store_true')
    args = parser.parse_args()
    reg = json.loads((P / 'REGISTRATION.json').read_text())
    worlds = {w['name']: w for w in reg['worlds']}
    receipts = sorted((P / 'runs').glob('*.receipt.json'))
    rows = []
    for receipt in receipts:
        data = json.loads(receipt.read_text())
        rows.append(audit(worlds[data['world']], receipt))
        if len(rows) % 12 == 0:
            print(len(rows), 'raw runs checked', flush=True)
    expected = {(w['name'], policy) for w in worlds.values()
                for policy in (['macro_' + k for k in OPTIONS] if w['split'] in {'train', 'calibration'}
                               else ['WAIT', 'condition', 'alwaysLD', 'budget_lookup', 'full', 'no_history_prob'])}
    actual = {(r['world'], r['policy']) for r in rows}
    assert actual <= expected and len(actual) == len(rows)
    if not args.partial:
        assert actual == expected and len(rows) == 160
    checked = cross_checks(rows)
    if not args.partial:
        assert checked['world_groups'] == 48 and checked['family_groups'] == 24
    report = {'passed': True, 'partial': args.partial, 'candidate_imports': False,
              'expected_runs': len(expected), 'observed_runs': len(rows), 'cross_checks': cross_checks(rows),
              'trajectory_normalization': 'Exclude macro_choice, policy labels and joint_summary.native_checks only. Model validation changes that implementation counter; all physical/control/service fields remain.',
              'auditor_sha256': digest(Path(__file__).read_bytes()), 'rows': rows}
    name = 'ROOT_MACRO_PARTIAL.json' if args.partial else 'ROOT_MACRO_AUDIT.json'
    (P / name).write_text(json.dumps(report, indent=2) + '\n')
    print(name, 'PASS', len(rows), flush=True)


if __name__ == '__main__':
    main()
