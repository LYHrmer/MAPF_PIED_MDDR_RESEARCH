"""Root independent augmented least-squares fit of the four R10 value heads."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import numpy as np

P=Path(__file__).resolve().parent
labels=json.loads((P/'TRAIN_CAL_LABELS.json').read_text())
saved=json.loads((P/'MODELS_FROZEN_BEFORE_TEST.json').read_text())
freeze=json.loads((P/'MODEL_FREEZE_RECEIPT.json').read_text())
assert hashlib.sha256((P/'TRAIN_CAL_LABELS.json').read_bytes()).hexdigest()==saved['labels_sha256']
assert hashlib.sha256((P/'MODELS_FROZEN_BEFORE_TEST.json').read_bytes()).hexdigest()==freeze['model_sha256']
assert freeze['existing_test_receipts']==0 and not saved['calibration_used_for_selection'] and not saved['test_seen_before_freeze']
for r in labels:
    expected=Fraction(r['whole_service_gain'])+Fraction(r['fixed_first4_time_gain'])/r['secondary_denominator']
    assert expected==Fraction(r['target'])
    if r['action']=='WAIT':assert r['features'] is None and expected==0
checks={}
for variant in ['history','nohistory']:
    blocked=list(range(10,18)) if variant=='nohistory' else []
    for action in ['QUERY','SKIP']:
        name='ridge_'+variant+'_'+action
        model=saved['models'][name]
        train=[r for r in labels if r['split']=='train' and r['action']==action]
        raw=np.array([[float(Fraction(v)) for v in r['features']] for r in train])
        raw[:,blocked]=0
        w=np.array([1/r['candidate_count'] for r in train])
        y=np.array([float(Fraction(r['target'])) for r in train])
        mean=np.average(raw,axis=0,weights=w)
        scale=np.sqrt(np.average((raw-mean)**2,axis=0,weights=w));scale[scale<1e-12]=1
        X=np.column_stack([np.ones(len(raw)),(raw-mean)/scale])
        penalty=np.eye(25)[1:]
        beta=np.linalg.lstsq(np.vstack([X*np.sqrt(w)[:,None],penalty]),np.r_[y*np.sqrt(w),np.zeros(24)],rcond=None)[0]
        coeff=np.r_[beta[0]-np.sum(beta[1:]*mean/scale),beta[1:]/scale]
        diff=float(np.abs(coeff-np.array(model['unrounded_raw'])).max())
        assert diff<1e-9 and np.allclose(mean,model['train_mean'],rtol=0,atol=1e-12)
        assert np.allclose(scale,model['train_scale'],rtol=0,atol=1e-12)
        assert model['lambda_value']==1 and model['unpenalized_intercept']
        assert all(abs(float(Fraction(v))-c)<=5.01e-10 for v,c in zip(model['coefficients'],coeff))
        assert model['masked_slots']==blocked and all(Fraction(model['coefficients'][j+1])==0 for j in blocked)
        checks[name]={'train_rows':len(train),'families':len({r['world'] for r in train}),
                      'opportunity_weight_sum':float(w.sum()),'max_raw_coefficient_difference':diff}
out={'passed':True,'candidate_imports':False,'models':checks,'labels':len(labels),
     'model_sha256':freeze['model_sha256'],
     'scope':'four separate QUERY/SKIP ridge heads, train-only weighted standardization, augmented least-squares, rounded exact deployment coefficients and pre-test freeze'}
(P/'ROOT_REFIT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
