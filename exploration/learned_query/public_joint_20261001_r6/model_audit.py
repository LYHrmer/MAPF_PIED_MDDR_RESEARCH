"""Exact rational ridge refit and independent labels; no numpy estimator imported."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
HERE=Path(__file__).resolve().parent

def solve(A,b):
 n=len(b);a=[row[:]+[z] for row,z in zip(A,b)]
 for k in range(n):
  pivot=next(i for i in range(k,n) if a[i][k]);a[k],a[pivot]=a[pivot],a[k];v=a[k][k];a[k]=[x/v for x in a[k]]
  for i in range(n):
   if i==k:continue
   v=a[i][k]
   if v:a[i]=[x-v*y for x,y in zip(a[i],a[k])]
 return [r[-1] for r in a]
def flow(s):
 t=s['service_time_sum'];return F(t['lower']+t['upper'],2*t['denominator'])+384*(s['task_count']-s['served'])
def main():
 out=HERE/'native_attempt_01';labels=json.loads((out/'TRAIN_CAL_LABELS.json').read_text());model=json.loads((out/'MODELS_FROZEN_BEFORE_TEST.json').read_text());checks=0
 for r in labels:
  w=json.loads((out/(r['world_id']+'__WAIT.receipt.json')).read_text())['summary'];p=json.loads((out/(r['world_id']+'__'+r['chosen_policy']+'.receipt.json')).read_text())['summary'];gain=flow(w)-flow(p);extra=p['served']-w['served'];assert gain==F(r['restricted_flow_gain']) and extra==r['extra_tasks'] and F(r['target'])==extra+gain/(384*48);assert r['split']!='test' and r['END_only_known']>=2;checks+=1
 train=[r for r in labels if r['split']=='train'];fits={}
 for name,m in model['models'].items():
  X=[[F(1)]+[F(z) if name=='ridge_history' or j<10 or j>=18 else F(0) for j,z in enumerate(r['features'])] for r in train];y=[F(r['target']) for r in train];A=[[sum((x[i]*x[j] for x in X),F(0))+int(i==j and i>0) for j in range(21)] for i in range(21)];b=[sum((x[i]*v for x,v in zip(X,y)),F(0)) for i in range(21)];q=solve(A,b);coef=[F(z) for z in m['coefficients']];errors=[abs(a-b) for a,b in zip(q,coef)];assert max(errors)<=F(500001,10**15);assert len(train)==m['train_rows'] and m['lambda_value']==1 and not m['test_for_selection'] and not m['calibration_for_selection'];checks+=21;fits[name]=dict(exact_ridge_refit=True,max_rounded_coefficient_error=str(max(errors)),train_rows=len(train),same_row_bindings=True)
 p=HERE/'MODEL_AUDIT.json';assert not p.exists();p.write_text(json.dumps(dict(passed=True,checks=checks,offline_label_recomputation=True,exact_rational_normal_equation_refit=True,test_rows_used=0,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),models=fits),indent=2)+'\n');print(fits)
if __name__=='__main__':main()
