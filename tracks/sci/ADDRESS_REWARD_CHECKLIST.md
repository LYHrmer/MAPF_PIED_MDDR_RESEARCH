# 奖励语义与记忆：36项有限比较清单

状态：**PENDING_USER，尚未运行**。旧种子8项、费用2项、预算3项等许可均已消费。本文件及JSON仅冻结提案，不能代替用户对本批的授权。比较理由、旧日志结果及继续/停止标准见[比较说明](ADDRESS_REWARD_COMPARISON.md)。

## 工件与任务

- [输入JSON](config/address_reward_holdout_v1_inputs.json)：SHA `660b7bc4b4282db1feedd373a9220dc98638c18bcb835123aff448c83eadcf3e`。
- [清单JSON](config/address_reward_holdout_v1_manifest.json)：SHA `6863861aa2a1a6856097620e1020f0340ea1d3b9a6f170de8b94c4c35b6fe791`；逐项代码/构建源/输入摘要都在JSON内。
- 二进制 `tracks/sci/.address_reward_build/final/build/address`：SHA `bafa04e5357f2c6dae7e5c316d84b6acd743a7838cf5809d73e9e8de22227330`；[既有构建收据](reward_contract_build_receipt.json)。没有重建或改变作者缓存。

| 完整任务 | 车辆 | 冻结初解SOC | makespan |
|---|---:|---:|---:|
| maze-32-32-2 / scenario4 | 16 | 1042 | 125 |
| maze-32-32-2 / scenario5 | 32 | 2000 | 121 |
| random-32-32-10 / scenario4 | 16 | 356 | 44 |
| random-32-32-10 / scenario5 | 32 | 753 | 48 |

输入只读重打包，无新初始规划。原R18 test完整场景与本轮s01设计场景不同，但历史上已有其他研究用途，不能称从未用过。任务数4，求解器种子0/1/2，模式author/cumulative/window16，合计36；不按结果筛选任务。顺序以JSON jobs为唯一依据：先种子，再任务，三模式在每个块内轮换执行位置。

## 每项预算与失败保留

每项总成功准入wall≤5秒；Python worker与原生进程各CPU≤10秒、地址空间≤512MiB、单文件≤16MiB。预留原生1秒wall/1秒CPU、外部1秒wall用于收尾和完整奖励账本核验；无修复次数上限。三臂同一限制，不通过多完成16次声称最终收益。

外层每项10秒TERM＋2秒KILL，36项硬保护合计≤432秒；不是放宽5秒内部预算。各项串行，不与其他科学任务竞争；完整准入覆盖导入、哈希、材料化、ADDRESS、逐次日志、候选与最终全检、结果输出及工件哈希。父管理收据写盘/退出在其后，受外层保护；嵌套费用不重复累计。

逐项检查有效收据与工件后才进入下一项。任一SHA变化、异常、非法/不完整输出、费用超限、超时、非零退出、强制清理、奖励账本不闭合或缺文件，立即关闭其余全部许可；零重试，不修复后沿用余下许可。到软截止而合法返回不算硬失败；零收益/退化不触发换任务。保留失败、partial日志及未运行项，不从分母删除。输出独占 `tracks/sci/results/address_reward_holdout_v1/<job>/`，存在即拒绝覆盖。

## 核验与执行格式

在SCI工作树执行只读检查（不调用规划器）：

```bash
rtk proxy python3 -B tracks/sci/run_address_adapter.py inspect --manifest tracks/sci/config/address_reward_holdout_v1_manifest.json --sha256 6863861aa2a1a6856097620e1020f0340ea1d3b9a6f170de8b94c4c35b6fe791
```

获得**本批**真实授权后才按JSON顺序逐项执行；首项命令为：

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_reward_holdout_v1_manifest.json --sha256 6863861aa2a1a6856097620e1020f0340ea1d3b9a6f170de8b94c4c35b6fe791 --job maze-32-32-2__s04__n16__seed0__author --authorization-reference '<本批真实用户指示引用>'
```

运行前在独占批目录保存原始用户指示、清单SHA、已推送的SCI提交、顺序和预算的AUTHORIZATION记录；记录不自行产生授权。结束或首个失败后，现有 `repair_profile.py address --manifest … --sha256 …` 仅离线归档并核对36项状态。无恢复、训练、world或硕士运动运行。

交付必须区分：①旧日志诊断；②软件核验；③这36项真实对照；④尚未成立的论文贡献。禁止把前两项写成第三项。
