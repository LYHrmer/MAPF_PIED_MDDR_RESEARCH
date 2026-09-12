# C27：论文贡献与实验论证建设咨询完整回执

2026-09-12；根实际调用，CONSTRUCTIVE / NONBALLOT。仅发送同号PROMPT的自包含设计问题；无工具/技能/MCP，不冒称Claude全读主稿。

唯一正常升级调用exec31205，终态chunkf1aa67/exit0。实际is_error=false、terminal_reason=completed、stop_reason=end_turn；客户端modelUsage为claude-opus-5/firstParty；session_id=f70957f2-dac3-401b-9923-fa85f7d4e700、duration_ms=74271、费用0.15826625 USD。完整原stdout另存同号RAW_RESPONSE.json。正文1361空白分词，真实END-C27-20260912，不因成功返回计设计通过。

## 完整原文

<!-- BEGIN_C27_RESULT -->
## 1. Contribution, mechanism chain, and claim types

**Primary contribution (algorithmic design + hypothesis).** A MOVE-preserving execution wrapper in which a single reservation centre *selectively purchases* in-motion progress evidence in order to retire swept spatial resources *behind* a body with bounded transverse error, and a query policy D that chooses whom to pay for using only paid shared knowledge. The claim is not "observations help"; it is: **under a declared population and a declared cost law, selective paid retirement changes true full-window task service Q by a measurable, signed amount, and we identify the regimes where that sign is positive.**

**Supporting contribution (systems engineering + protocol).** A cost-complete evaluation law for paid-observation execution layers: every online operation (query scoring, geometry events, retirement, messaging, memory) is charged, and the internal comparator R is given *identical* capability, information, envelope Z, cap and early-release power. This is what makes the sign of theta interpretable rather than an artifact of an under-equipped baseline.

**Mechanism chain (minimal, each link falsifiable).**
X=u+s·e+z+F with bounded z gives envelope Z → reserved swept set U(q,b) from retired progress q to cap b → some pending MOVE/extension requests are admissible but blocked only by potentially releasable nonterminal resources of an active transaction → D scores and selects one such transaction → paid committed proof q ≤ current s → retirement of the strictly-behind portion of U within the *same* MOVE → blocked request granted earlier → earlier start → earlier task/cursor consumption → more completions inside the fixed horizon → **minus** observation price, scoring cost, geometry cost, messages, memory, and any stalls induced. Net service is the *last* link, not an assumed consequence of the first.

**What is a theorem (provable now, safety only).** (T1) *Retirement soundness*: given the installed monotone cap, the shared envelope Z and a committed proof q ≤ s, the retired portion of U(q,b) cannot be reoccupied by that body within the MOVE. (T2) *Invariant preservation*: single-centre ownership plus retirement preserves the reservation disjointness invariant, hence no wrapper-induced collision; each original MOVE, task, slot and endpoint is preserved, and no detour, fake goal or replacement planner exists inside the wrapper. (T3) *Fence safety*: the GROUP\_PREFIX future-resource fence is not released until all members finish and paid retirement completes.

**What is explicitly not claimed.** No liveness, no starvation bound for D while positive scores persist, no global throughput improvement, no unconditional dominance over R, E0 or the external systems. D's lack of a starvation bound is reported as a *known property of the policy*, not as an open question the experiments will resolve.

**Novelty posture.** Because Kim TII 2026 and the two related AI/RAS papers have verified metadata but unavailable mechanism texts, and because PIE-D, Hoenig/ADG, Zhong/Rossi/Shell, B-UAVC, Shahar, S2M2, WinkTPG, SCALE and MAPF-X each supply adjacent ingredients, the paper claims **no novelty exclusion**. It claims a *specific composition plus a measured, cost-complete signed effect*: paid in-motion retirement of transverse-error swept reservations selected by a blocked-request query policy, evaluated against an equally-equipped stable round robin. That claim is publication-credible even if a near-neighbour independently holds part of the composition.

## 2. GROUP\_PREFIX decision

**Decision: common platform, identically enabled for D-S, R-S and E0, with a predeclared GROUP-off replicate of the whole internal matrix.**

Rationale. Making GROUP a D-only extension would silently give R and E0 less capability and would make theta a mixture of two mechanisms — unacceptable. Removing it entirely would drop the regime the study most needs (groups whose full original edges mutually block their starts) and would weaken the comparison to H19, which carries whole-MOVE caps. Common platform preserves fairness and keeps theta attributable to query selection at fixed platform configuration.

**What identifies D's incremental effect.** D-S vs R-S *at a fixed GROUP setting* (on, and again off). The 2×2 D/R × {spatial release, cap-held-until-END} ablation, with F\_cap omitting unused retirement work, isolates whether any benefit comes from retirement at all or merely from cap granting.

**What does not identify it.** GROUP-on vs GROUP-off at fixed query policy is *not* a D contribution — it is a platform contrast confounded with stall risk, and is reported as such. Any D–H19 gap is **system-level** and cannot be attributed to query selection.

**Costs and risks, reported not hidden.** GROUP can itself create delay and permanent stalls; stalled runs keep their actual Q and full denominators and are never excluded. No success-selected scenarios.

## 3. Figures, tables, matrix, refutation

Symbolic axes only: congestion c, observation price p, envelope width |Z|, task density d, agent count n, group-conflict rate g.

- **T1 Arms/systems.** D-S, R-S, E0, F\_cap 2×2 cells, H19E0, H19R-S (both mandatory, predeclared, simultaneous), native PIE-D on its own fidelity/domain track (collisions outside its physical-error domain are *not* evidence for D).
- **F1** Mechanism schematic: U(q,b), retirement, fence.
- **F2 (primary)** Paired full-window Q per preregistered block; weighted theta = E[Q(D-S) − Q(R-S)] with interval, independence from the declared input/execution law, not arm order. D-S vs E0 shown on the same panel.
- **T2 Cost ledger.** Simulated computation per online operation, real CPU/wall/memory separately; observation count and price; message and byte counts; G vs N first-use, reuse, preprocessing, invalidation, failed speculative work, scans, sorting, bit complexity; D's explicit reference scan charged as implemented. Any incremental reverse index appears only as a *costed proposal*, never as an implemented result.
- **F3** 2×2 mechanism ablation.
- **F4 Negative regimes.** theta vs p, |Z|, c, d, g — monotone hypotheses fixed before results.
- **F5 Scalability.** theta and cost vs n and map size; wait decomposition.
- **F6 (optional)** LIMO transverse-deviation traces against Z: mechanism evidence that z is real spatial deviation, never a Q claim.

**Refutation patterns.** Claim "paid retirement can be net-positive" is refuted if theta ≤ 0 across the declared population with intervals excluding benefit. "D's selection matters" is refuted if D ≈ R once both are equally equipped, or if the 2×2 shows benefit without spatial release. "Paying is worthwhile" is refuted if **D-S beats R-S but loses to E0** — explicitly declared in advance as falsifying the practical value of observations. Scalability is refuted if the sign of theta flips against n or if cost growth cancels service gain. Horizon is never retrospectively cut; a local earlier-service witness is not accepted for a full-window claim. Unknown Q makes the required comparison unestimable and is reported as such.

**If theta ≤ 0**, the paper still stands on: T1–T3, the cost-complete law, a mapped negative result (where paid observation does not pay and why), the G/N geometry cost characterization, and a possible E0-dominance finding — a useful, publishable negative.

## 4. Evidence-to-review checklist

**(A) Required now for a coherent design.** Declared population and weights; fixed roster, virtual observation windows and horizon; paired blocks; independence law; equal capability for R/E0; fixed sensitivity axes; preregistered external comparison; failure-accounting rule. **Also required now, not deferrable:** the finite-instruction/host-elapsed conflict is a known contradiction, so the paper must adopt a qualified deterministic simulated-computation law and scope theta *to that law*, never asserting equality with real-host deployment.

**(B) Deferred until legal implementation.** Backend qualification of the successor compute law; official PIE-D/LaCAM entry provenance with transparent shared repairs and adapters; H19 adaptation record; LIMO calibration of z against Z.

**(C) Hypotheses, not entrance requirements.** Sign and size of theta; external superiority; regime monotonicities; GROUP net effect.

**Containment.** Closed enumeration, one page per claim, a freeze date, a versioned appendix, and archived artifacts for everything else — missing full texts of near-neighbour work bound the novelty claim; they are not fatal.

**Title.** *Paying for Progress: Selective In-Motion Evidence for Retiring Transverse-Error Reservations in Lifelong MAPF Execution*

**Contribution paragraph.** We present a MOVE-preserving execution wrapper for lifelong MAPF with bounded transverse tracking error, in which a single reservation centre selectively purchases committed progress evidence to retire swept resources behind a moving body within one original MOVE. We prove retirement soundness, invariant preservation and fence safety, and claim no liveness or unconditional throughput improvement. We evaluate a blocked-request query policy against an equally-equipped stable round robin and an observation-free variant under a cost-complete law charging computation, communication, geometry and memory, with mandatory external comparators, and we predeclare the regimes and patterns that would falsify each claim.

END-C27-20260912
<!-- END_C27_RESULT -->

## 根独立分析与取舍

1. 采用一条主要机制链：付费取得进度→安全退休→请求可能提前准入→实际任务服务；每一箭头有额外条件，全E净效应待检。拒绝把任务/cursor消费作为真实Q的必要前提：现稿真实任务服务可先于READY或逻辑消费。
2. 保持GROUP为当前共同平台，D/R/E0同能力；不同GROUP设置下的比较可解释机制，不能把本咨询建议的整矩阵GROUP-off复制立即升级为必跑新规模。额外因子须证明辨识必要性且事前登记，防无目的倍增实验。
3. D/R主量仍Σw_b(Q_D−Q_R)/E_b，顾问F2漏E的表达不用。效应差不会再减一遍费用奖励分；费用已通过模拟排队影响Q，实际工作向量另报。
4. 不把“没有已证明饥饿上界”改称“已经证明不存在上界”。局部退休声称不能替代全不变量证明；P2需要未来所有新cap先预留以及END/交接覆盖，不能仅单中心+q≤s即自动宣布全安全。
5. 新颖性未排除时缩小断言是必要的，但不是“组合+测量一定可发表”的证据。不保证负结果论文成立或录用；原文“publication-credible/paper still stands/useful publishable negative”只作建议，不作结论。
6. 不预设效应随拥堵/误差/价格单调；失效、队列和策略交互可非单调。未发现显著差不等于等效或被反驳；“D≈R”需要事前实际等效界和有效推断，本咨询未提供。
7. 两个外部系统同报、E0必报、全窗口固定、失败/未知不删行和成本分账继续保留。D>R而D<E0只否定本制度下净购买价值，不推出所有主动观察无用。
8. 同意把源证据、设计定义、实现资格和待检结果分层，拒绝将官方源身份/许可及已知源语义缺陷全部移到实现之后。未来build/运行检验可后置；现时已知矛盾必须实质修复。
9. “一页一主张”作为可读性目标，不设按日期强行freeze或跳过承重审查。根采用有限义务清单与定点证据，停止没有新决策的泛检索/报告增长。

原调用已结束，无本题活句柄。仅科学建设材料；未实现/伪代码/测试/仿真/数据/保护参数赋值，不修改旧件或自动更新资格门。
