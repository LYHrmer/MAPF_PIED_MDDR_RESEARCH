from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,csv
import runner,verify_matched_tail as matched
P=runner.HERE
def main():
 if (P/"SUMMARY.json").exists():print("SUMMARY already complete; preserved");return
 reg=json.loads((P/'REGISTRATION.json').read_text());worlds={w['name']:w for w in reg['worlds']};es=[json.loads(p.read_text()) for p in (P/'runs').glob('*.receipt.json')];em={(e['world'],e['policy']):e for e in es};labels=json.loads((P/'TRAIN_CAL_LABELS.json').read_text());results=[];mechanisms=[];coverage=[]
 for name,w in worlds.items():
  if w['split']!='test':
   seen=set();cost=0;slots=[];base=matched.rows(em[name,'condition'])
   for d in [d for d in base if d['event']=='actor_decision' and d['remaining_capacity']>0]:
    key=(min(2,(16-d['remaining_capacity'])//6),min(2,len(d['candidates'])))
    if key in seen:continue
    seen.add(key);needed=1+2*len(d['candidates']);selected=cost+needed<=12
    if selected:cost+=needed
    slots.append(dict(tier=key[0],cardinality_slot=key[1],opportunity=d['opportunity'],cardinality=len(d['candidates']),branch_cost=needed,selected=selected,reason='first_public_slot' if selected else 'complete_opportunity_exceeds12'))
   coverage.append(dict(world=name,slots=slots,actual_branches=cost,absent_slots=[list(k) for k in [(a,b) for a in range(3) for b in [1,2]] if k not in seen]));continue
  base=matched.rows(em[name,'condition']);baseq=[x['move'] for x in base if x['event']=='certified_POSITION_committed'];baseservice=[x for x in base if x['event']=='task_service']
  for e in [z for z in es if z['world']==name]:
   rs=matched.rows(e);summary=e['summary'];f=matched.flow(w,rs);results.append(dict(world=name,map=w['map_name'],seed=w['seed'],shift=w['shift'],policy=e['policy'],served=summary['served'],queries=summary['queries'],first4_restricted_time=str(f),utility=str(Q(summary['served'])-f/(2*w['horizon']*w['N']*4+1)),max_candidates=summary['max_candidates'],error=e['error']))
   replacements=matched.check_episode(e,rs)
   for d in replacements:
    if not e['policy'].startswith('once_'):continue
    bd=next(x for x in base if x['event']=='actor_decision' and x['opportunity']==d['opportunity']);chosen=d['selected'];source=next((c['agent'] for c in d['candidates'] if c['move']==chosen),None);queries=[x for x in rs if x['event']=='certified_POSITION_committed'];skip=next((x for x in rs if x['event']=='public_SKIP_installed'),None);clear=next((x for x in rs if x['event']=='public_SKIP_cleared_normal_END'),None);at=rs.index(d);tail=rs[at+1:]
    original=bd['selected'];original_query=next((x for x in tail if x['event']=='certified_POSITION_committed' and x['move']==original),None);end=next((x for x in tail if x['event']=='public_END_delivered' and x['move']==chosen),None)
    masked=[x for x in tail if x['event']=='public_candidate_visibility' and source is not None and [source,chosen] in x['raw_candidates'] and [source,chosen] not in x['visible_candidates']]
    successors=[c for x in tail if x['event']=='public_candidate_visibility' for c in x['visible_candidates'] if c[0]==source and c[1]!=chosen]
    new_queries=[x['move'] for x in queries if x['move'] not in baseq];lost_queries=[x for x in baseq if x not in {q['move'] for q in queries}]
    mechanisms.append(dict(world=name,policy=e['policy'],at=d['at'],opportunity=d['opportunity'],remaining=d['remaining_capacity'],candidate_count=len(d['candidates']),selected_kind=d['selected_kind'],selected_move=chosen,baseline_move=original,actual_action_changed=(d['selected_kind'],chosen)!=(bd['selected_kind'],original),skip_install=skip,skip_clear=clear,accepted_END=end,skip_clear_at_accepted_END=bool(skip and clear and end and clear['at']==end['at']),budget_immediately_after=d['remaining_capacity']-(d['selected_kind']=='QUERY'),budget_at_skip_clear=(16-sum(x['event']=='certified_POSITION_committed' for x in rs[:rs.index(clear)])) if clear else None,first_QUERY_after_replacement=next((x for x in tail if x['event']=='certified_POSITION_committed'),None),total_queries_after_replacement=sum(x['event']=='certified_POSITION_committed' for x in tail),masked_reappearances=len(masked),successor_visible_occurrences=sorted(set(c[1] for c in successors)),same_original_MOVE_later_QUERY=original_query,query_delta=summary['queries']-em[name,'condition']['summary']['queries'],new_query_occurrences=new_queries,omitted_query_occurrences=lost_queries,service_delta=summary['served']-em[name,'condition']['summary']['served'],all_task_service_records_equal=[x for x in rs if x['event']=='task_service']==baseservice,ordinal64_started_before=sum(x['event']=='original_RUN' and int(x['id'].rsplit('-',1)[1])>=64 for x in rs[:at])))
 runner.write(P/'RESULTS.json',results)
 with (P/'RESULTS.csv').open('x') as f:
  cw=csv.DictWriter(f,fieldnames=list(results[0]));cw.writeheader();cw.writerows(results)
 runner.write(P/'MECHANISM_DIAGNOSTICS.json',mechanisms);runner.write(P/'SAMPLING_COVERAGE.json',coverage)
 totals={}
 for policy in reg['policies']:
  rr=[r for r in results if r['policy']==policy];totals[policy]=dict(episodes=len(rr),served=sum(r['served'] for r in rr),queries=sum(r['queries'] for r in rr),first4_restricted_time=str(sum((Q(r['first4_restricted_time']) for r in rr),Q(0))),family_task_delta_vs_condition={str(seed):sum(r['served']-next(b['served'] for b in results if b['world']==r['world'] and b['policy']=='condition') for r in rr if r['seed']==seed) for seed in sorted({r['seed'] for r in rr})})
 ld={}
 for split in ['train','calibration']:
  for action in ['QUERY','SKIP']:
   rr=[r for r in labels if r['split']==split and r['action']==action];ld[split+'_'+action]=dict(rows=len(rr),target_signs=dict(Counter('positive' if Q(r['target'])>0 else 'negative' if Q(r['target'])<0 else 'zero' for r in rr)),whole_service_gains=dict(Counter(str(r['whole_service_gain']) for r in rr)))
 runner.write(P/'SUMMARY.json',dict(totals=totals,label_distribution=ld,failed=sum(e['error'] is not None for e in es),native_episodes=len(es),probe_episodes=len(labels),selected_opportunities=sum(r['action']=='WAIT' for r in labels),selected_multi_opportunities=sum(r['action']=='WAIT' and r['candidate_count']>1 for r in labels),mechanisms={p:dict(replacements=sum(m['policy']==p for m in mechanisms),changed=sum(m['policy']==p and m['actual_action_changed'] for m in mechanisms),SKIPs=sum(m['policy']==p and m['selected_kind']=='SKIP' for m in mechanisms),services_changed=sum(m['policy']==p and not m['all_task_service_records_equal'] for m in mechanisms)) for p in reg['policies'] if p.startswith('once_')}))
 print(json.dumps(totals,indent=2))
if __name__=='__main__':main()
