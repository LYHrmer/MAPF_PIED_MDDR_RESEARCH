from pathlib import Path
import json,subprocess,sys
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
for receipt in (O/'runs').glob('*/receipt.json'):
    r=json.loads(receipt.read_text())
    if r['error']:
        assert r['decisions']==0 and 'Operation not permitted' in r['error']
        dest=O/'sandbox_attempt01'/receipt.parent.name;dest.parent.mkdir(exist_ok=True);assert not dest.exists();receipt.parent.rename(dest)
raise SystemExit(subprocess.run(['rtk','proxy','python3',str(H/'run_matrix.py'),sys.argv[1]]).returncode)
