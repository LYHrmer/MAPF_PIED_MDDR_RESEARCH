# 73C34：H19 首次匹配拼接——完整建设回执

2026-09-13；CONSTRUCTIVE / NONBALLOT。仅针对同号局部提示，不是整稿审查或正式票。

首个普通沙箱exec81310（d535a8启动；0036a2/b03ab5为空活轮询）最终1a12bf/exit1，api_error/FailedToOpenSocket，modelUsage空、API时长及费用为零，无模型正文。仅在确认这个网络错误终态后，按正常权限流程重试相同命令；唯一升级exec11369（6f0c7c启动，0275d0为空活轮询）最终e52cf9/exit0。实际模型claude-opus-5/firstParty，completed/end_turn/is_error=false，CLI4b7cbc04-5c95-4214-b76e-87d288190a3e，duration_ms=273735、duration_api_ms=273701、total_cost_usd=0.3260725。完整END_C34_H19_SPLICE。没有工具调用或权限拒绝记录；未重启任何旧咨询。

成功原stdout保存在[RAW.json](73C34_H19_FIRST_MATCH_SPLICE_RAW.json)，本件下面逐字保存其result正文。调用使用opus别名、high努力、空工具列表、safe-mode、无session持久化、JSON输出与同号文件作为stdin；模型身份据实际回执，不据别名猜测。

## 根独立取舍

采用前驱闭包的逐agent前缀性、保留旧首匹配/旧匹配撤出后扫描新后缀/新源只匹配新后缀的分类证明，以及严格时间分层排除new→old、两部DAG推出合图DAG。对应证明已在根读H19原文Algorithm1/2后独立推导，原文首次匹配必须同时满足端点及时标条件。GC后只比较未满足的活依赖，不宣称物理删除前后原始边集逐字相同。

不采C34把“未完成a、首匹配b已finished并GC”作为本合同合法历史的反例。对于已经存在且约束b入队的跨agent Type-2边a→b，b已finished必曾合法入队，当时a已在中心F；F事实单调且不为旧已入队动作加新前驱，所以该状态在这些前提内不可达。source_positive_mechanism另作独立无工具数学核对，确认推理并提醒不能推广到Type-1：同agent完成通知允许乱序。若只有任意图和任意finished标签而没有合法入队历史，这一前提确实缺失；本稿明确补上历史条件，不把任意标注当合法运行。

不采按目标b完成翻转源a出向槽的通用SATISFIED方案。实际义务由源a完成消解：根选择a进入F后，付费向仍需它的入向依赖转交完整源身份及完成依据，引用结束后才回收正文。未完成源及首匹配义务保留；无需为上述不可达状态增加每动作×fleet稠密槽表。原动作id保留(sourcejob,agent,源动作下标)，不采用丢失代际的(agent,index)。Type-1仍须原前驱身份与已入队/完成依据，裸状态位不足；不以任意已删最大下标当已完成前缀水位。

不采“已finished即可删除全部正文/出边/槽”的无条件时机，仍需转移全部未完成依赖依据并结束图、cut、捕获批、执行、消息和验证引用。费用、引用保留与故障结果照原合同，不主张固定内存。也不把无环当固定有限O内存在实际入队机会、运动授权、完成通知或净真实服务的证明；它只给图层的有条件结论。

## Claude 完整原文

## 1 精确条件与拼接定义

记号：旧 ADG 为 $G$，agent $i$ 的唯一 Type1 链为 $a_{i,1},a_{i,2},\dots$。种子 $\Sigma$ = desired ∪ 已入队/执行中/已授权/已发送缓存可能生效/旧 cut 承诺的责任动作；$P=\mathrm{Anc}_G(\Sigma)$（Type1∪Type2 前驱闭包）。

**引理0（前缀性）** Type1 边连接相邻动作，故 $P_i:=P\cap\text{agent }i$ 对 index 下闭，$P_i=\{a_{i,k}:k\le c_i\}$，$c_i$ 即 Alg2 的 cut。cut 外未承诺 staged 后缀退出允许域。

前提：
- **(T) 时间分离**：$\min_{x\in S}t(x)>\max_{y\in P}t(y)$，且各 $S_i$ 从 $a_{i,c_i}$ 终态接续、index 续排。
- **(H-break)** Alg1 只在同时满足 $s(a)=g(b)\wedge t(a)\le t(b)$ 的首个 $b$ 处加边并 break（对仅几何匹配即 break 的读法本构造不成立，见 §2）。
- **(F) 惰性化**：已 finished 动作的出边对任何后继恒满足，予以删除。

**参照语义** $R_i$ = agent $i$ 的原始完整前缀（含已 finished 甚至已 GC 者）到 $c_i$，续接 $S_i$；目标是 $\hat G$ 与 $\mathrm{A1}(R)$ 的**活依赖**相同。

$\hat G$：每 agent 串接 $P_i+S_i$，保留旧 Type1 边，加 $a_{i,c_i}\to$ 首个 $S_i$ 动作。Type2 对未完成源 $a\in P$ 与每个 $j\neq\mathrm{agent}(a)$ 按槽 $\mathrm{slot}(a,j)$ 三分：

- **情况一（活匹配）** $\mathrm{slot}=\mathrm{PENDING}(b)$ 且 $b\in P$：保留 $a\to b$，**不**再扫 $S_j$。
- **情况二（已消解）** $\mathrm{slot}=\mathrm{SATISFIED}$（原首次匹配已 finished，正文可能已 GC）：不加边、**不**扫 $S_j$。
- **情况三（重扫）** $\mathrm{slot}=\mathrm{ABSENT}$，或 $\mathrm{PENDING}(b)$ 而 $b\notin P$：在 $S_j$ 中取首个 $g(b')=s(a)$ 的 $b'$（时间条件由 (T) 自动成立），加 $a\to b'$；无则无边。

新源子句：$a\in S$ 只能匹配 $S_j$ 中动作（旧动作因 $t(a)>t(b)$ 全部落空且不触发 break），所得边恰为单独 $\mathrm{A1}(S)$ 的边。

## 2 证明与反例

**(P1) 活依赖等价** 对未完成 $a\in P$，$\mathrm{A1}(R)$ 扫 $R_j$ 命中原首次匹配 $b^\*$：$b^\*$ 已 finished ⇒ 该边惰性 ⇒ 情况二一致；$b^\*$ 未完成且 $\in P$ ⇒ 情况一；$b^\*$ index $>c_j$ ⇒ $b^\*\notin R_j$，而 $b^\*$ 是首次匹配故 $P_j$ 内无更早匹配，扫描顺延入 $S_j$ ⇒ 情况三。新源见上。∎

**(P2) 旧资格不可撤回** 闭包⇒任何保留动作的未完成前驱均被保留；$\hat G$ 中不存在 new→old 边（(T)+(H-break)），情况三与 Type1 尾→首只为**新**动作增加前驱。故保留旧动作的前驱集逐点不变，enqueued 资格不被撤回，中心 finished 单调。∎

**(P3) 无环** 跨段边方向恒为 $P\to S$；$P$ 内是 DAG $G$ 的诱导子图；$S$ 内等于无环的 $\mathrm{A1}(S)$。分层⇒$\hat G$ 无环。∎

**反例（根拟构造需修）** 以"b 不在存活图中"判情况三是错的：设 $s(a)=v$，agent $j$ 的 $b_1$ 满足 $g(b_1)=v,\;t(a)\le t(b_1)$ 且已 finished+GC，$S_j$ 另有 $b'$ 以 $v$ 为终点。$\mathrm{A1}(R)$ 只给 $a\to b_1$（惰性），朴素扫描却加伪边 $a\to b'$，把新动作压在未完成的 $a$ 之后，不等价。镜像错误更严重：把已被 cut 的 $b$ 误记为保留则漏掉 $a\to b'$，两 agent 可同占 $v$ —— 物理不安全。**修正**：槽必须三态且单调，情况二显式存在。

## 3 最小 GC 证据合同

**字段** 每未完成动作 $a$：$\mathrm{id}=(\text{agent},\text{index})$、$s(a),g(a),t(a)$、Type1 前驱状态位、以及每个 $j$ 一个 $\mathrm{slot}(a,j)\in\{\mathrm{ABSENT},\mathrm{PENDING}(\mathrm{id}_b),\mathrm{SATISFIED}\}$。每 agent 一条 cut 承诺记录：尾 id、尾终态、已发布/授权/缓存可生效集合。

**删除时机** 已 finished 动作的正文、出边、全部槽即可删；无需按顶点保留任何完成历史——只保留引用它的槽上的 SATISFIED 位。$b$ 的正文可在 $b$ finished 且所有 $\mathrm{PENDING}(b)$ 已翻转后删除。水位 $F_i$（每 agent 已删前缀最大 index）单调，仅用于 id 合法性判定。

**生命周期** 槽只能 $\mathrm{PENDING}\to\mathrm{SATISFIED}$，且仅由中心收到执行完成通知触发；消费/位置证书不得视为 finished。

**收费** 槽的建立/翻转/删除、闭包 $P$ 的计算、情况三对 $S_j$ 的重扫（每 $(a,j)$ 一次）、承诺登记与 cut 写入全部计费；槽总量以未完成前沿×agent 数为界，无零费无限历史（不主张固定内存，不主张任意 GC 后可恢复）。

**分层声明** 以上仅给出：(i) 图语义等价（活依赖同 $\mathrm{A1}(R)$）；(ii) 逻辑入队非自锁（无环⇒存在可入队序）。不由此推出连续物理安全（另需源动作端点/共同几何接续验证、逐边停止与已发布动作不可撤的适配），也不推出付费服务进展（需真实完成通知、计费与授权链）；不声称作者原样性能。

END_C34_H19_SPLICE

## 首次网络失败原回执

```json
{"is_error":true,"duration_api_ms":0,"num_turns":1,"stop_reason":"stop_sequence","session_id":"8a81c516-dace-44c8-bdf7-bf13c020f930","total_cost_usd":0,"usage":{"output_tokens_details":{"thinking_tokens":0},"input_tokens":0,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{},"permission_denials":[],"terminal_reason":"api_error","fast_mode_state":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subtype":"success","api_error_status":null,"result":"API Error: Can't reach the API server — check your internet or DNS (FailedToOpenSocket)","type":"result","duration_ms":175744,"uuid":"9eafbd8d-c585-46aa-9a05-9200ce7f9477"}
```
