# R9 matched continuation query experiment

This directory contains a new N16 experiment, frozen independently from R8. Read `CONTRACT.md` for the pre-outcome protocol; `REPORT.md` and `SUMMARY.json` for final findings; `HANDOFF.md` for the root audit handoff. Published raw members are listed and hashed in `RAW_ARCHIVE_MANIFEST.json`; extract the disjoint archives here only when raw replay is required. Do not add expanded `runs/`, `build/`, `audits/` or `__pycache__/` to Git.

The experiment uses the fixed original public `condition` selector before and after one counterfactual decision. Labels compare each query with WAIT at that decision, both followed by the same live condition strategy. Models include history/nohistory/nobudget variants of the same24-dimensional ridge. Deployment changes exactly one publicly triggered decision per run and returns to condition.

Reproduction requires the pinned local production headers, legal fixture and author OnlineGGO bridge/config recorded in `PARENT_PINS_VERIFIED.json` and `AUTHOR_PROVENANCE.json`. This package is not standalone or a full reproduction of the author's physical-position benchmark. Query counts are not production COST.

Use a fresh sibling directory for a new experiment: the writers use exclusive creation to protect registered evidence. The original execution order is:

```bash
rtk proxy python3 pipeline.py register
rtk proxy python3 pipeline.py base
rtk proxy python3 pipeline.py probes
rtk proxy python3 pipeline.py train
rtk proxy env R9_WORKERS=6 python3 pipeline.py test
rtk proxy python3 audit_all.py
rtk proxy python3 verify_matched_tail.py
rtk proxy python3 negative_controls.py
rtk proxy python3 summarize.py
rtk proxy python3 archive.py
```

`audit_all.py` may run concurrently with native execution, caching each completed episode audit once. `verify_matched_tail.py` independently replays exact complete prefixes, budget deductions and return-to-condition modes, recomputes label outcomes and refits models by augmented least squares. The parent/root performs a further independent heldout review before publication. Running the commands again against an already frozen directory is not a new independent experiment and may hit intentional existing-file guards.
