"""Independent root reconstruction of counterfactual labels and model fit.

Does not import runner/pipeline/audit or production geometry/controller code.
Physical validity is a separate Decimal auditor's responsibility.
"""
from collections import Counter
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import numpy as np

HERE = Path(__file__).resolve().parent
OUT = HERE/'statistical_attempt_01'
sha = lambda p: hashlib.sha256(p.read_bytes()).hexdigest()


def read_run(world, policy):
    p = OUT/f'{world}__{policy}.jsonl'
    receipt = json.loads((OUT/f'{world}__{policy}.receipt.json').read_text())
    assert receipt['error'] is None and sha(p) == receipt['raw_sha256']
    rows = [json.loads(line) for line in p.open()]
    services = {r['task']: F(r['at']['lower']+r['at']['upper'], 2*r['at']['denominator'])
                for r in rows if r['event'] == 'task_service'}
    assert len(services) == sum(r['event'] == 'task_service' for r in rows) == receipt['summary']['served']
    assert rows[-1] == receipt['summary']
    return rows, services


def public_prefix(rows, stop):
    result = []
    for row in rows:
        r = json.loads(json.dumps(row))
        if r['event'] == 'actor_decision':
            for key in ('policy', 'remaining_capacity', 'selected'):
                del r[key]
            for c in r['candidates']:
                del c['score']
        result.append(r)
        if r['event'] == 'actor_decision' and r['opportunity'] == stop:
            return result
    raise AssertionError('Missing predeclared opportunity')


def main():
    registration = json.loads((OUT/'REGISTRATION.json').read_text())
    labels = json.loads((OUT/'TRAIN_CAL_LABELS.json').read_text())
    frozen = json.loads((OUT/'MODELS_FROZEN_BEFORE_TEST.json').read_text())
    assert frozen['labels_sha256'] == sha(OUT/'TRAIN_CAL_LABELS.json')
    assert not frozen['test_seen_before_freeze'] and not frozen['calibration_used_for_selection']
    worlds = {w['name']: w for w in registration['worlds']}
    wait = {name: read_run(name, 'WAIT') for name, w in worlds.items() if w['split'] != 'test'}
    expected_rows, effects = [], Counter()
    for name, (records, _) in wait.items():
        decisions = [r for r in records if r['event'] == 'actor_decision']
        selected = [r for r in decisions if len(r['candidates']) == 1][:2] + [r for r in decisions if len(r['candidates']) > 1][:2]
        expected_rows.extend((name, r['opportunity'], c['agent']) for r in selected for c in r['candidates'])
    assert sorted(expected_rows) == sorted((r['world'], r['opportunity'], r['source']) for r in labels)
    for row in labels:
        w = worlds[row['world']]
        wr, ws = wait[row['world']]
        pr, ps = read_run(row['world'], row['probe'])
        assert public_prefix(wr, row['opportunity']) == public_prefix(pr, row['opportunity'])
        decision = next(r for r in wr if r['event'] == 'actor_decision' and r['opportunity'] == row['opportunity'])
        candidate = next(c for c in decision['candidates'] if c['agent'] == row['source'])
        assert candidate['features'] == row['features'] and candidate['move'] == row['move']
        queries = [r for r in pr if r['event'] == 'actor_decision' and r['selected']]
        assert len(queries) == 1 and queries[0]['opportunity'] == row['opportunity'] and queries[0]['selected'] == row['move']
        tasks = {task['task'] for robot in w['robots'] for task in robot['tasks'][:4]}
        assert len(tasks) == 64
        gain = sum((ws.get(t,F(w['horizon']))-ps.get(t,F(w['horizon'])) for t in tasks), F(0))
        delta = len(ps)-len(ws)
        assert gain == F(row['fixed_first4_time_gain']) and delta == row['whole_service_gain']
        assert F(row['target']) == delta+gain/(128*16*4)
        effects['positive' if F(row['target'])>0 else 'negative' if F(row['target'])<0 else 'zero'] += 1
    train = [r for r in labels if r['split'] == 'train']
    fits = {}
    for name, model in frozen['models'].items():
        x = np.array([[1.] + [float(F(z)) if name == 'ridge_history' or i < 10 or i >= 18 else 0.
                              for i,z in enumerate(r['features'])] for r in train])
        y = np.array([float(F(r['target'])) for r in train])
        penalty = np.eye(x.shape[1]); penalty[0,0] = 0.
        beta = np.linalg.lstsq(np.vstack((x, penalty)), np.r_[y, np.zeros(x.shape[1])], rcond=None)[0]
        raw_delta = float(np.max(np.abs(beta-np.array(model['unrounded']))))
        deployed_delta = float(np.max(np.abs(beta-np.array([float(F(v)) for v in model['coefficients']]))))
        assert raw_delta < 1e-10 and deployed_delta < 5.01e-10
        fits[name] = dict(unrounded_max_difference=raw_delta, deployed_rounding_max_difference=deployed_delta)
    result = dict(status='PASS', scope='Root independent labels, complete prefixes, predeclared sample coverage and augmented least-squares refit; physical audit separate',
                  script_sha256=sha(Path(__file__)), model_sha256=sha(OUT/'MODELS_FROZEN_BEFORE_TEST.json'),
                  labels=len(labels), train=len(train), calibration=len(labels)-len(train), effects=dict(effects), models=fits)
    (HERE/'ROOT_LABEL_AUDIT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
