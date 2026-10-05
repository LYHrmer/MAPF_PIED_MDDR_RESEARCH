"""Public-information query policies and grouped, frozen value regression.

The label is a measured paired complete-episode outcome, never a private rate.
No policy receives map identity, disturbance identity, seed, or future progress.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path

import numpy as np


FEATURES = [
    "elapsed_ratio", "history_ratio", "history_count_log", "history_cv",
    "progress_estimate", "remaining_estimate", "measurement_age_ratio",
    "no_current_measurement", "measurement_count_log", "outgoing_blocked",
    "upcoming_switchable", "downstream_log", "budget_per_agent",
    "gate_log", "active_fraction", "global_blocked_fraction",
    "overdue", "blocked_uncertainty", "overdue_blockers",
    "switchable_uncertainty", "remaining_blockers", "age_blockers",
]


def canonical_hash(obj):
    return hashlib.sha256(json.dumps(obj, sort_keys=True,
        separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def eligible(snapshot):
    return [a for a in snapshot["agents"] if a["query_eligible"]]


def allowance(snapshot):
    remaining = snapshot["budget_remaining"]
    if remaining is None:
        return int(snapshot["max_queries"])
    return max(0, min(int(remaining), int(snapshot["max_queries"])))


def features(snapshot, agent):
    nominal = max(1e-9, float(agent["nominal_duration"]))
    ratio = max(1e-9, float(agent["history_ratio"]))
    elapsed = float(agent["elapsed"]) / (nominal * ratio)
    cv = max(0., float(agent["history_cv"]))
    age = agent["last_measurement_age"]
    no_measurement = age is None
    age_ratio = float(agent["elapsed"] if no_measurement else age) / nominal
    blockers = float(agent["outgoing_blocked_agents"])
    influence = float(agent["upcoming_switchable_influence"])
    uncertainty = max(.25, cv) * ratio
    overdue = max(0., elapsed - 1.)
    n = max(1, len(snapshot["agents"]))
    remaining_budget = snapshot["budget_remaining"]
    values = [
        elapsed, ratio, math.log1p(agent["history_count"]), cv,
        float(agent["progress_estimate"]), float(agent["remaining_estimate"]),
        age_ratio, float(no_measurement), math.log1p(agent["measurement_count"]),
        blockers, influence, math.log1p(agent["downstream_nominal"]),
        float(remaining_budget or 0) / n, math.log1p(snapshot["gate_index"]),
        len(eligible(snapshot)) / n,
        sum(bool(a["blocked"]) for a in snapshot["agents"]) / n,
        overdue, blockers * uncertainty, overdue * blockers,
        influence * uncertainty, float(agent["remaining_estimate"]) * blockers,
        age_ratio * blockers,
    ]
    assert len(values) == len(FEATURES) and all(math.isfinite(x) for x in values)
    return values


def history_score(agent):
    """A public uncertainty/impact rule, with an explicit change-point floor.

    An overdue action can still block others when its clamped progress estimate
    is one, so it must not receive a zero score merely for zero predicted time.
    """
    nominal = max(1e-9, float(agent["nominal_duration"]))
    ratio = max(1., float(agent["history_ratio"]))
    age = agent["last_measurement_age"]
    if age is not None and float(age) < .5 * nominal:
        return 0.
    uncertainty = nominal * max(.25, float(agent["history_cv"])) * ratio
    overdue = max(0., float(agent["elapsed"]) - nominal * ratio)
    residual = max(float(agent["remaining_estimate"]), overdue, .25 * nominal)
    impact = float(agent["outgoing_blocked_agents"])
    downstream = 1. + min(2., float(agent["downstream_nominal"]) / nominal)
    return impact * min(residual, uncertainty + overdue) * downstream / (
        1. + float(agent["measurement_count"]))


class NoQuery:
    name = "history_only"

    def __call__(self, snapshot):
        return []


class FixedUpdate:
    name = "fixed_update"

    def __call__(self, snapshot):
        # A fixed cyclic scan on every gate, with the same budget and gate cap.
        agents = snapshot["agents"]
        if not agents:
            return []
        offset = (int(snapshot["gate_index"]) * int(snapshot["max_queries"])) % len(agents)
        order = agents[offset:] + agents[:offset]
        return [a["agent_id"] for a in order if a["query_eligible"]][:allowance(snapshot)]


class HistoryRule:
    name = "history_rule"

    def __call__(self, snapshot):
        ranked = sorted(eligible(snapshot), key=lambda a: (-history_score(a), a["agent_id"]))
        return [a["agent_id"] for a in ranked if history_score(a) > 0.][:allowance(snapshot)]


class LearnedQuery:
    name = "learned_query"

    def __init__(self, model):
        if isinstance(model, (str, Path)):
            model = json.loads(Path(model).read_text())
        assert model["features"] == FEATURES
        self.model = model

    def predict(self, snapshot, agent):
        x = np.asarray(features(snapshot, agent), dtype=float)
        m = self.model
        z = (x - np.asarray(m["mean"])) / np.asarray(m["scale"])
        return float(m["intercept"] + z @ np.asarray(m["coef"]))

    def __call__(self, snapshot):
        scored = [(self.predict(snapshot, a), a["agent_id"]) for a in eligible(snapshot)]
        scored.sort(key=lambda pair: (-pair[0], pair[1]))
        return [aid for score, aid in scored if score > 1e-8][:allowance(snapshot)]


def _fit(rows, alpha):
    x = np.asarray([r["features"] for r in rows], dtype=float)
    y = np.asarray([r["value"] for r in rows], dtype=float)
    counts = {family: sum(r["family"] == family for r in rows)
              for family in {r["family"] for r in rows}}
    w = np.asarray([1. / counts[r["family"]] for r in rows])
    w *= len(rows) / w.sum()
    mean = np.average(x, axis=0, weights=w)
    scale = np.sqrt(np.average((x-mean)**2, axis=0, weights=w))
    scale[scale < 1e-10] = 1.
    design = np.column_stack([np.ones(len(rows)), (x-mean)/scale])
    penalty = np.diag([0.] + [float(alpha)] * x.shape[1])
    normal = design.T @ (w[:, None] * design) + penalty
    target = design.T @ (w*y)
    beta = np.linalg.solve(normal, target)
    return dict(features=FEATURES, alpha=float(alpha), mean=mean.tolist(),
        scale=scale.tolist(), intercept=float(beta[0]), coef=beta[1:].tolist(),
        fitted_rows=len(rows), fitted_families=sorted(counts),
        normal_equation_max_residual=float(np.max(np.abs(normal @ beta-target))))


def fit_grouped(rows, alphas=(1., 10., 100.)):
    """Select regularization on TRAIN families only; CAL/TEST never enter fit."""
    assert rows and all(r["split"] == "TRAIN" for r in rows)
    assert len({r["pair_id"] for r in rows}) == len(rows)
    assert all(len(r["features"]) == len(FEATURES) and
               math.isfinite(r["value"]) for r in rows)
    families = sorted({r["family"] for r in rows})
    assert len(families) >= 2, "grouped selection needs independent families"
    validation = []
    for alpha in alphas:
        folds = []
        for family in families:
            train = [r for r in rows if r["family"] != family]
            held = [r for r in rows if r["family"] == family]
            model = _fit(train, alpha)
            x = np.asarray([r["features"] for r in held])
            predictions = model["intercept"] + ((x-np.asarray(model["mean"])) /
                np.asarray(model["scale"])) @ np.asarray(model["coef"])
            folds.append(dict(held_family=family, trained_families=model["fitted_families"],
                pair_ids=[r["pair_id"] for r in held], predictions=predictions.tolist(),
                mse=float(np.mean((predictions-np.asarray([r["value"] for r in held]))**2)),
                model=model))
        validation.append(dict(alpha=float(alpha), folds=folds,
            family_mean_mse=float(np.mean([f["mse"] for f in folds]))))
    selected = min(validation, key=lambda v: (v["family_mean_mse"], v["alpha"]))
    model = _fit(rows, selected["alpha"])
    model.update(schema="r18-paired-completion-value-ridge-v1",
        label="restricted completion time sum(noquery) - sum(query one agent), same continuation",
        fit_scope="TRAIN only, grouped by map/scenario across nested team sizes and disturbances",
        rows_sha256=canonical_hash(rows), query_threshold=1e-8,
        selected_by="minimum family-mean held-out MSE; smaller alpha breaks ties")
    return model, dict(families=families, candidates=validation,
        selected_alpha=selected["alpha"], test_or_calibration_used=False)
