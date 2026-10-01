from pathlib import Path
import hashlib,json,sys
HERE=Path(__file__).resolve().parent
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
phase=sys.argv[1];target=HERE/f'freeze_{phase}.json';assert not target.exists()
files=[p for p in HERE.iterdir() if p.suffix in ('.py','.cpp','.md','.patch')]
files += [HERE/p for p in ['runs.json','candidate_identity.json','inherited_binary_manifest.json','inherited_freeze_pin.json']]
for d in ['inputs','configs','xml']:files += [p for p in (HERE/d).rglob('*') if p.is_file()]
if phase=='test':files.append(HERE/'model_freeze.json')
pins={str(p):sha(p) for p in files}
pins.update(json.loads((HERE/'inherited_binary_manifest.json').read_text()))
identity=json.loads((HERE/'candidate_identity.json').read_text());pins[identity['binary']]=identity['binary_sha256'];pins.update(identity['retained_original_objects'])
target.write_text(json.dumps({'phase':phase,'pins':pins},indent=2)+'\n');print(target,len(pins))
