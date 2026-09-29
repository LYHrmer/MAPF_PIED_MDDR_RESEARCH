"""Offline recovery: consume public launches only while a cohort choice remains.

Original auditor and failed wrapper receipt remain unchanged; no native execution.
"""
from fractions import Fraction
from math import isqrt


def exact_time(bounds):
    if bounds["lower"] != bounds["upper"]:
        raise ValueError("public launch must have an exact recorded time")
    return Fraction(bounds["lower"], bounds["denominator"])


def sqrt_bounds(value):
    """Exact rational enclosure on a fixed 10^-18 grid, using integer arithmetic."""
    value = Fraction(value)
    denominator = 10 ** 18
    scaled_numerator = value.numerator * denominator * denominator
    root = isqrt(scaled_numerator // value.denominator)
    lower = Fraction(root, denominator)
    upper = lower if root * root * value.denominator == scaled_numerator else Fraction(root + 1, denominator)
    if not lower * lower <= value <= upper * upper:
        raise ValueError("invalid exact square-root enclosure")
    return lower, upper


def candidate_forecast(data, sequence):
    """Prove each logged discrete service using public rational interval propagation."""
    alpha = [Fraction(data["alpha"][side], data["alpha"]["denominator"]) for side in ("lower", "upper")]
    now = Fraction(data["at"])
    opportunities = list(map(Fraction, data["opportunities"]))
    delay = Fraction(1, 4)
    terms, total, all_feasible = [], Fraction(0), True
    for task in data["tasks"]:
        start = [Fraction(task["launched"]) if task["active"] else now] * 2
        feasible = task["non_owner_eligible"]
        if not task["active"]:
            for relation in task["relations"]:
                if not relation["retirable"] or relation["threshold"] is None:
                    feasible = False
                    break
                release = [x + delay for x in sqrt_bounds(3 * Fraction(relation["blocker_length"]))]
                clears = (relation["eligible"] and relation["epsilon"] is not None
                          and Fraction(relation["b"]) - Fraction(relation["epsilon"])
                          > Fraction(relation["threshold"]))
                selected = [opportunities[k] for k, action in enumerate(sequence)
                            if action == relation["action"] and clears]
                start = [max(start[side], min([release[side]] + selected)) for side in (0, 1)]
        arrival = [start[side] + delay * (len(task["lengths"]) - 1)
                   + sum(sqrt_bounds(alpha[side] * Fraction(length))[side] for length in task["lengths"])
                   for side in (0, 1)]
        services = [max(8, -(-value.numerator // value.denominator)) for value in arrival]
        if services[0] != services[1]:
            raise ValueError("public exact alpha enclosure does not certify a unique service slot")
        service = services[0]
        terms.append(dict(task=task["task"], assigned_at=task["assigned_at"],
                          predicted_service_at=str(service), feasible=feasible))
        if feasible:
            total += service - Fraction(task["assigned_at"])
        else:
            all_feasible = False
    return dict(sequence=sequence, terms=terms, feasible=all_feasible, flow=str(total))


def audit_cohort_choices(block, frozen_alpha):
    flow_policy = block[0]["policy"] == "current_cohort_flow_pair"
    launches, queried, decisions = {}, [], 0
    data, candidates, expected_action = None, [], None
    for event in block:
        kind = event["event"]
        if flow_policy and decisions < 2 and kind == "original_move_started":
            launches[event["id"]] = exact_time(event["at"])
        elif kind == "cohort_input":
            if not flow_policy or data is not None or expected_action is not None:
                raise ValueError("invalid cohort decision event order")
            data, candidates = event, []
            if data["alpha"] != frozen_alpha:
                raise ValueError("decision alpha differs from frozen predictor enclosure")
            if Fraction(data["at"]) != (Fraction(5, 2) if decisions == 0 else Fraction(11, 4)):
                raise ValueError("unexpected query opportunity")
            opportunities = [Fraction(5, 2), Fraction(11, 4)] if decisions == 0 else [Fraction(11, 4)]
            if list(map(Fraction, data["opportunities"])) != opportunities:
                raise ValueError("future query opportunity changed")
            if data["eligible_actions"] != [a for a in "ABC" if a not in queried]:
                raise ValueError("candidate actions differ from public query history")
            if [t["task"] for t in data["tasks"]] != ["D1-task1", "D2-task1", "D3-task1"]:
                raise ValueError("future or missing current cohort task")
            for task in data["tasks"]:
                key = task["demand"]
                if key not in ("D1", "D2", "D3") or Fraction(task["assigned_at"]) != 0:
                    raise ValueError("current public assignment differs")
                if list(map(Fraction, task["lengths"])) != [4 if key == "D3" else 6, 1]:
                    raise ValueError("current public route differs")
                if task["active"] != (key in launches):
                    raise ValueError("active state differs from actual public launch events")
                if task["active"] and Fraction(task["launched"]) != launches[key]:
                    raise ValueError("hidden or fabricated launch time")
                if not task["active"] and Fraction(task["launched"]) != 0:
                    raise ValueError("pending task has a launch label")
                required = [] if task["active"] else [a for a in ("C" if key == "D3" else "AB") if a not in queried]
                if [r["action"] for r in task["relations"]] != required:
                    raise ValueError("relations differ from public retirement history")
        elif kind == "cohort_candidate":
            if data is None:
                raise ValueError("candidate lacks a public input")
            expected = candidate_forecast(data, event["sequence"])
            if {k: v for k, v in event.items() if k != "event"} != expected:
                raise ValueError("native forecast disagrees with independent public-input calculation")
            candidates.append(expected)
        elif kind == "cohort_choice":
            if data is None:
                raise ValueError("choice lacks a public input")
            keys = [""] + data["eligible_actions"]
            sequences = ([[a] for a in keys] if len(data["opportunities"]) == 1 else
                         [[a, b] for a in keys for b in keys if not a or a != b])
            if [c["sequence"] for c in candidates] != sequences:
                raise ValueError("candidate set/order differs from declared WAIT/single/pair search")
            feasible = [c for c in candidates if c["feasible"]]
            winner = min(feasible, key=lambda c: (Fraction(c["flow"]), sum(bool(a) for a in c["sequence"])))
            if (event["sequence"] != winner["sequence"] or event["flow"] != winner["flow"]
                    or event["diagnostic_query_count"] != sum(bool(a) for a in winner["sequence"])):
                raise ValueError("cohort objective/tie selection differs")
            expected_action = winner["sequence"][0]
            data = None
            decisions += 1
        elif kind in ("query_selected", "no_query"):
            selected = event["id"] if kind == "query_selected" else ""
            if flow_policy and (expected_action is None or selected != expected_action):
                raise ValueError("executed query differs from selected current-cohort action")
            expected_action = None
            if selected:
                queried.append(selected)
    if data is not None or expected_action is not None or decisions != (2 if flow_policy else 0):
        raise ValueError("incomplete cohort decision audit")
    return decisions
