# 完整 ADDRESS 两项失败记录 DEV：当前后段恢复候选停止

2026-10-18。用户明确回复“授权这2项”后，按冻结顺序执行 random32、maze32；两项全部 COMPLETE，零重试，许可已消费。科学代码固定 `b0fa19e2b01d043968228a2d9e9c285eb3d3d9f7`，清单 SHA `edf8516ab73919c0fedc0542c407c5775f8601383259f69ead6949146f43c2f3`。这是完整 ADDRESS 的功能与失败分类 DEV，没有运行恢复、训练、world 或大论文运动任务。

## 完整任务结果

| 任务（各32车） | SOC 初→末 | makespan 初→末 | 总准入 wall | 原生 CPU | 修复次数 / SIPP调用 | 修复终止分类 |
|---|---:|---:|---:|---:|---:|---|
| random-32-32-10 s01 | 771→771 | 53→53 | 9.176288373 s | 9.000352829 s | 5 / 23 | 5 COST_STOP |
| maze-32-32-2 s01 | 1873→1866 | 129→129 | 0.489910144 s | 0.319070167 s | 16 / 108 | 12 COST_STOP、2 FOUND接纳、2 FOCAL_DRAINED_EMPTY |

两项均在15秒总准入、各进程10秒CPU和512 MiB地址空间限制内退出0，无强制清理；原生、外部和另一个代理独立实现的离线检查均确认最终32车路径合法，包含障碍、邻接、顶点冲突、对向边冲突和永久终点驻留。maze 的两次接纳分别减少2、5步，均来自原 ADDRESS，不能归于未执行的恢复机制。

random 在 GROUP 阶段触发9秒绝对CPU软截止后输出合法原方案；maze 正常完成16次已构组修复。二者均未触发实际 SIPP deadline、局部 repair deadline 或预处理回退。单次 DEV 不证明任意输入的返回保证；两案与旧结果共享任务，不能作为独立性能样本或稳定加速证据。

## 失败位置改变了候选判断

17 次 `COST_STOP` 的所有组内车辆均已返回 `FOUND`，停止发生在最后一辆返回后的累计成本检查；9 次候选成本等于旧组、8 次更大。`primary_complete=false` 在这里表示未到达primary完成标记，不表示单车未找到路径。`final_group_cost` 是回滚后的旧成本，候选成本须从该次 `primary_returns.path_cost` 求和，不能用它替代。它们不是“搜索到后段无路可走”的失败标签；单车FOUND也不单独认证被拒候选的联合可行性。

仅有两个正常空返回，均在 maze 的 agent 26：

| attempt_id | 组大小 | 失败零基位置 / 日常序号 | 已找到路径的前缀车辆 | 返回类别 | 原后段门槛 |
|---|---:|---|---|---|---|
| 5 | 6 | 1 / 第2辆 | 5 | FOCAL_DRAINED_EMPTY | 1 < floor(6/2)，不满足 |
| 16 | 8 | 3 / 第4辆 | 31、5、16 | FOCAL_DRAINED_EMPTY | 3 < floor(8/2)，不满足 |

两次均无局部/全局到期，属于固定作者源码的正常空返回位置；没有进行阻挡检查，原因不能进一步写成“被新前缀挡住”，也不能据此证明不可行或可恢复。两案满足预注册后段条件的正常空返回均为零；旧固定ID、带剩余成本cap探针的13/17后段现象没有在本批完整 ADDRESS 中得到对应证据。

**决定：停止当前材料上的后段失败恢复候选，不准备其收益比较或训练。** 保留已有预算、日志和恢复实现，不删除负结果；不把第4/8辆重新定义为后半段、不让成本停止进入原触发条件，也不追加场景追求正例。这不是所有局部恢复无效的证明；“恢复是否比继续选邻域划算”仍没有直接性能比较，本批给出的结论是当前候选未通过进入该比较的机会门槛。

## 完整费用及下一项诊断

| 本次测得的区间 | random32 | maze32 |
|---|---:|---:|
| primary 搜索 wall 合计 | 6.046748 ms | 278.238718 ms |
| runPP 尝试 wall 合计（trace写入前） | 6.091463 ms | 278.531740 ms |
| rollback wall 合计（包含在上行） | 0.005906 ms | 0.050903 ms |
| trace 写入/flush wall 合计 | 0.104548 ms | 0.237586 ms |
| 原生 main 至收据前 wall | 8.998065176 s | 0.317169271 s |

这些阶段嵌套于总准入，不能重复相加。CPU子区间存在毫秒级计时粒度，记录0不代表没有开销。总准入包括启动、输入检查、构造、求解、末检、输出与工件哈希；父管理收据写入和进程退出另由20秒TERM+2秒KILL外层保护覆盖。

random 的260497次构组调用只有5次进入 runPP；已测尝试合计约6.1 ms，说明本次大量时间位于这些尝试之外，但尚无构组内部阶段计时，不能将其余时间全部归于构组或声称均可省去。下一项应先在已有源码与日志中定位非runPP重复工作，并分清等成本与变差修复的接纳条件，提出一个共享工程优化之外的具体差异；需要新计时字段时仅做必要实现。当前不将经典下界、少调用或新学习评分器直接升格为方法贡献，也不建立新的运行清单。

## 可复核证据

- [真实授权](results/address_attempt_trace_v1/AUTHORIZATION.json)、[总收据](results/address_attempt_trace_v1/RUN_RECEIPT.json)，后者 SHA `308e5a65e98270b6049336dff0c50da88bbbf137755fc2875a9203d91d5a8632`；原27项工件和收据保持原字节。
- [random 原始逐次记录](results/address_attempt_trace_v1/random-32-32-10__s01__n32__attempt_trace/attempts.jsonl)、[maze 原始逐次记录](results/address_attempt_trace_v1/maze-32-32-2__s01__n32__attempt_trace/attempts.jsonl)。全部131次单车调用中129次FOUND、2次正常空返回；未删除19次未接纳尝试。
- [独立离线核验脚本](results/address_attempt_trace_v1/INDEPENDENT_AUDIT.py)、[核验结果](results/address_attempt_trace_v1/INDEPENDENT_AUDIT.json)、[审阅者及文件摘要](results/address_attempt_trace_v1/INDEPENDENT_AUDIT_PROVENANCE.json)。由另一个代理复算，非外部人工评审或独立科学实验；原总收据之后附加，不改写原工件清单。

复核无需任何搜索：在固定SCI工作树执行 `rtk proxy python3 -B tracks/sci/results/address_attempt_trace_v1/INDEPENDENT_AUDIT.py`；输出到 `/tmp/mapf_trace_independent_audit.json`，不覆盖仓库证据。原运行命令只作为[已消费清单](ADDRESS_TRACE_CHECKLIST.md)的历史记录，不能重复执行。
