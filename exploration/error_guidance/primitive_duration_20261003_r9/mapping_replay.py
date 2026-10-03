"""Independent causal replay of all official actions, native ADG nodes and service dwell."""
from pathlib import Path
import copy, hashlib, json, math

HERE=Path(__file__).resolve().parent
def require(ok,why):
    if not ok:raise ValueError(why)
def distance(a,b):return math.hypot(a['x']-b['x'],a['y']-b['y'])
def endpoint_error(o,cr):return math.hypot(o['x']+cr[1],o['y']+cr[0])
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def parser_one(path,initial_orientation):
    """Independently derive the native turn/half-grid/service geometry for one step."""
    s,t=path;start=[s[1],s[0]];goal=[t[1],t[0]]
    orientation={1:0,0:1,3:2,2:3}[initial_orientation]
    result=[]
    def node(kind,p,q,ori,task=-1):
        result.append({'type':kind,'start':p,'goal':q,'orientation':ori,'task_id':task})
    if s[3]>=0:node('S',start,start,orientation,s[3])
    if start==goal:return result
    needed=(2 if t[0]>s[0] else 0) if t[0]!=s[0] else (1 if t[1]>s[1] else 3)
    if needed!=orientation:
        if abs(needed-orientation)==2:node('T',start,start,(orientation+1)%4)
        node('T',start,start,needed)
    middle=[(x+y)/2 for x,y in zip(start,goal)]
    node('M',start,middle,needed);node('M',middle,goal,needed)
    # Native S inherits the second MOVE start, but its physical service target
    # is the integer endpoint. Do not silently normalize that author geometry.
    if t[3]>=0:node('S',middle,goal,needed,t[3])
    return result

def parser_contract(path,initial_orientation):
    result=[];ori=initial_orientation
    for step,(s,t) in enumerate(zip(path,path[1:])):
        begin=list(s)
        if step:begin[3]=-1
        nodes=parser_one([begin,t],ori)
        result.extend(dict(n,time=float(step)) for n in nodes)
        delta=(t[0]-s[0],t[1]-s[1])
        if delta!=(0,0):ori={(0,1):0,(1,0):3,(0,-1):2,(-1,0):1}[delta]
    return result

def check(events,decisions,pause_expected=False,strict_point_endpoints=True,layout=None,N=2,horizon_ticks=800):
    if layout is None:layout=json.loads((HERE/'map.json').read_text())['layout']
    rows,cols=len(layout),len(layout[0])
    observed={};history={};commands={};ended=set();tasks={};completed_tasks={}
    waiting={str(a):[] for a in range(N)};decrements={};front={};bookkept=set()
    latest_view=None;proposal=None;proposals=0;views=0;parsed_count=0;last_tick=-1
    min_sep=math.inf;ends=[];pauses=[];horizon=None;task_prefix=[]
    for seq,e in enumerate(events):
        require(e['sequence']==seq,'sequence')
        require(e['tick']>=last_tick,'time_order');last_tick=e['tick'];kind=e['kind']
        if kind=='observation':
            r=e['robot'];o=e['observation'];require(o['tick']==e['tick'],'observation_time')
            require(all(math.isfinite(o[f]) for f in ('x','y','angle','speed_cm_s','displacement_m')),'finite_pose')
            if r in observed:
                require(o['tick']==observed[r]['tick']+1,'missing_control_tick')
                require(abs(o['displacement_m']-distance(observed[r],o))<1e-8,'false_displacement')
            require(o['idle']==(o['queue_size']==0 and o['previous_zero_command'] and o['displacement_m']<=1e-6),'false_idle')
            observed[r]=o;history.setdefault(r,[]).append(o)
            if len(observed)==N and len({v['tick'] for v in observed.values()})==1:
                values=list(observed.values())
                for a in range(N):
                    for b in range(a):min_sep=min(min_sep,distance(values[a],values[b]))
        elif kind in ('invoke','view'):
            s=e['snapshot'];require(s['tick']==e['tick'],'snapshot_time')
            require(s['observations']==observed and len(observed)==N,'snapshot_not_latest_delivered')
            require(s['joint_settled'] and s['unfinished']==[0]*N,'unfinished_at_view')
            require(all(k in ended for k in commands) and not any(waiting.values()),'unacked_or_unadmitted_at_view')
            for r,o in observed.items():
                require(0<=e['tick']-o['tick']<=1,'future_or_stale_observation')
                require(o['queue_size']==0 and o['idle'] and o['previous_zero_command'],'nonidle_at_view')
                require(o['displacement_m']<=1e-6,'sampled_settled_gate')
            if kind=='view':
                latest_view=e['view'];views+=1;inst=latest_view['mapf_instance']
                require(len(inst['starts'])==N and len(inst['goals'])==N,'team_size')
                for a,(st,gs) in enumerate(zip(inst['starts'],inst['goals'])):
                    require(len(gs)==1 and gs[0]['agent_id']==a,'visible_task_owner')
                    g=gs[0];tid=g['id'];value=(a,g['location'])
                    require(tid not in tasks or tasks[tid]==value,'task_identity_changed')
                    if tid not in tasks:task_prefix.append([tid,a,g['location']])
                    tasks[tid]=value
                    require(endpoint_error(observed[str(a)],[st['location']%cols,st['location']//cols])<.03,'start_pose_mismatch')
        elif kind=='task_bookkeeping':
            for tid in e['new_finished_tasks']:
                require(tid in completed_tasks and tid not in bookkept,'bookkeeping_without_unique_real_service')
                require(completed_tasks[tid]['tick']<e['tick'],'premature_task_bookkeeping')
                bookkept.add(tid)
        elif kind=='proposal':
            require(latest_view is not None,'proposal_without_view');proposal=e['proposal']
            require(proposal['proposal_id']==proposals,'proposal_identity')
            require(proposal['view_sha256']==hashlib.sha256(json.dumps(latest_view,sort_keys=True).encode()).hexdigest(),'view_hash')
            require(proposals<len(decisions),'missing_official_decision');d=decisions[proposals]
            require(d['proposal']==proposal and d['view']==latest_view,'official_decision_binding')
            require(len(d['calls'])==2,'two_author_calls')
            paths=proposal['plan'];require(len(paths)==N,'proposal_team')
            for step,call in enumerate(d['calls']):
                require(call['result']['step']==2*proposals+step,'author_call_identity')
                require(call['request']['mapf_instance']['goals']==latest_view['mapf_instance']['goals'],'future_head_leak')
                for a,path in enumerate(paths):
                    require(len(path)==3 and [v[2] for v in path]==[0,1,2],'two_joint_steps')
                    st=call['request']['mapf_instance']['starts'][a];s0=path[step][0]*cols+path[step][1]
                    require(st['location']==s0,'frontier_binding')
                    action=call['result']['actions'][a];require(action in range(5),'author_action')
                    t=s0+[1,cols,-1,-cols,0][action]
                    require(path[step+1][:2]==[t//cols,t%cols],'author_action_mapping')
                    for row,col,_,_ in path:require(0<=row<rows and 0<=col<cols and layout[row][col]!='@','invalid_cell')
                    g=latest_view['mapf_instance']['goals'][a][0]
                    labels=[-1]*3
                    for j,point in enumerate(path):
                        if point[0]*cols+point[1]==g['location']:labels[j]=g['id'];break
                    require([v[3] for v in path]==labels,'exactly_once_current_task_annotation')
                require(len({tuple(p[step+1][:2]) for p in paths})==N,'vertex_collision')
                for a in range(N):
                    for b in range(a):require(not(paths[a][step][:2]==paths[b][step+1][:2] and paths[b][step][:2]==paths[a][step+1][:2]),'edge_swap')
            proposals+=1
        elif kind=='parsed':
            require(proposal is not None and e['proposal_id']==proposal['proposal_id'],'parsed_proposal_identity')
            expected=[parser_contract(path,latest_view['mapf_instance']['starts'][a]['orientation']) for a,path in enumerate(proposal['plan'])]
            require(e['actions']==expected,'complete_parser_decomposition')
            for a,nodes in enumerate(expected):waiting[str(a)].extend(nodes);parsed_count+=len(nodes)
        elif kind=='admit':
            r=e['robot'];require(e['agent']==int(r),'admit_agent')
            for a in e['actions']:
                require(len(a)==7 and a[0]==r,'admit_identity');key=(r,a[1])
                require(key not in commands and waiting[r],'duplicate_or_unmapped_admit')
                expected=waiting[r].pop(0)
                actual={'type':a[3],'start':a[4],'goal':a[5],'orientation':a[2],'task_id':a[6]}
                require(actual=={k:v for k,v in expected.items() if k!='time'},'admit_not_native_proposal_decomposition');commands[key]=a
        elif kind=='control':
            r=e['robot'];c=e['control'];require(r in observed,'control_without_observation')
            require(observed[r]['tick']==e['tick'],'control_pose_time')
            if c['phase']=='pause':
                require(c['paused'] and r=='0' and c['trigger_tick']<=e['tick']<c['trigger_tick']+20,'invalid_pause_interval')
                require(c['queue_size']==observed[r]['queue_size'],'pause_queue_causality')
                if c['queue_size']==0:require(c['nodes']==[] and c['type']==2,'forged_active_pause')
                else:require(c['nodes'] and (r,c['nodes'][0]) in commands and (r,c['nodes'][0]) not in ended,'pause_unknown_or_finished_node')
                pauses.append({'tick':e['tick'],'type':c['type'],'nodes':c['nodes'],'queue_size':c['queue_size']})
            else:
                require(not c['paused'] and c['nodes'],'control_node_identity')
                key=(r,c['nodes'][0]);require(key in commands and key not in ended,'control_unknown_or_finished_node')
                a=commands[key];require(c['type']=={'M':0,'T':1,'S':3}[a[3]],'control_type_mismatch')
                require(c['task_id']==a[6],'control_task_identity')
                # Consecutive half-MOVEs are natively merged; target may be
                # the final queued half-node, while front identity is first.
                target=commands[(r,c['nodes'][-1])][5]
                require(abs(c['target_x']+target[1])<1e-8 and abs(c['target_y']+target[0])<1e-8,'control_target_mismatch')
                front[key]=(e['tick'],c)
                if c['phase']=='service_decrement':
                    require(a[3]=='S' and c['timer']>0,'nonservice_decrement')
                    require(endpoint_error(observed[r],a[5])<.03,'service_residence_outside_tolerance')
                    decrements.setdefault(key,[]).append((e['tick'],c['timer'],copy.deepcopy(observed[r])))
                else:require(c['phase']=='front','unknown_control_phase')
        elif kind=='end':
            key=(e['robot'],e['node']);require(key in commands,'unknown_end')
            require(key not in ended,'duplicate_end');a=commands[key]
            require(e['observation']==observed[key[0]],'forged_or_future_end_observation')
            require(e['accepted'] and e['goal']==a[5],'end_goal_or_acceptance')
            require(e['task']==(a[3] in ('S','P')) and e['task_id']==a[6],'end_task_identity')
            err=endpoint_error(observed[key[0]],a[5])
            if err>=.03:
                c=front.get(key,(None,{}))[1]
                # The unchanged author's merged-half on-the-fly predicate is
                # radial to the final merged target; it is not point distance
                # to the intermediate half-node. Strict metric stays separate.
                radial=math.hypot(observed[key[0]]['x']-c.get('target_x',math.inf),observed[key[0]]['y']-c.get('target_y',math.inf))-.5*(len(c.get('nodes',[]))-1)
                native_half=bool(a[3]=='M' and len(c.get('nodes',[]))>1 and c['nodes'][0]==key[1] and radial<.03)
                require(not strict_point_endpoints and native_half,'end_outside_tolerance')
            require(key in front and front[key][0]==e['tick'],'end_without_current_control')
            if a[3]=='T':
                target={0:0,1:270,2:180,3:90}[a[2]]
                delta=(observed[key[0]]['angle']-target+180)%360-180
                require(abs(delta)<.5,'turn_end_angle')
            if a[3]=='S':
                tid=a[6];require(tid in tasks and tasks[tid]==(int(key[0]),int(a[5][1])*cols+int(a[5][0])),'service_wrong_owner_or_location')
                ds=decrements.get(key,[])
                require([v[1] for v in ds]==list(range(20,0,-1)),'service_dwell_timer_sequence')
                require(len({v[0] for v in ds})==20 and e['tick']-ds[0][0]>=20,'service_dwell20ticks')
                require(front[key][1]['timer']==0 and tid not in completed_tasks,'service_end_timer_or_duplicate_task')
                residence=[o for o in history[key[0]] if ds[0][0]<=o['tick']<=e['tick']]
                require(len(residence)==e['tick']-ds[0][0]+1 and all(endpoint_error(o,a[5])<.03 for o in residence),'service_residence_all_ticks')
                completed_tasks[tid]={'robot':key[0],'node':key[1],'tick':e['tick'],'start_tick':ds[0][0],'timer_decrements':20,'residence_samples_inclusive':len(residence),'max_endpoint_error_m':max(endpoint_error(o,a[5]) for o in residence)}
            ended.add(key);ends.append({'robot':key[0],'node':key[1],'tick':e['tick'],'type':a[3],'task_id':a[6],'endpoint_error_m':err})
        elif kind=='horizon':
            require(e['tick']==horizon_ticks and horizon is None,'invalid_horizon');horizon=e
            require(e['snapshot']['observations']==observed,'horizon_pose_causality')
            pending=[sum(k[0]==str(a) and k not in ended for k in commands)+len(waiting[str(a)]) for a in range(N)]
            require(e['snapshot']['unfinished']==pending,'horizon_unfinished_identity')
        else:raise ValueError('unknown_event_'+kind)
    require(proposals==len(decisions),'orphan_official_decision')
    require((len(pauses)==20 and [p['tick'] for p in pauses]==list(range(pauses[0]['tick'],pauses[0]['tick']+20))) if pause_expected else not pauses,'active_pause_coverage')
    return {'event_count':len(events),'last_event_tick':last_tick,'horizon_tick':horizon['tick'] if horizon else None,
        'observation_count':sum(map(len,history.values())),'views':views,'proposals':proposals,
        'parsed_nodes':parsed_count,'admitted_nodes':len(commands),'acknowledged_nodes':len(ended),
        'pending_admitted_nodes':[list(k) for k in commands if k not in ended],
        'pending_admitted_commands':[a for k,a in commands.items() if k not in ended],
        'pending_unadmitted_nodes':waiting,'assigned_task_prefix':task_prefix,
        'task_services':len(completed_tasks),'completed_tasks':completed_tasks,'bookkept_tasks':sorted(bookkept),
        'ends':ends,'sampled_min_center_distance_m':None if math.isinf(min_sep) else min_sep,
        'pause_controls':pauses,'pause_overlaps_active_move':any(p['type']==0 and p['nodes'] for p in pauses),
        'terminal_observations':observed,'unfinished_tasks':[[tid,*tasks[tid]] for tid in tasks if tid not in completed_tasks],
        'horizon_unfinished_nodes':horizon['snapshot']['unfinished'] if horizon else None,
        'latest_terminal_pose_tick':min(o['tick'] for o in observed.values()) if observed else None,
        'sampled_center_metric_only':True,'continuous_footprint_safety_established':False,
        'server_online_forged_END_rejection_established':False}
