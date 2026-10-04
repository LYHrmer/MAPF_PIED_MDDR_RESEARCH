"""Verify portable pins, replay saved checkpoints, or rebuild unchanged author sources."""
from pathlib import Path
import argparse,copy,gzip,hashlib,json,subprocess,tarfile,tempfile
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(p.read_text())
def unpack(p):return json.loads(gzip.decompress(p.read_bytes()))
def main():
 p=argparse.ArgumentParser();p.add_argument('--replay',default=None,help='one full result ID, or all');p.add_argument('--build',action='store_true');a=p.parse_args()
 reg=load(HERE/'REGISTRATION.json')
 for n,h in reg['source_pins'].items():assert sha(HERE/n)==h,('core freeze',n)
 if (HERE/'PUBLICATION_MEMBERS.json').exists():
  for n,h in load(HERE/'PUBLICATION_MEMBERS.json')['files'].items():assert sha(HERE/n)==h,('publication',n)
 if a.build:
  with tempfile.TemporaryDirectory(prefix='r13_author_rebuild_') as temp:
   root=Path(temp)
   with tarfile.open(HERE/'AUTHOR_SOURCES.tar.gz','r:gz') as bundle:
    for m in bundle.getmembers():assert m.isfile() and '..' not in Path(m.name).parts and not Path(m.name).is_absolute()
    bundle.extractall(root,filter='data')
   for n,r in load(HERE/'AUTHOR_SOURCE.json')['files'].items():assert sha(root/n)==r['sha256']
   cpp=['src/Algorithm/Astar.cpp','src/Algorithm/graph_algo.cpp','src/Algorithm/heuristic.cpp','src/graph/graph.cpp','src/graph/generate_graph.cpp','src/util/Timer.cpp']
   cmd=['rtk','proxy','g++','-std=c++17','-O3','-DNDEBUG','-I'+str(root/'inc'),str(HERE/'author_online.cpp')]+[str(root/n) for n in cpp]+['-o',str(root/'author_online')]
   subprocess.run(cmd,check=True)
   actual=sha(root/'author_online');assert actual==reg['binary_sha256'],('ELF bytes differ',actual)
   print(json.dumps({'author_source_pins':43,'rebuild_ELF_byte_identical':True,'binary_sha256':actual}))
 if a.replay:
  from executor import Executor
  from online import public_input,finish,continue_candidate
  from audit_events import audit
  rows=load(HERE/'RESULTS.json');selected=[r for r in rows if a.replay=='all' or r['id']==a.replay];assert selected,'unknown ID'
  for row in selected:
   stem=row['spec']['id'];snapshot=unpack(HERE/'raw'/(stem+'__checkpoint.json.gz'));public=load(HERE/'public'/(stem+'.json'));engine=Executor.restore(copy.deepcopy(snapshot));assert public_input(engine)==public
   if row['method']=='original':actual=finish(engine,engine.g)
   else:
    rp=HERE/'calls'/row['id']/'author_reply.json';reply=load(rp) if rp.exists() else None
    rc=load(HERE/'calls'/row['id']/'receipt.json');status=reply['status'] if reply else 'HostTimeout' if rc['returncode'] is None else 'AuthorError'
    actual,_=continue_candidate(snapshot,public,reply,status)
   data=gzip.decompress((HERE/row['raw']).read_bytes());assert hashlib.sha256(data).hexdigest()==row['raw_sha256']
   # Compare the complete serialized representation: Python tuples in commitment
   # metadata intentionally become JSON arrays in the frozen raw archive.
   assert json.loads(json.dumps(actual))==json.loads(data),('replay mismatch',row['id']);audit(actual);print(row['id'],'exact replay PASS',flush=True)
 print('frozen source pins PASS')
if __name__=='__main__':main()
