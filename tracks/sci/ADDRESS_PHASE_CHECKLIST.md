# ADDRESS 非修复费用：两项计时诊断待授权

状态：实现、软件核验、完整编译/help已完成；未获新运行授权。全部旧科学许可已消费。该清单仅测费用与事件分布，不运行新增优化机制、恢复、训练、world或大论文运动任务。

- JSON：[address_phase_profile_v1_manifest.json](config/address_phase_profile_v1_manifest.json)，SHA `0d4e08274314bb96f4596c3d43c3e4117c43d0f223b16af74e8850fa3c442ab7`。
- 输入仍为`repair_residual_v1_inputs.json`，SHA `be1e912e1e2ea3f59fcdc5d0c5737118e7f96d92227be536ada605f6751c0e5b`；复用初解，不换任务或参数。
- 二进制`.address_phase_profile_build/build/address`，SHA `fd99fa4ee3b964684d8778faf07f38bf3e8b4ad98618da729fbe0b96afb88d2b`；[构建收据](budget_phase_build_receipt.json) SHA `e5798acfb227185c693403531e82cc25222c136bf77346cd28cf75672b3589ad`。所有运行/构建源逐项固定摘要。
- 顺序：`random-32-32-10__s01__n32__phase_profile`，然后 `maze-32-32-2__s01__n32__phase_profile`。各32车，seed0、topK32、邻域上限8、最多16次已构组修复；`budget_guard`，attempt trace与phase profile均开启。

每项总准入wall≤15秒；worker/native各CPU硬限10秒、各地址空间512MiB、单文件16MiB。CPU9秒软截止，保留1秒CPU与1秒原生wall收尾，外部末检预留0.5秒；外层20秒TERM再2秒KILL，两项合计外层上限44秒。预算包括记录、输入/输出、完整合法性检查、日志核验和工件哈希；父管理收据与退出由外层保护覆盖。

零重试；前项退出0、最终方案完整合法、SOC不劣化、预算合规且日志一致后才开始下一项。任一失败、异常、缺工件、摘要变化或超限立即停批，余项许可同时关闭，保留partial、stderr及失败收据。正常软截止且合法输出可通过；零改善不失败。

新增验收：11个阶段独占wall之和等于配置至finish窗口；残差0；四类构组出口之和等于原生组调用数；scope次数与组/种子/游走/修复计数对应；seed分类数不超过seed调用；预算采样数量等于检查调用数整除1024。所有样本保持`extrapolated=false`，不当完整clock成本，嵌套费用不重复相加。不得据单次计时或旧无profile记录宣称稳定加速。

输出独占`tracks/sci/results/address_phase_profile_v1/`，当前不存在。实际授权后另存真实用户指示；运行前核对本清单所在已推送SCI提交和下列SHA。它不是继续消费旧两项许可。

当前可做无搜索inspect：

```bash
rtk proxy python3 -B tracks/sci/run_address_adapter.py inspect --manifest tracks/sci/config/address_phase_profile_v1_manifest.json --sha256 0d4e08274314bb96f4596c3d43c3e4117c43d0f223b16af74e8850fa3c442ab7
```

获得这两项新授权后，在SCI工作树按上述顺序逐项执行（替换job与真实授权引用）：

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 20s python3 -B tracks/sci/run_address_adapter.py run \
  --manifest tracks/sci/config/address_phase_profile_v1_manifest.json \
  --sha256 0d4e08274314bb96f4596c3d43c3e4117c43d0f223b16af74e8850fa3c442ab7 \
  --job random-32-32-10__s01__n32__phase_profile \
  --authorization-reference '<真实用户授权原文及本批范围>'
```

批次结束后仅离线汇总：

```bash
rtk proxy python3 -B tracks/sci/repair_profile.py address --manifest tracks/sci/config/address_phase_profile_v1_manifest.json --sha256 0d4e08274314bb96f4596c3d43c3e4117c43d0f223b16af74e8850fa3c442ab7
```

若分账不能区分瓶颈、开销主要由共同预算或统计引入，先处理共同工程条件；若简单零延迟准入足以解释机会分配，不启动复杂学习。实际优化需另行具体设计、公平比较与新授权；本批不自动开放后继运行。
