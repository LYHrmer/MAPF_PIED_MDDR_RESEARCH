# SCI 新旧预算合同：四项功能验证清单

**状态更新：已执行，许可消费。** 科学提交`08c38999515c0af196f76b0dfb0cfa92299aec39`下四项全部COMPLETE，零硬失败、零重试；[结果](ADDRESS_SHARED_BUDGET_RESULT.md)保留合同触发、NOT_EXERCISED、退化与完整成本。以下冻结范围和命令用于追溯，不得再次执行或复用许可。原manifest字节/SHA、输入、二进制、授权和逐项产物不改写。

本轮真实用户指示为：“验证SCI新旧预算合同的实际行为，以及硕士初始认证的预算可行性，再开展收益比较”。这是新的功能验证指示，不借用任何此前已消费许可。以下四项与资源上界是据此选定的最小实施范围，并非用户逐项指定的原文。主窗口已完成冻结、执行和记录；原准备阶段没有启动科学任务。

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

下列命令为本批已消费运行的追溯模板，不得重跑。主窗口的实际命令及授权引用见[外层执行记录](results/address_shared_budget_contract_v1/OUTER_EXECUTION.json)；[原授权](results/address_shared_budget_contract_v1/AUTHORIZATION.json)保存本轮用户原文、冻结提交、manifest SHA、四个job、限额、零重试与旧许可未复用，并区分实施安排与用户原文。参考字符串本身不授予许可。

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_shared_budget_contract_v1_manifest.json --sha256 a6818a3c28d0d6880d2b57b810b956b9c46658c6274c7bd3c76cec56026abb98 --job maze-32-32-2__s05__n32__seed0__legacy --authorization-reference '2026-10-25 current direct validation instruction; shared budget contract functional DEV four jobs; new authorization only'
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_shared_budget_contract_v1_manifest.json --sha256 a6818a3c28d0d6880d2b57b810b956b9c46658c6274c7bd3c76cec56026abb98 --job maze-32-32-2__s05__n32__seed0__search_then_admission --authorization-reference '2026-10-25 current direct validation instruction; shared budget contract functional DEV four jobs; new authorization only'
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_shared_budget_contract_v1_manifest.json --sha256 a6818a3c28d0d6880d2b57b810b956b9c46658c6274c7bd3c76cec56026abb98 --job random-32-32-10__s05__n32__seed0__legacy --authorization-reference '2026-10-25 current direct validation instruction; shared budget contract functional DEV four jobs; new authorization only'
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_shared_budget_contract_v1_manifest.json --sha256 a6818a3c28d0d6880d2b57b810b956b9c46658c6274c7bd3c76cec56026abb98 --job random-32-32-10__s05__n32__seed0__search_then_admission --authorization-reference '2026-10-25 current direct validation instruction; shared budget contract functional DEV four jobs; new authorization only'
```

产物唯一位置`results/address_shared_budget_contract_v1/`：批次`AUTHORIZATION.json`、外层命令/资源/退出记录；每项原始`attempt.json`、`receipt.json`、`result.json`、`native_receipt.json`、`rewards.jsonl`、初始输入、`final.paths`及stdout/stderr。失败和部分写盘也保留。执行结束后使用已有`repair_profile.py address --manifest … --sha256 …`离线核对并形成`RUN_RECEIPT.json`；分析器不启动搜索。实际触发计数和`NOT_EXERCISED`投影来自原始账本，派生分析另记录源码/来源SHA和离线费用，不回填原运行计时。

## 第二阶段：同两任务的12项收益DEV（本节为新范围）

当前用户原文“验证SCI新旧预算合同的实际行为，以及硕士初始认证的预算可行性，再开展收益比较”包含通过验证后开展收益比较的条件指示。SCI功能阶段已通过，[结果提交`4fcf289`](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/commit/4fcf289347bcf8f93410e61ae15cf2b1bb37e3fa)固定总收据SHA `70765e1f8e9ca3f2f64ed403bb0f7fe881ff50686e819a9be7ea1e93371446bc`和独立审计SHA `496fc47e93e3e06c638166f98b5ce26c2973b1e1c1b2421cc4771fdaf18934cc`。本节据此限定第二阶段最小实施范围；12项数量及预算由本轮实施安排，不冒充用户逐项给定，也不复用旧四项已消费许可。硕士认证失败不阻塞独立SCI支线。

新[manifest](config/address_shared_budget_gain_v1_manifest.json) SHA `48d0e66e7e69f447323ce3a3a6f55190433332834d3b3cf78798fdaf5f3606e7`；二进制、运行器/分析器、初解输入及全部源SHA沿用第一阶段冻结值，未改局部份额、奖励、all策略或观测。只增加同两份已知32车任务的solver seed1/2/3，不加入地图、初始搜索、训练或新模型。独立任务单位仍是2，三个seed只是任务内重复，六对结果不能算六份独立地图或留出验证。

| 配对顺序 | 任务 | seed | 本对合同顺序（各一项） |
|---|---|---:|---|
| 1 | maze-32-32-2 / s05 / n32 | 1 | legacy → search_then_admission |
| 2 | random-32-32-10 / s05 / n32 | 1 | search_then_admission → legacy |
| 3 | maze-32-32-2 / s05 / n32 | 2 | search_then_admission → legacy |
| 4 | random-32-32-10 / s05 / n32 | 2 | legacy → search_then_admission |
| 5 | maze-32-32-2 / s05 / n32 | 3 | legacy → search_then_admission |
| 6 | random-32-32-10 / s05 / n32 | 3 | search_then_admission → legacy |

同对两臂相邻，全批串行，三对旧先、三对新先；不与其他科学计时并跑。每项仍总准入wall≤5秒，worker/native各CPU≤10秒、地址空间≤512MiB、单文件≤16MiB，预留预算不变；外层10秒TERM＋2秒KILL。12项总准入上限60秒、外层保护总上限144秒。零重试，首个硬失败/超限/非法或缺失方案/账本不闭合停批，失败和未运行项照实保留；不通过替换seed或追加样本补齐。

主指标逐对报告`SOC_legacy − SOC_search_then_admission`，正值表示新合同最终SOC更低；每任务分别列三个seed，不跨任务抹去方向。makespan两臂原值/差值、全部准入/外层/CPU/内存和失败同时报告。修复次数和截尾仅解释机制，不作收益代理。若同任务不同seed的严格SOC差出现正负翻转，或仅修复次数变多而最终完整质量无改善，停止扩大这个具体候选。零差异、退化、不完整配对均保留，不从幸存项单独宣布有效；本批不作显著性或未见任务泛化结论。

准备阶段只进行byte/JSON inspect，无科学运行：

```bash
rtk proxy python3 -B tracks/sci/run_address_adapter.py inspect --manifest tracks/sci/config/address_shared_budget_gain_v1_manifest.json --sha256 48d0e66e7e69f447323ce3a3a6f55190433332834d3b3cf78798fdaf5f3606e7
```

主窗口冻结后按新manifest的12个job顺序执行。第一项具体命令如下，其余逐项使用manifest内的完整job ID；旧四项命令不得再次执行。新授权记录单列第二阶段、当前用户原文、前置功能证据、实际提交、全部12项和资源范围，提供`jobs`字段且逐项等于manifest，以兼容原聚合器。

```bash
rtk proxy timeout --signal=TERM --kill-after=2s 10s python3 -B tracks/sci/run_address_adapter.py run --manifest tracks/sci/config/address_shared_budget_gain_v1_manifest.json --sha256 48d0e66e7e69f447323ce3a3a6f55190433332834d3b3cf78798fdaf5f3606e7 --job maze-32-32-2__s05__n32__seed1__legacy --authorization-reference 'CURRENT_USER_CONDITIONAL_REQUEST_20261025_SECOND_STAGE_SCI_GAIN_DEV'
```

新产物只写`results/address_shared_budget_gain_v1/`，授权/外层执行/每项原始文件与离线总收据结构复用现有模块；不覆盖第一阶段。旧冻结聚合的PRIMARY_DONE投影缺口仍须直接复核原stage，不据零计数断言未触发。当前本窗口仅完成准备，不执行或扩展本批。
