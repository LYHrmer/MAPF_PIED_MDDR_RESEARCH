# R7：作者在线联合规划、持续 FIFO 与查询模型留出

R7 已修正 R6 的静态轨迹裁剪与第三任务后停车接口。60 个有效原生运行全部达到128时间单位，零死锁、零观测到的官方长环；持续补充任务、原始 MOVE、真实服务、公开 END、查询证书和模型评分形成了可重放链路。历史模型仍未取得任务收益：20 个留出臂中，四个world合计 WAIT/无历史180任务，RR/条件规则179任务，历史模型178任务。查询更少不能抵消少完成的任务。

## 实质接口变化与边界

使用现存、未修改的 OnlineGGO 官方 OBJ3 MAPFPlanner 对象、持久 bridge 和固定配置，不重写规划基线。每个运行有独立的 planner 进程。planner 输入是**公开已承诺路径的末端 frontier**，不是声称已测量到的机器人当前位置；当前 FIFO head 来自真实服务与正常 END。最多4个 MOVE 的已承诺前瞻，保留官方每个联合步的顶点/对向交换合法性和逐 cell 访问顺序。进入一个 cell 的 MOVE 先等待该 cell 上个访问者的离开 MOVE 已启动，再通过原精确 Geometry/Index/PositionCommit 的完整 swept-mask 资源门。

物理执行不设全队 END 屏障。7163次规划调用中6364次发生时仍有物理 MOVE 在途；56174次 RUN 发生时另一机器人仍在运动。256次 POSITION 中239次在被查 MOVE 物理 END 前、17次在物理 END 与正常 END 之间，144次源资源释放后同一时刻启动后继 RUN。因此查询机会没有被适配器整体清空。保留原 full-cap ReferenceController：unit MOVE 原始 END 约1.083441/1.292893/1.732051，正常 END 再延迟1/4；当前位置只经被选 POSITION 返回，actor 不能读取离线物理帧。

每agent有事前固定256项私有 FIFO 储备，前一目标真实到达且静止、正常 END 交付后才公开下一项。frontier已到目标而实际尚未服务时，官方planner继续看到旧head；不会用未来head催动。全部运行未耗尽储备。公开16-agent机械 WAIT 完成52项，单agent最高6项；所有正式train/cal/test WAIT world都有agent完成第4项，旧第三任务停车不存在。

这是公开 empty-32-32 地图上的作者在线 planner **frontier适配器**与精确连续执行 pilot，不是原作者物理当前位置调用约定的完整benchmark复现。机械2/4-agent用8x8构造；机械8/16和正式16-agent用公开地图、scenario起点以及注册seed生成的FIFO目标，不冒充作者原任务流。官方允许的同步长环可能无法在独占 full-sweep 资源门下启动；协议保留此类失败、不换自制planner，本次60臂未观测到长环，不等于证明适配器完整。

## 先注册、真拟合、冻结后留出

3个新完整训练run与1校准run，起点scenario行组及任务/噪声seed均在运行前固定。train/cal WAIT各出现12/3/4/11个多候选机会，最大候选数3/2/2/3。依预定公开基数规则取每run最早2个单候选机会和最早2个多候选机会，覆盖16个机会的**全部24个候选**：18训练、6校准。没有按查询收益筛选；未选机会与所有零/负结果均在raw中。

每个候选执行真实单次query后WAIT至终点，并与全WAIT核对查询前完整物理/公开前缀。私有误差按注册的(seed,agent,实际MOVE序号)固定，9:1持久符号；SHIFT从序号64翻转，配对IID/SHIFT保持相同任务和噪声抽样。目标是全run任务完成差，加同一组初始每agent前4项FIFO的受限绝对完成时间差除以128×16×4；未完成固定任务计128。此平滑项仅用于离线标注，不进入actor，也不伪装动态released-flow。24标签为20零、3正、1负；唯一负项让完成数44降至43。

同20公共特征/21系数ridge，lambda1、截距不惩罚、系数舍入1e−9。结构特征现表示当前已承诺前瞻前缀，不是完整静态到goal路径。history与nohistory共享行、标签、架构与容量，nohistory仅将10..17历史槽置零；两份权重都实际拟合并在原生执行中评分。校准不选模型/阈值：history/nohistory RMSE分别0.206526/0.131345，单位为注册标签。模型冻结SHA为 `5cb3fdef0cf16b85986c7075cf21849d8d8ac4f4118ead08c97baaee153f7cb7`，之后才启动2个新完整task-run×IID/SHIFT×5方法的20留出臂。

## 留出结果

每world16agent、H128；所有非WAIT策略容量同为16查询单位，实际费用单列。RR是真循环规则；condition使用同公开END历史、同声明误差law与条件生存概率，是内部同信息规则对照，不是发表SOTA方法。

|方法|IID任务（2world）|SHIFT任务（2world）|四world查询|早释放源资源|
|---|---:|---:|---:|---:|
|WAIT|90|90|0|0|
|RR|89|90|64|34|
|condition|89|90|64|34|
|ridge_history|89|89|14|6|
|ridge_nohistory|90|90|0|0|

每agent前4项固定FIFO受限完成时间和，IID/SHIFT分别为：WAIT与nohistory11323.583970/11327.475624；RR与condition11310.393429/11314.422557；history11318.456187/11322.895058。更早完成这一有限固定前缀与全run少完成任务可同时发生，不能把次指标改善代替主服务收益。动态已公开head的删失时间和另存在原始summary，释放集合可随策略变化，不用于伪造共同固定任务比較。

history在留出真实评分363候选，其中14个正分并提交14query；nohistory评分296候选，分数全部非正，实际选择WAIT。不是未加载模型。history/nohistory分别遇到12/16个仍有预算的多候选机会，均选择不查询；训练probe确实覆盖并执行了多候选中的每个候选，但不能声称部署模型已经学会了有益的多source排序。RR/condition的留出执行没有多候选事件，这一变化和实际预算消耗完整报告。

机械阶段仅用于接口验证：2-agent WAIT/RR/condition任务20/22/22，4-agent46/50/50，8-agent18/18/18，16-agent52/52/52。机械局部增益不能转写成独立留出的学习优势。正式测试只有2个独立task-run家族、共享地图，IID/SHIFT配对相关；18训练标签也不是18独立world，不做跨图或总体显著性宣称。

## 核验、失败与归档

独立70位Decimal控制器与闭矩形几何、官方action重建的cell访问依赖、真实服务/END/FIFO、owner/Index关系、候选全集、20特征及有理policy分数/选择全量通过：60臂、56536 MOVE、55868物理END、55755交付END、75543帧、256query。公共机会census为31016零候选、3438单候选、281多候选。8个futurehead/依赖/服务/证书/END时间/historyfeature/漏候选/预算负控全部拒绝。

独立有理正规方程重拟合与离线label重算通过；root另有不导入pipeline/runner/audit的24label、完整前缀、首2single+首2multi选择与增广lstsq审计，见ROOT_LABEL_AUDIT。模型实现正确和模型性能良好是两件事，本轮只证明前者。

首机械attempt01的12次输入因task ID超32位而被原生解析拒绝；仅修正输入ID尺度后运行attempt02，全部旧失败input/receipt/raw保留。R6冻结240文件、9生产头逐字未变。POSITION沿用现有admitted exact-native source，不声称生产AUTH；查询费只有计数，不声称已闭合货币COST或硬件通信费用。原始档案单份压缩、逐成员SHA核验，展开raw和缓存不进入发布成员。

本轮完成了持续在线FIFO与合法异步查询接口修正，也暴露出新的有效负证据：在当前小样本与固定架构下，引入历史没有增加任务完成。后续工作应使用新的训练/留出run检验价值标注、预算分配和前瞻约束，不能继续利用这两个测试家族挑策略或宣称历史已获益。
