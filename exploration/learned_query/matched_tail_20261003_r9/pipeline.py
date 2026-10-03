from pathlib import Path
from concurrent.futures import ThreadPoolExecutor,as_completed
from fractions import Fraction
from collections import Counter
import json,numpy as np,os,time,threading,sys
import runner
HERE=runner.HERE;OUT=HERE/'runs'
POLICIES=['WAIT','condition','once_history','once_nohistory','once_nobudget']
def records(e):return [json.loads(x) for x in Path(e['raw']).read_text().splitlines()]
def prefix(rs,op):
 out=[]
 for row in rs:
  r=json.loads(json.dumps(row))
  if r['event']=='actor_decision':
   r.pop('policy');r.pop('decision_mode')
   if r['opportunity']==op:
    r.pop('selected')
    for c in r['candidates']:c.pop('score')
  out.append(r)
  if row['event']=='actor_decision' and row['opportunity']==op:return out
 raise AssertionError('missing opportunity')
def fixed_flow(w,rs):
 selected={t['task'] for r in w['robots'] for t in r['tasks'][:4]};times={r['task']:Fraction(r['at']['lower']+r['at']['upper'],2_000_000) for r in rs if r['event']=='task_service'}
 return sum((times.get(t,Fraction(w['horizon'])) for t in selected),Fraction(0))
def selected_decisions(rs):
 # Fixed chronological first single/multi within each spent-budget tier.
 seen=set();selected=[];branches=0
 for r in rs:
  if r['event']!='actor_decision' or r['remaining_capacity']<=0:continue
  spent=16-r['remaining_capacity'];key=(min(2,spent//6),min(2,len(r['candidates'])))
  if key in seen:continue
  seen.add(key);cost=1+len(r['candidates'])
  if branches+cost>14:continue
  selected.append(r);branches+=cost
 return selected
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
  base=91000+mi*1000
  for j in range(2):
   w=runner.make_world(f'{map_name}_train_{base+101+j}',16,base+101+j,offset=256+j*16,map_name=map_name);w['split']='train';out.append(w)
  w=runner.make_world(f'{map_name}_cal_{base+201}',16,base+201,offset=288,map_name=map_name);w['split']='calibration';out.append(w)
  for j in range(2):
   for shift in [False,True]:
    w=runner.make_world(f'{map_name}_test_{base+301+j}_'+('SHIFT' if shift else 'IID'),16,base+301+j,offset=304+j*16,shift=shift,map_name=map_name);w['split']='test';out.append(w)
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
 train=[r for r in rows if r['split']=='train' and r['action']!='WAIT' and r.get('target') is not None];cal=[r for r in rows if r['split']=='calibration' and r['action']!='WAIT' and r.get('target') is not None];models={}
 weights=np.array([1/r['candidate_count'] for r in train]);y=np.array([float(Fraction(r['target'])) for r in train])
 for name in ['ridge_history','ridge_nohistory','ridge_nobudget']:
  masked=list(range(10,18)) if name=='ridge_nohistory' else [20,22,23] if name=='ridge_nobudget' else []
  def matrix(rs):return np.array([[float(Fraction(z)) if j not in masked else 0. for j,z in enumerate(r['features'])] for r in rs])
  raw=matrix(train);mean=np.average(raw,axis=0,weights=weights);scale=np.sqrt(np.average((raw-mean)**2,axis=0,weights=weights));scale[scale<1e-12]=1
  X=np.column_stack([np.ones(len(train)),(raw-mean)/scale]);penalty=np.eye(25);penalty[0,0]=0
  beta=np.linalg.solve(X.T@(weights[:,None]*X)+penalty,X.T@(weights*y));slopes=beta[1:]/scale;rawcoef=np.r_[beta[0]-mean@slopes,slopes]
  assert np.max(abs(X@beta-np.column_stack([np.ones(len(train)),raw])@rawcoef))<1e-10
  coef=[Fraction(str(round(float(z),9))) for z in rawcoef];q=np.array([float(z) for z in coef])
  assert all(coef[j+1]==0 and mean[j]==0 and scale[j]==1 for j in masked)
  def rmse(rs):
   pred=np.column_stack([np.ones(len(rs)),matrix(rs)])@q;truth=np.array([float(Fraction(r['target'])) for r in rs]);w=np.array([1/r['candidate_count'] for r in rs]);return float(np.sqrt(np.average((pred-truth)**2,weights=w)))
  models[name]=dict(coefficients=[str(z) for z in coef],unrounded_raw=rawcoef.tolist(),standardized_coefficients=beta.tolist(),train_mean=mean.tolist(),train_scale=scale.tolist(),lambda_value=1,unpenalized_intercept=True,train_rows=len(train),calibration_rows=len(cal),train_weighted_rmse=rmse(train),calibration_weighted_rmse=rmse(cal),masked_slots=masked)
 return dict(models=models,labels_sha256=runner.sha(HERE/'TRAIN_CAL_LABELS.json'),row_bindings=[dict(world=r['world'],opportunity=r['opportunity'],source=r['source'],weight=f"1/{r['candidate_count']}") for r in train],advantage_relative_to_current_WAIT_then_condition=True,WAIT_score_exactly_zero=True,calibration_used_for_selection=False,test_seen_before_freeze=False)
def registration():
 ws=worlds();preflight(ws);runner.compile_native()
 frozen={f:runner.sha(HERE/f) for f in ['CONTRACT.md','joint_history_native.cpp','runner.py','pipeline.py','audit.py','audit_reference.py']}
 runner.write(HERE/'REGISTRATION.json',dict(worlds=ws,frozen=frozen,binary_sha256=runner.sha(HERE/'build/joint_history_native'),bridge_sha256=runner.sha(runner.BRIDGE),config_sha256=runner.sha(runner.CONFIG),policies=POLICIES,selection='chronological first single/multi per spent tier0..5/6..11/12..15; complete opportunity only within14 probes per run',max_probes=84,planned_test_episodes=40,planned_scale_episodes=0))
def main():
 phase=sys.argv[1]
 if phase=='register':registration();return
 reg=json.loads((HERE/'REGISTRATION.json').read_text());ws=reg['worlds'];tc=[w for w in ws if w['split'] in ['train','calibration']]
 if phase=='base':
  es=batch([(w,'condition') for w in tc],4,'BASE4');assert all(e['error'] is None for e in es);return
 if phase=='probes':
  jobs=[];coverage=[]
  for w in tc:
   e=json.loads((OUT/(w['name']+'__condition.receipt.json')).read_text());rs=records(e);selected=selected_decisions(rs);ds=[r for r in rs if r['event']=='actor_decision']
   coverage.append(dict(world=w['name'],all_single=sum(len(r['candidates'])==1 for r in ds),all_multiple=sum(len(r['candidates'])>1 for r in ds),selected=[dict(opportunity=r['opportunity'],candidates=len(r['candidates']),remaining=r['remaining_capacity'],at=r['at']) for r in selected]))
   for d in selected:
    for action in ['WAIT']+[str(c['agent']) for c in d['candidates']]:jobs.append((w,f"cf_{d['opportunity']}_{action}"))
  runner.write(HERE/'LABEL_SELECTION_BEFORE_PROBES.json',dict(coverage=coverage,branches=len(jobs),jobs=[dict(world=w['name'],policy=p) for w,p in jobs],selection_depends_on_gain=False))
  es=batch(jobs,int(os.environ.get('R9_WORKERS','4')),'PROBES');assert all(e['error'] is None for e in es),'failed probes retained, inspect before fitting';return
 if phase=='train':
  labels=[]
  for w in tc:
   e=json.loads((OUT/(w['name']+'__condition.receipt.json')).read_text());rs=records(e)
   for d in selected_decisions(rs):
    op=d['opportunity'];wait=json.loads((OUT/(w['name']+f'__cf_{op}_WAIT.receipt.json')).read_text());wr=records(wait);assert prefix(rs,op)==prefix(wr,op)
    for action in ['WAIT']+[str(c['agent']) for c in d['candidates']]:
     ep=json.loads((OUT/(w['name']+f'__cf_{op}_{action}.receipt.json')).read_text());pr=records(ep);assert ep['error'] is None and prefix(rs,op)==prefix(pr,op)
     c=next((c for c in d['candidates'] if str(c['agent'])==action),None);chosen=next(r for r in pr if r['event']=='actor_decision' and r['opportunity']==op);assert chosen['selected']==(c['move'] if c else '')
     gain=fixed_flow(w,wr)-fixed_flow(w,pr);delta=ep['summary']['served']-wait['summary']['served'];den=2*w['horizon']*w['N']*4+1;target=Fraction(delta)+gain/den;assert abs(gain/den)<Fraction(1,2)
     labels.append(dict(world=w['name'],split=w['split'],opportunity=op,candidate_count=len(d['candidates']),remaining_capacity=d['remaining_capacity'],action=action,source=c['agent'] if c else None,move=c['move'] if c else None,features=c['features'] if c else None,policy=ep['policy'],WAIT_policy=wait['policy'],target=str(target),whole_service_gain=delta,fixed_first4_time_gain=str(gain),secondary_denominator=den,same_full_prefix=True))
  runner.write(HERE/'TRAIN_CAL_LABELS.json',labels);model=fit(labels);runner.write(HERE/'MODELS_FROZEN_BEFORE_TEST.json',model);print('MODEL_FROZEN',runner.sha(HERE/'MODELS_FROZEN_BEFORE_TEST.json'),'labels',len(labels),flush=True);return
 if phase=='test':
  model=json.loads((HERE/'MODELS_FROZEN_BEFORE_TEST.json').read_text());mh=runner.sha(HERE/'MODELS_FROZEN_BEFORE_TEST.json');runner.write(HERE/'TEST_START.json',dict(model_sha256=mh,unix_time=time.time(),planned_worlds=[w['name'] for w in ws if w['split']=='test']))
  es=batch([(w,p) for w in ws if w['split']=='test' for p in POLICIES],int(os.environ.get('R9_WORKERS','4')),'TEST',model['models']);assert runner.sha(HERE/'MODELS_FROZEN_BEFORE_TEST.json')==mh
  all_es=[json.loads(p.read_text()) for p in OUT.glob('*.receipt.json')];runner.write(HERE/'RECEIPT.json',dict(complete=True,native_episodes=len(all_es),test_episodes=len(es),failed=sum(e['error'] is not None for e in all_es),model_sha256=mh));return
 raise ValueError(phase)
if __name__=='__main__':main()
