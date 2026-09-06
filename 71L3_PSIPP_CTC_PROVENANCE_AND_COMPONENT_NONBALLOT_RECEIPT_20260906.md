# 71L3：PSIPP/CTC 来源层级及组件借鉴回执

2026-09-06；NONBALLOT。真实 /root/scale_journal_mechanisms 的第二个有界任务已实际完整返回，root 完整阅读最终消息。任务无 skill、不读本地文件、不写文件/运行，不替代旧 69L1，不给新候选投票。

题录：Kazumi Kasaura、Mai Nishimura、Ryo Yonetani；Prioritized Safe Interval Path Planning for Multi-Agent Pathfinding With Continuous Time on 2D Roadmaps；RA-L 7(4), 10494–10501，2022-10；DOI 10.1109/LRA.2022.3187265。代理亲见[作者官方项目](https://omron-sinicx.github.io/PSIPP-CTC/)、[Crossref 出版社登记](https://api.crossref.org/works/10.1109/LRA.2022.3187265)和[OMRON 机构介绍](https://www.omron.com/sinicx/activity/news/post-209/)相互支持题录，IROS2022 是展示并非把论文改称会议发表。

## 1. 实际阅读强度与来源限制

代理完整读作者项目、项目直链的 34 页[作者幻灯片文字](https://speakerdeck.com/player/e80c16e05e57466f90789a3d8d34f075)、机构介绍和 Crossref。IEEE 正式入口验证页、PDF 请求 HTTP 418、ResearchGate PDF 入口均未取得 PDF 字节；未登录、填表或绕过访问限制。

代理另完整读到 [ResearchGate 所展示的原刊全文文字转录](https://www.researchgate.net/publication/361655366_Prioritized_Safe_Interval_Path_Planning_for_Multi-Agent_Pathfinding_With_Continuous_Time_on_2D_Roadmaps)，覆盖原页 10494–10501、I–VII、公式 (1)–(6)、算法 1–3、VI-A–VI-H 和参考文献。文中原刊页眉/DOI/CC BY 4.0 与 Crossref vor 许可一致，是公开原文转录而非平台解读；**上传者身份未核、原生 PDF 未获、转录存在符号损失**。未逐图检查图 1–7、未看补充视频、未读参考文献全文。不能将此写成出版社 PDF 逐符号核对完成。

root 本轮随后独立完整打开作者项目 L0–66，点击项目直链并完整读作者幻灯片 34 页文字 L0–185；还核两位作者主页的该文入口仍链接 IEEE，没有取得新 PDF。root 没有重读 ResearchGate 全文，不把代理转录阅读算作自己期刊 PDF 全文亲见，也不将其纳入此前“四份一手期刊全文”最低计数。以下精确数学/复杂度信息若只由转录支持，保留其核对强度限制；后继自己的定理应自给推导。

## 2. 由一手项目/幻灯片确认的组件

作者用几何邻近搜索与扫描预标注顶点—边、边—边的潜在冲突及连续时间条件，减少重复在线几何检测；固定圆盘与线段是所述构造前提。整体仍是逐优先级规划路径的非完备方法，狭窄环境会有低效计划。作者展示差速轮物理仿真并加入转动、加减速用时，但这些展示不自动给任意定位偏差或错误反馈提供鲁棒性证明。[作者项目](https://omron-sinicx.github.io/PSIPP-CTC/)、[作者幻灯片](https://speakerdeck.com/player/e80c16e05e57466f90789a3d8d34f075)

代理从原文转录提取的有限补充：CTC 利用固定动作对的相对出发时间判碰撞；近邻/交叉候选数在密集图可二次增长，在线区间更新依实际冲突输出与搜索节点规模，不能称整算法常数开销。原版单起终点且目标后等待，不是 lifelong 持续任务协议。实验规模/耗时有地图条件，部分质量比较限双方成功实例。这里只保留这些带出处边界的结论，不转录性能数值或将其作本研究参数。原 PDF 未逐符号核对，本文不据转录符号直接认证复杂度定理。[原文转录](https://www.researchgate.net/publication/361655366_Prioritized_Safe_Interval_Path_Planning_for_Multi-Agent_Pathfinding_With_Continuous_Time_on_2D_Roadmaps)

## 3. 根采用范围与不采用的外推

接受为构造方向：保留 PIE 新 MOVE 时，独立研究固定几何关系预计算以减少在线重复判断。须自己证明在空间偏差包络下缓存仍保守、何时失效、如何重建。整套 SIPP 替换引入新路径、优先级与终点语义，属于另一规划器，不能称执行 wrapper。论文的连续时间并非我们 q 后缀退休的安全证明，不能直接拿相对时差区间容忍未知进度/空间偏差。

可证伪条件：如果成本主要在通信、证据排队或事务，预计算可能无主吞吐收益；密集几何关系和频繁模型变化可能使预处理/存储/重建负担反超。公平比较应共享实体几何判定能力，计首次总成本、复用成本、在线更新、内存及失效重建，保留同 MOVE 来源和全部失败，不能只报告缓存查询时间或双方都成功的主任务分数。此为根/代理条件性推论，非作者未读的 lifelong 算法。

官方代码入口 [omron-sinicx/PSIPP-CTC](https://github.com/omron-sinicx/PSIPP-CTC) 已确认；未克隆、构建、运行或源码审计。全部保护参数不赋值；不是效果结果，不改冻结候选。保持 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。
