"""Re-run this capsule's fixed author inputs; requires a built pinned author tree."""
from pathlib import Path
import argparse
import hashlib
import json
import subprocess
import time

cli=argparse.ArgumentParser()
cli.add_argument('--author-tree',type=Path,required=True)
cli.add_argument('--output',type=Path,required=True)
args=cli.parse_args();home=Path(__file__).resolve().parent
reg=json.loads((home/'REGISTERED_CASES.json').read_text())
tree=args.author_tree.resolve();args.output=args.output.resolve()
commit=subprocess.check_output(['rtk','proxy','git','rev-parse','HEAD'],cwd=tree,text=True).strip()
if commit!=reg['author_commit']:raise SystemExit('Author commit differs from registered commit')
if subprocess.check_output(['rtk','proxy','git','diff','--name-only'],cwd=tree,text=True).strip():raise SystemExit('Author tracked files have modifications')
args.output.mkdir(parents=True,exist_ok=False)
for case in reg['cases']:
    path=home/'inputs'/case['path'];sit=home/'inputs'/case['situation_file']
    assert hashlib.sha256(path.read_bytes()).hexdigest()==case['path_sha256']
    assert hashlib.sha256(sit.read_bytes()).hexdigest()==case['situation_sha256']
    for method,settings in reg['methods'].items():
        a,b,g,h,e,i,w=settings;folder=args.output/(case['map']+'__'+method);folder.mkdir()
        cmd=['rtk','proxy','prlimit','--as=4294967296','--cpu=90','--',str(tree/'build/simulate'),
             '-p',str(path),'-s',str(sit),'-t','16','-a',a,'-b',b,'-g',g,'-h',h,'-e',e,'-i',i,
             '--w_astar','1.0','--w_focal',str(w),'--random_seed','10','-o',str(folder/'stats.json'),'-n',str(folder/'new_paths.txt')]
        start=time.monotonic()
        with (folder/'stdout.log').open('w') as out,(folder/'stderr.log').open('w') as err:
            try:
                p=subprocess.run(cmd,cwd=tree,stdout=out,stderr=err,timeout=120)
                record={'returncode':p.returncode}
            except subprocess.TimeoutExpired:record={'returncode':None,'timeout_seconds':120}
        record.update(command=cmd,elapsed_seconds=time.monotonic()-start)
        (folder/'receipt.json').write_text(json.dumps(record,indent=2)+'\n')
        print(case['map'],method,record['returncode'],flush=True)
