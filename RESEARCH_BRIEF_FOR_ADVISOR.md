# 导师汇报：研究问题、数学表达与当前阶段

2026-09-30 第四轮更新（Q2 §74）：**两个探索分支均已真正训练模型并完成原生留出；当前均未建立学习相对强规则的独立收益。主线首次在原预算进入compute_position和Authority.capture。** 用户指定GPT-6.1-sol-ultra与research-mentor分别独立评审后，继续三线实作：[本轮结果与后继设计](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20260930_R4.md)。学习作为主动研究候选，是否进入论文主贡献由真实决策与任务收益判断。

主线用保留原SOURCE读取/Release顺序的私有内联历史存储消除15-command临时堆清理。第15次advance885223→865279，compute_position在1034309、Authority.capture在1034387真实进入；原1048576供给仍在重复精确时间比较耗尽。221项保存检查与根独立费用/指令/ELF核验通过；**尚无enclosure/POSITION或完整查询净费结论**。下一隔离后继复用接收阶段已付费解析并验证的私有精确时间，保持原比较、所有权、供给和kernel。

[查询价值模型](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/public_value_20260930_r4/RESULTS.md)从官方新60tick源抽12个任务不重叠组，固定8/2/2训练/校准/测试，完成598个原生臂并冻结ridge。两留出组均104/104任务；WAIT总流时2063.299166，强内部规则2056.297864，模型2060.381957。模型未胜规则；当前首次决策前没有本世界END，已运行候选的事后最好收益上限仅约0.4242%。下一实验接入持续任务与已交付历史，在新的完整run划分检验后续多次查询，不在已见测试组换网络追收益。

[真实执行误差模型](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/gpibt_lsmart_error_model_20260930_r4/REPORT.md)完成40次400tick官方GPIBT→LSMART运行、102训练与48校准整MOVE标签及24原生留出。校准MAE为解析5.1875、历史1.6146、学习2.0746ticks；四策略全部测试动作一致，实际排序翻转为0。原40run与模型保持，另立共同rank映射后继，先验证校准公共状态的动作敏感性再跑未见seed。两例中间ACK不满足更严0.03m点误差标准已单列，未更换原控制阈值。

[正式hm+GPIBT比较](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/published_guidance_comparison_20260930_r4/REPORT.md)补齐已发表方法：同作者800机器人/1000步、三个seed，hm平均吞吐12.253333，高于缩短训练预算的OnlineGGO模型11.871333。作者学习方法对自身初始化的+33.1%不能替代强基线比较；未来任务因作者共用随机流而随策略分叉，不能当严格配对样本。以下§73及以前均为历史快照。

2026-09-30 第三轮更新（Q2 §73）：**三线均已继续实作。查询首次完成END-only原生四机器人联合执行，第三线完成真实活动MOVE扰动，官方OnlineGGO首次完成实际训练与独立留出。下一阶段主动加入执行误差学习候选。** [本轮三线方法设计](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20260930_R3.md)区分已得结果、作者复现与我们尚待验证的新方法；不要求传统方法彻底失败才开始训练。

主线两个新隔离后继完成不可变请求共享与五处私有payload转移。共享曾使第15次advance885207→901566变慢，转移修正恢复至885223；原CAPTURE时间检查通过，末端已到15-command临时容器清理的live_record/free_head。Natural/Strict仍在E201原1048576供给耗尽，**尚未compute_position/POSITION，完整查询仍未闭合**。root从原始费用/指令/源码身份重核366保存检查、6实际ELF kernel和主稿SHA；主稿既有修改保持。下一步只解决具名存储生命周期/清理阻点，不把工程优化写作论文创新。

[查询联合运行](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/public_joint_20260930_r3/RESULTS_20260930_r3.md)完成63臂、973原MOVE/END、77真实证书查询，共享资源与任务状态。一个预注册世界中RR B1完成4/4，当前释放概率排序B1仅3/4；方向条件率和global率所有任务结果相同。END-only从离线重放落实到真正原生actor，root核154冻结工件及全部任务流时。支持域是一个公开trace的四当前head，非100机器人全局benchmark；下一模型目标是查询的边际任务价值与后续驻留阻塞影响。

[真实活动MOVE暂停](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/gpibt_lsmart_active_20260930_r3/REPORT.md)首次击中在途运动：tick59触发、59..78暂停，原半MOVE ACK68→88、整格END84→104，另一机器人的真实驻留服务完成136→156。两完整run已输出800行公开可交付context、800离线target及独立原整格监督；保留惯性尾移/未完成任务，不宣称连续足迹安全或学习收益。

[官方OnlineGGO真实训练](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/onlineggo_training_20260930_r3/REPORT.md)保持作者800机器人/1000步和quad560，2代200候选×2训练seed，共400次native；训练选模后3个留出seed两臂6次评估，初始权重平均吞吐8.916→训练权重11.871333（约+33.1%）。root独立重放480万留出动作并核400训练目标/权重/种子。收益属于作者方法对自身初始化，不是我们新方法胜GPIBT；作者10000候选完整预算仍未完成。下一步将新剩余占用时间/阻塞传播模型接入共同误差执行域，与正式作者方法和同信息内部消融比较。以下§72及以前保留为历史快照。

2026-09-30 第二轮更新（Q2 §72）：**三线均已实现并实跑。主线完成真实控制历史重建，查询线接入公共作者轨迹，第三线完成官方规划器到真实任务服务；学习尚无独立收益。** 本轮分别由用户指定gpt-6.1-sol-ultra子智能体作技术判断，另一子智能体使用research-mentor作导师判断。两者建议围绕任务价值、空间误差证据与完整费用继续，模型暂作比较臂；[更新后三线设计](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20260930_R2.md)给出具体下一实验。

主线共享成功验证的不可变运动profile，并以通用精确整数平方根替代机器字有理完平方的昂贵软件浮点路径。第15次advance从975,973经962,177到885,207，相对上轮提前90,766步；物理历史回放及原CAPTURE时间匹配已完成。Natural/Strict仍在E201原1,048,576供给耗尽，最终为receive返回前请求复制/字符串清理，**尚未进入compute_position/POSITION，完整查询核账仍invalid**。46场景精确差分及2393数值案例通过，root独立重核304保存检查、六实际ELF的kernel和两制度原费用。下一后继针对已准入请求的重复深复制，继续POSITION/后车RUN/四收据及报价反馈；不能把前缀提前当整次净费下降。详细本机`implementation_binding_evidence/rational_sqrt_successor_20260930_r2b/SOURCE_REVIEW_AND_HANDOFF.md`。

[查询公共轨迹实验](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/public_trace_20260930_r2/RESULTS_20260930_r2.md)完成六run/120phase：10,746条实际END、4,260个局部WAIT/QUERY episode、96个匹配公开head的端点服务。全部2000源动作、355跟随关系、严格认证退休和560项END-only因果重放均核验；[原作者result/map/tasks/命令日志](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/public_trace_author_archive_20260930_r2/README.md)逐字归档。原native actor的private-helper缺口保留；新END-only是离线因果重放，不是第二次native。当前每phase最多一个正权任务候选，方向bin/categorical/解析/global/RR任务同效，方向反转Brier显著变差。下一项为真正END-only原生联合执行、多候选竞争、WAIT和真实收费。

[官方GPIBT→LSMART](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/gpibt_lsmart_integration_20260930_r2/REPORT.md)本轮nominal/pause均完整200ticks，各5次官方plan、400位置样本、1次真实20tick驻留服务，RPC任务身份错误修复后严格审计通过。原暂停实际只延迟派发，尚未击中活动MOVE。[官方OnlineGGO OBJ4评估入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/onlineggo_neural_preflight_20260930_r2/REPORT.md)真实运行560参数quad引导代价，未训练常量诊断100步/27任务并经1000动作重放核验；已训练作者策略R0仍待权重/配置/日志。主要比较使用已发表作者方法，内部规则仅作消融。以下§71及更早为历史记录，旧RPC待许可状态已解决；本轮主稿已有修改逐字保持。

2026-09-30 三线更新（Q2 §71）：**任务导向查询已出现更少查询、较低任务流时的具名机制结果；主线回放继续推进；官方规划器与连续执行器完成首步接通。** Astra技术判断与科研导师skill分别评估后，继续以“主线共同执行/费用基础＋查询方法候选＋替代底座探索”组织，学习是否保留由相同信息与资源下的独立收益决定。

主线两个新后继消除同刻推进重算和相同时间戳重复精确解析。原每行1,048,576供给下，连续同刻回放间隔14,209→9,774→3,804步；第15次真实推进入口1,046,261→975,973，提前70,288步。Natural/Strict仍在E row201的Launch→Approach精确构造耗尽，**POSITION与完整查询/收据尚未通过，原核账仍invalid**；不能将行内推进写成整行费用节省。真实接收接口46场景精确差分及161项独立工件/费用核验通过；原供给、生产实现、private kernel与已有主稿修改保持。详细证据本机`implementation_binding_evidence/REPLAY_PROGRESS_20260930.md`。

[查询线完整新表](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/BUDGET_TASK_RESULTS_20260930.md)首次完成384次运行、3456任务、4032原MOVE，覆盖容量0/1/2与四种公共任务结构、42份真实active输入。同容量2的一个慢组，任务规则查C一次/全流时36，内部admission/RR查AB两次/37；另一结构，新目标将旧窗口目标40降到38。144个目标配对8改善、136相同，同时保留4项多查无益；AR与lag2全部96配对同效。后续六任务不产生新策略分歧，当前仍属人工机制/内部消融，不冒充公开benchmark或学习独立优势。

第三线已让作者GPIBT输出实际送入LSMART的parser/ADG/ARGoS控制链，并收到首步真实连续运动与END。适配发现默认get_location可能是未来承诺格点，改在全队列完成且实际停稳时使用当前视图；这是明确的同步R1接口。两机器人实例的作者LNS默认group_size10造成第二次规划崩溃，已改其公开参数为2，算法对象不改；失败保留。最终nominal/pause两例仍待本机RPC沙箱权限，**未报告200ticks完整集成成功或连续安全通过**。LSMART是试验台，OnlineGGO真实学习策略R0仍待完成。

[2026近作核查](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/LITERATURE_DELTA_20260930.md)新增已发表RL-RH-PP（JAIR2026）与LDG执行框架（Artificial Intelligence2026）：泛化的学习优先级、动态组合放行均已有直接工作。下一步围绕空间误差下的任务收益/完整成本和公共场景外部比较。主要对照使用已发表作者方法，AR/lag2/RR/admission只作消融。以下§70及更早记录为历史阶段。

2026-09-29 三线更新（Q2 §70）：**主线进入真实物理历史回放；两支线已从单动作推进到完整任务；公开作者基线开始实际复现。** 后续分别以完整收费查询、任务目标对齐、替代论文底座为目标。已分别完成Astra独立技术判断和科研导师skill判断，按“一篇当前主稿＋一条可替代底座路线”组织，不以加入学习模块充当贡献。

主线四个隔离后继实现控制器直接构造、有理报文验证、精确有理/共享只读代数存储和整数规范检查去格式化。固定每行1,048,576供给下，C-business从有理验证后继54,769,862/54段降至42,568,936/42段（22.28%）；C row101实际877,185、余171,391。Natural/Strict均越过E控制器构造并进入历史回放，**仍在E row201耗尽，尚无POSITION/后车RUN/完整收据闭环**。原全链核账仍invalid；138+274项保存工件核验通过。详证本机`implementation_binding_evidence/NUMERIC_STORAGE_PROGRESS_20260929.md`；原稿已有修改保持。

查询线已完成六条件62次完整任务episode（558任务），实际AR(1)与lag2同效；准确预测在旧窗口目标下仍可能选出全程流时更差的动作。新后继完成98次任务运行/882任务，以当前已揭示任务流时为目标：慢AR/lag2由C→AB，全任务flow40→39、末服务14→13，同时多查询一次；部分快条件多查却无收益、隐藏突变误判保留。72次选择及旧62项结果独立复算通过；AR仍无超lag2增益。两次日志/分析失败回执保留，最终native均成功，另行离线恢复分析没有重跑native。路径线64组合/124完成任务表明，正常END下非零误差仍可影响路线等待，但同信息解析解释全部完成到达，没有已证学习残差。[查询结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/TEMPORAL_TASK_MODEL.md)、[路径结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/CONTINUATION_RESULTS_20260929.md)。

**论文主要基线必须来自已发表方法。** 完整作者PIE-D固定版本原码跑通100 robots×20步，52任务/2000动作独立核验；官方GPIBT原版及明确导出/seed适配跑通450步，并扩到两个作者工作负载×两个seed。OnlineGGO仅C++目标构建通过，学习策略评测仍待完成；LSMART有2 robots×200 ticks、3任务的闭环试运行，是试验台而非竞争算法。各运行设置不同，任务数不可横比。AR、lag2、解析、SRDC、RR、WAIT只列内部机制/消融。[设计与公平比较合同](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/RESEARCH_DESIGN_AND_BASELINES_20260929.md)、[作者工件报告](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/BASELINE_PREFLIGHT_20260929.md)。以下§69及更早文字为阶段历史，旧“只静态/两支线保持”不代表当前状态。

2026-09-29 主线进展（Q2 §69）：**网络费用封存已通过，查询推进到执行端的采样数值重建。** 原单行预算1,048,576下，Natural和Strict的N封存实际分别803,192和803,420，均有约24.5万步余量，随后发布及清理完成。实现将账本阶段根与不可变记录分离，避免无修改时反复深复制容器；差分检查与实际费用日志支持这一结论。

进一步去掉已校验请求的重复编码比较后，E已读完物理历史、释放采样pin并开始构造参考控制器；仍在原供给row201耗尽，尚未完成POSITION回传、后车继续和收据反馈。新增140项工件与费用核验通过，全链核账仍invalid。N转发查询费用也从185,103增至215,511，反向代价保留，不能写成整体查询加速或算法性能收益。

本轮解决了一个明确阻点，并将下一阻点定位到E的精确数值重建。接下来优先减少构造中的重复初始化/复制、继续打通完整查询，再接两探索分支的真实费用净收益比较。原输入、供给与主稿保持；Strict只切换宿主制度循环，实际guest相同。详见Q2 §69及本机`implementation_binding_evidence/LEDGER_CAPTURE_PROGRESS_20260929.md`。以下§68及更早内容按历史阶段阅读。

2026-09-24 当前决定（Q2 §67）：**主线先完成一笔真实、完整计费并可反馈的查询。** 它是后续比较查询策略净收益的共同基础。本轮集中推进请求往返、可信进度提交、受阻机器人继续执行，以及实际费用收据用于下一次选择；已有两个探索分支暂不扩展。先验拟合的组件效果仍成立，论文级收益需要接入这个共同执行与计费闭环后比较。下方§66及更早路线按历史阶段阅读。

本轮实测（Q2 §67）：C/N/E准备均已通过，完整C setup为20,402,877步；此前原窗口耗尽仍未完成准备。当前已执行请求编码、消息导出准备及中心发布准备，最终停在RootRecord校验的数值构造，首Selection仍耗尽1,048,576步。请求尚未交给N，Strict未启动，完整查询核账仍为invalid。下一步继续打通这条实际链；两支线本轮保持。

2026-09-24 实施进展（Q2 §66）：**数据拟合模型已接入决策，不再停留于离线分类。** 查询在有限连续任务中，从先前已交付END拟合时长，能在较快条件下省去一次查询并保持任务曲线；4376检查通过。路径先实测固定先验会选错路，再用合法历史尺度修复，实际到达5.750325→5.231320，3722检查通过。模型没有读取当前真实扰动。两线均与单END解析校准同效，所以目前可以主张历史适配的闭环机制，不能主张学习优于解析或论文级净吞吐。

主线实现两个隔离分配后继并重绑三ELF，合法first-fit差分通过；原固定窗口仍未完成首Geometry。最新分配两函数合计占setup37.37%，剩余几何构造与数值工作仍需定位；原合同、供给、生产实现及主稿保持。工程解堵与研究支线继续并行。下一研究重点是让历史与当前执行存在合法变化，检验简单校准的失效范围，再决定是否需要更强预测；接连续任务与真实费用，而不是先增加网络规模。下面§65及旧实测按阶段阅读。

2026-09-24 双评估后的推进决定（Q2 §65）：查询与真实连续任务服务作为主要论文候选，主线工程限时解堵，路径作为并行探索。相比上一方案，先试改动更小的合法活块跳跃扫描，EH尾部分区保留后备；两者均需明示新实现身份，原合同不暗改。完成导向不只优化已知实验截止前的短MOVE，下一项接真实任务完成与任务续接，检查滚动视窗、积压及等待年龄。学习可在首批有效日志后并行试探，不必等待两步非学习胜出。两份评估意见和根取舍已记录，本轮没有新增性能结果。

2026-09-24 最新结论：研究值得继续，但将改进集中到**有限查询如何帮助机器人更早实际完成动作/任务**。查询线首次对原SRDC/RR、同预测单步与两步规则逐次提交后立即执行，发现两步未胜过原策略，而完成排序随共同截止反转；因此下一候选直接估计完成价值，学习只辅助证据可用性与等待预测。路径线确认观察时机能改变路线优劣，下一项用原prefix与解析等待对照分离可利用的效果。有限结果与论文终点仍区分：本轮是原MOVE完成及预定路线到达，尚无lifelong净任务收益，见Q2 §64。

工程上已证明当前几何表示在原准备窗口不可负担：仅140次必需分配重扫异常池就至少86,517,760步，超过53,477,376步。继续少量复制微调无望闭合该窗口；已提出同总内存的异常池尾部分区后继，保持精确几何和安全规则，但需明确新实现身份并实测，尚未修改原实现。这解决的是验证平台的成本瓶颈，本身不作为查询方法创新。

定点文献更新覆盖3篇锚点和10篇近邻。付费状态感知已有[AISTATS 2026正式方法](https://proceedings.mlr.press/v300/kapoor26a.html)，因此论文应具体回答：空间误差下多个请求共享阻塞、证据会过时且查询有成本时，如何分配查询以改善共同预算下的真实完成。改进型方法具备合理研究空间，不要求另造世界模型；当前证据支持继续构造和比较，不支持预定期刊分区或宣称已实现性能提升。

上一轮实测（Q2 §63）：减少几何外层复制的隔离候选通过8954项原生差分检查，实际复测使首个Geometry的第三cell从供给行98提前到87、窗口末构造位置更深。这是局部推进改善；完整查询仍未通过，中心准备仍耗尽原53,477,376步，扫描占99.012240%。观察版与候选plain的92条业务记录逐字一致、86条费用段守恒。原生产实现保持，候选未作为完整修复合入。窄核验又发现当前冻结合同明确逐候选扫描，不能直接跳过占用块；当时的必要成本问题现已由§64回答。

同仓库已建立独立[误差相关路径引导分支](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/error-aware-guidance)。首检790项断言通过：同一足迹、资源和t=4观察机会下，零误差时上绕较快（6.928对8.363），双方误差盒半宽1/5时下绕较快（8.363对9.196）。这给“误差相关占用/等待代价可能值得用于择路”提供了具体存在见证，仍不是学习收益或LMAPF吞吐。先对照共同观察时机与几何间隙，再比较简单解析代价；只有学习产生独立且计入全部费用的增益，才升级论文贡献。人工证书/END和预定路线的范围已写入研究合同，不据此替换PIE-D主线。

支线真实组件预检通过530项断言，证明两个需求共享A/B责任的组合阻塞在给定足迹、非零误差包络和同原MOVE条件下可合法实现。两次相同查询机会下，AB/BA可组件准入2个需求，其余四顺序为1。它支持研究查询互补性，但只是人工native存在见证，未验证生产AUTH、完整费用、任务完成或学习策略。后继先把单步与有限前瞻决策分开比较，再固定决策器检验学习是否有独立收益；暂不更换PIE-D主线。后文原生机制结果仍保持原范围。

更新：2026-09-21。**现在可以向导师汇报问题、方法及首轮原生机制闭环结果。** 共同执行模型沿用固定73及[73R4](73R4_ROOT_DESIGN_ACCEPTANCE_20260914.md)，后继查询选择方法已收敛为 D_SRDC_v1，核心组件及六种选择规则已经实现。真实控制进度经过数值观测和POSITION提交，已实际释放阻塞资源并让后车继续，两原MOVE关闭。完整计费业务和规模性能仍待验证；[当前进度](GITHUB_PROGRESS.md)保留准确范围。

研究问题是：在持续接收任务的多机器人路径规划中，机器人具有实际尺寸，存在有界跟踪误差（逐分量有界盒，其横向分量无法通过时间重参数化消除），状态获取、规划和通信均有成本。如何在模型内保证碰撞安全，同时减少保守等待，提高固定时间内真正完成的任务数？当前结论限定固定朝向平移及已声明的有界扰动模型，实物验证为可选补充，大规模评价采用仿真。

研究明确基于Zhang等的[PIE-D，AAAI2025](https://ojs.aaai.org/index.php/AAAI/article/view/34506)框架改进。当前来源复用固定作者代码中的LaCAM路径提议与PIE切分流程，并说明必要共同修订。在共同安全执行适配层上，当前集中完成一项算法贡献：**由空间释放阈值、执行依赖和历史实际查询成本共同驱动的进度查询调度，并复用区间索引增量维护。** 完整PIE-D复现与共同适配层的比较身份分别记录，不把改过的内部组合称为原样PIE-D。

ECBS只是准备Hönig等2019外部对照时采用的规划组件；既定修复用于使比较可信，已完成的源码和静态编译包予以保留。当前不继续扩展ECBS工作，优先完成PIE-D误差执行主线。这里“处理误差”的具体含义是在误差存在时保证模型内安全并减少保守等待，当前不以降低定位误差或估计扰动作为算法贡献。结果留空的[论文正文初稿](MANUSCRIPT_PREEXPERIMENT.md)已按这一主线形成。

方法分为三个相连环节：用误差包络表示可能占据的空间；沿同一原规划动作授予前缀执行权限；在可以发布查询的机会，选择最有希望以较低成本取得有效释放证据的活动动作。查询完成并提交可信进度后，才释放可以确认离开的空间。预测仅用于选择查询对象。规划、查询、通信、索引维护和协调均消耗共同有限供给，其排队和处理影响真实任务完成数。

一个直观例子是：机器人A挡住三个请求，但预计尚未越过释放阈值；机器人B只挡住一个请求，却很可能已经离开所需区域，而且其进度查询较快、较便宜。单纯数阻塞关系可能优先查A；本方法结合阈值、依赖及报价，可以优先查B。这是说明选择逻辑的例子，实际优势需要实验检验。

设机器人i沿当前原边运动，u_i为起点、e_i为单位方向、s_i为参考进度、F为足迹。实际占据空间和跟踪误差为

\[
X_i(t)=\{u_i+s_i(t)e_i+z_i(t)\}\oplus F,
\qquad \dot z_i=-\kappa z_i+w_i(t).
\]

逐分量条件给出误差闭盒的不变性：

\[
|w_{i,d}(t)|\le\kappa\bar z_d,\qquad
|z_{i,d}(0)|\le\bar z_d
\quad\Longrightarrow\quad z_i(t)\in Z.
\]

这里⊕为闵可夫斯基和；不把参考进度单调误认为实际位置也单调。

待保留空间定义为

\[
\mathcal U_i(q_i,b_i)
=\{u_i+\sigma e_i:\sigma\in[q_i,b_i]\}\oplus F\oplus Z,
\qquad q_i\le s_i\le C_i\le b_i\le\ell_i.
\]

q_i为已确认可退休的进度下界，b_i为中心授予上界，C_i为本地已经安装的上界，ell_i为原边长度。保持X_i⊆U_i，并在授权时检查静态合法及不同机器人所占资源不冲突，构成安全归纳的基础。

若在t_j取得可信下界underline_s_{i,j}≤s_i(t_j)，则在同一原动作、证据身份有效且完成付费核验/提交时，可安全采用

\[
q_i^+=\max\{q_i,\underline s_{i,j}\}.
\]

参考进度单调保证该下界不会超过提交时的真实参考进度。这是“信息取得→空间释放→减少等待”的关键机制，实际收益还取决于信息成本、拥堵结构和服务机会。

查询算法进一步把每条“需求p被动作i阻塞”的关系变成严格释放阈值θ_pi：同一动作占据的相关阻塞资源必须全部清除，且原终点责任不能靠普通进度查询释放。预测下界严格大于θ_pi才计为预计消障，等于阈值仍保留边界接触。预测只使用已交付的历史进度；成本报价只来自已结算且兼容的实际查询收据。

令A_x为预计可以立即准入的加权需求数，P_x为完整阻塞关系的部分消障分数，需求权重包含一跳执行依赖；令ĉ_x为预计实际查询工作量、Δ̂_x为预计发布至可用提交的等待。按

\[
\left(\frac{A_x}{\widehat c_x\widehat\Delta_x},
      \frac{P_x}{\widehat c_x\widehat\Delta_x}\right)
\]

的字典序选择，再用确定规则解平；没有有效正分时回退稳定轮询。该分数是可实现的启发式，不预设全局最优。区间索引和反向依赖索引随实际提交事件更新，避免每次重建全部关系；动态预测与评分在选择时计算。必要分析已有严格阈值条件、预测与安全释放分离、增量结构与重建结构的条件等价。

POSITION证据提交后即可按原规则退休资源并继续MOVE；成本收据异步收齐后更新后续查询报价，不增加当前MOVE的等待前置条件。

最终评价真实任务完成数：令T^{service}_{i,j,π}为方法π下任务实例j满足真实实体服务条件的完成时刻，未完成记为无穷大，在共同固定截止E比较

\[
Q_\pi(E)=\sum_{i,j}\mathbf1\{T^{\mathrm{service}}_{i,j,\pi}\le E\},
\qquad
\Delta Q(E)=Q_{D\text{-}S}(E)-Q_{R\text{-}S}(E).
\]

上式保留既定D-S/R-S正式比较的定义。后继SRDC按独立候选登记，在相同观测、释放和计费协议下，与稳定轮询RR、阻塞计数COUNT比较；分别去掉等待因素、工作量因素或一跳依赖权重，检查每个设计的作用。这些规则已经实现，后继候选不暗中替换冻结D或已有正式臂。

跨不同预定block比较时，按固定E_b归一化，再按预注册权重w_b合成服务率差；不能直接混加不同窗口的原始任务数，也不按结果改变权重。E0及外部PIE-D/Hönig等2019方法按各自已声明的共同域比较。除真实任务完成率外，报告等待、全部计算与通信开销、扩展性和失败；不会只展示预测释放量或删除未完成运行。

数学工具主要是不变集与微分方程、凸几何和集合运算、执行依赖图、增量索引、安全归纳及配对统计分析。当前剩余工作集中于完整业务接通、必要的小规模联合验证、既定输入和参数绑定，再开展大规模仿真。导师汇报可以明确提出问题、方法和验证假设，性能提升留待实验回答；无需等待全部工程完成才讨论研究价值。

2026-09-21的最小原生场景中，后车先受阻且静止；查询前车实际快照后，认证进度从0推进到2，释放两个资源单元，后车获得授权并RUN，最终两原MOVE都到达原终点。非零足迹和误差盒实际参与几何计算。此时无真实查询报价，SRDC按既定规则轮询，结果支持进度查询与空间释放的实现接通，尚不说明SRDC优于轮询。

另一路费用反馈诊断将真实B1负载的21/56/7步经账本、codec及收据算术反馈，下一选择由A转B；它只计指定B1负载，没有覆盖原生选择器、账本等开销和完整站点准入。下一步把完整查询费用链接上，再与RR/COUNT比较计入全部开销后的服务率和等待。已有检查直接复用；大规模实验再回答扩展性与稳定收益。
