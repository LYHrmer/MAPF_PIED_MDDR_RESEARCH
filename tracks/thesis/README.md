# 硕士论文集成支线

工作树 `/home/lyh/MAPF_THESIS_RESEARCH`，分支 `research/thesis-integration`。[main总体决定](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/docs/RESEARCH_PLAN.md)是唯一当前总体计划；本树公共文档只是创建时快照。SCI当前研究标准离散MAPF的局部路径修复与计算预算；旧固定路径误差模型只提供执行侧历史证据，不反向限定SCI选题。

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

## 新增：固定SCI修复结果的运动结构检查

[inspect_sci_paths.py](inspect_sci_paths.py)通过已有固定Git读取器消费SCI提交`535ee1adf3135ab79565e0b3aa5d189348fe7ab2`。[sci.lock.json](sci.lock.json)固定输入、六份result/receipt和汇总共14个对象，核对blob/SHA后仅解析已生成路径；没有复制优化器或引用相邻工作树的最新文件。

产物[derived/sci_path_structure.json](derived/sci_path_structure.json)为10,066字节，SHA `89e79538e5ee1f9bb849e76973c126157eec2307165a7bf86b19551e201b6f30`。标记`OFFLINE_GEOMETRY_OF_EXISTING_SCI_PLANS`、`new_experiment=false`。所有六任务保留，以下列出有SOC改善的三项：

| 任务 | SOC变化 | 移动步变化 | 等待步变化 | 内部四分之一圈变化 | 加上任意共同首末朝向后的方向旋转量变化区间 |
|---|---:|---:|---:|---:|---:|
| maze16 | -1 | -2 | +1 | +11 | [8, 14] |
| maze32 | -2 | -8 | +6 | +18 | [16, 20] |
| random32 | -1 | -2 | +1 | +108 | [80, 136] |

其余random16、warehouse16/32全部变化为0。等待保留上一移动方向，180度反向计2个四分之一圈；静止路径不虚构朝向。最后一列只针对“车头沿移动方向、格边之间作最短旋转”的方向序列：圆周距离满足`|d(h,u)-d(h,v)|≤d(u,v)`，分别作用于两端并求和。初始/终点共同朝向的不确定性不能抵消这三项内部转向的全部增加。

这是明确的**离散SOC与转向量不一致**证据，不是实际旋转时长或总完成时间的测量。尚未计入变速、加减速、倒车、圆弧转弯、等待中转向及多车重新定时；不能把单车原语时间相加后直接称完整安全执行结果。新增4项软件检查覆盖等待/反向、静止、非法格边及方向距离边界；几何结论的范围由定义和上述不等式限定。

大论文因此优先考察：**同一MAPF局部修复在加入运动代价后，哪些离散收益保留、哪些需改变接受或修复规则？** 这是具体候选问题，已有转向/运动学感知规划必须正面对照，不能把“加一个转弯惩罚”当新意。下一实质交付为声明少量运动原语、建立固定路径到运动时序的映射，再对所有车辆检查冲突、等待与终点驻留；当前没有该执行结果。

## 条件式论文章节与下一步

| 章节位置 | 问题与当前条件 |
|---|---|
| 绪论、共同问题与基座 | 明确离散路径修复、预算、完整成本和失败语义 |
| 传统方法章 | 引用SCI同一实现；有方法/分析差异并经仿真验证后成立 |
| 学习辅助章 | 只针对传统方法中已观测到的瓶颈，先取得有效标签与增强传统对照；当前没有训练任务或学习结果 |
| 运动代价、执行误差扩展与系统验证章 | 已有SOC改善伴随转向增加的结构证据；先核对原语转换后的收益和连续冲突，再区分误差算法、敏感性分析、系统可执行性 |
| 结论 | 按实际成立的贡献归纳，章数/创新点仍需学校与导师要求确认 |

林威《复杂环境下多智能体系统的有效覆盖控制》（2024，81页）可借鉴逐章“问题—方法—仿真”的结构：第三章区域覆盖，第四章未知离散目标覆盖，第五章搭建Khepera IV平台并实物验证第三章的方法；它没有独立学习章，不是学校章数规定。其外部相机/ArUco定位条件也不同于当前LIMO。

SCI已核定提交的路径/成本消费与几何分解已完成。下一项是连续运动原语适配，重新计算加减速、转弯、等待和终点驻留，声明离散合法性与连续执行条件的区别。**连续适配尚未实现或验证**，不能由几何计数或轨迹导出器代替。SCI算法维持一份，不在大论文支线复制第二套优化器。原v2只覆盖已声明的整任务初始位姿扰动和同输入同步执行，未覆盖持续滑移或闭环纠偏；两台LIMO的自身定位/里程计不能提供独立真实误差上界，实物可选且不阻塞SCI。
