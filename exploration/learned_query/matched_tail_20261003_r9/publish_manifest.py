"""Finalize the reviewable worker package; no Git mutation or external publication."""
from pathlib import Path
import json
import runner
P=runner.HERE
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text())
 for path,digest in reg['frozen'].items():assert runner.sha(P/path)==digest,'registered source changed '+path
 for path,digest in [(runner.BRIDGE,reg['bridge_sha256']),(runner.CONFIG,reg['config_sha256'])]:assert runner.sha(path)==digest
 assert runner.sha(P/'MODELS_FROZEN_BEFORE_TEST.json')==json.loads((P/'MODEL_FREEZE_RECEIPT.json').read_text())['model_sha256']
 for name in ['AUDIT_ALL.json','MATCHED_TAIL_MODEL_AUDIT.json','NEGATIVE_CONTROLS.json','RAW_ARCHIVE_MANIFEST.json']:assert json.loads((P/name).read_text())['passed']
 required=['REPORT.md','HANDOFF.md','RESULTS.csv','SUMMARY.json','ROOT_REFIT.json','ROOT_HELDOUT.json','root_refit.py','root_heldout.py']
 assert all((P/name).is_file() for name in required),'root audit/report still pending'
 ignored={'runs','audits','build','__pycache__'}
 members=sorted(str(p.relative_to(P)) for p in P.rglob('*') if p.is_file() and not ignored.intersection(p.relative_to(P).parts) and p.name not in ['PUBLICATION_MEMBERS.json','FROZEN_MANIFEST.json'])
 runner.write(P/'PUBLICATION_MEMBERS.json',dict(files=members+['PUBLICATION_MEMBERS.json','FROZEN_MANIFEST.json'],exclude=['runs/**','audits/**','build/**','__pycache__/**'],raw_archived_once=True,git_mutation_performed=False))
 frozen={name:dict(bytes=(P/name).stat().st_size,sha256=runner.sha(P/name)) for name in members+['PUBLICATION_MEMBERS.json']}
 runner.write(P/'FROZEN_MANIFEST.json',dict(frozen_files=frozen,source_registration_sha256=runner.sha(P/'REGISTRATION.json'),model_sha256=runner.sha(P/'MODELS_FROZEN_BEFORE_TEST.json'),native_episodes=json.loads((P/'RECEIPT.json').read_text())['native_episodes'],all_registered_sources_unchanged=True,production_COST=False,not_portable_without_pinned_external_dependencies=True,publication_by_root_pending=True))
 print('publication whitelist',len(members)+2,'files; original registered sources unchanged',flush=True)
if __name__=='__main__':main()
