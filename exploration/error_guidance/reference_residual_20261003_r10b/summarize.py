from pathlib import Path
import csv,json,statistics
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
POLS=['hm','learned','residual_history','residual_learned'];specs=json.loads((H/'runs.json').read_text())['runs'];rs={s['id']:json.loads((H/'per_run_audits'/(s['id']+'.json')).read_text()) for s in specs};assert len(rs)==32 and all(r['passed'] for r in rs.values())
(H/'audit_test.json').write_text(json.dumps({'all_passed':True,'runs':rs},indent=2)+'\n')
rows=[dict(s,tasks=rs[s['id']]['normal_station_END'],restricted_first10=rs[s['id']]['fixed_first10_restricted_ticks'],completed_rows=rs[s['id']]['rows'],censored=rs[s['id']]['censored'],planner_wall=rs[s['id']]['planner_wall'],forecast_wall=rs[s['id']]['forecast_wall']) for s in specs]
with (H/'summary.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
agg={p:{k:sum(r[k] for r in rows if r['policy']==p) for k in ['tasks','restricted_first10','completed_rows','censored','planner_wall','forecast_wall']} for p in POLS}
worlds=[];traces={};div=[];overlay={}
for s in specs:
 ds=[json.loads(x) for x in (O/'runs'/s['id']/'decisions.jsonl').open()];traces[s['id']]=ds
 if s['policy']=='hm':continue
 edges=[e for d in ds for c in d['calls'] for a in c['forecast']['estimates'] for e in a];costs=[v for d in ds for c in d['calls'] for row in c['request']['edge_costs'] for v in row]
 assert all(e['projected_ticks']>=0 for e in edges)
 station_roundoff=0.
 if s['policy'].startswith('residual_'):
  assert all(abs(e['projected_ticks']-max(0,e['edge_ticks']-e['reference_ticks']))<1e-12 for e in edges)
  for e in edges:
   parts=[p for p in e['parts'] if p['group']!='S'];reference=sum({'M_first':17.,'M_second':17.,'T':9.}[p['group']] for p in parts)
   station_roundoff=max(station_roundoff,abs(e['projected_ticks']-max(0,sum(p['mean_ticks'] for p in parts)-reference)))
  assert station_roundoff<1e-12
 overlay[s['id']]={'edges':len(edges),'zero_projected_edges':sum(e['projected_ticks']==0 for e in edges),'mean_edge_prediction':statistics.mean(e['edge_ticks'] for e in edges),'mean_reference':statistics.mean(e['reference_ticks'] for e in edges),'mean_projected':statistics.mean(e['projected_ticks'] for e in edges),'positive_cost_entries':sum(v>0 for v in costs),'max_overlay_cost':max(costs),'station_cancellation_max_float_roundoff':station_roundoff}
for name,seed,cond in sorted({(s['map'],s['seed'],s['condition']) for s in specs}):
 value={'map':name,'seed':seed,'condition':cond};selected={p:next(s for s in specs if (s['map'],s['seed'],s['condition'],s['policy'])==(name,seed,cond,p)) for p in POLS}
 for p,s in selected.items():r=rs[s['id']];value[p]={'tasks':r['normal_station_END'],'restricted':r['fixed_first10_restricted_ticks']}
 worlds.append(value)
 for p,q in [('hm','residual_history'),('hm','residual_learned'),('learned','residual_learned'),('residual_history','residual_learned')]:
  ds=traces[selected[p]['id']];es=traces[selected[q]['id']];first=None
  for i,(a,b) in enumerate(zip(ds,es)):
   for step in range(2):
    ca,cb=a['calls'][step],b['calls'][step]
    if ca['result']['actions']!=cb['result']['actions']:
     first={'batch':i,'step':step,'ticks':[a['snapshot']['tick'],b['snapshot']['tick']],'same_frontier':ca['request']['mapf_instance']==cb['request']['mapf_instance'],'history_rows':[a['public_history_rows'],b['public_history_rows']],'actions':{p:ca['result']['actions'],q:cb['result']['actions']}};break
   if first:break
  div.append({'world':[name,seed,cond],'pair':[p,q],'first_action_divergence':first,'tasks_delta':value[q]['tasks']-value[p]['tasks'],'fixed_first10_delta':value[q]['restricted']-value[p]['restricted']})
paired={}
for p,q in [('hm','learned'),('hm','residual_history'),('hm','residual_learned'),('learned','residual_learned'),('residual_history','residual_learned')]:
 fs=[]
 for name,seed in sorted({(s['map'],s['seed']) for s in specs}):
  ws=[w for w in worlds if (w['map'],w['seed'])==(name,seed)];fs.append({'map':name,'seed':seed,'tasks_delta':sum(w[q]['tasks']-w[p]['tasks'] for w in ws),'fixed_first10_delta':sum(w[q]['restricted']-w[p]['restricted'] for w in ws)})
 paired[q+'_minus_'+p]={'families':fs,'means':{k:statistics.mean(v[k] for v in fs) for k in ['tasks_delta','fixed_first10_delta']},'negative_zero_positive':{k:[sum(v[k]<0 for v in fs),sum(v[k]==0 for v in fs),sum(v[k]>0 for v in fs)] for k in ['tasks_delta','fixed_first10_delta']}}
out={'post_R10_new_exploration':True,'not_pooled_with_R10':True,'runs':32,'independent_task_families':4,'aggregate':agg,'worlds':worlds,'paired_family_effects':paired}
(H/'summary.json').write_text(json.dumps(out,indent=2)+'\n');(H/'overlay_diagnostics.json').write_text(json.dumps({'runtime_formula_all_checked':True,'runs':overlay,'divergences':div},indent=2)+'\n')
print(json.dumps(out,indent=2))
