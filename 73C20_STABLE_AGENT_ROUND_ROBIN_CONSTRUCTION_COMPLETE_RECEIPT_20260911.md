# C20：固定机器人身份轮询——完整实际 Opus 建设回执

2026-09-11，根 /root 记录。NO-SKILL / CONSTRUCTIVE / NONBALLOT，不是73正式审查或通过票。提示、原始JSON及本回执保留实际内容；根的取舍另在P25，不由工具成功推出意见正确。

## 1. 精确任务与实际终态

提示文件：73C20_STABLE_AGENT_ROUND_ROBIN_CONSTRUCTION_PROMPT_20260911.md，SHA256 1a2db6401a85bb5a620ca578bcf83e8871ace5b836b7b7de2be7c59cde504bef，3332 bytes /14 LF。该提示是动态动作编号下轮询公平的新数学问题，不是C14或C17失败题重试，也没有读取失落P7/L7任务。

实际使用 rtk proxy timeout 480s claude -p --safe-mode --model opus --effort high，max-budget-usd 5，permission-mode dontAsk，tools空、disable-slash-commands、strict-mcp-config且mcpServers为空、no-session-persistence、output-format json。模型无工具、MCP、网络、文件或skill调用能力。此前该环境已重复实证socket权限失败，C20只进行一次正常升级调用，没有先制造一条失败尝试或重复启动。

原exec session 69960，启动chunk e0c9aa；根续原句柄取得chunk fb8591、exit0。CLI session cfb4423f-1523-4a70-9a86-7369881776a4，terminal_reason=completed、stop_reason=end_turn、is_error=false，duration_ms=82858，output_tokens=5063，total_cost_usd=0.15166625。modelUsage实际报告claude-opus-5、canonicalModel同值、provider firstParty；不是仅按请求参数推断型号。permission_denials为空，完整result末行END-C20。无活C20句柄，没有超时或失败当通过。

原始完整返回另存73C20_STABLE_AGENT_ROUND_ROBIN_CONSTRUCTION_RAW_RESPONSE_20260911.json，包括实际用量和全部result。以下逐字保留result；其中“下界”和“固定费”等表述由根另外判断，不静默改写。

## 2. Opus 实际完整正文

## 1. 旧规则：反例成立，但只否定"有界超越"这一条

根的符号序列是正确的反例。缺的条件不是 fleet 有限，而是**游标所在的 key 空间有限**。RR 的 ≤N 界依赖"每次推进后，落在 last 与目标之间的 key 只能减少"；而 tid 的 e 分量无上界，a 每完成一次原 MOVE 就能在 (last, (b,f)) 这个已被扫过的区间里再插一个新 key，插入次数不受 fleet 基数约束。因此"固定有限 fleet ⇒ 一次轮询内必选到持久成员"是错的。

可补一点：a<b 的假设多余。若 b<a，则 (b,f)<(a,e)=last，(a,e') 仍是唯一严格大于 last 的最小 key，b 照样被跳过；回绕分支只在 a 恰好无 Active tid 的瞬间才起作用。

它否定的只是**有界超越/一轮公平**这条声明：不存在以 fleet 基数为界的"成功选择次数"上限。它**不**断言实际无限饥饿——那还需要 a 反复被中心确认 FINISHED 并重入、且时序上每次都抢在下一次选择之前，属于对抗性排程；也不断言官方 R0 会产生这些轨迹。

## 2. 新规则：纯 R 下界为 fleet 基数

命题：设 tid T 属 agent a，自某次选择前起持续 Active，且期间只发生成功提交的纯 R 选择，则 T 在至多 N=|fleet| 次这样的选择内被选中。

证明：由"每 agent 至多一个 Active tid"不变量，T Active ⇒ a 恒为候选，且绑定被迫是 T。在 agent 键的循环序上定义 d = 从 last_agent 起到 a 的循环步数 ∈[1,N]。每次成功选择取的是自 last_agent 起循环扫到的**第一个** Active agent g;因 a Active,g 的步距 ≤ d。若 g≠a,则新 d′ = d − step(g) < d,正整数严格下降;故至多 N 次后必选中 a。其他 agent 的原 MOVE 更替不产生新 agent 键、不重置 last_agent,故不影响该单调量。

必须区分的四件事：
- **成功选择提交**：界只以此计数。空 Active、版本/模式验证失败、未提交、过期都不推进 last_agent,因而不消耗轮次,但也不保证任何一次成功选择会发生;有限 O 耗尽时该界空洞成立。
- **CAPTURE 新鲜度**：被选中只意味着发布了绑定 T 的 POSITION 请求。采样/网络失败不回退 last_agent,故这一轮被消耗而没有新鲜位置。
- **消息到达**：不在界内。
- **有限 O 整体进展**：不蕴含。

不变量破坏（同 agent 多 Active tid）时规则拒选，界不适用。

## 3. 版本/费用/公开知识责任，以及 D 不能继承该界

资格仍按完整 tid 判：选中 agent 后必须完成后继完整版本/模式验证并提交才生成该 tid 的请求；这既保证绑定唯一，又保证失败不偷走轮次（除已发布后的采样/网络失败）。每次 QUERY 付固定费读中心 Active/last 根，界的单位是"已付费且已提交的选择"，不是时间。last_agent 与 Active 只是中心已提交知识：物理已 END 但中心未知的 tid 仍占轮次，中心不得从真实进度反推完成，否则把可见性泄漏进公平论证。writer 串行是游标读-改-写原子性的前提，计数论证依赖它。

D 不能继承：D 按最大正阻塞分（时间、完整 tid tie-break）选，与 agent 游标无关，却同样推进 last_agent。一次 D 选择可把游标推到 a 之后，使 d 回升至 N，单调下降量被破坏；正分反复命中即可反复越过 a。D 无正分才回退 RR，混合比例由状态决定而非固定排程。故混合下无 RR 公平界。

本节不主张该更强 R 更优、D 仍有正净收益或任何资格结论。

END-C20

## 3. 接收范围

根完整读取并解析原始JSON，确认终态和Opus型号。该回执只完成有界建设输入；候选73仍DRAFT / NOT-FIXED / NOT-REVIEWED / NOT-ACCEPTED，六门2 PASS /3 UNKNOWN /1 FAIL与HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT不变。未实现、构建测试、仿真、调参或生成实验载荷/结果，保护参数未赋值。P25另给不使用skill的独立分析，P26另查完整协议绑定，二者都不属于正式三路审查。
