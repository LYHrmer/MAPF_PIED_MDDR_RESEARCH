# R5b：事件触发实现通过，多次查询闭合；候选竞争仍缺失

事前固定R5全部8个train/cal任务组、新完整run seed8101、WAIT/真实RR/强条件规则三臂共24原生运行全部退出0；不使用R5两个test组，没有本轮训练、没有留出性能比较，也没有把旧18槽ridge包装成19槽模型。本轮只完成新协议可运行实现及独立机械验证。

| 内部机械方法 | world | 实际任务 | 实际query | 公开候选机会 | 最大同刻候选 | 局部受限completion sum |
|---|---:|---:|---:|---:|---:|---:|
| WAIT |8|56/64|0|61|1|2546.811858932113417248247645|
| 真实RR |8|56/64|19|46|1|2543.180873523470237276858978|
| 条件解析规则 |8|56/64|19|46|1|2543.180873523470237276858978|

RR/条件臂各19次真实证书查询，cohort02与08每臂4次，cohort03/05每臂3次，cohort07每臂2次；不是每world一次查询。cohort02 WAIT35个几何/历史合格source机会，查询臂31，其中预算耗尽后仍列公开候选、actor必须WAIT；数量机会不能全部当可付费动作。所有24run最大同时候选仍1，故‘多决策’已出现，‘多个source竞争/问谁价值’仍没有证据。各方法任务完成数均56/64，所有未完成、死锁及服务时间逐world保留，不挑收益阳性组。此表是train/cal机械效果，不是泛化或模型优势。

## 新接口与强参考

R5既定launch恰好3/4协议原样保留。R5b新合同在公共年龄门槛、已收到正常END/需求更新、公开WAIT结束/需求更新事件后调度actor；候选允许sourceage>=3/4，本agent已经交付自身END、全world>=2条END。实际motor segment/physicalEND/privateprogress本身不触发actor。每公共事件最多1query，B4总量；所有实体持续共享真实Geometry/Index/PositionCommit和原Controller，第一goal/rest服务+正常END后第二FIFOhead才公开。公共age新增第19槽，age和接收recency用floor1e-6量化使日志/接口有理，未复用R5权重。

强解析规则只从已交付END支持区间识别eta类别，以最近3条END做9:1声明生成律的theta后验和10%flip下一eta概率。然后利用当前source尚未收到END这一已知事实，排除T_eta+1/4<=sourceage的候选profile，重新归一化生存概率，计算严格认证lower>13/20的释放概率，再乘当前head倒数/责任关系数。独立Decimal从闭profile重算概率与实际选择，含生存排除。此参考使用事前已知仿真生成律参数，是**model-based内部对照**；不是学习更少信息条件下的公平性能优势。后续比较需将同一law供给模型，或仅从train估计参数。

该解析器调用假设profile的运动状态，没有访问当前机器人真实eta/progress；真正query才取当前Controller的可达人工证书快照并提交Geometry释放。人工native证据没有建立生产AUTH或完整付费COST，也不是硬件机器人试验。

## 独立审计与边界

全部24原生physics、闭矩形footprint、lease/retirement、正常END时序、现head特征、END-only历史、public trigger、19槽public量化age、真实RR cursor、强条件生存概率及任务服务由独立70位Decimal重放。全部source/input/seed/native/冻结身份核验；private condition、私有motor触发、伪age、错生存概率、未来任务、截断六负控拒绝，具体总数见AUDIT.json。原R5432冻结文件和9生产头保持字节不变。

仍只有4机器人、两head、单map原任务背景；无同时候选竞争，没有新训练/heldout，没有完整global taskflow。不能当认可MAPF/LMAPF主benchmark。下一协议应直接接全局公开持续任务流，并在train/cal机械层确认多次预算受限决策和多个source竞争，再按整个run/map/cohort冻结新训练和新测试。不得从当前R5 test无支持结果挑新的阳性组，也不能把本机械改善写成学习独立价值。

原始input/jsonl/receipt/native/编译源码保留并压缩归档；成员hash与冻结manifest可复核。audit.py独立重放；run_mechanical.py拒绝覆盖原运行。没有按结果重试或改变24run协议。
