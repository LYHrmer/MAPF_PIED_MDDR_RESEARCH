"""Archive each new raw member once and verify extracted bytes without reruns."""
from pathlib import Path
import json,hashlib,tarfile,time
import runner
P=runner.HERE
def main():
 done=json.loads((P/'COMPLETION_RECEIPT.json').read_text());assert done['complete']
 receipts=sorted((P/'runs').glob('*.receipt.json'));parts=[];seen=set()
 for k in range(0,len(receipts),4):
  part=P/f'RAW_R16_{k//4+1:02d}.tar.gz';members=[]
  with tarfile.open(part,'x:gz',compresslevel=3) as tar:
   for receipt in receipts[k:k+4]:
    e=json.loads(receipt.read_text());stem=receipt.name.removesuffix('.receipt.json')
    paths=[receipt,Path(e['raw']),Path(e['input']),Path(e['planner']),P/'runs'/(stem+'.native.stderr'),P/'runs'/(stem+'.official.stderr'),P/'audits'/(receipt.stem+'.audit.json')]
    for p in paths:
     relative=str(p.relative_to(P));assert relative not in seen;seen.add(relative)
     members.append(dict(path=relative,sha256=runner.sha(p),bytes=p.stat().st_size));tar.add(p,arcname=relative)
  assert part.stat().st_size<45_000_000
  with tarfile.open(part) as tar:
   names=tar.getnames();assert names==[m['path'] for m in members]
   for member in members:
    f=tar.extractfile(member['path']);h=hashlib.sha256()
    for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
    assert h.hexdigest()==member['sha256']
  parts.append(dict(path=part.name,sha256=runner.sha(part),bytes=part.stat().st_size,members=members));print(part.name,part.stat().st_size,'verified',flush=True)
 runner.write(P/'RAW_ARCHIVE_MANIFEST.json',dict(parts=parts,members=len(seen),new_native=len(receipts),old_C_not_duplicated=True,verified_unix_ns=time.time_ns()))
if __name__=='__main__':main()
