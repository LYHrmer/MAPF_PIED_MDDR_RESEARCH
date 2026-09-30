"""Independent causal replay of all official actions, native ADG nodes and service dwell."""
from pathlib import Path
import copy, hashlib, json, math

HERE=Path(__file__).resolve().parent
def require(ok,why):
    if not ok:raise ValueError(why)
def distance(a,b):return math.hypot(a['x']-b['x'],a['y']-b['y'])
def endpoint_error(o,cr):return math.hypot(o['x']+cr[1],o['y']+cr[0])
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def parser_contract(path,initial_orientation):
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

def check(events,decisions,pause_expected=False):
    layout=json.loads((HERE/'map.json').read_text())['layout']
    observed={};history={};commands={};ended=set();tasks={};completed_tasks={}
    waiting={str(a):[] for a in range(2)};decrements={};front={};bookkept=set()
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
            if len(observed)==2 and len({v['tick'] for v in observed.values()})==1:
                a,b=observed.values();min_sep=min(min_sep,distance(a,b))
        elif kind in ('invoke','view'):
            s=e['snapshot'];require(s['tick']==e['tick'],'snapshot_time')
            require(s['observations']==observed and len(observed)==2,'snapshot_not_latest_delivered')
            require(s['joint_settled'] and s['unfinished']==[0,0],'unfinished_at_view')
            require(all(k in ended for k in commands) and not any(waiting.values()),'unacked_or_unadmitted_at_view')
            for r,o in observed.items():
                require(0<=e['tick']-o['tick']<=1,'future_or_stale_observation')
                require(o['queue_size']==0 and o['idle'] and o['previous_zero_command'],'nonidle_at_view')
                require(o['displacement_m']<=1e-6,'sampled_settled_gate')
            if kind=='view':
                latest_view=e['view'];views+=1;inst=latest_view['mapf_instance']
                require(len(inst['starts'])==2 and len(inst['goals'])==2,'team_size')
                for a,(st,gs) in enumerate(zip(inst['starts'],inst['goals'])):
                    require(len(gs)==1 and gs[0]['agent_id']==a,'visible_task_owner')
                    g=gs[0];tid=g['id'];value=(a,g['location'])
                    require(tid not in tasks or tasks[tid]==value,'task_identity_changed')
                    if tid not in tasks:task_prefix.append([tid,a,g['location']])
                    tasks[tid]=value
                    require(endpoint_error(observed[str(a)],[st['location']%5,st['location']//5])<.03,'start_pose_mismatch')
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
            require(d['result']['step']==proposals and len(d['result']['actions'])==2,'official_step_identity')
            paths=proposal['plan'];require(len(paths)==2,'proposal_team')
            for a,path in enumerate(paths):
                require(len(path)==2 and [v[2] for v in path]==[0,1],'single_joint_step')
                s=latest_view['mapf_instance']['starts'][a]['location'];action=d['result']['actions'][a]
                require(action in range(5),'invalid_official_action');t=s+[1,5,-1,-5,0][action]
                require(path[0][:2]==[s//5,s%5] and path[1][:2]==[t//5,t%5],'official_action_mapping')
                require(abs(path[0][0]-path[1][0])+abs(path[0][1]-path[1][1])<=1,'nonadjacent_action')
                for row,col,_,_task in path:require(0<=row<5 and 0<=col<5 and layout[row][col]!='@','invalid_cell')
                g=latest_view['mapf_instance']['goals'][a][0];task=g['id'] if t==g['location'] else -1
                require([path[0][3],path[1][3]]==([task,-1] if t==s else [-1,task]),'task_annotation')
            require(paths[0][1][:2]!=paths[1][1][:2],'vertex_collision')
            require(not(paths[0][0][:2]==paths[1][1][:2] and paths[1][0][:2]==paths[0][1][:2]),'edge_swap')
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
                require(actual==expected,'admit_not_native_proposal_decomposition');commands[key]=a
        elif kind=='control':
            r=e['robot'];c=e['control'];require(r in observed,'control_without_observation')
            require(observed[r]['tick']==e['tick'],'control_pose_time')
            if c['phase']=='pause':
                require(c['paused'] and r=='0' and 30<=e['tick']<=49,'invalid_pause_interval')
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
            err=endpoint_error(observed[key[0]],a[5]);require(err<.03,'end_outside_tolerance')
            require(key in front and front[key][0]==e['tick'],'end_without_current_control')
            if a[3]=='T':
                target={0:0,1:270,2:180,3:90}[a[2]]
                delta=(observed[key[0]]['angle']-target+180)%360-180
                require(abs(delta)<.5,'turn_end_angle')
            if a[3]=='S':
                tid=a[6];require(tid in tasks and tasks[tid]==(int(key[0]),int(a[5][1])*5+int(a[5][0])),'service_wrong_owner_or_location')
                ds=decrements.get(key,[])
                require([v[1] for v in ds]==list(range(20,0,-1)),'service_dwell_timer_sequence')
                require(len({v[0] for v in ds})==20 and e['tick']-ds[0][0]>=20,'service_dwell20ticks')
                require(front[key][1]['timer']==0 and tid not in completed_tasks,'service_end_timer_or_duplicate_task')
                residence=[o for o in history[key[0]] if ds[0][0]<=o['tick']<=e['tick']]
                require(len(residence)==e['tick']-ds[0][0]+1 and all(endpoint_error(o,a[5])<.03 for o in residence),'service_residence_all_ticks')
                completed_tasks[tid]={'robot':key[0],'node':key[1],'tick':e['tick'],'start_tick':ds[0][0],'timer_decrements':20,'residence_samples_inclusive':len(residence),'max_endpoint_error_m':max(endpoint_error(o,a[5]) for o in residence)}
            ended.add(key);ends.append({'robot':key[0],'node':key[1],'tick':e['tick'],'type':a[3],'task_id':a[6],'endpoint_error_m':err})
        elif kind=='horizon':
            require(e['tick']==200 and horizon is None,'invalid_horizon');horizon=e
            require(e['snapshot']['observations']==observed,'horizon_pose_causality')
            pending=[sum(k[0]==str(a) and k not in ended for k in commands)+len(waiting[str(a)]) for a in range(2)]
            require(e['snapshot']['unfinished']==pending,'horizon_unfinished_identity')
        else:raise ValueError('unknown_event_'+kind)
    require(proposals==len(decisions),'orphan_official_decision')
    require([p['tick'] for p in pauses]==(list(range(30,50)) if pause_expected else []),'fixed_pause_coverage')
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

def main():
    audits={}
    for path in sorted((HERE/'attempts').glob('*')):
        if not (path/'events.jsonl').exists():continue
        events=[json.loads(s) for s in (path/'events.jsonl').read_text().splitlines()]
        decisions=[json.loads(s) for s in (path/'decisions.jsonl').read_text().splitlines()] if (path/'decisions.jsonl').exists() else []
        receipt=json.loads((path/'receipt.json').read_text())
        try:result=check(events,decisions,path.name.startswith('pause'));result['audit_passed']=True
        except (ValueError,KeyError,IndexError) as error:result={'audit_passed':False,'audit_error':str(error)}
        if result['audit_passed']:
            tests={}
            def negative(name,mutate):
                bad=copy.deepcopy(events);mutate(bad)
                try:check(bad,decisions,path.name.startswith('pause'))
                except (ValueError,KeyError,IndexError) as error:tests[name]={'rejected':True,'reason':str(error)}
                else:raise AssertionError('corruption passed '+name)
            def first(es,kind):return next(e for e in es if e['kind']==kind)
            def service_admit(es):return next(a for e in es if e['kind']=='admit' for a in e['actions'] if a[3]=='S')
            def service_end(es):return next(e for e in es if e['kind']=='end' and e['task'])
            def service_control(es):return next(e for e in es if e['kind']=='control' and e['control']['phase']=='service_decrement')
            negative('task_wire_omission',lambda es:service_admit(es).__setitem__(6,-1))
            negative('wrong_service_end_task_id',lambda es:service_end(es).__setitem__('task_id',0))
            negative('wrong_visible_task_owner',lambda es:first(es,'view')['view']['mapf_instance']['goals'][1][0].__setitem__('agent_id',0))
            negative('half_cell_wrong_endpoint',lambda es:first(es,'admit')['actions'][0][5].__setitem__(1,4))
            negative('wrong_native_decomposition',lambda es:first(es,'parsed')['actions'][1][0]['goal'].__setitem__(1,4))
            negative('wrong_view_hash',lambda es:first(es,'proposal')['proposal'].__setitem__('view_sha256','0'*64))
            negative('unknown_end',lambda es:first(es,'end').__setitem__('node',999))
            negative('future_end_pose',lambda es:first(es,'end')['observation'].__setitem__('x',99))
            negative('duplicate_end',lambda es:[e for e in es if e['kind']=='end'][1].__setitem__('node',0))
            negative('premature_task_bookkeeping',lambda es:first(es,'task_bookkeeping').__setitem__('new_finished_tasks',[1]))
            negative('wrong_service_timer',lambda es:service_control(es)['control'].__setitem__('timer',19))
            negative('missing_service_decrement',lambda es:service_control(es)['control'].__setitem__('phase','front'))
            negative('wrong_control_service_task_id',lambda es:service_control(es)['control'].__setitem__('task_id',-1))
            negative('fake_horizon_no_pending_nodes',lambda es:first(es,'horizon')['snapshot'].__setitem__('unfinished',[0,0]))
            negative('false_idle',lambda es:first(es,'observation')['observation'].__setitem__('previous_zero_command',False))
            if path.name.startswith('pause'):
                negative('forged_active_move_pause',lambda es:next(e for e in es if e['kind']=='control' and e['control']['paused'])['control'].__setitem__('nodes',[0]))
            result['negative_checks']=tests
        result.update(native_error=receipt['error'],trace_sha256=digest(path/'events.jsonl'),native_receipt_sha256=digest(path/'receipt.json'))
        result['full_fixed_trial_passed']=bool(result['audit_passed'] and result.get('horizon_tick')==200 and receipt['error'] is None)
        audits[path.name]=result
    for name,sha in json.loads((HERE/'previous_archive_manifest.json').read_text()).items():
        require(digest(HERE.parent/'gpibt_lsmart_integration_20260930'/name)==sha,'prior_archive_changed')
    # Final identities follow the declared wire correction, not best metrics.
    final=['nominal_retry01','pause_retry01']
    a=audits.get(final[0],{});b=audits.get(final[1],{})
    summary={'trials':audits,'prior_archive_preserved':True,'reported_fixed_trials':final,'selection_reason':'declared sole task_id wire correction; initial pair retained and rejected',
        'fixed_pair_passed':bool(a.get('full_fixed_trial_passed') and b.get('full_fixed_trial_passed')),
        'actual_task_prefix_equal':a.get('assigned_task_prefix')==b.get('assigned_task_prefix') if a and b and a.get('audit_passed') and b.get('audit_passed') else None,
        'pause_active_move_intervention_validated':b.get('pause_overlaps_active_move',False)}
    (HERE/'audit.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps({k:v for k,v in summary.items() if k!='trials'},indent=2))
    print(json.dumps({n:{k:v for k,v in a.items() if k in ('audit_passed','audit_error','full_fixed_trial_passed','proposals','task_services','horizon_tick','native_error')} for n,a in audits.items()},indent=2))
if __name__=='__main__':main()
