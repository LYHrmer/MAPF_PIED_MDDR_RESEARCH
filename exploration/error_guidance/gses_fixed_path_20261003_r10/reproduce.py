"""Offline rebuild using the already published, MIT-licensed author archive."""
from pathlib import Path
import argparse
import hashlib
import json
import shutil
import subprocess
import tarfile
import time

ROOT=Path(__file__).resolve().parent


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--dest',type=Path,required=True,help='new empty output directory')
    args=parser.parse_args()
    dest=args.dest.resolve()
    dest.mkdir(parents=True,exist_ok=False)
    upstream=ROOT.parent/'gses_author_preflight_20261003_r9'
    vendor=dest/'STPG'
    vendor.mkdir()
    with tarfile.open(upstream/'author_core_source.tar.gz') as archive:
        for member in archive.getmembers():
            target=(vendor/member.name).resolve()
            assert target.is_relative_to(vendor) and member.isfile(), 'unexpected archive member'
            target.parent.mkdir(parents=True,exist_ok=True)
            target.write_bytes(archive.extractfile(member).read())
    shutil.copytree(upstream/'inputs/data',vendor/'data')
    pins=json.loads((ROOT/'SOURCE_BINDINGS_01.json').read_text())
    for name,item in pins['files'].items():
        assert sha(vendor/name)==item['sha256'],name
    for name,digest in pins['adapter_before_build'].items():
        assert sha(ROOT/name)==digest,name
    sources=['src/Algorithm/Astar.cpp','src/Algorithm/graph_algo.cpp','src/Algorithm/heuristic.cpp',
             'src/graph/graph.cpp','src/graph/generate_graph.cpp','src/util/Timer.cpp']
    command=['rtk','proxy','g++','-std=c++17','-O3','-DNDEBUG','-I'+str(vendor/'inc'),str(ROOT/'export_author.cpp')]
    command += [str(vendor/s) for s in sources]+['-o',str(dest/'export_author')]
    started=time.monotonic()
    with (dest/'stdout.log').open('w') as out,(dest/'stderr.log').open('w') as err:
        proc=subprocess.run(command,stdout=out,stderr=err,timeout=300)
    receipt={'command':command,'returncode':proc.returncode,'wall_seconds':time.monotonic()-started,
             'author_files_verified':len(pins['files']),'adapter_files_verified':len(pins['adapter_before_build']),
             'archive_sha256':sha(upstream/'author_core_source.tar.gz')}
    if proc.returncode==0:
        receipt['binary_sha256']=sha(dest/'export_author')
        receipt['byte_identical_to_executed']=receipt['binary_sha256']==json.loads((ROOT/'BINARY_01.json').read_text())['sha256']
    (dest/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt))
    assert proc.returncode==0


if __name__=='__main__':
    main()
