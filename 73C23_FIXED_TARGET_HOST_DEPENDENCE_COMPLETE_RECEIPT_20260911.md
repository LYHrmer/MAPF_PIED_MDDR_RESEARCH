# 73C23：固定配对目标与宿主依赖——完整咨询回执

2026-09-11，/root/successor_statistics；NO-SKILL / CONSTRUCTIVE / NONBALLOT。这是一次新有界统计建设咨询，不是正式逻辑审查；根须另行独立判断。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 1. 固定提示与实际运输

唯一提示73C23_FIXED_TARGET_HOST_DEPENDENCE_CONSTRUCTION_PROMPT_20260911.md先由apply_patch创建；af905f核SHA256=00cdabfb564e6659adcc31ad5782da309a27e76c8cde830e295614fe078bfdf0。依据为全文读完的20260911交接、A4、C8SR、A3及C22回执和73完整§11–12；1d0e24实核主稿SHA256=9e06199cc6045ddd750b861b3091ec239c7c6ff2ae7eeaebbdd0e7fde61ec113。先独立推导固定目标的簇/Doob方案，再提交C23；提示未包含任何实验赋值或载荷。

既有A3/C22及本轮统计论文curl沙箱7号连接失败支持正常require_escalated审批；没有尝试规避网络限制或防护拒绝。唯一命令：

```text
rtk proxy timeout 480s claude -p --safe-mode --model opus --effort high --max-budget-usd 5 --permission-mode dontAsk --tools '' --disable-slash-commands --strict-mcp-config --mcp-config '{"mcpServers":{}}' --no-session-persistence --output-format json < /home/lyh/MAPF_PIED_MDDR_RESEARCH/73C23_FIXED_TARGET_HOST_DEPENDENCE_CONSTRUCTION_PROMPT_20260911.md
```

初始工具chunk7f500a、exec57718、stdout空；functions调用直接返回，没有yielded functions cell。只续同exec57718，1da722仍活且空；9d2e76取得完整JSON并exit0。未重复启动、未按同名PID猜结果；父根收到初始句柄与真实终态消息。timeout上限不是实际超时；本次成功返回。

实际字段：type=result、subtype=success、is_error=false、api_error_status=null、terminal_reason=completed、stop_reason=end_turn、num_turns=1；duration_ms=86272、duration_api_ms=86204；modelUsage唯一键claude-opus-5、canonicalModel=claude-opus-5、provider=firstParty。inputTokens=2、cacheCreationInputTokens=4182、cacheReadInputTokens=0、outputTokens=6317，其中usage.output_tokens_details.thinking_tokens=4197；webSearchRequests=0，total_cost_usd=0.1840725。session_id=72137c67-1afe-4282-87a2-b1b4493db90d，uuid=44988642-960f-42e0-af39-7c45713ed12e，permission_denials=[]。正文按空白分词595，末尾END-C23；模型名不是按请求臆测。

完整stdout原字符串先保留functions内存，再以apply_patch保存73C23_FIXED_TARGET_HOST_DEPENDENCE_RAW_RESPONSE_20260911.json；保留其终末LF。以下result不润色、不替换错误公式。e86431已核JSON result与下述标记间正文逐字相等、END-C23、实际modelUsage/终态且四新文件非符号链接；2ae2bb另将磁盘RAW与原内存stdout比较，raw_stdout_exact_equal=true。RAW的SHA256=d8379968148bb0be5835506b184f3bef83c87454550d30fc169c4715187c5ac1，6260 bytes/1 LF。科学意见需纠正，成功终态不等于资格通过。

## 2. 完整result原文

<!-- BEGIN_C23_RESULT -->
## 1. Smallest counterexample

Take two blocks, $w_1=w_2=\tfrac12$, $U_1=U_2=U$. Let $S$ be a single shared host state with $P(S=+U)=P(S=-U)=\tfrac12$, and let the arm-asymmetry be **arm-identity-linked, not position-linked**: $D$'s and $R$'s code paths respond oppositely to $S$ (e.g. differing allocator/cache footprints), so $d_1=d_2=S$ whatever the drawn D/R order. Then each $d_b$ is bounded in $[-U_b,U_b]$, each marginal law is exactly the symmetric two-point law it would have under independence, and $\theta=\sum_b w_b E[d_b|X]=0$; yet $|\Delta|=U$ a.s.

Generalising to $B$ equal blocks, the manuscript radius is $\sqrt{\tfrac{\log(2/\alpha)}{2}\sum_b(2w_bU)^2}=U\sqrt{2\log(2/\alpha)/B}$, which is $<U$ whenever $B>2\log(2/\alpha)$: coverage is $0$, not $1-\alpha$. No per-block marginal, no boundedness fact, and no within-block order randomisation distinguishes this law from the independent one, because randomisation permutes positions and the channel is not positional. Hence boundedness + randomised arm order cannot restore the block-independent radius; only a cross-block conditional statement can.

## 2. Flaws and exact sufficient conditions

**(i) Clusters.** The algebra is right: $\Delta=\sum_g V_g$, $V_g=\sum_{b\in C_g}w_bd_b\in[-A_g,A_g]$, $E[V_g|X]=\sum_{b\in C_g}w_bE[d_b|X]$, so $\theta$ is retained exactly and Hoeffding gives $\sqrt{2\log(2/\alpha)\sum_gA_g^2}$. Sufficient condition: **mutual** (not pairwise) conditional independence of the whole vectors $(d_b)_{b\in C_g}$ given $X$, which requires a declared measurable partition of the latent inputs such that each cluster body is a function of one block only. Quantitative flaw: $\sum_gA_g^2\ge A^2/G$ with $A=\sum_bw_bU_b$, so the radius is informative only if $G>2\log(2/\alpha)$; the single common-host cluster $G=1$ yields $\sqrt{2\log(2/\alpha)}\,A>A$ for every $\alpha<2e^{-1/2}$, i.e. strictly worse than the trivial $[-A,A]$ — vacuous, and the prohibited whole-range closure.

**(ii) Doob martingale.** $M_0=\theta$ holds; $M_J=\Delta$ requires **completeness**: $\Delta$ must be $\sigma(X,Z_1,\dots,Z_J)$-measurable. Otherwise $M_J=E[\Delta|X,Z]$ and you have silently bounded a compensator. Second condition: $\sum_jc_j^2$ bounded by a **deterministic** constant (a random bound gives no fixed radius); then $t=\sqrt{2\log(2/\alpha)\sum_jc_j^2}$. The host trajectory is not an enumerated primitive innovation, and if it is added as one its bounded difference is $c\approx A$ (it moves every downstream block), returning $\sqrt{2\log(2/\alpha)}A$ — again vacuous. So (ii) helps only under a declared generative model in which every cross-block channel is an enumerated innovation of small influence.

**(iii)** This is the only route recovering the *original* widths. Sufficient condition, exactly: with a predeclared block order and $\mathcal F_{b-1}=\sigma(X,d_1,\dots,d_{b-1},\text{all host covariates used})$, $E[d_b|X,\mathcal F_{b-1}]=E[d_b|X]$ a.s. Then $\Delta-\theta=\sum_bw_b(d_b-E[d_b|X])$ is a martingale whose $b$-th increment lies, given $\mathcal F_{b-1}$, in an interval of fixed length $2w_bU_b$; Azuma–Hoeffding returns precisely $\sqrt{\tfrac{\log(2/\alpha)}{2}\sum_b(2w_bU_b)^2}$. Within-block dependence and cross-block variance dependence remain unrestricted. Flaw: this is a conditional-mean-exchange assumption about the host, untestable from the run itself; non-significant autocorrelation is not evidence for it.

**(iv)** Correct as stated, and stronger: capsules change the sampling law, so the new $\theta'=\sum_bw_bE'[d_b|X]$ is a different number; identical roster/weights/$E_b$/formula is syntactic. Independence claim needs: (a) non-communication — the only inter-block channel is a state deterministically reinitialised; (b) independent primitive randomness per capsule; (c) residual shared channels (thermal, external load, drift) eliminated or bounded and carried as clusters/innovations. A reboot does not establish (c).

## 3. Obligation

No presently evidenced option closes inference: (i) and (ii) collapse to vacuous radii under one host, (iii) has no backend evidence, (iv) is unexecuted. Distinguish sharply: (i)–(iii) are **statistical regroupings** of the existing law that retain $\theta$ exactly; (iv) is a **changed execution law** that re-baselines the target. The narrowest qualifiable obligation is to declare, prospectively and honestly, which of the two you are doing, and then supply the corresponding evidence: for (iii), a design-level argument for conditional-mean exchange; for (iv), a written non-communication argument for (a)–(c) plus explicit acknowledgement that $\theta'\neq\theta$. Absent either, the comparison should be reported UNESTIMABLE at the intended resolution rather than published with a full-range interval. HOLD stands.

END-C23
<!-- END_C23_RESULT -->

## 3. 本代理独立纠正；不冒称根验收

1. 共享二点宿主状态反例有效。两个block已否定独立性/乘积步骤；在原置信水平下实际欠覆盖需使用其符号推广条件，而非说两个block就已造成95%欠覆盖。它无需改变任何单块边际，足以说明随机执行臂序不是独立性证据。没有生成具体实验块或赋保护参数。
2. 簇半径公式正确；簇向量的条件相互独立是充分条件，簇聚合量相互独立就已足够。独立原始创新的可测表示又是一种充分构造，不是所有条件独立分布必须满足的后端必要证明形式；其“function of one block”应为一簇根，不是原单block。
3. 顾问把“r≥A不能排除零”与“交已知域后必为整个[-A,A]”混在一起。一般A≤r<2A且Delta靠一端时，CI仍可裁去另一端；只是不能支持正/负符号结论。G>2log(2/alpha)是任何r<A的必要簇数条件，不是充分条件，且不是一般意义“区间有信息”的充要条件。单一簇在原alpha=0.05下r>A的两倍，确实全范围；全A=0按原退化分开。
4. 提示把c_j定义为Doob增量的条件支撑区间跨度，故正确半径为sqrt(log(2/alpha) V/2)，V为Σc_j²的事前确定上界。顾问sqrt(2log(2/alpha)Σc_j²)对应|increment|≤c_j的另一记号，误把两种界混用，保留原文但不采用。单个共同宿主创新可改变Delta由−A到+A，跨度上界应2A而非A。Doob最后σ域须足以决定Delta，这一完备性提醒采纳。
5. Doob鞅存在并不要求原始创新独立；直接验证其条件增量范围即可。独立创新有助从全统计量的坐标敏感度证明该范围。依赖只影响创新是否可独立分解及影响量，不能用单block局部U把对后继所有block的影响删去。
6. 原固定条件均值的鞅条件确为充分，但不是“唯一”可恢复原半径的概率结构；独立情形、合适负依赖/更直接矩母函数条件也可给同界，当前均无对应宿主证据。不得将此条件宣传为所有有效推断的必要条件。
7. 重置/隔离改变执行法时必须声明新宿主法及目标定义；但不推出theta'数值必≠theta。相同各block边际足以保均值；加权均值偶合也可能相等。正确结论是等值尚未证明，不能用相同公式代替证明。root尚未采用任何此类设计变更。
8. 独立性/域资格缺失按当前73是INFERENCE_UNAVAILABLE；实际必需评分缺失才UNESTIMABLE。合法但宽的CI是可报告的无方向性结论，不能将“未到拟议精度”更名为评分不可估；它也不能使当前设计闭合。原丢失评分时的无条件错误发布界及禁止条件于发布的95%覆盖不变。

P30给这些纠正后的完整自足证明、原始来源范围和下一可资格化义务。本回执没有对主稿或旧件作改动，没有实现、伪代码、构建测试、仿真、调参、数据/种子/O或载荷操作；35–38、受限Q与桌面边界保持，保护参数未赋值。所有C23句柄已真实终结，不留活任务，不重试。
