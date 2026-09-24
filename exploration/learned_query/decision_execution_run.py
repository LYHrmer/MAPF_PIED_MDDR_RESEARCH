"""Run the artificial decision/completion check; preserve failures and old pins."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

HERE = Path(__file__).resolve().parent


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def now():
    return datetime.now(timezone.utc).isoformat()


def text(value):
    return value.decode(errors="replace") if isinstance(value, bytes) else value or ""


def run(source_root, output):
    root = source_root.resolve()
    protected_names = ("legal_and_fixture.cpp", "legal_and_precheck.py",
                       "legal_and_sources.json", "legal_and_run_20260924_01.json")
    pins = json.loads((HERE / "legal_and_sources.json").read_text())
    protected = {name: sha(HERE / name) for name in protected_names}
    report = dict(started_utc=now(), status="failed_or_incomplete", commands=[],
                  scope="artificial_decisions_and_original_move_completion",
                  source_root=str(root), source_header_sha256=pins,
                  protected_sha256=protected,
                  fixture_sha256=sha(HERE / "decision_execution_fixture.cpp"),
                  runner_sha256=sha(Path(__file__)), production_AUTH=False,
                  full_paid_cost=False, task_service=False, learning=False)
    try:
        with tempfile.TemporaryDirectory(prefix="mapf_decision_execution_") as directory:
            build = Path(directory)
            for relative, expected in pins.items():
                source = root / relative
                if sha(source) != expected:
                    raise ValueError(f"source pin differs: {relative}")
                (build / source.name).write_bytes(source.read_bytes())
            library = root / "third_party/flint_host_config"
            sdk = root / "third_party/host_sdk/usr"
            binary = build / "decision_execution"
            compile_command = ["rtk", "proxy", "g++-11", "-std=c++14", "-O2",
                "-Wall", "-Wextra", "-Werror", "-pedantic", "-fno-elide-constructors",
                "-I", str(build), "-isystem", str(sdk / "include"), "-isystem",
                str(library / "src"), str(HERE / "decision_execution_fixture.cpp"),
                "-L", str(library), "-L", str(sdk / "lib/x86_64-linux-gnu"),
                f"-Wl,-rpath,{library}", "-lflint", "-lmpfr", "-lgmp", "-o", str(binary)]
            for argv, timeout in ((compile_command, 120), (["rtk", "proxy", str(binary)], 60)):
                command = dict(argv=argv, timeout_seconds=timeout, started_utc=now())
                report["commands"].append(command)
                try:
                    result = subprocess.run(argv, text=True, capture_output=True, timeout=timeout)
                    command.update(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
                except subprocess.TimeoutExpired as error:
                    command.update(timed_out=True, stdout=text(error.stdout), stderr=text(error.stderr))
                    raise
                finally:
                    command["finished_utc"] = now()
                if binary.exists():
                    report["binary_sha256"] = sha(binary)
                if result.returncode:
                    raise RuntimeError(f"command exited {result.returncode}")
            report["events"] = [json.loads(line) for line in report["commands"][-1]["stdout"].splitlines()]
            if report["events"][-1].get("status") != "passed":
                raise ValueError("no passing final summary")
            report["status"] = "passed"
    except Exception as error:
        report["failure"] = f"{type(error).__name__}: {error}"
    finally:
        try:
            after = {name: sha(HERE / name) for name in protected}
            report["protected_after_sha256"] = after
            unchanged = after == protected and all(sha(root / k) == v for k, v in pins.items())
            unchanged = unchanged and sha(HERE / "decision_execution_fixture.cpp") == report["fixture_sha256"]
            unchanged = unchanged and sha(Path(__file__)) == report["runner_sha256"]
            report["all_sources_unchanged"] = unchanged
            if not unchanged:
                report.update(status="failed_or_incomplete", integrity_failure="source changed")
        except Exception as error:
            report.update(status="failed_or_incomplete", integrity_failure=str(error))
        report["finished_utc"] = now()
        # Exclusive output preserves a previous record even in a concurrent race.
        with output.open("x") as stream:
            stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--evidence", required=True, type=Path)
    args = parser.parse_args()
    if args.evidence.exists() or args.evidence.resolve().parent != HERE or not args.evidence.name.startswith("decision_execution_run_"):
        parser.error("evidence must be a new decision_execution_run_* file in this package")
    report = run(args.source_root, args.evidence)
    print(json.dumps({"status": report["status"], "evidence": str(args.evidence),
                      "failure": report.get("failure"),
                      "results": [e for e in report.get("events", []) if e.get("event") in ("policy_result", "summary")]}, indent=2))
    raise SystemExit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
