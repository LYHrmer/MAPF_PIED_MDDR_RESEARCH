from pathlib import Path
import hashlib,json,math
import numpy as np
from public_model import FEATURES,nominal,predict
HERE=Path(__file__).resolve().parent;OUT=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/HERE.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()

def fit():
 splits={'train':[],'calibration':[]};pins={};counts={}
 for spec in json.loads((HERE/'runs.json').read_text())['runs']:
  if spec['split']=='test':continue
  root=OUT/'runs'/spec['id'];receipt=json.loads((root/'receipt.json').read_text());assert receipt['error'] is None and receipt['true_horizon_tick']==4000
  p=root/'supervised_rows.json';data=json.loads(p.read_text());pins[str(p)]=sha(p)
  rows=[dict(r,run=spec['id']) for r in data['rows']];splits[spec['split']].extend(rows);counts[spec['id']]={'completed':len(rows),'censored':len(data['censored'])}
 x=np.array([r['features'] for r in splits['train']],dtype=float);y=np.array([r['duration']-nominal(r['turns']) for r in splits['train']])
 mean=x.mean(axis=0);scale=x.std(axis=0);scale[scale<1e-12]=1.
 z=np.column_stack([np.ones(len(x)),(x-mean)/scale]);pen=np.eye(z.shape[1]);pen[0,0]=0
 beta=np.linalg.solve(z.T@z+pen,z.T@y)
 ridge={'features':FEATURES,'mean':mean.tolist(),'scale':scale.tolist(),'intercept':float(beta[0]),'coef':beta[1:].tolist(),'lambda':1.,'target':'normal final MOVE ACK tick minus proposal tick minus (45+10*quarter_turns)'}
 calibration={}
 for policy in ('history','learned'):
  errors=[abs(predict(r['features'],r['turns'],policy,ridge)-r['duration']) for r in splits['calibration']]
  rank=min(len(errors),math.ceil(.9*(len(errors)+1)));q=sorted(errors)[rank-1]
  calibration[policy]={'rows':len(errors),'q90_absolute_error':q,'rank':rank,'MAE':float(np.mean(errors)),'RMSE':float(np.sqrt(np.mean(np.square(errors))))}
 result={'ridge':ridge,'calibration':calibration,'rows_by_run':counts,'train_rows':len(x),'calibration_rows':len(splits['calibration']),'source_pins':pins,'protocol_sha256':sha(HERE/'PROTOCOL.md'),'training_script_sha256':sha(__file__),'public_model_sha256':sha(HERE/'public_model.py'),'test_seen':False}
 target=HERE/'model_freeze.json';assert not target.exists();target.write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'train':len(x),'calibration':calibration,'model_sha256':sha(target)}))
if __name__=='__main__':fit()
