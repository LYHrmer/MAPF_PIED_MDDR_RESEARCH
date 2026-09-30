"""Independent physical stop/restore facts and full original-step targets from saved public plans."""
from pathlib import Path
import hashlib,json,math
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def run():
    audit=json.loads((HERE/'audit.json').read_text());summary={}
    for trial in audit['reported_fixed_trials']:
        es=[json.loads(s) for s in (HERE/'attempts'/trial/'events.jsonl').read_text().splitlines()]
        cs=[json.loads(s) for s in (HERE/'datasets'/trial/'delivered_context.jsonl').read_text().splitlines()]
        ctx_by_seq={c['freeze_sequence']:c for c in cs}
        observations={(e['robot'],e['tick']):e['observation'] for e in es if e['kind']=='observation'}
        ends={(e['robot'],e['node']):e for e in es if e['kind']=='end'}
        proposal=None;steps={};at_seq={};node_steps={}
        for e in es:
            if e['kind']=='proposal':
                proposal=e['proposal']['proposal_id']
                for a,path in enumerate(e['proposal']['plan']):
                    start=[-path[0][0],-path[0][1]];goal=[-path[1][0],-path[1][1]]
                    steps[(proposal,str(a))]={'proposal_id':proposal,'agent':str(a),'public_start_xy_m':start,'public_goal_xy_m':goal,'public_length_m':math.dist(start,goal),'first_nonzero_MOVE_command_tick':None,'final_native_MOVE_node':None}
            elif e['kind']=='admit':
                for a in e['actions']:
                    if a[3]=='M':
                        node_steps[(e['robot'],a[1])]=(proposal,e['robot'])
                        s=steps[(proposal,e['robot'])]
                        if [-a[5][1],-a[5][0]]==s['public_goal_xy_m']:s['final_native_MOVE_node']=a[1]
            elif e['kind']=='control' and e['control']['phase']=='wheel_command':
                if proposal is not None:
                    key=(proposal,e['robot']);s=steps[key];at_seq[e['sequence']]=key
                    c=e['control']
                    if c['type']==0 and (c['issued_left_cm_s']!=0 or c['issued_right_cm_s']!=0) and s['first_nonzero_MOVE_command_tick'] is None:s['first_nonzero_MOVE_command_tick']=e['tick']
        rows=[]
        for seq,key in at_seq.items():
            c=ctx_by_seq[seq];s=steps[key];length=s['public_length_m']
            if length==0:continue
            r=c['agent'];t=c['tick'];o=observations[(r,t)];a=s['public_start_xy_m'];b=s['public_goal_xy_m']
            direction=[(b[i]-a[i])/length for i in range(2)];p=[o['x']-a[0],o['y']-a[1]]
            end=ends.get((r,s['final_native_MOVE_node']))
            rows.append({'trial':trial,'agent':r,'tick':t,'freeze_sequence':seq,'target_visibility':'offline_only_not_strategy_input',
                'proposal_id':key[0],'public_original_step_start_xy_m':a,'public_original_step_goal_xy_m':b,'public_original_step_length_m':length,
                'original_step_progress_m':p[0]*direction[0]+p[1]*direction[1],'original_step_signed_lateral_m':direction[0]*p[1]-direction[1]*p[0],
                'original_MOVE_first_nonzero_command_tick':s['first_nonzero_MOVE_command_tick'],'original_MOVE_final_node':s['final_native_MOVE_node'],
                'original_MOVE_normal_END_tick':end['tick'] if end else None,'original_MOVE_END_already_delivered_at_freeze':bool(end and end['sequence']<seq),
                'original_MOVE_remaining_ticks_offline':max(0,end['tick']-t) if end else None,'original_MOVE_right_censored_at_horizon':end is None})
        output=HERE/'datasets'/trial/'original_step_targets.jsonl'
        with output.open('x') as f:
            for row in rows:f.write(json.dumps(row,sort_keys=True)+'\n')
        trigger=audit['trials'][trial]['active_trigger'];T=trigger['tick'] if trigger else None
        plateau=[];tail=[];first_motion_after_resume=None
        if T is not None and trial=='pause':
            for t in range(T+1,T+21):
                d=observations[('0',t)]['displacement_m']
                (plateau if d<=1e-6 else tail).append({'tick':t,'displacement_m':d})
            first_motion_after_resume=next((t for t in range(T+21,200) if observations[('0',t)]['displacement_m']>1e-6),None)
            assert plateau and all(observations[('0',t)]['displacement_m']<=1e-6 for t in range(plateau[0]['tick'],T+21)), 'no sustained physical stop before resume'
            assert first_motion_after_resume is not None,'no actual motion after restored control'
        step_summary=[]
        for s in steps.values():
            if s['public_length_m']==0:continue
            end=ends.get((s['agent'],s['final_native_MOVE_node']))
            step_summary.append({**s,'normal_original_MOVE_END_tick':end['tick'] if end else None,'duration_from_first_nonzero_command_ticks':end['tick']-s['first_nonzero_MOVE_command_tick'] if end and s['first_nonzero_MOVE_command_tick'] is not None else None,'right_censored_at_horizon':end is None})
        summary[trial]={'raw_event_count':len(es),'parent_filtered_mapping_event_count':audit['trials'][trial]['event_count'],'original_step_target_rows':len(rows),'original_step_targets_sha256':sha(output),
            'trigger_tick':T,'actual_stop_coast_tail_samples':tail,'actual_zero_displacement_samples_through_resume_boundary':plateau,'first_actual_motion_tick_after_resume':first_motion_after_resume,'original_grid_MOVE_steps':step_summary}
    result={'status':'PASSED_PHYSICAL_STOP_RESTORE_AND_ORIGINAL_MOVE_RECONSTRUCTION','trials':summary,'no_new_native_run':True,'sampled_physical_metrics_not_continuous_footprint_proof':True,'auditor_sha256':sha(HERE/'motion_supplement.py')}
    with (HERE/'motion_supplement.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({n:{k:v for k,v in r.items() if k not in ['original_grid_MOVE_steps','actual_zero_displacement_samples_through_resume_boundary']} for n,r in summary.items()},indent=2))
if __name__=='__main__':run()
