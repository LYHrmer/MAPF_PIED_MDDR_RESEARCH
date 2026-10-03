"""Root independent outcome / actual model-consumption replay for all 40 tests."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import hashlib
import json

P=Path(__file__).resolve().parent
reg=json.loads((P/'REGISTRATION.json').read_text())
model=json.loads((P/'MODELS_FROZEN_BEFORE_TEST.json').read_text())['models']
summary=json.loads((P/'SUMMARY.json').read_text())
results={(r['world'],r['policy']):r for r in json.loads((P/'RESULTS.json').read_text())}
aggregate={p:{'served':0,'queries':0,'fixed_first4_time_sum':Q(0)} for p in reg['policies']}
checks=[];scores=0
for w in [w for w in reg['worlds'] if w['split']=='test']:
    fixed={task['task'] for a in w['robots'] for task in a['tasks'][:4]}
    for policy in reg['policies']:
        receipt=json.loads((P/'runs'/(w['name']+'__'+policy+'.receipt.json')).read_text())
        assert receipt['error'] is None
        raw=Path(receipt['raw']); assert hashlib.sha256(raw.read_bytes()).hexdigest()==receipt['raw_sha256']
        services={};queries=0;replacements=[];decisions=0
        for line in raw.open():
            e=json.loads(line)
            if e['event']=='task_service':
                assert e['task'] not in services and e['original_endpoint_at_rest'] and e['physical_footprint_inside_service_square']
                services[e['task']]=Q(e['at']['lower']+e['at']['upper'],2*e['at']['denominator'])
            elif e['event']=='certified_POSITION_committed':queries+=1
            elif e['event']=='actor_decision':
                decisions+=1
                assert not e['private_progress_input'] and not e['regime_input'] and not e['future_head_input']
                if e['decision_mode'].startswith('ridge_'):
                    replacements.append(e);coefs=list(map(Q,model[e['decision_mode']]['coefficients']))
                    positive=[]
                    for c in e['candidates']:
                        x=list(map(Q,c['features']));assert len(x)==24
                        score=coefs[0]+sum(a*b for a,b in zip(coefs[1:],x));assert score==Q(c['score']);scores+=1
                        assert x[20]==Q(e['remaining_capacity'],16)
                        if score>0:positive.append((score,c['agent'],c['move']))
                    chosen=sorted(positive,key=lambda q:(-q[0],q[1]))[0][2] if positive else ''
                    assert e['selected']==chosen
        expected=results[(w['name'],policy)];assert len(services)==expected['served']==receipt['summary']['served']
        assert queries==expected['queries']==receipt['summary']['queries']
        fixed_sum=sum((services.get(t,Q(w['horizon'])) for t in fixed),Q(0))
        assert fixed_sum==Q(expected['fixed_first4_time_sum'])
        assert len(replacements)==expected['replacements']<=1
        if replacements: assert replacements[0]['remaining_capacity']<=10 and policy.startswith('once_')
        a=aggregate[policy];a['served']+=len(services);a['queries']+=queries;a['fixed_first4_time_sum']+=fixed_sum
        checks.append({'world':w['name'],'policy':policy,'served':len(services),'queries':queries,
                       'model_replacements':len(replacements),'actual_model_choice':replacements[0]['selected'] if replacements else None})
for policy,a in aggregate.items():
    a['fixed_first4_time_sum']=str(a['fixed_first4_time_sum'])
    for k,v in a.items():assert v==summary['test_totals'][policy][k]
out={'passed':True,'heldout_runs':len(checks),'aggregate':aggregate,'exact_model_candidate_scores':scores,
     'runs':checks,'candidate_imports':False,
     'scope':'all native task services/fixed FIFO, every actual model score and selected action, query certificates, frozen input privacy flags; complete independent physics and counterfactual prefix audit supplied separately'}
(P/'ROOT_HELDOUT.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps({k:v for k,v in out.items() if k!='runs'},indent=2))
