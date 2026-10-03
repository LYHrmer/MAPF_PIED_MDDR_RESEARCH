"""Primitive public completion duration; private native fields never cross projection."""
from pathlib import Path
from collections import deque
import json, math, statistics
from mapping_replay import parser_contract

GROUPS=['M_first','M_second','T']
DEFAULT_D0={'M_first':17.,'M_second':17.,'T':10.,'S':20.}
FEATURES=['M_first','M_second','T','east','south','west','north',
          'agent_geometry_count/16','direction_count/8','pool_count/64',
          'history_residual/20','agent_mean_residual/20','last_residual/20','sd/20']
ALLOWED={'view':{'kind','tick','sequence','view'},'proposal':{'kind','tick','sequence','proposal'},
         'admit':{'kind','tick','sequence','robot','actions'},'end':{'kind','tick','sequence','robot','node','accepted'}}

def descriptor(node):
    kind=node['type'];direction=(int(node['orientation'])-1)%4
    if kind=='M':
        length=math.dist(node['start'],node['goal']);assert abs(length-.5)<1e-9
        group='M_first' if all(float(v).is_integer() for v in node['start']) else 'M_second'
    else:group=kind;length=0.
    return group,direction,length

def feature(rows,agent,group,direction,d0):
    hs=[r for r in rows if r['agent']==agent and r['group']==group][-16:]
    ds=[r for r in hs if r['direction']==direction][-8:]
    pool=[r['duration'] for r in rows if r['group']==group and r['direction']==direction][-64:]
    base=d0[group];pm=statistics.mean(pool) if pool else base
    history=(sum(r['duration'] for r in ds)+2*pm)/(len(ds)+2)
    values=[r['duration'] for r in hs]
    return [*[float(group==k) for k in GROUPS],*[float(direction==k) for k in range(4)],
            len(hs)/16.,len(ds)/8.,len(pool)/64.,(history-base)/20.,
            ((statistics.mean(values) if values else base)-base)/20.,
            ((values[-1] if values else base)-base)/20.,
            (statistics.pstdev(values) if len(values)>1 else 0.)/20.]

def predict(x,group,policy,checkpoint):
    if group=='S':return 20.
    residual=x[10]*20.
    if policy in ('learned','geometry'):
        if policy=='geometry':x=x[:7]+[0.]*7
        m=checkpoint['geometry_ridge' if policy=='geometry' else 'ridge'];residual=m['intercept']+sum(w*(v-u)/s for w,v,u,s in zip(m['coef'],x,m['mean'],m['scale']))
    return max(1.,min(200.,checkpoint['d0'][group]+residual))

class PublicHistory:
    def __init__(self,d0=None):
        self.d0=d0 or DEFAULT_D0;self.rows=[];self.moves={};self.last_view=None
        self.next_node={};self.last_sequence=-1;self.offset=0;self.projected=[]

    def ingest(self,path):
        with Path(path).open() as f:
            f.seek(self.offset)
            while True:
                line=f.readline()
                if not line or not line.endswith('\n'):break
                self.offset=f.tell();e=json.loads(line)
                if e['kind'] in ALLOWED:self.accept({k:e[k] for k in ALLOWED[e['kind']]})

    def accept(self,e):
        assert set(e)==ALLOWED[e['kind']] and e['sequence']>self.last_sequence
        self.last_sequence=e['sequence'];self.projected.append(e);kind=e['kind']
        if kind=='view':self.last_view=e['view']
        elif kind=='proposal':
            for a,path in enumerate(e['proposal']['plan']):
                ori=self.last_view['mapf_instance']['starts'][a]['orientation']
                for primitive in parser_contract(path,ori):
                    node=self.next_node.get(a,0);self.next_node[a]=node+1
                    group,direction,length=descriptor(primitive);key=(a,node)
                    self.moves[key]={'proposal_id':e['proposal']['proposal_id'],'agent':a,'node':node,
                        'logical_step':int(primitive['time']),'primitive':primitive,'group':group,
                        'direction':direction,'length_cells':length,'proposal_tick':e['tick'],
                        'features':feature(self.rows,a,group,direction,self.d0) if group!='S' else [],
                        'history_cutoff_sequence':e['sequence'],'admit_tick':None,'admit_sequence':None,
                        'duration':None,'end_tick':None,'end_sequence':None}
        elif kind=='admit':
            a=int(e['robot'])
            for c in e['actions']:
                r=self.moves[(a,c[1])];p=r['primitive'];assert r['admit_tick'] is None
                assert [c[3],c[4],c[5],c[2],c[6]]==[p[k] for k in ['type','start','goal','orientation','task_id']]
                r['admit_tick']=e['tick'];r['admit_sequence']=e['sequence']
        elif kind=='end':
            a=int(e['robot']);node=e['node'];r=self.moves[(a,node)]
            assert e['accepted'] and r['duration'] is None and r['admit_tick'] is not None
            prev=self.moves[(a,node-1)] if node else None
            assert prev is None or (prev['end_sequence'] is not None and prev['end_sequence']<e['sequence'])
            ep=prev['end_tick'] if prev else 0;b=max(r['admit_tick'],ep)
            assert r['admit_sequence']<e['sequence'] and e['tick']>=b
            r.update(own_predecessor_END_tick=ep,own_predecessor_END_sequence=prev['end_sequence'] if prev else -1,
                begin_tick=b,duration=e['tick']-b,end_tick=e['tick'],end_sequence=e['sequence'])
            assert r['duration']>=0 and r['end_sequence']>r['history_cutoff_sequence']
            assert (r['admit_tick']-r['proposal_tick'])+(b-r['admit_tick'])+r['duration']==e['tick']-r['proposal_tick']
            self.rows.append(dict(r))

def distances(layout,goal):
    cols=len(layout[0]);size=len(layout)*cols;ds={goal:0};queue=deque([goal])
    while queue:
        s=queue.popleft()
        for v in (s+1,s+cols,s-1,s-cols):
            if 0<=v<size and abs(v//cols-s//cols)+abs(v%cols-s%cols)==1 and layout[v//cols][v%cols]!='@' and v not in ds:
                ds[v]=ds[s]+1;queue.append(v)
    return ds

def forecast(hist,view,layout,policy,checkpoint):
    inst=view['mapf_instance'];cols=len(layout[0]);size=len(layout)*cols;own=[];estimates=[]
    for a,st in enumerate(inst['starts']):
        goal=inst['goals'][a][0]['location'];ds=distances(layout,goal);cache={}
        def edge(cell,ori,d):
            dest=cell+[1,cols,-1,-cols][d];station=dest==goal
            key=(ori,d,station)
            if key not in cache:
                s=[0,0,0,-1];dr,dc=[(0,1),(1,0),(0,-1),(-1,0)][d]
                nodes=parser_contract([s,[dr,dc,1,0 if station else -1]],ori);parts=[]
                for p in nodes:
                    group,direction,length=descriptor(p);x=feature(hist.rows,a,group,direction,checkpoint['d0']) if group!='S' else []
                    parts.append({'group':group,'direction':direction,'length_cells':length,'features':x,'mean_ticks':predict(x,group,policy,checkpoint)})
                cache[key]={'from_orientation':ori,'direction':d,'station':station,'parts':parts,'edge_ticks':sum(p['mean_ticks'] for p in parts)}
            return cache[key]
        estimates.append([edge(st['location'],st['orientation'],d) for d in range(4)])
        mass={(st['location'],st['orientation']):1.};projection=[0.]*size
        for depth in range(2):
            after={}
            for (cell,ori),prob in mass.items():
                options=[]
                for d,delta in enumerate((1,cols,-1,-cols)):
                    v=cell+delta
                    if 0<=v<size and abs(v//cols-cell//cols)+abs(v%cols-cell%cols)==1 and ds.get(v,10**9)<ds.get(cell,10**9):options.append((d,v))
                for d,v in options:
                    p=prob/len(options);projection[v]+=p*(.5**depth)*edge(cell,ori,d)['edge_ticks']
                    state=(v,{0:0,1:3,2:2,3:1}[d]);after[state]=after.get(state,0.)+p
            mass=after
        own.append(projection)
    total=[sum(row[j] for row in own) for j in range(size)]
    costs=[[max(0.,total[j]-own[a][j])*.025 for j in range(size)] for a in range(len(own))]
    assert all(math.isfinite(v) and v>=0 for row in costs for v in row)
    return {'policy':policy,'public_last_sequence':hist.last_sequence,'completed_rows':len(hist.rows),
            'estimates':estimates,'cost_by_agent_destination':costs,'objective_units_per_tick':.025,
            'shared_margin_ticks':0.,'depth':2,'meaning':'other-agent projected parser duration heuristic; not occupancy'}
