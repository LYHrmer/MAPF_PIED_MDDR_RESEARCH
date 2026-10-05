# Four new author searches and the weight boundary

The unchanged Improved GSES author program reaches the independent optimum on the two preregistered integer-duration, unit-type2 cases. It returns a nonoptimal orientation on both preregistered weight counterexamples. These are graph mechanism cases, not performance benchmarks or a claim about the paper's original unit-time domain.

| New valid input | Type1 durations | Type2 gap | Author status | Exact returned objective | Exact best objective |
|---|---|---:|---|---:|---:|
| p01 | integer current delay | 1 | Succ | 17 | 17 |
| p02 | integer future delay | 1 | Succ | 16 | 16 |
| p03 | binary-exact fractions | 1 | Succ | 101/16 | 99/16 |
| p04 | integers | 8 | Succ | 31 | 28 |

`valid_nominal_schedule/PHASE1_RESULTS.json` contains every result. The independent standard-library `Fraction` oracle enumerates both legal orientations, calculates full DAG longest paths and sums all three terminal arrival times. Every returned graph preserves the supplied type1 edges and belongs to the enumerated family. The third agent has a declared fixed downstream release dependency; it is a graph-level example, not an undeclared geometric collision.

The author's relaxed termination/branch test compares arrival differences to zero, while its heuristic uses a unit separation. On p03, relaxed A3=1 and B2=1.25 are ordered but do not satisfy the required one-unit gap. The returned forward graph costs 101/16, whereas the reverse graph costs 99/16. On p04, relaxed A3=3 and B2=4 are ordered but violate the supplied gap 8; the returned forward graph costs 31 and the reverse costs 28. Fractions in p03 have power-of-two denominators and are exactly representable by the author's float type. This excludes decimal roundoff as the explanation for these two examples; it does not diagnose every possible upstream numerical behavior.

The first four program invocations failed during input construction because the adapter supplied equal crossing timestamps. They never entered Astar. Their original inputs, registration and stdout remain under `inputs/` and `calls/`. `schedule_fix.py` separately registered the correction: B's nominal timestamps are shifted by four while coordinates, explicit edges, weights, legal directions and objectives remain identical. The corrected registration SHA256 is `cfc64c2bdba19a018fd1f9cabfd449a6854dd6c33e318b1683743c83e6542d82`. There are eight program invocations so far, of which four reached the author search. None were retried silently.

Author commit: `25fb931eff03f1cce23a22a68ab42b7533f85ab3`. Existing R13 adapter ELF SHA256: `b5e918f8913baca71a7b189e21e76bf3d7bfb41ec8042ee5ab306a52f109700c`. The existing adapter calls the original Improved GSES search with a 16-second limit; the external watchdog is 20 seconds. All 43 pinned upstream source files and the ELF were checked before the corrected calls. No author source changed.

**Qualification decision:** the native integer/unit-gap ordering model can be connected to a common guarded executor as an explicitly labelled surrogate. Arbitrary real durations and arbitrary type2 margins are not qualified by this implementation. Scaling time by 60 can make a selected set of rational durations integral, but it also changes the meaning of the hardcoded one-unit separation; it does not make the author's original search solve arbitrary weighted SADG action constraints. The continuous SADG .01 optimization margin is likewise not an interchangeable unit gap.
