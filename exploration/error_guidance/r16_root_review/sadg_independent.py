"""Reconstruct author SADG constraints, then independently verify saved solutions.

Small registered problems are checked by exhaustive binary assignments plus
SciPy/HiGHS continuous LPs; no author optimizer or simulation is rerun.
"""
from collections import Counter, defaultdict, deque
from itertools import product
from pathlib import Path
import hashlib
import json
import math
import numpy as np
from scipy.optimize import linprog

HERE = Path(__file__).resolve().parent
BASE = HERE.parent / 'sadg_preflight_20261004_r16'
EPS, BIG = .01, 1000000.


def load(p):
    return json.loads(Path(p).read_text())


def signature(terms, constant, sense='>'):
    return tuple(sorted(terms.items())), round(constant, 8), sense


def reconstruct(graph, history_rate=False):
    rows, by_agent = [], defaultdict(list)
    for v in graph['vertices']:
        uid = v['uid']
        by_agent[v['agent']].append(v)
        length = sum(math.dist(a[:2], b[:2]) for a,b in zip(v['path_tuples'],v['path_tuples'][1:]))
        scale = 1.25 if history_rate and v['agent']=='agent0' and v['index']>=1 else 1.
        assert abs(length/2*scale - v['nominal_duration']) < 1e-9
        rows.append(signature({uid+'_g':1.,uid+'_s':-1.}, -v['nominal_duration']-EPS))
    expected_type1 = [(v['uid'],v['successor']) for v in graph['vertices'] if v['successor']]
    assert Counter(expected_type1) == Counter(map(tuple,graph['type1']))
    for tail,head in graph['type1']:
        rows.append(signature({head+'_s':1.,tail+'_g':-1.},-EPS))
    for group in graph['groups']:
        binary = group['switchable'] and group['within_horizon']
        for dep in group['dependencies']:
            tail,head = dep['active']
            terms = {head+'_s':1.,tail+'_g':-1.}
            if binary:
                terms[group['uid']] = BIG
            rows.append(signature(terms,-EPS))
            if binary:
                tail,head = dep['forward'] if dep['b'] else dep['reverse']
                rows.append(signature({head+'_s':1.,tail+'_g':-1.,group['uid']:-BIG}, BIG-EPS))
    terminal = {}
    for chain in by_agent.values():
        chain.sort(key=lambda v:v['index'])
        terminal[chain[-1]['uid']+'_g'] = 1.
        first = next((v for v in chain if v['status'] != 'COMPLETED'),None)
        if first is None:
            uid,bound = chain[-1]['uid'],0.
        else:
            uid = first['uid']
            bound = first['nominal_duration'] * (1-first['progress']) if first['status']=='IN_PROGRESS' else first['nominal_duration']
        rows.append(signature({uid+'_g':1.},-bound))
    return Counter(rows),terminal


def graph_check(before, after, values):
    a = {v['uid']:v for v in before['vertices']}
    b = {v['uid']:v for v in after['vertices']}
    assert set(a)==set(b) and before['type1']==after['type1']
    for uid in a:
        assert {k:v for k,v in a[uid].items() if k!='registered_incoming'} == {
            k:v for k,v in b[uid].items() if k!='registered_incoming'}
    edges = list(map(tuple,after['type1']))
    changed = []
    for old,new in zip(before['groups'],after['groups']):
        assert old['uid']==new['uid']
        bit = int(round(values.get(old['uid'],0.)))
        if bit:
            assert old['switchable'] and old['within_horizon']
            changed.append(old['uid'])
        for d,e in zip(old['dependencies'],new['dependencies']):
            expect = (d['forward'] if d['b'] else d['reverse']) if bit else d['active']
            assert e['active']==expect and e['b']==(not d['b'] if bit else d['b'])
            if bit:
                assert a[e['active'][1]]['status']=='STAGED'
            edges.append(tuple(e['active']))
    indeg = Counter({uid:0 for uid in a})
    outgoing = defaultdict(list)
    for u,v in edges:
        assert u in a and v in a
        indeg[v]+=1; outgoing[u].append(v)
    queue = deque(uid for uid,n in indeg.items() if n==0)
    visited = []
    while queue:
        u=queue.popleft();visited.append(u)
        for v in outgoing[u]:
            indeg[v]-=1
            if indeg[v]==0: queue.append(v)
    assert len(visited)==len(a),'cyclic adopted graph'
    return changed


def verify_case(path):
    before,after = load(path/'graph_before.json'),load(path/'graph_after.json')
    models=load(path/'models.json');assert len(models)==1
    m=models[0]; result=load(path/'result.json')
    assert result['error'] is None and m['status']=='OPTIMAL'
    history_rate = path.name in ('mini_public_history_rate', 'mini_measured_history_rate')
    if history_rate:
        adapter = load(BASE/'inputs'/(path.name+'.json'))
        assert adapter['unfinished_duration_scale'] == {'agent0':1.25,'agent1':1.}
        assert adapter['core_optimizer_unchanged']
    expected,obj=reconstruct(before, history_rate)
    actual=Counter(signature(r['terms'],r['constant'],r['sense']) for r in m['constraints'])
    assert expected==actual,('semantic constraint mismatch',path.name,expected-actual,actual-expected)
    assert m['objective_expression']=={'constant':0.,'terms':obj}
    variables=m['variables'];idx={v['name']:i for i,v in enumerate(variables)}
    vals={v['name']:v['value'] for v in variables}
    assert len(idx)==len(variables)
    worst=0.
    for r in m['constraints']:
        lhs=r['constant']+sum(coef*vals[name] for name,coef in r['terms'].items())
        violation=max(0.,-lhs) if r['sense']=='>' else max(0.,lhs) if r['sense']=='<' else abs(lhs)
        worst=max(worst,violation)
    assert worst<1e-6
    for v in variables:
        if v['type']=='B':assert abs(v['value']-round(v['value']))<1e-7 and 0<=round(v['value'])<=1
        if v['lb'] is not None:assert v['value']>=v['lb']-1e-6
        if v['ub'] is not None:assert v['value']<=v['ub']+1e-6
    objective=sum(c*vals[n] for n,c in obj.items())
    assert abs(objective-m['objective'])<1e-6
    changed=graph_check(before,after,vals)
    binaries=[v['name'] for v in variables if v['type']=='B']
    assignments=[]
    if len(binaries)<=10 and len(variables)<1000:
        c=np.zeros(len(variables))
        for name,coef in obj.items():c[idx[name]]=coef
        A,B=[],[]
        for r in m['constraints']:
            assert r['sense']=='>'
            row=np.zeros(len(variables))
            for name,coef in r['terms'].items():row[idx[name]]=-coef
            A.append(row);B.append(r['constant'])
        bounds=[(None if v['lb'] is None or abs(v['lb'])>1e100 else v['lb'],
                 None if v['ub'] is None or abs(v['ub'])>1e100 else v['ub']) for v in variables]
        for bits in product((0,1),repeat=len(binaries)):
            fixed=list(bounds)
            for name,bit in zip(binaries,bits):fixed[idx[name]]=(bit,bit)
            lp=linprog(c,A_ub=np.array(A),b_ub=np.array(B),bounds=fixed,method='highs')
            assert lp.status in (0,2),lp.message
            assignments.append({'bits':dict(zip(binaries,bits)),'feasible':lp.success,
                                'objective':float(lp.fun) if lp.success else None})
        best=min(x['objective'] for x in assignments if x['feasible'])
        assert abs(best-objective)<1e-6,(path.name,best,objective)
    return dict(case=path.name,vertices=len(before['vertices']),constraints=sum(actual.values()),
                binary_variables=len(binaries),semantic_rows_exact=True,solver_solution_feasible=True,
                max_row_violation=worst,objective=objective,changed_groups=changed,
                independent_optimum_checked=bool(assignments),assignments=assignments,
                source_hashes={f:hashlib.sha256((path/f).read_bytes()).hexdigest()
                               for f in ('graph_before.json','graph_after.json','models.json','result.json')})


def main():
    cases=sorted((BASE/'cases').iterdir())
    # Reuse previously checked small LPs only when all four raw artifacts match.
    prior = {x['case']:x for x in load(HERE/'SADG_INDEPENDENT.json')['cases']} if (HERE/'SADG_INDEPENDENT.json').exists() else {}
    rows, reused = [], []
    for path in cases:
        if not (path/'models.json').exists():
            continue
        old = prior.get(path.name)
        if old and all(hashlib.sha256((path/f).read_bytes()).hexdigest()==h for f,h in old['source_hashes'].items()):
            rows.append(old)
            reused.append(path.name)
        else:
            rows.append(verify_case(path))
    assert len(rows)==12
    result=dict(passed=True,cases=rows,author_calls_rerun=0,simulations_run=0,
                reused_independent_checks=reused,
                independent_LPs=sum(len(x['assignments']) for x in rows),
                scope='author MILP rows, adopted graph and small-problem optimality; not full ROS or physical robot certification')
    (HERE/'SADG_INDEPENDENT.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'passed':True,'cases':len(rows),'independent_LPs':result['independent_LPs'],
                      'changed_groups':{x['case']:x['changed_groups'] for x in rows}},indent=2))


if __name__=='__main__':main()
