# 空间误差约束下的路径引导探索

2026-10-03 R11：[真实作者图的共同primitive执行](gses_primitive_20261003_r11/REPORT.md)完成27项验证。16项单位模式逐时刻复现作者原图/GSES/Improved，另外9项random60 primitive与2项lak41真实超时原图回退均完成；43作者源不变，未新跑优化器。分段线性事件层不是原ARGoS控制器；独立根审覆盖239,222 MOVE、523,274连续段和全部资源/前驱条件。

random60三条件均出现完工时间和改善而makespan变差，不能称整体支配。实际半MOVE checkpoint同图恢复逐事件一致、非法承诺反转被拒绝；尚未在执行中采用不同图。本轮未训练新模型，也未把旧时长ridge重新列为核心收益。[三线实绩与两份判断](THREE_ROUTE_POSTUPDATE_20261003_R11.md)、[下一方法合同](NEXT_METHOD_CONTRACT_20261003_R11.md)已给出：先合法异图采用及真实控制器/信息接口，再检验模型的完整任务价值，并与执行预测和重规划门控近邻明确区分。以下R10及更早为历史。

2026-10-03 R10：[几何/历史归因64臂](geometry_history_20261003_r10/REPORT.md)完成，hm/history/geometry/full任务371/363/363/363。模型有局部动作作用，尚无学习吞吐优势；[全部配对条件图](r10_root_review/FIGURE_CAPTION.md)保留收益、退化与零变化。

随后另登记[训练参考残差修正32臂](reference_residual_20261003_r10b/REPORT.md)，冻结模型只改代价接法，hm/旧full/残差history/残差full任务185/184/185/182。64与32分别封存，不混为事前96臂；当前ridge保留作诊断，停止该overlay的测试调参。

[原作者GSES图与轨迹接口](gses_fixed_path_20261003_r10/REPORT.md)已完成8配置、16次独立重放，作者源码不变，公开归档离线重编一致。未来边权不能直接表示连续primitive，下一优先做共同执行映射再评价模型。[本轮三线结果与Astra/科研导师分别判断](THREE_ROUTE_POSTUPDATE_20261003_R10.md) · [下一方法合同](NEXT_METHOD_CONTRACT_20261003_R10.md)。以下R9及更早按历史阅读。

2026-10-03 R9：[primitive时长模型](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/primitive_duration_20261003_r9/REPORT.md)修正队列等待混入标签的问题，6机械＋24新留出完成。hm/history/learned任务184/186/188；学习相对历史只在一个条件多2，其余7相同。12个primitive×方向组的预测MAE全部更差，两个条件零历史时已分叉。下一先分离离线几何先验与在线历史，再扩大验证。

[作者Improved GSES预检](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/gses_author_preflight_20261003_r9/REPORT.md)已跑通原始代码，四组成功；尚未与连续FIFO任务统一对照。保留作者原版结果，并另做固定路径依赖映射。[本轮Astra与科研导师分别判断、三线实绩](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/THREE_ROUTE_POSTUPDATE_20261003_R9.md)。下方R8及更早为保留历史。

[R8三线结果与两类判断](THREE_ROUTE_POSTUPDATE_20261001_R8.md) · [下一方法合同](NEXT_METHOD_CONTRACT_20261001_R8.md)。

2026-10-01 R8：[两步承诺缓冲与局部依赖执行](local_dependency_20261001_r8/REPORT.md)完成6机械＋48留出，均完成规定的仿真时长。global hm/history/learned任务174/177/177，local200/201/201；学习相对历史规则所有16个配对任务数均相同，local固定FIFO时间还多98ticks。局部执行的收益已实测，模型贡献不能由此替代。[根审配对图](local_dependency_20261001_r8/FIGURE_CAPTION.md)同时呈现共同执行收益和模型的监督单位问题。

本轮由GPT-6-Astra/ultra与research-mentor分别预审后实作。公开朝向/动作编码错误已在留出前修正，仅用原12训练＋6校准公共事件重建6062/3010行，再冻结新模型。root独立向量几何、事件与增广最小二乘复算通过。第二步累计时长进入单步history造成的偏移另行诊断，未按测试结果改模型。下一先统一单步监督单位，再比较依赖关键性/任务价值；[文献差异与可核验作者基线](NEIGHBOR_COMPARISON_20261001_R8.md)已补正文与官方工件入口。

2026-10-01 R7：[新执行残差模型与真实搜索引导](execution_residual_20261001_r7/REPORT.md)完成12训练+6校准+24留出、每run400秒。模型由6,062完整标签训练，在相同hm留出轨迹上MAE由同历史规则9.3860降至6.8969 ticks；4/6world实际动作分叉，其中一组22共同服务任务8提前、2延迟、12相同，累计完成时刻净少14.2秒。任务总数仍为模型/规则各119、原hm120、旧小预算OBJ4迁移模型100，尚无学习整体优势。

[本轮Astra/科研导师分别判断与三线结果](THREE_ROUTE_POSTUPDATE_20261001_R7.md)：主线已证实前车未闭合时付费POSITION使后车真实到达提前3，查询已从静态计划改为持续在线FIFO。新模型已有独立决策作用，下一重点是普通END/实际费用、完整任务边际价值、合法局部依赖执行；已有REMAP等近邻，不能把加入模型本身当创新。所有R7训练/原生raw/失败均归档，root独立复算模型及真实服务；旧结果继续保留。

2026-10-01 R6 当前结果：[共同物理执行的 24 组作者方法实验](published_continuous_execution_20261001_r6c/REPORT.md)全部实际完成 800 秒并通过 FIFO、真实服务、动作及严格点 ACK 审计。两个地图、8/16 机器人、三个执行条件下，hm+GPIBT 共完成 780 任务，旧冻结 OnlineGGO 迁移模型 648；12 个配对全部旧模型较低。模型真实调用 154,434 次，但这不是新执行误差模型，也不是充分训练的作者学习方法结论。原错误配置的 24 组及 R6b 预检完整保留。

[三线结果与两份独立后评审](THREE_ROUTE_POSTUPDATE_20261001_R6.md)：主线完整收费查询已闭合，精确收据优化后统一 8m 合同成功、总实际费用净降 9.61%；查询线 70 次成功原生运行与 40 次留出已完成，主要条件下模型未胜 RR。[下一方法设计](NEXT_METHOD_DESIGN_20261001_R6.md)优先把真实进度证书接入在线任务/资源阻塞释放，再评价学习选择查询的边际任务收益。以下 R5 及更早文字是历史记录。

2026-10-01 最新（20260930_R5批次）：[真实误差模型36次执行](gpibt_lsmart_error_model_20260930_r4c/REPORT.md)已让预测改变官方动作和服务时刻，但学习/解析/历史全动作相同、完成任务数无增益；严格半MOVE点误差失败保留。[800机器人同未来任务流正式比较](paired_published_guidance_20260930_r5/REPORT.md)及[四官方地图64机器人试跑](standard_map_pilot_20260930_r5/REPORT.md)均已真实完成。训练模型、实际运行及原始归档已有完整结果，下面旧“尚未训练/待权限”只是历史阶段。

[三线更新与两份独立复判](THREE_ROUTE_POSTUPDATE_20260930_R5.md)保留技术与导师的不同优先级；当前采纳共同执行误差平台优先，在其中验证查询价值，主线收敛证据消费/费用。[下一模型设计](LEARNING_DECISION_DESIGN_20260930_R5.md)与[MAPF／LMAPF实验规范](mapf_evaluation_20260930_r5/README.md)区分已运行的先导与尚待完成的正式规模实验。

2026-09-30 R2 最终路线：[gpt-6.1-sol-ultra与科研导师分别判断及下一实验](THREE_ROUTE_POSTUPDATE_20260930_R2.md)。[官方OnlineGGO OBJ4评估入口](onlineggo_neural_preflight_20260930_r2/REPORT.md)现已实际构建运行；560参数的未训练常量诊断完成100步、27任务，并经1000动作重放核验。它是官方quad引导代价入口，已训练策略资格仍为false；正式权重/配置/训练日志尚待核验。[GPIBT/LSMART root独立核验](gpibt_lsmart_root_review_20260930_r2.json)已通过77工件、18二进制/对象身份及真实服务重建。

2026-09-30第二轮：[官方GPIBT→LSMART真实闭环](gpibt_lsmart_integration_20260930_r2/REPORT.md)已完成固定nominal/pause两例200ticks，每例5次持久官方plan、400个实际位置样本和1个真实任务服务。全部27个parser节点、admit/ACK、任务身份、20次STATION减计及21个连续驻留样本通过[独立审计](gpibt_lsmart_integration_20260930_r2/audit.json)。GPIBT算法对象保持官方身份，公开group_size2修正支持2机器人；LSMART仍是执行试验台。真实两臂任务前缀一致；末尾未完成任务／节点保留删失，最后已送达位置为tick199，不冒充精确物理tick200终态。

首次第二轮pair发现作者ADG.getPlan把S任务ID从未赋值的task_ptr读成-1，严格映射审计拒绝；保留原始两臂及旧server二进制后，仅把wire字段改为已有action.task_id，固定retry01两臂通过15／16个篡改负例。原暂停ticks30–49实际全部为空队列STOP，只造成派发延迟，未验证活动MOVE暂停或一般执行误差鲁棒性；中心间距采样不构成连续足迹安全。上一轮[首步与失败证据](gpibt_lsmart_integration_20260930/REPORT.md)47份文件字节保持，并保留[旧root核验](gpibt_lsmart_root_review_20260930.json)。

这条线已取得包含真实任务服务的因果一致官方共同执行轨迹；下一步在正式可比任务流和确实作用活动执行的扰动下，检验强解析／历史校准之外是否留下合法可观察的学习残差。OnlineGGO的真实评估接口已推进，合格训练策略R0仍待完成。[新增文献核查](LITERATURE_DELTA_20260930.md)核实JAIR2026 RL-RH-PP及AI2026 LDG执行框架，进一步限定学习优先级和组合放行的新颖性边界。已有内部规则不替代已发表作者基线；以下9月29日及更早结果保持各自范围。

2026-09-29 设计收敛：见[三线设计与外部基线合同](RESEARCH_DESIGN_AND_BASELINES_20260929.md)。第三线优先评估作者 GPIBT／OnlineGGO 引导接口与 LSMART 执行环境；原作者复现和共同误差执行器上的适配比较分表。本文已有 motion-only、解析与历史校准均为内部机制对照，不冒充已发表外部基线。论文主比较须有作者源码、固定版本、可复核运行和公平预算。

本轮新增[作者基线实际构建/运行记录](BASELINE_PREFLIGHT_20260929.md)和[官方GPIBT固定2×2先导](external_baseline_pilot_20260929/REPORT.md)：两个作者工作负载×seed42/43均完成450步，独立重放189,000动作通过，全部原始数据、补丁、脚本及[共同误差执行接口合同](external_baseline_pilot_20260929/COMMON_EXECUTION_ERROR_CONTRACT.md)已归档。这里只验证外部方法实验入口，尚未接连续误差或学习臂；OnlineGGO的学习策略仍未完成R0。下一项实现共同接口并验零误差/反馈因果性，再从真实执行日志检验可学习残差。

分支 `explore/error-aware-guidance`，起点 `main@af17410`。本目录研究：在固定足迹和空间误差安全层不变时，学习预测占用或等待代价能否帮助 lifelong MAPF 选择路径。现定位为替代学习/模型 LMAPF 底座评估，不预设必须在PIE-D内追加路径模块；已有native机制可用于迁移接口判别，不代表已切换或复现OnlineGGO等外部方法。

最新[两任务连续执行实验](CONTINUATION_RESULTS_20260929.md)已完成预声明16实例×4路线组合，包含零/非零二维误差、同一合法历史校准、两次择一的共同观察时刻，以及正常真实END/无后续END两个制度。正常END下，非零误差的4组中3组解析等待选路提前0.519005、0.833071或2.019005，1组无收益；零误差8组均无收益。缺END早观察的完成数优势在正常END后消失，失败范围已保留。全部64组合的完成数和60个可完成组合的到达均被同信息强解析解释，当前不支持为增加工作量而另加复杂学习。详见[冻结协议](CONTINUATION_PROTOCOL_20260929.md)、[64行原始结果表](continuation_summary_20260929.csv)和[最终完整回执](continuation_run_20260929_03.json)。尚未计全费用或接正式标准benchmark。

此前[历史校准闭环](HISTORY_CALIBRATION_PRECHECK.md)通过3722检查：真实历史MOVE的已交付END拟合运动时长，再用于事前择路。在合法较快运动条件下，旧模型错误选择上绕，历史校准改选下绕，实际到达从5.750325提前至5.231320，消除约0.519005的两候选选择损失；其余三组选择不变。拟合与单END解析校准相同，尚未证明复杂学习的独立价值。此前[冻结先验失配检查](MISMATCH_PRECHECK.md)通过2962检查，明确了没有历史时两种私有条件对选择器不可区分。

最新[原prefix普通分支与解析等待对照](PREFIX_PRECHECK.md)通过2998项检查、完成8格实际执行：t=4时解析等待事前选择下绕，约8.363081到达，比基础代价上绕约9.196152提前0.833071；t=2.5两者均选上绕。当前只有一个未授请求，不满足GROUP_ADMIT循环条件，原prefix普通初授和full-MOVE同轨，因此该2×2的授权因子退化。收益来自匹配先验的解析等待，未运行学习器，也不构成一般部分cap授权消融。

此前共同观察时机预检：**3042 项断言，严格编译和运行均退出 0**。四个具名机会各检查“零/非零误差 × 上/下绕路径”四个组合，实际结果如下。

| 唯一共同观察时刻 | 证书下界 | 非零误差上绕结果 | 已完成路径比较 |
| --- | --- | --- | --- |
| `2` | `2 < 61/20` | 仍等待，`arrival=null` | 不作完工时间排序 |
| `√(61/10)` | `61/20`，精确等号 | 仍等待，`arrival=null` | 不作完工时间排序 |
| `5/2` | `25/8 > 61/20` | 到达 `≈7.696152` | 上绕更快 |
| `4` | `24√2−28 > 61/20` | 到达 `≈9.196152` | 下绕更快 |

所有机会下，下绕均到达于 `2(√3+√6)≈8.363081`；零误差上绕均为 `4√3≈6.928204`。决策与断言使用精确实代数数，小数仅供阅读。不足释放时保留合法驻留和待处理需求，没有追加第二次观察。

上绕路径经 y=1，下绕经 y=−2，均从 `(0,0)` 到 `(4,0)`；阻塞机器人固定沿 `(2,3/2) → (8,3/2)` 运动。每组双方使用相同误差盒 Z、共同控制参数及同一次观察，包括不等待的路线。真实 Geometry/Index 给出责任和阈值，PositionCommit 实际提交证书后才释放。

这些是有限人工路线的机制结果，已验证历史尺度拟合修复一次选路失误，尚未证明学习优于解析或LMAPF净吞吐。下一项将稳定历史改成合法变化条件并接后续任务，检验校准是否仍有预测价值；若专门研究部分初授，须构造确实满足GROUP_ADMIT条件的循环请求。此前精确结果及边界见 [TIMING_PRECHECK.md](TIMING_PRECHECK.md)，方向与已有工作的区别见 [研究合同](RESEARCH_CONTRACT.md)。

复现命令从本分支根目录执行；输出文件须使用新名字，旧记录不会被覆盖：

```sh
rtk proxy python3 -B exploration/error_guidance/run_timing_precheck.py --source-root /home/lyh/MAPF_PIED_MDDR_RESEARCH --output exploration/error_guidance/timing_run_20260924_02.json
```

新源码为 [timing_precheck.cpp](timing_precheck.cpp)，运行器为 [run_timing_precheck.py](run_timing_precheck.py)，完整命令、退出码、stdout/stderr 和 SHA 见 [timing_run_20260924_01.json](timing_run_20260924_01.json)。运行依赖 [source_pins.json](source_pins.json) 指定的本地主线头与既有 FLINT SDK；这些源码仅在临时目录使用，不随分支上传。

原 t=4 预检的 [源码](precheck.cpp)、[运行器](run_precheck.py)及 [790 项断言证据](precheck_run_20260924_01.json)保持不变。
