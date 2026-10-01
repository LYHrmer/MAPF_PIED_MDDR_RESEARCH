from pathlib import Path
import json,time
import runner,audit
out=runner.HERE/'statistical_attempt_01';target=out/'test_audits';target.mkdir(exist_ok=True);source=runner.sha(Path(audit.__file__));results={}
while True:
 for p in sorted(out.glob('test*.receipt.json')):
  if p.name in results:continue
  dest=target/(p.stem+'.audit.json')
  if dest.exists():
   r=json.loads(dest.read_text());assert r['source_sha256']==source;results[p.name]=r;continue
  e=json.loads(p.read_text());assert e['error'] is None;r=audit.audit(e);r['source_sha256']=source;runner.write(dest,r);results[p.name]=r;print('test audit',p.name,flush=True)
 if (out/'RECEIPT.json').exists() and len(results)==20:break
 time.sleep(2)
assert runner.sha(Path(audit.__file__))==source
runner.write(out/'AUDIT_TEST.json',dict(status='passed',source_sha256=source,exact_features_scores=True,episodes=list(results.values())))
