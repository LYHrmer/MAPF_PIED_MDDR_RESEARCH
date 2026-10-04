"""Post-hoc interpretation of frozen heads; no retraining or additional native arms."""
from fractions import Fraction as F
from collections import Counter
from pathlib import Path
import hashlib, json

P = Path(__file__).resolve().parent

def main():
    audit = json.loads((P / 'ROOT_MACRO_AUDIT.json').read_text())
    model = json.loads((P / 'MODELS_FROZEN_BEFORE_TEST.json').read_text())
    assert audit['passed'] and not audit['partial']
    worlds = {}
    for row in audit['rows']: worlds.setdefault(row['world'], {})[row['policy']] = row
    training = {}
    for split in ['train', 'calibration']:
        values = []
        for group in worlds.values():
            if next(iter(group.values()))['split'] != split: continue
            c, d = group['macro_C'], group['macro_LD']
            values.append({'world': c['world'], 'has_gate': c['gate'] is not None,
                           'task_gain': d['tasks'] - c['tasks'],
                           'time_gain_low': str(F(c['time_low']) - F(d['time_high'])),
                           'time_gain_high': str(F(c['time_high']) - F(d['time_low']))})
        training[split] = {'rows': values,
                           'task_signs': dict(Counter('positive' if r['task_gain'] > 0 else 'negative' if r['task_gain'] < 0 else 'zero' for r in values))}
    decisions = []
    for group in worlds.values():
        if next(iter(group.values()))['split'] != 'test': continue
        for variant in ['full', 'no_history_prob']:
            row = group[variant]; gate = row['gate']
            if gate is None: continue
            score = gate['scores'][1]
            tasks_only_choice = 'LD' if not gate['margin_infinite'] and F(score['tasks']) > F(gate['margin']) else 'C'
            decisions.append({'world': row['world'], 'family': row['family'], 'budget': row['budget'],
                              'variant': variant, 'actual_choice': row['macro'],
                              'task_score': score['tasks'], 'time_score': score['time'],
                              'fixed_threshold_task_score_only_choice': tasks_only_choice,
                              'choice_changed_by_time_term_at_fixed_model_and_threshold': tasks_only_choice != row['macro']})
    output = {'passed': True, 'post_hoc': True, 'new_native_runs': 0, 'model_changed': False,
              'scope': 'Frozen-score interpretation only. Removing a head without refitting/recalibrating is not a registered trained ablation or evidence that time information is generally useless.',
              'train_cal_complete_tail_labels': training, 'test_score_diagnostics': decisions,
              'model_sha256': hashlib.sha256((P / 'MODELS_FROZEN_BEFORE_TEST.json').read_bytes()).hexdigest(),
              'time_term_changed_choices': dict(Counter(r['variant'] for r in decisions if r['choice_changed_by_time_term_at_fixed_model_and_threshold']))}
    (P / 'ROOT_MODEL_DIAGNOSTICS.json').write_text(json.dumps(output, indent=2) + '\n')
    print('ROOT_MODEL_DIAGNOSTICS', output['time_term_changed_choices'])

if __name__ == '__main__': main()
