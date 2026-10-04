# R13 handoff

Scope is actual online adoption of a different author fixed-path suffix graph in the finite R11 primitive executor. Read REPORT.md, PROTOCOL.md and SOURCE_AND_LICENSE.md before interpreting results. The36 registered continuations/24 real author calls are complete. There is no TRAIN or TEST split: these are two reused author cases for interface verification.

Canonical data: REGISTRATION.json freezes source/input/binary before calls; RESULTS.json links all36 full traces and24 actual call receipts; SUMMARY.json stores exact signed effects. `public/` contains the only messages read by the native optimizer. `calls/` contains stdout/stderr, timestamped process receipts and native input/output exports. `raw/*checkpoint*` is private continuation state, never author input.

In trace JSON, `graph` is the full initial graph and `final_graph` is the graph actually used after adoption. `adoption.at` and `adoption.event_seq` identify the swap; old dependencies apply before that event index and new `adoption.graph` dependencies thereafter. The swap can occur during an active MOVE. Its queued events and geometric segments must remain unchanged. Sources/current states pruned for author optimization are lifted into the original full path-ID namespace; original satisfied dependency orientations remain present.

`executor.py` is copied byte-identically from frozen R11. Original sources in AUTHOR_SOURCES.tar.gz and SOURCE bindings remain unchanged; author_online.cpp is the explicitly separate input/output adapter. Local audit_events.py supports the graph switch without importing the executor. Root independent geometry/commitment evidence is bound in ROOT_AUDIT_BINDING.json when complete; do not edit the root review directory.

Replay one canonical adopted trace without new optimization:

```bash
rtk proxy python3 reproduce.py --replay random-32-32-10__t1_2__primitive_nominal__GSES
```

Offline source rebuild:

```bash
rtk proxy python3 reproduce.py --build
```

`--replay all` verifies all36 saved continuations and event/resource audits. It can take additional time; no original author source checkout or historical absolute expanded trace directory is required. No user result is overwritten by replay. This is not a full environment container; Python and compatible g++ are required. The exact observed rebuild/replay checks are recorded in REPRODUCTION.json.

Do not rerun prepare/run in this frozen directory; both intentionally refuse overwrite. New scenarios, asynchronous latency, primitive models or learning require a new protocol/directory. Scientific successes24, changed adoptions24, changed traces24; sum outcomes18 gains/6 losses, makespan12 losses/12 ties. Natural timeout/rejection0; injected failures are mechanical controls only. Publication is limited to PUBLICATION_MEMBERS.json; expanded binaries and author output staging under main evidence are excluded.
