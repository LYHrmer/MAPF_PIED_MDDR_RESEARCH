"""Root review: independently reconstruct primitive labels and task totals from raw events.

Does not import candidate/audit/model modules. The existing physical geometry audit is
separate; this checks the scientific outcome, label, and current-FIFO-head contract.
"""
from pathlib import Path
import hashlib
import json

P=Path(__file__).resolve().parent
R=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence')/P.name/'runs'
specs=[s for s in json.loads((P/'runs.json').read_text())['runs'] if s['split']=='test']
summary=json.loads((P/'summary.json').read_text())
out={}; aggregate={p:{'tasks':0,'restricted_first10':0} for p in ['hm','history','learned']}
for spec in specs:
    folder=R/spec['id']; env=json.loads((P/'inputs'/spec['input_id']/'environment.json').read_text())
    rows=json.loads((folder/'supervised_rows.json').read_text())
    target={(r['agent'],r['node']):r for r in rows['rows']+rows['censored']}
    nodes={}; admit={}; end={}; next_node=[0]*spec['N']; services={}; owner={}; heads={}; ordinals=[0]*spec['N']; proposal=None
    station_count=0; lastseq=-1; horizon=False
    for line in (folder/'events.jsonl').open():
        e=json.loads(line); assert e['sequence']>lastseq;lastseq=e['sequence']
        if e['kind']=='view':
            for a,goals in enumerate(e['view']['mapf_instance']['goals']):
                assert len(goals)==1
                g=goals[0];tid=g['id']
                if a not in heads or heads[a]!=tid:
                    if a in heads: assert heads[a] in services
                    ordinal=ordinals[a]; assert g['location']==env['FIFO_goals'][a][ordinal]
                    assert tid not in owner;owner[tid]=(a,ordinal,g['location']);heads[a]=tid;ordinals[a]+=1
        elif e['kind']=='proposal': proposal=e
        elif e['kind']=='parsed':
            for a,items in enumerate(e['actions']):
                for primitive in items:
                    k=(a,next_node[a]);next_node[a]+=1;nodes[k]=primitive;t=target[k]
                    assert t['primitive']==primitive and t['proposal_tick']==proposal['tick']
                    assert t['history_cutoff_sequence']==proposal['sequence']
                    if primitive['type']=='S': assert primitive['task_id']==heads[a]
        elif e['kind']=='admit':
            a=int(e['robot'])
            for action in e['actions']:
                k=(a,action[1]);assert k in nodes and k not in admit;admit[k]=(e['tick'],e['sequence'])
        elif e['kind']=='end':
            k=(int(e['robot']),e['node']);a,node=k;t=target[k]
            assert e['accepted'] and k in admit and k not in end
            previous=end[(a,node-1)][0] if node else 0
            b=max(admit[k][0],previous);duration=e['tick']-b
            assert (t['admit_tick'],t['begin_tick'],t['duration'],t['end_tick'])==(admit[k][0],b,duration,e['tick'])
            assert t['history_cutoff_sequence']<admit[k][1]<e['sequence']
            assert e['tick']-t['proposal_tick']==(admit[k][0]-t['proposal_tick'])+(b-admit[k][0])+duration
            end[k]=(e['tick'],e['sequence'])
            if nodes[k]['type']=='S':
                tid=nodes[k]['task_id']; assert e['task'] and e['task_id']==tid and heads[a]==tid and tid not in services
                assert duration==20 and owner[tid][0]==a
                goal=owner[tid][2]; assert nodes[k]['goal']==[goal%spec['cols'],goal//spec['cols']]
                services[tid]=e['tick'];station_count+=1
        elif e['kind']=='horizon': horizon=e['tick']==4000
    assert horizon and len(nodes)==len(target)
    assert all((k not in end)==(r['duration'] is None) for k,r in target.items())
    by_identity={(owner[tid][0],owner[tid][1]):tick for tid,tick in services.items()}
    restricted=sum(by_identity.get((a,k),4000) for a in range(spec['N']) for k in range(10))
    recorded=json.loads((P/'per_run_audits'/(spec['id']+'.json')).read_text())
    assert recorded['normal_station_END']==station_count and recorded['fixed_first10_restricted_ticks']==restricted
    assert {(v['agent'],v['ordinal']):v['tick'] for v in recorded['services']}==by_identity
    aggregate[spec['policy']]['tasks']+=station_count;aggregate[spec['policy']]['restricted_first10']+=restricted
    out[spec['id']]={'tasks':station_count,'fixed_first10_ticks':restricted,'completed_primitive_labels':len(end),
                     'censored':len(nodes)-len(end),'raw_sha256':hashlib.sha256((folder/'events.jsonl').read_bytes()).hexdigest()}
for policy,totals in aggregate.items():
    for key,value in totals.items():assert value==summary['aggregate'][policy][key]
report={'passed':True,'run_count':len(out),'aggregate':aggregate,'runs':out,'candidate_imports':False,
        'scope':'raw accepted END, native parsed primitives, public admit, current-head FIFO, exact 20-tick station duration, proposal-time label cutoff; physical checks separately documented'}
(P/'ROOT_REPLAY.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='runs'},indent=2))
