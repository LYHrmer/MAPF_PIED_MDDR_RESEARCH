# 官方GPIBT → LSMART：真实活动MOVE暂停、恢复与监督数据

2026-09-30。事前登记的首次活动MOVE干预已真实发生。固定nominal/pause两臂均运行200ticks，独立重算首次eligibility均为tick59：agent0原生node2仍未ACK，前一实际轮速为19.25612949/20.74387051cm/s，实测位移0.01667857139m。pause在59–78连续20tick发零轮速且保留原队列、目标和ADG节点，79恢复原控制，原半MOVE正常ACK68→88，原整格MOVE正常END84→104。**本轮关闭了旧pair只暂停空队列的缺口，未换窗口、调参数或native重跑。**两臂各一次真实20tick任务服务；当前没有运行我们自己的误差学习策略。

## 原生固定结果

作者front_fig_5x5、原2机器人起点、seed42、200ticks/10Hz、官方GPIBT持久对象、公开group2、原作者任务分配、同步停稳R1视图、r2 `action.task_id`唯一wire修复保持。nominal仅记录相同规则虚拟trigger，不抑制控制。LSMART仍为执行试验台。

| 保存事实 | nominal | pause |
|---|---:|---:|
| 实际正常horizon / 控制器位置样本 | 200 / 400，tick0–199 | 200 / 400，tick0–199 |
| 官方plan / parsed节点 | 5 / 27 | 4 / 22 |
| admit / 正常ACK | 26 / 23 | 22 / 21 |
| 实际轮速命令覆盖 | 400 | 400 |
| 最早活动trigger | 59，虚拟 | 59，施加干预 |
| 零轮速抑制 / 恢复 | 无 | 59–78 / 79 |
| 被暂停半MOVE node2正常ACK | 68 | 88 |
| 对应原整格MOVE node3正常END | 84 | 104 |
| 首非零MOVE命令→原整格END | 58→84，26ticks | 58→104，46ticks |
| task1 agent1/cell7 服务起止/END | 116–136 | 136–156 |
| timer减计 / 含END驻留样本 | 20 / 21 | 20 / 21 |
| 服务驻留最大位置误差 | 0.0218472478m | 0.0218472478m |
| 同tick采样最小中心距离 | 0.9726382081m | 0.9728262043m |
| horizon已admit未ACK / 未admit节点 | 3 / 1 | 1 / 0 |
| 整trial启动、运行、清理墙钟 | 1.949648s | 1.773055s |
| 活动/mapping篡改负例 | 10/10拒绝 | 14/14拒绝 |
| 数据可见性/标签篡改负例 | 7/7拒绝 | 7/7拒绝 |

两臂实际任务前缀均`[[0,0,21],[1,1,7],[2,1,20]]`，从每臂实际公开view核出，未用相同seed代替检查。task0/task2在horizon未完成，不补END。nominal真实invoke ticks `[1,39,87,138,187]`，pause `[1,39,107,158]`；共同动作前缀 `[WAIT,U]→[D,E]→[E,E]→[D,W]`相同，nominal另有`[D,D]`。任务服务晚20ticks和少一轮新plan是该固定同步R1调度中的实际结果，不是算法优劣排名。

## 真实停止、恢复与占用的范围

[试验前协议](PROTOCOL.md)与[冻结身份](ready_for_trial.json)在运行前已保存。触发发生在ControlStep当前pose观察之后、obtain_actions/出队/ACK/控制之前；独立审计用前一tick真正发给actuator的参数、当前观测位移和已admit未ACK集合重新求最早触发，并非信任一条trigger标签。原生缓存`speed_cm_s`仍保留，不用于证明活动轮速或实测速度。

pause原queue_size1、node2、target(-0.5,0)m、timer/task字段在20tick不变，无agent0派发、出队、ACK或service timer推进；每tick实际轮速参数均0。物理不会因一条零命令立即重置：tick60还有0.00332142861m惯性尾移，tick61–79各次位移0；79恢复前仍在同一物理位置，80观测到重新移动。所有这些样本留在raw与[物理补审](motion_supplement.json)。暂停不是位置传送，也没有重置作者PID缓存。原整格终点(-1,0)m及未ACK节点仍保留，正常第二半MOVE最终ACK104；没有用人工END闭合。

完整[mapping/服务审计](audit.py)及[audit.json](audit.json)复用父独立的action→proposal→原parser TURN/半MOVE/STATION→ADG admit→实际control/pose→正常ACK→任务驻留/owner/id/goal→后续bookkeeping检查，新增实际command/trigger/pause/resume检查保持独立数据路径。父mapping replay删除新增日志后计数为784/749；实际原raw事件为1185/1171，另在motion_supplement单列，不把过滤后数写成raw总数。原所有raw sequence连续性直接核验。坏trace拒绝仍是离线检查，不宣称服务器在线拒绝伪RPC。

最后已送达pose为tick199、物理推进之前，距horizon200为0.1s。nominal agent0约(-2.438987,-1.003773)m仍运动，agent1约(-1.000086,-1.015856)m有队列；pause agent0约(-1.972592,-0.999009)m停稳但task0未完，agent1约(-1.000030,-1.105748)m正在末半MOVE，pending `[0,1]`。原路径和占用作为截止删失保留。采样中心距离、signed进度/横偏和端点EPS0.03m检查不能替代连续机器人足迹/误差包络安全证明。

## 可用于主动学习的分离数据

[当前schema](DATA_SCHEMA.md)、[scope纠正说明](DATA_SCOPE_CLARIFICATION.md)与[datasets](datasets/)将每臂400个已交付context和400个离线target完全分开。context含当时已经发出的命令、公开task/intent、严格在freeze sequence之前交付的END及因果历史摘要；排除当前实际pose、progress、横向偏差、未来END、未来task/trigger、private PID或缓存speed。已施加的暂停状态和已发生pause tick可见，不补给过去的行。接口属于新增execution monitor影子信息，当前GPIBT没有逐tick读取它；正式学习策略还需固定共同信息合同。trial名称只是run分组元数据，不应拟合为未来regime。

独立offline_targets含实际pose、公开已派发MOVE队列段上的signed progress/lateral、下一tick位移、真实未来ACK及horizon删失。现有队列可能只有0.5m半MOVE，因此这些episode不能自动称原整格MOVE。初版scope文字、manifest及audit保留；数值和原数据没改写。另有各360行`original_step_targets.jsonl`，按真实公开proposal整格start/goal和最后原生M节点重建完整原MOVE的进度、横偏及最终END/删失，不偷放到online features。

已派发队列段的因果参照为此前已完成段的elapsed ticks/m滚动中位数；没有历史时unknown，不以整run均值或未来nominal填补。其offline ACK剩余量残差：nominal158个未删失且有历史的MOVE context，范围[-3,4.5]ticks；pause162个，范围[-4,17]ticks。最大已派发MOVE横偏为0.0227329242/0.0233771556m。这些是实际数据和参照，不是已证明难以解析的学习残差，也不是训练/泛化结果。当前数据可以立即支持低成本残差/释放时间模型的主动并行试验，训练目标、模型与完整run留出另行登记；不以解析参照先失效为训练许可前提。

[导出器](export_data.py)、[当前manifest](dataset_manifest.json)与[最终可见性审计](dataset_audit_final.json)重新从raw核400+400行/臂的context/target和所有历史END先后关系，真正执行7个泄漏/伪标签负例。两run只有一图、一任务seed及一处暂停，应按整个run划分，不能随机拆相邻tick取得虚假留出；不宣称OOD、吞吐学习优势或世界模型完成。当前算法未用监督target释放资源或签发权限。

## 构建、失败与身份

[来源/许可](SOURCE_AND_LICENSE.md)固定GPIBT `7f4b91e4ed134229710945a4670a78639cf008d5`和LSMART `a3780a45eb101f5b6834236f86bad39025f1e99f`。仅controller cpp/h两个native源变化；[完整source tree差分](native_source_tree_manifest.json)、[patch](active_move_r3.patch)、[编译源快照](source_snapshot/)与[source manifest](source_manifest.json)可核。实际client configure0.774s/build16.958s均exit0，.d绑定新cpp/h。server源码不改，已修复server二进制与官方bridge直接字节复用；14个官方GPIBT算法objects不变，全部18个runtime/object身份试验前、启动时、归档前核验。无自写planner、额外参数扫参或换任务源。

一次准备脚本断言把6个原actuator调用数成5，尚未构建/启动native；失败receipt和部分native树保留在`preparation_attempt01.json`所指目录，修正仅复制断言。成功prepare/build之后才冻结控制实现并真实运行，首次固定pair即通过，无native调试重试。初版数据“整格MOVE”的scope误称也明确保留并纠正，不改变任何raw、科学输入、control实现或既有输出数值。

旧r2全部78个文件（77个manifest成员加manifest本体）按[父目录SHA](previous_archive_manifest.json)保持。试验由root集中合法审批新精确prefix并代跑，未绕过sandbox socket限制；trial 49s业务阻塞守卫及至多4.5s集中进程组清理均纳入54s整体界限，fixedpair外层120s，实际远小于限额。该时长不是跨方法性能结论。

复核无需socket/native重跑：导入`audit.run()`或使用`audit.py --output NEW.json`；`dataset_audit.py --output NEW_DATA.json`可核当前导出；文件输出拒绝覆盖。冻结[source/control/代码/全部raw/数据/审计/报告SHA](artifact_manifest.json)由archive.py核验。root独立复核另存，不追认作本代理的结果；未commit/push，root统一发布。
