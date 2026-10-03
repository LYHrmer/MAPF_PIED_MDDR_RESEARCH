"""Root review: independent weighted ridge fit, including exact saved rounding."""
from pathlib import Path
from fractions import Fraction
import hashlib
import json
import numpy as np

H=Path(__file__).resolve().parent
labels=json.loads((H/'TRAIN_CAL_LABELS.json').read_text())
saved=json.loads((H/'MODELS_FROZEN_BEFORE_TEST.json').read_text())
freeze=json.loads((H/'MODEL_FREEZE_RECEIPT.json').read_text())
assert hashlib.sha256((H/'TRAIN_CAL_LABELS.json').read_bytes()).hexdigest()==saved['labels_sha256']
assert hashlib.sha256((H/'MODELS_FROZEN_BEFORE_TEST.json').read_bytes()).hexdigest()==freeze['model_sha256']
assert freeze['existing_test_receipts']==0 and not saved['calibration_used_for_selection'] and not saved['test_seen_before_freeze']
for r in labels:
    expected=Fraction(r['whole_service_gain'])+Fraction(r['fixed_first4_time_gain'])/r['secondary_denominator']
    assert expected==Fraction(r['target'])
    if r['action']=='WAIT':assert r['features'] is None and expected==0
train=[r for r in labels if r['split']=='train' and r['action']!='WAIT']
mask={'ridge_history':[],'ridge_nohistory':list(range(10,18)),'ridge_nobudget':[20,22,23]}
results={}
for name,blocked in mask.items():
    model=saved['models'][name]
    X=np.array([[float(Fraction(x)) for x in r['features']] for r in train]);X[:,blocked]=0
    w=np.array([1/r['candidate_count'] for r in train]);y=np.array([float(Fraction(r['target'])) for r in train])
    mean=np.average(X,axis=0,weights=w);scale=np.sqrt(np.average((X-mean)**2,axis=0,weights=w));scale[scale<1e-12]=1
    Z=np.column_stack([np.ones(len(X)),(X-mean)/scale]);penalty=np.eye(25)[1:]
    beta=np.linalg.lstsq(np.vstack([Z*np.sqrt(w)[:,None],penalty]),np.r_[y*np.sqrt(w),np.zeros(24)],rcond=None)[0]
    raw=np.r_[beta[0]-np.sum(beta[1:]*mean/scale),beta[1:]/scale]
    maxdiff=float(np.max(np.abs(raw-np.array(model['unrounded_raw']))))
    assert maxdiff<1e-9 and np.allclose(mean,model['train_mean'],atol=1e-12)
    assert np.allclose(scale,model['train_scale'],atol=1e-12)
    assert all(abs(float(Fraction(c))-v)<=5.0001e-10 for c,v in zip(model['coefficients'],raw))
    assert model['masked_slots']==blocked and all(Fraction(model['coefficients'][i+1])==0 for i in blocked)
    results[name]={'train_rows':len(train),'opportunity_weight_sum':float(w.sum()),'max_unrounded_coefficient_difference':maxdiff,'masked_slots':blocked}
out={'passed':True,'models':results,'explicit_WAIT_rows':sum(r['action']=='WAIT' for r in labels),
     'query_rows':sum(r['action']!='WAIT' for r in labels),'model_sha256':freeze['model_sha256'],
     'candidate_imports':False,'scope':'independent augmented weighted least-squares and saved model freeze/rounding; physical branch-label replay separately audited'}
(H/'ROOT_REFIT.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
