from pathlib import Path
import json,hashlib,statistics
import numpy as np
from public_model import PublicHistory,FEATURES,predict,GROUPS
H=Path(__file__).resolve().parent;R=H.parent/'execution_residual_20261001_r7';M=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/R.name
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
specs=[s for s in json.loads((R/'runs.json').read_text())['runs'] if s['split'] in ('train','calibration')]
histories={};pins={};raw_counts={}
for s in specs:
    d=M/'runs'/s['id'];p=d/'public_events.jsonl';hist=PublicHistory()
    for line in p.open():hist.accept(json.loads(line))
    pins[str(p)]=sha(p);raw=d/'events.jsonl';pins[str(raw)]=sha(raw);parsed=0;offset={};ends=0
    for line in raw.open():
        e=json.loads(line)
        if e['kind']=='parsed':
            for a,nodes in enumerate(e['actions']):
                for node in nodes:
                    i=offset.get(a,0);offset[a]=i+1;r=hist.moves[(a,i)]
                    # R7 parser trace lacks time (single logical step); geometry must match.
                    assert {k:v for k,v in r['primitive'].items() if k!='time'}=={k:v for k,v in node.items() if k!='time'}
                    parsed+=1
        elif e['kind']=='end':
            r=hist.moves[(int(e['robot']),e['node'])];assert r['end_tick']==e['tick'] and r['end_sequence']==e['sequence'];ends+=1
    assert parsed==len(hist.moves) and ends==len(hist.rows)
    histories[s['id']]=hist;raw_counts[s['id']]={'parsed':parsed,'accepted_END':ends,'censored':parsed-ends}
d0={g:float(statistics.median(r['duration'] for s in specs if s['split']=='train' for r in histories[s['id']].rows if r['group']==g)) for g in GROUPS};d0['S']=20.
splits={'train':[],'calibration':[]};censored=[]
for s in specs:
    hist=PublicHistory(d0)
    for e in histories[s['id']].projected:hist.accept(e)
    splits[s['split']].extend(dict(r,run=s['id']) for r in hist.rows)
    censored.extend(dict(r,run=s['id'],split=s['split']) for r in hist.moves.values() if r['duration'] is None)
train=[r for r in splits['train'] if r['group']!='S'];x=np.array([r['features'] for r in train]);y=np.array([r['duration']-d0[r['group']] for r in train]);mean=x.mean(0);scale=x.std(0);scale[scale<1e-12]=1
z=np.column_stack([np.ones(len(x)),(x-mean)/scale]);pen=np.eye(z.shape[1]);pen[0,0]=0;beta=np.linalg.solve(z.T@z+pen,z.T@y)
model={'d0':d0,'ridge':{'features':FEATURES,'mean':mean.tolist(),'scale':scale.tolist(),'intercept':float(beta[0]),'coef':beta[1:].tolist(),'lambda':1.},'shared_margin_ticks':0.,'test_seen':False,'target':'primitive E-max(A,own previous accepted END); ticks, not motor time','source_pins':pins,'raw_lineage_checks':raw_counts,'train_motion_rows':len(train),'train_total_rows':len(splits['train']),'calibration_total_rows':len(splits['calibration']),'censored_rows':len(censored),'protocol_sha256':sha(H/'PROTOCOL.md'),'script_sha256':sha(__file__),'public_model_sha256':sha(H/'public_model.py')}
cal={}
for group in [*GROUPS,'S','motion']:
    rows=[r for r in splits['calibration'] if (r['group']!='S' if group=='motion' else r['group']==group)];cal[group]={}
    for pol in ['history','learned']:
        errors=[predict(r['features'],r['group'],pol,model)-r['duration'] for r in rows]
        cal[group][pol]={'n':len(rows),'MAE':float(np.mean(np.abs(errors))),'RMSE':float(np.sqrt(np.mean(np.square(errors)))),'bias':float(np.mean(errors))}
model['calibration']=cal
assert not (H/'model_freeze.json').exists()
(H/'model_freeze.json').write_text(json.dumps(model,indent=2)+'\n');(H/'training_rows.json').write_text(json.dumps(dict(splits,censored=censored),separators=(',',':'))+'\n')
print(json.dumps({'d0':d0,'train_motion':len(train),'calibration':cal,'censored':len(censored),'model_sha256':sha(H/'model_freeze.json')},indent=2))
