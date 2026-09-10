# 73C9：组退栏与控制模式建设意见——真实完整终态回执

日期：2026-09-10。新独立有界建设题，NO-SKILL / CONSTRUCTIVE / NONBALLOT；不是正式审查或资格票。此调用已真实正常结束，意见正确性由 P10 不用skill逐条分析，不能由 exit 0 或完整正文推定。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 1. 输入、调用与实际终态

输入候选：73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md，SHA256 0beccea730aced26203406f8ffa69f5ffa93247f80cec64f00ec9de265065965，155562 bytes / 531 LF。子代理先独立全文读取并补齐工具截断窗口，再摘录必要原文；未读其他新审查意见。

提示文件：73C9_GROUP_RETIRE_CONTROL_MODE_CONSTRUCTIVE_PROMPT_20260910.md，7934 bytes / 43 LF，SHA256 b7b373f5da3ba79f31c9e036075999d547f5c11342944b04c554768220667032。提示不包含子代理对接口的结论，未给Claude工具或其他报告；未改旧C8L提示/回执，未复用其失效句柄。

实际命令，工作目录为研究目录（本次已执行的是顾问CLI，不是研究程序）：

```text
rtk proxy timeout 480s claude -p --safe-mode --model opus --effort high --max-budget-usd 5 --permission-mode dontAsk --tools '' --disable-slash-commands --strict-mcp-config --mcp-config '{"mcpServers":{}}' --no-session-persistence --output-format json < 73C9_GROUP_RETIRE_CONTROL_MODE_CONSTRUCTIVE_PROMPT_20260910.md
```

本新题首次调用依据同类沙箱网络失败记录通过正常 require_escalated 机制执行；exec 初次等待1000ms。functions cell 109 随后返回实际 exec session 29561；只观察该原句柄，未用同名进程代证PID、未向任何进程发送信号。最终chunk 455020，exit_code=0，完整JSON已返回；本题没有第二次调用、没有重试或重派。

CLI session_id=7fa8583c-34b7-4062-a7d6-bb61f0808613；uuid=2d5c2770-878d-467f-a7f6-c1e2e98a00ec；is_error=false，subtype=success，terminal_reason=completed，stop_reason=end_turn；duration_ms=175504，duration_api_ms=175468，num_turns=1；total_cost_usd=0.33605375。以下是实际 modelUsage 字段，不由请求参数猜测模型：

```json
{
  "claude-opus-5": {
    "inputTokens": 2,
    "outputTokens": 11920,
    "cacheReadInputTokens": 0,
    "cacheCreationInputTokens": 6087,
    "webSearchRequests": 0,
    "costUSD": 0.33605375,
    "contextWindow": 200000,
    "maxOutputTokens": 64000,
    "canonicalModel": "claude-opus-5",
    "provider": "firstParty"
  }
}
```

实际usage另报 input_tokens=2、cache_creation_input_tokens=6087、cache_read_input_tokens=0、output_tokens=11920；server_tool_use 中 web_search_requests=0、web_fetch_requests=0，permission_denials=[]。这些是CLI返回的用量字段，不把token数当作科学意见质量或额外完整全文阅读证据。

原始stdout JSON：73C9_GROUP_RETIRE_CONTROL_MODE_RAW_RESPONSE_20260910.json，8214 bytes / 1 LF，SHA256 7b441056ca980931b1ccaa27afab1ad5e4b34284dec7e2be33e411e7e093c764。以下result正文是该JSON字符串解码后的原文，3231 Unicode字符 / 7009 UTF-8 bytes / 49 LF，正文SHA256 78af0d6f77f67d571c1498ab9da8440d0f017e907321c3bcadf4e818a37e362f；没有纠正、删除或润色其错误。正文开始/结束标记不属于该hash。

## 2. 完整result原文开始

# 73C9 独立建设分析：一处最有分量的组合漏洞

## 一、结论：漏洞位于「GROUP_RETIRE 守卫谓词」×「无 ACK 的 writer 分区」×「控制尝试在实处理点才登记水位」的三方接口

单看三处条款都自洽，合起来出现一个**真实安全漏洞（物理占用冲突），而非合法停滞**：退栏守卫全部写在中心侧谓词上，而它要约束的对象（已安装 cap、已发布未处理的 RUN 尝试）按稿子明文属于 executor writer 且禁止向中心回报；于是围栏可以在一条仍然合法可执行的 RUN 命令尚未落地时被解除，而 ACTUATOR 的守卫清单里没有任何一项与组围栏/退栏相关。

## 二、最小合法事件前缀（每步均为付费合法动作）

1. 中心以 GROUP_ADMIT token 一次提交设栏：成员 {i, j}，各得唯一原 tid、c/l/B、b_i=c_i，A_i 改 tag，转 GRANTED。
2. agent i 的公开出现 n_i≡0：SOURCE_OR_EXTEND 落在「GRANTED 且 b<ell」分支，做一次最大合法扩展，中心 b_i 前进（尚未到 ell）。
3. n_i≡1：RESEND_CAP，b_packet≥C 在 GRANT_ARMED 被接纳，本地安装 C_i，且 s_i < C_i < ell_i（稿子明说「本地不需知道最新中心 b」，此不等式完全合法）。
4. n_i≡2：CONTROL_RETRY 按中心已知 tid_i/代际（含初始 RUN_ALLOWED 意图）产生一次绑定该公开行的尝试；Srv_E 付费验证通过并在严格后继行的控制发布容量中发布。**ACTUATOR 尚未处理**——按「认证通过的新尝试在实际处理点登记水位」，此刻本地水位未推进，且平台无 ACK，中心无从知晓其存在与命运。
5. 中心对 tid_i、tid_j 分别付费 FINISHED。稿子自陈「闭合 END…需付费中心 FINISHED、READY 和本地消费」，即 FINISHED 严格先于本地消费；故此刻 agent i 本地 tid 未闭，phase 仍是起点/中点 HOLD。
6. 公共 GROUP_RETIRE 在 Srv_C 付费扫描，按组建立行/规范 key 选中该组：全部成员中心 FINISHED ✓；终点 resident 合法接续 ✓；「旧 cap/RUN 受永久关闭守卫约束」只能以中心 b/关闭水位判定 ✓。提交退栏，F_G 解除，成员新 MOVE 限制解除。
7. 围栏内当前无物理 owner 的资源 r 不再受「不能对外称完全 FREE」保护，中心把 r 的登记责任新授给非成员 k（该资源落在 (s_i, C_i] 区间内）。
8. agent i 的 ACTUATOR 处理第 4 步命令：原 tid/slot/parent ✓、当前 phase ✓（本地未闭、中点 HOLD）、制动域 ✓（无 BRAKE，代际 RUN_ALLOWED）、已安装 cap C_i>s_i ✓ → 合法 START/RESUME，agent i 推进进入 r，与 k 冲突。

前缀长度四次公开出现＋两次中心提交＋一次公共退栏，无需任何丢包、超时或私有猜测。

## 三、精确冲突条款

- 退栏守卫：「按组建立行/规范 key 选择首个满足全部成员中心 FINISHED、终点 resident 合法接续、旧 cap/RUN 受永久关闭守卫约束者」——三项全在中心 writer 域。
- 观测禁令：「本平台不向中心发送 cap 安装/到达/START 结果 ACK，审计器日志不可供中心策略读取」——「已安装 cap」「START 结果」对中心不可见。
- writer 划分：「各 executor 管理 C/控制代际与尝试水位、自己的命令/c/READY 消费状态」＋「各应用 writer 至多一个计算或待发布槽，彼此不跨槽持锁等待」——禁止用跨 writer 会合来补齐守卫。
- 水位时点：「认证通过的新尝试在实际处理点登记水位…未认证包不推进水位」——已验证已发布但未处理的尝试，无任何一侧能宣布其已消费。
- ACTUATOR 义务与输入：「ACTUATOR 只执行已验证发布的命令」「只执行已有合法权限」，其接纳输入仅列「同 tid 命令及当前必要模式/幂等守卫」——**不含组围栏/退栏状态**。
- 被牺牲的保护：「禁止非本组登记责任新增占用 F_G；当前无物理 owner 的围栏资源也不能对外称完全 FREE」——第 7 步的唯一屏障恰由第 6 步以不完备守卫拆除。

## 四、二分（若坚持另一读法）

若把「中心 FINISHED」读成蕴含本地到达与 READY 消费，则中心必须导入 executor writer 状态，直接违反无 ACK 条款与单槽不跨锁条款；此时 GROUP_RETIRE 恒为付费空结果，SOURCE_OR_EXTEND 的 GROUP_HELD 分支成为吸收态。稿子明列的须保留负结果只有「中心 fail-stop、永久 no-start/失联/未闭 tid」，并不涵盖「成员确已完成而守卫不可判定」，故此读法下是**未被承认的接口不完备**，不能用「必须保留的负结果」豁免。两条读法都指向同一处需改稿的接口缝。

## 五、直接可改稿修复（仅中心→executor 单向、签名公开行，不引入任何参数）

1. 在累计 cap／控制条款增：「中心 FINISHED 同时写入该 tid 的**永久关闭标记**，并作为可被签发命令携带的公开行事实；任何控制尝试必须携带其绑定 tid 的关闭标记，Srv_E 验证标记与 tid 一致性，不一致为付费拒绝。」
2. 在 ACTUATOR 守卫清单增列关闭标记：「已带或已知永久关闭标记的 tid 的任何尝试一律 phase 拒绝并消费该尝试，不论本地是否已消费 READY、不论 C>s。」——此项独立封住第 8 步，无需任何回报。
3. 把退栏守卫第三项改写为可判定式：「全部成员原 tid 已写入中心永久关闭标记，且各标记公开行严格先于本次退栏提交行」，取代含义悬空的「旧 cap/RUN 受永久关闭守卫约束」。
4. 在退栏语义增：「退栏只解除准入禁令；围栏内仍可能被已签发 cap lineage 覆盖的资源，在其 tid 永久关闭标记发布前不得对外称 FREE、不得新增登记责任」，即逐资源以 lineage 消灭为闸（中心是 b/ell/grant 的 writer，可判定）。
5. 明文声明不对称补偿方向：缺失的 ACK 只允许以中心签名公开行在中心→executor 方向补齐，永不反向。

## 六、需要补的最小定义

(a) 中心 FINISHED 的确切证据谓词及其与本地到达/READY 消费的时序；(b) 已验证发布但未被 ACTUATOR 处理的控制尝试的生存期与可否被后继公开行作废；(c)「永久关闭守卫」的 writer 与可判定域；(d) 退栏后逐资源可称 FREE 的条件；(e) 空结果是否推进 n_i。

## 七、不计入本漏洞的两类

**合法停滞**：STOP_LATCHED 代际按 agent 单调，退栏并换新原 tid 后仍需一次付费 MODE RESUME 才可 START；相位轮转使解除限制后可能先耗掉 RESEND_CAP/CONTROL_RETRY 两次付费空动作。二者是明确条件下的有代价等待，不得读成无条件完成，也不是漏洞。
**定义歧义**：上文 (e) 项「空结果/丢包/私有进度不改变相位」是否等于 n_i 不增，只影响成本会计与可达时刻，不影响本漏洞成立。

NO-SKILL / NONBALLOT / HOLD

## 3. 完整result原文结束及审阅状态

子代理已完整读到上述result真实结尾，不是部分流/超时/空回执。其第5步把中心FINISHED与仍在中点、原tid未关闭并置；候选实际END链禁止该状态，因此该主反例不成立。详细独立复算及每项修补意见的采纳/否定理由见唯一主报告73P10_INTEGRATED_PREFIX_PROTOCOL_COST_AND_MODE_COMPOSITION_ANALYSIS_20260910.md；此处只记录真实终态和未经改动的顾问意见。

本次仅以apply_patch保存提示、完整原JSON及本回执；没有实现、伪代码、构建、研究测试、仿真、参数赋值或研究载荷，未改73、行政页、Git或桌面。调用成功不改变HOLD，不投资格票。
