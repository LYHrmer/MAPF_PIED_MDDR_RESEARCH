"""Reconstruct corrected R7 training data independently; no implementation imports."""
from collections import defaultdict
from pathlib import Path
import hashlib
import json
import math
import numpy as np

HERE = Path(__file__).resolve().parent


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def reconstruct(path):
    rows, pending, bound = [], {}, {}
    history = defaultdict(list)
    previous = -1
    for line in path.open():
        e = json.loads(line)
        assert e['sequence'] > previous
        previous = e['sequence']
        if e['kind'] == 'view':
            starts = e['view']['mapf_instance']['starts']
        elif e['kind'] == 'proposal':
            pid = e['proposal']['proposal_id']
            for agent, points in enumerate(e['proposal']['plan']):
                assert len(points) == 2
                s, t = points
                motion = (t[1]-s[1], t[0]-s[0])
                if motion == (0, 0):
                    continue
                direction = [(1,0), (0,1), (-1,0), (0,-1)].index(motion)
                # Independent geometric dot product: public headings E,N,W,S.
                heading = [(1,0), (0,-1), (-1,0), (0,1)][starts[agent]['orientation']]
                dot = sum(a*b for a,b in zip(motion, heading))
                turns = {1:0, 0:1, -1:2}[dot]
                past = history[agent][-16:]
                assert all(r['end_sequence'] < e['sequence'] for r in past)
                residual = [r['duration']-45-10*r['turns'] for r in past]
                directional = [r['duration']-45-10*r['turns'] for r in past if r['direction']==direction][-8:]
                features = [turns/2, *[float(direction==k) for k in range(4)], len(past)/16,
                            float(np.mean(residual))/50 if residual else 0.,
                            sum(directional)/(len(directional)+2)/50,
                            residual[-1]/50 if residual else 0.,
                            float(np.std(residual))/50 if residual else 0.]
                pending[pid,agent] = dict(proposal_id=pid, agent=agent, logical_step=0, direction=direction,
                    turns=turns, proposal_tick=e['tick'], start=[s[1],s[0]], goal=[t[1],t[0]],
                    features=features, history_cutoff_sequence=e['sequence'], duration=None, final_node=None)
        elif e['kind'] == 'admit':
            agent = int(e['robot'])
            row = pending.get((pid,agent))
            if row is not None:
                for action in e['actions']:
                    if action[3]=='M' and action[5]==row['goal']:
                        assert row['final_node'] is None
                        row['final_node'] = action[1]
                        bound[agent,action[1]] = row
        elif e['kind'] == 'end':
            row = bound.get((int(e['robot']),e['node']))
            if row is not None:
                assert e['accepted'] and row['duration'] is None
                row.update(duration=e['tick']-row['proposal_tick'], end_tick=e['tick'], end_sequence=e['sequence'])
                assert row['duration'] > 0
                rows.append(row)
                history[row['agent']].append(row)
        else:
            raise AssertionError('non-public event')
    return rows, len(pending)-len(rows)


def main():
    checkpoint = json.loads((HERE/'model_freeze.json').read_text())
    expected = json.loads((HERE/'refit_rows.json').read_text())
    parts = defaultdict(list)
    censored = 0
    runs = {}
    for filename, value in checkpoint['source_pins'].items():
        path = Path(filename)
        assert digest(path) == value
        run = path.parent.name
        assert run.startswith(('train_', 'calibration_'))
        split = 'train' if run.startswith('train_') else 'calibration'
        rows, censor = reconstruct(path)
        want = [r for r in expected[split] if r['run']==run]
        assert len(want)==len(rows)
        for row, other in zip(rows, want):
            assert set(other)==set(row)|{'run'}
            for key, val in row.items():
                if key=='features':
                    assert np.allclose(val, other[key], rtol=0, atol=1e-12)
                else:
                    assert val==other[key], (run, key)
        parts[split].extend(rows)
        censored += censor
        runs[run] = dict(completed=len(rows), censored=censor)
    assert len(runs)==18 and [len(parts[k]) for k in ('train','calibration')]==[6062,3010]
    x = np.array([r['features'] for r in parts['train']])
    y = np.array([r['duration']-45-10*r['turns'] for r in parts['train']])
    mean, scale = x.mean(0), x.std(0)
    scale[scale<1e-12] = 1
    z = np.column_stack([np.ones(len(x)), (x-mean)/scale])
    penalty = np.eye(z.shape[1]); penalty[0,0] = 0
    beta = np.linalg.lstsq(np.vstack([z, penalty]), np.r_[y,np.zeros(z.shape[1])], rcond=None)[0]
    ridge = checkpoint['ridge']
    assert ridge['lambda']==1 and checkpoint['test_seen'] is False
    assert np.allclose(mean,ridge['mean'],atol=1e-12,rtol=0)
    assert np.allclose(scale,ridge['scale'],atol=1e-12,rtol=0)
    difference = float(np.max(np.abs(beta-np.r_[ridge['intercept'],ridge['coef']])))
    assert difference < 1e-8
    calibration = {}
    for policy in ('history','learned'):
        errors = []
        for row in parts['calibration']:
            f = np.array(row['features'])
            residual = f[7]*50 if policy=='history' else beta[0]+((f-mean)/scale)@beta[1:]
            errors.append(abs(float(np.clip(45+10*row['turns']+residual,5,200))-row['duration']))
        rank = min(len(errors),math.ceil(.9*(len(errors)+1)))
        stats = dict(rows=len(errors),rank=rank,q90_absolute_error=sorted(errors)[rank-1],
                     MAE=float(np.mean(errors)),RMSE=float(np.sqrt(np.mean(np.square(errors)))))
        assert all(abs(value-checkpoint['calibration'][policy][key])<1e-8 for key,value in stats.items())
        calibration[policy] = stats
    report = dict(passed=True, implementation_imported=False, corrected_heading_checked_by_dot_product=True,
                  reconstructed_train=len(parts['train']),reconstructed_calibration=len(parts['calibration']),
                  censored=censored,maximum_coefficient_difference=difference,calibration=calibration,runs=runs,
                  model_sha256=digest(HERE/'model_freeze.json'))
    (HERE/'ROOT_MODEL_REFIT_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='runs'},indent=2))


if __name__=='__main__':
    main()
