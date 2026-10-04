"""Finite online STPG adapter; public solver inputs and private replay state separate."""
from pathlib import Path
from fractions import Fraction as F
import copy,hashlib,heapq,json,math
from executor import Executor,validate_graph,adoption_guard

def digest(data):return hashlib.sha256(json.dumps(data,sort_keys=True,separators=(',',':')).encode()).hexdigest()
def family(e):return min(tuple(e[:2]),(e[1]+1,e[0]-1))
def dag(g):
 size=sum(map(len,g['paths']));out=[[] for _ in range(size)];indegree=[0]*size
 for u,v,_ in g['type1']+g['type2']:
  assert 0<=u<size and 0<=v<size and u!=v,'bad graph vertex'
  out[u].append(v);indegree[v]+=1
 queue=[i for i,d in enumerate(indegree) if not d];seen=0
 while queue:
  u=queue.pop();seen+=1
  for v in out[u]:
   indegree[v]-=1
   if not indegree[v]:queue.append(v)
 assert seen==size,'candidate cycle'

def checkpoint(graph,profile,at):
 engine=Executor(graph,profile);at=F(at);engine.schedule()
 while engine.heap and engine.heap[0][0]<=at:
  engine.t=engine.heap[0][0]
  while engine.heap and engine.heap[0][0]==engine.t:
   _,_,a,kind,kw=heapq.heappop(engine.heap);engine.process(a,kind,kw)
  engine.schedule()
 assert len(engine.completed)<len(engine.ag),'checkpoint after completion'
 engine.t=at
 return engine

def public_input(engine):
 # No event heap, planned segments, true completion times, profile or future pauses.
 g=engine.g;ids,_,_=validate_graph(g);states=[r['state'] for r in engine.ag]
 result={'public_at':str(engine.t),'arrived_states':states,'active_commitments':[],
         'phases':[r['phase'] for r in engine.ag],
         'physical_cells':[[list(p) for p in sorted(r['physical'])] for r in engine.ag],
         'reservations':[[list(p),a] for p,a in sorted(engine.resources.items())],
         'edge_reservations':[[[list(p) for p in e],a] for e,a in sorted(engine.edges.items())],
         'nominal_contract':'unit future edges; only initial public hold remaining is rounded upward'}
 for a,r in enumerate(engine.ag):
  if 'active' in r:
   s,t,o,d=r['active'];result['active_commitments'].append({'agent':a,'from_state':s,'to_state':t,'origin':list(o),'destination':list(d)})
 initial_weights={ids[u]:int(w) for u,v,w in g['type1']}
 weights=[]
 for a,path in enumerate(g['paths']):
  for s in range(states[a],len(path)-1):
   hold=0
   if s==states[a] and engine.ag[a]['phase']=='initial':
    # The input's delay is already public, unlike physical future primitive lengths.
    hold=max(0,math.ceil(F(initial_weights[a,s]-1)-engine.t))
   weights.append([g['offsets'][a]+s,g['offsets'][a]+s+1,1+hold])
 deps=[]
 for e in g['type2']:
  a,s=ids[e[0]];b,t=ids[e[1]]
  if s>states[a]:
   assert t>states[b],'unmet dependency into an already arrived state'
   deps.append(e)
 result['solver_graph']={'paths':copy.deepcopy(g['paths']),'current':states,'offsets':g['offsets'][:],
                         'type1':sorted(weights),'type2':sorted(copy.deepcopy(deps))}
 validate_graph(result['solver_graph']);dag(result['solver_graph'])
 return result

def merge_candidate(old,public,candidate):
 inp=public['solver_graph'];validate_graph(candidate);dag(candidate)
 assert candidate['paths']==inp['paths'] and candidate['current']==inp['current'] and candidate['offsets']==inp['offsets'],'candidate path/current/offset changed'
 assert sorted(candidate['type1'])==sorted(inp['type1']),'candidate type1 changed'
 assert sorted(map(family,candidate['type2']))==sorted(map(family,inp['type2'])),'candidate reversed outside input family'
 orientations={family(e):e for e in candidate['type2']}
 assert len(orientations)==len(candidate['type2']),'duplicate reversal family'
 merged=copy.deepcopy(old)
 merged['type2']=sorted([copy.deepcopy(orientations.get(family(e),e)) for e in old['type2']])
 return merged

def guarded_adopt(snapshot,public,candidate):
 engine=Executor.restore(copy.deepcopy(snapshot));old=engine.g
 assert public==public_input(engine),'stale or private solver view'
 merged=merge_candidate(old,public,candidate)
 protected=[]
 for a,r in enumerate(engine.ag):
  protected.extend((a,s) for s in range(old['current'][a],r['state']))
  if 'active' in r:protected.append((a,r['state']))
 adoption_guard(old,merged,protected);dag(merged)
 # Also preserve all families already satisfied by actual ARRIVE, including their orientations.
 ids,_,_=validate_graph(old)
 for e in old['type2']:
  a,s=ids[e[0]]
  if s<=engine.ag[a]['state']:assert e in merged['type2'],'satisfied dependency changed'
 before=copy.deepcopy(engine.__dict__)
 _,weights,deps=validate_graph(merged);engine.g=merged;engine.weights=weights;engine.deps=deps
 for k,v in before.items():
  if k not in ('g','weights','deps'):assert engine.__dict__[k]==v,('execution commitment mutation',k)
 removed=sorted(e for e in old['type2'] if e not in merged['type2'])
 added=sorted(e for e in merged['type2'] if e not in old['type2'])
 return engine,{'at':str(engine.t),'event_seq':len(engine.events),'protected_transitions':protected,
               'active_count':len(public['active_commitments']),'removed_type2':removed,'added_type2':added,
               'changed':bool(removed),'initial_graph_sha256':digest(old),'adopted_graph_sha256':digest(merged)}

def finish(engine,initial_graph,adoption=None):
 trace=engine.run();trace['final_graph']=trace['graph'];trace['graph']=copy.deepcopy(initial_graph)
 trace['adoption']=adoption
 if adoption:trace['adoption']['graph']=copy.deepcopy(trace['final_graph'])
 return trace

def continue_candidate(snapshot,public,reply,status):
 initial=Executor.restore(snapshot).g;guard=None;error=None
 if status=='Succ':
  try:engine,guard=guarded_adopt(snapshot,public,reply['selected_graph'])
  except (AssertionError,KeyError,IndexError,TypeError,ValueError) as exc:
   error=repr(exc);engine=Executor.restore(copy.deepcopy(snapshot));status='Rejected'
 else:engine=Executor.restore(copy.deepcopy(snapshot))
 trace=finish(engine,initial,guard)
 return trace,{'status':status,'guard_error':error,'guard':{k:v for k,v in guard.items() if k!='graph'} if guard else None}
