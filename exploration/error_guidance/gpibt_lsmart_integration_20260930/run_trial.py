"""Bounded online RPC orchestration. No plan is computed before its view."""
import json, os, socket, subprocess, time, hashlib, sys, signal, traceback
from pathlib import Path
import msgpack
HERE=Path(__file__).resolve().parent
OLD=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/baseline_selection_20260929')
OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_integration_20260930')
class RPC:
    def __init__(self,port):
        self.s=socket.create_connection(('127.0.0.1',port),timeout=2)
        self.u=msgpack.Unpacker(raw=False);self.seq=0
    def call(self,name,*args):
        self.seq+=1; seq=self.seq
        self.s.sendall(msgpack.packb([0,seq,name,list(args)],use_bin_type=True))
        while True:
            for msg in self.u:
                assert msg[0]==1 and msg[1]==seq,msg
                if msg[2] is not None: raise RuntimeError(msg[2])
                return msg[3]
            data=self.s.recv(1<<20)
            if not data: raise EOFError('server closed')
            self.u.feed(data)

def main(trial):
    pause=int(trial.startswith('pause')); port=9241+pause
    dst=OUT/trial;dst.mkdir(exist_ok=False)
    env=os.environ.copy();env.update(INTEGRATION_TRACE=str(dst/'events.jsonl'),INTEGRATION_PAUSE=str(pause),GPIBT_R0_SEED='42')
    env['LD_LIBRARY_PATH']='/home/lyh/.local/lib:'+env.get('LD_LIBRARY_PATH','')
    config=(OLD/'lsmart_smoke_03.argos').read_text().replace('9239',str(port))
    config=config.replace(str(OLD/'lsmart_compat/client/build'),str(OUT/'client_build'))
    (dst/'experiment.argos').write_text(config)
    server=[str(OUT/'server_build/ExecutionManager'),'--num_robots=2',f'--port_number={port}',f'--output_file={dst}/stats.json','--save_stats=true','--screen=0','--total_sim_step_tick=200','--ticks_per_second=10','--look_ahead_dist=0','--look_ahead_tick=0','--seed=42','--sim_window_tick=10','--sim_window_timestep=1','--plan_window_timestep=1','--planner_invoke_policy=joint_settled','--backup_planner=PIBT',f'--map={HERE}/map.json','--grid_type=regular','--rotation=false','--task_assigner_type=one_goal']
    commands=[server,['argos3','-c',str(dst/'experiment.argos'),'--no-color'],[str(OUT/'gpibt_bridge')]]
    ps=[];logs=[];start=time.monotonic(); error=None; decisions=[]
    def alarm(_signal,_frame):
        raise TimeoutError('54 second process-wide trial limit, including blocking RPC/planner reads')
    signal.signal(signal.SIGALRM,alarm)
    signal.alarm(54)
    try:
        for i,args in enumerate(commands):
            log=(dst/f'process{i}.log').open('w');logs.append(log)
            p=subprocess.Popen(args,cwd=dst,env=env,stdout=subprocess.PIPE if i==2 else log,stderr=log,stdin=subprocess.PIPE if i==2 else subprocess.DEVNULL,text=True,start_new_session=True)
            ps.append(p)
            if i==0:
                for attempt in range(50):
                    if p.poll() is not None: raise RuntimeError(f'server exit {p.returncode}')
                    try: rpc=RPC(port);break
                    except ConnectionRefusedError: time.sleep(.02)
                else: raise RuntimeError('server did not open')
        layout=json.loads((HERE/'map.json').read_text())['layout']
        while ps[1].poll() is None:
            if time.monotonic()-start>55: raise TimeoutError('integration budget55s')
            try:
                if not rpc.call('is_initialized') or not rpc.call('invoke_planner'):
                    time.sleep(.0005);continue
                snapshot=json.loads(rpc.call('snapshot'))
                view=json.loads(rpc.call('get_location'))
                assert snapshot['joint_settled']
                req={'mapf_instance':view['mapf_instance'],'rows':5,'cols':5,'map':[int(ch=='@') for row in layout for ch in row]}
                ps[2].stdin.write(json.dumps(req)+'\n');ps[2].stdin.flush()
                result=json.loads(ps[2].stdout.readline())
                paths=[]
                for agent,action in enumerate(result['actions']):
                    s=view['mapf_instance']['starts'][agent]['location']
                    goal=view['mapf_instance']['goals'][agent][0]
                    t=s+[1,5,-1,-5,0][action]
                    assert t//5 in range(5) and t%5 in range(5) and layout[t//5][t%5]!='@'
                    task=goal['id'] if t==goal['location'] else -1
                    paths.append([[s//5,s%5,0,-1],[t//5,t%5,1,task]])
                proposal={'success':True,'plan':paths,'congested':False,'proposal_id':len(decisions),'view_sha256':hashlib.sha256(json.dumps(view,sort_keys=True).encode()).hexdigest()}
                decisions.append({'snapshot':snapshot,'view':view,'result':result,'proposal':proposal})
                with (dst/'decisions.jsonl').open('a') as f:f.write(json.dumps(decisions[-1])+'\n')
                rpc.call('add_plan',json.dumps(proposal))
            except (EOFError,ConnectionResetError):
                break
        for p in ps[:2]:p.wait(timeout=3)
        if any(p.returncode for p in ps[:2]):raise RuntimeError('native nonzero exit')
    except Exception:
        error=traceback.format_exc()
    finally:
        signal.alarm(0)
        status=[]
        for p in ps:
            before=p.poll()
            if before is None:
                os.killpg(p.pid,signal.SIGTERM)
                try:p.wait(timeout=2)
                except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
            status.append({'before_cleanup':before,'returncode':p.returncode})
        for f in logs:f.close()
        receipt={'trial':trial,'commands':commands,'wall_seconds':time.monotonic()-start,'decisions':len(decisions),'error':error,'processes':status,'pause_agent':0 if pause else None,'pause_ticks':[30,50] if pause else None}
        receipt['files']={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in dst.iterdir() if f.is_file()}
        (dst/'receipt.json').write_text(json.dumps(receipt,indent=2))
        print(json.dumps({k:v for k,v in receipt.items() if k not in ('commands','files')},indent=2))
    return 1 if error else 0
if __name__=='__main__':
    trials=['nominal_final','pause_final'] if sys.argv[1]=='--fixed-pair' else [sys.argv[1]]
    for trial in trials:
        result=main(trial)
        if result:raise SystemExit(result)
