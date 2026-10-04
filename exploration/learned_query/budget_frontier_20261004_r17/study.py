#!/usr/bin/env python3
"""Offline-only frozen three-tail study. Never launches native or reads TEST."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import hashlib,json,time,sys
import numpy as np

HERE=Path(__file__).resolve().parent
R13=HERE.parent/'late_budget_choice_20261004_r13';R16=HERE.parent/'stop_value_20261004_r16'
ARMS=['C','LD','STOP'];TIE=['STOP','C','LD'];LAMBDAS=[1,10,100]
FEATURES=['history_survival_release_probability','prior_survival_release_probability','public_target_age_over_2','sum_inverse_remaining_route_items_times_owners','minimum_remaining_route_items_over_64','claim_fraction','other_visible_fraction','remaining_budget_over_16','remaining_horizon_fraction','probability_times_feature3']
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text())
def write(name,x):(HERE/name).write_text(json.dumps(x,indent=2)+'\n')
def require(ok,reason):
 if not ok:raise ValueError(reason)
def iv(x):return Q(x['lower'],x.get('denominator',1000000)),Q(x['upper'],x.get('denominator',1000000))
def total(rows):
 return dict(tasks=sum(x['tasks'] for x in rows),queries=sum(x['queries'] for x in rows),T_lower=str(sum((Q(x['T_lower']) for x in rows),Q())),T_upper=str(sum((Q(x['T_upper']) for x in rows),Q())))
def robust_best(candidates):
 candidates=[c for c in candidates if c['total']['tasks']==max(x['total']['tasks'] for x in candidates)]
 survivors=[c for c in candidates if not any(Q(d['total']['T_upper'])<Q(c['total']['T_lower']) for d in candidates)]
 return min(survivors,key=lambda c:(c['total']['queries'],c['tie']))
def select_observed(rows):
 return robust_best([dict(arm=a,total=total([r['outcomes'][a] for r in rows]),tie=TIE.index(a)) for a in ARMS])['arm']
def canonical(r):
 r=dict(r);r.pop('policy',None)
 if r['event']=='joint_summary':r.pop('native_checks',None)
 return json.dumps(r,sort_keys=True,separators=(',',':'))
def raw_outcome(path,world):
 require('test' not in str(path).lower(),'TEST access forbidden')
 wanted={t['task'] for a in world['robots'] for t in a['tasks'][:4]};H=Q(world['horizon']);times={};prefix=hashlib.sha256();gate=None;queries=0;after_queries=0;summary=None
 for line in Path(path).open():
  r=json.loads(line);kind=r['event']
  if kind=='macro_choice':require(gate is None,'duplicate gate');gate=r
  elif gate is None:prefix.update((canonical(r)+'\n').encode())
  if kind=='task_service':require(r['task'] not in times,'duplicate task');times[r['task']]=iv(r['at'])
  if kind=='certified_POSITION_committed':queries+=1;after_queries+=int(gate is not None)
  if kind=='joint_summary':summary=r
 require(summary is not None and not summary['deadlock'] and iv(summary['last_clock'])==(H,H),'incomplete horizon')
 require(summary['served']==len(times) and summary['queries']==queries<=world['budget'],'raw totals differ')
 out=dict(tasks=len(times),queries=queries,T_lower=str(sum((times[t][0] if t in times else H for t in wanted),Q())),T_upper=str(sum((times[t][1] if t in times else H for t in wanted),Q())))
 return out,gate,prefix.hexdigest(),after_queries
def dataset_train():
 reg=read(HERE/'REGISTRATION.json')
 for path,h in reg['sources'].items():require(sha(path)==h,'frozen input changed '+path)
 labels={(r['world'],r['option']):r for r in read(R13/'TRAIN_CAL_LABELS.json') if r['split']=='train'}
 worlds={w['name']:w for w in read(R16/'REGISTRATION.json')['train_worlds']};pairs=read(R16/'TRAIN_PAIRS.json');data=[];checks=[]
 fields=['at','opportunity','initial_capacity','remaining_capacity','spent','target_agent','target_move','features']
 for pair in pairs:
  require(pair['split']=='train' and pair['prefix_equal'] and pair['input_equal'],'R16 matching not validated')
  w=worlds[pair['world']];outcomes={};raws={};prefixes=[];gates=[];inputs=[]
  for arm in ARMS:
   old=labels[pair['world'],arm] if arm in ['C','LD'] else pair[arm]
   raw=R13/'runs'/(pair['world']+'__macro_'+arm+'.jsonl') if arm in ['C','LD'] else Path(old['raw'])
   receipt=read(raw.with_suffix('.receipt.json'));require(receipt['error'] is None,'old failed arm')
   require(sha(raw)==old['raw_sha256']==receipt['raw_sha256'],'raw pin mismatch')
   require(sha(receipt['input'])==receipt['input_sha256'],'input pin mismatch')
   require(sha(receipt['planner'])==receipt['planner_sha256'],'planner pin mismatch')
   out,gate,pref,post=raw_outcome(raw,w)
   require(all(out[k]==old[k] for k in out),'raw label reconstruction mismatch '+pair['world']+arm)
   if arm=='STOP' and gate:require(post==0 and out['queries']==gate['spent'],'STOP bought after gate')
   outcomes[arm]=out;raws[arm]=dict(path=str(raw),sha256=sha(raw),receipt_sha256=sha(raw.with_suffix('.receipt.json')),planner_sha256=receipt['planner_sha256'],input_sha256=receipt['input_sha256'])
   prefixes.append(pref);gates.append({k:gate[k] for k in fields} if gate else None);inputs.append(receipt['input_sha256'])
  require(len(set(prefixes))==len(set(inputs))==1 and gates[0]==gates[1]==gates[2],'three-arm prefix/input/gate differs')
  require(prefixes[0]==pair['C']['prefix_sha256']==pair['STOP']['prefix_sha256'],'old prefix receipt mismatch')
  gate=gates[0];features=gate['features'] if gate else None
  require(features==labels[pair['world'],'C']['features']==labels[pair['world'],'LD']['features'],'public gate feature binding')
  data.append(dict(world=pair['world'],family=pair['family_key'],budget=pair['budget'],map=pair['map'],features=features,gate=gate,outcomes=outcomes,raws=raws))
  checks.append(dict(world=pair['world'],three_arm_prefix_sha256=prefixes[0],input_sha256=inputs[0],raws=raws))
 require(len(data)==24 and len({r['family'] for r in data})==12,'TRAIN inventory')
 for family in {r['family'] for r in data}:require(sorted(r['budget'] for r in data if r['family']==family)==[8,16],'family budgets split/missing')
 write('DATASET_AUDIT.json',dict(passed=True,contexts=24,families=12,arms=72,checks=checks,new_native_episodes=0,TEST_files_read=0));write('DATASET.json',data)
 return data
def fit(rows,lam):
 rows=[r for r in rows if r['features'] is not None];X=np.array([[float(Q(x)) for x in r['features']] for r in rows]);mean=X.mean(0);scale=X.std(0);scale[scale<1e-12]=1.;Z=np.column_stack([np.ones(len(X)),(X-mean)/scale]);Y=[]
 for r in rows:
  base=r['outcomes']['STOP'];bt=(Q(base['T_lower'])+Q(base['T_upper']))/2;y=[]
  for arm in ['C','LD']:
   o=r['outcomes'][arm];y.extend([o['tasks']-base['tasks'],float((Q(o['T_lower'])+Q(o['T_upper']))/2-bt),o['queries']-base['queries']])
  Y.append(y)
 penalty=np.eye(11)*lam;penalty[0,0]=0;beta=np.linalg.solve(.5*Z.T@Z+penalty,.5*Z.T@np.array(Y));raw=beta[1:]/scale[:,None];intercept=beta[0]-mean@raw
 return dict(lambda_value=lam,feature_names=FEATURES,mean=mean.tolist(),scale=scale.tolist(),standardized_coefficients=beta.tolist(),raw_coefficients=np.vstack([intercept,raw]).tolist(),output_order=[a+'_'+k for a in ['C','LD'] for k in ['tasks_minus_STOP','T_minus_STOP','queries_minus_STOP']],training_worlds=[r['world'] for r in rows],training_families=sorted({r['family'] for r in rows}),weight_per_context=.5)
def predict(model,row):
 if row['features'] is None:return 'C',dict(C=[0,0,0],LD=[0,0,0],STOP=[0,0,0])
 x=np.array([1.]+[float(Q(v)) for v in row['features']]);p=x@np.array(model['raw_coefficients']);scores={'C':p[:3].tolist(),'LD':p[3:].tolist(),'STOP':[0.,0.,0.]}
 candidates=list(TIE);best=max(scores[a][0] for a in candidates);candidates=[a for a in candidates if scores[a][0]>=best-1e-6]
 best=min(scores[a][1] for a in candidates);candidates=[a for a in candidates if scores[a][1]<=best+1e-3]
 best=min(scores[a][2] for a in candidates);candidates=[a for a in candidates if scores[a][2]<=best+1e-6]
 return candidates[0],scores
def choose_lambda(rows):
 reports=[]
 for lam in LAMBDAS:
  choices=[];out=[]
  for family in sorted({r['family'] for r in rows}):
   train=[r for r in rows if r['family']!=family];test=[r for r in rows if r['family']==family];model=fit(train,lam)
   require(family not in model['training_families'],'inner leakage')
   for r in test:
    arm,scores=predict(model,r);out.append(r['outcomes'][arm]);choices.append(dict(world=r['world'],held_family=family,arm=arm,scores=scores,training_families=model['training_families']))
  reports.append(dict(lambda_value=lam,total=total(out),tie=-lam,choices=choices))
 return robust_best(reports)['lambda_value'],reports
def fit_rules(rows):
 constant=select_observed(rows);lookup={str(b):select_observed([r for r in rows if r['budget']==b]) for b in [8,16]}
 candidates=[dict(feature=None,threshold=None,left=constant,right=constant,total=total([r['outcomes'][constant] for r in rows]),tie=0)]
 grid=[(j,Q(t)) for j in [0,8] for t in ['1/4','1/2','3/4']]+[(7,Q('3/8'))]
 for i,(feature,threshold) in enumerate(grid,1):
  left=[r for r in rows if r['features'] is not None and Q(r['features'][feature])<=threshold];right=[r for r in rows if r['features'] is not None and Q(r['features'][feature])>threshold]
  if min(len({r['family'] for r in side}) for side in [left,right])<2:continue
  la,ra=select_observed(left),select_observed(right);out=[]
  for r in rows:
   arm='C' if r['features'] is None else la if Q(r['features'][feature])<=threshold else ra;out.append(r['outcomes'][arm])
  candidates.append(dict(feature=feature,threshold=str(threshold),left=la,right=ra,total=total(out),tie=i))
 return dict(constant=constant,budget_lookup=lookup,stump=robust_best(candidates),candidate_stumps=candidates)
def rule_predict(model,row):
 s=model['stump'];stump='C' if row['features'] is None else s['left'] if s['feature'] is None or Q(row['features'][s['feature']])<=Q(s['threshold']) else s['right']
 return dict(train_constant=model['constant'],budget_lookup=model['budget_lookup'][str(row['budget'])],public_threshold=stump)
def policy_totals(data,choices):
 out={}
 for name,select in choices.items():
  selected=[dict(world=r['world'],family=r['family'],budget=r['budget'],arm=select[r['world']],**r['outcomes'][select[r['world']]]) for r in data]
  out[name]=dict(overall=total(selected),by_budget={str(b):total([r for r in selected if r['budget']==b]) for b in [8,16]},by_family={f:total([r for r in selected if r['family']==f]) for f in sorted({r['family'] for r in data})},choices=selected)
 return out
def dominance(a,b):
 # Conservative interval dominance: definitely no larger time, with strict gain.
 return a['tasks']>=b['tasks'] and a['queries']<=b['queries'] and Q(a['T_upper'])<=Q(b['T_lower']) and (a['tasks']>b['tasks'] or a['queries']<b['queries'] or Q(a['T_upper'])<Q(b['T_lower']))
def pareto_totals(summaries):
 return {scope:[name for name,s in summaries.items() if not any(other!=name and dominance(t[scope],s[scope]) for other,t in summaries.items())] for scope in ['overall']}
def frontier(groups):
 states={(0,0):(Q(),Q(),[])}
 for key,options in groups:
  next_states={}
  for (q,n),(lo,hi,path) in states.items():
   for name,o in options:
    k=(q+o['queries'],n+o['tasks']);v=(lo+Q(o['T_lower']),hi+Q(o['T_upper']),path+[dict(context=key,action=name)])
    if k not in next_states or (v[0]+v[1],str(v[2]))<(next_states[k][0]+next_states[k][1],str(next_states[k][2])):next_states[k]=v
  states=next_states
 candidates=[dict(queries=q,tasks=n,T_lower=str(v[0]),T_upper=str(v[1]),choices=v[2]) for (q,n),v in sorted(states.items())]
 # Midpoint frontier is exact-rational; interval uncertainty is exposed separately.
 mid=lambda x:(Q(x['T_lower'])+Q(x['T_upper']))/2
 result=[]
 for c in candidates:
  if not any(d['queries']<=c['queries'] and d['tasks']>=c['tasks'] and mid(d)<=mid(c) and (d['queries']<c['queries'] or d['tasks']>c['tasks'] or mid(d)<mid(c)) for d in candidates):result.append(c)
 envelope=[]
 for q in sorted({c['queries'] for c in candidates}):
  options=[dict(total={k:c[k] for k in ['tasks','queries','T_lower','T_upper']},tie=0,state=c) for c in candidates if c['queries']<=q];envelope.append(dict(query_cap=q,**robust_best(options)['state']))
 return dict(scope='Noncausal observed finite-action oracle, never a policy evaluation',state_count=len(states),midpoint_Pareto=result,task_first_query_cap_envelope=envelope,DP_rule='minimum exact midpoint T for each exact (queries,tasks); raw intervals retained')
def descriptive_cal(model,rules):
 labels={(r['world'],r['option']):r for r in read(R13/'TRAIN_CAL_LABELS.json') if r['split']=='calibration'};data=[]
 for p in read(R16/'CAL_PAIRS.json'):
  outcomes={a:{k:(labels[p['world'],a] if a=='LD' else p[a])[k] for k in ['tasks','queries','T_lower','T_upper']} for a in ARMS}
  data.append(dict(world=p['world'],family=p['family_key'],budget=p['budget'],features=p['gate']['features'] if p['gate'] else None,outcomes=outcomes))
 choices={a:{r['world']:a for r in data} for a in ARMS};choices['frozen_ridge']={r['world']:predict(model,r)[0] for r in data}
 for name in ['train_constant','budget_lookup','public_threshold']:choices[name]={r['world']:rule_predict(rules,r)[name] for r in data}
 return dict(scope='Previously used development CAL, no independent generalization claim and no tuning',policies=policy_totals(data,choices),cal_pairs_sha256=sha(R16/'CAL_PAIRS.json'))
def main():
 require(not (HERE/'MODEL_FROZEN.json').exists(),'model already frozen; use replay.py for recomputation, never silently refit')
 start=time.time_ns();data=dataset_train();families=sorted({r['family'] for r in data});folds=[];oof=[]
 for family in families:
  train=[r for r in data if r['family']!=family];test=[r for r in data if r['family']==family];lam,inner=choose_lambda(train);model=fit(train,lam);rules=fit_rules(train)
  folds.append(dict(held_family=family,lambda_value=lam,inner_validation=inner,model=model,rules=rules))
  for r in test:
   arm,scores=predict(model,r);oof.append(dict(world=r['world'],family=family,budget=r['budget'],ridge=arm,predictions=scores,**rule_predict(rules,r)))
 write('GROUPED_FOLDS.json',folds);write('OOF_PREDICTIONS.json',oof)
 choices={a:{r['world']:a for r in data} for a in ARMS}
 for name in ['ridge','train_constant','budget_lookup','public_threshold']:choices['OOF_'+name]={r['world']:r[name] for r in oof}
 summaries=policy_totals(data,choices);write('OOF_RESULTS.json',dict(policies=summaries,empirical_interval_Pareto=pareto_totals(summaries),families=12,contexts=24))
 lam,validation=choose_lambda(data);model=fit(data,lam);rules=fit_rules(data);frozen=dict(frozen_unix_ns=time.time_ns(),model=model,rules=rules,lambda_selection=validation,registration_sha256=sha(HERE/'REGISTRATION.json'),dataset_sha256=sha(HERE/'DATASET.json'),source_sha256=sha(Path(__file__)),new_native_episodes=0,scope='All TRAIN final model; no independent TEST result')
 write('MODEL_FROZEN.json',frozen)
 write('CAL_DEVELOPMENT_REPLAY.json',descriptive_cal(model,rules))
 final_choices={r['world']:predict(model,r)[0] for r in data};write('FINAL_TRAIN_RESUBSTITUTION.json',policy_totals(data,{'final_model_resubstitution':final_choices}))
 fronts={'same_gate_all':frontier([(r['world'],[(a,r['outcomes'][a]) for a in ARMS]) for r in data])}
 for budget in [8,16]:fronts['same_gate_B'+str(budget)]=frontier([(r['world'],[(a,r['outcomes'][a]) for a in ARMS]) for r in data if r['budget']==budget])
 fronts['episode_start_six_arm_oracle']=frontier([(f,[(str(r['budget'])+'_'+a,r['outcomes'][a]) for r in data if r['family']==f for a in ARMS]) for f in families]);write('ORACLE_FRONTIERS.json',fronts)
 errors={};lookup={r['world']:r for r in data}
 for a in ['C','LD']:
  diffs=[]
  for pred in oof:
   row=lookup[pred['world']];base=row['outcomes']['STOP'];o=row['outcomes'][a];actual=[o['tasks']-base['tasks'],float((Q(o['T_lower'])+Q(o['T_upper'])-Q(base['T_lower'])-Q(base['T_upper']))/2),o['queries']-base['queries']];diffs.append(np.array(pred['predictions'][a])-actual)
  values=np.array(diffs);errors[a]=dict(MAE=np.abs(values).mean(0).tolist(),RMSE=np.sqrt((values**2).mean(0)).tolist(),order=['tasks','restricted_T','queries'])
 write('MODEL_DIAGNOSTICS.json',dict(OOF_errors=errors,outer_lambda_counts=dict(Counter(x['lambda_value'] for x in folds)),final_lambda=lam,feature_names=FEATURES))
 write('COMPLETION.json',dict(started_unix_ns=start,finished_unix_ns=time.time_ns(),model_sha256=sha(HERE/'MODEL_FROZEN.json'),source_sha256=sha(Path(__file__)),new_native_episodes=0,TEST_files_read=0))
 print(json.dumps({name:r['overall'] for name,r in summaries.items()},indent=2))
if __name__=='__main__':main()
