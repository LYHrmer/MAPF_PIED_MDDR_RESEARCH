"""Replay actual native permission/service chain and independent adapter causality."""
from common import HERE,NATIVE,sha,events,context,forecast,public_steps,features,write
from mapping_replay import check as native_check
import copy,json,math
def require(ok,why):
 if not ok:raise ValueError(why)
def close(a,b):return abs(a-b)<1e-9
def check(es,ds,spec,model,amp):
 require(all(e['sequence']==i for i,e in enumerate(es)),'raw_sequence')
 filtered=[]
 for e in es:
  if e['kind']=='control' and e['control']['phase'] not in ('front','service_decrement'):continue
  x=copy.deepcopy(e);x['sequence']=len(filtered);filtered.append(x)
 result=native_check(filtered,ds,False);require(result['horizon_tick']==400 and result['observation_count']==800,'full400_horizon')
 prev=None;oldgoals=None;flips=0
 for d in ds:
  fc=d['forecast'];freeze=fc['context']['freeze_sequence'];prefix=es[:freeze+1]
  require(prefix[-1]['kind']=='view' and prefix[-1]['view']==d['view'],'context_view_boundary')
  expect=forecast(context(prefix),d['view'],json.loads((HERE/'map.json').read_text())['layout'],spec['policy'],model,amp)
  require(fc==expect,'forecast_not_causal_shared_interface')
  require(d['request']['priority_bias']==fc['bias'],'request_forecast_binding')
  p=d['result']['priority_adapter'];require(p['bias']==fc['bias'],'actual_bias_binding')
  if prev:
   require(all(close(x,y) for x,y in zip(p['p_before'],prev['p_after_restore'])),'aging_incoming')
   require(all(close(x,y) for x,y in zip(p['p_copy_before'],prev['p_copy_after_restore'])),'priority_copy_incoming')
  goals=[d['view']['mapf_instance']['goals'][a][0]['location'] for a in range(2)]
  base=[p['p_copy_before'][a] if oldgoals is None or goals[a]!=oldgoals[a] else p['p_before'][a]+1 for a in range(2)]
  require(all(close(x,y) for x,y in zip(base,p['effective_base'])),'original_effective_priority')
  require(all(close(p['effective_applied'][a],base[a]+p['bias'][a]) for a in range(2)),'applied_priority')
  require(all(close(p['p_after_restore'][a],base[a]) and close(p['p_copy_after_restore'][a],p['p_copy_before'][a]) for a in range(2)),'aging_restore')
  order=p['search_order'];require(sorted(order)==[0,1] and p['effective_applied'][order[0]]>=p['effective_applied'][order[1]]-1e-10,'actual_search_order')
  if abs(base[0]-base[1])>1e-9 and order[0]!=int(base[1]>base[0]):flips+=1
  prev=p;oldgoals=goals
 observations={(e['robot'],e['tick']):e['observation'] for e in es if e['kind']=='observation'}
 wheels={(e['robot'],e['tick']):e['control'] for e in es if e['kind']=='control' and e['control']['phase']=='wheel_command'}
 require(len(wheels)==800,'actual_wheel_delivery_coverage')
 triggers=[e for e in es if e['kind']=='control' and e['control']['phase']=='active_trigger'];eligible=[]
 for t in range(1,400):
  o=observations[('0',t)];old=wheels[('0',t-1)]
  c=next((e['control'] for e in es if e['tick']==t and e.get('robot')=='0' and e['kind']=='control' and e['control']['phase']=='front'),None)
  if c and c['type']==0 and c['nodes'] and (old['issued_left_cm_s']!=0 or old['issued_right_cm_s']!=0) and o['displacement_m']>1e-6:eligible.append(t)
 # During the first pause tick native front is suppressed; trigger carries same live identity.
 if spec['condition']=='unknown_pause' and triggers:eligible.append(triggers[0]['tick'])
 require(len(triggers)<=1 and bool(triggers)==bool(eligible),'trigger_existence')
 if triggers:require(triggers[0]['tick']==min(eligible),'first_active_trigger')
 pauses=[e for e in es if e['kind']=='control' and e['control']['phase']=='pause']
 if spec['condition']=='unknown_pause' and triggers:
  T=triggers[0]['tick'];require([e['tick'] for e in pauses]==list(range(T,T+20)),'actual20pause')
  for e in pauses:
   c=e['control'];require(c['nodes']==triggers[0]['control']['nodes'] and c['queue_size']==triggers[0]['control']['queue_size'],'pause_identity_held')
   require(wheels[('0',e['tick'])]['issued_left_cm_s']==wheels[('0',e['tick'])]['issued_right_cm_s']==0,'actual_zero_pause_wheels')
   require(not any(x['kind'] in ('end','admit') and x.get('robot')=='0' and x['tick']==e['tick'] for x in es),'pause_no_permission_progress')
 else:require(not pauses,'unexpected_pause')
 return result|{'priority_search_order_flips':flips,'actual_trigger_tick':triggers[0]['tick'] if triggers else None,'raw_event_count':len(es),'actual_wheel_commands':len(wheels)}
def main():
 frozen=json.loads((HERE/'model_freeze.json').read_text());model=json.loads((HERE/'trained_model.json').read_text());out={}
 for spec in json.loads((HERE/'runs.json').read_text())['runs']:
  runid=spec['id'];p=HERE/'attempts'/runid
  if not p.exists():continue
  receipt=json.loads((p/'receipt.json').read_text());es=events(p/'events.jsonl');ds=events(p/'decisions.jsonl');amp=frozen['amplitude'] if spec['split']=='test' else 0
  try:
   require(receipt['error'] is None,'native_error');r=check(es,ds,spec,model if spec['split']=='test' else None,amp)
   require(receipt['run_spec']==spec and receipt['whole_trial_limit_seconds_including_cleanup']==54 and receipt['wall_seconds']<=54,'run_input_receipt')
   require(receipt['model_sha256']==(sha(HERE/'trained_model.json') if spec['split']=='test' else None),'model_identity')
   for path,h in receipt['binary_identities'].items():require(sha(path)==h,'current_binary_identity')
   if ds:
    negative={}
    for name,mutate in [('private_pose_feature',lambda z:z[0]['forecast']['context'].__setitem__('actual_pose',[0,0])),('wrong_bias',lambda z:z[0]['request']['priority_bias'].__setitem__(0,99)),('unrestored_aging',lambda z:z[0]['result']['priority_adapter']['p_after_restore'].__setitem__(0,99))]:
     bad=copy.deepcopy(ds);mutate(bad)
     try:check(es,bad,spec,model if spec['split']=='test' else None,amp)
     except (ValueError,KeyError,AssertionError) as e:negative[name]={'rejected':True,'reason':str(e)}
     else:raise ValueError('mutation_passed_'+name)
    r['negative_checks']=negative
   r|={'passed':True,'trace_sha256':sha(p/'events.jsonl'),'decisions_sha256':sha(p/'decisions.jsonl')}
  except Exception as e:r={'passed':False,'error':str(e)}
  out[runid]=r;print(runid,r['passed'],r.get('error',''),flush=True)
 write(HERE/'audit.json',{'all_available_passed':all(r['passed'] for r in out.values()),'runs':out,'auditor_sha256':sha(HERE/'audit.py'),'mapping_replay_sha256':sha(HERE/'mapping_replay.py')})
if __name__=='__main__':main()
