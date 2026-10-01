from pathlib import Path
import csv,json,itertools
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
specs=[s for s in json.loads((H/'runs.json').read_text())['runs'] if s['split']=='test'];rs={s['id']:json.loads((H/'per_run_audits'/(s['id']+'.json')).read_text()) for s in specs};assert all(r['passed'] for r in rs.values())
(H/'audit_test.json').write_text(json.dumps({'all_passed':True,'runs':rs},indent=2)+'\n')
rows=[]
for s in specs:
 r=rs[s['id']];rows.append(dict(s,tasks=r['normal_station_END'],restricted_first10=r['fixed_first10_restricted_ticks'],rows=r['rows'],censored=r['censored'],nonzero_edge_calls=r['candidate_nonzero_calls'],planner_wall=r['planner_wall'],forecast_wall=r['forecast_wall']))
with (H/'summary.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
aggregate={}
for mode,pol in itertools.product(['global','local'],['hm','history','learned']):
 selected=[r for r in rows if r['execution']==mode and r['policy']==pol];aggregate[mode+'_'+pol]={k:sum(r[k] for r in selected) for k in ['tasks','restricted_first10','rows','censored','nonzero_edge_calls','planner_wall','forecast_wall']}
worlds=[];divergences=[]
for name,seed,cond in itertools.product(['empty-32-32','random-32-32-10'],[941821,941822],['nominal','axis']):
 world={'map':name,'seed':seed,'condition':cond}
 for mode,pol in itertools.product(['global','local'],['hm','history','learned']):
  r=next(r for r in rows if (r['map'],r['seed'],r['condition'],r['execution'],r['policy'])==(name,seed,cond,mode,pol));world[mode+'_'+pol]={'tasks':r['tasks'],'restricted':r['restricted_first10']}
 for mode in ['global','local']:
  hs=next(s for s in specs if (s['map'],s['seed'],s['condition'],s['execution'],s['policy'])==(name,seed,cond,mode,'history'));ls=next(s for s in specs if (s['map'],s['seed'],s['condition'],s['execution'],s['policy'])==(name,seed,cond,mode,'learned'))
  hd=[json.loads(x) for x in (O/'runs'/hs['id']/'decisions.jsonl').open()];ld=[json.loads(x) for x in (O/'runs'/ls['id']/'decisions.jsonl').open()];diff=None
  for i,(a,b) in enumerate(zip(hd,ld)):
   for step in range(2):
    if a['calls'][step]['result']['actions']!=b['calls'][step]['result']['actions']:
     diff={'batch':i,'logical_step':step,'tick':a['snapshot']['tick'],'same_actual_view':a['view']==b['view'],'same_snapshot':a['snapshot']==b['snapshot'],'same_frontier':a['calls'][step]['request']['mapf_instance']==b['calls'][step]['request']['mapf_instance']};break
   if diff:break
  hserv={(v['agent'],v['ordinal']):v['tick'] for v in rs[hs['id']]['services']};lserv={(v['agent'],v['ordinal']):v['tick'] for v in rs[ls['id']]['services']};common=set(hserv)&set(lserv);deltas=[lserv[k]-hserv[k] for k in common]
  divergences.append({'world':[name,seed,cond,mode],'first_action_divergence':diff,'common_served':len(common),'learned_earlier':sum(d<0 for d in deltas),'same':sum(d==0 for d in deltas),'later':sum(d>0 for d in deltas),'common_tick_delta':sum(deltas),'fixed_first10_delta':world[mode+'_learned']['restricted']-world[mode+'_history']['restricted']})
 worlds.append(world)
interactions={}
for pol in ['history','learned']:
 interactions[pol]={k:(aggregate['local_'+pol][k]-aggregate['global_'+pol][k])-(aggregate['local_hm'][k]-aggregate['global_hm'][k]) for k in ['tasks','restricted_first10']}
out={'runs':48,'aggregate':aggregate,'worlds':worlds,'history_learned_divergence':divergences,'execution_model_interaction_relative_to_hm':interactions,'independent_task_families':4,'conditions_paired_within_family':True};(H/'summary.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(aggregate,indent=2))
