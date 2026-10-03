from pathlib import Path
import json,copy
from public_model import PublicHistory
H=Path(__file__).resolve().parent;O=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/H.name
d=O/'runs/mechanical_mechanical_951900_unknown_pause_local_hm';events=[json.loads(s) for s in (d/'public_events.jsonl').open()]
res={}
def run(es):
    h=PublicHistory()
    for e in es:h.accept(e)
    return h
def reject(name,es):
    try:run(es)
    except (AssertionError,KeyError):res[name]='rejected';return
    raise AssertionError(name+' accepted')
bad=copy.deepcopy(events);next(e for e in bad if e['kind']=='proposal')['private_control_front']=1;reject('private_field_in_projection',bad)
bad=[e for e in events if not(e['kind']=='end' and e['robot']=='0' and e['node']==1)];reject('missing_own_previous_END',bad)
bad=copy.deepcopy(events);next(e for e in bad if e['kind']=='admit' and e['robot']=='0')['tick']=99999;reject('future_admission_timestamp',bad)
bad=copy.deepcopy(events);next(e for e in bad if e['kind']=='end')['accepted']=False;reject('rejected_ACK_as_duration',bad)
h=run(events);rows=[r for r in h.rows if r['begin_tick']>r['admit_tick']];assert rows
r=rows[0];assert r['duration']!=r['end_tick']-r['admit_tick'];res['queue_residence_mislabel_detected']={'node':[r['agent'],r['node']],'A':r['admit_tick'],'Eprev':r['own_predecessor_END_tick'],'E':r['end_tick'],'D':r['duration'],'wrong_queue_duration':r['end_tick']-r['admit_tick']}
(H/'label_negative_checks.json').write_text(json.dumps({'all_rejected':True,'cases':res},indent=2)+'\n');print(json.dumps(res))
