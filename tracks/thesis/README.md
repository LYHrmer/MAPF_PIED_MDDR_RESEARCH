# 硕士论文集成支线

工作树 `/home/lyh/MAPF_THESIS_RESEARCH`，分支 `research/thesis-integration`。[main总体决定](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/docs/RESEARCH_PLAN.md)是唯一当前总体计划；本树公共文档只是创建时快照。SCI候选问题是给定合法多机器人初解，在有限总计算预算内改善路径质量；大论文引用同一优化器，依次考察无误差运动适配、空间误差影响和系统验证。旧固定路径误差模型不反向限定SCI选题。

## 已完成：冻结日志离线导出

[export_frozen_trace.py](export_frozen_trace.py)仅解析已完成DEV的Git对象，输出明确标为 `OFFLINE_REEXPORT`、`new_experiment: false`。它不导入科学模块，不调用模型、求解器、world或训练。

[shared.lock.json](shared.lock.json)把公共读取器和manifest同时固定到 `4a89183cf0827dcae2fa20a7d816c760e4150457`，分别登记commit、blob和SHA-256。读取器本身先经Git树项、blob和内容SHA检查，再执行其通用读取函数；不使用公共工作树或旧工作树的最新代码。manifest登记12个代码模块、25份实际证据，本导出只消费其中9份证据：四案events/result及RUN_RECEIPT，固定在 `ae058c5025eaaa61a424ef7627515d40c2e83997`。

| 冻结案名 | 对齐记录 | 已接受且已送达的END |
|---|---:|---:|
| ids13_initial | 57 | 2 |
| ids13_enumerate | 57 | 2 |
| ids013_initial | 74 | 3 |
| ids013_enumerate | 74 | 3 |
| 合计 | 262 | 10 |

实际产物为 [derived/trace.csv](derived/trace.csv)、[derived/completion.csv](derived/completion.csv) 和 [derived/index.json](derived/index.json)。两份CSV合计187,582字节，没有复制原始大日志；索引保存输入pins、生成器SHA、产物SHA/大小、各案来源及解释边界。以本仓库根目录执行：

```bash
rtk proxy python3 -I -B tracks/thesis/export_frozen_trace.py
rtk proxy python3 -I -B tracks/thesis/test_export_frozen_trace.py
```

10项契约测试通过：完整冻结记录覆盖、按键而非行号配对、初始模式/状态区别、误差分解、缺真值保留空值、重复/漏配拒绝、时刻/时钟/观测错配拒绝、未接受或不完整END拒绝、错误送达收据拒绝，以及读取器SHA验证必须先于执行。测试仅解析旧字节并在内存修改小型测试副本；不会运行新科学实例。

## 列的含义与证据限制

评估记录没有序号，先以机器人和精确有理数采集时刻关联capture，再以机器人和序号关联delivery；最后用规范化包的SHA、字节数、精确接收时刻关联 `receive_attempts`。不做最近帧、插值或浮点时间舍入配对。每个公共状态都是采集时刻的状态，只有对应反馈接受并送达后才可被接收方使用。

参考/真值为三维位姿，定位观测只含x/y。`tracking_* = true - ref`，`localization_* = observed - true`，`reported_* = observed - ref`；缺独立真值时前两类误差及真值列为空，不能用定位观测冒充真值。当前真值是冻结闭式仿真的 `evaluation_only` 标签，并非LIMO实测真值；theta差值保持日志坐标下的原始差，不擅自重估朝向。参考、真值和控制等评估标签不增加在线决策的信息假设。

`source_primitive_mode`保留源原语标签，`actual_control_phase`根据公开状态和记录的控制命令另作说明，不声称收到电机实际执行ACK。例如初始标签为ACCEL，但公开状态STOPPED且控制为零；DONE的浮点残余命令仍原样保留。用于描述零命令的阈值为1e-12，不是物理停止界。`controller_phase_exact`是源控制器进度，也不解释为轨迹时间偏差。

`transmission_delay_s`仅是采集到接收的传输延迟；`trajectory_time_offset_s`为空，状态为 `NOT_IDENTIFIED`。完成记录必须有被接受的END包及匹配接收收据，核对packet、session和result的实际completion；完成时刻与知晓完成的接收时刻分别保存，不能用预定时钟推定完成。

四案源于同一个R16四车输入，分别投影为两/三车并比较initial/enumerate；它们是相关DEV，不是四个独立性能或学习任务。同投影两臂的评估记录摘要相同，262条导出记录也不是262个独立样本。采样帧不支持经验零碰撞、管束覆盖率、连续安全或误差硬界结论；源结果的collision/coverage仍为 `NOT_MEASURED`。日志中的localization_bound只是原声明值，此处没有重新校准或验证。

## 当前实质结果与实现

[等成本改路与运动适配诊断](PATH_DIAGNOSTIC.md)集中保存六任务的逐车分组、作者SIPP等成本选择线索、v2必要条件及结论边界；入口不重复详细数值。random32的29条等成本实际改路贡献转向+113，其余变长/缩短路径合计-5，净+108。旧/新完整路径和失败证据均保留；这仍是几何事实，未证明执行更慢或具体原因。

[inspect_sci_paths.py](inspect_sci_paths.py)通过固定SCI提交和14个证据对象扩展离线解析，不调用求解器；新[逐车产物](derived/sci_equal_cost_structure.json)与旧[几何产物](derived/sci_path_structure.json)分开保留。[plan_selection.py](plan_selection.py)已实现SOC、保留等成本旧路径、转向感知三种整方案规则，复用[固定SCI validator模块](plan_selection.lock.json)。任何路径混合必须全体冲突/终点驻留检查通过，不能逐车恢复旧路径后直接执行。

当前只通过软件夹具，未在真实六任务上运行这些新规则，也未产生新的科学比较。已有转向/运动学感知方法仍须正面对照；“增加转向次目标”或“接入误差模型”本身不作创新。

## 条件式论文章节与下一步

| 章节位置 | 问题与当前条件 |
|---|---|
| 绪论、共同问题与基座 | 明确离散路径修复、预算、完整成本和失败语义 |
| 传统方法章 | 引用SCI同一实现；有方法/分析差异并经仿真验证后成立 |
| 学习辅助章（有条件） | 简单规则仍有跨任务可重复不足时，再选监督学习、在线学习或RL；不预先承诺独立RL章节，当前没有训练任务或学习结果 |
| 运动代价、执行误差扩展与系统验证章 | 先查等成本改路原因和简单对照，再建立无误差多车原语时序；最后核验v2资格并研究误差改变的等待/可行性，区分误差算法、敏感性分析、系统可执行性 |
| 结论 | 按实际成立的贡献归纳，章数/创新点仍需学校与导师要求确认 |

林威《复杂环境下多智能体系统的有效覆盖控制》（2024，81页）可借鉴逐章“问题—方法—仿真”的结构：第三章区域覆盖，第四章未知离散目标覆盖，第五章搭建Khepera IV平台并实物验证第三章的方法；它没有独立学习章，不是学校章数规定。其外部相机/ArUco定位条件也不同于当前LIMO。

下一项实质交付先完成无误差的直行、转向、等待原语和全车时序/连续占用检查，再判断离散收益能否保留；**连续适配尚未实现或验证**。误差阶段单独核验新路径是否满足v2：同一初始位姿参数贯穿全部动作，同实际输入和同步时钟，不在路点重置。当前六案若采用1m/格均超出原v2必要位移界；仓储两案在“一格边一个原MOVE”的统一缩放下甚至无满足最小MOVE长度与最大任务位移的尺度。具体算式及未通过条件见诊断报告，不能自动缩放或扩域。

固定外包与传播外包使用同一允许误差集合、运动模型、信息和调度器；没有差异就保留适用性分析。现v2不是一般持续跟踪误差模型；后续如确需持续扰动，只选一种来源重新定义与传播。SCI算法维持一份；两台LIMO的自身定位/里程计不能提供独立真实误差上界，实物可选且不阻塞SCI。科学DEV许可已消费，本轮仅实现、既有字节离线分析与软件检查。
