from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,sys
HERE=Path(__file__).resolve().parent
phase=sys.argv[1];runs=[r for r in json.loads((HERE/'runs.json').read_text())['runs'] if (r['split']=='test')==(phase=='test')]
def run(r):
 p=subprocess.run(['rtk','proxy',sys.executable,str(HERE/'run_trial.py'),r['id']],capture_output=True,text=True)
 print(p.stdout,p.stderr,flush=True);return {'run':r['id'],'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
with ThreadPoolExecutor(max_workers=2) as pool:receipts=list(pool.map(run,runs))
(HERE/f'matrix_{phase}.json').write_text(json.dumps(receipts,indent=2)+'\n')
raise SystemExit(int(any(r['exit_code'] for r in receipts)))
