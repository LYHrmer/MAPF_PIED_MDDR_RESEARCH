# 两个已完成差异 case 的事后机制核查

这是根据正在运行的冻结留出矩阵提出的只读诊断，不是新增科学实验，也未用于调参、改模型、改 guard 或修改后续矩阵。`mechanism_diagnose.py` 只读 episode/CAS，核内容 SHA 后比较完整依赖方向及按 `(START/END, vertex)` 对齐的实际事件。没有运行 solver 或重新执行物理轨迹。原输入 episode、收据 SHA、相关图/model CAS 引用和逐 agent 完成差分均保存在 `TWO_CASE_DIAGNOSTICS.json`。完整独立物理审计由另一审核器承担。

| world | history 无查询 | learned 无查询 | EWMA 无查询 | history 结构查询 | learned 结构查询 | EWMA 结构查询 |
|---|---:|---:|---:|---:|---:|---:|
| maze s06 N32 bounded_pause | 5005 | 4916 | 4968 | 4894 | 4954 | 4876 |
| random s07 N32 speed_shift | 915 | 911 | 911 | 915 | 911 | 911 |

表中为实际 ΣT。maze 三个结构臂均查询 32；random 分别查询 19/18/18。不能只取 learned 无查询优于 history 的单元而忽略强 EWMA、结构查询回归和两者交互。

maze 的 history 与 learned 无查询首次方向差在 gate 4、t=54：双方原先均有 `dg_agent23_26` 正向，十条依赖的所有正反候选头均为 STAGED，switchable 与 horizon 均为 true。history 合法反转该组，learned 保持；两候选均通过，最大行残差约 `1.071e-10` 与 `2.309e-14`。实际 `v_30_30` START 为 history 54／learned 72；`v_23_27` START 为 72／61。因此差异已经进入真实执行事件，不是预测目标或查询数量的变化。

但最终 −89 **不能全归为纯预测收益**。history 首次拒绝在 t=161.5，learned 在 t=172.25，均晚于首个物理差异；之后 history 在 t=172.25、183 的 `dg_agent4_7` 翻转候选因最大行违约约 90.78 被拒绝，直到 t=193.75 才通过并实际翻转。learned 的后期拒绝序列不同。t=161.5 history 的 `1.0000000012e-5` 位于固定容差边界附近，也必须保留；本次不改变容差。结果包含估计、合法顺序、依赖传播及数值拒绝回退的整链效果，未运行反事实拆解。最终十个 agent 的 ΔEND 合计 −89，其中 agent1 −31.75、agent20/29 各 −18.75、agent4 −29.75，另有正负抵消；makespan 均279。

random 则是更干净的机制例：所有八臂均无求解拒绝。history_structural 与 learned_structural 首差在 gate 6、t=28.25 的 `dg_agent3_6`，原 `v_3_21 → v_7_29`；两候选头 STAGED 且在 horizon 内，learned 改为 `v_7_30 → v_3_20`，history 保持，两解残差约 `2e-15`／`3.8e-15`。实际 agent7 的 `v_7_29` START 从34提早到29，agent3 的 `v_3_20` START 从30延后到31。最终 agent7 END −5、agent3 END +1，ΣT −4，makespan 同为81。

random 的相同预测器下无查询／结构查询完整 START/END 时刻均相同，只改变查询数量。learned 与 EWMA 在该例也具有相同完整事件时刻。因此这里不是“学习修复了付费查询的伤害”，而是 learned 和强非学习 EWMA 都选择了相同的更好顺序；结构查询没有额外可观测执行收益。无即时收益不意味着这些查询在其他时刻或其他输入永远无价值。

复核命令：

```sh
rtk proxy python3 -B mechanism_diagnose.py --world maze-32-32-2__s06__n32__bounded_pause --world random-32-32-10__s07__n32__speed_shift --output mechanism_review/TWO_CASE_DIAGNOSTICS.json
```
