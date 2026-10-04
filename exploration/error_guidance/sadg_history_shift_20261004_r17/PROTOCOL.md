# R17：公共完成历史之后的失配，预登记机制试验

状态：探索性、不代表选题通过或可投稿。research-mentor 与 reproducing-papers 已读取；父代理授权该接入与有限实作。所有文件新建于本目录，旧 R16 结果只读。

机制一句话：只用已交付 END 历史和带捕获时刻的位置，改变原作者 SADG 的当前 Vertex.get_progress 边界输入，经共同承诺 guard 后执行其选择的依赖图；原优化器、目标、60 秒上限不改。

## 资格卡

|项目|判断|证据/边界|
|问题合同|PASS|完整历史速率在新停滞或速度转换后可能失配；测量是否改变可采用顺序，以实际 ΣT/makespan 检查，不以预测目标差冒充收益。|
|已发表锚点|PASS|固定作者 SADG c2626d996121a9d6c128844a167b917db24418ac、R16 SOURCE_ENVIRONMENT 与官方原生核心 R0。论文原本含进度边界，补 TODO 不是创新。|
|官方工件 R0|PASS|R16 官方 test.yaml ECBS→compile→原 optimize 已实跑；本轮不重复回归。沿用已单列的 k0/all-head 承诺适配。|
|外部基线|PASS（机制范围）|各臂均调用同一已发表作者优化器；强公共历史输入是可复核研究 adapter，不冒充论文完整实现或已发表新方法。|
|数据与场景|PASS（合成机制）|固定两车交叉公开路径与一个已完成动作历史，真实扰动由下列确定分段速度生成。无训练、CAL/TEST 或泛化声称。|
|纯仿真发表证据|UNKNOWN|此轮只识别历史失配和年龄机制；规模梯度、独立地图族、实际收费共同域、LMAPF持续任务仍缺。|

总资格 CONDITIONAL；只运行预登记最小机制试验。目标是证伪额外信息价值，而非锁题。

## 冻结条件、信息与上限

同 R16 mini 公开路径，2 agents × 7 actions，当前 index=1 为不可撤销 IN_PROGRESS；其他已完成/未开始状态固定。名义 2m/action，公共已完成历史为 A/B 各一次 2m/1s，完整可用历史时长模型对所有未完成动作均为 1s。历史实际 END：A 在0、B在0.25已交付；当前启动分别0、0.25；统一 decision/delivery=0.75。没有未来停止时刻、真实剩余时长或私有 profile 输入优化器。

三种真实 A 执行（进度每秒为单位；B始终1）：

1. stable：当前与未来 rate=1，预登记零增量控制。
2. short_stop：当前 [0,0.5] rate=0，之后 rate=1，未来动作rate=1。
3. speed_shift：从当前动作启动0起 rate=0.5，之后未完成动作保持0.5。

各条件比较 public_history 与 history_position_age0、history_position_age025 三种输入，9条比较记录。age0实际capture=.75；age.25实际capture=.5，从真实已发生前缀积分获得 POSITION；不能把decision真值填入旧捕获。位置只测A一次，B保持相同公共估计。测量臂的估计进度 `p_capture + age / historical_duration` 截于[0,1]；下界保持 p_capture，上界按公开速度界1推进，区间仅做预测误差记录，不能成为碰撞认证或 cap 授权。未来动作时长仍由同一完整公共历史得到，不利用 profile 持续性。

全程真实 q 仅供模拟捕获、独立误差核算和后缀执行；优化器输入文件不含真实 decision q 或未来速度。共同 guard 只检完整依赖图与当前承诺；点轨迹检查是执行后验证，不反向选图。

作者每call固定60s，上层90s。最多6个新增唯一优化调用、最多6个新增唯一后缀；如需超过必须先追加登记，不能事后扫参。按完整 graph_before（含所有时长/进度/状态/可切换资格）和原 optimizer SHA 精确复用旧解；compile patch须实编且完整语义相同方可复用，不能只凭输入名。按实际选择图、真实当前状态和未来真实速率复用后缀；short_stop的两种已有实际后缀可精确引用R16。所有零变化保留。

## 完整交付检查表

- [ ] 原始 public END/START → 分段前缀 → 捕获正文 → age projection → 只含可用信息的作者输入。
- [ ] 固定作者与共同 compiler/承诺适配 hash；新增调用日志/完整模型/求解状态，旧调用严格语义复用收据。
- [ ] before/after完整图、共同 guard、图差异与 active 承诺。
- [ ] 同真实状态下作者 can_execute/status 事件后缀，等待/完成后驻留全时域点距离审计。
- [ ] 预测进度/当前残余误差、图方向、实际 ΣT/makespan 单表；信息次数/年龄与求解时间分列，production_cost=null。
- [ ] 原结果不覆盖、失败保留、独立可复算输入和输出 hash；结论限定固定路径单次调度，不称 LMAPF 吞吐。

不新增学习器、不引入GSES量化改写、不用stub当强基线，不运行旧实物/ROS/旧地图后缀。误差模型的预测区间不是安全证明。
