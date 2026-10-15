# MAPF：空间跟踪误差下的执行协调

研究问题：多机器人沿 MAPF 路径运动时，如何把有依据的空间误差占用转成通行约束，在相同安全要求和合法信息条件下减少执行等待。当前以[统一方案](SPACE_TIME_INTERFACE_PLAN_20261016.md)为准，保留[文献依据](LITERATURE_GUIDED_RESEARCH_PLAN_20261016.md)。WinkTPG许可未明确；SADG已有无ROS作者核心复现，作为条件备选。MAPF-X与ExecTimeNet/ESADG保留为直接近邻，学习是否需要仍待验证。

最新交付为[S1空间占用—执行约束实例](SPACE_TIME_MINIMAL_EXAMPLE_20261016.md)：探索性接口与37项解析/静态检查通过，完整world及在线费用未测；简单方向规则已解释本例，不训练。

最新来源执行为[G2c 误差来源采集](PROBABILISTIC_ERROR_SOURCE_20261016.md)：旧日志去重与端点诊断完成；两次分别授权的采集先后因显示环境、IPC路径过长失败，新增有效观测为0。短IPC路径修正及唯一清单已静态冻结，未授权、未执行第三次world。最近有效机制结果仍为[G2b](PROBABILISTIC_WINDOW_DIAGNOSTIC_20261016.md)，仅支持合成方向规则，尚无学习或高斯独立优势。L20/21 选组扩展与训练保持停止。

- [当前状态、资格与下一步](.github/README.md)：唯一当前入口。
- [进度历史](GITHUB_PROGRESS.md)：按轮次查成果、失败和当时的限制。
- [论文工作稿](MANUSCRIPT_PREEXPERIMENT.md)：受保护草稿；本机未提交修改单独保留。
- [固定 73 科学规格](73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md)：固定时点依据，不由文件名 DRAFT 推断可修改。

## 分支与工作区

`main` 是唯一当前总入口。按职责保留分支，不按历史文件中的“下一步”重新启动研究路线。

| 分支 | 状态与职责 | 本机工作树 |
|---|---|---|
| [main](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/main) | 活动：方案、验收、总进度与论文 | `MAPF_PIED_MDDR_RESEARCH` |
| [explore/error-aware-guidance](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/error-aware-guidance) | 主线实现：空间占用到执行约束及完整执行比较；S1已静态检查，旧选组停止 | `MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE` |
| [explore/query-value-feasibility](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/query-value-feasibility) | 公共工具：合法反馈、日志、配对比较与费用；不重开查询学习 | `MAPF_QUERY_VALUE_FEASIBILITY` |
| [explore/learned-query](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/learned-query) | 归档：旧模型及正负证据，不重开 | `MAPF_PIED_MDDR_LEARNING_EXPLORE` |
| [explore/gaussian-mapf-feasibility](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/gaussian-mapf-feasibility) | 误差来源、动作条件范围与覆盖依据；有界/概率共同问题比较，不预设高斯 | `MAPF_GAUSSIAN_FEASIBILITY` |

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

本轮S1小型解析接口在执行分支公开，主仓公开方案与实例；旧实现和原始数据按原范围留本机。冻结路径和主稿保持，公开导航不会使旧本机证据自动公开。

旧 9 月 21 日交接、旧编号文件中的 WORKING/pending 和历史“下一步”只描述当时状态；DARI 已退出当前路线。
