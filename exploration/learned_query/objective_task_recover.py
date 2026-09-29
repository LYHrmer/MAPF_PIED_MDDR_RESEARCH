"""Recover complete native evidence with a corrected, decision-scoped offline observer.
No compile, native replay, parameter change or rewriting of earlier receipts.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from objective_task_run import INSTANCE_NAMES, TRAINING_SCOPE, digest_text, seconds
from objective_task_recovery_audit import audit_cohort_choices


def validate_events(events, index):
    expected_name = INSTANCE_NAMES[index]
    if events[0].get("id") != expected_name:
        raise ValueError("instance identity mismatch")
    histories = [e for e in events if e["event"] == "historical_native_END_delivered"]
    if len(histories) != 6 or len({e["run_id"] for e in histories}) != 6:
        raise ValueError("six unique training episodes required")
    if any(e["received"]["upper"] / e["received"]["denominator"] >= 32 for e in histories):
        raise ValueError("training history not available at held-out origin")
    models = [e for e in events if e["event"] == "frozen_predictor"]
    if len(models) != 6 or not all(e["frozen_before_test"] for e in models):
        raise ValueError("predictors were not frozen")
    first_test = next(k for k, e in enumerate(events) if e["event"] == "policy_begin")
    if any(e["event"] == "frozen_predictor" for e in events[first_test:]):
        raise ValueError("model was fit again after seeing test execution")
    results, block = [], None
    for event in events:
        kind = event["event"]
        if kind == "policy_begin":
            if block is not None:
                raise ValueError("unfinished prior test episode")
            if event["run_id"] in {e["run_id"] for e in histories}:
                raise ValueError("test episode in training")
            block = [event]
        elif block is not None:
            block.append(event)
            if kind == "policy_result":
                services = [e for e in block if e["event"] == "task_service"]
                launches = [e for e in block if e["event"] == "original_move_started"]
                labels = [e for e in block if e["event"] == "offline_duration_evaluation"]
                query_ids = [e["id"] for e in block if e["event"] == "query_selected"]
                curve = [sum(seconds(e["at"]) <= t for e in services)
                         for t in event["service_times"]]
                flow = sum(seconds(e["at"]) - seconds(e["assigned_at"]) for e in services)
                if (len(services) != 9 or len({e["task"] for e in services}) != 9
                        or len(launches) != 12 or len(labels) != 12
                        or any(e["feeds_online_model"] for e in labels)
                        or curve != event["completed_tasks"] or query_ids != event["queries"]
                        or flow != event["task_flow_sum"]
                        or max(seconds(e["at"]) for e in services) != event["last_task_service"]):
                    raise ValueError("independent task/decision/event accounting disagrees")
                compact = dict(event)
                first = [e for e in services if e["task"].endswith("-task1")]
                compact["current_cohort_service_times"] = {e["task"]: seconds(e["at"]) for e in first}
                compact["current_cohort_flow"] = sum(seconds(e["at"])-seconds(e["assigned_at"]) for e in first)
                compact["audited_cohort_decisions"] = audit_cohort_choices(block, next((m["alpha"] for m in models if m["predictor"]==event["predictor"]), None))
                compact["alpha_error_bounds"] = labels[0]["absolute_alpha_error"]
                compact["integrated_unfinished_tasks_8_to_16"] = sum(9 - n for n in curve)
                compact["native_quote_diagnostic"] = index >= 4
                results.append(compact)
                block = None
    expected_runs = 17 if index >= 4 else 16
    if block is not None or len(results) != expected_runs:
        raise ValueError("missing declared test episodes")
    common_count = sum(e["event"] == "common_initial_POSITION" for e in events)
    if common_count != expected_runs * (6 if index >= 4 else 0):
        raise ValueError("shared observation count mismatch")
    summary = events[-1]
    if (summary.get("event") != "summary" or summary.get("status") != "passed"
            or summary.get("training_scope") != TRAINING_SCOPE):
        raise ValueError("missing successful training/task summary")
    for flag in ("production_AUTH", "full_paid_cost", "independent_learning_advantage_claim",
                 "lifelong_performance_claim"):
        if summary.get(flag) is not False:
            raise ValueError(f"claim boundary changed: {flag}")
    return dict(instance=expected_name, results=results, checks=summary["checks"],
                history_fingerprint=digest_text(json.dumps(histories, sort_keys=True)),
                predictor_fingerprint=digest_text(json.dumps(models, sort_keys=True)))



def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text())
    if receipt["status"] != "failed_or_incomplete" or not receipt["all_sources_unchanged"]:
        raise ValueError("expected preserved second-run wrapper failure with intact sources")
    failures = receipt.get("instance_failures", [])
    if len(failures) != 6 or any(not f.endswith("ValueError: public launch must have an exact recorded time") for f in failures):
        raise ValueError("unexpected failure; this observer recovery does not apply")
    if hashlib.sha256(receipt["fixture_source"].encode()).hexdigest() != receipt["fixture_sha256"]:
        raise ValueError("embedded fixture snapshot hash mismatch")
    if hashlib.sha256(receipt["runner_source"].encode()).hexdigest() != receipt["runner_sha256"]:
        raise ValueError("embedded runner snapshot hash mismatch")
    if hashlib.sha256(receipt["auditor_source"].encode()).hexdigest() != receipt["auditor_sha256"]:
        raise ValueError("embedded independent auditor hash mismatch")
    native = receipt["commands"][1:]
    if len(native) != len(INSTANCE_NAMES):
        raise ValueError("six native instances required")
    actual = []
    for index, command in enumerate(native):
        if command["exit_code"] != 0 or command["timed_out"]:
            raise ValueError("failed native invocation")
        events = [json.loads(line) for line in command["stdout"].splitlines() if line.strip()]
        actual.append(validate_events(events, index))
    old_receipt = json.loads((args.receipt.parent / "temporal_task_run_20260929_03.json").read_text())
    reproduced = 0
    for previous, current in zip(old_receipt["instances"], actual):
        for prior in previous["results"]:
            matches = [x for x in current["results"] if (x["policy"], x["predictor"]) == (prior["policy"], prior["predictor"])]
            if len(matches) != 1 or any(matches[0][k] != v for k, v in prior.items() if k != "run_id"):
                raise ValueError("old objective/baseline behavior differs from historical receipt")
            reproduced += 1
    if reproduced != 62:
        raise ValueError("old episode reproduction incomplete")
    if (actual[2]["history_fingerprint"] != actual[3]["history_fingerprint"]
            or actual[2]["predictor_fingerprint"] != actual[3]["predictor_fingerprint"]):
        raise ValueError("no-signal pair received different predictor information")
    def decision_only(command):
        result, predictor, relevant = {}, None, False
        for event in [json.loads(line) for line in command["stdout"].splitlines() if line.strip()]:
            if event["event"] == "policy_begin":
                relevant = event["policy"] == "current_cohort_flow_pair"
                predictor = event["predictor"]
                if relevant:
                    result[predictor] = []
            elif relevant and event["event"] in ("cohort_input", "cohort_candidate", "cohort_choice", "query_selected", "no_query"):
                result[predictor].append(event)
        return result
    if decision_only(native[2]) != decision_only(native[3]):
        raise ValueError("same-history hidden shock changed public predictions or choices")
    rows = []
    for instance in actual:
        for result in instance["results"]:
            uses_duration = result["policy"].startswith("nominal_completion_") or result["policy"] == "current_cohort_flow_pair"
            error = result["alpha_error_bounds"]
            row = dict(instance=instance["instance"], predictor=result["predictor"], policy=result["policy"],
                       current_cohort_flow=result["current_cohort_flow"],
                       current_cohort_services=";".join(f"{k}:{v}" for k,v in result["current_cohort_service_times"].items()),
                       queries="".join(result["queries"]) or "WAIT",
                       query_count=len(result["queries"]),
                       common_initial_observations=result["common_initial_observations"],
                       task_flow_sum=result["task_flow_sum"],
                       last_task_service=result["last_task_service"],
                       integrated_unfinished_tasks=result["integrated_unfinished_tasks_8_to_16"],
                       final_tasks=result["final_tasks"],
                       original_requester_moves=result["original_requester_moves"],
                       duration_prediction_used_for_choice=uses_duration,
                       alpha_error_lower=error["lower"] / error["denominator"] if uses_duration else None,
                       alpha_error_upper=error["upper"] / error["denominator"] if uses_duration else None,
                       production_COST=False)
            row.update({f"completed_t{t}": n for t, n in
                        zip(result["service_times"], result["completed_tasks"])})
            rows.append(row)
    with args.csv.open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    pairs = []
    for instance in actual:
        for current in instance["results"]:
            if current["policy"] != "current_cohort_flow_pair":
                continue
            previous, = [x for x in instance["results"] if x["predictor"] == current["predictor"] and x["policy"] == "nominal_completion_pair_window6"]
            pairs.append(dict(instance=instance["instance"], predictor=current["predictor"],
                              old_queries="".join(previous["queries"]) or "WAIT",
                              new_queries="".join(current["queries"]) or "WAIT",
                              old_task_flow=previous["task_flow_sum"], new_task_flow=current["task_flow_sum"],
                              new_minus_old_flow=current["task_flow_sum"]-previous["task_flow_sum"],
                              old_current_cohort_flow=previous["current_cohort_flow"],
                              new_current_cohort_flow=current["current_cohort_flow"]))
    print(json.dumps(dict(status="passed", analysis_identity="independent_offline_recovery_no_native_rerun",
                          native_receipt_status_preserved=receipt["status"], wrapper_failures_preserved=failures,
                          all_62_old_episodes_reproduced=True,
                          recovery_analyzer_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                          recovery_auditor_sha256=hashlib.sha256((Path(__file__).parent / "objective_task_recovery_audit.py").read_bytes()).hexdigest(),
                          hidden_shock_public_inputs_candidates_choices_identical=True,
                          audited_cohort_decisions=sum(r["audited_cohort_decisions"] for x in actual for r in x["results"]),
                          paired_objective_comparisons=pairs, source_receipt_sha256=hashlib.sha256(args.receipt.read_bytes()).hexdigest(),
                          csv=str(args.csv), episodes=len(rows), tasks=sum(r["final_tasks"] for r in rows),
                          requester_moves=sum(r["original_requester_moves"] for r in rows),
                          native_checks=sum(x["checks"] for x in actual)), indent=2))


if __name__ == "__main__":
    main()
