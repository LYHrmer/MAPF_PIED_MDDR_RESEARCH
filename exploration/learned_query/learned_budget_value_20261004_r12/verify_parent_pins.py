"""Verify preserved frozen predecessors and original source dependencies."""
from pathlib import Path
import json
import runner
P=runner.HERE
def main():
 previous=P.parent/'public_opportunity_20261003_r11';old=json.loads((previous/'PARENT_PINS_VERIFIED.json').read_text());names=list(old['parents'])+['public_opportunity_20261003_r11'];result={}
 for name in names:
  parent=P.parent/name;manifest=parent/'FROZEN_MANIFEST.json';m=json.loads(manifest.read_text())
  for relative,entry in m['frozen_files'].items():assert runner.sha(parent/relative)==entry['sha256'],(name,relative)
  if name in old['parents']:assert runner.sha(manifest)==old['parents'][name]['manifest_sha256']
  result[name]=dict(manifest_sha256=runner.sha(manifest),files=len(m['frozen_files']))
 for relative,digest in old['production_headers'].items():assert runner.sha(runner.MAIN/relative)==digest
 assert runner.sha(P.parent/'legal_and_fixture.cpp')==old['legal_fixture_sha256']
 runner.write(P/'PARENT_PINS_VERIFIED.json',dict(passed=True,parents=result,production_headers=old['production_headers'],legal_fixture_sha256=old['legal_fixture_sha256']))
 print('all predecessor and original dependency hashes PASS',flush=True)
if __name__=='__main__':main()
