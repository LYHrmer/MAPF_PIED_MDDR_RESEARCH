"""Post-experiment diagnostic: best enumerated one-action branch versus pi0.

No new runs, training, selection or heldout tuning. This is not an optimal
multistep policy and applies only to the 30 registered TRAIN/CAL opportunities.
"""
from pathlib import Path
from fractions import Fraction as Q
from collections import defaultdict
import hashlib
import json

P=Path(__file__).resolve().parent
registration=json.loads((P/'REGISTRATION.json').read_text())
worlds={w['name']:w for w in registration['worlds']}
labels=json.loads((P/'TRAIN_CAL_LABELS.json').read_text())
groups=defaultdict(list)
for row in labels:groups[(row['world'],row['opportunity'])].append(row)
cache={}


def outcome(world,policy):
    key=(world,policy)
    if key in cache:return cache[key]
    w=worlds[world]
    receipt=json.loads((P/'runs'/(world+'__'+policy+'.receipt.json')).read_text())
    assert receipt['error'] is None
    path=Path(receipt['raw']);assert hashlib.sha256(path.read_bytes()).hexdigest()==receipt['raw_sha256']
    fixed={t['task'] for a in w['robots'] for t in a['tasks'][:4]}
    services={}
    for line in path.open():
        e=json.loads(line)
        if e['event']=='task_service':
            assert e['task'] not in services
            services[e['task']]=Q(e['at']['lower']+e['at']['upper'],2*e['at']['denominator'])
    tasks=len(services);assert tasks==receipt['summary']['served']
    restricted=sum((services.get(t,Q(w['horizon'])) for t in fixed),Q(0))
    cache[key]=(tasks,Q(tasks)-restricted/(2*w['horizon']*w['N']*4+1))
    return cache[key]


rows=[]
for (world,opportunity),group in sorted(groups.items()):
    assert worlds[world]['split'] in ['train','calibration']
    assert len(group)==1+2*group[0]['candidate_count']
    wt,wj=outcome(world,group[0]['WAIT_policy'])
    bt,bj=outcome(world,'condition')
    candidates=[(wt+r['whole_service_gain'],wj+Q(r['target']),r['policy']) for r in group]
    best=max(candidates,key=lambda x:x[1])
    assert best[0]==max(c[0] for c in candidates), 'task-priority scalar failed'
    assert best[1]>=bj, 'enumeration must include the original pi0 action'
    rows.append({'world':world,'split':worlds[world]['split'],'opportunity':opportunity,
                 'candidate_count':group[0]['candidate_count'],'WAIT_tasks':wt,'pi0_tasks':bt,
                 'best_enumerated_tasks':best[0],'best_enumerated_policy':best[2],
                 'best_task_gain_vs_pi0':best[0]-bt,'best_utility_gain_vs_pi0':str(best[1]-bj),
                 'best_task_gain_vs_WAIT':best[0]-wt})
report={'scope':'posthoc diagnostic on 30 preregistered TRAIN/CAL opportunities and all98 completed branches; exact same pi0 prefix/tail; no TEST selection or new runs; finite one-intervention headroom, not full-policy optimality',
        'opportunities':len(rows),'whole_task_improvable_vs_pi0':sum(r['best_task_gain_vs_pi0']>0 for r in rows),
        'utility_improvable_vs_pi0':sum(Q(r['best_utility_gain_vs_pi0'])>0 for r in rows),
        'whole_task_improvable_vs_current_WAIT':sum(r['best_task_gain_vs_WAIT']>0 for r in rows),
        'rows':rows,'candidate_imports':False,'new_training_or_simulations':False}
(P/'ROOT_OPPORTUNITY_HEADROOM.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='rows'},indent=2))
