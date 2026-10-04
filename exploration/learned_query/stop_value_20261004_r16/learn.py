"""Prespecified exact-rational depth-one exploratory selector; no tuning."""
from fractions import Fraction as Q
import time
def preference(row):
 d=row['delta_tasks'];lo=Q(row['T_gain_lower']);hi=Q(row['T_gain_upper'])
 return 'STOP' if d>0 or (d==0 and lo>=1) else 'C' if d<0 or (d==0 and hi<=-1) else 'neutral'
def fit(rows):
 prefs=[preference(r) for r in rows]
 gated=[r for r in rows if r['gate'] is not None]
 activated='STOP' in prefs and 'C' in prefs and len(gated)>=8
 out=dict(frozen_unix_ns=time.time_ns(),activated=activated,preferences={p:prefs.count(p) for p in ['STOP','C','neutral']},training_worlds=[r['world'] for r in rows],schema='late_target10_v1',rule='task prediction >0, or =0 and time gain >=1; otherwise C',max_depth=1,min_leaf_rows=4)
 if not activated:return out
 data=[([Q(x) for x in r['gate']['features']],Q(r['delta_tasks']),(Q(r['T_gain_lower'])+Q(r['T_gain_upper']))/2) for r in gated]
 def leaf(indices):
  tasks=sum((data[i][1] for i in indices),Q(0))/len(indices);timing=sum((data[i][2] for i in indices),Q(0))/len(indices)
  mean=tasks+timing/16385
  loss=sum(((data[i][1]+data[i][2]/16385-mean)**2/2 for i in indices),Q(0))
  return dict(tasks=str(tasks),time_gain=str(timing),n=len(indices),weight=str(Q(len(indices),2))),loss
 indices=list(range(len(data)));root,loss=leaf(indices);tree=dict(leaf=root);best=loss
 for feature in range(10):
  xs=sorted({x[feature] for x,_,_ in data})
  for a,b in zip(xs,xs[1:]):
   threshold=(a+b)/2;left=[i for i in indices if data[i][0][feature]<=threshold];right=[i for i in indices if data[i][0][feature]>threshold]
   if min(len(left),len(right))<4:continue
   l,ll=leaf(left);r,rr=leaf(right)
   if ll+rr<best:best=ll+rr;tree=dict(feature=feature,threshold=str(threshold),left=l,right=r)
 out.update(tree=tree,root_loss=str(loss),loss=str(best),training_gated_rows=len(data))
 return out
def choose(model,gate):
 if gate is None or not model['activated']:return 'C'
 tree=model['tree']
 leaf=tree['leaf'] if 'leaf' in tree else tree['left' if Q(gate['features'][tree['feature']])<=Q(tree['threshold']) else 'right']
 task=Q(leaf['tasks']);timing=Q(leaf['time_gain'])
 return 'STOP' if task>0 or (task==0 and timing>=1) else 'C'
