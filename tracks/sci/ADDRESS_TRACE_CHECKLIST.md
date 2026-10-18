# 完整 ADDRESS 逐次失败记录：两项 DEV 已完成，许可已消费

**状态：用户明确回复“授权这2项”后，两项按顺序全部 COMPLETE，零重试，许可已消费。** [结果及停止决定](ADDRESS_TRACE_RESULT.md)确认没有满足原后段门槛的正常空返回；停止当前材料上的恢复候选。以下保留原预算、命令和验收合同供审计，不能据此重跑。JSON清单及其SHA不变。

## 固定输入与代码

- [JSON清单](config/address_attempt_trace_v1_manifest.json)，SHA `edf8516ab73919c0fedc0542c407c5775f8601383259f69ead6949146f43c2f3`。运行/分析器、构建脚本和overlay逐项SHA已固定；执行前核对本清单所在的已推送SCI提交并记录实际授权。
- 输入复用`repair_residual_v1_inputs.json`，SHA `be1e912e1e2ea3f59fcdc5d0c5737118e7f96d92227be536ada605f6751c0e5b`。不重新求初解，不换地图或扰动参数。
- 只使用`budget_guard`，开启`attempt_trace=true`；运行器继续拒绝`recovery`和`budget_recovery`。新二进制`.address_attempt_trace_build/build/address`，SHA `72b1fcec8c0bfbd44e9107f59592cdfeb55e92ff3075022bf16b8459375e8cfb`。
- [构建收据](budget_trace_build_receipt.json)，SHA `f88c0112ad5b531ad498f7721453ca663b0609f18867d7295db7cf86d8315a28`。作者仍固定`b3d35c431ce03834f95e834d87986f2f341394a1`，作者树及旧二进制不变。

顺序固定为：

1. `random-32-32-10__s01__n32__attempt_trace`：此前GROUP软截止返回原方案，缺乏每次primary失败分类。
2. `maze-32-32-2__s01__n32__attempt_trace`：此前正常完成且有SOC改善，rollback数不能说明每次失败位置。

每项seed=0，PP/SIPP、RandomWalk/bernoulie、top-K=32、邻域上限8、最多16次已构组修复，无额外恢复调用。此前warehouse任务没有构组或搜索，不在本清单重复运行。

## 预算与验收

每项总成功准入wall≤15秒，从Python入口到产物写入、外部完整检查、日志核验和全部工件哈希；worker/native各CPU硬限10秒、各地址空间512MiB、单文件16MiB。外部末检预留0.5秒，原生墙钟收尾预留1秒、绝对CPU在9秒软截止预留1秒。外层20秒TERM再2秒KILL，两项外层保护合计≤44秒。父管理收据最终写入与进程退出排除于自计时总准入，由外层保护覆盖。软截止和日志不放宽任何硬限。

必须原生/worker退出0、无强制清理、输出齐全，原生及外部完整离散合法性校验一致，SOC不劣化，总准入不超限；零改善可以通过。新增`attempts.jsonl`必须完整，原生记录启用trace、行数/搜索调用/rollback与日志一致，逐次位置/车辆/成本/接纳状态可核对。零行只说明未进入runPP，须与原生计数一致，不补造失败记录。

任一异常、非零退出、超限、工件缺失或SHA变化、trace截断/不一致、末检失败或SOC变差即停整批，**零重试**，余项许可同时关闭。partial、stderr、失败收据全部保留；磁盘上还存在初解不能替代有效最终输出。正常软截止并输出合法方案属于功能成功，不作为穷尽、不可行或恢复训练标签。

输出已保存到`tracks/sci/results/address_attempt_trace_v1/`；真实指示、逐项收据和总账齐全，原27项工件已复核。总收据SHA `308e5a65e98270b6049336dff0c50da88bbbf137755fc2875a9203d91d5a8632`，不覆盖任何旧批。

## 只允许得出什么结论

可以核对实际primary调用、正常返回类别、失败车辆/位置及记录成本。`FOCAL_DRAINED_EMPTY`是作者返回位置，不是独立完备性证明；轻量日志没有做阻挡分析，`blockers_checked=false`、`recoverability_established=false`。记录本身会增加开销，并可能改变临近截止时的后续选择；不能与旧无trace单次计时宣称稳定加速。

若两案没有观察到可用的正常后段失败，记录该材料下的停止/收缩结论，不反复换场景或重跑寻找正例。若有，仅获得后继资格诊断的线索；仍须验证可复用路径及成本，并完成相同条件的随机重排、继续选邻域和优先级搜索对照，才能准备恢复收益比较。本批没有训练、world、实物、误差扩展或大论文运动运行。

## 命令

工作目录`/home/lyh/MAPF_SCI_RESEARCH`。当前允许静态inspect：

```bash
rtk proxy python3 -B tracks/sci/run_address_adapter.py inspect --manifest tracks/sci/config/address_attempt_trace_v1_manifest.json --sha256 edf8516ab73919c0fedc0542c407c5775f8601383259f69ead6949146f43c2f3
```

以下是本批已执行命令模板，仅供审计；许可已消费，输出独占目录不可重用：

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 20s python3 -B tracks/sci/run_address_adapter.py run \
  --manifest tracks/sci/config/address_attempt_trace_v1_manifest.json \
  --sha256 edf8516ab73919c0fedc0542c407c5775f8601383259f69ead6949146f43c2f3 \
  --job random-32-32-10__s01__n32__attempt_trace \
  --authorization-reference '<真实用户授权原文及本批范围>'
```

以下离线汇总已执行并保存总收据；不得覆盖原收据。后续只读复核使用结果报告中的独立核验脚本：

```bash
rtk proxy python3 -B tracks/sci/repair_profile.py address --manifest tracks/sci/config/address_attempt_trace_v1_manifest.json --sha256 edf8516ab73919c0fedc0542c407c5775f8601383259f69ead6949146f43c2f3
```
