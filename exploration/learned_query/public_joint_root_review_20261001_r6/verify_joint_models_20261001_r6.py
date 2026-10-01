"""Root refits by augmented least squares and replays exact held-out choices.

Independent of the package's normal-equation/model_audit implementation.
Reads saved native runs only; does not regenerate or select test worlds.
"""
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import numpy as np

BASE = Path('/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/public_joint_20261001_r6')
labels = json.loads((BASE/'TRAIN_CAL_LABELS.json').read_text())
models = json.loads((BASE/'MODELS.json').read_text())['models']
train = [r for r in labels if r['split'] == 'train']
assert len(train) == 12 and len(labels) == 16
fits = {}
for name, model in models.items():
    X = np.asarray([[1.] + [float(F(z)) if name == 'ridge_history' or j < 10 or j >= 18 else 0.
                            for j, z in enumerate(r['features'])] for r in train])
    y = np.asarray([float(F(r['target'])) for r in train])
    penalty = np.eye(21)[1:]
    coef, _, _, _ = np.linalg.lstsq(np.vstack([X, penalty]), np.concatenate([y, np.zeros(20)]), rcond=None)
    assert np.max(np.abs(coef - model['unrounded_coefficients'])) < 1e-12
    assert max(abs(F(round(float(c)*1e9), 10**9)-F(v)) for c, v in zip(coef, model['coefficients'])) == 0
    fits[name] = {'rows': len(train), 'parameters': len(coef), 'augmented_least_squares_refit': True}

causal_types = {'original_RUN', 'physical_original_END', 'public_END_delivered', 'task_service', 'public_head_revealed'}
traces, summaries, choices, scores = {}, {}, 0, 0
for path in sorted((BASE/'native_attempt_01').glob('group_0[45]__*.jsonl')):
    world, policy = path.stem.rsplit('__', 1)
    assert policy in {'WAIT', 'RR', 'condition', 'ridge_history', 'ridge_nohistory'}
    causal = []
    summary = None
    for line in path.open():
        if line.startswith('{"event":"world_frame_offline_only"'):
            continue
        row = json.loads(line)
        if row['event'] in causal_types:
            causal.append(row)
        elif row['event'] == 'joint_summary':
            summary = row
        elif row['event'] == 'actor_decision' and policy in models:
            coefficients = list(map(F, models[policy]['coefficients']))
            candidates = []
            for c in row['candidates']:
                fs = [F(z) if policy == 'ridge_history' or j < 10 or j >= 18 else F(0)
                      for j, z in enumerate(c['features'])]
                value = coefficients[0] + sum((a*b for a, b in zip(coefficients[1:], fs)), F(0))
                assert value == F(c['score'])
                if value > 0:
                    candidates.append((value, -c['agent'], c['move']))
                scores += 1
            expected = max(candidates)[2] if candidates and row['remaining_capacity'] else ''
            assert row['selected'] == expected
            assert not any(row[k] for k in ('private_progress_input', 'regime_input', 'future_head_input'))
            choices += 1
    assert summary and summary['status'] == 'passed'
    assert sum(r['event'] == 'task_service' for r in causal) == summary['served']
    traces[world, policy] = causal
    summaries[world, policy] = summary
assert len(summaries) == 40
equal_worlds = []
for world in sorted({w for w, _ in summaries}):
    if 'IID_' in world or 'SHIFT_' in world:
        assert traces[world, 'RR'] == traces[world, 'ridge_history'] == traces[world, 'ridge_nohistory']
        equal_worlds.append(world)
assert len(equal_worlds) == 6
totals = {p: {'served': sum(s['served'] for (w, q), s in summaries.items() if p == q),
              'queries': sum(s['queries'] for (w, q), s in summaries.items() if p == q)}
          for p in ('WAIT', 'RR', 'condition', 'ridge_history', 'ridge_nohistory')}
result = {'passed': True, 'model_sha256': hashlib.sha256((BASE/'MODELS.json').read_bytes()).hexdigest(),
          'refits': fits, 'heldout_native_runs': len(summaries), 'exact_model_choices': choices,
          'exact_candidate_scores': scores, 'IID_SHIFT_equal_causal_worlds': equal_worlds,
          'totals': totals, 'new_native_runs': 0,
          'scope': 'Saved training refit and logged public-feature choice/service replay; independent full geometry/history audit is separate.'}
out = Path(__file__).with_name('JOINT_MODELS_ROOT_20261001_R6.json')
out.write_text(json.dumps(result, indent=2)+'\n')
print(json.dumps(result, indent=2))
