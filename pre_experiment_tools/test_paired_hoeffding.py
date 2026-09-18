"""Fixed rational math fixtures only; no files, experiment inputs or subprocesses."""

from decimal import Decimal, Inexact, ROUND_FLOOR, Rounded, localcontext
from fractions import Fraction
import unittest

from paired_hoeffding import paired_hoeffding


def _log_bracket(value):
    """Independent exact-rational log bounds from the atanh series and its tail."""
    def series(x):
        z = (x - 1) / (x + 1)
        total = Fraction(0)
        power = z
        for k in range(72):
            total += 2 * power / (2 * k + 1)
            power *= z * z
        remainder = 2 * power / (145 * (1 - z * z))
        return total, total + remainder

    exponent = 0
    while value >= 2:
        value /= 2
        exponent += 1
    lower, upper = series(value)
    two_lower, two_upper = series(Fraction(2))
    return lower + exponent * two_lower, upper + exponent * two_upper


class PairedHoeffdingTests(unittest.TestCase):
    def assert_outward_radius(self, result, weights, bounds, alpha):
        log_lower, log_upper = _log_bracket(2 / alpha)
        coefficient = sum((2 * w * u) ** 2 for w, u in zip(weights, bounds)) / 2
        squared = Fraction(result.radius_upper) ** 2
        # The oracle uses exact fractions and a proved tail, not another sqrt/ln.
        self.assertGreaterEqual(squared, coefficient * log_upper)
        self.assertLess(squared, coefficient * log_lower * Fraction(1001, 1000))

    def test_exact_estimate_and_nonterminating_target_clip(self):
        w = [Fraction(1, 3), Fraction(2, 3)]
        d = [Fraction(1, 7), Fraction(-2, 7)]
        u = [Fraction(2, 7), Fraction(3, 7)]
        alpha = Fraction(1, 20)
        result = paired_hoeffding(w, d, u, alpha=alpha)
        self.assertEqual(result.estimate, Fraction(-1, 7))
        self.assertEqual(result.target_bound, Fraction(8, 21))
        self.assertEqual((result.lower, result.upper), (Fraction(-8, 21), Fraction(8, 21)))
        self.assert_outward_radius(result, w, u, alpha)
        self.assertEqual(result, paired_hoeffding(w[::-1], d[::-1], u[::-1], alpha=alpha))

    def test_outward_nonterminating_conversions_at_several_precisions(self):
        w = [Fraction(1, 3), Fraction(2, 3)]
        u = [Fraction(1, 7), Fraction(2, 11)]
        alpha = Fraction(3, 7)
        for precision in (8, 20, 50):
            with self.subTest(precision=precision):
                result = paired_hoeffding(w, [0, 0], u, alpha=alpha, precision=precision)
                self.assert_outward_radius(result, w, u, alpha)

    def test_unclipped_and_one_sided_clipped_endpoints_are_exact(self):
        w = [Fraction(1, 16)] * 16
        u = [Fraction(1, 3)] * 16
        alpha = Fraction(1, 20)
        centered = paired_hoeffding(w, [0] * 16, u, alpha=alpha)
        radius = Fraction(centered.radius_upper)
        self.assertLess(radius, Fraction(1, 3))
        self.assertEqual((centered.lower, centered.upper), (-radius, radius))
        self.assert_outward_radius(centered, w, u, alpha)
        positive = paired_hoeffding(w, [Fraction(1, 4)] * 16, u, alpha=alpha)
        negative = paired_hoeffding(w, [Fraction(-1, 4)] * 16, u, alpha=alpha)
        self.assertEqual(positive.lower, Fraction(1, 4) - radius)
        self.assertEqual(positive.upper, Fraction(1, 3))
        self.assertEqual((negative.lower, negative.upper), (-positive.upper, -positive.lower))

    def test_zero_support_including_zero_weight_entries(self):
        for w, d, u in [([1], [0], [0]), ([1, 0], [0, 1], [0, 1])]:
            result = paired_hoeffding(w, d, u, alpha=Fraction(1, 20))
            self.assertEqual(result.estimate, 0)
            self.assertEqual(result.target_bound, 0)
            self.assertEqual(result.radius_upper, Decimal(0))
            self.assertEqual((result.lower, result.upper), (Fraction(0), Fraction(0)))

    def test_invalid_dimensions_weights_bounds_and_alpha(self):
        cases = [
            ([], [], [], Fraction(1, 20)),
            ([1], [], [1], Fraction(1, 20)),
            ([1], [0], [], Fraction(1, 20)),
            ([Fraction(1, 2)], [0], [1], Fraction(1, 20)),
            ([-1, 2], [0, 0], [1, 1], Fraction(1, 20)),
            ([1], [0], [-1], Fraction(1, 20)),
            ([1], [2], [1], Fraction(1, 20)),
            ([1], [-2], [1], Fraction(1, 20)),
            ([1, 0], [0, 2], [0, 1], Fraction(1, 20)),
            ([1], [1], [0], Fraction(1, 20)),
            ([1], [0], [1], 0),
            ([1], [0], [1], 1),
            ([1], [0], [1], -1),
        ]
        for w, d, u, alpha in cases:
            with self.subTest(w=w, d=d, u=u, alpha=alpha), self.assertRaises(ValueError):
                paired_hoeffding(w, d, u, alpha=alpha)

    def test_rejects_inexact_or_implicit_input_types_and_bad_precision(self):
        for invalid in (0.5, True, "1/2", Decimal("0.5")):
            for field in ("weights", "differences", "bounds", "alpha"):
                args = dict(weights=[1], differences=[0], bounds=[1], alpha=Fraction(1, 20))
                args[field] = invalid if field == "alpha" else [invalid]
                with self.subTest(field=field, invalid=invalid), self.assertRaises(TypeError):
                    paired_hoeffding(**args)
        for invalid in (True, 1.5):
            with self.assertRaises(TypeError):
                paired_hoeffding([1], [0], [1], alpha=Fraction(1, 20), precision=invalid)
        with self.assertRaises(ValueError):
            paired_hoeffding([1], [0], [1], alpha=Fraction(1, 20), precision=0)

    def test_decimal_context_is_independent_and_not_mutated(self):
        args = ([Fraction(1, 3), Fraction(2, 3)], [0, 0], [Fraction(1, 7)] * 2)
        expected = paired_hoeffding(*args, alpha=Fraction(3, 7))
        with localcontext() as context:
            context.prec = 2
            context.rounding = ROUND_FLOOR
            context.Emin, context.Emax = -1, 1
            context.traps[Inexact] = True
            context.traps[Rounded] = True
            context.clear_flags()
            actual = paired_hoeffding(*args, alpha=Fraction(3, 7))
            self.assertEqual(actual, expected)
            self.assertEqual((context.prec, context.rounding), (2, ROUND_FLOOR))
            self.assertEqual((context.Emin, context.Emax), (-1, 1))
            self.assertTrue(context.traps[Inexact])
            self.assertTrue(context.traps[Rounded])
            self.assertFalse(any(context.flags.values()))


if __name__ == "__main__":
    unittest.main()
