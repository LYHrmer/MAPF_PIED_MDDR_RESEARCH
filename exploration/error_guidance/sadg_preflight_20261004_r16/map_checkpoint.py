#!/usr/bin/env python3
"""Read-only R14 -> native author compiler mapping audit; no solver invocation."""
import importlib.util
import contextlib
import io
import json
from fractions import Fraction
from pathlib import Path
import time
import sys

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('r16_core',HERE/'run_preflight.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
BASE=HERE.parent/'position_search_bridge_20261004_r14'
NAME='random-32-32-10__t1_2__axis_slow'


def main():
    global NAME
    if '--warehouse' in sys.argv:
        NAME='warehouse-10-20-10-2-1__t1_2__axis_slow'
    patched='--patched' in sys.argv
    suffix=('_warehouse' if '--warehouse' in sys.argv else '')+('_patched' if patched else '')
    if patched:
        sys.path.insert(0,str(HERE/'isolated_patch'))
        pspec=importlib.util.spec_from_file_location('r16_compiler_patch',HERE/'isolated_patch/compiler.py')
        pm=importlib.util.module_from_spec(pspec);pspec.loader.exec_module(pm)
        c.compile_sadg=pm.compile_sadg
    public_path=BASE/'public'/f'{NAME}.json'
    p=json.loads(public_path.read_text());old=p['solver_graph'];paths=old['paths'];offsets=old['offsets']
    evidence_path=BASE/'evidence'/f'{NAME}.json';e=json.loads(evidence_path.read_text())
    view_path=BASE/'views'/f'{NAME}__public.json';view=json.loads(view_path.read_text())
    estimates={x['agent']:x for x in view['estimates']}
    # Input is only published path tuples and state, not checkpoint private heap.
    sol={'schedule':{f'agent{a}':[dict(x=xy[0],y=xy[1],t=t) for xy,t in path] for a,path in enumerate(paths)}}
    dim={'dimensions':{'resolution':2.,'x_offset':0.,'y_offset':0.}}
    t=time.perf_counter();g=c.compile_sadg(c.Plan(sol,dim),c.LOG);elapsed=time.perf_counter()-t
    commits={x['agent']:x for x in p['active_commitments']};action_mapping=[];issues=[]
    for a,path in enumerate(paths):
        vs=g.vertices_by_agent[f'agent{a}'];current=p['arrived_states'][a]
        if len(vs)!=len(path)-1:issues.append(dict(kind='action_count',agent=a))
        for i,v in enumerate(vs):
            s=c.Status.COMPLETED if i<current else c.Status.IN_PROGRESS if a in commits and i==current else c.Status.STAGED
            v.set_status(s)
            if a in commits and i==current:
                progress=float(Fraction(estimates[a]['public_alpha']))
                v.get_progress=c.types.MethodType(lambda self,value=progress:value,v)
                assert commits[a]['from_state']==i and commits[a]['to_state']==i+1
            action_mapping.append(dict(uid=v.get_shorthand(),agent=a,from_state=i,to_state=i+1,status=s.name))
    with contextlib.redirect_stdout(io.StringIO()):snap=c.snapshot(g,5.)
    def node(uid):
        _,a,i=uid.split('_');return offsets[int(a)]+int(i)+1
    converted=[];bad_reverses=[];completed_switchable=[]
    for group in snap['groups']:
        for d in group['dependencies']:
            u,v=map(node,d['active']);converted.append([u,v,1])
            if d['reverse']:
                ru,rv=map(node,d['reverse']);fu,fv=map(node,d['forward'])
                if [ru,rv]!=[fv+1,fu-1]:bad_reverses.append(dict(group=group['uid'],forward=[fu,fv],reverse=[ru,rv],expected=[fv+1,fu-1],group_switchable=group['switchable'],within_horizon=group['within_horizon']))
            tail=next(v for v in snap['vertices'] if v['uid']==d['active'][0])
            if tail['status']=='COMPLETED' and group['switchable'] and group['within_horizon']:
                completed_switchable.append(dict(group=group['uid'],active=d['active'],reverse=d['reverse']))
    ids=[(a,i) for a,path in enumerate(paths) for i in range(len(path))]
    remaining_converted=[e for e in converted if ids[e[0]][1]>p['arrived_states'][ids[e[0]][0]]]
    canonical=lambda e:min(tuple(e[:2]),(e[1]+1,e[0]-1))
    old_families=sorted(canonical(e) for e in old['type2']);new_families=sorted(canonical(e) for e in remaining_converted)
    from collections import Counter
    missing=list((Counter(old_families)-Counter(new_families)).elements())
    extra=list((Counter(new_families)-Counter(old_families)).elements())
    committed_diff=[]
    for a,x in commits.items():
        target=offsets[a]+x['to_state']
        oldin=sorted(e[:2] for e in old['type2'] if e[1]==target)
        newin=sorted(e[:2] for e in remaining_converted if e[1]==target)
        if oldin!=newin:committed_diff.append(dict(agent=a,target=target,old=oldin,new=newin))
    binding=dict(public_file_sha256=c.sha(public_path),public_base_sha256=c.key(p),request_public_sha256=e['request']['public_base_sha256'],
        agent=e['request']['agent'],from_state=e['request']['from_state'],to_state=e['request']['to_state'],
        captured_at=e['body']['captured_at'],delivered_at=e['body']['delivered_at'],
        public_progress=estimates[e['request']['agent']]['public_alpha'],
        measured_progress=e['body']['progress_lower'],
        progress_identifies_same_action=e['request']['agent'] in commits and commits[e['request']['agent']]['from_state']==e['request']['from_state'])
    assert binding['public_base_sha256']==binding['request_public_sha256']
    eligible=not(missing or extra or committed_diff or bad_reverses or completed_switchable or issues)
    c.dump(HERE/'mapping'/f'native_graph{suffix}.json',snap)
    c.dump(HERE/'mapping'/f'action_mapping{suffix}.json',action_mapping)
    result=dict(context=NAME,source_files={str(x.relative_to(BASE)):c.sha(x) for x in [public_path,evidence_path,view_path]},
        author_compile_seconds=elapsed,agents=len(paths),visits=sum(map(len,paths)),author_actions=len(action_mapping),
        original_type2_count=len(old['type2']),compiled_type2_count=len(converted),compiled_remaining_type2_count=len(remaining_converted),binding=binding,
        active_commitments=len(commits),action_count_errors=issues,missing_relation_families=missing,
        extra_relation_families=extra,committed_incoming_changes=committed_diff,
        invalid_reverse_pairs=bad_reverses,completed_tail_groups_still_switchable=completed_switchable,common_adoption_eligible=eligible,
        original_guard_bypassed=False,actual_optimizer_calls=0,physical_suffix_runs=0,
        remaining_time_caveat='Native nominal1 residual differs from R14 historical-rate residual; STATION/TURN excluded.',
        outcome='PASS_MAPPING_ONLY' if eligible else 'BLOCK_COMMON_ADOPTION_KEEP_NATIVE_CORE_VALIDATION')
    result['compiler_version']='isolated_k0_plus_all_head_commitment_guard' if patched else 'unmodified_author'
    result['compiler_sha256']=c.sha(HERE/'isolated_patch/compiler.py') if patched else c.sha(c.SOURCE/'sadg_controller/sadg_controller/sadg/compiler.py')
    c.dump(HERE/f'MAPPING_AUDIT{suffix}.json',result)
    summary={k:v for k,v in result.items() if k not in ['source_files','missing_relation_families','extra_relation_families','committed_incoming_changes','invalid_reverse_pairs','completed_tail_groups_still_switchable']}
    summary.update(missing=len(missing),extra=len(extra),committed_changed=len(committed_diff),bad_reverses=len(bad_reverses),completed_switchable=len(completed_switchable))
    print(json.dumps(summary))


if __name__=='__main__':main()
