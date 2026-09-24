"""Synthetic checks only: these do not establish execution or research gains."""

import json
import math
import unittest

from .model import FEATURE_NAMES, MonotoneLogistic, Sample, evaluate, split_by_run


def synthetic_rows(run_id="train"):
    return [Sample(run_id, str(i), (0.5, 1.0, 0.0, 0.0, 1.0, gap), int(gap < 2.0))
            for i, gap in enumerate((0.2, 0.4, 0.8, 1.0, 3.0, 3.2, 3.6, 3.8))]


class ModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = synthetic_rows()
        cls.model = MonotoneLogistic.fit(cls.rows)

    def test_threshold_probability_is_monotone_for_unseen_contexts(self):
        for context in ((0.5, 1.0, 0.0, 0.0, 1.0), (1.5, 0.2, 4.0, 2.0, 0.0)):
            probabilities = [self.model.predict((*context, gap))
                             for gap in (-100.0, 0.0, 0.2, 1.5, 2.0, 8.0, 100.0)]
            self.assertTrue(all(a >= b for a, b in zip(probabilities, probabilities[1:])))
            self.assertTrue(all(0.0 <= p <= 1.0 for p in probabilities))
        self.assertLess(self.model.weights[-1], 0.0)
        self.assertTrue(all(s > 0 for s in self.model.scales))

    def test_projection_resists_training_labels_that_reward_higher_thresholds(self):
        reversed_rows = [Sample(r.run_id, r.query_id, r.features, 1 - r.target)
                         for r in self.rows]
        model = MonotoneLogistic.fit(reversed_rows)
        context = self.rows[0].features[:-1]
        self.assertGreaterEqual(model.predict((*context, 0.0)),
                                model.predict((*context, 10.0)))

    def test_holdout_changes_do_not_affect_training_or_normalization(self):
        holdout = synthetic_rows("held_out")
        altered = [Sample(r.run_id, r.query_id, tuple(v + 1e6 for v in r.features),
                          1 - r.target) for r in holdout]
        train, test = split_by_run(self.rows + holdout, {"held_out"})
        altered_train, altered_test = split_by_run(self.rows + altered, {"held_out"})
        first, second = MonotoneLogistic.fit(train), MonotoneLogistic.fit(altered_train)
        self.assertEqual(first.to_dict(), second.to_dict())
        self.assertEqual(first.means[0], 0.5)
        self.assertEqual(first.variances[0], 0.0)
        self.assertEqual(first.training_run_ids, ("train",))
        self.assertEqual({r.run_id for r in train} & {r.run_id for r in test}, set())
        self.assertEqual(len(altered_test), len(test))

    def test_fit_improves_synthetic_loss_and_serializes_finite_parameters(self):
        metrics = evaluate(self.model, synthetic_rows("held_out"))
        self.assertLess(metrics["log_loss"], math.log(2.0) * 0.5)
        self.assertLess(metrics["brier"], 0.125)
        self.assertEqual((metrics["rows"], metrics["runs"], metrics["queries"]), (8, 1, 8))
        self.assertEqual(json.loads(json.dumps(self.model.to_dict(), allow_nan=False))
                         ["feature_names"], list(FEATURE_NAMES))

    def test_split_rejects_missing_unknown_or_exhaustive_holdout(self):
        for test_runs in (None, [], ["unknown"], ["train"], "train", [""]):
            with self.subTest(test_runs=test_runs), self.assertRaises(ValueError):
                split_by_run(self.rows, test_runs)

    def test_invalid_data_and_hyperparameters_are_rejected(self):
        for features in ((0.0,), (0.0,) * 5 + (math.nan,), (math.inf,) * 6):
            with self.subTest(features=features), self.assertRaises(ValueError):
                Sample("run", "query", features, 0)
            with self.assertRaises(ValueError):
                self.model.predict(features)
        for target in (-1, 2, None, True, 0.0):
            with self.subTest(target=target), self.assertRaises(ValueError):
                Sample("run", "query", (0.0,) * 6, target)
        for arguments in ({"steps": 0}, {"steps": True}, {"learning_rate": 0},
                          {"learning_rate": math.inf}, {"l2": -1}, {"l2": math.nan}):
            with self.subTest(arguments=arguments), self.assertRaises(ValueError):
                MonotoneLogistic.fit(self.rows, **arguments)
        with self.assertRaises(ValueError):
            MonotoneLogistic.fit(self.rows[:2])
        with self.assertRaises(ValueError):
            evaluate(self.model, [])


if __name__ == "__main__":
    unittest.main()
