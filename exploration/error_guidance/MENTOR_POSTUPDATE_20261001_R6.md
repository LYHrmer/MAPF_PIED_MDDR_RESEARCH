科研导师独立后评审 · 2026-10-01 R6

独立复核：未参与R6实现，未读本轮SOL/root结论。资格卡：问题、发表锚点、外基线PASS；官方工件扩展、跨图规模数据与新方法因果闭环UNKNOWN，总体CONDITIONAL。

主线R6e在统一8m合同完成98段，Natural总费用净降9.61%，查询业务不变；可作为精确收费优化成果，MAPF论文需另补任务收益。[E1] query真训真用70臂却无IID/SHIFT增益，先恢复全局依赖和持续任务，再收集多候选反事实标签；当前负结果不支持加大模型。[E2]

第三线R6c在同步S1下24臂均跑满800秒并通过审计；迁移模型在12个匹配条件全落后，合计648对780任务。现模型只做流量引导。先拆分路程、转弯和同步等待损失；采样净空通过不构成连续安全证明。[E3]

面向SCI二区/三区，建议主攻“执行历史何时值得用于修正LMAPF决策”。候选机制：仅用当前公开状态与已交付END学习剩余耗时残差及不确定性，据此修正指导边权，不让模型绕过ADG验收；先用无历史、解析估计与学习模型同信息同预算比较。查询线另检验花费一次查询能否改变有效决策。一般执行预测及学习重规划已有近邻，贡献应落在因果反馈下可复现的净收益与失效条件。[L2]、[L3]

正式对照用作者hm+GPIBT、off+GPIBT、on+GPIBT，固定版本并声明权重来源；PIE-D只在兼容延迟合同下比较，自制规则是消融。[L1]、[L4] 下一轮加入仓储/分拣图与密度梯度，8/16/32/64规模、10个成对独立任务流，按图与整条任务流隔离训练测试；报告真实服务吞吐、失败/死锁、规划及推理时间、95%成对区间，并以执行策略消融排除同步屏障效应。先交付机制预检和预注册矩阵；若没有可利用的反馈收益，保留负结论并调整决策接口。

引用与核验材料（不计入正文）

[E1]: /home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/receipt_word_successor_20261001_r6e/RESULT.json
[E2]: /home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/public_joint_20261001_r6/REPORT.md
[E3]: /home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/published_continuous_execution_20261001_r6c/summary.json
[L1]: https://ojs.aaai.org/index.php/AAAI/article/download/33614/35769
[L2]: https://arxiv.org/abs/2511.21886v2
[L3]: https://arxiv.org/abs/2604.25567v1
[L4]: https://ojs.aaai.org/index.php/AAAI/article/view/34506

- E1：[R6e 实际结果][E1]；对照读取 [HANDOFF.md](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/receipt_word_successor_20261001_r6e/HANDOFF.md)、[STAGE_COSTS.csv](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/receipt_word_successor_20261001_r6e/STAGE_COSTS.csv)、[同 R6d 合同核验](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/receipt_word_successor_20261001_r6e/final_run_verification.json)及[统一 8m 合同核验](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/receipt_word_successor_20261001_r6e/uniform_8m_verification.json)。本人复算 10 条 Natural 变化行净额 15,266,608，未重新运行 guest。
- E2：[Query R6 报告][E2]。本人只读复核 240 冻结文件、10 归档与 189 成员的大小、SHA 和覆盖关系；52 个发布成员完整恢复冻结内容，未重做 70 臂科学审计。固定清单 SHA256：`baa7c85d04cd8d13e536509c5386356b923a6df79ed1a8b1374354b11a38a006`。
- E3：[R6c 汇总][E3]及[逐臂表](/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/published_continuous_execution_20261001_r6c/summary.csv)、[审计](/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/published_continuous_execution_20261001_r6c/audit.json)、[协议](/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/error_guidance/published_continuous_execution_20261001_r6c/PROTOCOL.md)。本人从 CSV 复算 hm+GPIBT=780、trained=648、12/12 条件 trained 较低；使用审计凭据，未重跑物理仿真。汇总 SHA256：`066057adc5ded557101219c9c98bd61902a69e13ca1cb8e29caf53e4e2c6764e`。R6/R6b 的 MOVE 合并和坐标配置缺陷另保留，不并入正确 R6c 的算法胜负。
- L1：[Zang et al., Online Guidance Graph Optimization for Lifelong Multi-Agent Path Finding, AAAI 2025][L1]，第 4.1 节明列 hm+GPIBT、off+GPIBT、on+GPIBT；[作者实现](https://github.com/zanghz21/OnlineGGO)。建议固定 swap/LNS、训练预算、地图及权重来源，先通过作者原版最小复现再接共同执行器。
- L2：[Yan et al., From Discrete Plans to Real-World Execution: A World-Model-Driven Framework for Execution-Aware Multi-Agent Path Finding][L2]，arXiv:2511.21886v2，2026-06-21 更新；包含 ExecTimeNet、REMAP 与 ESADG。作为需逐项比较的近邻预印本，不据此声称候选方法首次提出。
- L3：[Zahrádka et al., Should I Replan? Learning to Spot the Right Time in Robust MAPF Execution][L3]，arXiv:2604.25567v1；查询时页面仍标为提交 IEEE 双盲评审，列近邻预印本，不冒充已发表外部基线。
- L4：[Zhang et al., Concurrent Planning and Execution in Lifelong Multi-Agent Path Finding with Delay Probabilities, AAAI 2025][L4]。PIE-D 比较须保持其执行延迟和重规划合同，不能直接将不同执行语义的数字混作同场胜负。

本次采用 [research-mentor skill](/home/lyh/.codex/skills/research-mentor/SKILL.md)，仅加读行动原则、调查诊断与高质量打磨参考。文献核验日期：2026-10-01。正文共 754 字符（含 ASCII、标点及换行，不含本引用区）。分区作为目标，不构成期刊录用判断。
