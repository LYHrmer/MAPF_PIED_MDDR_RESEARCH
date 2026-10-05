"""In-memory negative controls; original evidence is never modified."""
import sys
sys.dont_write_bytecode=True
import copy
import json
from pathlib import Path
from audit_episode import Auditor,CAS,canon,ROOT

HERE=Path(__file__).resolve().parent
EP=ROOT/'episodes/maze-32-32-2__s06__n16__bounded_pause/learned_structural/episode.json'
a=Auditor(EP);a.events_and_outcomes()
key=next(k for k,p in a.predictions.items() if p['context']['status']=='IN_PROGRESS' and p['context']['elapsed']>0)
original=copy.deepcopy(a.predictions[key]);results=[]
for name,mutate in [
    ('elapsed_includes_dependency_wait',lambda p:p['context'].__setitem__('elapsed',p['context']['elapsed']+5)),
    ('future_END_in_features',lambda p:p['context']['completed_history'].append(dict(nominal_duration=1,duration=9,start=p['time'],end=p['time']+9,delivered=p['time']+9))),
    ('conditional_mean_replaced_by_zero',lambda p:p['predictor_output'].__setitem__('remaining_time',0.)),
    ('future_ratio_corrupted',lambda p:p['predictor_output'].__setitem__('future_duration_ratio',99.)),
    ('predictor_private_field',lambda p:p['context'].__setitem__('private_speed',.5))]:
    p=copy.deepcopy(original);mutate(p);newkey=canon(p);a.predictions[newkey]=p
    start=len(a.errors);a.check_prediction(newkey);errors=a.errors[start:]
    assert errors,name
    results.append(dict(case=name,rejected=True,failed_checks=sorted({r['check'] for r in errors})))
position=next(p for p in a.predictions.values() if p['delivered_position'] is not None)
p=copy.deepcopy(position);p['delivered_position']=None;p['provider']='end_history_predictor'
k=canon(p);a.predictions[k]=p;start=len(a.errors);a.check_prediction(k)
assert len(a.errors)>start
results.append(dict(case='delivered_POSITION_silently_ignored',rejected=True,failed_checks=sorted({r['check'] for r in a.errors[start:]})))
ref=a.e['initial_graph_ref'];store=CAS(a.e['evidence_store']);store.get(ref)
for name,change in [('cached_CAS_byte_count',{'raw_bytes':ref['raw_bytes']+1}),('CAS_path_traversal',{'path':'../outside.json.gz'})]:
    bad=dict(ref,**change)
    try:store.get(bad)
    except AssertionError:pass
    else:raise AssertionError(name+' escaped verification')
    results.append(dict(case=name,rejected=True))
out=dict(passed=True,cases=results,source_episode=str(EP),raw_modified=False,new_scientific_episodes=0,new_solver_calls=0)
(HERE/'VERIFIER_SELFCHECK.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print(json.dumps(out))
