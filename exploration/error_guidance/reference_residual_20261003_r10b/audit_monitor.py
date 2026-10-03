from pathlib import Path
import json,traceback,time
import audit
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
(H/'per_run_audits').mkdir(exist_ok=True)
for s in json.loads((H/'runs.json').read_text())['runs']:
 if s['split']!='test' or not (O/'runs'/s['id']/'receipt.json').exists():continue
 out=H/'per_run_audits'/(s['id']+'.json')
 if out.exists():continue
 try:r=audit.check(s)
 except Exception:r={'passed':False,'error':traceback.format_exc()}
 out.write_text(json.dumps(r,indent=2)+'\n');print(s['id'],r.get('normal_station_END'),r['passed'],r.get('error',''),flush=True)
