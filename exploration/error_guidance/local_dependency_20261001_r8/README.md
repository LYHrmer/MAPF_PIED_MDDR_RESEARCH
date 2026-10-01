# R8 local dependency execution exploration

Read [REPORT.md](REPORT.md) for results and limits; [PROTOCOL.md](PROTOCOL.md) records the pre-test contract and orientation correction. Six mechanical and48 held-out native runs passed. Local two-step-buffer execution improves completed tasks; learned and same-history rule complete equal numbers. [summary.csv](summary.csv) is the complete LF per-run table.

Original events/decisions/receipts and all13 failed or superseded preflight attempts are in [raw_archives/](raw_archives/) with [archive_manifest.json](archive_manifest.json). Each archive member was re-read and SHA256 verified. [source_archives/](source_archives/) contains the copied LSMART successor and exact native binaries; [source_archive_manifest.json](source_archive_manifest.json) records members. No previous source or freeze was edited. Git operations are reserved to root.

The original main-workspace raw directory is `/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/local_dependency_20261001_r8`. Raw archive paths are relative to that directory. Native source archive paths are relative to its parent. Restore into an isolated directory or the original expected paths before replaying audits; existing scientific runs must be retained instead of overwritten. Python needs numpy/msgpack; native execution additionally requires the inherited installed ARGoS/RPC libraries and official planner object paths described by build.py/binary_manifest.json. These archives are not a standalone container.

Read-only replay commands after restoration:

```bash
rtk proxy python3 audit.py mechanical
rtk proxy python3 audit.py test
rtk proxy python3 geometry_audit.py mechanical
rtk proxy python3 geometry_audit.py test
rtk proxy python3 diagnose_waits.py test
rtk proxy python3 negative_checks.py
rtk proxy python3 root_model_refit_audit.py
rtk proxy python3 root_execution_audit_final.py
```

The model refit reconstructs only original R7train/cal public events, listed by exact SHA in model_freeze.json. Restore those R7 artifacts before running its independent audit. refit_model.py intentionally refuses to overwrite the frozen checkpoint. Official OnlineGGO/LSMART source identities and full MIT notices are in SOURCE_AND_LICENSE.md. Final publishable files are enumerated by PUBLICATION_MEMBERS.json; caches and expanded native logs are excluded.
