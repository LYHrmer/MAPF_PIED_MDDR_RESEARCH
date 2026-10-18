# 共同根界终止修补：四项功能验证提案

状态：**代码、二进制、输入和预算已准备；未获新科学运行授权，未执行。** 上一批第3项失败后全部许可已关闭，不能据其剩余数量继续。本清单只验证新版本，不测试恢复机制、训练、world或方法优势。

## 固定版本与处理

- 仍用固定作者`b3d35c431ce03834f95e834d87986f2f341394a1`与原共同初解适配。
- 唯一算法控制流改动：合法incumbent的SOC达到同模型静态最短路和时，结束优化循环，继续原退出统计、全车末检和输出。`runPP`、奖励、邻域生成及随机源保持。该经典根界是所有方法共有的工程增强，不认定创新。
- [根界叠加代码](address_loop_guard.py)；3项软件检查通过，包括实际作者构组/walk/外层循环片段的红→绿复现、正余量正常推进与末检可达。
- [新构建收据](loop_guard_build_receipt.json)，SHA `45f04f8d7d05efe50c003a1cd1d11ec3d9445b75d45cab0f51f96dfcd1e0c6d0`。原作者缓存、旧二进制与失败证据不变。只编译并执行help，没有构造科学实例。
- 二进制工作树根`.address_loop_guard_build/build/address`，SHA `cb105b42707eef4a10ff868d0b1c04412c80e91ec40618842884bfe49c8f40e5`。
- [JSON清单](config/address_loop_guard_v1_manifest.json)，SHA `73662d861eda4f9618e23029deb67c53708921a745c8660fd7c587fb6fabd91d`。运行器绑定该变体与构建收据，不将原版收据用于修补版；拒绝尚未核定的recovery运行变体。
- 输入仍是原六份初解bundle，SHA `be1e912e1e2ea3f59fcdc5d0c5737118e7f96d92227be536ada605f6751c0e5b`。只选原失败任务及其后未运行的三任务，未重求初解、未用新任务替换失败。前两项已成功maze不重跑。

`inspect`已通过四份输入、代码/二进制/收据身份和完整初解合法性，均`search_executed=false`。这不证明实际修补版可完成该批；正余量而构组失败的情形仍受原时间限制，未一般化解决。

## 顺序、预算、停止

按下列固定顺序，前项完整成功并核验工件后再执行后项：

1. `random-32-32-10__s01__n16__loop_guard`
2. `random-32-32-10__s01__n32__loop_guard`
3. `warehouse-10-20-10-2-1__s01__n16__loop_guard`
4. `warehouse-10-20-10-2-1__s01__n32__loop_guard`

每项seed=0、PP/SIPP、RandomWalk/bernoulie、邻域上限8、top-K=min(32,n)，最多16次已构组修复。每项总成功准入15秒，worker/native分别CPU≤10秒、地址空间≤512 MiB、单文件≤16 MiB；内层末检预留0.25秒、外层0.5秒。全命令20秒TERM、再2秒KILL，四项最迟回收合计88秒；回收时间不增加优化预算。末尾管理收据与进程退出排除项照原口径单列。

任一非零退出、超时、强制回收、身份变化、路径/收据缺失、全车验证失败、SOC劣化或总费用超限即停全批。零重试；失败和partial保留，不修好后沿用剩余许可。零改善允许成功，不能当学习负标签或方法无价值证明。

## 待授权命令

从`/home/lyh/MAPF_SCI_RESEARCH`执行；只有新真实用户授权本清单后可运行，逐项替换job。

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 20s python3 -B tracks/sci/run_address_adapter.py run \
  --manifest tracks/sci/config/address_loop_guard_v1_manifest.json \
  --sha256 73662d861eda4f9618e23029deb67c53708921a745c8660fd7c587fb6fabd91d \
  --job random-32-32-10__s01__n16__loop_guard \
  --authorization-reference '<用户对本新清单的明确授权原文与范围>'
```

输出固定`tracks/sci/results/address_loop_guard_v1/`，当前不存在；每项独占目录保存attempt、输入、原生stdout/stderr、最终路径/原生收据（若产生）、外部完整校验与总费用，失败也保留。所有已尝试、未尝试及失败项目都进入总账。不得覆盖上一批`address_common_initial_v1`或把失败改为成功。
