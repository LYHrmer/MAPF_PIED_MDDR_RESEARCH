# S1 continuous occupancy and release interface

Exploratory, declared-model analytic fixture. This is project-owned code, **not
WinkTPG, SADG, or a reproduction of either author implementation**.

Run the finite algebraic check (standard library only):

```bash
rtk proxy python3 -B verify.py
```

It checks continuous straight sweeps, a conservative turn envelope with an
exact intermediate collision witness, fixed-priority conflict additions,
dependency cycles, time infeasibility, and release against the complete
permitted suffix including permanent goal occupancy. It reports analytic
feasible completion times for one allowed zero-error realization. No solver,
world, random draw, training, or empirical cost measurement occurs.

`release()` consumes a delivered observation-bound message, not a timer or
private truth. Unsupported suffixes fail closed. Its caller must provide an
authenticated, deduplicated source, enforce the bound/controller contract,
and keep the suffix commitment after release. Those production integrations
have not been executed. Condition labels alone are not physical evidence.

The whole-window bound follows from declared unicycle kinematics with ideal
primitive tracking and bounded initial pose error. These are not LIMO data.
The current full-task fixture contains straight/acceleration/braking/wait/goal
hold. Turning has geometric coverage and a counterexample, not a complete
multi-turn task or certified arbitrary controller.

Reuse: R16/R17 author-core qualification and feedback/paired-cost contracts are
retained, not re-run. This small new interface isolates the genuinely missing
spatial-to-release operation; it does not clone an optimizer or old worktree.

Detailed assumptions, all constraints and negative cases:
[main example](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_MINIMAL_EXAMPLE_20261016.md).
[main research plan](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md).

No scientific runtime is authorized by this README or by the old G2c permit.
