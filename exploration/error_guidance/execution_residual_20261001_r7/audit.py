"""Inherited independent geometry/action replay plus causal predictor binding."""
from pathlib import Path
import hashlib,importlib.util,json,math,statistics,sys
from public_model import PublicHistory,forecast,predict
HERE=Path(__file__).resolve().parent;PARENT=HERE.parent/'published_continuous_execution_20261001_r6c'
OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/HERE.name
sp=importlib.util.spec_from_file_location('mapping',PARENT/'mapping_replay.py');mapping=importlib.util.module_from_spec(sp);sp.loader.exec_module(mapping)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def check(spec):
 dst=OUT/'runs'/spec['id'];receipt=json.loads((dst/'receipt.json').read_text());assert receipt['error'] is None
 for p,h in receipt['files'].items():assert sha(dst/p)==h,p
 es=[json.loads(s) for s in (dst/'events.jsonl').open()];ds=[json.loads(s) for s in (dst/'decisions.jsonl').open()]
 inp=HERE/'inputs'/spec['input_id'];layout=json.loads((inp/'map.json').read_text())['layout'];env=json.loads((inp/'environment.json').read_text())
 filtered=[];front={};ack_speed=0.
 for e in es:
  if e['kind']=='control' and e['control']['phase']=='front' and e['control']['type']==0:
   c=e['control'];assert len(c['nodes'])==1;front[(e['robot'],c['nodes'][0])]=(e['tick'],c)
  elif e['kind']=='end' and (e['robot'],e['node']) in front:
   t,c=front[(e['robot'],e['node'])];assert t==e['tick'] and abs(e['observation']['speed_cm_s'])<=20.;ack_speed=max(ack_speed,abs(e['observation']['speed_cm_s']))
  if e['kind']=='control' and e['control']['phase'] not in ('front','service_decrement'):continue
  filtered.append(dict(e,sequence=len(filtered)))
 result=mapping.check(filtered,ds,False,True,layout,8,4000)
 assert result['horizon_tick']==4000 and result['observation_count']==32000
 prefixes=[[] for _ in range(8)]
 for tid,owner,goal in result['assigned_task_prefix']:prefixes[owner].append(goal)
 for a,goals in enumerate(prefixes):assert goals==env['FIFO_goals'][a][:len(goals)]
 cfg=json.loads((HERE/'configs'/(spec['id']+'.json')).read_text());calls=0;nonzero=0
 for d in ds:
  r=d['result'];assert r['objective']==(4 if spec['policy']=='trained' else 3)
  assert r['initial_priority_seed']==spec['seed'] and r['network_parameters']==cfg['parameters']
  calls+=r.get('r7_edge_cost_calls',0);nonzero+=r.get('r7_nonzero_edge_cost_calls',0)
 # Reconstruct the public-only history at each recorded decision cutoff.
 public=[json.loads(s) for s in (dst/'public_events.jsonl').open()];hist=PublicHistory();index=0
 checkpoint=json.loads((HERE/'model_freeze.json').read_text()) if spec['split']=='test' else None
 for d in ds:
  while index<len(public) and public[index]['sequence']<=d['public_last_sequence']:
   hist.accept(public[index]);index+=1
  assert hist.last_sequence==d['public_last_sequence'] and len(hist.rows)==d['public_history_rows']
  if d['forecast'] is not None:
   expected=forecast(hist,d['view'],layout,spec['policy'],checkpoint)
   assert expected==d['forecast'] and expected['cost_by_agent_destination']==d['request']['edge_costs']
 while index<len(public):hist.accept(public[index]);index+=1
 data=json.loads((dst/'supervised_rows.json').read_text());assert hist.rows==data['rows']
 assert [r for r in hist.moves.values() if r['duration'] is None]==data['censored']
 metrics={}
 if checkpoint:
  for policy in ('history','learned'):
   errors=[predict(r['features'],r['turns'],policy,checkpoint['ridge'])-r['duration'] for r in hist.rows]
   q=checkpoint['calibration'][policy]['q90_absolute_error']
   metrics[policy]={'rows':len(errors),'MAE':statistics.mean(abs(e) for e in errors),'RMSE':math.sqrt(statistics.mean(e*e for e in errors)),'within_calibration_margin':sum(abs(e)<=q for e in errors)/len(errors)}
 return {'passed':True,'spec':spec,'normal_station_END':result['task_services'],'completed_tasks':result['completed_tasks'],
  'unfinished_tasks':result['unfinished_tasks'],'views':len(ds),'rows':len(hist.rows),'censored_moves':len(data['censored']),
  'candidate_edge_calls':calls,'candidate_nonzero_calls':nonzero,'prediction_metrics':metrics,
  'maximum_MOVE_ACK_internal_speed_cm_s':ack_speed,'sampled_min_center_distance_m':result['sampled_min_center_distance_m'],
  'maximum_ACK_endpoint_error_m':max(r['endpoint_error_m'] for r in result['ends']),
  'planner_request_seconds':sum(d['planner_request_wall_seconds'] for d in ds),'forecast_seconds':sum(d['forecast_wall_seconds'] for d in ds),
  'raw_sha256':sha(dst/'events.jsonl'),'decisions_sha256':sha(dst/'decisions.jsonl')}

def main(phase):
 out={}
 for spec in json.loads((HERE/'runs.json').read_text())['runs']:
  if (spec['split']=='test')!=(phase=='test'):continue
  try:r=check(spec)
  except Exception as e:r={'passed':False,'error':repr(e)}
  out[spec['id']]=r;print(spec['id'],r.get('normal_station_END'),r['passed'],r.get('error',''),flush=True)
 (HERE/f'audit_{phase}.json').write_text(json.dumps({'all_passed':all(r['passed'] for r in out.values()),'runs':out,'auditor_sha256':sha(__file__)},indent=2)+'\n')
 if not all(r['passed'] for r in out.values()):raise SystemExit(1)
if __name__=='__main__':main(sys.argv[1])
