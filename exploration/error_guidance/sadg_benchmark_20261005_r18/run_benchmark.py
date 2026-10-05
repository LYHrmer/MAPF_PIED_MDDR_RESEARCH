#!/usr/bin/env python3
"""Registered, resumable complete-episode SADG query comparison.

Run with the pinned R16 virtualenv. Existing content-matching episodes are read,
never rerun. The author-input cache independently deduplicates repeated solves.
"""
from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import sys
import time

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import engine
import policies


DISTURBANCES = {
    "stable": dict(kind="stable", affected_fraction=0., stable_factor=1.),
    "bounded_pause": dict(kind="bounded_pause", affected_fraction=.5,
        stable_factor=1., pause_probability=.25, pause_duration=3., pause_fraction=.35),
    "speed_shift": dict(kind="speed_shift", affected_fraction=.5,
        stable_factor=1., shift_action_fraction=.35, shifted_factor=.5),
}
ARMS = ("history_only", "fixed_update", "history_rule", "learned_query", "dense_position")
PIN_FILES = ("PROTOCOL.md", "PUBLIC_SCHEMA.json", "engine.py", "policies.py", "run_benchmark.py")


def utc():
    return datetime.now(timezone.utc).isoformat()


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True, allow_nan=False) + "\n")
    temporary.replace(path)


def freeze(path, value):
    path = Path(path)
    if path.exists():
        assert load(path) == value, f"refuse mutation of frozen artifact: {path}"
    else:
        save(path, value)


def update_progress(stage, **kwargs):
    obj = dict(stage=stage, updated_utc=utc(), process_id=os.getpid(), **kwargs)
    save(HERE / "PROGRESS.json", obj)
    print(json.dumps(obj, ensure_ascii=False), flush=True)


def normalized_split(value):
    return {"TRAIN": "TRAIN", "CALIBRATION": "CAL", "CAL": "CAL", "TEST": "TEST"}[value.upper()]


def data_cases():
    registered = load(HERE / "data/REGISTERED_MATRIX.json")["cases"]
    result = []
    for record in registered:
        path = HERE / "data/cases" / record["case_id"] / "plan.json"
        assert path.exists(), f"dataset preparation incomplete: {path}"
        case = load(path)
        assert case["case_id"] == record["case_id"]
        assert case["status"] not in ("pending", "running"), "data still live"
        family = f'{record["map_name"]}__s{int(record["scenario_id"]):02d}'
        result.append(dict(record, split=normalized_split(record["split"]),
            family=family, case_path=str(path.relative_to(HERE)),
            case_sha256=sha(path), status=case["status"]))
    return result


def register():
    path = HERE / "EXPERIMENT_REGISTRATION.json"
    pins = {name: sha(HERE / name) for name in PIN_FILES}
    cases = data_cases()
    if path.exists():
        reg = load(path)
        assert reg["source_pins"] == pins, "scientific code changed after registration"
        assert reg["cases"] == cases, "registered data changed"
        assert reg["disturbances"] == DISTURBANCES and reg["arms"] == list(ARMS)
        return reg
    assert len(cases) == 45
    assert {c["num_agents"] for c in cases} == {8, 16, 32}
    assert len({c["map_name"] for c in cases}) == 3
    assert not (HERE / "MODEL_FROZEN.json").exists()
    reg = dict(schema="r18-standard-map-query-experiment-v1", registered_utc=utc(),
        source_pins=pins, data_registration_sha256=sha(HERE / "data/REGISTERED_MATRIX.json"),
        cases=cases, disturbances=DISTURBANCES, arms=list(ARMS),
        training_probe_gates=[1, 3], training_target_rules={"1": "highest_history_score", "3": "largest_downstream_nominal"},
        training_continuation="history_rule except single registered probe override",
        model_selection="TRAIN family LOFO MSE, alphas 1/10/100, fixed positive query threshold",
        evaluation_splits=["CAL", "TEST"], independent_unit="map_name x scenario_id",
        config=dict(period="max(4, public_nominal_makespan/12)", query_latency=.25,
            query_budget="N", max_queries_per_gate="ceil(N/8)", horizon=5.,
            max_time="max(100, 8*total_public_move_count+10)",
            save_gate_graphs=True, save_models=False),
        no_test_or_calibration_used_for_fit=True, production_charging=False)
    freeze(path, reg)
    return reg


def assert_pins(reg):
    assert reg["source_pins"] == {n: sha(HERE / n) for n in PIN_FILES}


def world_seed(family):
    # Independent of team size, disturbance, strategy, and action scheduling.
    return int(hashlib.sha256(("r18|" + family).encode()).hexdigest()[:8], 16)


def public_config(case, output_dir):
    schedules = case["solution"]["schedule"]
    makespan = max(float(path[-1]["t"]) for path in schedules.values())
    moves = sum(sum((a["x"], a["y"]) != (b["x"], b["y"])
        for a, b in zip(path, path[1:])) for path in schedules.values())
    n = len(schedules)
    return engine.EngineConfig(solve_period=max(4., makespan / 12.),
        query_latency=.25, query_budget=n, max_queries_per_gate=math.ceil(n/8),
        horizon=5., max_time=max(100., 8.*moves+10.),
        cache_dir=str(HERE / "author_cache"), output_dir=str(output_dir),
        save_models=False, save_gate_graphs=True)


def get_policy(arm):
    constructors = {"history_only": policies.NoQuery, "fixed_update": policies.FixedUpdate,
        "history_rule": policies.HistoryRule, "dense_position": engine.DensePositionPolicy}
    if arm == "learned_query":
        return policies.LearnedQuery(HERE / "MODEL_FROZEN.json")
    return constructors[arm]()


def episode(reg, case_record, disturbance, arm, *, probe=None, suffix=None):
    assert_pins(reg)
    case_path = HERE / case_record["case_path"]
    assert sha(case_path) == case_record["case_sha256"]
    case = load(case_path)
    assert case["status"] == "valid"
    world = case_record["case_id"] + "__" + disturbance
    directory = HERE / "episodes" / case_record["split"] / world / (suffix or arm)
    spec = dict(case=case_record, disturbance=DISTURBANCES[disturbance],
        seed=world_seed(case_record["family"]), arm=arm,
        probe_override={str(k): v for k, v in (probe or {}).items()},
        config=engine.asdict(public_config(case, directory)), source_pins=reg["source_pins"],
        model_sha256=sha(HERE / "MODEL_FROZEN.json") if arm == "learned_query" else None)
    spec_hash = policies.canonical_hash(spec)
    receipt_path = directory / "RUN_RECEIPT.json"
    output = directory / "episode.json"
    if receipt_path.exists():
        receipt = load(receipt_path)
        assert receipt["spec_sha256"] == spec_hash
        assert output.exists() and sha(output) == receipt["episode_sha256"]
        return load(output), directory, True
    if (directory / "STARTED.json").exists():
        raise RuntimeError(f"unfinished attempt requires live-process inspection before rerun: {directory}")
    start = dict(spec_sha256=spec_hash, started_utc=utc(), process_id=os.getpid(), spec=spec)
    freeze(directory / "STARTED.json", start)
    started = time.perf_counter()
    policy = get_policy(arm)
    try:
        result = engine.Simulator(case, DISTURBANCES[disturbance], spec["seed"],
            config=public_config(case, directory)).run(policy, probe_override=probe)
    except Exception as exc:
        # Constructor/source/graph failures remain in every method's denominator.
        config = public_config(case, directory)
        result = dict(schema="r18-constructor-failure", case_id=case_record["case_id"],
            status="constructor_failure", error=repr(exc), success=False,
            agents=case_record["num_agents"], completed_agents=0, query_count=0,
            restricted_sum_completion=config.max_time*case_record["num_agents"],
            sum_completion=None, makespan=None, common_horizon=config.max_time,
            gates=[], events=[], queries=[], solves=[], segments=[],
            config=engine.asdict(config), failures=[dict(kind="CONSTRUCTOR", error=repr(exc))])
    if arm == "learned_query":
        for gate in result["gates"]:
            snap = gate["public_snapshot"]
            gate["learned_scores"] = {a["agent_id"]: policy.predict(snap, a)
                for a in policies.eligible(snap)}
    result["benchmark"] = dict(world=world, family=case_record["family"],
        split=case_record["split"], disturbance=disturbance, arm=arm,
        probe=spec["probe_override"], spec_sha256=spec_hash)
    save(output, result)
    freeze(receipt_path, dict(**start, finished_utc=utc(), elapsed_seconds=time.perf_counter()-started,
        episode_sha256=sha(output), status=result["status"], success=result["success"]))
    return result, directory, False


def prefix_signature(result, gate_index):
    gate = next(g for g in result["gates"] if g["gate_index"] == gate_index)
    now = gate["capture_time"]
    physical = []
    for segment in result["segments"]:
        if segment["t0"] >= now:
            continue
        end = min(now, segment["t1"])
        fraction = (end-segment["t0"])/(segment["t1"]-segment["t0"])
        endpoint = [a+fraction*(b-a) for a, b in zip(segment["p0"], segment["p1"])]
        physical.append(dict(agent=segment["agent"], vertex=segment["vertex"], kind=segment["kind"],
            t0=round(segment["t0"], 8), t1=round(end, 8),
            p0=[round(x, 8) for x in segment["p0"]], p1=[round(x, 8) for x in endpoint]))
    return policies.canonical_hash(dict(
        prior_gates=[g for g in result["gates"] if g["gate_index"] < gate_index],
        current_public=gate["public_snapshot"],
        events=[e for e in result["events"] if e["time"] <= now],
        physical_prefix_quantized_1e8=physical))


def collect(reg):
    rows = []; omissions = []; pairs = []; world_count = 0
    for record in reg["cases"]:
        if record["split"] != "TRAIN":
            continue
        if record["status"] != "valid":
            omissions.append(dict(case_id=record["case_id"], reason="initial_planner_failure", status=record["status"]))
            continue
        for disturbance in DISTURBANCES:
            world_count += 1
            update_progress("collect", case=record["case_id"], disturbance=disturbance,
                world=world_count, labels=len(rows), omitted=len(omissions))
            base, base_dir, _ = episode(reg, record, disturbance, "history_rule")
            for g in reg["training_probe_gates"]:
                pair_id = f'{record["case_id"]}__{disturbance}__g{g}'
                gates = [gate for gate in base["gates"] if gate["gate_index"] == g]
                if not gates:
                    omissions.append(dict(pair_id=pair_id, reason="no_registered_gate", episode_status=base["status"]))
                    continue
                snap = gates[0]["public_snapshot"]
                available = policies.eligible(snap)
                if not available or policies.allowance(snap) == 0:
                    omissions.append(dict(pair_id=pair_id, reason="no_eligible_or_no_budget"))
                    continue
                if g == 1:
                    available.sort(key=lambda a: (-policies.history_score(a), a["agent_id"]))
                else:
                    available.sort(key=lambda a: (-a["downstream_nominal"], a["agent_id"]))
                candidate = available[0]
                paths = []; results = []; reuse = []
                for name, selection in [("noquery", []), ("query", [candidate["agent_id"]])]:
                    if gates[0]["selected"] == selection:
                        result, directory = base, base_dir
                        reused = "identical selected action; same history continuation"
                    else:
                        result, directory, was_existing = episode(reg, record, disturbance, "history_rule",
                            probe={g: selection}, suffix=f"probe_g{g}_{name}")
                        reused = "existing content-matched complete episode" if was_existing else None
                    results.append(result); paths.append(str((directory/"episode.json").relative_to(HERE))); reuse.append(reused)
                a, b = results
                same_prefix = prefix_signature(a, g) == prefix_signature(b, g) == prefix_signature(base, g)
                evidence = dict(pair_id=pair_id, family=record["family"], split="TRAIN",
                    target_agent=candidate["agent_id"], gate_index=g, public_snapshot=snap,
                    noquery_episode=paths[0], query_episode=paths[1],
                    episode_sha256=[sha(HERE/p) for p in paths], exact_episode_reuse=reuse,
                    same_prefix=same_prefix, status=[a["status"], b["status"]],
                    query_count_difference=b["query_count"]-a["query_count"],
                    completed_difference=b["completed_agents"]-a["completed_agents"])
                assert same_prefix, "counterfactual did not share public/physical prefix"
                legal = all(r["status"] in ("completed", "truncated") and
                    r.get("collision_audit", {}).get("passed", False) for r in results)
                evidence["eligible_label"] = legal
                if legal:
                    value = a["restricted_sum_completion"]-b["restricted_sum_completion"]
                    evidence["value"] = value
                    rows.append(dict(pair_id=pair_id, family=record["family"], split="TRAIN",
                        features=policies.features(snap, candidate), value=value,
                        pair_evidence_sha256=policies.canonical_hash(evidence)))
                else:
                    omissions.append(dict(pair_id=pair_id, reason="invalid_execution_for_value_label", status=evidence["status"]))
                pairs.append(evidence)
                save(HERE / "training/PAIRS.json", pairs)
                save(HERE / "training/LABELS.json", rows)
                save(HERE / "training/OMISSIONS.json", omissions)
    freeze(HERE / "training/COLLECTION_COMPLETE.json", dict(worlds=world_count,
        labels=len(rows), pairs=len(pairs), omissions=len(omissions),
        labels_sha256=policies.canonical_hash(rows), pairs_sha256=policies.canonical_hash(pairs),
        omissions_sha256=policies.canonical_hash(omissions)))
    return rows


def fit(reg):
    assert_pins(reg)
    rows = load(HERE / "training/LABELS.json")
    complete = load(HERE / "training/COLLECTION_COMPLETE.json")
    assert complete["labels_sha256"] == policies.canonical_hash(rows)
    model, selection = policies.fit_grouped(rows)
    model_path = HERE / "MODEL_FROZEN.json"
    freeze(model_path, model)
    freeze(HERE / "training/GROUPED_MODEL_SELECTION.json", selection)
    stamp = HERE / "MODEL_FREEZE_RECEIPT.json"
    if not stamp.exists():
        for split in ("CAL", "TEST"):
            assert not list((HERE / "episodes" / split).glob("*/learned_query/RUN_RECEIPT.json"))
        freeze(stamp, dict(frozen_utc=utc(), model_sha256=sha(model_path),
            source_pins=reg["source_pins"], label_sha256=sha(HERE / "training/LABELS.json"),
            training_rows=len(rows), training_families=len({r["family"] for r in rows}),
            before_any_calibration_or_test_learned_execution=True))
    assert load(stamp)["model_sha256"] == sha(model_path)
    update_progress("model_frozen", training_rows=len(rows), alpha=model["alpha"])


def evaluate(reg):
    assert_pins(reg)
    assert load(HERE / "MODEL_FREEZE_RECEIPT.json")["model_sha256"] == sha(HERE / "MODEL_FROZEN.json")
    count = 0
    for split in reg["evaluation_splits"]:
        for record in reg["cases"]:
            if record["split"] != split or record["status"] != "valid":
                continue
            for disturbance in DISTURBANCES:
                for arm in reg["arms"]:
                    count += 1
                    update_progress("evaluate", split=split, case=record["case_id"],
                        disturbance=disturbance, arm=arm, requested_episode=count)
                    episode(reg, record, disturbance, arm)
    update_progress("execution_complete", requested_evaluations=count)


def summarize(reg):
    rows = []; missing = []
    for record in reg["cases"]:
        if record["split"] not in reg["evaluation_splits"]:
            continue
        for disturbance in DISTURBANCES:
            world = record["case_id"] + "__" + disturbance
            for arm in reg["arms"]:
                base = dict(case_id=record["case_id"], family=record["family"],
                    map_name=record["map_name"], num_agents=record["num_agents"],
                    split=record["split"], disturbance=disturbance, arm=arm)
                if record["status"] != "valid":
                    rows.append(dict(base, status="initial_planner_"+record["status"],
                        success=False, completed_agents=0, episode_path=""))
                    continue
                path = HERE / "episodes" / record["split"] / world / arm / "episode.json"
                if not path.exists():
                    missing.append(dict(base, path=str(path.relative_to(HERE))))
                    continue
                result = load(path)
                receipt = load(path.parent / "RUN_RECEIPT.json")
                assert receipt["episode_sha256"] == sha(path)
                row = dict(base, episode_path=str(path.relative_to(HERE)), episode_sha256=sha(path))
                for key in ["status", "success", "completed_agents", "sum_completion", "restricted_sum_completion",
                            "makespan", "query_count", "query_payload_bytes", "solver_calls", "new_author_calls",
                            "reference_solver_seconds", "new_solver_seconds", "reference_author_seconds", "episode_wall_seconds"]:
                    row[key] = result.get(key)
                row["stale_queries"] = sum(q["delivery_status"] == "stale_occurrence" for q in result["queries"])
                row["pending_queries"] = sum(q["delivery_status"] == "pending" for q in result["queries"])
                row["solver_failure_count"] = sum(f["kind"] == "SOLVER_FAILURE_PARENT_GRAPH_RETAINED" for f in result["failures"])
                rows.append(row)
    save(HERE / "SUMMARY.json", dict(rows=rows, missing=missing))
    fields = sorted({k for r in rows for k in r})
    with (HERE / "SUMMARY.csv").open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    print(json.dumps(dict(summary_rows=len(rows), missing=len(missing))), flush=True)
    return rows, missing


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["register", "collect", "fit", "evaluate", "summarize", "all"])
    args = parser.parse_args()
    reg = register()
    if args.stage in ("collect", "all"):
        collect(reg)
    if args.stage in ("fit", "all"):
        fit(reg)
    if args.stage in ("evaluate", "all"):
        evaluate(reg)
    if args.stage in ("summarize", "all"):
        summarize(reg)


if __name__ == "__main__":
    main()
