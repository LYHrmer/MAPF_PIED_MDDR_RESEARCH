# 73L25：相关工作矩阵与定点核验计划

2026-09-18；NONBALLOT。本件把已收录的 26 篇不重复来源按五个对照维度排成矩阵，用于 `MANUSCRIPT_PREEXPERIMENT.md` §1.1 承诺的“完整对照沿既有文献矩阵补入”。本件**不新增任何检索**，全部来源取自现有回执与既有阅读包；**大多数单元格尚未取得定点证据**，凡未核者一律标 `[需核验]`，不以印象填表。本件不给候选投票，不改变任何门的资格状态。

矩阵的用途是双向的：确定本文在已发表工作中占据的位置，并把“补相关工作”这一模糊任务转成一份精确的定点阅读清单。**在对应单元格取得节号锚点之前，不得把该行写进正文的对照论述。**

## 1. 五个对照维度及其依据

维度直接由已收窄的可检验新颖性表述导出——“执行期由付费可信进度下界驱动的在线释放”——而非事后挑选：

| 维度 | 取值域 | 为何是对照维度 |
|---|---|---|
| **D1 空间误差表达** | 有界跟踪误差包络／概率不确定性／仅时间不确定性／静态足迹无误差集／无 | §2.1 式(1)(2) 的建模对象；决定“名义离开是否能证明实体清空” |
| **D2 占用粒度** | 连续时间区间／离散时步／整动作 | 新颖性排除的关键：亚动作粒度本身不是本文新内容 |
| **D3 执行期信息获取** | 付费主动观测／免费反馈／无（仅规划期） | §2.3 与 §3.4 的对象；付费是本文的实质约束 |
| **D4 执行期占用收缩** | 在线释放下界／固定至动作末／重排次序／不适用 | 本文机制所在维度，也是与执行谱系的分界 |
| **D5 主评价量** | 固定窗口真实服务率／累计路径完成时间／解代价／吞吐（未区分服务判定）／其他 | 决定两项工作的数值能否直接对比 |

**本文占据的单元**：有界跟踪误差包络 × 连续区间（执行期收缩）× 付费主动观测 × 在线释放下界 × 固定窗口真实服务率。该组合是否为空白，取决于下表中 `[需核验]` 的消解结果，现不宣称已确认为空白。

## 2. 二十六篇来源清单与核验强度

核验强度分四级：**锚点级**（读到节号／原文引用）、**首页级**（PDF 字节＋页数＋首页题名作者摘要，见 09-09 包 `99` 文档）、**题录级**（仅 Crossref 单 DOI）、**既有回执**（由本仓库先前回执支持）。

### A 组 框架与承重引用（正文 [1]–[4]）

| # | 题录 | DOI | 强度 |
|---|---|---|---|
| A1 | Zhang Y, et al. Concurrent Planning and Execution in Lifelong MAPF with Delay Probabilities. AAAI 2025, 39(22): 23387–23394 | 10.1609/aaai.v39i22.34506 | 既有回执 |
| A2 | Zhang Y, et al. Planning and Execution in MAPF: Models and Algorithms. ICAPS 2024, 34(1): 707–715 | 10.1609/icaps.v34i1.31534 | 既有回执 |
| A3 | Okumura K. Improving LaCAM for Scalable Eventually Optimal MAPF. IJCAI 2023: 243–251 | 10.24963/ijcai.2023/28 | 既有回执 |
| A4 | Hönig W, et al. Persistent and Robust Execution of MAPF Schedules in Warehouses. IEEE RA-L, 2019 | 10.1109/LRA.2019.2894217 | 首页级 |

### B 组 MAPF 语境近邻（既有阅读包 `MAPF_实验前必读论文_20260909`，首页级＋SHA256）

| # | 题录 | DOI | 强度 |
|---|---|---|---|
| B1 | Zhong 等. Planned synchronization for multi-robot systems with active observations. Autonomous Robots, 2026 | 10.1007/s10514-025-10225-4 | 首页级 |
| B2 | Chen 等. Scalable and Safe Multi-Agent Motion Planning with Nonlinear Dynamics and Bounded Disturbances（S2M2）. AAAI 2021 | 10.1609/aaai.v35i13.17340 | 首页级 |
| B3 | Okumura 等. Time-Independent Planning for Multiple Moving Agents. AAAI 2021 | 10.1609/aaai.v35i13.17347 | 首页级 |
| B4 | Shahar 等. Safe Multi-Agent Pathfinding with Time Uncertainty. JAIR, 2021 | 10.1613/jair.1.12397 | 首页级 |
| B5 | Zhu 等. Decentralized Probabilistic Multi-Robot Collision Avoidance Using Buffered Uncertainty-Aware Voronoi Cells（B-UAVC）. Autonomous Robots, 2022 | 10.1007/s10514-021-10029-2 | 首页级 |
| B6 | Yan、Smith、Li. WinkTPG: An Execution Framework for MAPF Using Temporal Reasoning | 10.48550/arXiv.2508.01495（arXiv；正式期刊 DOI 未核） | 首页级 |
| B7 | Okumura 等. Concrete multi-agent path planning enabling kinodynamically aggressive maneuvers. npj Robotics, 2026 | 10.1038/s44182-026-00083-2 | 首页级 |
| B8 | Stern 等. Multi-Agent Pathfinding: Definitions, Variants, and Benchmarks. SoCS 2019 | 10.1609/socs.v10i1.18510 | 首页级 |
| B9 | Li 等. Lifelong Multi-Agent Path Finding in Large-Scale Warehouses（RHCR）. AAAI 2021 | 10.1609/aaai.v35i13.17344 | 首页级 |
| B10 | Cao B. SCALE: From Real-Time Planning to Reliable Execution | 10.48550/arXiv.2607.00591（arXiv 预印本；期刊接受未核） | 首页级 |
| B11 | Chen 等. Traffic Flow Optimisation for Lifelong MAPF. AAAI 2024, 38(18): 20674–20682 | 10.1609/aaai.v38i18.30054 | 首页级 |

### C 组 连续时间占用（新颖性排除，正文 [5][6]）

| # | 题录 | DOI | 强度 |
|---|---|---|---|
| C1 | Andreychuk A, et al. Multi-agent pathfinding with continuous time. Artificial Intelligence, 2022, 305: 103662 | 10.1016/j.artint.2022.103662 | 题录级 |
| C2 | Kasaura K, et al. Prioritized Safe Interval Path Planning for MAPF With Continuous Time on 2D Roadmaps. IEEE RA-L, 2022, 7(4): 10494–10501 | 10.1109/LRA.2022.3187265 | **既有回执（71L3，强度高于本轮）** |

### D 组 执行谱系后继（正文 [7]）

| # | 题录 | DOI | 强度 |
|---|---|---|---|
| D1 | Berndt A, et al. Receding Horizon Re-Ordering of Multi-Agent Execution Schedules. IEEE T-RO, 2024, 40: 1356–1372 | 10.1109/TRO.2023.3344051 | **锚点级（73L24 §3，据作者预印本）** |

### E 组 误差建模上游（73L24，题录级）

| # | 题录 | DOI |
|---|---|---|
| E1 | Chen M, et al. FaSTrack: A Modular Framework for Real-Time Motion Planning and Guaranteed Safe Tracking. IEEE TAC, 2021, 66(12): 5861–5876 | 10.1109/TAC.2021.3059838 |
| E2 | Fridovich-Keil D, et al. Planning, Fast and Slow: A Framework for Adaptive Real-Time Safe Trajectory Planning. ICRA 2018: 387–394 | 10.1109/ICRA.2018.8460863 |
| E3 | Chen M, et al. Robust Sequential Trajectory Planning Under Disturbances and Adversarial Intruder. IEEE TCST, 2019, 27(4): 1566–1582 | 10.1109/TCST.2018.2828380 |
| E4 | Kousik S, et al. Bridging the gap between safety and real-time performance in receding-horizon trajectory design for mobile robots. IJRR, 2020, 39(12): 1419–1469 | 10.1177/0278364920943266 |
| E5 | Gong Z, et al. Safe Returning FaSTrack With Robust Control Lyapunov-Value Functions. IEEE L-CSS, 2024, 8: 1373–1378 | 10.1109/LCSYS.2024.3410636 |
| E6 | dos Reis de Souza A, et al. Robust output feedback MPC for constrained linear systems via interval observers. Automatica, 2022, 135: 109951 | 10.1016/j.automatica.2021.109951 |

### F 组 信息价值与鲁棒 MAPF（73L24，题录级）

| # | 题录 | DOI |
|---|---|---|
| F1 | Soleymani T, et al. Value of Information in Feedback Control: Global Optimality. IEEE TAC, 2023, 68(6): 3641–3647 | 10.1109/TAC.2022.3194125 |
| F2 | Atzmon D, et al. Robust Multi-Agent Path Finding and Executing. JAIR, 2020, 67: 549–579 | 10.1613/jair.1.11734 |

合计 26 篇不重复来源。其中已进入正文参考文献的为 A1–A4、C1、C2、D1 共 7 条。

## 3. 矩阵现状

`—` 表示该维度对该工作不适用；`[需核验]` 表示尚无定点证据，不得据此撰写对照论述。

| # | D1 空间误差 | D2 占用粒度 | D3 执行期信息 | D4 执行期收缩 | D5 主评价量 |
|---|---|---|---|---|---|
| **本文** | 有界跟踪误差包络 | 连续区间（执行期） | 付费主动观测 | 在线释放下界 | 固定窗口真实服务率 |
| A1 PIE-D | 概率执行延迟，非空间偏差 | [需核验] | [需核验] | [需核验] | [需核验] |
| A2 PIE | [需核验] | [需核验] | [需核验] | [需核验] | [需核验] |
| A3 LaCAM2 | — | — | — | — | 解代价 |
| A4 ADG | [需核验] | [需核验] | [需核验] | [需核验] | [需核验] |
| B1 Zhong | [需核验] | [需核验] | **主动观测**［需核节号］ | [需核验] | [需核验] |
| B2 S2M2 | 有界扰动→误差界→包络［需核节号］ | [需核验] | [需核验] | [需核验] | [需核验] |
| B3–B11 | [需核验] | [需核验] | [需核验] | [需核验] | [需核验] |
| C1 CCBS | [需核验] | 连续时间区间［需核节号］ | [需核验] | [需核验] | [需核验] |
| C2 PSIPP | **固定圆盘与线段，非误差包络**（71L3） | **连续时间区间**（71L3） | **无，规划期**（71L3） | — | [需核验] |
| **D1 Berndt** | **无误差集；有静态足迹 S_AGV，仅图构造期使用**（73L24 §3） | **依赖图顶点／整动作**（73L24 §3） | [需核验] | **重排次序**（73L24 §3） | **累计路径完成时间**（73L24 §3） |
| E1–E6 | [需核验]（预期为可达性／区间观测器类误差界） | — | — | [需核验] | [需核验] |
| F1 VoI | — | — | [需核验] | — | [需核验] |
| F2 Atzmon | [需核验] | [需核验] | [需核验] | [需核验] | [需核验] |

**已取得定点证据的单元共 9 个**（C2 三格、D1 四格、A1 与 B1、B2 各一格且两格待核节号），占矩阵约 7%。这是本件如实报告的现状，不因矩阵形式完整而暗示内容已完整。

## 4. 定点核验优先级

按“该单元是否决定本文的定位表述”排序。**只有第一优先级的四项完成后，§1.1 的对照论述才有完整依据。**

**第一优先级（决定本文是否占据空白单元）**

1. **C1 CCBS 的 D2 与 D4**：其连续时间区间是否只在规划期给出、执行期是否存在占用下界的在线收缩。若存在，本文新颖性表述须再次收窄。
2. **A1 PIE-D 的 D3 与 D4**：本文的直接改进锚点，其执行期是否已有任何形式的信息获取与占用收缩。此项若不清，“直接改进”这一定位就无依据。
3. **B1 Zhong 的 D3 与 D4**：既有阅读包中最接近付费观测的一篇，须确认其主动观测是否计费、是否用于释放空间而非仅用于状态恢复。
4. **D1 Berndt 的 D3**：其滚动重排所依据的信息从何而来、是否计费。这决定“付费”是否为本文独有约束。

**第二优先级（决定 §1.1 谱系论述的准确性）**

5. **A4 ADG 全部维度**：外部对照的基准，且 D1 Berndt 自述与其算法几乎相同。
6. **E1–E6 的 D1**：误差界的构造方式与本文式(2) 逐分量有界盒的关系，用于把 §2.1 从自定义假设改写为有文献谱系的建模选择。
7. **B2 S2M2 的 D1 节号**：MAPF 语境内最直接的误差包络工作。

**第三优先级（补齐覆盖，不阻塞定位）**

8. B3–B11、C2 的 D5、F1、F2 各维度。

## 5. 本件不主张的内容

不主张：矩阵内容已完整；本文确已占据空白单元；任何 `[需核验]` 单元的预期取值成立；26 篇已构成充分的近邻排除；任何一篇的期刊正式版全文已核。矩阵的维度取自已收窄的新颖性表述，若该表述因第一优先级核验结果再次改变，维度须相应重设，本件届时另立后继。

强度标注只描述本仓库已取得的证据，不评价论文本身质量；`题录级` 不构成对该工作内容的任何断言。既有阅读包位于仓库之外、不受版本控制，其 `99` 文档记录的字节核验以该文档为准，本件不复制其哈希。
