"""Meaningful mechanic intervention: history removal must affect only geometry arm."""
from pathlib import Path
import json
from public_model import predict
H=Path(__file__).resolve().parent;m=json.loads((H/'model_freeze.json').read_text())
checks=[];sensitive=[]
for gi,g in enumerate(['M_first','M_second','T']):
 for d in range(4):
  x=[float(i==gi) for i in range(3)]+[float(i==d) for i in range(4)]+[0.]*7
  y=x[:7]+[.75,.5,.75,1.2,.5,.8,.3]
  a=predict(x,g,'geometry',m);b=predict(y,g,'geometry',m);assert a==b
  checks.append({'group':g,'direction':d,'geometry_history_invariant':True,'ticks':a})
  sensitive.append(abs(predict(x,g,'learned',m)-predict(y,g,'learned',m)))
assert max(sensitive)>1e-6 and all(predict([], 'S',p,m)==20 for p in ['history','geometry','learned'])
(H/'negative_checks.json').write_text(json.dumps({'passed':True,'geometry_cases':checks,'full_history_max_change':max(sensitive),'station20':True},indent=2)+'\n')
print('mask intervention checks passed')
