from fractions import Fraction as Q
from collections import Counter,defaultdict
import json
import runner
P=runner.HERE
def main():
 labels=json.loads((P/'TRAIN_CAL_LABELS.json').read_text());models=json.loads((P/'MODELS_FROZEN_BEFORE_TEST.json').read_text())['models'];groups=defaultdict(list)
 for row in labels:groups[row['world'],row['opportunity']].append(row)
 decisions=[]
 for (world,op),rows in sorted(groups.items()):
  truth={r['action']:Q(r['target']) for r in rows};best=max(truth.values());allr={r['action']:r for r in rows}
  for name,m in models.items():
   coef=list(map(Q,m['coefficients']));mask=set(m['masked_slots']);scores={'WAIT':Q(0)}
   for r in rows:
    if r['action']=='WAIT':continue
    scores[r['action']]=coef[0]+sum((Q(f)*coef[j+1] for j,f in enumerate(r['features']) if j not in mask),Q(0))
   selected='WAIT';value=Q(0)
   for action in sorted((a for a in scores if a!='WAIT'),key=int):
    if scores[action]>value:selected=action;value=scores[action]
   decisions.append(dict(world=world,opportunity=op,split=rows[0]['split'],model=name,remaining=rows[0]['remaining_capacity'],candidates=len(rows)-1,selected=selected,predicted=str(scores[selected]),actual_advantage=str(truth[selected]),actual_task_gain=allr[selected]['whole_service_gain'],best_advantage=str(best),regret=str(best-truth[selected]),scores={a:str(s) for a,s in scores.items()},truth={a:str(t) for a,t in truth.items()}))
 summary={}
 for split in ['train','calibration']:
  summary[split]={}
  for model in models:
   ds=[r for r in decisions if r['split']==split and r['model']==model]
   summary[split][model]=dict(opportunities=len(ds),queries=sum(r['selected']!='WAIT' for r in ds),optimal_tied_choices=sum(Q(r['regret'])==0 for r in ds),task_advantage_sum=sum(r['actual_task_gain'] for r in ds),advantage_sum=str(sum((Q(r['actual_advantage']) for r in ds),Q(0))),regret_sum=str(sum((Q(r['regret']) for r in ds),Q(0))))
 runner.write(P/'LABEL_DECISION_DIAGNOSTICS.json',dict(post_freeze_reporting_only=True,no_hyperparameter_selection=True,summary=summary,decisions=decisions))
 print(json.dumps(summary,indent=2),flush=True)
if __name__=='__main__':main()
