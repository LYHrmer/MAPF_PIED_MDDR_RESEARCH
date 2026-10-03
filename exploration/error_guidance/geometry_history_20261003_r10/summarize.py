"""Pre-registered outcomes; diagnostics never change the frozen test policy."""
from pathlib import Path
import csv,itertools,json,math,statistics
import numpy as np
from public_model import predict,PublicHistory,forecast
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
POLS=['hm','history','geometry','learned'];PAIRS=[('history','learned'),('geometry','learned'),('history','geometry'),('hm','learned'),('hm','geometry')]
specs=json.loads((H/'runs.json').read_text())['runs'];m=json.loads((H/'model_freeze.json').read_text())
rs={s['id']:json.loads((H/'per_run_audits'/(s['id']+'.json')).read_text()) for s in specs};assert len(rs)==64 and all(r['passed'] for r in rs.values())
(H/'audit_test.json').write_text(json.dumps({'all_passed':True,'runs':rs},indent=2)+'\n')
rows=[dict(s,tasks=rs[s['id']]['normal_station_END'],restricted_first10=rs[s['id']]['fixed_first10_restricted_ticks'],completed_rows=rs[s['id']]['rows'],censored=rs[s['id']]['censored'],planner_wall=rs[s['id']]['planner_wall'],forecast_wall=rs[s['id']]['forecast_wall']) for s in specs]
with (H/'summary.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
aggregate={p:{k:sum(r[k] for r in rows if r['policy']==p) for k in ['tasks','restricted_first10','completed_rows','censored','planner_wall','forecast_wall']} for p in POLS}
worldkeys=sorted({(s['map'],s['seed'],s['condition']) for s in specs});worlds=[];families={};decisions={}
for s in specs:decisions[s['id']]=[json.loads(v) for v in (O/'runs'/s['id']/'decisions.jsonl').open()]
def spec(world,policy):return next(s for s in specs if (s['map'],s['seed'],s['condition'],s['policy'])==(*world,policy))
def compact(fc):
 out=[]
 for edges in fc['estimates']:
  out.append({'edge_duration_rank':sorted(range(4),key=lambda d:(edges[d]['edge_ticks'],d)),
   'edges':[{'direction':e['direction'],'edge_ticks':e['edge_ticks'],'parts':[{'group':p['group'],'direction':p['direction'],'features':p['features'],'ticks':p['mean_ticks']} for p in e['parts']]} for e in edges]})
 return out
def snapshot_attribution(world,policy,batch,step):
 s=spec(world,policy);d=decisions[s['id']][batch];call=d['calls'][step]
 hist=PublicHistory(m['d0'])
 for line in (O/'runs'/s['id']/'public_events.jsonl').open():
  e=json.loads(line)
  if e['sequence']>d['public_last_sequence']:break
  hist.accept(e)
 layout=json.loads((H/'inputs'/s['input_id']/'map.json').read_text())['layout'];view={'mapf_instance':call['request']['mapf_instance']}
 zero=PublicHistory(m['d0']);zero.last_sequence=hist.last_sequence
 preds={p:forecast(hist,view,layout,p,m) for p in ['history','geometry','learned']};z=forecast(zero,view,layout,'learned',m)
 delta=max(abs(x-y) for a,b in zip(preds['learned']['cost_by_agent_destination'],z['cost_by_agent_destination']) for x,y in zip(a,b))
 return {'source_policy':policy,'batch':batch,'logical_step':step,'tick':d['snapshot']['tick'],'completed_history':len(hist.rows),'zero_history':len(hist.rows)==0,'full_vs_zero_history_max_cost_difference':delta,
         'estimates':{**{p:compact(f) for p,f in preds.items()},'full_zero_history':compact(z)},'rank_scope':'primitive edge-duration heuristic; author final internal action ranking not exposed'}
divergences=[];first=[]
for world in worldkeys:
 value={'map':world[0],'seed':world[1],'condition':world[2]}
 for p in POLS:
  r=rs[spec(world,p)['id']];value[p]={'tasks':r['normal_station_END'],'restricted':r['fixed_first10_restricted_ticks']}
 worlds.append(value);first.append({'world':world,'decision':snapshot_attribution(world,'hm',0,0)})
 for p,q in PAIRS[:3]:
  a=decisions[spec(world,p)['id']];b=decisions[spec(world,q)['id']];diff=None
  for i,(da,db) in enumerate(zip(a,b)):
   for step in range(2):
    ca=da['calls'][step];cb=db['calls'][step]
    if ca['result']['actions']!=cb['result']['actions']:
     diff={'batch':i,'step':step,'ticks':[da['snapshot']['tick'],db['snapshot']['tick']],
      'same_view':da['view']==db['view'],'same_frontier':ca['request']['mapf_instance']==cb['request']['mapf_instance'],
      'history_rows':[da['public_history_rows'],db['public_history_rows']],'actions':{p:ca['result']['actions'],q:cb['result']['actions']},
      'changed_agents':[j for j,(x,y) in enumerate(zip(ca['result']['actions'],cb['result']['actions'])) if x!=y]}
     if diff['same_frontier']:diff['common_frontier_attribution']=snapshot_attribution(world,p,i,step)
     break
   if diff:break
  divergences.append({'world':world,'pair':[p,q],'first_action_divergence':diff,
   'tasks_delta':value[q]['tasks']-value[p]['tasks'],'fixed_first10_delta':value[q]['restricted']-value[p]['restricted']})
familykeys=sorted({(s['map'],s['seed']) for s in specs});paired={}
for p,q in PAIRS:
 ds=[]
 for name,seed in familykeys:
  group=[w for w in worlds if (w['map'],w['seed'])==(name,seed)]
  ds.append({'map':name,'seed':seed,'tasks_delta_sum_two_conditions':sum(w[q]['tasks']-w[p]['tasks'] for w in group),'fixed_first10_delta_sum_two_conditions':sum(w[q]['restricted']-w[p]['restricted'] for w in group)})
 intervals={}
 for key in ['tasks_delta_sum_two_conditions','fixed_first10_delta_sum_two_conditions']:
  vals=np.array([d[key] for d in ds]);rng=np.random.default_rng(103064);means=vals[rng.integers(0,len(vals),(10000,len(vals)))].mean(1)
  intervals[key]={'family_mean':float(vals.mean()),'bootstrap95_mean':np.quantile(means,[.025,.975]).tolist(),'negative_zero_positive':[int((vals<0).sum()),int((vals==0).sum()),int((vals>0).sum())]}
 paired[q+'_minus_'+p]={'families':ds,'descriptive_intervals':intervals}
summary={'runs':64,'independent_task_families':8,'conditions_paired_within_family':True,'aggregate':aggregate,'worlds':worlds,'paired_family_effects':paired}
(H/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
(H/'decision_attribution.json').write_text(json.dumps({'first_decisions':first,'pair_divergences':divergences,'no_policy_changes':True},indent=2)+'\n')
allrows=[]
for s in specs:
 if s['policy']=='hm':allrows.extend(dict(r,run=s['id'],map=s['map'],seed=s['seed'],condition=s['condition']) for r in json.loads((O/'runs'/s['id']/'supervised_rows.json').read_text())['rows'])
def metric(selected):
 if not selected:return {'n':0}
 value={'n':len(selected),'mean_D':statistics.mean(r['duration'] for r in selected),'mean_own_prefix_wait':statistics.mean(r['begin_tick']-r['admit_tick'] for r in selected),'mean_admit_wait':statistics.mean(r['admit_tick']-r['proposal_tick'] for r in selected)}
 for pol in ['history','geometry','learned']:
  er=np.array([predict(r['features'],r['group'],pol,m)-r['duration'] for r in selected]);value[pol]={'MAE':float(abs(er).mean()),'RMSE':float(np.sqrt((er**2).mean())),'bias':float(er.mean()),'median_abs':float(np.median(abs(er))),'p95_abs':float(np.quantile(abs(er),.95))}
 return value
prediction={'source':'same 16 hm traces, no retuning','all_motion':metric([r for r in allrows if r['group']!='S']),
 'primitive_direction':{g+'_'+str(d):metric([r for r in allrows if r['group']==g and r['direction']==d]) for g in ['M_first','M_second','T','S'] for d in range(4)},
 'logical_step':{str(step):metric([r for r in allrows if r['logical_step']==step and r['group']!='S']) for step in range(2)},
 'family_motion':{name+'_'+str(seed):metric([r for r in allrows if (r['map'],r['seed'])==(name,seed) and r['group']!='S']) for name,seed in familykeys},
 'history_availability':{label:metric([r for r in allrows if r['group']!='S' and (any(r['features'][7:10]) if present else not any(r['features'][7:10]))]) for label,present in [('no_relevant_completed_history',False),('relevant_completed_history',True)]}}
prediction['unweighted_family_motion_metrics']={p:{k:statistics.mean(v[p][k] for v in prediction['family_motion'].values()) for k in ['MAE','RMSE','bias','median_abs','p95_abs']} for p in ['history','geometry','learned']}
(H/'prediction_same_hm_traces.json').write_text(json.dumps(prediction,indent=2)+'\n')
print(json.dumps({'aggregate':aggregate,'paired':{k:v['descriptive_intervals'] for k,v in paired.items()}},indent=2))
