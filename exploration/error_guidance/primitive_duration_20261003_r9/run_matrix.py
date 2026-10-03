from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,sys
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
split=sys.argv[1];runs=[s for s in json.loads((H/'runs.json').read_text())['runs'] if s['split']==split]
def run(s):
 p=O/'runs'/s['id']/'receipt.json'
 if p.exists():
  assert json.loads(p.read_text())['error'] is None,s['id'];return
 r=subprocess.run(['rtk','proxy','python3',str(H/'run_trial.py'),s['id']],capture_output=True,text=True);print(r.stdout.strip(),flush=True);assert r.returncode==0,r.stderr
with ThreadPoolExecutor(max_workers=2) as pool:list(pool.map(run,runs))
