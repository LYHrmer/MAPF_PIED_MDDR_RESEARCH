# CAL 前登记：用语义证明节省三个重复 B16 STOP

登记发生于 TRAIN 完成、模型已冻结、任何 CAL 新执行开始之前。模型、CAL family、两预算和评价规则不变；仅改变三个 B16 STOP 的后果获取方式。全部原始 CAL 世界已在 REGISTRATION 登记。新的原生执行是三族 B8 STOP，共3次；总新 native = 29（24 TRAIN STOP + 2 C兼容 + 3 CAL STOP），不是32。

证明依据：C 的查询排序只含已送达 END 得出的生存释放概率及当前公开 claims；capacity 只作为 `capacity>0` 许可条件和记录/特征使用，没有进入 condition 分数，也不改变模拟时间。原 World3 的 queried 集、QUERY 执行和物理推进完全未改。C8 在前8次购买后只能选择空动作；STOP16 在相同公共候选门（已买8次）切换为零分 WAIT，以后同样选择空动作。空选择会立即返回 queries；其余普通 END、资源守卫、planner、FIFO和原物理时钟照常执行。预算特征、macro标签、actor分数和native检查计数只是输出，不能反馈到 condition 排序或物理。

使用范围限 N16、B8/B16、当前冻结原生源及bridge/config、无可学习参数、相同完整输入（含所有ordinal扰动）。至少8次查询且实际gate可到达；不推广到任意策略/预算。12个 TRAIN 族已经逐事件验证 C8 与原生 STOP16 的物理/公共投影完全一致，所有任务/时间/查询/等待后果一致。

CAL 必须逐族关闭下列检查后才允许别名：C8输入文本与C16完全相同；原始C8实际购买8次；C16真实gate恰好spent8/remaining8；C8和C16到该门之前的全部物理/公共事件投影相同；对应候选列表的非预算特征、公开概率/claims/身份、历史计数和触发事件相同；门前8次 POSITION 的完整记录（时刻、occurrence、certificate lower及removed）相同；C8之后没有QUERY或SKIP；C8原独立审计通过。记录完整状态前缀hash及前8证书hash。

别名不是同cache键。B16 STOP后果行保留 `source_world=B8`、`source_policy=macro_C`、原始raw/receipt/审计hash，同时绑定 `target_world=B16`、真实gate源C16及其receipt/hash、冻结源证明和别名检查hash。不会制造一份声称来自native STOP16的日志。原native门元数据仍标明来源C16；策略选择STOP是语义映射。任何项失败则记录失败原因并回到原六臂合同；不依据收益选复用病例。

完整prefix的等价口径也明确区分：新原生B8 STOP是忽略policy后的全日志prefix相等；B16别名是上面有源码证明的预算元数据投影等价，不宣称两种预算下actor日志逐字节相同。最后报告必须分别数出原生臂、C复用及STOP语义别名。
