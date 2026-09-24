"""Adversarial synthetic JSON checks; no experiment payloads are read."""

from copy import deepcopy
from dataclasses import FrozenInstanceError
from fractions import Fraction as F
import json
import unittest

from .component_io import UnsupportedNumberDomain, load_snapshot
from .shadow import forecast, rank


def exact(value):
    number = F(value)
    return {"numerator": str(number.numerator), "denominator": str(number.denominator)}


def fixture():
    binding = dict(geometry_version="fixture-geometry", number_encoding="rational",
                   coordinate_frame="fixture-frame", distance_unit="m", move_occurrence="move-A")
    history = [dict(action="move-A", source="source-A", key=f"certificate-{t}",
                    provenance="synthetic fixture", binding=deepcopy(binding),
                    captured=exact(t), delivered=exact(t + 1), lower=exact(t),
                    epsilon=exact(F(1, 4)), cap_at_capture=exact(t + 3)) for t in (1, 2)]
    return dict(
        schema="pie_query_component_snapshot_v1", source_kind="synthetic_component_fixture",
        outer_publication_verified=False, run_id="synthetic-run", snapshot_id="synthetic-snapshot",
        view_id="view-label", now=exact(4), committed_at=exact(3), policy="SRDC",
        generation=3, cursor="", actions=[dict(
            key="move-A", agent="agent-A", source="source-A", profile="profile-A",
            binding=binding, q=exact(2), cap=exact(10), epsilon=exact(F(1, 4)),
            eligible=True, history=history)], demands=[dict(
                key="demand-B", agent="agent-B", requester_action="", weight=1,
                joined=exact(0), other_ready=True, relations=[dict(
                    owner="move-A", action="move-A", retirable=True,
                    kind="RetirableAtCurrentCap", threshold=exact(3))])], receipts=[dict(
                        profile="profile-A", source="source-A", key="receipt-1",
                        provenance="synthetic fixture", epsilon=exact(F(1, 4)),
                        published=exact(0), captured=exact(1), committed=exact(2),
                        delivered=exact(3), charged_work=exact(2))])


def read(obj):
    return load_snapshot(json.dumps(obj))


class ComponentIOTests(unittest.TestCase):
    def test_projection_keeps_exact_values_and_provenance_immutable(self):
        result = read(fixture())
        self.assertEqual((result.run_id, result.snapshot_id, result.generation),
                         ("synthetic-run", "synthetic-snapshot", 3))
        self.assertEqual(result.committed_at, F(3))
        self.assertEqual(result.excluded_actions, ())
        self.assertEqual(result.snapshot.actions[0].epsilon, F(1, 4))
        self.assertEqual(result.raw["source_kind"], "synthetic_component_fixture")
        with self.assertRaises(FrozenInstanceError):
            result.generation = 99
        with self.assertRaises(TypeError):
            result.raw["actions"][0]["history"][0]["source"] = "mutated"
        with self.assertRaises(FrozenInstanceError):
            result.snapshot.actions[0].q = F(9)
        self.assertEqual(rank(result.snapshot).ranked[0].move_id, "move-A")

    def test_all_five_history_binding_fields_and_action_key_are_checked(self):
        for field in fixture()["actions"][0]["binding"]:
            obj = fixture()
            obj["actions"][0]["history"][0]["binding"][field] = "other"
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "binding mismatch"):
                read(obj)
        obj = fixture()
        obj["actions"][0]["binding"]["move_occurrence"] = "other"
        with self.assertRaisesRegex(ValueError, "action key mismatch"):
            read(obj)

    def test_history_is_bound_to_action_but_may_have_an_older_source(self):
        obj = fixture()
        obj["actions"][0]["history"][0]["source"] = "previous-trusted-source"
        result = read(obj)
        self.assertEqual(len(result.snapshot.actions[0].history), 2)
        self.assertEqual(result.raw["actions"][0]["history"][0]["source"], "previous-trusted-source")
        obj["actions"][0]["history"][0]["action"] = "other-MOVE"
        with self.assertRaisesRegex(ValueError, "binding mismatch"):
            read(obj)

    def test_history_chronology_cannot_exceed_committed_snapshot(self):
        for field, value in (("captured", 3), ("delivered", 4)):
            obj = fixture()
            obj["actions"][0]["history"][0][field] = exact(value)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "history chronology"):
                read(obj)
        obj = fixture()
        obj["committed_at"] = exact(5)
        with self.assertRaisesRegex(ValueError, "cannot exceed now"):
            read(obj)

    def test_history_lower_and_historical_cap_must_fit_committed_state(self):
        for field, value in (("lower", 3), ("cap_at_capture", 11), ("cap_at_capture", 0)):
            obj = fixture()
            obj["actions"][0]["history"][0][field] = exact(value)
            with self.subTest(field=field, value=value), self.assertRaisesRegex(ValueError, "current committed"):
                read(obj)

    def test_receipts_must_be_settled_before_snapshot_and_ordered(self):
        for field, value in (("published", 2), ("captured", 3), ("committed", 4), ("delivered", 4)):
            obj = fixture()
            obj["receipts"][0][field] = exact(value)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "settlement chronology"):
                read(obj)

    def test_incompatible_receipts_are_retained_without_pricing(self):
        for field, value in (("source", "other-source"), ("profile", "other-profile"),
                             ("epsilon", exact(F(1, 8))), ("epsilon", None)):
            obj = fixture()
            obj["receipts"][0][field] = value
            result = read(obj)
            with self.subTest(field=field, value=value):
                self.assertEqual(len(result.raw["receipts"]), 1)
                self.assertEqual(result.snapshot.actions[0].receipts, ())
                self.assertEqual(rank(result.snapshot).disposition, "defer_to_original")

    def test_zero_duration_receipt_is_retained_but_does_not_price(self):
        obj = fixture()
        for field in ("published", "captured", "committed", "delivered"):
            obj["receipts"][0][field] = exact(2)
        result = read(obj)
        self.assertEqual(len(result.snapshot.actions[0].receipts), 1)
        self.assertIsNone(forecast(result.snapshot.actions[0], result.snapshot.now))

    def test_missing_precision_excludes_action_without_erasing_owners(self):
        obj = fixture()
        obj["actions"][0]["epsilon"] = None
        result = read(obj)
        self.assertEqual(result.snapshot.actions, ())
        self.assertEqual(result.excluded_actions, (("move-A", "missing_precision_promise"),))
        self.assertEqual(result.snapshot.demands[0].relations[0].owner, "move-A")
        self.assertEqual(result.snapshot.demands[0].relations[0].action, "move-A")
        self.assertEqual(len(result.raw["actions"]), 1)

    def test_multiple_nonquery_owners_remain_distinct_and_in_denominator(self):
        obj = fixture()
        obj["demands"][0]["relations"].extend([
            dict(owner=owner, action="", retirable=False, kind="NonQueryOwner", threshold=None)
            for owner in ("resident-B", "resident-C")])
        result = read(obj)
        relations = result.snapshot.demands[0].relations
        self.assertEqual(tuple(rel.owner for rel in relations), ("move-A", "resident-B", "resident-C"))
        self.assertEqual(tuple(rel.action for rel in relations), ("move-A", "", ""))
        advice = rank(result.snapshot).ranked[0]
        self.assertEqual(advice.expected_admissions, 0)
        self.assertAlmostEqual(advice.partial_credit, 1 / 3)

    def test_retained_endpoint_can_keep_a_threshold(self):
        obj = fixture()
        obj["demands"][0]["relations"][0].update(retirable=False, kind="EndpointRetained")
        result = read(obj)
        self.assertEqual(result.snapshot.demands[0].relations[0].threshold, F(3))
        self.assertEqual(rank(result.snapshot).disposition, "defer_to_original")

    def test_empty_action_does_not_resolve_an_owner_name_as_a_move(self):
        obj = fixture()
        obj["demands"][0]["relations"][0].update(
            action="", retirable=False, kind="NonQueryOwner", threshold=None)
        result = read(obj)
        self.assertEqual(result.snapshot.demands[0].relations[0].owner, "move-A")
        self.assertEqual(rank(result.snapshot).disposition, "defer_to_original")

    def test_nonrational_anywhere_rejects_entire_record_with_field_path(self):
        obj = fixture()
        obj["actions"][0]["epsilon"] = None
        obj["actions"][0]["history"][1]["lower"] = {"unsupported": "non_rational"}
        with self.assertRaisesRegex(UnsupportedNumberDomain, r"\$\.actions\[0\]\.history\[1\]\.lower"):
            read(obj)

    def test_extremely_close_threshold_stays_exact(self):
        obj = fixture()
        threshold = F(2) + F(1, 10 ** 1000)
        obj["demands"][0]["relations"][0]["threshold"] = exact(threshold)
        result = read(obj)
        actual = result.snapshot.demands[0].relations[0].threshold
        self.assertEqual(actual, threshold)
        self.assertGreater(actual, result.snapshot.actions[0].q)
        self.assertEqual(float(actual), float(result.snapshot.actions[0].q))

    def test_noncanonical_rationals_and_float_or_interval_numbers_rejected(self):
        invalid = [dict(numerator="2", denominator="4"), dict(numerator="-0", denominator="1"),
                   dict(numerator="01", denominator="1"), dict(numerator="+1", denominator="1"),
                   dict(numerator="1", denominator="0"), dict(numerator="1", denominator="-2"),
                   dict(numerator=1, denominator="2"), "[0.1,0.2]", 1.0]
        for number in invalid:
            obj = fixture()
            obj["now"] = number
            with self.subTest(number=number), self.assertRaises(ValueError):
                read(obj)

    def test_unknown_fields_rejected_at_every_structural_level(self):
        for location in ("root", "action", "history", "binding", "receipt", "demand", "relation"):
            obj = fixture()
            target = {"root": obj, "action": obj["actions"][0],
                      "history": obj["actions"][0]["history"][0],
                      "binding": obj["actions"][0]["binding"], "receipt": obj["receipts"][0],
                      "demand": obj["demands"][0], "relation": obj["demands"][0]["relations"][0]}[location]
            target["captured_s"] = exact(2)
            with self.subTest(location=location), self.assertRaisesRegex(ValueError, "unknown fields.*captured_s"):
                read(obj)

    def test_duplicate_json_keys_and_nonstandard_constants_rejected(self):
        text = json.dumps(fixture())
        for field in ("schema", "geometry_version", "numerator"):
            needle = json.dumps(field) + ":"
            altered = text.replace(needle, needle + ' "duplicate", ' + needle, 1)
            with self.subTest(field=field), self.assertRaisesRegex(ValueError, "duplicate JSON key"):
                load_snapshot(altered)
        for constant in ("NaN", "Infinity", "-Infinity"):
            with self.subTest(constant=constant), self.assertRaisesRegex(ValueError, "JSON constant"):
                load_snapshot(text.replace('"generation": 3', '"generation": ' + constant))

    def test_unverified_component_cannot_claim_production_or_other_policy(self):
        for field, value in (("outer_publication_verified", True), ("outer_publication_verified", 0),
                             ("source_kind", "AUTH"), ("policy", "RR"),
                             ("schema", "production_snapshot_v1")):
            obj = fixture()
            obj[field] = value
            with self.subTest(field=field, value=value), self.assertRaises(ValueError):
                read(obj)

    def test_duplicate_identity_is_rejected_without_silent_merge(self):
        for location in ("actions", "demands", "receipts", "relations"):
            obj = fixture()
            target = obj["demands"][0]["relations"] if location == "relations" else obj[location]
            target.append(deepcopy(target[0]))
            with self.subTest(location=location), self.assertRaisesRegex(ValueError, "duplicate"):
                read(obj)

    def test_key_strings_do_not_imply_unproven_global_uniqueness(self):
        obj = fixture()
        # The component admission API scopes receipt retention by profile and
        # history retention by capture time, not global string-key uniqueness.
        other = deepcopy(obj["receipts"][0])
        other["profile"] = "other-profile"
        obj["receipts"].append(other)
        obj["actions"][0]["history"][1]["key"] = obj["actions"][0]["history"][0]["key"]
        result = read(obj)
        self.assertEqual(len(result.raw["receipts"]), 2)
        self.assertEqual(len(result.snapshot.actions[0].receipts), 1)
        self.assertEqual(len(result.snapshot.actions[0].history), 2)

    def test_precision_work_cap_and_types_are_validated(self):
        for location, field, value in (("action", "epsilon", exact(0)), ("action", "cap", exact(1)),
                                       ("action", "eligible", 1), ("receipt", "charged_work", exact(0)),
                                       ("receipt", "epsilon", exact(-1)), ("demand", "weight", True)):
            obj = fixture()
            target = {"action": obj["actions"][0], "receipt": obj["receipts"][0],
                      "demand": obj["demands"][0]}[location]
            target[field] = value
            with self.subTest(location=location, field=field), self.assertRaises(ValueError):
                read(obj)

    def test_relation_identity_kind_and_threshold_cannot_invent_queryability(self):
        changes = [dict(owner="different-responsibility"), dict(action="missing-MOVE"),
                   dict(kind="invented"), dict(action=""), dict(retirable=False),
                   dict(threshold=exact(10)), dict(threshold=exact(1)), dict(threshold=None)]
        for fields in changes:
            obj = fixture()
            obj["demands"][0]["relations"][0].update(fields)
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                read(obj)

    def test_requester_and_join_time_belong_to_committed_state(self):
        for fields in (dict(requester_action="missing-MOVE"), dict(requester_action="move-A"),
                       dict(joined=exact(4))):
            obj = fixture()
            obj["demands"][0].update(fields)
            with self.subTest(fields=fields), self.assertRaises(ValueError):
                read(obj)


if __name__ == "__main__":
    unittest.main()
