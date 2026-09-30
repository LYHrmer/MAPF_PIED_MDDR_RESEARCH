"""Causal delivered-context export and entirely separate offline supervision, never used by planner."""
from pathlib import Path
import argparse,csv,hashlib,json,math,statistics
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
FEATURE_KEYS={'action_type','node_ids','task_id','public_target_xy_m','public_episode_start_xy_m','public_episode_goal_xy_m','public_episode_length_m','wheel_left_cm_s','wheel_right_cm_s','queue_size','visible_head_tasks','delivered_END_count','last_delivered_ENDs','episode_first_nonzero_command_tick','episode_elapsed_ticks','observed_pause_ticks_so_far','intervention_applied_now','last_known_intervention_start_tick','completed_MOVE_episode_count','past_MOVE_ticks_per_median','historical_predicted_remaining_ticks'}
END_KEYS={'agent','node','kind','task_id','delivered_tick','delivered_sequence','first_command_tick','duration_ticks'}
def check_context(row):
    f=row['features'];assert set(f)==FEATURE_KEYS, 'unexpected/private context field'
    assert row['visibility']=='execution_monitor_delivered_after_current_wheel_command_not_current_GPIBT_input'
    for e in f['last_delivered_ENDs']:
        assert set(e)==END_KEYS,'private END history field'
        assert e['delivered_sequence']<row['freeze_sequence'] and e['delivered_tick']<=row['tick'],'future or undelivered END context'
    start=f['last_known_intervention_start_tick'];assert start is None or start<=row['tick'],'future trigger leaked'
    for k in ['episode_first_nonzero_command_tick']:
        assert f[k] is None or f[k]<=row['tick'],'future motion start leaked'
def data(events,trial):
    # Future lookup is used only below for targets. It never enters features.
    future_ends={(e['robot'],e['node']):e for e in events if e['kind']=='end'}
    all_observations={(e['robot'],e['tick']):e['observation'] for e in events if e['kind']=='observation'}
    trigger_ticks=[e['tick'] for e in events if e['kind']=='control' and e['control']['phase']=='active_trigger']
    offline_trigger=trigger_ticks[0] if trigger_ticks else None
    commands={};admit_ticks={};first_commands={};past_ends=[];goals=[];observed={}
    episodes={};node_episode={};completed_rates=[];completed_episode_ids=set();applied_start=None
    contexts=[];targets=[];residuals=[];motion=[]
    for e in events:
        kind=e['kind'];r=e.get('robot');t=e['tick'];seq=e['sequence']
        if kind=='view':goals=e['view']['mapf_instance']['goals']
        elif kind=='admit':
            for a in e['actions']:commands[(r,a[1])]=a;admit_ticks[(r,a[1])]=t
        elif kind=='observation':observed[r]=e['observation']
        elif kind=='end':
            key=(r,e['node']);a=commands[key];first=first_commands.get(key)
            past_ends.append({'agent':r,'node':e['node'],'kind':a[3],'task_id':a[6],'delivered_tick':t,'delivered_sequence':seq,'first_command_tick':first,'duration_ticks':t-first if first is not None else None})
            episode=node_episode.get(key)
            if episode is not None:
                ep=episodes[episode]
                if e['node']==ep['final_node']:
                    assert episode not in completed_episode_ids
                    completed_rates.append((t-ep['first_tick'])/ep['length_m']);completed_episode_ids.add(episode)
        elif kind=='control' and e['control']['phase']=='pause':
            if applied_start is None:applied_start=t
        elif kind=='control' and e['control']['phase']=='wheel_command':
            c=e['control'];nonzero=c['issued_left_cm_s']!=0 or c['issued_right_cm_s']!=0
            for n in c['nodes']:
                if c['type']==0 and nonzero:first_commands.setdefault((r,n),t)
            ep=None
            if c['type']==0 and c['nodes']:
                key=(r,c['nodes'][0]);episode=node_episode.get(key)
                if episode is None and nonzero:
                    first=commands[key][4];last=commands[(r,c['nodes'][-1])][5]
                    start=[-first[1],-first[0]];goal=[-last[1],-last[0]];length=math.dist(start,goal)
                    assert length>0
                    episode=f'{r}:{c["nodes"][0]}:{t}'
                    ep={'first_tick':t,'start':start,'goal':goal,'length_m':length,'nodes':list(c['nodes']),'final_node':c['nodes'][-1],'pause_ticks':0}
                    episodes[episode]=ep
                    for n in c['nodes']:node_episode[(r,n)]=episode
                if episode is not None:ep=episodes[episode]
                if ep and c['paused']:ep['pause_ticks']+=1
            rate=statistics.median(completed_rates) if completed_rates else None
            elapsed=t-ep['first_tick'] if ep else None
            remaining=max(0,rate*ep['length_m']-(elapsed-ep['pause_ticks'])) if rate is not None and ep else None
            features={'action_type':{0:'MOVE',1:'TURN',2:'STOP',3:'STATION'}[c['type']],'node_ids':list(c['nodes']),'task_id':c['task_id'],
                'public_target_xy_m':[c['target_x'],c['target_y']] if c['nodes'] else None,
                'public_episode_start_xy_m':ep['start'] if ep else None,'public_episode_goal_xy_m':ep['goal'] if ep else None,'public_episode_length_m':ep['length_m'] if ep else None,
                'wheel_left_cm_s':c['issued_left_cm_s'],'wheel_right_cm_s':c['issued_right_cm_s'],'queue_size':c['queue_size'],
                'visible_head_tasks':goals,'delivered_END_count':len(past_ends),'last_delivered_ENDs':past_ends[-4:],
                'episode_first_nonzero_command_tick':ep['first_tick'] if ep else None,'episode_elapsed_ticks':elapsed,
                'observed_pause_ticks_so_far':ep['pause_ticks'] if ep else 0,'intervention_applied_now':c['paused'],
                'last_known_intervention_start_tick':applied_start,'completed_MOVE_episode_count':len(completed_rates),
                'past_MOVE_ticks_per_median':rate,'historical_predicted_remaining_ticks':remaining}
            context={'trial':trial,'agent':r,'tick':t,'freeze_sequence':seq,'visibility':'execution_monitor_delivered_after_current_wheel_command_not_current_GPIBT_input','features':features}
            # deepcopy via JSON freezes mutable histories/tasks/pause counters.
            context=json.loads(json.dumps(context));check_context(context);contexts.append(context)
            o=observed[r];next_o=all_observations.get((r,t+1));progress=lateral=next_progress_delta=None
            if ep:
                dx=ep['goal'][0]-ep['start'][0];dy=ep['goal'][1]-ep['start'][1];length=ep['length_m']
                px=o['x']-ep['start'][0];py=o['y']-ep['start'][1]
                progress=(px*dx+py*dy)/length;lateral=(dx*py-dy*px)/length
                if next_o:next_progress_delta=((next_o['x']-o['x'])*dx+(next_o['y']-o['y'])*dy)/length
            node_acks=[{'node':n,'future_ack_tick':future_ends[(r,n)]['tick'] if (r,n) in future_ends else None,'right_censored_at_horizon':(r,n) not in future_ends} for n in c['nodes']]
            final_ack=future_ends.get((r,ep['final_node'])) if ep else None
            if final_ack:assert final_ack['sequence']>seq,'future target is already delivered'
            actual_remaining=final_ack['tick']-t if final_ack else None
            phase='pre_virtual_trigger' if offline_trigger is None or t<offline_trigger else ('pause' if c['paused'] else 'after_virtual_trigger_or_resume')
            target={'trial':trial,'agent':r,'tick':t,'freeze_sequence':seq,'target_visibility':'offline_only_not_strategy_input',
                'actual_sample_xy_m':[o['x'],o['y']],'actual_sample_angle_deg':o['angle'],'signed_progress_m':progress,'signed_progress_fraction':progress/ep['length_m'] if ep else None,'signed_lateral_m':lateral,
                'next_observed_displacement_m':math.dist([o['x'],o['y']],[next_o['x'],next_o['y']]) if next_o else None,'next_signed_progress_delta_m':next_progress_delta,
                'future_node_ACKs':node_acks,'future_episode_final_ACK_tick':final_ack['tick'] if final_ack else None,'future_episode_remaining_ticks':actual_remaining,
                'episode_right_censored_at_horizon':bool(ep and final_ack is None),'latest_delivered_pose_tick':199,'administrative_horizon_tick':200,'offline_stage':phase}
            targets.append(target)
            if ep:
                residuals.append({'trial':trial,'agent':r,'tick':t,'freeze_sequence':seq,'episode_id':episode,'baseline_visibility':'only_prior_delivered_normal_ACKs_and_public_intent',
                    'prior_completed_episode_count':len(completed_rates),'historical_predicted_remaining_ticks':remaining,'offline_actual_remaining_ticks':actual_remaining,
                    'offline_residual_ticks':actual_remaining-remaining if actual_remaining is not None and remaining is not None else None,'right_censored_at_horizon':final_ack is None,'offline_stage':phase})
                motion.append({'trial':trial,'agent':r,'tick':t,'sequence':seq,'episode_id':episode,'paused':c['paused'],'progress_m':progress,'lateral_m':lateral,'left_cm_s':c['issued_left_cm_s'],'right_cm_s':c['issued_right_cm_s']})
    assert len(contexts)==len(targets)==400
    return {'contexts':contexts,'targets':targets,'residuals':residuals,'motion':motion}
def write_jsonl(p,rows):
    with p.open('x') as f:
        for r in rows:f.write(json.dumps(r,sort_keys=True)+'\n')
def run():
    audit=json.loads((HERE/'audit.json').read_text());assert audit['fixed_pair_passed']
    summary={}
    for name in audit['reported_fixed_trials']:
        raw=HERE/'attempts'/name;events=[json.loads(s) for s in (raw/'events.jsonl').read_text().splitlines()];d=data(events,name)
        dst=HERE/'datasets'/name;dst.mkdir(parents=True,exist_ok=False)
        for filename,key in [('delivered_context.jsonl','contexts'),('offline_targets.jsonl','targets'),('feedback_residuals.jsonl','residuals')]:write_jsonl(dst/filename,d[key])
        with (dst/'motion_progress.csv').open('x',newline='') as f:
            keys=['trial','agent','tick','sequence','episode_id','paused','progress_m','lateral_m','left_cm_s','right_cm_s'];w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows(d['motion'])
        vals=[r['offline_residual_ticks'] for r in d['residuals'] if r['offline_residual_ticks'] is not None]
        summary[name]={'raw_sha256':sha(raw/'events.jsonl'),'context_rows':len(d['contexts']),'target_rows':len(d['targets']),'MOVE_context_rows':len(d['residuals']),'residual_rows_with_prior_history_and_uncensored_ACK':len(vals),'max_abs_lateral_m':max([abs(r['lateral_m']) for r in d['motion']] or [0]),'residual_range_ticks':[min(vals),max(vals)] if vals else None,'files':{p.name:sha(p) for p in dst.iterdir() if p.is_file()}}
    result={'status':'SEPARATE_CAUSAL_CONTEXT_AND_OFFLINE_TARGETS','context_has_actual_pose_or_future_targets':False,'current_planner_used_dataset':False,'trained_policy_evaluated':False,'schema_sha256':sha(HERE/'DATA_SCHEMA.md'),'exporter_sha256':sha(HERE/'export_data.py'),'trials':summary}
    with (HERE/'dataset_manifest.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':run()
