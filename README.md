# MAPF：空间跟踪误差下的执行协调

研究问题：多机器人沿 MAPF 路径运动时，如何把有依据的空间误差占用转成通行约束，在相同安全要求和合法信息条件下减少执行等待。当前按[文献修订方案](LITERATURE_GUIDED_RESEARCH_PLAN_20261016.md)优先评估 WinkTPG（T-ASE 2026）与 dSLAP（TAC 2025）的方法结合；MAPF-X 与 ExecTimeNet/ESADG 作为直接近邻。先核误差来源与作者工件，再判断学习预测的增量，最终模型尚未锁定。

最新执行为[G2c 误差来源采集](PROBABILISTIC_ERROR_SOURCE_20261016.md)：旧日志去重与端点诊断完成；新采集按一次授权启动，在显示环境初始化失败，新增观测为0。修正实现及替代清单已静态冻结，尚未授权、未运行。最近有效机制结果仍为[G2b](PROBABILISTIC_WINDOW_DIAGNOSTIC_20261016.md)，仅支持合成方向规则，尚无学习或高斯独立优势。L20/21 选组扩展与训练保持停止。

- [当前状态、资格与下一步](.github/README.md)：唯一当前入口。
- [进度历史](GITHUB_PROGRESS.md)：按轮次查成果、失败和当时的限制。
- [论文工作稿](MANUSCRIPT_PREEXPERIMENT.md)：受保护草稿；本机未提交修改单独保留。
- [固定 73 科学规格](73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md)：固定时点依据，不由文件名 DRAFT 推断可修改。

## 分支与工作区

`main` 是唯一当前总入口。按职责保留分支，不按历史文件中的“下一步”重新启动研究路线。

| 分支 | 状态与职责 | 本机工作树 |
|---|---|---|
| [main](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/main) | 活动：方案、验收、总进度与论文 | `MAPF_PIED_MDDR_RESEARCH` |
| [explore/error-aware-guidance](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/error-aware-guidance) | 执行与计量复用；新框架及空间占用接口待核，旧选组扩展停止 | `MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE` |
| [explore/query-value-feasibility](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/query-value-feasibility) | 合法反馈、配对工具与后续误差数据资格；不重开查询学习 | `MAPF_QUERY_VALUE_FEASIBILITY` |
| [explore/learned-query](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/learned-query) | 归档：旧模型及正负证据，不重开 | `MAPF_PIED_MDDR_LEARNING_EXPLORE` |
| [explore/gaussian-mapf-feasibility](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/gaussian-mapf-feasibility) | 误差来源与范围传播评估，保留有界/概率同条件比较；分布未锁定 | `MAPF_GAUSSIAN_FEASIBILITY` |

四探索分支各有独有提交，不能当作已合并临时分支删除。其 `.github/README.md` 提供当前角色并指向main；根README保留冻结L7快照。支线进度中的旧日期、运行许可和“下一步”只描述当时状态。活动代码/运行工件很多仅在本机，远端导航不代表已公开这些内容。

旧稿分支 `manuscript-revision-20260917` 已合并的历史完整保存在main，并以 `archive/manuscript-revision-20260917` 标签保留原tip；该历史不构成第六条研究线。

## 本机工件

| 位置 | 用途 |
|---|---|
| 本仓库 `implementation/` | 主线实际实现；当前留本机 |
| 本仓库 `implementation_binding_evidence/` | 按轮次冻结的实现证据、报告和清单；当前留本机 |
| 执行树 `exploration/optimizer_guidance/` | 当前L1–L14适配、捕获和实际运行材料 |
| query-value树 `exploration/optimizer_guidance/` | 当前完整配对收件与标签资格接口 |
| 旧学习树 `exploration/learned_query/` | 历史模型与正负证据 |
| 根目录编号文档 | 历史规格、论证和回执；按当前入口定点查阅 |

本次整理只改变导航与进度说明，不移动冻结路径、不改主稿、不上传实现或原始数据。公开仓库中的导航不会使本机证据自动公开。

旧 9 月 21 日交接、旧编号文件中的 WORKING/pending 和历史“下一步”只描述当时状态；DARI 已退出当前路线。
