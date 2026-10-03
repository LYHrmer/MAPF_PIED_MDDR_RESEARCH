"""Reconcile independently derived raw outcomes without importing root code."""
from fractions import Fraction as Q
import json
import runner
P=runner.HERE
def main():
 root=json.loads((P/'ROOT_VALUE_SPACE.json').read_text());rows=json.loads((P/'RESULTS.json').read_text());pairs=json.loads((P/'PAIR_REACHABILITY.json').read_text());by={(r['world'],r['policy']):r for r in rows};pm={(r['world'],r['policy']):r for r in pairs}
 assert root['passed'] and len(root['all_runs'])==len(by)==94
 for r in root['all_runs']:
  a=by[r['world'],r['policy']];assert (r['tasks'],r['queries'])==(a['served'],a['queries'])
  assert Q(r['fifo_low'])==Q(a['first4_time_lower']) and Q(r['fifo_high'])==Q(a['first4_time_upper'])
  for x,y in [('vs_pi0','vs_condition'),('vs_whole_WAIT','vs_whole_WAIT')]:
   ra,rb=r[x],a[y];assert ra['tasks']==rb['task_gain'] and ra['robust_J_improvement']==rb['robust_J_improvement']
   for left,right in [('fifo_saving_low','time_gain_lower'),('fifo_saving_high','time_gain_upper'),('J_saving_low','J_gain_lower'),('J_saving_high','J_gain_upper')]:assert Q(ra[left])==Q(rb[right])
  if r['policy'].startswith('pair_'):assert r['second_reached']==pm[r['world'],r['policy']]['second_reached']
 assert root['robust_J_probe_gains_over_both']==sum(r['policy'].startswith(('cf_','pair_')) and r['vs_condition']['robust_J_improvement'] and r['vs_whole_WAIT']['robust_J_improvement'] for r in rows)==11
 assert root['retrospective_task_totals']==dict(pi0=188,whole_WAIT=188,best_finite_registered_per_family=189,per_family_reference_envelope=189,note=root['retrospective_task_totals']['note'])
 runner.write(P/'ROOT_RECONCILIATION.json',dict(passed=True,episodes=94,whole_FIFO_counts_and_first4_interval_bounds_identical=True,both_reference_deltas_and_robust_J_flags_identical=True,pair_reachability_identical=True,root_script_sha256=runner.sha(P/'root_value_space.py'),root_result_sha256=runner.sha(P/'ROOT_VALUE_SPACE.json'),robust_J_probe_gains_over_both=11,retrospective_task_totals=root['retrospective_task_totals']))
 print('root independent outcome reconciliation PASS',flush=True)
if __name__=='__main__':main()
