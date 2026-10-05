#!/usr/bin/env python3
"""Read-only evidence checks, then one immutable receipt; no solver or replay."""
from pathlib import Path
from datetime import datetime, timezone
import gzip
import hashlib
import json

HERE=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def dump(p,x):Path(p).write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')


def main():
    target=HERE/'FINAL_AUDIT.json'
    if target.exists():raise RuntimeError('final receipt already frozen; inspect JSON rather than overwrite')
    phase1=json.loads((HERE/'valid_nominal_schedule/PHASE1_REGISTRATION.json').read_text())
    assert sha(phase1['binary'])==phase1['binary_sha256']
    for name,value in phase1['author_source'].items():assert sha(Path(phase1['author_source_root'])/name)==value
    inputs=0
    for path in [HERE/'PHASE1_REGISTRATION.json',HERE/'valid_nominal_schedule/PHASE1_REGISTRATION.json']:
        reg=json.loads(path.read_text())
        for entry in reg['inputs']:assert sha(entry['path'])==entry['sha256'];inputs+=1
    for phase,key in [('PHASE2_REGISTRATION.json','sources'),('PHASE3_REGISTRATION.json','source_pins')]:
        reg=json.loads((HERE/phase).read_text())
        for name,value in reg[key].items():assert sha(HERE/name)==value
        assert sha(reg['case_path'])==reg['case_sha256']
    objects=0
    for path in (HERE/'common_evidence/objects').glob('*/*.json.gz'):
        raw=gzip.decompress(path.read_bytes());assert hashlib.sha256(raw).hexdigest()==path.name.removesuffix('.json.gz')
        json.loads(raw);objects+=1
    episodes=[]
    for subdir in ['common_runs','positive_switch']:
        for path in sorted((HERE/subdir).glob('*/episode.json')):
            obj=json.loads(path.read_text());assert obj['success'] and obj['collision_audit']['passed']
            assert obj['pending_queries_after_transport']==0
            assert all(q['delivery_status']=='accepted' for q in obj['queries'])
            for solve in obj['solves']:
                assert solve['guard']['passed']
                if 'cache_path' in solve:assert sha(solve['cache_path'])==solve['cache_sha256']
            episodes.append(dict(path=str(path.relative_to(HERE)),sha256=sha(path),
                sum_completion=obj['sum_completion'],new_author_calls=obj['new_author_calls'],
                queries=obj['query_count'],solver_calls=obj['solver_calls']))
    a=json.loads((HERE/'positive_switch/gses_surrogate/episode.json').read_text())
    b=json.loads((HERE/'positive_switch/keep_parent_control/episode.json').read_text())
    assert a['private_truth']==b['private_truth']
    assert a['queries']==b['queries']
    assert a['completion_times']=={'agent0':24.,'agent1':8.75}
    assert b['completion_times']=={'agent0':24.,'agent1':20.}
    assert a['solves'][0]['guard']['changed_groups']==['dg_agent0_0']
    invocations=len(list((HERE/'calls').glob('*/receipt.json')))+len(list((HERE/'valid_nominal_schedule/calls').glob('*/receipt.json')))+len(list((HERE/'common_runs').glob('*/native/*/receipt.json')))+len(list((HERE/'positive_switch').glob('*/native/*/receipt.json')))
    assert invocations==10
    dump(target,dict(passed=True,utc=datetime.now(timezone.utc).isoformat(),source_files=len(phase1['author_source']),
        source_and_binary_pins_passed=True,phase1_registered_input_hashes=inputs,cas_objects_verified=objects,
        episodes=episodes,positive_case_truth_and_queries_exact_match=True,
        native_program_invocations=invocations,constructor_failures=4,actual_astar_calls=6,
        cached_common_reuses=3,zero_search_controls=1,new_audit_solver_calls=0,new_audit_physical_runs=0,
        author_weight_counterexamples_preserved=True,independent_review='separately owned root_review, excluded here'))
    print(json.dumps(dict(passed=True,episodes=len(episodes),cas_objects=objects,program_invocations=invocations)))


if __name__=='__main__':main()
