# ADDRESS 共用预算退出层：实现与软件证据

2026-10-18。本文记录`101f18c`的源码适配、软件夹具、完整编译和 `--help`；该实现阶段没有运行MAPF任务。后续按新授权完成的三项真实功能DEV见[单独结果](ADDRESS_BUDGET_RESULT.md)：random32本次在构组软截止后返回合法方案，未触发SIPP内部截止或预处理回退。本层完善强基线，不作为论文创新。旧失败见 [根界DEV结果](ADDRESS_GUARD_RESULT.md)。

## 当前实现

[`address_budget.py`](address_budget.py) 在固定作者代码、公共初解适配和根界guard之后应用；[`address_budget_support.h`](address_budget_support.h) 提供一次配置的预算状态。作者checkout、旧二进制、旧清单和旧运行证据未修改。

- `budget_guard` 不引入恢复诊断；构组调用、Bernoulli种子循环、random-walk、SIPP展开、safe-interval与占用时间扫描、支配检查、路径重建均有合作式截止检查。未加括号的 `PathTable::getHoldingTime` 循环亦被明确补齐。
- 全局墙钟截止为原生main入口加 `cutoffTime-finalReserve`。CPU读取 `CLOCK_PROCESS_CPUTIME_ID` 的**绝对进程CPU**，截止为 `cpuLimit-cpuReserve`，没有把main入口前的CPU另加回限额。外部Python入口至产物哈希仍由共同runner独立核验；启动开销和末尾管理边界不能省略。
- 每次修复沿用作者 `T=min(剩余时间,replan_time_limit)`，用 `RepairScope` 让所有该次SIPP调用共享局部截止。局部到期可继续选下一个邻域；全局到期退出优化。CPU限额始终为全进程共享。
- SIPP内部截止返回空路径并明确记 `DEADLINE`，清理其已注册节点。支配检查中尚未注册的新节点有异常所有权保护。deadline后的FOUND也拒收。公共runPP保留作者完整rollback：删除已插入的新路径，恢复全部邻域旧路径和reservation table；保留原奖励更新代码与顺序。
- 在构造LNS/静态heuristic之前，先独立读取并验证完整初解。heuristic构造到期时丢弃未完成对象，重新完整检查并输出该初解。初解读取、验证失败不会伪装成成功。正常路径仍走作者验证、适配器完整验证和最终输出。
- 节点释放、rollback、最终完整验证、输出不再次受同一软截止打断；它们使用保留时间并继续受外层CPU/墙钟/内存硬限及总准入约束。receipt记录共同预算参数、CPU、截止阶段、构组/SIPP/rollback计数及fallback；正常输出失败或超总限仍失败。

这是一套合作式预算边界，**不是任意输入规模下的硬实时保证**。输入加载/完整校验、容器操作、清理与输出并非全部可抢占。两次初解检查、异常清理及checkpoint开销全部计入实际成本。1秒CPU/墙钟收尾reserve已在本次random32构组退出场景通过，其他真实截止位置和更大任务尚未验证；不能沿用已消费许可。相对原方法强化了每次修复T的截止，因此未来各比较方法必须共同使用这一层，不能与旧软T结果直接宣称算法加速。

## 已完成核验

[`test_address_budget.py`](test_address_budget.py) 的6个软件测试通过。夹具抽取固定作者的实际方法，使用小型假图、假时钟或假搜索回调，不构造作者Instance，不调用科学任务。

1. 正余量且构组始终失败：旧实际控制流达100次proposal仍未耗已构组迭代额度；新层在假截止前停止，仍到达末检输出。
2. 单次SIPP及首次safe-interval内部：旧实际方法在假图展开41个节点才返回；新方法在内部截止并清空节点，标记DEADLINE。该夹具仅复现无内部截止的控制流，不声称复现random32最后卡点。
3. 假搜索在第2或最后一个FOUND返回时到期：实际runPP恢复完整邻域及table，最终完整检查和输出成功；未到期对照接收合法改善。
4. 绝对进程CPU截止、局部截止退出后复位、尚未纳管节点的异常释放。
5. 原奖励块、完整rollback逐字保留，重复overlay拒绝。
6. 实际heuristic方法在构造阶段到期，已预验证初解重新验证后按作者路径格式输出。

完整 `budget_guard` 构建和 `--help` 成功，见 [构建收据](budget_guard_build_receipt.json)，二进制位于 `.address_budget_guard_build/build/address`，SHA `6d94e123a7a825e65aaaa7a30339de49856b98e60e841980eae671051c374c33`。收据记录全部作者输入、overlay、编译器、阶段和二进制身份。未复制作者源码到提交中。

```bash
rtk proxy python3 -B -m unittest test_address_budget -v
```

上式在 `tracks/sci` 运行，仅为软件核验。新科学功能命令和输入预算由单独清单固定；本文件不能授权运行。

## 恢复候选的明确边界

`budget_recovery` 可以在源码层叠加同一SIPP/主修复截止，其6个实际翻译单元的syntax-only核验通过。尚未完整构建或运行该变体。其内部仍保留旧 `recovery_deadline_ns` 和诊断协议：恢复入口可能在检查stop前做完整诊断校验，CPU截止未贯穿全部恢复诊断。因此**完整恢复预算公平性尚未闭合**，共同runner仍拒绝该变体，不准备恢复比较清单。

强基线的三项功能验收已完成，覆盖范围见上述结果。下一步将恢复内部改成唯一公共截止、把诊断/候选验证与剩余预算合并，核对真实失败机会后再与继续选邻域、随机重排和适配优先级搜索比较。新层未证明恢复收益或学习价值。

当前构建入口和runner已发生变化。旧manifest保持原SHA不刷新；复核或重建旧版本须回到其固定历史提交，不能用当前源码冒充旧产物。
