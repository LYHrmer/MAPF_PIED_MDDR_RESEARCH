"""Preserve socket-sandbox denials and retry identical frozen native inputs."""
from pathlib import Path
import json,subprocess,sys
HERE=Path(__file__).resolve().parent;OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/HERE.name
if not (OUT/'sandbox_denied_runs').exists():
 for path in (OUT/'runs').glob('*/receipt.json'):
  r=json.loads(path.read_text());assert r['decisions']==0 and 'PermissionError' in r['error']
 (OUT/'runs').rename(OUT/'sandbox_denied_runs')
 (HERE/'matrix_train.json').rename(HERE/'matrix_train_sandbox_denied.json')
raise SystemExit(subprocess.call(['rtk','proxy',sys.executable,str(HERE/'run_matrix.py'),sys.argv[1]]))
