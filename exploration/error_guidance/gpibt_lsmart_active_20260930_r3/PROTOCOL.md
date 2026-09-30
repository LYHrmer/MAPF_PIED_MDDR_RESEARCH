# 官方 GPIBT → LSMART：首次真实活动MOVE暂停协议

冻结于2026-09-30，任何本目录真实试验之前。直接父为`gpibt_lsmart_integration_20260930_r2`；旧全部归档文件及manifest逐字节保留。此前固定tick30–49暂停全为空队列，本协议是新活动干预，绝不追认旧pair。

固定输入：作者front_fig_5x5、2robots、原起点(row0,col0)/(row2,col0)、seed42、200ticks、10Hz、原作者任务分配流、group_size2、同一官方GPIBT算法对象和持久bridge进程。仍只在全队列ACK、前一零轮速命令、两帧实测位移≤1e-6m的共同停稳view规划。继承唯一task wire修复`action.task_id`；原parser、ADG、运动PID/参数、正常ACK和20tickSTATION规则保持。

唯一首次触发规则，agent0 ControlStep观察之后、周期obtain_actions/出队/ACK/控制之前：当前front是原生MOVE，nodeIDS非空且这些节点尚未ACK；前一ControlStep实际传给SetLinearVelocity的left或right参数非零；当前观测位置较前一tick实测位移严格>1e-6m。三个条件同时成立的最早tick记T，至多触发一次。实际轮速命令由原生actuator调用参数记录，绝不使用cached speed_cm_s冒充实测/实际命令。nominal按相同规则只记虚拟触发；pause在T..T+19连续20tick将两个轮速参数设0，跳过原控制/周期派发/出队/ACK/服务减计，并保留queue、node身份、target和原ADG占用。T+20恢复原控制与原周期派发，PID内部状态不重置。如果200tick未出现T，则如实报告无触发，不移动窗口、不调参数、不追加假活动。

两臂分别执行各自真实作者任务流，不能以同seed假定前缀相等，也不强行重放另一臂未来任务。日志绑定官方决定→proposal→parsed→admit→实际轮速/pose→ACK→20tick驻留→服务owner/id/goal→任务bookkeeping。截止pending、未完成任务和最后已送达tick199位置保留；horizon200不是精确物理tick200位置。采样中心距离/进度/横向偏差不构成连续足迹安全证明。

事前验收：重新从前一tick已发轮速、当前pose位移和已admit未ACK集合计算首次eligibility；核两臂唯一trigger、pause恰20tick、期间没有agent0 admit/ACK/队列变化、每tick实际零轮速；核T+20恢复且原活动节点随后正常ACK或截止删失；完整mapping/服务/任务因果审计仍通过。篡改负例真正执行，覆盖伪轮速、伪位移、已ACK触发、提前恢复、暂停中ACK、错误目标/任务、抹除末占用。若真实运行出现明显接口bug，可在本目录保留旧raw/二进制/源码身份后作明确单项修复，固定重跑两臂，最多两次调试重试；不得改变输入、规则或择优。

每trial整体54s界限覆盖socket/readline和进程组清理：业务阻塞守卫49s，集中清理至多4.5s，整pair外层120s。启动/清理时长只是运行限额，不作算法性能。所有shell使用RTK，RPC沙箱拒绝沿require_escalated；不绕过已有审批。构建和offline检查不启动socket/native科学试验。

同时导出两份独立数据，为用户要求的主动学习候选准备：`delivered_context.jsonl`只用冻结边界之前已交付的原命令、公开view、历史正常END以及当前已发轮速/是否施加干预，排除未来END/任务、实际位置、progress、private PID、真实扰动未来；`offline_targets.jsonl`独立带实际pose的投影进度/横向偏差及未来ACK/删失标签。这是执行监视器可获得的影子学习接口，不声称当前GPIBT逐tick读取过它，不喂当前策略；正式新策略要另登记信息合同。当前干预状态是已经施加并记录的事件，不包含未来触发tick。按完整run划分训练/留出，不能按tick拆分同一运动；两臂仅pilot，不宣称学习收益、世界模型或作者论文R0。

原native端点EPS0.03m、每半MOVE0.5m、任务驻留20tick均不调整。监督target不直接签发权限或释放资源。原始流、来源/许可、构建receipt、源码/对象/二进制身份、独立审计和数据schema一起冻结，root统一commit/push。
