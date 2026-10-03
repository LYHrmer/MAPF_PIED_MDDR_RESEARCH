from pathlib import Path
import json,tempfile,copy
import runner,audit_all,verify_matched_tail as matched
P=runner.HERE
def first(rs,event,predicate=lambda r:True):return next(r for r in rs if r['event']==event and predicate(r))
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());worlds={w['name']:w for w in reg['worlds']};es=[json.loads(p.read_text()) for p in (P/'runs').glob('*.receipt.json')];valid=[e for e in es if e['error'] is None]
 query=next(e for e in valid if e['policy'].startswith('cf_') and not e['policy'].endswith('_WAIT'));wait=next(e for e in valid if e['policy'].startswith('cf_') and e['policy'].endswith('_WAIT'));results=[]
 def features(rs,j):first(rs,'actor_decision')['candidates'][0]['features'][j]='999'
 def tail(rs):
  op=int(query['policy'].split('_')[1]);first(rs,'actor_decision',lambda r:r['opportunity']>op)['decision_mode']='force_WAIT'
 def capacity(rs):
  op=int(query['policy'].split('_')[1]);first(rs,'actor_decision',lambda r:r['opportunity']>op)['remaining_capacity']+=1
 def missing(rs):first(rs,'actor_decision')['candidates'].pop()
 def future(rs):first(rs,'planner_request')['goals'][0]['id']+=1
 def cert(rs):first(rs,'certified_POSITION_committed')['certified_lower']['lower']+=100000
 def service(rs):first(rs,'task_service')['goal'][0]+=1
 cases=[('explicit_budget_feature',lambda rs:features(rs,20)),('budget_interaction_feature',lambda rs:features(rs,22)),('history_feature',lambda rs:features(rs,10)),('tail_not_pi0',tail),('query_budget_not_consumed',capacity),('candidate_omission',missing),('future_head',future),('certificate',cert),('task_service',service)]
 with tempfile.TemporaryDirectory(prefix='r9-negative-') as td:
  for name,mutate in cases:
   rs=matched.rows(query);mutate(rs);p=Path(td)/(name+'.jsonl');p.write_text(''.join(json.dumps(z)+'\n' for z in rs));e=copy.deepcopy(query);e['raw']=str(p);e['raw_sha256']=runner.sha(p)
   try:audit_all.check(e,worlds[e['world']])
   except AssertionError as exc:results.append(dict(case=name,rejected=True,reason=str(exc)))
   else:raise AssertionError('negative accepted '+name)
  rs=matched.rows(wait);op=int(wait['policy'].split('_')[1]);current=first(rs,'actor_decision',lambda r:r['opportunity']==op);nxt=first(rs,'actor_decision',lambda r:r['opportunity']==op+1);nxt['at']=copy.deepcopy(current['at'])
  try:matched.check_episode(wait,rs)
  except AssertionError as exc:results.append(dict(case='WAIT_same_time_compensation',rejected=True,reason=str(exc)))
  else:raise AssertionError('same-time WAIT accepted')
 runner.write(P/'NEGATIVE_CONTROLS.json',dict(passed=True,cases=results));print(json.dumps(results,indent=2),flush=True)
if __name__=='__main__':main()
