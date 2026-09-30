"""Freeze a complete file manifest after all causal replay checks pass."""
from pathlib import Path
import hashlib, json, platform, sys

HERE=Path(__file__).resolve().parent
OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_integration_20260930_r2')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
read=lambda p:json.loads(p.read_text())
for path,digest in read(HERE/'previous_archive_manifest.json').items():
    assert sha(HERE.parent/'gpibt_lsmart_integration_20260930'/path)==digest,path
for path,digest in read(HERE/'binary_manifest.json').items():assert sha(Path(path))==digest,path
retained=read(HERE/'first_pair_retained_binary.json')
assert sha(Path(retained['retained_path']))==retained['sha256']
initial=read(HERE/'first_pair_binary_manifest.json')
for path,digest in initial.items():
    location=Path(retained['retained_path']) if path==retained['original_path'] else Path(path)
    assert sha(location)==digest,path
for name,pins in read(HERE/'source_manifest.json').items():
    assert sha(OUT/'lsmart_successor'/name)==pins['successor'],name
for name,pins in read(HERE/'first_pair_source_manifest.json').items():
    assert sha(HERE/'first_pair_source_snapshot'/name)==pins['successor'],name
assert sha(HERE/'first_pair_source_snapshot/server/src/ADG.cpp')==read(HERE/'source_manifest.json')['server/src/ADG.cpp']['previous']
audit=read(HERE/'audit.json');assert audit['fixed_pair_passed']
for name,trial in audit['trials'].items():
    receipt=read(HERE/'attempts'/name/'receipt.json')
    for file,digest in receipt['files'].items():assert sha(HERE/'attempts'/name/file)==digest,(name,file)
    expected=read(HERE/('first_pair_binary_manifest.json' if name in ('nominal','pause') else 'binary_manifest.json'))
    assert receipt['binary_identities']==expected,name
assert audit['trials']['nominal']['audit_passed'] is False and audit['trials']['pause']['audit_passed'] is False
report={'status':'FROZEN_FIXED_TASK_WIRE_CORRECTION_PAIR','python':sys.version,'platform':platform.platform(),
    'prior_files_preserved':len(read(HERE/'previous_archive_manifest.json')),
    'final_native_fixed_trials':audit['reported_fixed_trials'],'final_pair_passed':True,
    'initial_pair_retained_and_strictly_rejected':True,'all_runtime_and_official_objects_verified':len(read(HERE/'binary_manifest.json')),
    'first_pair_server_binary_retained':True,'service_ends':[audit['trials'][n]['task_services'] for n in audit['reported_fixed_trials']],
    'actual_task_prefix_equal':audit['actual_task_prefix_equal'],
    'active_move_pause_validated':False,'continuous_footprint_safety_proved':False,'learned_policy_run':False}
(HERE/'archive_receipt.json').write_text(json.dumps(report,indent=2)+'\n')
manifest={str(p.relative_to(HERE)):sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and p.name!='artifact_manifest.json' and '__pycache__' not in p.parts}
(HERE/'artifact_manifest.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({**report,'archived_files':len(manifest),'artifact_manifest_sha256':sha(HERE/'artifact_manifest.json')},indent=2))
