"""Check source hashes, preserved ancestors and local registration file ordering."""
import json
import runner
P=runner.HERE
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());old=json.loads((P/'PARENT_PINS_VERIFIED.json').read_text());fix=json.loads((P/'AUDITOR_IMPORT_FIX_BEFORE_PROBES.json').read_text());parents={}
 for name,entry in old['parents'].items():
  path=P.parent/name/'FROZEN_MANIFEST.json';assert runner.sha(path)==entry['manifest_sha256'];manifest=json.loads(path.read_text())
  for relative,pin in manifest['frozen_files'].items():assert runner.sha(path.parent/relative)==pin['sha256'],(name,relative)
  parents[name]=dict(files=len(manifest['frozen_files']),manifest_sha256=runner.sha(path))
 for name,digest in old['production_headers'].items():assert runner.sha(runner.MAIN/name)==digest
 for name,digest in reg['frozen'].items():
  if name==fix['file']:assert digest==fix['before_sha256'];digest=fix['after_sha256']
  assert runner.sha(P/name)==digest
 for path,digest in [(P/'build/joint_history_native',reg['binary_sha256']),(runner.BRIDGE,reg['bridge_sha256']),(runner.CONFIG,reg['config_sha256'])]:assert runner.sha(path)==digest
 base=[];probes=[]
 for p in (P/'runs').glob('*.receipt.json'):
  e=json.loads(p.read_text());(base if e['policy'] in ['condition','WAIT'] else probes).append(p.stat().st_mtime)
 assert (P/'REGISTRATION.json').stat().st_mtime<min(base)
 assert (P/'BRANCHES_BEFORE_OUTCOMES.json').stat().st_mtime<min(probes)
 runner.write(P/'FINAL_PINS_VERIFIED.json',dict(passed=True,parents=parents,registered_scientific_sources_unchanged=True,auditor_import_only_recorded_exception=True,production_headers=len(old['production_headers']),binary_bridge_config_verified=True,local_file_ordering=dict(registration_mtime=(P/'REGISTRATION.json').stat().st_mtime,first_baseline_receipt_mtime=min(base),branch_registration_mtime=(P/'BRANCHES_BEFORE_OUTCOMES.json').stat().st_mtime,first_probe_receipt_mtime=min(probes)),ordering_scope='Local file timestamps corroborate pre-outcome registration; these are not trusted external timestamp signatures.'))
 print('final parent/source/input pins PASS',flush=True)
if __name__=='__main__':main()
