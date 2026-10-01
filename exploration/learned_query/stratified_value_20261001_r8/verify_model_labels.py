"""Independent reconstruction: does not import the runner or training pipeline."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import json,hashlib,numpy as np
P=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def raw(e):return [json.loads(x) for x in Path(e['raw']).read_text().splitlines()]
def prefix(rs,op):
 result=[]
 for r in rs:
  z=json.loads(json.dumps(r))
  if z['event']=='actor_decision':
   for k in ('policy','remaining_capacity','selected'):del z[k]
   for c in z['candidates']:del c['score']
  result.append(z)
  if r['event']=='actor_decision' and r['opportunity']==op:return result
 raise AssertionError('opportunity absent')
def flow(w,rs):
 times={r['task']:F(r['at']['lower']+r['at']['upper'],2000000) for r in rs if r['event']=='task_service'}
 return sum((times.get(t['task'],F(w['horizon'])) for a in w['robots'] for t in a['tasks'][:4]),F(0))
def main():
 reg=load(P/'REGISTRATION.json');labels=load(P/'TRAIN_CAL_LABELS.json');model=load(P/'MODELS_FROZEN_BEFORE_TEST.json');receipts=[load(p) for p in (P/'runs').glob('*.receipt.json')];lookup={(r['world'],r['policy']):r for r in receipts};expected={};checked=0
 for w in reg['worlds']:
  if w['split'] not in ['train','calibration']:continue
  wait=lookup[w['name'],'WAIT'];wr=raw(wait);ds=[r for r in wr if r['event']=='actor_decision']
  selected=[]
  for lo in [0,32,64,96]:
   for single in [True,False]:
    selected += [r for r in ds if min(3,r['at']['lower']//32000000)==lo//32 and (len(r['candidates'])==1)==single][:2]
  for d in selected:
   for c in d['candidates']:
    key=w['name'],d['opportunity'],c['agent'];probe=lookup[w['name'],f"probe_{d['opportunity']}_{c['agent']}"]
    expected[key]=(w,d,c,wait,probe,wr)
 assert len(labels)==len(expected)
 for row in labels:
  w,d,c,wait,probe,wr=expected.pop((row['world'],row['opportunity'],row['source']));assert row['features']==c['features'] and row['candidate_count']==len(d['candidates'])
  if probe['error'] is not None:assert row['target'] is None and row['error']==probe['error'];continue
  pr=raw(probe);assert prefix(wr,d['opportunity'])==prefix(pr,d['opportunity']);choice=next(r for r in pr if r['event']=='actor_decision' and r['opportunity']==d['opportunity']);assert choice['selected']==c['move']
  before=sum(r['event']=='task_service' for r in wr);after=sum(r['event']=='task_service' for r in pr);gain=flow(w,wr)-flow(w,pr);den=2*w['horizon']*w['N']*4+1
  assert row['whole_service_gain']==after-before and F(row['fixed_first4_time_gain'])==gain and F(row['target'])==F(after-before)+gain/den and abs(gain/den)<F(1,2);checked+=1
 assert not expected and model['labels_sha256']==sha(P/'TRAIN_CAL_LABELS.json')
 training=[r for r in labels if r['split']=='train' and r.get('target') is not None];results={}
 for name,m in model['models'].items():
  X=np.array([[float(F(s)) if name=='ridge_history' or j not in range(10,18) else 0. for j,s in enumerate(r['features'])] for r in training]);weights=np.array([1/r['candidate_count'] for r in training]);y=np.array([float(F(r['target'])) for r in training]);mean=(X*weights[:,None]).sum(0)/weights.sum();var=((X-mean)**2*weights[:,None]).sum(0)/weights.sum();scale=np.sqrt(var);scale[scale<1e-12]=1
  assert np.max(abs(mean-np.array(m['train_mean'])))<1e-12 and np.max(abs(scale-np.array(m['train_scale'])))<1e-12
  design=np.column_stack([np.ones(len(X)),(X-mean)/scale]);ridge=np.diag([0.]+[1.]*20);aug=np.vstack([np.sqrt(weights)[:,None]*design,ridge]);target=np.r_[np.sqrt(weights)*y,np.zeros(21)];beta=np.linalg.lstsq(aug,target,rcond=None)[0];rawcoef=np.r_[beta[0]-mean@(beta[1:]/scale),beta[1:]/scale]
  assert np.max(abs(beta-np.array(m['standardized_coefficients'])))<1e-9 and np.max(abs(rawcoef-np.array(m['unrounded_raw'])))<1e-8
  q=np.array([float(F(z)) for z in m['coefficients']]);assert np.max(abs(q-rawcoef))<5.1e-10
  err=float(np.max(abs(design@beta-np.column_stack([np.ones(len(X)),X])@rawcoef)));assert err<1e-10
  results[name]=dict(rows=len(X),opportunities=len({(r['world'],r['opportunity']) for r in training}),lstsq_refit_max_error=float(np.max(abs(rawcoef-np.array(m['unrounded_raw'])))),standardized_raw_prediction_max_error=err)
 assert model['advantage_relative_to_WAIT'] and model['WAIT_score_exactly_zero'] and not model['calibration_used_for_selection'] and not model['test_seen_before_freeze']
 frozen_at=(P/'MODELS_FROZEN_BEFORE_TEST.json').stat().st_mtime_ns;heldout_names={w['name'] for w in reg['worlds'] if w['split'] in ['test','scale']};freeze_checks=0
 for e in receipts:
  if e['world'] not in heldout_names:continue
  inp=Path(e['input']);assert inp.stat().st_mtime_ns>=frozen_at;parameters={}
  for line in inp.read_text().splitlines():
   z=line.split()
   if z[0]=='M':parameters.setdefault(z[1],[]).append(F(int(z[2]),int(z[3])))
  assert parameters=={name:[F(z) for z in m['coefficients']] for name,m in model['models'].items()};freeze_checks+=1
 out=dict(passed=True,labels_checked=checked,failed_labels=len(labels)-checked,all_selected_candidates_present=True,complete_prefixes=True,task_primary_secondary_abs_lt_half=True,WAIT_is_defined_zero_advantage_not_feature_row=True,models=results,heldout_input_parameter_and_freeze_order_checks=freeze_checks,source_sha256=sha(Path(__file__)))
 with (P/'MODEL_LABEL_AUDIT.json').open('x') as f:json.dump(out,f,indent=2);f.write('\n')
 print(json.dumps(out),flush=True)
if __name__=='__main__':main()
