"""Same frozen R7 rows, masked-history ridge. No TEST reading or selection."""
from pathlib import Path
import hashlib,json
import numpy as np
from public_model import predict
H=Path(__file__).resolve().parent;R=H.parent/'primitive_duration_20261003_r9'
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
original=json.loads((R/'model_freeze.json').read_text());data=json.loads((R/'training_rows.json').read_text())
train=[r for r in data['train'] if r['group']!='S'];X=np.array([r['features'] for r in train]);X[:,7:]=0
y=np.array([r['duration']-original['d0'][r['group']] for r in train]);mu=X.mean(0);sd=X.std(0);sd[sd<1e-12]=1
Z=np.column_stack([np.ones(len(X)),(X-mu)/sd]);pen=np.eye(Z.shape[1]);pen[0,0]=0;beta=np.linalg.solve(Z.T@Z+pen,Z.T@y)
m=dict(original);m['geometry_ridge']={'features':original['ridge']['features'],'mean':mu.tolist(),'scale':sd.tolist(),'intercept':float(beta[0]),'coef':beta[1:].tolist(),'lambda':1.,'masked_raw_slots':list(range(7,14))}
m['R10_provenance']={'original_full_model_sha256':sha(R/'model_freeze.json'),'training_rows_path':str(R/'training_rows.json'),'training_rows_sha256':sha(R/'training_rows.json'),'full_ridge_unchanged':m['ridge']==original['ridge'],'train_motion_rows':len(train),'test_seen':False,'protocol_sha256':sha(H/'PROTOCOL.md'),'fit_sha256':sha(__file__),'public_model_sha256':sha(H/'public_model.py')}
assert m['ridge']==original['ridge'] and len(train)==14542 and all(v==0 for v in m['geometry_ridge']['coef'][7:])
out={}
for group in ['M_first','M_second','T','S','motion']:
 rows=[r for r in data['calibration'] if (r['group']!='S' if group=='motion' else r['group']==group)];out[group]={}
 for pol in ['history','geometry','learned']:
  er=np.array([predict(r['features'],r['group'],pol,m)-r['duration'] for r in rows]);out[group][pol]={'n':len(er),'MAE':float(np.abs(er).mean()),'RMSE':float(np.sqrt((er**2).mean())),'bias':float(er.mean())}
m['R10_calibration']=out
assert not (H/'model_freeze.json').exists();(H/'model_freeze.json').write_text(json.dumps(m,indent=2)+'\n')
print(json.dumps({'train_rows':len(train),'full_unchanged':True,'sha256':sha(H/'model_freeze.json')}))
