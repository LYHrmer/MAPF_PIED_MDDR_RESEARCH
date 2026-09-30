from common import HERE,NATIVE,sha,write
import json
assert json.loads((HERE/'audit.json').read_text())['all_available_passed']
assert json.loads((HERE/'summary.json').read_text())['native_runs']==40
for n,h in json.loads((HERE/'parent_archive_manifest.json').read_text()).items():assert sha(HERE.parent/'gpibt_lsmart_active_20260930_r3'/n)==h,n
for p,h in json.loads((HERE/'binary_manifest.json').read_text()).items():assert sha(p)==h,p
for n,h in json.loads((HERE/'ready_for_trial.json').read_text())['frozen_files'].items():assert sha(HERE/n)==h,n
for n,h in json.loads((HERE/'model_freeze.json').read_text())['files'].items():assert sha(HERE/n)==h,n
write(HERE/'archive_receipt.json',{'status':'FROZEN_NULL_RESULT_40_NATIVE_RUNS','parent_files_preserved':len(json.loads((HERE/'parent_archive_manifest.json').read_text())),'native_identities':18,'model_sha256':sha(HERE/'trained_model.json'),'source_changes':['client/controllers/footbot_diffusion/footbot_diffusion.h','client/controllers/footbot_diffusion/footbot_diffusion.cpp'],'bridge_adapter_changed':True,'original_core_algorithm_changed':False})
write(HERE/'artifact_manifest.json',{str(p.relative_to(HERE)):sha(p) for p in sorted(HERE.rglob('*')) if p.is_file() and '__pycache__' not in p.parts and p.name!='artifact_manifest.json'})
print(sha(HERE/'artifact_manifest.json'))
