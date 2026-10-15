# 当前工作区与历史归档

2026-10-16。用户先要求整理入口、保留五分支，随后明确允许清理过时且不再推进的分支。本轮按现行职责保留四个活动分支，旧学习分支改为历史标签；不删除工作树或本机独有内容。

| 入口 | 当前职责 | 本机路径 |
|---|---|---|
| main | 一个论文问题、统一合同、验收和结论 | `/home/lyh/MAPF_PIED_MDDR_RESEARCH` |
| explore/error-aware-guidance | 空间占用—冲突—释放及完整执行比较 | `/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE` |
| explore/gaussian-mapf-feasibility | 声明动力学、动作条件、误差范围及覆盖 | `/home/lyh/MAPF_GAUSSIAN_FEASIBILITY` |
| explore/query-value-feasibility | 合法反馈、配对日志及费用工具 | `/home/lyh/MAPF_QUERY_VALUE_FEASIBILITY` |
| archive/learned-query-20261016（标签） | 停止的查询学习历史、正负结果 | `/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE`，detached HEAD |

分支名称保留以免扰动其他窗口，但 gaussian/query 不再代表独立选题。三轮推进依次解决接口、同信息对照、联合验收；详见[当前方案](SPACE_TIME_INTERFACE_PLAN_20261016.md)。

## 日常只读这些入口

1. [统一研究方案](SPACE_TIME_INTERFACE_PLAN_20261016.md)：问题、模型、四组比较、外部基线、继续/停止条件。
2. [最小空间—执行实例](SPACE_TIME_MINIMAL_EXAMPLE_20261016.md)：坐标、约束、释放及失效情形。
3. [当前进度](GITHUB_PROGRESS.md)：已完成、失败、待验证与运行状态。
4. [最新来源报告](PROBABILISTIC_ERROR_SOURCE_20261016.md)：G2c 两次失败、短 IPC 清单及边界。
5. [文献依据](LITERATURE_GUIDED_RESEARCH_PLAN_20261016.md)：固定版本和近邻定位，后续决策以统一方案覆盖。

MANUSCRIPT_PREEXPERIMENT.md 保留用户未提交修改。旧概率诊断、仿真说明及编号文档是证据；不把旧“下一步”或已消费授权作为当前任务。

## 清理范围与恢复

| 快照标签 | 原提交 | 从当前 Git 列表退出的文件数 |
|---|---|---:|
| archive/pre-cleanup-main-20261016 | bedf23b8 | 263 |
| archive/pre-cleanup-execution-20261016 | 0e1cc23b | 293 |
| archive/pre-cleanup-source-20261016 | e48d218f | 293 |
| archive/pre-cleanup-tools-20261016 | 36564301 | 1698 |
| archive/learned-query-20261016 | 57aee7b6 | 整条停止分支归档 |

共 2547 个重复/历史文件退出活动 Git 列表，其中公共工具分支的 1405 个旧学习文件回到历史快照。main 保留当前文稿引用闭包内的 27 个编号文件及统计工具，避免破坏在用引用。三个支线的旧根 README、旧主稿和导师简报也退出当前 Git 列表，改用 `.github/README.md` 指向 main。

所有归档标签已先推送并核对远端 SHA。使用 `git rm --cached` 保留冻结原路径字节；没有物理删除数据，因此**本轮不回收磁盘空间**。本机根目录仍可见冻结文件，GitHub 当前文件列表与日常入口已精简。main 的约 69 GB 主要是历史证据、第三方依赖和 Git 对象，不能按“旧文件”整体清空。不得用 `git clean -fdx` 清理这些保留文件。

历史内容可在 [GitHub 标签列表](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tags) 查看。读一个旧文件可使用：

```bash
rtk proxy git show archive/pre-cleanup-main-20261016:GITHUB_PROGRESS.md
```

若以后确需恢复旧分支，先检查本机 detached 工作树和其他窗口，再从 `archive/learned-query-20261016` 建分支；不直接覆盖现有目录。旧学习分支存在 16 个独有历史提交，标签完整保护；其已跟踪代码与公共工具分支旧快照相同，但本机未跟踪内容不同，故保留原目录。

本机整理前逐文件 SHA、移出清单与整理后核验保存在 `implementation_binding_evidence/repository_cleanup_20261016/`。未复制大型目录，冻结证据及失败不回写。后续新增代码进入各分支单一活动模块，轮次写入同一进度文件，不再每轮生成一套孤立目录。
