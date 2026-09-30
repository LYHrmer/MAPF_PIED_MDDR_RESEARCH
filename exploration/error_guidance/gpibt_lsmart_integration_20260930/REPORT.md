# 官方 GPIBT → LSMART 真实闭环接入：首步完成，完整两例待运行

2026-09-30。本轮已把作者官方 Guided-PIBT 的持久 `MAPFPlanner::plan` 接到 LSMART 的任务／状态 RPC、原生 ADG 和 ARGoS 连续控制器，**实际完成一个联合格点动作及其物理执行反馈**。后续调用暴露了两机器人配置不兼容与停稳门槛缺口；已修正并构建，但最终 nominal/pause 两个 200-tick 试验尚未获 RPC 运行权限。不能称为完成零误差一致性、完整闭环验收、误差鲁棒性或比较实验。

## 已发生的执行与独立核验

固定作者 `front_fig_5x5`，两个机器人从(row0,col0)、(row2,col0)启动，seed42。收到作者 OneGoalTaskAssigner 实际公开的任务0→agent0/cell21、任务1→agent1/cell7之后，官方 GPIBT 第一次输出 `[W,U]`。LSMART 原 parser 把 agent1 的1m移动切成两个0.5m节点，原控制器合并连续执行；agent0保持原地。

| 实际记录 | 结果 |
|---|---|
| 规划提案／公开状态查询 | 1个提案，2次查询；第二次调用崩溃，无第二个提案 |
| ARGoS观测／截止 | 76个机器人位姿观测，tick0–37；最后查询tick38，即3.8s |
| 原生ADG节点／正常ACK | 2个MOVE节点、2个ACK，tick20与36；不是总试验END |
| ACK位置误差 | 0.0159069800m、0.0227801209m，均小于作者EPS=0.03m |
| 任务 | 已分配2个，真实任务服务END为0，两任务均未完成 |
| 实际驻留 | agent0的38个观测始终(0,0)；agent1末端仍有1.853mm单tick残移 |
| 同tick中心间距 | 最小1.0209268813m；未提取真实足迹半径，不报告足迹安全 |

[独立审计](audit.json)检查原始事件顺序、最新已送达观测、提案绑定view hash、格点邻接／障碍／顶点／反向边、命令身份、去重ACK、ACK真实位置与任务标记。7个篡改负例均被拒绝。**原始真实trace也被加强后的停稳门槛拒绝**：tick38查询前两帧agent1位移0.0018532396m，超过1e-6m。这个拒绝是实际发现，未从成功结果中删去。没有任务服务事件，因此任务服务和20-tick服务驻留逻辑尚未实测核验。当前checker也尚未实现S/P服务节点task_id及完整驻留核验，尚未把ADG半格分解反核整个提案；它是本次首步的有限审计，不是通用全执行验证器。没有暂停臂，因此暂停是否作用于活动MOVE、两臂任务前缀是否一致均待核。

## 身份、接口和修正

GPIBT来源为官方 `nobodyczcz/Guided-PIBT` commit `7f4b91e4ed134229710945a4670a78639cf008d5` 的既有公开seed后继；继续链接其原 `MAPFPlanner.cpp.o` 和 traffic算法对象，未改算法源码。配置为GUIDANCE、GUIDANCE_LNS=10、INIT_PP、RELAX=100、OBJECTIVE=1、FOCAL_SEARCH=2、ROBOT_RUNNERS，Release，无MAPFT。[全部链接参数与失败日志](build_receipts/)及[最终二进制／复用对象SHA](binary_manifest.json)均归档。

初版默认LNS group_size10超过N=2，第二次plan在作者 `destory_improve` 段SIGSEGV；源码中邻居选择按N处理，后续仍遍历group_size项。最终桥接在初始化后设置作者公开的 `trajLNS.group_size=2`。这是唯一支持性参数修正，不是扫参，**最终配置不再等同先前group10的原生R0配置**。group2桥接构建成功5.549秒；本轮没有运行它，不能宣称崩溃已经通过运行验证。首次链接遗漏boost_thread的失败与修正也保留。

LSMART来源为作者 `lifelong-smart` commit `a3780a45eb101f5b6834236f86bad39025f1e99f` 的既有fmt兼容后继。新增 `observe/snapshot` RPC、JSONL事件日志、联合结束后再调用规划器的invocation policy，以及可选固定pause。原任务生成器、parser、ADG及控制律保留；这是**新同步执行适配语义**，不能冒称作者原生异步throughput。LSMART是执行试验台，不是竞争算法。

`get_location` 原本返回未来commit cut，作者任务统计也可能登记commit cut上的任务。本适配只在所有已下达节点收到正常ACK、队列空且上一控制tick零轮速后调用；最终补丁还增加实际两帧位移≤1e-6m守卫。这样目标查询发生在真实执行边界。观测的 `speed_cm_s` 是原控制器 `prevVelocity_` 缓存，STOP分支可能保留旧值；它只能解释原MOVE-END判据，不能当作实际速度或停稳证据。半格中间节点可在运动中ACK，最终联合边界才要求停稳。

新增planner只收到当前已公开任务和已执行完成的格点起点；不收到pause标签、未来位姿、未来任务或离线完整路线。每次只在新view后调用一次持久官方plan，绝非离线脚本预计算后包装成在线算法。此次接入仍未实现合同中的一般连续足迹准入／误差包络监测／伪造END在线拒绝；离线checker拒绝坏trace不等于服务器在线拒绝坏RPC。

## 可复核工件与明确未完成项

[事前协议及修正登记](PROTOCOL.md)、[后继生成器](prepare.py)、[精确LSMART补丁](lsmart_integration.patch)、[桥接](gpibt_bridge.cpp)、[有界runner](run_trial.py)、[独立审计](audit.py)、[源码SHA](source_manifest.json)、原始两次attempt与构建回执均已归档。旧证据目录未改。最终源码和二进制有SHA；初版失败运行未单独保存其二进制SHA，不能用最终SHA冒充初版运行身份。原始失败输出、命令、配置、trace和receipt仍完整保留。

离线重算无需RPC：`rtk proxy python3 audit.py`（在本目录运行）。剩余唯一固定native入口为 `rtk proxy python3 run_trial.py --fixed-pair`，依次运行nominal与agent0 ticks30–49暂停两例，每例200ticks；SIGALRM54s覆盖RPC和planner阻塞读取，再清理进程组。下一步还必须核对暂停是否落在活动动作、全部任务与END、真实截止删失、两臂公开任务前缀、最终同步停稳条件，并将末尾未完成占用保留。没有完整200tick或误差试验通过的结果。

第一次原生尝试因沙箱禁止localhost socket失败；经明确升级后第二次确实运行到上述首步。之后最终两例的升级请求两次停在权限等待，分别约1231秒和530秒后由主代理中断；这些等待不是算法耗时。最终两例目录没有产生。本轮按主代理要求停止进一步原生与权限请求，将审批留给主代理作为最后一步。
