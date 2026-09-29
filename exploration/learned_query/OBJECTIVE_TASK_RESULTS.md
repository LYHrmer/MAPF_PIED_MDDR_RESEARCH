# 当前 cohort-flow 目标消融：方法、结果与失败记录

新目标在慢交替条件下消除了一个已识别的目标错配：AR 和 lag2 从 C 改选 AB，
当前三任务流时由 28 降至 27，完整九任务 episode 流时由 40 降至 39。
AR 仍没有超越 lag2；新目标也没有在这些慢实例中超越既有两步 admission 或 RR。

最终证据身份是：**六组 native 全通过，第二轮包装器分析失败，独立离线恢复分析通过**。
不能把 `objective_task_run_20260929_02.json` 的状态改写为 passed。

## 固定方法与信息边界

运行前合同为 `OBJECTIVE_TASK_CONTRACT.md`。旧窗口 6 规则的 `completion_value`、
`choose_probe` 及六个冻结预测器代码块保持原样；两目标在同一新运行中逐一配对。
新目标只最小化三个当前已分配任务的 `Σ(predicted_service_at − assigned_at)`，
仍使用原有 release / 严格阈值 / END 延迟 / 周期服务 / WAIT-single-pair 候选规则。
查询数量仅同分时比较。未来六个补任务、评价终点、真 eta、控制器实时状态与事后
结束标签均不进入选择器。目标是内部消融，不是外部新基线或全未来最优规划器。

实现提供 active task 的公开 launch-time 与当前公开路线输入，并限制为第一 leg
已公开 grant 的状态；不读 `physical_x` 或 `Controller.snapshot()`。
但本固定表中 **72 次 cohort 输入的 active 项实际为 0**：AB 的第一步 A 尚不能
启动请求者，而可等待的单 C 常在第二机会才执行。因此 active 分支本轮只有源码
复核，没有运行覆盖；不能据此声称一般 active MOVE 评分已验证。
596 个实际枚举候选均可行，不可行候选排除分支同样没有运行覆盖。

## 完整结果

六个实例共 98 个完整 episode、882 个任务、1,176 个 requester 原 MOVE、
50,856 次 native 检查。每个 episode 都完成 9 个任务和 12 个 requester MOVE，
保留 END / READY / owner 收尾检查。编译 8.72 秒；六个 native 实例分别为
26.31、30.10、30.96、27.62、28.40、32.24 秒，均在预声明上限内。

独立恢复分析从原始事件重算了 72 次新目标决策的 596 个候选、每个任务预测服务、
流时与同分规则，并重算全部真实任务服务、查询、曲线及 MOVE 数量。
无理 alpha 以原生精确比较生成的包围区间记录；Python 使用 Fraction 和整数平方根
传播严格上下界，只有两端证明相同服务时刻时才接受，未使用近似中点选择动作。
旧 62 个 episode 的全部结果字段（新的 run 身份除外）逐项复现。

下表每格为“旧窗口目标 → 新 cohort-flow 目标”的 `查询 / 全 episode 流时`；
“同”表示两目标完全相同。quoted 的慢/快组与对应未报价组在这六预测器上结果相同。

| 预测器 | 慢交替 | 快交替 | 稳定快 | 同历史隐藏慢突变 |
| --- | --- | --- | --- | --- |
| nominal | C/40 → AB/39 | C/36 → AB/36 | C/36 → AB/36 | C/40 → AB/39 |
| last END | WAIT/41，同 | C/36 → AB/36 | WAIT/36，同 | WAIT/41，同 |
| mean3 | AB/39，同 | C/36，同 | WAIT/36，同 | WAIT/41，同 |
| median3 | WAIT/41，同 | C/36 → AB/36 | WAIT/36，同 | WAIT/41，同 |
| lag2 | C/40 → AB/39 | WAIT/36，同 | WAIT/36，同 | WAIT/41，同 |
| AR(1) OLS | C/40 → AB/39 | WAIT/36，同 | WAIT/36，同 | WAIT/41，同 |

慢组的首批服务从 C 策略的 `(D3=8, D1=10, D2=10)` 改成 AB 的 `(9,9,9)`。
这改善总流时，但推迟了最早的一项服务，不能称为对整个完成曲线逐点支配。
后续六任务当时尚未揭示，完整 episode 结果只是实际执行后的评价。

36 个有依赖的预测器配对中，7 项流时降低 1，29 项流时相同；其中 7 项多一次查询
却没有服务改善。这个计数不是总体成功率或统计显著性。stable-fast 与 hidden-shock
的历史、每次公共输入、所有候选预测和选择均相同；后者五个历史预测器仍 WAIT/41，
说明目标修正不能凭空推断隐藏突变。

quoted 慢组原 SRDC 确实走 PositiveScore，选择 CA，流时 40；共享 warmup 的 RR
和两步 admission 选择 AB，流时 39。新目标 AR/lag2 也为 AB/39，未胜过这些强简单
对照。quoted 所有臂都有六次真实共同初始化 POSITION，另行计数；报价是人工 admitted
native 诊断收据，不是生产 COST，也没有测量模型维护与查询的完整付费成本。

## 两次尝试与离线恢复

1. `objective_task_run_20260929_01.json`：严格编译通过，但新日志将无理 alpha 交给
   仅支持有理数的 `exact()`，六实例报 `nonrational output`。回执和源码快照保留。
2. 唯一修复只把该日志改为严格区间，预测器、目标和选择语义未改。
   `objective_task_run_20260929_02.json` 的六 native 命令均 exit 0、各自 summary passed，
   全部 98 episode 完整；之后包装器把决策结束后的无理 MOVE launch 当成精确有理日志，
   报 `public launch must have an exact recorded time`。失败状态原样保留。
3. 根明确授权独立离线恢复，无额外编译或 native 重跑。
   `objective_task_recovery_audit.py` 只在当前 cohort 决策尚未完成时收集公开 launch；
   后续原始服务事件仍用于完整九任务评价。`objective_task_recover.py` 验证具体失败身份、
   原生成功/摘要、源快照、旧结果、严格预测区间及真实任务指标。
   `objective_task_recovery_analysis_20260929.json` 为其独立 passed 结果。

原 fixture、runner、原 auditor、两次回执和旧 62-episode 文件均未因恢复被改写。
原 `objective_task_analyze.py` 是为 successful wrapper 设计的早期分析入口；本次交付
应使用下面的 recovery 入口，并保留它与原包装器的不同身份。

```bash
rtk proxy python3 -B exploration/learned_query/objective_task_recover.py \
  exploration/learned_query/objective_task_run_20260929_02.json \
  --csv /tmp/objective_task_rechecked.csv
```

CSV 以排他创建方式写入，目标必须不存在。完整表为 `objective_task_results_20260929.csv`。

## 论文贡献建议与下一步限界

本轮最清楚的机制证据是：固定预测能力时，窗口完成数与当前任务流时可能选择不同
查询组合；预测误差降低本身不能保证任务目标改善。公开历史可作为可替换性能层，
但当前 AR 与 lag2 相同，不能包装成独立学习贡献。有限场景中的目标修正也尚不能
独立承担论文新颖性，因为既有简单两步 admission / RR 已达到同样慢组流时。

后续应在公开非齐次任务中辨识目标差异、覆盖决策时已有 active MOVE 的状态、保留
强简单对照和完整 episode 留出，再判断可见特征是否留下值得学习的预测残差。
生产付费闭环、多任务地图、一般冲突与模型维护开销仍未解决；本轮不据 SCI 二区/
三区投稿目标夸大有限证据，也没有继续扩大实例或调整参数追求正结果。
