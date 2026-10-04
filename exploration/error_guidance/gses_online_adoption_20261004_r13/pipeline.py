from pathlib import Path
import argparse,copy,datetime,gzip,hashlib,json,shutil,subprocess,time
HERE=Path(__file__).resolve().parent
PARENT=HERE.parent
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')
RAW=MAIN/HERE.name
VENDOR=MAIN/'gses_author_preflight_20261003_r9/vendor/STPG'
OLD=PARENT/'gses_primitive_20261003_r11'
R10=PARENT/'gses_fixed_path_20261003_r10'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,x):p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,indent=2,default=str)+'\n')
def packed(p,obj):
 data=(json.dumps(obj,separators=(',',':'),default=str)+'\n').encode()
 with p.open('wb') as f:
  with gzip.GzipFile(fileobj=f,mode='wb',filename='',mtime=0) as z:z.write(data)
 return {'raw':str(p.relative_to(HERE)),'packed_sha256':sha(p),'raw_sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
def command(cmd,folder,timeout):
 folder.mkdir(parents=True,exist_ok=False);start=time.time_ns();r={'command':cmd,'started_unix_ns':start}
 with (folder/'stdout.log').open('w') as out,(folder/'stderr.log').open('w') as err:
  try:r['returncode']=subprocess.run(cmd,stdout=out,stderr=err,timeout=timeout).returncode
  except subprocess.TimeoutExpired:r['returncode']=None;r['timeout_seconds']=timeout
 r['finished_unix_ns']=time.time_ns();r['elapsed_seconds']=(r['finished_unix_ns']-start)/1e9
 write(folder/'receipt.json',r);return r
def prepare():
 assert not (HERE/'REGISTRATION.json').exists(),'already frozen'
 RAW.mkdir(parents=True,exist_ok=True)
 for name in ['executor.py','AUTHOR_LICENSE.txt']:shutil.copyfile(OLD/name,HERE/name)
 audit=(OLD/'audit_events.py').read_text()
 audit=audit.replace("for ix,e in enumerate(trace['events']):\n", "for ix,e in enumerate(trace['events']):\n  adoption=trace.get('adoption')\n  if adoption and ix==adoption['event_seq']:\n   assert F(adoption['at'])<=F(e['t']);deps={}\n   for u,v,w in adoption['graph']['type2']:deps.setdefault(ids[v],[]).append(ids[u])\n")
 (HERE/'audit_events.py').write_text(audit)
 bindings=json.loads((R10/'SOURCE_BINDINGS_01.json').read_text())
 for rel,row in bindings['files'].items():assert sha(VENDOR/rel)==row['sha256']
 write(HERE/'AUTHOR_SOURCE.json',bindings)
 sources=['src/Algorithm/Astar.cpp','src/Algorithm/graph_algo.cpp','src/Algorithm/heuristic.cpp','src/graph/graph.cpp','src/graph/generate_graph.cpp','src/util/Timer.cpp']
 cmd=['rtk','proxy','g++','-std=c++17','-O3','-DNDEBUG','-I'+str(VENDOR/'inc'),str(HERE/'author_online.cpp')]+[str(VENDOR/s) for s in sources]+['-o',str(RAW/'author_online')]
 build=command(cmd,HERE/'build_attempt01',300);assert build['returncode']==0,'build failure retained'
 cases=[]
 for case in ['random-32-32-10','warehouse-10-20-10-2-1']:
  source=R10/'raw/attempt01'/f'{case}__GSES.json.gz'
  cases.append({'case':case,'source':str(source),'sha256':sha(source)})
 runs=[]
 for c in cases:
  for at in ['1/2','5/2']:
   for profile in ['primitive_nominal','axis_slow','midpoint_pause']:
    runs.append(dict(c,at=at,profile=profile,id=c['case']+'__t'+at.replace('/','_')+'__'+profile))
 pins={name:sha(HERE/name) for name in ['author_online.cpp','executor.py','audit_events.py','online.py','pipeline.py','PROTOCOL.md','AUTHOR_SOURCE.json','AUTHOR_LICENSE.txt']}
 reg={'created_UTC':datetime.datetime.now(datetime.timezone.utc).isoformat(),'frozen_unix_ns':time.time_ns(),'author_commit':bindings['author_commit'],
      'methods':['GSES','Improved_GSES'],'solver_timeout_seconds':16,'host_timeout_seconds':25,'solver_concurrency':1,'profiles':3,'checkpoints':12,'solver_calls':24,'continuations':36,
      'runs':runs,'source_pins':pins,'binary':str(RAW/'author_online'),'binary_sha256':sha(RAW/'author_online'),
      'R11_executor_sha256':sha(OLD/'executor.py'),'independent_units':'two reused author instances; twelve mechanism contexts, not heldout families'}
 write(HERE/'REGISTRATION.json',reg)
def run():
 from executor import Executor
 from online import checkpoint,public_input,finish,continue_candidate,digest
 from audit_events import audit
 reg=json.loads((HERE/'REGISTRATION.json').read_text())
 for n,h in reg['source_pins'].items():assert sha(HERE/n)==h
 assert sha(reg['binary'])==reg['binary_sha256']
 assert not (HERE/'RUN_START.json').exists(),'run already started; preserve attempts'
 write(HERE/'RUN_START.json',{'started_unix_ns':time.time_ns(),'registration_sha256':sha(HERE/'REGISTRATION.json')})
 rows=[];(HERE/'raw').mkdir(exist_ok=True)
 for spec in reg['runs']:
  assert sha(spec['source'])==spec['sha256'];g=json.loads(gzip.decompress(Path(spec['source']).read_bytes()))['original']['graph']
  engine=checkpoint(g,spec['profile'],spec['at']);snapshot=json.loads(json.dumps(engine.snapshot()));public=public_input(engine)
  packed(HERE/'raw'/f"{spec['id']}__checkpoint.json.gz",snapshot)
  write(HERE/'public'/f"{spec['id']}.json",public)
  controls=finish(Executor.restore(copy.deepcopy(snapshot)),g);control_audit=audit(controls)
  archive=packed(HERE/'raw'/f"{spec['id']}__original.json.gz",controls)
  rows.append({'id':spec['id']+'__original','spec':spec,'method':'original','status':'Control','changed':False,'behavior_changed':False,
               'sum_completion_time':controls['sum_completion_time'],'makespan':controls['makespan'],'audit':control_audit,**archive})
  for method in reg['methods']:
   output=RAW/(spec['id']+'__'+method+'.json');folder=HERE/'calls'/(spec['id']+'__'+method)
   rc=command(['rtk','proxy',reg['binary'],str(HERE/'public'/f"{spec['id']}.json"),method,str(output)],folder,reg['host_timeout_seconds'])
   reply=json.loads(output.read_text()) if rc['returncode']==0 else None
   if reply:
    assert reply['input_graph']==public['solver_graph'];status=reply['status'];write(folder/'author_reply.json',reply)
   else:status='HostTimeout' if rc['returncode'] is None else 'AuthorError'
   trace,adopt=continue_candidate(snapshot,public,reply,status);local=audit(trace)
   archive=packed(HERE/'raw'/f"{spec['id']}__{method}.json.gz",trace)
   changed=bool(adopt['guard'] and adopt['guard']['changed'])
   different=trace['events']!=controls['events'] or trace['segments']!=controls['segments']
   if not changed:assert trace['events']==controls['events'] and trace['segments']==controls['segments'],'fallback diverged'
   # All pre-checkpoint physical/control events and all already committed segments are untouched.
   assert trace['events'][:len(engine.events)]==engine.events
   assert trace['segments'][:len(engine.segments)]==engine.segments
   rows.append({'id':spec['id']+'__'+method,'spec':spec,'method':method,'changed':changed,'behavior_changed':different,
                'sum_completion_time':trace['sum_completion_time'],'makespan':trace['makespan'],'audit':local,
                'public_sha256':sha(HERE/'public'/f"{spec['id']}.json"),'receipt':str((folder/'receipt.json').relative_to(HERE)),
                'author_search_us':reply['search_elapsed_us'] if reply else None,**adopt,**archive})
   write(HERE/'RESULTS.json',rows);print(rows[-1]['id'],rows[-1]['status'],'changed',changed,'behavior',different,flush=True)
 write(HERE/'COMPLETE.json',{'passed':True,'runs':len(rows),'solver_calls':24,'changed':sum(r['changed'] for r in rows),'behavior_changed':sum(r['behavior_changed'] for r in rows),'finished_unix_ns':time.time_ns()})
def main():
 p=argparse.ArgumentParser();p.add_argument('stage',choices=['prepare','run']);args=p.parse_args()
 (prepare if args.stage=='prepare' else run)()
if __name__=='__main__':main()
