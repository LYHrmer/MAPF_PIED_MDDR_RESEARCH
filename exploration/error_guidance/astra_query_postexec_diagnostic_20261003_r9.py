"""Read frozen R9 test streams; no native execution, refit, or model selection."""
from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import hashlib,json
HERE=Path(__file__).resolve().parent
P=Path('/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/matched_tail_20261003_r9')
rows=[r for r in json.loads((P/'RESULTS.json').read_text()) if r['split']=='test']
cache={};pins={}
def read(world,policy):
 key=world,policy
 if key not in cache:
  receipt_path=P/'runs'/(world+'__'+policy+'.receipt.json')
  receipt=json.loads(receipt_path.read_text());raw=Path(receipt['raw']);data=raw.read_bytes()
  digest=hashlib.sha256(data).hexdigest();assert digest==receipt['raw_sha256']
  pins[str(raw)]=digest
  events=[json.loads(line) for line in data.splitlines()]
  cache[key]=([e for e in events if e['event']=='actor_decision'],
              {e['task']:e['at'] for e in events if e['event']=='task_service'})
 return cache[key]
checks=[]
for row in rows:
 if not row['policy'].startswith('once_'):continue
 decisions,services=read(row['world'],row['policy']);base,baseline_services=read(row['world'],'condition')
 i=next(i for i,e in enumerate(decisions) if e['decision_mode'].startswith('ridge_'));event=decisions[i]
 original=next(e for e in base if e['opportunity']==event['opportunity'])
 assert event['at']==original['at'] and event['remaining_capacity']==original['remaining_capacity']
 check={'world':row['world'],'policy':row['policy'],'changed':event['selected']!=original['selected'],
        'candidate_count':len(event['candidates']),'selected':event['selected'],
        'condition_selected':original['selected'],'all_task_service_times_identical':services==baseline_services}
 if not event['selected']:
  following=decisions[i+1];a=event['at'];b=following['at']
  check.update(next_selected=following['selected'],next_candidates=[c['move'] for c in following['candidates']],
               next_mode=following['decision_mode'],next_at=b,
               time_delta_lower=str(Q(b['lower'],b['denominator'])-Q(a['upper'],a['denominator'])),
               time_delta_upper=str(Q(b['upper'],b['denominator'])-Q(a['lower'],a['denominator'])))
 checks.append(check)
summary={}
for policy in ['once_history','once_nohistory','once_nobudget']:
 chosen=[c for c in checks if c['policy']==policy]
 summary[policy]={'changed':sum(c['changed'] for c in chosen),
  'all_services_identical':all(c['all_task_service_times_identical'] for c in chosen),
  'candidate_counts':dict(Counter(c['candidate_count'] for c in chosen)),
  'all_WAIT_followed_by_same_original_MOVE_query':all(c['next_selected']==c['condition_selected'] and c['next_mode']=='condition' for c in chosen if not c['selected'])}
output={'scope':'post-freeze reporting only; read 24 model and 8 condition heldout streams, no new run or refit',
        'summary':summary,'checks':checks,'raw_sha256':pins}
(HERE/'QUERY_POSTEXEC_DIAGNOSTIC.json').write_text(json.dumps(output,indent=2)+'\n')
print(json.dumps(summary,indent=2))
