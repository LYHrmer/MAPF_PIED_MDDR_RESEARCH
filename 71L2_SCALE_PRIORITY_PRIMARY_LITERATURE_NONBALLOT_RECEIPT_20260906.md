# 71L2：大规模主线新增一手文献核验与候选比较记录

2026-09-06；NONBALLOT 来源/构造记录，不是已经审过的新候选，不替代旧 69L1 约定报告。原 69L1 尚无有效回执；本记录响应用户新要求，在大规模 lifelong 主线上增查不同方法与可借鉴组件。没有实验、性能验证、参数赋值或采用决定。若纳入 72，须随新固定候选完整顺序审查。

## 1. A/B 有界任务的完整实际回执登记

真实任务 /root/scale_journal_mechanisms，fork_turns=none，不用任何 skill，不读本地候选/旧报告、不写文件、不运行代码。原任务仅两篇新增期刊，已实际返回完整非空最终消息；root 完整阅读题录、亲见范围、合法全文寻找、机制边界、PIE 兼容性、可证伪预测和未读部分。以下为根按完整回执归档的事实与限定，不冒称两篇全文。

| 对象 | 核验题录 | 实际证据强度 |
|---|---|---|
| A：A Robust Lifelong Multi-Agent Path Finding With Active Conflict Resolution and Decentralized Execution | Feng Zhuang、Ting Huang、Quan Xu、Yue-Jiao Gong、Jing Liu；RA-L 10(5), 4652–4659，2025-05；DOI 10.1109/LRA.2025.3554099 | 代理亲见 IEEE 登记 Crossref 题录和作者学校主页条目；没有一手核实的摘要或正文 |
| B：A Scalable Framework for Lifelong Multiagent Path Finding With Asynchronous Actions | Hyojeong Kim、Woonsang Kang、Sung-Kee Park、Myo-Taeg Lim、Yoonseon Oh、ChangHwan Kim；TII 22(8), 6859–6870，2026-08-01；DOI 10.1109/TII.2026.3681327 | 代理亲见机构完整摘要/题录、Crossref、KIST 元数据、实验室成果列表；root 再次直接打开机构页核实摘要和正式卷期，未见正文 |

A 来源：[Crossref 出版社登记](https://api.crossref.org/works/10.1109/LRA.2025.3554099)、[黄婷作者学校主页期刊第 13 项](https://faculty.xidian.edu.cn/HT2/zh_CN/index.htm)、[Gong 作者成果页](https://yuejiaogong.github.io/pub/)、[IEEE 正式入口](https://ieeexplore.ieee.org/document/10937741/)。IEEE 及 PDF 入口未取得正文；作者页未发现该文公开全文。第三方摘要的性能数字和冲突规则不纳入技术证据。标题不足以判定处理的是时长、空间偏差还是反馈错误，也不足以证明 active conflict 消解能够只加 WAIT 保留 PIE 新 MOVE 来源。A 作为近邻全文缺口保留。

B 来源：[高丽大学当前官方记录](https://pure.korea.ac.kr/en/publications/a-scalable-framework-for-lifelong-multiagent-path-finding-with-as/)、[Crossref 出版社登记](https://api.crossref.org/works/10.1109/TII.2026.3681327)、[KIST 仓储](https://pubs.kist.re.kr/handle/201004/154784?mode=full)、[作者实验室成果](https://sites.google.com/view/robots-oh/publications)、[IEEE 正式入口](https://ieeexplore.ieee.org/document/11511843/)。机构现页明确 Published - 2026 Aug 1，与 Crossref 卷期一致。早先根搜索缓存的 Accepted/In press 及 KIST 早期 1–12 页元数据已由新证据更新，不能覆盖当前正式记录。KIST 标 isOpenAccess=N，所见 HTML 没有 PDF 链接；IEEE 验证页和视频读取失败均不算全文或看过视频。similarity-checking staging 链接不冒充公开全文。

B 摘要确认非一致动作时长下的异步执行：规划阶段处理循环冲突，执行调度维护顶点先后关系；复用非空闲者剩余路径，经重新同步接入规划；采用贪心任务分配。作者摘要报告较大仓储队列和吞吐增益，尚未核正文中的地图、预算、对照及安全统计。空间轨迹偏差、错误完成反馈、丢失/乱序保护和终身无饥饿的覆盖均 UNKNOWN。本文不移植其规模、增益或设置作为本研究参数或结果。

代理完整回执中的条件性建议，root 接受为待查方向：保留原路径时的先后约束放行；复用仍然有效的剩余计划并仅更新受影响部分。root 同时保留限制：完整替换 B 的规划器/任务分配会改变 PIE 提议源；没有足够剩余计划不可假设一部件可直接移植；等待不能自行消除循环依赖；重新同步必须保持已执行、执行中与未执行状态的一致性。上述属于我们的推论，不是未读正文的真实伪代码。

回执提出的四类可证伪判断均保留：依赖维护和重同步成本可能吞掉节省；变化传播到大部分计划时局部复用可能失去优势；消环的路径/等待代价可能大于收益；应把错误完成消息与真实执行延迟分开检验信息接口。公平条件是同任务/地图/扰动创新、固定提议源或显式独立算法域、总预算及全部维护成本，不能只统计规划核心时间。现有来源不能证明 B 或 71 对未读情形失效，也不能按“轻量”或“事务”名称先判优劣。

## 2. 根新增会议全文及期刊部分阅读

**ECAI 2024：Multi-Agent Path Finding with Real Robot Dynamics and Interdependent Tasks for Automated Warehouses。** Vassilissa Lehoux-Lebacque、Tomi Silander、Christelle Loiodice、Seungjoon Lee、Albert Wang、Sofia Michel；DOI 10.3233/FAIA241017。[官方会议 PDF](https://journals.sagepub.com/doi/pdf/10.3233/FAIA241017)。root 实际完整阅读 9 页提取文本 L0–856：首次 L0–336，后续连续窗口覆盖并从原缓存补 L469–508；未审图像、未核 PDF 原始字节散列。这是会议，不增加期刊全文计数。

正文将朝向、负载、动态行驶时间和实体扫掠占用结合到 IPP/VP*；指定等待位置及非干扰/可达条件限制其完备性。预计算边/占用有减少在线几何工作的借鉴意义；搜索预算停止与真正穷尽须区分。其鲁棒时长扰动不能转称任意空间偏差或错误反馈。真实机器人例子和限定规模研究不是本研究的大规模证明。完整 VP* 与任务分配改变路径来源；可借鉴几何接口与失败条件，不能直接称 PIE wrapper。同样应保留论文对时序裕量不足及意外偏差的限制。

**RAS：Elevating priorities for an efficient and complete lifelong multi-AGV pathfinding on roadmaps。** Gregor Klančar、Matevž Bošnak、Viktor Zaletelj、Rok Vrabič、Andrej Zdešar；DOI 10.1016/j.robot.2025.105295；RAS 197, 105295，2026-03。[出版商页](https://www.sciencedirect.com/science/article/pii/S0921889025003926)。root 实际读官方搜索返回的摘要、引言/章节预览、highlights 与代码可用性，直接打开 403，未获全文。预览涉及优先 SIPP、安全位置、预计算占用区间/安全裕量、异构足迹与速度；不能由摘要泛化完备性。作者代码入口 [PSIPP_demo](https://github.com/FE-LAK/PSIPP_demo) 已见但未读代码、未克隆/构建。

**Sensors：Robust Multi-Agent Path Finding Method for Obstacles and Environmental Changes in Factory Environments。** Seihoon Park、Jinwon Lee、Geonhyeok Park、Ikhyeon Cho、Seongjoon Moon、Woojin Chung；DOI 10.3390/s26134139；Sensors 26(13), 4139，2026-07-01。[官方页面](https://www.mdpi.com/1424-8220/26/13/4139)、[版本记录](https://www.mdpi.com/1424-8220/26/13/4139/notes)、[PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC13363869/)。root 已读官方/PMC 搜索返回摘要、引言贡献、部分 3.1/4.1、结论和可用性语句；PMC 直接打开验证码，未计全文。片段支持 CBS 框架的走廊/路口引导、受影响者局部重规划与交通裕量；不据此宣称其空间偏差/反馈错误能力已经查清，也不把测试集成功率当普遍定理。可借鉴受影响范围的测量与局部更新成本，整体 CBS 路径修改是不同提议域。

## 3. 新增有界后续与根选型问题

同一 /root/scale_journal_mechanisms 完成 A/B 之后，root 已实际发起新的有界 followup，只查 RA-L 2022 的 Prioritized Safe Interval Path Planning for Multi-Agent Pathfinding With Continuous Time on 2D Roadmaps，从[作者项目](https://omron-sinicx.github.io/PSIPP-CTC/)寻找合法全文。重点为预计算连续时间几何冲突的准确机制、离线/在线成本、失败与完备性边界，是否 lifelong 及误差身份。当前登记为运行中，不能把项目摘要或存在 PDF 链接先计全文完成；返回后另记亲见覆盖。

根当前待检验的组合想法：在不改变 PIE 新 MOVE 的条件下，研究固定地图/实体边界的几何退休阈值预计算和仅更新受影响阻塞关系，配合可信进度和观测调度，减少在线几何与全体扫描。此处是构造线索，不是新颖性或复杂度结论；预计算并不新，必须核保守几何阈值、受影响集合最坏规模、全成本和对照共享能力。也可能发现异步/剩余计划方向更合适，不能因 71 已写长稿而排除。

选型尚缺：直接近邻 A、B 以及既有 J6/J7 正文；原 clock 完整依赖/适配语义；各路线物理/信息/动作接口的匹配；主效应在实际维护费用下如何被推翻。已读/部分/摘要/题录严格分开，来源数量不等于这些问题已闭合。用户两台 LIMO 是可选现实证据资源，不以未确认的硬件成功替代大规模仿真，也不把离散格图中的纯随机延迟命名为空间误差。

本记录不赋保护参数、不生成载荷和结果，不改冻结候选。保留 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT；后继实质工件仍须科研导师、Nature、无 skill 独立逻辑和根顺序验收。
