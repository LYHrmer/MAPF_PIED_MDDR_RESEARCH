"""Actually fit ridge residuals on train runs; select lambda/amplitude on cal only."""
from common import HERE,FEATURES,sha,events,predict,write
import json,math,statistics,numpy as np
def load(split):
 rows=[];pins={}
 for r in json.loads((HERE/'runs.json').read_text())['runs']:
  if r['split']!=split:continue
  p=HERE/'datasets'/r['id'];xs=events(p/'delivered_context.jsonl');ys=events(p/'offline_original_MOVE_targets.jsonl')
  assert [x['key'] for x in xs]==[y['key'] for y in ys]
  pins[r['id']]={n:sha(p/n) for n in ('delivered_context.jsonl','offline_original_MOVE_targets.jsonl')}
  for x,y in zip(xs,ys):
   if y['duration_ticks'] is not None:rows.append((x['features'],y['duration_ticks'],r['id']))
 return rows,pins
train,tp=load('train');cal,cp=load('cal');assert train and cal
X=np.array([r[0] for r in train]);Y=np.array([r[1]-r[0][0] for r in train]);mu=X.mean(axis=0);scale=X.std(axis=0);scale[scale<1e-8]=1
Z=np.column_stack([np.ones(len(X)),(X-mu)/scale]);candidates=[]
for lam in [.1,1.,10.]:
 reg=np.eye(Z.shape[1])*lam;reg[0,0]=0;coef=np.linalg.solve(Z.T@Z+reg,Z.T@Y)
 m={'model':'ridge_original_MOVE_duration_residual','feature_names':FEATURES,'mean':mu.tolist(),'scale':scale.tolist(),'intercept':float(coef[0]),'coefficients':coef[1:].tolist(),'lambda':lam,'trained':True}
 errs=[abs(predict(x,'learned',m)-y) for x,y,_ in cal];candidates.append((statistics.mean(errs),lam,m))
mae,lam,model=min(candidates,key=lambda x:(x[0],x[1]))
contrast=[]
for r in json.loads((HERE/'runs.json').read_text())['runs']:
 if r['split']=='cal':
  for d in events(HERE/'attempts'/r['id']/'decisions.jsonl'):
   v=[]
   for a in d['forecast']['axis_features']:
    v.append(statistics.mean([predict(row['features'],'learned',model) for row in a]) if a else 20)
   contrast.append(abs(v[0]-v[1])/statistics.mean(v))
delta=statistics.median(contrast);amp=.5 if delta<.1 else 1. if delta<.3 else 2.
model|={'training_rows':len(train),'calibration_rows':len(cal),'training_run_ids':sorted(tp),'calibration_run_ids':sorted(cp),'train_source_sha256':tp,'calibration_source_sha256':cp}
write(HERE/'trained_model.json',model)
metrics={policy:statistics.mean([abs(predict(x,policy,model)-y) for x,y,_ in cal]) for policy in ['analytic','history','learned']}
write(HERE/'calibration.json',{'candidate_lambdas':[{'lambda':l,'MAE_ticks':e} for e,l,_ in candidates],'selected_lambda':lam,'calibration_MAE_ticks':metrics,'median_relative_agent_duration_contrast':delta,'amplitude':amp,'amplitude_rule':'<0.1=>0.5,<0.3=>1,otherwise2','no_test_accessed':True})
write(HERE/'model_freeze.json',{'files':{n:sha(HERE/n) for n in ['trained_model.json','calibration.json','train.py','export_data.py','common.py']},'amplitude':amp,'test_runs_started':False,'train_runs':sorted(tp),'cal_runs':sorted(cp)})
print(json.dumps({'trained_rows':len(train),'cal_rows':len(cal),'lambda':lam,'amplitude':amp,'calibration_MAE_ticks':metrics,'model_sha256':sha(HERE/'trained_model.json')},indent=2))
