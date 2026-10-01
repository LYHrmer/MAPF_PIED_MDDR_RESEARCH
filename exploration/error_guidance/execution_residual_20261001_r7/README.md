# R7: learned execution residuals in author guidance edge costs

Read PROTOCOL.md before interpreting results. REPORT.md and summary.csv are the
final scientific outcome; model_freeze.json is the actually fitted checkpoint.
The original OBJ3/OBJ4 methods remain published algorithm baselines. History
and learned edge-cost extensions are new exploratory methods/ablations.

Evidence locations:

- r6_agent_tick_accounting.csv and r6_diagnosis.json: all 24 old complete R6c
  runs, exact per-agent tick conservation and reconstructed type-2 dependencies.
- freeze_train.json / freeze_test.json: protocol, source, input, configuration,
  actual binary/object identities frozen before the corresponding runs.
- calibration_sensitivity.json: original vs zero-overlay equivalence and
  actual cost-to-action changes on predetermined calibration states.
- audit_train.json / audit_test.json: original parser/action/ADG/FIFO/ACK and
  public predictor binding. ROOT_MODEL_AUDIT.json / root_model_audit.py provide
  a separate root reconstruction of labels, features and the fitted model.
- sampled_geometry.json: sampled circular robot/box clearance only; it is
  not a continuous safety certificate or simulated contact test.
- raw_archives/ and archive_manifest.json: all raw native bytes, including
  the initial zero-decision sandbox denials, each member SHA round-trip checked.

The actor's data projection is in public_model.py; observation/control fields
never enter it. Labels include dispatch/ADG/turning/half-MOVE elapsed time from
proposal to the normal final MOVE ACK. STATION dwell is excluded. Censored
actions are retained, not assigned synthetic completion times.

Recorded build commands are in build_receipts.json. The base implementation is
OnlineGGO@ff6d830e, with the inherited R6c S1/FIFO execution adapter and native
dependencies. SOURCE_AND_LICENSE.md, candidate_identity.json and inherited
manifests locate all source/binary dependencies. This workspace-based build is
not a self-contained container; some inherited native dependencies are stored
outside this repository. Do not rerun prepare/freeze over existing evidence.

Read-only verification in the registered workspace:

```bash
rtk proxy python3 audit.py train
rtk proxy python3 audit.py test
rtk proxy python3 root_model_audit.py
```

These audit commands rewrite only their derived audit reports. To repeat the
native experiment, reconstruct the pinned dependencies and use a fresh isolated
successor directory/raw basename, preserving the registered task streams,
models, conditions, budgets and all failure receipts. Native simulation uses
local RPC sockets and may require sandbox escalation. Raw data must be restored
to the declared evidence root before the workspace-specific audit commands.
