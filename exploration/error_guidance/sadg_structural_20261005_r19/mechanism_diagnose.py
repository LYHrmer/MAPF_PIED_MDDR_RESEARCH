#!/usr/bin/env python3
"""Read frozen episodes and CAS only; never imports a solver or simulator."""
import argparse
from collections import Counter
from functools import lru_cache
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
PAIRS = [(p+"_no_query", p+"_structural") for p in ("history", "learned", "ewma")] + [
    ("history_no_query", "learned_no_query"), ("ewma_no_query", "learned_no_query"),
    ("history_structural", "learned_structural"), ("ewma_structural", "learned_structural")]


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


@lru_cache(maxsize=2048)
def read_cas(root, key):
    p = Path(root)/"objects"/key[:2]/(key+".json.gz")
    raw = gzip.decompress(p.read_bytes())
    assert hashlib.sha256(raw).hexdigest() == key
    return json.loads(raw)


def cas(root, ref):
    assert ref["path"] == str(Path("objects")/ref["sha256"][:2]/(ref["sha256"]+".json.gz"))
    return read_cas(str(root), ref["sha256"])


def graph_parts(episode, ref):
    root = episode["evidence_store"]
    g = cas(root, ref)
    return (cas(root, g["topology"]), cas(root, g["vertex_state"]), cas(root, g["group_state"]))


def orientations(episode, ref):
    topology, _, states = graph_parts(episode, ref)
    return {g["uid"]: [s[1] for s in state[2]] for g, state in zip(topology["groups"], states)}


def changed(episode, solve, output="after_ref"):
    before, after = [orientations(episode, solve[k]) for k in ("before_ref", output)]
    assert before.keys() == after.keys()
    return [k for k in before if before[k] != after[k]]


def solve_summary(episode, solve):
    return dict(gate=solve["gate_index"], time=solve["time"], adopted=solve["adopted"],
        status=solve["model"]["status"], max_row_violation=solve["model"]["max_violation"],
        max_bound_violation=solve["model"]["max_bound_violation"],
        max_integrality_violation=solve["model"]["max_integrality_violation"],
        actual_changed_groups=changed(episode, solve),
        candidate_changed_groups=changed(episode, solve, "candidate_ref"),
        semantic_key=solve["semantic_key"], model_ref=solve["model_ref"],
        before_ref=solve["before_ref"], after_ref=solve["after_ref"])


def boundary(episode, solve, names):
    topology, vertices, states = graph_parts(episode, solve["before_ref"])
    statuses = {v["uid"]: state[0] for v, state in zip(topology["vertices"], vertices)}
    after = orientations(episode, solve["after_ref"])
    result = []
    for group, state in zip(topology["groups"], states):
        if group["uid"] not in names:
            continue
        heads = sorted({d[direction][1] for d in group["dependencies"] for direction in ("forward", "reverse")})
        result.append(dict(uid=group["uid"], switchable=state[0], within_horizon=state[1],
            before_choices=[s[1] for s in state[2]], after_choices=after[group["uid"]],
            heads={h: statuses[h] for h in heads}, all_heads_staged=all(statuses[h]=="STAGED" for h in heads),
            dependencies=group["dependencies"]))
    return result


def compare(world, name_a, a, name_b, b):
    sa = {s["gate_index"]: s for s in a["solves"]}
    sb = {s["gate_index"]: s for s in b["solves"]}
    first = None
    for gate in sorted(sa.keys() & sb.keys()):
        x, y = sa[gate], sb[gate]
        assert abs(x["time"]-y["time"]) < 1e-7
        ox, oy = orientations(a, x["after_ref"]), orientations(b, y["after_ref"])
        assert ox.keys() == oy.keys()
        names = [k for k in ox if ox[k] != oy[k]]
        if names:
            first = dict(gate=gate, time=x["time"], groups=names,
                a=solve_summary(a, x), b=solve_summary(b, y),
                boundary_a=boundary(a,x,names), boundary_b=boundary(b,y,names))
            break
    ea = {(e["kind"],e["vertex"]):e for e in a["events"] if e["kind"] in ("START","END")}
    eb = {(e["kind"],e["vertex"]):e for e in b["events"] if e["kind"] in ("START","END")}
    common=ea.keys() & eb.keys()
    differences=sorted([(min(ea[k]["time"],eb[k]["time"]),k,ea[k],eb[k]) for k in common
        if abs(ea[k]["time"]-eb[k]["time"]) > 1e-7])
    first_time = differences[0][0] if differences else None
    failures = [[solve_summary(e,s) for s in e["solves"] if not s["adopted"]] for e in (a,b)]
    deltas={k: dict(a=v,b=b["completion_times"][k],delta=b["completion_times"][k]-v)
        for k,v in a["completion_times"].items()
        if k in b["completion_times"] and abs(b["completion_times"][k]-v)>1e-7}
    return dict(world=world, a=name_a, b=name_b,
        status_a=a["status"], status_b=b["status"],
        sum_completion_a=a["sum_completion"], sum_completion_b=b["sum_completion"],
        delta_sum_completion=b["sum_completion"]-a["sum_completion"],
        makespan_a=a["makespan"],makespan_b=b["makespan"],
        queries_a=a["query_count"],queries_b=b["query_count"],
        first_orientation_difference=first, first_physical_difference_time=first_time,
        different_event_times=len(differences), unmatched_events_a=len(ea.keys()-eb.keys()),
        unmatched_events_b=len(eb.keys()-ea.keys()),
        first_different_events=[dict(a=x[2],b=x[3]) for x in differences[:12]],
        physical_event_times_equal=not differences and ea.keys()==eb.keys(),
        completion_deltas=deltas, failures_a=failures[0], failures_b=failures[1],
        failures_before_first_physical_difference_a=[s for s in failures[0] if first_time is not None and s["time"]<=first_time],
        failures_before_first_physical_difference_b=[s for s in failures[1] if first_time is not None and s["time"]<=first_time],
        actual_orientation_changes_a=[solve_summary(a,s) for s in a["solves"] if changed(a,s)],
        actual_orientation_changes_b=[solve_summary(b,s) for s in b["solves"] if changed(b,s)])


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--world", action="append", default=[])
    parser.add_argument("--output",type=Path,default=HERE/"mechanism_review/DIAGNOSTICS.json")
    args=parser.parse_args()
    records, manifest, missing=[],[],[]
    for world in sorted((HERE/"episodes").iterdir()):
        if not world.is_dir() or (args.world and world.name not in args.world):continue
        episodes={}
        for path in sorted(world.glob("*/episode.json")):
            receipt=path.parent/"RUN_RECEIPT.json"
            if not receipt.exists():continue
            episode=json.loads(path.read_text())
            if episode.get("status")!="completed":continue
            episodes[path.parent.name]=episode
            manifest.append(dict(path=str(path),sha256=sha(path),receipt_sha256=sha(receipt)))
        for a,b in PAIRS:
            if a not in episodes or b not in episodes:
                missing.append(dict(world=world.name,a=a,b=b));continue
            records.append(compare(world.name,a,episodes[a],b,episodes[b]))
    summary={}
    for a,b in PAIRS:
        subset=[r for r in records if r["a"]==a and r["b"]==b]
        summary[a+" -> "+b]=dict(pairs=len(subset),
            completion_delta_counts=dict(Counter("gain" if r["delta_sum_completion"]<0 else "loss" if r["delta_sum_completion"]>0 else "equal" for r in subset)),
            same_physical_event_times=sum(r["physical_event_times_equal"] for r in subset),
            only_query_count_diff=sum(r["physical_event_times_equal"] and r["queries_a"]!=r["queries_b"] for r in subset),
            nonzero_delta_with_any_solver_rejection=sum(r["delta_sum_completion"]!=0 and bool(r["failures_a"] or r["failures_b"]) for r in subset))
    report=dict(scope="post-hoc read-only mechanism diagnosis; not new heldout experiment or tuning",
        new_native_calls=0,script_sha256=sha(__file__),input_manifest=manifest,summary=summary,
        pairs=records,missing_or_not_finished_pairs=missing)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_text(json.dumps(report,indent=2,sort_keys=True,allow_nan=False)+"\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":main()
