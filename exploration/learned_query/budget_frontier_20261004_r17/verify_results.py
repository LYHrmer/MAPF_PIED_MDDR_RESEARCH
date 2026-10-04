#!/usr/bin/env python3
"""Read-only independent reconciliation of saved fold predictions and outcomes."""
from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import hashlib,json
import numpy as np
B=Path(__file__).resolve().parent
def load(name):return json.loads((B/name).read_text())
def require(ok,reason):
 if not ok:raise ValueError(reason)
def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def totals(rows):return dict(tasks=sum(r['tasks'] for r in rows),queries=sum(r['queries'] for r in rows),T_lower=str(sum((F(r['T_lower']) for r in rows),F())),T_upper=str(sum((F(r['T_upper']) for r in rows),F())))
def selection(scores):
 arms=['STOP','C','LD'];m=max(scores[a][0] for a in arms);arms=[a for a in arms if scores[a][0]>=m-1e-6]
 m=min(scores[a][1] for a in arms);arms=[a for a in arms if scores[a][1]<=m+1e-3];m=min(scores[a][2] for a in arms)
 return next(a for a in arms if scores[a][2]<=m+1e-6)
def main():
 data=load('DATASET.json');byworld={r['world']:r for r in data};families={r['family'] for r in data};folds=load('GROUPED_FOLDS.json');pred=load('OOF_PREDICTIONS.json');frozen=load('MODEL_FROZEN.json')
 require(len(families)==12 and len(data)==len(pred)==24 and len(folds)==12,'sample/group inventory')
 require(digest(B/'study.py')==frozen['source_sha256'] and digest(B/'DATASET.json')==frozen['dataset_sha256'],'frozen model binding changed')
 require(frozen['frozen_unix_ns']<int((B/'CAL_DEVELOPMENT_REPLAY.json').stat().st_mtime_ns),'CAL produced before final model freeze')
 index={r['world']:r for r in pred};seen=[];models=0
 for fold in folds:
  held=fold['held_family'];m=fold['model'];expected=families-{held};require(set(m['training_families'])==expected,'outer family leakage or missing group')
  train=[r for r in data if r['family'] in expected and r['features'] is not None];X=np.array([[float(F(x)) for x in r['features']] for r in train]);mean=X.mean(0);scale=X.std(0);scale[scale<1e-12]=1
  require(np.max(abs(mean-np.array(m['mean'])))<1e-12 and np.max(abs(scale-np.array(m['scale'])))<1e-12,'preprocessing fitted beyond training fold')
  require(set(m['training_worlds'])=={r['world'] for r in train},'training row binding')
  for val in fold['inner_validation']:
   selected=[]
   for p in val['choices']:
    r=byworld[p['world']];require(r['family']!=held and set(p['training_families'])==expected-{r['family']},'inner group leakage')
    require(selection(p['scores'])==p['arm'],'inner selected action does not match saved prediction');selected.append(r['outcomes'][p['arm']])
   require(totals(selected)==val['total'],'inner selection aggregation')
  for r in data:
   if r['family']!=held:continue
   seen.append(r['world']);x=np.array([float(F(v)) for v in r['features']]);y=np.r_[1.,(x-mean)/scale]@np.array(m['standardized_coefficients']);scores={'C':y[:3],'LD':y[3:],'STOP':np.zeros(3)};p=index[r['world']]
   require(max(np.max(abs(np.array(p['predictions'][a])-scores[a])) for a in scores)<1e-8,'saved OOF score not produced by heldout standardized model')
   require(selection(scores)==p['ridge'],'OOF decision/tolerance mismatch')
  models+=1
 require(set(seen)==set(byworld) and len(seen)==24,'OOF worlds duplicated/missing')
 results=load('OOF_RESULTS.json')['policies']
 for name,record in results.items():
  choices=record['choices'];require(len(choices)==24,'policy coverage');out=[]
  for c in choices:
   r=byworld[c['world']];o=r['outcomes'][c['arm']];require(all(c[k]==v for k,v in o.items()),'selected arm outcome mismatch')
   if name.startswith('OOF_'):require(index[c['world']][name[4:]]==c['arm'],'OOF table action mismatch')
   else:require(c['arm']==name,'fixed policy switched action')
   out.append(o)
  require(totals(out)==record['overall'],'policy total mismatch')
 fronts=load('ORACLE_FRONTIERS.json');checked=0
 for name,front in fronts.items():
  for state in front['midpoint_Pareto']+front['task_first_query_cap_envelope']:
   selected=[];keys=[]
   for c in state['choices']:
    keys.append(c['context'])
    if name=='episode_start_six_arm_oracle':
     budget,arm=c['action'].split('_');r=next(r for r in data if r['family']==c['context'] and r['budget']==int(budget))
    else:r=byworld[c['context']];arm=c['action']
    selected.append(r['outcomes'][arm])
   require(len(keys)==len(set(keys)),'oracle double-counted context');require(all(state[k]==v for k,v in totals(selected).items()),'oracle state cannot be reconstructed from selected arms')
   if 'query_cap' in state:require(state['queries']<=state['query_cap'],'oracle exceeds cap')
   checked+=1
 # Mutation controls demonstrate the saved-selection checker rejects swapped costs and predictions.
 sample=pred[0];mutated={a:list(v) for a,v in sample['predictions'].items()};bad=next(a for a in ['STOP','C','LD'] if a!=sample['ridge']);mutated[bad][0]=1e9
 require(selection(mutated)!=sample['ridge'],'negative prediction control did not change choice')
 altered=dict(data[0]['outcomes']['C']);altered['queries']+=1;require(totals([altered])!=totals([data[0]['outcomes']['C']]),'negative accounting control ineffective')
 output=dict(passed=True,outer_folds=models,OOF_contexts=24,inner_choices_checked=sum(len(v['choices']) for f in folds for v in f['inner_validation']),oracle_states_reconstructed=checked,negative_controls=2,independent_reconciliation=True,scope='No study module imported: fold normalization, standardized predictions, all selected outcomes and oracle state reconstructions',native_episodes=0)
 (B/'VERIFICATION.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output))
if __name__=='__main__':main()
