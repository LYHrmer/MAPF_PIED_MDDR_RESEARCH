"""Execute pinned DyMAB reward helpers on artificial values, never MAPF tasks.

The upstream BasicLNS translation unit and header are compiled unchanged.
Only graph/search dependencies are inert stubs that throw if constructed.
The LNS initializer and adaptive-bandit initialization block are extracted
verbatim. A separately named counterfactual changes only argument binding.
No overlay is installed in ADDRESS or in the upstream source cache.
"""
from __future__ import annotations

import argparse
from collections import deque
from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parent
PIN_FILE = ROOT / "config/dymab_window_source.json"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def verified_sources(directory: Path) -> tuple[dict, dict[str, str]]:
    pins = json.loads(PIN_FILE.read_text())
    texts = {}
    for name, expected in pins["files"].items():
        data = (directory / name).read_bytes()
        blob = hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()
        if (len(data), sha(data), blob) != (
            expected["bytes"], expected["sha256"], expected["git_blob_sha1"]
        ):
            raise ValueError(f"Pinned source mismatch: {name}")
        texts[name] = data.decode()
    return pins, texts


def brace_block(text: str, start: str) -> str:
    begin = text.index(start)
    opening = text.index("{", begin)
    depth = 0
    for i in range(opening, len(text)):
        depth += (text[i] == "{") - (text[i] == "}")
        if depth == 0:
            return text[begin:i + 1]
    raise ValueError("Unclosed pinned source block")


STUB = r'''
#pragma once
#include <vector>
#include <list>
#include <set>
#include <string>
#include <chrono>
#include <limits>
#include <stdexcept>
using namespace std;
using namespace std::chrono;
struct Instance {}; // no map, agents, distances or task generation
struct IterationStats {};
using Path = vector<int>;
struct SingleAgentSolver {
    virtual ~SingleAgentSolver() = default;
    int start_location = 0;
    vector<int> my_heuristic;
};
'''


METHODS = r'''
    string getSolverName() const override { return "SOFTWARE_FIXTURE_ONLY"; }
    void observe(int arm, double value, bool condition) {
        heuristicBanditStats.banditIndex = arm;
        updateDestroyWeights(&heuristicBanditStats, value, condition);
    }
    void choose_pair() { sampleDestroyHeuristicAndNeighborhoodSize(); }
    void choose_one() { sampleDestroyHeuristic(&heuristicBanditStats); }
    void set_clock(int n) { iterationCount = n; }
    void set_queues(vector<deque<double>> values) {
        heuristicBanditStats.recent_rewards = values;
    }
    void report(const string& name) const {
        const auto& q = heuristicBanditStats.recent_rewards[0];
        cout << setprecision(17) << "{\"case\":\"" << name
             << "\",\"arms_parameter\":" << numberOfDestroyHeuristics
             << ",\"alpha\":" << alphaUCB
             << ",\"initial_epsilon\":" << initialEpsilon
             << ",\"lambda\":" << lambdaDecay
             << ",\"window_parameter\":" << decayWindow
             << ",\"clock\":" << iterationCount
             << ",\"epsilon\":" << epsilonT
             << ",\"selected\":" << heuristicBanditStats.banditIndex
             << ",\"size_bandit_objects\":" << neighborhoodBanditStats.size()
             << ",\"child_reward_rows\":"
             << (neighborhoodBanditStats.empty() ? 0 : neighborhoodBanditStats[0]->recent_rewards.size())
             << ",\"child_weight_rows\":"
             << (neighborhoodBanditStats.empty() ? 0 : neighborhoodBanditStats[0]->destroy_weights.size())
             << ",\"q0\":[";
        for (size_t i = 0; i < q.size(); ++i) {
            if (i) cout << ',';
            cout << q[i];
        }
        cout << "]}" << endl;
    }
'''


def fixture_source(texts: dict[str, str]) -> str:
    lns = texts["src/LNS.cpp"]
    start = lns.index("BasicLNS(instance,")
    original = lns[start:lns.index(")", start) + 1]
    original = original.replace("time_limit", "1.0").replace("neighbor_size", "8").replace("screen", "0")
    corrected = "BasicLNS(instance, 1.0, 8, 0, bandit_algorithm_name, neighborhoodSizes, DESTROY_COUNT, alphaUCB, initialEpsilon, lambdaDecay, decayWindow)"
    initialization = brace_block(lns, 'if (destroy_name == "Adaptive")')
    enum = texts["inc/LNS.h"].split("enum destroy_heuristic", 1)[1].split(";", 1)[0]
    code = "/* Generated audit fixture. Extracted upstream portions: MIT.\n" + texts["LICENSE"] + "\n*/\n"
    code += '#include "BasicLNS.h"\n#include <iomanip>\n#include <iostream>\n'
    code += "enum destroy_heuristic" + enum + ";\n"
    for name, initializer in [("OriginalBinding", original), ("CorrectedBindingOnly", corrected)]:
        code += f'''class {name} : public BasicLNS {{
public:
    {name}(const Instance& instance, const string& bandit_algorithm_name,
           int neighborhoodSizes, double alphaUCB, double initialEpsilon,
           double lambdaDecay, double decayWindow) : {initializer} {{
        const string destroy_name = "Adaptive";
        {initialization}
    }}
{METHODS}
}};
'''
    code += r'''
int main(int argc, char**) {
    Instance instance;
    const string alpha = "AlphaUCB", epsilon = "EpsilonGreedy";
    if (argc > 1) {
        // Deliberately exercise the source's inconsistent child dimensions.
        // _GLIBCXX_ASSERTIONS must stop BEFORE an invalid vector access.
        CorrectedBindingOnly dimensions(instance, alpha, 5, 10000, .5, 10, 100);
        dimensions.report("corrected_binding_size5_before_selection");
        dimensions.choose_pair();
        return 0;
    }
    OriginalBinding original(instance, alpha, 5, 10000, .5, 10, 100);
    original.report("original_readme_binding");
    for (int i = 1; i <= 105; ++i) original.observe(0, i, true);
    original.report("original_after_105_positive_rewards");
    original.choose_pair();
    original.report("original_after_one_two_level_selection");

    CorrectedBindingOnly only_success(instance, alpha, 0, 2, .5, .01, 3);
    only_success.report("binding_corrected_prefill");
    only_success.observe(0, 6, true);
    only_success.report("first_positive_reward");
    only_success.observe(0, 0, false);
    only_success.observe(0, -4, false);
    only_success.report("zero_and_negative_not_admitted");
    only_success.observe(0, 3, true);
    only_success.report("second_positive_reward");
    for (int i = 0; i < 1000; ++i) only_success.observe(1, 1, true);
    only_success.report("other_arm_updates_do_not_age_q0");

    CorrectedBindingOnly selector(instance, alpha, 0, 2, .5, .01, 3);
    selector.set_queues({{0}, {.5, .5}, {-100}});
    selector.choose_one();
    selector.report("ucb_denominator_counterexample");

    CorrectedBindingOnly one_level(instance, alpha, 0, 2, .5, .01, 3);
    one_level.choose_pair();
    one_level.report("one_level_clock");
    CorrectedBindingOnly two_level(instance, alpha, 3, 2, .5, .01, 3);
    two_level.choose_pair();
    two_level.report("two_level_clock_safe_dimensions");

    CorrectedBindingOnly greedy(instance, epsilon, 0, 2, .5, .01, 3);
    greedy.set_clock(99);
    greedy.choose_one();
    greedy.report("epsilon_restart_at_100");
}
'''
    return code


def paper_completed_candidate_window(old_new: list[tuple[int, int]], width: int) -> list[list[int]]:
    """Eq.13/Alg.4-5 only: every supplied pair is a COMPLETE candidate.

    Missing/aborted candidates are outside this reference's input domain.
    Do not silently turn absent costs or a global deadline into reward zero.
    """
    if width <= 0:
        raise ValueError("positive integer window required")
    q: deque[int] = deque(maxlen=width)
    trace = []
    for old, new in old_new:
        if type(old) is not int or type(new) is not int or min(old, new) < 0:
            raise ValueError("complete nonnegative integer costs required")
        q.append(old - new)
        trace.append(list(q))
    return trace


def check_rows(rows: list[dict], negative: subprocess.CompletedProcess) -> dict:
    by = {r["case"]: r for r in rows}
    assert len(by) == 12, len(by)
    initial = by["original_readme_binding"]
    assert [initial[k] for k in ("arms_parameter", "alpha", "initial_epsilon", "lambda", "window_parameter")] == [10000, .5, 10, 100, 3]
    assert initial["q0"] == [0] * 100
    assert by["original_after_105_positive_rewards"]["q0"] == list(range(6, 106))
    assert by["original_after_one_two_level_selection"]["clock"] == 2
    assert by["binding_corrected_prefill"]["q0"] == [0, 0, 0]
    assert by["first_positive_reward"]["q0"] == [0, 0, 6]
    assert by["zero_and_negative_not_admitted"]["q0"] == [0, 0, 6]
    assert by["second_positive_reward"]["q0"] == [0, 6, 3]
    assert by["other_arm_updates_do_not_age_q0"]["q0"] == [0, 6, 3]
    assert by["one_level_clock"]["clock"] == 1
    assert by["two_level_clock_safe_dimensions"]["clock"] == 2
    assert by["ucb_denominator_counterexample"]["selected"] == 0
    qs = [[0], [.5, .5], [-100]]
    paper_scores = [sum(q) / len(q) + math.sqrt(4 / (len(q) + 1)) for q in qs]
    assert max(range(3), key=lambda i: paper_scores[i]) == 1
    e = by["epsilon_restart_at_100"]
    assert e["clock"] == 100 and math.isclose(e["epsilon"], .5 / math.log(2) * math.log(100))
    assert e["epsilon"] > 1
    trace = paper_completed_candidate_window([(20, 14), (20, 20), (20, 24), (20, 17)], 3)
    assert trace == [[6], [6, 0], [6, 0, -4], [0, -4, 3]]
    try:
        paper_completed_candidate_window([(20, None)], 3)
    except ValueError:
        pass
    else:
        raise AssertionError("missing candidate must not become a zero reward")
    dims = json.loads(negative.stdout.splitlines()[0])
    assert dims["child_reward_rows"] == 3 and dims["child_weight_rows"] == 5
    assert negative.returncode == -6, negative.returncode
    # libstdc++ builds differ in whether checked-vector aborts emit text.
    # Keep the actual stderr; do not infer a diagnostic string that is absent.
    return {
        "paper_completed_candidate_trace": trace,
        "paper_scores_for_counterexample": paper_scores,
        "paper_selected_arm": 1,
        "source_selected_arm": 0,
        "constructor_only_fix_child_dimensions": dims,
        "expected_dimension_assertion_returncode": negative.returncode,
        "dimension_stderr_present": bool(negative.stderr),
        "assertions_scope": "helper semantics on artificial costs; no MAPF quality or timing evidence",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    pins, texts = verified_sources(args.source_dir)
    args.output.mkdir(parents=True, exist_ok=False)
    report = {
        "schema": "DYMAB_WINDOW_SOFTWARE_AUDIT_V1",
        "status": "STARTED", "scope": "SOFTWARE_FIXTURE_ONLY",
        "scientific_runs": 0, "training": False, "upstream_commit": pins["commit"],
        "source_manifest_sha256": sha(PIN_FILE.read_bytes()),
        "audit_script_sha256": sha(Path(__file__).read_bytes()),
        "started_utc": datetime.now(timezone.utc).isoformat(),
        "source_files": pins["files"],
        "limitations": ["not the full upstream program", "inert graph/search dependency stubs",
                        "LNS binding/initialization excerpt, not the LNS constructor's map preprocessing",
                        "constructor-only correction is a named counterfactual, not an installed fix",
                        "no MAPF instance, scientific benchmark, timing claim or regret guarantee"],
    }
    try:
        with tempfile.TemporaryDirectory(prefix="dymab-window-software-") as temporary:
            temp = Path(temporary)
            (temp / "common.h").write_text(STUB)
            for name in ("SIPP", "SpaceTimeAStar"):
                (temp / (name + ".h")).write_text('#pragma once\n#include "common.h"\n' +
                    f'struct {name} : SingleAgentSolver {{ {name}(const Instance&, int) {{ throw logic_error("solver construction forbidden"); }} }};\n')
            (temp / "BasicLNS.h").write_text(texts["inc/BasicLNS.h"])
            (temp / "BasicLNS.cpp").write_text(texts["src/BasicLNS.cpp"])
            fixture = fixture_source(texts)
            (args.output / "author_fixture.cpp").write_text(fixture)
            (args.output / "LICENSE").write_text(texts["LICENSE"])
            (temp / "fixture.cpp").write_text(fixture)
            command = ["g++", "-std=c++14", "-O0", "-D_GLIBCXX_ASSERTIONS", "-Wall", "-Wextra",
                       "-I", str(temp), str(temp / "BasicLNS.cpp"), str(temp / "fixture.cpp"),
                       "-o", str(temp / "fixture")]
            report["compiler"] = subprocess.check_output(["g++", "--version"], text=True).splitlines()[0]
            compiled = subprocess.run(command, capture_output=True, text=True, timeout=30)
            (args.output / "compile.stderr").write_text(compiled.stderr)
            report["compile_returncode"] = compiled.returncode
            if compiled.returncode:
                raise RuntimeError("software fixture compilation failed; retained compile.stderr")
            # Disable core dumps for the deliberate, checked dimension assertion.
            import resource
            def no_core():
                resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            normal = subprocess.run([str(temp / "fixture")], capture_output=True, text=True,
                                    timeout=5, preexec_fn=no_core)
            negative = subprocess.run([str(temp / "fixture"), "--binding-only-size5"],
                                      capture_output=True, text=True, timeout=5, preexec_fn=no_core)
            for label, result in [("normal", normal), ("dimension", negative)]:
                (args.output / (label + ".stdout")).write_text(result.stdout)
                (args.output / (label + ".stderr")).write_text(result.stderr)
            report["normal_returncode"] = normal.returncode
            report["dimension_returncode"] = negative.returncode
            if normal.returncode:
                raise RuntimeError("normal software fixture failed")
            rows = [json.loads(line) for line in normal.stdout.splitlines()]
            report["observations"] = rows
            report["checks"] = check_rows(rows, negative)
            report["status"] = "PASS_WITH_CONFIRMED_UPSTREAM_INTERFACE_DIFFERENCES"
    except Exception as exc:
        report["status"] = "AUDIT_FAILED"
        report["error"] = f"{type(exc).__name__}: {exc}"
    report["finished_utc"] = datetime.now(timezone.utc).isoformat()
    report["artifacts"] = {p.name: {"sha256": sha(p.read_bytes()), "bytes": p.stat().st_size}
                           for p in args.output.iterdir() if p.is_file()}
    target = args.output / "RESULT.json"
    target.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({"status": report["status"], "result": str(target),
                      "sha256": sha(target.read_bytes()), "scientific_runs": 0}, ensure_ascii=False))
    return 0 if report["status"].startswith("PASS_") else 1


if __name__ == "__main__":
    raise SystemExit(main())
