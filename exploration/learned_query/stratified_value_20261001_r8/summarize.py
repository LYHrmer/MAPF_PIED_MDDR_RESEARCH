from pathlib import Path
from fractions import Fraction as F
from collections import Counter,defaultdict
import csv,json
import runner
P=runner.HERE
def load(p):return json.loads(p.read_text())
def rows(e):return [json.loads(x) for x in Path(e['raw']).read_text().splitlines()]
def main():
 reg=load(P/'REGISTRATION.json');worlds={w['name']:w for w in reg['worlds']};entries=[load(p) for p in sorted((P/'runs').glob('*.receipt.json'))];entries += [load(p) for p in sorted((P/'scale_guard_successor/runs').glob('*.receipt.json'))];labels=load(P/'TRAIN_CAL_LABELS.json');models=load(P/'MODELS_FROZEN_BEFORE_TEST.json');results=[];groups={};allcensus=Counter()
 for e in entries:
  w=worlds[e['world']];rr=rows(e);ds=[r for r in rr if r['event']=='actor_decision'];multi=[r for r in ds if len(r['candidates'])>1];queries=[r for r in rr if r['event']=='certified_POSITION_committed'];census=Counter(str(min(2,r['candidates'])) for r in rr if r['event']=='opportunity_census');allcensus.update(census)
  base=dict(world=e['world'],map=w['map_name'],N=w['N'],split=w['split'],seed=w['seed'],shift=w['shift'],policy=e['policy'],error=e['error'],seconds=e['seconds'],census=dict(census),multi_opportunities=len(multi),multi_with_capacity=sum(r['remaining_capacity']>0 for r in multi),multi_selected=sum(bool(r['selected']) for r in multi),single_selected=sum(bool(r['selected']) for r in ds if len(r['candidates'])==1),selected_by_time_bin=dict(Counter(min(3,r['at']['lower']//32000000) for r in ds if r['selected'])),early_source_release=sum(bool(r['removed']) for r in queries),scored_candidates=sum(len(r['candidates']) for r in ds),positive_candidate_scores=sum(F(c['score'])>0 for r in ds for c in r['candidates']))
  base['execution_generation']='scale_guard_successor' if '/scale_guard_successor/' in e['raw'] else 'original_R8'
  eligible=[r for r in multi if r['remaining_capacity']>0 and (not e['policy'].startswith('paced_') or e['capacity']-r['remaining_capacity']<min(16,4*(1+int(r['at']['lower']//32000000))))]
  base.update(multi_admissible=len(eligible),multi_abstain_when_admissible=sum(not r['selected'] for r in eligible))
  if e['summary'] is not None:
   s=e['summary'];times={r['task']:F(r['at']['lower']+r['at']['upper'],2000000) for r in rr if r['event']=='task_service'};flow=sum((times.get(t['task'],F(w['horizon'])) for a in w['robots'] for t in a['tasks'][:4]),F(0))
   base.update(served=s['served'],queries=s['queries'],deadlock=s['deadlock'],last_clock=s['last_clock'],fixed_first4_restricted_time=str(flow),official_plan_calls=s['official_plan_calls'])
  results.append(base)
  if w['split'] in ['test','scale'] and e['summary'] is not None:
   key=(w['split'],e['policy']);g=groups.setdefault(key,dict(split=w['split'],policy=e['policy'],worlds=0,served=0,queries=0,multi_opportunities=0,multi_selected=0,deadlocks=0,fixed_first4_restricted_time=F(0)))
   g['worlds']+=1
   for key2 in ['served','queries','multi_opportunities','multi_selected']:g[key2]+=base[key2]
   g['deadlocks']+=base['deadlock'];g['fixed_first4_restricted_time']+=F(base['fixed_first4_restricted_time'])
 for g in groups.values():g['fixed_first4_restricted_time']=str(g['fixed_first4_restricted_time'])
 labelstats={}
 for split in ['train','calibration']:
  rs=[r for r in labels if r['split']==split];valid=[r for r in rs if r.get('target') is not None]
  labelstats[split]=dict(rows=len(rs),worlds=len({r['world'] for r in rs}),opportunities=len({(r['world'],r['opportunity']) for r in rs}),distinct_source_MOVEs=len({(r['world'],r['move']) for r in rs}),sign=dict(Counter('positive' if F(r['target'])>0 else 'negative' if F(r['target'])<0 else 'zero' for r in valid)),whole_task_gain=dict(Counter(str(r['whole_service_gain']) for r in valid)),multi_rows=sum(r['candidate_count']>1 for r in rs),execution_failures=len(rs)-len(valid))
 labelworlds=[]
 for name in sorted({r['world'] for r in labels}):
  rs=[r for r in labels if r['world']==name];valid=[r for r in rs if r.get('target') is not None]
  labelworlds.append(dict(world=name,rows=len(rs),distinct_source_MOVEs=len({r['move'] for r in rs}),whole_task_gain=dict(Counter(str(r['whole_service_gain']) for r in valid)),target_sign=dict(Counter('positive' if F(r['target'])>0 else 'negative' if F(r['target'])<0 else 'zero' for r in valid))))
 calibration={}
 cal=[r for r in labels if r['split']=='calibration' and r.get('target') is not None];ops=defaultdict(list)
 for r in cal:ops[(r['world'],r['opportunity'])].append(r)
 for name,m in models['models'].items():
  chosen=[];pairs=0;correct=0;nontrivial=0
  def score(r):return F(m['coefficients'][0])+sum((F(c)*F(v) for j,(c,v) in enumerate(zip(m['coefficients'][1:],r['features'])) if name!='ridge_nohistory' or j not in range(10,18)),F(0))
  for rs in ops.values():
   ordered=sorted(rs,key=lambda r:(-score(r),r['source']));selected=ordered[0] if score(ordered[0])>0 else None
   if selected:chosen.append(selected)
   if len(rs)>1 and len({F(r['target']) for r in rs})>1:nontrivial+=1
   for i,a in enumerate(rs):
    for b in rs[i+1:]:
     truth=F(a['target'])-F(b['target'])
     if truth:pairs+=1;correct+=(score(a)-score(b))*truth>0
  calibration[name]=dict(diagnostic_only_not_policy_rollout=True,opportunities=len(ops),queries_chosen=sum(1 for _ in chosen),sum_single_probe_task_advantages=sum(r['whole_service_gain'] for r in chosen),sum_single_probe_target=str(sum((F(r['target']) for r in chosen),F(0))),nontrivial_multi_opportunities=nontrivial,strict_pairwise_correct=correct,strict_pairwise_total=pairs)
 waitcensus=Counter()
 for r in results:
  if r['policy']=='WAIT' and r['split'] in ['train','calibration']:waitcensus.update(r['census'])
 out=dict(episodes=len(entries),failed=sum(e['error'] is not None for e in entries),aggregate_census=dict(allcensus),train_cal_WAIT_census=dict(waitcensus),labels=labelstats,label_worlds=labelworlds,groups=list(groups.values()),calibration=calibration,independent_N16_task_families=4,paired_IID_SHIFT_are_correlated=True,production_COST=False,primary_metric='whole_run_completed_FIFO_tasks')
 runner.write(P/'RESULTS.json',results);runner.write(P/'SUMMARY.json',out)
 fields=['world','map','N','split','seed','shift','policy','execution_generation','served','queries','deadlock','fixed_first4_restricted_time','multi_opportunities','multi_with_capacity','multi_admissible','multi_abstain_when_admissible','multi_selected','single_selected','early_source_release','scored_candidates','positive_candidate_scores','seconds','error']
 with (P/'RESULTS.csv').open('x',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields,extrasaction='ignore',lineterminator='\n');writer.writeheader();writer.writerows(results)
 print(json.dumps(out,indent=2),flush=True)
if __name__=='__main__':main()
