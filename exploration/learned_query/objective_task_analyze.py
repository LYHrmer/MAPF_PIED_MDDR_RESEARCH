"""Independently recheck raw native events and export a compact, reproducible result table."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from objective_task_run import INSTANCE_NAMES, validate_events


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--csv", required=True, type=Path)
    args = parser.parse_args()
    receipt = json.loads(args.receipt.read_text())
    if receipt["status"] != "passed" or not receipt["all_sources_unchanged"]:
        raise ValueError("a passing unmodified-source receipt is required")
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
    if actual != receipt["instances"]:
        raise ValueError("recomputed raw-event results differ from receipt")
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
    print(json.dumps(dict(status="passed", all_62_old_episodes_reproduced=receipt["all_62_old_episodes_reproduced"],
                          hidden_shock_public_inputs_candidates_choices_identical=True,
                          audited_cohort_decisions=sum(r["audited_cohort_decisions"] for x in actual for r in x["results"]),
                          paired_objective_comparisons=pairs, source_receipt_sha256=hashlib.sha256(args.receipt.read_bytes()).hexdigest(),
                          csv=str(args.csv), episodes=len(rows), tasks=sum(r["final_tasks"] for r in rows),
                          requester_moves=sum(r["original_requester_moves"] for r in rows),
                          native_checks=sum(x["checks"] for x in actual)), indent=2))


if __name__ == "__main__":
    main()
