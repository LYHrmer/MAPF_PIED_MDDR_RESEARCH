#!/usr/bin/env python3
"""Explicit isolated compiler/commitment-adapter variant; original SADG MILP."""
import argparse
import importlib.util
import json
from fractions import Fraction
from pathlib import Path
import sys

sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r16_core',HERE/'run_preflight.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
sys.path.insert(0,str(HERE/'isolated_patch'))
pspec=importlib.util.spec_from_file_location('r16_compiler_patch',HERE/'isolated_patch/compiler.py')
pc=importlib.util.module_from_spec(pspec);pspec.loader.exec_module(pc)
c.compile_sadg=pc.compile_sadg
BASE=HERE.parent/'position_search_bridge_20261004_r14'
NAME='warehouse-10-20-10-2-1__t1_2__axis_slow'


def register():
    patch={n:c.sha(HERE/'isolated_patch'/n) for n in ['compiler.py','r16_guard_group.py']}
    old=json.loads((HERE/'inputs/official_test_staged.json').read_text())
    official=dict(old,name='official_test_patched',compiler_variant='isolated_k0_plus_all_heads',patch_hashes=patch)
    p=json.loads((BASE/'public'/f'{NAME}.json').read_text());g=p['solver_graph']
    ev=json.loads((BASE/'evidence'/f'{NAME}.json').read_text())
    public=json.loads((BASE/'views'/f'{NAME}__public.json').read_text())
    estimates={x['agent']:x for x in public['estimates']}
    active={f'agent{x["agent"]}':x['from_state'] for x in p['active_commitments']}
    progress={aid:float(Fraction(estimates[int(aid.replace('agent',''))]['public_alpha'])) for aid in active}
    sol={'schedule':{f'agent{a}':[dict(x=xy[0],y=xy[1],t=t) for xy,t in path] for a,path in enumerate(g['paths'])}}
    base=dict(solution=sol,dimensions={'dimensions':{'resolution':2.,'x_offset':0.,'y_offset':0.}},
        active_indices=active,horizon=5.0,data_class='R14_archived_checkpoint_native_move_adapter',production_cost=None,
        public_file_sha256=c.sha(BASE/'public'/f'{NAME}.json'),evidence_file_sha256=c.sha(BASE/'evidence'/f'{NAME}.json'),
        compiler_variant='isolated_k0_plus_all_heads',patch_hashes=patch,
        model_scope='MOVE-only nominal 1 second/action. Original STATION/TURN/profile not in predictor. Original executor guard unchanged.')
    a=dict(base,name='warehouse_public_patched',progress=progress)
    measured=dict(progress);measured[f'agent{ev["request"]["agent"]}']=float(Fraction(ev['body']['progress_lower']))
    b=dict(base,name='warehouse_measured_patched',progress=measured)
    audit=json.loads((HERE/'MAPPING_AUDIT_warehouse_patched.json').read_text())
    assert audit['common_adoption_eligible']
    cases=[official,a,b]
    for obj in cases:c.dump(HERE/'inputs'/f'{obj["name"]}.json',obj)
    c.dump(HERE/'PATCHED_REGISTRATION.json',dict(author_calls_previously_successful=7,
        new_unique_calls=3,cumulative_author_call_upper_bound=10,per_call_author_cap_seconds=60,
        source_optimizer_unchanged=True,compiler_patch_hashes=patch,
        mapping_audit_sha256=c.sha(HERE/'MAPPING_AUDIT_warehouse_patched.json'),
        inputs={x['name']:c.key(x) for x in cases}))


def guard(name):
    p=json.loads((BASE/'public'/f'{NAME}.json').read_text());g=p['solver_graph']
    before=json.loads((HERE/'cases'/name/'graph_before.json').read_text())
    after=json.loads((HERE/'cases'/name/'graph_after.json').read_text())
    ids=[(a,i) for a,path in enumerate(g['paths']) for i in range(len(path))]
    def state(uid):
        _,a,i=uid.split('_');return g['offsets'][int(a)]+int(i)+1
    def convert(snap):
        return [[state(d['active'][0]),state(d['active'][1]),1] for gr in snap['groups'] for d in gr['dependencies']]
    initial=convert(before);final=convert(after)
    candidate=dict(g,type2=sorted(e for e in final if ids[e[0]][1]>g['current'][ids[e[0]][0]]))
    sys.path.insert(0,str(HERE.parent/'gses_online_adoption_20261004_r13'))
    from executor import adoption_guard
    committed=[(x['agent'],x['from_state']) for x in p['active_commitments']]
    error=None
    try:adoption_guard(g,candidate,committed)
    except Exception as exc:error=repr(exc)
    satisfied=[e for e in initial if ids[e[0]][1]<=g['current'][ids[e[0]][0]]]
    satisfied_preserved=all(e in final for e in satisfied)
    result=dict(case=name,original_R13_adoption_guard_pass=error is None,error=error,
        satisfied_directions_preserved=satisfied_preserved,
        active_commitment_count=len(committed),remaining_type2_count=len(candidate['type2']),
        changed_edges=len(set(map(tuple,final))-set(map(tuple,initial))),
        candidate_sha256=c.key(candidate),physical_execution_adopted=False,
        scope='Original graph validator and commitment guard only; no old private snapshot mutated or replayed.')
    c.dump(HERE/'cases'/name/'candidate_for_R13_guard.json',candidate)
    c.dump(HERE/'cases'/name/'original_guard_audit.json',result)
    print(json.dumps(result))


if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('action',choices=['register','solve','guard']);ap.add_argument('--case');args=ap.parse_args()
    if args.action=='register':register()
    elif args.action=='solve':c.solve(args.case)
    else:guard(args.case)
