"""Replay only the observed zero-policy prefix into fresh official objects before each fork."""
from common import HERE,NATIVE,sha,events,forecast,write
import json,os,subprocess,math
P=HERE.parent/'gpibt_lsmart_error_model_20260930_r4';model=json.loads((HERE/'trained_model.json').read_text());layout=json.loads((HERE/'map.json').read_text())['layout']
cases=[];changes={'analytic':0,'history':0,'learned':0};diagnostics={}
for condition in ['nominal','slow065','slow085','axis']:
 src=P/'attempts'/f'cal_s51_{condition}_zero'/'decisions.jsonl';ds=events(src);rows=[]
 for i,d in enumerate(ds):
  results={}
  for policy in ['zero','analytic','history','learned']:
   fc=forecast(d['forecast']['context'],d['view'],layout,policy,model,1.)
   reqs=[v['request'] for v in ds[:i]]+[d['request']|{'priority_bias':fc['bias']}]
   env=os.environ.copy();env['GPIBT_R0_SEED']='51'
   p=subprocess.run(['rtk','proxy',str(NATIVE/'gpibt_bridge')],input=''.join(json.dumps(r)+'\n' for r in reqs),text=True,capture_output=True,timeout=20,env=env)
   assert p.returncode==0,p.stderr
   returned=[json.loads(l) for l in p.stdout.splitlines()];assert len(returned)==i+1
   for j,v in enumerate(returned[:-1]):assert v['actions']==ds[j]['result']['actions'],'observed prefix reconstruction mismatch'
   result=returned[-1]
   if policy=='zero':
    assert result['actions']==d['result']['actions']
    for key in ['p_before','p_copy_before','effective_base','p_after_restore']:
     assert all(abs(x-y)<1e-9 for x,y in zip(result['priority_adapter'][key],d['result']['priority_adapter'][key])),key
   results[policy]={'forecast':fc,'request':reqs[-1],'result':result,'stderr':p.stderr}
  for policy in changes:changes[policy]+=results[policy]['result']['actions']!=results['zero']['result']['actions']
  starts=[v['location'] for v in d['view']['mapf_instance']['starts']]
  candidates=[]
  goals=[d['view']['mapf_instance']['goals'][a][0]['location'] for a in range(2)]
  for a in range(2):
   s=starts[a];gg=goals[a];cc=[]
   for delta in [1,5,-1,-5]:
    t=s+delta
    if 0<=t<25 and abs(t//5-s//5)+abs(t%5-s%5)==1 and layout[t//5][t%5]!='@' and abs(t//5-gg//5)+abs(t%5-gg%5)<abs(s//5-gg//5)+abs(s%5-gg%5):cc.append(t)
   candidates.append(cc)
  rows.append({'fixture_index':i,'starts':starts,'goals':goals,'manhattan_goal_decreasing_candidates':candidates,'shared_next_vertices':sorted(set(candidates[0])&set(candidates[1])),
   'adjacent_current_cells':abs(starts[0]//5-starts[1]//5)+abs(starts[0]%5-starts[1]%5)==1,
   'original_priority_gap':abs(results['zero']['result']['priority_adapter']['effective_base'][0]-results['zero']['result']['priority_adapter']['effective_base'][1]),
   'policies':{pol:{'signed_prediction_gap':results[pol]['forecast']['predicted_ticks'][0]-results[pol]['forecast']['predicted_ticks'][1],
   'bias':results[pol]['forecast']['bias'],'order_changed':results[pol]['result']['priority_adapter']['search_order']!=results['zero']['result']['priority_adapter']['search_order'],
   'actions_changed':results[pol]['result']['actions']!=results['zero']['result']['actions']} for pol in changes}})
  cases.append({'cal_condition':condition,'fixture_index':i,'source_sha256':sha(src),'results':results})
 diagnostics[condition]={'fixtures':len(rows),'priority_gap_range':[min(r['original_priority_gap'] for r in rows),max(r['original_priority_gap'] for r in rows)],
  'adjacent_states':sum(r['adjacent_current_cells'] for r in rows),'shared_next_vertex_states':sum(bool(r['shared_next_vertices']) for r in rows),
  'policies':{pol:{'prediction_gap_range':[min(r['policies'][pol]['signed_prediction_gap'] for r in rows),max(r['policies'][pol]['signed_prediction_gap'] for r in rows)],
   'deadband_count':sum(abs(r['policies'][pol]['signed_prediction_gap'])<1 for r in rows),'nonzero_bias':sum(r['policies'][pol]['bias']!=[0.,0.] for r in rows),
   'order_flips':sum(r['policies'][pol]['order_changed'] for r in rows),'action_changes':sum(r['policies'][pol]['actions_changed'] for r in rows)} for pol in changes},'rows':rows}
write(HERE/'warm_calibration_probe.json',{'status':'PASSED' if changes['learned'] else 'FAILED_NO_MODEL_ACTION_EFFECT','action_changed_fixtures':changes,'original_zero_prefix_state_reconstruction_passed':True,'model_unchanged_sha256':sha(HERE/'trained_model.json'),'cases':cases})
write(HERE/'calibration_gap_diagnostic.json',diagnostics)
print(json.dumps({'actual_warm_state_action_changes':changes,'condition_summary':{c:{k:v for k,v in d.items() if k!='rows'} for c,d in diagnostics.items()}},indent=2))
