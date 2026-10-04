# R15：MAPF / LMAPF 正式期刊算法侦察与三线接入判断

检索日期：2026-10-04（Asia/Shanghai）。本次只读 R13 方法合同、R13 近邻审查和 R14 三线总结，检索出版方、作者项目页、作者仓库及公开源码；**未 clone、安装、构建、训练、运行求解器或重跑任何实验，未修改既有科学工件**。本文件是新增文献与方法选择记录。SADG 固定提交源码发现由根智能体独立核查后传回，本文明确区分该来源与本侦察直接核查。

## 结论和选择顺序

最值得先预检的是 **SADG（T-RO 2024）**：它与现有固定路径、执行延迟、依赖重排问题密切相关，公开实现采用连续时间 MILP，能够检验位置证据是否通过有物理依据的残余时间改变合法顺序，避免直接修改 GSES 的单位步长假设。其动作分组与承诺模型尚不能视为和本项目同构。**OTIMAPP（T-RO 2023）** 则是本次确认的另一套许可明确、规划器、执行器、实例和实验脚本齐全的期刊底座，适合资源保持与任意时序执行的安全对照，但它会改变路径生成问题，不能冒充同一 checkpoint 的 GSES 后缀优化器。

**WinkTPG（T-ASE 2026）是学科上最贴近“位置更新—时间不确定性—后续执行”的候选之一，而且已找到官方源码。** 它不是只有 arXiv 的工作，正式卷页和 DOI 已由作者机构页及作者实现双重确认。不过当前公开代码的许可、论文全部不确定性模型及完整实验重现材料尚未确认，必须保留这些边界。

再次核对的 **LDG 执行框架（Artificial Intelligence 2026）** 已正式发表，直接覆盖根据实时状态改变共享位置通过次序并维持剩余执行可行性。根审确认本项目在 [9月30日记录](LITERATURE_DELTA_20260930.md)已登记此文；本次不是首次发现。即使暂未找到作者代码，它也是必须读的创新边界：仅“动态合法重排”“剩余计划可行性检查”不能作为新贡献。

查询线的近期方向仍应是扩大**有完整后果差异的合法动作与信息集合**，而非更换网络。PIBT 和 PRIMAL2 提供真正的持续任务环境、拥堵和局部信息学习参照，均不直接解决付费 POSITION 的购买价值。不能把它们的吞吐优势移植为当前 C/LD 两尾策略的学习空间。

## 六个正式期刊锚点

“源码齐全”指静态核对到必要工程材料；本次没有实际构建，不能写成已复现数值结果。没有据此生成任何 Q 分区或影响因子判断。T-RO 是机器人学 Transactions；T-ASE 是自动化应用强相关 Transactions；AIJ 是人工智能学科期刊；RA-L 明确为 Letters，不能统一称作 T-RO/IJRR 级别长文。

|优先级|正式题名与作者|正式期刊、年份、DOI、状态|作者实现与复现资格|主要服务对象|
|---|---|---|---|---|
|1|Alexander Berndt, Niels van Duijkeren, Luigi Palmieri, Alexander Kleiner, Tamás Keviczky. **Receding Horizon Re-Ordering of Multi-Agent Execution Schedules**|IEEE Transactions on Robotics **40:1356–1372, 2024**；[10.1109/TRO.2023.3344051](https://doi.org/10.1109/TRO.2023.3344051)；已正式发表，不能因 README 仍写 to appear 就降为预印本|[alexberndt/sadg-controller](https://github.com/alexberndt/sadg-controller)，**AGPL-3.0**；研究原型，状态反馈有已核实未接完的接口|第三线直接作者对照；主线证据到残余估计的接口|
|2|Keisuke Okumura, François Bonnet, Yasumasa Tamura, Xavier Défago. **Offline Time-Independent Multiagent Path Planning**|IEEE Transactions on Robotics **39(4):2720–2737, 2023**；[10.1109/TRO.2023.3258690](https://doi.org/10.1109/TRO.2023.3258690)；已正式发表；IJCAI 2022 是较早会议版|[Kei18/otimapp](https://github.com/Kei18/otimapp)，**MIT**；规划、延迟执行、测试、实例、实验脚本公开，静态复现材料完整度高|主线资源保持/时序安全；第三线安全参照|
|3|Jingtian Yan, Stephen F. Smith, Jiaoyang Li. **WinkTPG: An Execution Framework for Multi-Agent Path Finding Using Temporal Reasoning**|IEEE Transactions on Automation Science and Engineering **23:9162–9175, 2026**；[10.1109/TASE.2026.3688563](https://doi.org/10.1109/TASE.2026.3688563)；正式发表；IROS 2026 展示不改变期刊身份|[JingtianYan/WinkTPG-IEEE-TASE](https://github.com/JingtianYan/WinkTPG-IEEE-TASE)；官方源码明确，**许可 UNKNOWN**，完整论文实验重现资格待核|位置反馈、执行窗、速度规划、模型条件安全裕量|
|4|Yihao Liu, Xueyan Tang, Wentong Cai, Jingning Li. **Robust and effective multi-agent path execution with timing uncertainty**|Artificial Intelligence **358:104586, September 2026**；[10.1016/j.artint.2026.104586](https://doi.org/10.1016/j.artint.2026.104586)；正式期刊卷已出版|官方作者仓库 **UNKNOWN**；许可、依赖、完整数据、构建均 **UNKNOWN**，不能编造软件复现资格|第三线直接近邻（9月30日已登记）；资源/位置依赖与在线安全执行|
|5|Keisuke Okumura, Manao Machida, Xavier Défago, Yasumasa Tamura. **Priority inheritance with backtracking for iterative multi-agent path finding**|Artificial Intelligence **310:103752, 2022**；[10.1016/j.artint.2022.103752](https://doi.org/10.1016/j.artint.2022.103752)；正式发表；勿混同 IJCAI 2019 旧实现|[Kei18/pibt2](https://github.com/Kei18/pibt2)，**MIT**；MAPF/MAPD、实例、实验版本标签和脚本均有|查询线未来真正持续任务/拥堵底座；不是物理误差执行器|
|6|Mehul Damani, Zhiyao Luo, Emerson Wenzel, Guillaume Sartoretti. **PRIMAL2: Pathfinding Via Reinforcement and Imitation Multi-Agent Learning – Lifelong**|IEEE Robotics and Automation Letters **6(2):2666–2673, 2021**；[10.1109/LRA.2021.3062803](https://doi.org/10.1109/LRA.2021.3062803)；正式 RA-L 论文，亦在 ICRA 展示|[marmotlab/PRIMAL2](https://github.com/marmotlab/PRIMAL2)，**MIT**；环境/训练/模型外链公开，旧依赖和权重下载可用性未验证|局部观测、拥堵约定、持续任务学习参照；不是付费查询基线|

出版状态的 primary sources：[SADG 作者机构记录](https://research.tudelft.nl/en/publications/receding-horizon-re-ordering-of-multi-agent-execution-schedules/)、[OTIMAPP 作者项目页](https://kei18.github.io/otimapp/)、[OTIMAPP 作者实验室出版目录](https://www.coord.c.titech.ac.jp/publications/)、[WinkTPG 作者出版页](https://jingtianyan.github.io/publications/)、[WinkTPG 实验室页](https://arcs-group.github.io/execution/)、[LDG 出版方](https://www.sciencedirect.com/science/article/pii/S0004370226001128)、[LDG 合作者 NTU 页](https://personal.ntu.edu.sg/asxytang/)、[PIBT 出版方](https://www.sciencedirect.com/science/article/pii/S0004370222000923)、[PRIMAL2 作者实验室出版目录](https://www.marmotlab.org/publications.html)、[PRIMAL2 作者 CV 卷页](https://marmotlab.org/Sartoretti_curriculumvitae_2026.pdf)。IEEE DOI 页面部分遭机器人验证或访问错误，未将未读到的出版正文伪称已读；WinkTPG 的具体 IEEE 条目为 [11498333](https://ieeexplore.ieee.org/abstract/document/11498333)。

## 1. SADG：直接改善“证据进入哪一个可响应的量”

论文将可切换依赖与连续开始/完成时间结合为滚动 MILP，优化累计完成时间；依据是[项目公开正式论文](https://darko-project.eu/wp-content/uploads/papers/2024/Receding_Horizon_Re-Ordering_of_Multi-Agent_Execution_Schedules.pdf)。它与 GSES 都可在固定空间路径上处理访问顺序，但不能把两者内部权重、可切换集合和承诺条件视为相同。

作者仓库提供 Python、ROS2 控制/模拟节点、Dockerfile、requirements、libMultiRobotPlanning 子模块和六类示例地图；README 记载 Ubuntu 20.04/ROS Galactic、22.04/ROS Humble、colcon/rosdep，以及随机起终点可能使某些配置失败。没有在本侦察中取得并验证逐表逐图冻结实例清单；维护说明将其定位为研究原型。[作者仓库与构建说明](https://github.com/alexberndt/sadg-controller)

根智能体独立静态核对提交 `c2626d996121a9d6c128844a167b917db24418ac` 后报告：`sadg/vertex.py` 的 `get_progress()` 为 TODO，当前返回 `0.5`；优化器对 active 首段使用 `(1-progress)*expected_completion_time`，期望时间取路径长度/标称 2 m/s，且有固定 60 s 上限。这是**当前公开版本的接口欠缺**，不能反推出原论文实验也使用该常数。具体源码适配边界由根的 `SADG_SOURCE_FIT_20261004_R15.md` 另行记录。

**可改进切口（本项目推断）**：明确同一 occurrence 的捕获时间、送达年龄、几何位置与当前未完成段，先形成物理允许的残余时间区间；将公共估计与付费证据估计分别送入同一连续时间求解接口，再经过原承诺 guard。原版与适配版分别标识。补完 TODO 本身属于工程修复；研究贡献仍需是有限信息购买如何改变合法候选及完整后果，且有相应费用/预算与失败回退。

## 2. OTIMAPP：许可和材料清楚的 T-RO 底座

OTIMAPP 在离线阶段选择可容忍异步执行的路径集合，让执行不依赖精确同步时刻；其保证有资源互斥和执行公平性等模型条件，不能把“无需同步”读成无需碰撞避免或允许永久故障。它提供了死锁结构和规划保守性的不同参照。[作者项目与正式版本区分](https://kei18.github.io/otimapp/)

[作者仓库](https://github.com/Kei18/otimapp)明列 C++17、CMake ≥3.16、Google Test 与 grid-pathfinding 子模块；`app` 规划、`exec` 做 MAPF-DP 延迟执行，`instances.zip` 和 `exp_scripts` 对应论文实验，地图来自公开 Pathfinding Benchmarks；可视化依赖 openFrameworks/macOS，核心求解不必因此依赖 GUI。[CMake](https://raw.githubusercontent.com/Kei18/otimapp/master/CMakeLists.txt)与[MIT 许可正文](https://github.com/Kei18/otimapp/blob/master/LICENCE.txt)已静态核对。尚未校验压缩包完整性、实际构建或原表格数值。

**对三线的作用（推断）**：主线可用其“资源保持—释放—后继可行动”模型检查认证边界；第三线可比较“不靠在线精确时长的保守安全路径”和“同路径在线改序”的取舍，但要分别报告路径质量差异。它不是 lifelong 任务流生成器，也不提供证书购买价值；不能把现有固定批次换个名字称为 LMAPF。建议先做模型映射，不因库完整就新增一批重复运行。

## 3. WinkTPG：信息更新与物理时间的强相关候选

已读[公开论文 v2 的不确定性、窗口机制及评估章节](https://arxiv.org/html/2508.01495v2)。WinkTPG 在窗口边界更新状态并重新生成运动学可行速度轮廓；其安全裕量区分有界累积延迟、有界均匀扰动和 Gaussian 扰动，后者仅在给定概率阈值和模型条件下给出概率保证。论文中更频繁的位置更新影响执行效率；这与付费信息价值直接相关，但论文并未因此建立本项目的受保护 POSITION/收费合同。

论文给出的旧源码地址 [IEEE-T-ASE-WinkTPG](https://github.com/JingtianYan/IEEE-T-ASE-WinkTPG) 已实测跳转到 [WinkTPG-IEEE-TASE](https://github.com/JingtianYan/WinkTPG-IEEE-TASE)。可见 `inc/`、`src/`、示例路径、仓库路径文件；[README](https://raw.githubusercontent.com/JingtianYan/WinkTPG-IEEE-TASE/main/README.md)给出 `-m 1` 为 WinkTPG、`-m 0` 为 TPG。其[CMake](https://raw.githubusercontent.com/JingtianYan/WinkTPG-IEEE-TASE/main/CMakeLists.txt)要求 C++20/Boost system、program_options、filesystem，指定 `/usr/bin/g++`，启用 `-ffast-math`。当前根目录未见 LICENSE；**许可 UNKNOWN，不能写成 MIT 或已获得再发布权**。公开六图/25实例论文实验与 PBS 输入来源有论文说明，但库中完整批量脚本、全部精确路径输入、统计脚本和 robot stack 未确认。

**代码完整性的重要限制**：[driver.cpp](https://raw.githubusercontent.com/JingtianYan/WinkTPG-IEEE-TASE/main/src/driver.cpp)明列 `delay_type=0/1` 为无扰动/Gaussian，`delay_steps` 的帮助写为 legacy K-step 的 unused 参数；读入的 delay_steps_low/high 在该 driver 中未传入 simEnv 构造。仅凭这个入口不能确认论文的两个有界模型已随公开程序完整交付，也不能因此断言所有下层实现缺失。它具备实质求解/执行代码，但还不是已核实的逐表完整复现包。

**可改进切口（推断）**：在保持路径及安全裕量语义时，把“定时全量更新”改为预算内有条件取得局部证据，并研究证据年龄/精度对后续速度轮廓与完成时间的影响。需要证书绑定位置及速度/加速度知识的合法来源；单次位置不能自动给出未来 ETA。主线先统一执行域，第三线若仍采用原 ARRIVE guard，不能从 WinkTPG 的提前协调速度轮廓推导出可直接提前释放资源。

## 4. AIJ 2026 的 LDG：直接相关、作者代码尚未知

[出版方摘要与可见方法节](https://www.sciencedirect.com/science/article/pii/S0004370226001128)给出 Location Dependency Graph（LDG），在线检查剩余路径能否继续无冲突、无死锁地执行，并选择尽可能多的机器人并行动作；其可行性问题为 NP-complete。这与“固定空间路径、观测当前状态、调整共享节点顺序”的第三线非常接近。不能仅凭摘要认定其连续几何碰撞、已承诺 MOVE 或信息收费语义与本项目一致。

已核对[合作者 NTU 出版目录](https://personal.ntu.edu.sg/asxytang/)、[第一作者相关项目页](https://tc-imba.github.io/research/mapf-uncertainty/)和[第一作者连续时间项目页](https://tc-imba.github.io/research/mapf-countinuous/)。这两个项目页没有给出本次可验证的该 journal 软件链接；作者 GitHub 一般仓库列表也未建立到 journal 版本的来源关系。**官方仓库、许可、构建、全部实例、扩展源码接口均 UNKNOWN**；这表示本次未确认，不表示作者没有代码。不能用 SoCS 2024 同作者早期论文当成已复现 AIJ 2026 版本。

**对三线的作用（推断）**：主线对照其位置依赖所需证据类型；第三线对照其剩余计划可行性与本项目 guard 的充分性边界；查询线可讨论购买哪个状态能改变并行动作集合。当前仅够作为方法近邻和接口设计参照，不够立即挂牌“作者程序外部基线”。

## 5. PIBT / pibt2：真正持续任务的便于复现底座

PIBT 使用局部单步动作、动态优先级继承和回溯。正式论文的有限时间到达保证依赖图结构条件，例如相邻顶点属于简单环的图；不能对所有死胡同仓库无条件引用。[出版方正式论文](https://www.sciencedirect.com/science/article/pii/S0004370222000923)

[pibt2](https://github.com/Kei18/pibt2)明确是 AIJ 2022 期刊版本，非旧 `Kei18/pibt`；包含 MAPF/MAPD，HCA*、Push and Swap、TP、PIBT(+)；C++17、CMake ≥3.16、Google Test/grid-pathfinding 子模块、Ubuntu 18.04 Docker 方案。公开 `instances/mapf`、`instances/mapd`、地图及 Python3.7 的 `exp_scripts/mapf.py`/`mapd.py`，分别提供 `exp/mapf`、`exp/mapd` 实验标签。[构建与实验版本说明](https://raw.githubusercontent.com/Kei18/pibt2/master/readme.md)、[MIT 许可](https://raw.githubusercontent.com/Kei18/pibt2/master/LICENCE.txt)。

**可改进切口（推断）**：未来新 TRAIN/CAL 可引入公开持续任务流、局部拥堵和多候选动作，从完成任务/等待时间的后果建立信息价值标签；先保证同任务流、同信息权限与同误差执行层。PIBT 本身是离散规划器，不是现有真实付费证据执行器，因此优先作为任务流与规划骨架，保留独立执行审计。只有在动作集合出现可用价值差异后才讨论透明价值模型或小 MLP。

## 6. PRIMAL2：学习方向的期刊参照，当前不建议重训

正式 RA-L 身份由[作者实验室 publication](https://www.marmotlab.org/publications.html)、[录用公告](https://marmotlab.org/blog/2021/02/19/RAL2021.html)及[作者 CV](https://marmotlab.org/Sartoretti_curriculumvitae_2026.pdf)确认；[论文作者稿](https://arxiv.org/abs/2010.08184)针对高密度、结构化环境中的 lifelong 任务与局部观测。ICRA oral 是展示安排，不是另一篇期刊证据。

[官方仓库](https://github.com/marmotlab/PRIMAL2)提供环境、地图生成、观测、A3C/Ray 训练、OD-M* 扩展，以及 one-shot/LMAPF 两类预训练模型的 Dropbox 外链；[许可](https://github.com/marmotlab/PRIMAL2/blob/main/LICENSE.md)为 MIT。构建要先编译 `od_mstar3` 扩展；[requirements](https://raw.githubusercontent.com/marmotlab/PRIMAL2/master/requirements.txt)固定 TensorFlow 1.11.0、Ray 0.8.7 等旧版本。模型外链实际下载、推理成功、原评估脚本完整性均未验证；不能因为有训练代码就称当前系统可直接重现论文表格。

**对本项目的作用（推断）**：可借鉴局部观测设计与拥堵约定来构造有信息价值的任务机制；若未来比较 learned LMAPF，应与 PIBT 和更近的会议方法并列。PRIMAL2 策略输出移动动作，当前查询器输出是否购买证据，二者不能直接等同。它不解决查询价格、证书时效或提交后安全；当前 C/LD 价值空间近乎耗尽时重训 PRIMAL2 不构成合理下一步。

## 未列为六个主候选的直接线索

1. **Multi-agent pathfinding with continuous time**，AIJ 305:103662 (2022)，[DOI 10.1016/j.artint.2022.103662 / 出版方](https://www.sciencedirect.com/science/article/pii/S0004370222000029)。[作者 Continuous-CBS](https://github.com/PathPlanning/Continuous-CBS)含源码、实例、原始表格和实验标签，C++11/CMake；适合非整数动作时长问题。当前仓库 README 主要映射 IJCAI19/AAAI21，需另核 journal 版本对应关系；它是重新规划器，不是受承诺约束的固定路径执行重排，故不优先替代第三线。
2. **A Robust Lifelong Multi-Agent Path Finding With Active Conflict Resolution and Decentralized Execution**，RA-L 10(5):4652–4659 (2025)，[DOI 10.1109/LRA.2025.3554099](https://doi.org/10.1109/LRA.2025.3554099)。[IEEE 官方可见页面](https://xplorestaging.ieee.org/document/10937741/)明确持续任务、不确定性、active/passive conflicts、滚动窗和分散执行。作者代码、许可及完整数据本次 **UNKNOWN**；这是第三线升级为真正 robust LMAPF 时的直接近邻，优先级高于泛化无人机 MARL，但未达到本次“可立即复现”资格。
3. **Robust Multi-Agent Path Finding and Executing**，JAIR 67:549–579 (2020)，[正式出版页 / DOI 10.1613/jair.1.11734](https://jair.org/index.php/jair/article/view/11734)。是鲁棒计划、执行策略、通信延迟的基础锚点；不把 AAAI2021 k-CBSH-RM 源码自动视为这个 journal 的作者版本。
4. 既有 GSES / Improved GSES 是 **AAAI 2025 会议**；Should I Replan? 与 ExecTimeNet/REMAP 本轮不新增期刊认定。SMART 已为 **RA-L 2026 测试平台论文**，[作者页](https://arcs-group.github.io/execution/)可核 DOI，但用户已有平台，不把再次安装/运行 SMART 算新的算法或新实验。

## 不重跑旧实验的下一步方法合同建议

|线路|先补的实质问题|本次文献给出的用途|通过何种门槛后才新增运行|
|---|---|---|---|
|主线|同一真实执行对象的 occurrence、几何映射、捕获/送达年龄及费用权限|SADG 的残余估计接口；WinkTPG 的状态刷新/时间裕量；OTIMAPP 的资源保持逻辑|证书改变一个合法决策量且来源/费用/guard 可独立核对；不把 JSON 归档当新 capability|
|查询|C/STOP 等匹配尾策略是否有完整任务/时间后果差异；预算是否真的改变优选|PIBT 的持续任务骨架、PRIMAL2 的局部拥堵观测；不照搬移动策略|先以新 TRAIN/CAL 证明合法动作或信息集合有响应；旧 TEST、R13 模型、R14 已有零增益结果保持冻结|
|第三线|合法可见证据能否改变可采用顺序，或能否形成新的安全速度选项|优先同 checkpoint 的 SADG 作者对照；WinkTPG 另立速度控制合同；LDG 列入新颖性审查|先静态映射/公开敏感性分析，命中去重键复用；仅对新的合法采用与完整后果必要新增运行|

第三线当前固定批次应继续报告平均完成时间/ΣT 与 makespan，不能报告虚构的吞吐增益。使用连续时间求解器并不证明证据一定有用；观测差异可能仍不足以改变合法选择。若信息只能改善预测而不能改变任何实际后缀，应明确给出零价值结果，而不是加大网络或重复旧条件。

本报告筛出的最窄研究命题是：**在执行承诺不可撤销、状态证据有获取成本和时效限制时，何种证据足以改变合法候选的完整执行价值，以及何时值得购买。** 这需要本项目自行证明，六个期刊锚点只提供已存在的方法、边界与可复现底座；不能把它们替用户提供尚未取得的实验收益或创新结论。

## 核查边界与检索记录

检索覆盖了执行延迟/ADG/SADG、time-independent planning、WinkTPG、LDG、continuous-time CBS、PIBT、PRIMAL2 和 robust lifelong 执行。主要组合包括正式题名 + DOI / github、期刊名 + execution / lifelong / dependency。网页日期可能是抓取日期，本文年份/卷页使用出版方或作者正式引文，不用抓取日期代替出版日期。

六个主候选均已区分论文身份、代码来源与未知项。没有找到更贴近本问题且同时具备可验证作者代码的 IJRR 候选，因此没有为了凑“顶刊”填入不相关 IJRR 论文。除根已固定的 SADG SHA 外，其余链接指向本次访问时的公开分支；如进入实现，应先记录 commit/许可证/源码 hash，再用已有资产查重，不以当前分支自动等同论文版本。

本次新增实验数量：**0**；新增训练数量：**0**；现有冻结结果变更：**0**。
