"""All normal/failure native bytes, archives each <90 MB, member SHA round trip."""
from pathlib import Path
from collections import defaultdict
import hashlib,json,tarfile
HERE=Path(__file__).resolve().parent;OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/HERE.name
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 groups=defaultdict(list)
 for spec in json.loads((HERE/'runs.json').read_text())['runs']:
  key=f'{spec["split"]}_{spec["map"]}_{spec["seed"]}_{spec["condition"]}'
  groups[key].extend(p for p in (OUT/'runs'/spec['id']).rglob('*') if p.is_file())
 groups['sandbox_denied_attempts']=[p for p in (OUT/'sandbox_denied_runs').rglob('*') if p.is_file()]
 groups['candidate_native_build']=[OUT/'bridge_candidate',OUT/'search_overlay.o']
 dst=HERE/'raw_archives';dst.mkdir(exist_ok=True);man={};count=0;raw_bytes=0
 for key,files in groups.items():
  target=dst/(key+'.tar.gz');assert not target.exists()
  members={str(p.relative_to(OUT)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(files)}
  with tarfile.open(target,'w:gz',compresslevel=6) as tf:
   for p in sorted(files):tf.add(p,arcname=str(p.relative_to(OUT)),recursive=False)
  assert target.stat().st_size<90_000_000,(target,target.stat().st_size)
  with tarfile.open(target,'r:gz') as tf:
   assert set(tf.getnames())==set(members)
   for m in tf:
    h=hashlib.sha256();reader=tf.extractfile(m)
    for b in iter(lambda:reader.read(1<<20),b''):h.update(b)
    assert h.hexdigest()==members[m.name]['sha256']
  man[target.name]={'archive_sha256':sha(target),'archive_bytes':target.stat().st_size,'members':members}
  count+=len(members);raw_bytes+=sum(v['bytes'] for v in members.values());print(target.name,len(members),target.stat().st_size,flush=True)
 (HERE/'archive_manifest.json').write_text(json.dumps({'archives':man,'file_count':count,'raw_bytes':raw_bytes,'archive_bytes':sum(v['archive_bytes'] for v in man.values()),'all_members_roundtrip_verified':True},indent=2)+'\n')
if __name__=='__main__':main()
