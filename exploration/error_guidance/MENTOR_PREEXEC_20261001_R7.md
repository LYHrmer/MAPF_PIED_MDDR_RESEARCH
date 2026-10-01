# R7 独立导师预审（2026-10-01）

依据 research-mentor 与真实 R6 工件独立判断；未读取本轮 ASTRA/root 结论。目标为 SCI 二区/三区工程研究，不把分区当作降低证据标准。以下均为已授权隔离探索，不代表选题通过或可投稿。

## 推进判断（主体）

先核误差→动作。main的9.61%仅为固定输入全查询费用收益；query在IID/SHIFT无收益、训练均单候选、8/8留出死锁；third的648对780是旧flow模型负结果，全队屏障限制局部误差价值。

**main：**做两source竞争微例，固定物理输入、互换已交付历史/费用，核验排序。选前快照禁止私有进度/未来END/事后费用。两制度分列业务/选择/查询/receipt费用；走POSITION→MOVE→四terminal→receipt→下一选择。估计与最终账单分开，B不能代替费用。验收信息非干涉、守恒、真实选异。

**query：**接作者在线current-head/FIFO并保留承诺依赖；先8agent、两新整run、800秒WAIT/RR检验服务、未来任务隐藏和终点离开。不复制屏障/静态裁剪。通过后固定每run前8个公开机会，对全部候选做WAIT/单query同前缀续跑；全部保留、按整run隔离，记录竞争覆盖；RR/条件规则仅作消融。

**third：**24旧run按agent-tick拆移动/转弯、服务、依赖等待、队列空闲/屏障并守恒。4agent两独立路径加依赖对，延迟一MOVE20ticks；无依赖动作可推进，依赖动作须等原ACK，含零扰动对照。再用已交付ACK学耗时残差/不确定性，影响未来guidance；冻结新train/cal/test，逐级核预测→动作→正常服务，保留负结果。

**MAPF评测：**比较正式作者PIE-D、hm+GPIBT、OnlineGGO，统一地图/FIFO/执行/扰动/费用。机制通过后扩至公开empty/random/warehouse、8/16/32和至少10配对任务种子；保留失败删失，先安全/服务，再吞吐、等待、预测误差、全费用与规划wall-time，按整run报告配对区间。尚无学习优势。

## 资格卡

问题合同：机器人持续接新任务时，执行延迟使既定计划与实际进度不同。本文拟用合法已交付执行证据改善查询选择或未来引导成本。指标是正常服务、延迟传播及全部决策费用，不能用预测分数替代。

|资格项|main|query|third|可定位证据及关闭动作|
|---|---|---|---|---|
|1 通俗问题|PASS|PASS|PASS|上方合同；三线分别是费用底座、证据选择、执行误差引导|
|2 已发表锚点/归属|PASS|PASS|PASS|PIE-D AAAI2025已处理执行延迟；OnlineGGO AAAI2025已做在线交通引导。拟检验额外执行证据的决策价值，不声称首次|
|3 官方工件R0|UNKNOWN|PASS（来源）/UNKNOWN（新接口）|PASS（算法来源）/UNKNOWN（异步扩展）|main为自建认证层，非作者MAPF工件；query作者PIE-D@74cfba3、MIT与真实runner源轨迹可追溯；third OnlineGGO@ff6d830、MIT、持久MAPFPlanner实调已完成。S1为共同适配，非原版数值复现；新扩展须重新绑定构建与最小机制|
|4 外部基线|UNKNOWN|UNKNOWN|PASS（共同执行对照）|main/query尚无同问题公平外部对照；third OBJ3/OBJ4真实作者对象可比，但200候选旧训练不能代表完整官方最强模型|
|5 数据/场景|UNKNOWN（MAPF样本）|UNKNOWN（在线竞争）|PASS（诊断）/UNKNOWN（新训练）|main单固定输入；query48静态任务/已见背景/单候选标签；third公开MovingAI、独立FIFO，24run一个任务种子。新run分割及预测字段须冻结|
|6 纯仿真闭环|UNKNOWN|UNKNOWN|UNKNOWN|已具构建/日志/审计底座；仍需上方规模、任务种子、动作响应、费用及失败闭环|

判定：三线正式选题均CONDITIONAL；隔离探索继续执行，无新增审批。UNKNOWN限定可作何种论文结论，不撤销用户授权。优先解决信息→动作的因果缺口；候选失败时保留原始证据并明确收缩结论。

## 核验来源

- [research-mentor skill](/home/lyh/.codex/skills/research-mentor/SKILL.md)，仅加读references/11与29；采用真实证据、最小机制和配对统计规则，未采用中文核心目标。
- [main R6e HANDOFF](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/receipt_word_successor_20261001_r6e/HANDOFF.md)及uniform_8m_verification.json：98段、两制度真实完成；独立读取账单与回执。
- [query R6 REPORT](/home/lyh/MAPF_PIED_MDDR_LEARNING_EXPLORE/exploration/learned_query/public_joint_20261001_r6/REPORT.md)、CONTRACT.md、STATISTICAL_CONTRACT.md、SUPPORT.json与作者LICENSE。
- [third R6c REPORT](published_continuous_execution_20261001_r6c/REPORT.md)、PROTOCOL.md、audit.json、model_identity.json、official_bridge.cpp、R0_reference.json；R0_reference明确本轮未新跑R0。
- [OnlineGGO正式论文](https://ojs.aaai.org/index.php/AAAI/article/view/33614)，AAAI2025，39(14):14726–14735；[官方代码](https://github.com/zanghz21/OnlineGGO)，官方flow引导与训练/评估入口，非执行误差预测器。
- [PIE-D正式论文](https://ojs.aaai.org/index.php/AAAI/article/view/34506)，AAAI2025，39(22):23387–23394。它已解决延迟下并发规划执行框架，不将此问题本身重新包装为创新。

本审查为路线诊断；以上新机制/训练/统计尚未执行。原数据、引用和期刊要求仍须投稿前人工核对。
