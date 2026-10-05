# R19 全量失败候选复算

324 个已执行 episode 全部纳入只读审计；总登记分母仍为342，另18行初始 ECBS 失败没有被替换或伪装成执行 episode。此次审核新增 solver／物理执行均为0。`FINAL_SOURCE_BINDINGS.json` 核全部冻结 source pins、作者及隔离编译适配文件、324份 episode 与 RUN_RECEIPT 哈希，全部通过。

**135 条拒绝记录／77 个独特失败输入均通过独立 Decimal 复算：拒绝依据真实存在，不是把作者 OPTIMAL 状态当作可行保证。** 77次为原始作者调用，58条为完整语义相同的负缓存复用，不是重试。135条均标记 OPTIMAL，最大行违约最高109.339996965；边界与整数性最大违约均0，全部保留原父图。涉及23个 episode，均在 maze s06 N32：stable42条、bounded_pause38条、speed_shift55条。

| 分层 | 拒绝记录 | 独特输入 |
|---|---:|---:|
| 紧邻固定 `1e-5` 容差（≤`1.01e-5`） | 12 | 10 |
| 明显行违约（≥0.001） | 123 | 67 |

这只是事后诊断分层，未改变接受阈值或重跑输入。去重模型中，违反行包括 action duration、type1先后、fixed type2与少量switchable forward big-M行。75/77输入有涉及未完成动作的违反行，不能把问题全部解释为无关的已完成历史；6个失败候选拟改变组方向，但全部被拒绝且父图逐组件保留。最大违反行是固定type2，不能仅据结果把根因归为某一条big-M约束。

全部失败 payload 均检查：变量总数等于唯一变量名数（4287–4300），row/objective项全部解析到唯一保存变量，保存数量与原模型记录一致。因此排除了此批数据中按name字典发生变量别名／覆盖制造假残差的解释。本次也没有重复rowname；审核仍按constraint list位置 `row_index` 定位，重复标签本身不会被当作算法错误。完整系数、常数、方向、变量边界、类型、取值和独立objective复算保存在原CAS及审核文件。

这些证据证明当前接口返回的一部分 incumbent 不满足保存的完整输入模型，并证明共同拒绝回退有效；**尚未证明具体 CBC／Python-MIP 根因**，也没有证明另一优化器更可靠。不同臂触发不同拒绝时刻，因此有拒绝world的最终ΔΣT不能完全归于预测精度。下一步优先验证已复现 ImprovedGSES 的共同执行接口，详 `../EXTERNAL_BASELINE_NEXT.md`，而不是据此调整本轮阈值或选择性删除失败。

审核文件：`FAILURE_PAYLOAD_AUDIT.json` 保存135条逐行复算及324输入哈希；`FAILURE_STRATA.json` 按完整输入键去重，并保存每键全部出处、严重度、最差行和拟翻转组；`FINAL_SOURCE_BINDINGS.json` 保存源码、episode收据和机制链一致性核验。压缩镜像与文件哈希由 `FINAL_REVIEW_MANIFEST.json` 绑定，原可读JSON保留。

复核命令（均零新科学求解）：

```sh
rtk proxy python3 -B audit_solver_payloads.py
rtk proxy python3 -B summarize_failures.py
rtk proxy python3 -B verify_final_bindings.py
```
