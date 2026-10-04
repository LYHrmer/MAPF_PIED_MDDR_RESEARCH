"""Preregistered complete-macro labels, TRAIN ridge and shared CAL threshold."""
from pathlib import Path
from fractions import Fraction as Q
import json,time,numpy as np
import runner
P=runner.HERE;OPTIONS=['C','LD'];VARIANTS=['full','no_history_prob'];GRID=[Q(0),Q(1,10000),Q(1,1000),Q(1,100),Q(1,10),None]
def outcome(w,e):
 wanted={t['task'] for a in w['robots'] for t in a['tasks'][:4]};services={};gate=None
 for line in Path(e['raw']).open():
  r=json.loads(line)
  if r['event']=='task_service':services[r['task']]=r['at']
  elif r['event']=='macro_choice':assert gate is None;gate=r
 low=sum((Q(services[t]['lower'],1000000) if t in services else Q(w['horizon']) for t in wanted),Q(0));high=sum((Q(services[t]['upper'],1000000) if t in services else Q(w['horizon']) for t in wanted),Q(0))
 assert e['summary']['served']==len(services)
 return dict(tasks=len(services),T_lower=str(low),T_upper=str(high),queries=e['summary']['queries'],gate=gate,raw_sha256=e['raw_sha256'])
def labels():
 reg=json.loads((P/'REGISTRATION.json').read_text());rows=[]
 for w in reg['worlds']:
  if w['split']=='test':continue
  observed={}
  for option in OPTIONS:
   e=json.loads((P/'runs'/(w['name']+'__macro_'+option+'.receipt.json')).read_text());assert e['error'] is None;observed[option]=outcome(w,e)
  base=observed['C']
  for option in OPTIONS:
   out=observed[option];gate=out.pop('gate');features=gate['features'] if gate else None
   baseline_gate=base.get('gate')
   if option=='C':saved_features=features
   assert features==saved_features,'complete macro common gate features differ'
   task=out['tasks']-base['tasks'];time_gain=(Q(base['T_lower'])+Q(base['T_upper'])-Q(out['T_lower'])-Q(out['T_upper']))/2/16385
   if features is None:assert task==0 and time_gain==0 and out['queries']==base['queries'],'no-gate tails differ'
   rows.append(dict(world=w['name'],family_key=w['family_key'],map=w['map_name'],seed=w['seed'],scenario=w['scenario_identity'],offset=w['scenario_offset'],split=w['split'],budget=w['budget'],option=option,policy='macro_'+option,features=features,weight='1/2',task_target=str(task),time_target=str(time_gain),T_gain_lower=str(Q(base['T_lower'])-Q(out['T_upper'])),T_gain_upper=str(Q(base['T_upper'])-Q(out['T_lower'])),**out))
 runner.write(P/'TRAIN_CAL_LABELS.json',rows);return rows
def masks(variant):return [0,9] if variant=='no_history_prob' else []
def train(rows):
 models={}
 for variant in VARIANTS:
  mask=masks(variant)
  for option in OPTIONS[1:]:
   rs=[r for r in rows if r['split']=='train' and r['option']==option and r['features'] is not None]
   if not rs:
    for head in ['tasks','time']:models[variant+'_'+option+'_'+head]=dict(coefficients=['0']*11,unrounded_raw=[0.]*11,standardized_coefficients=[0.]*11,train_mean=[0.]*10,train_scale=[1.]*10,lambda_value=1,unpenalized_intercept=True,masked_slots=mask,train_rows=0,bindings=[],fallback='preregistered no TRAIN gate: zero advantage and C default')
    continue
   raw=np.array([[0. if j in mask else float(Q(x)) for j,x in enumerate(r['features'])] for r in rs]);weights=np.array([float(Q(r['weight'])) for r in rs]);mean=np.average(raw,axis=0,weights=weights);scale=np.sqrt(np.average((raw-mean)**2,axis=0,weights=weights));scale[scale<1e-12]=1;X=np.column_stack([np.ones(len(raw)),(raw-mean)/scale]);penalty=np.eye(11);penalty[0,0]=0
   for head in ['tasks','time']:
    y=np.array([float(Q(r['task_target' if head=='tasks' else 'time_target'])) for r in rs]);beta=np.linalg.solve(X.T@(weights[:,None]*X)+penalty,X.T@(weights*y));rawcoef=np.r_[beta[0]-mean@(beta[1:]/scale),beta[1:]/scale];quant=[str(Q(str(round(float(x),9)))) for x in rawcoef];assert np.max(abs(X@beta-np.column_stack([np.ones(len(raw)),raw])@rawcoef))<1e-10
    assert all(Q(quant[j+1])==0 and mean[j]==0 and scale[j]==1 for j in mask)
    models[variant+'_'+option+'_'+head]=dict(coefficients=quant,unrounded_raw=rawcoef.tolist(),standardized_coefficients=beta.tolist(),train_mean=mean.tolist(),train_scale=scale.tolist(),lambda_value=1,unpenalized_intercept=True,masked_slots=mask,train_rows=len(rs),bindings=[dict(world=r['world'],family_key=r['family_key'],budget=r['budget'],option=option,weight=r['weight']) for r in rs])
 return models
def scores(features,variant,models):
 if features is None:return [Q(0)]*2
 source=variant;mask=set(masks(variant));x=[Q(0) if j in mask else Q(v) for j,v in enumerate(features)];out=[Q(0)]
 for option in OPTIONS[1:]:
  value=Q(0)
  for head in ['tasks','time']:
   c=list(map(Q,models[source+'_'+option+'_'+head]['coefficients']));value+=c[0]+sum((a*b for a,b in zip(c[1:],x)),Q(0))
  out.append(value)
 return out
def select(values,margin):
 eligible=[i for i in range(1,2) if margin is not None and values[i]>margin]
 return OPTIONS[min(eligible,key=lambda i:(-values[i],i))] if eligible else 'C'
def total(rows):return dict(tasks=sum(r['tasks'] for r in rows),T_lower=str(sum((Q(r['T_lower']) for r in rows),Q(0))),T_upper=str(sum((Q(r['T_upper']) for r in rows),Q(0))),queries=sum(r['queries'] for r in rows))
def robust_best(candidates,tie):
 top=[r for r in candidates if r['tasks']==max(x['tasks'] for x in candidates)];undominated=[r for r in top if not any(Q(other['T_upper'])<Q(r['T_lower']) for other in top)];return min(undominated,key=lambda r:(r['queries'],tie(r)))
def calibrate(rows,models):
 cal=[r for r in rows if r['split']=='calibration'];worlds=sorted({r['world'] for r in cal});grid=[]
 for i,margin in enumerate(GRID):
  selections=[];selected=[]
  for world in worlds:
   context=[r for r in cal if r['world']==world];values=scores(context[0]['features'],'full',models);option=select(values,margin);row=next(r for r in context if r['option']==option);selected.append(row);selections.append(dict(world=world,selected_option=option,scores=[str(v) for v in values],raw_sha256=row['raw_sha256']))
  grid.append(dict(index=i,margin=None if margin is None else str(margin),selections=selections,**total(selected)))
 winner=robust_best(grid,lambda r:-r['index']);lookup={};lookup_diagnostics={}
 for budget in [8,16]:
  choices=[dict(option=o,index=i,**total([r for r in rows if r['split']=='train' and r['budget']==budget and r['option']==o])) for i,o in enumerate(OPTIONS)];best=robust_best(choices,lambda r:r['index']);lookup[str(budget)]=best['option'];lookup_diagnostics[str(budget)]=choices
 return dict(shared_margin=winner['margin'],selected_grid_index=winner['index'],grid=grid,used_variant='full',shared_by=['full','no_history_prob'],budget_lookup=lookup,lookup_candidates=lookup_diagnostics,lookup_split='train',time_tie_rule='max tasks, interval-undominated T set, min queries, larger margin or fixed C-before-LD index')
def main():
 assert not any('test_' in p.name for p in (P/'runs').glob('*.receipt.json'))
 reg=json.loads((P/'REGISTRATION.json').read_text())
 for name,digest in reg['frozen'].items():assert runner.sha(P/name)==digest,('registered core changed before fit',name)
 tc=json.loads((P/'TC_RECEIPT.json').read_text());assert tc['complete'] and tc['native_episodes']==64 and tc['failed']==0
 audited=[json.loads(p.read_text()) for p in (P/'audits').glob('*.json')];assert len(audited)==64 and all(a['status']=='passed' for a in audited),'original64 physics audits must precede fit'
 import prefix_audit
 prefix_audit.main()
 runner.write(P/'FIT_START.json',dict(unix_time_ns=time.time_ns(),registration_sha256=runner.sha(P/'REGISTRATION.json'),TC_receipt_sha256=runner.sha(P/'TC_RECEIPT.json'),TC_latest_finish_ns=max(json.loads(p.read_text())['finished_unix_ns'] for p in (P/'runs').glob('*.receipt.json'))))
 rows=labels();models=train(rows);cal=calibrate(rows,models);parameters={k:dict(coefficients=v['coefficients']) for k,v in models.items()};parameters['shared_margin']=dict(coefficients=['1' if cal['shared_margin'] is None else '0',cal['shared_margin'] or '0'])
 for budget,option in cal['budget_lookup'].items():parameters['budget_lookup_'+budget]=dict(coefficients=[str(OPTIONS.index(option))])
 runner.write(P/'MODELS_FROZEN_BEFORE_TEST.json',dict(models=models,calibration=cal,parameters=parameters,labels_sha256=runner.sha(P/'TRAIN_CAL_LABELS.json'),prefix_audit_sha256=runner.sha(P/'PREFIX_BEFORE_FIT.json'),registration_sha256=runner.sha(P/'REGISTRATION.json'),TRAIN_only_standardization=True,no_TEST_outcomes_seen=True,option_order=OPTIONS,split_families=dict(train=12,calibration=4,test=8)))
 runner.write(P/'MODEL_FREEZE_RECEIPT.json',dict(unix_time=time.time(),unix_time_ns=time.time_ns(),fit_start_sha256=runner.sha(P/'FIT_START.json'),model_sha256=runner.sha(P/'MODELS_FROZEN_BEFORE_TEST.json'),labels_sha256=runner.sha(P/'TRAIN_CAL_LABELS.json'),existing_test_receipts=0,TC_receipts=len(list((P/'runs').glob('*.receipt.json')))))
 print('frozen',len(models),'heads, shared margin',cal['shared_margin'],'TRAIN lookup',cal['budget_lookup'],flush=True)
if __name__=='__main__':main()
