from pathlib import Path
import hashlib,json,tarfile
import runner
HERE=runner.HERE
def main():
 manifests={}
 for label,dirs in [('mechanical',['mechanical_attempt_01','mechanical_attempt_02','build']),('statistical',['statistical_attempt_01'])]:
  files=sorted(p for d in dirs for p in (HERE/d).rglob('*') if p.is_file() and '__pycache__' not in p.parts);members={str(p.relative_to(HERE)):dict(sha256=runner.sha(p),bytes=p.stat().st_size) for p in files};target=HERE/('RAW_R7_'+label.upper()+'.tar.gz')
  assert not target.exists()
  with tarfile.open(target,'w:gz',compresslevel=6) as tar:
   for p in files:tar.add(p,arcname=str(p.relative_to(HERE)),recursive=False)
  with tarfile.open(target,'r:gz') as tar:
   assert {x.name for x in tar.getmembers()}==set(members)
   for m in tar.getmembers():
    data=tar.extractfile(m).read();assert len(data)==members[m.name]['bytes'] and hashlib.sha256(data).hexdigest()==members[m.name]['sha256']
  manifests[target.name]=dict(sha256=runner.sha(target),compressed_bytes=target.stat().st_size,uncompressed_bytes=sum(v['bytes'] for v in members.values()),members=members)
 runner.write(HERE/'RAW_ARCHIVE_MANIFEST.json',dict(archives=manifests,all_members_verified=True,single_copy_no_raw_duplication=True));print({k:{x:v[x] for x in ['compressed_bytes','uncompressed_bytes']} for k,v in manifests.items()},flush=True)
if __name__=='__main__':main()
