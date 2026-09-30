"""Lossless eight-job archive and final package hash freeze."""
from pathlib import Path
import hashlib,json,tarfile
HERE=Path(__file__).resolve().parent
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
RAW=MAIN/HERE.name;UP=MAIN/'baseline_selection_20260929/OnlineGGO'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
archive=HERE/'raw_native_and_inputs.tar.gz';assert not archive.exists()
freeze=json.loads((HERE/'freeze.json').read_text())
for p,h in freeze['pins'].items():assert sha(p)==h,p
files={str(p.relative_to(RAW)):p for p in RAW.rglob('*') if p.is_file()}
for rel in ['LICENSE','Guided-PIBT/guided-pibt/src/py_driver.cpp','Guided-PIBT/guided-pibt/src/Grid.cpp','Guided-PIBT/guided-pibt/src/CompetitionSystem.cpp','Guided-PIBT/guided-pibt/inc/CompetitionSystem.h','Guided-PIBT/guided-pibt/inc/common.h']:files['official/'+rel]=UP/rel
files['worker/native_worker.py']=HERE.parent/'onlineggo_training_20260930_r3/native_worker.py'
files['provenance/trained_checkpoint.json']=HERE.parent/'onlineggo_training_20260930_r3/training_02/trained_checkpoint.json'
files['provenance/training_freeze.json']=HERE.parent/'onlineggo_training_20260930_r3/training_02/freeze.json'
files['provenance/official_map_registry.json']=HERE.parent/'mapf_evaluation_20260930_r5/registry.json'
files['provenance/hm_build.json']=HERE.parent/'published_guidance_comparison_20260930_r4/build.json'
files['provenance/paired_module_freeze.json']=HERE.parent/'paired_published_guidance_20260930_r5/freeze.json'
manifest={name:{'sha256':sha(p),'bytes':p.stat().st_size} for name,p in sorted(files.items())}
with tarfile.open(archive,'w:gz',compresslevel=6) as tar:
 for name,p in sorted(files.items()):tar.add(p,arcname=name,recursive=False)
with tarfile.open(archive) as tar:
 members=tar.getmembers();assert len(members)==len(files)
 for member in members:
  assert member.isfile();data=tar.extractfile(member).read();expected=manifest[member.name];assert len(data)==expected['bytes'] and hashlib.sha256(data).hexdigest()==expected['sha256']
out={'verified':True,'archive_sha256':sha(archive),'archive_bytes':archive.stat().st_size,'raw_bytes':sum(x['bytes'] for x in manifest.values()),'files':manifest}
(HERE/'archive_manifest.json').write_text(json.dumps(out,indent=2)+'\n')
(HERE/'artifact_manifest.json').write_text(json.dumps({p.name:sha(p) for p in HERE.iterdir() if p.is_file() and p.name!='artifact_manifest.json'},indent=2)+'\n')
print(json.dumps({'verified_members':len(manifest),'raw_bytes':out['raw_bytes'],'archive_bytes':out['archive_bytes'],'artifact_manifest_sha256':sha(HERE/'artifact_manifest.json')}))
