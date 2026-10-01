"""Exact native execution plus official planner/network/initialization identity."""
from pathlib import Path
import hashlib,json,math,statistics
from mapping_replay import check as replay
HERE=Path(__file__).resolve().parent;OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/HERE.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def rows(p):
 with Path(p).open() as f:return [json.loads(s) for s in f]
def require(ok,why):
 if not ok:raise ValueError(why)
def check(spec):
 path=OUT/'runs'/spec['id'];receipt=json.loads((path/'receipt.json').read_text());require(receipt['error'] is None,'native_failed')
 es=rows(path/'events.jsonl');ds=rows(path/'decisions.jsonl');N=spec['N'];H=spec['horizon_ticks'];inp=HERE/'inputs'/spec['map'];layout=json.loads((inp/'map.json').read_text())['layout'];environment=json.loads((inp/'environment.json').read_text());cfg=json.loads((HERE/(spec['policy']+'_config.json')).read_text())
 require([e['sequence'] for e in es]==list(range(len(es))),'unfiltered_native_sequence')
 move_front={};move_end_count=0;max_move_ack_speed=0.
 for e in es:
  if e['kind']=='control' and e['control']['phase']=='front' and e['control']['type']==0:
   c=e['control'];require(len(c['nodes'])==1,'MOVE_front_must_not_merge');move_front[(e['robot'],c['nodes'][0])]=(e['tick'],c)
  elif e['kind']=='end' and (e['robot'],e['node']) in move_front:
   tick,c=move_front[(e['robot'],e['node'])];require(tick==e['tick'] and c['nodes']==[e['node']],'MOVE_ACK_current_single_node')
   speed=abs(e['observation']['speed_cm_s']);require(speed<=20.,'original_MOVE_stop_predicate');max_move_ack_speed=max(max_move_ack_speed,speed);move_end_count+=1
 filtered=[]
 for e in es:
  if e['kind']=='control' and e['control']['phase'] not in ['front','service_decrement']:continue
  z=e.copy();z['sequence']=len(filtered);filtered.append(z)
 result=replay(filtered,ds,False,True,layout,N,H);require(result['observation_count']==N*H and result['latest_terminal_pose_tick']==H-1,'complete_physical_horizon')
 views=[e for e in es if e['kind']=='view'];require([s['location'] for s in views[0]['view']['mapf_instance']['starts']]==environment['starts'][:N],'numeric_robot_initial_mapping')
 prefix=[[] for _ in range(N)]
 for tid,owner,goal in result['assigned_task_prefix']:prefix[owner].append(goal)
 for owner,goals in enumerate(prefix):require(goals==environment['FIFO_goals'][owner][:len(goals)],'real_head_FIFO_owner')
 ids=None;prev=None;reveal=[None]*N;lastids=[None]*N;calls=0
 for i,d in enumerate(ds):
  r=d['result'];require(r['objective']==(3 if spec['policy']=='hm_GPIBT' else 4),'published_objective');require(r['parameter_count']==560 and r['network_parameters']==cfg['parameters'],'actual560weights')
  require(r['initial_priority_seed']==cfg['initial_priority_seed'] and r['rand_seed']==cfg['initial_priority_seed'],'common_initial_seed')
  if ids is None:
   ids=r['initial_ids'];require(sorted(ids)==list(range(N)),'initial_permutation')
   p=[0.]*N
   for k,a in enumerate(ids):p[a]=(N-k)/(N+1.)
   require(all(abs(a-b)<1e-12 for a,b in zip(p,r['p_before'])) and r['p_copy_before']==r['p_before'],'author_initial_priority_formula')
  require(r['initial_ids']==ids and sorted(r['search_order'])==list(range(N)),'order_team_identity')
  if prev:require(r['p_before']==prev['p_after'] and r['p_copy_before']==prev['p_copy_after'],'persistent_official_priority_state')
  for a,g in enumerate(d['view']['mapf_instance']['goals']):
   if g[0]['id']!=lastids[a]:reveal[a]=i;lastids[a]=g[0]['id']
  require(r['goal_reveal_plan_steps']==reveal,'current_task_reveal_age')
  calls+=r['network_forward_calls'];require(calls==r['network_forward_calls_cumulative'],'official_forward_counter')
  prev=r
 require(calls>0 if spec['policy']=='trained' else calls==0,'actual_neural_method_activation')
 wheels={(e['robot'],e['tick']):e for e in es if e['kind']=='control' and e['control']['phase']=='wheel_command'};require(len(wheels)==N*H,'delivered_wheel_coverage')
 triggers=[e for e in es if e['kind']=='control' and e['control']['phase']=='active_trigger'];pauses=[e for e in es if e['kind']=='control' and e['control']['phase']=='pause'];require(len(triggers)==1,'first_live_trigger')
 trigger=triggers[0];T=trigger['tick'];o=next(e['observation'] for e in es if e['kind']=='observation' and e['robot']=='0' and e['tick']==T);w=wheels[('0',T-1)]['control'];require(trigger['robot']=='0' and trigger['control']['type']==0 and trigger['control']['nodes'] and o['displacement_m']>1e-6 and (w['issued_left_cm_s'] or w['issued_right_cm_s']),'actual_active_MOVE_trigger')
 resumes=[e for e in es if e['kind']=='control' and e['control']['phase']=='active_resume']
 if spec['condition']=='unknown_pause':
  require(len(resumes)==1 and resumes[0]['tick']==T+20,'actual_pause_resume')
  require([e['tick'] for e in pauses]==list(range(T,T+20)),'true20pause')
  for e in pauses:
   c=e['control'];require(c['nodes']==trigger['control']['nodes'] and c['queue_size']==trigger['control']['queue_size'],'pause_live_identity')
   w=wheels[('0',e['tick'])]['control'];require(w['issued_left_cm_s']==w['issued_right_cm_s']==0,'pause_actual_zero')
   require(not any(x['kind'] in ['end','admit'] and x.get('robot')=='0' and x['tick']==e['tick'] for x in es),'pause_permission_progress')
 else:require(not pauses,'unexpected_pause')
 durations=[d['planner_request_wall_seconds'] for d in ds];sorted_times=sorted(durations)
 return result|{'passed':True,'spec':spec,'wall_seconds':receipt['wall_seconds'],'network_forward_calls':calls,'actual_trigger_tick':T,'actual_pause_ticks':[T,T+19] if pauses else None,'initial_ids':ids,'strict_all_ACK_points_passed':True,'unfiltered_native_sequence_verified':True,'no_merged_MOVE_front_verified':True,'original_MOVE_stop_predicate_verified':True,'move_ACK_count':move_end_count,'maximum_MOVE_ACK_internal_speed_cm_s':max_move_ack_speed,'official_parameters_sha256':hashlib.sha256(json.dumps(cfg['parameters']).encode()).hexdigest(),'planner_wall_total_seconds':sum(durations),'planner_wall_p50_seconds':statistics.median(durations),'planner_wall_p95_seconds':sorted_times[min(len(sorted_times)-1,math.ceil(.95*len(sorted_times))-1)],'raw_sha256':sha(path/'events.jsonl'),'decision_sha256':sha(path/'decisions.jsonl'),'completed_FIFO_goals_by_owner':prefix}
def main():
 out={}
 for spec in json.loads((HERE/'runs.json').read_text())['runs']:
  path=OUT/'runs'/spec['id']
  if not (path/'receipt.json').exists():continue
  try:r=check(spec)
  except Exception as e:r={'passed':False,'error':str(e),'exception':type(e).__name__}
  out[spec['id']]=r;print(spec['id'],r['passed'],r.get('error',''),flush=True)
 (HERE/'audit.json').write_text(json.dumps({'all_available_passed':all(r['passed'] for r in out.values()),'runs':out,'auditor_sha256':sha(HERE/'audit.py'),'mapping_replay_sha256':sha(HERE/'mapping_replay.py')},indent=2)+'\n')
if __name__=='__main__':main()
