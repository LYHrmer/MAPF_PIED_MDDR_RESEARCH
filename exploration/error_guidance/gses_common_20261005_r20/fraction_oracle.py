"""Independent exact graph objective; no author/search/simulator imports."""
from fractions import Fraction as F
from itertools import product
import copy


def objective(graph):
    n=sum(map(len,graph['paths']))
    adj=[[] for _ in range(n)];ind=[0]*n
    for u,v,w in graph['type1']+graph['type2']:
        assert 0<=u<n and 0<=v<n and u!=v
        adj[u].append((v,F(str(w))));ind[v]+=1
    current=[o+s for o,s in zip(graph['offsets'],graph['current'])]
    values=[None]*n
    for v in current:values[v]=F(0)
    queue=[i for i,d in enumerate(ind) if not d];seen=0
    while queue:
        u=queue.pop();seen+=1
        for v,w in adj[u]:
            if values[u] is not None:
                candidate=values[u]+w
                values[v]=candidate if values[v] is None else max(values[v],candidate)
            ind[v]-=1
            if not ind[v]:queue.append(v)
    if seen!=n:return dict(feasible=False,reason='cycle')
    last=[o+len(path)-1 for o,path in zip(graph['offsets'],graph['paths'])]
    assert all(values[v] is not None for v in last)
    return dict(feasible=True,sum_completion=str(sum(values[v] for v in last)),
        makespan=str(max(values[v] for v in last)),last_times=[str(values[v]) for v in last],
        values=[None if x is None else str(x) for x in values])


def enumerate_legal(spec):
    g=spec['solver_graph'];choices=spec['reversible_edges'];out=[]
    for bits in product((0,1),repeat=len(choices)):
        candidate=copy.deepcopy(g)
        for e,bit in zip(choices,bits):
            if bit:
                candidate['type2'].remove(e)
                candidate['type2'].append([e[1]+1,e[0]-1,e[2]])
        result=objective(candidate);result.update(bits=list(bits),type2=candidate['type2'])
        out.append(result)
    feasible=[r for r in out if r['feasible']]
    best=min(F(r['sum_completion']) for r in feasible)
    return dict(candidates=out,optimum=str(best),optimal_bits=[r['bits'] for r in feasible if F(r['sum_completion'])==best])
