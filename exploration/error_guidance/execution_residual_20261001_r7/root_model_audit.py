"""Root's independent event reconstruction and augmented-least-squares refit.

Does not import the experiment's history builder, predictor or fitting code.
Raw events and the declared feature specification are the only inputs to the
reconstruction. This checks implementation consistency, not external validity.
"""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import math
import numpy as np

HERE = Path(__file__).resolve().parent
RAW = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence') / HERE.name


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct(root):
    expected = json.loads((root / 'supervised_rows.json').read_text())
    by_id = {(r['proposal_id'], r['agent']): r for r in expected['rows'] + expected['censored']}
    completed, proposed, node_map = [], {}, {}
    history = defaultdict(list)
    last_sequence = -1
    inst, pid = None, None
    count = 0
    with (root / 'public_events.jsonl').open() as stream:
        for line in stream:
            event = json.loads(line)
            assert event['sequence'] > last_sequence
            last_sequence = event['sequence']
            kind = event['kind']
            count += 1
            if kind == 'view':
                inst = event['view']['mapf_instance']
            elif kind == 'proposal':
                pid = event['proposal']['proposal_id']
                for a, (start, end) in enumerate(event['proposal']['plan']):
                    dy, dx = end[0] - start[0], end[1] - start[1]
                    if (dy, dx) == (0, 0):
                        continue
                    direction = [(0, 1), (1, 0), (0, -1), (-1, 0)].index((dy, dx))
                    d = (direction - inst['starts'][a]['orientation']) % 4
                    turns = min(d, 4 - d)
                    past = history[a][-16:]
                    assert all(x['end_sequence'] < event['sequence'] for x in past)
                    residual = [x['duration'] - 45 - 10*x['turns'] for x in past]
                    directional = [x['duration'] - 45 - 10*x['turns'] for x in past if x['direction'] == direction][-8:]
                    feats = [turns/2, *[float(direction == k) for k in range(4)], len(past)/16,
                             (float(np.mean(residual))/50 if residual else 0.),
                             sum(directional)/(len(directional)+2)/50,
                             (residual[-1]/50 if residual else 0.),
                             (float(np.std(residual))/50 if residual else 0.)]
                    row = dict(proposal_id=pid, agent=a, direction=direction, turns=turns,
                               proposal_tick=event['tick'], goal=[end[1], end[0]], features=feats,
                               history_cutoff_sequence=event['sequence'], duration=None, final_node=None)
                    assert (pid, a) not in proposed
                    proposed[(pid, a)] = row
            elif kind == 'admit':
                a = int(event['robot'])
                row = proposed.get((pid, a))
                if row is not None:
                    matches = [action for action in event['actions'] if action[3] == 'M' and action[5] == row['goal']]
                    # ADG admission may dispatch an earlier chunk (e.g. turn)
                    # before it admits the final MOVE half.
                    assert len(matches) <= 1
                    if not matches:
                        continue
                    row['final_node'] = matches[0][1]
                    assert (a, row['final_node']) not in node_map
                    node_map[(a, row['final_node'])] = row
            elif kind == 'end':
                row = node_map.get((int(event['robot']), event['node']))
                if row is not None:
                    assert event['accepted'] is True and row['duration'] is None
                    row['duration'] = event['tick'] - row['proposal_tick']
                    row['end_tick'], row['end_sequence'] = event['tick'], event['sequence']
                    assert row['duration'] > 0
                    history[row['agent']].append(row)
                    completed.append(row)
            else:
                raise AssertionError('Non-public event in actor projection: ' + kind)
    assert set(by_id) == set(proposed)
    for key, row in proposed.items():
        want = by_id[key]
        assert set(row) == set(want)
        for name in row:
            if name == 'features':
                assert np.allclose(row[name], want[name], atol=1e-12, rtol=0)
            else:
                assert row[name] == want[name], (root.name, key, name)
    assert len(completed) == len(expected['rows'])
    assert [(r['proposal_id'], r['agent']) for r in completed] == [(r['proposal_id'], r['agent']) for r in expected['rows']]
    return completed, dict(events=count, completed=len(completed), censored=len(proposed)-len(completed),
                           public_events_sha256=digest(root/'public_events.jsonl'))


def main():
    checkpoint = json.loads((HERE/'model_freeze.json').read_text())
    assert checkpoint['test_seen'] is False
    parts = defaultdict(list)
    audits, seeds = {}, defaultdict(set)
    for spec in json.loads((HERE/'runs.json').read_text())['runs']:
        seeds[spec['split']].add(spec['seed'])
        if spec['split'] == 'test':
            continue
        root = RAW/'runs'/spec['id']
        assert digest(root/'supervised_rows.json') == checkpoint['source_pins'][str(root/'supervised_rows.json')]
        rows, audit = reconstruct(root)
        audits[spec['id']] = audit
        parts[spec['split']].extend(rows)
    assert not (seeds['train'] & seeds['calibration'] or seeds['train'] & seeds['test'] or seeds['calibration'] & seeds['test'])
    x = np.array([r['features'] for r in parts['train']])
    y = np.array([r['duration']-45-10*r['turns'] for r in parts['train']])
    mean, scale = x.mean(0), x.std(0)
    scale[scale < 1e-12] = 1.
    z = np.column_stack((np.ones(len(x)), (x-mean)/scale))
    penalty = np.eye(z.shape[1]); penalty[0, 0] = 0.
    beta = np.linalg.lstsq(np.vstack((z, penalty)), np.concatenate((y, np.zeros(z.shape[1]))), rcond=None)[0]
    frozen = checkpoint['ridge']
    assert frozen['lambda'] == 1.
    assert np.allclose(mean, frozen['mean'], atol=1e-12, rtol=0)
    assert np.allclose(scale, frozen['scale'], atol=1e-12, rtol=0)
    delta = float(np.max(np.abs(beta - np.array([frozen['intercept'], *frozen['coef']]))))
    assert delta < 1e-8
    calibration = {}
    for policy in ('history', 'learned'):
        errors = []
        for row in parts['calibration']:
            features = np.array(row['features'])
            residual = features[7]*50 if policy == 'history' else beta[0] + ((features-mean)/scale)@beta[1:]
            prediction = np.clip(45+10*row['turns']+residual, 5, 200)
            errors.append(abs(prediction-row['duration']))
        rank = min(len(errors), math.ceil(.9*(len(errors)+1)))
        value = dict(rows=len(errors), rank=rank, q90_absolute_error=sorted(errors)[rank-1],
                     MAE=float(np.mean(errors)), RMSE=float(np.sqrt(np.mean(np.square(errors)))))
        for key, v in value.items():
            assert abs(v-checkpoint['calibration'][policy][key]) < 1e-8
        calibration[policy] = value
    result = dict(status='PASS', scope='Independent root event reconstruction + augmented least-squares solver; no experiment-module imports',
                  model_sha256=digest(HERE/'model_freeze.json'), script_sha256=digest(Path(__file__)),
                  train_rows=len(parts['train']), calibration_rows=len(parts['calibration']),
                  censored=sum(a['censored'] for a in audits.values()), max_coefficient_difference=delta,
                  seeds={k: sorted(v) for k,v in seeds.items()}, calibration=calibration, runs=audits)
    (HERE/'ROOT_MODEL_AUDIT.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k != 'runs'}))


if __name__ == '__main__':
    main()
