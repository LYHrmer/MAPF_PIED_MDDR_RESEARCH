# 完整ADDRESS共同截止：三项功能DEV待授权清单

**状态：实现、软件夹具、编译/help和inspect完成，未科学运行。**
本提案仅验证基线在当前预算内输出完整合法方案，不测试恢复收益或学习。
此前两批完整ADDRESS在失败后关闭的许可均不可复用。

[实现与适用边界](ADDRESS_BUDGET.md)采用共同墙钟/进程CPU软截止，覆盖构组、单次SIPP内部及预处理，收尾保留完整回滚、校验和输出。初解验证、回滚、清理、输出和系统调度没有任意规模硬实时保证；下面的固定任务仍须真实验证，不能把编译成功称为random32问题已解决。

## 固定身份

- [JSON清单](config/address_budget_guard_v1_manifest.json)，SHA `edcef325cb0099550f99b9200aa386625c5815bdf3e806cd90a5088486d67cd1`。
- 原六份完整初解bundle SHA `be1e912e1e2ea3f59fcdc5d0c5737118e7f96d92227be536ada605f6751c0e5b`；不重求初解、不换地图。
- 作者提交 `b3d35c431ce03834f95e834d87986f2f341394a1`，缓存原样保留。新二进制 `.address_budget_guard_build/build/address`，SHA `6d94e123a7a825e65aaaa7a30339de49856b98e60e841980eae671051c374c33`。
- [构建收据](budget_guard_build_receipt.json)，SHA `0cd92d9931558b78e1317998b874ec3b68a5465db0b0ef08b8b3cce30b64c7c8`。运行与构建代码SHA逐项列于清单。执行前另记录本清单所在的实际SCI提交与用户授权原文。
- 新运行器只接受`budget_guard`；`recovery`和`budget_recovery`仍拒绝。旧清单保持原SHA，历史运行需读取其固定提交，不用本次改变后的运行文件通过旧pins。

## 三项固定顺序

1. `random-32-32-10__s01__n32__budget_guard`：上批失败的正余量任务。
2. `maze-32-32-2__s01__n32__budget_guard`：有历史改善的正常修复任务；不要求复现旧改善数。
3. `warehouse-10-20-10-2-1__s01__n32__budget_guard`：较长路径的零余量任务。

各项seed=0，PP/SIPP、RandomWalk/bernoulie、邻域上限8、top-K=32、最多16次已构组修复。三项只作功能DEV，不能作为独立性能比较；原失败与未运行任务记录保留，不回填旧总账。

## 预算与验收

每项从Python入口到结果输出、外部完整校验及全部工件哈希，成功准入总wall≤15秒；worker和native各CPU硬限10秒、各地址空间512MiB、单文件16MiB。外部末检预留0.5秒，原生墙钟收尾预留1秒；原生绝对进程CPU在9秒软截止，为硬限前收尾预留1秒。配置参数为`--cpuLimit 10 --cpuReserve 1 --finalReserve 1`；软截止不扩大硬限。外层20秒TERM、再2秒KILL，三项硬保护合计≤66秒；管理收据最终写入和进程退出排除于15秒自计时，由外层保护覆盖。

每项必须原生及worker正常退出、无强制清理，原生和外部全车校验一致，SOC不劣化，完整输出/收据及SHA齐全，总准入不超限。收据记录构组/SIPP调用、各类deadline、回滚、终止阶段和预处理初解回退；软截止后成功输出合法incumbent允许零改善。若某项未触发deadline，只报告其实际覆盖，不能用正常提前结束证明真实到期路径。

任一异常、非零退出、超限、缺文件、错SHA、全检失败或SOC变差即停整批，零重试。即使初解仍在磁盘，缺有效最终输出仍是失败。剩余许可同时关闭，不修好后接续。失败与partial全部保留，计入分母；`DEADLINE`不是穷尽、不可行或恢复训练标签。

三项输出固定在`tracks/sci/results/address_budget_guard_v1/`，当前不存在。取得真实授权后另存授权记录，每项独占子目录；逐项核对attempt、result、receipt与工件后才执行下一项。沿用`repair_profile.py address`生成包含成功、失败和停批未运行项目的总账，不仅统计成功者。

## 命令

工作目录`/home/lyh/MAPF_SCI_RESEARCH`。授权前只有inspect可执行：

```bash
rtk proxy python3 -B tracks/sci/run_address_adapter.py inspect --manifest tracks/sci/config/address_budget_guard_v1_manifest.json --sha256 edcef325cb0099550f99b9200aa386625c5815bdf3e806cd90a5088486d67cd1
```

取得对本清单的真实用户授权后，逐项替换job和授权引用，不能并行或忽略退出码：

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 20s python3 -B tracks/sci/run_address_adapter.py run \
  --manifest tracks/sci/config/address_budget_guard_v1_manifest.json \
  --sha256 edcef325cb0099550f99b9200aa386625c5815bdf3e806cd90a5088486d67cd1 \
  --job random-32-32-10__s01__n32__budget_guard \
  --authorization-reference '<本批真实用户授权原文和范围>'
```

不启动新初解求解、恢复比较、world、训练或误差扩展。功能通过后再判断完整强基线上的恢复机会，基线完善本身不作创新。
