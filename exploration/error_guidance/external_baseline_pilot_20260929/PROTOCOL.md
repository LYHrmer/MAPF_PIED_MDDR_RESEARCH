# Frozen external baseline pilot: official GPIBT, 2 inputs x 2 seeds

Frozen before new native runs, 2026-09-29. Author repository nobodyczcz/Guided-PIBT at 7f4b91e4ed134229710945a4670a78639cf008d5. Exact README GP-R100-Re10-F2 configuration; separate trace+GPIBT_R0_SEED adapters are disclosed, not author-native features.

| Input (unaltered author file) | Team | Seeds |
| --- | ---: | --- |
| benchmark-lifelong/visualizer_example_sts.json | 10 | 42,43 |
| benchmark-lifelong/sortation_small_0_200.json | 200 | 42,43 |

Both reference the same author map, agents file and 50000-task sequence, with roundrobin and numTasksReveal=1; only author teamSize differs. Do not generate maps/tasks, select favorable cases, change solver flags or compare these discrete runs against PIE-D. Four cells are a pipeline/variance pilot of one published non-learning algorithm, not a new-method comparison or a reproduced paper performance table.

All cells use default450 simulation steps, planTimeLimit=10 seconds, hard process-tree limit60 seconds. Reuse previously validated 10-agent seed42 run01, preserving its original receipt; only three new runs, cumulative maximum180 seconds of new native runtime. No compilation is needed: verify source and binary hashes against the R0 artifact. A fresh portable reproduction may run all four cells with the same per-run cap. Do not rerun failures or extend caps.

Independent checker replays all actions with non-MAPFT R/D/L/U/W semantics and checks boundaries, obstacles, adjacency, vertex conflicts and reverse-edge conflicts. Reconstruct all tasks from the author's input roundrobin rule and actual arrivals. Preserve timeouts, invalid traces and pending tasks. Do not use AllValid/errors=[] as proof.

Report raw completions, full cumulative completion curves, assigned/completed/pending counts, completed-task flow (conditional statistic), restricted flow including pending up to450, native wall/planning times and all raw artifacts. Timings are host metadata under uncontrolled concurrent load; do not infer method superiority or scalability from this small matrix. Distinct seeds are whole-run units; moves/time points are not independent replicates. There is no learned method or continuous error execution in this pilot.
