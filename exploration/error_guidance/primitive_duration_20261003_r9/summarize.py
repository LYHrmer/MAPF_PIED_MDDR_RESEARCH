from pathlib import Path
import csv,json,itertools,statistics
from public_model import predict
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
specs=[s for s in json.loads((H/'runs.json').read_text())['runs'] if s['split']=='test'];rs={s['id']:json.loads((H/'per_run_audits'/(s['id']+'.json')).read_text()) for s in specs};assert all(r['passed'] for r in rs.values())
(H/'audit_test.json').write_text(json.dumps({'all_passed':True,'runs':rs},indent=2)+'\n');rows=[]
for s in specs:
    r=rs[s['id']];rows.append(dict(s,tasks=r['normal_station_END'],restricted_first10=r['fixed_first10_restricted_ticks'],rows=r['rows'],censored=r['censored'],nonzero_edge_calls=r['candidate_nonzero_calls'],planner_wall=r['planner_wall'],forecast_wall=r['forecast_wall']))
with (H/'summary.csv').open('w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator='\n');w.writeheader();w.writerows(rows)
aggregate={pol:{k:sum(r[k] for r in rows if r['policy']==pol) for k in ['tasks','restricted_first10','rows','censored','nonzero_edge_calls','planner_wall','forecast_wall']} for pol in ['hm','history','learned']}
worlds=[];divergences=[]
for name,seed,cond in itertools.product(['empty-32-32','random-32-32-10'],[951921,951922],['nominal','axis']):
    world={'map':name,'seed':seed,'condition':cond}
    for pol in ['hm','history','learned']:
        r=next(r for r in rows if (r['map'],r['seed'],r['condition'],r['policy'])==(name,seed,cond,pol));world[pol]={'tasks':r['tasks'],'restricted':r['restricted_first10']}
    hs=next(s for s in specs if (s['map'],s['seed'],s['condition'],s['policy'])==(name,seed,cond,'history'));ls=next(s for s in specs if (s['map'],s['seed'],s['condition'],s['policy'])==(name,seed,cond,'learned'))
    hd=[json.loads(x) for x in (O/'runs'/hs['id']/'decisions.jsonl').open()];ld=[json.loads(x) for x in (O/'runs'/ls['id']/'decisions.jsonl').open()];diff=None
    for i,(a,b) in enumerate(zip(hd,ld)):
        for step in range(2):
            if a['calls'][step]['result']['actions']!=b['calls'][step]['result']['actions']:
                diff={'batch':i,'logical_step':step,'tick':a['snapshot']['tick'],'same_actual_view':a['view']==b['view'],'same_snapshot':a['snapshot']==b['snapshot'],'same_frontier':a['calls'][step]['request']['mapf_instance']==b['calls'][step]['request']['mapf_instance']};break
        if diff:break
    hserv={(v['agent'],v['ordinal']):v['tick'] for v in rs[hs['id']]['services']};lserv={(v['agent'],v['ordinal']):v['tick'] for v in rs[ls['id']]['services']};common=set(hserv)&set(lserv);deltas=[lserv[k]-hserv[k] for k in common]
    divergences.append({'world':[name,seed,cond],'first_action_divergence':diff,'common_served':len(common),'learned_earlier':sum(d<0 for d in deltas),'same':sum(d==0 for d in deltas),'later':sum(d>0 for d in deltas),'common_tick_delta':sum(deltas),'tasks_delta':world['learned']['tasks']-world['history']['tasks'],'fixed_first10_delta':world['learned']['restricted']-world['history']['restricted']})
    worlds.append(world)
out={'runs':len(specs),'aggregate':aggregate,'worlds':worlds,'history_learned_divergence':divergences,'independent_task_families':4,'conditions_paired_within_family':True}
(H/'summary.json').write_text(json.dumps(out,indent=2)+'\n')
model=json.loads((H/'model_freeze.json').read_text());prediction={};allrows=[]
for s in specs:
    if s['policy']=='hm':allrows.extend(dict(r,run=s['id']) for r in json.loads((O/'runs'/s['id']/'supervised_rows.json').read_text())['rows'])
for step in range(2):
    for group in ['M_first','M_second','T','S','motion']:
        selected=[r for r in allrows if r['logical_step']==step and (r['group']!='S' if group=='motion' else r['group']==group)]
        value={'n':len(selected),'mean_D':statistics.mean(r['duration'] for r in selected),'mean_own_prefix_wait':statistics.mean(r['begin_tick']-r['admit_tick'] for r in selected),'mean_admit_wait':statistics.mean(r['admit_tick']-r['proposal_tick'] for r in selected)}
        for pol in ['history','learned']:
            errors=[predict(r['features'],r['group'],pol,model)-r['duration'] for r in selected]
            value[pol]={'MAE':statistics.mean(map(abs,errors)),'bias':statistics.mean(errors),'RMSE':(statistics.mean(e*e for e in errors))**.5}
        prediction[f'step{step}_{group}']=value
(H/'prediction_same_hm_traces.json').write_text(json.dumps({'source':'same eight hm held-out trajectories; no fit/calibration tuning','by_step_geometry':prediction},indent=2)+'\n')
print(json.dumps(out,indent=2))
