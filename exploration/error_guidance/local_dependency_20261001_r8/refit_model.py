from pathlib import Path
import hashlib,json,math
import numpy as np
from public_model import PublicHistory,FEATURES,nominal,predict
H=Path(__file__).resolve().parent;R=H.parent/'execution_residual_20261001_r7';M=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/R.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
splits={'train':[],'calibration':[]};pins={};counts={}
for spec in json.loads((R/'runs.json').read_text())['runs']:
 if spec['split']=='test':continue
 p=M/'runs'/spec['id']/'public_events.jsonl';pins[str(p)]=sha(p);hist=PublicHistory()
 for line in p.open():hist.accept(json.loads(line))
 rows=[dict(r,run=spec['id']) for r in hist.rows];splits[spec['split']].extend(rows);counts[spec['id']]={'completed':len(rows),'censored':sum(r['duration'] is None for r in hist.moves.values())}
(H/'refit_rows.json').write_text(json.dumps(splits,indent=2)+'\n')
x=np.array([r['features'] for r in splits['train']]);y=np.array([r['duration']-nominal(r['turns']) for r in splits['train']]);mean=x.mean(axis=0);scale=x.std(axis=0);scale[scale<1e-12]=1.;z=np.column_stack([np.ones(len(x)),(x-mean)/scale]);pen=np.eye(z.shape[1]);pen[0,0]=0;beta=np.linalg.solve(z.T@z+pen,z.T@y)
ridge={'features':FEATURES,'mean':mean.tolist(),'scale':scale.tolist(),'intercept':float(beta[0]),'coef':beta[1:].tolist(),'lambda':1.,'target':'normal final MOVE ACK minus proposal tick minus45+10actual quarter turns; public orientation explicitly converted'}
cal={}
for pol in ['history','learned']:
 er=[abs(predict(r['features'],r['turns'],pol,ridge)-r['duration']) for r in splits['calibration']];rank=min(len(er),math.ceil(.9*(len(er)+1)));cal[pol]={'rows':len(er),'q90_absolute_error':sorted(er)[rank-1],'rank':rank,'MAE':float(np.mean(er)),'RMSE':float(np.sqrt(np.mean(np.square(er))))}
out={'ridge':ridge,'calibration':cal,'rows_by_run':counts,'train_rows':len(x),'calibration_rows':len(splits['calibration']),'source_pins':pins,'protocol_sha256':sha(H/'PROTOCOL.md'),'training_script_sha256':sha(__file__),'public_model_sha256':sha(H/'public_model.py'),'public_model_parent_sha256':sha(H/'public_model_parent.py'),'test_seen':False,'source_data':'same R7 training/calibration runs; corrected orientation before R8test'}
assert not (H/'model_freeze.json').exists();(H/'model_freeze.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'train':len(x),'calibration':cal,'model_sha256':sha(H/'model_freeze.json')}))
