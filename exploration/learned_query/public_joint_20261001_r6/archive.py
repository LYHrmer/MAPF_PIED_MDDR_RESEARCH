from pathlib import Path
import hashlib,json,tarfile,gzip
HERE=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 groups={}
 for attempt in ['mechanical_attempt_01','mechanical_attempt_02']:
  groups['RAW_R6_'+attempt+'.tar.gz']=sorted(p for p in (HERE/attempt).rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 out=HERE/'native_attempt_01';members=sorted(p for p in out.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
 for i in range(6):groups[f'RAW_R6_GROUP_{i:02d}.tar.gz']=[p for p in members if p.name.startswith(f'group_{i:02d}__')]
 groups['RAW_R6_NATIVE_META.tar.gz']=[p for p in members if not p.name.startswith('group_')]
 groups['RAW_R6_GEOMETRY_BINARY.tar.gz']=[HERE/'geometry_differential']
 manifest={};total_members=0
 for name,files in groups.items():
  path=HERE/name;assert not path.exists();entries=[]
  with path.open('wb') as base,gzip.GzipFile(filename='',mode='wb',fileobj=base,mtime=0,compresslevel=6) as gz,tarfile.open(fileobj=gz,mode='w') as tar:
   for p in files:
    arc=str(p.relative_to(HERE));info=tar.gettarinfo(str(p),arcname=arc);info.uid=info.gid=0;info.uname=info.gname='';info.mtime=0
    with p.open('rb') as f:tar.addfile(info,f)
    entries.append(dict(path=arc,bytes=p.stat().st_size,sha256=sha(p)))
  assert path.stat().st_size<80_000_000
  with tarfile.open(path,'r:gz') as tar:
   assert len(tar.getmembers())==len(entries)
   for r in entries:assert hashlib.sha256(tar.extractfile(r['path']).read()).hexdigest()==r['sha256']
  manifest[name]=dict(bytes=path.stat().st_size,sha256=sha(path),members=entries,roundtrip_verified=True);total_members+=len(entries);print('ARCHIVE',name,len(entries),path.stat().st_size,flush=True)
 (HERE/'RAW_ARCHIVE_MANIFEST.json').write_text(json.dumps(dict(archives=manifest,total_members=total_members,originals_retained_locally=True,cache_excluded=True,all_roundtrip_hashes_verified=True),indent=2)+'\n');(HERE/'ARCHIVE_VERIFIED.json').write_text(json.dumps(dict(passed=True,archive_count=len(manifest),member_count=total_members,archive_bytes=sum(x['bytes'] for x in manifest.values()),source_sha256=sha(Path(__file__)),all_member_hashes_match=True),indent=2)+'\n')
if __name__=='__main__':main()
