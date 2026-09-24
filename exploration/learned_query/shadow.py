"""Research-only shadow scorer for learned progress-query ranking.

Synthetic/rational shadow prototype only. This module ranks *advisory*
progress queries from caller-supplied immutable snapshots. It never authorizes
movement, never changes ownership, implements no geometry, and performs no
C++ integration: the caller's ``retirable``/``valid``/``settled`` flags stand
for prior admission and are NOT authenticated here (no certificate
verification, no trusted committed evidence).

Limitations:
  * Synthetic/rational shadow prototype only; no original simulator, no real
    logs, no exporter, no Flint algebraic state bridge, no B1 accounting.
  * Scores are one-query estimates CONDITIONAL ON a valid matching response;
    they omit response failure risk and are neither a joint future-query
    probability nor a throughput guarantee.
  * No safety, liveness, or throughput claim is made or implied.
  * Returned advice is not an execution command: an empty ranking defers to
    the original scheduler, and a non-empty ranking is only a suggestion.

All time / progress / threshold / work quantities must be
``fractions.Fraction`` (floats are rejected). Floating point enters only ML
features, probabilities and expected scores.
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from fractions import Fraction

__all__ = [
    "Certificate", "Receipt", "Action", "Relation", "Demand", "Snapshot",
    "Forecast", "Advisory", "Decision",
    "forecast", "features", "rank", "label_return",
]

_ZERO = Fraction(0)
_STATUSES = frozenset({"valid", "invalid", "pending", "unqueried"})
FEATURE_NAMES = (
    "predicted_gain", "relative_precision", "log_age",
    "log_capture_wait", "two_certificates", "threshold_gap",
)


def _frac(value: object, label: str, *, nonneg: bool = True) -> Fraction:
    """Accept only exact Fraction values; floats/ints are malformed input."""
    if type(value) is not Fraction:
        raise ValueError(
            f"{label} must be a fractions.Fraction, got {type(value).__name__}")
    if nonneg and value < 0:
        raise ValueError(f"{label} must be non-negative, got {value}")
    return value


def _tup(value: object, label: str) -> tuple:
    if not isinstance(value, tuple):
        raise ValueError(f"{label} must be a tuple")
    return value


@dataclass(frozen=True)
class Certificate:
    move_id: str
    key: str
    captured: Fraction
    delivered: Fraction
    lower: Fraction
    epsilon: Fraction
    cap_at_capture: Fraction  # historical central cap at capture time
    valid: bool = True

    def __post_init__(self) -> None:
        for name in ("captured", "delivered", "lower", "epsilon", "cap_at_capture"):
            _frac(getattr(self, name), f"Certificate.{name}")


@dataclass(frozen=True)
class Receipt:
    key: str
    profile: str
    epsilon: Fraction
    published: Fraction
    captured: Fraction
    committed: Fraction
    delivered: Fraction
    charged_work: Fraction
    settled: bool = True

    def __post_init__(self) -> None:
        for name in ("epsilon", "published", "captured", "committed", "delivered"):
            _frac(getattr(self, name), f"Receipt.{name}")
        # Zero work can be unpriced; negative settled work is malformed.
        _frac(self.charged_work, "Receipt.charged_work")


@dataclass(frozen=True)
class Action:
    move_id: str
    profile: str
    epsilon: Fraction
    q: Fraction
    cap: Fraction
    history: tuple[Certificate, ...] = ()
    receipts: tuple[Receipt, ...] = ()
    eligible: bool = True

    def __post_init__(self) -> None:
        for name in ("epsilon", "q", "cap"):
            _frac(getattr(self, name), f"Action.{name}")
        if self.epsilon <= 0:
            raise ValueError("Action.epsilon must be positive")
        if self.q > self.cap:
            raise ValueError("Action requires q <= cap")
        _tup(self.history, "Action.history")
        _tup(self.receipts, "Action.receipts")


@dataclass(frozen=True)
class Relation:
    owner: str
    threshold: Fraction | None
    retirable: bool = True
    # None preserves old synthetic fixtures where owner is also the MOVE ID.
    # An explicit empty action denotes a non-query responsibility.
    action: str | None = None

    def __post_init__(self) -> None:
        if self.threshold is not None:
            _frac(self.threshold, "Relation.threshold")


@dataclass(frozen=True)
class Demand:
    key: str
    weight: int
    relations: tuple[Relation, ...]
    added_at: Fraction
    other_ready: bool = True

    def __post_init__(self) -> None:
        if type(self.weight) is not int or self.weight <= 0:
            raise ValueError("Demand.weight must be a positive int")
        _tup(self.relations, "Demand.relations")
        owners = [r.owner for r in self.relations]
        if len(set(owners)) != len(owners):
            raise ValueError(f"duplicate owner in demand {self.key!r}")
        _frac(self.added_at, "Demand.added_at")


@dataclass(frozen=True)
class Snapshot:
    view_id: str
    now: Fraction
    actions: tuple[Action, ...]
    demands: tuple[Demand, ...]

    def __post_init__(self) -> None:
        _frac(self.now, "Snapshot.now")
        moves = [a.move_id for a in _tup(self.actions, "Snapshot.actions")]
        if len(set(moves)) != len(moves):
            raise ValueError("duplicate move_id in snapshot")
        keys = [d.key for d in _tup(self.demands, "Snapshot.demands")]
        if len(set(keys)) != len(keys):
            raise ValueError("duplicate demand key in snapshot")
        if any(d.added_at > self.now for d in self.demands):
            raise ValueError("snapshot contains a demand from the future")


@dataclass(frozen=True)
class Forecast:
    q_hat: Fraction
    age: Fraction
    capture_wait: Fraction
    return_wait: Fraction
    work: Fraction
    two_certificates: bool

    def __post_init__(self) -> None:
        for name in ("q_hat", "age", "capture_wait", "return_wait", "work"):
            _frac(getattr(self, name), f"Forecast.{name}")


@dataclass(frozen=True)
class Advisory:
    move_id: str
    expected_admissions: float
    partial_credit: float
    denominator: Fraction

    def __post_init__(self) -> None:
        _frac(self.denominator, "Advisory.denominator")


@dataclass(frozen=True)
class Decision:
    view_id: str
    ranked: tuple[Advisory, ...]
    disposition: str

    def __post_init__(self) -> None:
        _tup(self.ranked, "Decision.ranked")
        if self.disposition not in ("advice", "defer_to_original"):
            raise ValueError(f"unknown disposition {self.disposition!r}")


def _midpoint(cert: Certificate) -> Fraction:
    # Interval midpoint uses the historical cap recorded at capture time.
    return (cert.lower + min(cert.cap_at_capture, cert.lower + cert.epsilon)) / 2


def forecast(action: Action, now: Fraction) -> Forecast | None:
    """Advisory progress/cost forecast, or None to defer (cold start)."""
    _frac(now, "now")
    if not action.eligible or action.cap <= action.q:
        return None

    per_capture: dict[Fraction, Certificate] = {}
    for cert in action.history:
        if (not cert.valid) or cert.move_id != action.move_id or cert.delivered > now:
            continue  # invalid / other-move / not yet admitted: ignorable
        if (cert.captured > cert.delivered or cert.epsilon <= 0
                or cert.lower > cert.cap_at_capture):
            raise ValueError(f"malformed certificate {cert.key!r}")
        prev = per_capture.get(cert.captured)
        rank_key = (cert.epsilon, -cert.lower, cert.key)
        if prev is None or rank_key < (prev.epsilon, -prev.lower, prev.key):
            per_capture[cert.captured] = cert
    if not per_capture:
        return None

    times = sorted(per_capture)[-2:]  # latest two distinct capture times
    mids = [_midpoint(per_capture[t]) for t in times]
    if len(times) == 2:
        velocity = max(_ZERO, (mids[1] - mids[0]) / (times[1] - times[0]))
    else:
        velocity = _ZERO

    chosen: Receipt | None = None
    for rec in action.receipts:
        if (not rec.settled or rec.profile != action.profile
                or rec.epsilon != action.epsilon or rec.delivered > now):
            continue
        if not (rec.published <= rec.captured <= rec.committed <= rec.delivered):
            raise ValueError(f"malformed receipt {rec.key!r}")
        if chosen is None or (-rec.committed, rec.key) < (-chosen.committed, chosen.key):
            chosen = rec
    if chosen is None:
        return None
    # Latest receipt is selected first; a degenerate latest receipt defers and
    # is never silently replaced by an older one.
    if chosen.charged_work <= 0 or (chosen.committed - chosen.published) <= 0:
        return None

    capture_wait = chosen.captured - chosen.published
    return_wait = chosen.committed - chosen.captured
    age = now - times[-1]
    # Physical extrapolation reaches now + capture_wait only; return_wait is a
    # reporting delay and is excluded from progress.
    estimated = mids[-1] + velocity * (age + capture_wait)
    if estimated < action.q:
        estimated = action.q
    elif estimated > action.cap:
        estimated = action.cap
    q_hat = max(action.q, max(_ZERO, estimated - action.epsilon))
    return Forecast(q_hat, age, capture_wait, return_wait,
                    chosen.charged_work, len(times) == 2)


def features(action: Action, threshold: Fraction,
             prediction: Forecast) -> tuple[float, ...]:
    """Feature vector in FEATURE_NAMES order; only the last uses threshold."""
    _frac(threshold, "threshold")
    span = action.cap - action.q
    if span <= 0:
        raise ValueError("feature span (cap - q) must be positive")
    try:
        values = (
            float((prediction.q_hat - action.q) / span),
            float(action.epsilon / span),
            math.log1p(float(prediction.age)),
            math.log1p(float(prediction.capture_wait)),
            float(bool(prediction.two_certificates)),
            float((threshold - action.q) / span),
        )
    except (OverflowError, ValueError) as exc:
        raise ValueError("features cannot be represented as finite floats") from exc
    for name, value in zip(FEATURE_NAMES, values):
        if not math.isfinite(value):
            raise ValueError(f"non-finite feature {name}")
    return values


def _probability(action: Action, threshold: Fraction,
                 prediction: Forecast, predictor: object | None) -> float:
    if predictor is None:
        return 1.0 if prediction.q_hat > threshold else 0.0  # exact, strict
    raw = predictor.predict(features(action, threshold, prediction))
    if type(raw) is bool or not isinstance(raw, (int, float)):
        raise ValueError("predictor.predict must return a real number")
    value = float(raw)
    if not math.isfinite(value) or value < 0.0 or value > 1.0:
        raise ValueError(f"predicted probability out of [0, 1]: {value}")
    return value


def rank(snapshot: Snapshot, predictor: object | None = None) -> Decision:
    """Rank advisory queries lexicographically by (A/K, P/K)."""
    candidates: dict[str, tuple[Action, Forecast]] = {}
    for action in snapshot.actions:
        if not action.eligible:
            continue
        prediction = forecast(action, snapshot.now)
        if prediction is not None:
            candidates[action.move_id] = (action, prediction)

    acc: dict[str, list] = {}  # move_id -> [A, P, earliest contributing added_at]
    for demand in snapshot.demands:
        owner_count = len(demand.relations)  # blocked owners still count
        if owner_count == 0 or not demand.other_ready:
            continue
        for rel in demand.relations:
            if not rel.retirable or rel.threshold is None:
                continue
            action_key = rel.owner if rel.action is None else rel.action
            found = candidates.get(action_key)
            if found is None:
                continue  # absent owner action is not assumed queryable
            action, prediction = found
            if not (action.q <= rel.threshold < action.cap):
                continue  # endpoint / non-query / cap failure scores nothing
            p = _probability(action, rel.threshold, prediction, predictor)
            if p <= 0.0:
                continue
            # Preserve exact indicator/count arithmetic for the secant path.
            # Learned p is still a float estimate; Fraction preserves that
            # returned value exactly without further accumulation rounding.
            probability = Fraction(p)
            row = acc.setdefault(action_key, [_ZERO, _ZERO, None])
            if owner_count == 1:
                row[0] += demand.weight * probability
            row[1] += demand.weight * probability / owner_count
            if row[2] is None or demand.added_at < row[2]:
                row[2] = demand.added_at

    rows = []
    for move_id, (a_score, p_score, added_at) in acc.items():
        try:
            reported_a, reported_p = float(a_score), float(p_score)
        except OverflowError as exc:
            raise ValueError("expected scores exceed finite report range") from exc
        if not math.isfinite(reported_a) or not math.isfinite(reported_p):
            raise ValueError("expected scores must remain finite")
        prediction = candidates[move_id][1]
        k = prediction.work * (prediction.capture_wait + prediction.return_wait)
        if k <= 0 or (a_score <= 0.0 and p_score <= 0.0):
            continue
        # Float report fields never participate in selection or tie-breaking.
        rows.append((-(a_score / k), -(p_score / k),
                     added_at, move_id,
                     Advisory(move_id, reported_a, reported_p, k)))
    rows.sort(key=lambda row: row[:4])
    ranked = tuple(row[4] for row in rows)
    return Decision(snapshot.view_id, ranked,
                    "advice" if ranked else "defer_to_original")


def label_return(*, query_id: str, move_id: str, threshold: Fraction,
                 response_query_id: str | None, response_move_id: str | None,
                 lower: Fraction | None, status: str) -> int | None:
    """Label conditional on a valid matching response; None means no label."""
    if status not in _STATUSES:
        raise ValueError(f"unknown status {status!r}")
    if status != "valid":
        return None  # invalid/pending/unqueried are unlabelled, never zero
    if any(not isinstance(key, str) or not key.strip()
           for key in (query_id, move_id, response_query_id, response_move_id)):
        raise ValueError("valid response requires nonempty query and MOVE IDs")
    if response_query_id != query_id or response_move_id != move_id:
        raise ValueError("valid response does not match the issued query")
    _frac(threshold, "threshold")
    _frac(lower, "lower")
    return int(lower > threshold)  # equality is a miss
