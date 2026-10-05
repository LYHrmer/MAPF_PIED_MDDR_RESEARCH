"""Original author optimizer invocation plus complete CAS-backed receipts."""
import contextlib
import copy
import io
import json
import math
from pathlib import Path
import signal
import sys
import time
import traceback

from evidence import digest


def finite_json(value):
    if isinstance(value, float) and not math.isfinite(value):
        return dict(nonfinite=repr(value))
    if isinstance(value, dict):
        return {k: finite_json(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [finite_json(v) for v in value]
    return value


def capture_model(model):
    values = {v.name: v.x for v in model.vars}
    finite = all(v is not None and math.isfinite(v) for v in values.values())
    rows = []
    maximum = 0.
    for row in model.constrs:
        expr = row.expr
        terms = {v.name: co for v, co in expr.expr.items()}
        lhs = violation = None
        if all(values[name] is not None and math.isfinite(values[name]) for name in terms):
            lhs = expr.const + sum(co*values[name] for name, co in terms.items())
            violation = max(0., lhs) if expr.sense == "<" else max(0., -lhs) if expr.sense == ">" else abs(lhs)
            maximum = max(maximum, violation)
        rows.append(dict(name=row.name, sense=expr.sense, constant=expr.const, terms=terms, lhs=lhs, violation=violation))
    bound = max((max(0., v.lb-v.x, v.x-v.ub) for v in model.vars), default=0.) if finite else None
    integer = max((abs(v.x-round(v.x)) for v in model.vars if v.var_type in ("B", "I")), default=0.) if finite else None
    payload = finite_json(dict(variables=[dict(name=v.name, type=v.var_type, lb=v.lb, ub=v.ub, value=v.x) for v in model.vars],
        constraints=rows, objective=dict(constant=model.objective.const, terms={v.name: co for v, co in model.objective.expr.items()})))
    record = finite_json(dict(status=model.status.name, objective=model.objective_value, bound=model.objective_bound,
        feasible=model.num_solutions > 0 and finite and maximum < 1e-5 and bound < 1e-5 and integer < 1e-5,
        all_values_finite=finite, max_violation=maximum, max_bound_violation=bound, max_integrality_violation=integer,
        variables=model.num_cols, constraints=model.num_rows, model_sha256=digest(payload)))
    return record, payload


def invoke(simulator):
    code = simulator.author["mip"].Model.optimize.__code__
    captures = []
    def observer(frame, event, arg):
        if frame.f_code is code:
            if event == "call":
                captures.append(dict(model=frame.f_locals["self"], start=time.perf_counter(), cap=frame.f_locals["max_seconds"]))
            elif event == "return":
                captures[-1]["wall"] = time.perf_counter()-captures[-1]["start"]
    def alarm(signum, frame):
        raise TimeoutError("author outer watchdog")
    started = time.perf_counter()
    old_profile = sys.getprofile()
    old_alarm = None
    error = error_trace = None
    stream = io.StringIO()
    try:
        old_alarm = signal.signal(signal.SIGALRM, alarm)
        signal.alarm(simulator.config.outer_solver_seconds)
        with contextlib.redirect_stdout(stream), contextlib.redirect_stderr(stream):
            sys.setprofile(observer)
            simulator.graph.optimize(horizon=simulator.config.horizon)
    except Exception as exc:
        error, error_trace = repr(exc), traceback.format_exc()
    finally:
        sys.setprofile(old_profile)
        signal.alarm(0)
        if old_alarm is not None:
            signal.signal(signal.SIGALRM, old_alarm)
    elapsed = time.perf_counter()-started
    record = dict(status="NO_MODEL", error=error, reference_solver_seconds=0., reference_author_seconds=elapsed,
        objective=None, bound=None, feasible=False, actual_author_calls=len(captures))
    payload = None
    if captures:
        capture = captures[-1]
        try:
            details, payload = capture_model(capture["model"])
            record.update(details, reference_solver_seconds=capture.get("wall", elapsed), author_max_seconds=capture["cap"])
        except Exception as exc:
            # Never erase the original exception when serialization itself fails.
            record.update(feasible=False, payload_capture_error=repr(exc))
            payload = dict(capture_error=repr(exc), traceback=traceback.format_exc())
    return record, payload, dict(stdout=stream.getvalue(), error_traceback=error_trace), elapsed


def solve(simulator, gate):
    from engine import graph_snapshot, adoption_guard, write_json
    simulator._update_predictor()
    before = graph_snapshot(simulator.graph, simulator.config.horizon)
    before_ref = simulator.store.put_graph(before)
    heads = {g.get_uid(): (g.first_head_active, getattr(g, "first_head_inactive", None))
        for groups in simulator.graph.switchable_dep_groups.values() for g in groups}
    semantic = digest(dict(graph=before, horizon=simulator.config.horizon, source=simulator.author["hashes"],
        semantics=simulator.author["semantic_version"], author_max_seconds=60))
    cache = simulator.cache / (semantic + ".json") if simulator.cache else None
    reused = bool(cache and cache.exists())
    wall = 0.
    if reused:
        cached = json.loads(cache.read_text())
        if cached["semantic_key"] != semantic or cached["before_sha256"] != digest(before):
            raise ValueError("R19 cache semantic mismatch")
        if Path(cached["evidence_store"]).resolve() != simulator.store.root.resolve():
            raise ValueError("cache must share its declared evidence store")
        model = copy.deepcopy(cached["model"])
        model_ref, log_ref = cached["model_ref"], cached["author_log_ref"]
        if model_ref is not None:
            if digest(simulator.store.get(model_ref)) != model["model_sha256"]:
                raise ValueError("cached model payload hash mismatch")
        candidate_ref = cached["candidate_ref"]
        candidate = simulator.store.get_graph(candidate_ref)
        if cached["adopted"]:
            simulator._restore_directions(candidate)
        else:
            simulator._restore_directions(before, heads)
        guard = copy.deepcopy(cached["candidate_guard"])
    else:
        model, payload, log, wall = invoke(simulator)
        if payload is not None:
            model["model_sha256"] = digest(payload)
        model_ref = simulator.store.put(payload) if payload is not None else None
        log_ref = simulator.store.put(log)
        candidate = graph_snapshot(simulator.graph, simulator.config.horizon)
        candidate_ref = simulator.store.put_graph(candidate)
        guard = adoption_guard(before, candidate)
        if model.get("error") or not model["feasible"] or not guard["passed"]:
            simulator._restore_directions(before, heads)
    after = graph_snapshot(simulator.graph, simulator.config.horizon)
    adopted = bool(model["feasible"] and not model.get("error") and guard["passed"])
    actual_guard = adoption_guard(before, after)
    if not actual_guard["passed"]:
        simulator._restore_directions(before, heads)
        after = graph_snapshot(simulator.graph, simulator.config.horizon)
        adopted = False
        guard = actual_guard
    after_ref = simulator.store.put_graph(after)
    if not model["feasible"] or model.get("error"):
        simulator.failures.append(dict(time=simulator.now, kind="SOLVER_FAILURE_PARENT_GRAPH_RETAINED", detail=copy.deepcopy(model),
            model_ref=model_ref, before_ref=before_ref, candidate_ref=candidate_ref, after_ref=after_ref,
            cache_reused=reused, semantic_key=semantic))
    elif not guard["passed"]:
        simulator.failures.append(dict(time=simulator.now, kind="ADOPTION_REJECTED_PARENT_GRAPH_RETAINED", detail=guard,
            model_ref=model_ref, candidate_ref=candidate_ref, after_ref=after_ref, cache_reused=reused))
    if cache and not reused:
        # Retain failed attempts too. An identical input reuses the same observed
        # failed result and parent fallback; there is no success-seeking retry.
        write_json(cache, dict(schema="r19-exact-author-cache-v1", semantic_key=semantic,
            before_sha256=digest(before), before_ref=before_ref, candidate_ref=candidate_ref, after_ref=after_ref,
            model=model, model_ref=model_ref, author_log_ref=log_ref, adopted=adopted, candidate_guard=guard,
            evidence_store=str(simulator.store.root.resolve())))
    record = dict(gate_index=gate["gate_index"], time=simulator.now, semantic_key=semantic, cache_reused=reused,
        new_author_calls=0 if reused else model["actual_author_calls"], new_author_wall_seconds=wall,
        new_solver_seconds=0. if reused else model["reference_solver_seconds"], model=model, model_ref=model_ref,
        guard=guard, adopted=adopted, before_sha256=digest(before), after_sha256=digest(after),
        before_ref=before_ref, candidate_ref=candidate_ref, after_ref=after_ref, author_log_ref=log_ref,
        cache_source=str(cache) if cache else None, inherited_reference_outcome=reused,
        prediction_keys=dict(simulator._last_predictions),
        active_commitments=[v["uid"] for v in before["vertices"] if v["status"] == "IN_PROGRESS"])
    simulator.solves.append(record)
    if simulator.output_dir:
        write_json(simulator.output_dir/"solves"/f'{gate["gate_index"]:05d}'/"receipt.json", record)
