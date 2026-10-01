from concurrent.futures import ThreadPoolExecutor,as_completed
from fractions import Fraction
from pathlib import Path
import json,threading,hashlib,numpy as np
import mechanical as helper
HERE=Path(__file__).resolve().parent;sha=helper.sha;write=helper.write;run=helper.run

def flow(s):
 v=s['service_time_sum'];return Fraction(v['lower']+v['upper'],2*v['denominator'])+384*(s['task_count']-s['served'])
def records(e):return [json.loads(x) for x in Path(e['raw']).read_text().splitlines()]
def prefix(rs,op):
 out=[]
 for row in rs:
  r=json.loads(json.dumps(row))
  if r['event']=='actor_decision':
   r.pop('policy');r.pop('remaining_capacity');r['selected']=''
   for c in r['candidates']:c.pop('score')
  out.append(r)
  if row['event']=='actor_decision' and row['opportunity']==op:return out
 raise AssertionError('missing public opportunity')
def main():
 out=HERE/'native_attempt_01';out.mkdir(exist_ok=True);sup=json.loads((HERE/'SUPPORT.json').read_text());binary=HERE/'mechanical_attempt_02/joint_history_native';assert binary.exists()
 frozen={f:sha(HERE/f) for f in ['SUPPORT.json','CONTRACT.md','STATISTICAL_CONTRACT.md','pipeline.py','mechanical.py','joint_history_native.cpp']};worlds=[]
 for c in sup['cohorts']:
  split=c['split'];cases=[dict(name=f'IID_{s}',seed=s) for s in ({'train':[10101,10102],'calibration':[11101,11102],'test':[12101,12102]}[split])]
  if split=='test':cases.extend([dict(name='SHIFT_12201',seed=12201,shift=True),dict(name='eta0',seed=0,zero=True)])
  for case in cases:
   private=helper.dynamics(c,case['seed'],case.get('shift',False),case.get('zero',False));wid=c['cohort_id']+'__'+case['name'];p=out/(wid+'.input.txt');txt=helper.render(c,private)
   if p.exists():assert p.read_text()==txt
   else:p.write_text(txt)
   worlds.append(dict(world_id=wid,cohort_id=c['cohort_id'],split=split,case=case,input=str(p),input_sha256=sha(p),private_world_only=private))
 registration=dict(frozen=frozen,worlds=worlds,production_headers=json.loads((HERE.parent/'legal_and_sources.json').read_text()),binary_sha256=sha(binary),concurrency=12,label_first_opportunities=2,budget=16,deadline=384,model_fit_before_test=True,whole_groups=True)
 rp=out/'REGISTRATION.json'
 if rp.exists():assert json.loads(rp.read_text())==registration
 else:write(rp,registration)
 episodes={};lock=threading.Lock();counter=0
 def native(w,policy,model_lines=''):
  nonlocal counter
  assert all(sha(HERE/f)==h for f,h in frozen.items());p=Path(w['input'])
  if model_lines:
   p=out/(w['world_id']+'.model.input.txt');txt=Path(w['input']).read_text()+model_lines
   with lock:
    if p.exists():assert p.read_text()==txt
    else:p.write_text(txt)
  stem=w['world_id']+'__'+policy;receipt=out/(stem+'.receipt.json')
  b=0 if policy=='WAIT' else 1 if policy.startswith('probe_') else 16
  if receipt.exists():
   e=json.loads(receipt.read_text());assert e['returncode']==0 and sha(Path(e['raw']))==e['raw_sha256'] and sha(p)==e['input_sha256'];e['reused_this_invocation']=True
  else:
   e=run([str(binary),str(p),policy,str(b)],600);raw=out/(stem+'.jsonl');raw.write_text(e.pop('stdout'));e.update(world_id=w['world_id'],cohort_id=w['cohort_id'],split=w['split'],policy=policy,capacity=b,input=str(p),input_sha256=sha(p),raw=str(raw),raw_sha256=sha(raw))
   if e['returncode']==0:e['summary']=json.loads(raw.read_text().splitlines()[-1])
   write(receipt,e)
  with lock:episodes[stem]=e;counter+=1;print('NATIVE',counter,stem,e['returncode'],round(e['seconds'],3),'tasks',e.get('summary',{}).get('served'),'query',e.get('summary',{}).get('queries'),flush=True)
  assert e['returncode']==0,'native failure '+stem+' '+e['stderr'];return e
 def batch(jobs):
  results=[]
  with ThreadPoolExecutor(max_workers=12) as pool:
   futures=[pool.submit(native,*j) for j in jobs]
   for f in as_completed(futures):results.append(f.result())
  return results
 tc=[w for w in worlds if w['split']!='test'];waits=batch([(w,'WAIT') for w in tc]);wm={e['world_id']:e for e in waits};candidates=[];jobs=[]
 for w in tc:
  ds=[r for r in records(wm[w['world_id']]) if r['event']=='actor_decision'][:2]
  for d in ds:
   for c in d['candidates']:
    p=f"probe_{d['opportunity']}_{c['agent']}";jobs.append((w,p));candidates.append((w,d,c,p))
 probes=batch(jobs);pm={(e['world_id'],e['policy']):e for e in probes};rows=[]
 for w,d,c,p in candidates:
  wait=wm[w['world_id']];probe=pm[w['world_id'],p];wr=records(wait);pr=records(probe);op=d['opportunity'];assert prefix(wr,op)==prefix(pr,op),'prequery causal mismatch'
  selected=next(r for r in pr if r['event']=='actor_decision' and r['opportunity']==op);assert selected['selected']==c['move'];gain=flow(wait['summary'])-flow(probe['summary']);extra=probe['summary']['served']-wait['summary']['served'];target=Fraction(extra)+gain/(384*wait['summary']['task_count'])
  rows.append(dict(world_id=w['world_id'],cohort_id=w['cohort_id'],split=w['split'],opportunity=op,source=c['agent'],move=c['move'],features=c['features'],END_only_known=d['END_only_known'],at=d['at'],target=str(target),restricted_flow_gain=str(gain),extra_tasks=extra,chosen_policy=p,verified_identical_prequery_physical_public_prefix=True))
 rows.sort(key=lambda r:(r['world_id'],r['opportunity'],r['source']));lp=out/'TRAIN_CAL_LABELS.json'
 if lp.exists():assert json.loads(lp.read_text())==rows
 else:write(lp,rows)
 train=[r for r in rows if r['split']=='train'];assert train;models={}
 for name in ['ridge_history','ridge_nohistory']:
  def matrix(rs):return np.array([[1]+[float(Fraction(z)) if name=='ridge_history' or j<10 or j>=18 else 0.0 for j,z in enumerate(r['features'])] for r in rs])
  X=matrix(train);y=np.array([float(Fraction(r['target'])) for r in train]);penalty=np.eye(21);penalty[0,0]=0;fit=np.linalg.solve(X.T@X+penalty,X.T@y);coef=[Fraction(str(round(float(z),9))) for z in fit];q=np.array([float(z) for z in coef]);cal=[r for r in rows if r['split']=='calibration'];rmse=lambda rs:float(np.sqrt(np.mean((matrix(rs)@q-np.array([float(Fraction(r['target'])) for r in rs]))**2))) if rs else None
  models[name]=dict(coefficients=[str(z) for z in coef],unrounded_coefficients=fit.tolist(),features=20,lambda_value=1,unpenalized_intercept=True,train_rows=len(train),calibration_rows=len(cal),train_rmse=rmse(train),calibration_rmse=rmse(cal),nohistory_zero_slots=list(range(10,18)) if name=='ridge_nohistory' else [],calibration_for_selection=False,test_for_selection=False)
 model=dict(models=models,train_label_sha256=sha(lp),train_cohorts=sorted({r['cohort_id'] for r in train}),same_architecture_rows_ridge_budget=True);mp=out/'MODELS_FROZEN_BEFORE_TEST.json'
 if mp.exists():assert json.loads(mp.read_text())==model
 else:write(mp,model)
 mh=sha(mp);print('MODEL FROZEN',mh,'train',len(train),'cal',len(rows)-len(train),flush=True);lines=''.join(f'M {name} {Fraction(z).numerator} {Fraction(z).denominator}\n' for name,m in models.items() for z in m['coefficients']);test=[w for w in worlds if w['split']=='test'];batch([(w,p,lines) for w in test for p in ['WAIT','RR','condition','ridge_history','ridge_nohistory']]);assert sha(mp)==mh
 vals=sorted(episodes.values(),key=lambda e:(e['world_id'],e['policy']));receipt=dict(complete=True,episodes=vals,total_native_episodes=len(vals),worlds=len(worlds),cohorts=6,all_native_passed=True,model_sha256=mh,binary_sha256=sha(binary),all_counterfactual_prefixes_verified=True,train_cal_rows=len(rows),test_worlds=len(test),test_policies=5)
 write(out/'RECEIPT.json',receipt);print('COMPLETE',len(vals),'native',flush=True)
if __name__=='__main__':main()
