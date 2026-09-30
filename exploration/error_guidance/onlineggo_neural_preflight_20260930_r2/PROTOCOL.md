# Official OnlineGGO neural evaluator qualification

Declared before the new build or native tests, 2026-09-30, round 2.

This qualification closes the gap between the earlier OBJECTIVE=3 static binary
and the author's OBJECTIVE=4 (`OBJ::NN`) evaluator. It is not a trained-policy
benchmark or a comparison against the proposed method. The official repository
is https://github.com/zanghz21/OnlineGGO at
`ff6d830e2fd5bf85ccbb72eaec0fb8df1cf1c256` (MIT). No algorithm source changes.
Use its bundled pybind11/MiniDNN and the already available system Eigen, as in
the prior disclosed build. Build a new directory; retain the old source/binary.

Each configure/build is limited to 120 seconds. Native smoke tests are limited
to 60 seconds, use the author's `visualizer_example_sts.json`, 10 agents,
100 discrete steps, one revealed task per agent, and original priority RNG.
One valid 560-value constant vector (all 5, the author's optimization initial
mean) is explicitly **untrained diagnostic input**; a 559-value vector must be
rejected by the official shape check. Neither vector is a scientific baseline.
Retain all receipts and full actual paths, goals and task events. Independently
replay all executed actions and reconstruct roundrobin task service. A stopped
native run remains stopped; no synthetic task completion. Do not compare smoke
task counts with runs using different settings or describe them as learned gains.

The evaluator requires an explicit `optimal_update_model.json` with finite
`params` and a separate provenance record. Missing/bad weights cannot fall back
to random, zero, static or hand-written weights. A trained-policy claim further
requires matching author config, training/source lineage and a held-out evaluation
contract. The current tracked repository has no such checkpoint; the author's
README describes extracting it from training logs, and its release page has no
release assets. This is a scoped checkpoint-availability finding, not proof that
the authors never supplied weights elsewhere.

The source priority shuffle uses random_device even when the task source has a
seed. No deterministic-pair or original-paper reproduction claim is made here.
The build follows the author's no-LNS neural configuration; it is distinct from
the separate original GPIBT GP-R100-Re10-F2 nonlearning baseline. LSMART remains
an execution testbed. No continuous-error experiment is included in this package.

First smoke invocation failed before network construction: the assumed
`OnlineGGO/Guided-PIBT/.../visualizer_example_sts.json` is not present in that
repository. Both failed receipts are retained and are not a shape-test success.
The fixed input is now read from the previously archived **original GPIBT author
input**, `external_baseline_pilot_20260929/author_inputs/visualizer_example_sts.json`,
with all map/starts/tasks bytes preserved and hashed. This is an evaluator-support
input, not an OnlineGGO original experiment config. Validate its existence,
teamSize=10 and reveal=1 before either second smoke invocation; retain suffix02.
