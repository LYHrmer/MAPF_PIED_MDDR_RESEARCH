"""Explicit reviewable publication whitelist; no staging or Git mutation."""
from pathlib import Path
import json,time
import runner
P=runner.HERE
def main():
 assert json.loads((P/'COMPLETION_RECEIPT.json').read_text())['complete']
 archives=json.loads((P/'RAW_ARCHIVE_MANIFEST.json').read_text())
 for part in archives['parts']:assert runner.sha(P/part['path'])==part['sha256']
 files=[]
 for p in sorted(P.iterdir()):
  if not p.is_file() or p.name.startswith(('ROOT_','PUBLICATION_MANIFEST')):continue
  if p.suffix in ['.py','.cpp','.md','.json','.csv','.patch'] or p.name.endswith('.tar.gz'):files.append(p)
 files.extend(sorted((P/'build').glob('compile*.json')))
 assert all(p.stat().st_size<45_000_000 for p in files)
 runner.write(P/'PUBLICATION_MANIFEST.json',dict(created_unix_ns=time.time_ns(),status='ready_for_root_review_not_committed',files=[dict(path=str(p.relative_to(P)),sha256=runner.sha(p),bytes=p.stat().st_size) for p in files],raw_archives_cover_all_new_native=True,new_native_archived=archives['new_native'],old_C_LD_not_repacked=True,old_source_and_gate_references=['REGISTRATION.json','CAL_ALIAS_REGISTRATION.json','ARM_HASHES.json'],excluded=['runs/ expanded files (fully archived)','audits/ expanded files (fully archived)','build/joint_history_native (rebuild from pinned source)','__pycache__/','ROOT_* (root owns publication)']))
 print('publication manifest',len(files),'files',flush=True)
if __name__=='__main__':main()
