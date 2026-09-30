from common import HERE,sha,events,predict,write
import json,statistics,hashlib
audit=json.loads((HERE/'audit.json').read_text());model=json.loads((HERE/'trained_model.json').read_text());summaries={};metrics={};all_rows=0
for spec in json.loads((HERE/'runs.json').read_text())['runs']:
 rid=spec['id'];r=audit['runs'][rid];p=HERE/'datasets'/rid;xs=events(p/'delivered_context.jsonl');ys=events(p/'offline_original_MOVE_targets.jsonl')
 assert [x['key'] for x in xs]==[y['key'] for y in ys]
 ds=events(HERE/'attempts'/rid/'decisions.jsonl');receipt=json.loads((HERE/'attempts'/rid/'receipt.json').read_text())
 gaps=[y['proposal_to_first_nonzero_MOVE_gap_ticks'] for y in ys if y['duration_ticks'] is not None]
 summaries[rid]={'spec':spec,'native_error':receipt['error'],'wall_seconds':receipt['wall_seconds'],'decisions':len(ds),'task_services':r['task_services'],
   'task_prefix':r['assigned_task_prefix'],'pending':r['horizon_unfinished_nodes'],'sampled_min_center_distance_m':r['sampled_min_center_distance_m'],
   'original_MOVE_rows':len(xs),'uncensored_rows':sum(y['duration_ticks'] is not None for y in ys),'censored_rows':sum(y['duration_ticks'] is None for y in ys),
   'trigger_tick':r['actual_trigger_tick'],'priority_order_flips':r['priority_search_order_flips'],'strict_point_endpoint_gate':r['strict_all_node_point_endpoint_gate_passed'],
   'point_deviations':r['point_endpoint_deviations'],'proposal_to_nonzero_MOVE_gap_mean_ticks':statistics.mean(gaps) if gaps else None,
   'actions':[d['result']['actions'] for d in ds],'decision_ticks':[d['snapshot']['tick'] for d in ds]}
 all_rows+=len(xs)
 if spec['split']=='test' and spec['policy']=='zero':
  usable=[(x,y) for x,y in zip(xs,ys) if y['duration_ticks'] is not None]
  metrics[spec['condition']]={pol:statistics.mean(abs(predict(x['features'],pol,model)-y['duration_ticks']) for x,y in usable) for pol in ['analytic','history','learned']}
conditions={}
for c in ['nominal','slow065','slow085','axis','unknown_pause','unknown_shift']:
 rs={p:summaries[f'test_s61_{c}_{p}'] for p in ['zero','analytic','history','learned']}
 conditions[c]={'all_actual_actions_equal':all(r['actions']==rs['zero']['actions'] for r in rs.values()),
  'all_decision_ticks_equal':all(r['decision_ticks']==rs['zero']['decision_ticks'] for r in rs.values()),'policies':rs,'shadow_chosen_axis_duration_MAE_ticks':metrics[c]}
write(HERE/'summary.json',{'status':'TRAINED_LIVE_PREDICTION_BUT_NO_HELDOUT_ACTION_INFLUENCE','native_runs':len(summaries),'all_native400_completed':all(r['native_error'] is None for r in summaries.values()),
 'all_mapping_original_predicate_and_service_audits_passed':audit['all_available_passed'],'all_node_point_gate_passed':all(r['strict_point_endpoint_gate'] for r in summaries.values()),
 'total_original_MOVE_rows':all_rows,'model_sha256':sha(HERE/'trained_model.json'),'training_rows':model['training_rows'],'calibration_rows':model['calibration_rows'],
 'calibration':json.loads((HERE/'calibration.json').read_text()),'conditions':conditions,'runs':summaries,'scientific_closed_loop_action_effect_established':False,'learning_performance_advantage_established':False})
print(json.dumps({'runs':len(summaries),'conditions':{c:{'tasks':v['policies']['zero']['task_services'],'actions_equal':v['all_actual_actions_equal'],'MAE':metrics[c]} for c,v in conditions.items()}},indent=2))
