"""Finite committed-prefix guard, separate from any optimizer or learned policy."""
import copy
from executor import Executor,adoption_guard,validate_graph

def guarded_restore(snapshot,candidate_graph):
 engine=Executor.restore(copy.deepcopy(snapshot));old=engine.g;protected=[]
 for a,r in enumerate(engine.ag):
  protected.extend((a,s) for s in range(old['current'][a],r['state']))
  if 'active' in r:protected.append((a,r['state']))
 adoption_guard(old,candidate_graph,protected)
 # A combination of individually legal reversals may still be cyclic.
 size=sum(map(len,old['paths']));out=[[] for _ in range(size)];indegree=[0]*size
 for u,v,_ in candidate_graph['type1']+candidate_graph['type2']:out[u].append(v);indegree[v]+=1
 queue=[v for v,d in enumerate(indegree) if d==0];seen=0
 while queue:
  u=queue.pop();seen+=1
  for v in out[u]:
   indegree[v]-=1
   if not indegree[v]:queue.append(v)
 assert seen==size,'candidate graph cycle'
 _,weights,deps=validate_graph(candidate_graph);engine.g=copy.deepcopy(candidate_graph);engine.weights=weights;engine.deps=deps
 return engine,{'protected_transitions':[list(x) for x in protected],'active_move_identities':[[a,*list(r['active'][:2])] for a,r in enumerate(engine.ag) if 'active' in r],'at':str(engine.t)}
