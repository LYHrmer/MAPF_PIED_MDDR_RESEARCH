from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
pins=json.loads((H/'binary_manifest.json').read_text())
for p in [*H.glob('*.py'),H/'PROTOCOL.md',H/'model_freeze.json',H/'runs.json',*H.glob('*.cpp'),*H.glob('*.patch'),*H.glob('inputs/*/*'),*H.glob('configs/*.json'),*H.glob('xml/*.argos'),*list((O/'lsmart_successor').rglob('*'))]:
 if p.is_file() and '__pycache__' not in str(p):pins[str(p)]=sha(p)
(H/'freeze.json').write_text(json.dumps({'pins':pins},indent=2)+'\n');print('frozen',len(pins))
