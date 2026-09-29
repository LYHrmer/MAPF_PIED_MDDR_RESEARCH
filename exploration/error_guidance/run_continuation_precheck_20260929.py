"""Run the preregistered 16-instance, four-plan native continuation experiment."""
import argparse
from datetime import datetime, timezone
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
PROTECTED = ('HISTORY_CALIBRATION_PRECHECK.md', 'MISMATCH_PRECHECK.md', 'OPUS_AUDIT.md', 'PREFIX_PRECHECK.md', 'README.md', 'RESEARCH_CONTRACT.md', 'TIMING_PRECHECK.md', 'history_calibration_precheck.cpp', 'history_calibration_run_20260924_01.json', 'mismatch_precheck.cpp', 'mismatch_run_20260924_01.json', 'precheck.cpp', 'precheck_run_20260924_01.json', 'prefix_precheck.cpp', 'prefix_run_20260924_01.json', 'prefix_run_20260924_02.json', 'run_history_calibration_precheck.py', 'run_mismatch_precheck.py', 'run_precheck.py', 'run_prefix_precheck.py', 'run_timing_precheck.py', 'source_pins.json', 'timing_precheck.cpp', 'timing_run_20260924_01.json')
SOURCES = ("continuation_precheck_20260929.cpp", "continuation_world_20260929.hpp",
           "CONTINUATION_PROTOCOL_20260929.md", "mismatch_precheck.cpp")

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def command(argv, limit):
    row = {"argv": argv, "timeout_seconds": limit}
    started = time.monotonic()
    try:
        result = subprocess.run(argv, text=True, capture_output=True, timeout=limit)
        row.update(exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr)
    except subprocess.TimeoutExpired as exc:
        def decoded(value):
            return value.decode(errors="replace") if isinstance(value, bytes) else value or ""
        row.update(timed_out=True, stdout=decoded(exc.stdout), stderr=decoded(exc.stderr))
    row["elapsed_seconds"] = time.monotonic() - started
    return row

def run(root, output):
    pins = json.loads((HERE / "source_pins.json").read_text())
    protected = {name: sha(HERE / name) for name in PROTECTED}
    report = {"started_utc": datetime.now(timezone.utc).isoformat(), "status": "failed_or_incomplete",
              "data_status": "synthetic_native_mechanism", "source_root": str(root),
              "protected_before": protected, "source_header_pins": pins,
              "sources": {name: sha(HERE / name) for name in SOURCES},
              "runner_sha256": sha(Path(__file__)), "instances": [],
              "scope": "transferable_geometry_evidence_waiting_not_OnlineGGO_or_full_cost",
              "fixed_horizon": 24, "full_online_cost_measured": False,
              "production_AUTH_verified": False}
    try:
        report["source_identity"] = command(["rtk", "proxy", "git", "-C", str(root), "rev-parse", "HEAD"], 10)
        with tempfile.TemporaryDirectory(prefix="mapf_continuation_") as directory:
            build = Path(directory)
            for relative, expected in pins.items():
                path = root / relative
                if sha(path) != expected:
                    raise ValueError(f"pinned header changed: {relative}")
                (build / path.name).write_bytes(path.read_bytes())
            library = root / "third_party/flint_host_config"
            sdk = root / "third_party/host_sdk/usr"
            binary = build / "continuation_precheck"
            argv = ["rtk", "proxy", "g++-11", "-std=c++14", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-pedantic", "-fno-elide-constructors", "-I", str(build),
                    "-isystem", str(sdk / "include"), "-isystem", str(library / "src"),
                    str(HERE / "continuation_precheck_20260929.cpp"), "-L", str(library),
                    "-L", str(sdk / "lib/x86_64-linux-gnu"), f"-Wl,-rpath,{library}",
                    "-lflint", "-lmpfr", "-lgmp", "-o", str(binary)]
            report["compile"] = command(argv, 120)
            if report["compile"].get("exit_code") != 0:
                raise RuntimeError("strict compilation failed")
            report["binary_sha256"] = sha(binary)
            # Protocol fixed table: do not add/remove instances after seeing results.
            for z, eta, opportunity, end in itertools.product((0, 1), (-1, 1), (0, 1), (0, 1)):
                entry = {"error_case": z, "private_eta_offline_label": eta,
                         "opportunity_case": opportunity, "native_END_delivery": bool(end)}
                entry["command"] = command(["rtk", "proxy", str(binary), str(z), str(eta),
                                             str(opportunity), str(end)], 60)
                report["instances"].append(entry)
                try:
                    events = [json.loads(line) for line in entry["command"]["stdout"].splitlines()]
                    entry["events"] = events
                    if entry["command"].get("exit_code") != 0 or events[-1].get("status") != "passed":
                        raise RuntimeError("native instance did not pass")
                    if sum(e["event"] == "candidate_result" for e in events) != 4:
                        raise RuntimeError("four actual candidate results missing")
                    entry["status"] = "passed"
                except Exception as exc:
                    entry["status"] = "failed_or_incomplete"
                    entry["failure"] = f"{type(exc).__name__}: {exc}"
                    raise RuntimeError("native instance failed; preserve this attempt before correction") from exc
            report["status"] = "passed"
    except Exception as exc:
        report["failure"] = f"{type(exc).__name__}: {exc}"
    finally:
        report["protected_after"] = {name: sha(HERE / name) for name in PROTECTED}
        report["source_headers_after"] = {name: sha(root / name) for name in pins}
        report["sources_after"] = {name: sha(HERE / name) for name in SOURCES}
        if (report["protected_after"] != protected or report["source_headers_after"] != pins
                or report["sources_after"] != report["sources"]):
            report["status"] = "failed_or_incomplete"
            report["protection_failure"] = True
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        with output.open("x") as stream:
            json.dump(report, stream, indent=2, allow_nan=False)
            stream.write("\n")
    return report

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists() or output.parent != HERE or not output.name.startswith("continuation_run_"):
        parser.error("output must be a new continuation_run_* file inside this package")
    report = run(args.source_root.resolve(), output)
    print(json.dumps({"status": report["status"], "failure": report.get("failure"), "output": str(output),
                      "compile": {k: v for k, v in report.get("compile", {}).items() if k not in ("stdout", "argv")},
                      "instances": [{"status": row["status"], "seconds": row["command"]["elapsed_seconds"],
                                     "stderr": row["command"]["stderr"],
                                     "summary": row.get("events", [{}])[-1]} for row in report["instances"]]}, indent=2))
    raise SystemExit(0 if report["status"] == "passed" else 1)

if __name__ == "__main__":
    main()
