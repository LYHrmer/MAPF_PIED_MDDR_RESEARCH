# MAPF：SCI 小论文与硕士论文

本仓库维护两条研究支线，共享必要的代码与证据底座。当前均处于候选问题验证阶段，尚未确认论文创新或投稿条件。

- **[SCI 小论文](tracks/sci/README.md)**：给定合法初解，在有限总计算预算内改善MAPF路径质量。以ADDRESS为实现主干，集中检验一项修复机制；学习按实际瓶颈选择，不另搭深度RL系统。目标是2026年形成SCI稿件。
- **[硕士论文](tracks/thesis/README.md)**：引用同一优化器，先查等成本改路与名义运动收益，再研究空间误差改变哪些可行性、等待和完成时间约束。学习不预先承诺独立RL章节，小论文不等待误差模块或实物标定。

[唯一当前研究决定](docs/RESEARCH_PLAN.md) · [最新进度](GITHUB_PROGRESS.md) · [工作树和模块导航](REPOSITORY_NAVIGATION.md) · [共享版本清单](shared/README.md) · [历史与停止路线](archive/README.md)

## 启动顺序

1. 先读总体研究决定和最新进度，再进入相应研究工作树；修改前重查本地及真实远端状态。
2. 新代码分别进入 `tracks/sci/`、`tracks/thesis/`；共享组件按固定提交和内容摘要引用。旧执行、来源、工具树暂为底座交接入口，不能读取它们任意最新文件作为正式依赖。
3. 新科学运行或训练必须按真实授权、固定输入、预算和失败保留规则执行。SCI前两批各六项DEV已完成；第三批完整ADDRESS在第3项失败后停批，结果见[支线入口](tracks/sci/README.md)。授权文件不能替代用户指示，已消费或关闭的许可不得重用。

共同预算三项功能DEV已按新授权全部完成，零重试、许可消费；random32本次在构组软截止后返回合法方案。旧完整ADDRESS及根界修补版的成功与失败原位保留。大论文完整任务运动比较的六项三臂清单仍待授权。恢复收益、运动收益和学习价值仍未验证；详细结果与实际覆盖见[最新进度](GITHUB_PROGRESS.md)链接的单份报告。

四次旧预执行闭式DEV已全部SUCCESS，但枚举没有完成时间收益；见[冻结结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/ae058c5025eaaa61a424ef7627515d40c2e83997/exploration/spatial_constraints_s1_20261016/PREEXECUTION_DEV_RESULT.md)。它们不是独立性能实验或学习结果。

主仓 `MANUSCRIPT_PREEXPERIMENT.md` 的未提交修改、冻结证据、作者代码和失败日志原位保护。旧空间误差方案保留作历史资料，不再是总体选题约束。不复制论文库、数据或环境。
