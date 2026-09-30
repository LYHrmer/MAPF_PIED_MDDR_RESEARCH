"""Independent partial-trace audit; passing checks never imply a full trial.

This checks the available real first-step trace. It also reports (rather than
conceals) that its second view violates the strengthened sampled-settled gate.
There are no task-service events in this trace: task service remains untested.
"""
from pathlib import Path
import json, math, hashlib, copy
HERE=Path(__file__).resolve().parent
def require(ok,reason):
    if not ok:raise ValueError(reason)
def distance(a,b):return math.hypot(a['x']-b['x'],a['y']-b['y'])
def check(events,strict_settled=False):
    layout=json.loads((HERE/'map.json').read_text())['layout']
    observed={}; history={}; commands={}; ended=set(); tasks={}; latest_view=None
    ends=[];proposals=0;views=0;min_sep=math.inf; last_tick=-1; sampled_gate_violations=[]
    for seq,e in enumerate(events):
        require(e['sequence']==seq,'sequence')
        require(e['tick']>=last_tick,'time_order');last_tick=e['tick']
        kind=e['kind']
        if kind=='observation':
            r=e['robot'];o=e['observation']
            require(o['tick']==e['tick'],'observation_time')
            require(all(math.isfinite(o[f]) for f in ('x','y','angle','speed_cm_s')),'finite_pose')
            observed[r]=o;history.setdefault(r,[]).append(o)
            if len(observed)==2 and len({o['tick'] for o in observed.values()})==1:
                a,b=observed.values();min_sep=min(min_sep,distance(a,b))
        elif kind in ('invoke','view'):
            s=e['snapshot'];require(s['tick']==e['tick'],'snapshot_time')
            require(s['observations']==observed,'snapshot_not_latest_delivered')
            require(s['joint_settled'] and s['unfinished']==[0,0],'unfinished_at_view')
            require(all(k in ended for k in commands),'unacked_command_at_view')
            for r,o in observed.items():
                require(o['tick']<=e['tick'] and e['tick']-o['tick']<=1,'future_or_stale_observation')
                require(o['queue_size']==0 and o['idle'],'nonidle_at_view')
                if len(history[r])>1:
                    delta=distance(history[r][-2],o)
                    if delta>1e-6:
                        sampled_gate_violations.append({'kind':kind,'tick':e['tick'],'robot':r,'displacement_m':delta})
                        require(not strict_settled,'sampled_settled_gate')
            if kind=='view':
                latest_view=e['view'];views+=1
                inst=latest_view['mapf_instance']
                require(len(inst['starts'])==2 and len(inst['goals'])==2,'team_size')
                for a,(st,gs) in enumerate(zip(inst['starts'],inst['goals'])):
                    require(len(gs)==1,'task_visibility')
                    g=gs[0];require(g['agent_id']==a,'task_owner')
                    value=(a,g['location'])
                    require(g['id'] not in tasks or tasks[g['id']]==value,'task_changed_identity')
                    tasks[g['id']]=value
                    r=str(a);pose=observed[r];loc=st['location']
                    require(math.hypot(pose['x']+loc//5,pose['y']+loc%5)<.03,'start_pose_mismatch')
        elif kind=='proposal':
            require(latest_view is not None,'missing_view')
            p=e['proposal'];proposals+=1
            require(p['view_sha256']==hashlib.sha256(json.dumps(latest_view,sort_keys=True).encode()).hexdigest(),'view_hash')
            require(p['proposal_id']==proposals-1,'proposal_id')
            paths=p['plan'];require(len(paths)==2,'proposal_team')
            for a,path in enumerate(paths):
                require(len(path)==2,'not_single_joint_step')
                start=latest_view['mapf_instance']['starts'][a]['location']
                require(path[0][:2]==[start//5,start%5],'wrong_proposal_start')
                for row,col,t,task in path:
                    require(0<=row<5 and 0<=col<5 and layout[row][col]!='@','invalid_cell')
                require(abs(path[0][0]-path[1][0])+abs(path[0][1]-path[1][1])<=1,'nonadjacent_action')
                goal=latest_view['mapf_instance']['goals'][a][0]
                expected=goal['id'] if path[1][0]*5+path[1][1]==goal['location'] else -1
                require(path[1][3]==expected,'task_annotation')
            require(paths[0][1][:2]!=paths[1][1][:2],'vertex_collision')
            require(not(paths[0][0][:2]==paths[1][1][:2] and paths[1][0][:2]==paths[0][1][:2]),'edge_swap')
        elif kind=='admit':
            for a in e['actions']:
                key=(e['robot'],a[1]);require(key not in commands,'duplicate_admit')
                require(a[0]==e['robot'],'admit_robot')
                commands[key]=a
        elif kind=='end':
            key=(e['robot'],e['node']);require(key in commands,'unknown_end')
            require(key not in ended,'duplicate_end');a=commands[key]
            require(e['observation']==observed[e['robot']],'forged_or_future_end_observation')
            require(e['accepted'],'rejected_end')
            require(e['goal']==a[5],'end_goal_identity')
            require(e['task']==(a[3] in ('S','P')),'task_end_type')
            o=e['observation'];col,row=a[5]
            err=math.hypot(o['x']+row,o['y']+col)
            require(err<.03,'end_outside_endpoint_tolerance')
            # Intermediate half-cell MOVE nodes may acknowledge on the fly.
            # speed_cm_s is stale controller memory, not sensed actual speed.
            ended.add(key);ends.append({'robot':key[0],'node':key[1],'tick':e['tick'],'type':a[3],'endpoint_error_m':err})
        else:raise ValueError('unknown_event')
    return {'event_count':len(events),'observation_count':sum(len(v) for v in history.values()),'last_event_tick':last_tick,
            'views':views,'proposals':proposals,'admitted_nodes':len(commands),'acknowledged_nodes':len(ended),
            'pending_admitted_nodes':len(commands)-len(ended),'assigned_tasks':len(tasks),'task_services':sum(e['type'] in ('S','P') for e in ends),
            'task_prefix':[[tid,*value] for tid,value in sorted(tasks.items())],'ends':ends,
            'sampled_min_center_distance_m':min_sep,'sampled_settled_violations':sampled_gate_violations,
            'footprint_radius_m':None,'footprint_reason':'not extracted from installed ARGoS binary; center distances only',
            'actual_terminal_residence':{'robot0_observations':len(history.get('0',[])),'robot0_max_distance_from_initial_m':max(distance(history['0'][0],v) for v in history['0'])},
            'no_continuous_collision_or_error_envelope_claim':True}

def main():
    p=HERE/'attempts/nominal_attempt02/events.jsonl'
    events=[json.loads(s) for s in p.read_text().splitlines()]
    result=check(events)
    result.update(status='INCOMPLETE_NATIVE_CRASH_AFTER_FIRST_JOINT_STEP',full_200_tick_trial_passed=False,
                  final_group2_nominal_run='NOT_RUN_PERMISSION_WAIT_STOPPED',final_group2_pause_run='NOT_RUN_PERMISSION_WAIT_STOPPED',
                  pause_intervention_validated=False,task_service_validation='NOT_EXERCISED_NO_TASK_ENDS',
                  trace_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
                  audit_scope_limits=['admit decomposition is not yet matched against the complete proposal',
                                      'no S/P service nodes observed; task identity and dwell service checks remain unimplemented',
                                      'server online rejection of forged END is not established'])
    tests={}
    def negative(name,mutate):
        bad=copy.deepcopy(events);mutate(bad)
        try:check(bad)
        except (ValueError,KeyError,IndexError) as ex:tests[name]={'rejected':True,'reason':str(ex)}
        else:raise AssertionError('negative passed '+name)
    def first(es,kind):return next(e for e in es if e['kind']==kind)
    negative('nonadjacent_proposal',lambda es:first(es,'proposal')['proposal']['plan'][1][1].__setitem__(0,4))
    negative('wrong_view_hash',lambda es:first(es,'proposal')['proposal'].__setitem__('view_sha256','0'*64))
    negative('unknown_command_end',lambda es:first(es,'end').__setitem__('node',999))
    negative('forged_end_pose',lambda es:first(es,'end')['observation'].__setitem__('x',-99))
    negative('forged_task_end',lambda es:first(es,'end').__setitem__('task',True))
    negative('future_observation',lambda es:first(es,'observation')['observation'].__setitem__('tick',100))
    negative('duplicate_command_end',lambda es:[e for e in es if e['kind']=='end'][1].__setitem__('node',0))
    try:check(events,strict_settled=True)
    except ValueError as ex:tests['real_old_trace_fails_new_settled_gate']={'rejected':True,'reason':str(ex)}
    else:raise AssertionError('old trace incorrectly passed new gate')
    result['negative_checks']=tests
    (HERE/'audit.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
