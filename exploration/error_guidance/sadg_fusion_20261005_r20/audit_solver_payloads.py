#!/usr/bin/env python3
"""Independent Decimal residual reconstruction; no engine/MIP imports or solves."""
import argparse
from collections import Counter
from decimal import Decimal, localcontext
import gzip
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TOLERANCE = Decimal("0.00001")


def load(path):
    return json.loads(Path(path).read_text())


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cas(root, ref):
    expected = Path("objects")/ref["sha256"][:2]/(ref["sha256"]+".json.gz")
    assert Path(ref["path"]) == expected
    raw = gzip.decompress((root/expected).read_bytes())
    assert hashlib.sha256(raw).hexdigest() == ref["sha256"]
    return json.loads(raw)


def number(value):
    if value is None or isinstance(value, dict):
        return None
    result = Decimal(str(value))
    return result if result.is_finite() else None


def recompute(payload):
    variables = payload["variables"]
    names = [v["name"] for v in variables]
    assert len(names) == len(set(names)), "duplicate variable names could alias coefficient/value serialization"
    all_names = set(names)
    row_names = [row["name"] for row in payload["constraints"]]
    for row in payload["constraints"]:
        assert set(row["terms"]) <= all_names, "constraint term references absent variable"
    assert set(payload["objective"]["terms"]) <= all_names, "objective term references absent variable"
    values = {v["name"]: number(v["value"]) for v in variables}
    row_max = bound_max = integral_max = Decimal(0)
    bad_rows = []
    unevaluable = []
    with localcontext() as context:
        context.prec = 60
        for row_index, row in enumerate(payload["constraints"]):
            if any(values[name] is None for name in row["terms"]):
                unevaluable.append(row["name"])
                continue
            lhs = Decimal(str(row["constant"])) + sum(Decimal(str(c))*values[name] for name,c in row["terms"].items())
            sense = row["sense"]
            assert sense in ("<", ">", "=")
            violation = max(Decimal(0), lhs) if sense == "<" else max(Decimal(0), -lhs) if sense == ">" else abs(lhs)
            row_max = max(row_max, violation)
            if violation >= TOLERANCE:
                bad_rows.append(dict(row_index=row_index, name=row["name"], lhs=str(lhs), sense=sense,
                    violation=str(violation), constant=row["constant"], terms=row["terms"]))
        for v in variables:
            x = values[v["name"]]
            if x is None:
                continue
            lo, hi = number(v["lb"]), number(v["ub"])
            bound_max = max(bound_max, Decimal(0), lo-x if lo is not None else Decimal(0), x-hi if hi is not None else Decimal(0))
            if v["type"] in ("B", "I"):
                integral_max = max(integral_max, abs(x-x.to_integral_value()))
        objective = None
        if all(values[name] is not None for name in payload["objective"]["terms"]):
            objective = Decimal(str(payload["objective"]["constant"])) + sum(
                Decimal(str(c))*values[name] for name,c in payload["objective"]["terms"].items())
    return dict(max_row_violation=float(row_max), max_bound_violation=float(bound_max),
        max_integrality_violation=float(integral_max), all_values_present=all(x is not None for x in values.values()),
        serialization_mapping=dict(variable_count=len(names),unique_variable_names=len(all_names),
            all_constraint_and_objective_terms_resolve=True,constraint_count=len(row_names),
            unique_constraint_names=len(set(row_names)),duplicate_constraint_name_count=len(row_names)-len(set(row_names)),
            row_identity="constraint list position; duplicate row labels do not merge rows"),
        unevaluable_rows=unevaluable, rejected_rows=bad_rows,
        recomputed_objective=None if objective is None else str(objective))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes-root", type=Path, default=HERE/"episodes")
    parser.add_argument("--output", type=Path, default=HERE/"solver_failure_review/FAILURE_PAYLOAD_AUDIT.json")
    parser.add_argument("--scope", default="R19 scientific episodes, read-only incremental audit")
    args = parser.parse_args()
    rows, errors, paths, kinds = [], [], [], Counter()
    for path in sorted(args.episodes_root.rglob("episode.json")):
        episode = load(path)
        paths.append(dict(path=str(path), sha256=sha(path)))
        for solve in episode.get("solves", []):
            if solve.get("adopted", False):
                continue
            try:
                root = Path(episode["evidence_store"])
                before = cas(root, solve["before_ref"])
                after = cas(root, solve["after_ref"])
                assert before["full_sha256"] == after["full_sha256"], "failed candidate changed parent graph"
                for part in ("topology", "vertex_state", "group_state"):
                    assert before[part] == after[part], "failed candidate changed graph component"
                    cas(root, before[part])
                result = dict(episode=str(path), gate=solve["gate_index"], semantic_key=solve["semantic_key"],
                    cache_reused=solve["cache_reused"], new_author_calls=solve["new_author_calls"],
                    status=solve["model"]["status"], source_model_sha256=solve["model"].get("model_sha256"),
                    parent_retained=True, model_ref=solve["model_ref"])
                if solve["model_ref"] is not None:
                    assert solve["model_ref"]["sha256"] == solve["model"]["model_sha256"]
                    payload = cas(root, solve["model_ref"])
                    if "variables" in payload:
                        if isinstance(solve["model"].get("variables"),int):
                            assert len(payload["variables"]) == solve["model"]["variables"], "captured variable count mismatch"
                        if isinstance(solve["model"].get("constraints"),int):
                            assert len(payload["constraints"]) == solve["model"]["constraints"], "captured constraint count mismatch"
                        check = recompute(payload)
                        result["independent_decimal"] = check
                        for key, original in (("max_row_violation","max_violation"),("max_bound_violation","max_bound_violation"),
                            ("max_integrality_violation","max_integrality_violation")):
                            old = solve["model"].get(original)
                            if isinstance(old, (int, float)):
                                assert abs(check[key]-old) < 1e-6, f"logged {original} disagrees with decimal model"
                        categories = [key for key in ("max_row_violation","max_bound_violation","max_integrality_violation") if check[key] >= float(TOLERANCE)]
                        if not check["all_values_present"]:categories.append("missing_or_nonfinite_incumbent")
                    else:
                        categories = ["model_payload_capture_error"]
                else:
                    categories = ["no_model_created"]
                if solve["model"].get("error"):categories.append("author_exception")
                if not solve["guard"]["passed"]:categories.append("adoption_guard")
                if not categories:categories.append("status_or_no_incumbent_rejection")
                result["categories"] = categories
                kinds.update(categories)
                rows.append(result)
            except Exception as exc:
                errors.append(dict(episode=str(path), gate=solve["gate_index"], error=repr(exc)))
    report = dict(passed=not errors, scope=args.scope, new_native_solver_calls=0,
        episodes_seen=len(paths), failed_attempt_records=len(rows), unique_failed_inputs=len({r["semantic_key"] for r in rows}),
        actual_author_calls=sum(r["new_author_calls"] for r in rows), cached_failure_records=sum(r["cache_reused"] for r in rows),
        categories=dict(kinds), input_manifest=paths, records=rows, errors=errors, script_sha256=sha(__file__))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False)+"\n")
    print(json.dumps({k:report[k] for k in ("passed","episodes_seen","failed_attempt_records","unique_failed_inputs","categories")},indent=2))
    if errors:raise SystemExit(1)


if __name__ == "__main__":
    main()
