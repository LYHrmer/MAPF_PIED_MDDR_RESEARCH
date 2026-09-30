# 官方 GPIBT → LSMART：完整200tick闭环与真实任务服务通过

2026-09-30。第二轮完成了固定 nominal/pause 两例真实执行，并闭合官方在线动作、原生 parser/ADG、控制器实际位置、正常 ACK 和任务服务的逐事件审计。两例修复后试验都正常运行到作者200tick截止，分别调用官方 GPIBT 五次、完成一个有真实20tick驻留的任务服务。**此前仅一个联合动作、零任务服务的状态已被实质推进。**固定暂停未击中活动 MOVE，当前结果不支持一般执行误差鲁棒性、连续足迹安全或学习优越性。

## 固定试验结果

作者 front_fig_5x5、2机器人原始起点(row0,col0),(row2,col0)、seed42、200ticks/10Hz。GPIBT是持久官方 `MAPFPlanner::plan`，只接受最新已公开任务和共同完成、实际停稳后的格点起点；LSMART是执行试验台。最终报告的 nominal_retry01/pause_retry01 是事前登记的唯一 task_id 接口修复重跑，两例同时采用同一修复。首次 nominal/pause 完整原始数据与失败审计保留，未按性能择优。

| 实际指标 | nominal_retry01 | pause_retry01 |
|---|---:|---:|
| 原生正常截止 | tick200 | tick200 |
| 控制器位置观察 | 400，tick0–199 | 400，tick0–199 |
| 官方 plan／原生 parsed 节点 | 5／27 | 5／27 |
| 实际 admit／正常 ACK | 26／23 | 22／22 |
| 真正服务完成数 | 1 | 1 |
| task1（agent1/cell7）服务区间及END | tick116–136 | tick126–146 |
| 原生 timer 减计／含END驻留位置样本 | 20／21 | 20／21 |
| 服务驻留最大位置误差 | 0.0218472478m | 0.0218472478m |
| 同tick采样最小中心间距 | 0.9726382081m | 0.9726001682m |
| 末尾已admit未ACK／未admit节点 | 3／1 | 0／5 |
| 外层启动、运行和清理总墙钟 | 1.814380s | 1.860675s |
| 篡改负例被拒绝 | 15/15 | 16/16 |

各例真实任务前缀均为 `(task0,agent0,cell21) → (task1,agent1,cell7) → (task2,agent1,cell20)`。这是从各臂实际公开 view 逐次提取的相等前缀；没有以同seed代替检查，也没有强行重放另一臂的任务源。task0/task2均在截止时未完成，未补END。五次官方动作序列相同 `[WAIT,U] → [D,E] → [E,E] → [D,W] → [D,D]`；对应实际 invoke ticks 为 nominal `[1,39,87,138,187]`、pause `[1,39,97,148,197]`。这里E/D/W/U按行列网格定义，不代表机器人直接免转向移动；原生 parser 生成了真实 TURN 与0.5m MOVE。

## 审计与修复

[独立审计](audit.py)和[完整结果](audit.json)核对全部官方决定与提案 hash／step身份、格点邻接／障碍／顶点／反向边、原生转向和半格及S分解、每个admit的几何和任务身份、每个ACK的最新已送达位置与节点、每次新view之前的全部ACK和停稳、20次STATION timer减计及其间全部21个位置、真实任务owner/id/目标与后续bookkeeping。末尾 pending 节点和命令几何完整保留，模拟截止仅作为删失。负例包括半格错误、task_id遗漏、错误服务END身份、伪未来位置、重复ACK、未发生服务的任务完成、timer篡改／减计缺失、伪装活动暂停及抹掉末尾占用。

第一对试验原生运行正常但严格审计拒绝：原生ADG的S `action.task_id=1`，`getPlan`从从未被parser填充的 `action.task_ptr`输出 `task_id=-1`，控制器也收到-1；服务器END仍带1。唯一修复将RPC wire任务字段取自已有 `action.task_id`，未改任务生成、服务计时器、运动参数、ADG放行或规划算法。旧server二进制、源码快照、二进制／源码清单、原始两臂和[首次失败审计](first_pair_audit.json)均保留；[精确补丁](task_wire_fix.patch)及6.671s重建回执可复核。新server SHA `ceecb90658c53e327cbd4c0b0ec35862a222a510ae5e78a8bd7ce5396bd5b003`；旧server SHA `128bf76262a137d351e74227399072fe10906c5af0a0c93fb774590c33bea21d`，绝不用新身份追认首次运行。

已到可见目标的WAIT使用初始点task注释，令作者parser生成原有STATION；若只标重复的最终点，作者wait分支会直接continue并丢任务。这是登记的适配表示修正。本例实际服务来自MOVE到goal，因此WAIT到goal分支本轮未被真实服务触发，不能额外声称该分支的原生执行验证。

## 暂停与截止的准确含义

robot0 ticks30–49的20个暂停日志全为STOP、空队列、无node。该物理控制暂停同时跳过作者每10tick的obtain_actions，使新任务动作派发从tick40推迟到50；没有暂停正在移动的节点。agent1任务END延迟10ticks与后续invoke偏移是实际结果，但不是“活动MOVE暂停后恢复”的验证。固定设计保留，没有换暂停时窗寻找更好的效果。pause的末尾5节点尚未派发，机器人仍真实驻留在上一次完成位置；这既不是完成全部工作，也不是新增END。

正常horizon是服务器实际tick200，位置观察在ControlStep、物理推进之前采样，最后已送达位置为tick199，距截止0.1s。nominal末样robot0约(-2.438987,-1.003773)m仍在运动，robot1约(-1.000086,-1.015856)m尚有队列；pause末样约(-1.972540,-0.999000)m、(-1.000086,-1.015856)m，实际停稳但ADG还有未派发计划。audit保留这些位置、队列、未完成节点、命令路径和未完成任务，不把tick199样本冒充物理tick200精确终态，也不推导最后0.1s的连续安全。

观察的speed_cm_s仍是原控制器缓存而非真实测量速度。停稳审计使用上一轮零轮速命令、空队列和实际两帧位移≤1e-6m。中间半格MOVE可边移动边正常ACK，终端共同边界才要求停稳。中心间距是采样指标，未提取足迹半径；没有误差包络、一般连续足迹准入、在线伪END拒绝或误差空间实验。离线坏trace拒绝不等同服务器在线拒绝坏RPC。

## 身份、成本与复核入口

[源码与许可说明](SOURCE_AND_LICENSE.md)、[事前协议](PROTOCOL.md)、[patch](lsmart_integration_r2.patch)、[全部构建回执](build_receipts/)、[二进制及官方对象SHA](binary_manifest.json)和[全部工件SHA](artifact_manifest.json)在本目录；旧47份文件按[旧目录清单](previous_archive_manifest.json)逐字节保持。原官方GPIBT算法对象和上轮group2桥接完全相同；参数仍GUIDANCE、GUIDANCE_LNS10、INIT_PP、RELAX100、OBJECTIVE1、FOCAL_SEARCH2、ROBOT_RUNNERS、group2，不能冒称原group10 R0。server全构建28.970s、client16.967s、wire修复server重建6.671s，均正常退出。五次官方plan计时为 nominal48/80/73/150/74μs，pause42/159/88/157/125μs；这是桥接内plan调用时间，不包含初始化、RPC、原生物理执行和日志开销，不是跨方法性能比较。

无需socket的复核：`rtk proxy python3 audit.py`（本目录）。所有试验目录不可覆盖；runner每例SIGALRM54s覆盖socket／readline，进程组有界清理，fixed pair外层120s。初次sandbox socket探测仍EPERM；主代理集中审批fixed-pair并保存精准命令prefix，之后只有该身份下的固定修复重跑，没有重复等待用户。未运行额外published方法比较或学习器。

这轮足以把真实官方planner闭环、完整动作映射与真实任务服务纳入下一步共同执行接口。下一研究问题是，在可比的正式任务流和确实击中活动执行的扰动下，强解析／历史校准已解释多少收益，以及是否留下合法可观察的学习残差；当前两例无法回答这一点。
