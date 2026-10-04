"""Verify frozen ridge equations, fold isolation, outcomes and finite DP bounds."""
from fractions import Fraction as F
from pathlib import Path
import hashlib
import json
import numpy as np

HERE=Path(__file__).resolve().parent
BASE=Path('/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/budget_frontier_20261004_r17')
def load(p): return json.loads(p.read_text())
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def mid(v): return (F(v['T_lower'])+F(v['T_upper']))/2
def total(values):
    return {'tasks':sum(v['tasks'] for v in values),'queries':sum(v['queries'] for v in values),
            'T_lower':str(sum((F(v['T_lower']) for v in values),F(0))),
            'T_upper':str(sum((F(v['T_upper']) for v in values),F(0)))}
def select(scores):
    candidates=list(scores)
    best=max(scores[a][0] for a in candidates)
    candidates=[a for a in candidates if scores[a][0]>=best-1e-6]
    best=min(scores[a][1] for a in candidates)
    candidates=[a for a in candidates if scores[a][1]<=best+1e-3]
    best=min(scores[a][2] for a in candidates)
    candidates=[a for a in candidates if scores[a][2]<=best+1e-6]
    return next(a for a in ('STOP','C','LD') if a in candidates)


def model_check(model, data):
    subset=[data[w] for w in model['training_worlds']]
    assert len(subset)==2*len(model['training_families'])
    assert {r['family'] for r in subset}==set(model['training_families'])
    x=np.array([[float(F(v)) for v in r['features']] for r in subset])
    mean=x.mean(axis=0);scale=x.std(axis=0);scale[scale<1e-12]=1
    assert np.allclose(mean,model['mean'],rtol=0,atol=1e-12)
    assert np.allclose(scale,model['scale'],rtol=0,atol=1e-12)
    z=np.column_stack((np.ones(len(x)),(x-mean)/scale))
    targets=[]
    for r in subset:
        o=r['outcomes'];stop=o['STOP'];y=[]
        for a in ('C','LD'):
            y += [o[a]['tasks']-stop['tasks'],float(mid(o[a])-mid(stop)),o[a]['queries']-stop['queries']]
        targets.append(y)
    y=np.array(targets);beta=np.array(model['standardized_coefficients'])
    ridge=np.eye(z.shape[1])*model['lambda_value'];ridge[0,0]=0
    residual=(.5*z.T@z+ridge)@beta-.5*z.T@y
    assert np.max(np.abs(residual))<1e-8
    raw=np.array(model['raw_coefficients'])
    assert np.allclose(np.column_stack((np.ones(len(x)),x))@raw,z@beta,rtol=0,atol=1e-8)
    return float(np.max(np.abs(residual)))


def dp_check(groups, report):
    states={(0,0):F(0)}
    for options in groups:
        nxt={}
        for (queries,tasks),t in states.items():
            for v in options:
                key=(queries+v['queries'],tasks+v['tasks']);value=t+mid(v)
                if key not in nxt or value<nxt[key]:nxt[key]=value
        states=nxt
    assert len(states)==report['state_count']
    best_by_tasks={};front=set()
    for (q,n),t in sorted(states.items(),key=lambda p:(p[0][0],-p[0][1],p[1])):
        if not any(n0>=n and t0<=t for n0,t0 in best_by_tasks.items()):front.add((q,n,t))
        best_by_tasks[n]=min(t,best_by_tasks.get(n,t))
    recorded={(r['queries'],r['tasks'],mid(r)) for r in report['midpoint_Pareto']}
    assert recorded==front
    return {'states':len(states),'frontier_points':len(front),'max_tasks':max(n for q,n in states)}


def main():
    rows=load(BASE/'DATASET.json');data={r['world']:r for r in rows};families={r['family'] for r in rows}
    assert len(rows)==24 and len(families)==12
    old13=BASE.parent/'late_budget_choice_20261004_r13'
    old16=BASE.parent/'stop_value_20261004_r16'
    labels={(r['world'],r['option']):r for r in load(old13/'TRAIN_CAL_LABELS.json') if r['split']=='train'}
    stop={r['world']:r['STOP'] for r in load(old16/'TRAIN_PAIRS.json')}
    for r in rows:
        assert {q['budget'] for q in rows if q['family']==r['family']}=={8,16}
        for arm,o in r['outcomes'].items():
            source=stop[r['world']] if arm=='STOP' else labels[(r['world'],arm)]
            assert all(o[k]==source[k] for k in ('tasks','queries','T_lower','T_upper'))
            assert r['raws'][arm]['sha256']==source['raw_sha256']
    residuals=[];folds=load(BASE/'GROUPED_FOLDS.json');predictions={r['world']:r for r in load(BASE/'OOF_PREDICTIONS.json')}
    for fold in folds:
        held=fold['held_family'];m=fold['model']
        assert set(m['training_families'])==families-{held}
        residuals.append(model_check(m,data))
        for r in rows:
            if r['family']!=held:continue
            x=np.array([1]+[float(F(v)) for v in r['features']]);p=x@np.array(m['raw_coefficients'])
            scores={'C':p[:3],'LD':p[3:],'STOP':np.zeros(3)}
            recorded=predictions[r['world']]
            assert all(np.allclose(scores[a],recorded['predictions'][a],rtol=0,atol=1e-8) for a in scores)
            assert select(scores)==recorded['ridge']
        for candidate in fold['inner_validation']:
            values=[]
            for choice in candidate['choices']:
                r=data[choice['world']]
                assert r['family']!=held and choice['held_family']==r['family']
                assert set(choice['training_families'])==families-{held,r['family']}
                assert select(choice['scores'])==choice['arm']
                values.append(r['outcomes'][choice['arm']])
            assert total(values)==candidate['total']
        candidates=fold['inner_validation'];mx=max(c['total']['tasks'] for c in candidates)
        candidates=[c for c in candidates if c['total']['tasks']==mx]
        candidates=[c for c in candidates if not any(F(other['total']['T_upper'])<F(c['total']['T_lower']) for other in candidates)]
        selected=min(candidates,key=lambda c:(c['total']['queries'],-c['lambda_value']))
        assert selected['lambda_value']==fold['lambda_value']
    frozen=load(BASE/'MODEL_FROZEN.json');residuals.append(model_check(frozen['model'],data))
    observed=load(BASE/'OOF_RESULTS.json')['policies']
    for name,report in observed.items():
        values=[]
        for choice in report['choices']:
            values.append(data[choice['world']]['outcomes'][choice['arm']])
        assert total(values)==report['overall']
    frontiers=load(BASE/'ORACLE_FRONTIERS.json');results={}
    for name,budget in [('same_gate_all',None),('same_gate_B8',8),('same_gate_B16',16)]:
        groups=[list(r['outcomes'].values()) for r in rows if budget is None or r['budget']==budget]
        results[name]=dp_check(groups,frontiers[name])
    groups=[[o for r in rows if r['family']==family for o in r['outcomes'].values()] for family in sorted(families)]
    results['episode_start_six_arm_oracle']=dp_check(groups,frontiers['episode_start_six_arm_oracle'])
    out={'passed':True,'contexts':len(rows),'independent_families':len(families),'frozen_model_normal_equations_checked':len(residuals),'maximum_ridge_normal_residual':max(residuals),'DP':results,'totals':{k:v['overall'] for k,v in observed.items()},'source_hashes':{p.name:sha(p) for p in BASE.glob('*.json')},'scope':'No new training or execution; independently verify frozen math/labels/selections and exact finite-action upper bounds. Original physical audits are reused.'}
    (HERE/'QUERY_INDEPENDENT.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'passed':True,'models':len(residuals),'DP':results}))


if __name__=='__main__':main()
