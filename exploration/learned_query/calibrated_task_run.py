"""Run native historical-duration calibration and scalar regression; preserve all prior evidence."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent
FIXTURE = HERE / "calibrated_task_fixture.cpp"
TRAINING_SCOPE = "exact_one_parameter_regression_on_native_historical_END"
PROTECTED_NAMES = (
    "legal_and_fixture.cpp", "legal_and_precheck.py", "legal_and_sources.json",
    "legal_and_run_20260924_01.json", "decision_execution_fixture.cpp",
    "decision_execution_run.py", "decision_execution_run_20260924_01.json",
    "task_continuation_fixture.cpp", "task_continuation_run.py",
    "task_continuation_run_20260924_01.json",
    "task_continuation_run_20260924_02.json",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def output_text(value):
    return value.decode(errors="replace") if isinstance(value, bytes) else value or ""


def run(source_root, output):
    root = source_root.resolve()
    pins = {}
    protected = {}
    report = dict(
        started_utc=now(), status="failed_or_incomplete", commands=[],
        scope="artificial_task_service_with_historical_duration_regression", source_root=str(root),
        source_header_sha256=pins, protected_sha256=protected,
        production_AUTH=False, full_paid_cost=False, learning=None,
        training_scope=TRAINING_SCOPE, independent_learning_advantage_claim=False,
        lifelong_performance_claim=False, finite_task_service=False,
        finite_task_service_scope="service conditions observed in this finite native fixture only",
    )
    # Reserve the output before compilation, including against concurrent runs.
    # Input/pin failures below still produce a failure receipt in this new file.
    with output.open("x", encoding="utf-8") as stream:
        try:
            for name in PROTECTED_NAMES:
                protected[name] = sha(HERE / name)
            report["fixture_sha256"] = sha(FIXTURE)
            report["runner_sha256"] = sha(Path(__file__))
            loaded = json.loads((HERE / "legal_and_sources.json").read_text(encoding="utf-8"))
            if not isinstance(loaded, dict) or len(loaded) != 9:
                raise ValueError("expected the nine original source header pins")
            for relative, expected in loaded.items():
                path = Path(relative)
                if (path.is_absolute() or ".." in path.parts or path.suffix != ".hpp"
                        or not isinstance(expected, str) or len(expected) != 64
                        or any(c not in "0123456789abcdef" for c in expected)):
                    raise ValueError(f"invalid source pin: {relative}")
            if len({Path(relative).name for relative in loaded}) != len(loaded):
                raise ValueError("pinned headers have conflicting build names")
            pins.update(loaded)
            with tempfile.TemporaryDirectory(prefix="mapf_calibrated_task_") as directory:
                build = Path(directory)
                for relative, expected in pins.items():
                    source = root / relative
                    source_bytes = source.read_bytes()
                    if hashlib.sha256(source_bytes).hexdigest() != expected:
                        raise ValueError(f"source pin differs: {relative}")
                    (build / source.name).write_bytes(source_bytes)
                library = root / "third_party/flint_host_config"
                sdk = root / "third_party/host_sdk/usr"
                binary = build / "calibrated_task"
                compile_command = [
                    "rtk", "proxy", "g++-11", "-std=c++14", "-O2", "-Wall",
                    "-Wextra", "-Werror", "-pedantic", "-fno-elide-constructors",
                    "-I", str(build), "-isystem", str(sdk / "include"),
                    "-isystem", str(library / "src"), str(FIXTURE),
                    "-L", str(library), "-L", str(sdk / "lib/x86_64-linux-gnu"),
                    f"-Wl,-rpath,{library}", "-lflint", "-lmpfr", "-lgmp",
                    "-o", str(binary),
                ]
                for argv, timeout in (
                    (compile_command, 120), (["rtk", "proxy", str(binary)], 60)
                ):
                    command = dict(
                        argv=argv, timeout_seconds=timeout, started_utc=now(),
                        exit_code=None, stdout="", stderr="", timed_out=False,
                    )
                    report["commands"].append(command)
                    try:
                        result = subprocess.run(
                            argv, text=True, capture_output=True, timeout=timeout,
                        )
                        command.update(
                            exit_code=result.returncode, stdout=result.stdout,
                            stderr=result.stderr,
                        )
                    except subprocess.TimeoutExpired as error:
                        command.update(
                            timed_out=True, stdout=output_text(error.stdout),
                            stderr=output_text(error.stderr),
                        )
                        raise
                    except OSError as error:
                        command["launch_error"] = f"{type(error).__name__}: {error}"
                        raise
                    finally:
                        command["finished_utc"] = now()
                        if binary.exists():
                            report["binary_sha256"] = sha(binary)
                    if result.returncode:
                        raise RuntimeError(f"command exited {result.returncode}")
                events = []
                report["events"] = events
                for line in report["commands"][-1]["stdout"].splitlines():
                    if not line.strip():
                        continue
                    event = json.loads(line)
                    if not isinstance(event, dict):
                        raise ValueError("JSONL event must be an object")
                    events.append(event)
                if (not events or events[-1].get("event") != "summary"
                        or events[-1].get("status") != "passed"):
                    raise ValueError("no passing final summary")
                summary = events[-1]
                if summary.get("learning") is not True:
                    raise ValueError("passing summary does not confirm the fitted regression")
                actual_scope = summary.get("training_scope", summary.get("learning_scope"))
                if actual_scope != TRAINING_SCOPE:
                    raise ValueError("summary has an unexpected training scope")
                for flag in ("production_AUTH", "full_paid_cost", "lifelong_performance_claim",
                             "independent_learning_advantage_claim"):
                    if summary.get(flag) is not False:
                        raise ValueError(f"summary does not preserve the finite claim boundary: {flag}")
                report["learning"] = True
                report["training_scope"] = actual_scope
                report["finite_task_service"] = summary.get("finite_task_service") is True
                report["status"] = "passed"
        except Exception as error:
            report["failure"] = f"{type(error).__name__}: {error}"
        finally:
            integrity_errors = []
            after = {}
            for name in PROTECTED_NAMES:
                try:
                    after[name] = sha(HERE / name)
                except Exception as error:
                    integrity_errors.append(f"{name}: {type(error).__name__}: {error}")
            report["protected_after_sha256"] = after
            headers_after = {}
            for relative in pins:
                try:
                    headers_after[relative] = sha(root / relative)
                except Exception as error:
                    integrity_errors.append(f"{relative}: {type(error).__name__}: {error}")
            report["source_header_after_sha256"] = headers_after
            for field, path in (("fixture", FIXTURE), ("runner", Path(__file__))):
                try:
                    report[field + "_after_sha256"] = sha(path)
                except Exception as error:
                    integrity_errors.append(f"{field}: {type(error).__name__}: {error}")
            unchanged = (
                not integrity_errors and len(protected) == len(PROTECTED_NAMES)
                and after == protected and len(pins) == 9 and headers_after == pins
                and report.get("fixture_after_sha256") == report.get("fixture_sha256")
                and report.get("runner_after_sha256") == report.get("runner_sha256")
            )
            report["all_sources_unchanged"] = unchanged
            if not unchanged:
                report.update(status="failed_or_incomplete", integrity_failure="source missing or changed")
            if integrity_errors:
                report["integrity_errors"] = integrity_errors
            if report["status"] != "passed":
                report["finite_task_service"] = False
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
            or not output.name.startswith("calibrated_task_run_") or output.suffix != ".json"):
        parser.error("evidence must be a new calibrated_task_run_*.json file in this package")
    report = run(args.source_root, output)
    print(json.dumps({
        "status": report["status"], "evidence": str(output),
        "failure": report.get("failure"),
        "results": [event for event in report.get("events", [])
                    if event.get("event") in ("fit_result", "policy_result", "summary")],
    }, indent=2))
    raise SystemExit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
