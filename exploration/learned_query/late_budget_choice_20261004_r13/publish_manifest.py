"""Reviewable final whitelist; root owns publication and all Git operations."""
import json
import runner
P=runner.HERE
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());freeze=json.loads((P/'MODEL_FREEZE_RECEIPT.json').read_text())
 for name,digest in reg['frozen'].items():assert runner.sha(P/name)==digest,('registered core changed',name)
 assert freeze['model_sha256']==runner.sha(P/'MODELS_FROZEN_BEFORE_TEST.json') and freeze['labels_sha256']==runner.sha(P/'TRAIN_CAL_LABELS.json')
 for name in ['SOURCE_DELTA_AUDIT.json','PARENT_PINS_VERIFIED.json','PREFIX_BEFORE_FIT.json','AUDIT_ALL.json','DEPLOYMENT_AUDIT.json','NEGATIVE_CONTROLS.json','SKIP_LIFETIMES.json','RAW_ARCHIVE_MANIFEST.json','ROOT_MACRO_AUDIT.json','MENTOR_MODEL_AUDIT.json','OFFLINE_REPLAY_RECEIPT.json','ROOT_TEST_RESULTS.json','ROOT_MODEL_DIAGNOSTICS.json']:
  result=json.loads((P/name).read_text());assert result.get('passed') is True,('audit not passed',name)
 assert json.loads((P/'RECEIPT.json').read_text())['native_episodes']==160
 assert all((P/name).is_file() for name in ['REPORT.md','HANDOFF.md','SUMMARY.json','RESULTS.csv','FAMILY_RESULTS.json','BUDGET_RESULTS.json','root_macro_audit.py','mentor_model_audit.py','ROOT_CONCLUSION.md','ASTRA_POSTEXEC_20261004_R13.md','MENTOR_POSTEXEC_20261004_R13.md','REVIEW_PROVENANCE.json','figures/CAPTION.md','figures/r13_test_comparison.pdf','figures/r13_test_comparison.svg','figures/r13_test_comparison.png'])
 assert 'pending' not in (P/'REPORT.md').read_text()
 ignored={'runs','audits','build','__pycache__'};excluded={'PUBLICATION_MEMBERS.json','FROZEN_MANIFEST.json','ROOT_MACRO_PARTIAL.json'}
 members=sorted(str(p.relative_to(P)) for p in P.rglob('*') if p.is_file() and not ignored.intersection(p.relative_to(P).parts) and p.name not in excluded)
 runner.write(P/'PUBLICATION_MEMBERS.json',dict(files=members+['PUBLICATION_MEMBERS.json','FROZEN_MANIFEST.json'],exclude=['runs/**','audits/**','build/**','__pycache__/**','ROOT_MACRO_PARTIAL.json'],raw_archived_once=True,git_mutation_performed=False))
 pins={name:dict(bytes=(P/name).stat().st_size,sha256=runner.sha(P/name)) for name in members}
 runner.write(P/'FROZEN_MANIFEST.json',dict(frozen_files=pins,source_registration_sha256=runner.sha(P/'REGISTRATION.json'),model_sha256=freeze['model_sha256'],model_freeze_receipt_sha256=runner.sha(P/'MODEL_FREEZE_RECEIPT.json'),native_episodes=160,independent_TEST_families=8,paired_budgets=[8,16],production_COST=False,not_portable_without_pinned_external_dependencies=True,publication_by_root_pending=True))
 print('publication whitelist',len(members)+2,'files',flush=True)
if __name__=='__main__':main()
