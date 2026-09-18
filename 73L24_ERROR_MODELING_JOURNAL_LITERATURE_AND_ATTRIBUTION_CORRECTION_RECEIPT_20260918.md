# 73L24：误差影响／建模／解决方案期刊文献题录、归属更正与影响侧缺口回执

2026-09-18；NONBALLOT。本件补记 2026-09-17 至 09-18 一轮期刊文献工作的题录、核验强度、两处更正与一处缺口。本轮**核验强度低于既有文献回执体例**：除一篇外只做 Crossref 单 DOI 题录核验，未取得任何期刊正式版 PDF 字节，未做全文精读。本件不给新候选投票，不改变任何门的资格状态，不替代 71L2、71L3、72L1–72L3 及 73L1–73L23。

台账说明：本轮工作原先未产出回执，成果散落于仓库外的桌面文档与对话。仓库现有 165 份 `70C*/71L*/72C*/73L*` 回执，而 09-17 与 09-18 两日原为零。本件即为补齐该断档；断档本身记录在此，不追溯改写既有回执。

## 1. 核验强度与其限制

**已做**：下列每条 DOI 经 `https://api.crossref.org/works/{DOI}` 单条查询命中，题名、作者、刊名、年、卷、期、页码取 Crossref 权威字段原样，未凭记忆补写任何字段。

**未做**：期刊正式版 PDF 未下载、未做字节与页数核验、未固定 SHA256、未做全文精读、未检查 SI、未完成近邻排除闭合。

因此第 2 节的“用途”一栏是**待核验的阅读目标**，不是已确认的论文结论。凡拟写入正文的内容主张，须先取得该论文的节号锚点，否则按 `[需核验]` 处理。Crossref 命中只证明题录存在，不证明论文表述了引用者所述内容——本轮已有一次实证，见第 4 节。

## 2. 题录（10 篇期刊论文，2026-09-18 核验）

| # | 题录 | 刊物／年／卷(期)／页 | DOI |
|---|---|---|---|
| 1 | Berndt A, van Duijkeren N, Palmieri L, Kleiner A, Keviczky T. Receding Horizon Re-Ordering of Multi-Agent Execution Schedules | IEEE Trans. Robotics, 2024, 40: 1356–1372 | 10.1109/TRO.2023.3344051 |
| 2 | Chen M, Herbert S L, Hu H, Pu Y, Fisac J F, Bansal S, Han S, Tomlin C J. FaSTrack: A Modular Framework for Real-Time Motion Planning and Guaranteed Safe Tracking | IEEE Trans. Autom. Control, 2021, 66(12): 5861–5876 | 10.1109/TAC.2021.3059838 |
| 3 | dos Reis de Souza A, Efimov D, Raïssi T, Ping X. Robust output feedback model predictive control for constrained linear systems via interval observers | Automatica, 2022, 135: 109951 | 10.1016/j.automatica.2021.109951 |
| 4 | Chen M, Bansal S, Fisac J F, Tomlin C J. Robust Sequential Trajectory Planning Under Disturbances and Adversarial Intruder | IEEE Trans. Control Syst. Technol., 2019, 27(4): 1566–1582 | 10.1109/TCST.2018.2828380 |
| 5 | Kousik S, Vaskov S, Bu F, Johnson-Roberson M, Vasudevan R. Bridging the gap between safety and real-time performance in receding-horizon trajectory design for mobile robots | Int. J. Robotics Research, 2020, 39(12): 1419–1469 | 10.1177/0278364920943266 |
| 6 | Gong Z, Li B, Herbert S. Safe Returning FaSTrack With Robust Control Lyapunov-Value Functions | IEEE Control Syst. Lett., 2024, 8: 1373–1378 | 10.1109/LCSYS.2024.3410636 |
| 7 | Soleymani T, Baras J S, Hirche S, Johansson K H. Value of Information in Feedback Control: Global Optimality | IEEE Trans. Autom. Control, 2023, 68(6): 3641–3647 | 10.1109/TAC.2022.3194125 |
| 8 | Atzmon D, Stern R, Felner A, Wagner G, Barták R, Zhou N-F. Robust Multi-Agent Path Finding and Executing | J. Artif. Intell. Research, 2020, 67: 549–579 | 10.1613/jair.1.11734 |
| 9 | Andreychuk A, Yakovlev K, Surynek P, Atzmon D, Stern R. Multi-agent pathfinding with continuous time | Artificial Intelligence, 2022, 305: 103662 | 10.1016/j.artint.2022.103662 |
| 10 | Kasaura K, Nishimura M, Yonetani R. Prioritized Safe Interval Path Planning for Multi-Agent Pathfinding With Continuous Time on 2D Roadmaps | IEEE Robotics and Automation Lett., 2022, 7(4): 10494–10501 | 10.1109/LRA.2022.3187265 |

进入 `MANUSCRIPT_PREEXPERIMENT.md` 参考文献的是 #9、#10、#1，对应正文 [5]、[6]、[7]。其余七条本轮**未进入参考文献**，因其在正文尚无定点锚点，避免只为篇数而列。

**#10 与既有回执重叠**：`71L3_PSIPP_CTC_PROVENANCE_AND_COMPONENT_NONBALLOT_RECEIPT_20260906.md` 已对同一篇做过远高于本轮的核验（作者官方项目、34 页作者幻灯片文字、公开全文转录、Crossref、机构介绍相互支持，并记录了上传者未核与符号损失等限制）。本轮对该篇的工作为重复劳动，此处不另立结论，以 71L3 为准。本轮唯一新增的是把它与 #9 一并用于新颖性近邻排除。

**年份口径**：#3 的 DOI 后缀含 2021（Elsevier 在线先发），Crossref `issued` 与卷号对应 2022 卷 135；#1 的 DOI 后缀含 2023（IEEE Early Access），`issued` 与卷号对应 2024 卷 40。两处均以正式卷期年引用。

## 3. #1 的全文核验（本轮唯一达到锚点级的一篇）

核验对象为**作者预印本**，非 IEEE 正式版：arXiv:2312.04190v1，17 页 32 图，`%PDF-` 签名与 `pdfinfo` 页数已核，SHA256 `1046945c8f7f0d9838aa1faeede914f71459cd8cf7be9c7d66cbaea6b68c879a`；身份由 Semantic Scholar `externalIds` 与 arXiv 官方检索两个独立来源交叉确认。下列节号来自预印本，正式版节号与页码尚未逐项对应。

§III **Assumption 1** 原文：

> A single AGV can navigate the workspace (represented by roadmap G) occupied by static and dynamic obstacles in a collision-free manner using on-board navigation methods.

论文称该假设 "relatively nonconstraining"，将单车避障整体外置给车载导航。碰撞安全（Corollary 1／Proof 1）来自“有效 MAPF 计划＋执行策略顺序约束”的名义执行论证。§VII 的扰动为 `Each Δt_delay seconds, a randomly selected subset of 20% of the AGVs are stopped for Δt_delay seconds`，是纯停车时序量。全文词频：`delay` 88、`disturbance` 4；`tracking error`／`lateral`／`uncertainty`／`envelope`／`localization`／`radius` 各 0。

**须记的一处自我更正**：曾据关键词 `footprint` 零命中判断该文无车体几何，属假阴性。§III-A 符号表定义 `loc(p_i): P_i → R²`、`S_AGV ⊂ R²`（"represents the area occupied by an AGV"）与闵可夫斯基和 `⊕`，并在 Algorithm 1 第 7 行以 `loc(p) ⊕ S_AGV ∩ loc(p_i^k) ⊕ S_AGV = ∅` 判定空间互斥。准确表述为：**有静态足迹、无误差不变集**，且足迹只在依赖图构造期使用一次，不是执行期可收缩的保留区间。关键词零命中不得作为“论文没有该概念”的依据。

**谱系由论文自述与引用双重确认**：§III 明文 `Algorithm 1 is practically identical to the ADG algorithm in [4]`；逐条解析其 41 条参考文献，`ref4` = `10.1109/lra.2019.2894217`（Hönig 等 2019，即本稿参考文献 [4]、H19 外部对照），`ref5` = `10.1613/jair.1.11734`（本表 #8）。该 41 条中不含 FaSTrack、RTD、S2M2、区间观测器等任何以可达性或跟踪误差界构造空间包络的工作。

**可据此说的**：该执行谱系（含本项目外部对照及其 2024 年后继）把扰动一律建模为时序延迟，其相关工作视野内不含有界空间跟踪误差的包络表达。**不可据此说的**：不得断言其方法内部没有处理空间误差——参考文献缺席是强指示，不是证明。

## 4. 两处更正

**（一）归属更正。** 曾把“在线多 TEB（tracking error bound）切换”归给本表 #2（FaSTrack，IEEE TAC 2021）。经核 TAC 2021 只演示三组 tracking-planning 模型对；在线自适应切换的出处是：

> Fridovich-Keil D, Herbert S L, Fisac J F, Deglurkar S, Tomlin C J. Planning, Fast and Slow: A Framework for Adaptive Real-Time Safe Trajectory Planning. 2018 IEEE ICRA: 387–394. DOI 10.1109/ICRA.2018.8460863（会议论文，不计入第 2 节 10 篇）

此条记录于此的目的是防止再犯：**Crossref 命中只证明题录存在，不证明论文说了引用者所述内容。** 该更正此前只存在于仓库之外的文档，无版本控制落点。

**（二）检索工具编造标识符。** 检索本表 #1 的预印本时，网络检索工具返回 `arXiv:2204.13154` 并伴以看似完整的摘要。实际该编号对应 Soydaner D，*Attention Mechanism in Neural Networks: Where it Comes and Where it Goes*，Neural Computing and Applications 34: 13371–13385，2022，DOI 10.1007/s00521-022-07366-3，与本表 #1 无关。正确编号 2312.04190 由 Semantic Scholar `externalIds` 与 arXiv 官方检索两个独立来源确认。**检索工具给出的标识符须独立复核后方可使用。**

## 5. 影响侧缺口

原任务为“误差的**影响**、建模、解决方案”三项。第 2 节的覆盖情况：

- **建模**：#2 #3 #4 #5 #6，覆盖充分
- **解决方案**：同上加 #1 #8，覆盖充分
- **影响**：**基本空缺**。10 篇中无一篇定量回答误差如何影响吞吐、等待或固定窗口任务完成量。#8 最接近，但其衡量对象是解的代价，不是执行期真实服务率

该缺口直接关系 §4.3 与 §4.5 的主评价量。补齐时须注意一项结构事实：MAPF 领域“误差／延迟 → 吞吐”的关键工作多为 AAAI／IJCAI／ICAPS 会议论文，期刊论文较少；若限定只收期刊，该维很可能补不满。既有阅读包中 `12_Traffic_Flow_Optimisation_AAAI_2024`（拥堵→吞吐）与 `05_Shahar_2021`（时间不确定性）已部分覆盖该侧，可先回读。本件不预注册任何补齐方案。

## 6. 一处已放弃的做法

本轮曾考虑“预注册公开来源 agent 数阶梯中最密的合法一档”作为主工况，以抬高相对效应、降低所需块数。该做法**已放弃**：固定 73 四处（行 190、503、729、757）把 density N 与保护参数、调参量并列，行 729 另要求其合法绑定须经来源核验、禁止按文件名取值；在受保护参数上朝有利于结果的方向取值，与 §4.4 的参数选择规定冲突。放弃理由与该记录已同时写入 `MANUSCRIPT_PREEXPERIMENT.md` 的修订说明。

## 7. 本件不主张的内容

本件只完成题录核验、一篇预印本的锚点级阅读、两处更正与一处缺口登记。不主张：任何一篇的期刊正式版全文已核；近邻排除已闭合；#1 应或不应进入外部对照集合（其结果层可替代性未检验，已作为局限写入正文）；本轮文献工作改变了任何门的资格状态；影响侧缺口已有补齐方案。仓库外的桌面导航文档不属版本控制范围，以本件为仓库内准。
