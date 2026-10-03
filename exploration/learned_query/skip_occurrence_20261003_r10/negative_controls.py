from pathlib import Path
import json,tempfile,copy
import runner,audit,verify_matched_tail as matched
P=runner.HERE
def first(rs,event,predicate=lambda r:True):return next(r for r in rs if r['event']==event and predicate(r))
def main():
 es=[json.loads(p.read_text()) for p in (P/'runs').glob('*.receipt.json')];valid=[e for e in es if e['error'] is None]
 query=next(e for e in valid if e['policy'].startswith('cf_') and '_QUERY' in e['policy']);skip=next(e for e in valid if e['policy'].startswith('cf_') and '_SKIP' in e['policy']);wait=next(e for e in valid if e['policy'].startswith('cf_') and e['policy'].endswith('_WAIT'));results=[]
 def feature(rs,j):first(rs,'actor_decision')['candidates'][0]['features'][j]='999'
 def tail(rs):
  op=int(query['policy'].split('_')[1]);first(rs,'actor_decision',lambda r:r['opportunity']>op)['decision_mode']='force_WAIT'
 def capacity(rs):
  op=int(query['policy'].split('_')[1]);first(rs,'actor_decision',lambda r:r['opportunity']>op)['remaining_capacity']+=1
 def missing(rs):first(rs,'actor_decision')['candidates'].pop()
 def future(rs):first(rs,'planner_request')['goals'][0]['id']+=1
 def cert(rs):first(rs,'certified_POSITION_committed')['certified_lower']['lower']+=100000
 def service(rs):first(rs,'task_service')['goal'][0]+=1
 def skip_score(rs):first(rs,'actor_decision')['candidates'][0]['skip_score']='100'
 def wrong_agent(rs):first(rs,'public_candidate_visibility',lambda r:bool(r['skip_state']))['skip_state'][0][0]+=1
 def old_action(rs):first(rs,'public_candidate_visibility',lambda r:bool(r['skip_state']))['skip_state'][0][1]+='-old'
 def remove_clear(rs):rs.remove(first(rs,'public_SKIP_cleared_normal_END'))
 def early_clear(rs):
  clear=first(rs,'public_SKIP_cleared_normal_END');rs.remove(clear);end=first(rs,'physical_original_END',lambda r:r['id']==clear['id']);clear['at']=copy.deepcopy(end['at']);rs.insert(rs.index(end)+1,clear)
 cases=[('budget_feature',query,lambda rs:feature(rs,20)),('history_feature',query,lambda rs:feature(rs,10)),('tail_not_pi0',query,tail),('query_budget_not_consumed',query,capacity),('candidate_omission',query,missing),('future_head',query,future),('certificate',query,cert),('task_service',query,service),('SKIP_score',skip,skip_score),('SKIP_agent_alias',skip,wrong_agent),('SKIP_action_alias',skip,old_action),('SKIP_not_cleared',skip,remove_clear),('SKIP_cleared_at_private_END',skip,early_clear)]
 with tempfile.TemporaryDirectory(prefix='r10-negative-') as td:
  for name,episode,mutate in cases:
   rs=matched.rows(episode);mutate(rs);p=Path(td)/(name+'.jsonl');p.write_text(''.join(json.dumps(z)+'\n' for z in rs));e=copy.deepcopy(episode);e['raw']=str(p);e['raw_sha256']=runner.sha(p)
   try:audit.audit(e)
   except (AssertionError,KeyError) as exc:results.append(dict(case=name,rejected=True,reason=str(exc)))
   else:raise AssertionError('negative accepted '+name)
  rs=matched.rows(wait);op=int(wait['policy'].split('_')[1]);current=first(rs,'actor_decision',lambda r:r['opportunity']==op);nxt=first(rs,'actor_decision',lambda r:r['opportunity']==op+1);nxt['at']=copy.deepcopy(current['at'])
  try:matched.check_episode(wait,rs)
  except AssertionError as exc:results.append(dict(case='WAIT_same_time_compensation',rejected=True,reason=str(exc)))
  else:raise AssertionError('same-time WAIT accepted')
 runner.write(P/'NEGATIVE_CONTROLS.json',dict(passed=True,cases=results));print('negative controls rejected',len(results),flush=True)
if __name__=='__main__':main()
