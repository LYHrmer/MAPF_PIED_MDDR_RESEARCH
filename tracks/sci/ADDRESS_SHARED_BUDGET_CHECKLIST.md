# SCI 新旧预算合同：四项功能验证清单

本轮真实用户指示为：“验证SCI新旧预算合同的实际行为，以及硕士初始认证的预算可行性，再开展收益比较”。这是新的功能验证指示，不借用任何已消费许可。以下四项与资源上界是据此选定的最小实施范围，并非用户逐项指定的原文。主窗口负责冻结、执行和记录；本清单准备阶段没有启动科学任务。

目标是核实共同预算合同在真实完整ADDRESS调用中的行为、合法输出和费用闭合。只比较两个已参与设计的32车任务、seed0，不能作为独立收益、统计显著性或学习结果。新旧两臂均使用同一新二进制和相同观测，不能将旧无观测运行当作配对基线。

## 固定输入、代码和范围

- 科学运行代码基座：`34a80e37034ef47608d609195070e6d4b34a23e9`；原生二进制和运行器无改动；本轮仅在现有离线分析器增加功能覆盖投影，并准备清单和入口。执行时另记录包含本清单的实际提交。
- [manifest](config/address_shared_budget_contract_v1_manifest.json) SHA `a6818a3c28d0d6880d2b57b810b956b9c46658c6274c7bd3c76cec56026abb98`。JSON中的`PENDING_USER`是现有运行器要求的冻结提案字面值，不是当前指示状态；真实指示与消费状态由独立授权和运行收据记录。
- 直接读取[现有完整初解](config/address_reward_holdout_v1_inputs.json)，SHA `660b7bc4b4282db1feedd373a9220dc98638c18bcb835123aff448c83eadcf3e`，不重新求初解。文件另含的任务不在本批作业中。
- 同一二进制：`.address_reward_build/shared_budget_v1_r2/build/address`，SHA `8a9a8226eafc47894ae25a9fe2ae34615d8c790e29819dcb5dd5377d36724da3`。[构建收据](shared_budget_build_receipt.json) SHA `4e022cb6868dd28059c7570050ccc7b6a027d80eb3b66a2a860901435f677ebd`；作者版本仍为`b3d35c431ce03834f95e834d87986f2f341394a1`。
- 运行器、外部验证、分析器和所有构建源SHA均列于manifest，load检查漂移。两臂共同固定author奖励、positive_delay种子、top-K=32、`candidateValidation=all`、`executionObservations=1`、费用记录、PP/SIPP、初末全检与缓存；不切换门控或奖励。

| 顺序 | job末段 | 任务 | 初始SOC / makespan | 唯一合同差异 |
|---|---|---|---:|---|
| 1 | `seed0__legacy` | `maze-32-32-2__s05__n32` | 2000 / 121 | 保留局部事务期限 |
| 2 | `seed0__search_then_admission` | 同上 | 2000 / 121 | 搜索结束后认证/提交仅服从全局期限 |
| 3 | `seed0__legacy` | `random-32-32-10__s05__n32` | 753 / 48 | 保留局部事务期限 |
| 4 | `seed0__search_then_admission` | 同上 | 753 / 48 | 搜索结束后认证/提交仅服从全局期限 |

选择迷宫和random是因为已有记录分别暴露修复/认证与大量回滚费用，输入及资源配置已可复核；不是为了重新寻找正例。作者邻域参数8不构成成员数硬上限，实际成员和顺序必须按日志报告。局部搜索比例仍为1/100；不加大它，不重新调参。

## 资源和停止条件

每项总成功准入wall≤5秒，包含入口、输入检查、构造、搜索、认证、观测、输出、外部全检及产物哈希。原生与外部各保留1秒wall，原生保留1秒CPU；worker/native各CPU≤10秒、地址空间≤512MiB，单文件≤16MiB。外层10秒TERM＋2秒KILL只负责异常收尾，不扩展可用搜索预算。四项总成功准入上限20秒、外层保护上限48秒。

按表串行。零重试，任一SHA漂移、硬退出、超限、缺失/截断产物、非法或不完整最终方案、后验/身份/结算或费用不闭合，立即保留失败并关闭全部剩余项。未运行项记`NOT_RUN_AFTER_BATCH_STOP`，不能当零收益或补跑。软截止若按合同回滚并按时输出完整合法方案，是功能观察，不等同硬失败。固定总wall没有下降也不是功能失败或独立否定收益的依据。

不运行门控性能比较、新奖励、恢复、额外seed、训练、world或旧R16。没有收益时不加预算、改任务或自动追加次数。输出路径独占，不覆盖任何旧目录。

## 必须回答的行为问题

| 问题 | 现有原始字段/证据 | 解释边界 |
|---|---|---|
| 搜索在哪个期限结束，是否仍有全局余量？ | `execution_observations.search_return`的有符号余量、search_censored、local/global标志；`cost_diagnostics`原始停止和remaining | 时间余量是检查点观测，不能用负余量替代真实截止触发分类 |
| 新合同是否保留搜索截尾，且不误提交？ | `SEARCH_CENSORED`、accepted、plan_identity/revision、完整输出 | 局部时钟解除不能复活已截尾搜索；最终全检仍必需 |
| 正常完整搜索之后，局部期限与认证是否发生实际耦合？ | 搜索返回状态、首次local/global截止的阶段、完整认证、作者更新、提交/回滚 | 只在真实日志出现相应触发时记`EXERCISED`；缺失记`NOT_EXERCISED`，不凭人工夹具或另一次运行推断本次已触发 |
| 认证完成后全局到期是否阻止提交？ | candidate_validated、global截止阶段、accepted=false、身份/revision不变 | 没触发就保留`NOT_EXERCISED`，不主动补跑追触发 |
| 后验与实际收益是否分开且每次仅结算一次？ | 真实author_update前后与原谓词、selected_posterior_after_settlement；selection_id/settlements、committed_gain | 作者回滚前正更新可能与回滚共存；不能将提交收益审计臂当实际作者后验 |
| 总费用是否闭合，输出是否完整？ | 逐事件费用、哈希/日志、native/worker/外层收据、初末路径及全检 | 嵌套时间不重复相加；固定时间内更多修复不代表质量收益 |

离线聚合复用`repair_profile.py`：仅在已通过现有完整账本核验后投影覆盖。新合同只有`candidate_validated`且搜索正常完整，并满足`search_return.local_remaining_wall_ns >= 0`且`candidate_validation_wall_ns > search_return.local_remaining_wall_ns + 2`时，才把认证超出原局部期限记为充分证据；再有accepted才记提交见证。2ns用于整数时钟舍入保护；不满足该充分式只记缺少直接证据，不能反推没有跨界。`post_search_through_settlement`不用于证明提交时刻。新增人工夹具覆盖真正跨界、结算跨界但认证未跨界、全局截尾身份不变及旧合同首次期限阶段。

关键触发应分别报告：①搜索本身局部到期；②完整搜索后、局部期限到期而全局尚有余量；③全局到期；④认证成功后提交前全局到期。新模式不再检查已解除的局部期限，因此不能从其未记录local触发推出“旧合同一定会拒绝同一候选”；不同臂的后继顺序和候选也可能分化，日志不构成逐候选反事实重放。两臂SOC/makespan和完整费用照实列出，但本轮不判断独立算法优势。

功能通过后仍需先看哪些触发实际发生、哪些保留软件证据。只有出现清楚的真实行为和成本差异，才另定收益比较；缺失触发、零差异及退化均保留，不自动扩大本批。

## 命令及产物

准备阶段已执行以下inspect，四项返回`PINNED_BYTES_AND_JSON_ONLY`，没有构造问题或调用搜索：

```bash
rtk proxy python3 -B tracks/sci/run_address_adapter.py inspect --manifest tracks/sci/config/address_shared_budget_contract_v1_manifest.json --sha256 a6818a3c28d0d6880d2b57b810b956b9c46658c6274c7bd3c76cec56026abb98
```

运行由主窗口在冻结后执行。授权记录须保存上面的当前用户原文、实际提交、本清单SHA、四个job、限额、零重试、旧许可未复用，并明确四项数量/预算是实施安排。以下参考字符串必须连接该真实记录，不能单凭字符串或文件授权。

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_shared_budget_contract_v1_manifest.json --sha256 a6818a3c28d0d6880d2b57b810b956b9c46658c6274c7bd3c76cec56026abb98 --job maze-32-32-2__s05__n32__seed0__legacy --authorization-reference '2026-10-25 current direct validation instruction; shared budget contract functional DEV four jobs; new authorization only'
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_shared_budget_contract_v1_manifest.json --sha256 a6818a3c28d0d6880d2b57b810b956b9c46658c6274c7bd3c76cec56026abb98 --job maze-32-32-2__s05__n32__seed0__search_then_admission --authorization-reference '2026-10-25 current direct validation instruction; shared budget contract functional DEV four jobs; new authorization only'
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_shared_budget_contract_v1_manifest.json --sha256 a6818a3c28d0d6880d2b57b810b956b9c46658c6274c7bd3c76cec56026abb98 --job random-32-32-10__s05__n32__seed0__legacy --authorization-reference '2026-10-25 current direct validation instruction; shared budget contract functional DEV four jobs; new authorization only'
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_shared_budget_contract_v1_manifest.json --sha256 a6818a3c28d0d6880d2b57b810b956b9c46658c6274c7bd3c76cec56026abb98 --job random-32-32-10__s05__n32__seed0__search_then_admission --authorization-reference '2026-10-25 current direct validation instruction; shared budget contract functional DEV four jobs; new authorization only'
```

产物唯一位置`results/address_shared_budget_contract_v1/`：批次`AUTHORIZATION.json`、外层命令/资源/退出记录；每项原始`attempt.json`、`receipt.json`、`result.json`、`native_receipt.json`、`rewards.jsonl`、初始输入、`final.paths`及stdout/stderr。失败和部分写盘也保留。执行结束后使用已有`repair_profile.py address --manifest … --sha256 …`离线核对并形成`RUN_RECEIPT.json`；分析器不启动搜索。实际触发计数和`NOT_EXERCISED`投影来自原始账本，派生分析另记录源码/来源SHA和离线费用，不回填原运行计时。
