"""Build an isolated real-header component fixture and check its ML projection.

Only the seven hash-pinned headers are copied. Added getters are const and
restricted to a retained View. The original source tree is never edited.
This runs artificial component inputs, not the production services or world.
"""

import argparse
import difflib
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent

SCHEDULER_GETTERS = """
    // Isolated learning-branch projection: same immutable scheduler root.
    const std::vector<Evidence>* export_history(const std::string& action) const {
        const auto found = state_->histories.find(action);
        return found == state_->histories.end() ? nullptr : found->second.get();
    }
    const Receipt* export_receipt(const std::string& profile) const {
        const auto found = state_->receipts.find(profile);
        return found == state_->receipts.end() ? nullptr : found->second.get();
    }
    const Real& export_committed_at() const { return state_->at; }
    std::uint64_t export_generation() const { return state_->generation; }
"""

VIEW_GETTERS = """
        // References remain owned by THIS View, including after later commits.
        const std::vector<typename Scheduler::Evidence>* export_history(
                const std::string& action) const {
            return get().scheduler.export_history(action);
        }
        const typename Scheduler::Receipt* export_receipt(const std::string& profile) const {
            return get().scheduler.export_receipt(profile);
        }
        const Real& export_committed_at() const { return get().scheduler.export_committed_at(); }
        std::uint64_t export_generation() const { return get().scheduler.export_generation(); }
        pie_query::QueryPolicy export_policy() const { return get().scheduler.policy(); }
"""


def isolated_headers(source_root, destination):
    pins = json.loads((HERE / "component_sources.json").read_text())
    originals = {}
    for relative, expected in pins.items():
        raw = (source_root / relative).read_bytes()
        if hashlib.sha256(raw).hexdigest() != expected:
            raise ValueError(f"source changed; review before rebuilding: {relative}")
        originals[Path(relative).name] = raw.decode("utf-8")
    patches = {
        "pie_query_scheduler.hpp": (
            "    const std::string& round_robin_cursor() const { return state_->cursor; }\n",
            SCHEDULER_GETTERS),
        "pie_position_commit.hpp": (
            "        const std::string& round_robin_cursor() const { return get().scheduler.round_robin_cursor(); }\n",
            VIEW_GETTERS),
    }
    diffs = []
    for name, original in originals.items():
        modified = original
        if name in patches:
            anchor, addition = patches[name]
            if original.count(anchor) != 1:
                raise ValueError(f"ambiguous getter insertion point: {name}")
            modified = original.replace(anchor, anchor + addition, 1)
            diffs.extend(difflib.unified_diff(original.splitlines(True),
                                             modified.splitlines(True),
                                             fromfile=name, tofile=name))
        (destination / name).write_text(modified)
    return pins, hashlib.sha256("".join(diffs).encode()).hexdigest()


def reference_number(value):
    if set(value) != {"numerator", "denominator"}:
        raise ValueError("C++ reference must be rational")
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def check_output(stdout, stderr):
    from .component_io import load_snapshot, UnsupportedNumberDomain
    from .example import synthetic_samples
    from .model import MonotoneLogistic, split_by_run
    from .shadow import forecast, rank

    reference_record = json.loads(stderr)
    reference = reference_record["reference"]
    projections, unsupported = {}, []
    for line in stdout.splitlines():
        raw = json.loads(line)
        key = raw["snapshot_id"]
        if key in projections or any(item["snapshot_id"] == key for item in unsupported):
            raise AssertionError("component snapshot IDs must be unique")
        try:
            projections[key] = load_snapshot(line)
        except UnsupportedNumberDomain as exc:
            unsupported.append({"snapshot_id": key, "reason": str(exc)})
    if len(unsupported) != 1:
        raise AssertionError("fixture must exercise exactly one unsupported algebraic snapshot")
    loaded = projections[reference["snapshot_id"]]
    snapshot = loaded.snapshot
    baseline = rank(snapshot)
    if not baseline.ranked or baseline.ranked[0].move_id != reference["first_action"]:
        raise AssertionError("Python and C++ disagree on the positive-score first action")
    chosen = baseline.ranked[0]
    if {d.key: len(d.relations) for d in snapshot.demands} != reference["owner_counts"]:
        raise AssertionError("projection lost or merged owner responsibilities")
    if {d.key: d.weight for d in snapshot.demands} != reference["weights"]:
        raise AssertionError("projection changed C++ dependency weights")
    unpriced = reference_record["unpriced"]
    if (unpriced["choice_kind"] != "RoundRobin"
            or rank(projections[unpriced["snapshot_id"]].snapshot).disposition
            != "defer_to_original"):
        raise AssertionError("unpriced projection did not preserve original fallback authority")
    action = next(a for a in snapshot.actions if a.move_id == chosen.move_id)
    predicted = forecast(action, snapshot.now)
    if predicted.q_hat != reference_number(reference["predicted_lower"]):
        raise AssertionError("Python and C++ progress lower forecasts differ")
    if chosen.denominator != reference_number(reference["denominator"]):
        raise AssertionError("Python and C++ cost-delay denominators differ")
    for value, name in ((chosen.expected_admissions, "admission"),
                        (chosen.partial_credit, "partial")):
        if not math.isclose(value, float(reference_number(reference[name])),
                            rel_tol=1e-12, abs_tol=1e-12):
            raise AssertionError(f"Python and C++ {name} scores differ")

    # Existing artificial training rows only: no fixture outputs become labels,
    # and no unseen physical truth is used as a feature or training target.
    train, _ = split_by_run(synthetic_samples(), {"toy-holdout"})
    model = MonotoneLogistic.fit(train)
    learned = rank(snapshot, model)
    if not learned.ranked or not all(math.isfinite(row.expected_admissions)
                                     for row in learned.ranked):
        raise AssertionError("exported features did not support finite model inference")
    return {
        "component_assertions": reference_record["component_checks"],
        "supported_snapshots": len(projections),
        "unsupported_snapshots": unsupported,
        "reference_snapshot": reference["snapshot_id"],
        "cpp_python_first_action": chosen.move_id,
        "exact_predicted_lower": str(predicted.q_hat),
        "exact_cost_delay_denominator": str(chosen.denominator),
        "score_comparison": "float projection compared at 1e-12; boundaries remain exact",
        "excluded_actions": loaded.excluded_actions,
        "model_advisory_order": [row.move_id for row in learned.ranked],
        "component_data_used_for_training": False,
    }


def run(source_root):
    source_root = source_root.resolve()
    with tempfile.TemporaryDirectory(prefix="mapf_learning_component_") as directory:
        build = Path(directory)
        pins, patch_sha = isolated_headers(source_root, build)
        library = source_root / "third_party/flint_host_config"
        sdk = source_root / "third_party/host_sdk/usr"
        binary = build / "component_fixture"
        command = [
            "rtk", "proxy", "g++-11", "-std=c++14", "-Wall", "-Wextra", "-Werror",
            "-pedantic", "-fno-elide-constructors", "-I", str(build), "-I", str(HERE),
            "-isystem", str(sdk / "include"), "-isystem", str(library / "src"),
            str(HERE / "component_fixture.cpp"),
            "-L", str(library), "-L", str(sdk / "lib/x86_64-linux-gnu"),
            f"-Wl,-rpath,{library}", "-lflint", "-lmpfr", "-lgmp", "-o", str(binary),
        ]
        subprocess.run(command, check=True, timeout=120)
        result = subprocess.run(["rtk", "proxy", str(binary)], check=True,
                                capture_output=True, text=True, timeout=30)
        checks = check_output(result.stdout, result.stderr)
        # Concurrent source changes must be reported, never mistaken for this
        # check's provenance. Only scratch copies were compiled or patched.
        for relative, expected in pins.items():
            if hashlib.sha256((source_root / relative).read_bytes()).hexdigest() != expected:
                raise ValueError(f"source changed during component check: {relative}")
        return {
            "status": "isolated_component_export_and_model_interface_passed",
            "source_kind": "synthetic_component_fixture",
            "source_header_sha256": pins,
            "const_getter_patch_sha256": patch_sha,
            "checks": checks,
            "outer_publication_verified": False,
            "production_query_linkage": False,
            "b1_accounting_or_representative_data": False,
            "learning_improvement_or_task_throughput_claim": False,
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-root", type=Path, required=True,
                        help="local read-only main source and existing FLINT SDK")
    arguments = parser.parse_args()
    print(json.dumps(run(arguments.source_root), indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
