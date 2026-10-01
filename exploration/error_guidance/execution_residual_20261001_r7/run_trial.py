"""Real native S1 runs; only allowlisted delivered events reach the actor."""
from pathlib import Path
import hashlib,importlib.util,json,os,signal,subprocess,time,traceback,xml.etree.ElementTree as ET
from public_model import PublicHistory,forecast
HERE=Path(__file__).resolve().parent;PARENT=HERE.parent/'published_continuous_execution_20261001_r6c'
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence');OUT=MAIN/HERE.name;OLD=MAIN/PARENT.name
sp=importlib.util.spec_from_file_location('r6_runner',PARENT/'run_trial.py');r6=importlib.util.module_from_spec(sp);sp.loader.exec_module(r6)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main(ident):
 spec=next(r for r in json.loads((HERE/'runs.json').read_text())['runs'] if r['id']==ident)
 freeze=json.loads((HERE/('freeze_test.json' if spec['split']=='test' else 'freeze_train.json')).read_text())
 for p,h in freeze['pins'].items():assert sha(p)==h,p
 checkpoint=json.loads((HERE/'model_freeze.json').read_text()) if spec['split']=='test' else None
 n=spec['N'];h=spec['horizon_ticks'];port=spec['port'];inp=HERE/'inputs'/spec['input_id'];dst=OUT/'runs'/ident;dst.mkdir(parents=True,exist_ok=False)
 cfg=HERE/'configs'/(ident+'.json');candidate=spec['policy'] in ('history','learned');bridge=OUT/'bridge_candidate' if candidate else OLD/('bridge_'+spec['policy'])
 env=os.environ.copy();env.update(INTEGRATION_TRACE=str(dst/'events.jsonl'),INTEGRATION_PAUSE='0',R4_CONDITION=spec['condition']);env['LD_LIBRARY_PATH']='/home/lyh/.local/lib:'+env.get('LD_LIBRARY_PATH','')
 (dst/'experiment.argos').write_bytes((HERE/'xml'/(ident+'.argos')).read_bytes())
 server=[str(OLD/'server_build/ExecutionManager'),f'--num_robots={n}',f'--port_number={port}',f'--output_file={dst}/stats.json','--save_stats=true','--screen=0',f'--total_sim_step_tick={h}','--ticks_per_second=10','--look_ahead_dist=0','--look_ahead_tick=0',f'--seed={spec["seed"]}','--sim_window_tick=10','--sim_window_timestep=1','--plan_window_timestep=1','--planner_invoke_policy=joint_settled','--backup_planner=PIBT',f'--map={inp}/map.json','--grid_type=regular','--rotation=false','--task_assigner_type=one_goal',f'--task_file={inp}/tasks_n8.txt']
 commands=[server,['argos3','-c',str(dst/'experiment.argos'),'--no-color'],[str(bridge),str(cfg)]]
 ps=[];logs=[];rpc=None;start=time.monotonic();error=None;count=0;times=[];last=-1;hist=PublicHistory()
 def alarm(*args):raise TimeoutError('115s real trial bound')
 signal.signal(signal.SIGALRM,alarm);signal.alarm(115)
 try:
  for i,args in enumerate(commands):
   log=(dst/f'process{i}.log').open('w');logs.append(log);p=subprocess.Popen(['rtk','proxy',*args],cwd=dst,env=env,stdout=subprocess.PIPE if i==2 else log,stderr=log,stdin=subprocess.PIPE if i==2 else subprocess.DEVNULL,text=True,start_new_session=True);ps.append(p)
   if i==0:
    for _ in range(100):
     if p.poll() is not None:raise RuntimeError('server exited')
     try:rpc=r6.RPC(port);break
     except ConnectionRefusedError:time.sleep(.02)
    else:raise RuntimeError('server unavailable')
  layout=json.loads((inp/'map.json').read_text())['layout']
  while ps[1].poll() is None:
   try:
    if not rpc.call('is_initialized') or not rpc.call('invoke_planner'):time.sleep(.0005);continue
    snapshot=json.loads(rpc.call('snapshot'));view=json.loads(rpc.call('get_location'));assert snapshot['joint_settled']
    hist.ingest(dst/'events.jsonl')
    req={'mapf_instance':view['mapf_instance'],'rows':32,'cols':32,'map_name':spec['map'],'map':[int(c=='@') for row in layout for c in row]}
    fc=None;t0=time.monotonic()
    if candidate:
     fc=forecast(hist,view,layout,spec['policy'],checkpoint);req['edge_costs']=fc['cost_by_agent_destination']
    forecast_wall=time.monotonic()-t0
    t0=time.monotonic();ps[2].stdin.write(json.dumps(req)+'\n');ps[2].stdin.flush();line=ps[2].stdout.readline()
    if not line:raise RuntimeError(f'bridge exit {ps[2].poll()}')
    result=json.loads(line);wall=time.monotonic()-t0;times.append(wall)
    assert result['step']==count and result['objective']==(4 if spec['policy']=='trained' else 3) and len(result['actions'])==n
    assert result['network_parameters']==json.loads(cfg.read_text())['parameters']
    paths=[]
    for a,action in enumerate(result['actions']):
     assert action in range(5);s=view['mapf_instance']['starts'][a]['location'];goal=view['mapf_instance']['goals'][a][0];t=s+[1,32,-1,-32,0][action]
     assert 0<=t<1024 and abs(t//32-s//32)+abs(t%32-s%32)<=1 and layout[t//32][t%32]!='@'
     task=goal['id'] if t==goal['location'] else -1
     paths.append([[s//32,s%32,0,task if t==s else -1],[t//32,t%32,1,-1 if t==s else task]])
    assert len({tuple(p[1][:2]) for p in paths})==n
    for a in range(n):
     for b in range(a):assert not(paths[a][0][:2]==paths[b][1][:2] and paths[b][0][:2]==paths[a][1][:2])
    proposal={'success':True,'plan':paths,'congested':False,'proposal_id':count,'view_sha256':hashlib.sha256(json.dumps(view,sort_keys=True).encode()).hexdigest()}
    decision={'snapshot':snapshot,'view':view,'request':req,'result':result,'proposal':proposal,'planner_request_wall_seconds':wall,'forecast_wall_seconds':forecast_wall,'forecast':fc,'public_history_rows':len(hist.rows),'public_last_sequence':hist.last_sequence}
    with (dst/'decisions.jsonl').open('a') as f:f.write(json.dumps(decision)+'\n')
    count+=1;rpc.call('add_plan',json.dumps(proposal))
   except (EOFError,ConnectionResetError):break
  for p in ps[:2]:p.wait(timeout=3)
  assert all(p.returncode==0 for p in ps[:2]),'native nonzero'
  hist.ingest(dst/'events.jsonl')
  with (dst/'events.jsonl').open() as f:
   for line in f:
    e=json.loads(line)
    if e['kind']=='horizon':last=e['tick']
  assert last==h,'missing actual horizon'
 except Exception:error=traceback.format_exc()
 finally:
  signal.alarm(0)
  if rpc:rpc.close()
  status=r6.cleanup(ps,start)
  for f in logs:f.close()
  (dst/'public_events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in hist.projected))
  (dst/'supervised_rows.json').write_text(json.dumps({'rows':hist.rows,'censored':[r for r in hist.moves.values() if r['duration'] is None]},indent=2)+'\n')
  receipt={'trial':ident,'spec':spec,'commands':commands,'wall_seconds':time.monotonic()-start,'error':error,'decisions':count,'processes':status,'true_horizon_tick':last,'planner_total_request_wall_seconds':sum(times),'freeze':freeze,'bridge_sha256':sha(bridge),'config_sha256':sha(cfg),'model_sha256':sha(HERE/'model_freeze.json') if checkpoint else None}
  receipt['files']={str(p.relative_to(dst)):sha(p) for p in dst.rglob('*') if p.is_file()}
  (dst/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ('trial','wall_seconds','error','decisions','true_horizon_tick')}),flush=True)
 return int(error is not None)
if __name__=='__main__':
 import sys
 raise SystemExit(main(sys.argv[1]))
