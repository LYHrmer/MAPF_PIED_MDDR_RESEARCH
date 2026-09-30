"""Independent saved-event causality: actual commands, earliest MOVE intervention, full mapping/services."""
from pathlib import Path
import argparse,copy,hashlib,importlib.util,json,math
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('parent_mapping',HERE/'parent_mapping_audit.py')
parent=importlib.util.module_from_spec(spec);spec.loader.exec_module(parent)
require=parent.require
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
EXTRA={'active_trigger','active_resume','wheel_command','pause'}
def active_check(events,decisions,pause):
    # Parent's independent action/parser/ADG/service audit is reused verbatim.
    # New intervention/command events are checked separately, not accepted by
    # relaxing any original mapping, task or service invariant.
    clean=[copy.deepcopy(e) for e in events if not(e['kind']=='control' and e['control']['phase'] in EXTRA)]
    for i,e in enumerate(clean):e['sequence']=i
    base=parent.check(clean,decisions,False)
    commands={};ended={};obs={};wheel={};wheel_history={};trigger=None;resume=None
    eligible=[];pauses=[];admit_during=[];end_during=[];first_move_command={}
    def zero(c):return c['issued_left_cm_s']==0 and c['issued_right_cm_s']==0
    def known(r,c):
        if c['type'] in (0,1,3):
            require(c['nodes'] and c['queue_size']>0,'active_control_empty_queue')
            for node in c['nodes']:
                key=(r,node);require(key in commands and key not in ended,'control_unadmitted_or_already_ACK')
                require(commands[key][3]=={0:'M',1:'T',3:'S'}[c['type']],'actual_command_action_type')
            target=commands[(r,c['nodes'][-1])][5]
            require(abs(c['target_x']+target[1])<1e-8 and abs(c['target_y']+target[0])<1e-8,'actual_command_endpoint_identity')
            require(c['task_id']==commands[(r,c['nodes'][0])][6],'actual_command_task_identity')
        else:require(c['type']==2 and c['nodes']==[] and c['queue_size']==0,'invalid_STOP_command_context')
    for i,e in enumerate(events):
        require(e['sequence']==i,'raw_sequence_not_contiguous')
        t=e['tick'];r=e.get('robot');kind=e['kind']
        inside=pause and trigger is not None and trigger['tick']<=t<trigger['tick']+20
        if kind=='admit':
            if inside and r=='0':admit_during.append(t)
            for a in e['actions']:commands[(r,a[1])]=a
        elif kind=='observation':
            o=e['observation'];obs[r]=o
            require(all(math.isfinite(o[k]) for k in ['previous_wheel_left_cm_s','previous_wheel_right_cm_s']),'nonfinite_actual_wheel_history')
            if r in wheel:
                require(wheel[r]['tick']==t-1,'missing_previous_actual_command')
                require(o['previous_wheel_left_cm_s']==wheel[r]['control']['issued_left_cm_s'] and o['previous_wheel_right_cm_s']==wheel[r]['control']['issued_right_cm_s'],'observation_not_previous_actual_command')
            else:require(t==0 and o['previous_wheel_left_cm_s']==o['previous_wheel_right_cm_s']==0,'false_initial_wheel_command')
            if r=='0' and r in wheel:
                c=wheel[r]['control']
                live=bool(c['nodes']) and all((r,n) in commands and (r,n) not in ended for n in c['nodes'])
                if c['type']==0 and live and o['queue_size']>0 and (o['previous_wheel_left_cm_s']!=0 or o['previous_wheel_right_cm_s']!=0) and o['displacement_m']>1e-6:
                    eligible.append(t)
        elif kind=='control':
            c=e['control'];phase=c['phase']
            require(r in obs and obs[r]['tick']==t,'control_without_current_delivered_pose')
            require(c['controller_tick']==t and c['displacement_m']==obs[r]['displacement_m'],'control_tick_or_displacement_mismatch')
            require(c['mode']==('pause' if pause else 'nominal'),'wrong_fixed_arm')
            require(all(math.isfinite(c[k]) for k in ['issued_left_cm_s','issued_right_cm_s']),'nonfinite_issued_command')
            if r=='0' and trigger is not None:require(c['trigger_tick']==trigger['tick'],'trigger_identity_changed')
            if phase=='active_trigger':
                require(r=='0' and trigger is None and eligible and t==eligible[0],'not_unique_earliest_eligible_trigger')
                require(c['type']==0 and not c['paused'] and c['trigger_tick']==t,'trigger_not_native_active_MOVE')
                known(r,c)
                require(c['nodes']==wheel[r]['control']['nodes'],'trigger_changed_front_nodes')
                require(c['issued_left_cm_s']==obs[r]['previous_wheel_left_cm_s'] and c['issued_right_cm_s']==obs[r]['previous_wheel_right_cm_s'] and not zero(c),'trigger_not_actual_prior_nonzero_wheels')
                require(obs[r]['displacement_m']>1e-6,'trigger_without_actual_motion')
                trigger=copy.deepcopy(e)
            elif phase=='active_resume':
                require(pause and r=='0' and trigger is not None and resume is None and t==trigger['tick']+20,'incorrect_resume_interval')
                known(r,c)
                require(c['nodes']==trigger['control']['nodes'] and c['queue_size']==trigger['control']['queue_size'],'resume_lost_original_queue')
                require(not c['paused'] and zero(c),'resume_not_after_zero_wheels')
                resume=copy.deepcopy(e)
            elif phase=='pause':
                require(inside and r=='0' and c['paused'] and c['type']==0,'pause_not_active_interval_MOVE')
                known(r,c)
                require(zero(c),'pause_nonzero_actual_wheel_command')
                require(c['nodes']==trigger['control']['nodes'] and c['queue_size']==trigger['control']['queue_size'],'pause_queue_changed')
                for k in ['target_x','target_y','timer','task_id']:require(c[k]==trigger['control'][k],'pause_mutated_original_'+k)
                require(c['queue_size']==obs[r]['queue_size'],'pause_queue_causality')
                pauses.append(copy.deepcopy(e))
            elif phase=='wheel_command':
                known(r,c)
                require(r not in wheel or wheel[r]['tick']==t-1,'duplicate_or_missing_actual_wheel_tick')
                require(c['paused']==bool(inside and r=='0'),'wheel_pause_flag')
                if inside and r=='0':require(zero(c),'nonzero_actuator_during_pause')
                if c['type'] in (2,3):require(zero(c),'nonzero_STOP_or_STATION_wheels')
                wheel[r]=copy.deepcopy(e);wheel_history.setdefault(r,[]).append(copy.deepcopy(e))
                if c['type']==0 and not zero(c):
                    for n in c['nodes']:first_move_command.setdefault((r,n),t)
            else:
                require(phase in ['front','service_decrement'],'unknown_control_phase')
                require(not (inside and r=='0'),'native_control_or_timer_ran_during_pause')
        elif kind=='end':
            if inside and r=='0':end_during.append(t)
            ended[(r,e['node'])]=copy.deepcopy(e)
    require(all(len(v)==200 and [e['tick'] for e in v]==list(range(200)) for v in wheel_history.values()) and len(wheel_history)==2,'full_actual_wheel_command_coverage')
    require((trigger is None)==(not eligible),'missing_eligible_trigger')
    require(not admit_during and not end_during,'dispatch_or_ACK_during_active_pause')
    if pause and trigger:
        require([e['tick'] for e in pauses]==list(range(trigger['tick'],min(trigger['tick']+20,200))),'fixed20tick_pause_coverage')
        if trigger['tick']+20<200:require(resume is not None,'missing_native_resume')
    else:require(not pauses and resume is None,'unexpected_pause_or_resume')
    acked=[];resume_motion=False
    if trigger:
        for n in trigger['control']['nodes']:
            e=ended.get(('0',n))
            acked.append({'node':n,'normal_ack_tick':e['tick'] if e else None,'censored_at_horizon':e is None})
            if e and pause:require(e['tick']>=trigger['tick']+20,'trigger_node_ACK_before_resume')
        if resume:
            resume_motion=any(e['tick']>resume['tick'] and e['robot']=='0' and e['kind']=='observation' and e['observation']['displacement_m']>1e-6 for e in events if e.get('robot')=='0')
    all_ack=bool(acked) and all(a['normal_ack_tick'] is not None for a in acked)
    base.update(active_rule_recomputed_independently=True,first_eligible_tick=eligible[0] if eligible else None,
        active_trigger=trigger,active_resume=resume,actual_pause_ticks=[e['tick'] for e in pauses],
        actual_wheel_command_count=sum(map(len,wheel_history.values())),trigger_nodes_normal_ack=acked,
        pause_overlaps_active_move=bool(pause and trigger and pauses),resume_actual_motion_observed=resume_motion,
        active_move_intervention_fully_validated=bool(pause and trigger and len(pauses)==20 and resume_motion and all_ack),
        actual_stop_max_post_trigger_displacement_m=max([obs_e['observation']['displacement_m'] for obs_e in events if obs_e['kind']=='observation' and obs_e['robot']=='0' and trigger and trigger['tick']<obs_e['tick']<trigger['tick']+20] or [0]),
        trigger_unACK_target_retained=True if trigger else None)
    return base
def read_trial(p):
    es=[json.loads(s) for s in (p/'events.jsonl').read_text().splitlines()]
    ds=[json.loads(s) for s in (p/'decisions.jsonl').read_text().splitlines()] if (p/'decisions.jsonl').exists() else []
    return es,ds,json.loads((p/'receipt.json').read_text())
def run():
    trials={}
    for p in sorted((HERE/'attempts').glob('*')):
        if not (p/'events.jsonl').exists():continue
        es,ds,receipt=read_trial(p);pause=p.name.startswith('pause')
        try:r=active_check(es,ds,pause);r['audit_passed']=True
        except (ValueError,KeyError,IndexError) as ex:r={'audit_passed':False,'audit_error':str(ex)}
        if r['audit_passed']:
            negatives={}
            def mutate_test(name,change):
                bad=copy.deepcopy(es);change(bad)
                try:active_check(bad,ds,pause)
                except (ValueError,KeyError,IndexError) as ex:negatives[name]={'rejected':True,'reason':str(ex)}
                else:raise AssertionError('negative accepted '+name)
            def one(xs,kind,phase=None):return next(e for e in xs if e['kind']==kind and (phase is None or e['control']['phase']==phase))
            mutate_test('wrong_task_wire',lambda xs:next(a for e in xs if e['kind']=='admit' for a in e['actions'] if a[3]=='S').__setitem__(6,-1))
            mutate_test('wrong_task_owner',lambda xs:one(xs,'view')['view']['mapf_instance']['goals'][1][0].__setitem__('agent_id',0))
            mutate_test('wrong_task_END',lambda xs:next(e for e in xs if e['kind']=='end' and e['task']).__setitem__('task_id',0))
            mutate_test('wrong_station_timer',lambda xs:one(xs,'control','service_decrement')['control'].__setitem__('timer',19))
            mutate_test('fake_terminal_empty',lambda xs:one(xs,'horizon')['snapshot'].__setitem__('unfinished',[0,0]))
            mutate_test('false_previous_actual_wheels',lambda xs:next(e for e in xs if e['kind']=='observation' and e['robot']=='0' and e['tick']==1)['observation'].__setitem__('previous_wheel_left_cm_s',100))
            if r['active_trigger']:
                mutate_test('trigger_without_nonzero_wheels',lambda xs:one(xs,'control','active_trigger')['control'].update(issued_left_cm_s=0,issued_right_cm_s=0))
                mutate_test('trigger_without_real_displacement',lambda xs:one(xs,'control','active_trigger')['control'].__setitem__('displacement_m',0))
                mutate_test('trigger_unknown_or_ACK_node',lambda xs:one(xs,'control','active_trigger')['control'].__setitem__('nodes',[9999]))
                mutate_test('wrong_trigger_tick',lambda xs:one(xs,'control','active_trigger')['control'].__setitem__('trigger_tick',199))
            if pause and r['actual_pause_ticks']:
                mutate_test('nonzero_wheels_during_pause',lambda xs:one(xs,'control','pause')['control'].__setitem__('issued_left_cm_s',1))
                mutate_test('lost_pause_endpoint',lambda xs:one(xs,'control','pause')['control'].__setitem__('target_x',0))
                mutate_test('pause_queue_removed',lambda xs:one(xs,'control','pause')['control'].__setitem__('queue_size',0))
                mutate_test('early_resume',lambda xs:one(xs,'control','active_resume')['control'].__setitem__('controller_tick',one(xs,'control','active_trigger')['tick']))
            r['negative_checks']=negatives
        r.update(native_error=receipt['error'],trace_sha256=sha(p/'events.jsonl'),native_receipt_sha256=sha(p/'receipt.json'))
        r['full_fixed_trial_passed']=bool(r['audit_passed'] and r.get('horizon_tick')==200 and receipt['error'] is None)
        for filename,h in receipt['files'].items():require(sha(p/filename)==h,'native_raw_file_changed')
        require(receipt['binary_identities']==json.loads((HERE/'binary_manifest.json').read_text()),'native_binary_identity_mismatch')
        trials[p.name]=r
    for filename,h in json.loads((HERE/'previous_archive_manifest.json').read_text()).items():require(sha(HERE.parent/'gpibt_lsmart_integration_20260930_r2'/filename)==h,'frozen_parent_changed')
    final=['nominal','pause'];a=trials.get(final[0],{});b=trials.get(final[1],{})
    return {'trials':trials,'reported_fixed_trials':final,'selection_reason':'first fixed event-triggered nominal/pause pair; no tuning',
        'fixed_pair_passed':bool(a.get('full_fixed_trial_passed') and b.get('full_fixed_trial_passed')),
        'actual_task_prefix_equal':a.get('assigned_task_prefix')==b.get('assigned_task_prefix') if a.get('audit_passed') and b.get('audit_passed') else None,
        'active_move_intervention_fully_validated':b.get('active_move_intervention_fully_validated',False),
        'frozen_direct_parent_preserved':True,'learned_policy_evaluated':False,'continuous_footprint_safety_proved':False}
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--output',default='audit.json');args=parser.parse_args()
    result=run()
    with (HERE/args.output).open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({k:v for k,v in result.items() if k!='trials'},indent=2))
    print(json.dumps({n:{k:v for k,v in t.items() if k in ['audit_passed','audit_error','first_eligible_tick','task_services','horizon_tick','native_error','actual_pause_ticks','active_move_intervention_fully_validated']} for n,t in result['trials'].items()},indent=2))
