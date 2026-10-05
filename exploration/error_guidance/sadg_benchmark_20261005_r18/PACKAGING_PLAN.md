# R18 local evidence packaging

`package_results.py` uses only the Python standard library. It imports no scientific implementation, runs no subprocess, sends no messages, and performs no upload or Git operation. The scientific files, caches, model, and source pins are read-only. This script must not run `pack` until the root agent confirms the scientific matrix and final audit are complete.

Safe while experiments are live:

```bash
rtk proxy python3 package_results.py inventory
```

This mode reads directory names and file sizes, counts directories with `RUN_RECEIPT.json`, and reports unfinished `STARTED.json` directories. It does not open episode, TEST-result, model, or cache contents; it writes no file and performs no compression. Counts may change during the snapshot, so inventory is not an acceptance report.

After the root's completion instruction:

```bash
rtk proxy python3 package_results.py pack --audit review/COMPLETED_ARTIFACTS_AUDIT.json
```

The default audit contract is the existing independent audit schema. Packaging requires all of the following:

- `SUMMARY.json.missing` is exactly `[]`, with a unique full evaluation denominator reconstructed from registration.
- Every current registration source pin matches, including engine and policy; model and receipt hashes match and the TRAIN collection is complete.
- The collection hashes match all labels, pairs and omissions; the 108 registered TRAIN pair IDs occur exactly once as a label or omission. Standalone `LEARNING_AUDIT.json.passed` is true. All 45 data rows retain their normalized TRAIN/CAL/TEST split and exact registered plan hash.
- All collected episodes have a complete `RUN_RECEIPT.json`, matching specification/raw episode/case/source/model hashes. Any unfinished scientific `STARTED.json` causes refusal rather than exclusion of an inconvenient attempt.
- Final audit `passed` and `learning.passed` are true, `requested_splits` covers TRAIN/CAL/TEST, and its unique episode list exactly matches every completed receipt and raw hash. Per-episode audit files must be PASS and reference the current independent auditor hash. Recorded scientific failures remain included; audit PASS does not mean the experiment was successful.
- The existing 4.70 MB data bundle matches its frozen SHA-256. The live inventory and hashes must remain unchanged throughout packaging, with final acceptance checks repeated.

If the final auditor changes its report schema, explicitly adapt these checks before packaging; do not weaken the checks to accept a partial TRAIN audit. The output directory must not already exist. An interrupted packaging attempt is retained for review; no source/raw evidence is deleted or overwritten to make a retry appear successful.

Output goes only to new `package_results/` files. Scientific episodes are grouped by split × map and then chunked; all receipt-complete TRAIN probes and failed outcomes are included. All final author-cache JSON/model records are grouped in bounded chunks. Other root artifacts preserve code, training, final review, figures, summaries, pilot artifacts, and documentation. Python bytecode, cache directories, temporary files and live lock files are excluded. The existing frozen data archive is copied once, with unpacked data excluded from the new parts. This preserves the original maps/scenarios, raw ECBS attempts, unchanged author source/license and binary without duplicating the whole old branch.

The two exact R16 dependencies (`isolated_patch/compiler.py`, `isolated_patch/r16_guard_group.py`) are read and archived under `dependencies/sadg_preflight_20261004_r16/`. Their hashes join the source manifest. They implement the already-disclosed compiler/guard adaptation; their inclusion does not turn the adapted baseline into untouched author code. The original author implementation and license are in the frozen data archive.

Each part is lossless `tar.gz`, ordered by member path, with normalized timestamps and owners. Initial chunks use a 128 MiB raw-byte ceiling for convenience; acceptance uses actual compressed bytes, never an estimate. An oversized part is recursively split. If one source file alone still compresses above 50 MiB, it is stored as byte-range fragments with original path, offsets, original full size/hash, and per-member hashes. Reassembly concatenates fragments by offset and verifies the full original hash. Only disposable oversized packaging candidates are removed; scientific source files are never removed. Every accepted archive is reopened and every member rehashed before `PACKAGE_COMPLETE.json` is written.

The package includes:

- `ACCEPTANCE_GATE.json`: exact final inputs and acceptance hashes.
- `SOURCE_FIGURE_MANIFEST.json`: code/document/figure identities, separate from raw episode parts.
- One `*.members.json` per part: full original paths, sizes, and per-member SHA-256 hashes.
- `PACKAGE_MANIFEST.json`: archive hashes, reconstruction contract, data/author/R16 dependencies and exclusions.
- `PACKAGE_COMPLETE.json`: final round-trip success marker. Its absence means incomplete packaging.
- `GIT_STAGING_PLAN.json`: exact proposed thin-file and archive paths, measured sizes and hashes, with at most 1 GiB of new payload in each reviewable batch. It does not stage, commit, or push anything.

Root may stage the small source/docs/result JSON and this package directory without staging thousands of raw episode/cache files. Check the final complete marker and every file's measured size before Git staging; each output must be at most 50 MiB. Absolute environment paths inside the original receipts remain archival provenance and are not silently rewritten. Restore `R18/` and the dependency directory structure when relocating. No data/software redistribution license is invented by this packager; preserve the original attribution and license files.

Implementation verification before final packaging: Python syntax passed; live inventory ran without writing artifacts. A separate temporary synthetic test reduced the limit to 64 KiB and packaged a 200,000-byte incompressible input twice. It produced four parts (largest 50,386 bytes), matching byte-for-byte across both runs; member hashes and contiguous-offset reconstruction recovered the exact original. The synthetic source remained unchanged, and no scientific episode/cache/model was opened by that test. The actual R18 `pack` command has not yet been run.

## Capacity snapshot and explicit staging

A later pure-stat snapshot had 593/641 completed scientific episodes. Author cache contained 3,287 already-compressed model files (202,927,381 bytes) and 3,287 JSON files (2,999,722,952 bytes). Receipt-complete episodes contained 14,392,434,271 JSON bytes and 910,344,211 log bytes. No content was opened and no precompression was performed for this inventory.

Using the current TEST-maze average only as a size extrapolation for the remaining 48 episodes, and scaling cache bytes by 641/593, suggests about 17.62 GB episode raw data, 3.24 GB cache JSON, and 219 MB already-compressed models. These are not final measurements or compression forecasts. To fit all new archives into 2 GiB, JSON/log data would need to compress below approximately 9.22% of raw size. Illustrative 5%, 8%, and 10% fractions imply approximately 1.18, 1.76, and 2.15 GiB respectively. A single push therefore cannot be promised to stay below 2 GiB before final actual compression.

The explicit staging plan keeps top-level source/docs/light JSON/CSV, training JSON, top-level independent review source/reports, final figures, selected lightweight data provenance (including `data/CASES.json` and `data/prepare_data.py`), recursive `parallel/**/*.py` and `parallel/**/*.json`, and every completed package artifact visible. `parallel/**/process.log` enters the lossless archive only. It excludes direct `episodes/`, `author_cache/`, data case/output trees, per-episode review JSON, bytecode and temporary/lock files from Git staging; those raw records remain recoverable from the archives and remain untouched in the workspace. No broad `git add .` is used. The plan's paths are relative to R18, with one self-reference for its own metadata file.

After reviewing the final plan, root can create a NUL-delimited path list for an explicitly selected batch and run `rtk git add --pathspec-from-file=<list> --pathspec-file-nul` from R18, then review the staged paths before committing. Each proposed batch contains at most 1 GiB of measured new files, leaving room below the stated 2 GiB transport ceiling. Multiple commits sent together still form one push; if the final total is too large, commits must be pushed in separate authorized batches. Existing unpushed history and Git pack overhead are outside these measured new-file totals and must be checked by the Git owner. The packager itself performs no Git operation.
