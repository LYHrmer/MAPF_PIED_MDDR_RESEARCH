from common import HERE,NATIVE,sha,write
from pathlib import Path
import json
assert json.loads((HERE/'audit.json').read_text())['all_available_passed']
assert json.loads((HERE/'dataset_audit.json').read_text())['all_passed']
s=json.loads((HERE/'summary.json').read_text());assert s['native_runs']==36 and s['all_native800_completed'] and s['scientific_closed_loop_action_effect_established'] and not s['learning_performance_advantage_established']
parent=HERE.parent/'gpibt_lsmart_error_model_20260930_r4b'
pm=json.loads((HERE/'parent_archive_manifest.json').read_text())
for n,h in pm.items():assert sha(parent/n)==h,n
grandparent=HERE.parent/'gpibt_lsmart_error_model_20260930_r4'
gm=json.loads((parent/'parent_archive_manifest.json').read_text())
for n,h in gm.items():assert sha(grandparent/n)==h,n
for p,h in json.loads((HERE/'binary_manifest.json').read_text()).items():assert sha(p)==h,p
for n,h in json.loads((HERE/'ready_for_trial.json').read_text())['frozen_files'].items():assert sha(HERE/n)==h,n
for n,h in json.loads((HERE/'model_freeze.json').read_text())['files'].items():assert sha(HERE/n)==h,n
native_manifest=json.loads((HERE/'native_source_tree_manifest.json').read_text())
for n,h in native_manifest['server_sources'].items():assert sha(NATIVE/'lsmart_successor'/n)==h,n
write(HERE/'archive_receipt.json',{'status':'FROZEN_36_NATIVE_ACTION_EFFECT_NO_LEARNING_ADVANTAGE','native_runs':36,'horizon_ticks':800,'parent_files_preserved':len(pm),'R4_files_preserved':len(gm),'native_identities':18,'model_sha256':sha(HERE/'trained_model.json'),'model_retrained':False,'new_native_source_changes':['server/src/task_assigners/OneGoalTaskAssigner.cpp'],'official_search_objects_changed':False,'official_controller_changed':False,'priority_adapter_unchanged_from_R4b':True,'protocol_sha256':sha(HERE/'PROTOCOL.md'),'original_ACK_predicates_passed':True,'strict_all_node_point_gate_passed':s['all_node_point_gate_passed'],'continuous_safety_established':False})
write(HERE/'artifact_manifest.json',{str(p.relative_to(HERE)):sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='artifact_manifest.json'})
print('FROZEN',sha(HERE/'artifact_manifest.json'))
