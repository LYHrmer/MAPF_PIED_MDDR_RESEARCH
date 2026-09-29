# Portable official GPIBT pilot artifact

Read [REPORT.md](REPORT.md) for identities, all four outcomes and limitations, [PROTOCOL.md](PROTOCOL.md) for the fixed experiment, and [COMMON_EXECUTION_ERROR_CONTRACT.md](COMMON_EXECUTION_ERROR_CONTRACT.md) for the unimplemented next interface. This is a native discrete baseline pilot, not a learned algorithm or a continuous-error benchmark.

Offline re-verification needs only Python 3, the included files, and `rtk` available for the project's command convention. Run from this directory; no upstream checkout or solver is needed:

```sh
rtk proxy python3 -B verify_archive.py
```

It independently replays the raw actions/tasks and checks the archived input/output hashes; it also checks explicit invalid examples. All raw per-case receipts retain the original absolute execution paths as provenance. Those paths are not required by the offline verifier. `archive_manifest.json` lists copied artifact hashes.

To rebuild in a fresh sibling workspace, use the author's clean fixed checkout and a separate patched worktree. The commands below are a reproduction recipe, not additional runs performed for this archive. Commands assume this artifact has been copied to `pilot-artifact` under the current working directory. They install no dependencies. Required tools: Python 3, `rtk`, Git, CMake, C++ compiler, GNU timeout and Boost program_options/graph/system/filesystem. The actual R0 used host Boost 1.74 while the README recommends 1.83; upstream CMake accepts >=1.49. Preserve the dependency difference if claiming a literal author environment.

```sh
rtk git clone https://github.com/nobodyczcz/Guided-PIBT Guided-PIBT
rtk git -C Guided-PIBT checkout --detach 7f4b91e4ed134229710945a4670a78639cf008d5
rtk git -C Guided-PIBT worktree add --detach ../seeded-trace 7f4b91e4ed134229710945a4670a78639cf008d5
rtk proxy patch -d seeded-trace -p1 --input ../pilot-artifact/gpibt_trace_export.patch
rtk proxy patch -d seeded-trace -p1 --input ../pilot-artifact/gpibt_seed_adapter.patch
rtk proxy timeout --signal=KILL 120 cmake -S seeded-trace/guided-pibt -B seeded-build -DGUIDANCE=ON -DGUIDANCE_LNS=10 -DFLOW_GUIDANCE=OFF -DINIT_PP=ON -DRELAX=100 -DOBJECTIVE=1 -DFOCAL_SEARCH=2 -DCMAKE_BUILD_TYPE=RELEASE
rtk proxy timeout --signal=KILL 120 cmake --build seeded-build -j2
rtk proxy python3 -B pilot-artifact/harness.py --author-root Guided-PIBT --seeded-root seeded-trace --binary seeded-build/lifelong --output-dir fresh-runs
```

The harness refuses an existing output directory, checks the clean author commit, exactly two changed source files and their hashes, compiler definitions and unchanged inputs, and runs only the declared four cases. Each native process group is killed after 60 seconds; no retry occurs. This fresh recipe executes all four cells (maximum240 seconds), whereas the archived session reused one previous verified cell and ran only three. Different compiler/library builds can change binary hashes and host times; the manifest captures the actual binary. Do not assume cross-platform shuffle or trajectory identity without checking.

`--reuse-r0-dir` is optional and exists only to reuse the exact already-verified local R0 artifact with matching binary and raw hashes. It is unnecessary for a fresh reproduction and is deliberately omitted above. The original author's clone, earlier unseeded/seeded runs and native build directories are not moved or bundled here.

The copied author files and patch contexts retain their upstream MIT terms in [UPSTREAM_LICENSE.txt](UPSTREAM_LICENSE.txt). The archived original inputs are byte-identical; no map, task list, solver objective or published baseline has been invented for this pilot.
