# 当前任务 cohort-flow 目标：运行前合同

2026-09-29，首次编译与运行前声明。本实验是 temporal task 的内部目标消融，
不改变旧 62 episode 夹具、回执、预测器或结果。只新增独立文件，最多一次修复后重跑；
所有失败保留。编译上限 120 秒，每个固定实例上限 60 秒。

## 唯一研究变量

旧规则保持窗口 6 内 pending task 预测完成数最大。新规则在同一 WAIT、single、
ordered pair 候选集合中，最小化当前已分配三个任务的
`cohort_flow = Σ(predicted_service_at − assigned_at)`。
分配时刻是各候选共有的常数，但明确记录。仅目标同分时少查询优先，之后沿用
WAIT、字典序与候选枚举顺序。查询次数是诊断项，不是假造生产净成本。

两规则共用原来的 relation release、严格 unit-clears 判断、blocker 公开标称时长、
END 交付先验 1/4、机会 2.5/2.75、周期服务从 8 起、当前任务公开路线和
`sqrt(alpha L)`。新规则不接收评价终点 16、未揭示补任务、Controller、真 eta、
实际结束时刻或物理位置。不可行候选不参与排序；当前有限实例要求存在可行候选。

当前任务包括 pending 和已经公开 grant 的 active 任务。pending 的最早开始由原
relation release 预测；active 使用已经公开的 MOVE launch time 加其公开长度
预测完整剩余路线，不能读取隐藏实时进度。新增公开 launch-time 记录在 grant 时写入。
本实例两次机会均早于第一次 service，只可能第一 leg 已启动；运行时检查此边界。
active 项在本有限独立 sweep 实例的各候选之间相同，但仍显式计入总和。
本方法没有声称适用于一般冲突、暂停/重新规划或任意 active MOVE 状态。

每次新目标决策记录当前任务 public input、所有候选 sequence、逐任务预测服务与
分配时刻、可行性、总 flow 和选中结果。Python 从 public input 独立重算 release、
时长、离散服务时刻、排序与实际选中 action；真实服务评价独立从原始事件重算。

## 固定实验表

沿用 `TEMPORAL_TASK_CONTRACT.md` 的六个实例、六条历史、六个冻结预测器、
真实 Geometry / PositionCommit / ReferenceController、任务源与服务条件。
预测器为 nominal、last END、mean3、median3、lag2 和 AR(1) OLS，均在测试前冻结。
每个实例运行六预测器 × 两目标，共 12 个配对 episode；另保留原 AR 单步 completion、
原 SRDC、两步 admission 和 WAIT 四臂。两个 quoted 实例再加原 RR，因此总共
`4×16 + 2×17 = 98` 个完整 episode，预期 882 个任务和 1,176 个 requester MOVE。
不扩大模型结构，不按结果改历史、窗口、参数、任务或条件。

六实例仍为 alternating-next-slow、alternating-next-fast、stable-fast、
同历史 hidden-slow-shock、以及前两者的共享观察与人工 native quote 诊断版。
各臂共享相同历史和外生任务源，实例 0/4、1/5 共享历史，实例 2/3 历史字节相同。
这些是有依赖的有限配对机制证据，不能把 98 episode 当作独立统计样本。
人工报价来源、六次共同初始化观察、SRDC PositiveScore/RR 分支要求保持原合同。
它们不是生产 COST，也不移植主线未闭合的成本。

## 评价与结论约束

每个 episode 必须真实执行 9 个任务、12 个 requester 原 MOVE，并完成 END/READY/
owner 收尾。保留全任务服务曲线、flow 总和、末服务、所有查询及离线预测误差；
另报告首批当前 cohort 的实际三个服务时刻及 flow。首批目标没有偷看后续六任务，
其效果不等于全未来 episode 最优。

新运行的旧目标六臂及基线与旧 successful receipt 逐项比对，证明变化来源没有
扩展到原世界或基线。保留 AR≈lag2、隐藏突变损失、查询增加却无服务改善、以及任何
新目标负结果。目标消融不构成新外部 baseline，也不自动建立学习贡献。
若新目标消除“预测更准但服务更差”，结论限于此处目标错配机制；否则如实记录。

## 首轮记录与唯一修复

`objective_task_run_20260929_01.json` 保留六组失败及源码快照：新增日志用
`exact(model.alpha)` 输出无理数时报错。目标、预测器与选择逻辑没有失败证据。
唯一修复仅将该字段改为原精确比较生成的 alpha 包围区间；独立审计使用有理数
区间运算和整数平方根构造严格 sqrt 包围，要求上下界证明同一个离散服务时刻，
不能用近似中点回流 native 决策。第二轮若仍失败即保留并结束，不再改配置重跑。
