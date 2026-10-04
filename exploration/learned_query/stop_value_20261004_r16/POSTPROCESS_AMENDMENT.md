# Analysis-only amendment: nondeterministic planner timing metadata

Recorded during TRAIN execution, after the first two compatibility C arms and before all TRAIN outcomes or model fitting. Both new compatibility native raw streams are byte-identical to their R13 C raw streams. All planner result fields match except `result.planner_us`, which is measured host time and cannot be equal on a repeated execution. It does not enter native execution, policy or simulator time.

The frozen pipeline.py wrongly requires raw planner SHA equality and will reject the compatibility step after completing all registered native runs and audits. Keep that failure and all original source/protocol hashes. `finish_train.py` performs the same registered pair extraction, additionally requiring exact full native raw SHA equality and all planner JSON fields except `result.planner_us` to match. The original two planner hashes remain distinct and are both recorded. No native rerun, source change, sample change, gate/metric/feature/model/activation change or wall-clock performance equivalence is claimed.

This corrects analysis of nondeterministic logging metadata, not the scientific intervention. It is also stricter on native traces than the original protocol because full raw byte equality holds without removing policy/check metadata.
