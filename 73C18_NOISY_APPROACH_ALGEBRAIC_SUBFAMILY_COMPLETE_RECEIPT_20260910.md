# 73C18：保留参考扰动的 APPROACH 代数子族——Claude 完整实际回执

任务始于2026-09-10，根于2026-09-11实际收取最终回执。CONSTRUCTIVE / NO-SKILL / NONBALLOT。不是候选正式审查，不对六门投票。73仍DRAFT / NOT-FIXED / NOT-REVIEWED / NOT-ACCEPTED，HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 调用身份与真实终态

固定提示：`73C18_NOISY_APPROACH_ALGEBRAIC_SUBFAMILY_CONSTRUCTION_PROMPT_20260910.md`，SHA256 `6c4c5b986855c8c38b878cbe93d5f428be5122cc2dd4b64d3c2bda2cd9f2f6a7`，3763 bytes /25 LF。命令通过 rtk proxy timeout 480s claude -p，以 --safe-mode --model opus --effort high --max-budget-usd 5 --permission-mode dontAsk --tools '' --disable-slash-commands --strict-mcp-config --mcp-config '{"mcpServers":{}}' --no-session-persistence --output-format json 和该完整提示调用；无工具、skill、文件读取或网络检索授权。请求别名不替代下述实际模型身份。

第一次exec 86950在chunk276d45/exit1终止，完整原始JSON保存于`73C18_NOISY_APPROACH_ALGEBRAIC_SUBFAMILY_ATTEMPT1_RAW_RESPONSE_20260910.json`。is_error=true、terminal_reason=api_error、FailedToOpenSocket、modelUsage为空、用量及费用为零，没有END-C18；外层subtype=success不能将此改判成功。此为网络失败，不是提供方科学拒绝。按环境规则以完全相同命令正常提权重试，第一次已结束后才启动，没有重复活调用；不是C14拒绝或C17超时的重启。

第二次提权调用经functions.exec cell431返回exec 8231，根只续同句柄；实际最终chunk b30495 / exit0。完整JSON保存于`73C18_NOISY_APPROACH_ALGEBRAIC_SUBFAMILY_ATTEMPT2_RAW_RESPONSE_20260910.json`。is_error=false、terminal_reason=completed、stop_reason=end_turn、num_turns=1；实际modelUsage明确canonicalModel=claude-opus-5、provider=firstParty，不自行推断别名。duration_ms=162865，duration_api_ms=162826；input_tokens=2、cache_creation_input_tokens=4430、output_tokens=12979，其中响应报告thinking_tokens=9339；费用0.35217249999999994 USD。隐藏思考没有返回正文，不声称已读取。permission_denials为空；CLI session_id=6448dd3b-b5e7-4227-9088-155b8953ac5d，uuid=f326b07e-991a-4839-bb13-8f8ddf3f8a92。result有独占末行END-C18；以下完整保留result，不删改其中可疑意见。

## 完整实际 result（原文）

## 1. 推导核验：结论成立（并可强化）

**链条闭合。** 由 $r=v^2/[2(C-s)]$、$\dot s=v$、$\dot v=a_{cmd}+\eta$ 得 $\dot r=\frac{v}{C-s}(a_{cmd}+\eta+r)$，而原 APPROACH 公式给出恒等式
$$a_{cmd}+\eta+r=\tfrac{2\delta}{D}\Big[\tfrac{a_{hi}+a_{lo}}{2}+\tfrac{\eta D}{2\delta}-r\Big]=k\,(r_\star-r).$$
以 $y=\sqrt{C-s}$，$\dot y=-v/(2y)=-\sqrt{r/2}$，故 $dr/dy=2k(r-r_\star)/y$，即给定的 $r=r_\star+A(y/y_0)^{2k}$。**关系 $a_{hi}-a_{lo}=4\delta$ 的唯一作用是 $k=2\delta/D=1/2$，即指数 $2k=1$**，于是 $r$ 在 $y$ 中仿射，$r_\star=\frac{a_{hi}+a_{lo}}{2}+2\eta$。

**三条猜想皆真。** 令 $g=\sqrt r$。由 $2g\dot g=\dot r=(A/y_0)\dot y=-(A/y_0)g/\sqrt2$ 得 $\dot g\equiv-\dfrac{A}{2\sqrt2\,y_0}$（常值，仅需 $g>0$ 处除 $g$），故 $g(\tau)=h_0-\dfrac{A\tau}{2\sqrt2 y_0}$；再积 $\dot y=-g/\sqrt2$ 得 $y(\tau)=y_0-\dfrac{h_0\tau}{\sqrt2}+\dfrac{A\tau^2}{8y_0}$。两式与所给一致。

**最早根与分支。** $y(T)=0\Rightarrow T=\dfrac{2\sqrt2 y_0(h_0\pm\sqrt{r_\star})}{A}$（用 $h_0^2-A=r_\star$）。$A>0$ 时 $h_0>\sqrt{r_\star}$，减号支为最小正根；$A<0$ 时 $h_0<\sqrt{r_\star}$，仅减号支正。两种情形同一有理化式
$$T_{cap}=\frac{2\sqrt2\,y_0}{h_0+\sqrt{r_\star}}=\frac{4(C-s_0)}{v_0+\sqrt{2r_\star(C-s_0)}},$$
$A=0$ 时连续退化为 $2(C-s_0)/v_0$：**不必除 $A$，亦无分支选择歧义**。抛物线顶点在 $\tau_v=2\sqrt2y_0h_0/A>T_{cap}$（$A>0$）或 $\tau_v<0$（$A<0$），故 $y$ 在 $[0,T_{cap}]$ 严格单调降，不越 cap。

**正性与带界。** $|\eta|\le\delta$ 给 $\eta D/(2\delta)\in[-D/2,D/2]$，故恒有 $r_\star\in[a_{lo},a_{hi}]$（此点对任意 $D$ 成立，非本子族特有）。$g$ 仿射且 $g(0)=h_0>0$、$g(T_{cap})=\sqrt{r_\star}>0$ $\Rightarrow g>0$ 全程；$r$ 在 $r_0$ 与 $r_\star$ 之间单调，故 $r_0\in[a_{lo},a_{hi}]$ 时闭带不变，$T_{cap}$ 有限。合法非零速入口：$s<C,v>0\Rightarrow y_0>0,r_0>0$；若 $v=0,s<C$ 则 $r=0<a_{lo}$ 本属 LAUNCH，故 APPROACH 段恒有 $y_0>0$，公式中 $1/y_0$ 不退化。到达时 $v=\sqrt2\,y\,g\to0$。

**代数性（强于猜想）。** 因 $h_0/\sqrt2=v_0/(2y_0)$，
$$s(\tau)=C-\frac{\big[(C-s_0)-\tfrac{v_0\tau}{2}+\tfrac{A\tau^2}{8}\big]^2}{(C-s_0)^2}\,(C-s_0),\qquad v(\tau)=\Big(v_0-\tfrac{A\tau}{2}\Big)\frac{(C-s_0)-\tfrac{v_0\tau}{2}+\tfrac{A\tau^2}{8}}{C-s_0},$$
即 $s,v$ 是 $(C,s_0,v_0,a_{lo},a_{hi},\eta,\tau)$ 的**有理函数，不含根式**；只有 $T_{cap}$ 需一个二次根 $\sqrt{2r_\star(C-s_0)}$。LAUNCH（$a\equiv a_{launch}+\delta+\eta$）与 BRAKE（$a\equiv-a_{hi}-\delta+\eta$）为抛物运动，其切换时刻（$v^2=2a_{lo}(C-s)$ 的二次方程根、$v=0$ 的有理根）同样代数。每次 cap 扩张或 $\eta$ 换值处以该时刻的 $(s,v,C,\eta)$ 重置局部常量：若事件时刻代数，则新段初值代数，有限段落合成仍落在有限次实代数扩张内，段间与外部时刻的判等/排序在实闭域中可判定。**故"任意积分值代数"未被默认，而是被显式解证出**——但仅在此子族；$2k\neq1$ 时 $y$ 满足 $\dot y=-\sqrt{(r_\star+A(y/y_0)^{2k})/2}$，到达值一般非代数，该缺口未被本关系之外关闭。

**同刻优先仍必须保留。** 在 $T_{cap}$ 处 $v=0,y=0$；若同刻扩 cap 而先走 RUN，则 $r_{new}=0<a_{lo}$ 触发 LAUNCH，既破坏"原 $\ell$ 终点关闭优先/中点不 END"，也使下一 APPROACH 段以 $y_0=0$ 开启而令上述表示奇异。故"旧 cap 到达与扩 cap 同刻先 HOLD""HOLD 扩 cap 不自动 RUN""显式 BRAKE 不可撤销"三条必须原样保留；本关系不为它们提供任何豁免。

## 2. 保留与限制

**不偷执行器。** 在 $r\in[a_{lo},a_{hi}]$ 上 $a_{cmd}\in[-a_{hi}-\delta,\,-a_{lo}+\delta]$（端点恒等式 $a_{cmd}|_{r=a_{hi}}=-a_{hi}-\delta$ 对任意 $D$ 成立）。故 APPROACH 的最大减速指令恰等于原 BRAKE 的 $a_{hi}+\delta$：**不要求超出原命令范围的权限**。

**不免费测 $\eta$（用于控制）。** $a_{cmd}$ 只依赖 $(s,v,C)$。$\eta$ 仅进入分析量 $r_\star$。若要给出**精确**代数 $T_{cap}$，则需该段 $\eta$ 值——这是知识代价；若只要代数**夹逼**，由 $T_{cap}$ 对 $r_\star$ 单调，取 $r_\star\in[a_{lo},a_{hi}]$ 得两端闭式包络，无需任何 $\eta$ 观测。应只宣称后者。

**限制的是参数域而非物理。** 子域为 $\{\delta=(a_{hi}-a_{lo})/4\}$，叠加 $\delta<a_{lo}\Rightarrow a_{hi}<5a_{lo}$：在 $(a_{lo},a_{hi},\delta)$ 中是余维一切片再加不等式，零测度，**不得冒充原整个参数域等价**。真实实体 $X=u+se+z+F,\ \dot z=-\kappa z+w$ 完全未被触动，随机延迟 $z$ 未被重命名为空间误差。相对"删除参考 $\eta$ 的名义发生器"，本子族**保留了 $\eta$**：扰动仍在动力学与闭带证明中，科学代价从模型保真转移到参数域收窄——此子族确实避免了删除 $\eta$ 那一项代价。

**共同可满足性（须事前披露）。** 设硬件实际可用减速上界 $a_{\max}$，真实扰动界 $\delta$ 由硬件给定（不得为过关反向缩 $\delta$）：需 $a_{hi}+\delta\le a_{\max}$ 且 $a_{lo}>\delta$，代入 $a_{hi}=a_{lo}+4\delta$ 得 $a_{lo}+5\delta\le a_{\max}$，即 $a_{\max}>6\delta$。

## 3. 建议

值得作为**一个不同的后继工作选项**并行比较（与"全域任意有界可测 $\eta$、到达值非代数"路线及"删 $\eta$ 名义发生器"路线三方对照），因为它以零测度参数切片换来 $s,v$ 的无根式有理表示与二次代数 $T_{cap}$，且不加执行器权限、不删 $\eta$、不改 $a_{cmd}$ 形式。采用条件：$\delta=(a_{hi}-a_{lo})/4$ 与 $a_{\max}>6\delta$ 事前披露、对所有臂相同、不得事后调参。

仍不可据此声称：实际计费后端通过；任何观测信息/精度结论（本推导只涉及参考 $(s,v)$，与 $X,z,w,F$ 无关）；有限 $O$ 进展（"已发生 $\eta$ 因果前缀分段常值"与"事件/外部时刻本身代数"均仍是假设，非结论）；净吞吐通过。亦不可声称整个方案通过。

END-C18

## 根收取边界

完整实际回执只证明本次建设性建议已返回。根另以不用skill的独立推导和取舍报告P20分析；不把Claude自称“成立”、硬件条件或建议自动采纳为候选资格。原文关于同刻切换必然出现y0=0的论证、把z写作“随机延迟”的一句、只许宣称eta包络的意见及新增硬件符号条件均须独立判断，保留原文不等于认同。既有保护参数未赋值，未实现、构建测试、仿真、调参或产生实验载荷/结果。
