"""Fixed active-MOVE pair; 49s blocking guard plus bounded collective cleanup <=54s."""
import argparse,hashlib,json,os,signal,socket,subprocess,time,traceback
from pathlib import Path
import msgpack
from common import context,forecast,events as read_events
HERE=Path(__file__).resolve().parent
OLD=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/baseline_selection_20260929')
OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_error_model_20260930_r4')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class RPC:
    def __init__(self,port):
        self.s=socket.create_connection(('127.0.0.1',port),timeout=2)
        self.u=msgpack.Unpacker(raw=False);self.seq=0
    def call(self,name,*args):
        self.seq+=1;seq=self.seq
        self.s.sendall(msgpack.packb([0,seq,name,list(args)],use_bin_type=True))
        while True:
            for msg in self.u:
                assert msg[0]==1 and msg[1]==seq,msg
                if msg[2] is not None:raise RuntimeError(msg[2])
                return msg[3]
            data=self.s.recv(1<<20)
            if not data:raise EOFError('server closed')
            self.u.feed(data)
    def close(self):self.s.close()
def verify(require_ready=True):
    ids=json.loads((HERE/'binary_manifest.json').read_text())
    for path,h in ids.items():assert sha(Path(path))==h,path
    pins=json.loads((HERE/'preflight_identity.json').read_text())
    assert sha(HERE/'PROTOCOL.md')==pins['protocol_sha256']
    for name,pin in json.loads((HERE/'source_manifest.json').read_text()).items():assert sha(OUT/'lsmart_successor'/name)==pin['successor'],name
    if require_ready:
        ready=json.loads((HERE/'ready_for_trial.json').read_text())
        for name,h in ready['frozen_files'].items():assert sha(HERE/name)==h,name
    return ids,pins
def collective_cleanup(ps,start):
    """All process groups receive TERM together; shared grace rather than 3 serial waits."""
    before=[p.poll() for p in ps]
    for p,status in zip(ps,before):
        if status is None:
            try:os.killpg(p.pid,signal.SIGTERM)
            except ProcessLookupError:pass
    deadline=min(start+53,time.monotonic()+3.8)
    while any(p.poll() is None for p in ps) and time.monotonic()<deadline:time.sleep(.01)
    for p in ps:
        if p.poll() is None:
            try:os.killpg(p.pid,signal.SIGKILL)
            except ProcessLookupError:pass
    deadline=min(start+53.5,time.monotonic()+.5)
    while any(p.poll() is None for p in ps) and time.monotonic()<deadline:time.sleep(.005)
    return [{'before_cleanup':status,'returncode':p.poll()} for p,status in zip(ps,before)]
def main(trial):
    identities,pins=verify()
    spec=next(r for r in json.loads((HERE/'runs.json').read_text())['runs'] if r['id']==trial)
    pause=spec['condition']=='unknown_pause';port=9461;seed=spec['seed']
    model=None;amplitude=0.0;checkpoint_sha=None
    if spec['split']=='test':
        freeze=json.loads((HERE/'model_freeze.json').read_text())
        for name,h in freeze['files'].items():assert sha(HERE/name)==h,name
        model=json.loads((HERE/'trained_model.json').read_text());amplitude=freeze['amplitude']
        checkpoint_sha=sha(HERE/'trained_model.json')
    dst=HERE/'attempts'/trial;dst.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy();env.update(INTEGRATION_TRACE=str(dst/'events.jsonl'),INTEGRATION_PAUSE=str(int(pause)),GPIBT_R0_SEED=str(seed),R4_CONDITION=spec['condition'])
    env['LD_LIBRARY_PATH']='/home/lyh/.local/lib:'+env.get('LD_LIBRARY_PATH','')
    config=(OLD/'lsmart_smoke_03.argos').read_text().replace('9239',str(port))
    config=config.replace(str(OLD/'lsmart_compat/client/build'),str(OUT/'client_build')).replace('random_seed="42"',f'random_seed="{seed}"').replace('simDuration="200"','simDuration="400"')
    (dst/'experiment.argos').write_text(config)
    server=[str(OUT/'server_build/ExecutionManager'),'--num_robots=2',f'--port_number={port}',f'--output_file={dst}/stats.json','--save_stats=true','--screen=0','--total_sim_step_tick=400','--ticks_per_second=10','--look_ahead_dist=0','--look_ahead_tick=0',f'--seed={seed}','--sim_window_tick=10','--sim_window_timestep=1','--plan_window_timestep=1','--planner_invoke_policy=joint_settled','--backup_planner=PIBT',f'--map={HERE}/map.json','--grid_type=regular','--rotation=false','--task_assigner_type=one_goal']
    commands=[server,['argos3','-c',str(dst/'experiment.argos'),'--no-color'],[str(OUT/'gpibt_bridge')]]
    ps=[];logs=[];rpc=None;start=time.monotonic();error=None;decisions=[];events=[]
    def alarm(_sig,_frame):raise TimeoutError('49s blocking guard; cleanup reserved inside54s whole trial')
    signal.signal(signal.SIGALRM,alarm);signal.alarm(49)
    try:
        for i,args in enumerate(commands):
            log=(dst/f'process{i}.log').open('w');logs.append(log)
            p=subprocess.Popen(['rtk','proxy',*args],cwd=dst,env=env,stdout=subprocess.PIPE if i==2 else log,stderr=log,stdin=subprocess.PIPE if i==2 else subprocess.DEVNULL,text=True,start_new_session=True)
            ps.append(p)
            if i==0:
                for _ in range(50):
                    if p.poll() is not None:raise RuntimeError(f'server exit {p.returncode}')
                    try:rpc=RPC(port);break
                    except ConnectionRefusedError:time.sleep(.02)
                else:raise RuntimeError('server did not open')
        layout=json.loads((HERE/'map.json').read_text())['layout']
        while ps[1].poll() is None:
            try:
                if not rpc.call('is_initialized') or not rpc.call('invoke_planner'):
                    time.sleep(.0005);continue
                snapshot=json.loads(rpc.call('snapshot'));view=json.loads(rpc.call('get_location'))
                assert snapshot['joint_settled']
                delivered=read_events(dst/'events.jsonl')
                assert delivered[-1]['kind']=='view' and delivered[-1]['view']==view
                fc=forecast(context(delivered),view,layout,spec['policy'],model,amplitude)
                req={'mapf_instance':view['mapf_instance'],'rows':5,'cols':5,'map':[int(ch=='@') for row in layout for ch in row],'priority_bias':fc['bias']}
                ps[2].stdin.write(json.dumps(req)+'\n');ps[2].stdin.flush()
                line=ps[2].stdout.readline()
                if not line:raise RuntimeError(f'official planner stdout closed, status={ps[2].poll()}')
                result=json.loads(line);assert len(result['actions'])==2
                paths=[]
                for agent,action in enumerate(result['actions']):
                    assert action in range(5),action
                    s=view['mapf_instance']['starts'][agent]['location'];goal=view['mapf_instance']['goals'][agent][0]
                    t=s+[1,5,-1,-5,0][action]
                    assert 0<=t<25 and abs(t//5-s//5)+abs(t%5-s%5)<=1 and layout[t//5][t%5]!='@'
                    task=goal['id'] if t==goal['location'] else -1
                    paths.append([[s//5,s%5,0,task if t==s else -1],[t//5,t%5,1,-1 if t==s else task]])
                assert paths[0][1][:2]!=paths[1][1][:2]
                assert not(paths[0][0][:2]==paths[1][1][:2] and paths[1][0][:2]==paths[0][1][:2])
                proposal={'success':True,'plan':paths,'congested':False,'proposal_id':len(decisions),'view_sha256':hashlib.sha256(json.dumps(view,sort_keys=True).encode()).hexdigest()}
                decision={'snapshot':snapshot,'view':view,'request':req,'result':result,'proposal':proposal,'forecast':fc,'model_sha256':checkpoint_sha}
                decisions.append(decision)
                with (dst/'decisions.jsonl').open('a') as f:f.write(json.dumps(decision)+'\n')
                rpc.call('add_plan',json.dumps(proposal))
            except (EOFError,ConnectionResetError):break
        for p in ps[:2]:p.wait(timeout=3)
        if any(p.returncode for p in ps[:2]):raise RuntimeError('native nonzero exit')
        events=[json.loads(s) for s in (dst/'events.jsonl').read_text().splitlines()]
        assert any(e['kind']=='horizon' and e['tick']==400 for e in events),'no real400tick horizon'
    except Exception:error=traceback.format_exc()
    finally:
        signal.alarm(0)
        if rpc:rpc.close()
        status=collective_cleanup(ps,start)
        for f in logs:f.close()
        if not events and (dst/'events.jsonl').exists():events=[json.loads(s) for s in (dst/'events.jsonl').read_text().splitlines()]
        trigger=[e['tick'] for e in events if e['kind']=='control' and e['control']['phase']=='active_trigger']
        receipt={'trial':trial,'run_spec':spec,'commands':commands,'launch_prefix':['rtk','proxy'],'wall_seconds':time.monotonic()-start,'decisions':len(decisions),'error':error,'processes':status,'trigger_ticks':trigger,'actual_pause_ticks_inclusive':[trigger[0],trigger[0]+19] if pause and len(trigger)==1 else None,'protocol_sha256':pins['protocol_sha256'],'fixed_horizon_ticks':400,'ticks_per_second':10,'seed':seed,'blocking_guard_seconds':49,'whole_trial_limit_seconds_including_cleanup':54,'binary_identities':identities,'model_sha256':checkpoint_sha}
        if receipt['wall_seconds']>54 and error is None:receipt['error']='whole54s limit exceeded'
        receipt['files']={str(f.relative_to(dst)):sha(f) for f in dst.rglob('*') if f.is_file()}
        (dst/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps({k:v for k,v in receipt.items() if k not in ('commands','files','binary_identities')},indent=2),flush=True)
    return 1 if receipt['error'] else 0
if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('trial',nargs='?');parser.add_argument('--offline-check',action='store_true')
    args=parser.parse_args();assert bool(args.trial)!=args.offline_check
    if args.offline_check:
        ids,pins=verify(False);assert not (HERE/'attempts').exists()
        frozen=['PROTOCOL.md','runs.json','prepare.py','build.py','run_trial.py','common.py','gpibt_bridge.cpp','controller_condition.patch','source_manifest.json','native_source_tree_manifest.json','preflight_identity.json','binary_manifest.json','map.json']
        ready={'status':'READY_FOR_SPLIT_COLLECTION','verified_binary_and_objects':len(ids),'whole_trial_seconds':54,'frozen_files':{p:sha(HERE/p) for p in frozen}}
        with (HERE/'ready_for_trial.json').open('x') as f:json.dump(ready,f,indent=2);f.write('\n')
        print(json.dumps(ready,indent=2))
    else:raise SystemExit(main(args.trial))
