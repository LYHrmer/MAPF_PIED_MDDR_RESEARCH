# 期刊机制的学习与定点复现

2026-10-18，按用户“多复现模仿相关顶刊论文思路”的新要求更新。ADDRESS继续作为唯一实现主干；先借鉴成熟论文的问题拆分、具体求解机制和消融设计，再检验本项目的针对性改动。此次已阅读下列正式来源，并定点查作者工件；**没有编译或运行这些新增作者程序，没有完成其论文实验复现**。原[八项种子开发结果](ADDRESS_SEED_RESULT.md)及其科学提交保持冻结。

## 选择与优先级

| 期刊工作 | 已有机制 | 本项目如何学习 | 当前复现状态 |
|---|---|---|---|
| [DyMAB，JAIR 86，Article 39，2026](https://jair.org/index.php/jair/article/view/19324) | 用近期奖励队列适应邻域算子价值变化 | 首选下一项机制参考；固定算子池后比较累计记忆与窗口记忆，不能把它当车辆种子排序 | 正式全文、作者链接、MIT和固定代码已核；论文与代码有具体语义差异，未编译/运行 |
| [CPLNS，IEEE TPDS 35(11):2069–2086，2024](https://ieeexplore.ieee.org/document/10553642/) | 分组协作与独立搜索平衡集中改进和多样性 | 学习多样性消融和完整计算成本控制；当前不新增多核系统 | 出版信息和摘要已核；候选公开源码已定点读，官方关联、完整论文/许可未闭合 |
| [X*，Artificial Intelligence 291:103417，2021](https://vedder.io/publications/expanding_astar_aij.pdf) | 随窗口扩大复用已有联合搜索信息 | 学习何时可复用、何时须重算，以及与无复用版本的比较 | 正式全文已读、作者项目已定位；固定代码的许可/构建条件未完成，未复现 |

ADDRESS、BALANCE、TACKLE等直接近邻仍应比较，但它们是会议论文，不能因重要就改称期刊。不会仅按刊物声望把不同问题的算法当作公平基线；三项参考也不同时接入。先完成简单强对照的未见任务准备，再选一个有具体决策空间的机制。

## 首选：DyMAB 的窗口记忆

[正式PDF](https://www.jair.org/index.php/jair/article/download/19324/27343)共27页，期刊页及DOI元数据均记录2026-07-29发表；PDF SHA `0d2355fb9e3b15e56a4b58212c12965330b7d5683959666a877adb0f01db3f0f`。不把README中旧的“accepted 2025”当发表日期。论文第17页脚注链接[作者仓库](https://github.com/amathsow/dymab)，本次固定提交`a9e43eefc6814c343a49db40d3bc4774b76f7381`，[许可为MIT](https://github.com/amathsow/dymab/blob/a9e43eefc6814c343a49db40d3bc4774b76f7381/LICENSE)。不复制论文库或地图目录。

值得学习的核心是每个邻域算子保留近期奖励，较旧奖励退出队列，从而根据搜索阶段调整算子选择。其对象是随机、同步游走、熵引导等构组算子；当前ADDRESS比较固定RandomWalk和邻域上限8，并在车辆中选种子，决策层不同。原文第4节式13–14及算法4–5、实验0和窗口消融分别提供定义、诊断与比较模板；不能将其非平稳bandit的假设和保证直接转给本项目的状态依赖搜索。

固定代码中的具体扩展点：

- [`BasicLNS::sampleDestroyHeuristicAndNeighborhoodSize`](https://github.com/amathsow/dymab/blob/a9e43eefc6814c343a49db40d3bc4774b76f7381/src/BasicLNS.cpp#L77)：算子与大小选择；[`updateDestroyWeights`](https://github.com/amathsow/dymab/blob/a9e43eefc6814c343a49db40d3bc4774b76f7381/src/BasicLNS.cpp#L55)：奖励窗口更新。本项目对应构组分派前、修复/回滚后的接口，不是简单换掉Beta抽样。
- [`generateNeighborBySynchroizedRandomWalk`](https://github.com/amathsow/dymab/blob/a9e43eefc6814c343a49db40d3bc4774b76f7381/src/LNS.cpp#L611)已经仅把正延迟车辆加入初始种子候选，零延迟车仍可在游走中成为邻域成员。这是当前朴素规则的直接代码先例，继续将它视为强对照。

已定位、仍需在复现实现中明确处理的三项差异：

1. [`LNS`构造调用](https://github.com/amathsow/dymab/blob/a9e43eefc6814c343a49db40d3bc4774b76f7381/src/LNS.cpp#L18)与[`BasicLNS`唯一声明](https://github.com/amathsow/dymab/blob/a9e43eefc6814c343a49db40d3bc4774b76f7381/inc/BasicLNS.h#L78)的参数顺序不一致。后者要求“算子数量、alpha、epsilon、lambda、window”，调用却传“alpha、epsilon、lambda、window、算子数量”。已核定义及driver入口；C++允许数值转换，故这里只报告静态映射差异，不能写成编译或科学运行失败。
2. [LNS.cpp奖励调用](https://github.com/amathsow/dymab/blob/a9e43eefc6814c343a49db40d3bc4774b76f7381/src/LNS.cpp#L201)使用按邻域大小归一化的SOC差，并仅在严格改善条件为真时入队；初始化还预填零。原文算法写逐次更新、空队列；正文采用SOC差，实验0另采用归一化差。应分别登记，不能把“仅成功入队”默认为最近所有尝试。
3. 固定源码探索重启为100，原文默认实验周期为1000；UCB分母与选择时钟也有差异。复现版应固定哪套定义，作者代码版与依据论文修订的overlay必须分开命名和保留，不默默修好后称原版。

**下一项实现交付具体限定为窗口奖励接口的软件验证与上述语义对应。** 覆盖空队列、零改善、正常失败、预算截止、出队和选择时钟；截止不自动当作搜索失败奖励。先说明选择对象及固定算子池，不同时调整种子、邻域大小、奖励定义和低层求解器。若只借用窗口思想接到现有车辆种子上，明确标为本项目适配，不能称完整DyMAB。

真正科学对照之前，需有相同算子池、奖励与总预算下的固定规则、累计记忆、窗口记忆三者；输入与代码固定，计入所有空构组、选择、修复、校验和输出成本。当前random32只有一个正延迟种子，不构成学习车辆排序的任务。原六份开发任务不改标独立测试；新初解、未见任务和多seed比较均须新清单与对应授权。

## 两项保留参考的适配边界

CPLNS的期刊摘要支持学习分组共享最好解、保留搜索多样性及通信/内存费用的设计。只读候选库[`KaenChan/cplns`](https://github.com/KaenChan/cplns/tree/e3fbcc82bf6a1f2cbab0ceb166d547865ca8210a)固定`e3fbcc82bf6a1f2cbab0ceb166d547865ca8210a`；本次尚未取得明确论文到该仓库的作者链接，树中未找到LICENSE，不能称已取得复用许可。已读源码显示默认退火主要作用于初解消冲突，合法解优化阶段默认关闭退火并把低层权重重置为1；不能把这些默认行为误称为当前“给定合法初解”阶段的已验证增强。故现阶段只作设计参考。后续如研究并行，须同时固定核数、总CPU和wall，并与等资源独立多次搜索比较，不能把额外硬件算作方法增量。

X*原文第4–5节给出逐步扩大窗口和变换搜索树的复用条件，并用不复用的NWA*作对照；[作者项目](https://vedder.io/xstar.html)链接`kylevedder/libMultiRobotPlanning`。已定位`xstar`分支SHA `11f23a490ea70e9929648960ee3572af1812bd21`，但固定源码/许可读取发生网络失败，且该分支是否对应正式论文实验版本尚未确认。窗口联合搜索不同于当前ADDRESS逐车SIPP，直接移植会扩大实现范围；先学习复用失效条件与消融设计，不重启已停止的后段失败恢复，也不继承原文最优性结论。

每项推进应留下一个具体可核对结果：原论文机制、固定工件、可执行最小入口、与当前接口的差异、共同预算下的正负结果。阅读、静态对应、编译/help、功能DEV、独立任务性能分开记录；当前只完成阅读与定点对应阶段，不用“顶刊方法”替代实际效果判断。
