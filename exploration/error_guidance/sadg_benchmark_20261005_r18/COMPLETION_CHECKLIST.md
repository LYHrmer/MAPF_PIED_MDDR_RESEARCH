# R18 完成核对

本表对应冻结 PROTOCOL.md 的交付要求；冻结协议本身及五份科学源码均未改动。目标是完成标准地图、多规模、扰动条件下的固定更新、历史规则、学习查询比较，不以学习胜出作为完成条件。

|要求|实绩|证据|
|---|---|---|
|公开标准输入和作者初始规划|3地图、5场景、N=8/16/32，45/45有效；所有失败分母保留，无补选|data/CASES.json、DATA_FREEZE.json、原始路径归档|
|共同作者底座与在线执行|原 SADG 优化器未改，公共适配共享；捕获/延迟/过期、预算、START/END、全程连续轨迹完成|engine.py、ENGINE_VALIDATION.json、PUBLIC_SCHEMA.json、逐episode日志|
|真实学习及先于测试冻结|54训练世界、108完整配对、236唯一执行；α=100模型与19次拟合核验|training/、MODEL_FROZEN.json、MODEL_FREEZE_RECEIPT.json、review/LEARNING_AUDIT.json|
|完整校准和独立测试矩阵|135 CAL+270 TEST=405结果，missing=0；各臂全部任务完成|SUMMARY.json/CSV、TOTALS.csv、ANALYSIS.json|
|避免重复科学执行|34条等价训练完整结果复用；并行冲突拒绝重复启动；恢复评价复用405完成收据|COLLECTION_COMPLETE、ORCHESTRATION.md、EVALUATION_RESUME.log|
|独立执行和信息合法性核验|641/641原始执行PASS，TRAIN/CAL/TEST全覆盖|review/COMPLETED_ARTIFACTS_AUDIT.json及逐episode明细|
|完整统计/分母/故障/配对核验|405行、180分层、族bootstrap与图数据通过；0新仿真|review/SUMMARY_AUDIT.json：passed=true，10158项检查|
|独立失败归因和模型局限|评价阶段11次父图回退明确保留；TRAIN零预测诊断、稀疏标签和续策偏移明示|REPORT.md、review/、MECHANISM_REVIEW.md|
|结果图与后续科研设计|2组SVG/PDF/600dpi PNG完成并目检；三线后续合同已写|figures/、REPORT.md、NEXT_METHOD_DESIGN.md|
|研究原稿保护|主线MANUSCRIPT_PREEXPERIMENT.md SHA256未变：204316c27e17ecb37a8646d53cb5941a9b11b6c8eff3378ce55e80878b271452|root最终只读哈希核验|

所有 PASS 都带有相应范围：连续安全是本轮点机器人执行，统计比较是六个独立地图/场景测试族，计数不是生产费用。失败求解若没有保存完整原始模型，不将其原始违规摘要冒充独立逐行重算；父图保留与后续执行另有完整核验。

归档发布由 `package_results/PACKAGE_COMPLETE.json` 与逐成员 SHA256 清单另行证明；打包不删除原始证据、不新增科学实验。该文件只在所有分卷实际验证后由打包脚本写出。Git 推送状态以分支 HEAD 与远端相同为准，不由本表提前代替。
