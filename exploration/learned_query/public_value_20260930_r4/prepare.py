from collections import deque,Counter
import hashlib,itertools,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def write(p,o):
    with p.open('x') as f:json.dump(o,f,indent=2);f.write('\n')
def scan(source):
    d=json.loads(source.read_text());D={'EA':(1,0),'WE':(-1,0),'NO':(0,-1),'SO':(0,1),'W':(0,0)}
    paths=[s.split(',') for s in d['actualPaths']];states=[[(c,r) for r,c,_ in d['start']]]
    for t in range(len(paths[0])):states.append([(x+D[paths[a][t]][0],y+D[paths[a][t]][1]) for a,(x,y) in enumerate(states[-1])])
    goals={tid:(c,r) for tid,r,c in d['tasks']};groups={}
    for t in range(len(paths[0])):
        rows={}
        for a,ev in enumerate(d['events']):
            q=deque();assigned={}
            for tid,at,k in ev:
                if at>t:break
                if k=='assigned':q.append(tid);assigned[tid]=at
                else:assert q.popleft()==tid
            if not q:continue
            tid=q[0];finish=next((at for i,at,k in ev if i==tid and k=='finished' and at>t),None)
            if finish is None or finish-t>16 or goals[tid]==states[t][a] or paths[a][t]=='W' or tid in [14,22,99,118]:continue
            rows[a]=dict(agent=a,task=tid,goal=list(goals[tid]),start=list(states[t][a]),source_assigned_tick=assigned[tid],
                source_finish_tick=finish,route=paths[a][t:finish],route_points=[list(states[k][a]) for k in range(t,finish+1)],source_revealed_queue=list(q))
        pairs=[(a,b) for b in rows for a in rows if a!=b and states[t+1][b]==states[t][a] and states[t+1][a]!=states[t][b]]
        for u,v in itertools.combinations(pairs,2):
            aa=sorted(set(u+v))
            if len(aa)!=4:continue
            if any(states[t+1][a] in [states[t][b] for b in aa if b!=a] for a in [u[0],v[0]]):continue
            sets={a:set(map(tuple,rows[a]['route_points'])) for a in aa};seen={aa[0]}
            for _ in aa:seen|={b for b in aa if any(sets[b]&sets[a] for a in seen)}
            if len(seen)!=4:continue
            tt=tuple(sorted(rows[a]['task'] for a in aa))
            groups.setdefault(tt,dict(source_tick=t,agents=aa,initial_follow_pairs=[list(u),list(v)],robots=[rows[a] for a in aa],
                resource_cells=[list(x) for x in sorted(set().union(*[sets[a] for a in aa]))],source=str(source),source_sha256=sha(source),task_group=list(tt)))
    return groups
def main():
    source=HERE/'author_60.json';groups=scan(source);selected=[];used=set()
    for k,c in groups.items():
        if set(k)&used:continue
        c['cohort_id']=f'cohort_{len(selected):02d}';c['split']=['train','train','train','calibration','test'][len(selected)%5]
        selected.append(c);used.update(k)
        if len(selected)==15:break
    result=dict(source_sha256=sha(source),unique_connected_task_groups=len(groups),selected_task_disjoint_cohorts=len(selected),
       split_counts=dict(Counter(c['split'] for c in selected)),cohorts=selected,task_disjoint=True,excluded_R3_tasks=[14,22,99,118],source_maps=1)
    write(HERE/'SUPPORT_AUDIT_60.json',result);print({k:v for k,v in result.items() if k!='cohorts'})
if __name__=='__main__':main()
