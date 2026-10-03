# Astra R11 三线非盲技术后评

本稿由实际 GPT-6-Astra/ultra 工作代理形成。本人实施主线，读取第三线和查询线最终报告、汇总与root独立复核，并独立只读复核查询native与通用Index的结构条件；因此这是非盲技术判断，不是外部盲审，也不代替research-mentor的独立意见。三线本轮登记工作均已完成；本稿形成时没有新增实验、改动冻结实现或训练新模型。主线完整工件仍在本机ignored目录，第三线与查询线链接指各自公开分支的工件路径，发布操作由root负责。

我的优先路线是：保留已证明等事件省费用的主线实现，停止把现有时长ridge或换大模型当作默认下一步；优先把原控制器、合法资源释放与任务后果接到同一决策接口，再判断学习目标。R11支持三个有限进展：相同物理/公共行为下的实际计费下降，真实作者图到明确primitive几何执行层的有限映射，以及查询相对原策略的小幅TRAIN任务空间和稳健服务时间空间。这些尚未共同构成一个优于作者方法的学习规划算法，也不能将查询线结论概括为“没有任何学习空间”。

## 主线：优化成立，研究收益的解释仍须克制

十二个原输入全部完成。每次SOURCE的pin、schema、35个字段、完整历史逐字读取、身份核验及release保持；guest仅在稳定身份/种子/账户与全部旧命令前缀相等后，复用原控制器的不可变根并执行新增命令。失效、保留、数值运算、负控和析构均真实付费。这是有前缀依据的增量执行，不是把核验工作转到host或免费跳过SOURCE。

|长度/策略|R11 Natural实际步|相对R10减少|R11 Strict收费|相对R10减少段数|
|---|---:|---:|---:|---:|
|3 WAIT|155,022,891|41,550,232|1,602,224,128|3|
|3 paid|248,455,204|39,670,744|2,332,033,024|5|
|12 WAIT|235,468,736|40,188,955|1,669,332,992|5|
|12 paid|345,001,806|51,105,653|2,441,084,928|4|
|27 WAIT|385,829,407|51,134,165|1,811,939,328|4|
|27 paid|504,723,713|66,414,390|2,575,302,656|8|

Natural总实际工作降低11.63%–21.14%，Strict收费降低1.36%–2.54%；两者不能互换。全部2964段守恒、1388条非费用/非host耗时事件等价、792个物理帧、十八ELF隔离重编及10350父pin均通过，root另行核对原始记录也通过。49个登记构建/原生/重编命令成功，两次提前读取尚未生成RESULTS的后处理顺序错误另行保留，没有修改实验补救。

我认为这是应保留的系统改进。它没有新任务收益：原16tick、四项任务和全部服务时刻未变，长例paid相对WAIT仍只将服务时间和50降至44，本轮多付118,894,306个Natural实际步。三种固定长度不是泛化样本，制度/策略臂也不是独立场景。没有计价汇率时不能说这个取舍产生净收益。

空间代价同样真实：每个活动头保留最新完整history和控制器根；批量获取时旧缓存与新历史共存，更新及诊断还暂存根和局部副本。源端完整读取及guest前缀比较未消失，缓存不是常量空间。服务换occurrence时在C-END内释放，最终缓存为空；没有测量峰值guest字节，不声称已得到空间上界。较小的Strict降幅也说明大量公共poll和必需段仍然存在，但不应据此在本轮继续扩实验挑选更大节省。

信息边界没有改变：WAIT与paid的生命周期内部共同读取完整未闭合历史，代码只用来核验END/服务；额外POSITION提供当前合同要求的认证放行权限。因此现在可说“认证放行的时间—费用价值”，不能说paid买到了整个WAIT系统完全未知的新物理信息。若下一研究要讨论信息获取，必须实际分离NORMAL_END通知与付费进度接口，让前者只向决策模块交付已发生的闭合事实和完整身份；内部原历史的访问边界也须实现和验证，不能仅在已有全可见数据上约定不使用某字段。

本机ignored依据：[主线报告](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/incremental_lifecycle_20261003_r11/REPORT.md)、[逐事件和分项比较](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/incremental_lifecycle_20261003_r11/R10_COMPARISON.json)、[独立root复核](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/incremental_lifecycle_20261003_r11/ROOT_COMPARE.json)、[负控](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/incremental_lifecycle_20261003_r11/NEGATIVE_CHECKS.json)、[重编](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/incremental_lifecycle_20261003_r11/REPRO_CHECK.json)。这些绝对路径标示本地证据位置，不是远程公开下载链接；不能将四份公开进度文档说成已公开这些实现。

## 第三线：跨过有限执行映射，尚未接通原控制器闭环

本轮27次登记执行全部通过：16次单位步逐状态、cost与makespan精确复现作者图；11次新增primitive执行包括九个random60图/时长配置及两次真实timeout回退同迹检查。原43个作者源文件未改，没有重新运行优化器。独立审计覆盖239,222个MOVE、523,274个连续轨迹段和终点驻留；同图中途序列化恢复、已承诺依赖保护和反转拒绝也已落实。这比仅能编译作者程序或导出图更进一步。

这个执行层是有理数时间、分段仿射位移、圆包络的独立模型：TURN/STATION不平移，半MOVE不提前推进作者顶点状态，几何ENTER/EXIT与资源预约分开，type2按实际ARRIVE释放。其瞬时速度切换不等价于原加速度/反馈控制器；当前独立几何审计是机器人之间的圆盘间距，不是另一次地图障碍或执行动力学认证。原路径来自作者，不能把继承有效路径和新层两两避碰合起来夸大为全部原控制器适配完成。

在复用random60上，三种primitive配置的作者selected图均减少完工时间总和，却增加makespan。例如nominal的original为2085.75/77.25，GSES为2042.75/79.5；axis下GSES总和2341，Improved为2345，也不能依据名称推定后者在新目标上支配前者。图仍按原作者目标选出，并未针对新增TURN/STATION/停顿重新优化。这是接口和目标差异的证据，不是新的规划性能排名。

我建议将这套公共事件/资源合同保留为下一控制器适配的检查基准，接入原实际primitive控制器后再接优化器的合法图更新：先验证真实到达/离开、目标驻留和活动前缀，再接受满足承诺的依赖修改，最后在同一扰动和目标下比较原图/GSES/Improved。现有真实同图恢复不能替代在线换图闭环。固定路径调度与LMAPF重路由仍分别报告；当前时长ridge不宜重新作为核心方法加入。

依据：[第三线最终报告](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/gses_primitive_20261003_r11/REPORT.md)、[第三线协议](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/gses_primitive_20261003_r11/PROTOCOL.md)。

## 查询线：存在有限任务和时间空间，尚不是学到的策略

R11完成四个新TRAIN family的94次原生运行：8个整程参考、26个完整单次分支、60个事前固定两次干预臂，执行失败0。原140是上限，实际公开选择产生94次；没有补满预算。独立物理/精确策略审计及root原始价值空间复算均94/94通过；前缀与固定π0续策、38个同动作或第二点不可达的全轨迹对照、58项SKIP生命周期及22个负控均通过。登记前random场景行数不足、下载404和审计器缺失import的修正与时点在报告保留，不能写成整个工作流从未遇到失败。

|family（新TRAIN种子）|原condition π0任务|整程WAIT任务|最佳单次任务|最佳两次任务|
|---|---:|---:|---:|---:|
|empty 111101|48|49|49|49|
|empty 111102|41|40|41|41|
|random 112101|48|48|48|48|
|random 112102|51|51|51|51|

八个完整单机会中，empty 111101的持久SKIP有真实的相对π0 +1任务空间：48变49，整程WAIT本来也是49。逐family事后选择登记最佳臂得到189，高于固定condition和固定WAIT各188，恰等于逐family选择两个参考中较好者的189任务包络。因而条件选择有可检验的潜力；既不能说“没有任务空间”，也不能把这个后见选择器写成已实现的189任务策略。没有登记臂在自己的family严格超过两个参考的任务数；这只限定本轮有限集合，不是全策略最优性证明。

服务时间的改善也不应抹掉。登记目标J=全FIFO任务数−T/16385，T是每机器人固定前四项任务的截断服务时间和，未完成项记128；T不包含全部FIFO，也不是生产计算费。11个探测臂的J下界均严格优于两个参考，分布在empty 111101四臂和random 112101七臂。在random 112101，事后最佳`pair_9_SKIP5_SKIP_distinct`同为48任务，T相对condition减少[6.988960, 6.989052]，相对WAIT减少[20.621247, 20.621339]。empty 111101的`pair_1_SKIP6_SKIP_distinct`同为WAIT的49任务，T再少[1.268228, 1.268320]。这些区间已排除0，不能归作数值中点噪声；它们仍是TRAIN后见诊断。这两个臂各用16次QUERY，WAIT为0次，尚未接入主线实际计价，不能宣布净收益。

两次干预的第二动作在distinct臂48/48达到，在successor臂5/12达到。相对相同首动作的单次臂，60臂的任务变化为59个0及1个−2，正增益0；distinct臂有5个稳健J次项增益。负例是random 112101的`pair_9_QUERY5_SKIP_distinct`，第二次合法SKIP造成−2任务，必须保留。七个未触发successor臂不是“成功WAIT”：四个在预算耗尽前看见后继head却没有合格候选，三个在耗尽前连后继head也没有看见。公开后继存在、合法查询机会存在和预算仍可用是不同条件。

八个选中单机会中只有一个双候选，coupled机会为0；全部94条含重复轨迹的普查中有180个多候选决策、分布于84臂，coupled仍为0。这些重复决策不能当作独立样本。58个完整occurrence SKIP均在匹配正常END被接受后解除，原身份曾在被遮蔽期间重新可见162次，44项出现同agent后继occurrence；这支持持久跳过改变次数预算分配，不证明计算费用下降。

独立源码判断见附录：当前World3的coupled层不可达，来源于几何、访问先序和需求资格共同构成的不变量，不是仅因四family未观察到。它限制“靠增密获得coupled训练样本”的做法，却不证明查询任务价值为零。不同源格的候选仍会竞争预算并影响后续任务；本轮+1任务和时间次项正说明瞬时关系不耦合不等于策略没有后果。没有训练或留出测试，不能称模型成功、模型失败或学习收益。

我的判断是保留两个明确目标：现接口下可小规模检验公开条件选择或同吞吐的时间改善；若要研究多资源证据选择，则先实作能产生该问题的合法接口。前者不要求等待coupled层成立，但需要比固定参考及简单公开选择器更强的留出结果；后者不能靠给现匹配关系图加GNN来替代。依据：[查询最终报告](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/public_opportunity_20261003_r11/REPORT.md)、[汇总](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/public_opportunity_20261003_r11/SUMMARY.json)、[root原始价值空间复核](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/public_opportunity_20261003_r11/ROOT_VALUE_SPACE.json)。

## 优先路线及下一可执行方法

第一优先是把决策接口与研究问题对齐。保留当前安全和身份条件，在新的隔离协议中构造2–4机器人、有限FIFO、真正跨多个资源的原控制器MOVE或其他有物理依据的资源事件，使一个已认证进度可能合法退役多个不同资源，或者一个当前需求确实依赖多个foreign责任。需求必须真实生成并满足公开先序/承诺条件；不能手写claims，也不能删掉precedence检查制造“复杂图”。长primitive是一条可执行路径，不是唯一数学必要条件。扩大真实包络、多个合法资源类型等也可能改变拓扑，但均需相应的安全合同。

第二优先是对新的接口重新验证动作价值。先用新TRAIN-only有限机制，把正常END、立即认证查询、当前WAIT、持久SKIP及登记的有限查询组合放在相同公开前缀和同续策上实际执行，对强简单策略和整程WAIT分别比较。候选可依据公开释放阈值、当前责任集合、预算及当前任务目标排序；小候选集合先用透明的有限枚举或规则作参照。本轮现接口已经有1/8单机会超过π0及稳健时间次项，不能将“先确认空间”误写成全线零空间；新的多资源接口则尚无这项证据。后果依赖实际允许的释放和服务，不能把预测更快、关系更多或查询变少自动当成任务改善。

空间成立后进入第三步：冻结预测目标、数据切分和公开特征，再学习“同续策的任务—时间—费用差”或其中明确可识别的概率，而非继续把完整执行时长直接加到目的地代价。现查询线也可单独登记一个小型条件选择研究：预先决定是以固定π0为任务目标，还是在不减任务条件下改善T，对照同时包括整程WAIT、固定condition及简单公开选择器；不能用本轮四family的事后最佳充当已学选择器。采用历史规则、公开解析概率、无历史版本等强简单对照，保留多候选与组合决策的实际覆盖。所有测试family应在机制选择之后另行登记，不把本轮TRAIN探索包装成事前TEST。生产实际费用、查询次数预算和第三线几何时间仍分别计量，接口未统一前不相加。

与上述方法开发并行的基础工作是第三线的原控制器/作者优化器接入；它提供真正统一的外部固定路径调度对照。我的研究优先序仍将真实多资源决策置前，导师工程上优先作者异图采用的顺序则更直接补外部对照；两者有交集，但不是相同意见，也不应写成一致投票。当前不建议以进一步微调缓存、叠加GNN或反复调整ridge投影系数替代这些依赖问题。主线费用改进可以支撑方法可实现性，不能独立替代MAPF层面的算法贡献。

## 与已有学习工作的区别及尚未证明之处

[REMAP v2的IV-C与V节](https://arxiv.org/html/2511.21886v2)不止学习动作时长及末端状态：它用在线后验改善概率门控昂贵预测器调用；ESADG在固定路径上搜索可逆边组，并以预测执行目标评价。该文的执行接口也合并连续平移。因此“学习时长”“不确定性门控”“固定路径可逆群优化”或长MOVE本身均不能单独作为本项目新意。

[Should I Replan? v1的III-C节](https://arxiv.org/html/2604.25567v1)已将同一受扰场景触发重规划前后的真实执行SOC差作为学习目标。因而把标签从时长换成实际任务/时间差，不自动构成新的方法贡献。其动作是重规划而非本项目的进度证据查询，这个区别需要由观察接口、授权规则和计价后果体现，不能把邻近工作表述成只做预测误差。

本项目可继续检验的区别，是带完整occurrence身份和时效约束的物理证据/认证，怎样在有限费用下改变合法资源退役及后继任务服务；晚到或失效证据仍须承担费用，预测本身不能授权释放。与已知状态下选择是否重规划相比，这里可能涉及不同的观察、授权与责任合同。这个差异目前是候选问题定位，不是已证明的新意：共同内部history已可见时，应称认证权限价值；只有实际隔离后才可讨论新增信息价值。还需要统一执行器、强作者对照、明确可改善空间和针对性的近邻核查，不能靠审计或工件数量宣布论文贡献成立。

## 附录：当前coupled层不可达的条件性源码论证

论证对象是当前查询R11 `World3` 的合法可达状态，不是所有MAPF执行器，也不是通用Index。前提包括：整数网格中心、单位cardinal MOVE、半宽0.1实体加0.05误差扩张、独占格owner、每机器人只提交一个ready next demand、完整承诺路径不被重写、按规划轮唯一目标以及保存的last_depart先序。以下定位指冻结的R11源码；本次只读分析未新增实验。

**1. 一个当前demand最多一个foreign relation。**

[coarse_cells](/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/public_opportunity_20261003_r11/joint_history_native.cpp:33)以1/20整数单位构造扩张0.15的闭AABB；[geometry](/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/public_opportunity_20261003_r11/joint_history_native.cpp:240)给出单位cardinal端点与0.1+0.05包络。相邻单位格之外的其他行/列与该扫掠严格分离，所以完整资源mask至多含源格s和目标格d。

[rebuild_demands](/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/public_opportunity_20261003_r11/joint_history_native.cpp:279)只给ready、存在next且precedence成立的机器人生成一个demand。ready时源格由初始化resident或[正常END交接](/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/public_opportunity_20261003_r11/joint_history_native.cpp:341)保留为自己的resident；未收到正常END时机器人仍不ready。Index的[owners映射](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation/pie_query/include/pie_query_index.hpp:96)每格只有一个责任，[rebuild](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation/pie_query/include/pie_query_index.hpp:405)忽略本agent责任并按foreign responsibility分组。源格不贡献foreign relation，唯一目标格至多贡献一个，所以relations.size()≤1。

**2. 一个候选至多有一个可退役的当前head claim。**

Index在[endpoint检查](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation/pie_query/include/pie_query_index.hpp:424)把包含原终点的责任置为不可退役。[candidates](/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/public_opportunity_20261003_r11/joint_history_native.cpp:371)只收集retirable且有threshold的关系。因此单位MOVE候选只能通过其源格c产生claims，不能通过保留的目标格产生claims。

每轮规划的[unique目标检查及last_depart登记](/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/public_opportunity_20261003_r11/joint_history_native.cpp:269)先处理全体离开，再给每个进入冻结最新离开的依赖；即使前机器人本轮离开、后机器人本轮进入，也记录到正确的本轮departure。[precedence](/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/public_opportunity_20261003_r11/joint_history_native.cpp:255)要求该departure已launched。

据此把格c的历次计划访问按规划轮排序。若某次进入e仍是被挡住、尚未RUN的当前请求，则同机器人在e之后离开c的outgoing不可能已launched：自身执行按next顺序，[RUN后ready=false](/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/public_opportunity_20261003_r11/joint_history_native.cpp:318)，只能在正常END后再次ready。下一次计划访问c的进入因此未满足precedence；沿访问链归纳，更晚的进入也不能成为合法当前demand。所以同一候选源格最多有一个合法等待进入请求，候选claims.size()≤1。已经暴露的候选至少有一项claim，因此实际恰为claims=1、owners=1。

coupled定义中的“一个候选阻塞多个当前task/head”及“某claim有多个owner”在这些不变量下都不能成立。多个不同格上的候选—请求对可以同时存在；多候选数不能代替耦合度。这是源码条件性推导，未声称完成形式化证明，也不是从四family的空观测直接推出不可能。

**3. 反例说明结论不能推广到通用Index。**

通用Index的[关系重建](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation/pie_query/include/pie_query_index.hpp:405)遍历任意资源集合，[out计数](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation/pie_query/include/pie_query_index.hpp:458)没有1的上界。例如，若不要求“前次访问的outgoing已launched才公开后次进入需求”，可有活动A从(0,0)移向(1,0)，ready B在(0,1)、C在(−1,0)，二者都提交进入(0,0)的合法待授权需求。两者的源格分别归自己，目标格同由A源格责任阻塞，通用Index可给A两项claim。它们竞争同一资源，不能同时获准RUN；独占授予仍可保持安全。当前World3的规划轮唯一目标与last_depart链恰好禁止二者同时成为合格当前demand，所以这不是当前程序的可达反例。

因此，仅加密度或给同一瞬时关系图换GNN不能使coupled层出现；但不能推广为一般图模型无效或查询不能影响未来任务。若需要改变拓扑，应通过真实更长的扫掠、多资源事件或其他经过新合同批准的物理接口改变上述前提。不能直接绕过precedence、重复当前head或把不合格未来请求计入claims来制造模型所需的数据。

---

完成状态：主线12臂、第三线27次、查询94次的最终报告与独立复核均已读，三线非盲技术后评完成。没有新增实验、追加模型或修改原稿；实现范围和信息边界仍以各自登记协议为准。此终评不将已完成的工程量等同于已确立论文贡献。
