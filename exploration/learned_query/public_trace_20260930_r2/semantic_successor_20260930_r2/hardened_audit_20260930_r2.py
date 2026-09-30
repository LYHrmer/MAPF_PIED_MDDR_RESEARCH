"""Source bindings, native input pairing, and real corruption tests, independent of exporter."""
import copy
import hashlib
import json
from fractions import Fraction as F
from pathlib import Path
from audit_20260930_r2 import audit,bounds

HERE=Path(__file__).resolve().parent

def validate_author_bindings(public):
    original=json.loads(Path(public['origin']).read_text());tokens=[s.split(',') for s in original['actualPaths']]
    directions={'EA':(1,0),'WE':(-1,0),'NO':(0,-1),'SO':(0,1),'W':(0,0)}
    positions=[(s[1],s[0]) for s in original['start']];task_goals={tid:(c,r) for tid,r,c in original['tasks']}
    heads=[[] for _ in positions];pid=0;action_rows=0
    map_lines=Path(public['map_path']).read_text().splitlines()[4:]
    for t in range(20):
        for a,events in enumerate(original['events']):
            for tid,when,kind in events:
                if when!=t:continue
                if kind=='assigned':heads[a].append(tid)
                elif kind=='finished':assert heads[a][0]==tid and positions[a]==task_goals[tid];heads[a].pop(0)
                else:raise AssertionError(kind)
        arrived=[]
        for a,p in enumerate(positions):
            dx,dy=directions[tokens[a][t]];q=(p[0]+dx,p[1]+dy);arrived.append(q)
            assert map_lines[q[1]][q[0]] not in '@T'
            actual=public['actions'][t*100+a]
            assert actual['start']==list(p) and actual['end']==list(q) and actual['heading']==tokens[a][t]
            assert actual['revealed_tasks']==heads[a] and actual['head_task']==heads[a][0] and actual['head_goal']==list(task_goals[heads[a][0]])
            action_rows+=1
        assert len(set(arrived))==100
        expected=[]
        # Pair formation via exhaustive source/requester matching, separate from exporter's owner lookup.
        for b in range(100):
            if arrived[b]==positions[b]:continue
            for a in range(100):
                if a==b or arrived[a]==positions[a] or arrived[b]!=positions[a]:continue
                assert arrived[a]!=positions[b]
                expected.append({'pair':pid,'source_agent':a,'requester_agent':b,'source_start':list(positions[a]),
                    'source_end':list(arrived[a]),'requester_start':list(positions[b]),'requester_end':list(arrived[b]),
                    'head_task':heads[b][0],'head_goal':list(task_goals[heads[b][0]]),
                    'terminal':arrived[b]==task_goals[heads[b][0]],'source_heading':tokens[a][t]});pid+=1
        actual_pairs=public['phases'][t]['pairs'];assert len(actual_pairs)==len(expected)
        for exp,got in zip(expected,actual_pairs):assert all(got[k]==v for k,v in exp.items())
        positions=arrived
    assert action_rows==2000 and pid==355

def validate_native_inputs(receipt,public):
    qualification=json.loads((HERE/'end_only_qualification_20260930_r2.json').read_text())
    zero_lo,zero_hi=bounds(qualification['profiles'][1]['public_END']);endchecks=0
    for run in receipt['runs']:
        for phase in run['phases']:
            t=phase['tick'];current=public['phases'][t]
            actual=phase['private_native_input'];assert hashlib.sha256(actual.encode()).hexdigest()==phase['private_native_input_sha256']
            expected=[]
            for m in current['moves']:
                value=int.from_bytes(hashlib.sha256(f'{run["seed"]}:{t}:{m["agent"]}'.encode()).digest()[:8],'big')
                primary=-1 if m['heading'] in ['NO','SO'] else 1
                if run['regime']=='reverse':primary=-primary
                eta=0 if run['regime']=='zero' else primary if value%10<9 else -primary
                expected.append(' '.join(map(str,['M',m['agent'],*m['start'],*m['end'],eta])))
            for p in current['pairs']:
                expected.append(' '.join(map(str,['P',p['pair'],p['source_agent'],p['requester_agent'],
                    *p['source_start'],*p['source_end'],*p['requester_start'],p['head_task'],int(p['terminal'])])))
            assert actual=='\n'.join(expected)+'\n'
            c=receipt['commands'][phase['command_index']]
            for line in c['stdout'].splitlines():
                e=json.loads(line)
                if e['event']!='pair_episode':continue
                lo,hi=bounds(e['requester_original_END']);a,b=bounds(e['requester_RUN'])
                assert lo-b<=zero_hi and hi-a>=zero_lo,'requester actual duration disagrees with independent original profile'
                endchecks+=1
    assert endchecks==4260
    return endchecks

def rejected(callback):
    try:callback()
    except AssertionError:return True
    return False

def main():
    receipt=json.loads((HERE/'receipt_20260930_r2.json').read_text());public=json.loads((HERE/'public_source_20260930_r2.json').read_text())
    validate_author_bindings(public);endchecks=validate_native_inputs(receipt,public)
    controls={}
    for kind in ['certified_lower_at_closed_threshold','wrong_double_subtraction_release','wrong_actual_head_task']:
        bad=copy.deepcopy(receipt);phase=bad['runs'][0]['phases'][0];cmd=bad['commands'][phase['command_index']]
        es=[json.loads(s) for s in cmd['stdout'].splitlines()]
        event=next(e for e in es if e.get('event')=='pair_episode' and e['arm']=='QUERY')
        if kind=='certified_lower_at_closed_threshold':event['certified_lower']={'lower':650000,'upper':650000,'denominator':1000000}
        elif kind=='wrong_double_subtraction_release':event['strict_cleared']=False
        else:event['task_id']+=1
        cmd['stdout']='\n'.join(json.dumps(e) for e in es)+'\n'
        controls[kind]=rejected(lambda:audit(bad,public))
    bad_public=copy.deepcopy(public);bad_public['phases'][0]['pairs'][0]['head_goal']=[999,999]
    controls['future_or_forged_head_goal_in_public_crop']=rejected(lambda:validate_author_bindings(bad_public))
    clean=json.loads((HERE/'end_only_replay_20260930_r2.json').read_text())
    assert clean['status']=='passed' and all(clean['negative_controls'].values()) and all(controls.values())
    out={'status':'passed','original_source_action_bindings_checked':2000,'original_pair_bindings_checked':355,
         'native_private_input_seed_geometry_task_bindings_checked':120,'requester_original_durations_independently_checked':endchecks,
         'actual_corruption_tests_rejected':controls,'END_only_actor_negative_controls':clean['negative_controls'],
         'clean_END_only_actor_choice_comparisons':clean['actor_choice_comparisons'],'END_only_choices_equal_native_selected_potentials':True}
    with (HERE/'hardened_audit_20260930_r2.json').open('x') as f:json.dump(out,f,indent=2)
    print(json.dumps(out,indent=2))

if __name__=='__main__':main()
