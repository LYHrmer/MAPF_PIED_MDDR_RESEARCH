from pathlib import Path
import copy,importlib.util,json
from public_model import PublicHistory,forecast,projection_duration
H=Path(__file__).resolve().parent;R=H.parent/'geometry_history_20261003_r10';m=json.loads((H/'model_freeze.json').read_text())
layout=['....']*4;view={'mapf_instance':{'starts':[{'location':0,'orientation':0},{'location':15,'orientation':0}],'goals':[[{'location':3,'id':0}],[{'location':12,'id':1}]]}}
hist=PublicHistory(m['d0']);zero=forecast(hist,view,layout,'residual_history',m);assert all(v==0 for row in zero['cost_by_agent_destination'] for v in row)
fake=copy.deepcopy(m);fake['ridge']['intercept']=0.;fake['ridge']['coef']=[0.]*14
z=forecast(hist,view,layout,'residual_learned',fake);assert all(v==0 for row in z['cost_by_agent_destination'] for v in row)
for pol in ['residual_history','residual_learned']:
 for values in [[17.,17.,9.],[25.,24.,17.],[1.,1.,1.]]:
  parts=[{'group':g,'mean_ticks':v} for g,v in zip(['M_first','M_second','T'],values)];a=projection_duration(parts,pol,m);b=projection_duration(parts+[{'group':'S','mean_ticks':20.}],pol,m);assert a==b and a>=0
hist.rows=[{'agent':0,'group':'M_first','direction':0,'duration':25.},{'agent':1,'group':'T','direction':2,'duration':19.}]
sp=importlib.util.spec_from_file_location('original',R/'public_model.py');old=importlib.util.module_from_spec(sp);sp.loader.exec_module(old)
assert forecast(hist,view,layout,'learned',m)['cost_by_agent_destination']==old.forecast(hist,view,layout,'learned',m)['cost_by_agent_destination']
newseeds={s['seed'] for s in json.loads((H/'runs.json').read_text())['runs']};oldseeds=set()
for name in ['execution_residual_20261001_r7','primitive_duration_20261003_r9','geometry_history_20261003_r10']:
 oldseeds.update(s['seed'] for s in json.loads((H.parent/name/'runs.json').read_text())['runs'])
assert not newseeds&oldseeds
(H/'residual_mechanics.json').write_text(json.dumps({'passed':True,'station20_exact_cancellation':True,'zero_excess_zero_overlay':True,'zero_history_statistical_overlay_zero':True,'old_full_forecast_identical':True,'all_residuals_nonnegative':True,'new_seeds_disjoint_R7_R9_R10':True,'new_seeds':sorted(newseeds)},indent=2)+'\n');print('residual mechanics passed')
