"""Independent prefix, one-current-WAIT semantics, labels and model refit checks."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import copy,json,numpy as np
import runner
P=runner.HERE
def rows(e):return [json.loads(s) for s in Path(e['raw']).read_text().splitlines()]
def prefix(rs,op):
 out=[]
 for x in rs:
  z=copy.deepcopy(x)
  if z['event']=='actor_decision':
   z.pop('policy');z.pop('decision_mode')
   if z['opportunity']==op:
    z.pop('selected')
    for c in z['candidates']:c.pop('score')
  out.append(z)
  if z['event']=='actor_decision' and z['opportunity']==op:return out
 raise AssertionError('missing prefix target')
def flow(w,rs):
 wanted={t['task'] for r in w['robots'] for t in r['tasks'][:4]};actual={r['task']:Q(r['at']['lower']+r['at']['upper'],2000000) for r in rs if r['event']=='task_service'}
 return sum((actual.get(t,Q(w['horizon'])) for t in wanted),Q(0))
def assert_same_action_trajectory(baseline,branch,op):
 assert len(baseline)==len(branch),'same action changed trajectory length'
 for left,right in zip(baseline,branch):
  aa=[]
  for item in [left,right]:
   r=copy.deepcopy(item)
   if r['event']=='actor_decision':
    r.pop('policy');r.pop('decision_mode')
    if r['opportunity']==op:
     for c in r['candidates']:c.pop('score')
   elif r['event']=='joint_summary':r.pop('policy');r.pop('native_checks')
   aa.append(r)
  assert aa[0]==aa[1],'same intervention action changed public/physical continuation'
def check_episode(e,rs):
 decisions=[x for x in rs if x['event']=='actor_decision'];queries=0;last=None;replacements=[]
 for d in decisions:
  now=(d['at']['lower'],d['at']['upper'])
  assert last is None or now!=last,'WAIT must advance to next native decision event'
  assert last is None or now[0]>=last[0],'decision clock regressed'
  last=now
  assert d['remaining_capacity']==16-queries,'budget replay mismatch'
  mode=e['policy']
  if mode.startswith('cf_'):
   _,op,action=mode.split('_');mode='force_'+action if d['opportunity']==int(op) else 'condition'
  elif mode.startswith('once_'):
   mode='ridge_'+mode[5:] if not replacements and queries>=6 and queries<16 else 'condition'
  assert d['decision_mode']==mode,'continuation changed from fixed pi0'
  if mode.startswith(('ridge_','force_')):replacements.append(d)
  if d['selected']:queries+=1
 assert queries==e['summary']['queries']<=16
 if e['policy'].startswith('cf_'):assert len(replacements)==1
 if e['policy'].startswith('once_'):assert len(replacements)<=1
 for d in replacements:
  nxt=next((x for x in decisions if x['opportunity']==d['opportunity']+1),None)
  if nxt:
   assert nxt['remaining_capacity']==d['remaining_capacity']-bool(d['selected']),'WAIT/query first-step budget wrong'
   assert nxt['at']!=d['at'],'immediate same-opportunity compensation query'
 return replacements
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());worlds={w['name']:w for w in reg['worlds']};es=[json.loads(p.read_text()) for p in (P/'runs').glob('*.receipt.json')];em={(e['world'],e['policy']):e for e in es};labels=json.loads((P/'TRAIN_CAL_LABELS.json').read_text());cache={};verified=[];changes=[];selection=[];identical=0
 frozen=json.loads((P/'MODELS_FROZEN_BEFORE_TEST.json').read_text());freeze=json.loads((P/'MODEL_FREEZE_RECEIPT.json').read_text());start=json.loads((P/'TEST_START.json').read_text())
 assert frozen['labels_sha256']==runner.sha(P/'TRAIN_CAL_LABELS.json') and not frozen['calibration_used_for_selection'] and not frozen['test_seen_before_freeze']
 assert freeze['existing_test_receipts']==0 and freeze['unix_time']<start['unix_time']
 assert freeze['model_sha256']==start['model_sha256']==runner.sha(P/'MODELS_FROZEN_BEFORE_TEST.json')
 for e in es:
  assert e['native_source_sha256']==reg['frozen']['joint_history_native.cpp'] and e['binary_sha256']==reg['binary_sha256'] and e['bridge_sha256']==reg['bridge_sha256'] and e['config_sha256']==reg['config_sha256']
  if worlds[e['world']]['split']=='test':
   bound={}
   for line in Path(e['input']).read_text().splitlines():
    fields=line.split()
    if fields[0]=='M':bound.setdefault(fields[1],[]).append(Q(int(fields[2]),int(fields[3])))
   assert bound=={name:list(map(Q,m['coefficients'])) for name,m in frozen['models'].items()},'test input changed frozen coefficients'
 def get(e):
  key=(e['world'],e['policy'])
  if key not in cache:cache[key]=rows(e)
  return cache[key]
 # Bound memory by clearing each world's raw cache after all its arms.
 for name,w in worlds.items():
  base=em[name,'condition'];br=get(base)
  if w['split']!='test':
   seen=set();chosen=[];cost=0
   for d in [d for d in br if d['event']=='actor_decision' and d['remaining_capacity']>0]:
    spent=16-d['remaining_capacity'];key=(0 if spent<6 else 1 if spent<12 else 2,1 if len(d['candidates'])==1 else 2)
    if key in seen:continue
    seen.add(key);needed=len(d['candidates'])+1
    if cost+needed<=14:chosen.append(d);cost+=needed
   expected={(d['opportunity'],action) for d in chosen for action in ['WAIT']+[str(c['agent']) for c in d['candidates']]}
   present={(r['opportunity'],r['action']) for r in labels if r['world']==name}
   assert expected==present and len(present)==sum(r['world']==name for r in labels),'predeclared complete candidate/WAIT sampling differs'
   selection.append(dict(world=name,opportunities=len(chosen),branches=cost,all_candidates_and_WAIT=True))
  for e in [e for e in es if e['world']==name and e['error'] is None]:
   rs=get(e);repl=check_episode(e,rs)
   for d in repl:
    op=d['opportunity'];assert prefix(br,op)==prefix(rs,op),'pi0 physical/public prefix differs'
    bd=next(z for z in br if z['event']=='actor_decision' and z['opportunity']==op)
    if bd['selected']==d['selected']:assert_same_action_trajectory(br,rs,op);identical+=1
    if e['policy'].startswith('once_'):
     prior=rs[:rs.index(d)];shifted_started=sum(z['event']=='original_RUN' and int(z['id'].rsplit('-',1)[1])>=64 for z in prior)
     changes.append(dict(world=name,policy=e['policy'],opportunity=op,at=d['at'],remaining=d['remaining_capacity'],candidate_count=len(d['candidates']),baseline_choice=bd['selected'],learned_choice=d['selected'],changed=d['selected']!=bd['selected'],scores={c['move']:c['score'] for c in d['candidates']},shift_world=w['shift'],ordinal64_moves_started_before_replacement=shifted_started))
   verified.append(dict(world=name,policy=e['policy'],replacements=len(repl),decision_count=sum(r['event']=='actor_decision' for r in rs)))
  for label in [r for r in labels if r['world']==name]:
   bd=next(d for d in br if d['event']=='actor_decision' and d['opportunity']==label['opportunity'])
   assert label['candidate_count']==len(bd['candidates']) and label['remaining_capacity']==bd['remaining_capacity']
   if label['action']!='WAIT':
    bc=next(c for c in bd['candidates'] if str(c['agent'])==label['action'])
    assert label['features']==bc['features'] and label['move']==bc['move'] and label['source']==bc['agent'],'training row public feature binding'
   ep=em[name,label['policy']];wait=em[name,label['WAIT_policy']];pr=get(ep);wr=get(wait)
   delta=ep['summary']['served']-wait['summary']['served'];gain=flow(w,wr)-flow(w,pr);den=2*w['horizon']*w['N']*4+1
   assert label['whole_service_gain']==delta and Q(label['fixed_first4_time_gain'])==gain and Q(label['target'])==delta+gain/den
   if label['action']=='WAIT':assert Q(label['target'])==0 and label['features'] is None
  cache.clear()
 # Independent augmented weighted least-squares refit, no direct normal equation.
 train=[r for r in labels if r['split']=='train' and r['action']!='WAIT'];fit_checks=[]
 for name,m in frozen['models'].items():
  assert m['lambda_value']==1 and m['unpenalized_intercept']
  assert m['masked_slots']==(list(range(10,18)) if name=='ridge_nohistory' else [20,22,23] if name=='ridge_nobudget' else [])
  mask=set(m['masked_slots']);raw=np.array([[0. if j in mask else float(Q(x)) for j,x in enumerate(r['features'])] for r in train]);weights=np.array([1/r['candidate_count'] for r in train]);y=np.array([float(Q(r['target'])) for r in train]);mean=np.average(raw,axis=0,weights=weights);scale=np.sqrt(np.average((raw-mean)**2,axis=0,weights=weights));scale[scale<1e-12]=1
  assert np.max(abs(mean-m['train_mean']))<1e-12 and np.max(abs(scale-m['train_scale']))<1e-12
  X=np.column_stack([np.ones(len(raw)),(raw-mean)/scale]);penalty=np.eye(25);penalty[0,0]=0
  A=np.vstack([X*np.sqrt(weights)[:,None],penalty]);b=np.r_[y*np.sqrt(weights),np.zeros(25)];beta=np.linalg.lstsq(A,b,rcond=None)[0];coef=np.r_[beta[0]-mean@(beta[1:]/scale),beta[1:]/scale]
  error=float(max(abs(coef-np.array(m['unrounded_raw']))));assert error<1e-8
  assert max(abs(float(Q(q))-raw) for q,raw in zip(m['coefficients'],m['unrounded_raw']))<=0.500001e-9
  assert max(abs(X@beta-np.column_stack([np.ones(len(raw)),raw])@coef))<1e-10
  assert all(Q(m['coefficients'][j+1])==0 and mean[j]==0 and scale[j]==1 for j in mask)
  fit_checks.append(dict(model=name,max_raw_coefficient_error=error,masked_slots=sorted(mask)))
 announced=json.loads((P/'LABEL_SELECTION_BEFORE_PROBES.json').read_text())
 assert {(x['world'],x['policy']) for x in announced['jobs']}=={(r['world'],r['policy']) for r in labels} and sum(x['branches'] for x in selection)==announced['branches']<=84
 runner.write(P/'MATCHED_TAIL_MODEL_AUDIT.json',dict(passed=True,episode_count=len(verified),label_rows=len(labels),full_prefix_includes_budget_and_previous_actions=True,current_WAIT_advances_event=True,same_live_condition_tail=True,same_action_full_trajectory_controls=identical,selection=selection,refits=fit_checks,episodes=verified))
 runner.write(P/'TEST_REPLACEMENT_DECISIONS.json',dict(replacements=changes,changed=sum(x['changed'] for x in changes),by_policy={p:dict(replacements=sum(x['policy']==p for x in changes),changed=sum(x['policy']==p and x['changed'] for x in changes)) for p in ['once_history','once_nohistory','once_nobudget']}))
 print('matched tail/model audit passed',len(verified),len(labels),len(changes),flush=True)
if __name__=='__main__':main()
