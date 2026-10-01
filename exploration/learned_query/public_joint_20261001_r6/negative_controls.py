from pathlib import Path
from copy import deepcopy
import json
from audit_joint_replay import Replay,sha
HERE=Path(__file__).resolve().parent

def main():
 out=HERE/'mechanical_attempt_02';rr=json.loads((out/'RECEIPT.json').read_text());reg=json.loads((out/'REGISTRATION.json').read_text());e=next(e for e in rr['episodes'] if e['world_id'].startswith('mechanical_n16') and e['policy']=='RR');w=next(w for w in reg['worlds'] if w['world_id']==e['world_id']);c=next(c for c in json.loads((HERE/'SUPPORT.json').read_text())['mechanical'] if c['cohort_id']==e['cohort_id']);rs=[json.loads(x) for x in Path(e['raw']).read_text().splitlines()];tests=[]
 def check(name,event,mutate):
  ix=next(i for i,x in enumerate(rs) if x['event']==event);prefix=deepcopy(rs[:ix+1]);mutate(prefix[-1]);r=Replay(c,w,e['policy'],e['capacity']);rejected=False;message=''
  try:r.run(prefix)
  except AssertionError as x:rejected=True;message=str(x)
  assert rejected and message!='truncated run';tests.append(dict(name=name,rejected=True,reason=message,event_index=ix))
 check('private_eta_END_rejected','public_END_delivered',lambda x:x.update(private_eta=1))
 check('missing_legal_candidate_rejected','actor_decision',lambda x:x['candidates'].clear())
 check('false_budget_rejected','actor_decision',lambda x:x.update(remaining_capacity=0))
 check('false_controller_lower_rejected','certified_POSITION_committed',lambda x:x.update(certified_lower=dict(lower=0,upper=0,denominator=1000000)))
 check('skipped_future_head_rejected','public_head_revealed',lambda x:x.update(head_index=2))
 check('false_normal_END_time_rejected','public_END_delivered',lambda x:x['at'].update(lower=x['at']['lower']+2,upper=x['at']['upper']+2))
 (HERE/'NEGATIVE_CONTROLS.json').write_text(json.dumps(dict(passed=True,audit_source_sha256=sha(HERE/'audit_joint_replay.py'),source_raw_sha256=e['raw_sha256'],tests=tests),indent=2)+'\n');print(tests)
if __name__=='__main__':main()
