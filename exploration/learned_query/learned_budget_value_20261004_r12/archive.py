from pathlib import Path
import json,tarfile
import runner
P=runner.HERE
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());splits={w['name']:w['split'] for w in reg['worlds']};receipts=sorted((P/'runs').glob('*.receipt.json'));archives=[];seen=set()
 for label in ['TRAIN_CAL','TEST']:
  chosen=[p for p in receipts if (splits[json.loads(p.read_text())['world']]=='test')==(label=='TEST')]
  for i in range(0,len(chosen),20):
   name=f'RAW_R12_{label}_{i//20+1:02d}.tar.gz';members=[]
   for r in chosen[i:i+20]:
    stem=r.name.removesuffix('.receipt.json')
    for p in sorted((P/'runs').glob(stem+'.*')):
     rel=str(p.relative_to(P));assert rel not in seen;seen.add(rel);members.append(dict(path=rel,bytes=p.stat().st_size,sha256=runner.sha(p)))
   with tarfile.open(P/name,'w:gz',compresslevel=6) as tar:
    for m in members:tar.add(P/m['path'],arcname=m['path'],recursive=False)
   size=(P/name).stat().st_size;assert size<45_000_000,(name,size)
   with tarfile.open(P/name,'r:gz') as tar:
    import hashlib
    for m in members:assert hashlib.sha256(tar.extractfile(m['path']).read()).hexdigest()==m['sha256']
   archives.append(dict(path=name,bytes=size,sha256=runner.sha(P/name),episodes=len(chosen[i:i+20]),members=members));print(name,size,flush=True)
 assert seen=={str(p.relative_to(P)) for p in (P/'runs').iterdir() if p.is_file()}
 runner.write(P/'RAW_ARCHIVE_MANIFEST.json',dict(passed=True,raw_member_count=len(seen),raw_archived_once=True,archives=archives))
if __name__=='__main__':main()
