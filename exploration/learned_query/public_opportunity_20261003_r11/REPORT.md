# R11: public opportunity and finite two-intervention value space

Completed 94 native runs across four new TRAIN families: 8 whole-run references, 26 complete one-intervention branches, and 60 fixed public two-intervention arms; 0 execution failures. Of the registered probe arms, 0 improve whole-task throughput strictly over both original condition pi0 and whole-run WAIT. The finite probe set improves throughput over pi0 in 1/4 families. A second intervention improves throughput over its matched first-only branch in 0/60 arms. These are TRAIN mechanism diagnostics, not a fitted model, held-out result, or an optimality claim.

| Family (map / scenario / offset / seed) | pi0 tasks | whole WAIT | best single | best pair | arms with task gain over both |
|---|---:|---:|---:|---:|---:|
| empty-32-32_scen1_offset448_train_111101 | 48 | 49 | 49 | 49 | 0 |
| empty-32-32_scen1_offset464_train_111102 | 41 | 40 | 41 | 41 | 0 |
| random-32-32-10_scen2_offset0_train_112101 | 48 | 48 | 48 | 48 | 0 |
| random-32-32-10_scen2_offset16_train_112102 | 51 | 51 | 51 | 51 | 0 |

Selecting each family's best registered probe retrospectively gives 189 tasks, versus 188 for fixed condition and 188 for fixed whole WAIT. This equals the 189-task envelope obtained by choosing the better reference separately per family. Thus one of eight single opportunities exposes a real +1 TRAIN task over pi0, and conditional policy selection may have learning potential. The data show no extra throughput beyond that reference envelope. The familywise retrospective selector has not been learned or evaluated on new families.

All task counts use the entire FIFO through H=128. The secondary objective is J=tasks−T/16385, where T is the sum of restricted completion times for the fixed first four tasks per agent (unfinished tasks contribute 128). RESULTS retains the summed interval bounds; a robust gain requires the lower bound of the J difference to exceed 0. Small midpoint differences whose interval contains 0 are unresolved. Arms and candidates are correlated interventions within a family, not independent replicates.

## Registered coverage and public action semantics

The run cap was 140; deterministic public selection produced 94 runs and was not filled to the cap. The condition baselines selected 8 opportunities, the first early (spent 0–7) and late (spent 8–15) slots per family. Exactly 1 selected opportunity has two visible candidates. There are 0 selected coupled opportunities: no candidate simultaneously blocked multiple distinct current heads and no blocked-head claim had multiple owners in the sampled condition strata. Two visible candidates, multi-owner/multi-head blocking, and two interventions are separate notions. This experiment does not validate combined blocking.

Each selected opportunity includes current WAIT and QUERY/SKIP for every visible candidate. SKIP binds the full (agent, move occurrence) pair and removes only that occurrence until accepted, delivered normal END. Current WAIT installs no skip state. Both forced actions and the live continuation use public state; the original physics, ownership/certificate rules, author World3 bridge, controller and count budget are pinned. Public task lineage is updated only after accepted END and successor-head revelation. No private future END or unseen FIFO task is used to select either intervention.

Each early/late anchor fixes six first WAIT/QUERY/SKIP × second QUERY/SKIP policies. The second event is the earliest eligible public decision with budget and a different complete identity. The early anchor also fixes three successor-triggered second-SKIP policies. Targets rank by exact public condition score, then agent and action ID, including zero scores in these forced diagnostics. No second point or action is selected from outcomes. All registered pair arms and empty coverage strata are retained.

| Second trigger | Registered arms | Second action actually reached | Positive task gain over same-first single | Robust J gain over same-first single |
|---|---:|---:|---:|---:|
| distinct | 48 | 48 | 0 | 5 |
| successor | 12 | 5 | 0 | 0 |

Unreached second actions: 7. These mean no qualifying public trigger occurred before the count budget was exhausted or H was reached; they are not successful forced WAIT actions. PAIR_REACHABILITY records budget exhaustion, public descendant heads and the actual first/second identities. Unreached branches are checked against their matched first-only full public/physical trajectory. A public descendant being revealed alone does not establish a visible legal query opportunity.

Among the 7 unreached successor arms, 4 had public descendant heads revealed before budget exhaustion but still no legal successor-trigger candidate; 3 had none revealed before exhaustion. Later revelation alone cannot recover already spent budget. This describes observed public availability rather than attributing the result to a private future event.

Across all 94 full trajectories (including repeated references), 180 public decisions in 84 arms have multiple candidates; 0 decisions in 0 arms meet the registered coupled-blocking predicate. This is a descriptive repeated-trajectory census, not additional independent coverage.

## Secondary service effects and persistence

| Family | Robust J-improving probe arms vs pi0 | Robust J-improving probe arms vs both references |
|---|---:|---:|
| empty-32-32_scen1_offset448_train_111101 | 4 | 4 |
| empty-32-32_scen1_offset464_train_111102 | 0 | 0 |
| random-32-32-10_scen2_offset0_train_112101 | 7 | 7 |
| random-32-32-10_scen2_offset16_train_112102 | 3 | 0 |

The following maximum-J choices include both references and are retrospective descriptions of this finite set. They are not deployed selectors; ties use the policy name only to choose a reproducible representative. T gains are fixed-first-four restricted-time sums in seconds, not per-task averages.

| Family | Retrospective maximum-J arm | task gain vs pi0 / WAIT | T gain interval vs pi0 | T gain interval vs WAIT |
|---|---|---:|---:|---:|
| empty-32-32_scen1_offset448_train_111101 | pair_1_SKIP6_SKIP_distinct | 1 / 0 | [42.206238, 42.206329] | [1.268228, 1.268320] |
| empty-32-32_scen1_offset464_train_111102 | cf_1_QUERY4 | 0 / 1 | [-0.000041, 0.000041] | [4.395465, 4.395546] |
| random-32-32-10_scen2_offset0_train_112101 | pair_9_SKIP5_SKIP_distinct | 0 / 0 | [6.988960, 6.989052] | [20.621247, 20.621339] |
| random-32-32-10_scen2_offset16_train_112102 | WAIT | 0 / 0 | [5.319154, 5.319256] | [-0.000051, 0.000051] |

Negative effects are retained: random-32-32-10_scen2_offset0_train_112101 / pair_9_QUERY5_SKIP_distinct changes throughput by -2 relative to its same-first single and pi0; the second legal action is SKIP on m-13-23 at opportunity 10 with remaining budget 7.

The eight complete single opportunities include 1 with task headroom over pi0 and 0 over both references. OPPORTUNITY_VALUE_SPACE preserves every zero-space opportunity. Full task-service record equality and gained/omitted query identities are in RESULTS; fixed-first-four timing is reported separately from whole-FIFO throughput.

Across all arms, 58 SKIP occurrences were installed; 58 cleared immediately after the matching accepted normal END. Their original identities reappeared in raw candidate visibility 162 times while remaining masked. 44 installations have a later distinct occurrence of the same agent visible; 58 lie in branches querying identities absent from that family's condition run. SKIP_LIFETIMES reports per-installation budget at installation/clear and the next actual QUERY. This proves retained count budget and changed allocation where observed; it does not price production CPU or network cost.

The maximum simultaneous skip set is 2 identities, reached in 1 arm. All 86 intervention arms finish with [16] queries, while whole WAIT uses zero. The retained budget is eventually spent; these results concern changed allocation and service, not reduced total query counts.

## Validation, failures and provenance

Independent Decimal physics/controller/owner/FIFO and exact rational policy audit: PASS 94 episodes. Prefix and fixed-tail replay: PASS; 38 same-action or unreached full-trajectory controls. Negative controls: 22 rejected. Root-owned independent raw value-space/lineage/score/trigger audit: PASS 94 runs. ROOT_RECONCILIATION compares all 94 independently computed throughput, timing interval, J and reachability results. These independent checks include candidate lists before/after masking, exact scoring/ties, no forced QUERY without a legal target, actual budget consumption, and accepted-END-only skip clearance.

Before scientific runs, the initial random scenario 1 offsets were rejected because the file has only 461 rows. The preserved preflight documents the correction to separately pinned official scenario 2 offsets 0/16, with seeds and experiment cap unchanged. The first guessed ZIP URL returned 404; the correct [official MAPF benchmark archive](https://movingai.com/benchmarks/mapf/random-32-32-10.map-scen-random.zip) was then downloaded. Both the failed attempt and final input hashes are retained. The two empty families use original scenario 1 offsets 448/464. Family keys include map, scenario identity, offset and seed. NOVELTY_PREFLIGHT checks prior registered seeds/task IDs and scenario row groups.

An auditor-only missing re import was corrected before any probe outcomes or pair audits; AUDITOR_IMPORT_FIX_BEFORE_PROBES records both hashes and the approved audit-supervisor restart. Registered native/runner/pipeline/contract and experiment behavior were unchanged. This exception is explicit in final source-pin verification. R7–R10 frozen artifacts and original production headers remain pinned. No model was trained and no result-selected sample or horizon extension was run.

Raw records are preserved exactly once in 5 compressed archives (564 files), each below 45 MB, with verified member SHA256. Build/runs/audits caches are excluded from the publication whitelist; archive and frozen source hashes permit reconstruction with the pinned external author dependencies.

## Consequence for the next learning target

The +1 task over fixed pi0 is small but real TRAIN headroom, so these results do not rule out learning a conditional choice among condition, WAIT and persistent SKIP. They do not establish that public features can generalize that choice: the familywise best throughput merely reaches the condition/WAIT reference envelope, and no model or held-out family was tested. A next learning study should preregister that modest selection target and compare with both fixed references and explicit public selectors; increasing model size alone is not supported. Robust service-time effects under a throughput constraint offer a separate target. Keep the zero-space and unreachable opportunities, and do not recast finite diagnostic maxima as deployed performance.
