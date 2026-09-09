# 73P4：付费 END 推送、前缀权限与共同服务组合

2026-09-09。独立有界建设性 **NO-SKILL / NONBALLOT** 回执；不是正式审查或主策略定案。本文仅新增一个可供根整合的终点服务合同，不改 73、P2/P3、L3、账本或 Git，不重解 cap 贪心反例及失落的异步环问题，没有 spawn 或 Claude 调用。

保持 **HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT**。未实现、编写代码/伪代码、构建、创建或运行研究测试、仿真、调参、生成实验载荷/结果或控制机器人。下面是声明式状态、消息、权限及费用合同。

## 1. 当前读取与问题定位

本次先核新文件不存在，完整读取当前 73 的 §5、§7、§9；读取 L3 的 §4.1–4.3，包含其付费 END 推送提议。此前 P2/P3 是本 agent 已完成的独立文本，本次只承接其权限接口，不重做其任务。

| 输入 | 开始实核 SHA256 | bytes / lines |
|---|---|---|
| 73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md | decef3a8908b21796c3ff86eaf2a8361289c76d13cbd09b1f45d66c1b138b38f | 109595 / 418 |
| 73L3_PUBLISHED_LIFELONG_COMPARATOR_ADAPTATION_AND_PROVENANCE_20260908.md | e0c21289ea3047ff3aa72b1871dc4f39044074a7227268b2572d9a0db5ba5dd | 32022 / 201 |

新版 73 在真实 END 原子地清 active_tid、令 resident_ref 为原终点、resident_gamma 为 NONE；在合法一次消费时先从 pending 复制新 resident 身份再清 pending。这条修复可以组合，但 §9 的“END 只关旧 tid 并建立 latch，其余修改走应用提交”必须明确包含这些 END 字段写入，否则文字上仍有两个不相容的写域描述。

L3 要求外部方法可以付费推送终点事实，而非只能等中心主动轮询。本报告把这项能力接成首推、重放、轮询合流、中心 FINISHED/READY 缓存及本地消费的完整链。物理 END、本地历史证据封存、传输、中心知道 END、中心 FINISHED、READY 验证和原槽消费是七个不同节点；不能压为同一“完成”。

## 2. 共同身份、记录与单一写域

原动作身份 alpha 绑定 session、物理 agent、source_family/source_job、plan_epoch、原 action/slot index、原 u→V、MOVE 类型、几何/控制版本、tid 和 parent_gamma。PIE 臂的原 index 仍是起始 slot k；H19-PR-COMMON-SYSTEM 绑定其真实外部源动作，不把外部求解器改名为 PIE。协议不创造新的原边或任务。

一个原 MOVE 最多发生一次真实 END。其 end_id 是 alpha 与本地不可逆关闭代际的唯一组合，不能按重传次数生成新 end_id。新 gamma_prime 由这一完整身份确定并保存，不因 push/poll 先后或证书重传改变。

本地终点对象分为两部分：**不可变 EndRecord** 保存真实 END 的原事实及新 gamma 候选；**可变 TerminalHandshake** 保存 ready_verified、consumed、证书缓存引用和重试账。pending 指向这两部分。旧网络/服务作业可 pin 不可变记录；消费清 pending 不等于销毁仍有引用的历史记录，也不允许旧服务作业把 pending 再写回。

| 状态或对象 | 唯一逻辑 authority / 写入事件 | 禁止的旁路 |
|---|---|---|
| s/v/z、混合模式与真实 END 守卫 | 本地可信控制 authority；连续流及物理优先的已列明混合转移 | 应用服务槽不能锁住物理流，中心不能改真实进度 |
| phase、active_tid、resident_ref/gamma、pending、g_i | 同一本地状态 authority；其实际 ACTUATOR/应用提交及下节规定的唯一原子 END 转移，按公共全序串行 | 不允许多个线程各覆盖同一字段；END 的字段变化不是普通后台应用写入 |
| c、ready_verified、consumed | 同一本地状态 authority 的收费应用提交；END 不消费 c | READY 接收者、网络站或中心不能直接推进 c |
| EndRecord | 原 END 转移创建一次，此后只读 | push/poll/重传不能刷新为当前 pose 或当前 c |
| EndProofCache、发送意图、服务引用及 GC | Srv_E(i) 对应本地应用 writer | 物理守卫不签名/编码证书，网络站不改证据语义 |
| owner、中心活动状态、d_i、FINISHED/READY 缓存、Kc | Srv_C 的唯一中心 writer | 本地 END token、普通 COMPLETE、网络送达本身都不能写入 |
| 通道排队/编码/发送/有限副本 | 既有 Srv_N(u,v) 的通道 writer | 通道不能直接改 owner、pending 或 c |
| H19 ADG 的 enqueued/finished 等算法状态 | Srv_C 同一中心 writer 内的 H19 收费算法作业，使用已经合法交付的共同收据 | 不读取本地 EndRecord 或把 POSITION 当 ADG finished，不另开免费算法服务站 |

本地“一个 writer”指一个逻辑状态 authority 和唯一全序提交语义，不代表占住一个应用作业槽就能阻挡控制守卫。END 可以在本地应用作业尚在计算/等待发布时先发生；后者发布必须复核当前 phase、终点 fence/g_i 及其特定依赖，失效就无作用，不能把旧快照写回。

## 3. phase 字段的完整约束及真实 END 原子转移

| phase | 本地字段的有效解释 | 允许的终点/控制作用 |
|---|---|---|
| BOOTSTRAP | 当前 bootstrap HOLD；无新 MOVE、无原 END pending | INIT 以外应用业务返回限定未就绪结果；不能凭普通完成消息造 END |
| RESIDENT_OPEN | active_tid=NONE、pending=NONE，resident_ref/gamma 为当前合法 resident | 新原 MOVE 仍须完整 PRECHECK/预留；WAIT 一次消费；旧 READY 无作用 |
| GRANT_ARMED | 唯一 active_tid，尚未 START，pending=NONE | 安装合法累计 cap；实际合法 START；no-start 不消费。保留的旧 resident 字段仅是 parent 绑定，不是新增 resident 授权 |
| MOVE_LIVE | 唯一原 tid 的运动/BRAKE/HOLD，pending=NONE | 同原 MOVE cap/RUN/STOP；真正原 END。若还保留 resident_ref=u/parent_gamma，它们只是旧起点元数据，不能当实际当前位置 |
| TERMINAL_UNCONSUMED | active_tid=NONE，resident_ref=V，resident_gamma=NONE，匹配 pending 且 c=k | 封存/重放 END 证据，验证 READY，后继合法一次消费；拒绝新 PRECHECK、cap 和 RUN |
| QUARANTINE | 保留所有尚存物理责任与历史记录，不把 NONE 当清空 | 无新授权/消费；已缓存历史收据可收费重放，其他新应用作用返回限定隔离结果，不伪造恢复 |

唯一真实 END 守卫为：MOVE_LIVE、同 alpha/active_tid、原 c=k 且原 occurrence 未关闭，可信 s=ell、v_ref=0。前缀不变量 s≤C≤b≤ell 在此蕴含 C=b=ell；仅到 C<ell 的中点 HOLD 永远不触发这个守卫。

在该物理优先转移中，作为一个不可拆分的本地状态变更：关闭原入口并推进 g_i；建立 EndRecord 与 pending；phase 置 TERMINAL_UNCONSUMED，参考 HOLD；active_tid 置 NONE，resident_ref 置 V，resident_gamma 置 NONE；c 保持 k，ready_verified/consumed 为 false。原 tid、u/V、parent、gamma_prime 和控制/几何身份先保存到不可变记录，不能因清 active_tid 而失去证明对象。

EndRecord 至少包含 end_id、alpha、原 u/V/ell、parent_gamma、gamma_prime、原 END 守卫事实、不可逆 closed 标志、物理 END 的权威事件点、源/几何/控制版本和本地记录提交身份。它不包含后来的新 c、任务完成计数、任意时刻当前 pose，亦不声称真实刚体绝对静止；长时端点仍用 E=V+K 覆盖误差运动。

END 同时仅留下一个绑定 end_id 的**本地不透明待服务引用**。其固定描述符登记、记录持久化、守卫和字段位长费用归共同控制基础设施，明确计入；它不是已签发 END 证书，不是中心消息，也不直接更新 Active/owner/Kc/ADG。真实任务服务仍由独立公共环境判断，不由这个 token 计分。

对已有原控制责任，不能因为 Srv_E 被占用就推迟真实到达、略去 END 或重跑控制。共同控制域必须能够在该事件点完成所列原子记录，且承担其明确费用；若实际物理/记录事件不能认证，按原故障合同保留未知或无效，不能把一个未完成 latch 的事件记成成功推送。本文没有用无限免费控制容量补这个前提。

## 4. 消息字段与它们分别能证明什么

下表字段均是合同，不是实际载荷。每种 envelope 另有发送/接收角色、语义消息 id、传输 attempt/copy 身份及编码版本；改变传输 attempt 不能改变物理 end_id 或证书采样点。

| 类型 | 必需语义字段 | 接收者可据此作的限定作用 |
|---|---|---|
| LOCAL_END_OFFER | end_id、不可变 EndRecord 引用、本地 earliest-eligible 行 | 仅允许本地后继收费服务访问；中心不可见 |
| END_POLL_REQUEST | 请求 id、alpha、预期原 u/V/parent/版本、目标 agent、kind=END | 请求一次限定 END 服务，不赋当前位置/c 读取权 |
| END_PROOF | end_id、alpha、EndRecord 的完整绑定和原 END/closed 事实、首次收费记录捕获 id/point、记录提交身份、签发 authority 及完整性证明 | 证明这一原动作历史上已真实 END；不直接证明当前 c、新边当前位置或当前 owner 已变 |
| END_NOT_YET / NO_MATCH / HISTORY_RETIRED | 原请求 id、限定 alpha、该次服务的捕获/处理身份及状态 | 明确本次没有可用匹配终点证据；不能推断空间清空或提高 q |
| END_PUSH / END_POLL_REPLY | 同一个 END_PROOF 的不可变引用/字节，另加 push或poll 来源及相关请求 id | 两种取得证据的通路，合流后按 end_id 去重；来源不同不构成两次 END |
| FINISH_RECEIPT / READY | alpha、end_id、gamma_prime、V/终点包络版本、中心 FINISHED 提交 id、唯一 READY id、中心 authority/完整性证明 | 证明原终点资源交接已提交，允许匹配 pending 的本地 READY 验证；不直接消费 c |
| CUM_CAP | alpha、原授权 lineage、单调 cap 序号、中心已兑现 b、不可变源/几何/parent 绑定 | 仅增加同原 MOVE 的本地 cap；不含 s/q、不要求已到 cap，不生成进度回报 |
| RUN / STOP | alpha、control_epoch、desired_mode、公开控制尝试 key、签发身份 | 当前守卫下的一次控制尝试，不能复用旧无作用尝试为未来恢复，不能替代 END |

END_PROOF 的记录捕获 point 是**付费读取持久历史记录**的时刻；EndRecord 中的 END event point 才是物理 END 的时刻。后续复制/发送/中心接收时刻另列，不将任何一个改名为新的动态物理采样。证明原 END 的历史事实与证明此刻仍在端点是两件事；首次中心完成之所以安全，还依赖原入口已经关闭且消费/新边准入受 READY 链保护。

## 5. 首次付费封存、事件推送与主动轮询合流

LOCAL_END_OFFER 只允许在严格后继公共行成为 Srv_E(i) 的候选作业；不能在创建 END 的物理阶段递归完成封装、网络和中心发布。Srv_E 的实际 PROCESS_SLICE 先按原事件规则推进物理及已完成结果，再执行队首收费工作。对尚无正证书缓存的首次封存，authority 的首个语义读取为付费 CAPTURE：固定指定不可变 EndRecord 的引用/版本，容量不足就没有读取或证书。已有正缓存时只走收费缓存查验/复制，不再次登记 CAPTURE 或新 sample point；本地 retry 读取自己的 pending/握手字段是普通收费应用读取，不假称新的物理采样。

首次匹配的正 END 服务在本地私有工作区完成字段读取/复制、绑定验证、完整性封装与签发，后继本地应用提交建立 EndProofCache[end_id]。缓存与封存后的发送意图同时合法可用，之后才可登记通道 token；sender 不持本地槽等待网络或中心。EndRecord 已不可变，工作期间新 READY/消费不改变被 pin 的历史事实；服务只能更新自己的缓存/发送记录，绝不重建已清除 pending。

首推与轮询用同一个正证书缓存。两种服务都在同一本地应用 writer 上串行：若自动推送先封存，后来的匹配 poll 直接重用同一 END_PROOF；若 poll 先捕获真实 EndRecord 并封存，后来的自动推送重用它。首次正封存只发生一次；缓存命中仍要支付查验/复制/封装 envelope/引用管理成本，不当免费消息。

主动 poll 在真实 END 以前实际捕获时，只返回该次限定 END_NOT_YET 或 NO_MATCH，不返回 s、C、实际 c 或正确下一槽。这个负结果只绑定其自己的请求/捕获点，不能永久缓存为“此 tid 永不 END”。重传这份旧负回执仍是旧负回执；以后要新鲜检查须新的付费请求。真正 END 随后发生时仍独立产生本地首推，不因旧负 poll 被取消。

已封存的 END_PROOF 以后可通过 push 重试、poll 回复或显式缓存重放发送；这些都没有新的动态 END 采样、没有新 sample point，也不重复计算真实服务。若本地旧记录已依合法 GC 规则退休，则返回 HISTORY_RETIRED，不用当前新边状态造旧 END；中心的 FINISHED 缓存恢复路径仍独立存在。

本合同不假设每个 END 只有一封网络消息。push/poll/有限网络副本可能同时在途，全部真实发送、接收、验证和拒绝费用保留；幂等的是原 END 的语义、中心资源交接和本地消费，不是把重复工作从成本账删掉。

## 6. 中心总接收与 FINISHED/READY 原子缓存

END_PUSH 与 END_POLL_REPLY 经既有 Srv_N 付费编码/传输后，只登记中心后继接收 token。中心自己的 Srv_C 作业才解包、验证完整性和来源、读取/复制证据以及检查当前账本。收到不透明 token 或普通 COMPLETE 不让中心提前移除 Active，也不提前唤醒 ADG 依赖。

下表以收到的 alpha 定位原请求/关闭记录；同 agent 已有后继当前 tid 不抹除仍合法保留的历史缓存。历史分支只重放自身收据或拒绝，不得据旧 alpha 改后来当前 owner。

| 中心当前状态与收到证据 | 唯一合法处理 |
|---|---|
| 格式、authority、alpha/end_id/版本或原绑定无效 | 收取已发生检查成本，拒绝；不改 owner/d/Active，不从失败猜真实状态 |
| 同 alpha 当前 GRANTED，首次有效 END_PROOF | 准备并收费核验完整终点交接、FINISHED 记录和完整 READY 缓存，完成后同一次中心原子提交 |
| 已 FINISHED，end_id 与完整绑定匹配且 READY 缓存仍在 | 只取既有 READY/FINISH_RECEIPT 准备后继重发；不再改 tag/d，不重新退休原资源 |
| 已 FINISHED 但同 alpha 的 gamma/end_id 等矛盾 | PROTOCOL_CONTRADICTION；不以较新包覆盖已提交身份 |
| 已 ABORTED、尚无合法 GRANTED 或合法生命周期不匹配 | 拒绝并保留原责任；有效可信 END 与未授取消矛盾属于协议证据问题，不复活已关请求 |
| 旧请求已由水位关闭且对应缓存按规则退休 | 返回限定 CLOSED/HISTORY_RETIRED；不重建 READY，不删后来新 holder |
| 中心 fail-stop | 不执行新的接收提交/重发，已提交 owner、FINISHED 和缓存不回滚；网络已发生费用保留 |

首次完成的原子提交必须同时完成：匹配当前 GRANTED tid/occurrence/parent/end_id/gamma_prime；检查终点 Mask(E) 当前归该原责任并连续保留；将 E 改为同 agent 的 resident gamma_prime、清其余原 tid 资源；记录 FINISHED/d_i；从 Active 及已失效阻塞需求中去除本 tid；存下可重发的完整 READY/FINISH_RECEIPT；登记后继发送意图。上述全部计算、owner访问、必要索引维护、记录/签发与发布检查都收费。

特别禁止“先提交 FINISHED、以后有空再生成可能丢失的 READY”。本合同的 FINISHED 状态就蕴含相应 READY 已在同一持久提交内可重放。若封装/签发/持久提交容量不足，整个变更仍是未发布的私有工作，旧资源继续保留；不能已经改 tag 却没有可恢复的收据。

READY 的实际网络发送仍发生于后继 Srv_N 作业，不与上述原子提交合并为免费通信。中心提交以后、首次发送以前故障，只是保留了一份尚未投送的合法收据；不证明本地已经知道或已经消费。

首次 END_PROOF 可以给中心限定的物理完成事实，真正 owner 交接仍需上述原子提交。H19 的共同适配在收到已合法提交的 FINISH_RECEIPT 后，用自己的收费 ADG 作业更新原动作 finished/后继使能；同中心可复用已付费验证的不可变证据而不再购买传感样本，但 ADG 字段读写/依赖处理仍收费。它不能从本地 END token 免费得到先发优势。D/R 的 Active 变化与 H19 的 ADG 变化具有各自明确时间，不当成同一个布尔位。

## 7. READY 接收、原槽一次消费及丢包恢复

READY 经后继通道送达本地后，Srv_E 验证完整身份和中心提交证明。只有匹配当前 TERMINAL_UNCONSUMED 的 pending/end_id/alpha/gamma_prime 才置 ready_verified=true；resident_gamma 仍为 NONE，c 仍 k。重复匹配 READY 是有费用的幂等验证，错误或已消费旧 READY 不改当前命令版本、当前 pending 或后继原槽。

后继 LOCAL_POLICY 的收费捕获和实际提交须同时满足：TERMINAL_UNCONSUMED、c=k、原 MOVE/occurrence 匹配、closed=true、ready_verified=true、consumed=false、active_tid=NONE、resident_ref=V、resident_gamma=NONE，可信参考保持于该原终点且 gamma_prime 完整绑定。唯一原子结果是先从已匹配 pending 复制 resident_ref=V、resident_gamma=gamma_prime，标记该原槽消费并令 c=k+1，保持 active_tid=NONE，之后清当前 pending，最后转 RESIDENT_OPEN。不能先清 pending 再尝试找回 gamma，也不能在同一 token 消费下一 WAIT 或生成新 MOVE。

这个转移与新版 73 的字段修复相容：END 的 NONE 表示尚未接纳中心新 resident 身份；READY 验证不提前填 gamma；消费用 pending 中受 READY 认证的 gamma 一次建立当前 resident。所有旧 parent 绑定来自旧原动作的不可变描述符，不能用已经置 NONE 的 resident_gamma 来错误地否定旧 END 证据。

**恢复路径一：本地重放已封存 END。** pending 尚未 ready_verified 时，公共 END_LOCAL_RETRY 作业重发同一 END_PROOF。若中心尚 GRANTED，正常第一次完成；若中心已 FINISHED，直接重发其缓存 READY。没有新的动态 END 采样，也不要求再产生一次物理 END。

**恢复路径二：中心直接重发 READY。** 公共 READY_CENTER_RETRY 作业只读自己的 FINISHED 缓存及已合法得到的消费证据，匹配未确认消费的最近终点则重发缓存 READY。它不向本地先查询 END，不读取私有 pending/c，也不将“已发送”当“已接收”。两种路径可以同时存在，重复字节和队列代价照实际收费。

如果 READY 已验证但 LOCAL_POLICY 未有合格容量，本地继续 TERMINAL_UNCONSUMED/HOLD、gamma=NONE；这不是资源未受保护。中心早已保留新 resident E，本地也没有新边入口。消费后的 Kc 仍必须通过原付费 CURSOR 或该算法既定合法知识接口更新；这里不把 END/READY 当通用 cursor 快照。

## 8. 缓存、历史重放与可收费回收

本地从 END 至合法消费前必须保留 EndRecord、必要握手状态和已经生成的 EndProofCache；不能因首推成功入队、发送次数或时间过长就删除。消费后还须保留所有尚被编码、在途或应用作业 pin 住的不可变对象，完成原 resident 接续并无引用后才收费 GC。g_i/单调 c 保留对旧授权/旧 READY 的拒绝能力，不依靠无限消费位图。

中心不得仅因 READY 已发过、未获 ACK、超时或本地不再推送而删除其唯一可恢复 READY。允许回收的事实基础是已经合法获得的同计划代际消费证据，例如既有付费 CURSOR 证明 c≥k+1，或后继原请求的合法付费 PRECHECK 明确证明前一原槽已消费且新 resident 绑定相符。后者只用于限定生命周期核验，不顺带更新 Kc 或赠送通用新 cursor。已有活动/消息/审计引用仍须先释放。

如果中心已合法得到这些事实，持久不回滚的本地状态不再可能合法需要旧 READY 来消费 k；旧 END 包可按关闭水位被拒绝，不能重放资源退休到新 holder。若没有消费证据，中心继续保留缓存并承担内存/查询费用；不承诺固定字节的无限期总内存界。

“FINISHED 但缓存无故丢失”不在正常 READY 丢包恢复路径内：它违反本报告原子持久缓存不变量，须标记协议/存储问题并保留当前 owner，不通过一次新的动态 END 采样伪造旧 FINISHED 的收据。中心 fail-stop 不重启的原模型也没有被本报告升级为任意崩溃恢复系统。

## 9. 公开服务机会、自动首推与唯一服务容量

本报告的组合配置称为 **PUSH_RECOVERY**：所有共同适配臂都启用真实 END 的本地首推及缓存重试能力；原 ENTRY(i,END) 主动轮询接口保留，但配置本身不要求任何臂定期购买无用的 END 动态查询。POLL_ONLY 或 PUSH_AND_POLL 可作为事前明确的其他共同配置；不能看收益后切换并仍把结果视为同一主比较。最终主配置由根固定，本文不代替该决策。

需在 73 机会文法中显式登记两个新的公共固定角色 END_LOCAL_RETRY(i)、READY_CENTER_RETRY(i)，以及唯一受允许的真实 END 本地首推来源。它们不动态增加服务器或 PROCESS_SLICE 容量。两个 retry token 的主体/writer 在公共描述符中已经确定，不由读取私有 phase 后临时选择中心或本地；没有对应业务时返回收费空结果。具体 O、容量和周期均未实例化、未赋值。

| 机会/来源 | 最早可作的事情及实际作业 | 唯一服务站/写域 | 对后继可见的东西 |
|---|---|---|---|
| 真实 END 物理守卫 | 原子 EndRecord/pending/NONE 字段转移及一个本地不透明待办；共同控制记录费 | 本地可信控制 authority | 仅后继本地服务引用，中心无结果 |
| 本地自动 END 待办 | 后继 Srv_E 队首收费 CAPTURE 历史记录、首次封存或缓存复用 | Srv_E(i)，本地应用 writer | 本地缓存与后继 END_PUSH 发送意图 |
| END_LOCAL_RETRY(i) | 收费读自己的 pending/cache；未 READY 时封存尚缺证书或重放已有证书；无 pending/已 READY 则无新推送 | Srv_E(i) | 一个实际后继发送意图或明确空结果 |
| 原 ENTRY(i,END) | 只有事前配置/明确主动请求要求 polling 才由中心收费产生请求；否则 NO_END_POLL。请求经网络后在本地收费查限定 END 记录 | 请求 Srv_C，通道 Srv_N，服务 Srv_E(i) | 独立请求/负结果或同一 END_PROOF，不改中心知识 |
| 原 ENTRY(i,PRECHECK) | 原完整准入证据服务，不与 END/消费混合 | Srv_C/Srv_N/Srv_E(i) 的既有分段链 | 只给限定准入事实 |
| END_PUSH / END_POLL_REPLY 接收 | 中心收费验证及第 6 节总分支 | Srv_C | 原子 FINISHED/READY 缓存，或重复/拒绝结果 |
| READY_CENTER_RETRY(i) | 收费查中心自己的真实缓存，必要时重复其 READY；无有效缓存/已证消费则空结果 | Srv_C | 后继 READY 发送意图，不触发新的 END CAPTURE |
| NETWORK(u,v) | 既有 FIFO 下读取/复制/编码/传输指定发送对象、应用该消息有限故障/copy 规则 | Srv_N(u,v) | 仅目的角色的后继不透明接收 token |
| READY 本地接收 | 收费验证匹配 pending，只置 ready_verified | Srv_E(i) | 本地待消费状态；不发送免费 cursor |
| 原 LOCAL_POLICY(i) | 收费执行完整一次消费，原 WAIT/其他 phase 的总分支保持 | Srv_E(i) | 原子新 resident/单步 c/phase；不连锁创建新角色 |
| cap 选择/累计重传/RUN 重试 | 采用已登记的同原 MOVE 公开维护角色，不因到中点产生新服务机会 | Srv_C→Srv_N→Srv_E/ACTUATOR | 只有已有资源兑现后的权限，不含途中 q |

这些机会只登记待工作引用；实际语义读取、签发、解包、验证、owner 计算、重传和空结果都消耗其既有站的服务。自动首推是唯一明确声明的由真实 END 引出的本地作业来源，它不携带可供中心解引用的真值，也不以本次 END 给该臂额外 PROCESS_SLICE；同公共容量下只会改变该臂实际本地队列负荷。

所有新生可见结果仍在严格后继行发布，不在单行内完成 END→封装→网络→FINISHED→READY→消费的递归链。本地/中心 writer 各自封存 envelope 后释放槽，绝不持槽等待远端回执。仍在运行的物理/自主模式和真实 TASK_SERVICE 不被这些应用槽暂停；独立审计器看到的本地待办类型/队列也不能反向提供中心的查询选择信息。

## 10. CAND/cap 选择模块和 RUN 水位的接入边界

cap 候选仍由完整原边几何的有限相交区间端点及相邻中点形成 CAND。一个已固定版本的总选择模块，在自己的付费串行快照上给出一个 x∈CAND、x>b 且其完整新增资源可授，或 NO_EXTENSION/BLOCKED/INVALID；明确选中前不得发布权限。P2 的“最大可行 x”可以作为其中一个完整模块，P3 的受限规则另有不同成本/调度含义，不能在同个实例中私下择优。

本文的 END 服务证明不依赖选最大还是另一个安全可授 cap；只要求中心 b 单调、预留先于签发、本地 C 单调且不超过已授 b、原 s≤C 和 q 的独立可信前向性质。替换选择模块须重新固定其费用及主比较，但不需要将真实 END 改成多个中点完成。本文没有重新证明或消除最大 cap 的停滞反例。

CUM_CAP 不包含 q/s/到达位，不生成 cap 安装或到达 ACK 给中心；失包按公共累计重发修复。中点 HOLD 不创建 EndRecord/LOCAL_END_OFFER。END 之前即使中心 b=ell，本地 C 尚小或参考未到 ell，都不能首推 END。END 之后，即使本地 active_tid 已 NONE，旧 tid 的合法历史记录仍可服务，不能把 NONE 当无对象而拒绝所有必要重放。

RUN/STOP 仍绑定 control_epoch 与公开尝试 key。本地持久处理水位排除同 key 重放；经过认证而已经实际处理的成功、no-start、运行中无作用、C=s、缺 grant 或 phase 拒绝尝试均不能在以后重新当恢复。旧代际不覆盖新代际，BRAKE 已开始必须到首次零速；合法 cap 增大本身不自动 START。原 END 的 g_i/closed/phase fence 优先于一切旧 cap/RUN 发布，应用作业的旧 command_revision 相同也不能绕过这一当前终点守卫。

这保持 E0 的能力边界：不查询 POSITION 仍有公开 cap 扩展和显式控制重试；其 END 首推是所有臂共同可得的**原动作终点证据**，不是偷偷新增的中点进度服务。收到 END 后可以走共同终点交接，但不得借其历史 end_id 更新新原 MOVE 的 q。

## 11. 公平能力与完整费用

D/R/E0/H19-PR-COMMON-SYSTEM 均具有同一原终点推送、缓存复用、有限重试、可选主动 polling、共同 cap 接入及真实 END/READY/消费能力；其各自允许的原提案来源和 ADG/查询规则仍单列。PUSH_RECOVERY 下，H19/E0 不需要购买途中 POSITION 或为了收到终点通知而先等 D/R 的查询选择。若另选只轮询配置，必须标为额外受限轨，不能冒称已保留原事件通知能力。

同能力不要求跨臂真实 END 时刻、推送数、重传数、排队时延或总工作量相同；这些由各臂自身闭环和故障创新产生。公共容量/费用函数与故障 key 规则相同，不能复制另一反事实臂的证据 payload，也不能按实际请求次数顺移共享随机流。

| 实际费用项 | 责任和去重边界 |
|---|---|
| END 守卫、字段原子写入、不可变记录/待办登记 | 共同控制项；依实际位长计，不把所有业务封装免费塞入物理事件 |
| 首个正 END 的 CAPTURE、固定引用、完整字段读取、封装/签发、缓存提交 | 本地 Srv_E；push/poll 首个实际封存者支付一次，后来按已付对象复用 |
| 主动 polling 的请求生成、传输、未到达/无匹配查询及负回复 | 请求者实际支付；PUSH_RECOVERY 不强迫无用途的新动态查询 |
| 缓存重放、retry 空检查、复制/引用、日志与 GC | 各实际 writer；没有免费后台扫描，缓存命中不是零工作 |
| 所有 END/READY 的编码、传输字节、每接收端、有限副本和故障重试 | 既有通道及接收站；重复语义不删除真实重复费用 |
| 中心验证、owner检查/终点改tag/退休、Active/P维护、FINISHED与READY耐久缓存、发布 | Srv_C；一次语义提交，重复到达仍付检查/取缓存费 |
| 本地 READY 验证、消费守卫/原子 gamma复制/c推进 | Srv_E；一次消费，重复/拒绝也记实际费用 |
| 原 cap/QUERY、H19 ADG/cut、planner、TASK/CURSOR、INIT及物理宿主 | 仍按各原角色收费；不把这些成本移到无价的 END 服务层 |

NATURAL 报实际所有工作、等待及保留内存对同有限供给的竞争；STRICT 另报预付供给和实际工作，不强制 E0/H19 执行无用途动态查询来凑等工作。物理真实服务 Q 与 END/READY 的收费链独立，初次与复用、被动推送与主动查询、失败/重复/未完成工作须可分别归账，仍纳入固定完整观察期，不能只展示通知更快的局部轨迹。

## 12. 当前可证明事项与故障反例

**覆盖。** END 的本地 NONE 不改中心 owner，原 tid 的终点 E 仍被保留；END_PROOF 排队期间旧原入口已不可逆关闭，本地未 READY 消费不能进入下一原边。首次中心提交保留 E 并同 owner 改 tag；READY及消费期间不删 E，消费只安装中心已兑现的新 resident 身份。下一原边仍先预留后进入。因此这些新增消息/字段转移没有制造资源覆盖空隙，前提是既有控制、可信身份及串行原子语义成立。

**历史证据与迟到。** 推送/轮询封存的是同一不可变真实 END，而非重新采当前物理状态。若中心仍为原 GRANTED，READY 链阻止本地已合法进入新边，首次交接可引用该历史 END；若已经 FINISHED 或换新 tid，旧 proof 只触发缓存重放/关闭拒绝，不再清资源。因此旧记录重放不会把后来 holder 删除。

**一次性。** 原控制守卫每 occurrence 只创建一次 end_id；中心首次 FINISHED 原子改变当前状态并持久缓存，后来的有效重复只重发；本地匹配 pending 的 consumed/c/phase 守卫只允许一次消费。三种一次性分别由各自持久状态保证，不能用“只有一条消息”代替。

**恢复的条件边界。** 缓存存在且以后有合格工作容量/消息交付时，已 FINISHED 的 READY 丢失可由中心缓存或本地同 END_PROOF 重放恢复，无需新的动态 END 采样。永久失联、中心 fail-stop、无后续公共机会或本地消费服务永无容量仍可无限停留；有限缓存/去重不保证恢复或全局活性。

最小错误前缀包括：真实 END 当行直接中心 FINISHED（免费跨域）；只有 active_tid=NONE 就拒绝持久 END 记录（丢恢复对象）；READY 验证提前填 gamma 后消费仍要求 gamma=NONE（永久不能消费）；先清 pending 再复制 gamma（身份丢失）；FINISHED 先提交而 READY 尚未耐久缓存（无法按正常丢包恢复）；两个通路各执行一次终点清理（旧 tag 破坏）；midcap 到达建立 EndRecord（伪原完成）；旧无作用 RUN 副本在新 cap 后恢复（尝试水位失效）；中心凭无 ACK/超时删除 READY（把发送推断成消费）。这些是声明式反例条件，没有编写或运行测试。

## 13. 根整合点与未闭合范围

可以直接整合的规则是：第 2–3 节统一 END 与应用提交的本地写域；第 4–8 节唯一端点记录、push/poll 合流、FINISHED/READY 原子缓存、终点未消费/复制 gamma 及恢复/GC；第 9 节公开 retry 角色和唯一 END 首推来源；第 10–11 节前缀控制信息边界与共同费用。这些均是本报告自给的条件构造，不自动将当前 73 改为已采用。

根仍须最终选择并在全稿一致登记：主 END 配置及新增公共角色文法、其有限供给/调度发生规则；cap 总选择模块和对应 D/R/E0/H19 策略；P2 的公开 cap/RUN 维护与本新增 END 服务的角色冲突消解；H19 整法动作/任务/ADG版本及实际发布字段；SOURCE/INIT/故障/评分/检查合同的完整跨节适配；所有一手来源与正式顺序审查。当前没有证明总体正效益、一般活性、任意崩溃恢复、物理硬件认证或全部实现可行性。

本文只读取指定科学文本、作身份/文本静态检查并通过 apply_patch 写这个新文件；P2/P3/L3和当前 73 不修改。完成前再次核所读 73/L3 的身份，实际结果与本文件最终 hash/bytes/lines 随完成回执给出。H、T_delay、B_CAL、B_max、B*、P_active、density N 保持原义且未赋值；受限载荷未读，实验前门仍未放行。
