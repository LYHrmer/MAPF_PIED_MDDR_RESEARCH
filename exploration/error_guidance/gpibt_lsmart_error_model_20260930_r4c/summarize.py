"""All fixed mechanism arms, task-count primary and unselected timing consequences."""
from common import HERE,sha,events,write,predict
import json,statistics
POLICIES=['zero','analytic','history','learned','fixed_agent0','fixed_agent1']
CONDITIONS=['nominal','slow065','slow085','axis','unknown_pause','unknown_shift']
audit=json.loads((HERE/'audit.json').read_text());dataset=json.loads((HERE/'dataset_audit.json').read_text());model=json.loads((HERE/'trained_model.json').read_text());runs={};decisions={}
for spec in json.loads((HERE/'runs.json').read_text())['runs']:
 rid=spec['id'];r=audit['runs'][rid];p=HERE/'attempts'/rid;receipt=json.loads((p/'receipt.json').read_text());ds=events(p/'decisions.jsonl');decisions[rid]=ds
 prefixes=[[],[]];owners={}
 for tid,owner,goal in r['assigned_task_prefix']:owners[str(tid)]=(owner,len(prefixes[owner]),goal);prefixes[owner].append({'task_id':tid,'goal':goal,'completion_tick':None})
 for tid,s in r['completed_tasks'].items():
  owner,k,goal=owners[str(tid)];prefixes[owner][k]['completion_tick']=s['tick']
 rows=dataset['runs'][rid];ys=events(HERE/'datasets'/rid/'offline_original_MOVE_targets.jsonl');gaps=[y['proposal_to_first_nonzero_MOVE_gap_ticks'] for y in ys if y['duration_ticks'] is not None]
 runs[rid]={'spec':spec,'native_error':receipt['error'],'wall_seconds':receipt['wall_seconds'],'decisions':len(ds),'task_services':r['task_services'],
  'bookkept_tasks':len(r['bookkept_tasks']),'assigned_task_prefix':r['assigned_task_prefix'],'FIFO_tasks_by_owner':prefixes,'completed_tasks':r['completed_tasks'],
  'trigger_tick':r['actual_trigger_tick'],'priority_order_flips':r['priority_search_order_flips'],'original_MOVE_rows':rows['original_MOVE_rows'],'uncensored_rows':rows['uncensored'],'censored_rows':rows['censored'],
  'sampled_min_center_distance_m':r['sampled_min_center_distance_m'],'strict_point_endpoint_gate':r['strict_all_node_point_endpoint_gate_passed'],'point_deviations':r['point_endpoint_deviations'],
  'full_MOVE_endpoint_max_error_m':rows['full_MOVE_endpoint_max_error_m'],'pending_tasks':r['unfinished_tasks'],'pending_nodes_by_owner':r['horizon_unfinished_nodes'],'last_actual_pose_tick':r['latest_terminal_pose_tick'],
  'proposal_to_first_nonzero_MOVE_gap_mean_ticks':statistics.mean(gaps) if gaps else None,'actions':[d['result']['actions'] for d in ds],'decision_ticks':[d['snapshot']['tick'] for d in ds]}
conditions={}
for c in CONDITIONS:
 rs={p:runs[f'test_s62_{c}_{p}'] for p in POLICIES};zd=decisions[f'test_s62_{c}_zero'];comparisons={}
 for p in POLICIES:
  dd=decisions[f'test_s62_{c}_{p}'];first=None
  for i,(z,d) in enumerate(zip(zd,dd)):
   if z['result']['actions']!=d['result']['actions']:
    first={'proposal_index':i,'zero_tick':z['snapshot']['tick'],'policy_tick':d['snapshot']['tick'],'same_public_view':z['view']==d['view'],'same_tick':z['snapshot']['tick']==d['snapshot']['tick'],
     'zero_actions':z['result']['actions'],'policy_actions':d['result']['actions'],'zero_proposal':z['proposal'],'policy_proposal':d['proposal'],'public_view':d['view'],
     'predicted_ticks':d['forecast']['predicted_ticks'],'bias':d['forecast']['bias'],'priority':d['result']['priority_adapter'],'delivered_context':d['forecast']['context']};break
  deltas=[]
  for owner in range(2):
   for k,(z,t) in enumerate(zip(rs['zero']['FIFO_tasks_by_owner'][owner],rs[p]['FIFO_tasks_by_owner'][owner])):
    assert z['goal']==t['goal']
    deltas.append({'owner':owner,'FIFO_ordinal':k,'goal':z['goal'],'zero_completion_tick':z['completion_tick'],'policy_completion_tick':t['completion_tick'],
     'delta_policy_minus_zero_ticks':t['completion_tick']-z['completion_tick'] if t['completion_tick'] is not None and z['completion_tick'] is not None else None,
     'right_censored_in_either_arm':t['completion_tick'] is None or z['completion_tick'] is None})
  values=[d['delta_policy_minus_zero_ticks'] for d in deltas if d['delta_policy_minus_zero_ticks'] is not None]
  comparisons[p]={'actual_action_sequence_equal_to_zero':rs[p]['actions']==rs['zero']['actions'],'actual_decision_ticks_equal_to_zero':rs[p]['decision_ticks']==rs['zero']['decision_ticks'],
   'first_actual_action_difference':first,'all_common_FIFO_service_timing_differences':deltas,'matched_uncensored_timing_changes':{'earlier':sum(v<0 for v in values),'same':sum(v==0 for v in values),'later':sum(v>0 for v in values),'sum_delta_ticks':sum(values),'min_delta_ticks':min(values,default=None),'max_delta_ticks':max(values,default=None)},
   'first_three_completion_ticks_by_owner':[[s['completion_tick'] for s in rs[p]['FIFO_tasks_by_owner'][a][:3]] for a in range(2)]}
 p2=decisions[f'test_s62_{c}_learned'][2]
 conditions[c]={'primary_actual_task_services':{p:rs[p]['task_services'] for p in POLICIES},'actual_order_flips':{p:rs[p]['priority_order_flips'] for p in POLICIES},
  'model_action_influence_at_identical_public_state':bool(comparisons['learned']['first_actual_action_difference'] and comparisons['learned']['first_actual_action_difference']['same_public_view'] and comparisons['learned']['first_actual_action_difference']['same_tick']),
  'learned_actions_equal_analytic':rs['learned']['actions']==rs['analytic']['actions'],'learned_actions_equal_history':rs['learned']['actions']==rs['history']['actions'],
  'predeclared_third_request':{'tick':p2['snapshot']['tick'],'public_view':p2['view'],'history_completed_steps':len(p2['forecast']['context']['completed_steps']),'bias':p2['forecast']['bias'],'predictions':p2['forecast']['predicted_ticks'],'actual_actions':p2['result']['actions'],'actions_equal_zero':p2['result']['actions']==zd[2]['result']['actions']},'comparisons_to_zero':comparisons}
out={'status':'REAL_PREDICTION_ACTION_SERVICE_CHAIN_WITH_NO_LEARNING_ADVANTAGE','native_runs':len(runs),'all_native800_completed':all(r['native_error'] is None for r in runs.values()),'all_mapping_original_predicate_service_audits_passed':audit['all_available_passed'],'all_independent_dataset_audits_passed':dataset['all_passed'],
 'model_sha256':sha(HERE/'trained_model.json'),'model_training_rows':model['training_rows'],'model_calibration_rows':model['calibration_rows'],'model_retrained_or_test_tuned':False,
 'total_original_MOVE_rows':sum(r['original_MOVE_rows'] for r in runs.values()),'total_uncensored_rows':sum(r['uncensored_rows'] for r in runs.values()),'total_censored_rows':sum(r['censored_rows'] for r in runs.values()),
 'all_node_point_gate_passed':all(r['strict_point_endpoint_gate'] for r in runs.values()),'point_deviation_run_count':sum(not r['strict_point_endpoint_gate'] for r in runs.values()),'sampled_min_center_distance_m':min(r['sampled_min_center_distance_m'] for r in runs.values()),'full_MOVE_endpoint_max_error_m':max(r['full_MOVE_endpoint_max_error_m'] for r in runs.values()),
 'scientific_closed_loop_action_effect_established':any(c['model_action_influence_at_identical_public_state'] for c in conditions.values()),'learning_performance_advantage_established':False,'standard_MAPF_benchmark_claim_supported':False,'continuous_footprint_safety_established':False,'task_count_metric':'actual normal STATION END, includes unbookkept final service','timing_diagnostics':'all matched owner/FIFO-ordinal services; no released-flow aggregate objective','conditions':conditions,'runs':runs}
write(HERE/'summary.json',out)
print(json.dumps({'native_runs':len(runs),'model_sha256':out['model_sha256'],'task_services':{c:r['primary_actual_task_services'] for c,r in conditions.items()},'actual_model_action_changes':{c:r['model_action_influence_at_identical_public_state'] for c,r in conditions.items()},'whole_MOVE_rows':out['total_original_MOVE_rows'],'uncensored':out['total_uncensored_rows'],'censored':out['total_censored_rows']},indent=2))
