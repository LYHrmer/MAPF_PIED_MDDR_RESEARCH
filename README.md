# MAPF：有界跟踪误差下的执行协调

研究问题：MAPF执行中，如何依据合法进度信息，在空间误差与有限真实更新资源下安全协调。现有有界模型及结果作为基线；当前优先核对[概率模型的对象、风险口径与决策增量](PROBABILISTIC_MODEL_ASSESSMENT_20261015.md)，有同风险强规则之外的完整收益再引入学习。L20/21当前任务上的选组扩展与训练保持停止。

- [当前状态、资格与下一步](.github/README.md)：唯一当前入口。
- [进度历史](GITHUB_PROGRESS.md)：按轮次查成果、失败和当时的限制。
- [论文工作稿](MANUSCRIPT_PREEXPERIMENT.md)：受保护草稿；本机未提交修改单独保留。
- [固定 73 科学规格](73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md)：固定时点依据，不由文件名 DRAFT 推断可修改。

## 分支与工作区

`main` 是唯一当前总入口。按职责保留分支，不按历史文件中的“下一步”重新启动研究路线。

| 分支 | 状态与职责 | 本机工作树 |
|---|---|---|
| [main](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/main) | 活动：方案、验收、总进度与论文 | `MAPF_PIED_MDDR_RESEARCH` |
| [explore/error-aware-guidance](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/error-aware-guidance) | 活动：空间执行、完整搜索与计量 | `MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE` |
| [explore/query-value-feasibility](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/query-value-feasibility) | 活动：合法信息、配对收件及学习接口 | `MAPF_QUERY_VALUE_FEASIBILITY` |
| [explore/learned-query](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/learned-query) | 归档：旧模型及正负证据，不重开 | `MAPF_PIED_MDDR_LEARNING_EXPLORE` |
| [explore/gaussian-mapf-feasibility](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/gaussian-mapf-feasibility) | 优先适配评估：误差对象、概率占用与同风险比较；尚未运行 | `MAPF_GAUSSIAN_FEASIBILITY` |

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
