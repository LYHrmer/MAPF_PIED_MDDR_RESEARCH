"""Small, deterministic probability model; it never authorizes spatial release."""

from dataclasses import dataclass
import math


FEATURE_NAMES = (
    "predicted_gain", "relative_precision", "log_age", "log_capture_wait",
    "two_certificates", "threshold_gap",
)


def _features(values):
    try:
        values = tuple(values)
    except TypeError as exc:
        raise ValueError("features must be a sequence") from exc
    if len(values) != len(FEATURE_NAMES):
        raise ValueError("incorrect feature dimension")
    if any(isinstance(v, bool) or not isinstance(v, (int, float))
           or not math.isfinite(v) for v in values):
        raise ValueError("features must contain finite numbers")
    return tuple(float(v) for v in values)


@dataclass(frozen=True)
class Sample:
    run_id: str
    query_id: str
    features: tuple[float, ...]
    target: int

    def __post_init__(self):
        if any(not isinstance(v, str) or not v.strip()
               for v in (self.run_id, self.query_id)):
            raise ValueError("run_id and query_id must be nonempty strings")
        if type(self.target) is not int or self.target not in (0, 1):
            raise ValueError("target must be the integer 0 or 1")
        object.__setattr__(self, "features", _features(self.features))


def _samples(samples):
    rows = tuple(samples)
    if not rows or any(not isinstance(row, Sample) for row in rows):
        raise ValueError("a nonempty sequence of Sample objects is required")
    return rows


def _sigmoid(score):
    if score >= 0:
        return 1.0 / (1.0 + math.exp(-score))
    value = math.exp(score)
    return value / (1.0 + value)


@dataclass(frozen=True)
class MonotoneLogistic:
    means: tuple[float, ...]
    variances: tuple[float, ...]
    scales: tuple[float, ...]
    weights: tuple[float, ...]
    intercept: float
    training_run_ids: tuple[str, ...]
    training_rows: int

    @classmethod
    def fit(cls, samples, *, steps=600, learning_rate=0.1, l2=0.01):
        rows = _samples(samples)
        if type(steps) is not int or steps <= 0:
            raise ValueError("steps must be a positive integer")
        for name, value in (("learning_rate", learning_rate), ("l2", l2)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) \
                    or not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} must be a finite nonnegative number")
        if learning_rate == 0:
            raise ValueError("learning_rate must be positive")
        if {row.target for row in rows} != {0, 1}:
            raise ValueError("training requires both target classes")

        size, width = len(rows), len(FEATURE_NAMES)
        # These statistics use only the supplied training rows.
        try:
            means = tuple(math.fsum(row.features[j] / size for row in rows)
                          for j in range(width))
            variances = tuple(math.fsum((row.features[j] - means[j]) ** 2 / size
                                        for row in rows) for j in range(width))
        except (OverflowError, ValueError) as exc:
            raise ValueError("feature normalization overflowed") from exc
        if not all(math.isfinite(v) for v in means + variances):
            raise ValueError("feature normalization must remain finite")
        scales = tuple(math.sqrt(v) if v > 0 else 1.0 for v in variances)
        features = [tuple((v - m) / s for v, m, s
                          in zip(row.features, means, scales)) for row in rows]
        weights, intercept = [0.0] * width, 0.0
        for _ in range(steps):
            gradients, intercept_gradient = [0.0] * width, 0.0
            for row, values in zip(rows, features):
                score = intercept + sum(w * x for w, x in zip(weights, values))
                if not math.isfinite(score):
                    raise ValueError("training diverged; reduce learning_rate")
                error = _sigmoid(score) - row.target
                intercept_gradient += error / size
                for j in range(width):
                    gradients[j] += error * values[j] / size
            intercept -= learning_rate * intercept_gradient
            weights = [w - learning_rate * (g + l2 * w)
                       for w, g in zip(weights, gradients)]
            # Positive scales preserve the sign in original feature units.
            weights[-1] = min(weights[-1], 0.0)
            if not all(math.isfinite(v) for v in [intercept, *weights]):
                raise ValueError("training diverged; reduce learning_rate")
        return cls(means, variances, scales, tuple(weights), intercept,
                   tuple(sorted({row.run_id for row in rows})), size)

    def _score(self, features):
        values = _features(features)
        score = self.intercept + sum(w * ((x - m) / s)
                                    for w, x, m, s in
                                    zip(self.weights, values, self.means, self.scales))
        if not math.isfinite(score):
            raise ValueError("prediction score must remain finite")
        return score

    def predict(self, features) -> float:
        return _sigmoid(self._score(features))

    def to_dict(self):
        return {
            "model": "monotone_logistic_v1",
            "feature_names": list(FEATURE_NAMES),
            "normalization": "training_population_variance; zero_variance_scale=1",
            "means": list(self.means), "variances": list(self.variances),
            "scales": list(self.scales), "weights": list(self.weights),
            "intercept": self.intercept,
            "threshold_weight_constraint": "nonpositive",
            "training_run_ids": list(self.training_run_ids),
            "training_rows": self.training_rows,
        }


def split_by_run(samples, test_run_ids):
    rows = _samples(samples)
    if test_run_ids is None or isinstance(test_run_ids, (str, bytes)):
        raise ValueError("test_run_ids must be a nonempty collection of run IDs")
    requested = tuple(test_run_ids)
    if not requested or any(not isinstance(v, str) or not v.strip() for v in requested):
        raise ValueError("test_run_ids must contain nonempty strings")
    requested = set(requested)
    if requested - {row.run_id for row in rows}:
        raise ValueError("test_run_ids contains unknown runs")
    train = [row for row in rows if row.run_id not in requested]
    test = [row for row in rows if row.run_id in requested]
    if not train or not test:
        raise ValueError("training and test partitions must both be nonempty")
    return train, test


def evaluate(model, samples):
    rows = _samples(samples)
    squared_errors, losses = [], []
    for row in rows:
        score = model._score(row.features)
        squared_errors.append((_sigmoid(score) - row.target) ** 2)
        losses.append(max(score, 0.0) - row.target * score
                      + math.log1p(math.exp(-abs(score))))
    return {
        "rows": len(rows), "runs": len({row.run_id for row in rows}),
        "queries": len({(row.run_id, row.query_id) for row in rows}),
        "brier": math.fsum(squared_errors) / len(rows),
        "log_loss": math.fsum(losses) / len(rows),
    }
