"""Root audit: public two-step selection and task headroom on all registered runs.

No candidate imports, training, extra simulations, or TEST selection. Reported
best branches are a finite retrospective bound, not a deployed oracle policy.
"""
from collections import defaultdict
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parent


def bound(x):
    return F(x['lower'], x['denominator']), F(x['upper'], x['denominator'])


def condition_score(c):
    return sum((F(c['probability']) / (cl['remaining_route_items'] * cl['owners']) for cl in c['claims']), F(0))


def ranked(candidates):
    return min(candidates, key=lambda c: (-condition_score(c), c['agent'], c['move']))


def read_run(world, policy):
    receipt = json.loads((P / 'runs' / (world['name'] + '__' + policy + '.receipt.json')).read_text())
    assert receipt['error'] is None
    raw = Path(receipt['raw']).read_bytes()
    assert hashlib.sha256(raw).hexdigest() == receipt['raw_sha256']
    heads = {r['agent']: r['tasks'][0]['task'] for r in world['robots']}
    parent, services, last_end, skipped, queried = {}, {}, {}, set(), set()
    decisions, replacements = [], []
    pair = policy.split('_') if policy.startswith('pair_') else None
    anchor = None
    stage = 0
    for line in raw.splitlines():
        e = json.loads(line)
        kind = e['event']
        if kind == 'task_service':
            assert e['task'] not in services and heads[e['agent']] == e['task']
            assert e['original_endpoint_at_rest'] and e['physical_footprint_inside_service_square']
            services[e['task']] = bound(e['at'])
        elif kind == 'public_END_delivered':
            last_end[e['agent']] = e['at']
            skipped.discard((e['agent'], e['move']))
        elif kind == 'public_head_revealed':
            a, task = e['agent'], e['task']
            assert e['previous_service_and_END'] and heads[a] in services and last_end[a] == e['at']
            assert task not in parent
            parent[task] = heads[a]; heads[a] = task
        elif kind == 'actor_decision':
            assert e['policy'] == policy
            assert e['remaining_capacity'] == 16 - len(queried)
            assert not any(e[k] for k in ['private_progress_input', 'regime_input', 'future_head_input'])
            assert e['head_lineage_count'] == len(parent)
            for c in e['candidates']:
                assert (c['agent'], c['move']) not in skipped
                assert all(cl['task'] in heads.values() for cl in c['claims'])
            if pair:
                expected_index, eligible = 0, []
                if stage == 0 and e['opportunity'] == int(pair[1]):
                    first = ranked(e['candidates'])
                    first_agent = int(''.join(x for x in pair[2] if x.isdigit()))
                    assert first['agent'] == first_agent
                    anchor = {'agent': first_agent, 'move': first['move'], 'tasks': {cl['task'] for cl in first['claims']}}
                    stage = 1; expected_index = 1
                    first_kind = ''.join(x for x in pair[2] if not x.isdigit())
                    assert e['selected_kind'] == first_kind
                    assert e['selected'] == ('' if first_kind == 'WAIT' else first['move'])
                elif stage == 1 and e['opportunity'] > int(pair[1]) and e['remaining_capacity'] > 0:
                    def descendant(task):
                        visited = set()
                        while task in parent:
                            assert task not in visited
                            visited.add(task); task = parent[task]
                            if task in anchor['tasks']:
                                return True
                        return False
                    eligible = [c for c in e['candidates'] if (c['agent'], c['move']) != (anchor['agent'], anchor['move'])
                                and (pair[4] == 'distinct' or any(descendant(cl['task']) for cl in c['claims']))]
                    if eligible:
                        chosen = ranked(eligible)
                        assert e['selected_kind'] == pair[3] and e['selected'] == chosen['move']
                        stage = 2; expected_index = 2
                assert e['intervention_index'] == expected_index and e['pair_stage'] == stage
                if expected_index == 0:
                    assert e['decision_mode'] == 'condition'
                assert e['second_eligible'] == [c['move'] for c in eligible]
                if anchor:
                    assert (e['anchor_agent'], e['anchor_move'], set(e['anchor_tasks'])) == (anchor['agent'], anchor['move'], anchor['tasks'])
                if expected_index:
                    replacements.append(e)
            choices = []
            for c in e['candidates']:
                mode = e['decision_mode']
                if mode == 'condition':
                    assert F(c['score']) == condition_score(c) and F(c['skip_score']) == 0
                elif mode.startswith('force_'):
                    action = mode[6:]
                    assert F(c['score']) == int(action == 'QUERY' + str(c['agent']))
                    assert F(c['skip_score']) == int(action == 'SKIP' + str(c['agent']))
                else:
                    assert mode == 'WAIT' and F(c['score']) == F(c['skip_score']) == 0
                for index, name, score in [(0, 'QUERY', F(c['score'])), (1, 'SKIP', F(c['skip_score']))]:
                    if score > 0 and e['remaining_capacity'] > 0:
                        choices.append((-score, index, c['agent'], c['move'], name))
            choice = min(choices) if choices else None
            assert (e['selected_kind'], e['selected']) == ((choice[-1], choice[3]) if choice else ('WAIT', ''))
            if choice:
                identity = choice[2], choice[3]
                if choice[-1] == 'QUERY':
                    assert identity not in queried
                    queried.add(identity)
                else:
                    assert identity not in skipped
                    skipped.add(identity)
            decisions.append(e)
    assert len(services) == receipt['summary']['served'] and len(queried) == receipt['summary']['queries']
    fixed = {t['task'] for r in world['robots'] for t in r['tasks'][:4]}
    low = sum((services.get(t, (F(world['horizon']),) * 2)[0] for t in fixed), F(0))
    high = sum((services.get(t, (F(world['horizon']),) * 2)[1] for t in fixed), F(0))
    if pair:
        assert [e['intervention_index'] for e in replacements] in [[1], [1, 2]]
    return {'policy': policy, 'tasks': len(services), 'fifo_low': str(low), 'fifo_high': str(high),
            'queries': len(queried), 'pair_replacements': len(replacements), 'second_reached': stage == 2,
            'raw_sha256': receipt['raw_sha256'], 'decisions': decisions}


def delta(out, baseline):
    tasks = out['tasks'] - baseline['tasks']
    low = F(baseline['fifo_low']) - F(out['fifo_high'])
    high = F(baseline['fifo_high']) - F(out['fifo_low'])
    return {'tasks': tasks, 'fifo_saving_low': str(low), 'fifo_saving_high': str(high),
            'J_saving_low': str(tasks + low / 16385), 'J_saving_high': str(tasks + high / 16385),
            'robust_J_improvement': tasks + low / 16385 > 0}


def best(outcomes):
    return min(outcomes, key=lambda x: (-x['tasks'], (F(x['fifo_low']) + F(x['fifo_high'])) / 2, x['policy']))


def main():
    registration = json.loads((P / 'REGISTRATION.json').read_text())
    branches = json.loads((P / 'BRANCHES_BEFORE_OUTCOMES.json').read_text())
    final = json.loads((P / 'RECEIPT.json').read_text())
    assert final['complete'] and final['failed'] == 0 and final['native_episodes'] <= 140
    expected = {(w['name'], p) for w in registration['worlds'] for p in ['condition', 'WAIT']}
    expected |= {(r['world'], r['policy']) for r in branches['jobs']}
    assert len(expected) == final['native_episodes']
    rows, opportunities, pair_effects, families, selection = [], [], [], [], []
    for w in registration['worlds']:
        outcomes = {p: read_run(w, p) for name, p in sorted(expected) if name == w['name']}
        condition, wait = outcomes['condition'], outcomes['WAIT']
        # Independently reconstruct public stratum coverage and the complete branch cap.
        seen, selected, spent = set(), [], 0
        for d in condition['decisions']:
            if d['remaining_capacity'] <= 0:
                continue
            coupled = any(len({cl['task'] for cl in c['claims']}) > 1 or any(cl['owners'] > 1 for cl in c['claims']) for c in d['candidates'])
            key = (16 - d['remaining_capacity'] >= 8, coupled)
            if key in seen:
                continue
            seen.add(key)
            cost = 1 + 2 * len(d['candidates'])
            if spent + cost <= 18:
                spent += cost; selected.append(d)
        recorded = next(r for r in branches['coverage'] if r['world'] == w['name'])
        assert [d['opportunity'] for d in selected] == recorded['selected_opportunities']
        expected_singles = set()
        for d in selected:
            policies = ['cf_' + str(d['opportunity']) + '_' + action for action in ['WAIT'] + [kind + str(c['agent']) for c in d['candidates'] for kind in ['QUERY', 'SKIP']]]
            expected_singles.update(policies)
            winner = best([outcomes[p] for p in policies])
            assert winner['tasks'] >= condition['tasks']
            opportunities.append({'world': w['name'], 'opportunity': d['opportunity'], 'candidates': len(d['candidates']),
                                  'best_policy': winner['policy'], 'vs_pi0': delta(winner, condition), 'vs_whole_WAIT': delta(winner, wait)})
        assert expected_singles == {p for p in outcomes if p.startswith('cf_')}
        for p, out in outcomes.items():
            if p.startswith('pair_'):
                fields = p.split('_')
                first_action = 'WAIT' if fields[2].startswith('WAIT') else fields[2]
                single = outcomes['cf_' + fields[1] + '_' + first_action]
                pair_effects.append({'world': w['name'], 'policy': p, 'second_reached': out['second_reached'],
                                    'vs_same_first_single': delta(out, single), 'vs_pi0': delta(out, condition), 'vs_whole_WAIT': delta(out, wait)})
                if not out['second_reached']:
                    assert (out['tasks'], out['fifo_low'], out['fifo_high'], out['queries']) == (single['tasks'], single['fifo_low'], single['fifo_high'], single['queries'])
            compact = {k: v for k, v in out.items() if k != 'decisions'}
            rows.append({'world': w['name'], **compact, 'vs_pi0': delta(out, condition), 'vs_whole_WAIT': delta(out, wait)})
        winner = best(list(outcomes.values()))
        families.append({'world': w['name'], 'pi0_tasks': condition['tasks'], 'WAIT_tasks': wait['tasks'],
                         'best_registered_policy': winner['policy'], 'best_registered_tasks': winner['tasks'],
                         'best_vs_pi0': delta(winner, condition), 'best_vs_whole_WAIT': delta(winner, wait)})
        selection.append({'world': w['name'], 'public_strata_observed': len(seen), 'selected_opportunities': len(selected), 'complete_single_branches': spent})
        print(w['name'], 'PASS', len(outcomes), 'pi0/WAIT/best', condition['tasks'], wait['tasks'], winner['tasks'], flush=True)
    report = {'passed': True, 'candidate_imports': False, 'TRAIN_only': True, 'runs': len(rows), 'families': families,
              'selection': selection, 'single_opportunities': opportunities, 'pair_effects': pair_effects, 'all_runs': rows,
              'single_task_improvable_over_pi0': sum(r['vs_pi0']['tasks'] > 0 for r in opportunities),
              'pair_task_gain_over_same_first': sum(r['vs_same_first_single']['tasks'] > 0 for r in pair_effects),
              'robust_J_probe_gains_over_both': sum(r['policy'] not in ['condition', 'WAIT'] and r['vs_pi0']['robust_J_improvement'] and r['vs_whole_WAIT']['robust_J_improvement'] for r in rows),
              'retrospective_task_totals': {
                  'pi0': sum(r['pi0_tasks'] for r in families),
                  'whole_WAIT': sum(r['WAIT_tasks'] for r in families),
                  'best_finite_registered_per_family': sum(r['best_registered_tasks'] for r in families),
                  'per_family_reference_envelope': sum(max(r['pi0_tasks'], r['WAIT_tasks']) for r in families),
                  'note': 'Per-family hindsight choices are not a deployed selector; envelope equality does not rule out learning which reference to use.'},
              'second_reached': sum(r['second_reached'] for r in pair_effects),
              'scope': 'All preregistered finite TRAIN policies; raw services, interval FIFO bounds, public head lineage, legal distinct/successor second targets, budget/skip/tie selection. Best choices are retrospective diagnostic bounds, not deployed policy or TEST gains.'}
    (P / 'ROOT_VALUE_SPACE.json').write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
