"""A synthetic software example, not a research dataset or robot simulation."""

from fractions import Fraction as F
import json
from time import perf_counter

from .model import MonotoneLogistic, Sample, evaluate, split_by_run
from .shadow import (
    Action, Certificate, Demand, Receipt, Relation, Snapshot,
    features, forecast, label_return, rank,
)


def toy_action(move_id, progress):
    """All fractions here are illustrative fixture values, not experiment settings."""
    return Action(
        move_id=move_id, profile="synthetic", epsilon=F(1, 10),
        q=progress, cap=F(1),
        history=(
            Certificate(move_id, "first", F(0), F(0), F(0), F(1, 10), F(1)),
            Certificate(move_id, "second", F(1), F(1), progress, F(1, 10), F(1)),
        ),
        receipts=(Receipt("receipt", "synthetic", F(1, 10), F(0), F(0),
                          F(1), F(1), F(1)),),
    )


def synthetic_samples():
    """Four threshold labels share each query; entire runs stay together."""
    rows = []
    for run_id in ("toy-train-a", "toy-train-b", "toy-holdout"):
        for index in range(1, 5):
            action = toy_action(f"move-{index}", F(index, 10))
            prediction = forecast(action, F(2))
            query_id = f"query-{index}"
            # An explicitly invented returned lower bound; never a private
            # production state, an observed trajectory, or a measured result.
            returned_lower = min(action.cap, 2 * action.q)
            for step in range(1, 5):
                threshold = action.q + (action.cap - action.q) * F(step, 5)
                target = label_return(
                    query_id=query_id, move_id=action.move_id, threshold=threshold,
                    response_query_id=query_id, response_move_id=action.move_id,
                    lower=returned_lower, status="valid",
                )
                rows.append(Sample(run_id, query_id,
                                   features(action, threshold, prediction), target))
    return rows


def main():
    train, held_out = split_by_run(synthetic_samples(), {"toy-holdout"})
    started = perf_counter()
    model = MonotoneLogistic.fit(train)
    fit_seconds = perf_counter() - started
    slow = toy_action("slow", F(1, 5))
    fast = toy_action("fast", F(2, 5))
    snapshot = Snapshot("synthetic-view", F(2), (slow, fast), (
        Demand("waiting-slow", 1, (Relation("slow", F(3, 5)),), F(0)),
        Demand("waiting-fast", 1, (Relation("fast", F(3, 5)),), F(0)),
    ))
    started = perf_counter()
    learned = rank(snapshot, predictor=model)
    inference_seconds = perf_counter() - started
    baseline = rank(snapshot)
    print(json.dumps({
        "data_status": "synthetic_software_example_only",
        "probability_target": "threshold_crossing_conditional_on_valid_response",
        "training_runs": model.training_run_ids,
        "held_out": evaluate(model, held_out),
        "secant_order": [row.move_id for row in baseline.ranked],
        "learned_order": [row.move_id for row in learned.ranked],
        "disposition": learned.disposition,
        "host_fit_seconds": fit_seconds,
        "host_shadow_rank_seconds": inference_seconds,
        "b1_cost_mapping": "not_implemented",
        "production_integration": False,
        "safety_or_throughput_evidence": False,
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
