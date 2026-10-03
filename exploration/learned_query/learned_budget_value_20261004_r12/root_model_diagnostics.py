"""Descriptive signal/selection diagnostics; never fit or change the frozen model."""
from collections import Counter, defaultdict
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json

P = Path(__file__).resolve().parent
OPTIONS = ['C', 'W', 'E', 'L', 'ED', 'LD']
VARIANTS = ['full', 'nohistory', 'nobudget', 'tasks_only']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    model = json.loads((P / 'MODELS_FROZEN_BEFORE_TEST.json').read_text())
    labels = json.loads((P / 'TRAIN_CAL_LABELS.json').read_text())
    audit = json.loads((P / 'ROOT_MACRO_AUDIT.json').read_text())
    assert audit['passed'] and audit['observed_runs'] == 152 and not audit['partial']
    assert sha(P / 'TRAIN_CAL_LABELS.json') == model['labels_sha256']
    margin = model['calibration']['shared_margin']
    margin = None if margin is None else F(margin)
    contexts = defaultdict(dict)
    for row in labels:
        contexts[row['world']][row['option']] = row
    assert len(contexts) == 16
    signal = []
    for split in ['train', 'calibration']:
        for option in OPTIONS[1:]:
            rows = [r for r in labels if r['split'] == split and r['option'] == option]
            signal.append({'split': split, 'option': option, 'budget_contexts': len(rows),
                           'independent_families': len({r['family_key'] for r in rows}),
                           'task_gain_counts': dict(Counter(r['task_target'] for r in rows)),
                           'strict_time_gain_contexts': sum(F(r['T_gain_lower']) > 0 for r in rows),
                           'strict_time_loss_contexts': sum(F(r['T_gain_upper']) < 0 for r in rows)})
    choices = []
    errors = defaultdict(list)
    for world, options in sorted(contexts.items()):
        assert set(options) == set(OPTIONS)
        base = options['C']
        for variant in VARIANTS:
            source = 'full' if variant == 'tasks_only' else variant
            mask = set(range(10, 18)) if variant == 'nohistory' else {20, 22, 23} if variant == 'nobudget' else set()
            scores = {option: F(0) for option in OPTIONS}
            if base['features'] is not None:
                x = [F(1)] + [F(0) if j in mask else F(v) for j, v in enumerate(base['features'])]
                for option in OPTIONS[1:]:
                    for head in (['tasks'] if variant == 'tasks_only' else ['tasks', 'time']):
                        coefficients = list(map(F, model['models'][source + '_' + option + '_' + head]['coefficients']))
                        assert len(x) == len(coefficients) == 26
                        prediction = sum((a * b for a, b in zip(x, coefficients)), F(0))
                        scores[option] += prediction
                        target = F(options[option]['task_target' if head == 'tasks' else 'time_target'])
                        errors[base['split'], variant, head].append(abs(prediction - target))
            eligible = [o for o in OPTIONS[1:] if margin is not None and scores[o] > margin]
            selected = min(eligible, key=lambda o: (-scores[o], OPTIONS.index(o))) if eligible else 'C'
            score_winner = min(OPTIONS, key=lambda o: (-scores[o], OPTIONS.index(o)))
            actual = options[selected]
            choices.append({'world': world, 'split': base['split'], 'family': base['family_key'],
                            'budget': base['budget'], 'variant': variant, 'selected': selected,
                            'unthresholded_score_winner_diagnostic_only': score_winner,
                            'scores': {o: str(v) for o, v in scores.items()},
                            'actual_task_gain_vs_C': int(actual['task_target']),
                            'actual_time_gain_lower': actual['T_gain_lower'],
                            'actual_time_gain_upper': actual['T_gain_upper'],
                            'actual_queries': actual['queries'],
                            'hindsight_best_of_six_tasks_minus_selected': max(r['tasks'] for r in options.values()) - actual['tasks']})
    test = defaultdict(dict)
    for row in audit['rows']:
        if row['split'] == 'test':
            test[row['world']][row['policy']] = row
    comparisons = []
    for policy in ['nohistory', 'nobudget', 'tasks_only', 'budget_lookup']:
        cells = []
        for world, rows in sorted(test.items()):
            full, other = rows['full'], rows[policy]
            cells.append({'world': world, 'family': full['family'], 'budget': full['budget'],
                          'full_macro': full['macro'], 'comparison_macro': other['macro'],
                          'macro_differs': full['macro'] != other['macro'],
                          'tasks_full_minus_comparison': full['tasks'] - other['tasks'],
                          'time_saved_lower': str(F(other['time_low']) - F(full['time_high'])),
                          'time_saved_upper': str(F(other['time_high']) - F(full['time_low'])),
                          'same_service_records': full['service_sha256'] == other['service_sha256']})
        comparisons.append({'comparison': policy, 'macro_difference_contexts': sum(r['macro_differs'] for r in cells),
                            'task_gain': sum(r['tasks_full_minus_comparison'] for r in cells), 'cells': cells})
    train_gates = [r for r in labels if r['split'] == 'train' and r['option'] == 'C' and r['features'] is not None]
    report = {'passed': True, 'model_sha256': sha(P / 'MODELS_FROZEN_BEFORE_TEST.json'),
              'labels_sha256': sha(P / 'TRAIN_CAL_LABELS.json'), 'raw_audit_sha256': sha(P / 'ROOT_MACRO_AUDIT.json'),
              'script_sha256': sha(Path(__file__)), 'fitting_or_tuning_performed': False,
              'available_train_families': len({r['family_key'] for r in train_gates}),
              'available_train_budget_contexts': len(train_gates),
              'zero_task_heads': sum(all(F(c) == 0 for c in head['coefficients'])
                  for name, head in model['models'].items() if name.endswith('_tasks')),
              'shared_margin': model['calibration']['shared_margin'],
              'calibration_grid': [{k: row[k] for k in ['index', 'margin', 'tasks', 'T_lower', 'T_upper', 'queries']}
                  for row in model['calibration']['grid']],
              'nonconstant_train_feature_slots': [j for j in range(25) if len({F(r['features'][j]) for r in train_gates}) > 1],
              'signal': signal, 'train_cal_selections': choices,
              'train_cal_mean_absolute_errors': [{'split': k[0], 'variant': k[1], 'head': k[2],
                  'mean_absolute_error': str(sum(v, F(0)) / len(v))} for k, v in sorted(errors.items())],
              'test_full_vs_ablations': comparisons,
              'interpretation': 'TRAIN errors are fit diagnostics; CAL is used to choose a common margin. Neither is heldout evidence. Hindsight best-of-six is a restricted diagnostic, not a deployed policy or global optimal bound. TEST comprises four independent families, each repeated at two budgets. A nohistory selector retains history-based eligibility and the condition tail; nobudget retains hard budgets and macro semantics.'}
    (P / 'ROOT_MODEL_DIAGNOSTICS.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({'passed': True, 'test_comparisons': [{k: v for k, v in r.items() if k != 'cells'} for r in comparisons]}))


if __name__ == '__main__':
    main()
