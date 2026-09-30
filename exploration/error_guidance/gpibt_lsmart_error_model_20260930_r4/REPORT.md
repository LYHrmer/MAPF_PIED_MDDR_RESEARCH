# R4：真实训练完成，原定留出接口没有动作影响

40/40官方 GPIBT→LSMART native run 均真实完成400tick、退出0，没有调试重跑或挑选seed。12train/4cal按完整run切分，102个未删失原整格MOVE时长标签实际拟合ridge residual，48个cal标签选lambda1。checkpoint为`trained_model.json`，SHA `16fac44d6d23c7c472a5caed4bdce87ba19bca632e6a70f7fa16a9ccf14c8094`。模型和幅值冻结后完成seed61六条件×四policy的24次留出。

校准MAE：analytic5.1875、history1.614583、learned2.074607ticks。学习模型暂输强历史。原定幅值规则给出0.5；留出期间模型确从已交付command/END历史在线产生非零偏置，bridge实际加到公开p/p_copy、执行官方plan并恢复原aging，独立核对全部数值通过。但是所有实际search-order flip为0，六条件的四臂官方动作prefix和决策tick完全相同。因此本包**没有完成预测改变动作的闭环验收，没有执行收益**。事前±2公开争用探针可改变动作，只说明接口有能力，不能代替实际冻结幅值的学习决策证据。

| seed61条件 | 四臂相同真实服务数 | 截止pending节点 | 采样最小中心距离m | analytic/history/learned整MOVE影子MAE ticks |
|---|---:|---|---:|---|
|nominal|3|[2,1]|0.609305|5.1538 / 1.9231 / 2.9877|
|slow065|2|[3,4]|0.725384|5.2727 / 2.7727 / 3.9859|
|slow085|2|[1,1]|0.651954|4.8333 / 2.2500 / 2.8873|
|axis|2|[3,3]|0.725083|7.1818 / 4.0455 / 5.1133|
|unknown_pause|2|[0,1]|0.609598|6.6923 / 5.7692 / 4.6839|
|unknown_shift|1|[1,0]|0.766471|6.6364 / 3.5000 / 4.5479|

误差表是在zero-policy留出轨迹上按实际随后公开选择的轴计算三预测的共同影子误差，不是反事实新轨迹吞吐，也不是实时planner平均候选轴预测的逐值同一指标。unknown_pause首次实际活动MOVE tick29，真实抑制29..48；unknown_shift同tick开始未知0.55执行倍率。未来干预名称/倍率/时长未进模型。seed44四个训练run都在一次agent1完整MOVE后进入361次 `[WAIT,WAIT]` 持续等待，362个不同规划tick，约38秒，无agent0 trigger/服务；未跳过或当0标签。

`summary.json`保存所有40run分项与六条件四臂。`audit.json`完成原动作映射、ADG/实际原ACK谓词、停稳view、20tick服务驻留、task owner/id、pending、400tick/800pose及800实际轮速命令、历史截断、预测输入/bias、原priority aging及恢复的重放；120个真实篡改负例拒绝。其原谓词通过不代表所有节点点误差<0.03：train42slow065的中间半节点ACK点误差0.030192m，cal51axis也有中间半节点偏差，分别显式列出，原作者径向on-the-fly谓词仍符合；整格END、服务/settled view仍按0.03核。原阈值、原控制算法、所有raw均未改；不宣称连续足迹安全。

模型目标明确为first_nonzero_MOVE_command→最终整格MOVE ACK，排除了proposal后的转向/派发等待。两半节点未当两整步；删失target为null。额外导出proposal/first_dispatch→whole_END及前置间隔诊断，不能把运动段预测说成完整占用周期。每tick合法输入和offline剩余ACK target分文件，活动预测仅诊断，实际规划作用点仍joint-settled。完整字段/校准MAE-MAPE口径差异及离线审计初版修正见`DATA_SCHEMA.md`；初版代码/audit保留，没有原生重跑。

本包是明确的planner-adapter原型，搜索算法14对象和group2保持，R4只增加共同输入与临时priority偏置及执行条件倍率；解析/history/learned均采用同一共享信息/偏置函数。zero是内部R1参考，其他两个是内部同信息消融，不能冒称发表方法。来源、许可沿用包内GPIBT/LSMART LICENSE、parent manifest、source/patch/build receipt和18binary/object身份。学习priority或执行时长本身已有相关工作，不能据本pilot宣称新颖性；正式纯LMAPF作者baseline比较属于另一包，不能当连续执行误差对照。

后继另立R4b，原40run、协议和模型全保留。失败是预注册幅值不足以影响离散排序，不能在本包test后改幅值伪造成功。
