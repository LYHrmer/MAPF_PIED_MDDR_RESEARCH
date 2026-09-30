"""Root source/receipt/complete-grid and task-flow replay from raw events."""
import csv
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE/'public_joint_20260930_r3'
MAIN=Path('/home/lyh/MAPF_PIED_MDDR_RESEARCH')
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def bounds(x):return Fraction(x['lower'],x['denominator']),Fraction(x['upper'],x['denominator'])

def main():
    frozen=read(ROOT/'FROZEN_MANIFEST_20260930_r3.json')['frozen_files']
    for name,identity in frozen.items():
        p=ROOT/name;assert p.stat().st_size==identity['bytes'] and sha(p)==identity['sha256']
    registration=read(ROOT/'attempt_01/registration.json')
    for name,digest in registration['frozen'].items():assert sha(ROOT/name)==digest
    for name,digest in registration['production_headers'].items():assert sha(MAIN/name)==digest
    for name,digest in read(ROOT/'protected_before_20260930_r3.json').items():assert sha(HERE/name)==digest
    receipt=read(ROOT/'attempt_01/receipt.json');assert receipt['compile_returncode']==0
    rows=list(csv.DictReader((ROOT/'JOINT_ALL_RESULTS_20260930_r3.csv').open()))
    table={(r['condition'],r['policy'],int(r['capacity'])):r for r in rows}
    assert len(table)==len(rows)==len(receipt['episodes'])==63
    seen=set();counts={'MOVE':0,'END':0,'queries':0,'actor_decisions':0,'world_frames':0}
    outcomes={}
    for rec in receipt['episodes']:
        key=(rec['condition'],rec['policy'],rec['capacity']);assert key not in seen;seen.add(key)
        p=ROOT/'attempt_01'/Path(rec['raw']).name
        assert sha(p)==rec['raw_sha256'] and rec['returncode']==0 and rec['status']=='completed'
        events=[json.loads(s) for s in p.read_text().splitlines()]
        summary=events[-1];assert summary==rec['summary'] and summary['event']=='joint_summary'
        services=[e for e in events if e['event']=='task_service']
        queries=[e for e in events if e['event']=='certified_POSITION_committed']
        decisions=[e for e in events if e['event']=='actor_decision']
        assert len(services)==summary['served']==int(table[key]['served'])
        assert len({e['task'] for e in services})==len(services)
        assert all(e['original_endpoint_at_rest'] and e['physical_footprint_inside_service_square'] for e in services)
        assert len(queries)==summary['queries']==int(table[key]['queries'])<=rec['capacity']
        assert all(e['endpoint_retained'] for e in queries)
        assert all(not e['private_progress_input'] and not e['regime_input'] for e in decisions)
        first=next(e for e in decisions if e['remaining_capacity']>0) if rec['capacity'] else decisions[0]
        assert len(first['candidates'])==2
        low=sum((bounds(e['at'])[0] for e in services),Fraction(40*(4-len(services))))
        high=sum((bounds(e['at'])[1] for e in services),Fraction(40*(4-len(services))))
        assert low<=Fraction(table[key]['restricted_flow_sum'])<=high
        counts['MOVE']+=sum(e['event']=='original_RUN' for e in events)
        counts['END']+=sum(e['event']=='public_END_delivered' for e in events)
        counts['queries']+=len(queries);counts['actor_decisions']+=len(decisions)
        counts['world_frames']+=sum(e['event']=='world_frame_offline_only' for e in events)
        outcomes[key]=(summary['served'],tuple((e['task'],e['at']['lower'],e['at']['upper']) for e in services),first['selected'])
    assert counts=={'MOVE':973,'END':973,'queries':77,'actor_decisions':706,'world_frames':2803}
    condition='first7_1_first49_1'
    assert outcomes[condition,'WAIT',0][0]==3
    assert outcomes[condition,'RR',1][0]==4 and outcomes[condition,'RR',1][2]=='m-7-0'
    assert outcomes[condition,'task_rank',1][0]==3 and outcomes[condition,'task_rank',1][2]=='m-49-0'
    for condition in {r['condition'] for r in rows}:
        for budget in [1,2]:
            assert outcomes[condition,'task_rank',budget][:2]==outcomes[condition,'global_task',budget][:2]
    out={'passed':True,'frozen_files_verified':len(frozen),'complete_joint_episodes':63,'counts':counts,
         'current_probability_model_has_independent_task_gain':False,'query_choice_changes_completion':True,
         'full_100_robot_benchmark':False,'production_COST_complete':False,'verifier_sha256':sha(Path(__file__))}
    (HERE/'public_joint_root_review_20260930_r3.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps(out))

if __name__=='__main__':main()
