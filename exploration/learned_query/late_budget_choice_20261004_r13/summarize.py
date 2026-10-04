"""Complete frozen deployment outcomes; paired budgets remain within-family settings."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,csv,hashlib
import runner
P=runner.HERE
def digest(value):return hashlib.sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def read(w,e,models):
 wanted={t['task'] for a in w['robots'] for t in a['tasks'][:4]};service=[];gate=None;changes=[];queries=[];maxskip=0;counts=Counter();last=None
 for line in Path(e['raw']).open():
  r=json.loads(line);counts[r['event']]+=1
  if r['event']=='task_service':service.append(r)
  elif r['event']=='macro_choice':assert gate is None;gate=r
  elif r['event']=='actor_decision':
   last=r
   if r['intervention_index']:changes.append(r)
  elif r['event']=='certified_POSITION_committed':queries.append(dict(move=r['move'],at=r['at']))
  elif r['event']=='public_candidate_visibility':maxskip=max(maxskip,len(r['skip_state']))
 times={r['task']:r['at'] for r in service};low=sum((Q(times[t]['lower'],1000000) if t in times else Q(128) for t in wanted),Q(0));high=sum((Q(times[t]['upper'],1000000) if t in times else Q(128) for t in wanted),Q(0));tasks=len(service)
 assert tasks==e['summary']['served'] and len(queries)==e['summary']['queries']
 selected=gate['selected_option'] if gate else ('W' if e['policy']=='WAIT' else 'C')
 planned=('LD' if e['policy'] in ['macro_LD','alwaysLD'] else models['calibration']['budget_lookup'][str(w['budget'])] if e['policy']=='budget_lookup' else selected);requested=2 if planned=='LD' else 0
 return dict(world=w['name'],family_key=w['family_key'],map=w['map_name'],seed=w['seed'],scenario=w['scenario_identity'],offset=w['scenario_offset'],split=w['split'],budget=w['budget'],policy=e['policy'],tasks=tasks,queries=len(queries),remaining=w['budget']-len(queries),T_lower=str(low),T_upper=str(high),J_lower=str(Q(tasks)-high/16385),J_upper=str(Q(tasks)-low/16385),service_sha256=digest(service),gate=gate,selected_option=selected,planned_option=planned,late_gate_reached=gate is not None,requested_interventions=requested,actual_interventions=len(changes),interventions=changes,unreached_interventions=requested-len(changes),unreached_observation=None if requested==len(changes) else ('no_qualifying_late_gate_through_H' if gate is None else 'no_qualifying_second_trigger_before_budget_exhaustion' if len(queries)==w['budget'] else 'no_qualifying_second_trigger_through_H'),query_occurrences=queries,max_simultaneous_skip=maxskip,skip_installs=counts['public_SKIP_installed'],skip_clears=counts['public_SKIP_cleared_normal_END'],inference_calls=gate['inference_calls'] if gate else 0,selector_scoring_ns=gate['inference_ns'] if gate else 0,error=e['error'])
def delta(a,b):
 low=Q(b['T_lower'])-Q(a['T_upper']);high=Q(b['T_upper'])-Q(a['T_lower']);jl=Q(a['J_lower'])-Q(b['J_upper']);ju=Q(a['J_upper'])-Q(b['J_lower'])
 return dict(tasks=a['tasks']-b['tasks'],queries=a['queries']-b['queries'],T_gain_lower=str(low),T_gain_upper=str(high),J_gain_lower=str(jl),J_gain_upper=str(ju),robust_J_improvement=jl>0,robust_J_worse=ju<0,service_records_equal=a.get('service_sha256')==b.get('service_sha256') if 'service_sha256' in a else None)
def total(rows):return dict(tasks=sum(r['tasks'] for r in rows),queries=sum(r['queries'] for r in rows),T_lower=str(sum((Q(r['T_lower']) for r in rows),Q(0))),T_upper=str(sum((Q(r['T_upper']) for r in rows),Q(0))),J_lower=str(sum((Q(r['J_lower']) for r in rows),Q(0))),J_upper=str(sum((Q(r['J_upper']) for r in rows),Q(0))))
def main():
 receipt=json.loads((P/'RECEIPT.json').read_text());assert receipt['complete'];models=json.loads((P/'MODELS_FROZEN_BEFORE_TEST.json').read_text());reg=json.loads((P/'REGISTRATION.json').read_text());worlds={w['name']:w for w in reg['worlds']};es=[json.loads(p.read_text()) for p in (P/'runs').glob('*.receipt.json')];rows=[]
 for e in es:
  assert e['error'] is None,'retain execution failure; do not invent outcome'
  rows.append(read(worlds[e['world']],e,models))
 lookup={(r['world'],r['policy']):r for r in rows};test=[r for r in rows if r['split']=='test'];totals={};families=[]
 for r in test:
  for ref in ['condition','alwaysLD','WAIT','budget_lookup']:r['vs_'+ref]=delta(r,lookup[r['world'],ref])
  base={x['move'] for x in lookup[r['world'],'condition']['query_occurrences']};actual={x['move'] for x in r['query_occurrences']};r['new_query_identities']=sorted(actual-base);r['omitted_query_identities']=sorted(base-actual)
 for policy in reg['test_policies']:
  selected=[r for r in test if r['policy']==policy];a=total(selected);a['macro_choices']=dict(Counter(r['selected_option'] or 'NO_GATE' for r in selected));a['late_gates']=sum(r['late_gate_reached'] for r in selected);a['no_late_gates']=sum(not r['late_gate_reached'] for r in selected);a['inference_calls']=sum(r['inference_calls'] for r in selected);a['interventions']=sum(r['actual_interventions'] for r in selected);a['unreached_interventions']=sum(r['unreached_interventions'] for r in selected)
  for ref in ['condition','alwaysLD','WAIT','budget_lookup']:a['vs_'+ref]=delta(a,total([r for r in test if r['policy']==ref]))
  totals[policy]=a
  for family in sorted({r['family_key'] for r in test}):
   a=total([r for r in selected if r['family_key']==family]);families.append(dict(family_key=family,policy=policy,**a,vs_condition=delta(a,total([r for r in test if r['family_key']==family and r['policy']=='condition'])),vs_alwaysLD=delta(a,total([r for r in test if r['family_key']==family and r['policy']=='alwaysLD'])),vs_WAIT=delta(a,total([r for r in test if r['family_key']==family and r['policy']=='WAIT'])),vs_budget_lookup=delta(a,total([r for r in test if r['family_key']==family and r['policy']=='budget_lookup']))))
 ablations={}
 for policy in ['no_history_prob']:
  rr=[r for r in test if r['policy']==policy];ablations[policy]=dict(macro_disagreements_vs_full=sum(r['selected_option']!=lookup[r['world'],'full']['selected_option'] for r in rr),service_changes_vs_full=sum(r['service_sha256']!=lookup[r['world'],'full']['service_sha256'] for r in rr),task_difference_vs_full=sum(r['tasks']-lookup[r['world'],'full']['tasks'] for r in rr))
 models=json.loads((P/'MODELS_FROZEN_BEFORE_TEST.json').read_text());labels=json.loads((P/'TRAIN_CAL_LABELS.json').read_text());ld={}
 for split in ['train','calibration']:
  for option in reg['options']:
   selected=[r for r in labels if r['split']==split and r['option']==option];ld[split+'_'+option]=dict(rows=len(selected),gate_rows=sum(r['features'] is not None for r in selected),task_targets=dict(Counter(r['task_target'] for r in selected)),time_target_signs=dict(Counter('positive' if Q(r['time_target'])>0 else 'negative' if Q(r['time_target'])<0 else 'zero' for r in selected)))
 budget_results=[]
 for b in [8,16]:
  for policy in reg['test_policies']:
   chosen=total([r for r in test if r['budget']==b and r['policy']==policy]);entry=dict(budget=b,policy=policy,**chosen)
   for ref in ['condition','alwaysLD','WAIT','budget_lookup']:entry['vs_'+ref]=delta(chosen,total([r for r in test if r['budget']==b and r['policy']==ref]))
   budget_results.append(entry)
 runner.write(P/'RESULTS.json',rows);runner.write(P/'FAMILY_RESULTS.json',families);runner.write(P/'BUDGET_RESULTS.json',budget_results)
 fields=['world','family_key','split','map','scenario','offset','seed','budget','policy','selected_option','planned_option','late_gate_reached','tasks','queries','remaining','T_lower','T_upper','J_lower','J_upper','requested_interventions','actual_interventions','unreached_interventions','inference_calls','selector_scoring_ns','skip_installs','skip_clears','service_sha256','error']
 with (P/'RESULTS.csv').open('x') as f:
  writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');writer.writeheader();writer.writerows(rows)
 summary=dict(native_episodes=len(rows),failed=receipt['failed'],TRAIN_CAL_episodes=sum(r['split']!='test' for r in rows),TEST_episodes=len(test),independent_TEST_families=8,budgets=[8,16],totals=totals,ablations=ablations,shared_margin=models['calibration']['shared_margin'],TRAIN_budget_lookup=models['calibration']['budget_lookup'],label_distribution=ld,TEST_gate_count=sum(r['gate'] is not None for r in test),no_model_selected_total_budget=True,production_COST=False)
 runner.write(P/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
