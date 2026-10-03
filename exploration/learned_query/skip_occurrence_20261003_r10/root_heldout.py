"""Root audit of all 48 heldout service streams and exact persistent decisions."""
from pathlib import Path
from fractions import Fraction as Q
import hashlib
import json

P=Path(__file__).resolve().parent
reg=json.loads((P/'REGISTRATION.json').read_text())
models=json.loads((P/'MODELS_FROZEN_BEFORE_TEST.json').read_text())['models']
summary=json.loads((P/'SUMMARY.json').read_text())
result={(r['world'],r['policy']):r for r in json.loads((P/'RESULTS.json').read_text())}
aggregate={p:{'served':0,'queries':0,'first4_restricted_time':Q(0)} for p in reg['policies']}
checks=[];total_scores=0
for world in [w for w in reg['worlds'] if w['split']=='test']:
    identity={t['task']:(a,k) for a,r in enumerate(world['robots']) for k,t in enumerate(r['tasks'])}
    fixed={t['task'] for r in world['robots'] for t in r['tasks'][:4]}
    for policy in reg['policies']:
        receipt=json.loads((P/'runs'/(world['name']+'__'+policy+'.receipt.json')).read_text())
        assert receipt['error'] is None
        raw=Path(receipt['raw']);assert hashlib.sha256(raw.read_bytes()).hexdigest()==receipt['raw_sha256']
        services={};counts=[0]*len(world['robots']);queries=0
        skipped=set();pending_clear=None;visible=[];last_decision=None
        replacements=[];installations=clears=masked=0
        for line in raw.open():
            e=json.loads(line);event=e['event']
            if pending_clear is not None:
                assert event=='public_SKIP_cleared_normal_END' and e['id']==pending_clear[0][1] and e['at']==pending_clear[1]
            if event=='task_service':
                t=e['task'];assert t not in services and t in identity
                a,k=identity[t];assert counts[a]==k;counts[a]+=1
                assert e['original_endpoint_at_rest'] and e['physical_footprint_inside_service_square']
                services[t]=Q(e['at']['lower']+e['at']['upper'],2*e['at']['denominator'])
            elif event=='public_candidate_visibility':
                assert {tuple(x) for x in e['skip_state']}==skipped
                assert e['visible_candidates']==[x for x in e['raw_candidates'] if tuple(x) not in skipped]
                masked+=sum(tuple(x) in skipped for x in e['raw_candidates'])
                visible=e['visible_candidates']
            elif event=='actor_decision':
                last_decision=e
                assert not e['private_progress_input'] and not e['regime_input'] and not e['future_head_input']
                assert e['remaining_capacity']==16-queries
                assert [[c['agent'],c['move']] for c in e['candidates']]==visible
                mode=e['decision_mode']
                if mode in ['force_WAIT','skip_condition','ridge_history','ridge_nohistory']:
                    replacements.append(e)
                    assert policy.startswith('once_') and 0<e['remaining_capacity']<=10
                if mode.startswith('ridge_'):
                    positive=[]
                    for c in e['candidates']:
                        x=list(map(Q,c['features']));assert len(x)==24 and x[20]==Q(e['remaining_capacity'],16)
                        for order,(action,field) in enumerate([('QUERY','score'),('SKIP','skip_score')]):
                            m=models[mode+'_'+action];coefs=list(map(Q,m['coefficients']))
                            score=coefs[0]+sum(a*b for a,b in zip(coefs[1:],x))
                            assert score==Q(c[field]);total_scores+=1
                            if score>0:positive.append((score,order,c['agent'],c['move'],action))
                    chosen=sorted(positive,key=lambda v:(-v[0],v[1],v[2],v[3]))[0] if positive else None
                    assert (e['selected_kind'],e['selected'])==((chosen[4],chosen[3]) if chosen else ('WAIT',''))
            elif event=='public_SKIP_installed':
                assert last_decision['selected_kind']=='SKIP' and last_decision['selected']==e['id']
                c=next(c for c in last_decision['candidates'] if c['move']==e['id'])
                key=(c['agent'],c['move']);assert key not in skipped
                skipped.add(key);installations+=1
            elif event=='public_END_delivered':
                key=(e['agent'],e['move'])
                if key in skipped:pending_clear=(key,e['at'])
            elif event=='public_SKIP_cleared_normal_END':
                assert pending_clear is not None
                skipped.remove(pending_clear[0]);pending_clear=None;clears+=1
            elif event=='certified_POSITION_committed':
                assert last_decision['selected_kind']=='QUERY' and last_decision['selected']==e['move']
                assert all(k[1]!=e['move'] for k in skipped)
                queries+=1;assert queries<=16
        assert pending_clear is None
        expected=result[(world['name'],policy)]
        assert len(services)==expected['served']==receipt['summary']['served']
        assert queries==expected['queries']==receipt['summary']['queries']
        restricted=sum((services.get(t,Q(world['horizon'])) for t in fixed),Q(0))
        assert restricted==Q(expected['first4_restricted_time'])
        assert len(replacements)<=(1 if policy.startswith('once_') else 0)
        assert installations==clears+len(skipped)
        a=aggregate[policy];a['served']+=len(services);a['queries']+=queries;a['first4_restricted_time']+=restricted
        checks.append({'world':world['name'],'policy':policy,'served':len(services),'queries':queries,
                       'replacement_kind':replacements[0]['selected_kind'] if replacements else None,
                       'skip_installs':installations,'normal_END_clears':clears,'censored_skips':len(skipped),
                       'raw_candidate_mask_occurrences':masked})
for policy,a in aggregate.items():
    a['first4_restricted_time']=str(a['first4_restricted_time'])
    for k,v in a.items():assert summary['totals'][policy][k]==v
report={'passed':True,'heldout_runs':len(checks),'aggregate':aggregate,'exact_candidate_action_scores':total_scores,
        'candidate_imports':False,'runs':checks,
        'scope':'raw services and FIFO identity, exact QUERY/SKIP scoring and deterministic tie rule, real budgets, candidate filtering and public-END-only skip lifetime; physical geometry independently checked by separate auditor'}
(P/'ROOT_HELDOUT.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='runs'},indent=2))
