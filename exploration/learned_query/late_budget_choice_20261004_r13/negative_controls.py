"""Corrupt frozen-deployment evidence and require independent rejection."""
from pathlib import Path
import copy,json,tempfile
import runner,audit
P=runner.HERE
def first(rs,event,test=lambda r:True):return next(r for r in rs if r['event']==event and test(r))
def rows(e):return [json.loads(line) for line in Path(e['raw']).open()]
def main():
 es=[json.loads(p.read_text()) for p in sorted((P/'runs').glob('*.receipt.json'))];learned=next((e for e in es if e['policy']=='full' and any(r['event']=='macro_choice' for r in rows(e))),None);skip=next((e for e in es if e['policy']=='macro_LD' and any(r['event']=='actor_decision' and r['intervention_index']==2 for r in rows(e))),None);cases=[]
 def change_score(rs):first(rs,'macro_choice')['scores'][1]['total']='999'
 def change_task_head(rs):first(rs,'macro_choice')['scores'][1]['tasks']='999'
 def gate_budget(rs):first(rs,'macro_choice')['features'][7]='999'
 def gate_history(rs):first(rs,'macro_choice')['features'][0]='999'
 def gate_count(rs):first(rs,'macro_choice')['features'][6]='999'
 def margin(rs):first(rs,'macro_choice')['margin']='999'
 def option(rs):g=first(rs,'macro_choice');g['selected_option']='LD' if g['selected_option']!='LD' else 'C'
 def calls(rs):first(rs,'macro_choice')['inference_calls']=2
 def duplicate_gate(rs):g=first(rs,'macro_choice');rs.insert(rs.index(g)+1,copy.deepcopy(g))
 def missing_gate(rs):rs.remove(first(rs,'macro_choice'))
 def second(rs):return first(rs,'actor_decision',lambda r:r['intervention_index']==2)
 def stage(rs):second(rs)['pair_stage']=1
 def anchor(rs):second(rs)['anchor_move']+='-old'
 def agent(rs):second(rs)['anchor_agent']+=1
 def eligibility(rs):second(rs)['second_eligible'].append(second(rs)['anchor_move'])
 def early(rs):first(rs,'actor_decision')['intervention_index']=2
 def late_spent(rs):first(rs,'macro_choice')['spent']=0
 def late_target(rs):first(rs,'macro_choice')['target_move']+='-alias'
 def premature_choice(rs):
  gate=first(rs,'macro_choice');rs.remove(gate);decision=first(rs,'actor_decision');gate['at']=copy.deepcopy(decision['at']);rs.insert(rs.index(decision),gate)
 def mode(rs):first(rs,'actor_decision',lambda r:r['opportunity']>1)['decision_mode']='WAIT'
 def capacity(rs):first(rs,'actor_decision',lambda r:r['opportunity']>1)['remaining_capacity']+=1
 def omit(rs):first(rs,'actor_decision')['candidates'].pop()
 def future(rs):first(rs,'planner_request')['goals'][0]['id']+=1
 def cert(rs):first(rs,'certified_POSITION_committed')['certified_lower']['lower']+=100000
 def service(rs):first(rs,'task_service')['goal'][0]+=1
 def skipped_alias(rs):first(rs,'public_candidate_visibility',lambda r:bool(r['skip_state']))['skip_state'][0][1]+='-alias'
 def remove_clear(rs):rs.remove(first(rs,'public_SKIP_cleared_normal_END'))
 def private_clear(rs):
  clear=first(rs,'public_SKIP_cleared_normal_END');rs.remove(clear);end=first(rs,'physical_original_END',lambda r:r['id']==clear['id']);clear['at']=copy.deepcopy(end['at']);rs.insert(rs.index(end)+1,clear)
 jobs=[(name,learned,fn) for name,fn in [('macro_total_score',change_score),('macro_task_head',change_task_head),('gate_budget_feature',gate_budget),('gate_history_feature',gate_history),('gate_candidate_count',gate_count),('shared_margin',margin),('selected_complete_macro',option),('repeated_inference_count',calls),('duplicate_macro_choice',duplicate_gate),('missing_macro_choice',missing_gate),('gate_before_half_budget',late_spent),('gate_target_alias',late_target),('premature_model_call',premature_choice)]]
 jobs += [(name,skip,fn) for name,fn in [('second_stage',stage),('old_occurrence_anchor',anchor),('wrong_agent_anchor',agent),('wrong_second_set',eligibility),('second_on_first_event',early),('wrong_fixed_tail',mode),('budget_not_consumed',capacity),('candidate_omission',omit),('future_head',future),('false_certificate',cert),('wrong_task_service',service),('SKIP_alias',skipped_alias),('SKIP_missing_clear',remove_clear),('SKIP_private_END_clear',private_clear)]]
 with tempfile.TemporaryDirectory(prefix='r13-negative-') as td:
  for name,episode,mutate in jobs:
   if episode is None:
    cases.append(dict(case=name,rejected=None,not_applicable=True,reason='No registered realized gate/second-SKIP source; no synthetic scientific trajectory created'));continue
   rs=rows(episode);mutate(rs);path=Path(td)/(name+'.jsonl');path.write_text(''.join(json.dumps(r)+'\n' for r in rs));e=copy.deepcopy(episode);e['raw']=str(path);e['raw_sha256']=runner.sha(path)
   try:audit.audit(e)
   except (AssertionError,KeyError,AttributeError,IndexError) as ex:cases.append(dict(case=name,rejected=True,reason=str(ex),world=episode['world'],policy=episode['policy'],source_raw_sha256=episode['raw_sha256']))
   else:raise AssertionError('negative accepted '+name)
 runner.write(P/'NEGATIVE_CONTROLS.json',dict(passed=True,rejected=sum(c['rejected'] is True for c in cases),not_applicable=sum(c.get('not_applicable',False) for c in cases),cases=cases));print('rejected/NA negative controls',sum(c['rejected'] is True for c in cases),sum(c.get('not_applicable',False) for c in cases),flush=True)
if __name__=='__main__':main()
