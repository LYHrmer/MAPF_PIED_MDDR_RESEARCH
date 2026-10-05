"""Audit only finished receipts, reusing unchanged full dependency-bound proofs."""
import sys
sys.dont_write_bytecode=True
import argparse
from collections import Counter
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import time
from audit_episode import Auditor,ROOT,BUNDLE

HERE=Path(__file__).resolve().parent


def main():
    p=argparse.ArgumentParser();p.add_argument('--root',default=str(ROOT));p.add_argument('--store');p.add_argument('--bundle',default=str(BUNDLE))
    p.add_argument('--path-map',action='append',default=[]);p.add_argument('--map');p.add_argument('--limit',type=int)
    p.add_argument('--output',default=str(HERE/'COMPLETED_AUDIT.json'));args=p.parse_args()
    root=Path(args.root);maps=dict(x.split('=',1) for x in args.path_map);memo={}
    def sha(path):
        path=Path(path);stat=path.stat();key=(str(path),stat.st_size,stat.st_mtime_ns)
        if key not in memo:memo[key]=hashlib.sha256(path.read_bytes()).hexdigest()
        return memo[key]
    auditor_hash=sha(HERE/'audit_episode.py');reports=[];new=reused=0
    receipts=sorted((root/'episodes').glob('*/*/RUN_RECEIPT.json'))
    if args.map:receipts=[r for r in receipts if r.parent.parent.name.startswith(args.map+'__')]
    if args.limit is not None:receipts=receipts[:args.limit]
    started=time.monotonic()
    for index,receipt in enumerate(receipts):
        episode=receipt.parent/'episode.json';world=receipt.parent.parent.name;arm=receipt.parent.name
        target=HERE/'episodes'/world/(arm+'.json')
        raw_receipt=json.loads(receipt.read_text())
        assert sha(episode)==raw_receipt['episode_sha256'],str(episode)
        cached=None
        if target.exists():
            old=json.loads(target.read_text())
            if old.get('passed') and old.get('episode_sha256')==sha(episode) and old.get('auditor_sha256')==auditor_hash:
                try:
                    if all(sha(path)==digest for path,digest in old['dependencies'].items()):cached=old
                except FileNotFoundError:pass
        if cached is not None:report=cached;reused+=1
        else:
            try:report=Auditor(episode,root=root,store=args.store,path_maps=maps,bundle=args.bundle).run()
            except Exception as exc:
                report=dict(passed=False,checks=0,errors=[dict(check='auditor_initialization',detail=repr(exc))],
                    episode=str(episode),episode_sha256=sha(episode),auditor_sha256=auditor_hash,dependencies={})
            target.parent.mkdir(parents=True,exist_ok=True);target.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+'\n');new+=1
        reports.append(dict(world=world,arm=arm,report=str(target),passed=report['passed'],checks=report['checks'],
            episode_sha256=sha(episode),recorded_status=raw_receipt['status'],recorded_success=raw_receipt['success']))
        if not report['passed']:
            print(json.dumps(dict(index=index,world=world,arm=arm,errors=report['errors'][:20])),flush=True)
        if (index+1)%20==0:print(json.dumps(dict(audited=index+1,available=len(receipts),new=new,reused=reused)),flush=True)
    out=dict(schema='r19-completed-independent-audit-v1',audited_utc=datetime.now(timezone.utc).isoformat(),
        passed=all(r['passed'] for r in reports),completed_receipts_audited=len(reports),
        checks=sum(r['checks'] for r in reports),new_proofs=new,reused_proofs=reused,
        audit_wall_seconds=time.monotonic()-started,recorded_statuses=dict(Counter(r['recorded_status'] for r in reports)),
        recorded_successes=sum(r['recorded_success'] for r in reports),reports=reports,
        auditor_sha256=auditor_hash,engine_or_policy_imported=False,scientific_episode_reruns=0,
        scope='Finished scientific execution receipts only; registered initial-planner failures remain in the root denominator. Solver residual proof is separate.')
    Path(args.output).write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k!='reports'}))
    raise SystemExit(0 if out['passed'] else 1)


if __name__=='__main__':main()
