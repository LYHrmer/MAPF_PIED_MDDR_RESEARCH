"""Read-only reconstruction of causal visibility and independent targets; true leakage negatives."""
from pathlib import Path
import argparse,copy,hashlib,json,math
HERE=Path(__file__).resolve().parent
FEATURE_KEYS={'action_type','node_ids','task_id','public_target_xy_m','public_episode_start_xy_m','public_episode_goal_xy_m','public_episode_length_m','wheel_left_cm_s','wheel_right_cm_s','queue_size','visible_head_tasks','delivered_END_count','last_delivered_ENDs','episode_first_nonzero_command_tick','episode_elapsed_ticks','observed_pause_ticks_so_far','intervention_applied_now','last_known_intervention_start_tick','completed_MOVE_episode_count','past_MOVE_ticks_per_median','historical_predicted_remaining_ticks'}
def require(ok,why):
    if not ok:raise ValueError(why)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def lines(p):return [json.loads(s) for s in p.read_text().splitlines()]
def verify(events,contexts,targets,residuals):
    require(len(contexts)==len(targets)==400,'dataset_tick_coverage')
    by_seq={e['sequence']:e for e in events};all_END={(e['robot'],e['node']):e for e in events if e['kind']=='end'}
    observations={(e['robot'],e['tick']):e['observation'] for e in events if e['kind']=='observation'}
    keys=[(r['agent'],r['tick'],r['freeze_sequence']) for r in contexts]
    require(len(set(keys))==400 and sorted((a,t) for a,t,s in keys)==[(a,t) for a in ['0','1'] for t in range(200)],'context_agent_tick_missing')
    target_keys=[(r['agent'],r['tick'],r['freeze_sequence']) for r in targets];require(keys==target_keys,'context_target_misaligned')
    for ctx,y in zip(contexts,targets):
        r=ctx['agent'];t=ctx['tick'];seq=ctx['freeze_sequence'];f=ctx['features']
        require(set(f)==FEATURE_KEYS,'private_or_unknown_online_feature')
        require(ctx['visibility']=='execution_monitor_delivered_after_current_wheel_command_not_current_GPIBT_input','wrong_context_visibility')
        e=by_seq[seq];require(e['kind']=='control' and e['control']['phase']=='wheel_command' and e['robot']==r and e['tick']==t,'context_not_real_current_command')
        c=e['control'];require(f['node_ids']==c['nodes'] and f['queue_size']==c['queue_size'] and f['task_id']==c['task_id'],'context_command_identity')
        require(f['action_type']=={0:'MOVE',1:'TURN',2:'STOP',3:'STATION'}[c['type']],'context_command_kind')
        require([f['wheel_left_cm_s'],f['wheel_right_cm_s']]==[c['issued_left_cm_s'],c['issued_right_cm_s']],'context_actual_wheel_parameters')
        require(f['intervention_applied_now']==c['paused'],'context_future_or_wrong_intervention')
        past=[q for q in events[:seq] if q['kind']=='end']
        require(f['delivered_END_count']==len(past),'history_count_not_prior_delivered_ENDs')
        h=f['last_delivered_ENDs'];require(len(h)==min(len(past),4),'history_tail_size')
        for hrow,end in zip(h,past[-4:]):
            require(hrow['agent']==end['robot'] and hrow['node']==end['node'] and hrow['task_id']==end['task_id'],'history_wrong_END_identity')
            require(hrow['delivered_sequence']==end['sequence']<seq and hrow['delivered_tick']==end['tick']<=t,'current_future_or_undelivered_END')
        views=[q for q in events[:seq] if q['kind']=='view']
        require(f['visible_head_tasks']==(views[-1]['view']['mapf_instance']['goals'] if views else []),'future_or_unrevealed_task')
        prior_pause=[q for q in events[:seq] if q['kind']=='control' and q['control']['phase']=='pause']
        require(f['last_known_intervention_start_tick']==(prior_pause[0]['tick'] if prior_pause else None),'future_trigger_or_pause_time_leaked')
        start=f['episode_first_nonzero_command_tick'];require(start is None or start<=t,'future_command_start')
        require(y['target_visibility']=='offline_only_not_strategy_input','wrong_target_visibility')
        o=observations[(r,t)];require(y['actual_sample_xy_m']==[o['x'],o['y']] and y['actual_sample_angle_deg']==o['angle'],'target_not_actual_delivered_pose')
        following=observations.get((r,t+1));next_dist=math.hypot(following['x']-o['x'],following['y']-o['y']) if following else None
        require(y['next_observed_displacement_m']==next_dist,'target_next_pose')
        if f['public_episode_length_m'] is not None:
            a=f['public_episode_start_xy_m'];b=f['public_episode_goal_xy_m'];length=math.hypot(b[0]-a[0],b[1]-a[1]);require(abs(length-f['public_episode_length_m'])<1e-12,'public_intent_span')
            u=[(b[0]-a[0])/length,(b[1]-a[1])/length];v=[o['x']-a[0],o['y']-a[1]]
            require(abs(y['signed_progress_m']-(v[0]*u[0]+v[1]*u[1]))<1e-10,'false_offline_progress')
            require(abs(y['signed_lateral_m']-(u[0]*v[1]-u[1]*v[0]))<1e-10,'false_offline_lateral')
            require(abs(y['signed_progress_fraction']-y['signed_progress_m']/length)<1e-10,'false_progress_fraction')
        else:require(y['signed_progress_m'] is None and y['signed_lateral_m'] is None,'invented_progress_without_intent')
        require([p['node'] for p in y['future_node_ACKs']]==c['nodes'],'target_ACK_node_identity')
        for a in y['future_node_ACKs']:
            end=all_END.get((r,a['node']));require(a['future_ack_tick']==(end['tick'] if end else None) and a['right_censored_at_horizon']==(end is None),'false_future_ACK_target')
            if end:require(end['sequence']>seq,'target_ACK_not_future')
        if y['future_episode_final_ACK_tick'] is not None:require(y['future_episode_remaining_ticks']==y['future_episode_final_ACK_tick']-t,'false_remaining_ticks')
        else:require(y['future_episode_remaining_ticks'] is None,'invented_censored_remaining')
    indexed={(c['agent'],c['tick'],c['freeze_sequence']):(c,y) for c,y in zip(contexts,targets)}
    for row in residuals:
        c,y=indexed[(row['agent'],row['tick'],row['freeze_sequence'])];f=c['features'];pred=f['historical_predicted_remaining_ticks'];actual=y['future_episode_remaining_ticks']
        require(row['historical_predicted_remaining_ticks']==pred and row['offline_actual_remaining_ticks']==actual,'residual_input_mismatch')
        expected=actual-pred if actual is not None and pred is not None else None
        require(row['offline_residual_ticks']==expected,'false_offline_residual')
    return {'causal_context_rows_checked':400,'offline_target_rows_checked':400,'MOVE_residual_rows_checked':len(residuals),'features_actual_pose_or_future_labels':False,'all_historical_ENDs_strictly_prior_to_freeze':True}
def run():
    manifest=json.loads((HERE/'dataset_manifest.json').read_text());summary={}
    for name,pins in manifest['trials'].items():
        d=HERE/'datasets'/name;raw=HERE/'attempts'/name/'events.jsonl';require(sha(raw)==pins['raw_sha256'],'raw_changed')
        for f,h in pins['files'].items():require(sha(d/f)==h,'dataset_changed')
        es=lines(raw);cs=lines(d/'delivered_context.jsonl');ys=lines(d/'offline_targets.jsonl');rs=lines(d/'feedback_residuals.jsonl')
        result=verify(es,cs,ys,rs);neg={}
        def bad(name,mutate):
            cc=copy.deepcopy(cs);yy=copy.deepcopy(ys);rr=copy.deepcopy(rs);mutate(cc,yy,rr)
            try:verify(es,cc,yy,rr)
            except (ValueError,KeyError,IndexError) as ex:neg[name]={'rejected':True,'reason':str(ex)}
            else:raise AssertionError('bad dataset accepted '+name)
        bad('actual_pose_in_features',lambda c,y,r:c[0]['features'].__setitem__('actual_x',0))
        bad('future_END_in_features',lambda c,y,r:next(x for x in c if x['features']['last_delivered_ENDs'])['features']['last_delivered_ENDs'][-1].__setitem__('delivered_sequence',999999))
        bad('future_intervention_start',lambda c,y,r:c[0]['features'].__setitem__('last_known_intervention_start_tick',199))
        bad('future_or_wrong_task_owner',lambda c,y,r:next(x for x in c if x['features']['visible_head_tasks'])['features']['visible_head_tasks'][0][0].__setitem__('agent_id',99))
        bad('wrong_motion_target_progress',lambda c,y,r:next(x for x in y if x['signed_progress_m'] is not None).__setitem__('signed_progress_m',99))
        bad('wrong_ACK_target',lambda c,y,r:next(x for x in y if x['future_node_ACKs'])['future_node_ACKs'][0].__setitem__('future_ack_tick',999))
        if any(x['offline_residual_ticks'] is not None for x in rs):bad('wrong_feedback_residual',lambda c,y,r:next(x for x in r if x['offline_residual_ticks'] is not None).__setitem__('offline_residual_ticks',999))
        result['negative_checks']=neg;result['audit_passed']=True;summary[name]=result
    return {'status':'PASSED_SEPARATE_VISIBILITY_AND_TARGET_AUDIT','trials':summary,'raw_not_rerun':True,'current_planner_used_dataset':False,'dataset_manifest_sha256':sha(HERE/'dataset_manifest.json'),'auditor_sha256':sha(HERE/'dataset_audit.py')}
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',default='dataset_audit.json');a=p.parse_args();r=run()
    with (HERE/a.output).open('x') as f:json.dump(r,f,indent=2);f.write('\n')
    print(json.dumps(r,indent=2))
