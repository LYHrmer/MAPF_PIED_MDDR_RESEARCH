import csv,json,math
from fractions import Fraction
from decimal import Decimal
from pathlib import Path
HERE=Path(__file__).resolve().parent
def write(p,o):
    with p.open('x') as f:json.dump(o,f,indent=2);f.write('\n')
def main():
    out=HERE/'scheduled_successor_01';audit=json.loads((HERE/'AUDIT.json').read_text());model=json.loads((out/'MODEL_FROZEN_BEFORE_TEST.json').read_text())
    labels=json.loads((out/'ALL_COUNTERFACTUAL_LABELS.json').read_text());coef=[Fraction(z) for z in model['coefficients']]
    prediction=[]
    for r in labels:
        pred=coef[0]+sum((w*Fraction(x) for w,x in zip(coef[1:],r['features'])),Fraction(0))
        prediction.append(r|dict(prediction=str(pred),prediction_error=float(pred-Fraction(r['target_flow_gain']))))
    errors={}
    for split in ['train','calibration','test']:
        rs=[r for r in prediction if r['split']==split]
        errors[split]=dict(rows=len(rs),cohorts=len({r['cohort_id'] for r in rs}),rmse=math.sqrt(sum(r['prediction_error']**2 for r in rs)/len(rs)),
          mae=sum(abs(r['prediction_error']) for r in rs)/len(rs),target_min=min(float(Fraction(r['target_flow_gain'])) for r in rs),
          target_max=max(float(Fraction(r['target_flow_gain'])) for r in rs),negative_true_gains=sum(Fraction(r['target_flow_gain'])<0 for r in rs),
          positive_true_gains=sum(Fraction(r['target_flow_gain'])>0 for r in rs))
    raw_paths={(e['world_id'],e['policy']):e['raw'] for e in json.loads((out/'RECEIPT.json').read_text())['episodes']}
    episodes=audit['episodes'];by={(e['world_id'],e['policy']):e for e in episodes};testworlds=sorted({e['world_id'] for e in episodes if e['split']=='test'})
    policies=['WAIT','RR','probability','task_rank','structural','ridge'];metrics=[];details=[]
    for cid in sorted({e['cohort_id'] for e in episodes if e['split']=='test'}):
        worlds=[w for w in testworlds if w.startswith(cid+'__')]
        for policy in policies:
            rs=[by[(w,policy)] for w in worlds];wait=[by[(w,'WAIT')] for w in worlds]
            total=sum(Decimal(e['restricted_flow_sum']) for e in rs);base=sum(Decimal(e['restricted_flow_sum']) for e in wait)
            metrics.append(dict(cohort_id=cid,policy=policy,worlds=len(worlds),served_heads=sum(e['served'] for e in rs),assigned_heads=4*len(worlds),
             queries=sum(e['queries'] for e in rs),deadlocked_worlds=sum(e['deadlock'] for e in rs),restricted_flow_sum=str(total),
             restricted_flow_gain_vs_WAIT=str(base-total),extra_heads_vs_WAIT=sum(e['served'] for e in rs)-sum(e['served'] for e in wait)))
    for w in testworlds:
        for p in policies:
            e=by[(w,p)];wait=by[(w,'WAIT')];opt=min([Decimal(wait['restricted_flow_sum'])]+[Decimal(v['restricted_flow_sum']) for (wid,q),v in by.items() if wid==w and q.startswith('forced_')])
            records=[json.loads(x) for x in Path(raw_paths[(w,p)]).read_text().splitlines()]
            choice=next(x['selected'] for x in records if x['event']=='actor_decision')
            details.append(dict(world_id=w,cohort_id=e['cohort_id'],policy=p,served=e['served'],queries=e['queries'],deadlock=e['deadlock'],
              first_selected=choice,restricted_flow_sum=e['restricted_flow_sum'],flow_gain_vs_WAIT=str(Decimal(wait['restricted_flow_sum'])-Decimal(e['restricted_flow_sum'])),
              extra_heads_vs_WAIT=e['served']-wait['served'],oracle_regret=str(Decimal(e['restricted_flow_sum'])-opt)))
    total=[]
    for p in policies:
        rs=[m for m in metrics if m['policy']==p]
        total.append(dict(policy=p,worlds=26,cohorts=2,served_heads=sum(r['served_heads'] for r in rs),assigned_heads=104,
         queries=sum(r['queries'] for r in rs),deadlocked_worlds=sum(r['deadlocked_worlds'] for r in rs),
         flow_sum=str(sum(Decimal(r['restricted_flow_sum']) for r in rs)),flow_gain_vs_WAIT=str(sum(Decimal(r['restricted_flow_gain_vs_WAIT']) for r in rs)),
         extra_heads_vs_WAIT=sum(r['extra_heads_vs_WAIT'] for r in rs)))
    result=dict(trained_model_sha256=audit['trained_model_sha256'],regression=errors,heldout_cohort_metrics=metrics,heldout_total=total,
        test_world_details=details,independent_test_cohorts=2,test_exogenous_worlds=26,source_maps=1,no_statistical_significance_claim=True,
        no_current_world_END_before_first_choice=True,current_p_from_old_train_END=True,formal_external_comparison=False,production_COST=False)
    write(HERE/'RESULTS.json',result)
    for name,rows in [('HELDOUT_ALL_WORLDS.csv',details),('HELDOUT_BY_COHORT.csv',metrics),('ALL_COUNTERFACTUAL_PREDICTIONS.csv',prediction)]:
        with (HERE/name).open('x') as f:
            wr=csv.DictWriter(f,fieldnames=list(rows[0]));wr.writeheader();wr.writerows(rows)
    print(json.dumps({k:v for k,v in result.items() if k not in ['heldout_cohort_metrics','test_world_details']},indent=2))
if __name__=='__main__':main()
