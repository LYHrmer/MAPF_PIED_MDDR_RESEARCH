#!/usr/bin/env python3
"""Classify retained failed model evidence, without solving or changing results."""
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

from audit_solver_payloads import cas, load, sha

HERE = Path(__file__).resolve().parent


def row_kind(row):
    name=row["name"]
    if name.startswith("sw_nan_"):return "fixed_type2"
    if name.startswith("sw_fwd_"):return "switchable_forward_bigM"
    if name.startswith("sw_rev_"):return "switchable_reverse_bigM"
    if name.startswith("boundary_"):return "current_boundary"
    match=re.fullmatch(r"(v_\d+_\d+)_s_to_(v_\d+_\d+)_g",name)
    if match and match[1]==match[2]:return "vertex_duration"
    if re.fullmatch(r"v_\d+_\d+_g_to_v_\d+_\d+_s",name):return "type1_sequence"
    return "other"


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--audit",type=Path,default=HERE/"solver_failure_review/FAILURE_PAYLOAD_AUDIT.json")
    p.add_argument("--output",type=Path,default=HERE/"solver_failure_review/FAILURE_STRATA.json")
    args=p.parse_args();audit=load(args.audit)
    groups=defaultdict(list)
    for r in audit["records"]:groups[r["semantic_key"]].append(r)
    unique=[];row_counts=Counter();levels=Counter();byarm=Counter();byworld=Counter()
    for key,records in sorted(groups.items()):
        r=records[0]
        assert len({x["source_model_sha256"] for x in records})==1,"same key has distinct model payloads"
        episode=load(r["episode"])
        solve=next(s for s in episode["solves"] if s["gate_index"]==r["gate"])
        root=Path(episode["evidence_store"])
        before=cas(root,solve["before_ref"])
        topology=cas(root,before["topology"])
        states=cas(root,before["vertex_state"])
        status={v["uid"]:s[0] for v,s in zip(topology["vertices"],states)}
        check=r.get("independent_decimal",{})
        maximum=check.get("max_row_violation")
        if maximum is None or not check.get("all_values_present",False):level="missing_or_nonfinite_incumbent"
        elif maximum<=1.01e-5:level="near_fixed_tolerance"
        elif maximum<.001:level="small_above_tolerance"
        else:level="material_ge_0.001"
        types=Counter();domains=Counter();examples=[]
        for row in check.get("rejected_rows",[]):
            kind=row_kind(row);types[kind]+=1;row_counts[kind]+=1
            ids={v[:-2] for v in row["terms"] if re.fullmatch(r"v_\d+_\d+_[sg]",v)}
            domain="completed_only" if ids and all(status[v]=="COMPLETED" for v in ids) else "includes_uncompleted" if ids else "non_vertex"
            domains[domain]+=1
            examples.append(dict(**row,kind=kind,status_domain=domain,vertex_statuses={v:status[v] for v in sorted(ids)}))
        examples.sort(key=lambda x:float(x["violation"]),reverse=True)
        occurrences=[dict(episode=x["episode"],gate=x["gate"],cache_reused=x["cache_reused"],new_author_calls=x["new_author_calls"]) for x in records]
        for x in records:
            path=Path(x["episode"]);byarm[path.parent.name]+=1;byworld[path.parent.parent.name]+=1;levels[level]+=1
        candidate=cas(root,solve["candidate_ref"])
        candidate_states=cas(root,candidate["group_state"])
        original_group_states=cas(root,before["group_state"])
        changed_groups=[g["uid"] for g,a,b in zip(topology["groups"],original_group_states,candidate_states)
            if [x[1] for x in a[2]] != [x[1] for x in b[2]]]
        unique.append(dict(semantic_key=key,status=r["status"],model_ref=r["model_ref"],
            occurrences=occurrences,level=level,max_row_violation=maximum,
            max_bound_violation=check.get("max_bound_violation"),max_integrality_violation=check.get("max_integrality_violation"),
            violated_row_types=dict(types),violated_row_status_domains=dict(domains),
            worst_rows=examples[:5],candidate_changed_groups=changed_groups,
            parent_retained=all(x["parent_retained"] for x in records)))
    result=dict(scope="post-hoc failure evidence classification, not solver root-cause proof or tolerance retuning",
        new_native_calls=0,script_sha256=sha(__file__),audit_path=str(args.audit),audit_sha256=sha(args.audit),
        audited_episodes=audit["episodes_seen"],failed_attempt_records=audit["failed_attempt_records"],
        unique_failed_inputs=len(unique),actual_author_calls=audit["actual_author_calls"],cached_failure_records=audit["cached_failure_records"],
        independently_verified=audit["passed"],record_severity=dict(levels),records_by_arm=dict(byarm),records_by_world=dict(byworld),
        unique_model_violated_row_counts=dict(row_counts),
        unique_severity=dict(Counter(r["level"] for r in unique)),
        unique_with_candidate_orientation_change=sum(bool(r["candidate_changed_groups"]) for r in unique),
        unique_with_uncompleted_violated_rows=sum(bool(r["violated_row_status_domains"].get("includes_uncompleted")) for r in unique),
        inputs=unique)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("inputs","records_by_world")},indent=2))


if __name__=="__main__":main()
