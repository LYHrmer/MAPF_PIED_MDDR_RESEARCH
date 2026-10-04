# SADG history-shift mechanism R17

Start with [REPORT.md](REPORT.md). This is a frozen, synthetic, single-decision scheduling probe, not a ROS reproduction or an LMAPF throughput benchmark. Author SADG commit is `c2626d996121a9d6c128844a167b917db24418ac` (AGPL-3.0); unchanged optimizer, shared R16 isolated compiler/commitment adapter.

The run registered nine comparisons and executed one new author optimization and three new event suffixes. Full semantic input matching reused eight old solve results; graph + true-state + rate matching reused existing suffixes. Original R16 data remain unchanged.

Files:

- `PROTOCOL.md`, `REGISTRATION.json`: before-run qualification, scope, bounds, hashes.
- `public.json`, `worlds/`, `captures/`, `inputs/`: delivered history, private simulation truth, actual capture-time position, and estimator-only optimizer inputs.
- `cases/`: full before/after graphs, immutable-commitment guard, solver or exact-reuse receipts, suffix references. The single new model includes all rows/variables, LP and author stdout.
- `suffix/`: three new exact-rational event executions, including waiting and goal residence.
- `RESULTS.json`, `SUMMARY.csv`, `ARTIFACT_AUDIT.json`: complete results and zero-solve artifact verification.
- `REUSE_PROVENANCE.json`: distinguishes each current registered input hash from historical `result.input_sha256/content_key` fields retained by exact solver reuse; frozen result bytes are preserved.

Existing environment: `/home/lyh/.cache/mapf_research/sadg-r16-venv`; author source: `/home/lyh/.cache/mapf_research/sadg-controller-c2626d9`. [SOURCE_ENVIRONMENT.json](SOURCE_ENVIRONMENT.json) records actual packages and source hashes. Python `-I` isolates the invocation. Actual executed commands were:

```bash
rtk proxy /home/lyh/.cache/mapf_research/sadg-r16-venv/bin/python -I run_chain.py register
rtk proxy /home/lyh/.cache/mapf_research/sadg-r16-venv/bin/python -I run_chain.py run
rtk proxy python3 validate_outputs.py
```

`run` deliberately refuses existing case results; do not rerun completed science for routine verification. `validate_outputs.py` does not run an optimizer or suffix. To replicate new science, use a new sibling output directory containing the same scripts/protocol, rebuild the fixed author environment, and register before running. The script depends on the sibling R16 audit/adapter/source material.

On a fresh Git checkout, detailed R16 raw cases may be only in its published archive. Use R16 `package_publication.py extract --destination /tmp/sadg-r16-restored` for safe, verified restoration into a new directory. Then restore the required `cases/mini_public_elapsed`, `cases/mini_measured`, `cases/mini_stub` and remaining registered mini case directories from that verified tree into their originally archived R16 paths, refusing any conflicting existing files. The two reused readable R16 suffixes are already in its publication set. This R17 publication references those bytes by SHA; it does not duplicate old large models or external R13 trajectories.

Fees remain unknown (`null`). The source is a simulated capture with explicit provenance; it does not claim production AUTH or use host truth to choose an ordering. The author dependency executor has point-geometry checks, not footprint/controller certification.
