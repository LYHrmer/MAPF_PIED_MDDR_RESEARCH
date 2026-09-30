"""Before native execution: enumerate the frozen public tail factors, never search a length."""
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from objective_task_recovery_audit import candidate_forecast

HERE=Path(__file__).resolve().parent

def run(output):
    source=HERE/'objective_task_run_20260929_02.json'
    raw=json.loads(source.read_text())
    data=None
    for command in raw['commands']:
        for line in command['stdout'].splitlines():
            if line.startswith('{'):
                event=json.loads(line)
                if event.get('event')=='cohort_input':
                    data=event;break
        if data is not None:break
    assert data['alpha']==dict(lower=3000000,upper=3000000,denominator=1000000)
    rows=[]
    for ab in (0,1):
        for ct in (0,1):
            public=copy.deepcopy(data)
            for task in public['tasks']:
                if not (ct if task['demand']=='D3' else ab):task['lengths'].pop()
            for capacity in (0,1,2):
                sequences=[[a,b] for a in ['', 'A','B','C'] for b in ['', 'A','B','C']
                           if (not a or a!=b) and sum(bool(k) for k in (a,b))<=capacity]
                scores=[candidate_forecast(public,s) for s in sequences]
                winner=min(scores,key=lambda c:(Fraction(c['flow']),sum(bool(a) for a in c['sequence'])))
                rows.append(dict(ab_tail=ab,c_tail=ct,capacity=capacity,public_input=public,
                                 candidates=scores,winner=winner['sequence'],flow=winner['flow']))
    witnesses=[r for r in rows if r['capacity']==1 and r['c_tail']==1]
    assert len(witnesses)==2 and all(r['winner']==['C',''] for r in witnesses)
    # Public C is granted at 2.5; its positive first-leg duration cannot end by 2.75.
    assert all(next(t for t in r['public_input']['tasks'] if t['demand']=='D3')['lengths'][0]=='4' for r in witnesses)
    with output.open('x') as stream:
        json.dump(dict(status='passed',kind='public-model feasibility preflight, not native result',
                       source=str(source),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                       active_case_witnesses=len(witnesses),rows=rows),stream,indent=2)
    print('frozen 12 public budget/route cells enumerated; 2 strict early-C active witnesses')

if __name__=='__main__':
    run(HERE/'budget_task_preflight_20260930.json')
