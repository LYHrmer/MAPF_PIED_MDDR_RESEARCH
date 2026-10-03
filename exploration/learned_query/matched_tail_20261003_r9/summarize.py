from pathlib import Path
from fractions import Fraction as Q
from collections import Counter
import json,csv
import runner,verify_matched_tail as matched
P=runner.HERE
def main():
 reg=json.loads((P/'REGISTRATION.json').read_text());worlds={w['name']:w for w in reg['worlds']};es=[json.loads(p.read_text()) for p in (P/'runs').glob('*.receipt.json')];results=[]
 for e in sorted(es,key=lambda e:(e['world'],e['policy'])):
  w=worlds[e['world']];result=dict(world=e['world'],split=w['split'],policy=e['policy'],map=w['map_name'],seed=w['seed'],shift=w['shift'],N=w['N'],error=e['error'],seconds=e['seconds'])
  if e['error'] is None:
   rs=matched.rows(e);fixed=matched.flow(w,rs);ds=[r for r in rs if r['event']=='actor_decision'];repl=matched.check_episode(e,rs)
   result.update(served=e['summary']['served'],queries=e['summary']['queries'],deadlock=e['summary']['deadlock'],fixed_first4_time_sum=str(fixed),fixed_first4_time_float=float(fixed),H_reached=e['summary']['last_clock']['lower']==w['horizon']*1000000,opportunities=len(ds),multi_opportunities=sum(len(r['candidates'])>1 for r in ds),replacements=len(repl),replacement_selected=repl[0]['selected'] if repl else None)
  results.append(result)
 runner.write(P/'RESULTS.json',results)
 with (P/'RESULTS.csv').open('x',newline='') as f:
  fields=sorted({k for r in results for k in r});cw=csv.DictWriter(f,fields);cw.writeheader();cw.writerows(results)
 test=[r for r in results if r['split']=='test' and r['error'] is None];totals={p:dict(episodes=sum(r['policy']==p for r in test),served=sum(r['served'] for r in test if r['policy']==p),queries=sum(r['queries'] for r in test if r['policy']==p),fixed_first4_time_sum=str(sum((Q(r['fixed_first4_time_sum']) for r in test if r['policy']==p),Q(0)))) for p in reg['policies']};em={(r['world'],r['policy']):r for r in test};pairs=[]
 for w in [w for w in worlds.values() if w['split']=='test']:
  n=w['name'];pairs.append(dict(world=n,map=w['map_name'],seed=w['seed'],shift=w['shift'],arms={p:dict(served=em[n,p]['served'],queries=em[n,p]['queries'],fixed=em[n,p]['fixed_first4_time_sum']) for p in reg['policies']},learned_minus_condition={p:em[n,p]['served']-em[n,'condition']['served'] for p in reg['policies'] if p.startswith('once_')}))
 labels=json.loads((P/'TRAIN_CAL_LABELS.json').read_text());signal={}
 for split in ['train','calibration']:
  ls=[r for r in labels if r['split']==split and r['action']!='WAIT'];signal[split]=dict(candidate_rows=len(ls),opportunities=len({(r['world'],r['opportunity']) for r in ls}),runs=len({r['world'] for r in ls}),sign=dict(Counter('positive' if Q(r['target'])>0 else 'negative' if Q(r['target'])<0 else 'zero' for r in ls)),whole_task_gain=dict(Counter(str(r['whole_service_gain']) for r in ls)),remaining_budgets=dict(Counter(str(r['remaining_capacity']) for r in ls)))
 runner.write(P/'SUMMARY.json',dict(total_episodes=len(es),failures=sum(e['error'] is not None for e in es),test_totals=totals,paired_worlds=pairs,label_signal=signal,all_reached_H=all(r.get('H_reached',False) for r in results if r['error'] is None),deadlocks=sum(r.get('deadlock',False) for r in results)))
 print(json.dumps(dict(totals=totals,signal=signal),indent=2),flush=True)
if __name__=='__main__':main()
