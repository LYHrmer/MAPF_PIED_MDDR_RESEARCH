from pathlib import Path
from fractions import Fraction as F
from collections import Counter
import json,csv,hashlib
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def flow(s):
 v=s['service_time_sum'];return F(v['lower']+v['upper'],2*v['denominator'])+384*(s['task_count']-s['served'])
def value(v):return float(v)
def classify_deadlock(rs):
 frame=next(r for r in reversed(rs) if r['event']=='world_frame_offline_only');robots={r['agent']:r for r in frame['robots']};owners={c:int(a[6:]) for c,a,act in frame['owners']};graph={a:set() for a,r in robots.items() if not r['served']};resident_links=[]
 for d in frame['demands']:
  a=int(d['agent'][6:]);foreign={owners[c] for c in d['resources'] if c in owners and owners[c]!=a};graph.setdefault(a,set()).update(foreign)
  for b in foreign:
   if robots[b]['served'] and robots[b]['head_index']==2:resident_links.append([a,b])
 def cyclic(a,path):
  if a in path:return path[path.index(a):]
  out=[]
  for b in graph.get(a,set()):
   z=cyclic(b,path+[a])
   if z:return z
  return out
 cycles=[]
 for a in graph:
  c=cyclic(a,[])
  if c and sorted(c) not in cycles:cycles.append(sorted(c))
 return dict(terminal_resident_links=resident_links,static_wait_cycles=cycles,final_active_actions=len(frame['actions']),unfinished_agents=len(graph))
def main():
 out=HERE/'native_attempt_01';receipt=json.loads((out/'RECEIPT.json').read_text());sup=json.loads((HERE/'SUPPORT.json').read_text());task_heads={h['task']:i for c in sup['cohorts'] for r in c['robots'] for i,h in enumerate(r['heads'])};rows=[];test={}
 for e in receipt['episodes']:
  s=e['summary'];rs=[json.loads(x) for x in Path(e['raw']).read_text().splitlines()];queries=[r for r in rs if r['event']=='certified_POSITION_committed'];decisions=[r for r in rs if r['event']=='actor_decision'];milestones=Counter(task_heads[r['task']] for r in rs if r['event']=='task_service');physics=[r for r in rs if r['event'] in ['original_RUN','physical_original_END','public_END_delivered','task_service','public_head_revealed','public_WAIT_started','public_WAIT_ended']];pd=hashlib.sha256(json.dumps(physics,sort_keys=True,separators=(',',':')).encode()).hexdigest();selection=hashlib.sha256(json.dumps([(r['move'],r['at']) for r in queries],sort_keys=True,separators=(',',':')).encode()).hexdigest()
  row=dict(world_id=e['world_id'],cohort_id=e['cohort_id'],split=e['split'],policy=e['policy'],fixed_tasks=s['task_count'],served=s['served'],first_head_complete=milestones[0],second_head_complete=milestones[1],third_head_complete=milestones[2],restricted_fixed_task_completion_sum=str(flow(s)),queries=s['queries'],capacity=s['capacity'],early_resource_releases=sum(bool(r['removed']) for r in queries),query_without_resource_release=sum(not r['removed'] for r in queries),opportunities=s['eligible_opportunities'],maximum_candidates=s['max_candidates'],competing_decisions=sum(len(r['candidates'])>=2 for r in decisions),model_scoring_candidates=sum(len(r['candidates']) for r in decisions) if e['policy'].startswith('ridge') else 0,MOVEs=s['started_MOVEs'],END=s['delivered_END'],head_reveals=sum(r['event']=='public_head_revealed' for r in rs),deadlock=s['deadlock'],physics_sha256=pd,selection_sha256=selection,raw_sha256=e['raw_sha256'],native_seconds=e['seconds'],deadlock_diagnostic=classify_deadlock(rs) if s['deadlock'] else None);rows.append(row)
  if e['split']=='test':test[e['world_id'],e['policy']]=row
 aggregates=[]
 for case in ['ALL','IID','SHIFT','eta0']:
  for p in ['WAIT','RR','condition','ridge_history','ridge_nohistory']:
   rr=[r for r in rows if r['split']=='test' and r['policy']==p and (case=='ALL' or (case=='IID' and '__IID_' in r['world_id']) or (case=='SHIFT' and '__SHIFT_' in r['world_id']) or case=='eta0' and r['world_id'].endswith('__eta0'))];aggregates.append(dict(case=case,policy=p,worlds=len(rr),fixed_tasks=sum(r['fixed_tasks'] for r in rr),served=sum(r['served'] for r in rr),first_head_complete=sum(r['first_head_complete'] for r in rr),second_head_complete=sum(r['second_head_complete'] for r in rr),third_head_complete=sum(r['third_head_complete'] for r in rr),restricted_fixed_task_completion_sum=str(sum((F(r['restricted_fixed_task_completion_sum']) for r in rr),F(0))),queries=sum(r['queries'] for r in rr),early_resource_releases=sum(r['early_resource_releases'] for r in rr),competing_decisions=sum(r['competing_decisions'] for r in rr),model_scoring_candidates=sum(r['model_scoring_candidates'] for r in rr),deadlocks=sum(r['deadlock'] for r in rr)))
 paired=[]
 for w in sorted({k[0] for k in test}):
  h=test[w,'ridge_history'];n=test[w,'ridge_nohistory'];base=test[w,'WAIT'];rr=test[w,'RR'];rule=test[w,'condition'];paired.append(dict(world_id=w,history_extra_tasks_over_nohistory=h['served']-n['served'],history_restricted_time_improvement_over_nohistory=str(F(n['restricted_fixed_task_completion_sum'])-F(h['restricted_fixed_task_completion_sum'])),history_extra_tasks_over_WAIT=h['served']-base['served'],history_restricted_time_improvement_over_WAIT=str(F(base['restricted_fixed_task_completion_sum'])-F(h['restricted_fixed_task_completion_sum'])),history_restricted_time_improvement_over_RR=str(F(rr['restricted_fixed_task_completion_sum'])-F(h['restricted_fixed_task_completion_sum'])),history_restricted_time_improvement_over_condition=str(F(rule['restricted_fixed_task_completion_sum'])-F(h['restricted_fixed_task_completion_sum'])),history_vs_nohistory_physics_differ=h['physics_sha256']!=n['physics_sha256'],history_vs_nohistory_query_choices_differ=h['selection_sha256']!=n['selection_sha256']))
 result=dict(native_successful=receipt['total_native_episodes'],mechanical_successful=6,prior_preserved_timeouts=2,statistical_worlds=receipt['worlds'],whole_task_groups=6,train_worlds=6,calibration_worlds=2,test_worlds=8,source_maps=1,model_sha256=receipt['model_sha256'],train_rows=12,calibration_rows=4,train_labels_all_first2_single_candidate=True,aggregates=aggregates,paired=paired,rows=rows,production_COST=False,external_baseline=False,online_replanning=False,model_selection_on_test=False)
 (HERE/'RESULTS.json').write_text(json.dumps(result,indent=2)+'\n')
 for filename,rr in [('ALL_NATIVE_RESULTS.csv',rows),('HELDOUT_RESULTS.csv',[r for r in rows if r['split']=='test'])]:
  fields=[k for k in rr[0] if k!='deadlock_diagnostic']
  with (HERE/filename).open('w',newline='') as f:
   w=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore');w.writeheader();w.writerows(rr)
 print(json.dumps(dict(aggregates=[a for a in aggregates if a['case']=='ALL'],paired=paired),indent=2))
if __name__=='__main__':main()
