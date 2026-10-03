"""Raw node/ACK reconstruction and augmented least squares; no candidate import."""
from pathlib import Path
import hashlib,json,math,statistics
import numpy as np
H=Path(__file__).resolve().parent
m=json.loads((H/'model_freeze.json').read_text());O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
rows_by_run={}
for spec in json.loads((H/'runs.json').read_text())['runs']:
    run=spec['id'];data=json.loads((O/'runs'/run/'supervised_rows.json').read_text())
    rows_by_run[run]={(r['agent'],r['node']):r for r in data['rows']+data['censored']}
counts={};feature_error=0.;labels=0;prefix_wait=0;station=[]
for run,target in rows_by_run.items():
    raw=O/'runs'/run/'events.jsonl'
    assert hashlib.sha256(raw.read_bytes()).hexdigest()==json.loads((raw.parent/'receipt.json').read_text())['files']['events.jsonl']
    nodes={};admit={};end={};history=[];expected_features={};proposal=None
    for line in raw.open():
        e=json.loads(line)
        if e['kind']=='proposal':proposal=e
        elif e['kind']=='parsed':
            for a,items in enumerate(e['actions']):
                offset=sum(k[0]==a for k in nodes)
                for i,p in enumerate(items):
                    key=(a,offset+i);nodes[key]=p;r=target[key]
                    assert r['proposal_id']==proposal['proposal']['proposal_id'] and r['proposal_tick']==proposal['tick'] and r['history_cutoff_sequence']==proposal['sequence']
                    group=p['type']
                    if group=='M':group='M_first' if all(v%1==0 for v in p['start']) else 'M_second'
                    d=(int(p['orientation'])+3)%4;assert (r['group'],r['direction'],r['logical_step'])==(group,d,int(p['time']))
                    if group=='S':x=[]
                    else:
                        base=m['d0'][group];hs=[q for q in history if q[0]==a and q[1]==group][-16:];ds=[q for q in hs if q[2]==d][-8:];pool=[q[3] for q in history if q[1]==group and q[2]==d][-64:]
                        vals=[q[3] for q in hs];pooled=sum(pool)/len(pool) if pool else base;pred=(sum(q[3] for q in ds)+2*pooled)/(len(ds)+2)
                        x=[*[float(group==g) for g in ['M_first','M_second','T']],*[float(d==v) for v in range(4)],len(hs)/16,len(ds)/8,len(pool)/64,(pred-base)/20,((sum(vals)/len(vals) if vals else base)-base)/20,((vals[-1] if vals else base)-base)/20,(statistics.pstdev(vals) if len(vals)>1 else 0)/20]
                    assert len(x)==len(r['features']);feature_error=max(feature_error,max((abs(u-v) for u,v in zip(x,r['features'])),default=0.))
                    expected_features[key]=x
        elif e['kind']=='admit':
            for act in e['actions']:
                key=(int(e['robot']),act[1]);assert key in nodes and key not in admit;admit[key]=(e['tick'],e['sequence'])
        elif e['kind']=='end':
            key=(int(e['robot']),e['node']);a,i=key;r=target[key];assert e['accepted'] and key in admit and key not in end
            ep=end[(a,i-1)][0] if i else 0;assert not i or end[(a,i-1)][1]<e['sequence'];b=max(ep,admit[key][0]);duration=e['tick']-b
            assert (r['admit_tick'],r['admit_sequence'],r['own_predecessor_END_tick'],r['begin_tick'],r['duration'],r['end_tick'],r['end_sequence'])==(admit[key][0],admit[key][1],ep,b,duration,e['tick'],e['sequence'])
            assert e['tick']-r['proposal_tick']==admit[key][0]-r['proposal_tick']+b-admit[key][0]+duration
            end[key]=(e['tick'],e['sequence']);history.append((a,r['group'],r['direction'],duration));labels+=1;prefix_wait+=b>admit[key][0]
            if r['group']=='S':station.append(duration)
    assert len(nodes)==len(target)
    assert all((key not in end)==(r['duration'] is None) for key,r in target.items())
    counts[run]={'nodes':len(nodes),'completed':len(end),'censored':len(nodes)-len(end)}
assert feature_error<1e-10
out={'passed':True,'labels':labels,'public_feature_max_difference':feature_error,'positive_own_prefix_wait_nodes':prefix_wait,'station_D_range':[min(station),max(station)],'runs':counts,'imports_candidate_builder':False,'model_sha256':hashlib.sha256((H/'model_freeze.json').read_bytes()).hexdigest()}
(H/'INDEPENDENT_LIVE_LABELS.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='runs'},indent=2))
