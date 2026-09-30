# 官方 OnlineGGO 训练前运行量测

2026-09-30，本目录任何训练之前。固定官方 OnlineGGO 提交
`ff6d830e2fd5bf85ccbb72eaec0fb8df1cf1c256` 的 `sortation_small.gin`：
原 sortation_small_kiva 地图、800 agents、1000 ticks、quad 560 参数、原生 OBJECTIVE=4、
默认生成任务和原 config.py。权重全5，seed719只用于运行量测，不进入训练/留出。
加载未经修改的 config.py 和原 gen_sim_kwargs 方法 AST；保留完整 kwargs、源码和二进制身份。
每次 native 新进程，120秒时限。该运行不证明训练收益。

量测只决定本机并发和有限训练预算，不能按吞吐结果选图、选任务、改模型或过滤样本。
随后在首次 ask/evaluate 训练之前另行冻结训练协议。训练后保留权重、全候选目标、
随机种子、选择规则、配置差异和完全独立的留出评估。有限预算结果不能冒充作者论文完整R0。
