"""Freeze explicit reviewable whitelist after independent checks; no Git mutation."""
import json
import runner
P=runner.HERE
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());fix=json.loads((P/'AUDITOR_IMPORT_FIX_BEFORE_PROBES.json').read_text())
 for name,digest in reg['frozen'].items():
  if name==fix['file']:
   assert digest==fix['before_sha256'] and fix['branch_outcomes_seen']==0 and not fix['scientific_policy_source_changed'];digest=fix['after_sha256']
  assert runner.sha(P/name)==digest,'registered source changed '+name
 for path,digest in [(P/'build/joint_history_native',reg['binary_sha256']),(runner.BRIDGE,reg['bridge_sha256']),(runner.CONFIG,reg['config_sha256'])]:assert runner.sha(path)==digest
 for name in ['AUDIT_ALL.json','MATCHED_TAIL_AUDIT.json','NEGATIVE_CONTROLS.json','SKIP_LIFETIMES.json','RAW_ARCHIVE_MANIFEST.json','ROOT_VALUE_SPACE.json','ROOT_RECONCILIATION.json','FINAL_PINS_VERIFIED.json']:assert json.loads((P/name).read_text())['passed']
 reconciled=json.loads((P/'ROOT_RECONCILIATION.json').read_text());assert reconciled['root_result_sha256']==runner.sha(P/'ROOT_VALUE_SPACE.json') and reconciled['root_script_sha256']==runner.sha(P/'root_value_space.py')
 assert all((P/name).is_file() for name in ['REPORT.md','HANDOFF.md','RESULTS.csv','RESULTS.json','SUMMARY.json','root_value_space.py'])
 ignored={'runs','audits','build','__pycache__'};excluded={'PUBLICATION_MEMBERS.json','FROZEN_MANIFEST.json'}
 members=sorted(str(p.relative_to(P)) for p in P.rglob('*') if p.is_file() and not ignored.intersection(p.relative_to(P).parts) and p.name not in excluded)
 runner.write(P/'PUBLICATION_MEMBERS.json',dict(files=members+['PUBLICATION_MEMBERS.json','FROZEN_MANIFEST.json'],exclude=['runs/**','audits/**','build/**','__pycache__/**'],raw_archived_once=True,git_mutation_performed=False))
 frozen={name:dict(bytes=(P/name).stat().st_size,sha256=runner.sha(P/name)) for name in members+['PUBLICATION_MEMBERS.json']}
 runner.write(P/'FROZEN_MANIFEST.json',dict(frozen_files=frozen,source_registration_sha256=runner.sha(P/'REGISTRATION.json'),auditor_import_correction_sha256=runner.sha(P/'AUDITOR_IMPORT_FIX_BEFORE_PROBES.json'),native_episodes=json.loads((P/'RECEIPT.json').read_text())['native_episodes'],TRAIN_only=True,production_COST=False,not_portable_without_pinned_external_dependencies=True,publication_by_root_pending=True))
 print('publication whitelist',len(members)+2,'files',flush=True)
if __name__=='__main__':main()
