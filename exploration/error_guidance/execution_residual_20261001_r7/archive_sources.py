from pathlib import Path
import hashlib,json,tarfile
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 target=HERE/'reproduction_sources.tar.gz';assert not target.exists()
 excluded={'raw_archives','__pycache__','reproduction_sources.tar.gz','source_archive_manifest.json'}
 files=[p for p in HERE.rglob('*') if p.is_file() and not any(x in excluded for x in p.relative_to(HERE).parts)]
 assert (HERE/'REPORT.md') in files and (HERE/'ROOT_MODEL_AUDIT.json') in files and (HERE/'root_model_audit.py') in files
 members={str(p.relative_to(HERE)):sha(p) for p in sorted(files)}
 with tarfile.open(target,'w:gz',compresslevel=6) as tf:
  for p in sorted(files):tf.add(p,arcname=str(p.relative_to(HERE)),recursive=False)
 assert target.stat().st_size<90_000_000
 with tarfile.open(target,'r:gz') as tf:
  assert set(tf.getnames())==set(members)
  for m in tf:assert hashlib.sha256(tf.extractfile(m).read()).hexdigest()==members[m.name]
 (HERE/'source_archive_manifest.json').write_text(json.dumps({'archive':target.name,'archive_sha256':sha(target),'archive_bytes':target.stat().st_size,'members':members,'roundtrip_passed':True},indent=2)+'\n')
 print('source bundle',len(members),target.stat().st_size)
if __name__=='__main__':main()
