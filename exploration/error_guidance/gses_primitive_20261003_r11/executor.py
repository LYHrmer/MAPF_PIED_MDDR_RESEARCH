"""Explicit research event executor; no author state trace is used as policy input."""
from fractions import Fraction as F
import copy,heapq

def q(x):return str(F(x))
def pos(p):return [q(x) for x in p]
def direction(a,b):return {(1,0):0,(0,1):1,(-1,0):2,(0,-1):3}[tuple(y-x for x,y in zip(a,b))]
def keyedge(a,b):return tuple(sorted((tuple(a),tuple(b))))

def validate_graph(g):
 paths=g['paths'];counts=[len(p) for p in paths];off=[];ids=[]
 for a,path in enumerate(paths):
  off.append(len(ids));ids.extend((a,s) for s in range(len(path)))
  for x,y in zip(path,path[1:]):assert sum(abs(u-v) for u,v in zip(x[0],y[0]))==1,'path not unit-adjacent'
 assert off==g['offsets'] and len(g['current'])==len(paths)
 weights={};deps={}
 for u,v,w in g['type1']:
  a,s=ids[u];assert ids[v]==(a,s+1) and s>=g['current'][a]
  assert w>=1 and int(w)==w and (s==g['current'][a] or w==1),'unsupported future weight'
  assert (a,s) not in weights;weights[a,s]=int(w)
 assert set(weights)=={(a,s) for a,path in enumerate(paths) for s in range(g['current'][a],len(path)-1)}
 for u,v,w in g['type2']:
  assert w==1 and ids[u][0]!=ids[v][0]
  a,s=ids[u];b,t=ids[v];assert s>=1 and paths[a][s-1][0]==paths[b][t][0],'type2 not a leave/enter cell pair'
  deps.setdefault((b,t),[]).append((a,s))
 return ids,weights,deps

def adoption_guard(old,new,committed):
 validate_graph(old);validate_graph(new)
 assert old['paths']==new['paths'] and old['current']==new['current'] and old['type1']==new['type1'],'path/current/type1 prefix changed'
 canonical=lambda e:min(tuple(e[:2]),(e[1]+1,e[0]-1))
 assert sorted(map(canonical,old['type2']))==sorted(map(canonical,new['type2'])),'non-author dependency family'
 for a,s in committed:
  target=old['offsets'][a]+s+1
  before={tuple(e) for e in old['type2'] if e[1]==target};after={tuple(e) for e in new['type2'] if e[1]==target}
  assert before==after,'committed transition dependencies changed'
 return True

class Executor:
 def __init__(self,graph,profile):
  self.g=copy.deepcopy(graph);self.profile=profile;_,self.weights,self.deps=validate_graph(graph)
  self.t=F(0);self.heap=[];self.ticket=0;self.events=[];self.segments=[];self.resources={};self.edges={};self.ag=[];self.completed={};self.checkpoint=None
  for a,(path,s) in enumerate(zip(graph['paths'],graph['current'])):
   p=tuple(path[s][0]);assert p not in self.resources,'initial resource overlap';self.resources[p]=a
   yaw=direction(path[s-1][0],p) if s else 0;last=len(path)-1;delay=F(self.weights.get((a,s),1)-1)
   self.ag.append({'state':s,'point':p,'yaw':yaw,'phase':'need_turn','last_end':F(0),'last_point':p,'physical':{p},'finish':F(0) if s==last else None})
   self.emit(a,'INITIAL',state=s,cell=list(p),yaw=yaw)
   if s==last:self.ag[a]['phase']='done';self.completed[a]=F(0)
   elif delay:
    self.segment(a,F(0),delay,p,p,'INITIAL_HOLD',s,s,yaw,yaw);self.ag[a]['phase']='initial';self.push(delay,a,'INITIAL_READY')
 def emit(self,a,kind,**kw):
  self.events.append({'seq':len(self.events),'t':q(self.t),'agent':a,'kind':kind,**kw})
 def push(self,t,a,kind,**kw):
  self.ticket+=1;heapq.heappush(self.heap,(F(t),self.ticket,a,kind,kw))
 def segment(self,a,t0,t1,p0,p1,kind,s0,s1,y0,y1):
  r=self.ag[a];assert t0>=r['last_end'] and t1>=t0
  if t0>r['last_end']:
   p=r['last_point'];self.segments.append({'agent':a,'t0':q(r['last_end']),'t1':q(t0),'p0':pos(p),'p1':pos(p),'kind':'WAIT','from_state':s0,'to_state':s0,'yaw0':r['yaw'],'yaw1':r['yaw']})
  if t1>t0:self.segments.append({'agent':a,'t0':q(t0),'t1':q(t1),'p0':pos(p0),'p1':pos(p1),'kind':kind,'from_state':s0,'to_state':s1,'yaw0':y0,'yaw1':y1})
  r['last_end']=t1;r['last_point']=tuple(p1)
 def station(self,a):
  r=self.ag[a];s=r['state'];duration=F(0) if self.profile=='author_unit' else F(1,2)
  if duration:
   self.emit(a,'STATION_START',state=s,cell=list(r['point']));self.segment(a,self.t,self.t+duration,r['point'],r['point'],'STATION',s,s,r['yaw'],r['yaw']);r['phase']='station';self.push(self.t+duration,a,'STATION_END',state=s)
  else:self.ready_after_station(a)
 def ready_after_station(self,a):
  r=self.ag[a]
  if r['state']==len(self.g['paths'][a])-1:
   r['phase']='done';r['finish']=self.t;self.completed[a]=self.t;self.emit(a,'GOAL_COMPLETE',state=r['state'],cell=list(r['point']))
  else:r['phase']='need_turn'
 def schedule(self):
  for a,r in enumerate(self.ag):
   if r['phase']=='need_turn':
    s=r['state'];target=self.g['paths'][a][s+1][0];d=direction(r['point'],target);diff=(d-r['yaw'])%4;turns=diff if diff<=2 else -1
    if self.profile!='author_unit' and turns:
     step=1 if turns>0 else -1;end=self.t
     for k in range(abs(turns)):
      nxt=end+F(1,4);y=(r['yaw']+step*k)%4;self.segment(a,end,nxt,r['point'],r['point'],'TURN',s,s,y,(y+step)%4);end=nxt
     self.emit(a,'TURN_START',state=s,cell=list(r['point']),yaw0=r['yaw'],yaw1=d,quarters=abs(turns));r['phase']='turn';self.push(end,a,'TURN_END',yaw=d)
    else:r['yaw']=d;r['phase']='ready'
   if r['phase']!='ready':continue
   s=r['state'];dest=tuple(self.g['paths'][a][s+1][0]);origin=r['point'];edge=keyedge(origin,dest)
   if any(self.ag[b]['state']<v for b,v in self.deps.get((a,s+1),[])):continue
   if dest in self.resources or edge in self.edges:continue
   assert self.resources.get(origin)==a and r['physical']=={origin}
   self.resources[dest]=a;self.edges[edge]=a;r['phase']='move';r['active']=(s,s+1,origin,dest)
   self.emit(a,'MOVE_START',from_state=s,to_state=s+1,origin=list(origin),destination=list(dest),dependencies=[list(v) for v in self.deps.get((a,s+1),[])])
   self.emit(a,'RESERVE_DESTINATION',cell=list(dest),from_state=s,to_state=s+1);self.emit(a,'RESERVE_EDGE',edge=[list(v) for v in edge],from_state=s,to_state=s+1)
   duration=F(3,2) if self.profile=='axis_slow' and origin[1]!=dest[1] else F(1)
   pause=F(3,4) if self.profile=='midpoint_pause' and (a+s)%11==0 else F(0)
   mid=tuple((F(x)+F(y))/2 for x,y in zip(origin,dest));half=self.t+duration/2;end=self.t+duration+pause
   self.segment(a,self.t,half,origin,mid,'MOVE_HALF1',s,s+1,r['yaw'],r['yaw'])
   if pause:self.segment(a,half,half+pause,mid,mid,'MIDPOINT_PAUSE',s,s+1,r['yaw'],r['yaw'])
   self.segment(a,half+pause,end,mid,dest,'MOVE_HALF2',s,s+1,r['yaw'],r['yaw'])
   self.push(self.t+duration*F(2,5),a,'CELL_ENTER',cell=dest)
   self.push(half,a,'HALF_END',from_state=s,to_state=s+1,pause=q(pause))
   if pause:self.push(half+pause,a,'MIDPOINT_RESUME',from_state=s,to_state=s+1)
   self.push(self.t+duration*F(3,5)+pause,a,'CELL_EXIT',cell=origin)
   self.push(end,a,'ARRIVE',from_state=s,to_state=s+1,cell=dest,edge=edge)
 def process(self,a,kind,kw):
  r=self.ag[a]
  if kind=='INITIAL_READY':r['phase']='need_turn';self.emit(a,kind,state=r['state'])
  elif kind=='TURN_END':r['yaw']=kw['yaw'];r['phase']='ready';self.emit(a,kind,state=r['state'],cell=list(r['point']),yaw=r['yaw'])
  elif kind=='STATION_END':self.emit(a,kind,state=r['state'],cell=list(r['point']));self.ready_after_station(a)
  elif kind=='CELL_ENTER':
   cell=kw['cell'];assert self.resources[cell]==a;r['physical'].add(cell);self.emit(a,kind,cell=list(cell),state=r['state'])
  elif kind=='CELL_EXIT':
   cell=kw['cell'];assert self.resources[cell]==a and cell in r['physical'];del self.resources[cell];r['physical'].remove(cell);self.emit(a,kind,cell=list(cell),state=r['state']);self.emit(a,'RELEASE_SOURCE',cell=list(cell),state=r['state'])
  elif kind in ('HALF_END','MIDPOINT_RESUME'):
   assert r['state']==kw['from_state'] and len(r['physical'])==2;self.emit(a,kind,state=r['state'],**kw)
  elif kind=='ARRIVE':
   assert r['state']==kw['from_state'] and self.edges[kw['edge']]==a and r['physical']=={kw['cell']};del self.edges[kw['edge']]
   r['state']=kw['to_state'];r['point']=kw['cell'];r.pop('active');self.emit(a,'RELEASE_EDGE',edge=[list(v) for v in kw['edge']],state=r['state']);self.emit(a,'ARRIVE',from_state=kw['from_state'],to_state=r['state'],cell=list(r['point']));self.station(a)
  else:raise AssertionError(kind)
 def step(self):
  self.schedule()
  if len(self.completed)==len(self.ag):return False
  assert self.heap,'resource/dependency deadlock';t=self.heap[0][0];self.t=t
  while self.heap and self.heap[0][0]==t:
   _,_,a,kind,kw=heapq.heappop(self.heap);self.process(a,kind,kw)
  return True
 def run(self):
  while self.step():assert len(self.events)<5000000,'event bound'
  for a,r in enumerate(self.ag):
   if r['last_end']<self.t:self.segment(a,r['last_end'],self.t,r['point'],r['point'],'GOAL_HOLD',r['state'],r['state'],r['yaw'],r['yaw'])
  return {'profile':self.profile,'graph':self.g,'radius':'1/10','agents':len(self.ag),'makespan':q(self.t),'sum_completion_time':q(sum(self.completed.values(),F(0))),'completion_times':{str(a):q(t) for a,t in self.completed.items()},'events':self.events,'segments':self.segments,'semantics':'research affine event model; not original continuous controller'}
 def snapshot(self):
  # Explicit data tree, encoded as JSON by snapshot_json; no executable pickle.
  def enc(v):
   if isinstance(v,F):return {'$fraction':str(v)}
   if isinstance(v,tuple):return {'$tuple':[enc(x) for x in v]}
   if isinstance(v,set):return {'$set':[enc(x) for x in sorted(v)]}
   if isinstance(v,list):return [enc(x) for x in v]
   if isinstance(v,dict):return {'$dict':[[enc(k),enc(x)] for k,x in v.items()]}
   return v
  return enc(self.__dict__)
 @classmethod
 def restore(cls,data):
  def dec(v):
   if isinstance(v,list):return [dec(x) for x in v]
   if not isinstance(v,dict):return v
   if '$fraction' in v:return F(v['$fraction'])
   if '$tuple' in v:return tuple(dec(x) for x in v['$tuple'])
   if '$set' in v:return set(dec(x) for x in v['$set'])
   if '$dict' in v:return {dec(k):dec(x) for k,x in v['$dict']}
   raise AssertionError('unknown snapshot tag')
  self=cls.__new__(cls);self.__dict__=dec(data);return self
