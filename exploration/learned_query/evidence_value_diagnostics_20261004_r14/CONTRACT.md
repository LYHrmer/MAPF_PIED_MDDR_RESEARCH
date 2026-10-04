# R14 frozen-evidence value diagnostics

This is a post-hoc descriptive reuse of R13, with zero native simulations, zero new fitting and zero TEST threshold selection. R13 and all predecessors remain read-only. The export uses already verified structured results, not a second audit of 160 raw trajectories.

The extraction unit is a complete registered episode. The paired value unit is one world (family and supplied budget) with the same public condition prefix up to the actual late gate and two fully executed continuation policies, C and LD. Preserve all 160 arms and all 48 C/LD pairs: 24 TRAIN, 8 CAL and 16 TEST contexts. The latter are eight registered families, each with B8/B16. Families are disjoint row blocks and error seeds from two official scenario-2 files; they are not eight independent scenario files or unseen-map tests.

The task label is N_LD−N_C over the whole FIFO through H=128. The time label is T_C−T_LD, where T is the sum of restricted completion times of each agent's fixed first four FIFO tasks, with unfinished tasks assigned H. Keep rational numerical bounds, actual queries and budget remaining separately. Do not identify this restricted time with all-task flowtime. Preserve public gate features and separate provenance identities from deployable features.

Diagnostics distinguish task gain/loss/equality, the time envelope among equal-task branches, and cases where task and time directions conflict. The finite two-tail oracle is only an after-the-fact opportunity diagnostic; it is not a baseline, deployed policy, new experiment or guarantee for unseen contexts. The report includes all TEST families and both budgets, with no outcome-based subgroup or threshold selection. Public structural summaries use only existing candidate multiplicity, claim count, budget and gate features; they do not define a newly tuned decision rule.

Content hashes bind the R13 freeze manifest, structured values, registration, archived raw member identities and completed audits. First execution writes deterministic exports and a cache manifest. A second execution with the same source, schema and code hashes must verify and reuse those artifacts with zero extracted arms/pairs and zero raw reads. Changed inputs create a different cache key and must never be silently accepted as a hit. Mechanical corruption checks operate on copied small metadata only.

Root owns Git and entry documentation. R14 changes no model, original source, planner, physics, controller, prior publication member or README.
