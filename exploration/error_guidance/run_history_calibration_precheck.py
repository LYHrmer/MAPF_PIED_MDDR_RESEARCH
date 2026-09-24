"""Run the minimal requester-history calibration successor.

Only self-written successor code is compiled. Nine pinned main headers are
copied unmodified into a temporary directory; prior artifacts remain untouched.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

HERE = Path(__file__).resolve().parent
RULE = "73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md"
RULE_SHA = "b64f5b555034655b2676226d051a70c03aab3679d67c00bc334fb588c4811a8a"
BASELINE = (
    "README.md", "RESEARCH_CONTRACT.md", "OPUS_AUDIT.md",
    "precheck.cpp", "run_precheck.py", "precheck_run_20260924_01.json", "source_pins.json",
    "timing_precheck.cpp", "run_timing_precheck.py", "TIMING_PRECHECK.md",
    "timing_run_20260924_01.json",
    "prefix_precheck.cpp", "run_prefix_precheck.py", "PREFIX_PRECHECK.md",
    "prefix_run_20260924_01.json", "prefix_run_20260924_02.json",
    "mismatch_precheck.cpp", "run_mismatch_precheck.py", "MISMATCH_PRECHECK.md",
    "mismatch_run_20260924_01.json",
)


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def run(source_root, output):
    source_root = source_root.resolve()
    report = {
        "started_utc": datetime.now(timezone.utc).isoformat(), "status": "failed_or_incomplete",
        "scope": "requester_duration_calibration_from_delivered_native_END",
        "source_root": str(source_root), "commands": [],
        "AUTH_or_production_lifecycle_verified": False, "full_online_cost_measured": False,
        "general_GROUP_ADMIT_implemented": False, "learning_or_lifelong_throughput_claim": False,
        "research_payload_read": False,
    }
    pins, protected = {}, {}
    try:
        protected = {name: sha(HERE / name) for name in BASELINE}
        pins = json.loads((HERE / "source_pins.json").read_text())
        report.update(
            protected_baseline_sha256=protected, source_header_sha256=pins,
            fixture_sha256=sha(HERE / "history_calibration_precheck.cpp"),
            runner_sha256=sha(Path(__file__)),
            normative_rule={"path": RULE, "sha256": sha(source_root / RULE), "sections": ["4", "5"]},
        )
        def predictor_bytes(path):
            source = path.read_bytes()
            start = source.index(b"R nominal_duration(")
            end = source.index(b"\nclass World {", start)
            return source[start:end]
        frozen = predictor_bytes(HERE / "prefix_precheck.cpp")
        successor = predictor_bytes(HERE / "mismatch_precheck.cpp")
        if frozen != successor:
            raise ValueError("the original public nominal predictor changed")
        report["frozen_predictor_sha256"] = hashlib.sha256(frozen).hexdigest()
        report["frozen_predictor_matches_prefix"] = True
        report["self_written_include_sha256"] = {"mismatch_precheck.cpp": sha(HERE / "mismatch_precheck.cpp")}
        prior_source = (HERE / "prefix_precheck.cpp").read_text()
        block = prior_source[prior_source.index("Prediction predict("):prior_source.index("void prediction_json(")]
        expected = block.replace("Prediction predict(", "Prediction calibrated_predict(").replace(
            "const Opportunity& opportunity) {",
            "const Opportunity& opportunity, const DurationPrior& model) {"
        ).replace("const R duration = nominal_duration(g.length());", "const R duration = model.duration(g.length());")
        calibrated_source = (HERE / "history_calibration_precheck.cpp").read_text()
        actual = calibrated_source[
            calibrated_source.index("Prediction calibrated_predict("):calibrated_source.index("Decision calibrated_choose(")
        ]
        if actual.strip() != expected.strip():
            raise ValueError("calibrated predictor changed more than requester duration input")
        report["calibrated_predictor_only_requester_duration_changed"] = True
        if report["normative_rule"]["sha256"] != RULE_SHA:
            raise ValueError("normative original-prefix contract pin changed")
        identity_argv = ["rtk", "proxy", "git", "-C", str(source_root), "rev-parse", "HEAD"]
        identity = subprocess.run(identity_argv, capture_output=True, text=True, timeout=10)
        report["source_identity_command"] = {
            "argv": identity_argv, "exit_code": identity.returncode,
            "stdout": identity.stdout, "stderr": identity.stderr,
        }
        if identity.returncode:
            raise RuntimeError("source Git identity unavailable")
        report["source_head"] = identity.stdout.strip()
        with tempfile.TemporaryDirectory(prefix="mapf_error_history_calibration_") as directory:
            build = Path(directory)
            for relative, expected in pins.items():
                path = source_root / relative
                if sha(path) != expected:
                    raise ValueError(f"source pin changed: {relative}")
                (build / path.name).write_bytes(path.read_bytes())
            library = source_root / "third_party/flint_host_config"
            sdk = source_root / "third_party/host_sdk/usr"
            binary = build / "error_guidance_history_calibration_precheck"
            compile_command = [
                "rtk", "proxy", "g++-11", "-std=c++14", "-O2", "-Wall", "-Wextra", "-Werror",
                "-pedantic", "-fno-elide-constructors", "-I", str(build),
                "-isystem", str(sdk / "include"), "-isystem", str(library / "src"),
                str(HERE / "history_calibration_precheck.cpp"), "-L", str(library),
                "-L", str(sdk / "lib/x86_64-linux-gnu"), f"-Wl,-rpath,{library}",
                "-lflint", "-lmpfr", "-lgmp", "-o", str(binary),
            ]
            for argv, limit in ((compile_command, 120), (["rtk", "proxy", str(binary)], 60)):
                entry = {"argv": argv, "timeout_seconds": limit}
                report["commands"].append(entry)
                started = time.monotonic()
                try:
                    completed = subprocess.run(argv, capture_output=True, text=True, timeout=limit)
                except subprocess.TimeoutExpired as error:
                    entry.update(timed_out=True, stdout=str(error.stdout or ""), stderr=str(error.stderr or ""))
                    raise
                entry.update(exit_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr,
                             elapsed_seconds=time.monotonic() - started)
                if completed.returncode:
                    raise RuntimeError(f"precheck command exited {completed.returncode}")
                if argv == compile_command:
                    report["binary_sha256"] = sha(binary)
            report["events"] = [json.loads(line) for line in report["commands"][-1]["stdout"].splitlines()]
            if report["events"][-1].get("status") != "passed":
                raise ValueError("native output lacks passing final result")
            if len([e for e in report["events"] if e["event"] == "paired_route_result"]) != 8:
                raise ValueError("native output lacks eight actually executed paired routes")
            report["status"] = "passed"
    except Exception as error:
        report["failure"] = f"{type(error).__name__}: {error}"
    finally:
        # Preserve failed builds/runs too, including all readable after hashes.
        try:
            after = {name: sha(HERE / name) for name in protected}
            headers_after = {relative: sha(source_root / relative) for relative in pins}
            report["protected_baseline_after_sha256"] = after
            report["source_header_after_sha256"] = headers_after
            report["normative_rule_after_sha256"] = sha(source_root / RULE)
            if after != protected or headers_after != pins or report["normative_rule_after_sha256"] != RULE_SHA:
                raise ValueError("protected baseline, source header or normative rule changed during run")
        except Exception as error:
            report["status"] = "failed_or_incomplete"
            report["after_hash_failure"] = f"{type(error).__name__}: {error}"
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        with output.open("x") as stream:
            stream.write(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    if args.output.exists():
        parser.error("output must be new; preserve prior evidence")
    if args.output.resolve().parent != HERE or not args.output.name.startswith("history_calibration_run_"):
        parser.error("output must be history_calibration_run_* in this package")
    report = run(args.source_root, args.output)
    print(json.dumps({
        "status": report["status"], "output": str(args.output),
        "failure": report.get("failure"), "summary": report.get("events", [{}])[-1],
        "commands": [
            {"argv": c["argv"], "exit_code": c.get("exit_code"),
             "timed_out": c.get("timed_out", False), "stderr": c.get("stderr", "")}
            for c in report["commands"]
        ],
    }, indent=2))
    raise SystemExit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
