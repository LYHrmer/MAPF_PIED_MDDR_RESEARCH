"""Complete-grid/input binding plus additional real receipt corruption controls."""
from copy import deepcopy
import hashlib,json
from pathlib import Path
from audit_20260930_r3 import HERE,QUERY,Replay,decode,sha,require

def main():
    attempt=HERE/'attempt_01';reg=json.loads((attempt/'registration.json').read_text());receipt=json.loads((attempt/'receipt.json').read_text())
    sup=json.loads((HERE/'support_20260930_r3.json').read_text());training=json.loads((HERE/'public_training_END_20260930_r3.json').read_text())
    parent=json.loads((QUERY/'public_trace_20260930_r2/semantic_successor_20260930_r2/end_only_replay_20260930_r2.json').read_text())
    require(training==[x for x in parent['actor_observations'] if x['run_id'] in ['train_1103','train_2207']],'training original frozen public END binding')
    condition={c['name']:c for c in reg['conditions']}
    expected_names={f'first7_{a}_first49_{b}' for a in [-1,1] for b in [-1,1]}|{'all_eta0','direction_IID','direction_reverse'}
    require(set(condition)==expected_names,'all factors and two fixed seeds retained')
    expected_grid={(c,p,b) for c in expected_names for p,b in [['WAIT',0]]+[[p,b] for p in ['RR','task_rank','global_task','task_trigger'] for b in [1,2]]}
    actual_grid=[(e['condition'],e['policy'],e['capacity']) for e in receipt['episodes']]
    require(len(actual_grid)==63 and set(actual_grid)==expected_grid,'all whole-run grid cells unique/complete')
    public=(HERE/'public_native_input_20260930_r3.txt').read_text();private_bound=0
    for name,c in condition.items():
        expected=[]
        for r in sup['robots']:
            for leg,h in enumerate(r['route']):
                eta=0
                if name.startswith('first7_') and leg==0 and r['agent'] in [7,49]:
                    eta=int(name.split('_')[1 if r['agent']==7 else 3])
                elif name.startswith('direction_') and h!='W':
                    seed=4409 if name=='direction_IID' else 5501
                    word=hashlib.sha256(f'{seed}:{r["agent"]}:{leg}'.encode()).digest()[:8]
                    v=int.from_bytes(word,'big')%10;preferred=-1 if h in ['NO','SO'] else 1
                    if name=='direction_reverse':preferred=-preferred
                    eta=preferred if v<9 else -preferred
                expected.append(dict(agent=r['agent'],leg=leg,heading=h,eta=eta))
        require(expected==c['private_world_only'],'predeclared per-leg exogenous factors')
        text=public+''.join(f'E {x["agent"]} {x["leg"]} {x["eta"]}\n' for x in expected)
        require(Path(c['input']).read_text()==text,'native public/private input exact binding')
        private_bound+=len(expected)
    key=('first7_1_first49_1','RR',1)
    ep=next(e for e in receipt['episodes'] if (e['condition'],e['policy'],e['capacity'])==key)
    base=[json.loads(x) for x in Path(ep['raw']).read_text().splitlines()];tests=[]
    bad=deepcopy(base);next(x for x in bad if x['event']=='actor_decision')['selected']='m-49-0';tests.append(('false actor choice',bad))
    bad=deepcopy(base);x=next(x for x in bad if x['event']=='certified_POSITION_committed');x['certified_lower']={'lower':0,'upper':0,'denominator':1000000};tests.append(('certificate private physics mismatch',bad))
    bad=deepcopy(base);next(x for x in bad if x['event']=='public_END_delivered')['progress']=.9;tests.append(('private progress END schema leak',bad))
    bad=deepcopy(base);i=next(i for i,x in enumerate(bad) if x['event']=='physical_original_END');bad.pop(i);tests.append(('deleted original END',bad))
    negative=[]
    for name,records in tests:
        try:Replay(sup,condition[key[0]],key[1],key[2],training).run(records)
        except AssertionError as e:negative.append(dict(test=name,rejected=True,reason=str(e)))
        else:raise AssertionError('corruption not rejected '+name)
    result=dict(status='passed',complete_unique_joint_episodes=63,private_leg_inputs_bound=private_bound,
        training_public_END_rows_bound=3582,first_audit_sha256=sha(HERE/'AUDIT_20260930_r3.json'),
        first_audit_source_sha256=sha(HERE/'audit_20260930_r3.py'),hardened_source_sha256=sha(Path(__file__)),mutation_controls=negative)
    with (HERE/'AUDIT_HARDENED_20260930_r3.json').open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps(result,indent=2))
if __name__=='__main__':main()
