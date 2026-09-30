"""Static support selection, no R1 physics/eta/outcomes are inspected."""
from collections import deque
import hashlib,itertools,json
from pathlib import Path

HERE=Path(__file__).resolve().parent
QUERY=HERE.parent
PARENT=QUERY/'public_trace_20260930_r2'
SOURCE=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/baseline_selection_20260929/pied_run_01/result.json')
DELTA={'EA':(1,0),'WE':(-1,0),'NO':(0,-1),'SO':(0,1),'W':(0,0)}

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,obj):
    with p.open('x') as f:json.dump(obj,f,indent=2);f.write('\n')

def prepare():
    assert sha(SOURCE)=='67c10baa0faa4b10200591982d970368c6f8292e87959a47b8f7d0d832849b10'
    d=json.loads(SOURCE.read_text());goals={tid:(c,r) for tid,r,c in d['tasks']};paths=[s.split(',') for s in d['actualPaths']]
    states=[[(c,r) for r,c,_ in d['start']]]
    for t in range(20):states.append([(x+DELTA[paths[a][t]][0],y+DELTA[paths[a][t]][1]) for a,(x,y) in enumerate(states[-1])])
    chosen=None
    for t in range(20):
        rows={}
        for a,ev in enumerate(d['events']):
            queue=deque();assigned={}
            for tid,at,k in ev:
                if at>t:break
                if k=='assigned':queue.append(tid);assigned[tid]=at
                else:assert queue.popleft()==tid
            if not queue:continue
            head=queue[0];end=next((at for tid,at,k in ev if tid==head and k=='finished' and at>t),None)
            if end is None or goals[head]==states[t][a] or paths[a][t]=='W':continue
            rows[a]={'agent':a,'task':head,'goal':list(goals[head]),'start':list(states[t][a]),
                     'source_assigned_tick':assigned[head],'source_finish_tick':end,'route':paths[a][t:end],
                     'route_points':[list(states[k][a]) for k in range(t,end+1)],
                     'source_revealed_queue':list(queue),'route_cell_set':set(states[k][a] for k in range(t,end+1))}
        pairs=[(a,b) for b in rows for a in rows if a!=b and states[t+1][b]==states[t][a] and states[t+1][a]!=states[t][b]]
        for p,q in itertools.combinations(pairs,2):
            aa=sorted(set(p+q))
            if len(aa)!=4:continue
            if any(states[t+1][a] in [states[t][b] for b in aa if b!=a] for a in [p[0],q[0]]):continue
            seen={aa[0]}
            for _ in aa:seen|={b for b in aa if any(rows[b]['route_cell_set']&rows[a]['route_cell_set'] for a in seen)}
            if len(seen)!=4:continue
            chosen={'source_tick':t,'agents':aa,'initial_follow_pairs':[list(p),list(q)],'robots':[rows[a] for a in aa]};break
        if chosen:break
    assert chosen and chosen['source_tick']==4 and chosen['agents']==[7,11,49,59]
    cells=set()
    for row in chosen['robots']:cells|=row.pop('route_cell_set')
    chosen.update(source=str(SOURCE),source_sha256=sha(SOURCE),source_commit='74cfba3c81a0c165c2e7044dea6fd4dee8ddf415',
        resource_cells=[list(p) for p in sorted(cells)],only_current_heads=True,future_tasks_replenished=False,
        selection='earliest source tick, first source-order pair pair with 4 distinct robots, two initial unblocked sources, current-head routes connected by cell intersection; no R1 execution outcome used')
    training=json.loads((PARENT/'semantic_successor_20260930_r2/end_only_replay_20260930_r2.json').read_text())
    obs=[o for o in training['actor_observations'] if o['run_id'] in ['train_1103','train_2207']]
    assert len(obs)==3582 and all(set(o)=={'run_id','tick','agent','heading','original_END','received','full_cap_uninterrupted','length'} for o in obs)
    write(HERE/'support_20260930_r3.json',chosen);write(HERE/'public_training_END_20260930_r3.json',obs)
    source_lines=[]
    for x,y in chosen['resource_cells']:source_lines.append(f'C {x} {y}')
    for r in chosen['robots']:
        source_lines.append(' '.join(map(str,['R',r['agent'],r['task'],*r['start'],*r['goal'],','.join(r['route'])])))
    for o in obs:
        e=o['original_END'];source_lines.append(' '.join(map(str,['H',o['heading'],e['lower'],e['upper'],e['denominator'],o['length'],int(o['full_cap_uninterrupted'])])))
    with (HERE/'public_native_input_20260930_r3.txt').open('x') as f:f.write('\n'.join(source_lines)+'\n')
    protected={str(p.relative_to(QUERY)):sha(p) for p in QUERY.iterdir() if p.is_file()}
    protected.update({str(p.relative_to(QUERY)):sha(p) for p in PARENT.rglob('*') if p.is_file()})
    write(HERE/'protected_before_20260930_r3.json',protected)
    print(json.dumps({k:v for k,v in chosen.items() if k!='robots'},indent=2))

if __name__=='__main__':prepare()
