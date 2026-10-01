from pathlib import Path
from collections import Counter,defaultdict
from fractions import Fraction
import csv,json
import runner,pipeline
HERE=runner.HERE
def inspect(e,w):
 rs=pipeline.records(e);census=Counter(str(min(2,r['candidates'])) for r in rs if r['event']=='opportunity_census');cycles=[]
 for line in Path(e['planner']).open():
  z=json.loads(line);q=z['request'];aa=z['result']['actions'];n=len(aa);occ={s:a for a,s in enumerate(q['starts'])};edges={a:occ[q['starts'][a]+[1,q['cols'],-1,-q['cols'],0][aa[a]]] for a in range(n) if aa[a]!=4 and q['starts'][a]+[1,q['cols'],-1,-q['cols'],0][aa[a]] in occ};seen=set()
  for a in edges:
   path=[];at=a
   while at in edges and at not in path and at not in seen:path.append(at);at=edges[at]
   if at in path:
    cyc=path[path.index(at):];cycles.append(dict(round=q['round'],agents=cyc,length=len(cyc)))
   seen.update(path)
 s=e['summary'];count=Counter(r['event'] for r in rs);peragent=Counter(r['agent'] for r in rs if r['event']=='task_service');early=sum(bool(r['removed']) for r in rs if r['event']=='certified_POSITION_committed')
 return dict(world=e['world'],policy=e['policy'],served=s['served'],released=s['task_count'],uncompleted_released=s['uncompleted_heads'],fixed_first4_restricted_time=float(pipeline.fixed_flow(w,rs)),query_count=s['queries'],early_release_queries=early,deadlock=s['deadlock'],true_horizon_reached=s['last_clock']['lower']==w['horizon']*1000000,opportunities_0=census['0'],opportunities_1=census['1'],opportunities_multi=census['2'],max_candidates=s['max_candidates'],official_plan_calls=s['official_plan_calls'],official_long_cycles=cycles,service_by_agent=dict(peragent),physical_END=count['physical_original_END'],normal_END=count['public_END_delivered'],wall_seconds=e['seconds'])
def main():
 rows=[]
 for directory in ['mechanical_attempt_02','statistical_attempt_01']:
  out=HERE/directory;reg=json.loads((out/'REGISTRATION.json').read_text());wm={w['name']:w for w in reg['worlds']}
  for p in sorted(out.glob('*.receipt.json')):
   e=json.loads(p.read_text())
   if e['error'] is not None:rows.append(dict(world=e['world'],policy=e['policy'],error=e['error']));continue
   r=inspect(e,wm[e['world']]);r['stage']=directory;r['split']=wm[e['world']].get('split','mechanical');rows.append(r)
 runner.write(HERE/'RESULTS.json',rows)
 columns=['world','policy','split','served','released','uncompleted_released','fixed_first4_restricted_time','query_count','early_release_queries','deadlock','true_horizon_reached','opportunities_0','opportunities_1','opportunities_multi','max_candidates','official_plan_calls','wall_seconds']
 with (HERE/'RESULTS.csv').open('x') as f:
  cw=csv.DictWriter(f,fieldnames=columns,extrasaction='ignore');cw.writeheader();cw.writerows(rows)
 totals={}
 for group in ['mechanical','test_IID','test_SHIFT']:
  for policy in ['WAIT','RR','condition','ridge_history','ridge_nohistory']:
   subset=[r for r in rows if r.get('policy')==policy and (r.get('split')=='mechanical' if group=='mechanical' else r.get('split')=='test' and r['world'].endswith(group.split('_')[1]))]
   if subset:totals[group+'__'+policy]={k:sum(r[k] for r in subset) for k in ['served','fixed_first4_restricted_time','query_count','early_release_queries','opportunities_0','opportunities_1','opportunities_multi']}
 runner.write(HERE/'SUMMARY.json',dict(rows=len(rows),totals=totals,all_cycles=[dict(world=r['world'],policy=r['policy'],cycles=r.get('official_long_cycles')) for r in rows if r.get('official_long_cycles')]))
 print(json.dumps(totals,indent=2))
if __name__=='__main__':main()
