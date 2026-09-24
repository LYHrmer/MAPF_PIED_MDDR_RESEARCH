"""Compile/run named common-observation timing interventions on pinned headers.

No main source is vendored into this branch. Headers are copied only into a
temporary build directory, unmodified, then removed by TemporaryDirectory.
"""
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


def run(source_root, output):
    source_root = source_root.resolve()
    pins = json.loads((HERE / "source_pins.json").read_text())
    protected = {
        name: sha(HERE / name) for name in (
            "precheck.cpp", "run_precheck.py", "precheck_run_20260924_01.json", "source_pins.json"
        )
    }
    report = {
        "started_utc": datetime.now(timezone.utc).isoformat(), "status": "failed_or_incomplete",
        "scope": "artificial_finite_common_observation_timing", "source_root": str(source_root),
        "protected_baseline_sha256": protected,
        "source_header_sha256": pins, "fixture_sha256": sha(HERE / "timing_precheck.cpp"),
        "runner_sha256": sha(Path(__file__)), "commands": [],
        "AUTH_or_production_lifecycle_verified": False, "full_online_cost_measured": False,
        "learning_or_lifelong_throughput_claim": False, "research_payload_read": False,
    }
    try:
        with tempfile.TemporaryDirectory(prefix="mapf_error_timing_") as directory:
            build = Path(directory)
            for relative, expected in pins.items():
                path = source_root / relative
                if sha(path) != expected:
                    raise ValueError(f"source pin changed: {relative}")
                (build / path.name).write_bytes(path.read_bytes())
            library = source_root / "third_party/flint_host_config"
            sdk = source_root / "third_party/host_sdk/usr"
            binary = build / "error_guidance_timing_precheck"
            compile_command = [
                "rtk", "proxy", "g++-11", "-std=c++14", "-O2", "-Wall", "-Wextra", "-Werror",
                "-pedantic", "-fno-elide-constructors", "-I", str(build),
                "-isystem", str(sdk / "include"), "-isystem", str(library / "src"),
                str(HERE / "timing_precheck.cpp"), "-L", str(library),
                "-L", str(sdk / "lib/x86_64-linux-gnu"), f"-Wl,-rpath,{library}",
                "-lflint", "-lmpfr", "-lgmp", "-o", str(binary),
            ]
            for argv, limit in ((compile_command, 120), (["rtk", "proxy", str(binary)], 60)):
                entry = {"argv": argv, "timeout_seconds": limit}
                report["commands"].append(entry)
                try:
                    completed = subprocess.run(argv, capture_output=True, text=True, timeout=limit)
                except subprocess.TimeoutExpired as error:
                    entry.update(timed_out=True, stdout=str(error.stdout or ""), stderr=str(error.stderr or ""))
                    raise
                entry.update(exit_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
                if completed.returncode:
                    raise RuntimeError(f"precheck command exited {completed.returncode}")
            report["binary_sha256"] = sha(binary)
            report["events"] = [json.loads(line) for line in report["commands"][-1]["stdout"].splitlines()]
            if report["events"][-1].get("status") != "passed":
                raise ValueError("native output lacks passing final result")
            for relative, expected in pins.items():
                if sha(source_root / relative) != expected:
                    raise ValueError(f"source changed during run: {relative}")
            protected_after = {name: sha(HERE / name) for name in protected}
            report["protected_baseline_after_sha256"] = protected_after
            if protected_after != protected:
                raise ValueError("a protected baseline source or receipt changed during timing precheck")
            report["status"] = "passed"
    except Exception as error:
        report["failure"] = f"{type(error).__name__}: {error}"
    finally:
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        output.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be new; preserve prior evidence")
    if args.output.resolve().parent != HERE or not args.output.name.startswith("timing_run_"):
        parser.error("output must be timing_run_* in this package")
    report = run(args.source_root, args.output)
    print(json.dumps(report, indent=2, allow_nan=False))
    raise SystemExit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()

