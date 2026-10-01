from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from fractions import Fraction
from collections import Counter
import json,numpy as np,os,time,threading
import runner
HERE=runner.HERE;OUT=HERE/'runs';POLICIES=['WAIT','RR','condition','paced_condition','paced_ridge_history','paced_ridge_nohistory']

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
def selected_decisions(rs):
 ds=[r for r in rs if r['event']=='actor_decision'];selected=[]
 for b in range(4):
  for cardinality in [1,2]:
   selected.extend([r for r in ds if min(3,r['at']['lower']//32000000)==b and min(2,len(r['candidates']))==cardinality][:2])
 return sorted(selected,key=lambda r:r['opportunity'])
def batch(jobs,workers,tag,models=None):
 result=[];stop=threading.Event();peak=dict(rss_bytes=0,processes=0,cpu_ticks=0,samples=0);start=time.monotonic()
 def sample():
  while not stop.is_set():
   stats={}
   for p in Path('/proc').iterdir():
    if not p.name.isdigit():continue
    try:
     z=(p/'stat').read_text().split();stats[int(p.name)]=(int(z[3]),int(z[23])*os.sysconf('SC_PAGE_SIZE'),int(z[13])+int(z[14]))
    except (OSError,ValueError,IndexError):pass
   ids={os.getpid()}
   while True:
    new={i for i,z in stats.items() if z[0] in ids}|ids
    if new==ids:break
    ids=new
   z=[stats[i] for i in ids if i in stats];peak['rss_bytes']=max(peak['rss_bytes'],sum(r[1] for r in z));peak['processes']=max(peak['processes'],len(z));peak['cpu_ticks']=max(peak['cpu_ticks'],sum(r[2] for r in z));peak['samples']+=1;stop.wait(1)
 monitor=threading.Thread(target=sample,daemon=True);monitor.start()
 try:
  with ThreadPoolExecutor(max_workers=workers) as pool:
   futures=[pool.submit(runner.native,w,p,OUT,models) for w,p in jobs]
   for f in as_completed(futures):result.append(f.result())
 finally:stop.set();monitor.join()
 runner.write(HERE/(tag+'_SCHEDULING.json'),dict(workers=workers,jobs=len(jobs),seconds=time.monotonic()-start,descendant_peak=peak,failed=sum(e['error'] is not None for e in result)))
 return result
def worlds():
 out=[]
 for mi,map_name in enumerate(['empty-32-32','random-32-32-10']):
  base=85000+mi*1000
  for j in range(3):
   w=runner.make_world(f'{map_name}_train_{base+101+j}',16,base+101+j,offset=128+j*16,map_name=map_name);w['split']='train';out.append(w)
  w=runner.make_world(f'{map_name}_cal_{base+201}',16,base+201,offset=176,map_name=map_name);w['split']='calibration';out.append(w)
  for j in range(2):
   for shift in [False,True]:
    w=runner.make_world(f'{map_name}_test_{base+301+j}_'+('SHIFT' if shift else 'IID'),16,base+301+j,offset=192+j*16,shift=shift,map_name=map_name);w['split']='test';out.append(w)
  w=runner.make_world(f'{map_name}_scale_{base+401}_IID',32,base+401,offset=224,map_name=map_name);w['split']='scale';out.append(w)
 return out
def preflight(ws):
 result=[]
 for w in ws:
  blocked=[(x,y) for y,row in enumerate(w['layout']) for x,c in enumerate(row) if c=='@'];free={(x,y) for y,row in enumerate(w['layout']) for x,c in enumerate(row) if c=='.'}
  assert len(free)+len(blocked)==w['rows']*w['cols']
  for r in w['robots']:
   assert tuple(r['start']) in free
   assert all(tuple(t['goal']) in free for t in r['tasks'])
  edges=0
  for x,y in free:
   for dx,dy in [(1,0),(0,1),(-1,0),(0,-1)]:
    if (x+dx,y+dy) not in free:continue
    # All coordinates are exact integer twentieths; closed rectangles.
    xl,xh=20*min(x,x+dx)-3,20*max(x,x+dx)+3;yl,yh=20*min(y,y+dy)-3,20*max(y,y+dy)+3
    assert all(xh<20*bx-10 or 20*bx+10<xl or yh<20*by-10 or 20*by+10<yl for bx,by in blocked),'closed swept footprint hits blocked square'
    edges+=1
  result.append(dict(world=w['name'],N=w['N'],free=len(free),blocked=len(blocked),all_directed_free_edges_checked=edges,goals_checked=sum(len(r['tasks']) for r in w['robots'])))
 ids={split:{t['task'] for w in ws if w['split']==split for r in w['robots'] for t in r['tasks']} for split in ['train','calibration','test','scale']}
 assert all(not a&b for i,a in enumerate(ids.values()) for b in list(ids.values())[i+1:])
 runner.write(HERE/'MAP_INPUT_PREFLIGHT.json',dict(passed=True,worlds=result,split_task_ids_disjoint=True))
def fit(rows):
 train=[r for r in rows if r['split']=='train' and r.get('target') is not None];cal=[r for r in rows if r['split']=='calibration' and r.get('target') is not None];models={}
 weights=np.array([1/r['candidate_count'] for r in train]);y=np.array([float(Fraction(r['target'])) for r in train])
 for name in ['ridge_history','ridge_nohistory']:
  def matrix(rs):return np.array([[float(Fraction(z)) if name=='ridge_history' or j<10 or j>=18 else 0. for j,z in enumerate(r['features'])] for r in rs])
  raw=matrix(train);mean=np.average(raw,axis=0,weights=weights);scale=np.sqrt(np.average((raw-mean)**2,axis=0,weights=weights));scale[scale<1e-12]=1
  X=np.column_stack([np.ones(len(train)),(raw-mean)/scale]);penalty=np.eye(21);penalty[0,0]=0
  beta=np.linalg.solve(X.T@(weights[:,None]*X)+penalty,X.T@(weights*y));slopes=beta[1:]/scale;rawcoef=np.r_[beta[0]-mean@slopes,slopes]
  assert np.max(abs(X@beta-np.column_stack([np.ones(len(train)),raw])@rawcoef))<1e-10
  coef=[Fraction(str(round(float(z),9))) for z in rawcoef];q=np.array([float(z) for z in coef])
  def rmse(rs):
   pred=np.column_stack([np.ones(len(rs)),matrix(rs)])@q;truth=np.array([float(Fraction(r['target'])) for r in rs]);w=np.array([1/r['candidate_count'] for r in rs]);return float(np.sqrt(np.average((pred-truth)**2,weights=w)))
  models[name]=dict(coefficients=[str(z) for z in coef],unrounded_raw=rawcoef.tolist(),standardized_coefficients=beta.tolist(),train_mean=mean.tolist(),train_scale=scale.tolist(),lambda_value=1,unpenalized_intercept=True,train_rows=len(train),calibration_rows=len(cal),train_weighted_rmse=rmse(train),calibration_weighted_rmse=rmse(cal),history_zero_slots=list(range(10,18)) if name=='ridge_nohistory' else [])
 return dict(models=models,labels_sha256=runner.sha(HERE/'TRAIN_CAL_LABELS.json'),row_bindings=[dict(world=r['world'],opportunity=r['opportunity'],source=r['source'],weight=f"1/{r['candidate_count']}") for r in train],advantage_relative_to_WAIT=True,WAIT_score_exactly_zero=True,calibration_used_for_selection=False,test_seen_before_freeze=False)
def main():
 ws=worlds();preflight(ws);runner.compile_native()
 frozen={f:runner.sha(HERE/f) for f in ['CONTRACT.md','joint_history_native.cpp','runner.py','pipeline.py','audit.py','audit_reference.py']}
 runner.write(HERE/'REGISTRATION.json',dict(worlds=ws,frozen=frozen,binary_sha256=runner.sha(HERE/'build/joint_history_native'),bridge_sha256=runner.sha(runner.BRIDGE),config_sha256=runner.sha(runner.CONFIG),policies=POLICIES,selection='four public time bins x first2 single and first2 multi opportunities; every candidate',planned_test_episodes=48,planned_scale_episodes=12))
 tc=[w for w in ws if w['split'] in ['train','calibration']];waits=batch([(w,'WAIT') for w in tc],4,'WAIT4');wm={e['world']:e for e in waits};samples=[];jobs=[];coverage=[]
 assert all(e['error'] is None for e in waits),'WAIT execution error; retained and stop before fitting'
 for w in tc:
  rs=records(wm[w['name']]);ds=[r for r in rs if r['event']=='actor_decision'];selected=selected_decisions(rs)
  coverage.append(dict(world=w['name'],all_single=sum(len(r['candidates'])==1 for r in ds),all_multiple=sum(len(r['candidates'])>1 for r in ds),selected=[dict(opportunity=r['opportunity'],candidates=len(r['candidates']),at=r['at']) for r in selected],census=dict(Counter(str(min(2,r['candidates'])) for r in rs if r['event']=='opportunity_census'))))
  for d in selected:
   for c in d['candidates']:
    policy=f"probe_{d['opportunity']}_{c['agent']}";jobs.append((w,policy));samples.append((w,d,c,policy))
 runner.write(HERE/'LABEL_SELECTION_BEFORE_PROBES.json',dict(coverage=coverage,candidate_rows=len(samples),selection_depends_on_gain=False))
 probes=batch(jobs[:4],4,'PROBE4')+batch(jobs[4:12],8,'PROBE8')
 resource=json.loads((HERE/'PROBE8_SCHEDULING.json').read_text());workers=8 if resource['descendant_peak']['rss_bytes']<3_500_000_000 else 4
 probes+=batch(jobs[12:],workers,'PROBE_REMAINDER');pm={(e['world'],e['policy']):e for e in probes};rows=[]
 for w,d,c,policy in samples:
  wait=wm[w['name']];probe=pm[w['name'],policy];base=dict(world=w['name'],split=w['split'],opportunity=d['opportunity'],candidate_count=len(d['candidates']),source=c['agent'],move=c['move'],features=c['features'],probe=policy)
  if probe['error'] is not None:rows.append(dict(base,target=None,error=probe['error']));continue
  wr,pr=records(wait),records(probe);assert prefix(wr,d['opportunity'])==prefix(pr,d['opportunity']),'counterfactual prefix mismatch'
  chosen=next(r for r in pr if r['event']=='actor_decision' and r['opportunity']==d['opportunity']);assert chosen['selected']==c['move']
  gain=fixed_flow(w,wr)-fixed_flow(w,pr);delta=probe['summary']['served']-wait['summary']['served'];den=2*w['horizon']*w['N']*4+1;target=Fraction(delta)+gain/den;assert abs(gain/den)<Fraction(1,2)
  rows.append(dict(base,target=str(target),fixed_first4_time_gain=str(gain),whole_service_gain=delta,secondary_denominator=den,same_full_prefix=True,query_deadlock=probe['summary']['deadlock'],WAIT_deadlock=wait['summary']['deadlock']))
 rows.sort(key=lambda r:(r['world'],r['opportunity'],r['source']));runner.write(HERE/'TRAIN_CAL_LABELS.json',rows)
 model=fit(rows);runner.write(HERE/'MODELS_FROZEN_BEFORE_TEST.json',model);mh=runner.sha(HERE/'MODELS_FROZEN_BEFORE_TEST.json');print('MODEL_FROZEN',mh,'labels',len(rows),flush=True)
 tests=batch([(w,p) for w in ws if w['split']=='test' for p in POLICIES],workers,'TEST',model['models'])
 scales=batch([(w,p) for w in ws if w['split']=='scale' for p in POLICIES],workers,'SCALE',model['models'])
 assert runner.sha(HERE/'MODELS_FROZEN_BEFORE_TEST.json')==mh
 runner.write(HERE/'RECEIPT.json',dict(complete=True,native_episodes=len(waits)+len(probes)+len(tests)+len(scales),test_episodes=len(tests),scale_episodes=len(scales),labels=len(rows),failed=sum(e['error'] is not None for e in waits+probes+tests+scales),model_sha256=mh,workers=workers))
if __name__=='__main__':main()
