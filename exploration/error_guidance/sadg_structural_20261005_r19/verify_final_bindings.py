#!/usr/bin/env python3
"""Final source/receipt binding and diagnostic consistency, no experiment imports."""
import hashlib
import json
from pathlib import Path

HERE=Path(__file__).resolve().parent


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    reg=json.loads((HERE/"EXPERIMENT_REGISTRATION.json").read_text())
    pins=[];episodes=[];authors={}
    for name,expected in reg["source_pins"].items():
        file=HERE.parent/"sadg_benchmark_20261005_r18"/name.split("/")[-1] if name.startswith("inherited:R18/") else HERE/name
        actual=sha(file);pins.append(dict(name=name,path=str(file),expected=expected,actual=actual,passed=actual==expected))
    for path in sorted((HERE/"episodes").rglob("episode.json")):
        episode=json.loads(path.read_text());receipt=json.loads((path.parent/"RUN_RECEIPT.json").read_text())
        passed=(receipt["episode_sha256"]==sha(path) and receipt["spec"]["source_pins"]==reg["source_pins"]
            and receipt["spec"]["registration_sha256"]==sha(HERE/"EXPERIMENT_REGISTRATION.json")
            and episode["author_pin"]=="c2626d996121a9d6c128844a167b917db24418ac")
        for name,value in episode["adapter_source_hashes"].items():passed=passed and reg["source_pins"][name]==value
        for name,value in episode["source_hashes"].items():
            if name in authors:assert authors[name]==value
            authors[name]=value
        episodes.append(dict(path=str(path),sha256=sha(path),receipt_sha256=sha(path.parent/"RUN_RECEIPT.json"),passed=passed))
    for name,expected in authors.items():
        if name.startswith("/"):
            actual=sha(name);pins.append(dict(path=name,expected=expected,actual=actual,passed=actual==expected))
    diagnostic_path=HERE/"mechanism_review/DIAGNOSTICS.json"
    diagnostics=json.loads(diagnostic_path.read_text());errors=[];physical=nonzero=0
    for row in diagnostics["pairs"]:
        if row["delta_sum_completion"]:nonzero+=1
        if row["physical_event_times_equal"]:continue
        physical+=1;first=row["first_orientation_difference"]
        if first is None or first["time"]>row["first_physical_difference_time"]+1e-7:
            errors.append(dict(world=row["world"],a=row["a"],b=row["b"],reason="missing preceding orientation change"));continue
        for side in ("a","b"):
            for group in first["boundary_"+side]:
                if group["before_choices"]!=group["after_choices"] and not (
                    group["all_heads_staged"] and group["switchable"] and group["within_horizon"] and first[side]["adopted"]):
                    errors.append(dict(world=row["world"],a=row["a"],b=row["b"],group=group["uid"],reason="first changed boundary not legal"))
    result=dict(scope="Final read-only source, all episode receipts and mechanism consistency audit",
        script_sha256=sha(__file__),new_solver_calls=0,new_physical_runs=0,registered_rows=reg["planned_rows"],
        initial_failure_retention_policy=reg["initial_failure_rows_in_denominator"],
        registered_rows_without_executed_episode=reg["planned_rows"]-len(episodes),episode_count=len(episodes),
        all_source_pins_passed=all(x["passed"] for x in pins),all_episode_bindings_passed=all(x["passed"] for x in episodes),
        source_pins=pins,environment_metadata={k:v for k,v in authors.items() if not k.startswith("/")},episodes=episodes,
        mechanism_diagnostics_sha256=sha(diagnostic_path),mechanism_pairs=len(diagnostics["pairs"]),
        nonzero_completion_delta_pairs=nonzero,physical_event_time_difference_pairs=physical,
        first_changes_legal_and_precede_physical_differences=not errors,mechanism_errors=errors)
    result["passed"]=(result["all_source_pins_passed"] and result["all_episode_bindings_passed"] and not errors and len(episodes)==324)
    output=HERE/"solver_failure_review/FINAL_SOURCE_BINDINGS.json"
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in result.items() if k not in ("source_pins","episodes")},indent=2))
    assert result["passed"]


if __name__=="__main__":main()
