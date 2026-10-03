"""Frozen exact model choices versus complete observed counterfactual action sets."""
from fractions import Fraction as Q
from collections import defaultdict,Counter
import json
import runner
P=runner.HERE
def main():
 labels=json.loads((P/'TRAIN_CAL_LABELS.json').read_text());models=json.loads((P/'MODELS_FROZEN_BEFORE_TEST.json').read_text())['models'];groups=defaultdict(list)
 for r in labels:groups[r['world'],r['opportunity']].append(r)
 output=[]
 for (world,op),rows in groups.items():
  variants={}
  assert len(rows)==1+2*rows[0]['candidate_count']
  for variant in ['history','nohistory']:
   choices=[]
   for r in rows:
    if r['action']=='WAIT':score=Q(0)
    else:
     m=models['ridge_'+variant+'_'+r['action']];coefs=list(map(Q,m['coefficients']));features=list(map(Q,r['features']));score=coefs[0]+sum((x*w for j,(x,w) in enumerate(zip(features,coefs[1:])) if j not in m['masked_slots']),Q(0))
    rank=0 if r['action']=='WAIT' else 1 if r['action']=='QUERY' else 2
    choices.append((-score,rank,r['source'] or 0,r['move'] or '',r))
   chosen=min(choices,key=lambda z:z[:4])[-1];best=max(Q(r['target']) for r in rows)
   variants[variant]=dict(action=chosen['action'],source=chosen['source'],target=str(Q(chosen['target'])),best_observed_target=str(best),regret=str(best-Q(chosen['target'])),whole_task_gain=chosen['whole_service_gain'])
  output.append(dict(world=world,opportunity=op,split=rows[0]['split'],candidate_count=rows[0]['candidate_count'],variants=variants,targets=[dict(action=r['action'],source=r['source'],target=r['target'],whole_service_gain=r['whole_service_gain']) for r in rows]))
 summary={}
 for split in ['train','calibration']:
  for variant in ['history','nohistory']:
   rr=[x['variants'][variant] for x in output if x['split']==split];summary[split+'_'+variant]=dict(opportunities=len(rr),observed_optimal=sum(Q(x['regret'])==0 for x in rr),total_regret=str(sum((Q(x['regret']) for x in rr),Q(0))),actions=dict(Counter(x['action'] for x in rr)))
 runner.write(P/'LABEL_DECISION_DIAGNOSTICS.json',dict(calibration_used_for_tuning=False,summary=summary,opportunities=output));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
