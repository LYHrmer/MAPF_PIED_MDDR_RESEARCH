# MAPF：SCI 小论文与硕士论文

本仓库维护两条研究支线，共享必要的代码与证据底座。当前均处于候选问题验证阶段，尚未确认论文创新或投稿条件。

- **[SCI 小论文](tracks/sci/README.md)**：优先检验标准离散 MAPF 的局部路径修复效率；先补强传统对照并定位实际瓶颈，之后决定是否采用图学习、监督学习或 RL。目标是2026年形成质量正常的SCI稿件，时间目标不等于发表保证。
- **[硕士论文](tracks/thesis/README.md)**：围绕同一 MAPF 修复/优化问题组织传统方法、学习辅助及执行误差扩展与系统验证。小论文不等待误差模块或实物标定。

[唯一当前研究决定](docs/RESEARCH_PLAN.md) · [最新进度](GITHUB_PROGRESS.md) · [工作树和模块导航](REPOSITORY_NAVIGATION.md) · [共享版本清单](shared/README.md) · [历史与停止路线](archive/README.md)

## 启动顺序

1. 先读总体研究决定和最新进度，再进入相应研究工作树；修改前重查本地及真实远端状态。
2. 新代码分别进入 `tracks/sci/`、`tracks/thesis/`；共享组件按固定提交和内容摘要引用。旧执行、来源、工具树暂为底座交接入口，不能读取它们任意最新文件作为正式依赖。
3. 本轮仅实现和静态核验；新科学运行或训练必须按真实授权、固定输入、预算和失败保留规则执行。授权文件不能替代用户指示，已消费许可不得重用。

四次旧预执行闭式DEV已全部SUCCESS，但枚举没有完成时间收益；见[冻结结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/ae058c5025eaaa61a424ef7627515d40c2e83997/exploration/spatial_constraints_s1_20261016/PREEXECUTION_DEV_RESULT.md)。它们不是独立性能实验或学习结果。

主仓 `MANUSCRIPT_PREEXPERIMENT.md` 的未提交修改、冻结证据、作者代码和失败日志原位保护。旧空间误差方案保留作历史资料，不再是总体选题约束。不复制论文库、数据或环境。
