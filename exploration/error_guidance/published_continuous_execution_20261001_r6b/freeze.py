from pathlib import Path
import hashlib,json,importlib.util,sys,datetime
HERE=Path(__file__).resolve().parent;MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence');OUT=MAIN/HERE.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert not (HERE/'freeze.json').exists() and not (OUT/'runs').exists()
for n,h in json.loads((HERE/'native_source_manifest.json').read_text()).items():assert sha(OUT/'lsmart_successor'/n)==h,n
for files in json.loads((HERE/'official_object_manifest.json').read_text()).values():
 for p,h in files.items():assert sha(p)==h,p
spec=importlib.util.spec_from_file_location('r6_official_source_audit',HERE.parent/'published_guidance_comparison_20260930_r4/run.py');m=importlib.util.module_from_spec(spec);sys.modules[spec.name]=m;spec.loader.exec_module(m);source=m.source_audit()
files=[p for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts]
pins={str(p):sha(p) for p in files}
pins.update(json.loads((HERE/'binary_manifest.json').read_text()))
for p in [HERE.parent/'onlineggo_training_20260930_r3/training_02/trained_checkpoint.json',HERE.parent/'onlineggo_training_20260930_r3/training_02/freeze.json',HERE.parent/'gpibt_lsmart_error_model_20260930_r4c/artifact_manifest.json',HERE.parent/'standard_map_pilot_20260930_r5/artifact_manifest.json']:pins[str(p)]=sha(p)
freeze={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'pins':pins,'official_source_before':source,'native_runs':24,'ACK_version':'S1_point_no_merge','horizon_ticks':8000,'physical_seconds':800,'raw_root':str(OUT/'runs'),'method_names':['author hm+GPIBT OBJ3 adapted S1','author frozen OnlineGGO OBJ4 adapted S1'],'internal_tie_sequence_fully_paired_after_divergence':False}
(HERE/'freeze.json').write_text(json.dumps(freeze,indent=2)+'\n')
print('READY',sha(HERE/'freeze.json'),len(pins))
