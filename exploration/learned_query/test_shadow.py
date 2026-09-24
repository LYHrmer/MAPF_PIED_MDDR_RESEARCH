"""Synthetic rational fixtures only; no production data, guests, or claims."""

import copy
import unittest
from dataclasses import FrozenInstanceError, fields, replace
from fractions import Fraction as F

from .shadow import (
    Action, Certificate, Demand, Receipt, Relation, Snapshot,
    forecast, label_return, rank,
)


class ConstantPredictor:
    def __init__(self, probability=1.0):
        self.probability = probability

    def predict(self, values):
        return self.probability


def action(move="move-A"):
    """Two admitted samples imply unit secant speed, not physical truth."""
    history = (
        Certificate(move, "c0", F(0), F(0), F(0), F(1, 4), F(10)),
        Certificate(move, "c1", F(2), F(2), F(2), F(1, 4), F(10)),
    )
    receipt = Receipt("r1", "profile", F(1, 4), F(0), F(1),
                      F(2), F(2), F(2))
    return Action(move, "profile", F(1, 4), F(2), F(10),
                  history, (receipt,))


def snapshot(candidate=None, relations=None, weight=1):
    candidate = action() if candidate is None else candidate
    if relations is None:
        relations = (Relation(candidate.move_id, F(3)),)
    demand = Demand("demand", weight, relations, F(0))
    return Snapshot("committed-view-7", F(4), (candidate,), (demand,))


class ShadowBoundaryTests(unittest.TestCase):
    def test_exact_partial_tie_uses_join_time_not_float_accumulation(self):
        a, b = action("move-A"), action("move-B")
        retained = tuple(Relation(f"resident-{i}", None, False, action="")
                         for i in range(9))
        # Both have exact P=3/10 and identical costs. B joined first.
        # Float accumulation makes 1/10+1/10+1/10 exceed 3/10.
        demands = tuple(Demand(f"A-{i}", 1,
                               (Relation(a.move_id, F(3)),) + retained, F(1))
                        for i in range(3)) + (
            Demand("B", 3, (Relation(b.move_id, F(3)),) + retained, F(0)),)
        view = Snapshot("exact-tie", F(4), (a, b), demands)
        for predictor in (None, ConstantPredictor(1.0)):
            with self.subTest(predictor=predictor):
                self.assertEqual(rank(view, predictor).ranked[0].move_id, "move-B")

    def test_strict_equality_has_no_predicted_release(self):
        a = action()
        predicted = forecast(a, F(4))
        self.assertEqual(predicted.q_hat, F(39, 8))
        equal = snapshot(a, (Relation(a.move_id, F(39, 8)),))
        self.assertEqual(rank(equal).disposition, "defer_to_original")
        crossed = snapshot(a, (Relation(a.move_id, F(38, 8)),))
        self.assertEqual(rank(crossed).ranked[0].expected_admissions, 1.0)

    def test_return_wait_changes_cost_but_not_capture_progress(self):
        a = action()
        delayed = replace(a.receipts[0], committed=F(3), delivered=F(3))
        b = replace(a, receipts=(delayed,))
        short, long = forecast(a, F(4)), forecast(b, F(4))
        self.assertEqual(short.capture_wait, long.capture_wait)
        self.assertEqual(short.q_hat, long.q_hat)
        self.assertEqual((short.return_wait, long.return_wait), (F(1), F(2)))
        self.assertEqual(rank(snapshot(a)).ranked[0].denominator, F(4))
        self.assertEqual(rank(snapshot(b)).ranked[0].denominator, F(6))

    def test_future_other_move_and_invalid_certificates_are_ignored(self):
        a = action()
        extra = (
            Certificate(a.move_id, "future", F(5), F(6), F(8), F(1, 4), F(10)),
            Certificate("other-MOVE", "other", F(3), F(3), F(8), F(1, 4), F(10)),
            Certificate(a.move_id, "invalid", F(3), F(3), F(8), F(1, 4),
                        F(10), valid=False),
        )
        self.assertEqual(forecast(replace(a, history=a.history + extra), F(4)),
                         forecast(a, F(4)))

    def test_future_or_unsettled_receipts_cannot_change_quote(self):
        a = action()
        extra = (
            Receipt("future", "profile", F(1, 4), F(2), F(3), F(4), F(5), F(99)),
            Receipt("pending", "profile", F(1, 4), F(2), F(3), F(4), F(4),
                    F(99), settled=False),
        )
        self.assertEqual(forecast(replace(a, receipts=a.receipts + extra), F(4)),
                         forecast(a, F(4)))

    def test_latest_zero_duration_does_not_fall_back_to_old_quote(self):
        a = action()
        zero = Receipt("zero", "profile", F(1, 4), F(3), F(3),
                       F(3), F(3), F(2))
        unpriced = replace(a, receipts=a.receipts + (zero,))
        self.assertIsNone(forecast(unpriced, F(4)))
        self.assertEqual(rank(snapshot(unpriced), ConstantPredictor()).ranked, ())

    def test_model_cannot_override_known_relation_ineligibility(self):
        a = action()
        impossible = (
            Relation(a.move_id, F(1), retirable=False),
            Relation(a.move_id, None),
            Relation(a.move_id, a.cap),
            Relation(a.move_id, a.cap + 1),
        )
        for relation in impossible:
            with self.subTest(relation=relation):
                decision = rank(snapshot(a, (relation,)), ConstantPredictor())
                self.assertEqual(decision.ranked, ())
                self.assertEqual(decision.disposition, "defer_to_original")
        held = snapshot(a)
        held = replace(held, demands=(replace(held.demands[0], other_ready=False),))
        self.assertEqual(rank(held, ConstantPredictor()).ranked, ())

    def test_unqueryable_owner_still_prevents_immediate_admission(self):
        a = action()
        both = (Relation(a.move_id, F(3)), Relation("resident-owner", None, False))
        advice = rank(snapshot(a, both, weight=2), ConstantPredictor()).ranked[0]
        self.assertEqual(advice.expected_admissions, 0.0)
        self.assertEqual(advice.partial_credit, 1.0)
        alone = rank(snapshot(a, weight=2), ConstantPredictor()).ranked[0]
        self.assertEqual(alone.expected_admissions, 2.0)
        self.assertEqual(alone.partial_credit, 2.0)

    def test_no_history_or_ineligible_action_defers_without_invented_features(self):
        for a in (replace(action(), history=()), replace(action(), eligible=False)):
            with self.subTest(action=a):
                self.assertIsNone(forecast(a, F(4)))
                self.assertEqual(rank(snapshot(a), ConstantPredictor()).ranked, ())

    def test_unobserved_and_invalid_results_are_missing_labels(self):
        for status in ("pending", "unqueried", "invalid"):
            with self.subTest(status=status):
                result = label_return(query_id="query-7", move_id="move-A",
                                      threshold=F(2), response_query_id=None,
                                      response_move_id=None, lower=None, status=status)
                self.assertIsNone(result)

    def test_valid_labels_require_identity_and_strict_lower_bound(self):
        record = dict(query_id="query-7", move_id="move-A", threshold=F(2),
                      response_query_id="query-7", response_move_id="move-A",
                      lower=F(2), status="valid")
        self.assertEqual(label_return(**record), 0)
        self.assertEqual(label_return(**dict(record, lower=F(5, 2))), 1)
        for change in ({"response_query_id": "other-query"},
                       {"response_move_id": "other-MOVE"},
                       {"lower": None}, {"status": "unknown"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                label_return(**dict(record, **change))

    def test_ranking_preserves_snapshot_and_returns_advice_without_authority(self):
        source = snapshot()
        before = copy.deepcopy(source)
        decision = rank(source, ConstantPredictor())
        self.assertEqual(source, before)
        self.assertEqual(decision.view_id, source.view_id)
        self.assertEqual(decision.disposition, "advice")
        self.assertEqual({f.name for f in fields(decision)},
                         {"view_id", "ranked", "disposition"})
        self.assertEqual({f.name for f in fields(decision.ranked[0])},
                         {"move_id", "expected_admissions", "partial_credit", "denominator"})
        self.assertIsInstance(source.actions, tuple)
        self.assertIsInstance(source.actions[0].history, tuple)
        with self.assertRaises(FrozenInstanceError):
            source.now = F(9)
        with self.assertRaises(FrozenInstanceError):
            source.actions[0].q = F(9)

    def test_duplicate_identities_and_nonfinite_probability_fail_visibly(self):
        source = snapshot()
        duplicates = (
            lambda: replace(source, actions=source.actions * 2),
            lambda: replace(source, demands=source.demands * 2),
            lambda: replace(source, demands=(replace(source.demands[0],
                                                     relations=source.demands[0].relations * 2),)),
        )
        for case, construct in enumerate(duplicates):
            with self.subTest(case=case), self.assertRaises(ValueError):
                rank(construct(), ConstantPredictor())
        for probability in (float("nan"), float("inf"), -0.1, 1.1):
            with self.subTest(probability=probability), self.assertRaises(ValueError):
                rank(source, ConstantPredictor(probability))

    def test_float_progress_is_not_accepted_as_an_exact_boundary(self):
        with self.assertRaises(ValueError):
            forecast(replace(action(), q=0.0), F(4))
        with self.assertRaises(ValueError):
            rank(snapshot(relations=(Relation("move-A", 1.0),)))


if __name__ == "__main__":
    unittest.main()
