# LMAPF 空间误差与执行占用引导探索

当前分支：`explore/error-aware-guidance`。从 `main@af17410` 建立，使用同一远端
仓库 `LYHrmer/MAPF_PIED_MDDR_RESEARCH`。本目录是独立 Git worktree。

| 分支 | 负责的问题 | 当前工作入口 |
| --- | --- | --- |
| [`main`](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/main) | PIE-D 误差执行、完整查询与实际费用闭环 | 主线当前进度 |
| [`explore/learned-query`](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/tree/explore/learned-query) | 在既有路径上选择查询对象，分离预测与组合决策 | 查询学习及合法 AND 预检 |
| **`explore/error-aware-guidance`（本分支）** | 固定空间误差安全层上，以执行占用/等待代价引导路径 | [误差引导探索](exploration/error_guidance/README.md) |

先检验空间误差与实际等待是否能改变合法路径候选的优劣，再判断学习能否提供
独立收益。当前不宣称模型已训练、OnlineGGO 已复现、全成本净收益或完整 LMAPF
实验已通过。PIE-D 是可继续使用的规划执行基础，探索学习路径引导不自动意味着换底座。

本分支新增工作只放在 `exploration/error_guidance/`。继承的论文和历史文档是
分支起点快照；主线最新事实请看 `main`。主线未提交的主稿修改不属于这个分支。
