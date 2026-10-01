from pathlib import Path
import json,tempfile,copy
import runner,audit,pipeline
HERE=runner.HERE
e=json.loads((HERE/'mechanical_attempt_02/mechanical_N2__RR.receipt.json').read_text());original=pipeline.records(e);results=[]
def modify(rows,name):
 if name=='future_goal':next(r for r in rows if r['event']=='planner_request')['goals'][0]['id']+=1
 elif name=='plan_order':next(r for r in rows if r['event']=='official_move_committed')['dependency_departure_started']='m-999-0'
 elif name=='wrong_service':next(r for r in rows if r['event']=='task_service')['goal'][0]+=1
 elif name=='false_certificate':
  r=next(r for r in rows if r['event']=='certified_POSITION_committed');r['certified_lower']['lower']+=100000;r['certified_lower']['upper']+=100000
 elif name=='history_feature':next(r for r in rows if r['event']=='actor_decision')['candidates'][0]['features'][10]='999'
 elif name=='missing_candidate':next(r for r in rows if r['event']=='actor_decision')['candidates'].clear()
 elif name=='budget':next(r for r in rows if r['event']=='actor_decision')['remaining_capacity']+=1
 elif name=='END_early':
  r=next(r for r in rows if r['event']=='public_END_delivered');r['public_original_END']['lower']-=100000;r['public_original_END']['upper']-=100000
for name in ['future_goal','plan_order','wrong_service','false_certificate','END_early','history_feature','missing_candidate','budget']:
 rows=copy.deepcopy(original);modify(rows,name)
 with tempfile.TemporaryDirectory(prefix='r7-negative-') as td:
  p=Path(td)/'raw.jsonl';p.write_text(''.join(json.dumps(r)+'\n' for r in rows));copye=dict(e,raw=str(p));rejected=False;reason=None
  try:audit.audit(copye)
  except (AssertionError,KeyError,ValueError) as exc:rejected=True;reason=str(exc)
  assert rejected,name
  results.append(dict(control=name,rejected=True,reason=reason))
runner.write(HERE/'NEGATIVE_CONTROLS_ACTOR.json',results);print(json.dumps(results,indent=2))
