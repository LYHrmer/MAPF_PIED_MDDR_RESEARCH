"""Post-test descriptive audit only; no fitting, parameter changes or extra episodes."""
from pathlib import Path
import json,statistics
from public_model import predict
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
m=json.loads((H/'model_freeze.json').read_text());specs=json.loads((H/'runs.json').read_text())['runs'];sets={'calibration':json.loads((H/'training_rows.json').read_text())['calibration'],'heldout_same_hm':[]}
for s in specs:
    if s['split']=='test' and s['policy']=='hm':sets['heldout_same_hm'].extend(json.loads((O/'runs'/s['id']/'supervised_rows.json').read_text())['rows'])
metrics={}
for name,rows in sets.items():
    metrics[name]={}
    for group in ['M_first','M_second','T','S']:
        for direction,dname in enumerate(['E','S','W','N']):
            rr=[r for r in rows if r['group']==group and r['direction']==direction]
            if not rr:continue
            v={'n':len(rr),'mean_D':statistics.mean(r['duration'] for r in rr)}
            for pol in ['history','learned']:
                pred=[predict(r['features'],group,pol,m) for r in rr];er=[p-r['duration'] for p,r in zip(pred,rr)]
                v[pol]={'mean_prediction':statistics.mean(pred),'bias_prediction_minus_D':statistics.mean(er),'MAE':statistics.mean(map(abs,er))}
            metrics[name][group+'_'+dname]=v
out=[]
for r in json.loads((H/'summary.json').read_text())['history_learned_divergence']:
    diff=r['first_action_divergence']
    if not diff:continue
    name,seed,cond=r['world'];calls={}
    for pol in ['history','learned']:
        s=next(s for s in specs if (s['split'],s['map'],s['seed'],s['condition'],s['policy'])==('test',name,seed,cond,pol))
        decisions=[json.loads(x) for x in (O/'runs'/s['id']/'decisions.jsonl').open()];calls[pol]=decisions[diff['batch']]['calls'][diff['logical_step']]
    assert calls['history']['request']['mapf_instance']==calls['learned']['request']['mapf_instance']
    h=calls['history'];l=calls['learned'];parts=[p for row in h['forecast']['estimates'] for edge in row for p in edge['parts'] if p['group']!='S']
    value={'world':r['world'],'first_divergence':diff,'completed_rows':h['completed_rows'],'public_last_sequence':h['public_last_sequence'],
           'no_completed_online_history':h['completed_rows']==0,'history_feature_count_max':{'agent_geometry':max(p['features'][7]*16 for p in parts),'agent_direction':max(p['features'][8]*8 for p in parts),'pooled_direction':max(p['features'][9]*64 for p in parts)},
           'actions_history':h['result']['actions'],'actions_learned':l['result']['actions'],'changed_agents':[a for a,(x,y) in enumerate(zip(h['result']['actions'],l['result']['actions'])) if x!=y],
           'all_agent_direction_estimates':[]}
    for a,(hx,lx) in enumerate(zip(h['forecast']['estimates'],l['forecast']['estimates'])):
        value['all_agent_direction_estimates'].append({'agent':a,'edges':[{'direction':e['direction'],'turns':sum(p['group']=='T' for p in e['parts']),'station':e['station'],'history_ticks':e['edge_ticks'],'learned_ticks':le['edge_ticks'],'primitive_predictions':[{'group':p['group'],'direction':p['direction'],'history_ticks':p['mean_ticks'],'learned_ticks':lp['mean_ticks'],'features':p['features']} for p,lp in zip(e['parts'],le['parts'])]} for e,le in zip(hx,lx)]})
    out.append(value)
result={'posthoc_descriptive_only':True,'no_new_native_runs':True,'no_model_change':True,'prediction_bias_by_primitive_direction':metrics,'first_divergences':out}
(H/'bias_and_divergence.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'first_divergences':[{k:v for k,v in x.items() if k!='all_agent_direction_estimates'} for x in out],'heldout_bias':metrics['heldout_same_hm']},indent=2))
