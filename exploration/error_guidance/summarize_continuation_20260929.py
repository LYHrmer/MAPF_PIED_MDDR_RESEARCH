"""Verify and tabulate one frozen continuation receipt without rerunning trajectories."""
import argparse
import csv
import hashlib
import itertools
import json
from pathlib import Path

def midpoint(value):
    if value is None:
        return None
    return (value["lower_numerator"] + value["upper_numerator"]) / (2 * value["denominator"])

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--output-prefix", type=Path, required=True)
    args = parser.parse_args()
    raw = json.loads(args.receipt.read_text())
    assert raw["status"] == "passed"
    assert raw["protected_before"] == raw["protected_after"]
    assert raw["source_header_pins"] == raw["source_headers_after"]
    assert raw["sources"] == raw["sources_after"]
    assert len(raw["instances"]) == 16
    got = set()
    rows, comparisons, normalized = [], [], {}
    for instance in raw["instances"]:
        key = (instance["error_case"], instance["private_eta_offline_label"],
               instance["opportunity_case"], instance["native_END_delivery"])
        assert key not in got
        got.add(key)
        assert instance["status"] == "passed" and instance["command"]["exit_code"] == 0
        events = [json.loads(line) for line in instance["command"]["stdout"].splitlines()]
        assert events == instance["events"]
        decision = next(e for e in events if e["event"] == "selection_before_any_evaluation")
        assert events.index(decision) < next(i for i,e in enumerate(events) if e["event"] == "candidate_execution_begin")
        assert decision["legal_history_rows"] == 2
        assert not any(decision[k] for k in ("private_eta_feature", "future_END_truth_feature", "offline_counterfactual_feature"))
        results = [e for e in events if e["event"] == "candidate_result"]
        assert {e["plan"] for e in results} == {"UU", "UL", "LU", "LL"} and len(results) == 4
        for result in results:
            assert result["position_commits"] == 1
            assert result["native_blocker_END_delivered"] == key[3]
            if result["completed_tasks"] == 2:
                assert result["completed_original_MOVEs"] == 6 and not result["censored"]
                assert result["sum_task_flow_times"] == result["task2_completed_at"]
            else:
                assert result["task2_completed_at"] is None and result["censored"]
                assert midpoint(result["stopped_at"]) == 24
            assert abs(midpoint(result["stopped_at"]) - midpoint(result["movement"]) - midpoint(result["owner_evidence_wait"])) <= 2e-6
            row = dict(error_half_width=0.2 if key[0] else 0, requester_eta_offline_label=key[1],
                       observation_at=4 if key[2] else 2.5, native_END=key[3], plan=result["plan"],
                       completed_tasks=result["completed_tasks"], task1_completed_at=midpoint(result["task1_completed_at"]),
                       task2_completed_at=midpoint(result["task2_completed_at"]),
                       movement=midpoint(result["movement"]), owner_evidence_wait=midpoint(result["owner_evidence_wait"]),
                       task2_flow_time_from_activation=midpoint(result["task2_flow_time_from_activation"]),
                       sum_task_completion_times=midpoint(result["sum_task_completion_times"]),
                       motion_selected=result["plan"] == decision["motion_plan"],
                       analytic_selected=result["plan"] == decision["analytic_plan"], censored=result["censored"])
            rows.append(row)
        comparison = next(e for e in events if e["event"] == "comparison")
        comparison = dict(instance_id=events[0]["id"], **comparison)
        comparisons.append(comparison)
        normalized[key] = (decision, {r["plan"]: r for r in results})
    assert got == set(itertools.product((0,1),(-1,1),(0,1),(False,True)))
    # Same received calibration and query opportunity, change only spatial envelope.
    for eta, opportunity, end in itertools.product((-1,1),(0,1),(False,True)):
        zero, nonzero = normalized[(0,eta,opportunity,end)], normalized[(1,eta,opportunity,end)]
        assert zero[0]["alpha"] == nonzero[0]["alpha"]
        for plan in ("UU","UL","LU","LL"):
            a,b = zero[1][plan],nonzero[1][plan]
            assert midpoint(a["owner_evidence_wait"]) == 0
            if a["completed_tasks"] == b["completed_tasks"] == 2:
                assert a["movement"] == b["movement"]
    # Latent dynamics affect physical runs/history, never initial committed owners.
    for z, opportunity, end in itertools.product((0,1),(0,1),(False,True)):
        assert normalized[(z,-1,opportunity,end)][0]["public_signature"] == normalized[(z,1,opportunity,end)][0]["public_signature"]
    residuals = [e for i in raw["instances"] for e in i["events"] if e["event"] == "forecast_residual"]
    report = {"status": "passed", "receipt": str(args.receipt),
              "receipt_sha256": hashlib.sha256(args.receipt.read_bytes()).hexdigest(),
              "instances": 16, "actual_plan_executions": len(rows),
              "completed_task_pairs": sum(r["completed_tasks"] == 2 for r in rows),
              "censored_task_pairs": sum(r["censored"] for r in rows),
              "actual_completed_tasks": sum(r["completed_tasks"] for r in rows),
              "alpha_equal_across_error_interventions": True,
              "complete_plan_movement_equal_across_error_interventions": True,
              "initial_public_signatures_equal_across_private_eta": True,
              "all_completion_prediction_errors_zero": all(e["actual_minus_predicted_completed_tasks"] == 0 for e in residuals),
              "complete_arrival_residuals": [midpoint(e["task2_arrival_actual_minus_predicted"]) for e in residuals],
              "comparisons": comparisons,
              "data_status": "synthetic_native_mechanism", "full_online_cost_measured": False}
    with Path(str(args.output_prefix) + ".csv").open("x", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]), lineterminator="\n"); writer.writeheader(); writer.writerows(rows)
    with Path(str(args.output_prefix) + ".json").open("x") as stream:
        json.dump(report, stream, indent=2); stream.write("\n")
    print(json.dumps({k:v for k,v in report.items() if k not in ("comparisons","complete_arrival_residuals")}, indent=2))

if __name__ == "__main__":
    main()
