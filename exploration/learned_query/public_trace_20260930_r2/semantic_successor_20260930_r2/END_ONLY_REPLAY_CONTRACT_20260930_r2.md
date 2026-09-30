# END-only 信息合同修正：因果重放前登记

六完整native运行已完成，原回执保持不变。审计已发现：原actor helper `source_label` 直接读取离线progress，虽然只在已交付END后的下一phase维护历史且全部标签可由END唯一恢复，不能把这种代码路径冒称已实现END-only。该缺口如实保留。

本后继只纠正信息通道：对原合同已声明、full-cap rest-to-rest、固定系数、eta∈{-1,0,+1}支持域，另以原controller运行三种公开参数的qualification。它们的完整原END持续时间分别在sqrt3、约1.292894、约1.083442；门槛5/4仅识别唯一fast类，严格区间必须处于门槛一侧。三参数的3/4处物理progress和实际Geometry资源归属作为**独立qualification标签**，不进入actor。它不是一般eta变化、cap变更、暂停、转弯或未知profile的END逆推保证。

新actor只接收到达的`original_END/received`严格区间、full_cap_uninterrupted、length、agent/tick/run/公开heading；输入白名单拒绝progress、private eta、regime。训练和lag2的release标签真正由这个END-only decoder产生。当前phase-END仍在冻结选择后交付；模型仍只由两train run拟合；cal/test、seed、机会、任务/预算完全保持。

新产物是**离线因果决策重放**。复用原native已经实际执行的全部WAIT/QUERY局部potential outcomes，逐项比较新END-only模型、历史、分数、选择和端点结果是否与原回执相同；不称又跑了一次物理native，也不修改原回执的数据来源说明。若相同，则本表相同选择的物理结果已有真实native覆盖；若不同，保留差异，不调decoder找一致。接口负控应拒绝私有progress和current/future END进入旧历史，精度误减、等阈及task因果审计仍保持。
