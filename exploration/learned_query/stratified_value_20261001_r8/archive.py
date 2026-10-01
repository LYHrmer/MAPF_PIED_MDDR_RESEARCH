from pathlib import Path
import tarfile,json,sys
import runner
P=runner.HERE
def main():
 archives=[]
 train_only=sys.argv[1:]==['train']
 for heldout in ([False] if train_only else [False,True]):
  members=[]
  candidates=list((P/'runs').iterdir())+list((P/'scale_guard_successor/runs').iterdir())
  for p in sorted(candidates):
   if p.is_file() and ('_test_' in p.name or '_scale_' in p.name)==heldout:members.append(dict(path=str(p.relative_to(P)),bytes=p.stat().st_size,sha256=runner.sha(p)))
  target=P/('RAW_R8_TEST_SCALE.tar.gz' if heldout else 'RAW_R8_TRAIN_CAL.tar.gz')
  if not target.exists():
   with tarfile.open(target,'x:gz',compresslevel=6) as tf:
    for row in members:tf.add(P/row['path'],arcname=row['path'],recursive=False)
  with tarfile.open(target,'r:gz') as tf:
   for row in members:
    import hashlib
    assert hashlib.sha256(tf.extractfile(row['path']).read()).hexdigest()==row['sha256']
  archives.append(dict(archive=target.name,sha256=runner.sha(target),bytes=target.stat().st_size,members=members,verified_every_member=True))
  print('archive verified',len(members),'members',target.stat().st_size,flush=True)
 if not train_only:runner.write(P/'RAW_ARCHIVE_MANIFEST.json',dict(archives=archives,all_verified=True))
if __name__=='__main__':main()
