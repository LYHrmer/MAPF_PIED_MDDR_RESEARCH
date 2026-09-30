"""Independent decimal physics, closed rectangles, public-END actor, and lease replay.
No production Geometry/Index/controller is imported. Never fits a policy to outcomes.
"""
from collections import Counter,deque
from copy import deepcopy
from decimal import Decimal,getcontext
from fractions import Fraction
import hashlib,json
from pathlib import Path

getcontext().prec=70
D=Decimal;HERE=Path(__file__).resolve().parent;QUERY=HERE.parent
ROOT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH')
DELTA={'EA':(1,0),'WE':(-1,0),'NO':(0,-1),'SO':(0,1),'W':(0,0)}
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def require(v,msg):
    if not v:raise AssertionError(msg)
def iv(x):
    require(set(x)=={'lower','upper','denominator'},'interval schema')
    require(x['denominator']==1000000 and 0<=x['upper']-x['lower']<=1,'interval resolution')
    return D(x['lower'])/D(x['denominator']),D(x['upper'])/D(x['denominator'])
def inside(x,y,msg):
    lo,hi=iv(x);require(lo-D('1e-60')<=y<=hi+D('1e-60'),msg)
def decode(x,length=1,full=True):
    lo,hi=iv(x)
    if length!=1 or not full:return None
    ranges=[(1083441,1083442),(1292893,1292894),(1732050,1732051)]
    if not any(D(a)/D(1000000)<=lo<=hi<=D(b)/D(1000000) for a,b in ranges):return None
    return 1 if hi<D('1.25') else 0 if lo>D('1.25') else None
def profile(eta):
    # Independently substitute fixed coefficients into the two continuous formulas.
    a=D(2+eta);t=(D(4)/(a*(a+2))).sqrt();s=a*t*t/2;v=a*t;xi=1-s
    astar=D(4+2*eta);A=D(2)-astar
    u=4*xi/(v+(2*astar*xi).sqrt())
    return t,s,v,xi,A,u,t+u
def motion(eta,age):
    t,s,v,xi,A,u,total=profile(eta)
    if age>=total-D('1e-60'):return D(1),D(0)
    if age<=t:return D(2+eta)*age*age/2,D(2+eta)*age
    tau=age-t;n=xi-v*tau/2+A*tau*tau/8
    return 1-n*n/xi,(v-A*tau/2)*n/xi
def cell(xy):return f'cell-{xy[0]}-{xy[1]}'
def mask(cells,x,y):
    # Actual footprint+error rectangle intersects the CLOSED cell rectangle.
    return {cell(c) for c in cells if abs(x-D(c[0]))<=D('.65')+D('1e-60') and abs(y-D(c[1]))<=D('.65')+D('1e-60')}
def bind_source(sup):
    source=Path(sup['source']);require(sha(source)==sup['source_sha256'],'source hash')
    d=json.loads(source.read_text());paths=[x.split(',') for x in d['actualPaths']]
    state=[(c,r) for r,c,_ in d['start']];t=sup['source_tick']
    for tick in range(t):state=[(x+DELTA[paths[a][tick]][0],y+DELTA[paths[a][tick]][1]) for a,(x,y) in enumerate(state)]
    tasks={tid:(c,r) for tid,r,c in d['tasks']};union=set()
    for row in sup['robots']:
        a=row['agent'];q=deque()
        for tid,at,k in d['events'][a]:
            if at>t:break
            if k=='assigned':q.append(tid)
            else:require(q.popleft()==tid,'source FIFO finished')
        require(q[0]==row['task'] and list(q)==row['source_revealed_queue'],'public current FIFO head')
        require(list(state[a])==row['start'] and list(tasks[row['task']])==row['goal'],'source coordinates/task')
        finish=next(at for tid,at,k in d['events'][a] if tid==row['task'] and k=='finished')
        require(paths[a][t:finish]==row['route'],'source route full binding')
        points=[tuple(row['start'])]
        for h in row['route']:points.append(tuple(points[-1][j]+DELTA[h][j] for j in [0,1]))
        require(points[-1]==tuple(row['goal']) and points==[tuple(x) for x in row['route_points']],'source goal/path')
        union.update(points)
    require(union==set(map(tuple,sup['resource_cells'])) and len(union)>=4,'resource support union')
    baseline=ROOT/'implementation_binding_evidence/baseline_selection_20260929'
    pre=json.loads((baseline/'pied_preflight.json').read_text())
    rel='lifelong_benchmark/random/maps/random-32-32-20.map';mp=baseline/'PIED-full'/rel
    require(sha(mp)==pre['manifest'][rel]['sha256'],'public source map hash')
    grid=mp.read_text().splitlines()[4:]
    require(all(grid[y][x]=='.' for x,y in union),'whole joint route support on original free map')
    return d

class Replay:
    def __init__(self,sup,condition,policy,capacity,training):
        self.sup=sup;self.cells=sup['resource_cells'];self.policy=policy;self.capacity=capacity
        self.eta={(x['agent'],x['leg']):x['eta'] for x in condition['private_world_only']}
        self.rows={r['agent']:r for r in sup['robots']}
        self.robot={a:dict(x=r['start'][0],y=r['start'][1],next=0,ready=True,active='',served=False,wait=None) for a,r in self.rows.items()}
        self.owner={cell(r['start']):(a,'') for a,r in self.rows.items()};self.moves={};self.asked=set();self.opps=set()
        self.count=Counter();self.success=Counter();self.known=0;self.clock=D(0);self.rawclock=None
        self.services={};self.pending_choice=None;self.frames=0;self.decisions=0;self.positions=0;self.end_count=0
        self.continuous_grants=0;self.initial_two=False;self.last_event=None;self.coefficients=[];self.deadlock=False
        for o in training:
            require(set(o)=={'run_id','tick','agent','heading','original_END','received','full_cap_uninterrupted','length'},'clean training schema')
            require(o['run_id'] in ['train_1103','train_2207'],'train/test run split')
            require(iv(o['received'])[0]>=iv(o['original_END'])[1],'training feedback delivered')
            label=decode(o['original_END'],o['length'],o['full_cap_uninterrupted']);require(label is not None,'training decoder support')
            self.feed(o['heading'],label)
        require(self.known==3582,'training count')
    def feed(self,h,label):self.count[h]+=1;self.success[h]+=label;self.known+=1
    def next_times(self):
        out=[]
        for key,m in self.moves.items():
            if not m['physical']:out.extend([m['launch']+profile(m['eta'])[0],m['launch']+profile(m['eta'])[-1]])
            if m['physical'] and not m['native']:out.append(m['end']+D('.25'))
            if key not in self.opps:out.append(m['launch']+D('.75'))
        out.extend(r['wait'] for r in self.robot.values() if r['wait'] is not None)
        return [x for x in out if x>self.clock+D('1e-60')]
    def tick(self,e):
        value=e.get('at',e.get('last_clock'))
        if value is None:return
        token=(value['lower'],value['upper'])
        if token!=self.rawclock:
            if self.rawclock is not None:
                times=self.next_times();require(times,'missing independent next event')
                self.clock=min([D(64)]+times)
            self.rawclock=token
        inside(value,self.clock,'event time differs from independently reconstructed earliest physics/END/WAIT/opportunity')
    def full(self,a,leg):
        points=self.rows[a]['route_points'];return {cell(points[leg]),cell(points[leg+1])}
    def relations(self,a,resources):
        groups={}
        for c in sorted(resources):
            if c not in self.owner or self.owner[c][0]==a:continue
            foreign,act=self.owner[c];gkey=act or 'resident-'+str(foreign)
            rel=groups.setdefault(gkey,dict(action=act,retirable=True,threshold=None))
            if not act:rel['retirable']=False;continue
            m=self.moves[act];threshold='1' if c==cell(m['end_point']) else '13/20'
            if rel['threshold'] is None or Fraction(threshold)>Fraction(rel['threshold']):rel['threshold']=threshold
            if threshold=='1':rel['retirable']=False
        return [groups[k] for k in sorted(groups)]
    def demands(self):
        out={}
        for a,r in self.robot.items():
            route=self.rows[a]['route']
            if not r['ready'] or r['served'] or r['next']>=len(route) or route[r['next']]=='W':continue
            resources=self.full(a,r['next']);key=f"d-{a}-{r['next']}"
            out[key]=dict(id=key,agent=f'agent-{a}',resources=sorted(resources),relations=self.relations(a,resources))
        return out
    def candidates(self):
        out=[];demands=self.demands()
        for key,m in self.moves.items():
            if m['native'] or key in self.asked or self.clock-m['launch']<D('.75')-D('1e-60'):continue
            claims=[]
            for did,d in sorted(demands.items()):
                a=int(d['agent'][6:]);r=self.robot[a]
                for rel in d['relations']:
                    if rel['action']==key and rel['retirable']:
                        claims.append(dict(task=self.rows[a]['task'],remaining_route_items=len(self.rows[a]['route'])-r['next'],owners=len(d['relations'])))
            if claims:
                stats=[0,0,Fraction(0),0,0,0,0,0,0]
                for did,d in sorted(demands.items()):
                    if not any(rel['action']==key and rel['retirable'] for rel in d['relations']):continue
                    a=int(d['agent'][6:]);r=self.robot[a];row=self.rows[a];begin=r['next'];points=row['route_points'][begin:];path=set(map(tuple,points))
                    stats[0]+=1;stats[1]+=len(row['route'])-begin;stats[2]+=Fraction(1,len(row['route'])-begin);stats[3]+=len(d['relations'])
                    for aa,other in self.robot.items():
                        if aa==a:continue
                        ob=self.moves[other['active']]['leg'] if other['active'] else other['next'];orow=self.rows[aa];op=set(map(tuple,orow['route_points'][ob:]))
                        stats[4]+=len(path&op);end=tuple(orow['goal'])
                        if end in path:
                            stats[5]+=1;stats[6]+=next(i for i,z in enumerate(points) if tuple(z)==end);stats[7]+=len(orow['route'])-ob
                        stats[8]+=int(tuple(row['goal']) in op)
                features=[Fraction(self.success[m['heading']]+1,self.count[m['heading']]+2),Fraction(stats[0],3),Fraction(stats[1],16),stats[2],Fraction(stats[3],3),Fraction(stats[4],64),Fraction(stats[5],3),Fraction(stats[6],16),Fraction(stats[7],16),Fraction(stats[8],3)]
                out.append(dict(move=key,agent=m['agent'],heading=m['heading'],launch=m['launch'],claims=claims,features=features))
        return out
    def event(self,e):
        self.tick(e);kind=e['event']
        if kind=='original_RUN':
            key=e['id'];_,aa,ll=key.split('-');a,leg=int(aa),int(ll);r=self.robot[a];row=self.rows[a]
            require(key not in self.moves and r['ready'] and not r['served'] and not r['active'] and r['next']==leg,'RUN lifecycle')
            require(row['route'][leg]!='W' and self.relations(a,self.full(a,leg))==[],'RUN denied by shared foreign lease')
            require((r['x'],r['y'])==tuple(row['route_points'][leg]),'actual start follows source leg')
            m=dict(agent=a,leg=leg,heading=row['route'][leg],launch=self.clock,eta=self.eta[(a,leg)],
                   start=tuple(row['route_points'][leg]),end_point=tuple(row['route_points'][leg+1]),q=D(0),physical=False,native=False)
            self.moves[key]=m;r['next']+=1;r['ready']=False;r['active']=key
            for c in self.full(a,leg):
                require(c not in self.owner or self.owner[c][0]==a,'grant collision');self.owner[c]=(a,key)
            # Unit cardinal swept ±.15 rectangle is covered by its two source/dest closed cells.
            require(len(self.full(a,leg))==2,'nonunit grant outside controller/decoder contract');self.continuous_grants+=1
        elif kind=='physical_original_END':
            m=self.moves[e['id']];require(not m['physical'],'duplicate physical END')
            require(abs(self.clock-m['launch']-profile(m['eta'])[-1])<D('1e-60'),'END fixed original profile')
            m['physical']=True;m['end']=self.clock;r=self.robot[m['agent']];r['x'],r['y']=m['end_point']
        elif kind=='public_END_delivered':
            require(set(e)=={'event','move','agent','heading','at','public_original_END','public_launch','duration','decoded_END_class','full_cap_uninterrupted','length','progress_field_sent_to_actor'},'public END schema/private field leak')
            m=self.moves[e['move']];require(m['physical'] and not m['native'],'END missing physical predecessor/duplicate')
            require(abs(self.clock-m['end']-D('.25'))<D('1e-60'),'normal END delivery latency')
            inside(e['public_original_END'],m['end'],'public original END provenance');inside(e['public_launch'],m['launch'],'END launch provenance')
            duration=profile(m['eta'])[-1];inside(e['duration'],duration,'END duration from independent physics')
            label=decode(e['duration'],e['length'],e['full_cap_uninterrupted'])
            require(label==e['decoded_END_class'] and label==int(m['eta']==1),'END decoder recovered class independently')
            require(not e['progress_field_sent_to_actor'] and e['agent']==m['agent'] and e['heading']==m['heading'],'actor feedback fields')
            self.feed(e['heading'],label);self.end_count+=1;m['native']=True
            for c,(a,act) in list(self.owner.items()):
                if act==e['move']:
                    if c==cell(m['end_point']):self.owner[c]=(a,'')
                    else:del self.owner[c]
            r=self.robot[m['agent']];r['active']='';r['ready']=True
        elif kind=='native_READY':
            m=self.moves[e['id']];require(m['native'] and self.robot[m['agent']]['ready'],'READY before normal END')
        elif kind=='public_WAIT_started':
            a=int(e['id']);r=self.robot[a];require(r['ready'] and self.rows[a]['route'][r['next']]=='W','source WAIT lifecycle')
            r['wait']=self.clock+1;r['ready']=False;r['next']+=1
        elif kind=='public_WAIT_ended':
            r=self.robot[int(e['id'])];require(abs(r['wait']-self.clock)<D('1e-60'),'source WAIT duration');r['wait']=None;r['ready']=True
        elif kind=='task_service':
            a=e['agent'];r=self.robot[a];row=self.rows[a];require(a not in self.services,'duplicate task service')
            require(e['task']==row['task'] and e['goal']==row['goal'] and [r['x'],r['y']]==row['goal'] and r['next']==len(row['route']),'task source/head/endpoint binding')
            m=self.moves[r['active']];require(m['physical'] and motion(m['eta'],self.clock-m['launch'])==(D(1),D(0)),'task actual endpoint/rest')
            require(D('.1')<D('.2') and e['original_endpoint_at_rest'] and e['physical_footprint_inside_service_square'],'service footprint qualification')
            self.services[a]=self.clock;r['served']=True
        elif kind=='actor_decision':
            require(set(e)=={'event','at','policy','remaining_capacity','candidates','selected','END_only_known','END_unknown','private_progress_input','regime_input'},'actor input schema/private field leak')
            require(not e['private_progress_input'] and not e['regime_input'] and e['policy']==self.policy,'actor private input')
            self.opps.update(key for key,m in self.moves.items() if abs(m['launch']+D('.75')-self.clock)<D('1e-60'))
            actual=self.candidates();require(len(actual)==len(e['candidates']),'candidate completeness')
            best=None;best_score=Fraction(0)
            for c,raw in zip(actual,e['candidates']):
                require(set(raw)=={'move','agent','heading','public_launch','probability','score','claims','features'},'candidate clean schema')
                require(all(raw[k]==c[k] for k in ['move','agent','heading','claims']),'candidate from real common Geometry leases and current source head')
                inside(raw['public_launch'],c['launch'],'public launch');require([Fraction(z) for z in raw['features']]==c['features'],'independent public planned-path features')
                if self.policy=='global_task':p=Fraction(sum(self.success.values())+1,sum(self.count.values())+2)
                else:p=Fraction(self.success[c['heading']]+1,self.count[c['heading']]+2)
                score=Fraction(1) if self.policy=='RR' else Fraction(0)
                if self.policy in ['task_rank','global_task','task_trigger'] and (self.policy!='task_trigger' or p>=Fraction(1,2)):
                    score=p*sum((Fraction(1,x['remaining_route_items']*x['owners']) for x in c['claims']),Fraction(0))
                if self.policy.startswith('forced_'):score=Fraction(int(c['agent']==int(self.policy[7:])))
                elif self.policy=='probability':score=p
                elif self.policy=='structural':score=c['features'][6]*1000000+c['features'][5]*1000+p*c['features'][3]
                elif self.policy=='ridge':
                    require(len(self.coefficients)==11,'missing real trained model');score=self.coefficients[0]+sum((z*w for z,w in zip(c['features'],self.coefficients[1:])),Fraction(0))
                require(Fraction(raw['probability'])==p and Fraction(raw['score'])==score,'END-only calibrated probability/trained causal score')
                if self.capacity>len(self.asked) and score>0 and (best is None or (c['agent']<best['agent'] if self.policy=='RR' else score>best_score or score==best_score and c['agent']<best['agent'])):
                    best=c;best_score=score
            require(e['remaining_capacity']==self.capacity-len(self.asked) and e['END_only_known']==self.known and e['END_unknown']==0,'causal history/capacity count')
            require(e['selected']==(best['move'] if best else ''),'independent public-END actor selection')
            if self.decisions==0:self.initial_two=len(actual)==2
            self.pending_choice=e['selected'];self.decisions+=1
        elif kind=='certified_POSITION_committed':
            key=e['move'];m=self.moves[key];require(self.pending_choice==key and key not in self.asked and len(self.asked)<self.capacity,'POSITION selection/capacity/uniqueness')
            s,v=motion(m['eta'],self.clock-m['launch']);inside(e['certified_lower'],s,'actual controller certified lower')
            require(s>=m['q'] and e['epsilon']=='1/10' and e['endpoint_retained'],'certificate monotone/lower semantics')
            removed=[c for c,(a,act) in self.owner.items() if act==key and c==cell(m['start']) and s>D('.65')]
            require(sorted(removed)==e['removed'],'independent source release: certified lower > 13/20, no epsilon subtraction')
            for c in removed:del self.owner[c]
            m['q']=s;self.asked.add(key);self.pending_choice=None;self.positions+=1
        elif kind=='world_frame_offline_only':
            require(not e['actor_consumes_this_frame'],'private frame actor leak')
            expected=sorted((c,f'agent-{a}',act) for c,(a,act) in self.owner.items())
            require(expected==[tuple(x) for x in e['owners']],'independent common owner reconstruction')
            acts={x['id']:x for x in e['actions']};require(set(acts)=={key for key,m in self.moves.items() if not m['native']},'active set')
            for key,a in acts.items():
                m=self.moves[key];inside(a['q'],m['q'],'retirement q');want={cell(m['end_point'])}
                if m['q']<=D('.65'):want.add(cell(m['start']))
                require(set(a['mask'])==want and all(self.owner[c]==(m['agent'],key) for c in want),'independent residual responsibility')
            require({x['id']:x for x in e['demands']}==self.demands(),'independent requester resource/index relations')
            require({x['agent'] for x in e['robots']}==set(self.robot),'frame robot support')
            occupied=set()
            for x in e['robots']:
                a=x['agent'];r=self.robot[a];row=self.rows[a]
                require(all(x[k]==r[k] for k in ['next','served','ready','active']) and x['task']==row['task'],'robot cursor/lifecycle/frame')
                s=v=D(0);px,py=D(r['x']),D(r['y'])
                if r['active']:
                    m=self.moves[r['active']];s,v=motion(m['eta'],self.clock-m['launch']);dx,dy=DELTA[m['heading']]
                    px=D(m['start'][0])+s*dx;py=D(m['start'][1])+s*dy
                    require(s>=m['q']-D('1e-60'),'physical progress below certified lower')
                for name,num in [('x',px),('y',py),('s',s),('v',v)]:inside(x[name],num,'independent analytic physical '+name)
                footprint=mask(self.cells,px,py);require(footprint==set(x['actual_enlarged_mask']),'independent closed rectangle footprint')
                require(not footprint&occupied and all(self.owner[c][0]==a for c in footprint),'joint exact exclusive physical support')
                occupied|=footprint
            self.frames+=1
        elif kind=='joint_deadlock':
            self.deadlock=True
            require(not self.next_times() and len(self.services)<4,'deadlock genuine no future local event')
            require(all(d['relations'] for d in self.demands().values()),'deadlock has ready unblocked move')
        elif kind=='joint_summary':
            require(e['status']=='passed' and e['served']==len(self.services) and e['queries']==len(self.asked) and e['capacity']==self.capacity and e['policy']==self.policy,'summary/source cohort counts')
            require(e['started_MOVEs']==len(self.moves) and e['delivered_END']==self.end_count and e['uncompleted_heads']==4-len(self.services),'summary actual native lifecycle')
            require(e['max_candidates']>=2 and self.initial_two and e['joint_shared_owner_state'] and not e['published_external_comparison'] and not e['production_COST'],'support/claim flags')
            inside(e['service_time_sum'],sum(self.services.values(),D(0)),'actual task time sum')
            require(e['deadlock']==self.deadlock,'deadlock/censor flag')
        else:raise AssertionError('unreviewed raw event '+kind)
        self.last_event=kind
    def run(self,records):
        for e in records:self.event(e)
        require(self.last_event=='joint_summary','truncated run')
        return dict(served=len(self.services),queries=len(self.asked),deadlock=len(self.services)<4,
          head_service_times={str(self.rows[a]['task']):str(t) for a,t in self.services.items()},
          restricted_flow_sum=str(sum(self.services.values(),D(0))+D(64)*(4-len(self.services))),
          frames=self.frames,decisions=self.decisions,original_MOVEs=len(self.moves),END_feedback=self.end_count,
          initial_two_candidates=self.initial_two,continuous_exclusive_lease_grants=self.continuous_grants)
