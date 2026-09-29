# cohort-flow 后继的独立导师源码与结果审查

2026-09-29。审查角色与实现 agent 分离；本次只读源码、合同和原始输出，独立重算后新增本文件，没有修改夹具、运行器、旧审计器、失败回执或研究参数，没有编译/重跑 native/运行 guest，也未 commit。

**结论：支持这项有限目标消融的结果，无阻断问题。** 新目标修正了本例的短窗计数与完整当前任务代价错配；它没有建立 AR 相对 lag2 的学习优势，也没有完成生产计费或一般 lifelong 优化。恢复分析合法使用了全部第二次原生运行证据，没有删除 episode、修改决策或补跑挑结果。两个覆盖限界应明确保留：实际决策输入中 active 任务项为零，全部候选均可行，因此这两条源码分支没有本表的运行覆盖。

## 源码审查

已读 [运行前合同](OBJECTIVE_TASK_CONTRACT.md)、[新夹具](objective_task_fixture.cpp)、[原运行器](objective_task_run.py)、[原审计器](objective_task_audit.py)、[恢复审计器](objective_task_recovery_audit.py) 和 [离线恢复程序](objective_task_recover.py)，并对照旧 `temporal_task_fixture.cpp` 与旧 successful receipt。

1. **同信息与 active MOVE。** `public_launch_times` 只在真实公开 grant 提交时写入当前 clock；`public_cohort()` 只读当前 assignment、已公开 plan、grant 计数和该记录，并以 `task==1`、`assigned_at==0`、`next_leg<=1` 和公开 action/demand 存在性限制范围。新选择器没有访问 `Controller.snapshot()`、`physical_x`、`ended/delivery`、私有 eta 或未来 task queue。active 项以完整公开首 leg 的 launch time 加公开路线预测，从实际 grant 的时间起算，没有免费读取已走进度。它只适用于当前 first-leg 有限场景，不能外推暂停、重规划或一般 active 状态。
2. **未来信息边界。** 第二、第三任务只在旧 `service_row()` 服务之后交付；新目标两次选择早于首次服务，只包含 D1/D2/D3 的 task1。评价终点16只在世界循环；模型和选择器不接收它。条件名字/当前 eta 只进入世界构造与结果标签。历史模型仍在测试前从六条已收到 END 拟合并冻结；测试结束误差字段不回流。
3. **不可行性不被静默抹去。** `cohort_flow_value()` 总是逐项输出三任务；遇到 non-owner 不可行或不可释放关系时，将候选整体 `feasible=false`。`choose_cohort_probe()` 只比较完整可行候选，无可行解则显式拒绝。虽然部分和只累加可行项，不可行候选并不会以这个偏小的数获胜。
4. **唯一研究变量。** 旧 `completion_value`/`choose_probe`、历史结构与 `frozen_models`/condition 定义与 temporal 源码逐字一致。新旧共用模型、正常 END、运动执行、两次机会、WAIT/有序 pair 枚举、几何安全和实际任务源。新增公共字段没有新增观察或读取权限；active 项在这个独立 sweep 设置下对同一次选择的各候选是共同项。查询数量仅作 flow 同分规则，不与人工报价合并成收费目标。
5. **精确预测没有被日志近似取代。** 01→02 的 C++ 唯一修复把日志 `exact(model.alpha)` 改为既有精确比较构造的 alpha 包围区间；预测计算与排名仍使用原精确 Real。区间仅供离线核验，不回流选择器。

恢复审计器相对原审计器的实质差异只有收集 launch 的 guard：只为 cohort-flow、在尚有 cohort 决策时记录公开 launch。两个选择之后的续接 MOVE 不再被无关的“必须为有理数时刻”条件拒绝。完整服务验证仍读取所有后续事件，保留每臂九任务和12 MOVE；这个修复没有改变或缩短评价范围。

## 独立数值核验与完整性

原审计器最终版本以 `Fraction` 和 `isqrt` 在固定 `10^-18` 网格包围平方根：取 `floor(sqrt(floor(x D²)))/D` 为下界，非精确平方时加 `1/D` 为上界。release 的 min、start 的 max、正长度上的 sqrt(alpha×L)、求和均单调，因此逐端传播得到保守 arrival 包围；只有两端 ceil 对应同一服务格时才接受。跨服务边界会拒绝，不能靠任意 Decimal 精度猜测。alpha 输入另与该 predictor 的冻结区间逐字核对。

本审查另外直接解析 02 的 raw stdout，没有导入上述 runner/auditor，使用独立的 `Fraction`/`isqrt` 包围计算（网格 `10^-20`）重建所有候选、逐任务服务格、流时、枚举次序、同分规则和实际查询；同时从全部真实 service/launch 事件重建全程指标。结果如下：

| 独立核验项 | 结果 |
|---|---:|
| 完整 native 实例 / episode | 6 / 98 |
| 实际任务 / requester MOVE | 882 / 1176 |
| cohort 决策 / 完整候选预测 | 72 / 596 |
| 每个候选的当前任务数 | 3 |
| 旧62个 episode 的任务、曲线、flow、查询及收尾结果 | 全部复现 |
| stable-fast / hidden-slow-shock 的历史与冻结模型 | 逐字相同 |
| 上述两组两目标的公共输入、预测候选、选择和查询 | 逐项相同 |
| AR / lag2 在两个目标、六条件的查询与任务结果 | 全部相同 |
| 51个受保护文件 / 9个组件头 / fixture/runner/原auditor | 当前 SHA 与02记录一致 |

第二次原生严格编译8.723秒，六次运行26.308—32.236秒，均在120/60秒限额内，全部 native exit0，合计50,856项原生检查。以上宿主秒数不是生产收费，也不是算法速度基准。

## 结果解释

| 有代表性的固定比较 | 旧 window6 | 新 cohort-flow | 可支持的解释 |
|---|---|---|---|
| alternating-next-slow，AR/lag2 | C；全flow40，首批28 | AB；全flow39，首批27 | 同预测器下目标对齐改善；查询从1增至2 |
| 同慢组，mean3 | AB；全flow39 | AB；全flow39 | 新目标消除AR对该简单模型的任务劣势，没有建立独立学习优势 |
| alternating-next-fast，偏慢 nominal/last/median | C；全flow36 | AB；全flow36 | 多查一次没有任务增益，必须保留负面费用方向 |
| stable-fast，历史预测器 | WAIT；全flow36 | WAIT；全flow36 | 已有历史下省去冗余查询，任务数并未增加 |
| hidden-slow-shock，全部历史预测器 | WAIT；全flow41 | WAIT；全flow41 | 相同可见历史无法识别突变，新目标没有消除预测失误 |
| hidden-slow-shock，固定nominal | C；全flow40 | AB；全flow39 | 强先验在这一负例优于历史模型；不能删去该结果 |

36个目标配对中7个完整任务flow改善1、29个相同、0个变差；这些是固定人工表内的计数，包含共享历史和 quoted 重复条件，不能转成独立样本显著率或泛化概率。首批目标并未看到后续六任务，本例首批改善传播到全程，不等于已优化任意未来队列。所有臂最终任务数均为9，所以不应把流时改善写成最终吞吐增加。

新目标的额外查询有实际代价的可能，但本表仍没有生产 COST/AUTH。人工报价组只检验原 SRDC 正常评分入口；本项目 SRDC、AR/lag2及新目标均是内部规则或消融，不替代作者 PIE-D/GPIBT/OnlineGGO 外部基线。学习贡献仍需同信息的强简单模型之外、完整留出运行上的额外任务与费用收益。

## 失败保留与运行覆盖限界

- **01 是真实 native 失败。** 日志尝试把无理 alpha 输出成有理数，抛 `nonrational output`；其源码快照、已有完整/部分输出和失败原样保留。
- **02 是 native 完成、wrapper 离线观察失败。** 六组都完成后，原 Python auditor 对所有后续 MOVE launch 无条件调用 rational-only `exact_time`，误拒绝决策之后的合法无理时刻。02 的 `failed_or_incomplete` 没有改成 passed，六条错误仍在；新恢复分析有独立身份和 SHA，未再编译或运行 native。
- **active 分支未被本表触发。** 72份 cohort_input 里 active 项为0：先查A还不能启动依赖AB的需求；单C在枚举的等待同分顺序下在第二机会选择。源码的信息边界得到审查支持，但不能称已经运行验证 active 任务预测。
- **不可行分支未被本表触发。** 596候选均可行。源码不会静默漏项，但缺阈值/永久驻留等失败域并非本表的运行证据。无需为扩张本轮结果临时追加实例。
- 原生几何/owner/END/READY检查沿用，但实际服务仍为该夹具声明的 z=0 见证；有非零误差包络不等于本表已经跑了非零横向轨迹。一般碰撞竞争、连续轨迹安全、未返回/缺失标签、地图规模泛化和生产全费用仍需外部共同执行实验。
- `sum(9−completed[t])` 是相对固定九任务全集的描述量，包含尚未揭示任务，不能称活动队列面积。CSV 的单一 `alpha_error_bounds` 取每臂第一条 MOVE；原始12条误差全部在，不能把该列误称12条的平均预测误差。

主要证据：[失败01](objective_task_run_20260929_01.json)、[完整native/失败wrapper02](objective_task_run_20260929_02.json)、[新恢复分析](objective_task_recovery_analysis_20260929.json)、[完整98行结果](objective_task_results_20260929.csv)。02 SHA 为 `73e898313d97d6a37ad9b8f35ef80f4d9586f7ec1b3d1fa8684c0c2d3f1a3520`；恢复分析 SHA 为 `86b94755d708dda1f6ff19a8c6d8fe9acb81b4bd1c7ea4095b8550e43a30c5da`；最终 fixture SHA 为 `cb400935496c3cb56065d2ff1997f1537f30f0b157f783a9aebdc42caed2f72f`。

建议将本轮作为主稿“任务目标为什么必须明确”的机制图和消融证据。下一步先在真实外部算法和统一执行接口中验证同类目标，再决定是否增加残差学习；不要将已解释的目标收益重新命名为学习收益。
