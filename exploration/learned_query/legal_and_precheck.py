"""Finite native geometry/AND precheck, with source pins and retained run evidence.

Only explicitly listed source headers and the existing FLINT SDK are read.
No model, research payload, original service, AUTH chain, or B1 is run.
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


def run(source_root, evidence):
    source_root = source_root.resolve()
    pins = json.loads((HERE / "legal_and_sources.json").read_text())
    report = {
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "status": "failed_or_incomplete",
        "source_kind": "artificial_native_legal_and_precheck",
        "source_root_read_only": str(source_root),
        "source_header_sha256": pins,
        "fixture_sha256": sha(HERE / "legal_and_fixture.cpp"),
        "runner_sha256": sha(Path(__file__)),
        "commands": [],
        "production_AUTH_or_publication_verified": False,
        "full_fee_chain_or_B1_accounting": False,
        "research_payload_or_model_training": False,
        "original_scheduler_or_learning_improvement_claim": False,
    }
    try:
        with tempfile.TemporaryDirectory(prefix="mapf_legal_and_") as directory:
            build = Path(directory)
            for relative, expected in pins.items():
                path = source_root / relative
                if sha(path) != expected:
                    raise ValueError(f"source pin changed: {relative}")
                (build / path.name).write_bytes(path.read_bytes())
            library = source_root / "third_party/flint_host_config"
            sdk = source_root / "third_party/host_sdk/usr"
            binary = build / "legal_and_fixture"
            command = [
                "rtk", "proxy", "g++-11", "-std=c++14", "-O2", "-Wall", "-Wextra",
                "-Werror", "-pedantic", "-fno-elide-constructors", "-I", str(build),
                "-isystem", str(sdk / "include"), "-isystem", str(library / "src"),
                str(HERE / "legal_and_fixture.cpp"), "-L", str(library),
                "-L", str(sdk / "lib/x86_64-linux-gnu"), f"-Wl,-rpath,{library}",
                "-lflint", "-lmpfr", "-lgmp", "-o", str(binary),
            ]
            for argv, limit in ((command, 120), (["rtk", "proxy", str(binary)], 60)):
                entry = {"argv": argv, "timeout_seconds": limit}
                report["commands"].append(entry)
                completed = subprocess.run(argv, capture_output=True, text=True, timeout=limit)
                entry.update(exit_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
                if completed.returncode:
                    raise RuntimeError(f"native command exited {completed.returncode}")
            report["binary_sha256"] = sha(binary)
            report["result"] = json.loads(report["commands"][-1]["stdout"])
            for relative, expected in pins.items():
                if sha(source_root / relative) != expected:
                    raise ValueError(f"source changed during run: {relative}")
            report["status"] = "passed"
    except Exception as error:
        report["failure"] = f"{type(error).__name__}: {error}"
    finally:
        report["finished_utc"] = datetime.now(timezone.utc).isoformat()
        if evidence:
            evidence.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True,
                        help="new legal_and_* JSON report; failures are retained too")
    args = parser.parse_args()
    if args.evidence.exists():
        parser.error("evidence must be a new path, preserving previous runs")
    if args.evidence.resolve().parent != HERE or not args.evidence.name.startswith("legal_and_"):
        parser.error("evidence must stay in this package as legal_and_*")
    report = run(args.source_root, args.evidence)
    print(json.dumps(report, indent=2, allow_nan=False))
    raise SystemExit(0 if report["status"] == "passed" else 1)


if __name__ == "__main__":
    main()
