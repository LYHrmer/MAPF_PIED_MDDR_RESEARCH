# P6 当前入口（2026-10-11）

[五线统一进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md#portfolio-p6)。

高斯仍保留P3限额备选：原版单次25+5秒提案不变、未运行；不继承主线P4授权。本轮C组支持主线P4独立结果核验与P6小型监督适配，没有扩大高斯模型/实验。

P4冻结G0/G1已实际完成并独立核对，G1 makespan10.1→8.3s、消息数相同；仅登记有限圆盘条件模型的简单里程碑机制，不是高斯结论或学习收益。P6前序历史+双向完整实现已冻结，未执行；下一步先判强规则余量。完整费用、实机安全和学习有效性仍UNKNOWN，旧高斯资料与五稿保持。

---

## 当前入口：P5（2026-10-11）

高斯工件及P3限额原版提案保持。第三组本轮对主线两车任务公式、END延迟、双向安装和历史接口作定点反方，无新增高斯实现或运行。 优先P4已备基线在具体授权后取得执行证据，再收敛P5完整配对与合法信息来源。本轮仅实现/静态/冻结/清单，科学运行、预测、训练和新标签均0。[统一P5进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md#portfolio-p5)。本机主报告`implementation_binding_evidence/portfolio_p5_20261011/REPORT.md`，以下历史保持。

## 当前入口：P4（2026-10-11）

本轮高斯工件无变更；第三组转为支持主线共同执行的监督实现和几何peer。P3高斯原版25+5秒提案、权重/语义缺口及限额定位保持，未运行。新P4的60+5秒清单仅覆盖主线两臂，不共享授权。 本轮仅实现、静态核查、冻结与具体清单，科学运行/预测/训练均0，研究有效性UNKNOWN。[统一P4进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md#portfolio-p4)。主本机入口`/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/portfolio_p4_20261011/REPORT.md`；以下历史保留。

## 当前入口：P3（2026-10-11）

C已接固定MAPF-X原版单次监督与结果接纳实现，复用P2构建；1次/25+5秒/4GiB/16MiB监测/零重试，默认关闭且无运行。训练语义/权重及研究增量仍UNKNOWN。 本轮只实现非决策基础接口并作静态核查，科学运行/预测/训练均0，CONDITIONAL。[统一P3进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md#portfolio-p3)；本机各组`portfolio_p3_20261011/`报告为详细入口。以下历史保留。

## 当前入口：P2 高斯限额可行性（2026-10-10）

C组已保存81份作者小源码／配置、核27处代码；MAPF-X原版main静态构建成功，27.753秒。已知整边几何、时间不确定与风险分配不再作为泛化新意。仅保留同风险相位条件占用待证问题；科学运行、候选实现、推理与训练均0，R0整体仍UNKNOWN。原版运行清单已列，但监督入口／授权及学习语义仍缺。 状态CONDITIONAL。[统一P2进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md#portfolio-p2)。本机交付目录：`exploration/gaussian_mapf/portfolio_p2_20261010/`。以下P1及更早记录保留，最新优先级以P1/P2为准。

# 高斯 MAPF 可行性研究支线

> **P1 路线调整（2026-10-10）**
> P1：继续作为限额模型备选，主研究回到 MAPF/LMAPF 空间执行误差。先核 CC-K-CBS/MAPF-X 下的具体缺口；未锁题、未实现、未运行。不能以高斯加学习本身作为创新；最新近邻补充与组织取舍见总方案。
> [统一研究问题、各线职责与停止条件](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/RESEARCH_PORTFOLIO_20261010.md)。本轮仅调整研究计划，未改冻结证据或授权科学运行。以下旧轮次按历史范围阅读。

本分支为 `explore/gaussian-mapf-feasibility`。请先读[高斯支线入口](GAUSSIAN_HANDOFF.md)：G1 已完成问题与文献/工件登记，尚未锁题、实现候选方法或运行实验。

以下为分支基点继承的有界主线导航，不代表高斯支线已经取得同样实现或安全保证。

## 继承的有界主线导航

研究问题：MAPF 执行中，在有界空间跟踪误差与有限真实更新资源下，何时查询进度，以及如何据此安全协调。

- [当前状态、资格与下一步](.github/README.md)：唯一当前入口。
- [进度历史](GITHUB_PROGRESS.md)：按轮次查成果、失败和当时的限制。
- [论文工作稿](MANUSCRIPT_PREEXPERIMENT.md)：受保护草稿；本机未提交修改单独保留。
- [固定 73 科学规格](73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md)：固定时点依据，不由文件名 DRAFT 推断可修改。

## 工作区位置

| 位置 | 用途 |
|---|---|
| 本仓库 `implementation/` | 主线实际实现；当前留本机 |
| 本仓库 `implementation_binding_evidence/` | 按轮次冻结的实现证据、报告和清单；当前留本机 |
| 相邻 `MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/` | 查询支线工作树 |
| 相邻 `MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/` | 执行支线工作树 |
| 根目录编号文档 | 历史规格、论证和回执；按当前入口定点查阅 |

本次整理只改变导航与进度说明，不移动冻结路径、不改主稿、不上传实现或原始数据。公开仓库中的导航不会使本机证据自动公开。

旧 9 月 21 日交接、旧编号文件中的 WORKING/pending 和历史“下一步”只描述当时状态；DARI 已退出当前路线。
