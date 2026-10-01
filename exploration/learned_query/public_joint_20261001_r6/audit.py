from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
import json,hashlib,sys
from audit_joint_replay import Replay,sha,Fraction
HERE=Path(__file__).resolve().parent

def replay(job):
 e,w,c,models=job;assert sha(Path(e['raw']))==e['raw_sha256'] and sha(Path(e['input']))==e['input_sha256'];r=Replay(c,w,e['policy'],e['capacity']);r.coefficients={n:[Fraction(z) for z in m['coefficients']] for n,m in models.items()};v=r.run([json.loads(x) for x in Path(e['raw']).read_text().splitlines()]);return dict(world_id=e['world_id'],policy=e['policy'],raw_sha256=e['raw_sha256'],passed=True,**v)
def main():
 partial='--train-cal' in sys.argv;sup=json.loads((HERE/'SUPPORT.json').read_text());cohorts={c['cohort_id']:c for c in sup['cohorts']+sup['mechanical']};jobs=[];m=HERE/'mechanical_attempt_02';mr=json.loads((m/'RECEIPT.json').read_text());mw={w['world_id']:w for w in json.loads((m/'REGISTRATION.json').read_text())['worlds']}
 for e in mr['episodes']:jobs.append((e,mw[e['world_id']],cohorts[e['cohort_id']],{}))
 n=HERE/'native_attempt_01';nr=n/'RECEIPT.json'
 if nr.exists() or partial:
  reg=json.loads((n/'REGISTRATION.json').read_text());nw={w['world_id']:w for w in reg['worlds']};models=json.loads((n/'MODELS_FROZEN_BEFORE_TEST.json').read_text())['models']
  es=json.loads(nr.read_text())['episodes'] if nr.exists() else [json.loads(p.read_text()) for p in n.glob('*.receipt.json')]
  for e in es:
   if not partial or e['split']!='test':jobs.append((e,nw[e['world_id']],cohorts[e['cohort_id']],models))
 cache={}
 for f in [HERE/'AUDIT_MECHANICAL.json',HERE/'AUDIT_TRAIN_CAL.json']:
  if f.exists():
   old=json.loads(f.read_text());assert old['source_sha256']==sha(HERE/'audit_joint_replay.py')
   cache.update({(r['world_id'],r['policy'],r['raw_sha256']):r for r in old['rows']})
 rows=[];pending=[]
 for j in jobs:
  e=j[0];key=(e['world_id'],e['policy'],e['raw_sha256'])
  if key in cache:assert sha(Path(e['raw']))==e['raw_sha256'];rows.append(cache[key])
  else:pending.append(j)
 with ProcessPoolExecutor(max_workers=10) as pool:
  fs=[pool.submit(replay,j) for j in pending]
  for f in as_completed(fs):
   r=f.result();rows.append(r);print('AUDIT',len(rows),r['world_id'],r['policy'],flush=True)
 rows.sort(key=lambda r:(r['world_id'],r['policy']));suffix='TRAIN_CAL' if partial else 'ALL' if nr.exists() else 'MECHANICAL';p=HERE/('AUDIT_'+suffix+'.json');assert not p.exists();p.write_text(json.dumps(dict(passed=True,source_sha256=sha(HERE/'audit_joint_replay.py'),episodes=len(rows),rows=rows,frames=sum(r['frames'] for r in rows),MOVEs=sum(r['original_MOVEs'] for r in rows),END=sum(r['END_feedback'] for r in rows),queries=sum(r['queries'] for r in rows),independent_decimal_precision=70,production_geometry_controller_not_imported=True),indent=2)+'\n')
if __name__=='__main__':main()
