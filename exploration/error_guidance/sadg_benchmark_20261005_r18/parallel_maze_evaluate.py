#!/usr/bin/env python3
"""Disjoint TEST maze scheduling through the unchanged frozen episode function."""
import os
from pathlib import Path
import run_benchmark as benchmark


def main():
    reg = benchmark.register()
    benchmark.assert_pins(reg)
    model = benchmark.HERE / "MODEL_FROZEN.json"
    model_receipt = benchmark.load(benchmark.HERE / "MODEL_FREEZE_RECEIPT.json")
    assert model_receipt["model_sha256"] == benchmark.sha(model)
    assert model_receipt["source_pins"] == reg["source_pins"]
    assert model_receipt["before_any_calibration_or_test_learned_execution"]
    destination = benchmark.HERE / "parallel" / "maze-32-32-2"
    helper_sha = benchmark.sha(Path(__file__).resolve())
    cases = sorted((case for case in reg["cases"]
        if case["split"] == "TEST" and case["map_name"] == "maze-32-32-2"
        and case["status"] == "valid"),
        key=lambda case: (int(case["scenario_id"]), case["num_agents"]))
    assert [(int(c["scenario_id"]), c["num_agents"]) for c in cases] == [
        (scenario, size) for scenario in (4, 5) for size in (8, 16, 32)]
    disturbances = list(benchmark.DISTURBANCES)
    assert disturbances == ["stable", "bounded_pause", "speed_shift"]
    spec = dict(map_name="maze-32-32-2", split="TEST", requested_episodes=90,
        case_ids=[case["case_id"] for case in cases], disturbances=disturbances,
        disturbance_specs=reg["disturbances"], arms=reg["arms"],
        source_pins=reg["source_pins"], model_sha256=benchmark.sha(model),
        model_freeze_receipt_sha256=benchmark.sha(benchmark.HERE / "MODEL_FREEZE_RECEIPT.json"),
        helper_sha256=helper_sha, episode_function_unchanged=True,
        rationale="Disjoint maze TEST scheduling after model freeze; complete receipts reused, unfinished attempts never rerun.",
        timing_scope="Concurrent host timings are diagnostics, not controlled method runtime ranking.")
    benchmark.freeze(destination / "REGISTRATION.json", spec)
    done = []
    for case in cases:
        for disturbance in disturbances:
            for arm in reg["arms"]:
                progress = dict(case_id=case["case_id"], disturbance=disturbance,
                    arm=arm, completed=len(done), requested_episodes=90,
                    updated_utc=benchmark.utc(), process_id=os.getpid(),
                    helper_sha256=helper_sha)
                benchmark.save(destination / "PROGRESS.json", progress)
                print(progress, flush=True)
                try:
                    result, path, reused = benchmark.episode(reg, case, disturbance, arm)
                except Exception as exc:
                    benchmark.freeze(destination / "STOPPED.json", dict(progress,
                        error=repr(exc), prior_completed=done, rerun_attempted=False))
                    raise
                done.append(dict(episode=str((path / "episode.json").relative_to(benchmark.HERE)),
                    episode_sha256=benchmark.sha(path / "episode.json"), status=result["status"],
                    existing_complete_receipt=reused))
                benchmark.save(destination / "PROGRESS.json", dict(progress,
                    completed=len(done), last_status=result["status"], updated_utc=benchmark.utc()))
    benchmark.freeze(destination / "COMPLETION.json", dict(requested_episodes=90,
        episodes=done, helper_sha256=helper_sha,
        source_registration_sha256=benchmark.sha(destination / "REGISTRATION.json")))
    print(dict(completed=len(done), helper_sha256=helper_sha), flush=True)


if __name__ == "__main__":
    main()
