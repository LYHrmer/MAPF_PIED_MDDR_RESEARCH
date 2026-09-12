# C25：固定目标与宿主干扰建设咨询

2026-09-12；根实际调用并独立分析。CONSTRUCTIVE / NONBALLOT，不是正式审稿票。提示为同号 CONSTRUCTIVE_PROMPT；仅发送该自包含问题，未给Claude文件/浏览/写入工具，不冒称其全读主稿。

## 实际调用

首次沙箱 exec19266 起始 chunk5606e8，终态 chunkd2063f/exit1，API FailedToOpenSocket、modelUsage空、无科学意见；原失败JSON单独保留。依工具规则正常升级同题，exec52776 起始 chunk975913，终态 chunk2ae2bb/exit0。实际 terminal_reason=completed、stop_reason=end_turn、is_error=false，客户端 modelUsage=claude-opus-5/firstParty，session_id=ca14a36e-064e-4b79-8b39-a900daf77eab，duration_ms=111819，费用0.23824125 USD。正文有END-C25-20260912，原raw完整保留，不以调用成功等于设计成立。

## 完整原文

<!-- BEGIN_C25_RESULT -->
# C25 response

## 1. Is there an original-law-preserving intervention? No, and the gap is physical, not statistical

Any non-vacuous confidence statement about the unchanged Δ under the unchanged P must be driven by one of exactly three inputs: (a) a factorization of the conditional law across predeclared boundaries (the P30 cluster route); (b) a *proven deterministic* bound V\* on predictable increment spans (the Doob route); (c) a transport identity to a modified law. Each of these reduces to a claim about the machine, not about the estimator.

- (a) requires that the host state carried across each boundary be, conditionally on X, independent of all later blocks' outcomes — i.e. a **regeneration event** at each boundary: the process forgets thermal, cache, allocator, OS-load and timing-service state in a verified sense. On a serial, non-restorable host this is precisely what is stated to be unavailable. Order randomization, restarts, cores, days and undetected autocorrelation are not proofs of it.
- (b) requires a **quantitative sensitivity certificate**: an upper bound on how much a carried host variable can move the later conditional expectation of Δ, propagating through elapsed time → timeout decision → returned path → virtual publication time → Q. Absent a calibrated runtime object (explicitly unavailable), the only defensible span for a variable that can affect all later blocks is 2Λ, and V\* = (2Λ)² returns a radius Λ·sqrt(2 log(2/α)), which exceeds the a priori bound Λ.
- (c) requires E\_{P'}[Δ | X] = E\_P[Δ | X]; a plausible reset is not that proof.

The seed argument does not help and should be named explicitly: Q is a measurable function of the registered seeds **and** of a shared, unmodeled host argument. Writing d\_b as a function of independent seeds plus a common argument does not factorize the joint law; independence of the seeds is a statement about a marginal sub-σ-field, not about the σ-field in which Δ is measurable.

Missing premise, stated exactly: *either* a verified boundary-wise conditional-independence (regeneration) event for the carried host state, *or* a verified deterministic bound on the influence of that carried state on the remaining weighted score sum. Both are physical claims about this computer. Neither exists. The correct status is therefore **INFERENCE\_UNAVAILABLE for the concentration claim**, not UNESTIMABLE: all required scores exist, θ is well defined, and Δ remains a lawful complete-roster descriptive statistic. The only assumption-free valid interval is the deterministic [−Λ, Λ]; it may be *reported* as a bound but, per the contract, may not be used to declare the design complete.

## 2. Entire-campaign replication

**Mathematical validity and preservation of θ.** Let campaign k reproduce every original block, order law, state propagation, w\_b and E\_b, and let Δ^{(k)} be its complete statistic. Unbiasedness needs only that each campaign's *marginal* law equal P: then E[Δ^{(k)} | X] = θ for every k, so the average Δ̄\_K targets **precisely the original θ**. This is the key separation: identity of marginal campaign laws preserves the estimand; independence across campaigns is needed only for the radius. The roster, weights and windows are untouched, so this is a change of **observation plan**, not an expansion of the repetition roster — adding repeat indices inside a block would alter w\_b and hence redefine θ, which the amendment does not do. P is preserved *within* campaigns by construction; what is newly assumed is a law *between* campaigns.

**What must be true.** (A1) *Campaign-start law transport*: the state from which each campaign begins must be a draw from one fixed law, and that law must be the one under which θ was defined. The original campaign began from a single realized, unrepeatable host state; if a new fixed start-preparation is introduced, the resulting law is P′ and equality E\_{P′}[Δ|X] = E\_P[Δ|X] must be argued, not assumed. Equality of each block's marginal law under P and P′ is sufficient and stronger. (A2) *No cross-campaign interference*: residual carryover between consecutive campaigns (thermal, cache, allocator, log/disk growth, machine aging) must be absent or provably irrelevant, otherwise campaigns are neither independent nor identically distributed and only a mixing certificate — which we do not have — could substitute.

Neither A1 nor A2 is verified on this host, and I do not claim they are implementable here. Conditional on A1 and A2 the concentration statement is immediate, since |Δ^{(k)}| ≤ Λ deterministically: for i.i.d. campaigns,

  |Δ̄\_K − θ| ≤ Λ·sqrt(2 log(2/α)/K) with probability ≥ 1 − α.

This is non-vacuous only when K > 2 log(2/α); I do not select K. Note the amendment buys independence at the *campaign* level — the operationally meaningful unit — and never asserts block-level independence.

## 3. The two-corner obstruction is fatal for deterministic procedures

Let B be an unobserved Bernoulli(p) host state with d = (+U\_b)\_b if B = 1 and (−U\_b)\_b otherwise, so Δ ∈ {+Λ, −Λ} and θ = (2p−1)Λ, p unknown. A deterministic procedure is a pair (I₊, I₋). Coverage at p is p·1{θ(p) ∈ I₊} + (1−p)·1{θ(p) ∈ I₋} ≥ 1 − α. Hence θ(p) ∉ I₊ forces 1 − p ≥ 1 − α, i.e. p ≤ α. Contrapositive: **whenever the observed corner has probability exceeding α, its θ cannot be excluded.** So I₊ ⊇ closure{(2p−1)Λ : p > α} = [−(1−2α)Λ, Λ] and symmetrically I₋ ⊇ [−Λ, (1−2α)Λ]. Consequences: every valid interval has length ≥ 2Λ(1−α) at either corner — the vacuous [−Λ, Λ] is within a factor 1/(1−α) of optimal; and for α < 1/2, I₊ contains a nonpositive point and I₋ a positive point, so **no directional conclusion about sign(θ) is attainable at either corner, for any roster size, weights, or window**. This strictly strengthens "a single cluster may give no directional information": the full roster with arbitrary within-block dependence and one binary host variable already forbids directional inference, and it shows the P30 span 2Λ is attained, not merely conservative.

Scope limits, stated plainly: bounded-score compatibility is **not** proof that a legal MAPF source realizes these corners; the family is admissible under the declared constraints, so the theorem is an obstruction to procedures required to be valid under boundedness plus arbitrary dependence alone — it does not assert the real experiment is uninformative. Randomization does not evade it: validity forces the exclusion probability at the observed corner to be at most α/p, so expected length at the + corner is ≥ 2Λ[(1−α) + α log α], and a valid randomized rule can declare θ > 0 at θ = 0 with probability at most about 2α — a level statement with no guaranteed power, not an escape. Observed host metadata helps only through a *verified* restriction linking observables to the host state; metadata independent of B changes nothing, and asserting identification of B is a new probability assumption requiring proof — the same missing certificate as in §1.

## 4. Recommendation

Do not attempt a within-campaign fix. Adopt, as the narrowest amendment, **entire-campaign replication** with the original campaign re-declared as campaign 1 and a fixed, predeclared start-of-campaign preparation applied identically thereafter; report Δ̄\_K with the radius above **explicitly conditional on A1 (start-law transport, including that the original start was a draw from that law) and A2 (no cross-campaign carryover)**, and report the assumption-free [−Λ, Λ] alongside. Unresolved evidence requirements: a start-state preparation argument or marginal-law transport proof, and a cross-campaign carryover argument. If A1/A2 cannot be evidenced on this single serial host, the honest reported status remains INFERENCE\_UNAVAILABLE for the concentration claim, with θ defined and Δ reported descriptively. I do not adopt the amendment or choose K here.

END-C25-20260912
<!-- END_C25_RESULT -->

## 根直接取舍（非正式审稿）

1. 接受数学核心：只要每个完整campaign具有原P的相同边缘分布，campaign均值仍以原theta为期望；获得所给集中界还要跨campaign独立。扩大观察计划不等于现有固定roster已经授权扩展，也没有当前主机恢复同分布/独立的证据。本轮不采纳campaign重做。
2. 接受二点族确定闭区间下界。正角必须包含[(2alpha−1)Lambda,Lambda]，负角对称；alpha<1/2时不能据任一角确定符号。此是仅有有界性/任意依赖假设下的障碍，不是合法MAPF源的可达反例，不能宣布实际研究没有信息。
3. 拒绝“只有全范围区间有效”：原文自己给出长度更短的有效必含集合，且其他已有结构会带来其他有效程序。拒绝“恰好三种信息来源”的穷尽性主张；它没有给一般定理。
4. 2Lambda可作一个全局潜变量增量的跨度；不能无额外分解就把任意完整Doob序列的平方跨度和自动认定为(2Lambda)^2。按整个统计量的一步揭示可用全局界，但这不是所有过滤下的证书。
5. 随机化角点排除概率至多alpha/p的积分可以给其所写期望长度下界；在theta=0时正角条件的错误正结论概率至多2alpha，而无条件错误率仍至多alpha。原文“about”不够精确，不将条件/无条件混用；没有证明随机化在所有意义无用。
6. 不接受末段将原campaign重新宣布为campaign1的实操建议。本研究尚未运行任何campaign；新准备会改变起始分布，不能靠重命名保P。原文“original campaign began from a single realized...”也不符合本任务事实，源于顾问自行补前提。
7. 当前实际建设方向是独立比较显式P_model计算模型：所有在线工作确定性计费，真实host耗时另报，因而主虚拟Q不依host。若采用，须明示theta的执行环境分布变更，不称与原real-host theta等值；这一方案交C26及实际后端证据进一步构造。

本件支持缩小不成立的统计路线，不关闭G3/G6或主目标；无实现/测试/仿真/数据/参数赋值。原始调用结束，无活C25句柄。
