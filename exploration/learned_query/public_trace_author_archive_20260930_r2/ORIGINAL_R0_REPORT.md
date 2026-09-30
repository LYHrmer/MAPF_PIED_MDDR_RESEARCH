# 作者完整 PIE-D 候选的原生 R0 回执

2026-09-29。结论：指定作者完整分支的原源码已构建并完成一次合法原生运行，独立路径与任务核验通过。该结果证明外部工件可运行；它还不是论文数值复现、规模实验或本项目误差执行器下的公平比较。原源码存在下述问题，不能因一次成功就宣称已获得无条件可用的正式基线。

来源是 [YueZhang-studyuse/LMAPF-delay](https://github.com/YueZhang-studyuse/LMAPF-delay/tree/74cfba3c81a0c165c2e7044dea6fd4dee8ddf415)，固定 `improve_morereveal@74cfba3c81a0c165c2e7044dea6fd4dee8ddf415`，tree `1ddae17a7a33fbd7175db7ec6697d5281e84404d`。新隔离 clone 为 `PIED-full/`；未修改作者任何 tracked 源码或数据。该版本与此前 `0b5b336` 的旧 R0 区分记录。原仓根 LICENSE 为 MIT，copyright 2022 The League of Robot Runners，原文及 SHA 已保存在 `pied_preflight.json`；本记录不另行推定捆绑组件的许可证。

## 固定运行及原始结果

运行前写入 `pied_preflight.json`，只执行一次，无扫参或筛选结果。选择作者最小团队规模 100 的 random scen-1，以及源码示例采用的 `0.010` 延迟配置；将资格运行时域明确限制为 20 步，以满足单次 60 秒上限。作者 JSON、地图、起点、任务、延迟文件均原样使用，没有生成本项目输入替代作者数据。

| 项目 | 固定设置或观测 |
|---|---|
| 编译 | 原 CMake，Release，`PYTHON=OFF`，GNU 11.4.0，CMake 3.22.1，Boost 1.74.0，parallel 4 |
| 配置 / 编译 | exit 0 / exit 0；0.559 秒 / 21.858 秒；各 120 秒上限 |
| 作者输入 | `lifelong_benchmark/random/agent-100_scen-delay-0.010-1.json` |
| 地图 / 起点 | 32×32，819 可通行格，100 个互异且可通行起点 |
| 任务 / 延迟 | 12500 合法任务位置；实际使用的 100 个延迟序列各 2000 步 |
| 算法入口 | `mapfPlanner=2` → LaCAM/LNS replan-all；`delayPolicy=3` → time-dependent PIBT；`delaySimulateAll=false` |
| 其他参数 | `simulationTime=20`，`commitStep=1`，`planTimeLimit=1`，完整 JSON 输出 |
| 原生运行 | exit 0，21.128 秒，未触发 60 秒截止，stderr 为空 |
| 任务 | 252 个已分配任务，52 个完成，200 个在时域末仍待完成 |
| 延迟 | 前 20 步 93 个作者文件的 delay flags；日志计数一致 |
| 安全 / 执行核验 | 全部 2000 个实际动作合法，无顶点冲突、无反向交换；`AllValid=Yes`，`errors=[]` |
| 规划 | 原结果 21 次规划，总时间 21.004 秒；这是原生平台运行观测 |

完整 argv 位于 `pied_preflight.json` 与 `pied_run_01/receipt.json`。工作目录固定为新 clone，执行命令的算法参数来自 `src/driver.cpp:57` 的作者示例；团队规模和短时域是资格运行设置。默认参数中的 `mapfPlanner=1` 是 LaCAM-only，本次没有用该默认入口冒充完整重规划执行组合。这里也不声称选择的变体已与论文最佳配置一一对应；正式实验仍需按论文实验设定核对变体。

独立核验脚本 `pied_verify.py` 仅读作者数据和运行输出，未实现或替换规划策略。它检查作者 JSON 实际字段及相对路径、所有起点和任务的地图合法性、延迟长度与二值域，重放全部网格动作，检查顶点和交换碰撞，再核对 round-robin 任务序列、FIFO 完成顺序、完成时刻的实际位置以及任务 ID/总数。完成任务的 `completion−assignment` 之和为 618；该数只含完成的 52 个任务，不作为包含 200 个未完成任务的全程 flow 指标。

## 必须保留的原源码边界

1. `src/driver.cpp:158` 以 `commit_window+1` 设置揭示任务数，忽略 JSON 的 `numTasksReveal=1`。本次真实值是 2，已进入元数据；后续公平比较必须对齐真实值。
2. `inc/CompetitionSystem.h:93` 的 `init_time_limit` 未初始化，`src/CompetitionSystem.cpp:359` 读取它；CLI 的 `initTimeLimit` 没有赋给该成员。这是原代码的未定义行为风险，尽管当前选定分支首次规划随后把运行限额设为 1 秒，不能据此抹去该问题。原版 R0 保持未改，若正式基线要修复，应另建有完整 diff 的作者修复适配版本。
3. `src/CompetitionSystem.cpp:807` 起的若干 stdout 平均数使用未初始化的 `sum_time`、`sum_cost`、`cnt`、`sum_delay_replan`。保留原日志，但不采用这些平均数作为证据。上表规划时间从 JSON 的完整 `plannerTimes` 直接求和。
4. 原编译器警告还包括未返回值的非 void 函数，详见 `pied_build_01/stderr.log`。本次没有为获得成功而修改这些函数；短跑成功不能覆盖未触发路径。
5. 源码没有明确的 CLI 随机种子入口，且搜索受墙钟时限影响；这一轮没有重复运行来寻找优值，也没有宣称位级确定性。
6. 这里运行的是作者离散网格与预置时间延迟模型。它没有本项目的非零二维误差包络、合法 POSITION/END 证据回执或生产计费链。正式比较中这些接口若由统一执行器补充，必须单独标注 `PIE-D + common executor` 及适配改动，不能声称作者原生支持。

## 文件与后续比较资格

- `pied_checkout_01/`、`pied_configure_01/`、`pied_build_01/`、`pied_run_01/`：各自完整 argv、cwd、退出码、时长、stdout/stderr 及其 SHA；运行目录另有作者 log 和完整 result JSON。
- `pied_metadata.json`：版本、构建环境、原码无改动状态及 clone 命令。clone 的工具返回成功，但没有单独保存其原始日志/精确时长，这个缺口已按实标注；后续步骤均有落盘原始回执。
- `pied_preflight.json`：运行前固定参数、完整许可证、输入 schema 和各输入/二进制 SHA。
- `pied_postflight.json`：独立核验结果。结果 JSON SHA 为 `67c10baa0faa4b10200591982d970368c6f8292e87959a47b8f7d0d832849b10`；二进制 SHA 为 `949af736131741a0bd61a460b691d770017c978edf19f6552654dbf234af0f6f`。

该作者工件可以进入主稿外部基线实施队列。下一步应先保留这份原生 R0，再以独立适配版本处理上述源码问题和统一执行接口；在共同地图、任务流、真实揭示数、时间预算与观测制度下进行论文对照。SRDC、AR/lag2、EWMA、解析代价仍是本项目机制或消融，不能替代这项外部作者基线。此次未改主线冻结参数、未运行 guest、未修改其他 baseline 仓库、未 commit 或 push。
