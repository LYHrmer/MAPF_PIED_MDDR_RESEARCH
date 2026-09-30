"""Independent raw reconstruction of FIFO and whole-MOVE supervision boundaries."""
from pathlib import Path
import hashlib,json,math,statistics,copy
HERE=Path(__file__).resolve().parent
def load(p):return json.loads(p.read_text())
def rows(p):return [json.loads(s) for s in p.read_text().splitlines()]
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(ok,why):
 if not ok:raise ValueError(why)
def reconstruct(es):
 steps={};node_owner={};pid=None
 for e in es:
  kind=e['kind']
  if kind=='proposal':
   pid=e['proposal']['proposal_id']
   for agent,path in enumerate(e['proposal']['plan']):
    s=[-path[0][0],-path[0][1]];g=[-path[1][0],-path[1][1]]
    if s!=g:steps[(pid,str(agent))]={'proposal':e,'start':s,'goal':g,'dispatch':None,'first':None,'final':None,'end':None,'commands':[],'zeros':0}
  elif kind=='admit' and (pid,e['robot']) in steps:
   s=steps[(pid,e['robot'])]
   if e['actions'] and s['dispatch'] is None:s['dispatch']=e['tick']
   for a in e['actions']:
    if a[3]=='M':
     node_owner[(e['robot'],a[1])]=(pid,e['robot'])
     if [-a[5][1],-a[5][0]]==s['goal']:s['final']=a[1]
  elif kind=='control' and e['control']['phase']=='wheel_command' and (pid,e['robot']) in steps:
   s=steps[(pid,e['robot'])];c=e['control']
   if c['type']==0:
    speed=(abs(c['issued_left_cm_s'])+abs(c['issued_right_cm_s']))/2
    if speed:
     if s['first'] is None:s['first']=e['tick']
     s['commands'].append(speed)
    else:s['zeros']+=1
  elif kind=='end' and (e['robot'],e['node']) in node_owner:
   s=steps[node_owner[(e['robot'],e['node'])]]
   if e['node']==s['final']:s['end']=e
 return steps
def expected_context(es):
 completed=[]
 for (pid,a),s in reconstruct(es).items():
  if s['end'] is not None and s['first'] is not None:
   completed.append({'proposal_id':pid,'agent':a,'axis':int(s['start'][1]!=s['goal'][1]),'length':math.dist(s['start'],s['goal']),
    'first_command_tick':s['first'],'end_tick':s['end']['tick'],'end_sequence':s['end']['sequence'],'duration':s['end']['tick']-s['first'],
    'max_command_cm_s':max(s['commands'],default=0),'mean_command_cm_s':statistics.mean(s['commands']) if s['commands'] else 0,'past_zero_command_ticks':s['zeros']})
 return {'freeze_sequence':es[-1]['sequence'],'completed_steps':completed}
def expected_features(ctx,agent,axis):
 hs=[s for s in ctx['completed_steps'] if s['agent']==str(agent)][-6:];matched=[s for s in hs if s['axis']==axis][-3:];last=hs[-1] if hs else None
 speed=max(10.,last['max_command_cm_s'] if last else 200.);accel=200.;distance=100.;ramp=speed*speed/accel
 seconds=2*math.sqrt(distance/accel) if distance<=ramp else 2*speed/accel+(distance-ramp)/speed
 base=math.ceil(10*seconds)+10;median=statistics.median([s['duration'] for s in hs[-3:]]) if hs else base;axis_median=statistics.median([s['duration'] for s in matched]) if matched else median
 return [base,median,axis_median,last['duration'] if last else base,last['max_command_cm_s'] if last else 200,last['mean_command_cm_s'] if last else 100,int(bool(last and last['axis']==axis)),len(hs),axis]
def check(runid):
 raw=HERE/'attempts'/runid;data=HERE/'datasets'/runid;es=rows(raw/'events.jsonl');ds=rows(raw/'decisions.jsonl');steps=reconstruct(es)
 xs=rows(data/'delivered_context.jsonl');ys=rows(data/'offline_original_MOVE_targets.jsonl');ax=rows(data/'active_delivered_context.jsonl');ay=rows(data/'offline_remaining_targets.jsonl')
 require(len(xs)==len(ys)==len(steps),'original_step_coverage');require([x['key'] for x in xs]==[y['key'] for y in ys],'input_target_key_alignment')
 require(len(ax)==len(ay) and [x['key'] for x in ax]==[y['key'] for y in ay],'active_key_alignment')
 manifest=load(data/'manifest.json');require(manifest['raw_sha256']==digest(raw/'events.jsonl') and manifest['decision_sha256']==digest(raw/'decisions.jsonl'),'raw_identity')
 for n,h in manifest['files'].items():require(digest(data/n)==h,'dataset_file_identity')
 uncensored=0;maxerr=0;node_set=set();end_by_key={}
 for x,y in zip(xs,ys):
  k=(x['proposal_id'],x['agent']);s=steps[k];d=ds[k[0]];end=s['end'];tick=end['tick'] if end else None;dur=tick-s['first'] if tick is not None and s['first'] is not None else None
  require(x['context']==expected_context(es[:x['freeze_sequence']+1]) and x['context']==d['forecast']['context'],'delivered_context_raw_history')
  require(x['features']==expected_features(x['context'],k[1],x['axis']),'training_input_delivered_features')
  require(all(c['end_sequence']<=x['freeze_sequence'] for c in x['context']['completed_steps']),'future_END_leak')
  require(y['first_nonzero_command_tick']==s['first'] and y['normal_full_MOVE_END_tick']==tick and y['final_native_MOVE_node']==s['final'],'whole_MOVE_identity')
  require(y['duration_ticks']==dur and y['right_censored']==(dur is None),'censor_or_duration')
  require(y['original_start_xy_m']==s['start'] and y['original_goal_xy_m']==s['goal'] and y['original_length_m']==1.,'original_grid_step')
  require(y['proposal_received_tick']==s['proposal']['tick'] and y['first_native_dispatch_tick']==s['dispatch'],'proposal_dispatch_boundary')
  require(y['proposal_to_whole_MOVE_END_ticks']==(tick-s['proposal']['tick'] if tick is not None else None),'total_proposal_occupancy')
  require(y['first_dispatch_to_whole_MOVE_END_ticks']==(tick-s['dispatch'] if tick is not None and s['dispatch'] is not None else None),'total_dispatch_occupancy')
  end_by_key[k]=s
  if dur is not None:
   uncensored+=1;node_set.add((k[1],s['final']));o=end['observation'];maxerr=max(maxerr,math.dist([o['x'],o['y']],s['goal']))
 for x,y in zip(ax,ay):
  sequence=x['freeze_sequence'];e=es[sequence];require(e['kind']=='control' and e['control']['phase']=='wheel_command' and e['tick']==x['tick'] and e['robot']==x['agent'],'active_delivered_command_identity')
  pid=None
  for prev in reversed(es[:sequence+1]):
   if prev['kind']=='proposal':pid=prev['proposal']['proposal_id'];break
  s=end_by_key[(pid,x['agent'])];tick=s['end']['tick'] if s['end'] else None;seen=s['first'] is not None and s['first']<=e['tick']
  require(x['features']==expected_features(ds[pid]['forecast']['context'],x['agent'],int(s['start'][1]!=s['goal'][1])) and not x['used_by_active_planner'],'tick_step_start_features')
  require(x['issued_left_cm_s']==e['control']['issued_left_cm_s'] and x['issued_right_cm_s']==e['control']['issued_right_cm_s'] and x['active_nodes']==e['control']['nodes'],'delivered_current_command')
  require(x['first_command_already_delivered']==seen and x['elapsed_from_delivered_first_MOVE_command_ticks']==(e['tick']-s['first'] if seen else 0),'elapsed_not_future')
  require(y['remaining_ticks']==(max(0,tick-e['tick']) if tick is not None else None) and y['right_censored']==(tick is None),'remaining_target_whole_MOVE_or_censor')
  require(y['normal_full_MOVE_END_tick']==tick and y['final_native_MOVE_node']==s['final'],'remaining_whole_END_identity')
  require(y['END_already_delivered']==bool(s['end'] and s['end']['sequence']<sequence),'END_delivery_time')
 a=load(HERE/'audit.json')['runs'][runid];future=load(HERE/'task_environment.json')['agent_goal_lists'];by=[[],[]]
 for tid,owner,goal in a['assigned_task_prefix']:by[owner].append(goal)
 for owner,goals in enumerate(by):require(goals==future[owner][:len(goals)],'environment_FIFO_prefix')
 require(a['task_services']==len(a['completed_tasks']),'actual_service_count')
 return {'passed':True,'original_MOVE_rows':len(xs),'uncensored':uncensored,'censored':len(xs)-uncensored,'active_input_target_rows':len(ax),'full_MOVE_endpoint_max_error_m':maxerr,'original_FIFO_goals_by_owner':by,'actual_services':a['task_services'],'raw_sha256':digest(raw/'events.jsonl')}
def main():
 out={s['id']:check(s['id']) for s in load(HERE/'runs.json')['runs']}
 (HERE/'dataset_audit.json').write_text(json.dumps({'all_passed':all(r['passed'] for r in out.values()),'runs':out,'auditor_sha256':digest(HERE/'dataset_audit.py'),'future_targets_used_as_live_inputs':False},indent=2)+'\n')
 print('PASS',len(out),'runs',sum(r['original_MOVE_rows'] for r in out.values()),'whole MOVE rows',sum(r['active_input_target_rows'] for r in out.values()),'tick rows')
if __name__=='__main__':main()
