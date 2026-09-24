"""End-to-end synthetic software checks, with no production event replay."""

from dataclasses import replace
from fractions import Fraction as F
import unittest

from .example import synthetic_samples, toy_action
from .model import FEATURE_NAMES, MonotoneLogistic, split_by_run
from .shadow import (
    FEATURE_NAMES as SHADOW_FEATURE_NAMES,
    Demand, Relation, Snapshot, features, forecast, label_return, rank,
)


class IntegrationTests(unittest.TestCase):
    def test_label_fit_and_shadow_rank_compose_without_changing_state(self):
        train, held_out = split_by_run(synthetic_samples(), {"toy-holdout"})
        self.assertEqual(FEATURE_NAMES, SHADOW_FEATURE_NAMES)
        self.assertFalse({s.run_id for s in train} & {s.run_id for s in held_out})
        # Multiple thresholds from one query stay in the same partition.
        self.assertEqual(len(held_out), 4 * len({s.query_id for s in held_out}))
        model = MonotoneLogistic.fit(train)
        slow, fast = toy_action("slow", F(1, 5)), toy_action("fast", F(2, 5))
        view = Snapshot("toy-view", F(2), (slow, fast), (
            Demand("slow-request", 1, (Relation("slow", F(3, 5)),), F(0)),
            Demand("fast-request", 1, (Relation("fast", F(3, 5)),), F(0)),
        ))
        advice = rank(view, model)
        self.assertEqual(advice.ranked[0].move_id, "fast")
        self.assertEqual(advice.view_id, "toy-view")
        self.assertEqual((slow.q, fast.q), (F(1, 5), F(2, 5)))
        predicted = forecast(fast, F(2))
        probabilities = [model.predict(features(fast, t, predicted))
                         for t in (F(1, 2), F(3, 5), F(7, 10), F(4, 5))]
        self.assertTrue(all(a >= b for a, b in zip(probabilities, probabilities[1:])))

    def test_missing_id_cannot_create_a_valid_label(self):
        for missing in (None, "", " "):
            with self.subTest(missing=missing), self.assertRaises(ValueError):
                label_return(query_id=missing, response_query_id=missing,
                             move_id="move", response_move_id="move",
                             threshold=F(0), lower=F(1), status="valid")

    def test_negative_work_and_future_demands_are_not_legal_snapshots(self):
        action = toy_action("move", F(1, 5))
        with self.assertRaises(ValueError):
            replace(action.receipts[0], charged_work=F(-1))
        with self.assertRaises(ValueError):
            Snapshot("view", F(2), (action,), (
                Demand("future", 1, (Relation("move", F(3, 5)),), F(3)),
            ))


if __name__ == "__main__":
    unittest.main()
