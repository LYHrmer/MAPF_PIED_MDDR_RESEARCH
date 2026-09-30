"""Use actual frozen model/history predictions; no trajectory/test performance selection."""
from common import HERE,NATIVE,sha,events,forecast,write
import json,os,subprocess
P=HERE.parent/'gpibt_lsmart_error_model_20260930_r4';model=json.loads((HERE/'trained_model.json').read_text());layout=json.loads((HERE/'map.json').read_text())['layout']
cases=[];changes={'analytic':0,'history':0,'learned':0}
for condition in ['nominal','slow065','slow085','axis']:
 src=P/'attempts'/f'cal_s51_{condition}_zero'/'decisions.jsonl'
 for d in events(src):
  results={}
  for policy in ['zero','analytic','history','learned']:
   fc=forecast(d['forecast']['context'],d['view'],layout,policy,model,1.)
   req=d['request']|{'priority_bias':fc['bias']};env=os.environ.copy();env['GPIBT_R0_SEED']='51'
   p=subprocess.run(['rtk','proxy',str(NATIVE/'gpibt_bridge')],input=json.dumps(req)+'\n',text=True,capture_output=True,timeout=20,env=env)
   assert p.returncode==0,p.stderr
   results[policy]={'forecast':fc,'request':req,'result':json.loads(p.stdout),'stderr':p.stderr}
  for policy in changes:changes[policy]+=results[policy]['result']['actions']!=results['zero']['result']['actions']
  cases.append({'cal_condition':condition,'cal_sequence':d['forecast']['context']['freeze_sequence'],'source_sha256':sha(src),'results':results})
write(HERE/'calibration_rank_probe.json',{'status':'PASSED_ACTUAL_MODEL_RANK_ACTION_INFLUENCE' if changes['learned']>0 else 'FAILED_NO_ACTUAL_MODEL_ACTION_INFLUENCE','public_fixtures':len(cases),'action_changed_fixtures':changes,'cold_start_not_live_counterfactual_replay':True,'model_sha256':sha(HERE/'trained_model.json'),'cases':cases})
counts={p:{'nonzero_bias_fixtures':sum(c['results'][p]['forecast']['bias']!=[0.,0.] for c in cases),'search_order_changes':sum(c['results'][p]['result']['priority_adapter']['search_order']!=c['results']['zero']['result']['priority_adapter']['search_order'] for c in cases),'action_changes':changes[p]} for p in changes}
write(HERE/'calibration_rank_probe_summary.json',{'fixtures':len(cases),'counts':counts,'test_permitted':changes['learned']>0})
print(json.dumps({'fixtures':len(cases),'counts':counts},indent=2))
assert changes['learned']>0,'actual learned rank bias has no calibration action influence'
