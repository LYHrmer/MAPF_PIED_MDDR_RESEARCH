# 公开基线的实际复现入口

2026-09-29。已从作者代码构建并实际运行 PIE-D、GPIBT 与 LSMART。以下是最小工件资格运行，**不是跨算法性能比较**：地图、规模、时间单位和执行模型不同，任务数不可横向排名。内部 AR、lag2、解析、RR、WAIT、SRDC 只用于机制与消融，不冒充外部基线。

| 工件与固定版本 | 本轮实际交付 | 正式比较前还缺什么 |
|---|---|---|
| [PIE-D / AAAI 2025](https://ojs.aaai.org/index.php/AAAI/article/view/34506)，[作者代码](https://github.com/YueZhang-studyuse/LMAPF-delay/tree/74cfba3c81a0c165c2e7044dea6fd4dee8ddf415) | 完整分支原码，GNU11/Release构建21.858秒；作者random输入100 robots、20步，运行21.128秒，52任务；独立重放2000动作、任务分配/服务检查通过。原码与数据未改。 | 核对论文变体；独立修复版处理未初始化成员/统计变量和真实task reveal=2；再适配共同误差执行器。源码默认LaCAM-only入口没有充当完整PIE-D。 |
| [Guided PIBT / AAAI 2024](https://ojs.aaai.org/index.php/AAAI/article/view/30054)，[作者代码](https://github.com/nobodyczcz/Guided-PIBT/tree/7f4b91e4ed134229710945a4670a78639cf008d5) | 原GP-R100-Re10-F2，作者10 robots sortation输入450步完成141任务；独立导出适配核4500动作无格点冲突。另一个公开seed适配以42运行两次，任务/轨迹/非时间JSON字段相同。原算法未改。 | 公开地图与负载pilot、连续误差执行适配；离散安全不能代替连续足迹安全。原版没有公开种子，未固定seed两次轨迹不同的记录保留。 |
| [OnlineGGO / AAAI 2025](https://ojs.aaai.org/index.php/AAAI/article/view/33614)，[作者代码](https://github.com/zanghz21/OnlineGGO/tree/ff6d830e2fd5bf85ccbb72eaec0fb8df1cf1c256) | 作者C++ lifelong静态引导目标及固定官方子模块构建通过，27.304秒。 | **训练/权重与学习策略评测未复现**。静态OBJECTIVE=3不能占OnlineGGO学习方法结果栏。 |
| [LSMART作者试验台](https://github.com/smart-mapf/lifelong-smart/tree/a3780a45eb101f5b6834236f86bad39025f1e99f) | 原client和RHCR构建；server独立兼容版仅3个enum日志转int。作者5×5场景、2 robots、200 ticks，隔离运行2.280秒，报告3任务/20次planner调用。 | 共享执行反馈与GPIBT/OnlineGGO适配；还未独立检查连续轨迹。success=true不代替安全验证。LSMART不是竞争算法。 |

构建时间和宿主秒数只供复现实验成本参考，不是公平算法性能。各原始仓根许可证、commit、命令、实际输入和binary SHA已留本机证据。PIE-D使用作者`mapfPlanner=2, delayPolicy=3, delaySimulateAll=false`示例组合；20步中93个作者delay flags进入执行。52个已完成任务流时和618不包含200个未完成任务，因此不作为全体流时。

GPIBT区分三身份：作者原版、只恢复实际轨迹导出的适配版、再增加`GPIBT_R0_SEED`输入与日志的适配版。unset时仍用原random_device。seed42两次canonical动作SHA为`ff4468a7bd8befda873d786ca9a0cf8137529d67c7ed5197c5a82f63ff0e9df0`。没有修改原规划算法或原validator；独立检查器另外核边界、障碍、邻接、顶点、反向交换与FIFO任务到达。

LSMART先保留原fmt8构建失败，再保留兼容补丁及sandbox RPC运行失败。最终smoke03使用独立端口，在前次进程结束后运行；smoke02与失败前次曾短暂重叠，不作为主要回执。最终stats SHA `7594afa23f925bba2e5fc12b07cada8d6c2df3604a2e564d48d4748da779ef59`；补丁SHA `5f7e085b76803744962a436a8a92b8238fcd7a407fc1bab08619c5cdd4390ead`。没有安装新系统依赖、修改作者原版或通过重跑挑最佳值。

本机详证根：`/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/baseline_selection_20260929/`，分别见`PIED_R0_REPORT.md`、`gpibt_seeded_R0_REPORT.md`、`ARTIFACT_PREFLIGHT_20260929.json`及各原始receipt。大体积第三方仓库和二进制不重复提交到本分支；GPIBT新pilot的可复核脚本/patch/小型回执单独归档。

正式实验分两层：作者原生R0核实现身份；“公开算法＋共同执行器”表测新增误差处理。共同表统一地图、任务序列/揭示规则、机器人足迹、误差、控制器、正常END、可见字段、计算与通信预算、调参预算及失败处理。原有充分反馈方法保留原生信息版本，同信息适配另列。详见[三线设计与实验合同](RESEARCH_DESIGN_AND_BASELINES_20260929.md)。

扩展的[官方GPIBT 2×2先导](external_baseline_pilot_20260929/REPORT.md)已完成：10/200 robots × seed42/43，450步完成141/141/2244/2253任务，189,000动作独立重放。作者roundrobin任务切片随团队规模变化，因此是两工作负载试运行，不作为纯密度因果对照；没有学习或连续空间误差结果。
