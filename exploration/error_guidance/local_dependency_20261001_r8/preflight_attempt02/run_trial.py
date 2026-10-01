from pathlib import Path
import copy,hashlib,importlib.util,json,os,signal,subprocess,time,traceback
from public_model import PublicHistory,forecast
H=Path(__file__).resolve().parent;P=H.parent/'published_continuous_execution_20261001_r6c';M=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence');O=M/H.name
sp=importlib.util.spec_from_file_location('r6',P/'run_trial.py');r6=importlib.util.module_from_spec(sp);sp.loader.exec_module(r6)
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main(ident):
 spec=next(s for s in json.loads((H/'runs.json').read_text())['runs'] if s['id']==ident)
 for p,h in json.loads((H/'freeze.json').read_text())['pins'].items():assert sha(p)==h,p
 n=spec['N'];cols=spec['cols'];h=spec['horizon_ticks'];inp=H/'inputs'/spec['input_id'];port=spec['port'];dst=O/'runs'/ident;dst.mkdir(parents=True,exist_ok=False)
 cfg=H/'configs'/(ident+'.json');candidate=spec['policy']!='hm';bridge=O/('bridge_candidate' if candidate else 'bridge_official');model=json.loads((H/'model_freeze.json').read_text())
 env=os.environ.copy();env.update(INTEGRATION_TRACE=str(dst/'events.jsonl'),INTEGRATION_PAUSE=str(int(spec['condition']=='unknown_pause')),R4_CONDITION=spec['condition'],R8_EXECUTION=spec['execution']);env['LD_LIBRARY_PATH']='/home/lyh/.local/lib:'+env.get('LD_LIBRARY_PATH','')
 (dst/'experiment.argos').write_bytes((H/'xml'/(ident+'.argos')).read_bytes())
 server=[str(O/'server_build/ExecutionManager'),f'--num_robots={n}',f'--port_number={port}',f'--output_file={dst}/stats.json','--save_stats=true','--screen=0',f'--total_sim_step_tick={h}','--ticks_per_second=10','--look_ahead_dist=0','--look_ahead_tick=0',f'--seed={spec["seed"]}','--sim_window_tick=10','--sim_window_timestep=1','--plan_window_timestep=2','--planner_invoke_policy=joint_settled','--backup_planner=PIBT',f'--map={inp}/map.json','--grid_type=regular','--rotation=false','--task_assigner_type=one_goal',f'--task_file={inp}/tasks_n{n}.txt']
 commands=[server,['argos3','-c',str(dst/'experiment.argos'),'--no-color'],[str(bridge),str(cfg)]]
 ps=[];logs=[];rpc=None;start=time.monotonic();error=None;batch=0;call=0;last=-1;hist=PublicHistory();times=[];fc_times=[]
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
    snapshot=json.loads(rpc.call('snapshot'));view=json.loads(rpc.call('get_location'));assert snapshot['joint_settled'];hist.ingest(dst/'events.jsonl')
    virtual=copy.deepcopy(view);paths=[[[s['location']//cols,s['location']%cols,0,-1]] for s in view['mapf_instance']['starts']];calls=[]
    for step in range(2):
     req={'mapf_instance':copy.deepcopy(virtual['mapf_instance']),'rows':cols,'cols':cols,'map_name':spec['map'],'map':[int(c=='@') for row in layout for c in row]};fc=None;t=time.monotonic()
     if candidate:fc=forecast(hist,virtual,layout,spec['policy'],model);req['edge_costs']=fc['cost_by_agent_destination']
     ft=time.monotonic()-t;fc_times.append(ft);t=time.monotonic();ps[2].stdin.write(json.dumps(req)+'\n');ps[2].stdin.flush();line=ps[2].stdout.readline();assert line,'bridge exit';result=json.loads(line);wt=time.monotonic()-t;times.append(wt)
     assert result['step']==call and result['objective']==3 and len(result['actions'])==n;call+=1
     assert result['network_parameters']==json.loads(cfg.read_text())['parameters']
     locs=[]
     for a,action in enumerate(result['actions']):
      assert action in range(5);s=virtual['mapf_instance']['starts'][a]['location'];z=s+[1,cols,-1,-cols,0][action]
      assert 0<=z<cols*cols and abs(z//cols-s//cols)+abs(z%cols-s%cols)<=1 and layout[z//cols][z%cols]!='@';locs.append(z);paths[a].append([z//cols,z%cols,step+1,-1])
     assert len(set(locs))==n
     for a in range(n):
      for b in range(a):assert not(locs[a]==virtual['mapf_instance']['starts'][b]['location'] and locs[b]==virtual['mapf_instance']['starts'][a]['location'])
     calls.append({'logical_step':step,'request':req,'result':result,'forecast':fc,'planner_wall':wt,'forecast_wall':ft,'public_last_sequence':hist.last_sequence,'completed_rows':len(hist.rows)})
     for a,z in enumerate(locs):
      virtual['mapf_instance']['starts'][a]['location']=z
      if result['actions'][a]!=4:virtual['mapf_instance']['starts'][a]['orientation']=result['actions'][a]
    for a,path in enumerate(paths):
     goal=view['mapf_instance']['goals'][a][0]
     for point in path:
      if point[0]*cols+point[1]==goal['location']:point[3]=goal['id'];break
    proposal={'success':True,'plan':paths,'congested':False,'proposal_id':batch,'view_sha256':hashlib.sha256(json.dumps(view,sort_keys=True).encode()).hexdigest()}
    decision={'snapshot':snapshot,'view':view,'calls':calls,'proposal':proposal,'public_history_rows':len(hist.rows),'public_last_sequence':hist.last_sequence}
    with (dst/'decisions.jsonl').open('a') as f:f.write(json.dumps(decision)+'\n')
    batch+=1;rpc.call('add_plan',json.dumps(proposal))
   except (EOFError,ConnectionResetError):break
  for p in ps[:2]:p.wait(timeout=3)
  assert all(p.returncode==0 for p in ps[:2]),'native nonzero';hist.ingest(dst/'events.jsonl')
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
  (dst/'public_events.jsonl').write_text(''.join(json.dumps(e)+'\n' for e in hist.projected));(dst/'supervised_rows.json').write_text(json.dumps({'rows':hist.rows,'censored':[r for r in hist.moves.values() if r['duration'] is None]},indent=2)+'\n')
  receipt={'trial':ident,'spec':spec,'commands':commands,'wall_seconds':time.monotonic()-start,'error':error,'decisions':batch,'calls':call,'processes':status,'true_horizon_tick':last,'planner_wall':sum(times),'forecast_wall':sum(fc_times),'freeze_sha256':sha(H/'freeze.json'),'model_sha256':sha(H/'model_freeze.json')};receipt['files']={str(p.relative_to(dst)):sha(p) for p in dst.rglob('*') if p.is_file()};(dst/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps({k:receipt[k] for k in ['trial','wall_seconds','error','decisions','true_horizon_tick']}),flush=True)
 return int(error is not None)
if __name__=='__main__':
 import sys
 raise SystemExit(main(sys.argv[1]))
