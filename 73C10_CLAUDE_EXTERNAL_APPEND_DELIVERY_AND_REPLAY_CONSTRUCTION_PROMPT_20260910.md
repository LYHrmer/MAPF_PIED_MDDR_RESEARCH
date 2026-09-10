# 73C10：新外部执行追加记录的投送与重放构造

2026-09-10。请以Claude Opus做一个NO-SKILL / NONBALLOT建设题，只依据下述定义，不使用任何skill、工具、网络、文件、实现或伪代码。不是正式审稿。只检查新设计的APPEND_ACTION投送/重放接口，不构造或审核H19名义时长、PLAN_CHECK、commit-cut、源求解器；这些属于其他独立工作，旧L7缺回执未重启。本题的新接口来自根刚写的73L11（SHA256 c845f894147dc2e3cdcf6def1df06fb8478298e82d4d670f9799296f00535046，18880 bytes/89 LF），下面是自足输入，不假称你读过原件/原论文。

每agent有只追加不可改的执行记录Π_i[0..L_i]，固定episode的plan_epoch，原动作MOVE或WAIT对应槽k及起止顶点。中心只有已交付Kc_i；executor私有真实c_i只合法单步消费，Kc≤c≤本地已安装尾长。本地执行记录可以落后中心尾长，不能凭中心记录已追加就说本地收到。每个动作有全局唯一source_job/agent/source_index，映射到槽后永不复用；tid与该动作/slot/两端点/parent/控制及几何版本完整绑定。

上层外部协调可以按Type-1前驱已入队或finished、Type-2前驱全部finished，将未来多个动作逻辑入队。逻辑入队成功的同一中心原子提交才追加一个执行记录，并保存认证APPEND_ACTION及后继发送意图。Type-1和顺序保证每agent不跳动作，中心尾端与新增起点一致。未来图改动不能撤销已追加/入队动作；本题不审怎样选cut，直接把这个不可撤回条件作为前提。

APPEND_ACTION完整绑定source动作、中心提交id、plan_epoch/agent/slot、前一记录身份及动作内容。通过原收费Srv_N投送到Srv_E，Srv_E收费验证后只按连续前驱安装；前驱缺失的包不给跳槽效果，重复相同记录幂等，不同记录占同一槽为矛盾并拒绝。不能重置c、给q或改变原MOVE。中心不接收本地安装ACK；本地安装与否不产生额外机会，缓存/失败/重复全收费。需要你指出是否还缺可靠缓存或关闭条件，而非默许无限免费消息。

每agent至多一个未关闭物理请求/活动tid。SOURCE_OR_EXTEND公共角色依据中心已交付Kc和中心执行记录，为当前原MOVE发请求或重试旧请求。可信PRECHECK必须在本地已安装同一原动作、真实c=k、RESIDENT_OPEN、无active/pending、原起点resident合法时成功；不满足只给限定拒绝，不回正确c/缺失记录下标或pose。中心缺乏相应本地记录时可能请求过早；普通完整grant只在先预留M0、PRECHECK等全条件合格后发出，b=ell。MODE/安全guard可合法阻止。grant有效接纳后最多一个活动MOVE；它真正到原终点产生不可逆END，后续付费END→中心FINISHED/READY→本地验证→一次LOCAL_POLICY消费，c才从k到k+1。WAIT没有END，只有合法LOCAL_POLICY消费。未来MOVE不能越过未消费当前槽。

既有SOURCE_REQUEST公开出现序从零计，按modulo 3固定SOURCE_OR_EXTEND、RESEND_CAP、CONTROL_RETRY。每角色只产生自己规定的一个作用，无自触发递归。给外部的RESEND_CAP规则是：当前中心GRANTED未FINISHED则重传最大已提交CUM_CAP；否则重传规范最早尚无中心消费证据的APPEND_ACTION；无对象为空。一次不同时发cap及APPEND。CONTROL_RETRY只重发绑定公开新尝试key的控制意图，无GRANTED为空；本地no-start/无cap/模式拒绝也消费已认证控制尝试，副本不能以后自动恢复。当前MOVE的APPEND已经合法安装才可能有PRECHECK/GRANTED，但后继动作记录未必已安装。

共同CURSOR独立按规范agent轮询，在本地付费CAPTURE真实c，只在付费交付后增加Kc。完整后继PRECHECK还可给其明确蕴含的旧槽消费事实，用于生命周期/重试缓存退出，但不额外修改通用Kc。MOVE的ADG finished仅在付费FINISH_RECEIPT后维护；WAIT的ADG finished需要CURSOR越槽或上述严格消费蕴含，再付ADG维护，不能在逻辑入队就算完成。重复旧APPEND即使在END以后也不能重新建立pending/active或重用slot。GC必须等不再需要重传且所有有效消息/作业/图/审计引用结束；缺消费证据保留缓存成本。

公共有限O事前固定，所有中心/本地/网络角色同FIFO、有限收费容量和后继发布，连续物理仍推进。无无限成功/公平交付保证。若证明条件活性，须准确列出需要的公开机会、足额服务、重传交付、新鲜CURSOR/END/READY及no-start解除等；不能从规范轮询就断言任意有限O保证。

请只回答：
1. 至多两条真实接口反例：无ACK、乱序前驱拒绝、cap优先重传、Kc滞后与WAIT完成是否能让已许诺动作在其它必要条件成立时仍不可恢复，或发生重放再执行？逐行说明；找不到就给有限条件证明，不能编造bug。
2. 如需修复，给最小消息/缓存/水位/角色合同；不增免费服务、额外角色或真实进度ACK，不改变原动作/保护参数。
3. 最强的未承诺活性条件及一条公平收费负例。区分物理安全、消息恢复和任务吞吐。

输出约1200–1800中文字，完整写完，末行必须END-C10。不要扩到投稿、文献搜索、源UB、数值绑定、名义时长或cut选择。不要给H、T_delay、B_CAL、B_max、B*、P_active、density N任何数值、范围、默认或改义。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT保持。
