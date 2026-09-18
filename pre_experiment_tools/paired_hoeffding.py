"""Pure arithmetic for the manuscript's fixed weighted Hoeffding interval.

Only Python's standard library is required. Integer/Fraction inputs, all sums,
the estimate, the target range, and the returned endpoints are exact rationals.
Binary floats and implicit string/Decimal conversions are deliberately excluded.

The radius is rounded OUTWARD: convert the exact positive rational 2/alpha and
sum((2*w*U)**2)/2 using ROUND_CEILING; move the correctly rounded ln result to
next_plus; multiply upward; then move the correctly rounded sqrt to next_plus.
Both functions are increasing on these inputs, so the result bounds the real
radius from above. ln and sqrt use round-to-nearest, not directed rounding;
merely setting ROUND_CEILING is insufficient. Fraction(Decimal) is exact, so
subtracting/adding the radius and clipping against the rational target range
introduce no further rounding. Lower precision may widen the returned interval.

These guarantees rely on the standard Decimal correctly rounded operations:
https://docs.python.org/3/library/decimal.html#decimal.Decimal.ln
https://docs.python.org/3/library/decimal.html#decimal.Decimal.sqrt
https://docs.python.org/3/library/decimal.html#decimal.Decimal.next_plus
Numerical limits raise an arithmetic exception instead of returning a claimed
interval. Explicit contexts avoid depending on or changing the caller's context.

This module does not establish independence, fixed-design eligibility, valid
score provenance, or complete required scores. Its output is an arithmetic
interval, not a certification that a research comparison is inferentially valid.
"""

from dataclasses import dataclass
from decimal import (
    MAX_EMAX, MAX_PREC, MIN_EMIN, ROUND_CEILING, Context, Decimal,
    DivisionByZero, InvalidOperation, Overflow, Underflow,
)
from fractions import Fraction
from typing import Iterable, Union


ExactRational = Union[int, Fraction]


@dataclass(frozen=True)
class HoeffdingInterval:
    """Exact endpoints enclose the ideal interval; radius_upper is an upper bound."""

    estimate: Fraction
    target_bound: Fraction
    radius_upper: Decimal
    lower: Fraction
    upper: Fraction


def _fraction(value: ExactRational, name: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError(f"{name} must be int or Fraction (not float, bool or text)")
    return Fraction(value)


def _decimal_upper(value: Fraction, context: Context) -> Decimal:
    # Decimal(integer) is exact regardless of the precision; only divide rounds.
    return context.divide(
        Decimal(value.numerator, context=context),
        Decimal(value.denominator, context=context),
    )


def paired_hoeffding(
    weights: Iterable[ExactRational],
    differences: Iterable[ExactRational],
    bounds: Iterable[ExactRational],
    *,
    alpha: ExactRational,
    precision: int = 50,
) -> HoeffdingInterval:
    """Compute §4.5 with r = sqrt(log(2/alpha)/2 * sum((2*w*U)**2)).

    The three finite iterables must have equal, nonzero length. Weights must be
    nonnegative and sum to exactly one, bounds must be nonnegative, and every
    absolute difference must be within its bound, including zero-weight entries.
    alpha must be strictly between zero and one. precision is Decimal arithmetic
    precision only; it does not assign any experimental design parameter.

    The ideal interval [estimate-r, estimate+r] is intersected with the known
    target range [-target_bound, target_bound], where target_bound=sum(w*U).
    Our exact rational endpoints enclose that ideal clipped interval and stay
    inside the same target range. Zero weighted support returns exactly [0, 0].
    TypeError/ValueError denote invalid inputs; Decimal arithmetic exceptions
    denote unsupported numerical limits. No input is dropped or renormalized.
    """
    w = tuple(_fraction(v, "weight") for v in weights)
    d = tuple(_fraction(v, "difference") for v in differences)
    u = tuple(_fraction(v, "bound") for v in bounds)
    a = _fraction(alpha, "alpha")
    if not w or len(w) != len(d) or len(w) != len(u):
        raise ValueError("weights, differences and bounds need equal nonzero lengths")
    if any(v < 0 for v in w) or sum(w, Fraction(0)) != 1:
        raise ValueError("weights must be nonnegative and sum to exactly one")
    if any(v < 0 for v in u):
        raise ValueError("bounds must be nonnegative")
    if any(abs(delta) > limit for delta, limit in zip(d, u)):
        raise ValueError("each absolute difference must be within its bound")
    if not 0 < a < 1:
        raise ValueError("alpha must be strictly between zero and one")
    if isinstance(precision, bool) or not isinstance(precision, int):
        raise TypeError("precision must be an integer")
    if not 1 <= precision <= MAX_PREC:
        raise ValueError("precision is outside Decimal's supported range")

    estimate = sum((weight * delta for weight, delta in zip(w, d)), Fraction(0))
    support = tuple(weight * limit for weight, limit in zip(w, u))
    target_bound = sum(support, Fraction(0))
    if target_bound == 0:
        return HoeffdingInterval(estimate, target_bound, Decimal(0), Fraction(0), Fraction(0))

    half_squared_ranges = sum(((2 * v) ** 2 for v in support), Fraction(0)) / 2
    context = Context(
        prec=precision, rounding=ROUND_CEILING, Emin=MIN_EMIN, Emax=MAX_EMAX,
        capitals=1, clamp=0, flags=[],
        traps=[InvalidOperation, DivisionByZero, Overflow, Underflow],
    )
    log_argument_upper = _decimal_upper(2 / a, context)
    log_upper = context.next_plus(context.ln(log_argument_upper))
    radicand_upper = context.multiply(
        log_upper, _decimal_upper(half_squared_ranges, context),
    )
    radius_upper = context.next_plus(context.sqrt(radicand_upper))
    if not radius_upper.is_finite():
        raise ArithmeticError("radius exceeds Decimal's finite representable range")
    radius_rational = Fraction(radius_upper)
    return HoeffdingInterval(
        estimate=estimate,
        target_bound=target_bound,
        radius_upper=radius_upper,
        lower=max(-target_bound, estimate - radius_rational),
        upper=min(target_bound, estimate + radius_rational),
    )
