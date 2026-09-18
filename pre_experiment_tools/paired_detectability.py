"""Planning arithmetic for §4.5 detectability: what effect can this design resolve?

The manuscript fixes the inference procedure but never sizes it. This module
answers the two planning questions that decide the experiment's scale:

  1. For a design (weights, per-block bounds, alpha), how large must the point
     estimate be before the reported interval can exclude zero at all?
  2. For a target relative effect, how many equal-weight blocks are needed,
     under the manuscript's Hoeffding radius versus an empirical Bernstein
     radius that scales with the observed variance instead of the range?

Two thresholds are reported, because they answer different questions:

  detect: the estimate must exceed the radius r for the lower end to clear zero.
      Necessary, but carries no guarantee -- an estimate below r is simply
      unresolvable, not evidence of a null effect.
  guaranteed: if the true target is at least 2r, then the lower end clears zero
      with probability at least 1 - alpha/2, distribution-free. This follows
      from the one-sided half of the same two-sided bound and is the honest
      planning number: guaranteed detection costs four times the blocks.

`effective_blocks` is the Kish count target_bound**2 / sum((w*U)**2). The radius
depends on the design only through sum((w*U)**2), so an unequal-weight design
behaves exactly like an equal-weight design with this many blocks. It is the
direct measure of what the manuscript's nested equal weighting costs.

Only Python's standard library is required. Rational inputs stay exact; every
returned bound is rounded OUTWARD so that a reported radius is never smaller,
and a reported block count never larger, than the real requirement. Exact
Fraction arithmetic is completed first and converted to Decimal exactly once,
which keeps every directed rounding on the conservative side of a quotient.
Correctly rounded Decimal ln/sqrt use round-to-nearest, so each result is moved
to next_plus; setting ROUND_CEILING alone is insufficient. Numerical limits
raise an arithmetic exception rather than returning a claimed bound.

`_ceiling_context` and `_decimal_upper` duplicate two private helpers of
paired_hoeffding rather than importing them: that module carries completed
verification receipts, and this planning tool must not change its bytes.
`design_radius` reproduces its radius formula exactly, and the accompanying
tests assert the two agree, so the duplication cannot drift silently.

The empirical Bernstein radius is the two-sided Maurer-Pontil (2009) bound for
independent equal-weight blocks; its second term dominates at realistic block
counts, so it reduces the required count by a single-digit factor, not by orders
of magnitude. A betting-style confidence sequence would be tighter and is
deliberately not implemented here. Bernstein results are PLANNING figures for an
equal-weight design; the analysis bound for the actual weighted design must be
derived separately before any interval is reported.

`move_time_lower` supplies the one input `physical_service_bound` cannot compute
for itself: a proven lower bound on a single MOVE. It is derived from the
registered reference control profile rather than assumed, and every one of its
arguments must be bounded on the side its docstring names -- the expression is
decreasing in the acceleration parameters, so an accidentally conservative
acceleration is the unsafe direction there, not the safe one.

This module does not establish independence, fixed-design eligibility, score
provenance, or that any required score exists. It assigns no experimental design
parameter: every quantity is supplied by the caller. Its output sizes an
experiment; it certifies no comparison.
"""

from dataclasses import dataclass
from decimal import (
    MAX_EMAX, MAX_PREC, MIN_EMIN, ROUND_CEILING, ROUND_FLOOR, Context, Decimal,
    DivisionByZero, InvalidOperation, Overflow, Underflow,
)
from fractions import Fraction
from typing import Iterable, Union


ExactRational = Union[int, Fraction]

# Doubling the search past this many blocks means the target is unreachable in
# any plausible design; raise instead of iterating indefinitely.
_MAX_SEARCH_BLOCKS = 2 ** 40


@dataclass(frozen=True)
class DesignSummary:
    """Detectability of one fixed design; every Decimal field is an upper bound."""

    blocks: int
    target_bound: Fraction
    squared_support: Fraction
    effective_blocks: int
    radius_upper: Decimal
    relative_radius_upper: Decimal
    guaranteed_effect_upper: Decimal


@dataclass(frozen=True)
class ServiceBound:
    """Per-block service ceiling; `bound` is the U_b that design_summary consumes."""

    opportunity_pairs: int
    moves_per_agent: int
    services_per_agent: int
    physical_pairs: int
    binding: str
    pairs: int
    bound: Fraction


def _fraction(value: ExactRational, name: str) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError(f"{name} must be int or Fraction (not float, bool or text)")
    return Fraction(value)


def _integer(value: int, name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} must be an integer")
    return value


def _ceiling_context(precision: int) -> Context:
    if isinstance(precision, bool) or not isinstance(precision, int):
        raise TypeError("precision must be an integer")
    if not 1 <= precision <= MAX_PREC:
        raise ValueError("precision is outside Decimal's supported range")
    return Context(
        prec=precision, rounding=ROUND_CEILING, Emin=MIN_EMIN, Emax=MAX_EMAX,
        capitals=1, clamp=0, flags=[],
        traps=[InvalidOperation, DivisionByZero, Overflow, Underflow],
    )


def _decimal_upper(value: Fraction, context: Context) -> Decimal:
    # Decimal(integer) is exact regardless of the precision; only divide rounds.
    return context.divide(
        Decimal(value.numerator, context=context),
        Decimal(value.denominator, context=context),
    )


def _checked_alpha(alpha: ExactRational) -> Fraction:
    a = _fraction(alpha, "alpha")
    if not 0 < a < 1:
        raise ValueError("alpha must be strictly between zero and one")
    return a


def _checked_ratio(value: ExactRational, name: str, *, allow_zero: bool) -> Fraction:
    ratio = _fraction(value, name)
    low_ok = ratio >= 0 if allow_zero else ratio > 0
    # |d_b| <= U_b bounds both the target and the per-block spread by U_b, so a
    # ratio above one describes no reachable design.
    if not (low_ok and ratio <= 1):
        floor_text = "zero" if allow_zero else "strictly positive"
        raise ValueError(f"{name} must be at least {floor_text} and at most one")
    return ratio


def _log_upper(argument: Fraction, context: Context) -> Decimal:
    """Upper bound of log(argument) for argument > 1; ln is increasing."""
    return context.next_plus(context.ln(_decimal_upper(argument, context)))


def _sqrt_upper(radicand: Decimal, context: Context) -> Decimal:
    """Upper bound of sqrt(radicand); sqrt is increasing on nonnegative inputs."""
    return context.next_plus(context.sqrt(radicand))


def _finite(value: Decimal, what: str) -> Decimal:
    if not value.is_finite():
        raise ArithmeticError(f"{what} exceeds Decimal's finite representable range")
    return value


def physical_service_bound(
    *,
    exposure: ExactRational,
    agents: int,
    move_time_lower: ExactRational,
    min_task_moves: int,
    opportunity_pairs: int,
) -> ServiceBound:
    """Tighten U_b by intersecting the opportunity ceiling with a travel ceiling.

    §4.5 sets U_b = Q_max_b/E_b from the opportunity structure alone, so it holds
    even if every agent served a task at every row. Physical travel forbids that:
    each MOVE starts and ends at rest, so an agent completes at most
    floor(E_b/move_time_lower) moves inside the window, hence at most
    1 + floor(moves/min_task_moves) services -- the leading one because §4.3
    grants that a legal initial residency can already serve its assigned head.

    Both ceilings bound Q_a,b almost surely, so their minimum does too, and U_b
    shrinks without weakening the concentration argument. Every step floors, so
    `pairs` is an upper bound on the reachable service count.

    CALLER OBLIGATION: `move_time_lower` must be a LOWER bound on the time of one
    full original MOVE from rest to rest, proved separately from the registered
    control profile and pre-registered before any score exists. The fixed spec
    supplies the analytic machinery for this -- the APPROACH remainder lies in
    [sqrt(2*xi/a_hi), sqrt(2*xi/a_lo)] and the constant-eta subfamily has a
    closed-form first END time -- but that minimisation over |eta| <= delta is a
    derivation, not arithmetic, and is deliberately NOT performed here. Supplying
    a value larger than the true minimum makes U_b too small and INVALIDATES the
    interval, which is worse than a wide one. T_nom bounds a MOVE from above and
    must not be used here.

    `min_task_moves` is the design-level minimum number of MOVEs between two
    consecutive services, at least one. If consecutive services can occur without
    moving, the travel ceiling says nothing and the opportunity ceiling governs.

    `binding` names which ceiling is active, so a caller can see whether supplying
    a travel bound bought anything at all.
    """
    window = _fraction(exposure, "exposure")
    step = _fraction(move_time_lower, "move_time_lower")
    n_agents = _integer(agents, "agents")
    per_task = _integer(min_task_moves, "min_task_moves")
    pairs_cap = _integer(opportunity_pairs, "opportunity_pairs")
    if window <= 0:
        raise ValueError("exposure must be strictly positive")
    if step <= 0:
        raise ValueError("move_time_lower must be strictly positive")
    if n_agents < 1:
        raise ValueError("agents must be at least one")
    if per_task < 1:
        raise ValueError("min_task_moves must be at least one")
    if pairs_cap < 0:
        raise ValueError("opportunity_pairs must be nonnegative")

    # Exact rational floors: a partial MOVE completes no MOVE, and a partial task
    # leg completes no service.
    moves = window / step
    moves_per_agent = moves.numerator // moves.denominator
    services_per_agent = 1 + moves_per_agent // per_task
    physical_pairs = n_agents * services_per_agent

    if physical_pairs < pairs_cap:
        binding, pairs = "travel", physical_pairs
    else:
        binding, pairs = "opportunity", pairs_cap
    return ServiceBound(
        opportunity_pairs=pairs_cap,
        moves_per_agent=moves_per_agent,
        services_per_agent=services_per_agent,
        physical_pairs=physical_pairs,
        binding=binding,
        pairs=pairs,
        bound=Fraction(pairs) / window,
    )


def _floor_context(precision: int) -> Context:
    if isinstance(precision, bool) or not isinstance(precision, int):
        raise TypeError("precision must be an integer")
    if not 1 <= precision <= MAX_PREC:
        raise ValueError("precision is outside Decimal's supported range")
    return Context(
        prec=precision, rounding=ROUND_FLOOR, Emin=MIN_EMIN, Emax=MAX_EMAX,
        capitals=1, clamp=0, flags=[],
        traps=[InvalidOperation, DivisionByZero, Overflow, Underflow],
    )


def _decimal_lower(value: Fraction, context: Context) -> Decimal:
    # Decimal(integer) is exact regardless of the precision; only divide rounds.
    return context.divide(
        Decimal(value.numerator, context=context),
        Decimal(value.denominator, context=context),
    )


def move_time_lower(
    *,
    edge_length_lower: ExactRational,
    a_launch_upper: ExactRational,
    a_hi_upper: ExactRational,
    delta_upper: ExactRational,
    precision: int = 50,
) -> Fraction:
    """Rational lower bound on one full MOVE from rest to rest, for U_b tightening.

    Derived from the registered reference control profile, whose relevant facts
    are: progress is monotone (v_ref >= 0, s' = v_ref); the braking invariant
    v_ref**2 <= 2*a_hi*(C - s) is maintained in every mode; and commanded
    acceleration obeys v_ref' = a_cmd + eta with |eta| <= delta, where LAUNCH
    commands a_launch + delta, APPROACH commands at most -a_lo + delta, BRAKE
    commands -a_hi - delta, and HOLD commands zero. Since 0 < delta < a_lo, the
    largest attainable acceleration in any mode is A := a_launch + 2*delta, so
    v_ref**2 <= 2*A*s from rest. With C = ell the braking invariant gives
    v_ref**2 <= 2*a_hi*(ell - s). Changing the integration variable to s,

        T >= integral_0^ell ds / min(sqrt(2*A*s), sqrt(2*a_hi*(ell - s)))
           = sqrt(2*ell*(1/A + 1/a_hi)).

    A mid-MOVE cap below ell only tightens the invariant and adds HOLD, so the
    C = ell value bounds every case from below. No minimisation over eta is
    performed: the uniform worst-case acceleration is used instead, which is
    monotone and therefore safe to bound directly.

    DIRECTION OF EACH ARGUMENT -- the returned value is only a lower bound if
    every argument is bounded on the stated side. The expression is DECREASING
    in a_launch, a_hi and delta, and INCREASING in ell, hence:

        edge_length_lower   LOWER bound on the shortest original edge length
        a_launch_upper      UPPER bound on a_launch
        a_hi_upper          UPPER bound on a_hi
        delta_upper         UPPER bound on delta

    Supplying a LOWER bound for an acceleration overstates the MOVE time, which
    makes the travel ceiling too small, makes U_b too small, and INVALIDATES the
    reported interval. That is the dangerous direction; a loose bound merely
    widens the interval. The result is rounded DOWN, which is the same safe
    direction: a smaller move time admits more moves and a larger U_b.

    NOT ESTABLISHED HERE: that MOVE boundaries are genuinely rest to rest (the
    profile permits nonzero-speed LAUNCH re-entry inside a MOVE, which does not
    affect the boundaries but is the premise of v_ref(0) = 0); and that any of
    a_launch, a_hi, delta, ell has been bound to a value at all -- they remain
    unassigned model conditions. This function performs arithmetic on supplied
    bounds and registers no design parameter.
    """
    ell = _fraction(edge_length_lower, "edge_length_lower")
    launch = _fraction(a_launch_upper, "a_launch_upper")
    high = _fraction(a_hi_upper, "a_hi_upper")
    delta = _fraction(delta_upper, "delta_upper")
    if ell <= 0:
        raise ValueError("edge_length_lower must be strictly positive")
    if launch <= 0:
        raise ValueError("a_launch_upper must be strictly positive")
    if high <= 0:
        raise ValueError("a_hi_upper must be strictly positive")
    if delta <= 0:
        raise ValueError("delta_upper must be strictly positive")
    # Necessary consequence of the profile's 0 < delta < a_lo < a_hi, not
    # sufficient: these are bounds on different parameters.
    if delta >= high:
        raise ValueError("delta_upper must stay below a_hi_upper")
    context = _floor_context(precision)

    accel = launch + 2 * delta
    radicand = 2 * ell * (1 / accel + 1 / high)
    root = context.next_minus(context.sqrt(_decimal_lower(radicand, context)))
    if not root.is_finite():
        raise ArithmeticError("MOVE time bound left Decimal's representable range")
    bound = Fraction(root)
    if bound <= 0:
        raise ArithmeticError("MOVE time bound underflowed to zero at this precision")
    return bound


def design_summary(
    weights: Iterable[ExactRational],
    bounds: Iterable[ExactRational],
    *,
    alpha: ExactRational,
    precision: int = 50,
) -> DesignSummary:
    """Summarise what a fixed design can resolve, before any score exists.

    `weights` and `bounds` are the manuscript's w_b and U_b: equal, nonzero
    length, nonnegative, with weights summing to exactly one. No differences are
    needed, which is the point -- this is answerable while all results are empty.

    radius_upper reproduces §4.5's r = sqrt(log(2/alpha)/2 * sum((2*w*U)**2)) and
    equals the radius paired_hoeffding returns for the same design.
    relative_radius_upper is that radius as a fraction of target_bound, and is
    directly comparable to a hypothesised relative effect.

    Zero weighted support returns exact zeros: a design that can serve nothing
    resolves nothing. TypeError/ValueError denote invalid inputs.
    """
    w = tuple(_fraction(v, "weight") for v in weights)
    u = tuple(_fraction(v, "bound") for v in bounds)
    a = _checked_alpha(alpha)
    if not w or len(w) != len(u):
        raise ValueError("weights and bounds need equal nonzero lengths")
    if any(v < 0 for v in w) or sum(w, Fraction(0)) != 1:
        raise ValueError("weights must be nonnegative and sum to exactly one")
    if any(v < 0 for v in u):
        raise ValueError("bounds must be nonnegative")
    context = _ceiling_context(precision)

    support = tuple(weight * limit for weight, limit in zip(w, u))
    target_bound = sum(support, Fraction(0))
    squared_support = sum((v ** 2 for v in support), Fraction(0))
    if target_bound == 0:
        return DesignSummary(
            blocks=len(w), target_bound=target_bound, squared_support=squared_support,
            effective_blocks=0, radius_upper=Decimal(0),
            relative_radius_upper=Decimal(0), guaranteed_effect_upper=Decimal(0),
        )

    # Kish count: the radius depends on the design only through squared_support.
    # Floor keeps the reported effective size on the pessimistic side.
    effective = target_bound ** 2 / squared_support
    effective_blocks = effective.numerator // effective.denominator

    half_squared_ranges = sum(((2 * v) ** 2 for v in support), Fraction(0)) / 2
    radicand = context.multiply(
        _log_upper(2 / a, context), _decimal_upper(half_squared_ranges, context),
    )
    radius_upper = _finite(_sqrt_upper(radicand, context), "radius")
    relative_upper = context.divide(
        radius_upper, _decimal_upper(target_bound, context),
    )
    return DesignSummary(
        blocks=len(w),
        target_bound=target_bound,
        squared_support=squared_support,
        effective_blocks=effective_blocks,
        radius_upper=radius_upper,
        relative_radius_upper=_finite(relative_upper, "relative radius"),
        guaranteed_effect_upper=_finite(
            context.multiply(Decimal(2), radius_upper), "guaranteed effect",
        ),
    )


def required_hoeffding_blocks(
    *,
    effect_ratio: ExactRational,
    alpha: ExactRational,
    guaranteed: bool = False,
    precision: int = 50,
) -> int:
    """Smallest equal-weight block count whose Hoeffding radius resolves an effect.

    `effect_ratio` is the hypothesised target as a fraction of sum(w*U), in
    (0, 1]. With equal weights and bounds the radius is U*sqrt(2*log(2/alpha)/B),
    so the returned count is ceil(2*log(2/alpha)/effect_ratio**2), or four times
    that when `guaranteed` asks for the 2r threshold instead of the bare radius.

    The count is rounded up from upward-rounded intermediates, so it is never
    smaller than the real requirement.
    """
    epsilon = _checked_ratio(effect_ratio, "effect_ratio", allow_zero=False)
    a = _checked_alpha(alpha)
    if isinstance(guaranteed, bool) is False:
        raise TypeError("guaranteed must be a bool")
    context = _ceiling_context(precision)

    coefficient = 8 if guaranteed else 2
    # 1/epsilon**2 enters as a multiplicand, so rounding it up keeps the product
    # an upper bound; rounding a denominator up would understate the count.
    scaled = context.multiply(
        context.multiply(Decimal(coefficient), _log_upper(2 / a, context)),
        _decimal_upper(1 / epsilon ** 2, context),
    )
    blocks = _finite(scaled, "required block count").to_integral_value(ROUND_CEILING)
    return max(1, int(blocks))


def bernstein_relative_radius(
    *,
    blocks: int,
    variance_ratio: ExactRational,
    alpha: ExactRational,
    precision: int = 50,
) -> Decimal:
    """Upper bound of the equal-weight empirical Bernstein radius, relative to U.

    Two-sided Maurer-Pontil (2009) for `blocks` independent blocks whose paired
    differences lie in [-U, U]:

        r/U <= variance_ratio*sqrt(2*L/B) + 14*L/(3*(B-1)),    L = log(4/alpha)

    `variance_ratio` is the pilot standard deviation of d_b as a fraction of U,
    in [0, 1]; U itself cancels, so the result is scale free. `blocks` must be at
    least two. The second term dominates at realistic block counts.

    This is a planning figure for an equal-weight design. It is not the analysis
    bound for the manuscript's nested weighting, which must be derived before any
    interval is reported.
    """
    n = _integer(blocks, "blocks")
    if n < 2:
        raise ValueError("blocks must be at least two")
    rho = _checked_ratio(variance_ratio, "variance_ratio", allow_zero=True)
    a = _checked_alpha(alpha)
    context = _ceiling_context(precision)

    log_upper = _log_upper(4 / a, context)
    variance_term = context.multiply(
        _decimal_upper(rho ** 2 * 2 / n, context), log_upper,
    )
    range_term = context.multiply(
        _decimal_upper(Fraction(14, 3 * (n - 1)), context), log_upper,
    )
    total = context.add(_sqrt_upper(variance_term, context), range_term)
    return _finite(total, "Bernstein radius")


def required_bernstein_blocks(
    *,
    effect_ratio: ExactRational,
    variance_ratio: ExactRational,
    alpha: ExactRational,
    guaranteed: bool = False,
    precision: int = 50,
) -> int:
    """Smallest equal-weight block count whose Bernstein radius resolves an effect.

    Same arguments as `required_hoeffding_blocks` plus the pilot
    `variance_ratio`, so the two counts are directly comparable and quantify what
    switching the inference procedure is worth for this design.

    The relative radius strictly decreases in `blocks`, so a doubling search
    followed by a bisection finds the smallest sufficient count. Each candidate
    is tested against an upward-rounded radius compared exactly as a Fraction,
    so the returned count always satisfies the requirement.
    """
    epsilon = _checked_ratio(effect_ratio, "effect_ratio", allow_zero=False)
    rho = _checked_ratio(variance_ratio, "variance_ratio", allow_zero=True)
    a = _checked_alpha(alpha)
    if isinstance(guaranteed, bool) is False:
        raise TypeError("guaranteed must be a bool")

    target = epsilon / 2 if guaranteed else epsilon

    def resolves(candidate: int) -> bool:
        radius = bernstein_relative_radius(
            blocks=candidate, variance_ratio=rho, alpha=a, precision=precision,
        )
        # Fraction(Decimal) is exact, so this comparison adds no rounding.
        return Fraction(radius) <= target

    low = 2
    # The bisection needs a `low` that does not resolve. Two blocks in fact never
    # do -- the range term 14*log(4/alpha)/3 exceeds six for every valid alpha --
    # but the invariant is checked rather than assumed.
    if resolves(low):
        return low
    high = 4
    while not resolves(high):
        low = high
        high *= 2
        if high > _MAX_SEARCH_BLOCKS:
            raise ArithmeticError("no plausible block count resolves this effect")
    while high - low > 1:
        middle = (low + high) // 2
        if resolves(middle):
            high = middle
        else:
            low = middle
    return high
