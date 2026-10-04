# R16 query STOP handoff

- Entry: `REPORT.md`, `MENTOR_PREEXEC.md`, `MENTOR_POSTEXEC.md`, `PROTOCOL.md`.
- Scientific pairs: `TRAIN_PAIRS.json` (24), `CAL_PAIRS.json` (6), `RESULTS.csv` (60 arm records). Independent units: 12 TRAIN and 3 CAL families; budget rows are paired settings.
- Actual added native: 29 = 24 TRAIN STOP + 2 C binary compatibility + 3 CAL B8 STOP. Existing C: 30 referenced outcomes. Three CAL B16 STOP arms are separately qualified semantic aliases, not new native runs or fabricated logs.
- Raw arms: `runs/<world>__macro_STOP.receipt.json` or `__macro_C.receipt.json`; full per-arm SHA and audit references: `ARM_HASHES.json`. Expanded raw/input/planner/receipt/stderr/audit files are fully archived once in `RAW_R16_*.tar.gz`, verified by `RAW_ARCHIVE_MANIFEST.json`; no old C/LD raw repacked.
- Native pre-gate prefix: all events before first `macro_choice`, ignoring only policy (and native_checks in a possible no-gate summary); gate matches at/opportunity/initial_capacity/remaining_capacity/spent/target_agent/target_move/features. All new STOP runs stop POSITION/SKIP at this gate and continue to H128.
- CAL B16 aliases: `CAL_ALIAS_AMENDMENT.md`, `CAL_ALIAS_REGISTRATION.json`, `BUDGET_ALIAS_OBSERVATION.json`. Raw points to the genuine old C8 receipt; gate points to genuine old C16. Prefix proof excludes actor/macro/budget-summary metadata and separately matches all non-budget candidate features/history. Do not treat alias policy metadata as original native STOP output.
- Model source fixed before TRAIN: `learn.py`; tree and exact rational values: `MODEL_FROZEN.json`. CAL selection and selected-arm SHA: `CAL_SELECTIONS.json`. No CAL refit or old TEST access.
- Validation: 29 independent original Decimal audits, full C byte equivalence, all true prefixes, five intentional corruption rejections in `NEGATIVE_CONTROLS.json`. `COMPLETION_RECEIPT.json` and `PUBLICATION_MANIFEST.json` give final status and publication whitelist.
- Preserved analysis issue: frozen pipeline required raw planner SHA equality even though planner_us is nondeterministic host timing. Both native raw logs were byte-identical; only planner_us differed. Original failure is preserved, with a pre-analysis amendment and `finish_train.py` recovery; no native rerun or scientific source change.

Key result: TRAIN C/STOP both1077 tasks (285/144 queries), STOP T about102.388 seconds worse. CAL C237 / STOP238 / learned238 tasks, queries72 /36 /52; learned T is about90.775 seconds worse than fixed STOP. Thus there is action-value heterogeneity, but no learned advantage over the strong fixed policy.

No stage, commit, push, README change or production code edit was performed. Root owns independent three-tail analysis and publication.
