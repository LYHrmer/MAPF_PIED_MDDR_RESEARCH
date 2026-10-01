"""Post-outcome diagnostics only; never used to fit or select a policy."""
from pathlib import Path
from fractions import Fraction as F
import json
import runner
P=runner.HERE
def load(p):return json.loads(Path(p).read_text())
def trace(e):return [json.loads(z) for z in Path(e['raw']).read_text().splitlines()]
def serviced(rs):return {r['task']:r for r in rs if r['event']=='task_service'}
def fixed(w,ts):return sum((F(ts[t['task']]['at']['lower']+ts[t['task']]['at']['upper'],2000000) if t['task'] in ts else F(w['horizon']) for a in w['robots'] for t in a['tasks'][:4]),F(0))
def main():
 reg=load(P/'REGISTRATION.json');labels=load(P/'TRAIN_CAL_LABELS.json');receipts=[load(p) for p in (P/'runs').glob('*.receipt.json')]+[load(p) for p in (P/'scale_guard_successor/runs').glob('*.receipt.json')];lookup={(e['world'],e['policy']):e for e in receipts};label_checks=[];heldout=[]
 for r in labels:
  e=lookup[r['world'],r['probe']]
  if e['error'] is not None:continue
  rs=trace(e);qs=[x for x in rs if x['event']=='certified_POSITION_committed'];assert len(qs)==1
  choice=next(i for i,x in enumerate(rs) if x['event']=='actor_decision' and x['opportunity']==r['opportunity']);qi=next(i for i,x in enumerate(rs) if x['event']=='certified_POSITION_committed');assert qi>choice
  post_queries=sum(x['event']=='certified_POSITION_committed' for x in rs[qi+1:]);assert post_queries==0
  label_checks.append(dict(world=r['world'],opportunity=r['opportunity'],source=r['source'],query_count=1,subsequent_queries=0))
 for w in reg['worlds']:
  if w['split'] not in ['test','scale']:continue
  wait=lookup[w['name'],'WAIT'];wait_services=serviced(trace(wait));wf=fixed(w,wait_services);task_metadata={t['task']:dict(task=t['task'],agent=a['agent'],FIFO_ordinal=j+1,in_fixed_first4=j<4) for a in w['robots'] for j,t in enumerate(a['tasks'])}
  for policy in reg['policies']:
   e=lookup[w['name'],policy]
   if e['error'] is not None:heldout.append(dict(world=w['name'],policy=policy,error=e['error']));continue
   rs=trace(e);ts=serviced(rs);queries=sum(r['event']=='certified_POSITION_committed' for r in rs);lost=sorted(set(wait_services)-set(ts));gained=sorted(set(ts)-set(wait_services));delta=len(ts)-len(wait_services);gain=wf-fixed(w,ts)
   assert delta==len(gained)-len(lost)
   heldout.append(dict(world=w['name'],split=w['split'],policy=policy,whole_task_delta=delta,queries=queries,queries_after_first=max(0,queries-1),lost_vs_WAIT=[task_metadata[t] for t in lost],gained_vs_WAIT=[task_metadata[t] for t in gained],fixed_first4_time_gain=str(gain),secondary_improvement_with_primary_loss=delta<0 and gain>0))
 runner.write(P/'TAIL_DISTRIBUTION_DIAGNOSTICS.json',dict(post_outcome_not_used_for_selection=True,training_target='single current query, then WAIT to H128',deployment_tail='up to16 adaptive queries with cumulative public-time pacing for paced policies',tail_policy_mismatch_not_corrected_by_more_labels=True,training_cal_probe_checks=len(label_checks),all_probe_subsequent_query_counts_zero=True,training_negative_task_labels=sum(r.get('whole_service_gain',0)<0 for r in labels if r['split']=='train'),calibration_negative_task_labels=sum(r.get('whole_service_gain',0)<0 for r in labels if r['split']=='calibration'),heldout=heldout))
 print('tail diagnostic',len(label_checks),'single-query continuations;',len(heldout),'heldout policy outcomes',flush=True)
if __name__=='__main__':main()
