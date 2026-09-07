# 73T1：终点待消费 phase 与私有游标权限合同候选

状态：CONSTRUCTIVE / NO-SKILL / NONBALLOT；供后继整合的文字候选，未固定 73，未启动正式审查，未取得通过票。

## 1. 读取边界与本候选结论

唯一科学来源为 `/home/lyh/MAPF_PIED_MDDR_RESEARCH/72_PIE_CENTRAL_SPATIAL_RETIREMENT_AND_PAID_OBSERVATION_PREEXPERIMENT_CANDIDATE_20260906.md`。
实际只读该文件 L78–150 与 L164–188，即任务指定的 §5–8 和 §9 付费主体片段；没有读取 skill、旧审稿、Claude 材料或其他科学文件。
以下是从这些片段提出的候选补充，不把它们描述为 72 已经明文具备的全部条件。

最小补充是：不可逆 END 建立 `TERMINAL_UNCONSUMED`；中心 FINISHED、READY 在途、READY 已验证，都不能自行退出该 phase。
只有绑定该终点记录的 executor LOCAL_POLICY 一次消费提交，才能使 `c:k→k+1` 并打开下一原槽的 resident 入口。
中心 SOURCE_REQUEST 仅用已付费交付的 Kc 选择原 MOVE；executor LOCAL_POLICY 可读自己的 c 消费原 WAIT 或匹配 READY，但不给中心发送由 c 选择出的“正确下一步”。

## 2. 最小记录与不混淆的两端状态

原 occurrence 身份为 `o=(session,plan_epoch,i,k)`；原记录为 `Π_i[k]=u, Π_i[k+1]=v, kind`。
MOVE 要求 `u≠v` 且源计划记录类型为 MOVE；WAIT 要求源记录类型为 WAIT 且 `u=v`。k 是原起始 slot。
executor 独占写真实 c、控制记录与消费标志；中心独占写 owner、请求记录、d_i 及 FINISHED。任何一端都不以指针别名读取另一端的私有状态。

executor 保留 `phase, c, resident_gamma, resident_ref, active_tid, command_revision`，以及至多一个 `terminal_pending`。
`terminal_pending=(tid,o,u,v,parent_gamma,gamma_prime,closed,ready_verified,consumed)` 在 END 时持久建立；初始 `closed=true, ready_verified=false, consumed=false`。
`Ended(o)` 表示该 occurrence 已产生不可逆 END；当前未消费槽必须可由 terminal_pending / 保留 closed 记录判断，不能把 active_tid=NONE 当作其否定。
已消费旧槽由单调 c 和关闭水位拒绝重放；本合同不要求为每个旧槽增加无限位图。当前终点记录至少保留至后继新 grant 进入，遵守 72 的保留边界。

| executor phase | 明确条件 | 可发生的下一本地动作 |
|---|---|---|
| RESIDENT_OPEN | active_tid=NONE；terminal_pending=NONE；有持久 resident_gamma 与 resident_ref | 原 WAIT 的一次消费；原 MOVE 的 PRECHECK；保持 reference HOLD |
| GRANT_ARMED | 唯一 tid 的 grant 已验证接纳；active_tid=tid；当前原 MOVE 未 END；c 为其 slot；started=false | 对同 tid 首次 START；未启动时保持覆盖；不消费 |
| MOVE_LIVE | 唯一 tid 已进入；active_tid=tid；started=true；其原 occurrence 未 END | 同 tid 已承诺的流/制动/HOLD；满足端点守卫后 END |
| TERMINAL_UNCONSUMED | active_tid=NONE；terminal_pending.closed=true；c=terminal_pending.k；consumed=false | 付费生成/重传 END 证据；接收验证 READY；匹配的一次 MOVE 消费；reference HOLD |
| QUARANTINE | 上述持久记录互相矛盾，或原槽/绑定/覆盖证据不能满足所需谓词 | 不开始新原槽、不清资源、不制造可消费 WAIT；保留既有物理责任 |

RESIDENT_OPEN 可对应中心无未关闭请求、当前 UNGRANTED、或中心 GRANTED 而 grant 尚未被本地接纳；最近关闭历史也可为 ABORTED 或已消费的 FINISHED。中心请求状态不等同于 executor phase。
GRANT_ARMED/MOVE_LIVE 对应中心 GRANTED；TERMINAL_UNCONSUMED 可对应中心仍 GRANTED，也可对应中心已 FINISHED。
中心 FINISHED 对 executor 不是免费可读变量；本地只读自己已交付并验证的 READY 标志。
READY 在途与 READY 已验证只是 TERMINAL_UNCONSUMED 的子状态，均禁止 PRECHECK、START、新原 WAIT 消费及新原 MOVE 执行。
对发生在上述 phase 之外的同名事件，按 §5 的拒绝谓词返回，不隐式补阶段。

## 3. PRECHECK：捕获、稳定性与中心准入

请求 `p=(tid,o,u,v,parent_gamma,geometry_version,plan_epoch)` 先由中心 SOURCE_REQUEST 用 §6 的权限产生；其 e 必须是中心当前唯一未关闭请求序号。gate 验证可信来源与固定请求绑定，不免费读取中心 d_i；本地 g_i 也不能替代 d_i。
gate 的 ENTRY/PRECHECK 作业只有在付费 CAPTURE 的同一视图内同时满足下列条件，才可封存成功证明：

1. session、签发角色、agent、原计划代际及请求身份验证成功；源计划中 slot k 存在，记录恰为请求的 MOVE u→v。
2. `phase=RESIDENT_OPEN`、`active_tid=NONE`、没有已接纳尚未启动的 grant，且 `terminal_pending=NONE`。
3. gate 当前持久 resident 身份恰为 `parent_gamma`；其参考顶点 `resident_ref=u`，且为 reference HOLD、参考速度为零。实体覆盖证据仍绑定该 resident。
4. `true c=k`，该 occurrence 未消费，且 `Ended(o)=false`；“slot 相等”不能取代后两个条件。
5. 此请求的固定原记录/计划代际/parent/命令依赖与捕获的版本相等；不是普通消息伪造的新原步或新序号。

成功证明绑定全部身份、原边、slot、resident 参考起点、未 END 谓词、版本和 CAPTURE 点；不返回正确下一 slot 或其他游标值。
任何一项不满足，不产生成功证明。authority 内部可记录具体失败谓词，但向中心只返回绑定原 request_id 的付费 `DEFERRED_REJECT`；不附真实 c、当前位置或修正原边。
付费检查不足完成 CAPTURE 时没有读取；捕获后离散依赖变化使准备结果失效，实际接纳检查不能以旧快照覆盖新状态。

稳定性界限是“成功 PRECHECK 捕获后，到对应 grant 接入或请求明确失效之前”，不是证明永久有效。
此时当前槽为 MOVE；无 grant 时不能消费该 MOVE，也不能走 WAIT 分支。terminal_pending 为空，故不存在可消费该槽的旧 READY。
小于 k 的 READY 是已消费旧槽，大于 k 的 READY 不匹配当前槽，等于 k 的 READY 只有在对应 END 先建立 terminal_pending 后才可能消费。
对应 END 又要求该 occurrence 的 grant 先接入。因此迟到旧 READY 不可能在这段区间把 c 从 k 推走。
重复旧 READY 的拒绝不改 c、parent、phase 或 command_revision；处理记录的幂等缓存不得冒充相关命令版本变化。
若对应 grant 已接入/执行，或 parent/代际/请求关闭状态明确变化，后到的证明必须重新按当前准入谓词检查，不能援用上述区间外的稳定性。

中心授予时还须在其付费串行提交内同时满足：当前请求恰为 tid 且 UNGRANTED；`e=d_i+1`；不存在另一未关闭请求/活动 tid；请求绑定与证明完全相同；当前中心 resident parent、原记录与几何版本未失效；M0 每一资源均为 FREE 或同 agent 的该 parent resident；parent E 包含于 U(0)。
通过时一次改 M0 tag、记录 GRANTED、封存 grant；资源冲突时不部分预留，保持 UNGRANTED；其他绑定/水位/版本失败则明确拒绝，按 72 移除失效阻塞记录。
中心只从付费 ENTRY 证明使用 `c=k` 的限定准入事实，不把它登记成 CURSOR、不推进 Kc，也不据此构造后继 slot。

## 4. END → FINISHED → READY → 一次消费

**END：** `phase=MOVE_LIVE, active_tid=tid, c=k`，同 tid 已接纳控制器到达所绑定参考终点，端点守卫为 `s=ell`、`v_ref=0`、参考顶点为 v，且 closed 尚为 false。
END 在世界全序的物理阶段不可逆地关闭该 tid 入口、提升 gate 已执行关闭水位、令 active_tid=NONE、建立 gamma_prime 与 terminal_pending，并进入 TERMINAL_UNCONSUMED。
END 不消费 c，不改中心 owner/d_i，不生成免费可信证书；同一 tid 的重复 END 不重建 latch、不重开入口。

**中心 FINISHED：** 付费 END 证据经生成/交付/验证后，中心检查 session/tid/o/原终点/parent/gamma_prime/closed 与当前 GRANTED 完整一致。
检查通过后一次把端点 Mask(E) 从 tid 转为同 agent 的 gamma_prime、删除该 tid 其余保留、记录 FINISHED 和 d_i=e，再封存 READY 供后继发送。
水位已关闭或当前 tag/tid 不匹配的重复/迟到 END 不改任何新 holder。普通 COMPLETE、NONE、超时或本地 latch 不能替代这次提交。
中心 FINISHED 只解除旧运动资源责任并建立中心 resident，不打开本地原槽入口，不写 c。

**READY 接收验证：** READY 必须来自本会话中心 authority，证明 FINISHED 已提交，并与 terminal_pending 的 tid/o/原边/终点/gamma_prime 完全匹配。
第一次匹配验证的付费提交只设 ready_verified=true；不消费 c。尚未 END、无 pending、字段不符、错误会话/代际或伪造 authority 均拒绝。
同一匹配 READY 重复验证只返回已登记结果；不新增消费许可。此处不允许把一个 READY 拆成多个计数票。

**LOCAL_POLICY MOVE 消费：** 付费输入捕获并准备消费后，实际发布仍须复核 `phase=TERMINAL_UNCONSUMED`、`c=k`、pending.o 为当前原 MOVE、closed=true、consumed=false、ready_verified=true、active_tid=NONE，且 pending/gamma_prime/原记录/代际的绑定未变。
还须确认当前 reference HOLD 的参考顶点为该原终点 v，resident latch 为 gamma_prime；若所需记录不一致，不消费并进入 QUARANTINE。
一次原子提交将该 occurrence 标为 consumed、令 `c=k+1`、将 gamma_prime/v 作为 RESIDENT_OPEN 的 resident、清除当前 pending，并保留规定的 closed/幂等证据。
该提交不生成后继原请求，不连锁消费下一 WAIT/MOVE；下一槽等后继属于相应角色的付费机会。
候选计算、READY 投送、FINISHED、HOLD、重复 POLICY 发布均不能提前或再次消费。

## 5. 事件总拒绝与一次性条件

| 事件/输入 | 接受条件之外的处理 | 保持不变的责任 |
|---|---|---|
| PRECHECK | §3 任一谓词不满足，回不泄露真值的 DEFERRED_REJECT；费用保留 | c、旧 latch、grant 与资源责任 |
| grant 首次接入 | session/authority、`e>g_i`、当前 c=原 slot、原边/parent/版本/唯一授权任一不符，或 phase≠RESIDENT_OPEN、pending 非空、Ended(o)=true，则拒绝；同一已接纳 tid 只返回幂等结果 | 不重开 END occurrence，不重复接纳 |
| 首次 START | phase≠GRANT_ARMED、active_tid≠指定 tid、started≠false、closed≠false、c≠原 slot，或已验证命令/parent/起点 HOLD 依赖不匹配，则拒绝/等待；已启动同 tid 只返回幂等结果 | 不重复 START，不因等待清 M0 |
| CANCEL | e≤d_i 拒绝重开；e 跳号拒绝；未授当前请求可 ABORTED；GRANTED 返回 DENIED_GRANT_LIVE | 已授责任和未消费 c |
| END 证据 | 没有匹配 closed 记录返回 NO_MATCH；旧 tid/tag/水位不匹配不释放 | 新 holder 与 endpoint 覆盖 |
| READY | 无匹配 pending 或字段不符拒绝；pending 内重复已验证只幂等登记；已消费旧槽返回 STALE_OR_CONSUMED | 不增 c、不改 parent/phase/相关命令版本 |
| LOCAL_POLICY 原 WAIT | 非 RESIDENT_OPEN、c/原记录不匹配、active 或 pending 非空、resident_ref 不等于原起点，均不消费 | 既有物理/资源责任 |
| LOCAL_POLICY MOVE 消费 | §4 消费谓词任一失败则不提交；重复已消费结果只返回幂等状态 | c 不回滚，不新增消费票 |
| 未登记/未知事件身份 | 返回 NO_REQUEST / NO_MATCH；不从未来或其他臂补造对象 | 原账本与物理责任 |

grant 的首次接入必须重复使用 PRECHECK 已证起点绑定，并在实际接纳点检查 RESIDENT_OPEN、无 terminal_pending、无 END 和当时命令/parent 依赖；检查失败不可只靠旧证书继续执行。
同一 occurrence 的 END、READY 登记与消费是三个不同的一次性位；中心 FINISHED 是第四个不同提交，不能以其中一个推断其余已发生。
所有拒绝、重复解析/验证/缓存/发布检查按实际工作收费；不因无状态变化就免费。

## 6. 主体读权限：SOURCE_REQUEST 与 LOCAL_POLICY

| 主体/角色 | 可付费读取的输入 | 可写/输出 | 不可作为输入或输出捷径 |
|---|---|---|---|
| 中心 SOURCE_REQUEST | 已交付 CURSOR 形成的 Kc；不可变 Π/L/代际；中心当前 parent、d_i、唯一请求、模式与已收费几何 | 最多一个绑定 Kc 原 MOVE 的请求，或其同身份重试，或明确空结果 | 本地 c、pending/READY 消费位、由 executor 提示的正确 slot、POSITION 猜出的逻辑进度 |
| executor LOCAL_POLICY | 自己的 c/phase/原记录、已交付并验证的 READY、自己的命令/latch，以及获准已交付知识 | 最多一次原 WAIT 或 READY 对应 MOVE 消费；本地保持/继续既有责任 | 向中心/QUERY/planner 发送由私有 c 选出的下一 MOVE；把消费同步写到 Kc |
| ENTRY/PRECHECK authority | §3 所列本地视图，先付费 CAPTURE | 所请求原 MOVE 的限定准入证明或不带真值的拒绝 | 回传正确下一步、通用新游标、额外位置值 |
| CURSOR authority | 自己的当前 c，先付费 CAPTURE | 冻结的 CURSOR 身份/样本点/c，经后继付费交付才更新 Kc | 在完成或重传时刷新 payload |
| 中心 QUERY | 72 §7–9 已付费捕获的 Active/P/owner/Mask(E)/last/模式 | 按规定总函数选择 POSITION 请求 | executor 的 c、READY 消费位、私有 WAIT 次数或由其驱动的旁路索引 |
| planner / PROJECT | 已交付 Kc、K_task、Π 和冻结环境 | 既定源输出、受检追加候选 | 活的 executor 引用、未交付 CURSOR、终点/WAIT 私有日志 |

SOURCE_REQUEST 的选择总函数为：若模式禁止新 occurrence 则 STOPPED；若已有未关闭请求则只处理其原绑定，不能凭新 Kc 覆写它；若 Kc 未知则 NO_SOURCE_INPUT；若 Kc=L 则 NO_REMAINING_SLOT；若 `0≤Kc<L` 且原槽是 WAIT 则 NO_MOVE_REQUEST；若该槽是 MOVE 才提 `(slot=Kc,u=Π[Kc],v=Π[Kc+1])`；索引/原记录不成立则拒绝输入。
Kc 的变化只能来自已验证交付的 CURSOR（及 72 的共同初始证据）。READY 所证旧 MOVE 已终结不意味着 executor 已消费，不能令中心自行写 `Kc=k+1`。
本地 LOCAL_POLICY 的分支依次为：存在匹配已验证 READY 且满足 §4 则消费一个；TERMINAL_UNCONSUMED 但尚不可消费则 HOLD；GRANT_ARMED/MOVE_LIVE 则继续同 tid 责任；RESIDENT_OPEN 且无剩余槽则 HOLD；RESIDENT_OPEN 且当前原槽 WAIT 则按下段消费一个；当前原槽 MOVE 则本地等待中心来源请求/授权；记录不一致则 QUARANTINE。
WAIT 的提交谓词为 `phase=RESIDENT_OPEN, active_tid=NONE, pending=NONE, true c=k`，原记录是 `u→u` 的 WAIT、未消费、reference HOLD 的 resident_ref=u、resident latch 与捕获/提交绑定一致。一次提交只做 `c:k→k+1`，位置、resident、Kc 均不变。

SOURCE_REQUEST 与 LOCAL_POLICY 是对 72 请求生成/消费职责的候选显式拆分，不是新 O 事件类型。
为防止“只有本地看到 MOVE 才替中心触发请求”成为免费提示，角色归属须由既有 POLICY 公共描述符中的固定主体标记决定；不由 c、pending、READY 或本地分支决定是否给中心一个机会。
一个 POLICY token 只归属一个角色，最多提交一次消费或一个新原请求；无主体标记返回 NO_ROLE，不现场猜主体。后继需共同声明这些标记，不能依某臂收益或私有进度分派。
本报告不列任何 O 行、时刻、数量、频率或实验参数，也不补建公共机会表。该主体标记是拟议接口约束，尚不是已经存在的实现事实。
SOURCE_REQUEST 和 LOCAL_POLICY 都支付实际捕获/计算/版本检查/提交成本；各自 writer 槽及后继发布规则维持 72 的串行提交约束。
读取自己 c 的权限不跨越角色；即使共享进程、同一日志系统或同一对象库，也不能由 SOURCE_REQUEST/QUERY/planner 解引用私有字段。
PRECHECK 的成功/拒绝是已付费 ENTRY 的业务结果；其中心准入用途不等于免费游标接口。调试日志、执行耗时、队列长度、消费 ACK 等也不得被算法再解释为 Kc 或正确下一槽。
该合同规定算法可用信息与读接口，不声称消除了实现中一切物理时序侧信道。

## 7. 纯 WAIT 链与选择后果

若当前是原 WAIT，LOCAL_POLICY 可在每个归属于自己的后继付费机会独立推进一个；即使中心 Kc 长期不变，纯 WAIT 链仍可逐槽本地推进。
SOURCE_REQUEST 看到旧 Kc 的 WAIT 时返回 NO_MOVE_REQUEST；看到旧 Kc 的已结束 MOVE 时可能产生旧槽请求，但 PRECHECK 按明确谓词拒绝，不能由拒绝修正 slot。
到达下一原 MOVE 后，本地保持 resident 并等待中心根据足够新的付费 Kc 产生来源请求；不发带正确 slot 的“请推进”消息替代 CURSOR。
因此本候选不额外强制“每个 WAIT 先等 CURSOR”，但从 WAIT 链进入 MOVE 或从已消费 MOVE 进入后继 MOVE，可能仍等待固定 CURSOR 的捕获、处理、交付和中心 SOURCE_REQUEST 机会。
快照在中途 WAIT 后捕获并在更晚 WAIT 后交付时仍只更新到捕获值；再次知道更远进度须新请求及新付费 CAPTURE。
若改为所有本地决策也等待 Kc，纯 WAIT 会新增观察依赖和延迟；若允许 executor 用 c 直接选 MOVE，则改变此处中心来源权限与信息/成本合同。两者均不是本候选默认许可。
固定主体分派减少每个角色可用的 POLICY 机会，可能增加排队/等待；本地消费与中心源选择的工作均须计费，不能以拆角色隐藏费用。此处不判断净性能优劣。

## 8. 纸面事件序：迟 READY 在 PRECHECK 前、后与重复

以下只是符号级先后关系，不是 O、实验载荷或调度表。每个 CAPTURE、生成、投送、验证与提交均遵守 72 的付费及严格后继发布要求。

**序列 A：迟 READY 先到，但 PRECHECK 早于消费。**
`MOVE(k,u→v) END → TERMINAL_UNCONSUMED,c=k → 中心 FINISHED → READY 延迟投送并验证 → 旧 Kc=k 的来源请求尝试 PRECHECK → 后继 LOCAL_POLICY 消费 READY`。
PRECHECK 时 ready_verified=true 仍不够：phase 不是 RESIDENT_OPEN、pending 非空、Ended(o)=true，且 resident_ref=v≠u，所以拒绝，哪怕 true c=k。
后继消费把 c 推到 k+1；拒绝的旧请求不能获得可执行 grant。

**序列 B：PRECHECK 尝试先到，迟 READY 后到。**
`END → 中心 FINISHED → 中心基于旧 Kc=k 提旧原 MOVE（新请求序号也不能改原 slot）→ PRECHECK → READY 延迟验证 → LOCAL_POLICY 消费`。
PRECHECK 时无 READY 不能被理解成“该旧 occurrence 未执行”：closed/pending 已持久存在，明确拒绝。
READY 后来只使该 pending 获得一次消费条件；消费前后均不能复活此前失败的证明。若新请求仍未关闭，中心按唯一请求/水位规则处理其关闭，不能并发另开一个。

**序列 C：后继 PRECHECK 已成功，旧 READY 再延迟或重复。**
`旧 k 的 END/FINISHED/READY → 一次消费 c=k+1 → 新 CURSOR 捕获并交付 Kc=k+1 → SOURCE_REQUEST 提后继原 MOVE(k+1,v→w) → PRECHECK 成功捕获 → 旧 READY(k) 重传/延迟到达 → 后继 PRECHECK 结果交付及准入`。
在成功捕获时 phase=RESIDENT_OPEN、resident_ref=v、c=k+1、pending 为空、后继 occurrence 未 END。
旧 READY 的 slot 为 k，已消费；即使旧终点记录尚保留，它也不等于当前 pending，返回 STALE_OR_CONSUMED，不改 c/parent/phase/相关命令版本。
同一个旧 READY 任意有限次重复均得到相同无消费效果；成功 PRECHECK 的稳定性因此不被旧 READY 破坏。若后继 grant 已先接入，后到 PRECHECK 按当前 GRANTED 状态拒绝重复准入。

**序列 D：同一 READY 的重复 POLICY 发布。**
`匹配 READY 验证 → POLICY 准备消费 k → 第一次消费提交 c=k+1 → 同一准备结果/READY 再发布`。
再次提交的 `c=k`、pending 当前身份、consumed=false 至少一项不成立，不能消费 k+1；旧消息不能顺手作用到下一原槽。

**序列 E：纯 WAIT 的私有推进与滞后知识。**
`Kc=k,c=k，原 WAIT → LOCAL_POLICY 消费至 k+1 → CURSOR 付费 CAPTURE 冻结 k+1 → 后继 LOCAL_POLICY 再消费原 WAIT 至 k+2 → CURSOR 交付只使 Kc=k+1`。
两次 WAIT 均逐次验证 RESIDENT_OPEN、原顶点/slot 与未消费状态；中心/QUERY/planner 在交付前看不到新 c，交付后也不能把证书刷新到 k+2。

## 9. 中点 HOLD 与结论边界

如果后继另提可变 cap，中途停止只可作为同一 tid 的 MOVE_LIVE/HOLD：原 occurrence 未 END、c 不消费、中心仍 GRANTED，剩余覆盖与原责任继续保留。
中点 HOLD 不能建立 endpoint resident、生成 END/READY、通过新 PRECHECK 或消费一个伪 WAIT。本报告不设计 cap 更新、RESUME 或完整 cap 协议。
以上仅给出终点 phase、限定主体权限、拒绝和一次性保持论证；未证明全系统无死锁、通信恢复、正吞吐或性能改善。
H、T_delay、B_CAL、B_max、B*、P_active、density、N 均未赋值、范围或默认值。

## 10. 本次真实执行回执

- 创建前以只读存在性检查确认目标文件不存在；退出码为 0。
- 唯一科学读取命令为指定 72 文件的 `sed -n '78,150p;164,188p'`；退出码为 0；命令经 `rtk proxy` 执行。
- 写作前工具时钟为 `2026-09-07 13:34:48 UTC`（北京时间同日 21:34:48）；这是取得的真实时刻，不冒称后续写入完成时刻。
- 本报告通过 apply_patch 新增；未修改 69–72 或旧报告，未触达禁止的 35–38、Q-CAL、Q-CONFIRM、results、受限载荷或桌面。
- 新建后只读检查了本报告正文，并仅用 apply_patch 补明本地 phase 与中心 grant 在途的对应、gate 不读 d_i，以及 START/END 的具体接纳谓词；此为作者文字核对，不是正式审查或实验。
- 未读取 skill；未创建子代理；未启动正式审查；未实现、构建、创建或运行测试/仿真、调参或生成载荷；未生成 O。
- 完成写入后的 SHA-256、字节数与行数由独立只读命令核对，在交付消息中报告；正文不嵌入对自身终稿的自指哈希。
- 本回执只证实这份候选工件和上述实际动作，不把文字事件序当实验结果，不声明后继 73 已固定或已通过审查。
