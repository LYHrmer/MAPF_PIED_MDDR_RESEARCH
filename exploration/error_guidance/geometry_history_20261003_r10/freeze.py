from pathlib import Path
import hashlib,json,datetime
H=Path(__file__).resolve().parent;R=H.parent/'primitive_duration_20261003_r9'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pins=json.loads((R/'freeze.json').read_text())['pins']
for p in [R/'freeze.json',R/'training_rows.json',R/'model_freeze.json',*H.glob('*.py'),H/'PROTOCOL.md',H/'model_freeze.json',H/'runs.json',*H.glob('inputs/*/*'),*H.glob('configs/*.json'),*H.glob('xml/*.argos')]:pins[str(p)]=sha(p)
assert not (H/'freeze.json').exists()
(H/'freeze.json').write_text(json.dumps({'pins':pins,'inherited_R9_freeze_sha256':sha(R/'freeze.json'),'native_changes':[],'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat()},indent=2)+'\n')
print('frozen',len(pins))
