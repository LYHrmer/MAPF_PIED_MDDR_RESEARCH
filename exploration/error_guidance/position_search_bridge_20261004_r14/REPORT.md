# R14：POSITION 到原作者搜索视图的真实接线与工作复用

已实现 `public_base / separately verified evidence / search_view`，并将一次当前位置测量导致的整数残余权重变化真正送入未改的原作者 GSES。12 个已冻结 R13 checkpoint 中，2 个目标进度估计改变、1 个搜索图改变；只新增 **1 次 GSES 调用**。该调用返回的依赖方向与既有结果一致，恢复真实执行权重后的完整图不变，所以 **0 次新增物理续跑**，36 个 keep/public/position 结果引用全部复用已有 R13 完整轨迹。POSITION 相对公开视图的完成时间和与 makespan 差均为零。

这是一项有明确零结果的接口机制试验。它证明测量可经过独立核验影响真实作者输入，也定位了本批次中的取整与候选不敏感性；不证明有价信息收益，更没有训练模型或增加新的统计留出。

## 本轮具体完成了什么

保持两份原作者完整实例、两个时点 1/2 与5/2、三个原 R13 profile，共12个固定上下文。每个上下文只按公共规则选择一个 active MOVE：其下一次实际 ARRIVE 可满足的未满足 type2 依赖数量最多者；同分按 agent/from_state 升序。没有观察测量后换目标，没有同时免费获取所有 agent 位置，也没有追加 Improved GSES 或原图物理控制运行。

公开视图保留 R13 的实际到达状态、phase、占用与承诺，并增加事前白名单内已经发生的 MOVE_START、CELL_ENTER/EXIT 等事件。排除包含私有暂停时长的 HALF_END、heap、未来段和 profile。对于 active MOVE，公开占用给出进度区间；若已发生 ENTER/EXIT，用最近公开 landmark 的起点平均速度外推，否则用名义速度1，再投影到当前公开区间。查询视图仅把已选目标的估计进度换成测量进度，其余估计完全相同。

两视图共用 `residual = age × (1−alpha) / alpha`，age或alpha为零时退回名义1；当前 active type1 采用 `max(1, ceil(residual))`。该式是固定平均速度外推，不是未来速度、暂停或真实 ETA 的保证。非active当前边保持 R13 的已知初始等待/其余单位合同，未来边仍1；没有仅对某一策略加 TURN/STATION。POSITION 不推进 `current`，不能替代 ARRIVE、改变资源释放或修改已承诺动作。

`measurement.py` 是单独的模拟测量源，只在请求时点从已存连续段插值得到一个当前点；输出不含未来时刻、速度或暂停。`bridge.py` 消费者只接收限制字段的 body 与受信本地签发收据，核对完整 agent/occurrence/几何/时间、公开区间和位置—进度一致性，再产生搜索视图。收据是内容与来源绑定，不冒充生产密码学认证或恶意issuer安全证明。测量来源明确为 `synthetic_position_measurement`，`production_cost=null`，12是请求次数，不是12次主线guest收费。

作者 candidate 先对实际 search_view 核验路径/current/type1/关系族和无环性，再恢复原搜索type1，调用未改的 R13 guard/lift。实际完整执行图保留原type1、实际ARRIVE、已满足方向和active incoming。新搜索权重始终只作排序估计，从不替代真实物理时长。源码与字段见 [SCHEMA](SCHEMA.md)、[冻结协议](PROTOCOL.md)和[来源/复用说明](SOURCE_AND_REUSE.md)。

## 输入敏感性及实际作者结果

|原上下文/选中agent|公开alpha → 测量alpha|残余估计|ceil权重|后果|
|---|---|---|---|---|
|random，1/2，axis_slow，agent14|2/5 → 1/3|3/4 → 1|1 → 1|进度增量被整数接口抹平；复用作者调用|
|warehouse，1/2，axis_slow，agent2|1/4 → 1/6|3/4 → 5/4|1 → 2|真实新增GSES调用；最终依赖方向与原结果相同|
|其余10个固定上下文|一致|一致|一致|复用作者调用与完整轨迹|

完整12行包括目标的公共criticality、原始有理数、图/结果差，见 [SENSITIVITY.csv](SENSITIVITY.csv)。唯一变化的 warehouse 目标从 t=1/4 启动，到checkpoint t=1/2年龄为1/4；它由7条未满足释放依赖事前选出。新调用在冻结的16秒作者预算/25秒host期限内成功，作者search为1.098750秒，host记录1.268987236秒。求解阶段仍冻结虚拟时间，未把该host延迟当成物理轨迹中的停顿或净实时开销。

新reply携带权重2，因此其完整搜索图与旧图有差别；type2方向却没有变化。lift后的真实执行图正好匹配旧 GSES continuation，完成时间和为83311/4=20827.75、makespan为775/2=387.5。相对公共GSES均零变化。这些数值来自已发布原完整轨迹的内容复用，不是本轮重跑；候选图“有变化”若仅指type1搜索权重，不能被写成执行策略改变。

12个公开估计图本身均与对应 R13 作者输入相同。24个公共/测量调用请求共9个唯一solver键：8个键来自旧成功调用，1个新键。23个请求引用旧结果；新键只执行1次。既有同键多份reply的selected_graph一致，无需处理不确定选择；协议已固定若以后发生分歧只取最早成功收据并披露，不按物理效果择优。

所有12个position与public的实际完整执行图相同；ΣT和makespan的12个配对差均精确为0。旧GSES相对keep的正负效果仍是R13结果，不能重复计为本轮新增样本、额外优化收益或新增安全运行数。

## 去重、恢复与证据

solver键绑定规范化完整输入图、GSES方法、全部配置、binary、adapter及作者源码hash，忽略不被solver消费的外围metadata。新 `FIRST_ATTEMPT` 在进程开始前写入；成功同键必须复用，未完成尝试保留并停止，失败不能被悄悄覆盖重试。原作者源码及R13 executable逐字保持。

continuation键更严格：完整私有checkpoint的压缩SHA、实际采用的完整图、executor/guard源码及语义。它不会把公开图相同而隐藏profile不同的世界混用。keep与candidate共36条记录全部引用旧R13轨迹；原timestamps和packed/raw SHA保持，未包装成36次新执行。[RESULTS](RESULTS.json)逐行列出调用/视图/证据/guard/实际图和轨迹来源，[REUSED_MEMBERS](REUSED_MEMBERS.json)列104项外部冻结依赖。

第二次运行 orchestration 作为resume机械检查，已有调用的input/reply/receipt/stdout/stderr和RESULTS逐字不变，新调用数与新continuation数均为0，见 [RESUME_CHECK](RESUME_CHECK.json)。它只读取/校验并复用已完成行，不重启原作者求解器或物理执行器。

[机械控制](MECHANICS.json)4项正检查、9项故意破坏拒绝：精确残余/ceil、搜索权重恢复、隐藏profile/heap/严格未来段不影响当前输入、规范图键；body改写、错agent、错occurrence、错时点、主线证书跨域、额外ARRIVE能力字段、无证据修改搜索权重、POSITION提升实际ARRIVE和真实active incoming反转均被拒绝。其中错身份控制有重新绑定内容的畸形本地签发体，故并非全部只靠body哈希失配拒绝。没有额外科学case或solver负控运行。

root未导入候选实现，独立重建12个公开目标/估计/模拟点位，以及36条作者input/reply、lift/active guard、费用null和复用来源，全部通过。36条记录对应24条唯一旧轨迹，其packed SHA与R13独立资源/连续几何审计绑定，0新增物理重放。见[独立视图核验](../r14_root_review/ROOT_VIEW_AUDIT.json)、[独立结果核验](../r14_root_review/ROOT_RESULT_AUDIT.json)与本包[ROOT_AUDIT_BINDING](ROOT_AUDIT_BINDING.json)。本报告不把自身机械检查说成独立验证，也不把复用几何审计计作新运行。

## 研究判断与范围

本轮选择合同的边际执行标签全为零，因此此刻训练“是否买POSITION再GSES”的模型没有实测价值目标；不因想激活模型而改目标agent、去掉ceil或购买所有agent。它也不证明一般POSITION无用：只覆盖两个旧实例、12个固定上下文、一个公开购买规则和一个有意简化的残余估计。应把两个不同原因分开：一个增量在整数化前被抹平，另一个确实改变作者权重却没有改变合法依赖选择。

当前仅固定中心线圆盘、持续时间/暂停误差与单次固定路径后缀图；没有非零横向轨迹、原主线Z控制器统一、持续任务LMAPF、真实证书与本几何的共同world安装，也没有生产费用净收益。主线的真实POSITION body捕获属于另一来源/执行域，不能复制到本目录冒充已经打通统一控制器。

下一步应根据这一接口边界决定是否有可公开、可验证且能改变合法候选的新问题；任何更细权重、时间风险规则或证据权限改变都需新的协议及正确性检查。完成旧结果的可复用桥接是真实工程推进，当前有限结果不支持把购买价值学习或新算法性能作为论文结论。

## 科研导师的下一步判断

本轮应停在这个完整零结果，保留从测量、整数化、作者候选到执行后果的证据链。它已经说明：有更准的当前位置不自动意味着有更好的合法后缀。下一步优先补真实主线证书与第三线几何、occurrence和预算的共同合同，明确新增的是信息精度还是认证权限；当前两个来源不能只靠字段相似就拼接。若仍以残余时间改变作者评分，应先说明整数接口能表达什么，再为更细权重建立正确性依据，不直接改成float。随后只在一个事前可解释、可合法出现决策差异的新机制范围内验证，旧12条件继续封存并按内容键复用。查询线已有完整尾标签可用于诊断任务风险与时间次项的决策作用；只有完整干预后果出现可泛化差异，再训练选择模型。现阶段增加网络、重复旧模拟或以接口数量替代作者基线，都不会补足论文贡献。
