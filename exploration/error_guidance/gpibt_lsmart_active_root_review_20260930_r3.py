"""Root replay of raw activity, stopping, normal ACK and real task service."""
from collections import deque
import hashlib
import importlib.util
import json
import math
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE/'gpibt_lsmart_active_20260930_r3'
def read(p):return json.loads(p.read_text())
def rows(p):return [json.loads(x) for x in p.read_text().splitlines()]
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def run():
    for path,digest in read(ROOT/'binary_manifest.json').items():assert sha(path)==digest
    frozen=ROOT/'artifact_manifest.json'
    if frozen.exists():
        for path,digest in read(frozen).items():assert sha(ROOT/path)==digest
    result={}
    for trial in ['nominal','pause']:
        p=ROOT/'attempts'/trial
        receipt=read(p/'receipt.json')
        assert receipt['error'] is None and receipt['fixed_horizon_ticks']==200
        for file,digest in receipt['files'].items():assert sha(p/file)==digest
        events=rows(p/'events.jsonl')
        obs={};wheels={};queue=deque();eligible=[];ends={};admitted={};task_ends=[]
        for event in events:
            kind=event['kind'];tick=event['tick'];robot=event.get('robot')
            if kind=='admit':
                for command in event['actions']:
                    admitted[(command[0],command[1])]=command
                    if command[0]=='0':queue.append(command)
            elif kind=='observation':
                o=event['observation'];obs[(robot,tick)]=o
                if tick>0:
                    prev=obs[(robot,tick-1)];actual=wheels[(robot,tick-1)]
                    displacement=math.hypot(o['x']-prev['x'],o['y']-prev['y'])
                    assert abs(displacement-o['displacement_m'])<1e-12
                    assert o['previous_wheel_left_cm_s']==actual['issued_left_cm_s']
                    assert o['previous_wheel_right_cm_s']==actual['issued_right_cm_s']
                    if robot=='0' and queue and queue[0][3]=='M' and displacement>1e-6 and (
                        actual['issued_left_cm_s']!=0 or actual['issued_right_cm_s']!=0):
                        eligible.append(tick)
            elif kind=='control' and event['control']['phase']=='wheel_command':
                wheels[(robot,tick)]=event['control']
            elif kind=='end':
                ends[(robot,event['node'])]=event
                if robot=='0':
                    assert queue[0][1]==event['node'];queue.popleft()
                if event['task']:task_ends.append(event)
        assert len(obs)==len(wheels)==400 and eligible[0]==59
        assert ends[('0',2)]['tick']==(88 if trial=='pause' else 68)
        assert len(task_ends)==1
        task=task_ends[0];assert task['robot']=='1' and task['task_id']==1
        t=156 if trial=='pause' else 136
        assert task['tick']==t
        cmd=admitted[('1',task['node'])];assert cmd[3]=='S' and cmd[-1]==1
        # Public map coordinates convert (row,col) to (-col,-row) in this adapter.
        x,y=-cmd[5][1],-cmd[5][0]
        residence=[obs[('1',k)] for k in range(t-20,t+1)]
        assert all(math.hypot(o['x']-x,o['y']-y)<=.03 for o in residence)
        if trial=='pause':
            for tick in range(59,79):
                c=wheels[('0',tick)]
                assert c['issued_left_cm_s']==c['issued_right_cm_s']==0
                assert c['nodes']==[2] and c['queue_size']>0 and c['target_x']==-.5 and c['target_y']==0
            assert wheels[('0',79)]['issued_left_cm_s']!=0 or wheels[('0',79)]['issued_right_cm_s']!=0
            assert all(not(e['kind']=='end' and e.get('robot')=='0' and 59<=e['tick']<79) for e in events)
            assert obs[('0',60)]['displacement_m']>0
        contexts=rows(ROOT/f'datasets/{trial}/delivered_context.jsonl')
        targets=rows(ROOT/f'datasets/{trial}/offline_targets.jsonl')
        assert len(contexts)==len(targets)==400
        for c,targ in zip(contexts,targets):
            assert all(c[k]==targ[k] for k in ['agent','tick','freeze_sequence','trial'])
            f=c['features'];assert not any(k in f for k in ['actual_sample_xy_m','signed_progress_m','future_node_ACKs'])
            pose=obs[(c['agent'],c['tick'])]
            assert targ['actual_sample_xy_m']==[pose['x'],pose['y']]
        result[trial]={'first_actual_MOVE_trigger':eligible[0],'original_node_ACK':ends[('0',2)]['tick'],
                       'task1_completed':task['tick'],'residence_samples':len(residence),
                       'observations':len(obs),'causal_context_rows':len(contexts),
                       'post_stop_inertia_m':obs[('0',60)]['displacement_m'] if trial=='pause' else None}
    out={'passed':True,'trials':result,'continuous_footprint_safety_proved':False,
         'learning_benefit_established':False,'verifier_sha256':sha(Path(__file__))}
    (HERE/'gpibt_lsmart_active_root_review_20260930_r3.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))

if __name__=='__main__':run()
