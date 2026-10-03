"""Offline one-call intervention on cloned deterministic author planner state.

Replays the exact full-policy request prefix. This is not a new simulation and
cannot establish task effects for the unexecuted zero-history branch.
"""
from pathlib import Path
import copy,json,os,subprocess
from public_model import PublicHistory,forecast
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
bridge=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/local_dependency_20261001_r8/bridge_candidate')
m=json.loads((H/'model_freeze.json').read_text());specs=json.loads((H/'runs.json').read_text())['runs']
attribution=json.loads((H/'decision_attribution.json').read_text());targets={}
for s in specs:
 if s['policy']=='learned':
  targets[(s['id'],0,0)]={'reason':['first_decision']}
  targets[(s['id'],10,0)]={'reason':['posthoc_fixed_batch10_history_probe']}
for pair in attribution['pair_divergences']:
 if 'learned' not in pair['pair']:continue
 d=pair['first_action_divergence']
 if not d or not d['same_frontier']:continue
 s=next(s for s in specs if (s['map'],s['seed'],s['condition'],s['policy'])==(*pair['world'],'learned'))
 targets.setdefault((s['id'],d['batch'],d['step']),{'reason':[]})['reason'].append('_vs_'.join(pair['pair']))
results=[]
for (ident,batch,step),info in targets.items():
 s=next(s for s in specs if s['id']==ident);ds=[json.loads(line) for line in (O/'runs'/ident/'decisions.jsonl').open()];d=ds[batch];call=d['calls'][step];hist=PublicHistory(m['d0'])
 for line in (O/'runs'/ident/'public_events.jsonl').open():
  e=json.loads(line)
  if e['sequence']>d['public_last_sequence']:break
  hist.accept(e)
 zero=PublicHistory(m['d0']);zero.last_sequence=hist.last_sequence
 layout=json.loads((H/'inputs'/s['input_id']/'map.json').read_text())['layout'];view={'mapf_instance':call['request']['mapf_instance']}
 forecasts={'full':forecast(hist,view,layout,'learned',m),'full_zero_history':forecast(zero,view,layout,'learned',m),'geometry':forecast(hist,view,layout,'geometry',m),'history':forecast(hist,view,layout,'history',m)}
 prefix=[c for z in ds[:batch] for c in z['calls']]+d['calls'][:step];branches={}
 for name,fc in forecasts.items():
  env=os.environ.copy();env['LD_LIBRARY_PATH']='/home/lyh/.local/lib:'+env.get('LD_LIBRARY_PATH','')
  p=subprocess.Popen(['rtk','proxy',str(bridge),str(H/'configs'/(ident+'.json'))],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,env=env)
  try:
   for old in prefix:
    p.stdin.write(json.dumps(old['request'])+'\n');p.stdin.flush();rr=json.loads(p.stdout.readline());assert rr['actions']==old['result']['actions'] and rr['step']==old['result']['step']
   request=copy.deepcopy(call['request']);request['edge_costs']=fc['cost_by_agent_destination'];p.stdin.write(json.dumps(request)+'\n');p.stdin.flush();rr=json.loads(p.stdout.readline())
   assert rr['step']==call['result']['step'];branches[name]={'actions':rr['actions'],'search_order':rr['search_order'],'priority_before':rr['p_before'],'priority_after':rr['p_after'],'nonzero_edge_cost_calls':rr['r7_nonzero_edge_cost_calls']}
   if name=='full':assert rr['actions']==call['result']['actions'] and rr['p_before']==call['result']['p_before']
  finally:
   p.stdin.close();p.wait(timeout=5);assert p.returncode==0
 assert len({json.dumps(v['priority_before']) for v in branches.values()})==1
 results.append({'run':ident,'batch':batch,'step':step,'tick':d['snapshot']['tick'],'completed_history':len(hist.rows),'reason':info['reason'],'exact_prefix_calls':len(prefix),'branches':branches,'full_history_action_effect':branches['full']['actions']!=branches['full_zero_history']['actions'],'full_geometry_action_difference':branches['full']['actions']!=branches['geometry']['actions']})
 print(ident,batch,step,'history effect',results[-1]['full_history_action_effect'],flush=True)
out={'passed':True,'scope':'offline single-call author bridge intervention, exact request prefix and priority state; no counterfactual task claim','batch10_status':'added after partial raw runs as descriptive probe when online history exists; not preregistered endpoint, no selection by effect','no_additional_native_episodes':True,'target_count':len(results),'full_baseline_action_replay_exact':True,'results':results}
(H/'counterfactual_decisions.json').write_text(json.dumps(out,indent=2)+'\n')
