# ADDRESS费用归因：三轮实现与6项待授权诊断

状态：实现、编译和人工软件夹具已完成；**新科学任务0项，诊断6项待授权**。旧36项及此前许可均已消费，不可复用。本轮没有改选择器、奖励记忆、局部期限、候选或最终合法性检查，也没有训练、恢复或实机运行。旧论文作者源码、原清单与冻结结果保留。

## 第一轮：保留首次观察到截止的证据

**问题。** 已完成36项中的maze32有83.019% selection截尾；旧`last_stage`会被后续检查覆盖，无法据其判断首先在哪个检查点发现到期。

**实现。** 共同预算模块增加显式`costDiagnostics`开关，默认关闭。在既有`expired()`的同一次wall/CPU采样上记录首次任意、首次有效局部wall、首次全局截止观察；保存检查点、三个真实触发标志、已观察时钟值和对应期限。每selection重置事件观察，整项另保留运行观察；`last_stage`继续记录最后检查点。全局CPU触发时，旧`repair_deadline`仍可能置位，但不会伪造新的局部wall触发证据。

**软件证据。** 人工时钟验证局部先到、随后全局CPU到期及重复检查不覆盖首次；CPU-only不误写局部wall；同时触发的记录必须一致。外部核验拒绝漏项、后写覆盖和显著越过期限却标false的记录，允许double秒量化到整数ns时同一ns格内的边界。默认关闭不新增时钟采样。

**待实测。** 新记录是first observed，仍不是时钟真实越界瞬间。`local_wall_limit_ns`是`min(global_wall_stop, repair_start+T)`的有效局部边界；全局wall截短T时两者可同时触发，不能声称原始T独立到期。首次实际发生在哪一阶段须等新诊断。

## 第二轮：把校验费用、搜索状态和提交结果接通

**问题。** 旧498条`REWARD_VALIDATION`截尾有完整fresh路径，但未验证，也包含`COST_STOP`；其整段selection时间不能全部归到校验，更不能当作498次有效改善丢失。

**实现。** 在现有修复循环退出、`primary_done`前记录时间和原始停止状态，再用已置位截止标志和remaining数量区分实际循环出口；不新增`expired()`检查。候选校验用RAII计时，覆盖正常、截止和异常展开。费用关系为：

```text
selection（日志前） ⊇ 搜索循环结束至结算（日志前） ⊇ 候选完整性校验
搜索后费用 = 候选校验 + 搜索后其他
候选校验 = 路径/地图物化 + 联合合法性检查 + 校验其他
```

wall与process-CPU分别核账。三个校验子段互斥；异常展开和清理计入异常发生时活动子段，联合检查费用不等于纯验证算法计算时间。日志费用另有原生汇总，所有计时、字段构造、日志与外部核验仍在既有总准入wall内；上述嵌套费用不可相加成总成本。

事件同时记录search返回、fresh/remaining、进入校验、最后校验阶段、校验结果、实际提交及截尾。截尾实际提交改善为0，未验证候选的潜在改善保持未知。`topAgents`完成构池处记录同一次selection的eligible/top-k候选数；中断或未进入构池为null，不能用全run累计选过的不同seed数代替同次选择空间。

**软件证据。** 实际覆盖层配合假图、假规划器及人工时钟验证：接受、部分路径、搜索截止、成本停止、物化截止、联合检查截止和完整回滚；外部validator拒绝嵌套双计费及伪造完整pool。实际种子选择函数的人工夹具验证完整pool为2及中断pool为unknown。新`ADDRESS_REWARD_COST_V1`字段只在开启诊断时要求；旧36份V1账本21,873条事件的返回摘要与冻结worker摘要逐项完全一致。

**待实测。** 已具备归因观测能力，尚未获得公共复制/校验开销比例、预算失配或奖励改动收益结论。完整fresh、FOUND、通过校验和实际接受分别记录。

## 第三轮：编译、兼容核验及有界清单

**问题。** 诊断必须进入完整构建和原有预算/核验流程，且不能把旧许可或旧无计时运行当成新实验对照。

**实现与软件证据。** 在只读作者commit `b3d35c431ce03834f95e834d87986f2f341394a1`之外构建完整reward overlay；仅执行编译和`--help`，未构造作者Instance。诊断`inspect`只核验冻结bytes和JSON，测试通过mock保证不调用`unpack`构造GridProblem。软件结果及命令见[核验收据](derived/reward_cost_diagnostic_software.json)，完整构建见[构建收据](reward_cost_diagnostic_build_receipt.json)。

- [新manifest](config/address_reward_cost_diagnostic_v1_manifest.json) SHA：`baf2255de8838c2d3bc2dc253523693fe78f9e3ceb24a04dad495a1b0aedf3cd`。
- 二进制`.address_reward_build/cost_diagnostic_v1_final/build/address` SHA：`56348dd7b42a51ad5f94e90a5bb07328f2010159b07ee42722c8798c56d39609`。
- 构建收据SHA：`1d526714bb44523697089a683baa8d8f0b267e44c2e1a09bfb77b2b033fdafc2`。
- 直接复用[旧冻结输入bytes](config/address_reward_holdout_v1_inputs.json)，SHA：`660b7bc4b4282db1feedd373a9220dc98638c18bcb835123aff448c83eadcf3e`；输入包含原四任务，但新jobs只选择下表两个既知任务，无新初始规划。

| 固定完整任务 | 车辆 | 初始SOC | 种子 | 模式 |
|---|---:|---:|---|---|
| maze-32-32-2 / s05 | 32 | 2000 | 0/1/2 | author，window=0 |
| random-32-32-10 / s05 | 32 | 753 | 0/1/2 | author，window=0 |

两完整任务、任务内三个seed，共6项。执行顺序按manifest：每seed先maze32再random32。使用positive_delay、邻域上限8、top-k=32、PP/SIPP、原局部比例1/100、同一冻结初解及完整合法性检查，无修复次数上限。它们是已用于设计的同源DEV诊断，不能称新留出验证；与旧未加诊断的wall不能作配对速度比较。本批没有奖励模式对照。

每项总成功准入wall≤5秒，原生及外部各预留1秒wall、原生预留1秒CPU；worker与native各CPU≤10秒，地址空间≤512MiB、单文件≤16MiB。6项成功准入wall合计上限30秒；每项外层10秒TERM+2秒KILL，硬保护合计上限72秒。收据落盘/管理退出受外层保护，不能把外层保护当作更多搜索预算。

**待实测与停止规则。** 新batch为`address_reward_cost_diagnostic_v1`，状态`PENDING_USER`；先保存对应真实新授权、manifest SHA、已推送SCI提交，再逐项串行运行。零重试，任一SHA变化、异常、超限、非法或不完整结果、非零退出、强杀、账本不闭合或缺文件，立即关闭余下许可；失败和未运行项完整保留。软截止后合法返回不算硬失败。已存在的输出目录拒绝覆盖。无结果筛选、追加seed或改任务追收益。

只读检查命令：

```bash
rtk proxy python3 -B tracks/sci/run_address_adapter.py inspect --manifest tracks/sci/config/address_reward_cost_diagnostic_v1_manifest.json --sha256 baf2255de8838c2d3bc2dc253523693fe78f9e3ceb24a04dad495a1b0aedf3cd
```

获得本批真实新授权后，首项命令格式如下；当前未执行：

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_reward_cost_diagnostic_v1_manifest.json --sha256 baf2255de8838c2d3bc2dc253523693fe78f9e3ceb24a04dad495a1b0aedf3cd --job maze-32-32-2__s05__n32__seed0__author --authorization-reference '<本批真实用户授权引用>'
```

完成或首硬失败后用原有`repair_profile.py address --manifest … --sha256 …`离线核验，不运行新搜索。一次诊断后立即分叉：若费用主要来自共同实现，先修公共组件；若仍有重复出现的预算失配及在线可观测决策信息，才准备单一小原型和强对照。若未定位或只有截尾率变化而无最终质量证据，不追加奖励变体、恢复或旧排序。
