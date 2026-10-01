"""Only allowlisted public events enter this module; no physical/control fields."""
from collections import deque
from pathlib import Path
import hashlib, json, math, statistics

def nominal(turns): return 45. + 10. * turns

def turn_count(orientation, direction):
    # Author planner orientations E,S,W,N = 0,1,2,3.
    delta = abs(orientation - direction)
    return min(delta, 4 - delta)

def feature(history, agent, direction, turns):
    hs = [r for r in history if r['agent'] == agent][-16:]
    ds = [r for r in hs if r['direction'] == direction][-8:]
    residuals = [r['duration'] - nominal(r['turns']) for r in hs]
    dr = [r['duration'] - nominal(r['turns']) for r in ds]
    avg = statistics.mean(residuals) if residuals else 0.
    sm = sum(dr)/(len(dr)+2)
    return [turns/2., *[float(direction == k) for k in range(4)],
            len(hs)/16., avg/50., sm/50., (residuals[-1] if residuals else 0.)/50.,
            (statistics.pstdev(residuals) if len(residuals)>1 else 0.)/50.]

FEATURES = ['quarter_turns/2','east','south','west','north','history_count/16',
            'mean_residual/50','direction_shrunk_residual/50','last_residual/50','residual_sd/50']

def predict(x, turns, policy, model=None):
    residual = x[7]*50.
    if policy == 'learned':
        residual = model['intercept'] + sum(w*(v-m)/s for w,v,m,s in zip(model['coef'],x,model['mean'],model['scale']))
    return max(5., min(200., nominal(turns)+residual))

class PublicHistory:
    def __init__(self):
        self.rows=[]; self.moves={}; self.node_moves={}; self.last_view=None
        self.offset=0; self.last_sequence=-1; self.projected=[]

    def ingest(self, path):
        # File reads may encounter a partial final line. Nothing is accepted
        # until its newline arrives. Projection removes every private field.
        with Path(path).open() as f:
            f.seek(self.offset)
            while True:
                pos=f.tell(); line=f.readline()
                if not line or not line.endswith('\n'): break
                self.offset=f.tell(); e=json.loads(line); k=e['kind']
                if k not in ('view','proposal','admit','end'): continue
                if k=='view': z={q:e[q] for q in ('kind','tick','sequence','view')}
                elif k=='proposal': z={q:e[q] for q in ('kind','tick','sequence','proposal')}
                elif k=='admit': z={q:e[q] for q in ('kind','tick','sequence','robot','actions')}
                else: z={q:e[q] for q in ('kind','tick','sequence','robot','node','accepted')}
                self.accept(z)

    def accept(self, e):
        allowed={'view':{'kind','tick','sequence','view'}, 'proposal':{'kind','tick','sequence','proposal'},
                 'admit':{'kind','tick','sequence','robot','actions'}, 'end':{'kind','tick','sequence','robot','node','accepted'}}
        assert set(e)==allowed[e['kind']] and e['sequence']>self.last_sequence
        self.last_sequence=e['sequence']; self.projected.append(e); k=e['kind']
        if k=='view': self.last_view=e['view']
        elif k=='proposal':
            pid=e['proposal']['proposal_id']; inst=self.last_view['mapf_instance']
            for a,p in enumerate(e['proposal']['plan']):
                s,t=p; delta=(t[0]-s[0],t[1]-s[1])
                if delta==(0,0):continue
                d={(0,1):0,(1,0):1,(0,-1):2,(-1,0):3}[delta]
                turns=turn_count(inst['starts'][a]['orientation'],d)
                self.moves[(pid,a)]={'proposal_id':pid,'agent':a,'direction':d,'turns':turns,
                    'proposal_tick':e['tick'],'goal':[t[1],t[0]],'features':feature(self.rows,a,d,turns),
                    'history_cutoff_sequence':e['sequence'],'duration':None,'final_node':None}
            self.pid=pid
        elif k=='admit':
            a=int(e['robot']); move=self.moves.get((self.pid,a))
            if move:
                for c in e['actions']:
                    if c[3]=='M' and c[5]==move['goal']:
                        move['final_node']=c[1];self.node_moves[(a,c[1])]=move
        elif k=='end':
            move=self.node_moves.get((int(e['robot']),e['node']))
            if move:
                assert e['accepted'] and move['duration'] is None
                move['duration']=e['tick']-move['proposal_tick'];move['end_tick']=e['tick'];move['end_sequence']=e['sequence']
                assert move['duration']>0 and move['end_sequence']>move['history_cutoff_sequence']
                self.rows.append(dict(move))

def distances(layout, goal):
    cols=len(layout[0]); n=len(layout)*cols; ds={goal:0}; queue=deque([goal])
    while queue:
        s=queue.popleft()
        for v in (s+1,s+cols,s-1,s-cols):
            if 0<=v<n and abs(v//cols-s//cols)+abs(v%cols-s%cols)==1 and layout[v//cols][v%cols]!='@' and v not in ds:
                ds[v]=ds[s]+1;queue.append(v)
    return ds

def forecast(hist, view, layout, policy, checkpoint):
    inst=view['mapf_instance']; n=len(inst['starts']); cols=len(layout[0]); size=len(layout)*cols
    model=checkpoint['ridge'] if checkpoint else None
    margin=checkpoint['calibration'][policy]['q90_absolute_error'] if checkpoint and policy in ('history','learned') else 0.
    estimates=[]; own=[]
    for a,st in enumerate(inst['starts']):
        preds=[]
        for d in range(4):
            turns=turn_count(st['orientation'],d);x=feature(hist.rows,a,d,turns)
            y=predict(x,turns,policy,model)
            preds.append({'direction':d,'turns':turns,'features':x,'mean_ticks':y,'margin_ticks':margin,
                          'duration_ratio':(y+margin)/nominal(turns)})
        estimates.append(preds); target=inst['goals'][a][0]['location']; ds=distances(layout,target)
        mass={st['location']:1.}; occ=[0.]*size
        for depth in range(2):
            after={}
            for cell,p in mass.items():
                options=[]
                for d,delta in enumerate((1,cols,-1,-cols)):
                    v=cell+delta
                    if 0<=v<size and abs(v//cols-cell//cols)+abs(v%cols-cell%cols)==1 and ds.get(v,10**9)<ds.get(cell,10**9):options.append((d,v))
                for d,v in options:
                    prob=p/len(options);occ[v]+=prob*(.5**depth)*preds[d]['duration_ratio'];after[v]=after.get(v,0.)+prob
            mass=after
        own.append(occ)
    total=[sum(row[j] for row in own) for j in range(size)]
    costs=[[max(0.,total[j]-own[a][j]) for j in range(size)] for a in range(n)]
    assert all(math.isfinite(v) and v>=0 for row in costs for v in row)
    return {'policy':policy,'public_last_sequence':hist.last_sequence,'completed_rows':len(hist.rows),
            'estimates':estimates,'cost_by_agent_destination':costs,'dimensionless_scale':1.,'depth':2}
