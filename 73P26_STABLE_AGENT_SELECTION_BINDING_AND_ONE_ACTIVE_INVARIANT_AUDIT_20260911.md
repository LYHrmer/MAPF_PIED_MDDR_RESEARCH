# 73P26：稳定agent选择绑定与单一中心Active不变量核验

2026-09-11，`/root/source73_r0_remaining_contract`。NO-SKILL / CONSTRUCTIVE / NONBALLOT；不是正式独立逻辑审查或资格验收。未调用Claude，未读取C20或P24/P25，未重做P23、失落P7/L7或源码/数值后端调查。保持 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 1. 结论

在当前73已经写出的唯一未闭请求、原子中心提交、不可撤授予和END/READY/消费规则下，主PIE与H19共同适配均可归纳保持：**同一session/agent至多一个中心GRANTED且未FINISHED的tid**。本题未找到遵守这些转换而产生两个此类tid的合法轨迹；H19多个enqueued、源规划并行或本地先END都不是绕过该不变量的更新入口。

拟将RR排序投影为稳定(session,agent)是可明确实施于纸面的方法修订，无须改变Active定义、物理门或加入新优先级。必须同时明确：从同一冻结中心视图选择agent并绑定其唯一完整tid；SELECT成功发布时，请求、提交身份与last_agent一次原子生效。若实际中心出现重复Active或唯一请求槽与索引不一致，属于协议矛盾，不能任意去重、挑旧/新tid、隐去一项或返回普通NO_QUERY。

需要补写的是既有状态不变量的映射和提交检查，不是再增加一套物理准入条件。稳定key修正原动作e变化可能影响RR顺序的问题；它不保证有限O有足够成功选择、消息交付、到达、原终点关闭或研究净收益，主D的正分分支也不因此获得普遍公平性。

## 2. 输入身份与实际阅读

写前精确确认目标不存在且非符号链接。唯一科学输入为当前主稿：

`73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md`

- SHA256：`60e128eed81a7448e6e8bfcdd51cbc930e437716651ffb0b76259c004c71f661`
- 208378 bytes / 649 LF。
- 完整读§5 L92–149、§7 L176–201、§8 L202–227、§10 L354–430、§11 L431–462；定点读§9 L244–258、L262–274、L298–306，以及§12 L463–508；再只读§13–15中RR/last/轮询相关命中L515/523/549/557/558/615。没有读取源文件、实验载荷或其它新审查意见。

这些段落给出了本题全部创建、关闭、队列、选择和失败分类依据。以下论证是对纸面转换的独立分析，不声称已建立实现状态机、执行过测试或证明整稿所有不变量。

## 3. 中心不变量应精确指向哪个状态

固定a=(session,agent)。令U_a是当前中心权威请求记录中状态为UNGRANTED或GRANTED、尚未关闭的请求集合；令A_a是其中当前状态为GRANTED者。由§5 L96与§7 L178，预期不变量为：U_a至多一个；非空时其e=d_i+1；A_a包含于U_a；Active恰为所有A_a之并。tid只识别请求，完整不可变alpha还绑定source/job、plan_epoch/slot、原边、parent及几何/控制版本。

这里数的是**当前中心状态**，不数历史GRANT日志、被快照保留的旧状态、在途重传副本、资源瓦片owner条目数或本地active_tid。一个tid可以拥有多个资源，历史记录也可长期保留；都不构成多个当前授予。审计旧快照中的GRANTED字段不能被重新加入当前Active。

建议将中心“唯一未闭请求槽”和Active的按agent索引关系写明：同一规范agent key只能映射到该唯一槽的GRANTED tid；原有Active总集合和索引必须一致。索引只加速这个已定义集合，不允许覆盖旧键值而丢掉仍活授权。普通重传同一tid只有一项；同e的不同alpha不是两个可并存请求，而是绑定矛盾。session/agent身份来自原合法INIT，source generation、append revision、请求e、control_epoch均不生成新的agent身份。

这是§5唯一性声明的显式化，不要求每次QUERY扫描全部历史证据来重新证明。维护及局部提交检查可在原中心writer内收费完成；实际采用的索引仍需与参考集合等价，不能靠数据结构“一个key只存一个值”掩盖被覆盖的活责任。

## 4. 创建、关闭及例外更新的归纳核对

| 更新链 | 已写依据及其对U_a/Active的作用 | 本题裁定 |
|---|---|---|
| WORLD_GIVEN与软件INIT | §5 L100、§12 L465–467：只有bootstrap/resident责任；合法INIT才建立应用身份/索引，不产生MOVE grant | 合法初态无GRANTED；失败不部分接管、不清空旧责任来伪重启 |
| SOURCE_OR_EXTEND生成／重试 | §7 L190先分当前GRANTED、UNGRANTED、无未闭请求等互斥分支；仅最后合法MOVE分支生成一个原请求，重试同绑定不换tid | 未闭请求存在时没有创建另一e的合法分支 |
| 普通首次授予 | §5 L102–104：原请求、PRECHECK与完整不可变绑定，一次提交将该UNGRANTED改GRANTED、预留并封存授权 | 改变唯一槽状态，不增加第二槽；同tid重复不生成新授权身份 |
| GROUP_ADMIT | §5 L106–112从有效未授请求构组，全组一个原子单元，每成员的原请求转GRANTED | 从U_a唯一性可推成员agent互异；序列化成员须显式核同agent无重复引用，重复不能当两个成员发两个tid |
| 扩cap／重传／控制恢复 | §5 L114、L124–130及§7 L192：只作用于既有原tid，保持不可撤lineage；RUN/BRAKE、模式及attempt各有独立水位 | 可能改b/C/模式/发送次数，不创建中心新GRANTED请求 |
| 未授CANCEL | §5 L120：未GRANTED才ABORTED并推进d；已GRANTED一律DENIED_GRANT_LIVE | 不靠取消释放正在授权的请求槽；新e只在合法关闭后产生 |
| 物理END及首推 | §5 L134–138：本地active_tid置NONE、产生历史记录，中心仍要付费接收/核验 | 不改变中心Active。物理已END而中心未FINISHED仍是可选Active |
| 中心FINISHED | §5 L140：关闭记录、d、Active移除、owner终点改tag及READY/FINISH_RECEIPT同一原子提交 | 唯一GRANTED在该提交关闭；没有“已移除Active但仍允许旧grant活着”的半状态 |
| READY接收／消费／WAIT | §5 L142、§7 L194：READY只置验证标志；后继LOCAL_POLICY一次消费并进入RESIDENT_OPEN；WAIT在无active/pending下消费 | 不创建中心grant；下一MOVE还须新请求和PRECHECK。FINISHED不等于已消费 |
| GROUP_RETIRE | §5 L118：全部成员中心FINISHED等条件下只退栏，endpoint owner保留；READY/消费本可先进行 | 不关闭额外tid、不分配新tid，不是给某agent第二个授权的旁门 |

归纳的关键是中心唯一writer和原子单元。GROUP_ADMIT必须在实际发布时仍绑定同一批唯一UNGRANTED记录及PRECHECK；不能把私有候选当成允许覆盖后来状态的授权。但当前单槽模型本身排除了另一中心应用作业在候选持槽期间先行提交；相应版本检查是对完整合同和故障的防护，不构造一个本模型没有的并发writer。

两个容易误读的中间态均合法：其一，本地已END/active_tid=NONE但中心A_a非空；其二，中心已FINISHED、A_a为空但本地pending/READY未消费。前者不能从RR中删去，后者不能为了“等消费”继续伪装Active。下一MOVE的物理许可由原PRECHECK/READY链限制，不由本选择器重新定义。

若FINISHED后Kc仍指旧槽，SOURCE可能只有滞后信息，后继PRECHECK依真实c/phase/起点拒绝不合格绑定；不会因新e就允许重执行已消费槽。这样的未授停滞或重试代价不能被解释成双Active，也不能为修RR悄悄用真实c更新Kc或跳槽。

## 5. H19、源CAS及恢复没有第二创建入口

H19 §10 L390将enqueued和物理GRANTED明确分开：ADG_ENQUEUE只连续追加执行记录并记逻辑入队；APPEND安装仅增长本地执行尾，重复旧槽不重建控制或c。L402的SOURCE_OR_EXTEND沿共同Kc/原记录产生或重试当前MOVE，初授整cap且沿§5物理门。因此多个已入队原动作只增加待执行承诺，既不各自产生一个中心请求，也不因Type-1前驱已enqueued就可以越过唯一请求槽。

L400另将finished、消费、安装分开。某MOVE的ADG finished需要付费维护中心FINISH_RECEIPT；WAIT finished没有MOVE tid。外部finished索引尚未维护时，中心FINISHED已完成也不把旧tid再加回Active；反之，不能用APPEND安装、物理END或名义时长让中心提前关闭它。H19R-S只能轮询其同定义中心Active，不能把可调度/staged/enqueued整图投影成eligible agent。

内部PIE的接纳CAS仅append不可变Π，§8 L206/224不改既有槽/授权；拒收保留合法源内部历史，不生成新物理请求。H19的cut必须纳入所有已登记请求/授权和可能生效缓存，L380–388不撤旧执行历史，source generation不重置plan_epoch/c。新候选可以预示未来动作，但不能改当前tid的alpha或把原请求槽换成新源版本。

END/READY重发、H19两类RESEND及CONTROL_RETRY沿已有身份恢复；没有创建新tid的恢复例外。SHARED-OFF/DRAIN/恢复ACTIVE不清d、c、Active或已提交grant；CENTER_FAIL_STOP禁止后续中心计算/发布且不恢复清空，WORKER_FAIL只停止源会话，原物理责任保留。独立NATIVE旁路在共享副作用之前选择，不能热切来重新INIT活授权。以上已写路径没有绕过中心唯一性；若后来另加恢复/重置入口，须另证，当前不能预授许可。

## 6. 稳定agent轮询的唯一绑定合同

保留原Active集合。对SELECT的付费CAPTURE视图V，取I(V)={a：A_a(V)非空}；在唯一性成立时，每个a对应唯一完整tid。RR只对I(V)的稳定(session,agent)规范序排序，last_agent初态为小于全部合法key的前哨；非空时取严格大于last_agent的最小key，无则回绕最小key，空则NO_QUERY且不更新。这里只定义记录初态，未赋任何保护参数。

选出的a及其唯一tid必须在**同一V内**一起确定。准备的POSITION请求保留该tid和原要求的完整请求/源/几何绑定，不能只发agent等后继authority自行挑“当时最新tid”，也不能发布时悄悄换成这个agent后来新动作。stable key用于顺序，不缩短授权或证书身份。

后继SELECT成功发布的唯一单元应同时形成请求／其不可变发送意图、原提交幂等身份和last_agent←a。请求准备失败、无eligible对象、非法模式、未完成、版本/绑定失效、发布容量不足或未发布废弃均不推进游标；已经合法发布后，采样不匹配、失败、迟到、丢包或无增量q不回滚游标。重放同一选择提交既不新建请求，也不重复推进。只有已发布完整选择计一次，不能按“曾计算出候选”计一次。

游标在该方法session内持久保留；agent暂离Active、旧tid FINISHED、新e、组退栏、planner job/generation、append revision、QUERY_OFF/DRAIN/QUERY_ON均不重置。合法新episode/session的独立INIT另按原合同，不把尚有责任者重置为新session。CURSOR全fleet轮询、SOURCE modulo 3、READY重试及H19 APPEND/两类重传游标保持独立，不能与last_agent合并或互相推进。

适用范围：R、R-S、R-F_cap及H19R-S统一用该RR；D-S/D-F_cap正score最大与原“最早贡献需求、再完整tid”tie规则保持，零正分才用同RR，**D的每次成功选择也把自己的last_agent更新为所选agent**。各臂各自持有状态，不跨臂对齐；E0/H19E0仍不生成POSITION，不为维护一个不用的选择器虚收业务扫描。F_cap收到证据仍只更新q_evidence，H19仍保留原Type-2 finished限制。

## 7. SELECT同刻版本及失败分类

§9 L244/262给出的顺序是物理推进、自主事件、前行已完成单元发布，然后本行的付费操作。若中心FINISHED已在SELECT CAPTURE之前合法提交，快照中不再有旧tid；若只有物理END或在途回执，旧tid仍Active。SELECT持中心单槽直到它自己的单元发布，后继FINISHED/SOURCE/MODE应用作业不能同时写中心状态；H19批也不能与SELECT同时持槽。因此“选完agent，另一个中心job先FINISHED并GRANT新tid，再原SELECT发布”的调度不是本稿合法反例。

实际后端或未来并发修改若仍产生绑定不符，原发布检查应拒绝该私有单元并计费，不在发布点免费重新选择。单独物理END、真实任务A变化或同agent连续s变化不构成SELECT中心Active/选择依赖失效；不能据它们免费取消选中旧tid或刷新候选。尚未生效、只已排队的MODE也不提前改变eligibility；原外生CENTER_FAIL_STOP/全臂Stop按公共顺序阻止其后的发布。先已成功发布的选择保持游标，后发故障不回滚它。

| 观察到的情况 | 正确处理 | 不允许的替代 |
|---|---|---|
| 合法Active为空／策略模式禁新查询 | 原NO_QUERY或对应模式空结果，费用照计、last_agent不改 | 为补轮询而向resident、UNGRANTED或enqueued动作发POSITION |
| 正常选择准备／发布失败或未完成 | 保留私有/失败身份、实际费用和原游标；沿原容量与生命周期处理 | 把失败当选中过，或免费换另一个agent |
| 相同tid的历史重传／同一提交重复 | 完整身份核验后原幂等处理 | 因副本数大而在RR中占多个位置 |
| 两个不同当前GRANTED tid同属a；唯一槽/Active索引不一致；同tid异alpha | PROTOCOL_CONTRADICTION，按§12协议/身份破坏留证；不给普通选择结果、不清理活责任来“修复” | 去重取最小/最新、把一项改FINISHED或当普通NO_QUERY |
| 不能认证索引/版本或评分前缀 | 保留未知及UNVERIFIABLE/INFERENCE_UNAVAILABLE等原边界，不伪称不变量成立 | 用未发现重复或中心只见一项代替证明 |

若协议状态已无法维持定义，原§12 L483/485的Stop/PROTOCOL_OR_SOURCE_INVALID及前缀评分规则适用；本题不新增任意停止时刻，也不把未认证前缀填零。普通来源输入/非匹配包仍按原拒绝分类，不能把一个被正确拒绝的包当已发生双授权。

## 8. 真实排序差异及不应声称的公平性

原RR key=(session,agent,e)有一个合法差异场景：令a在规范序上先于b；上次成功选择a的旧e，b持续Active。其后原日历恰有足够合法服务使a旧tid完成中心FINISHED、READY消费、CURSOR更新及下一MOVE正常授权，而下次QUERY尚未发生。到下次选择时a的新e严格大于旧e，新的完整key仍排在b之前，原规则可以再次选a。全程每agent至多一个Active；这不是双授予反例，也不依赖跳过付费链。

稳定key保留last_agent=a后，a的新tid不会仅因e增加而插到“严格大于a”的区段；仍在集合中的后继agent可按同一规则被选。这是明确定义的顺序变化，不宣称a换代在任意有限O内都可能完成，也不保证b一定成功收到或完成查询。

不加入“必须运动中”“已安装cap”“未物理END”“有正阻塞分”“已APPEND确认”等额外eligibility；这些事实有些是私有的，有些与原Active定义不同。主D仍可能反复选择高正分者而不给另一agent机会；D每次成功更新last_agent不等于交替公平策略。有限日历、长中心作业、丢包或服务耗尽仍可阻止后继成功SELECT，因此不能从稳定序得到壁钟饥饿界、到cap／END或Q正效应。

## 9. 最小同步改稿点与交付边界

建议只同步§5 L96/普通及组首次提交的唯一槽—完整绑定检查，§7 L178/184的稳定投影及游标规则，§9 L250/262的writer字段和原子SELECT单元，§10 L429的外部RR引用，及§13 W21/W22对应文字。GROUP_ADMIT成员agent不重复从既有唯一未授请求导出，补明其核验；不修改PRECHECK、END/READY、GROUP_RETIRE、H19 enqueued或D正分eligibility。

新增/维护按agent索引、身份比较、扫描排序、游标位长、请求封存、发布核验、失败和日志全部沿原Srv_C及后继通信服务收费。不要求R执行D的完整score计算，不向E0加不存在的查询；索引替代若采用，仍须同快照等价和维护成本证据。主D/R比较将对应这个明确更新后的R及D回退规则，不能冒称与旧逐occurrence RR逐迹等价，更不能运行后择强弱版本。

本报告条件结论是：现有合法转换可维持单一中心Active，稳定agent选择可在原门和费用规则内精确绑定；尚无实现或后端资格证据。未改73、旧报告、行政/Git/桌面；只以apply_patch新增本文件。未读35–38、Q及任何受限载荷，无实现、伪代码、测试、仿真、调参、参数或结果生成。最终全文读回并核SHA256/bytes/LF后结束，无Claude或其它活工具句柄；六门与HOLD不变。
