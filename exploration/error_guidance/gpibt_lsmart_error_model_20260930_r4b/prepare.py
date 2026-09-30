from pathlib import Path
import hashlib,json,shutil
HERE=Path(__file__).resolve().parent;P=HERE.parent/'gpibt_lsmart_error_model_20260930_r4'
N=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_error_model_20260930_r4b');PN=N.with_name('gpibt_lsmart_error_model_20260930_r4')
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):Path(p).write_text(json.dumps(v,indent=2,allow_nan=False)+'\n')
assert not N.exists()
parent=json.loads((P/'artifact_manifest.json').read_text())
for n,h in parent.items():assert sha(P/n)==h,n
write(HERE/'parent_archive_manifest.json',parent|{'artifact_manifest.json':sha(P/'artifact_manifest.json')})
N.mkdir()
for n in ['gpibt_bridge','server_build','client_build','lsmart_successor']:(N/n).symlink_to(PN/n,target_is_directory=n!='gpibt_bridge')
for n in ['trained_model.json','map.json','GPIBT_LICENSE.txt','LSMART_LICENSE.txt','gpibt_bridge.cpp','source_manifest.json','native_source_tree_manifest.json','binary_manifest.json','mapping_replay.py','export_data.py','audit.py']:shutil.copy2(P/n,HERE/n)
s=(P/'common.py').read_text().replace("gpibt_lsmart_error_model_20260930_r4')","gpibt_lsmart_error_model_20260930_r4b')")
a="    bias=[0.,0.] if policy=='zero' else [max(-amplitude,min(amplitude,amplitude*(v/mean-1))) for v in predicted]"
b="    bias=[0.,0.] if policy=='zero' or abs(predicted[0]-predicted[1])<1.0 else ([amplitude,-amplitude] if predicted[0]>predicted[1] else [-amplitude,amplitude])"
assert s.count(a)==1;(HERE/'common.py').write_text(s.replace(a,b))
s=(P/'run_trial.py').read_text().replace("gpibt_lsmart_error_model_20260930_r4')","gpibt_lsmart_error_model_20260930_r4b')").replace('port=9461','port=9471')
a="frozen=['PROTOCOL.md','runs.json','prepare.py','build.py','run_trial.py','common.py','gpibt_bridge.cpp','controller_condition.patch','source_manifest.json','native_source_tree_manifest.json','preflight_identity.json','binary_manifest.json','map.json']"
b="frozen=['PROTOCOL.md','runs.json','prepare.py','run_trial.py','common.py','gpibt_bridge.cpp','source_manifest.json','native_source_tree_manifest.json','preflight_identity.json','binary_manifest.json','map.json','model_freeze.json','calibration_rank_probe.json']"
assert s.count(a)==1;(HERE/'run_trial.py').write_text(s.replace(a,b))
runs=[{'id':f'test_s62_{c}_{pol}','split':'test','seed':62,'condition':c,'policy':pol,'horizon_ticks':400} for c in ['nominal','slow065','slow085','axis','unknown_pause','unknown_shift'] for pol in ['zero','analytic','history','learned']]
write(HERE/'runs.json',{'protocol_sha256':sha(HERE/'PROTOCOL.md'),'runs':runs})
write(HERE/'preflight_identity.json',{'protocol_sha256':sha(HERE/'PROTOCOL.md'),'runs_sha256':sha(HERE/'runs.json'),'parent_manifest_sha256':sha(P/'artifact_manifest.json'),'parent_server_sha256':sha(N/'server_build/ExecutionManager')})
write(HERE/'model_freeze.json',{'files':{n:sha(HERE/n) for n in ['trained_model.json','common.py','export_data.py','PROTOCOL.md']},'amplitude':1.,'test_runs_started':False,'model_training_unchanged':True,'parent_model_freeze_sha256':sha(P/'model_freeze.json')})
print(N)
