"""Post-test diagnostics only; never used to choose worlds, labels or policies."""
from pathlib import Path
from fractions import Fraction as Q
import json
import runner
P=runner.HERE
def load(name,policy):return [json.loads(z) for z in (P/'runs'/(name+'__'+policy+'.jsonl')).read_text().splitlines()]
def mid(r):return Q(r['at']['lower']+r['at']['upper'],2000000)
def main():
 ds=json.loads((P/'TEST_REPLACEMENT_DECISIONS.json').read_text())['replacements'];out=[]
 for d in ds:
  if not d['changed']:continue
  br=load(d['world'],'condition');lr=load(d['world'],d['policy']);bd=next(x for x in br if x['event']=='actor_decision' and x['opportunity']==d['opportunity']);ld=next(x for x in lr if x['event']=='actor_decision' and x['opportunity']==d['opportunity']);certificate=next(x for x in br if x['event']=='certified_POSITION_committed' and x['move']==bd['selected']);nxt=next((x for x in lr if x['event']=='actor_decision' and x['opportunity']>d['opportunity']),None)
  physical={'official_move_committed','planner_request','original_RUN','physical_original_END','task_service','public_END_delivered','public_head_revealed','native_READY','public_WAIT_ended'}
  identities={kind:[x for x in br if x['event']==kind]==[x for x in lr if x['event']==kind] for kind in ['task_service','original_RUN','planner_request','physical_original_END']}
  out.append(dict(world=d['world'],policy=d['policy'],baseline_source=bd['selected'],baseline_removed=certificate['removed'],baseline_certified_progress=certificate['certified_lower'],learned_action=ld['selected'],next_learned_decision=nxt and dict(opportunity=nxt['opportunity'],selected=nxt['selected'],remaining=nxt['remaining_capacity'],at=nxt['at'],elapsed_midpoint=str(mid(nxt)-mid(ld))),full_planner_motion_END_service_projection_identical=[x for x in br if x['event'] in physical]==[x for x in lr if x['event'] in physical],event_type_identical=identities))
 runner.write(P/'REPLACEMENT_MECHANISM_DIAGNOSTICS.json',dict(post_test_only=True,changed_replacements=len(out),baseline_empty_releases=sum(not x['baseline_removed'] for x in out),identical_motion_and_service=sum(x['full_planner_motion_END_service_projection_identical'] for x in out),event_type_identical_counts={kind:sum(x['event_type_identical'][kind] for x in out) for kind in ['task_service','original_RUN','planner_request','physical_original_END']},cases=out));print(json.dumps({k:v for k,v in json.loads((P/'REPLACEMENT_MECHANISM_DIAGNOSTICS.json').read_text()).items() if k!='cases'},indent=2),flush=True)
if __name__=='__main__':main()
