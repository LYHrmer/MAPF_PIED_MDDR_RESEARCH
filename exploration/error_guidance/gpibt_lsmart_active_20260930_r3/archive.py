"""Freeze r3 after runtime identity, parent immutability, raw and separated-data checks."""
from pathlib import Path
import hashlib,json,platform,sys
HERE=Path(__file__).resolve().parent
OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_active_20260930_r3')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
for name,h in read(HERE/'previous_archive_manifest.json').items():assert sha(HERE.parent/'gpibt_lsmart_integration_20260930_r2'/name)==h,name
ids=read(HERE/'binary_manifest.json')
for name,h in ids.items():assert sha(Path(name))==h,name
for name,h in read(HERE/'ready_for_trial.json')['frozen_files'].items():assert sha(HERE/name)==h,name
tree=read(HERE/'native_source_tree_manifest.json')
changed=[]
for name,h in tree['successor'].items():
    assert sha(OUT/'lsmart_successor'/name)==h,name
    if h!=tree['parent'][name]:changed.append(name)
assert changed==['client/controllers/footbot_diffusion/footbot_diffusion.cpp','client/controllers/footbot_diffusion/footbot_diffusion.h']
for name,pins in read(HERE/'source_manifest.json').items():assert sha(HERE/'source_snapshot'/name)==pins['successor'],name
a=read(HERE/'audit.json');assert a['fixed_pair_passed'] and a['active_move_intervention_fully_validated']
for name in a['reported_fixed_trials']:
    p=HERE/'attempts'/name;receipt=read(p/'receipt.json')
    assert receipt['binary_identities']==ids and receipt['error'] is None and receipt['wall_seconds']<54
    for filename,h in receipt['files'].items():assert sha(p/filename)==h,(name,filename)
data=read(HERE/'dataset_manifest.json');assert sha(HERE/'DATA_SCHEMA.md')==data['schema_sha256']
for name,pins in data['trials'].items():
    for f,h in pins['files'].items():assert sha(HERE/'datasets'/name/f)==h,(name,f)
    assert sha(HERE/'datasets'/name/'original_step_targets.jsonl')==data['additional_full_original_step_targets'][name]
assert read(HERE/'dataset_audit_final.json')['dataset_manifest_sha256']==sha(HERE/'dataset_manifest.json')
assert read(HERE/'dataset_audit_final.json')['status']=='PASSED_SEPARATE_VISIBILITY_AND_TARGET_AUDIT'
assert read(HERE/'motion_supplement.json')['status']=='PASSED_PHYSICAL_STOP_RESTORE_AND_ORIGINAL_MOVE_RECONSTRUCTION'
receipt={'status':'FROZEN_REAL_ACTIVE_MOVE_INTERVENTION_PAIR','python':sys.version,'platform':platform.platform(),
    'direct_parent_files_byte_preserved':len(read(HERE/'previous_archive_manifest.json')),'verified_runtime_and_official_objects':len(ids),
    'only_changed_native_sources':changed,'fixed_native_trials':a['reported_fixed_trials'],'first_pair_passed':True,'native_retry_count':0,
    'preparation_failure_retained':True,'active_MOVE_pause_validated':True,'trigger_tick':59,'pause_ticks_inclusive':[59,78],'restore_tick':79,
    'original_MOVE_END_ticks':[84,104],'real_task_service_END_ticks':[136,156],'actual_coast_tail_m':0.003321428611342341,
    'contexts_per_arm':400,'offline_targets_per_arm':400,'original_step_targets_per_arm':360,
    'actual_task_prefix_equal':a['actual_task_prefix_equal'],'learned_policy_evaluated':False,'continuous_footprint_safety_proved':False,
    'data_scope_clarification_and_initial_artifacts_retained':True}
with (HERE/'archive_receipt.json').open('x') as f:json.dump(receipt,f,indent=2);f.write('\n')
manifest={str(p.relative_to(HERE)):sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json' and '__pycache__' not in p.parts}
with (HERE/'artifact_manifest.json').open('x') as f:json.dump(manifest,f,indent=2);f.write('\n')
print(json.dumps({**receipt,'frozen_files':len(manifest),'artifact_manifest_sha256':sha(HERE/'artifact_manifest.json')},indent=2))
