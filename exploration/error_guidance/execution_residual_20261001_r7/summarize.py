from pathlib import Path
from collections import defaultdict,Counter
import csv,hashlib,json,statistics
HERE=Path(__file__).resolve().parent;OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/HERE.name

def service_ordinals(spec,result):
 public=[json.loads(s) for s in (OUT/'runs'/spec['id']/'public_events.jsonl').open()]
 ids={};counts=Counter()
 for e in public:
  if e['kind']!='view':continue
  for a,goals in enumerate(e['view']['mapf_instance']['goals']):
   tid=goals[0]['id']
   if tid not in ids:ids[tid]=(a,counts[a]);counts[a]+=1
 return {f'{ids[int(tid)][0]}:{ids[int(tid)][1]}':v['tick'] for tid,v in result['completed_tasks'].items()}

def first_difference(a,b):
 for k,(x,y) in enumerate(zip(a,b)):
  if x['result']['actions']!=y['result']['actions']:
   fc=y['forecast']
   return {'decision':k,'shared_public_view':x['view']==y['view'],'shared_snapshot':x['snapshot']==y['snapshot'],
           'tick_reference':x['snapshot']['tick'],'tick_candidate':y['snapshot']['tick'],
           'reference_actions':x['result']['actions'],'candidate_actions':y['result']['actions'],
           'candidate_forecast':None if fc is None else {q:fc[q] for q in ('policy','completed_rows','estimates','dimensionless_scale','depth')},
           'candidate_forecast_sha256':None if fc is None else hashlib.sha256(json.dumps(fc,sort_keys=True).encode()).hexdigest()}
 return None

def main():
 audit=json.loads((HERE/'audit_test.json').read_text());assert audit['all_passed'];groups=defaultdict(dict);rows=[]
 for ident,r in audit['runs'].items():
  s=r['spec'];key=(s['map'],s['seed'],s['condition']);groups[key][s['policy']]=r
  receipt=json.loads((OUT/'runs'/ident/'receipt.json').read_text())
  rows.append({'run':ident,'map':s['map'],'condition':s['condition'],'policy':s['policy'],
   **{k:r[k] for k in ('normal_station_END','views','rows','censored_moves','candidate_edge_calls','candidate_nonzero_calls','planner_request_seconds','forecast_seconds')},
   'whole_native_wall_seconds':receipt['wall_seconds'],'unfinished_tasks':len(r['unfinished_tasks']),
   'learned_MAE':r['prediction_metrics']['learned']['MAE'],'history_MAE':r['prediction_metrics']['history']['MAE']})
 comparisons=[]
 for key,arms in groups.items():
  decisions={p:[json.loads(s) for s in (OUT/'runs'/r['spec']['id']/'decisions.jsonl').open()] for p,r in arms.items()}
  services={p:service_ordinals(r['spec'],r) for p,r in arms.items()}
  restricted={p:8016*4000-sum(4000-t for t in ss.values()) for p,ss in services.items()}
  value={'map':key[0],'seed':key[1],'condition':key[2],'services':{p:r['normal_station_END'] for p,r in arms.items()},
         'exploratory_fixed_8016_task_restricted_tick_sum':restricted,'pairs':{}}
  for base,policy in [('hm_GPIBT','trained'),('hm_GPIBT','history'),('hm_GPIBT','learned'),('history','learned')]:
   common=sorted(set(services[base])&set(services[policy]));deltas=[services[policy][k]-services[base][k] for k in common]
   value['pairs'][base+'__'+policy]={'service_count_difference':arms[policy]['normal_station_END']-arms[base]['normal_station_END'],
    'first_action_difference':first_difference(decisions[base],decisions[policy]),
    'matched_served_fifo_count':len(common),'served_earlier':sum(d<0 for d in deltas),'served_equal':sum(d==0 for d in deltas),'served_later':sum(d>0 for d in deltas),
    'matched_ticks_differences':dict(zip(common,deltas)), 'matched_tick_sum_difference':sum(deltas),
    'exploratory_fixed_8016_task_restricted_tick_sum_difference':restricted[policy]-restricted[base],
    'served_only_reference':sorted(set(services[base])-set(services[policy])),
    'served_only_candidate':sorted(set(services[policy])-set(services[base]))}
  comparisons.append(value)
 with (HERE/'summary.csv').open('w') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 total={p:sum(r['normal_station_END'] for r in rows if r['policy']==p) for p in ('hm_GPIBT','trained','history','learned')}
 (HERE/'summary.json').write_text(json.dumps({'totals':total,'paired_worlds':comparisons,'all_runs':rows,
  'primary_metric':'normal STATION END within fixed400s; incomplete current heads retained',
  'matched_time_scope':'matched already-served owner/FIFO ordinals only; not uncensored total flow or policy-independent released-flow',
  'exploratory_fixed_task_scope':'added after results solely for complete paired reporting; all 8*1002 pre-frozen FIFO tasks, even unrevealed, have min(normal service time,4000), with unfinished=4000; this is not released-flow or a preregistered primary endpoint',
  'timing_scope':'planner request round trip includes bridge; forecast includes Python predictions/BFS/cost-map construction; public-event projection and logging excluded from these two timers but included in whole native process wall'},indent=2)+'\n')
 print(total)
 for c in comparisons:print(c['map'],c['condition'],c['services'],'learned-v-history',c['pairs']['history__learned']['first_action_difference'] is not None)
if __name__=='__main__':main()
