# R13 直接来源复核与本轮对照定位

2026-10-04，本轮重新访问以下论文原始页面。本文只记录与当前三线推进有关的边界，不将文献浏览替代实验，也不声称已完整复现下列方法的benchmark。

|直接来源与版本|页面支持的内容|对本轮的约束|
|---|---|---|
|[Jiang、Lin、Li：Speedup Techniques for Switchable Temporal Plan Graph Optimization，AAAI 2025](https://ojs.aaai.org/index.php/AAAI/article/view/34487)，DOI 10.1609/aaai.v39i22.34487|已发表方法Improved GSES通过更强启发式、边分组、分支优先和增量实现加速固定路径的可切换时间图优化。|第三线使用真实作者GSES/Improved实现作为算法对照。R13新增的执行中checkpoint适配、完整图映射与物理继续必须单列，不冒充作者原CLI的原始数值结果。|
|[Should I Replan? Learning to Spot the Right Time in Robust MAPF Execution，arXiv:2604.25567v1](https://arxiv.org/abs/2604.25567v1)，2026-04-28|公开预印本用执行状态的ADG特征和前馈网络估计延迟场景中单次重规划的收益。页面记录为投稿中，不能仅凭arXiv页写成已正式录用论文。|“学习一次决策的完整后果差”“学习何时调用规划器”本身不是足以成立的新颖性陈述。查询证据获取与重规划是不同动作，但仍须给出信息、费用与任务后果的具体差异。|
|[From Discrete Plans to Real-World Execution: A World-Model-Driven Framework for Execution-Aware Multi-Agent Path Finding，arXiv:2511.21886v2](https://arxiv.org/abs/2511.21886v2)，2026-06-21|公开预印本提出预测执行状态/完成时间的ExecTimeNet，并用于REMAP规划和ESADG执行调度优化。|不能把“加入世界模型预测时间并调整执行”作为未有人研究的方向。本轮晚点查询选择与合法后缀采用先检验各自可观察、可实际执行的收益。|

官方STPG代码来源另由第三线核对：[固定commit的作者README](https://raw.githubusercontent.com/DiligentPanda/STPG/25fb931eff03f1cce23a22a68ab42b7533f85ab3/README.md)。原43个作者编译源、许可证与构建由既有R9/R10/R11来源记录及本轮pin复核绑定；研究wrapper的修改不能混入“作者源码未改”的说法中。

本轮对照有不同用途：查询线的condition、WAIT、固定LD及TRAIN预算查表是内部模块对照；第三线的GSES和Improved GSES是真实已发表作者算法；主线WAIT/paid是同输入的信息/费用机制对照。这三类不能合并成一张对外算法排名表。正式论文仍需在统一问题、输入信息、计算预算和任务流上建立适用的已发表基线比较；R13并不以接口验证条数替代这项工作。

本次从原始页面推得的研究取舍是：主线明确可收费证据的可见性，查询线在实际预算决策时刻学习完整后果，第三线先实现作者候选在已承诺执行中的真实采用。它们是需要实测的具体问题，不是未经比较的首次提出声明。
