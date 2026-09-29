"""Run the six predeclared paired objective instances, without overwriting evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "objective_task_fixture.cpp"
from objective_task_audit import audit_cohort_choices
TRAINING_SCOPE = "historical_AR1_OLS_five_episode_transitions"
INSTANCE_NAMES = [
    "alternating_next_slow", "alternating_next_fast", "stable_fast",
    "unpredictable_slow_shock", "native_quote_alternating_next_slow",
    "native_quote_alternating_next_fast",
]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def digest_text(text):
    return hashlib.sha256(text.encode()).hexdigest()


def command(argv, timeout):
    entry = dict(argv=argv, timeout_seconds=timeout, started_utc=now(),
                 exit_code=None, stdout="", stderr="", timed_out=False)
    try:
        result = subprocess.run(argv, text=True, capture_output=True, timeout=timeout)
        entry.update(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except subprocess.TimeoutExpired as error:
        decode = lambda value: value.decode(errors="replace") if isinstance(value, bytes) else value or ""
        entry.update(timed_out=True, stdout=decode(error.stdout), stderr=decode(error.stderr))
    except OSError as error:
        entry["launch_error"] = f"{type(error).__name__}: {error}"
    entry["finished_utc"] = now()
    return entry


def seconds(interval):
    if interval["lower"] != interval["upper"]:
        raise ValueError("service/assignment expected exact rational grid time")
    return interval["lower"] / interval["denominator"]


def validate_events(events, index):
    expected_name = INSTANCE_NAMES[index]
    if events[0].get("id") != expected_name:
        raise ValueError("instance identity mismatch")
    histories = [e for e in events if e["event"] == "historical_native_END_delivered"]
    if len(histories) != 6 or len({e["run_id"] for e in histories}) != 6:
        raise ValueError("six unique training episodes required")
    if any(e["received"]["upper"] / e["received"]["denominator"] >= 32 for e in histories):
        raise ValueError("training history not available at held-out origin")
    models = [e for e in events if e["event"] == "frozen_predictor"]
    if len(models) != 6 or not all(e["frozen_before_test"] for e in models):
        raise ValueError("predictors were not frozen")
    first_test = next(k for k, e in enumerate(events) if e["event"] == "policy_begin")
    if any(e["event"] == "frozen_predictor" for e in events[first_test:]):
        raise ValueError("model was fit again after seeing test execution")
    results, block = [], None
    for event in events:
        kind = event["event"]
        if kind == "policy_begin":
            if block is not None:
                raise ValueError("unfinished prior test episode")
            if event["run_id"] in {e["run_id"] for e in histories}:
                raise ValueError("test episode in training")
            block = [event]
        elif block is not None:
            block.append(event)
            if kind == "policy_result":
                services = [e for e in block if e["event"] == "task_service"]
                launches = [e for e in block if e["event"] == "original_move_started"]
                labels = [e for e in block if e["event"] == "offline_duration_evaluation"]
                query_ids = [e["id"] for e in block if e["event"] == "query_selected"]
                curve = [sum(seconds(e["at"]) <= t for e in services)
                         for t in event["service_times"]]
                flow = sum(seconds(e["at"]) - seconds(e["assigned_at"]) for e in services)
                if (len(services) != 9 or len({e["task"] for e in services}) != 9
                        or len(launches) != 12 or len(labels) != 12
                        or any(e["feeds_online_model"] for e in labels)
                        or curve != event["completed_tasks"] or query_ids != event["queries"]
                        or flow != event["task_flow_sum"]
                        or max(seconds(e["at"]) for e in services) != event["last_task_service"]):
                    raise ValueError("independent task/decision/event accounting disagrees")
                compact = dict(event)
                first = [e for e in services if e["task"].endswith("-task1")]
                compact["current_cohort_service_times"] = {e["task"]: seconds(e["at"]) for e in first}
                compact["current_cohort_flow"] = sum(seconds(e["at"])-seconds(e["assigned_at"]) for e in first)
                compact["audited_cohort_decisions"] = audit_cohort_choices(block, next((m["alpha"] for m in models if m["predictor"]==event["predictor"]), None))
                compact["alpha_error_bounds"] = labels[0]["absolute_alpha_error"]
                compact["integrated_unfinished_tasks_8_to_16"] = sum(9 - n for n in curve)
                compact["native_quote_diagnostic"] = index >= 4
                results.append(compact)
                block = None
    expected_runs = 17 if index >= 4 else 16
    if block is not None or len(results) != expected_runs:
        raise ValueError("missing declared test episodes")
    common_count = sum(e["event"] == "common_initial_POSITION" for e in events)
    if common_count != expected_runs * (6 if index >= 4 else 0):
        raise ValueError("shared observation count mismatch")
    summary = events[-1]
    if (summary.get("event") != "summary" or summary.get("status") != "passed"
            or summary.get("training_scope") != TRAINING_SCOPE):
        raise ValueError("missing successful training/task summary")
    for flag in ("production_AUTH", "full_paid_cost", "independent_learning_advantage_claim",
                 "lifelong_performance_claim"):
        if summary.get(flag) is not False:
            raise ValueError(f"claim boundary changed: {flag}")
    return dict(instance=expected_name, results=results, checks=summary["checks"],
                history_fingerprint=digest_text(json.dumps(histories, sort_keys=True)),
                predictor_fingerprint=digest_text(json.dumps(models, sort_keys=True)))


def run(source_root, output):
    root = source_root.resolve()
    report = dict(started_utc=now(), status="failed_or_incomplete", commands=[], instances=[],
                  source_root=str(root), predeclared_instances=INSTANCE_NAMES,
                  production_AUTH=False, full_paid_cost=False,
                  independent_learning_advantage_claim=False, lifelong_performance_claim=False,
                  training_scope=TRAINING_SCOPE, test_unit="complete held-out native task episode",
                  quote_source="declared artificial admitted native diagnostic receipt; not production COST")
    protected, pins = {}, {}
    with output.open("x", encoding="utf-8") as stream:
        try:
            # Every older package file is protected; new successor files and
            # documentation are not silently substituted for historical inputs.
            protected = {p.name: sha(p) for p in HERE.iterdir() if p.is_file()
                         and (not p.name.startswith("objective_")
                              or (p.name.startswith("objective_task_run_") and p.resolve() != output.resolve()))
                         and p.name not in ("README.md", "OBJECTIVE_TASK_MODEL.md", "OBJECTIVE_TASK_CONTRACT.md")}
            pins = json.loads((HERE / "legal_and_sources.json").read_text())
            if len(pins) != 9:
                raise ValueError("expected nine pinned component headers")
            report.update(protected_sha256=protected, source_header_sha256=pins,
                          fixture_sha256=sha(FIXTURE), runner_sha256=sha(Path(__file__)),
                          fixture_source=FIXTURE.read_text(), runner_source=Path(__file__).read_text())
            old = (HERE / "temporal_task_fixture.cpp").read_text()
            new = FIXTURE.read_text()
            begin, end = "unsigned completion_value(", "struct Leg {"
            frozen_old = old[old.index(begin):old.index(end)]
            frozen_new = new[new.index(begin):new.index(begin)+len(frozen_old)]
            if frozen_old != frozen_new:
                raise ValueError("completion predictor/decision function changed")
            report["frozen_completion_decider_sha256"] = digest_text(frozen_new)
            model_begin, model_end = "struct DeliveredDuration {", "void task_comparison("
            if old[old.index(model_begin):old.index(model_end)] != new[new.index(model_begin):new.index(model_end)]:
                raise ValueError("historical data or frozen predictors changed")
            report["contract_sha256"] = sha(HERE / "OBJECTIVE_TASK_CONTRACT.md")
            report["auditor_sha256"] = sha(HERE / "objective_task_audit.py")
            report["auditor_source"] = (HERE / "objective_task_audit.py").read_text()
            with tempfile.TemporaryDirectory(prefix="mapf_objective_task_") as directory:
                build = Path(directory)
                for relative, expected in pins.items():
                    source = root / relative
                    if Path(relative).is_absolute() or ".." in Path(relative).parts or sha(source) != expected:
                        raise ValueError(f"source pin differs: {relative}")
                    (build / source.name).write_bytes(source.read_bytes())
                library = root / "third_party/flint_host_config"
                sdk = root / "third_party/host_sdk/usr"
                binary = build / "objective_task"
                compile_argv = ["rtk", "proxy", "g++-11", "-std=c++14", "-O2", "-Wall", "-Wextra",
                                "-Werror", "-pedantic", "-fno-elide-constructors", "-I", str(build),
                                "-isystem", str(sdk / "include"), "-isystem", str(library / "src"),
                                str(FIXTURE), "-L", str(library), "-L", str(sdk / "lib/x86_64-linux-gnu"),
                                f"-Wl,-rpath,{library}", "-lflint", "-lmpfr", "-lgmp", "-o", str(binary)]
                compilation = command(compile_argv, 120)
                report["commands"].append(compilation)
                if compilation["exit_code"] != 0:
                    raise RuntimeError("strict compilation failed")
                report["binary_sha256"] = sha(binary)
                failures = []
                for index, name in enumerate(INSTANCE_NAMES):
                    result = command(["rtk", "proxy", str(binary), str(index)], 60)
                    result["instance"] = name
                    report["commands"].append(result)
                    try:
                        if result["exit_code"] != 0:
                            raise RuntimeError(f"native exit {result['exit_code']}")
                        events = [json.loads(line) for line in result["stdout"].splitlines() if line.strip()]
                        report["instances"].append(validate_events(events, index))
                    except Exception as error:
                        failures.append(f"{name}: {type(error).__name__}: {error}")
                if failures:
                    report["instance_failures"] = failures
                    raise RuntimeError("one or more declared instances failed")
                stable, shock = report["instances"][2:4]
                if (stable["history_fingerprint"] != shock["history_fingerprint"]
                        or stable["predictor_fingerprint"] != shock["predictor_fingerprint"]):
                    raise ValueError("no-signal pair received different model information")
                report["identical_history_no_signal_pair_verified"] = True
                old_receipt = json.loads((HERE / "temporal_task_run_20260929_03.json").read_text())
                for previous, current in zip(old_receipt["instances"], report["instances"]):
                    for prior in previous["results"]:
                        matches = [x for x in current["results"] if (x["policy"],x["predictor"]) == (prior["policy"],prior["predictor"])]
                        if len(matches)!=1 or any(matches[0][k]!=v for k,v in prior.items() if k!="run_id"):
                            raise ValueError("old objective/baseline behavior differs from historical receipt")
                report["all_62_old_episodes_reproduced"] = True
                report["status"] = "passed"
        except Exception as error:
            report["failure"] = f"{type(error).__name__}: {error}"
        finally:
            after = {name: sha(HERE / name) for name in protected}
            headers_after = {relative: sha(root / relative) for relative in pins}
            report.update(protected_after_sha256=after, source_header_after_sha256=headers_after)
            report["all_sources_unchanged"] = (after == protected and headers_after == pins
                and report.get("fixture_sha256") == sha(FIXTURE)
                and report.get("runner_sha256") == sha(Path(__file__))
                and report.get("contract_sha256") == sha(HERE / "OBJECTIVE_TASK_CONTRACT.md")
                and report.get("auditor_sha256") == sha(HERE / "objective_task_audit.py"))
            if not report["all_sources_unchanged"]:
                report.update(status="failed_or_incomplete", integrity_failure="source changed")
            report["finished_utc"] = now()
            stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    output = args.evidence
    if (output.exists() or output.is_symlink() or output.resolve().parent != HERE
            or not output.name.startswith("objective_task_run_") or output.suffix != ".json"):
        parser.error("evidence must be a new objective_task_run_*.json file in this package")
    report = run(args.source_root, output)
    print(json.dumps({"status": report["status"], "evidence": str(output),
                      "failure": report.get("failure"), "instance_failures": report.get("instance_failures"),
                      "instances": [{"instance": x["instance"], "checks": x["checks"],
                                     "test_episodes": len(x["results"])} for x in report["instances"]]}, indent=2))
    raise SystemExit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
