"""Fixed rational fixtures and independent oracles; no files, inputs or subprocesses."""

from decimal import Decimal
from fractions import Fraction
import unittest

from paired_detectability import (
    bernstein_relative_radius, design_summary, move_time_lower,
    physical_service_bound, required_bernstein_blocks, required_hoeffding_blocks,
)
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


def _equal_design(blocks, bound=1):
    """Weights and bounds for `blocks` equally weighted blocks of one bound."""
    return [Fraction(1, blocks)] * blocks, [Fraction(bound)] * blocks


class DesignSummaryTests(unittest.TestCase):
    def assert_relative_radius(self, value, blocks, alpha):
        """The relative radius must enclose sqrt(2*log(2/alpha)/blocks)."""
        log_lower, log_upper = _log_bracket(2 / alpha)
        squared = Fraction(value) ** 2
        # The oracle uses exact fractions and a proved tail, not another sqrt/ln.
        self.assertGreaterEqual(squared, 2 * log_upper / blocks)
        self.assertLess(squared, 2 * log_lower / blocks * Fraction(1001, 1000))

    def test_radius_matches_the_manuscript_tool_bit_for_bit(self):
        w = [Fraction(1, 3), Fraction(2, 3)]
        u = [Fraction(2, 7), Fraction(3, 7)]
        alpha = Fraction(1, 20)
        summary = design_summary(w, u, alpha=alpha)
        reference = paired_hoeffding(w, [0, 0], u, alpha=alpha)
        # Guards the duplicated formula against silent drift from its sibling.
        self.assertEqual(summary.radius_upper, reference.radius_upper)
        self.assertEqual(summary.target_bound, reference.target_bound)

    def test_equal_weights_give_the_nominal_effective_count(self):
        for blocks in (2, 37, 400):
            with self.subTest(blocks=blocks):
                w, u = _equal_design(blocks)
                summary = design_summary(w, u, alpha=Fraction(1, 20))
                self.assertEqual(summary.blocks, blocks)
                self.assertEqual(summary.effective_blocks, blocks)
                self.assertEqual(summary.target_bound, 1)

    def test_relative_radius_is_scale_free_and_encloses_the_oracle(self):
        alpha = Fraction(1, 20)
        for bound in (1, Fraction(3, 8), 250):
            with self.subTest(bound=bound):
                w, u = _equal_design(64, bound)
                summary = design_summary(w, u, alpha=alpha)
                self.assert_relative_radius(summary.relative_radius_upper, 64, alpha)

    def test_unequal_weighting_costs_effective_blocks(self):
        # Four categories at equal weight, but one holds a single block and
        # another holds sixteen: the Kish count falls well below sixteen.
        weights = [Fraction(1, 4)] + [Fraction(1, 64)] * 16 + [Fraction(1, 8)] * 2
        weights += [Fraction(1, 4) - sum(weights[-2:], Fraction(0))]
        weights += [Fraction(1) - sum(weights, Fraction(0))]
        bounds = [Fraction(1)] * len(weights)
        summary = design_summary(weights, bounds, alpha=Fraction(1, 20))
        self.assertEqual(sum(weights, Fraction(0)), 1)
        self.assertLess(summary.effective_blocks, summary.blocks)
        self.assertGreaterEqual(summary.effective_blocks, 1)

    def test_guaranteed_effect_is_twice_the_radius(self):
        w, u = _equal_design(50)
        summary = design_summary(w, u, alpha=Fraction(1, 20))
        # Fraction(Decimal) is exact; comparing Decimals would re-round the
        # doubling at the default 28-digit context instead of the module's.
        self.assertEqual(
            Fraction(summary.guaranteed_effect_upper),
            2 * Fraction(summary.radius_upper),
        )

    def test_zero_support_resolves_nothing(self):
        w, u = _equal_design(5, 0)
        summary = design_summary(w, u, alpha=Fraction(1, 20))
        self.assertEqual(summary.target_bound, 0)
        self.assertEqual(summary.effective_blocks, 0)
        self.assertEqual(summary.radius_upper, Decimal(0))
        self.assertEqual(summary.guaranteed_effect_upper, Decimal(0))

    def test_rejects_invalid_designs(self):
        good_w, good_u = _equal_design(3)
        with self.assertRaises(ValueError):
            design_summary([], [], alpha=Fraction(1, 20))
        with self.assertRaises(ValueError):
            design_summary(good_w, good_u[:2], alpha=Fraction(1, 20))
        with self.assertRaises(ValueError):
            design_summary([Fraction(1, 2), Fraction(1, 3)], [1, 1], alpha=Fraction(1, 20))
        with self.assertRaises(ValueError):
            design_summary(good_w, [1, 1, -1], alpha=Fraction(1, 20))
        with self.assertRaises(ValueError):
            design_summary(good_w, good_u, alpha=1)
        with self.assertRaises(TypeError):
            design_summary(good_w, good_u, alpha=0.05)


class RequiredHoeffdingBlocksTests(unittest.TestCase):
    def test_five_percent_effect_needs_the_stated_counts(self):
        alpha = Fraction(1, 20)
        effect = Fraction(1, 20)
        self.assertEqual(required_hoeffding_blocks(effect_ratio=effect, alpha=alpha), 2952)
        self.assertEqual(
            required_hoeffding_blocks(effect_ratio=effect, alpha=alpha, guaranteed=True),
            11805,
        )

    def test_returned_count_is_sufficient_and_one_fewer_is_not(self):
        alpha = Fraction(1, 20)
        for effect in (Fraction(1, 5), Fraction(1, 10), Fraction(1, 8)):
            with self.subTest(effect=effect):
                blocks = required_hoeffding_blocks(effect_ratio=effect, alpha=alpha)
                w, u = _equal_design(blocks)
                self.assertLessEqual(
                    Fraction(design_summary(w, u, alpha=alpha).relative_radius_upper),
                    effect,
                )
                w, u = _equal_design(blocks - 1)
                self.assertGreater(
                    Fraction(design_summary(w, u, alpha=alpha).relative_radius_upper),
                    effect,
                )

    def test_guaranteed_count_halves_the_radius(self):
        alpha = Fraction(1, 20)
        effect = Fraction(1, 5)
        blocks = required_hoeffding_blocks(
            effect_ratio=effect, alpha=alpha, guaranteed=True,
        )
        w, u = _equal_design(blocks)
        self.assertLessEqual(
            Fraction(design_summary(w, u, alpha=alpha).relative_radius_upper), effect / 2,
        )

    def test_rejects_invalid_targets(self):
        with self.assertRaises(ValueError):
            required_hoeffding_blocks(effect_ratio=0, alpha=Fraction(1, 20))
        with self.assertRaises(ValueError):
            required_hoeffding_blocks(effect_ratio=Fraction(3, 2), alpha=Fraction(1, 20))
        with self.assertRaises(TypeError):
            required_hoeffding_blocks(effect_ratio=Fraction(1, 20), alpha=Fraction(1, 20), precision=True)


class BernsteinRadiusTests(unittest.TestCase):
    def test_zero_variance_leaves_only_the_range_term(self):
        alpha = Fraction(1, 20)
        for blocks in (2, 19, 5000):
            with self.subTest(blocks=blocks):
                value = bernstein_relative_radius(
                    blocks=blocks, variance_ratio=0, alpha=alpha,
                )
                log_lower, log_upper = _log_bracket(4 / alpha)
                exact = Fraction(14, 3 * (blocks - 1))
                self.assertGreaterEqual(Fraction(value), exact * log_upper)
                self.assertLess(
                    Fraction(value), exact * log_lower * Fraction(1001, 1000),
                )

    def test_radius_strictly_decreases_in_blocks(self):
        alpha = Fraction(1, 20)
        previous = None
        for blocks in (2, 5, 40, 300, 2000, 20000):
            value = bernstein_relative_radius(
                blocks=blocks, variance_ratio=Fraction(1, 10), alpha=alpha,
            )
            if previous is not None:
                self.assertLess(value, previous)
            previous = value

    def test_beats_hoeffding_once_the_variance_is_small(self):
        alpha = Fraction(1, 20)
        blocks = 3000
        w, u = _equal_design(blocks)
        hoeffding = Fraction(design_summary(w, u, alpha=alpha).relative_radius_upper)
        bernstein = Fraction(bernstein_relative_radius(
            blocks=blocks, variance_ratio=Fraction(1, 10), alpha=alpha,
        ))
        self.assertLess(bernstein, hoeffding)

    def test_rejects_invalid_inputs(self):
        with self.assertRaises(ValueError):
            bernstein_relative_radius(blocks=1, variance_ratio=0, alpha=Fraction(1, 20))
        with self.assertRaises(ValueError):
            bernstein_relative_radius(
                blocks=10, variance_ratio=Fraction(3, 2), alpha=Fraction(1, 20),
            )
        with self.assertRaises(TypeError):
            bernstein_relative_radius(blocks=True, variance_ratio=0, alpha=Fraction(1, 20))


class RequiredBernsteinBlocksTests(unittest.TestCase):
    def test_returned_count_is_sufficient_and_one_fewer_is_not(self):
        alpha = Fraction(1, 20)
        rho = Fraction(1, 10)
        for effect in (Fraction(1, 5), Fraction(1, 20), Fraction(1, 50)):
            with self.subTest(effect=effect):
                blocks = required_bernstein_blocks(
                    effect_ratio=effect, variance_ratio=rho, alpha=alpha,
                )
                self.assertGreaterEqual(blocks, 2)
                self.assertLessEqual(
                    Fraction(bernstein_relative_radius(
                        blocks=blocks, variance_ratio=rho, alpha=alpha,
                    )),
                    effect,
                )
                if blocks > 2:
                    self.assertGreater(
                        Fraction(bernstein_relative_radius(
                            blocks=blocks - 1, variance_ratio=rho, alpha=alpha,
                        )),
                        effect,
                    )

    def test_guaranteed_count_halves_the_radius(self):
        alpha = Fraction(1, 20)
        rho = Fraction(1, 10)
        effect = Fraction(1, 20)
        blocks = required_bernstein_blocks(
            effect_ratio=effect, variance_ratio=rho, alpha=alpha, guaranteed=True,
        )
        self.assertLessEqual(
            Fraction(bernstein_relative_radius(
                blocks=blocks, variance_ratio=rho, alpha=alpha,
            )),
            effect / 2,
        )

    def test_two_blocks_never_resolve_a_reachable_effect(self):
        """The range term 14*log(4/alpha)/3 exceeds 6.4 at every valid alpha.

        No effect_ratio can exceed one, so the two-block floor is never
        sufficient. This is why the Bernstein bound saves a single-digit factor
        rather than orders of magnitude: its range term, not its variance term,
        governs realistic block counts.
        """
        for alpha in (Fraction(1, 2), Fraction(1, 20), Fraction(1, 1000)):
            with self.subTest(alpha=alpha):
                floor_radius = bernstein_relative_radius(
                    blocks=2, variance_ratio=0, alpha=alpha,
                )
                self.assertGreater(Fraction(floor_radius), 6)
                self.assertGreater(
                    required_bernstein_blocks(
                        effect_ratio=1, variance_ratio=0, alpha=alpha,
                    ),
                    2,
                )

    def test_larger_variance_never_needs_fewer_blocks(self):
        alpha = Fraction(1, 20)
        effect = Fraction(1, 20)
        counts = [
            required_bernstein_blocks(
                effect_ratio=effect, variance_ratio=Fraction(k, 10), alpha=alpha,
            )
            for k in (0, 1, 5, 10)
        ]
        self.assertEqual(counts, sorted(counts))


class PhysicalServiceBoundTests(unittest.TestCase):
    def test_travel_ceiling_binds_and_reports_itself(self):
        # 20 agents, window 100, one MOVE takes at least 7, three MOVEs per task:
        # 14 moves -> 1 + 4 = 5 services each -> 100 pairs, below the 900 rows.
        result = physical_service_bound(
            exposure=100, agents=20, move_time_lower=7,
            min_task_moves=3, opportunity_pairs=900,
        )
        self.assertEqual(result.moves_per_agent, 14)
        self.assertEqual(result.services_per_agent, 5)
        self.assertEqual(result.physical_pairs, 100)
        self.assertEqual(result.binding, "travel")
        self.assertEqual(result.pairs, 100)
        self.assertEqual(result.bound, Fraction(1, 1))

    def test_opportunity_ceiling_still_binds_when_travel_is_loose(self):
        result = physical_service_bound(
            exposure=100, agents=20, move_time_lower=Fraction(1, 10),
            min_task_moves=1, opportunity_pairs=40,
        )
        self.assertEqual(result.binding, "opportunity")
        self.assertEqual(result.pairs, 40)
        self.assertEqual(result.bound, Fraction(40, 100))

    def test_initial_residency_keeps_one_service_without_any_move(self):
        # A window too short for even one MOVE must still allow the resident head.
        result = physical_service_bound(
            exposure=3, agents=8, move_time_lower=5,
            min_task_moves=2, opportunity_pairs=1000,
        )
        self.assertEqual(result.moves_per_agent, 0)
        self.assertEqual(result.services_per_agent, 1)
        self.assertEqual(result.physical_pairs, 8)

    def test_partial_moves_and_partial_legs_are_floored(self):
        result = physical_service_bound(
            exposure=Fraction(59, 2), agents=1, move_time_lower=Fraction(5, 2),
            min_task_moves=4, opportunity_pairs=10 ** 6,
        )
        # 29.5/2.5 = 11.8 -> 11 moves; 11//4 = 2 legs; plus the resident head.
        self.assertEqual(result.moves_per_agent, 11)
        self.assertEqual(result.services_per_agent, 3)

    def test_never_exceeds_either_ceiling(self):
        for step in (Fraction(1, 3), 2, 11, 500):
            with self.subTest(step=step):
                result = physical_service_bound(
                    exposure=250, agents=6, move_time_lower=step,
                    min_task_moves=2, opportunity_pairs=77,
                )
                self.assertLessEqual(result.pairs, result.opportunity_pairs)
                self.assertLessEqual(result.pairs, result.physical_pairs)

    def test_slower_moves_never_raise_the_ceiling(self):
        previous = None
        for step in (1, 2, 5, 9, 40, 300):
            result = physical_service_bound(
                exposure=600, agents=4, move_time_lower=step,
                min_task_moves=3, opportunity_pairs=10 ** 9,
            )
            if previous is not None:
                self.assertLessEqual(result.pairs, previous)
            previous = result.pairs

    def test_tightening_the_bound_shrinks_the_required_block_count(self):
        alpha = Fraction(1, 20)
        loose = physical_service_bound(
            exposure=100, agents=20, move_time_lower=Fraction(1, 1000),
            min_task_moves=1, opportunity_pairs=900,
        )
        tight = physical_service_bound(
            exposure=100, agents=20, move_time_lower=7,
            min_task_moves=3, opportunity_pairs=900,
        )
        self.assertEqual(loose.binding, "opportunity")
        self.assertEqual(tight.binding, "travel")
        self.assertLess(tight.bound, loose.bound)
        # A fixed absolute effect becomes a larger fraction of a smaller bound,
        # so the same design resolves it with fewer blocks.
        effect = Fraction(1, 10)
        blocks = [
            required_hoeffding_blocks(
                effect_ratio=effect / b.bound, alpha=alpha,
            )
            for b in (loose, tight)
        ]
        self.assertLess(blocks[1], blocks[0])

    def test_rejects_invalid_inputs(self):
        base = dict(
            exposure=100, agents=5, move_time_lower=2,
            min_task_moves=1, opportunity_pairs=10,
        )
        for field, value in (
            ("exposure", 0), ("move_time_lower", 0), ("agents", 0),
            ("min_task_moves", 0), ("opportunity_pairs", -1),
        ):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    physical_service_bound(**{**base, field: value})
        with self.assertRaises(TypeError):
            physical_service_bound(**{**base, "exposure": 100.0})
        with self.assertRaises(TypeError):
            physical_service_bound(**{**base, "agents": True})


class MoveTimeLowerTests(unittest.TestCase):
    def radicand(self, ell, launch, high, delta):
        """The exact rational whose square root the bound must stay below."""
        return 2 * Fraction(ell) * (1 / (Fraction(launch) + 2 * Fraction(delta))
                                    + 1 / Fraction(high))

    def test_square_never_exceeds_the_exact_radicand(self):
        # The only correctness property that matters: the returned rational must
        # square to at most the exact radicand, so it cannot overstate the time.
        cases = [
            (1, 1, 1, Fraction(1, 10)),
            (Fraction(1, 3), 2, 5, Fraction(1, 4)),
            (17, Fraction(3, 7), Fraction(9, 2), Fraction(1, 100)),
            (Fraction(10 ** 6), 1000, 1000, 1),
        ]
        for ell, launch, high, delta in cases:
            with self.subTest(ell=ell, launch=launch):
                bound = move_time_lower(
                    edge_length_lower=ell, a_launch_upper=launch,
                    a_hi_upper=high, delta_upper=delta,
                )
                exact = self.radicand(ell, launch, high, delta)
                self.assertLessEqual(bound ** 2, exact)
                # Tight enough to be useful, not merely valid.
                self.assertGreater(bound ** 2, exact * Fraction(10 ** 40 - 1, 10 ** 40))

    def test_an_exact_square_still_rounds_strictly_down(self):
        # ell=1/4, A=1, a_hi=1 gives radicand exactly one; next_minus must fire.
        bound = move_time_lower(
            edge_length_lower=Fraction(1, 4), a_launch_upper=Fraction(4, 5),
            a_hi_upper=1, delta_upper=Fraction(1, 10),
        )
        self.assertEqual(self.radicand(Fraction(1, 4), Fraction(4, 5), 1, Fraction(1, 10)), 1)
        self.assertLess(bound, 1)
        self.assertGreater(bound, Fraction(10 ** 40 - 1, 10 ** 40))

    def test_faster_actuation_never_raises_the_bound(self):
        # Decreasing in every acceleration parameter, increasing in length.
        base = dict(
            edge_length_lower=4, a_launch_upper=2, a_hi_upper=3,
            delta_upper=Fraction(1, 5),
        )
        reference = move_time_lower(**base)
        for field in ("a_launch_upper", "a_hi_upper", "delta_upper"):
            with self.subTest(field=field):
                faster = move_time_lower(**{**base, field: base[field] * 2})
                self.assertLess(faster, reference)
        self.assertGreater(
            move_time_lower(**{**base, "edge_length_lower": 8}), reference,
        )

    def test_a_looser_acceleration_bound_stays_a_valid_lower_bound(self):
        # Overstating the acceleration is the SAFE direction: it lowers the
        # reported time, which can only admit more moves and widen U_b.
        truth = dict(
            edge_length_lower=1, a_launch_upper=1, a_hi_upper=1,
            delta_upper=Fraction(1, 20),
        )
        loose = move_time_lower(**{**truth, "a_launch_upper": 10, "a_hi_upper": 10})
        self.assertLess(loose, move_time_lower(**truth))
        self.assertLessEqual(loose ** 2, self.radicand(1, 10, 10, Fraction(1, 20)))

    def test_feeding_the_bound_into_the_service_ceiling_tightens_u_b(self):
        move = move_time_lower(
            edge_length_lower=1, a_launch_upper=1, a_hi_upper=1,
            delta_upper=Fraction(1, 10),
        )
        tightened = physical_service_bound(
            exposure=100, agents=20, move_time_lower=move,
            min_task_moves=3, opportunity_pairs=900,
        )
        self.assertEqual(tightened.binding, "travel")
        # The opportunity ceiling alone would allow every agent a service per row.
        self.assertLess(tightened.bound, Fraction(900, 100))
        # A tighter U_b needs strictly fewer blocks for the same absolute effect.
        alpha = Fraction(1, 20)
        effect = Fraction(1, 20)
        self.assertLess(
            required_hoeffding_blocks(effect_ratio=effect / tightened.bound, alpha=alpha),
            required_hoeffding_blocks(
                effect_ratio=effect / Fraction(900, 100), alpha=alpha,
            ),
        )

    def test_rejects_invalid_inputs(self):
        base = dict(
            edge_length_lower=1, a_launch_upper=1, a_hi_upper=2,
            delta_upper=Fraction(1, 2),
        )
        for field in ("edge_length_lower", "a_launch_upper", "a_hi_upper", "delta_upper"):
            with self.subTest(field=field):
                with self.assertRaises(ValueError):
                    move_time_lower(**{**base, field: 0})
                with self.assertRaises(ValueError):
                    move_time_lower(**{**base, field: -1})
        # delta must stay under a_hi, per 0 < delta < a_lo < a_hi.
        with self.assertRaises(ValueError):
            move_time_lower(**{**base, "delta_upper": 2})
        with self.assertRaises(TypeError):
            move_time_lower(**{**base, "edge_length_lower": 1.0})
        with self.assertRaises(TypeError):
            move_time_lower(**{**base, "a_hi_upper": True})


if __name__ == "__main__":
    unittest.main()
