"""Independently recheck raw native events and export a compact, reproducible result table."""
import argparse
import csv
import hashlib
import json
from pathlib import Path

from temporal_task_run import INSTANCE_NAMES, validate_events


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
    rows = []
    for instance in actual:
        for result in instance["results"]:
            uses_duration = result["policy"].startswith("nominal_completion_")
            error = result["alpha_error_bounds"]
            row = dict(instance=instance["instance"], predictor=result["predictor"],
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
    print(json.dumps(dict(status="passed", source_receipt_sha256=hashlib.sha256(args.receipt.read_bytes()).hexdigest(),
                          csv=str(args.csv), episodes=len(rows), tasks=sum(r["final_tasks"] for r in rows),
                          requester_moves=sum(r["original_requester_moves"] for r in rows),
                          native_checks=sum(x["checks"] for x in actual)), indent=2))


if __name__ == "__main__":
    main()
