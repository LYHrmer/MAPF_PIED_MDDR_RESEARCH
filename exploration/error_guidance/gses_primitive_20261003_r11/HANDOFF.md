# R11 third-line handoff

Status: complete finite R2 precheck. No changes to frozen R10/R10b directories, author native sources, manuscript, entry documents or Git were made by this worker.

Start with `REPORT.md`, `RESULTS.json`, `PROTOCOL.md`, `SCHEMA.md` and `SOURCE_AND_LICENSE.md`. The exact allowlist is `PUBLICATION_MEMBERS.json`. All 27 full traces and 27 original receipts are present; the actual half-MOVE checkpoint is `mechanical_checkpoint.json.gz`. Author source/native build provenance remains in the pinned prior R9/R10 directories. Root-owned independent audit files are pinned dependencies, not local publication members.

Run read-only archive/source verification from this directory:

```bash
rtk proxy python3 reproduce.py
```

Optionally replay a complete archived graph using only its graph and registered profile, comparing the entire generated output without writing results:

```bash
rtk proxy python3 reproduce.py --replay random60__Improved_GSES__midpoint_pause
```

This depends on the referenced source/export and root-audit paths remaining available at their recorded locations. It is not an environment container. `COMMANDS.json` documents the actual original command arguments. Do not rerun `prepare.py` in this frozen directory; it deliberately refuses to overwrite the registration. The original `run.py` similarly refuses to reuse an expanded run directory.

Accepted claims: 16 complete author-unit time-series equivalences; a shared event/affine primitive executor for genuine original/GSES/Improved graphs; 27 event/resource and independent continuous pairwise disk-clearance passes; finite actual in-flight snapshot continuity; explicit commitment rejection and observed author timeout fallback. The root checker found 239,222 MOVEs, 523,274 continuously covering segments and 72,636 exact candidate segment-pair checks.

Excluded claims: original ARGoS continuous-controller integration, a full online GSES reoptimization loop, hardware dynamics safety, fresh heldout performance, learning benefit, or strict primitive-mode dominance. The main robot objective and makespan differ on the reused random60 case; preserve both in any summary.

Future work requires a new protocol/directory. Preserve this finite evidence package unchanged. The all-three-line research-mentor postassessment belongs in the parent error_guidance directory after the main/query R11 reports are final, not appended to this package.
