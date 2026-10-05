#!/usr/bin/env python3
"""Schedule a disjoint TEST map with the original frozen episode function.

No scientific parameter, model, policy, cache key or simulator is changed.
The original sequential job later reads these same completed receipts.
"""
import argparse
from pathlib import Path
import os
import run_benchmark as benchmark


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("map_name", choices=["warehouse-10-20-10-2-1"])
    args=parser.parse_args()
    reg=benchmark.register()
    model=benchmark.HERE/"MODEL_FROZEN.json"
    assert benchmark.load(benchmark.HERE/"MODEL_FREEZE_RECEIPT.json")["model_sha256"]==benchmark.sha(model)
    destination=benchmark.HERE/"parallel"/args.map_name
    receipt=destination/"COMPLETION.json"
    requested=[r for r in reg["cases"] if r["split"]=="TEST" and r["map_name"]==args.map_name and r["status"]=="valid"]
    spec=dict(map_name=args.map_name,split="TEST",case_ids=[r["case_id"] for r in requested],
        arms=reg["arms"],disturbances=reg["disturbances"],source_pins=reg["source_pins"],
        model_sha256=benchmark.sha(model),episode_function_unchanged=True,
        rationale="disjoint map scheduling after model freeze; existing complete receipts reused by original sequential run",
        timing_scope="concurrent host timings are diagnostics, not controlled method runtime ranking")
    benchmark.freeze(destination/"REGISTRATION.json",spec)
    done=[]
    for case in requested:
        for disturbance in reg["disturbances"]:
            for arm in reg["arms"]:
                benchmark.save(destination/"PROGRESS.json",dict(case_id=case["case_id"],disturbance=disturbance,
                    arm=arm,completed=len(done),updated_utc=benchmark.utc(),process_id=os.getpid()))
                result,path,reused=benchmark.episode(reg,case,disturbance,arm)
                done.append(dict(episode=str((path/"episode.json").relative_to(benchmark.HERE)),
                    episode_sha256=benchmark.sha(path/"episode.json"),status=result["status"],
                    existing_complete_receipt=reused))
    benchmark.freeze(receipt,dict(requested_episodes=len(requested)*len(reg["disturbances"])*len(reg["arms"]),
        episodes=done,source_registration_sha256=benchmark.sha(destination/"REGISTRATION.json")))


if __name__=="__main__":main()
