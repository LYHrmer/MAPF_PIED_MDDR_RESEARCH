# R19 held-out prediction: secondary diagnostic

This diagnostic was requested and registered after the main R19 experiment began. It is secondary and cannot change the frozen model, predictor, original planning analysis or scientific matrix. It performs no training, solver call or physical execution.

Use exactly one common `history_no_query` trajectory per registered executable world. Do not pool rows from different policy trajectories. Compare all nine modes already fixed in the original model package: nominal, all_history, recent4, ewma03, constant_survival, all_history_survival, recent4_survival, ewma03_survival, learned. Every mode uses the same frozen MODEL.json; online history calculations use only already delivered ENDs, never future features or test-fitted dispersion.

Reconstruct each actual START's nominal duration and earlier END history; score its predicted complete action duration against the later END−START. Reconstruct every public active gate's occurrence, START age and earlier delivered ENDs; score remaining-time prediction against the later END−gate time. Dependency waiting is excluded from duration/elapsed and retained separately. Future END is an offline label only. Repeated ages remain correlated rows within the same world, not additional independent experiments.

Report MAE/MSE/bias with equal family weight, equal world weight within family and equal row weight within world. Core (N16/32, scenarios6/7) comprises 36 worlds in six map/scenario families. The registered N64 extension comprises nine planned worlds across three families; only six worlds in two families have valid initial plans. Keep the initial-failure coverage denominator visible and score the executable families separately. Do not combine core and scale extension into a population claim.

A missing terminal END is right-censored: retain its prediction and observed lower bound, exclude it from an uncensored MAE/MSE without imputing its final duration, and report censored counts. A missing canonical RUN_RECEIPT blocks a final complete-reference report; it is not silently replaced by another arm.

Save canonical source paths/hashes, frozen model/code and original registration hashes, per-row predictions, per-world/family errors and final coverage. These metrics describe the common history-policy state distribution. They neither prove the deployed learned policy experiences the same state distribution nor establish scheduling benefit or calibrated uncertainty.
