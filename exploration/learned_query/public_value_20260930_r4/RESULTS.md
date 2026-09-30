# R4：查询边际任务价值的真实训练与原生留出闭环

**本轮已经训练、导出并实际运行ridge查询价值模型；它相对WAIT略有改善，但没有超过强简单规则。** 首次B1的两个测试cohort全部策略均完成104/104 head；模型减少流时约2.9172，RR/方向经验率/task_rank/公开结构规则均减少约7.0013。没有用留出改特征、lambda、阈值、seed或选题支持域；负收益与失败诊断保留。该结果支持实现/信息合同闭环，不支持独立模型性能优势或论文创新完成。

## 新公开源、完整任务组隔离

R3父154冻结文件不变，R3任务14/22/99/118不参与训练或测试。旧100×20源排除这些head后无符合两候选连通条件的新任务组，因此按事前 `SOURCE_REGISTRATION_20260930_r4.json` 原样运行作者PIE-D `74cfba3c81a0c165c2e7044dea6fd4dee8ddf415` 的已安装官方binary、同random100输入，仅将公开执行延长至60tick。原命令/输入/binary SHA、stdout/stderr/log保留，61.166秒返回0；206个源任务完成和6000个源动作经过全量独立FIFO/地图/vertex/edge核验。未使用作者driver已知未初始化聚合summary作为指标。

源SHA为 `7bea881c981223b84e971835ff03a589c7570b126dcc7c5823b700cd45f7bf97`。按最早tick/source次序、四当前已revealed head路径≤16项、两源初始合法follow、路径连通规则抽到57唯一task groups；贪婪接受互不共享task ID的12个cohort，共48个不同head。事前mod5固定8训练/2校准/2测试，测试是cohort_04/cohort_09，和训练/校准没有task组重叠。仍单map、单新source trace，机器人/地图背景可共享；不能叫跨地图泛化或把26扰动世界称26独立几何。

每cohort四机器人真正共享Geometry/Index/PositionCommit/时间，不是独立crop相加；只执行四当前head公开给定计划，不补未来task，resident/失败/死锁/截止保持。它是公共来源局部R1、内部方法探索，不是原100机器人在线PIE-D、不重演原离散delay benchmark，也没有构造新的“外部baseline”。

## 真训练→导出→原生选择→真实服务

每cohort13固定世界：8独立方向IID seeds（训练1001–1008，校准2001–2008，测试3001–3008，SHA含cohort/agent/leg），首两源eta±1完整四角，及eta0；相同世界所有臂共享private E。完整cohort是划分单位。真实反事实实跑WAIT/问首源A/问首源B，y为WAIT受限flow之和减查询后实际受限flow之和；future用于离线标签，未进入actor。deadline64、每head原MOVE到goal/rest真实服务，未完成取64。

唯一模型是固定lambda1、10个预注册公开特征、截距不惩罚的ridge closed-form；只fit8训练组208条候选标签，校准52条和测试52条不参与fit/超参/标准化/选择。无data-dependent标准化，特征尺度在合同固定。11个系数以1e-9舍入后的有理数导出，原生EndOnlyActor精确算分数，最高正预测值查询，否则WAIT。模型公开副本 `MODEL.json` 与实际冻结文件相同SHA `70df421875fe3c68d8c16b792a22709295b1708abf0d9128c68f8b3c0ae17131`；原训练行bindings、完整参数与numpy系数均保留。

特征仅使用公开已交付END方向p、当前head剩余路线、阻塞关系数、公开路径交汇、其他head终点驻留侵入/索引与服务链。完整顺序在 `MODEL_FEATURE_SCHEMA.json`，原代码 `joint_value_native.cpp`；native计算不用eta/regime/未来task/当前progress。真实Controller只有被选查询进入证书提交；其它Controller运动也按正常世界时序运行。严格lower>13/20才退休，等阈保留，不重复减epsilon，endpoint保持resident，正常END+1/4→READY。

**本世界首次选择在0.75，尚无任何本世界正常END交付。** p完全来自父包两旧训练run的3582公开END，不能称在线适应了本世界执行速度。独立hardening验证每cohort同13外生世界的首次特征和同策略选择完全相同；模型实际学习的是静态公开结构条件期望，而非此世界已发生执行残差的决策价值。

## 全部留出结果

流时为26完整测试世界各四head实际服务时间之和，以下显示六位小数来自独立70位Decimal闭式时钟重建；全native有理包围区间和逐世界明细保留，显示精度不是统计置信度。native合计区间宽26e-6以内，root midpoint汇总与此值数微单位差异均在包围区间内。

| 策略 | 完成head | 查询数 | 流时总和 | 相对WAIT减少 | 额外head |
|---|---:|---:|---:|---:|---:|
| WAIT | 104/104 | 0 | 2063.299168 | 0 | 0 |
| RR | 104/104 | 26 | 2056.297865 | 7.001303 | 0 |
| 方向经验概率 | 104/104 | 26 | 2056.297865 | 7.001303 | 0 |
| task_rank | 104/104 | 26 | 2056.297865 | 7.001303 | 0 |
| 公开结构规则 | 104/104 | 26 | 2056.297865 | 7.001303 | 0 |
| ridge价值模型 | 104/104 | 26 | 2060.381959 | 2.917209 | 0 |

cohort_04模型收益1.750325、强规则1.166884；cohort_09模型1.166884、强规则5.834419。不能只展示第一组的模型优势、遗漏第二组；合计模型弱于全部强规则约4.084093。模型的训练/校准/测试候选回归RMSE分别0.543790/0.277416/0.326211，预测误差不能代替实际任务收益。

训练候选有6个真实负收益，范围最低-3.833116，全部保留；测试候选收益范围0至1.166884，无额外head任务完成。测试13世界含人工四角/eta0和8IID实例，总和仅描述这组固定混合，不能假设它等于实际扰动概率分布。所有逐世界、cohort和候选预测表在 `HELDOUT_ALL_WORLDS.csv`、`HELDOUT_BY_COHORT.csv`、`ALL_COUNTERFACTUAL_PREDICTIONS.csv`，完整汇总 `RESULTS.json`；没有统计显著性/泛化宣称。

从实际WAIT/两首源反事实事后取最小，测试总流时约2054.547540；这是当前**首次B1已记录动作族的hindsight最好值**，不可实施、不是正式baseline，更不是全局理论最优。它相对WAIT可改善仅约0.4242%；RR距它约0.0851%的RR流时。14/26世界有任一查询正收益，12/26世界两候选有可分辨价值差（严格Decimal相等的1e-68舍入残差不算机制差异）。当前支持域的可改进空间很小，堆更大网络不是本数据所支持的下一步。

## 执行、审计与失败保留

首次严格g++-11构建通过，二进制SHA `6ba89da478023eb23f94f571c1fa4d6ee9e277865c3cc3fa5260464f99964363`。完成598个成功原生臂：原串行126个成功receipt按input/raw SHA复用，纯调度后继10独立world并行执行472新臂；模型必须全部train/cal完成才冻结，test随后运行。原pipeline/合同/source/binary/inputs未变。原串行unified exec一次Ctrl-C退出130，在途没有可认证完整capture；事实登记 `SCHEDULER_INTERRUPTION.json`，不伪造成功/隐藏终止，不重复成功native。宿主秒只说明调度限额，不当方法代价。

合计23738实际MOVE、23738正常END反馈、71915共同frame、442证书查询。`AUDIT.json` 从6000官方源动作/206源task、12合法cohort到全部native，独立Decimal公式/最早事件、闭矩形足迹、lease授权/退休/resident、正常END/READY、真实task、公开特征、有理模型选择和train-only refit核验passed，5项真实raw篡改拒绝。`AUDIT_HARDENED.json`另核598 actual input的公共C/R/H、私有E与测试M参数完整绑定，24个cohort/source首次公共特征、没有本world END提前进入actor、同组13世界首次选择一致；154父文件与9生产头字节不变。

独立audit前两次失败均保留source/raw/receipt：第一次继承R3错误固定19资源格，改为cohort全union核验；第二次独立70位Decimal WAIT终点直接==产生1e-68舍入差，改用既有1e-60解析核验界。第三次全部通过。这两修复不改native、标签、训练、测试选择或原精确时钟。训练原生过程没有因结果调参重跑。

生产AUTH/网络/完整COST以及正式外部共同误差环境仍未闭合；这里B1只算查询数量。当前计划离线源出自作者轨迹、当前head给定，不承担完整在线持续任务生成/规划的benchmark结论。

## 结论与下一最高价值实验

本轮目标已完成：真实反事实标签、真正train-only训练、有理参数导出、原生模型选择与共同物理任务服务全部闭环。模型弱于强规则的结果完整保留，尚不进入主稿核心性能贡献。

下一应在独立新任务流中把选择放到已经获得至少一个正常交付END/执行残差的后续机会，并持续公开释放新任务，固定多决策查询预算及正常服务/占用；比较同架构加入/去掉误差历史以及强结构/概率规则，从而识别误差信息本身的价值。不能在这两个测试cohort上改网络/换奖励，不能只用永久head驻留死锁当lifelong吞吐收益，也不必等所有传统规则失败才训练。

近邻不可回避：[DCC](https://arxiv.org/abs/2109.05413)已学选择通信；[Should I Replan?](https://arxiv.org/html/2604.25567v1)已用历史/依赖特征与同世界SOC差回归重规划价值；[REMAP v2](https://arxiv.org/abs/2511.21886v2)含逐动作时间/末运动学态预测、ESADG与Bayesian gating付代价调用预测器。本文不宣称首次历史图回归价值、世界模型或有成本信息选择；差异候选限定真实机器人进度证据查询、连续原MOVE空间证书退休/占用和任务驻留传播。REMAP作者代码据其文稿仍待录用后公开，不假称获得作者实现。正式外部比较与最终论文定位由root另核。

原始local保持；`RAW_NATIVE_RECEIPTS.tar.gz`压缩包含原生jsonl/input/receipt、官方源/log/命令、调度和审计失败材料，逐文件hash见 `RAW_ARCHIVE_MANIFEST.json`。公开正文保留代码/真实模型/全表/审计/manifest，不需要把数百重复raw单文件提交Git。首运行入口pipeline.py；实际成功调度后继scheduler_successor.py；目录拒绝覆盖已有尝试。冻结后复核应在兄弟目录或另定新输出，不覆盖旧结果。
