# 正延迟种子对照：八项有限DEV已完成，许可已消费

状态：用户针对提交`93af30f`明确回复“授权这8项，严格按清单执行”，问题引用`call_b30d0e75ab0d47969e79ae4b9641c810`。本批按原顺序全部COMPLETE，零硬失败、零未运行、零重试，许可已消费；[结果及独立核验](ADDRESS_SEED_RESULT.md)。random/all固定次数项仅完成4/16后CPU软截止，保留为截尾。原两JSON、输入、二进制及代码摘要不改，以下为实际执行范围的记录，不得据此重跑。

比较依据与边界见[实现说明](ADDRESS_SEED_COMPARISON.md)。两口径使用同一二进制，复用两份32车开发初解，不调用初始规划器、不训练、不启动world、不恢复后段候选。

## 固定输入和工件

- 输入`config/repair_residual_v1_inputs.json` SHA `be1e912e1e2ea3f59fcdc5d0c5737118e7f96d92227be536ada605f6751c0e5b`；仅random32与maze32，每口径各比较`all`、`positive_delay`。
- [固定次数JSON](config/address_seed_fixed_v1_manifest.json) SHA `c5e6f03bc9378b52dc3ab88a7fba4688dc41f7f3f14910aced73b3e1efd23993`，4项。
- [固定时间JSON](config/address_seed_time_v1_manifest.json) SHA `508652f403e758e4fd1d0831b7a7093b3b56c317bb92d9414a8ba5514acb8d31`，4项。
- `.address_seed_admission_build/build/address` SHA `d4dc680dee3d4d9ad7ebd3d4da391618a29f8868cf5d1f6c427e56f28e7de473`；[构建收据](seed_admission_build_receipt.json) SHA `83452ed1636d5d76b568741a34eee07296eb855d06ae2cdba74ca26198ddf87e`。运行器、构建源及收据完整摘要分别固定在两JSON中。运行前登记包含这些文件的已推送SCI提交。

两臂共同配置：作者`b3d35c4`，PP/SIPP、RandomWalk、Bernoulli/canonical，seed0，top-k32、邻域上限8；不改变缓存、作者`a=i`或预算检查频率。新增初始种子筛选是唯一策略差异。逐次trace和阶段profile两臂都关闭，保留相同基础计数与最终收据。

## 资源预算、顺序及停止

固定次数4项各目标16次修复，总准入wall≤15秒；固定时间4项各总准入wall≤5秒、无修复次数上限。各项Python worker和原生进程分别CPU≤10秒、地址空间≤512MiB、单文件≤16MiB；原生CPU软截止9秒。两口径均预留原生1秒wall/1秒CPU、外部0.5秒wall收尾。完整准入计时覆盖输入校验、筛选/构组、修复、回滚、输出、完整路径与日志校验和哈希。最终管理收据及退出由外层保护覆盖，单列边界。

先固定次数4项，再固定时间4项；每组顺序均为random/all、random/positive_delay、maze/all、maze/positive_delay。逐项检查成功收据与工件后才启动下一项。外层固定次数20秒TERM+2秒KILL，固定时间10秒TERM+2秒KILL，八项合计硬保护上限136秒；不是增加内部预算。

零重试。任一代码/输入/二进制SHA不符、异常、非法最终方案、缺工件、超限、非零退出或强制清理立即关闭**两份清单的全部剩余项**。保留成功、失败、未运行和partial日志，不修复后沿用余下许可。科学退出到期且合法输出为成功准入；固定16未达目标须标截尾，不能报等工作量加速；零SOC改善不是硬失败。

输出分别独占`results/address_seed_fixed_v1/`、`results/address_seed_time_v1/`，现均已冻结。实际授权记录包含原始用户指示、两JSON SHA、顺序和科学提交，全部科学启动前保存；目录存在即拒绝覆盖。固定次数总收据SHA `f33214f2…9a1ff`，总预算总收据SHA `1dd7777c…6f22d`，完整摘要见结果报告。5秒仍包含CPU保护，本批四项实际均为wall截止。因原单次修复额度随总预算变化，禁止跨两口径合并归因。

## 已执行命令格式（许可已消费，不重跑）

工作目录`/home/lyh/MAPF_SCI_RESEARCH`。只读检查：

```bash
rtk proxy python3 -B tracks/sci/run_address_adapter.py inspect --manifest tracks/sci/config/address_seed_fixed_v1_manifest.json --sha256 c5e6f03bc9378b52dc3ab88a7fba4688dc41f7f3f14910aced73b3e1efd23993
rtk proxy python3 -B tracks/sci/run_address_adapter.py inspect --manifest tracks/sci/config/address_seed_time_v1_manifest.json --sha256 508652f403e758e4fd1d0831b7a7093b3b56c317bb92d9414a8ba5514acb8d31
```

固定次数四项已按下列格式逐项执行，实际授权引用已保存于各项attempt；job严格按表顺序：

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 20s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_seed_fixed_v1_manifest.json --sha256 c5e6f03bc9378b52dc3ab88a7fba4688dc41f7f3f14910aced73b3e1efd23993 --job random-32-32-10__s01__n32__fixed_repairs__all --authorization-reference '<本次真实用户授权>'
```

| 顺序 | 固定次数job |
|---|---|
| 1 | `random-32-32-10__s01__n32__fixed_repairs__all` |
| 2 | `random-32-32-10__s01__n32__fixed_repairs__positive_delay` |
| 3 | `maze-32-32-2__s01__n32__fixed_repairs__all` |
| 4 | `maze-32-32-2__s01__n32__fixed_repairs__positive_delay` |

前四项全部通过后，按以下格式完成固定时间四项：

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_seed_time_v1_manifest.json --sha256 508652f403e758e4fd1d0831b7a7093b3b56c317bb92d9414a8ba5514acb8d31 --job random-32-32-10__s01__n32__total_budget__all --authorization-reference '<同次真实用户授权>'
```

| 顺序 | 固定时间job |
|---|---|
| 5 | `random-32-32-10__s01__n32__total_budget__all` |
| 6 | `random-32-32-10__s01__n32__total_budget__positive_delay` |
| 7 | `maze-32-32-2__s01__n32__total_budget__all` |
| 8 | `maze-32-32-2__s01__n32__total_budget__positive_delay` |

每份已执行批次可用`repair_profile.py address --manifest <对应JSON> --sha256 <对应SHA>`仅离线汇总；若第一份硬失败，第二份整体记未运行/许可关闭，不创建假运行收据。最终报告两口径独立的全部任务分母、合法性、SOC/makespan、截尾、修复次数、候选计数与完整成本。未见任务比较、扩展seed和训练不包含在这八项中。
