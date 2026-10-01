from pathlib import Path
import json
import runner
P=runner.HERE
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text())
 for name,h in reg['frozen'].items():assert runner.sha(P/name)==h,'changed registered source '+name
 assert runner.sha(runner.BRIDGE)==reg['bridge_sha256'] and runner.sha(runner.CONFIG)==reg['config_sha256']
 successor=P/'scale_guard_successor';sr=json.loads((successor/'REGISTRATION.json').read_text())
 for name,h in sr['frozen'].items():assert runner.sha(successor/name)==h
 assert (successor/'joint_history_native.cpp').read_text()==(P/'joint_history_native.cpp').read_text().replace('robots.size()<=16','robots.size()<=32')
 assert runner.sha(P/'MODELS_FROZEN_BEFORE_TEST.json')==sr['parent_model_sha256']
 old=P.parent/'online_fifo_20261001_r7';manifest=json.loads((old/'FROZEN_MANIFEST.json').read_text())
 for name,item in manifest['frozen_files'].items():assert runner.sha(old/name)==item['sha256']
 pins=json.loads((P.parent/'legal_and_sources.json').read_text())
 for name,h in pins.items():assert runner.sha(runner.MAIN/name)==h
 fixture_pin=json.loads((P.parent/'legal_and_run_20260924_01.json').read_text())['fixture_sha256'];assert runner.sha(P.parent/'legal_and_fixture.cpp')==fixture_pin
 author=json.loads((old/'AUTHOR_PROVENANCE.json').read_text())
 for name,h in author['official_objects'].items():assert runner.sha(name)==h
 assert runner.sha(author['source_wrapper'])==author['wrapper_sha256']
 author['public_source_inputs']={str(p):runner.sha(p) for mapname in ['empty-32-32','random-32-32-10'] for p in [runner.THIRD/'inputs'/mapname/(mapname+'.map'),runner.THIRD/'inputs'/mapname/(mapname+'-random-1.scen')]}
 runner.write(P/'AUTHOR_PROVENANCE.json',author)
 runner.write(P/'PARENT_PINS_VERIFIED.json',dict(R7_frozen_files=len(manifest['frozen_files']),R7_manifest_sha256=runner.sha(old/'FROZEN_MANIFEST.json'),production_headers=len(pins),legal_fixture_original_retained_pin=fixture_pin,official_objects=len(author['official_objects']),all_unchanged=True))
 for f in P.rglob('*'):
  if not f.is_file() or any(x in {'runs','audits','build','__pycache__'} for x in f.relative_to(P).parts):continue
  if f.suffix in ['.py','.cpp','.md','.json','.csv']:
   assert b'\r' not in f.read_bytes(),'non-LF new text '+f.name
 required=['ROOT_HELDOUT_AUDIT.json','ROOT_COMPLETE_AUDIT.json','ROOT_FIGURE_CAPTION.md','AUDIT_ALL.json','MODEL_LABEL_AUDIT.json','NEGATIVE_CONTROLS.json','REPORT.md','README.md','RAW_ARCHIVE_MANIFEST.json','RECEIPT.json','scale_guard_successor/AUDIT_ALL.json','scale_guard_successor/RECEIPT.json']
 assert all((P/f).is_file() for f in required)
 members=sorted(str(p.relative_to(P)) for p in P.rglob('*') if p.is_file() and p.name not in ['PUBLICATION_MEMBERS.json','FROZEN_MANIFEST.json'] and not any(x in {'runs','audits','build','__pycache__'} for x in p.relative_to(P).parts))+['PUBLICATION_MEMBERS.json','FROZEN_MANIFEST.json']
 runner.write(P/'PUBLICATION_MEMBERS.json',dict(files=members,exclude=['**/runs/','**/audits/','**/build/','**/__pycache__/'],raw_archived_once=True))
 frozen={name:dict(sha256=runner.sha(P/name),bytes=(P/name).stat().st_size) for name in members if name!='FROZEN_MANIFEST.json'}
 runner.write(P/'FROZEN_MANIFEST.json',dict(frozen_files=frozen,frozen_count=len(frozen),public_members=len(members),original_attempt_receipt=json.loads((P/'RECEIPT.json').read_text()),scale_successor_receipt=json.loads((successor/'RECEIPT.json').read_text()),all_registered_sources_unchanged=True,R7_frozen_files_unchanged=True,production_COST=False,not_portable_without_pinned_external_dependencies=True))
 print('FROZEN',len(frozen),'files',flush=True)
if __name__=='__main__':main()
