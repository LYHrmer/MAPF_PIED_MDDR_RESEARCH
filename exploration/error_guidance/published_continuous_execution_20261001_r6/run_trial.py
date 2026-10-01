"""Shared S1 continuous execution for the two real author planner object sets."""
from pathlib import Path
import hashlib,json,os,signal,socket,subprocess,time,traceback
import msgpack
HERE=Path(__file__).resolve().parent;OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/HERE.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
class RPC:
 def __init__(self,port):self.s=socket.create_connection(('127.0.0.1',port),timeout=2);self.u=msgpack.Unpacker(raw=False);self.seq=0
 def call(self,name,*args):
  self.seq+=1;self.s.sendall(msgpack.packb([0,self.seq,name,list(args)],use_bin_type=True))
  while True:
   for m in self.u:
    assert m[0]==1 and m[1]==self.seq
    if m[2] is not None:raise RuntimeError(m[2])
    return m[3]
   data=self.s.recv(1<<20)
   if not data:raise EOFError('closed')
   self.u.feed(data)
 def close(self):self.s.close()
def verify():
 freeze=json.loads((HERE/'freeze.json').read_text())
 for p,h in freeze['pins'].items():assert sha(p)==h,p
 for policy,files in json.loads((HERE/'official_object_manifest.json').read_text()).items():
  for p,h in files.items():assert sha(p)==h,p
 return freeze
def cleanup(ps,start):
 before=[p.poll() for p in ps]
 for p,status in zip(ps,before):
  if status is None:
   try:os.killpg(p.pid,signal.SIGTERM)
   except ProcessLookupError:pass
 end=min(start+119,time.monotonic()+3.8)
 while any(p.poll() is None for p in ps) and time.monotonic()<end:time.sleep(.01)
 for p in ps:
  if p.poll() is None:
   try:os.killpg(p.pid,signal.SIGKILL)
   except ProcessLookupError:pass
 for p in ps:
  try:p.wait(timeout=.1)
  except subprocess.TimeoutExpired:pass
 return [{'before_cleanup':b,'returncode':p.poll()} for p,b in zip(ps,before)]
def main(trial):
 freeze=verify();spec=next(r for r in json.loads((HERE/'runs.json').read_text())['runs'] if r['id']==trial)
 N=spec['N'];H=spec['horizon_ticks'];inp=HERE/'inputs'/spec['map'];dst=OUT/'runs'/trial;dst.mkdir(parents=True,exist_ok=False)
 env=os.environ.copy();env.update(INTEGRATION_TRACE=str(dst/'events.jsonl'),INTEGRATION_PAUSE=str(int(spec['condition']=='unknown_pause')),R4_CONDITION=spec['condition'])
 env['LD_LIBRARY_PATH']='/home/lyh/.local/lib:'+env.get('LD_LIBRARY_PATH','')
 (dst/'experiment.argos').write_bytes((inp/f'experiment_n{N}.argos').read_bytes())
 server=[str(OUT/'server_build/ExecutionManager'),f'--num_robots={N}','--port_number=9491',f'--output_file={dst}/stats.json','--save_stats=true','--screen=0',f'--total_sim_step_tick={H}','--ticks_per_second=10','--look_ahead_dist=0','--look_ahead_tick=0','--seed=930401','--sim_window_tick=10','--sim_window_timestep=1','--plan_window_timestep=1','--planner_invoke_policy=joint_settled','--backup_planner=PIBT',f'--map={inp}/map.json','--grid_type=regular','--rotation=false','--task_assigner_type=one_goal',f'--task_file={inp}/tasks_n{N}.txt']
 commands=[server,['argos3','-c',str(dst/'experiment.argos'),'--no-color'],[str(OUT/('bridge_'+spec['policy'])),str(HERE/(spec['policy']+'_config.json'))]]
 ps=[];logs=[];rpc=None;start=time.monotonic();error=None;count=0;planning=[];last_step=-1
 def alarm(*args):raise TimeoutError('115s blocking guard; shared cleanup inside120s')
 signal.signal(signal.SIGALRM,alarm);signal.alarm(115)
 try:
  for i,args in enumerate(commands):
   log=(dst/f'process{i}.log').open('w');logs.append(log);p=subprocess.Popen(['rtk','proxy',*args],cwd=dst,env=env,stdout=subprocess.PIPE if i==2 else log,stderr=log,stdin=subprocess.PIPE if i==2 else subprocess.DEVNULL,text=True,start_new_session=True);ps.append(p)
   if i==0:
    for _ in range(100):
     if p.poll() is not None:raise RuntimeError('server exited')
     try:rpc=RPC(9491);break
     except ConnectionRefusedError:time.sleep(.02)
    else:raise RuntimeError('server unavailable')
  layout=json.loads((inp/'map.json').read_text())['layout']
  while ps[1].poll() is None:
   try:
    if not rpc.call('is_initialized') or not rpc.call('invoke_planner'):time.sleep(.0005);continue
    snapshot=json.loads(rpc.call('snapshot'));view=json.loads(rpc.call('get_location'));assert snapshot['joint_settled']
    assert len(view['mapf_instance']['starts'])==N
    req={'mapf_instance':view['mapf_instance'],'rows':32,'cols':32,'map_name':spec['map'],'map':[int(c=='@') for row in layout for c in row]}
    t0=time.monotonic();ps[2].stdin.write(json.dumps(req)+'\n');ps[2].stdin.flush();line=ps[2].stdout.readline()
    if not line:raise RuntimeError(f'official bridge exit{ps[2].poll()}')
    result=json.loads(line);wall=time.monotonic()-t0;planning.append(wall)
    assert result['step']==count and result['objective']==(3 if spec['policy']=='hm_GPIBT' else 4) and len(result['actions'])==N and result['parameter_count']==560
    assert result['network_parameters']==json.loads((HERE/(spec['policy']+'_config.json')).read_text())['parameters']
    paths=[]
    for a,action in enumerate(result['actions']):
     assert action in range(5);s=view['mapf_instance']['starts'][a]['location'];goal=view['mapf_instance']['goals'][a][0];t=s+[1,32,-1,-32,0][action]
     assert 0<=t<1024 and abs(t//32-s//32)+abs(t%32-s%32)<=1 and layout[t//32][t%32]!='@'
     task=goal['id'] if t==goal['location'] else -1
     paths.append([[s//32,s%32,0,task if t==s else -1],[t//32,t%32,1,-1 if t==s else task]])
    assert len({tuple(p[1][:2]) for p in paths})==N
    for a in range(N):
     for b in range(a):assert not(paths[a][0][:2]==paths[b][1][:2] and paths[b][0][:2]==paths[a][1][:2])
    proposal={'success':True,'plan':paths,'congested':False,'proposal_id':count,'view_sha256':hashlib.sha256(json.dumps(view,sort_keys=True).encode()).hexdigest()}
    decision={'snapshot':snapshot,'view':view,'request':req,'result':result,'proposal':proposal,'planner_request_wall_seconds':wall,'config_sha256':sha(HERE/(spec['policy']+'_config.json'))}
    with (dst/'decisions.jsonl').open('a') as f:f.write(json.dumps(decision)+'\n')
    count+=1;rpc.call('add_plan',json.dumps(proposal))
   except (EOFError,ConnectionResetError):break
  for p in ps[:2]:p.wait(timeout=3)
  assert all(p.returncode==0 for p in ps[:2]),'native nonzero'
  with (dst/'events.jsonl').open() as f:
   for line in f:
    e=json.loads(line)
    if e['kind']=='horizon':last_step=e['tick']
  assert last_step==H,'missing true8000tick horizon'
 except Exception:error=traceback.format_exc()
 finally:
  signal.alarm(0)
  if rpc:rpc.close()
  status=cleanup(ps,start)
  for f in logs:f.close()
  receipt={'trial':trial,'spec':spec,'commands':commands,'wall_seconds':time.monotonic()-start,'error':error,'decisions':count,'processes':status,'true_horizon_tick':last_step,'whole_trial_limit_seconds':120,'planner_total_request_wall_seconds':sum(planning),'protocol_sha256':sha(HERE/'PROTOCOL.md'),'freeze_sha256':sha(HERE/'freeze.json'),'config_sha256':sha(HERE/(spec['policy']+'_config.json')),'binary_identities':json.loads((HERE/'binary_manifest.json').read_text()),'model_identity':json.loads((HERE/'model_identity.json').read_text())}
  if receipt['wall_seconds']>120 and receipt['error'] is None:receipt['error']='whole120s exceeded'
  receipt['files']={str(p.relative_to(dst)):sha(p) for p in dst.rglob('*') if p.is_file()}
  (dst/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ['trial','wall_seconds','error','decisions','true_horizon_tick','planner_total_request_wall_seconds']}),flush=True)
 return int(receipt['error'] is not None)
if __name__=='__main__':
 import sys
 raise SystemExit(main(sys.argv[1]))
