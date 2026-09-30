# R5：真实END历史与两项FIFO任务流；留出决策支持缺失

本轮完成了真正训练、导出装载、共享物理执行和完整独立重放，但**不能评价历史模型的测试价值**：14个完整留出world×6方法的84次原生执行全部没有合法查询机会、没有查询、没有模型打分调用。六方法实际物理/正常END/任务序列相同，各110/112任务完成，局部受限completion sum为3361.877687914489…；1个world两任务未完成。不能把它写成学习零收益、模型与规则性能相当或学习无价值。

## 实际扩展与来源

直接父R4的1558冻结文件及9生产头保持不变。新包将每个真实联合world从四个单head扩成四机器人各两项原FIFO任务，第一head实际到goal/rest并交付正常END后，第二head才进入公共执行接口。当前计划/任务边界供actor，未来head由world feeder持有，不用于需求、关系或分数。所有实体共享Geometry/Index/PositionCommit、资源与时序；不是独立crop拼接，也不是作者100机器人全局执行。原作者可能早已排队第二task，本地只延迟head可见性；这是受限队列接口，不冒称原作者任务释放时间不变。

原PIE-D74cfba3未改binary/config真实100tick返回0，10000动作/352服务，但固定几何规则只4个互不重叠组，原mod5划分没有test组。完整失败支持审计保留。随后按相同规则追加原生200tick，真实返回0、20000动作/730服务；348个公开几何候选中贪婪接受前10组、80不同task IDs，排除R3/R4全部使用task。六train、两cal、两test按完整任务组冻结；一张random32×32地图、同配置任务背景，没有跨地图泛化。来源选择没有用模型或任何局部query收益。

每组固定四IID seed加eta0诊断；test另两未见shift seed在第二head后反转隐含速度，合计54完整world。合成误差为agent内persistent±1、每leg10%flip，全部在原bounded eta域。它是事前声明的可辨识关联，不是实测误差规律。actor没有condition/eta/privateprogress输入，也没有旧run先验H；查询候选必须本agent已有正常END交付、全world至少2条END，而且source恰好RUN+3/4，Quantity预算B4。真实RR维护循环cursor，仅实际查询后更新。

八task的completion从world0起算，未完成按96删失。该局部restricted-flow不是原作者LMAPF throughput，也不是按原release timestamp计算的标准flow，更不是生产完整COST。MAPF认可的完整global taskflow/标准负载比较仍由主项目另接；本包只能作局部机制pilot。

## 训练和全部真实结果

每world先跑WAIT；其前3个实际合格机会逐候选跑唯一单query，其余全WAIT。32个真实反事实标签：22train、10cal、0test。全WAIT物理/公共END/当前特征前缀逐项一致，仅方法policy/score/预算元数据排除。当前协议最大同时候选数只有1：train30world中22个1机会、8个0；cal10world中8个1、1个2、1个0；test14个全部0。这是覆盖失败，不能隐藏或按收益筛掉。

两个固定lambda1 ridge同18槽、同22标签、同组划分、同尺度、相同选择/预算；无history的后8槽在fit/predict恒0。最后8槽来自本world已交付END的agent率、近3条率、最新类、heading率、数量、接收时间和固定结构交互。权重真实closed-form训练，1e-9导出有理数，模型SHA e134ec8eec3a2064d2536cd1bea1983469914b171072039b4a101bb8e7206384。train RMSE：有history0.298923，无history0.407613；这仅是训练拟合，不能作为部署收益。校准误差完整记录RESULTS.json，没有据此调参。测试RMSE未定义，因为没有测试标签。

| 留出方法 | 原生world | 实际任务 | query | actor机会 | 局部restricted-flow总和 |
|---|---:|---:|---:|---:|---:|
| WAIT |14|110/112|0|0|3361.877687914489…|
| 真实RR |14|110/112|0|0|3361.877687914489…|
| 条件END规则 |14|110/112|0|0|3361.877687914489…|
| 当前head结构规则 |14|110/112|0|0|3361.877687914489…|
| ridge有history |14|110/112|0|0|3361.877687914489…|
| ridge无history |14|110/112|0|0|3361.877687914489…|

模型在全部test输入中实际装载，但测试并未调用其score，不能写成学习完成了有效闭环决策。单query WAIT-continuation训练与多query部署本有分布/互补偏移，本轮更早因支持缺失而无法识别该影响。所有world/反事实保留，HELDOUT_ALL_WORLDS表不按成功筛选。

## 复核、失败与后继边界

156次成功原生臂完整归档，独立70位Decimal从原连续profile/closed rectangle/公共END/已揭示head重放，实际15993MOVE、15993正常END、55653世界frame、32证书query、619后继head揭示。所有lease/退役严格认证lower>13/20、实际goal/rest服务、全源20000动作/FIFO730服务、全部模型train-only再拟合通过；五个private/history/未来head/错score/截断负控被拒。全部test84序列相同由root另独立确认；该root验证与本包物理重放互补。

机械attempt01严格编译失败（misleading indentation），保留原源码/receipt；此时没有native/fit。root指出旧draft最小agent并非多次RR，attempt02在任何统计执行前改为真正循环cursor。训练采集原pipeline曾因probe第2机会将WAIT0/probe1预算当作物理前缀而失败；后继调度脚本仅规范化该方法元数据，保留失败、复用所有hash绑定成功臂，不改native/inputs/seed/标签/模型或收益。没有丢弃失败/负值/无机会world。

下一事件驱动R5b是**新决策协议**，不是对既定R5语义的小bug修复：当前只source恰好3/4查看一次，需求在稍后END/WAIT/新head事件出现时，已超过3/4的合法source可能漏接。R5b先只用train/cal做实现和独立机械验证：公共需求变化/正常END/WAIT事件和年龄门槛触发，age>=3/4；加入public age，强解析规则条件于‘END尚未交付’的生存信息；真实多次query/竞争/任务影响与同world END因果通过后，再另冻结新训练/新留出。不能用这14个无支持test来挑新的收益阳性组。本轮R5b的承诺边界是可运行实现+train/cal机械验证，不新增无止境模型搜索。

DCC已有选择通信，Should I Replan?已有同世界反事实执行收益回归，REMAPv2已有带计算费用的世界模型gating。通用‘历史图→信息价值’不是新贡献；未来差异仍须落在真实执行进度证据查询、连续空间证书释放、正常END生存条件和global持续任务传播，且用认可标准共同负载验证。

可运行：`rtk proxy python3 audit.py`复核完整本地raw；`rtk proxy python3 scheduler_prefix_successor.py`只复用既有成功臂/冻模型并确认完整合同，不能用现有目录重做新设计。首次从归档恢复后按本包README的本地路径身份恢复raw；归档逐文件manifest可检查字节。
