"""Preserve exact native evidence and upstream context, excluding build/env caches."""
import gzip
import hashlib
import io
import json
from pathlib import Path
import shutil
import tarfile

HERE=Path(__file__).resolve().parent
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
UPSTREAM=MAIN/'baseline_selection_20260929/OnlineGGO'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

archive=HERE/'native_evidence.tar.gz'
assert not archive.exists()
roots={'attempt01':MAIN/'onlineggo_training_20260930_r3',
       'attempt02':MAIN/'onlineggo_training_20260930_r3_attempt02'}
manifest={};omitted_checkpoints={};empty_attempt01=[]
with archive.open('wb') as out,gzip.GzipFile(filename='',mode='wb',fileobj=out,mtime=0) as gz,tarfile.open(fileobj=gz,mode='w') as tar:
    for prefix,root in roots.items():
        for p in sorted(root.rglob('*')):
            if p.is_dir():
                if prefix=='attempt01' and p.name.startswith('g') and not list(p.iterdir()):empty_attempt01.append(str(p.relative_to(root)))
                continue
            name=prefix+'/'+str(p.relative_to(root))
            if p.suffix=='.pickle':
                omitted_checkpoints[name]={'sha256':sha(p),'bytes':p.stat().st_size,'local_only':True}
                continue
            data=p.read_bytes();info=tarfile.TarInfo(name);info.size=len(data);info.mtime=0;info.mode=0o644
            tar.addfile(info,io.BytesIO(data));manifest[name]={'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
source=HERE/'upstream_context';source.mkdir(exist_ok=False)
freeze=json.loads((HERE/'training_02/freeze.json').read_text())
for path in freeze['official_sources']:
    dest=source/path;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(UPSTREAM/'CMAES'/path,dest)
for name,path in [('sortation_small_kiva.map',UPSTREAM/'Guided-PIBT/guided-pibt/benchmark-lifelong/maps/sortation_small_kiva.map'),
                  ('UPSTREAM_LICENSE.txt',UPSTREAM/'LICENSE')]:
    shutil.copyfile(path,source/name)
result={'native_archive_sha256':sha(archive),'native_archive_bytes':archive.stat().st_size,
        'native_files':manifest,'attempt01_pre_job_failures':empty_attempt01,
        'local_optimizer_checkpoints':omitted_checkpoints,
        'upstream_context':{str(p.relative_to(source)):sha(p) for p in source.rglob('*') if p.is_file()}}
(HERE/'native_archive_manifest.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({'archive_bytes':archive.stat().st_size,'native_files':len(manifest),
                  'attempt01_pre_job_failures':len(empty_attempt01)}))
