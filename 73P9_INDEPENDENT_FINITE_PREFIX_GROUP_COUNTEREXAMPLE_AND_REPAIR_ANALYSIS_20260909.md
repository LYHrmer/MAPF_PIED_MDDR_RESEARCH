# 73P9：有限前缀组、早扩展与付费查询的独立查错及修复建议

2026-09-09，`/root/source73_r0_remaining_contract`。**NO-SKILL / CONSTRUCTIVE / NONBALLOT**。本件是独立构造查错，不是正式独立逻辑审查、根验收或资格票。保持 **HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT**。

## 1. 实际结论与阅读身份

P8 的两个核心集合论步骤成立：共享阈值族确实覆盖其声称的 P5 等长正方环充分见证；任意合法早扩展的新资源确实落在该成员的 B_i 内。由此还能严格证明：本组扩展的阻塞者不可能是已经清除旧前缀的成员，其最终终点资源也不会成为被漏掉的阻塞贡献。没有找到反驳这三项条件命题的反例。

需要修订的主要位置是 **P8 §8 的进展量词和 §3／10 尚未登记的公共角色**。有限 O、精度合格以及已购买消息最终送达，不能单独保证在达到初始 cap 后还会发起有用采样；“所需服务最终有”若未明确包括这个后继链，会把要证明的进展藏进前提。围栏的类型也须完整保留：它不是第二个物理 owner，却是有真实排他效果和长期阻塞代价的准入保留。

目标创建前精确核为不存在。本次完整读取 P8、P2、P4、P5；没有读取 P6、P7、C7 或其他独立审查文件，也没有启动／重启 P7。P5 原文自带根修订说明，本文没有沿其引用读取别路报告。当前 73 只作 §7 查询／来源规则及相关 Active、终点、MODE／付费发布定位阅读，不冒称本轮全读。根在本稿初次写入后，另以消息告知其独立发现 END／FINISHED 及后 cap 采样量词问题；本稿此前已在 §4–6 列明同项，没有读取 C7 的提示或结果。

| 亲见输入 | SHA256 | bytes／LF |
|---|---|---|
| [P8 全文](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73P8_ROOT_FINITE_THRESHOLD_GROUP_ADMISSION_AND_PAID_BARRIER_CONSTRUCTION_20260909.md) | `7663fdb4548f43ed71781c23f2d24761854ddf3141b57f5972eb54e0b6c778f3` | 15119／93 |
| [P2 全文](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73P2_PREFIX_END_TO_END_PROTOCOL_AND_FAIR_COST_CONSTRUCTION_20260908.md) | `5dfaa2adcbe6fcd11ecb16b9d093519f1733dc8fe947d7f64c7316a0db5ba5dd` | 36848／202 |
| [P4 全文](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73P4_PAID_END_PUSH_PREFIX_ROLES_AND_FAIR_CAPABILITY_COMPOSITION_20260909.md) | `70ddcb01292a8e74773113403084f7b146ddcdb29ba237b4cac88222634cf1e1` | 33281／214 |
| [P5 全文](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73P5_ROOT_PAID_CERTIFICATE_TWO_STAGE_ASYNCHRONOUS_RING_WITNESS_20260909.md) | `dd897d4d87f833681daa804fcbd62cbc7051109d2b05879dc58faa74a1cf9a5e` | 15589／126 |
| [73 定点规则](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md) | `529a67132eabf915401df097c0a78be91e2c1e47ce9f9205518acdef5ec7420c` | P8 登记为 137460／480；本轮独立核 hash，未重计全文尺寸 |

以下均为纸面推导，未生成几何实例、O、配置、测试或实验结果。局部“成立”不改变六门裁决。

## 2. 共享阈值确实发现 P5 的所述向量

定位：[P8 §4，特别是 L35](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73P8_ROOT_FINITE_THRESHOLD_GROUP_ADMISSION_AND_PAID_BARRIER_CONSTRUCTION_20260909.md:35)，及 P5 §3。记 P5 的开区间为 (A,B)，各边等长 ell，共同精度为 epsilon_obs。P5 的 G+ 证明已经从有限闭方瓦片覆盖推出每个 CAND_i 在该开区间中非空；这一步不依赖共同晶格。

独立复核：取 d_i=min[CAND_i∩(A,B)]，d_max=max_i d_i。某成员的 d_i 就等于 d_max，所以 alpha=d_max/ell 是 Theta 的成员。由于 d_i≤alpha ell=d_max，P8 的向下取最大候选满足 d_i≤c_i(alpha)≤d_max。于是每个 c_i 严格位于 (A,B)，不会被含 0／ell 的剔除条件删除。

初始 A_i 全含在进度 [0,c_max] 的阶段包络内，ell−c_max>r_geo；未来 B_i 的起点 l_i=c_i−epsilon_obs>r_geo，故它全含在进度 [l_min,ell] 的阶段包络内。P5 的闭瓦片分离引理分别适用，得到 A_i 两两不交和 B_i 两两不交。不同方向 CAND 可以不相同，不需要 d_max 本身出现在每个 CAND_i。

选择更早的另一个通过 alpha 不破坏论证，因为它已经逐项验证 A／B 条件；P5 的指定 alpha 只是枚举非空的一个见证。闭边界没有被取整跳过，也没有把“候选只需接近开区间”当成真的属于开区间。

限定必须保留：这是**给定该组被检查时的几何发现命题**。它不证明源必输出这四条 MOVE，不保证公共作业实际轮到该 SCC，不证明它在任何外国围栏或 owner 已插入之后仍合格。非等长／非对称问题的独立可行向量未必由共享阈值表示；P8 已诚实声明不完备，不能把线性多个向量扩大为全调度完备性。

## 3. 早扩展新增资源的包含式成立，而且可加强

定位：[P8 §6 L51–57](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73P8_ROOT_FINITE_THRESHOLD_GROUP_ADMISSION_AND_PAID_BARRIER_CONSTRUCTION_20260909.md:51)，P2 §3／8。对 q≤b≤x，有 U(q,x)=U(q,b)∪U(b,x)，因此 Mask 也保持这个并集。一个资源若与 U(q,x) 相交却不与 U(q,b) 相交，它的相交见证只能来自后一段，故

\[
\operatorname{Mask}(U_i(q,x))\setminus\operatorname{Mask}(U_i(q,b))
\subseteq \operatorname{Mask}(U_i(b,x))
\subseteq B_i.
\]

最后一步只用 b≥c_i≥l_i 和 x≤ell_i。闭端点重叠不会破坏包含式：差集中的资源已经排除了旧段相交，允许右边多包含端点资源只会使右边更大。不要求资源互不重叠，也不要求每个资源只出现一个相交区间。

若未来把 q 退休与 b 扩展合为同一原子事务，更强的式子仍成立：对 q_old≤q_new≤b≤x，新目标 Mask(U(q_new,x)) 减去旧实际持有 Mask(U(q_old,b)) 也包含于 Mask(U(b,x))。但这只是集合保持证明；目前 P2 将退休与扩展分开串行，不能由此免费合并消息、跳过 owner 复核或遗漏删除记录费用。

从初始持有 A_i 起，任意次数合法早扩展与退休后，当前持有 S_i 总满足 S_i⊆A_i∪B_i。一旦**实际释放下界** q_release,i≥l_i，就有 S_i=Mask(U_i(q_release,i,b_i))⊆B_i；后续扩展仍只在 B_i 中，因而不会重新变成未清成员。中心 FINISHED 后保留的 endpoint resident 也属于 B_i。

这里必须使用 q_release，不能用 F_cap 中没有实际退休作用的 q_evidence。P8 L67 已提醒分账，但 §8 定理建议显式限定到 S／途中退休制度；F_cap 与 E0 不能凭采样精度套用 S_i⊆B_i。

## 4. D 的 endpoint 排除在本组条件下不漏关键 holder

定位：[P8 §7 L63–67](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73P8_ROOT_FINITE_THRESHOLD_GROUP_ADMISSION_AND_PAID_BARRIER_CONSTRUCTION_20260909.md:63)。取一个未完成成员 j 的完整扩展需求 D_j=Mask(U_j(q_release,j,ell_j))，其当前持有为 S_j=Mask(U_j(q_release,j,b_j))。若资源 r∈D_j 的外国物理 owner 是成员 i，则由单 owner 和 S_j 已兑现可知 r∉S_j；所以

\[
r\in D_j\setminus S_j\subseteq B_j.
\]

若 i 已经 q_release,i≥l_i，则 r∈S_i⊆B_i，与 B_i∩B_j=∅ 矛盾。若 i 已 FINISHED，其 endpoint resident 同样属于 B_i，也不可能阻挡 j。即使 i 尚未清除旧前缀，只要 r 属于它的最终 endpoint Mask，仍因 endpoint Mask⊆B_i 得到同一个矛盾。因此，任何确实阻塞本组完整扩展的外国资源，必属于**未清除旧前缀且中心仍 Active 的成员的非 endpoint 资源**。

这补齐了 P8 L73 的关键一步：当只统计本组合法 CAP_EXTEND、围栏和所有非 owner 条件通过时，有资源阻塞就存在正分 holder；最终 endpoint 的排除不会使 D 看不见它。自己的已持有资源不算外国冲突，同一 occurrence 多个资源只贡献一次，均与原去重语义相容。

结论有三个必要边界。第一，真正 END 但中心尚未 FINISHED 的 tid 仍在 Active，这一点由 73 §7 明确规定；不能用隐藏的本地 END 免费删它。第二，此时 POSITION 可能只返回 NO_MATCH，必须依 P4 的正常 END 首推／重试／中心 FINISHED 链最终清除旧占有。第三，外部请求若被组围栏阻挡，就不满足非 owner 条件，即使同时撞到组内某物理 owner 也不应贡献 score；建议将 L65 的“仅被围栏挡住”改为“任何未通过围栏准入条件”，避免被误读为只排除一种纯围栏情形。

## 5. 需修订的进展量词与最小反例

定位：[P8 §8 L71–73](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73P8_ROOT_FINITE_THRESHOLD_GROUP_ADMISSION_AND_PAID_BARRIER_CONSTRUCTION_20260909.md:71)。其中“此后”如果严格指采样发生于参考已达到 c_i 之后，不等式没有问题；如果只指证书在那之后到达／发布，则不足。必须分别写出达到初始 cap 的时刻、实际 CAPTURE 时刻和中心退休提交时刻。

**有限日历反例。** 保持 P5 的合格初始组与既定精度不变，所有已购买 POSITION 都在各成员尚处起点时合法捕获，随后完整付费交付，给出合法下界零。最后一份由 QUERY 产生的 POSITION 已完成实际 CAPTURE 之后，正常控制／传输才使各成员达到 c_i；余下公开维护继续得到服务，却没有后继 QUERY 发出新 POSITION。此时采样、精度、送达、控制、维护均没有伪造或永久丢失，D 的中心仍可有正分 holder，但没有新的已授权采样，阶段证据不会自来，完整扩展可一直受阻至截止。

这不是对包含“到 cap 后仍有必要 QUERY 服务”的强前提的反驳，而是对**当前文字较弱读法**的反例。若“所有所需服务”本来意在包括它，就应展开为可核的后继事件条件，不能把“凡完成需要的一切都发生”作为进展证明。P2 已明确 O 有限且耗尽后不能自行加行；P5 §5 也要求实际到 cap 后的付费捕获，P8 不应在从手选顺序升级为 D 选择器时丢掉这个量词。

另一个必要链是 END→封存→传输→中心 FINISHED。物理 END 已发生但这条链没有后继容量时，中心仍保存旧 tid 非终点资源；重复 POSITION 的 NO_MATCH 不提高 q，也不能清 owner。只有说“原动作最终 END”不足以替代中心真正完成交接。该反例不需要第二种传感噪声，也不证明已有 P4 恢复合同错误；它说明条件进展必须把 P4 的服务前提带入。

## 6. 可直接替换的严格条件进展命题

建议根将 P8 §8 限定为下面同一个命题，而不是声称无条件有限完成：在一个已原子准入、无外国占有插入、没有其他正分需求竞争的有限组中，所有成员使用实际 q_release 退休；模式允许 QUERY 和既有扩展；初始累计 cap／必要 RUN 与控制使每个成员在某个有限时刻达到至少 c_i，或已经真实 END。令 T 为这些初始进展时刻的最大值。T 是证明中的轨迹时刻，不是新公开信号或可由中心免费读取的数值。

还须逐项具有以下**后继服务条件**，不赋其次数、周期或时长：

- 在 T 以后，只要仍存在本组正分阻塞，后继公共 QUERY／SELECT 能成功产生一次仍相关的请求，且其实际 CAPTURE 在 T 以后；若 holder 已 END，则对应付费终点链在有限后继时刻完成中心 FINISHED。请求失效而未带来清除时，不能把这次尝试当作已满足该条件。
- 相关 POSITION 的既定精度、传输、中心验证和实际 q 退休提交均在有限后继时刻完成；q 融合单调且不跨 tid。QUERY 空结果、失败和等待仍收费。
- 已经资源可授的未完成成员在后继公开 cap 维护中得到完整检查／扩至 ell；累计授权、新的有效 RUN、必要不中断控制及 END／FINISHED 链随后得到服务。不能将中心 b=ell 直接当作本地 C=ell 或真实 END。

证明使用中心可判的已清集合：q_release,i≥l_i 或已 FINISHED 的成员。这个集合只增不减，且其成员不会再成为本组扩展的正分 holder，见 §3–4。若仍有正分，被选 holder 尚未清除；在 T 后的实际采样满足 q_sample≥s_sample−epsilon_i≥c_i−epsilon_i，结合非负性得到 q_release,i≥l_i，或者 END 链使其 FINISHED。每一次这样的**有效清除**严格增加已清集合，有限成员只需各清除一次。

实际选择与回执之间可以已有别份在途证据先清除同一 holder；此时用那次既成清除记录进展，后来重复回执不能再算一次减元。上述归纳针对尚未清除者的有效推进，不假设同一 holder 只有一个在途请求。

若没有正分，而结构、控制、围栏等非 owner 条件都已合格，则 §4 排除任何外国物理 owner 阻塞；后继维护能按常规规则扩到 ell。结合明确列出的控制／交接服务前提，得到有限的组内完成链。早扩展不破坏论证；它只增加 B_i 中的占有，而 T 前后都不降低参考进度。

这不界定 QUERY 总次数、重复成本或任意预定 E 内完成；“至多每成员一次有效清除”不是“至多每成员一次采样”。证明也不要求 D 对成员轮询公平：在已经满足后继服务条件的封闭组内，任意仍相关的正分选择均指向尚未清除者；其后要么已由其他回执清除，要么由本链完成清除。它**仍要求作业和交付有足够后继服务**，不能把这项调度条件误报为 D 分数自动提供。

R 在该固定有限组也能用真实后继轮询和同样服务条件获得必要证据，故没有 D 胜 R 的结论。跨组正分、不断产生的其他需求、QUERY_OFF、无后继容量或受控永久故障均超出这个进展命题；它们继续属于主 roster 的可能零／负结果，不可据此删行。

## 7. 围栏不是第二个物理 owner，但确实是排他保留

定位：[P8 §5 L41–47](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73P8_ROOT_FINITE_THRESHOLD_GROUP_ADMISSION_AND_PAID_BARRIER_CONSTRUCTION_20260909.md:41)。在既有单中心 owner 账本中，F_G 不为每个资源再登记一个可用来证明实体覆盖的物理持有人；覆盖仍只来自当前 S_i／endpoint。因此它不与“每资源最多一个物理 owner”矛盾。

但对尚无物理 owner 的 r∈F_G，外部本可获取的请求仍被拒绝，所以它具有**保留未来准入的排他权**。这是本组进展证明需要的外部隔离条件和一种真实调度能力，不是只读注释。面积／时长、索引／查询、外部等待和失败后保留均须计入能力与成本；不得只报告实际 owner 占用而把围栏覆盖区域当完全 FREE。

P8 的设栏前检查足以排除已有外国已授但未接收 cap：其潜在权限已由当前 owner 兑现，若与 F_G 相交就会使检查失败。物理尚未 START 不构成例外。设栏后，普通整边准入、其他前缀扩展、其他组准入等**每条新增占有路径**都须遵守同一围栏检查；不仅 GROUP_ADMIT 自己检查。现有中心单 writer 已排除另一中心事务在私有计算期间插队发布，不应再虚构一个它本来允许的并发写反例。

同一中心原子提交设栏与初始 A_i 改 tag，可以同时满足唯一 owner 和完整覆盖；所需计算／记录／签发先付费，容量不够就不发布，不能先挂围栏再等待部分 A_i 准入。此处的原子组账本变更不是同时物理 START，P8 已正确区分。

组成员 END 后的合法 gamma_prime 属于登记的终点接续，不应被“只有原 tid 才是成员”的实现性误读挡住；它不增加新的覆盖区域。下一原 MOVE 是新 occurrence，围栏退出前必须依 P8 禁止。允许 WAIT 消费不移动 resident，不能顺便穿越到下一 MOVE；中心使用 Kc／PRECHECK 时还须检查该 agent 的组成员约束，而非只看原 tid 已 FINISHED。

退出应保持 P8 所列条件：全部中心 FINISHED、endpoint resident 成立、原授权受关闭水位拒绝，再付费去栏；不必等待无止境的重复网络包全部消失才能解除准入，但历史对象 GC 仍须等引用消退。去栏不删除 endpoint owner。只看本地 END、无 ACK、超时或期望已到 cap 均不足以退栏。

**围栏代价的最小机制反例：** 组内一个成员永久 no-start 或其终点交接永远未完成，F_G 就不能按本合同退出；一个外部请求即使只需要其中当前未被实际 S_i 占用的未来区域，也仍不能取得准入。该请求的失败原因是围栏，不是可以通过查询某个当前 holder 清除的物理阻塞。P8 §9 已承认长期锁住 F_G，这个代价应进入主方法名称／费用／等待结果，而非只藏在异常附录。该反例是规则层条件，不是声称已实例化公开 MAPF 场景。

## 8. 公共角色和需求账本仍须明确登记

定位：[P8 L25 与 L93](/home/lyh/MAPF_PIED_MDDR_RESEARCH/73P8_ROOT_FINITE_THRESHOLD_GROUP_ADMISSION_AND_PAID_BARRIER_CONSTRUCTION_20260909.md:25)。P8 自承尚未给公共角色总文法，因此“几何选择族可算”不能自动称为整个调度总函数。尤其要排除 P2 的旧单请求最大初始前缀在组检查之前抢先生效；P8 的通常独立初始请求只允许整边准入，不能将其误接回旧任意部分准入。

一个最小明确修复是登记单独的公共 **GROUP_ADMIT** 角色：仅由预先 O 的具名行释放，作业排入原 Srv_C FIFO，不从发现循环的私有结果自动赠送 token，不新增 PROCESS_SLICE／服务器。其内部按 P8 的 SCC／最早请求与规范 key 次序，选择首个合格组或付费空结果。原 SOURCE_OR_EXTEND 保留独立请求整边尝试与已授 tid 的安全扩展；累计重传、RUN、QUERY、终点推送继续各走既定角色。

不同角色按已有公共行序和 Srv_C FIFO 竞争，不另承诺 GROUP_ADMIT 或 QUERY 的隐藏高优先级。若同一机会被同时叫两个角色，须在未来 O 文法中排除；不能一行既组准入又扩展／重传。这个修复给出确定的模块入口，不保证给定组一定在外国动作改变闭合条件以前轮到；后者属于明确的日历／服务条件。

CAP_EXTEND 与 UNGRANTED 原需求应分类型保存，但每原 occurrence 在 D 贡献中最多一个。前者的登记点建议固定为组初始准入的同一中心提交；它的首次需求加入行用于原 tie 规则，后继 b／q 更新不重新刷新“首次加入”。b=ell、中心可用的 END 关闭事实或绑定失效才退出；不能通过尚未到中心的物理 END 免费删除。源原请求授予时从旧 P 退出、CAP_EXTEND 同步出现，两者不并存双计分。

组内扩展目标选择改为完整 ell 需求，是 P8 相对 P2“最小下一候选需求”的实质策略变更，应在 73 的参考函数、索引失效、tie 及费用中统一替换。仅在正文新增 CAP_EXTEND 名词而让旧实现仍只扫 UNGRANTED P，会让全组初始准入后 D 的需求集合变空，无法引用 §6 的正分证明。这里是待实施接口一致性义务，没有运行或编写实现。

## 9. 公平、复杂度与结论层级

D／R／E0 须共同具有同一有限组选择、F_G、早扩展、CUM_CAP／RUN、终点恢复、组退出及下一 MOVE 限制。E0 仍可对所有真实可授更大 cap 作同样尝试，不能加一个只因没买 POSITION 就禁止扩展的阶段门。P5 的“无第一个完整授权”证明因此仍适用于其环：q_release 恒零保留各起点，第一次 b=ell 必碰后继尚保留的起点；即使允许任意合法早扩展也无逃逸。它不证明其他无 POSITION 架构都失败。

共同精度合同在这里参与组选择和 B_i 几何证明，不等于 E0 已购买实际样本。各臂为自身真正执行的候选／围栏工作付费；不能给 D 免费建表，或要求 E0 额外维护完全不用的 D 分数索引。新增失败判定缓存、相交查询和围栏版本维护同样不得无费。组几何可能改善所有臂，不能把全部收益归为 D 的证据选择。

P8 的 O(M m² R) 是固定组朴素枚举／成对集合检查的保守抽象界，作为局部界未见错误；精确位长、图构造、全部候选组、未变化重试、证书／通信／RUN／终点、内存和围栏等待另计。共享阈值线性的是向量个数，不是全系统总成本，也不是大规模性能已证。

本件建议保留三个清楚层级：P5/G+ 域内能找到向量；在 §6 明列的后继服务条件下，已准入闭合组可完成；固定主 roster 的全窗净效应尚未知。前两项不能推出主 D−R 正差、E0 总体更差、一般无死锁或新颖性；长期围栏、其他正分竞争和有限日历耗尽都是应保留的失败机制。

## 10. 逐项交付状态与未执行边界

| 检查项 | 独立证据与判断 | 根的最小处理 |
|---|---|---|
| 共享阈值发现 P5 | §2 给出 d_i≤c_i≤d_max 的完整链，闭边界无遗漏 | 保留条件命题；不扩大为一般完备 |
| 早扩展新增资源⊆B_i | §3 用 swept union 与 Mask 并集证明，并覆盖 q 同时增大的情形 | 保留；继续按实际 owner／原子事务收费 |
| D endpoint 排除和已清 holder | §4 证明外国冲突位于 D_j 减去 S_j 的新增需求，故属于 B_j | 建议把此关键引理写入正文 |
| D 条件进展 | §5 的早采样／有限后继日历反例揭示量词缺口；§6 给严格修复 | 明列 T 后 QUERY／实际捕获／退休及 END-FINISHED 链，不偷加公平性 |
| 围栏类型与失败 | §7 证明不重复物理 owner，并列真实准入排他／失败成本 | 全新增占有路径检查；退出与 GC 分开 |
| 公共优先序／P 索引 | §8 指明 P8 仍未总定义并给一个具名入口修复 | 注册 GROUP_ADMIT 到原站 FIFO，统一 CAP_EXTEND 的加入／退出／tie |
| E0／F／强 R | §9 及 q_release／q_evidence 区分 | 同能力早扩展；S 进展不套 F_cap；不声称 D 必胜 R |

只新增本文件，未修改 P8、73 或任何旧件／Git；没有调用 skill、Claude 或新 agent，没有启动 P7，没有读取其他审查报告、35–38、受限 Q-CAL／Q-CONFIRM、地图／scen／配置／任务／delay 载荷或桌面旧备份。所有 shell／链段使用 rtk，原文用 rtk proxy；编辑只用 apply_patch。未实现、写伪代码、构建、测试、仿真、调参或生成参数／实验载荷／结果；保护参数保持原义且未赋值、范围或默认值。完整报告完成不改变 HOLD 或六门状态。
