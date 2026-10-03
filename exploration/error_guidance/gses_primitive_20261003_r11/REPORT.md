# R11: finite primitive execution mapping for genuine author GSES graphs

The registered 27 runs passed. All 16 unit-step executions reproduce the author's complete recorded state series, sum of completion times and makespan. All 11 added primitive executions preserve actual resource occupancy through TURN, STATION and midpoint pauses. A separate auditor checked 239,222 MOVEs and 523,274 continuous trajectory segments, including completed robots remaining at goals; no pairwise disk collision was found. This closes a finite execution-interface precheck. It does not establish equivalence to the original continuous feedback controller or a new planning-performance contribution.

## Inputs and interpretation

The graphs are the original and actually adopted outputs of unmodified author GSES and Improved GSES from R10: random-32-32-10 with 60 agents, warehouse-10-20-10-2-1 with 110, Paris_1_256 with 120, and lak303d with 41, all at the registered instance 1/situation 0. Their full paths and selected type2 orderings are retained. The 43 pinned author compilation sources remain unchanged. There was no R11 optimizer rerun, model training or parameter search.

`PROTOCOL.md` and `REGISTRATION.json` preceded execution. The 27 runs comprise 16 author-unit regressions, nine random60 primitive runs (three selected graphs times three profiles), and two lak41 primitive runs verifying the already observed actual GSES timeout fallback. Reusing these inputs tests the interface; these are not 27 independent heldout instances.

The common execution layer is an exact rational-time, piecewise affine geometric model. A unit grid MOVE has two affine half segments. Disk radius is 1/10. A moving disk enters the destination cell at progress 2/5 and fully leaves the source at 3/5. A half-MOVE at 1/2 leaves the author vertex state unchanged. Destination-cell and edge reservations begin at MOVE_START and are distinguished from geometric cell entry and exit. Type2 dependencies release only when their predecessor really ARRIVEs at its next vertex; future geometry or predictions do not count as arrival. TURN and STATION keep the current cell occupied, and every robot stays at its goal through the joint makespan.

The author's initial current type1 delay is a pre-move hold of weight minus one, measured from reset independently of dependency blocking. It is not slower motion. Future type1 weights must equal one. The added `axis_slow` profile changes physical movement duration independently and is never presented as author-equivalent mode.

## Exact author-unit regression

MOVE takes one, TURN and STATION take zero. The executor schedules from the graph; it never consumes the author's future recorded states as actions. The independent after-the-fact checker compares the entire integer-time state series. The root auditor repeated these comparisons from the emitted segments/events.

| Author case | Original sum / makespan | GSES sum / makespan | Improved GSES sum / makespan |
|---|---:|---:|---:|
| random-32-32-10, N60 | 1375 / 54 | 1292 / 50 | 1292 / 50 |
| warehouse-10-20-10-2-1, N110 | 10816 / 200 | 10804 / 201 | 10804 / 201 |
| Paris_1_256, N120 | 29860 / 530 | 29860 / 530 (timeout fallback) | 29786 / 522 |
| lak303d, N41 | 10496 / 528 | 10496 / 528 (timeout fallback) | 10229 / 511 |

Each optimizer export supplied both its original and selected record, hence 16 executions. These costs reproduce previously observed author results; they are not new comparative optimizer evidence.

## Registered primitive mechanisms

The nominal primitive profile sets MOVE=1, each quarter-TURN=1/4 and STATION=1/2 at every newly reached path vertex, including the final goal. `axis_slow` changes second-coordinate MOVEs to 3/2. `midpoint_pause` adds a 3/4 stationary pause when `(agent + from_state) % 11 == 0`. Every graph uses the same profile definitions and executor.

| Random60 profile | Original sum / makespan | GSES sum / makespan | Improved GSES sum / makespan |
|---|---:|---:|---:|
| Nominal primitive | 2085.75 / 77.25 | 2042.75 / 79.5 | 2043.75 / 79.5 |
| Axis slow | 2362 / 87.5 | 2341 / 90.5 | 2345 / 90.5 |
| Midpoint pause | 2172 / 79.5 | 2133.5 / 83.25 | 2133 / 83.25 |

The selected graphs reduce the completion sum on this reused case while increasing makespan under every primitive profile. That objective difference prevents a blanket improvement claim. In the separate lak41 nominal-primitive fallback pair, original and timeout-selected runs both give sum=16380 and makespan=826.25; their complete raw trace bytes and compressed hashes are identical.

## Occupancy, commitments and negative controls

`EVENT_RESOURCE_AUDIT.json` reports 27 successful graph/event/resource reconstructions. The independent root report `../r11_root_review/ROOT_GSES_EXECUTION.json`, pinned by `ROOT_AUDIT_BINDING.json`, also passed all 27. Its exact Fraction-based pairwise segment calculation examined 72,636 potentially close segment pairs after safe spatial rejection; it covered all agents from zero to makespan, including goal residence. It imported no candidate executor. The root audit separately checked type2 actual-ARRIVE thresholds, destination entry at 2/5, source exit at 3/5, midpoint state nonadvancement, and stationary TURN/STATION.

At time 1/2 in the genuine Improved GSES random60 midpoint-pause run, 57 MOVEs were active. A complete JSON snapshot was serialized and restored. Guarded same-graph continuation exactly reproduced all uninterrupted events and segments. The guard preserves already executed transitions and active MOVE identities, restricts changes to legal author type2 reversal families, protects committed incoming dependencies, and rejects cycles. A real author original-to-Improved reversal conflicting with a specifically protected transition was rejected. This establishes a finite commitment guard and real same-graph in-flight resume. It does not demonstrate a complete online optimizer-to-controller graph-switching loop.

Nine local corruptions were rejected: false midpoint state advancement; source exit at 1/2 instead of 3/5; source release during STATION; missing type2 binding; corrupted half-segment geometry; missing goal residence; altered active path prefix; an actual author reversal changing a committed dependency; and fake timeout adoption. The altered path-prefix control fails the unit-adjacency check, so it should not be read as an isolated test of every commitment rule. The root auditor additionally rejected two independent event corruptions and four geometry/coverage corruptions, including trajectories with safe endpoints but an interior collision. Some controls target overlapping failure classes; their counts do not denote independent scenario samples.

## Evidence and limits

The pre-execution 60 pins and pre-mechanics five pins still match. All 27 attempts succeeded without startup or execution failures. The 27 full graph/event/segment trace archives total 34,873,897 bytes; the largest is 4,164,872 bytes. A separate compressed checkpoint and all original receipts are included. `RESULTS.json` contains exact fractions and per-run hashes. `PUBLICATION_MEMBERS.json` is the explicit publication allowlist; expanded traces remain in the ignored main-workspace evidence directory.

This model has instantaneous velocity changes between affine segments and stationary holds. It does not model acceleration, tracking error, actuator dynamics or the original ARGoS controller. The independent geometry result is robot-to-robot disk clearance; this suite does not add an independent map-obstacle or dynamics certification. Traversable paths are inherited from the author artifact. Station service at every vertex is a constructed mechanism stress case, not an externally measured service distribution. Selected graph orderings were obtained under the author's original objective and are not reoptimized for the new primitive profiles.

The next justified interface step is a separately registered controller/optimizer integration that preserves the same actual release and commitment contract. A learned method should wait until that interface and a meaningful action-quality opportunity are established. R11 alone supports a transparent common execution precheck, not an externally comparable learned planning claim.
