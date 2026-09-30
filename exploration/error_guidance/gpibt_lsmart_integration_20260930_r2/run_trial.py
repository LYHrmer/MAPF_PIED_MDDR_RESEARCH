"""Fixed bounded online pair: every official plan follows its real public view."""
import argparse, hashlib, json, os, signal, socket, subprocess, time, traceback
from pathlib import Path
import msgpack

HERE=Path(__file__).resolve().parent
OLD=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/baseline_selection_20260929')
OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_integration_20260930_r2')

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

def verify_binaries():
    ids=json.loads((HERE/'binary_manifest.json').read_text())
    for path,sha in ids.items():
        assert hashlib.sha256(Path(path).read_bytes()).hexdigest()==sha,path
    return ids

def main(trial):
    identities=verify_binaries()
    pause=int(trial.startswith('pause'));port=9251+pause
    dst=HERE/'attempts'/trial;dst.mkdir(parents=True,exist_ok=False)
    env=os.environ.copy();env.update(INTEGRATION_TRACE=str(dst/'events.jsonl'),INTEGRATION_PAUSE=str(pause),GPIBT_R0_SEED='42')
    env['LD_LIBRARY_PATH']='/home/lyh/.local/lib:'+env.get('LD_LIBRARY_PATH','')
    config=(OLD/'lsmart_smoke_03.argos').read_text().replace('9239',str(port))
    config=config.replace(str(OLD/'lsmart_compat/client/build'),str(OUT/'client_build'))
    (dst/'experiment.argos').write_text(config)
    server=[str(OUT/'server_build/ExecutionManager'),'--num_robots=2',f'--port_number={port}',f'--output_file={dst}/stats.json','--save_stats=true','--screen=0','--total_sim_step_tick=200','--ticks_per_second=10','--look_ahead_dist=0','--look_ahead_tick=0','--seed=42','--sim_window_tick=10','--sim_window_timestep=1','--plan_window_timestep=1','--planner_invoke_policy=joint_settled','--backup_planner=PIBT',f'--map={HERE}/map.json','--grid_type=regular','--rotation=false','--task_assigner_type=one_goal']
    commands=[server,['argos3','-c',str(dst/'experiment.argos'),'--no-color'],[str(OUT/'gpibt_bridge')]]
    ps=[];logs=[];rpc=None;start=time.monotonic();error=None;decisions=[]
    def alarm(_signal,_frame):raise TimeoutError('54 second whole-trial limit including socket/planner reads')
    signal.signal(signal.SIGALRM,alarm);signal.alarm(54)
    try:
        for i,args in enumerate(commands):
            log=(dst/f'process{i}.log').open('w');logs.append(log)
            p=subprocess.Popen(['rtk','proxy',*args],cwd=dst,env=env,stdout=subprocess.PIPE if i==2 else log,stderr=log,stdin=subprocess.PIPE if i==2 else subprocess.DEVNULL,text=True,start_new_session=True)
            ps.append(p)
            if i==0:
                for attempt in range(50):
                    if p.poll() is not None:raise RuntimeError(f'server exit {p.returncode}')
                    try:rpc=RPC(port);break
                    except ConnectionRefusedError:time.sleep(.02)
                else:raise RuntimeError('server did not open')
        layout=json.loads((HERE/'map.json').read_text())['layout']
        while ps[1].poll() is None:
            try:
                if not rpc.call('is_initialized') or not rpc.call('invoke_planner'):
                    time.sleep(.0005);continue
                snapshot=json.loads(rpc.call('snapshot'))
                view=json.loads(rpc.call('get_location'))
                assert snapshot['joint_settled']
                req={'mapf_instance':view['mapf_instance'],'rows':5,'cols':5,'map':[int(ch=='@') for row in layout for ch in row]}
                ps[2].stdin.write(json.dumps(req)+'\n');ps[2].stdin.flush()
                line=ps[2].stdout.readline()
                if not line:raise RuntimeError(f'official planner stdout closed, status={ps[2].poll()}')
                result=json.loads(line);assert len(result['actions'])==2
                paths=[]
                for agent,action in enumerate(result['actions']):
                    assert action in range(5),action
                    s=view['mapf_instance']['starts'][agent]['location']
                    goal=view['mapf_instance']['goals'][agent][0]
                    t=s+[1,5,-1,-5,0][action]
                    assert 0<=t<25 and abs(t//5-s//5)+abs(t%5-s%5)<=1 and layout[t//5][t%5]!='@'
                    task=goal['id'] if t==goal['location'] else -1
                    # Native parser discards duplicate final wait points.
                    initial_task=task if t==s else -1
                    final_task=-1 if t==s else task
                    paths.append([[s//5,s%5,0,initial_task],[t//5,t%5,1,final_task]])
                assert paths[0][1][:2]!=paths[1][1][:2]
                assert not(paths[0][0][:2]==paths[1][1][:2] and paths[1][0][:2]==paths[0][1][:2])
                proposal={'success':True,'plan':paths,'congested':False,'proposal_id':len(decisions),'view_sha256':hashlib.sha256(json.dumps(view,sort_keys=True).encode()).hexdigest()}
                decision={'snapshot':snapshot,'view':view,'request':req,'result':result,'proposal':proposal}
                decisions.append(decision)
                with (dst/'decisions.jsonl').open('a') as f:f.write(json.dumps(decision)+'\n')
                rpc.call('add_plan',json.dumps(proposal))
            except (EOFError,ConnectionResetError):break
        for p in ps[:2]:p.wait(timeout=3)
        if any(p.returncode for p in ps[:2]):raise RuntimeError('native nonzero exit')
        events=[json.loads(s) for s in (dst/'events.jsonl').read_text().splitlines()]
        assert any(e['kind']=='horizon' and e['tick']==200 for e in events),'no real200tick horizon'
    except Exception:error=traceback.format_exc()
    finally:
        signal.alarm(0)
        if rpc:rpc.close()
        status=[]
        for p in ps:
            before=p.poll()
            if before is None:
                try:os.killpg(p.pid,signal.SIGTERM)
                except ProcessLookupError:pass
                try:p.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    os.killpg(p.pid,signal.SIGKILL);p.wait(timeout=1)
            status.append({'before_cleanup':before,'returncode':p.returncode})
        for f in logs:f.close()
        receipt={'trial':trial,'commands':commands,'launch_prefix':['rtk','proxy'],'wall_seconds':time.monotonic()-start,'decisions':len(decisions),'error':error,'processes':status,'pause_agent':0 if pause else None,'pause_ticks_inclusive':[30,49] if pause else None,'fixed_horizon_ticks':200,'ticks_per_second':10,'seed':42,'binary_identities':identities}
        receipt['files']={str(f.relative_to(dst)):hashlib.sha256(f.read_bytes()).hexdigest() for f in dst.rglob('*') if f.is_file()}
        (dst/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
        print(json.dumps({k:v for k,v in receipt.items() if k not in ('commands','files','binary_identities')},indent=2),flush=True)
    return 1 if error else 0

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('trial',nargs='?',choices=['nominal','pause','nominal_retry01','pause_retry01','nominal_retry02','pause_retry02'])
    parser.add_argument('--fixed-pair',action='store_true')
    parser.add_argument('--offline-check',action='store_true')
    args=parser.parse_args()
    assert sum((bool(args.trial),args.fixed_pair,args.offline_check))==1,'select one fixed entry'
    if args.offline_check:
        identities=verify_binaries()
        assert not any(p.name in ('nominal','pause') for p in (HERE/'attempts').glob('*'))
        print(json.dumps({'status':'READY_FOR_FIXED_NATIVE_PAIR','verified_binary_and_objects':len(identities),'whole_trial_alarm_seconds':54,'pair_outer_timeout_seconds':120,'socket_execution_required':True},indent=2))
    else:
        for trial in (['nominal','pause'] if args.fixed_pair else [args.trial]):
            result=main(trial)
            if result:raise SystemExit(result)
