# 按接纳必要条件跳过候选校验：共同工程实现与4项待授权DEV

2026-10-24。[六项费用诊断](ADDRESS_COST_RESULT.md)已定位项目 `reward_contract` 覆盖层的冗余：random32中候选校验占selection约79.41%，其中99.42%用于已因成本停止而不满足接纳条件的候选。当前完成最小可选优化、人工软件验证、完整编译/help和新清单静态核验；**新优化科学运行0项**。六项旧许可已消费，本页四项须新授权。它是共同工程完善，不是作者原版ADDRESS的缺陷，也不是独立创新或新奖励机制。

## 改动及边界

新增 `--candidateValidation all|acceptance_eligible`，默认 `all`，旧默认的账本结构保持兼容。首版 `acceptance_eligible` 仅允许 `author` 奖励模式，并由独立 `candidate_validation_v1` 运行协议显式选择。

完整fresh候选仍先经过原来的入口截止检查。之后使用当前实际变量核对作者既有接纳必要条件：

```text
remaining_agents == 0  且  fresh_cost_sum <= old_group_cost
```

若不满足，则跳过路径/地图物化与联合候选几何校验；日志记 `SKIPPED_ACCEPTANCE_INELIGIBLE`，理由为 `REMAINING_AGENTS` 或 `COST_EXCEEDS_OLD`。不根据 `COST_STOP` 诊断标签判断，不因fresh齐全就将remaining改成0；`<=`保持原条件，不偷换成严格`<`。当前实际PP在成本达到旧组成本时先break、再递减remaining，所以等成本完整fresh通常仍remaining=1；人工边界另验证remaining=0、等成本时仍完整校验。

跳过后 `candidate_validated=false`、`candidate_subset_soc=null`、`candidate_reward=null`，实际提交收益为0。新增 `fresh_cost_sum_unvalidated` 仅是已产生路径的成本和，不是联合可行性证书或完成候选奖励。原author后验更新公式和位置、回滚、一次结算、预算阈值、可能接纳候选的完整验证及最终完整方案全检保留。新增外部核验拒绝漏记policy、错误remaining、伪造skip、候选奖励回填和重复结算。

RAII费用仍记录入口截止检查和门控的常量开销；被跳过者的物化/联合校验费用必须为0，不能把所有候选检查成本记为0。节省的时间可能使原本会截尾的尝试正常回滚，改变后续修复次数、截止分类和随机轨迹。被预先拒绝的候选也不再提供内部几何错误的联合诊断；可能接纳的无效候选仍完整检测、回滚并失败。因此不声称所有控制流、错误发现或后继序列完全等价，也不以较低截尾率代替最终质量收益。

期刊思路仅作设计参考，定点原理映射见[文献复现入口](REFERENCE_REPRODUCTION.md)：先用廉价必要条件缩小昂贵评估对象，必要验证与费用边界仍保留。本实现没有复制L-GLS/X*作者代码或移植其理论保证。

## 软件与构建证据

- 既有三个测试模块共53项人工软件夹具通过，25.341秒；没有作者Instance、SIPP或真实任务搜索。
- 新实际覆盖层夹具覆盖完整改善、等成本/变差成本停止、部分路径、搜索/入口截止、可能接纳但联合非法、author后验不变、回滚、一次结算及最终全检。单独边界确认remaining=0且等成本仍完整验证。
- 独立只读复核的人工夹具另覆盖remaining=0但成本大于旧组成本，以及同一候选入口已到期时必须先记DEADLINE而非skip。
- 新分析器逐项复算旧36份/21,873条事件及刚完成6份/1,893条事件，42份返回摘要与原worker精确一致，无搜索、无证据回填。
- 完整构建只编译和`--help`成功。作者源码、旧六项清单、总收据、独立审计和旧二进制SHA不变。

详见[软件收据](derived/candidate_validation_gate_software.json)及[新构建收据](candidate_validation_gate_build_receipt.json)。新二进制 `.address_reward_build/validation_gate_v1/build/address` SHA `eb5dd7e0d4c5c16a2db30714521329bc6a81227ac9f74e6a50db94d91575e61f`，构建收据SHA `80096095df3a9bd932f79b01ba5c13e0b8327f2ff36b5eb0f61773827533bc21`。旧科学代码固定 `e8edaff`、结果固定 `65d7211`；当前源文件变化后不得重签旧清单，旧运行仅能在其冻结代码树恢复。

## 四项配对DEV提案

[manifest](config/address_candidate_validation_v1_manifest.json) SHA `4aa5d08c349d532f5d7cbcb32f817721e1becb2f4e8d00509716ad8fc382ad8b`，状态 `PENDING_USER`。直接读取旧完整初解输入，SHA `660b7bc4b4282db1feedd373a9220dc98638c18bcb835123aff448c83eadcf3e`，无新初始搜索。固定顺序如下：

| 顺序 | 任务 | seed | candidateValidation |
|---|---|---:|---|
| 1 | maze-32-32-2 / s05 / n32 | 0 | all |
| 2 | 同上 | 0 | acceptance_eligible |
| 3 | random-32-32-10 / s05 / n32 | 0 | all |
| 4 | 同上 | 0 | acceptance_eligible |

四臂共用同一新二进制、原作者后验、正延迟初始种子、top-k=32、邻域上限8、PP/SIPP、局部期限比例1/100、成本诊断开关、缓存机制及初末全检；不改奖励/窗口、预算比例、候选组生成或邻域大小。每项总成功准入wall≤5秒，原生及外部各预留1秒wall、原生预留1秒CPU；worker/native各CPU≤10秒、地址空间≤512MiB、单文件≤16MiB，外层10秒TERM+2秒KILL。总准入上限20秒，外层保护上限48秒；保护时间不转为额外搜索预算。

此批按固定总预算比较最终完整SOC，辅以makespan、全部费用、接纳/回滚/截尾/skip和修复数。每次selection可比较已记录费用构成，但修复数量和后继选择可能不同，**不属于固定修复次数的等工作量加速实验**。两任务都已参与设计、仅seed0，是共同工程DEV；若只有费用降低而质量不变，就报告工程收益，不包装为路径质量贡献。若更慢、输出不合法或不完整，保留退化并停止该实现。只有共同修补后的强基线还暴露稳定选择空间，才考虑单一学习机制；不因本批准备而启动训练。

已执行只读检查，返回四项 `PINNED_BYTES_AND_JSON_ONLY`，没有构造问题或搜索：

```bash
rtk proxy python3 -B tracks/sci/run_address_adapter.py inspect --manifest tracks/sci/config/address_candidate_validation_v1_manifest.json --sha256 4aa5d08c349d532f5d7cbcb32f817721e1becb2f4e8d00509716ad8fc382ad8b
```

**以下命令尚未执行，须取得本清单的新明确授权。** 逐项串行，每项完整收据通过后才可下一项；零重试，任一SHA漂移、硬退出、超限、缺产物、不完整/非法最终方案或账本不闭合，立即关闭全部剩余项。所有失败及未运行项保留，不换任务、不补seed。结果独占 `tracks/sci/results/address_candidate_validation_v1/<job>/`，已存在即拒绝覆盖；本轮该结果目录尚未创建。

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_candidate_validation_v1_manifest.json --sha256 4aa5d08c349d532f5d7cbcb32f817721e1becb2f4e8d00509716ad8fc382ad8b --job maze-32-32-2__s05__n32__seed0__all --authorization-reference '<本批真实用户授权引用>'
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_candidate_validation_v1_manifest.json --sha256 4aa5d08c349d532f5d7cbcb32f817721e1becb2f4e8d00509716ad8fc382ad8b --job maze-32-32-2__s05__n32__seed0__acceptance_eligible --authorization-reference '<同一批授权引用>'
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_candidate_validation_v1_manifest.json --sha256 4aa5d08c349d532f5d7cbcb32f817721e1becb2f4e8d00509716ad8fc382ad8b --job random-32-32-10__s05__n32__seed0__all --authorization-reference '<同一批授权引用>'
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_candidate_validation_v1_manifest.json --sha256 4aa5d08c349d532f5d7cbcb32f817721e1becb2f4e8d00509716ad8fc382ad8b --job random-32-32-10__s05__n32__seed0__acceptance_eligible --authorization-reference '<同一批授权引用>'
```

完成或首次硬失败后，原有 `repair_profile.py address --manifest … --sha256 …`核验全部终态和配对，既有AUTHORIZATION、逐项attempt/receipt及总收据流程不变。实际授权文件只记录用户指示，本身不能授予许可。旧六项诊断许可不能用于这四项优化比较。
