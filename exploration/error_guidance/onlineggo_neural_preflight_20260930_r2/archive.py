"""Archive the exact qualification receipts; never copies external binaries."""
from pathlib import Path
import hashlib
import json
import shutil

HERE=Path(__file__).resolve().parent
LOCAL=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/onlineggo_neural_r0_20260930_r2')
SOURCE=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/baseline_selection_20260929/OnlineGGO')
raw=HERE/'raw'
raw.mkdir()
for path in LOCAL.iterdir():
    if path.name=='build_nn':
        continue
    if path.is_dir():
        shutil.copytree(path,raw/path.name)
    else:
        shutil.copyfile(path,raw/path.name)
shutil.copyfile(SOURCE/'LICENSE',HERE/'UPSTREAM_LICENSE.txt')
manifest={str(p.relative_to(HERE)):hashlib.sha256(p.read_bytes()).hexdigest()
          for p in HERE.rglob('*') if p.is_file() and '__pycache__' not in p.parts
          and p.name!='artifact_manifest.json'}
with (HERE/'artifact_manifest.json').open('x') as out:
    json.dump(manifest,out,indent=2);out.write('\n')
print(json.dumps({'archived_files':len(manifest),'bytes':sum(p.stat().st_size for p in HERE.rglob('*') if p.is_file())}))
