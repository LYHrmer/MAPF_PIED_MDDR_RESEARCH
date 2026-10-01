from pathlib import Path
from fractions import Fraction as F
import json,importlib.util
import runner
HERE=runner.HERE;OUT=HERE/'statistical_attempt_01'
spec=importlib.util.spec_from_file_location('exact_r6_solver',HERE.parent/'public_joint_20261001_r6/model_audit.py');old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
def first4(e):
 heads={};H=None
 for line in Path(e['input']).read_text().splitlines():
  z=line.split()
  if z[0]=='D':H=int(z[3])
  elif z[0] in ['R','F']:heads.setdefault(int(z[1]),[]).append(int(z[2]))
 selected={t for v in heads.values() for t in v[:4]};times={};served=0
 for line in Path(e['raw']).open():
  r=json.loads(line)
  if r['event']=='task_service':times[r['task']]=F(r['at']['lower']+r['at']['upper'],2*r['at']['denominator']);served+=1
 return served,sum((times.get(t,F(H)) for t in selected),F(0))
def main():
 labels=json.loads((OUT/'TRAIN_CAL_LABELS.json').read_text());model=json.loads((OUT/'MODELS_FROZEN_BEFORE_TEST.json').read_text());fits={}
 cache={}
 def values(world,policy):
  key=world+'__'+policy
  if key not in cache:cache[key]=first4(json.loads((OUT/(key+'.receipt.json')).read_text()))
  return cache[key]
 for r in labels:
  wn,wt=values(r['world'],'WAIT');pn,pt=values(r['world'],r['probe']);assert F(r['fixed_first4_time_gain'])==wt-pt;assert r['whole_service_gain']==pn-wn;assert F(r['target'])==pn-wn+(wt-pt)/(128*16*4)
 train=[r for r in labels if r['split']=='train'];assert all(r['split']!='test' for r in labels)
 for name,m in model['models'].items():
  X=[[F(1)]+[F(z) if name=='ridge_history' or j<10 or j>=18 else F(0) for j,z in enumerate(r['features'])] for r in train];y=[F(r['target']) for r in train];A=[[sum((x[i]*x[j] for x in X),F(0))+int(i==j and i>0) for j in range(21)] for i in range(21)];b=[sum((x[i]*v for x,v in zip(X,y)),F(0)) for i in range(21)];fit=old.solve(A,b);error=max(abs(a-F(b)) for a,b in zip(fit,m['coefficients']));assert error<=F(500001,10**15);fits[name]=dict(exact_rational_refit=True,max_rounding_error=str(error))
 assert len(model['row_bindings'])==len(train);assert not model['test_seen_before_freeze'] and not model['calibration_used_for_selection']
 runner.write(HERE/'MODEL_AUDIT.json',dict(passed=True,labels_independently_recomputed=len(labels),models=fits,source_sha256=runner.sha(Path(__file__))))
 print('exact model and label audit passed',len(labels),flush=True)
if __name__=='__main__':main()
