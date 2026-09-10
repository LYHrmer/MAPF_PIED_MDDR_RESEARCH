# 73P12：根控制代际、实际接纳与组退栏独立分析

2026-09-10，根 /root。NO-SKILL / CONSTRUCTIVE / NONBALLOT；不是正式独立逻辑票或根最终验收。根完整读取P10与C9终态正文并逐项复算，随后直接修改73。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 1. 实际输入与结果身份

P10输入为完整0beccea730aced26203406f8ffa69f5ffa93247f80cec64f00ec9de265065965，155562 bytes /531 LF。P10实际SHA256 0f86e240da1ea980f1a2f14870f1bec53ac3e26ffd41f222876244f58ad2d6a2，17656 bytes /88 LF；C9完整回执072de18cdc760f93e64da3f695efbfb108a000045528332b888a67f054d962f9，11096 bytes /99 LF，原JSON 7b441056ca980931b1ccaa27afab1ad5e4b34284dec7e2be33e411e7e093c764，8214 bytes /1 LF。C9一次实际exec29561最终exit0，CLI session 7fa8583c-34b7-4062-a7d6-bb61f0808613，实际modelUsage为claude-opus-5 / firstParty，duration175504ms；没有此题第二次调用，不把Opus实际终态当科学通过。

根修改后的73为 **d613bc26c54ac9a3eac0cb5483120752f710eef8acb08e7418c240ddf1a9cf52，159064 bytes /533 LF**。新增W68–70只为纸面检查合同，NOT_IMPLEMENTED/NOT_RUN。P10/C9不曾审这个新身份；旧完整回执均保持字节。本件也不将L11/C10R外部构造说成已经整入73。

## 2. 根独立否定C9碰撞前缀及五项修复

C9主反例第5步把中心FINISHED放在本地仍处中点HOLD、原tid未关闭的时刻。按73原§5，原END仅在参考到原端s=C=b=ell、零速时发生，并先永久关闭入口及提升g_i，再产生EndRecord；之后才有付费证书和中心FINISHED。READY未消费只意味着c还未推进，不撤销之前的END。故该第5步无法由合法前缀产生，不是碰撞漏洞。

其第7步另把(s,C]的资源称为FREE。原END前q_release≤s、已安装C≤b，当前Mask(U(q_release,b))仍覆盖该段；围栏仅是额外准入排他，不能代替这段owner责任。即使暂不使用第5步矛盾，第7步仍违反P3。根因此独立否定整个前缀，而非按代理赞同数投票。

C9所谓“中心要么未知本地、要么等READY消费”的二分也不成立：END_PROOF正是已有的、付费的历史本地关闭证据；它不需要安装、中点到达或START ACK，不读取当前C，也不要求跨writer持槽等待。历史事实与当前私有状态不能混为一类。

修复1–3不采用。中心后来产生的closed标记不能修改旧在途RUN的已签字节；旧命令尚未知该标记时，所谓中心单向修复并没有封住它自称的前缀。现规则的安全方向是本地END先不可逆关闭，中心凭其历史证明才退栏。根采用的只是明确引用这条已存在证据链和持久保留证明。

修复4不新增机制。终点交接已要求先核END、保留endpoint并清旧tid其余责任；在途消息和审计引用仍可存在，安全退栏不等于全部缓存消失，GC也不能提早删除引用。修复5的“补偿永不反向”与合法END_PROOF/CURSOR冲突，根拒绝；禁止特定安装ACK不等于禁止全部机器人到中心的信息。

C9清单中真正需要加强的是控制验证与实际接纳的时点，以及换原tid时控制代际的作用域。FINISHED谓词、永久关闭writer和endpoint责任在原全文已有，不因为提示摘录较短就变成全文缺项。C9认为新tid必继承STOP并等RESUME也未经现稿定义支撑，不能据猜测认定合法停滞。

## 3. 根采用P10控制作用域修订，并限定缺grant分支

P10给的区分前缀有效：若中心每个新活动记录重置epoch，而gate跨tid保留最大epoch，则旧tid曾BRAKE/RESUME后可使下一tid普通RUN永久低代际拒绝；若两端按agent连续则不出现此额外停滞。原稿未明确二者，因此须选唯一语义，不能交给实现者自行选择。这个问题是协议可判定性，未证明界内碰撞。

现73选择同session、同agent持久control_epoch。每次普通/组首次GRANT取严格后继代际并登记该tid的RUN_ALLOWED意图；FINISHED、退栏及换tid不重置计数。MODE BRAKE/RESUME仅修改当前GRANTED原tid，无则收费NO_MATCH且不锁存到未来tid。cap增加、重传与CONTROL_RETRY不增加代际。新意图仍需真实控制尝试；不自动RUN。

Srv_E只认证并发布不可变候选，有效epoch/尝试水位只在ACTUATOR实际处理时改变。否则“先验证新STOP、后处理旧RUN”会在验证阶段偷偷实施STOP，与所声明ACTUATOR作用点冲突。实际队列用已发布入列次序，一次接纳一条，完整复核后登记事实及单次作用；Srv_E的旧快照不能覆盖ACTUATOR后来状态。各自发布/消费字段和队列成本均计入既有供给。

根对P10的“缺grant也消费尝试”补了必要身份范围：只有完整认证的alpha/slot/parent匹配本地RESIDENT_OPEN、真实c、resident及未END原步，active_tid/pending均空且e>g_i，才登记一次缺grant拒绝。不允许任意未来或旧tid抬高活动水位。已闭/其他活动tid包按持久closed/身份直接拒绝；未认证包不推进任何控制水位。合法no-start、C=s、运行中无作用及BRAKE未停均消费本次尝试，未来cap安装不能令其副本复活。

公共MODE和SOURCE_REQUEST使用同一公共机会全序及来源身份，不各起冲突计数器。n_i按每次SOURCE_REQUEST公共出现递增，空业务结果也占该次；私有进度和丢包不能暂停、跳过或插入相位。上述规则只给实际出现机会的唯一语义，不承诺有限日历一定含足够成功RUN或网络投送。

## 4. 其余意见的根复算及正文实际修订

单闭区间[a,d]在q≤b时满足1{a≤b}−1{d<q}=1{a≤b且d≥q}，因为被减项必已经计入；对所有合并区间求和即得计数等价。d=q仍接触，严格退出不能改成非严格。根接受P10此局部证明，且新增明确(q_release,b,n_r,两指针,owner/P版本)同事务提交，失败增量不发布但费用/日志/保留内存不退。局部成功路径枚举界不覆盖失败重扫、整表复制和大整数费用。

组内新增集合包含于B_i，B_i两两不交；某holder已付q_release≥l_i或中心FINISHED时，其责任只在自己B_i，不可能阻挡另一成员的新增B_j。这支持条件推进，无需把“所有到cap”当早扩展的前置条件。到分析时刻以后真正CAPTURE及后继付费交付仍必需，不能用早样本晚交付替代；原END到Q还须真实任务服务，不推固定评价窗净收益。

GROUP_RETIRE现在明确只凭固定成员已验证END_PROOF支撑的历史关闭事实及终点接续，禁止读C/s、待ACTUATOR队列或READY消费。组记录引用成员证明及gamma_prime至退栏完成，避免唯一证据先GC。仍不新增ACK或提前清owner。

DRAIN现在明确禁止已登记但仍UNGRANTED请求取得首次正cap，只保留可行CANCEL；已授责任的合法扩展/重试/终点继续。QUERY_ON设ACTIVE、QUERY_OFF设SHARED-OFF；E0也可恢复ACTIVE，但其固定不购买POSITION的策略不变。原E0“STRATEGY_DISABLED”不得解释为不能退出DRAIN，否则人为删掉新准入能力。

WHOLE_EDGE的“初始b=C=ell”改为中心准入只设b=ell、本地C等合法grant实际安装后才到ell；尚未安装或丢包时不预置。E0不做无用lambda的旧措辞换为不构建无用途退出事件/退休索引，实际有用几何仍计费。未强迫整边/外部做无用途组工作。

## 5. 实际范围与下一步

本轮只整入P10经根独立接受的控制/模式/费用澄清；主GROUP_PREFIX、纯D、AA来源历史、PROCESS_SLICE及原配对主量保持。L11和C10R仍是外部下一轮整合输入。根另直接重读H19作者版p.4–5，原IV-B允许已满足依赖的多个动作排入命令队列，未给“一公共协调机会至多一个动作”的原法限制；L11这一人为粒度须在整合前重新核其自然成本和机会公平，不能仅因同容量就称强基线已闭。此项是根新识别的适配问题，不重跑失落L7或声称原文有未写的批量算法。

用户新增LMAPF顶刊顶会架构精读任务已实际交给Copernicus，在P10/C9交付后接续L12和新Opus C11；要求至少四篇非PIE-D正式论文、原文阅读范围、贡献/基线/消融/规模/费用/失败证据到本项目的映射。中途已读信息不替最终报告；桌面必读更新待根核选。论文架构学习不改变最终固定后的正式顺序。

两次根文档补丁先后因上下文选择/区块顺序不符在应用前失败，修正后才实际成功；不把失败调用记为修改成功或研究测试。新工件仅研究目录、编辑仅apply_patch、shell每段rtk；没有实现、伪代码、构建、研究测试、仿真、调参或实验载荷/结果，未读35–38及受限载荷。冻结文件和完成回执保字节，H、T_delay、B_CAL、B_max、B*、P_active、density N仍原义未赋值。73未固定/未送审/未接受，六门仍2 PASS /3 UNKNOWN /1 FAIL；目标active，实验前准备未完成。
