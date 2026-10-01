"""Run every predefined arm once, preserving failures and raw output."""
from pathlib import Path
import subprocess,sys,json,time
HERE=Path(__file__).resolve().parent;OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/HERE.name
results=[]
for spec in json.loads((HERE/'runs.json').read_text())['runs']:
 path=OUT/'runs'/spec['id']
 if (path/'receipt.json').exists():
  r=json.loads((path/'receipt.json').read_text());results.append({'id':spec['id'],'previous_record_retained':True,'error':r['error']});continue
 start=time.monotonic();p=subprocess.run(['rtk','proxy','timeout','--kill-after=5s','130s',sys.executable,str(HERE/'run_trial.py'),spec['id']])
 results.append({'id':spec['id'],'returncode':p.returncode,'wall_seconds':time.monotonic()-start})
 (HERE/'matrix_results.json').write_text(json.dumps(results,indent=2)+'\n')
print('matrix finished',len(results),flush=True)
