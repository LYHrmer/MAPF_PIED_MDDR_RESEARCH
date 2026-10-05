# R20 Improved GSES: native weight boundary and common execution witness

The original author optimizer is now callable inside the same guarded continuous event executor used in R19. It has a demonstrated legal-switch execution chain, but remains qualified only as an explicitly declared integer/unit-gap ordering surrogate. Two new exact counterexamples prevent claiming arbitrary continuous-weight equivalence.

The preregistered native checks gave:

| Case | Author returned objective | Fraction minimum | Finding |
|---|---:|---:|---|
| Integer current delay, unit type2 | 17 | 17 | optimum on this case |
| Integer future duration, unit type2 | 16 | 16 | optimum on this case |
| Binary-exact fractional type1, unit type2 | 101/16 | 99/16 | nonoptimal |
| Integer type1, type2 gap 8 | 31 | 28 | nonoptimal |

These cases enumerate all two legal orientations and retain the full original author outputs. The failure is in extending the search's unit-separation semantics to unsupported weights; it is not evidence that the original unit-time paper claim is false. The native relaxed branch/termination logic uses a nonnegative arrival difference and the heuristic adds one. Neither float storage nor rescaling alone changes that algorithmic assumption. See `PHASE1_REPORT.md` and `valid_nominal_schedule/`.

The common adapter uses public END history/current residuals, rounds durations into integer ticks, calls the unchanged Improved GSES ELF, lifts the complete proposed family orientation and invokes the unchanged R19 guard. The executor always enforces actual dependency END releases and immutable active actions. Thus the surrogate's weak timing semantics cannot authorize a premature physical dependency release.

Four transport micro-episodes varied no query/POSITION and capture age 0/.25. They all completed with sum completion `21.254785268177695`, the same final order, and full continuous point audits passing. Integer quantization made the four native inputs exactly identical, so they used one author call and three exact reuses. Both native orientations had objective 14. This is a retained zero result, not a POSITION benefit.

A separate preregistered positive mechanism case fixed A's speed to .25 and B's speed to 1. A's first END at time4 delivers its observed duration4. At 4.5 the policy captures A2 at progress .125; it is delivered at4.75. The author receives public duration predictions only, and changes `dg_agent0_0` to B-first. Full native enumeration gives forward objective36 and reverse24; the original author returns24. The guard passes while A2 continues unmodified from4 to8. B3 starts at4.75, B4 ends6.75, and A3 starts at8 after that dependency is complete.

| Constructed common-executor arm | A completion | B completion | Sum completion | Makespan |
|---|---:|---:|---:|---:|
| Original author surrogate + guard | 24 | 8.75 | 32.75 | 24 |
| Registered keep-parent control | 24 | 20 | 44 | 24 |

Both arms have one identical charged POSITION capture and complete continuous MOVE/WAIT/GOAL_HOLD audit coverage. Their private action speed profiles are identical by agent/action key. The difference is a legal ordering change followed by actual events. It is a constructed execution witness, not a learned-query benefit, heldout estimate or standard-map comparison. The oracle's objective24 is the quantized relative arrival objective; it is not confused with the actual absolute-time sum32.75.

POSITION adds no residual information in this particular witness: the delivered END history already gives duration ratio4. At decision4.75, elapsed since A2 START is .75, so the END-only residual is `4-.75=3.25`. The dated POSITION projection is likewise `(1-.125)*4-.25=3.25`. The intervention is author-chosen new direction versus keeping the old graph; both arms purchase the same query. This case establishes neither an incremental POSITION value nor a need to query, and no additional trial is added to manufacture such an effect.

The ledger contains ten original-program invocations: four initial input-constructor failures, four corrected phase1 searches, one unique transport search and one positive-switch search. The four early failures were our equal-crossing-timestamp input error; they never reached Astar and remain unmodified. A separately hashed amendment corrected only B's nominal constructor timestamps. There were six actual author searches, three cache reuses and one zero-search parent control. All source files, registrations, raw outputs and failed attempts are retained. No upstream or frozen old source changed, no large matrix was run, and no commit/push was made by this worker.

Research-mentor decision: retain Improved GSES as the closest executable external ordering baseline and state its native timing contract. Do not present this surrogate as a like-for-like continuous optimum or spend a full benchmark budget on that claim. A future common comparison must preregister the quantization, one-tick gap, equal observer information, common adoption failures and solver-time budget. An exact continuously weighted alternative would require a separately labelled algorithmic extension and new correctness tests; this round deliberately preserves the original author result.

`COMMON_CONTRACT.md` contains the callable API and mapping. `FINAL_AUDIT.json` verifies current source/input/cache/evidence integrity with zero new solver or physical runs. `FINAL_MANIFEST.json` covers this worker's files only and excludes the independently produced `root_review/`. Point collision checking is not a robot-footprint, acceleration or ROS validation.
