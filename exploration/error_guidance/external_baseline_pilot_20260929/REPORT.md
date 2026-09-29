# 官方 Guided-PIBT：固定 2 × 2 外部基线运行先导

2026-09-29。固定两个作者完整输入、seed 42/43，共4格，每格450步，均运行完成并通过独立轨迹与任务核验。复用先前已验证的10-agent seed42；本次只新增3次native，合计 **12.332587秒**，没有重跑挑结果、扩大地图、改变作者配置或增加规划预算。这是外部已发表方法的实验管线先导，尚不是新方法性能比较或原论文结果表复现。

## 来源与实现身份

上游：[作者官方 Guided-PIBT](https://github.com/nobodyczcz/Guided-PIBT)，固定提交 `7f4b91e4ed134229710945a4670a78639cf008d5`（2025-07-21，论文发表后的仓库版本），许可证见 [原文副本](UPSTREAM_LICENSE.txt)。不是OnlineGGO vendored副本。实际配置保持作者README的 `GP-R100-Re10-F2`：GUIDANCE、GUIDANCE_LNS=10、INIT_PP、RELAX=100、OBJECTIVE=1、FOCAL_SEARCH=2，Release，未启用MAPFT。

| 身份 | 源码变化 | 本次用途与可主张内容 |
| --- | --- | --- |
| 作者原版 | 固定commit，无变化 | 原先完成原版R0运行；未导出轨迹，不能补写成原版同轨验真 |
| 仅观测后继 | 恢复已有start/actualPaths/tasks/events导出 | 原先独立轨迹已验真；保留random_device，未证明与另次原版同轨 |
| 公开seed＋日志后继 | 观测补丁，再显式传入原优先级shuffle种子 | 本次四格实际身份；seed接口是公开复现适配，不是作者原生功能或新算法 |

两份精确补丁为 [轨迹导出](gpibt_trace_export.patch) 与 [seed读取](gpibt_seed_adapter.patch)。运行前逐一比较所有guided-pibt tracked文件，仅 `CompetitionSystem.cpp` 和 `MAPFPlanner.cpp` 不同，并检查最终源码SHA；未改算法、验证器或目标。复用既有binary SHA `faa343622008efc546bac1dd18fc80223d5d64fca8860223623a8233a5e69694`，本次没有重新编译。源码/二进制/配置/输入身份见 [manifest](runs/manifest.json)。原版、仅观测和seeded目录及其旧回执保留不动。

## 固定工作负载与预算

[事前协议](PROTOCOL.md)在新native启动前写入。作者 `visualizer_example_sts.json` 与 `sortation_small_0_200.json` 只在teamSize=10/200不同，均使用原33×57地图、1564可通行格、同一200起点和50000任务序列，roundrobin、每agent只揭示1任务。没有生成或修改输入。两种密度约0.639%和12.788%。**roundrobin给agent分配的任务切片依赖N，因而这是两个作者工作负载，不是严格控制所有个体任务后的纯密度效应实验。**

所有格保持原默认450离散步、每次规划限10秒、整进程组硬限60秒。成功轨迹统一检查450步；失败/超时本应保留，实际本次无失败或超时。三个新进程的运行数和上限没有因结果改变。10-agent seed42完整旧结果、事件和原receipt通过SHA校验后复制，保留`origin_receipt.json`；没有把重用格计入新运行时间。

## 实际结果

| 作者team / seed | 完成 / 分配 / 截止pending | 已完成任务平均flow（离散步） | 已完成flow总和 | pending截止年龄总和 | native wall秒 | planner秒总和 / 最大单次 |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| 10 / 42，复用 | 141 / 151 / 10 | 30.078014 | 4241 | 259 | 1.718601 | 1.622174 / 0.010748 |
| 10 / 43，新跑 | 141 / 151 / 10 | 30.113475 | 4246 | 254 | 1.820483 | 1.747924 / 0.014244 |
| 200 / 42，新跑 | 2244 / 2444 / 200 | 38.090018 | 85474 | 4526 | 5.381932 | 5.169388 / 0.023048 |
| 200 / 43，新跑 | 2253 / 2453 / 200 | 37.726143 | 84997 | 5003 | 5.130172 | 4.950696 / 0.020824 |

[JSON汇总](runs/summary.json)、[CSV](runs/summary.csv)保留未舍入数值；每格`verification.json`包含451点完整累计完成曲线、动作计数、原始文件SHA及删失统计。每格`result.json`、`event_log.txt`、stdout/stderr和receipt完整保留。

四格累计 **189,000动作、189,420位置**；边界、障碍、非邻接移动、顶点和反向边冲突均未发现。独立核验器使用实际非旋转`R/D/L/U/W`语义，未信任原JSON中的`actionModel=MAPF_T`标签、AllValid或空errors。每个时间步从原起点重建全体位置；按作者roundrobin任务源和实际到达重建全部分配/完成，再逐项匹配JSON及文本事件日志。另有正例和7个负例验证顶点/反向边/越界/障碍/未知动作/伪造任务事件/缺失动作均被拒绝。离线重算回执见 [offline_verification](offline_verification/receipt.json)。

这个roundrobin场景每agent始终恰有一个已分配任务，因而“已完成flow＋pending截止年龄”恒为`N×450`，四格分别4500/4500/90000/90000。这是记账恒等式，不能拿它声称方法优劣。已完成均值是有条件统计，不能隐藏未完成任务；完成任务数和完整服务曲线才是本pilot的主要原始产出。此处flow是完成−分配，不是所有绝对完成时刻之和。

规划/墙钟时间来自并行工作的宿主，没有环境隔离，不能据此声称算法更快或可扩展性。seed是全运行单位；450时间步、200个agent、任务数均不构成独立随机重复。两seed、单地图不支持置信区间或广泛优越性。

## 本次交付与下一步

交付可执行[harness](harness.py)、独立[validator](validator.py)、无需native的[归档重算](verify_archive.py)、两个作者输入及其原地图/起点/任务副本、补丁、许可证和全部raw。初次归档复制曾使用不存在的`LICENSE`路径，读取到真实`LICENCE.txt`后改为原文复制；此文件名修正未触发任何额外native或改变实验数据。

下一实质工作是[共同执行误差适配合同](COMMON_EXECUTION_ERROR_CONTRACT.md)的实现与零误差一致性验收，然后接官方OnlineGGO实际学习策略。合同目前只有设计，没有连续执行、空间扰动或学习臂结果。它明确因果信息集、正常END、终点占用、共用安全准入、误差与延迟区分、失败/删失和成本记账。当前motion-only/解析/lag2等只可作为内部诊断与消融；不能替代GPIBT、OnlineGGO等外部论文基线。
