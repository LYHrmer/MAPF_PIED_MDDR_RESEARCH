from pathlib import Path
import hashlib,json,tarfile,sys
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name;A=H/'raw_archives';A.mkdir(exist_ok=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
allfiles={};archives=[]
for group in ['runs','sandbox_attempt01']:
 for d in sorted((O/group).glob('*')):
  if not (d/'receipt.json').exists():continue
  files=sorted(p for p in d.rglob('*') if p.is_file());relname=group+'__'+d.name+'.tar.gz';dst=A/relname
  members={str(p.relative_to(O)):{'sha256':sha(p),'bytes':p.stat().st_size} for p in files};allfiles.update(members)
  if not dst.exists():
   with tarfile.open(dst,'w:gz',compresslevel=6) as t:
    for p in files:t.add(p,arcname=str(p.relative_to(O)),recursive=False)
  with tarfile.open(dst,'r:gz') as t:
   checked={}
   for m in t.getmembers():
    if m.isfile():checked[m.name]={'sha256':hashlib.sha256(t.extractfile(m).read()).hexdigest(),'bytes':m.size}
  assert checked==members
  archives.append({'path':str(dst.relative_to(H)),'sha256':sha(dst),'bytes':dst.stat().st_size,'members':members})
print('verified archives',len(archives),flush=True)
(H/'archive_manifest.json').write_text(json.dumps({'archives':archives,'total_raw_bytes':sum(x['bytes'] for x in allfiles.values()),'total_archive_bytes':sum(x['bytes'] for x in archives),'all_member_sha256_verified':True},indent=2)+'\n')
