# R4 运行前合同：首次证书查询的边际任务价值训练

用户已授权隔离实现。本包直接父 R3 的154冻结文件与9生产头不改，不修改旧README/主稿，不提交/推送。R3七世界不用于任何权重训练或测试；其四任务14/22/99/118全部排除。

## 源与冻结划分

老100×20作者trace排除R3任务后没有新的两候选/连通四head组，因此按SOURCE_REGISTRATION事前规则实跑原PIE-D 74cfba3完整作者runner、同random100输入、60tick，无源码/配置/binary修改。真实返回0、61.166秒、206源任务服务。原stdout未初始化聚合量不用；source任务/动作全量另核。源SHA7bea881c981223b84e971835ff03a589c7570b126dcc7c5823b700cd45f7bf97。

源只按公开计划/任务语义抽取：两同时合法follow、四机器人不同、两源第一格可启动、当前head完整源完成路径≤16项、路径交集连通；按最早tick/source顺序、首次task-group登记，再贪婪接受任务ID完全互不重叠cohort。57候选task groups得到12cohorts（48不同head）；已固定序号mod5的8训练/2校准/2测试。全部仍单map单新trace，机器人身份/地图背景可能共享，不能叫跨地图留出。每cohort四实体真正共享Geometry/Index/PositionCommit，不把crop拼全局。仅执行当前已揭示head，未来task不补；给定当前head计划来自作者源，非在线原PIE-D重新规划比较。

每组13世界：8个IID seeds（训练1001–1008/校准2001–2008/测试3001–3008），每leg独立SHA(seed,cohortID,agent,leg)，NO/SO eta=-1概率9/10、EA/WE eta=+1概率9/10，其余相反；另外全eta0与两个首源±1完整四角，其他leg eta0。相同世界各臂共用E列表，不向actor送condition/eta。每组split由整个task-group决定，不按episode/动作行混切；13干预世界不是13个独立几何。

## 单一扩展与学习合同

沿用R3真实ReferenceController/正常END+1/4、公开END-only支持域、闭资源责任及严格lower>13/20，未知profile仍UNKNOWN，安全证书/身份不由模型猜。本次明确只在首个公开launch+3/4机会选择一次B1或WAIT，之后不查询，截止64；各任务真实goal/原END/rest服务，resident/死锁/未完成按64删失。B1是数量预算，未称生产COST。

离线反事实每世界实跑WAIT、问首源A、问首源B，均真实改变同一共享状态；标签y=WAIT四head受限流时之和 - 问此源的受限流时之和。任务完成数另列主要运行指标，不合成事后奖励。未来服务/轨迹允许用于离线标签，不能进入actor特征。校准/测试标签不参与fit；训练冻结后再生成/评估测试。

10维特征来自已交付END方向经验概率和当前公共head计划/责任图：p、被阻head数/3、剩余路线项之和/16、剩余路线倒数之和、阻塞责任数之和/3、被阻路线与其他当前head剩余路线交汇数/64、其他head终点侵入该路线数/3、首终点侵入索引之和/16、侵入终点head剩余路线之和/16、被阻head终点侵入其他head路线数/3。当前head路线/软件RUN cursor公开；物理progress/x更新、未来END、eta、未来task、source condition不进入features。所有组首决策时刻均无本世界正常END先交付，初始历史为冻结父R2的3582条训练run公开END。行为目标/特征不声称新领域首次。

唯一模型为带截距ridge：固定尺度，无data-dependent标准化，lambda=1，仅10特征系数L2惩罚，截距不惩罚；训练closed-form solve，参数导出为1e-9四舍五入后的有理数。原生actor读真实11系数，精确算分数；选最大正预测y候选，非正则WAIT，平分按机器人号。不试其他模型/超参，不用留出挑lambda/feature/阈值，不按收益重选cohort/seed。校准只报告误差/排序，不调模型。

强内部对照同B1：RR最小源号；probability最大END方向p；task_rank最大p×当前head倒数/owner关系数；structural按当前公共终点侵入数、路线交汇数、p×路线倒数词典序（原生用固定尺度1000000/1000等价编码，候选最多3个head/路径≤16）排序；WAIT B0。它们均内部消融/诊断，不叫外部发表baseline。模型预测误差以世界内候选为记录、cohort为泛化单位，测试主表报告每cohort四head完成/受限流时/真实查询/相对WAIT和强规则差，所有无效/负收益/死锁保留。根组另处理正式已发表共同执行对照。

阶段顺序：先固定源码/输入/split/hash并编译；训练+校准反事实实际采集；train-only fit→导出/冻结模型；随后测试反事实+六臂真实原生运行。编译120s，单native90s，完整失败源码/receipt保留，可纠明显接口bug但不得看测试后改收益规则。独立audit复算6000源动作/FIFO、各cohort合法支持、所有native精确物理事件/责任/END/任务、公开特征/有理权重选择、fit只train与split不重叠，保留负控。宿主秒数仅执行限额，不写方法代价。

近邻界限：DCC (arXiv2109.05413)已研究选择通信；Should I Replan? (arXiv2604.25567)已有历史/依赖特征和同世界反事实SOC差回归。这里不宣称首次历史图回归边际收益；探索差异限定有限真实证书查询、连续原MOVE空间退休/保持占用和当前任务驻留传播。最终新贡献与泛化是否成立由测试/外部比较决定。
