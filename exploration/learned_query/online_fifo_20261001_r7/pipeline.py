from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from fractions import Fraction
from collections import Counter
import json,numpy as np
import runner
HERE=runner.HERE;OUT=HERE/'statistical_attempt_01'
def records(e):return [json.loads(x) for x in Path(e['raw']).read_text().splitlines()]
def prefix(rs,op):
 out=[]
 for row in rs:
  r=json.loads(json.dumps(row))
  if r['event']=='actor_decision':
   for k in ['policy','remaining_capacity','selected']:r.pop(k)
   for c in r['candidates']:c.pop('score')
  out.append(r)
  if row['event']=='actor_decision' and row['opportunity']==op:return out
 raise AssertionError('missing opportunity')
def fixed_flow(w,rs):
 selected={t['task'] for r in w['robots'] for t in r['tasks'][:4]};times={r['task']:Fraction(r['at']['lower']+r['at']['upper'],2_000_000) for r in rs if r['event']=='task_service'}
 return sum((times.get(t,Fraction(w['horizon'])) for t in selected),Fraction(0))
def batch(jobs):
 result=[]
 with ThreadPoolExecutor(max_workers=4) as pool:
  futures=[pool.submit(runner.native,*j,OUT) for j in jobs]
  for f in as_completed(futures):
   e=f.result();result.append(e);assert e['error'] is None,e
 return result
def main():
 worlds=[]
 for i,seed in enumerate([74101,74102,74103,74201]):
  w=runner.make_world(('train' if i<3 else 'calibration')+f'_{seed}',16,seed,offset=i*16);w['split']='train' if i<3 else 'calibration';worlds.append(w)
 for i,seed in enumerate([74301,74302]):
  for shift in [False,True]:
   w=runner.make_world(f'test_{seed}_'+('SHIFT' if shift else 'IID'),16,seed,offset=(i+4)*16,shift=shift);w['split']='test';worlds.append(w)
 frozen={f:runner.sha(HERE/f) for f in ['CONTRACT.md','STATISTICAL_CONTRACT.md','joint_history_native.cpp','runner.py','pipeline.py']}
 reg=dict(worlds=worlds,frozen=frozen,binary_sha256=runner.sha(HERE/'build/joint_history_native'),bridge_sha256=runner.sha(runner.BRIDGE),config_sha256=runner.sha(runner.CONFIG),task_ID_overlap_train_cal_test=False,history_nohistory_architecture_control=True,label_rule='first2 cardinality1 and first2 cardinality>=2, all candidates',concurrency=4)
 rp=OUT/'REGISTRATION.json'
 if rp.exists():assert json.loads(rp.read_text())==reg
 else:runner.write(rp,reg)
 tc=[w for w in worlds if w['split']!='test'];waits=batch([(w,'WAIT') for w in tc]);wm={e['world']:e for e in waits};samples=[];jobs=[];coverage=[]
 for w in tc:
  rs=records(wm[w['name']]);ds=[r for r in rs if r['event']=='actor_decision'];selected=[r for r in ds if len(r['candidates'])==1][:2]+[r for r in ds if len(r['candidates'])>1][:2];coverage.append(dict(world=w['name'],all_single=sum(len(r['candidates'])==1 for r in ds),all_multiple=sum(len(r['candidates'])>1 for r in ds),selected=[dict(opportunity=r['opportunity'],candidates=len(r['candidates'])) for r in selected],census=dict(Counter(str(min(2,r['candidates'])) for r in rs if r['event']=='opportunity_census'))))
  for d in selected:
   for c in d['candidates']:
    policy=f"probe_{d['opportunity']}_{c['agent']}";jobs.append((w,policy));samples.append((w,d,c,policy))
 runner.write(OUT/'LABEL_SELECTION_BEFORE_PROBES.json',dict(coverage=coverage,candidate_rows=len(samples),selection_depends_on_gain=False))
 probes=batch(jobs);pm={(e['world'],e['policy']):e for e in probes};rows=[]
 for w,d,c,policy in samples:
  wait=wm[w['name']];probe=pm[w['name'],policy];wr,pr=records(wait),records(probe);assert prefix(wr,d['opportunity'])==prefix(pr,d['opportunity']),'counterfactual prefix mismatch'
  chosen=next(r for r in pr if r['event']=='actor_decision' and r['opportunity']==d['opportunity']);assert chosen['selected']==c['move']
  gain=fixed_flow(w,wr)-fixed_flow(w,pr);delta=probe['summary']['served']-wait['summary']['served'];target=Fraction(delta)+gain/(128*16*4)
  rows.append(dict(world=w['name'],split=w['split'],opportunity=d['opportunity'],candidate_count=len(d['candidates']),source=c['agent'],move=c['move'],features=c['features'],target=str(target),fixed_first4_time_gain=str(gain),whole_service_gain=delta,same_full_prefix=True,probe=policy))
 rows.sort(key=lambda r:(r['world'],r['opportunity'],r['source']));runner.write(OUT/'TRAIN_CAL_LABELS.json',rows);train=[r for r in rows if r['split']=='train'];cal=[r for r in rows if r['split']=='calibration'];models={}
 for name in ['ridge_history','ridge_nohistory']:
  def matrix(data):return np.array([[1]+[float(Fraction(z)) if name=='ridge_history' or j<10 or j>=18 else 0. for j,z in enumerate(r['features'])] for r in data])
  X=matrix(train);y=np.array([float(Fraction(r['target'])) for r in train]);penalty=np.eye(21);penalty[0,0]=0;fit=np.linalg.solve(X.T@X+penalty,X.T@y);coef=[Fraction(str(round(float(z),9))) for z in fit];q=np.array([float(z) for z in coef]);rmse=lambda rs:float(np.sqrt(np.mean((matrix(rs)@q-np.array([float(Fraction(r['target'])) for r in rs]))**2))) if rs else None
  models[name]=dict(coefficients=[str(z) for z in coef],unrounded=fit.tolist(),lambda_value=1,unpenalized_intercept=True,train_rows=len(train),calibration_rows=len(cal),train_rmse=rmse(train),calibration_rmse=rmse(cal),history_zero_slots=list(range(10,18)) if name=='ridge_nohistory' else [])
 model=dict(models=models,labels_sha256=runner.sha(OUT/'TRAIN_CAL_LABELS.json'),row_bindings=[dict(world=r['world'],opportunity=r['opportunity'],source=r['source']) for r in train],test_seen_before_freeze=False,calibration_used_for_selection=False)
 runner.write(OUT/'MODELS_FROZEN_BEFORE_TEST.json',model);mh=runner.sha(OUT/'MODELS_FROZEN_BEFORE_TEST.json');print('MODEL_FROZEN',mh,'train/cal',len(train),len(cal),flush=True)
 test=[w for w in worlds if w['split']=='test'];results=[]
 with ThreadPoolExecutor(max_workers=4) as pool:
  fs=[pool.submit(runner.native,w,p,OUT,models) for w in test for p in ['WAIT','RR','condition','ridge_history','ridge_nohistory']]
  for f in as_completed(fs):
   e=f.result();results.append(e);assert e['error'] is None,e
 assert runner.sha(OUT/'MODELS_FROZEN_BEFORE_TEST.json')==mh
 runner.write(OUT/'RECEIPT.json',dict(complete=True,statistical_native_episodes=len(waits)+len(probes)+len(results),test_episodes=len(results),model_sha256=mh,coverage=coverage,labels=len(rows)))
if __name__=='__main__':main()
