"""TRAIN-only finite value-space summary from every registered raw branch."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,csv,re
import runner
P=runner.HERE
def interval(r):return Q(r['at']['lower'],1000000),Q(r['at']['upper'],1000000)
def outcome(w,e):
 wanted={t['task'] for a in w['robots'] for t in a['tasks'][:4]};service=[];ds=[];queries=[];events=Counter()
 for s in Path(e['raw']).open():
  r=json.loads(s);events[r['event']]+=1
  if r['event']=='task_service':service.append(r)
  elif r['event']=='actor_decision':ds.append(r)
  elif r['event']=='certified_POSITION_committed':queries.append(r['move'])
 actual={r['task']:interval(r) for r in service};lo=sum((actual.get(t,(Q(w['horizon']),)*2)[0] for t in wanted),Q(0));hi=sum((actual.get(t,(Q(w['horizon']),)*2)[1] for t in wanted),Q(0));den=2*w['horizon']*w['N']*4+1
 assert den==16385 and len(service)==e['summary']['served']
 coupled=lambda d:any(len({cl['task'] for cl in c['claims']})>1 or any(cl['owners']>1 for cl in c['claims']) for c in d['candidates'])
 row=dict(world=w['name'],scenario=w['scenario_identity'],offset=w['scenario_offset'],seed=w['seed'],policy=e['policy'],served=len(service),queries=len(queries),first4_time_lower=str(lo),first4_time_upper=str(hi),first4_time_midpoint=str((lo+hi)/2),J_lower=str(Q(len(service))-hi/den),J_upper=str(Q(len(service))-lo/den),max_candidates=e['summary']['max_candidates'],public_decisions=len(ds),multi_candidate_decisions=sum(len(d['candidates'])>1 for d in ds),coupled_blocking_decisions=sum(coupled(d) for d in ds),skip_installs=events['public_SKIP_installed'],error=e['error'])
 return row,service,ds,queries
def difference(a,b):
 gainlo=Q(b['first4_time_lower'])-Q(a['first4_time_upper']);gainhi=Q(b['first4_time_upper'])-Q(a['first4_time_lower']);jl=Q(a['J_lower'])-Q(b['J_upper']);ju=Q(a['J_upper'])-Q(b['J_lower'])
 return dict(task_gain=a['served']-b['served'],query_delta=a['queries']-b['queries'],time_gain_lower=str(gainlo),time_gain_upper=str(gainhi),J_gain_lower=str(jl),J_gain_upper=str(ju),robust_J_improvement=jl>0,midpoint_J_improvement=jl+ju>0,interval_unresolved=jl<=0<=ju)
def successor_evidence(w,e,anchor_tasks):
 heads={a:t['tasks'][0]['task'] for a,t in enumerate(w['robots'])};parents={};revealed=[];before=[];queries=0;budget_end=None
 def descendant(task):
  while task in parents:
   task=parents[task]
   if task in anchor_tasks:return True
  return False
 for line in Path(e['raw']).open():
  r=json.loads(line)
  if r['event']=='public_head_revealed':
   parents[r['task']]=heads[r['agent']];heads[r['agent']]=r['task']
   if descendant(r['task']):
    revealed.append(dict(task=r['task'],at=r['at']))
    if queries<16:before.append(r['task'])
  elif r['event']=='certified_POSITION_committed':
   queries+=1
   if queries==16:budget_end=r['at']
 return dict(public_descendant_heads_revealed=revealed,public_descendants_before_budget_exhaustion=before,budget_exhaustion_at=budget_end)
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());registered=json.loads((P/'BRANCHES_BEFORE_OUTCOMES.json').read_text());receipt=json.loads((P/'RECEIPT.json').read_text());assert receipt['complete'];es=[json.loads(p.read_text()) for p in (P/'runs').glob('*.receipt.json')];results=[];families=[];pairs=[];opportunities=[]
 for w in reg['worlds']:
  ee=[e for e in es if e['world']==w['name']];data={e['policy']:outcome(w,e) for e in ee if e['error'] is None};base,bs,bd,bq=data['condition'];wait,ws,wd,wq=data['WAIT'];byop={d['opportunity']:d for d in bd}
  for policy,(r,service,ds,queries) in data.items():
   r['vs_condition']=difference(r,base);r['vs_whole_WAIT']=difference(r,wait);r['service_sequence_equal_condition']=service==bs;r['service_sequence_equal_whole_WAIT']=service==ws;r['new_query_occurrences_vs_condition']=[m for m in queries if m not in bq];r['omitted_query_occurrences_vs_condition']=[m for m in bq if m not in queries];results.append(r)
   if not policy.startswith('pair_'):continue
   m=re.fullmatch(r'pair_(\d+)_(WAIT|QUERY|SKIP)(\d+)_(QUERY|SKIP)_(distinct|successor)',policy);op,first,agent,second,trigger=m.groups();first_only=f"cf_{op}_{first+agent if first!='WAIT' else 'WAIT'}";interventions=[d for d in ds if d['intervention_index']];assert len(interventions) in [1,2];firstd=interventions[0];secondd=interventions[1] if len(interventions)==2 else None;fd=data[first_only][0]
   pairs.append(dict(world=w['name'],policy=policy,trigger=trigger,first_only_policy=first_only,first_opportunity=firstd['opportunity'],first_action=firstd['selected_kind'],anchor_identity=[firstd['anchor_agent'],firstd['anchor_move']],anchor_tasks=firstd['anchor_tasks'],second_reached=secondd is not None,second_opportunity=secondd['opportunity'] if secondd else None,second_at=secondd['at'] if secondd else None,second_action=secondd['selected_kind'] if secondd else None,second_move=secondd['selected'] if secondd else None,second_eligible=secondd['second_eligible'] if secondd else [],remaining_at_first=firstd['remaining_capacity'],remaining_at_second=secondd['remaining_capacity'] if secondd else None,final_remaining=16-r['queries'],unreached_observation=None if secondd else ('no_qualifying_public_trigger_before_budget_exhaustion' if r['queries']==16 else 'no_qualifying_public_trigger_through_H'),successor_evidence=successor_evidence(w,next(e for e in ee if e['policy']==policy),set(firstd['anchor_tasks'])) if trigger=='successor' else None,vs_first_only=difference(r,fd),service_equal_first_only=service==data[first_only][1],vs_condition=r['vs_condition'],vs_whole_WAIT=r['vs_whole_WAIT']))
  singles=[r for r in results if r['world']==w['name'] and r['policy'].startswith('cf_')];pp=[r for r in results if r['world']==w['name'] and r['policy'].startswith('pair_')];allprobe=singles+pp
  for op in sorted({int(r['policy'].split('_')[1]) for r in singles}):
   rr=[r for r in singles if int(r['policy'].split('_')[1])==op];d=byop[op];opportunities.append(dict(world=w['name'],opportunity=op,at=d['at'],remaining=d['remaining_capacity'],candidate_count=len(d['candidates']),candidates=[dict(agent=c['agent'],move=c['move'],claims=c['claims']) for c in d['candidates']],branches=len(rr),best_tasks=max(r['served'] for r in rr),max_task_gain_vs_condition=max(r['vs_condition']['task_gain'] for r in rr),max_task_gain_vs_whole_WAIT=max(r['vs_whole_WAIT']['task_gain'] for r in rr),robust_J_improving_branches_vs_condition=sum(r['vs_condition']['robust_J_improvement'] for r in rr),robust_J_improving_branches_vs_both=sum(r['vs_condition']['robust_J_improvement'] and r['vs_whole_WAIT']['robust_J_improvement'] for r in rr)))
  families.append(dict(world=w['name'],condition_tasks=base['served'],whole_WAIT_tasks=wait['served'],condition_queries=base['queries'],whole_WAIT_queries=wait['queries'],single_branches=len(singles),pair_branches=len(pp),best_single_tasks=max(r['served'] for r in singles),best_pair_tasks=max(r['served'] for r in pp),best_registered_probe_tasks=max(r['served'] for r in allprobe),task_improving_arms_vs_condition=sum(r['vs_condition']['task_gain']>0 for r in allprobe),task_improving_arms_vs_both=sum(r['vs_condition']['task_gain']>0 and r['vs_whole_WAIT']['task_gain']>0 for r in allprobe),robust_J_improving_arms_vs_condition=sum(r['vs_condition']['robust_J_improvement'] for r in allprobe),robust_J_improving_arms_vs_both=sum(r['vs_condition']['robust_J_improvement'] and r['vs_whole_WAIT']['robust_J_improvement'] for r in allprobe)))
 runner.write(P/'RESULTS.json',results);runner.write(P/'PAIR_REACHABILITY.json',pairs);runner.write(P/'OPPORTUNITY_VALUE_SPACE.json',opportunities)
 fields=['world','scenario','offset','seed','policy','served','queries','first4_time_lower','first4_time_upper','first4_time_midpoint','J_lower','J_upper','max_candidates','skip_installs','error','service_sequence_equal_condition','service_sequence_equal_whole_WAIT']
 with (P/'RESULTS.csv').open('w') as f:
  out=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');out.writeheader();out.writerows(results)
 summary=dict(stage='new TRAIN-only finite mechanism exploration; no fit/no TEST',native_episodes=len(es),failed=sum(e['error'] is not None for e in es),baseline_episodes=8,single_branches=sum(r['policy'].startswith('cf_') for r in results),pair_branches=len(pairs),selected_opportunities=len(opportunities),selected_two_candidate_opportunities=sum(o['candidate_count']==2 for o in opportunities),selected_coupled_opportunities=sum(any(len({cl['task'] for cl in c['claims']})>1 or any(cl['owners']>1 for cl in c['claims']) for c in o['candidates']) for o in opportunities),families=families,pairs_by_trigger={t:dict(arms=sum(p['trigger']==t for p in pairs),second_reached=sum(p['trigger']==t and p['second_reached'] for p in pairs),task_gain_vs_first_only=dict(Counter(str(p['vs_first_only']['task_gain']) for p in pairs if p['trigger']==t)),robust_J_improvements_vs_first_only=sum(p['trigger']==t and p['vs_first_only']['robust_J_improvement'] for p in pairs)) for t in ['distinct','successor']},single_opportunities_task_headroom_vs_condition=sum(o['max_task_gain_vs_condition']>0 for o in opportunities),single_opportunities_task_headroom_vs_both=sum(o['max_task_gain_vs_condition']>0 and o['max_task_gain_vs_whole_WAIT']>0 for o in opportunities),all_registered_branches_retained=True,global_policy_optimality_claim=False)
 summary['whole_run_visible_census']=dict(episodes_with_multi_candidates=sum(r['multi_candidate_decisions']>0 for r in results),multi_candidate_decisions=sum(r['multi_candidate_decisions'] for r in results),episodes_with_coupled_blocking=sum(r['coupled_blocking_decisions']>0 for r in results),coupled_blocking_decisions=sum(r['coupled_blocking_decisions'] for r in results))
 runner.write(P/'SUMMARY.json',summary);print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
