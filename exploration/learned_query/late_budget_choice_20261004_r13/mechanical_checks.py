"""Synthetic arithmetic-only checks; no scientific family or native simulator."""
from fractions import Fraction as Q
import learn,runner
P=runner.HERE
def main():
 zero=learn.train([]);assert len(zero)==4 and all(len(m['coefficients'])==11 and set(m['coefficients'])=={'0'} for m in zero.values())
 assert learn.select(learn.scores(None,'full',zero),Q(0))=='C'
 rows=[dict(split='train',option='LD',features=[str(Q((i+1)*(j+1),100)) for j in range(10)],weight='1/2',task_target='0',time_target=str(Q(1 if i%2 else -1,100)),world='synthetic_'+str(i),family_key='synthetic_'+str(i//2),budget=8 if i%2==0 else 16) for i in range(6)]
 models=learn.train(rows);assert len(models)==4 and all(len(m['coefficients'])==11 and m['train_rows']==6 for m in models.values())
 for head in ['tasks','time']:
  m=models['no_history_prob_LD_'+head];assert all(Q(m['coefficients'][j+1])==0 for j in [0,9])
 x=rows[0]['features'];y=list(x);y[0]='999';y[9]='-999';assert learn.scores(x,'no_history_prob',models)==learn.scores(y,'no_history_prob',models)
 assert learn.select([Q(0),Q(0)],Q(0))=='C' and learn.select([Q(0),Q(1)],None)=='C' and learn.select([Q(0),Q(1)],Q(0))=='LD'
 runner.write(P/'MECHANICAL_CHECKS.json',dict(passed=True,native_runs=0,scientific_outcomes_used=False,checks=['zero-gate four-head fallback','ten-feature eleven-coefficient fit','history-probability mask dimensions and invariance','strict LD threshold C tie and infinity fallback'],learn_sha256=runner.sha(P/'learn.py'),script_sha256=runner.sha(P/'mechanical_checks.py')))
 print('arithmetic-only mechanical checks PASS',flush=True)
if __name__=='__main__':main()
