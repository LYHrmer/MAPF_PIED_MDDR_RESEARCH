"""Build against unchanged author source, run registered cases, preserve all attempts."""
from pathlib import Path
import argparse
import datetime as dt
import gzip
import hashlib
import json
import subprocess
import time

ROOT = Path(__file__).resolve().parent
MAIN = Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
OLD = MAIN / 'gses_author_preflight_20261003_r9'
DEFAULT_VENDOR = OLD / 'vendor/STPG'


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path, obj):
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n')


def record(command, cwd, folder, timeout):
    folder.mkdir(parents=True, exist_ok=False)
    start=time.monotonic()
    receipt={'command':command, 'cwd':str(cwd), 'started_utc':dt.datetime.now(dt.timezone.utc).isoformat()}
    with (folder/'stdout.log').open('w') as out, (folder/'stderr.log').open('w') as err:
        try:
            proc=subprocess.run(command, cwd=cwd, stdout=out, stderr=err, timeout=timeout)
            receipt['returncode']=proc.returncode
        except subprocess.TimeoutExpired:
            receipt.update(returncode=None, timeout_seconds=timeout)
    receipt['elapsed_seconds']=time.monotonic()-start
    write(folder/'receipt.json',receipt)
    print(json.dumps(receipt),flush=True)
    return receipt


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('stage', choices=['build','run'])
    parser.add_argument('--vendor',type=Path,default=DEFAULT_VENDOR)
    parser.add_argument('--raw',type=Path,default=MAIN/'gses_fixed_path_20261003_r10')
    parser.add_argument('--attempt',default='01')
    args=parser.parse_args()
    args.raw.mkdir(parents=True,exist_ok=True)
    vendor=args.vendor.resolve()
    registration=json.loads((ROOT/'REGISTERED_CASES.json').read_text())
    if args.stage=='build':
        sources=['src/Algorithm/Astar.cpp','src/Algorithm/graph_algo.cpp','src/Algorithm/heuristic.cpp',
                 'src/graph/graph.cpp','src/graph/generate_graph.cpp','src/util/Timer.cpp']
        files=sorted([p for p in (vendor/'inc').rglob('*') if p.is_file()]+[vendor/s for s in sources])
        bindings={str(p.relative_to(vendor)):{'sha256':digest(p),'bytes':p.stat().st_size} for p in files}
        pins={'author_commit':registration['author_commit'],'files':bindings,
              'adapter_before_build':{p.name:digest(p) for p in [ROOT/'export_author.cpp',ROOT/'PROTOCOL.md',ROOT/'run_pipeline.py',ROOT/'verify_replay.py']}}
        write(ROOT/('SOURCE_BINDINGS_'+args.attempt+'.json'),pins)
        command=['rtk','proxy','g++','-std=c++17','-O3','-DNDEBUG','-I'+str(vendor/'inc'),
                 str(ROOT/'export_author.cpp')]+[str(vendor/s) for s in sources]+['-o',str(args.raw/'export_author')]
        receipt=record(command,vendor,ROOT/('build_attempt'+args.attempt),300)
        assert receipt['returncode']==0, 'build failure retained'
        write(ROOT/('BINARY_'+args.attempt+'.json'),{'sha256':digest(args.raw/'export_author'),
             'bytes':(args.raw/'export_author').stat().st_size})
        return
    results=[]
    for case in registration['cases']:
        for key,sha in [('path','path_sha256'),('situation_file','situation_sha256')]:
            assert digest(vendor/case[key])==case[sha]
        for method in registration['methods']:
            name=case['map']+'__'+method
            dest=args.raw/(name+'.json')
            folder=ROOT/'commands'/name/('attempt'+args.attempt)
            command=['rtk','proxy','prlimit','--as='+str(4*1024**3),'--cpu=90','--',str(args.raw/'export_author'),
                     str(vendor/case['path']),str(vendor/case['situation_file']),method,str(dest)]
            receipt=record(command,vendor,folder,120)
            row={'case':case['map'],'agents':case['agents'],'method':method,**receipt}
            if receipt['returncode']==0:
                data=json.loads(dest.read_text())
                packed=ROOT/'raw'/('attempt'+args.attempt)/(name+'.json.gz')
                packed.parent.mkdir(parents=True,exist_ok=True)
                with packed.open('wb') as f:
                    with gzip.GzipFile(filename='',mode='wb',fileobj=f,mtime=0) as z:
                        z.write(dest.read_bytes())
                row.update(status=data['status'],original_cost=data['original']['cost'],cost=data['selected']['cost'],
                           search_elapsed_us=data['search_elapsed_us'],raw=str(packed.relative_to(ROOT)),
                           raw_sha256=digest(packed),uncompressed_sha256=digest(dest))
            results.append(row)
            write(ROOT/('RESULTS_attempt'+args.attempt+'.json'),results)
    assert all(x['returncode']==0 for x in results), 'execution failure retained'


if __name__=='__main__':
    main()
