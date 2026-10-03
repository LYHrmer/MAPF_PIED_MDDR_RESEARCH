from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;R=H.parent/'local_dependency_20261001_r8'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pins=json.loads((R/'freeze.json').read_text())['pins']
for p in [H/'public_model.py',H/'mapping_replay.py',H/'run_trial.py',H/'prepare.py',H/'run_matrix.py',H/'fit_model.py',H/'PROTOCOL.md',H/'model_freeze.json',H/'training_rows.json',H/'runs.json',*H.glob('inputs/*/*'),*H.glob('configs/*.json'),*H.glob('xml/*.argos')]:pins[str(p)]=sha(p)
assert not (H/'freeze.json').exists()
(H/'freeze.json').write_text(json.dumps({'pins':pins,'inherited_R8_freeze_sha256':sha(R/'freeze.json'),'native_changes':[]},indent=2)+'\n');print('frozen',len(pins))
