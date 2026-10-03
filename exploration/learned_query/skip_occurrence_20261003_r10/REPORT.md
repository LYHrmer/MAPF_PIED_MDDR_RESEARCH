# R10：持久跳过当前 occurrence 的查询决策

R10完成156个真实原生运行：10个新train/cal condition收集、98个完整H128反事实分支、48个冻结模型留出臂，执行失败0。留出总任务condition=344、history=344、nohistory=344、一次SKIP诊断=344、整程WAIT=348。history/nohistory相对condition的总任务差为+0/+0。本轮没有新增学习任务收益；两个模型全部真实服务序列与condition相同。持久SKIP诊断改善了两支服务时间序列，first4次项合计改善2.333768，但主任务无变化。整程WAIT反而多4任务。接口及预算作用已落实，不能以接口正确或少查询代替任务收益。

## 实作接口

公开动作QUERY(agent, MOVE identity)扣一次容量；当前WAIT返回原事件循环，不安装状态；SKIP_OCCURRENCE(agent, MOVE identity)不扣次数，持续屏蔽这个完整身份直到已接受/交付normal END。私有physical END不能提前清除。正常END、物理资源、认证POSITION、任务服务照常运行，后继MOVE使用新身份。

原候选提取不变，query层显式输出raw_candidates、visible_candidates、skip_state，以及安装/normalEND清除事件。反事实前缀、动作和部署的尾策略始终是同一个公开condition函数pi0，作用于扩展后的可见状态。不重置历史/预算，不约束自然尾轨迹分叉，不把旧WAIT重命名为SKIP；学习策略仍只替换一次。

## 预登记与标签

两图empty-32-32/random-32-32-10，N16、H128、capacity16、每agent FIFO256。每图4个新训练family、1个校准、2个测试family；训练seed101101..101104/102101..102104，校准101201/102201，测试101301/101302/102301/102302。场景行偏移训练336/352/368/384、校准400、测试416/432，split任务ID及行组互斥。测试每family配对IID/SHIFT，SHIFT在各agent实际MOVE ordinal64后翻转私有误差，不能作为特征。

按已用预算0..5、6..11、12..15和单/多候选各取首机会，每world最多12个完整分支，总上限120。完整机会含WAIT及每候选QUERY/SKIP。实际30个机会，其中4个多候选；98分支，没有按收益补满上限。超出完整分支额度的首机会和缺失层保存在SAMPLING_COVERAGE.json。

优势为J(action→pi0)−J(当前WAIT→pi0)。J优先全程完成任务，再减固定每agent初始first4 FIFO受限完成时间和/16385，未完成计128；时间使用原1e-6日志区间中点。次项绝不反转一任务差。WAIT有真实续跑及精确零标签，无伪特征行。

|split/action|rows|advantage sign counts|whole-task gain counts|
|---|---:|---|---|
|train_QUERY|28|{'zero': 14, 'negative': 7, 'positive': 7}|{'0': 27, '1': 1}|
|train_SKIP|28|{'zero': 13, 'negative': 8, 'positive': 7}|{'0': 28}|
|calibration_QUERY|6|{'zero': 5, 'negative': 1}|{'0': 6}|
|calibration_SKIP|6|{'positive': 2, 'zero': 4}|{'0': 6}|

本轮训练终于出现一行主任务+1：random102102/op7的QUERY13完成49、WAIT及SKIP完成48，各支最终16次query。这是预登记新family中的标签，没有据此补采样。SKIP全部训练主任务差仍为零；其正负信号来自固定FIFO时间次项。

## 对原π0的可改善空间：事后诊断

root对原已登记TRAIN/CAL的30个机会、完整98个分支作事后枚举复核：相对原condition pi0，能增加主任务的机会为0/30；按已登记区间中点J能改善时间次项的机会为15/30。唯一相对当前WAIT的+1 QUERY标签只是恢复原pi0本来就选择的动作，未超越pi0。因此“存在正主标签”不能解释为“训练集合存在一次替换的吞吐改进空间”。

这是原有限one-intervention集合的posthoc诊断，没有新增实验、重训、挑选测试或修改目标，不是任意时刻/多次策略的全局最优性证明。15个J次项机会按既定1e-6时间区间中点计算，其中极小差可能处于日志分辨率内，不能全作有实际幅度的时间收益。数据和复算代码为ROOT_OPPORTUNITY_HEADROOM.json及root_opportunity_headroom.py。

## 模型冻结

history/nohistory各有QUERY/SKIP两头，24个原公开特征、lambda1、截距不惩罚。训练集加权均值/尺度标准化，每头权重1/cardinality，零方差scale1；折回25个raw系数并舍入1e-9。nohistory在预处理和评分屏蔽10..17，前缀/尾策略仍共享END历史，这不是完全移除世界历史。WAIT得分0，动作分数必须严格正；正分同分先QUERY再SKIP，随后低agent及完整action字典序。

校准只诊断，无阈值/模型选择。冻结SHA为52e1573ffd45eb5920450eb9f67a40d369b353162d94856894f663cf8d16cd14，MODEL_FREEZE_RECEIPT记录已有test receipt=0，之后才调用测试，48输入均绑定同一系数。

|head|train weighted RMSE|calibration weighted RMSE|
|---|---:|---:|
|ridge_history_QUERY|0.117526691|0.207102494|
|ridge_history_SKIP|0.000355384|0.000247336|
|ridge_nohistory_QUERY|0.179125694|0.088906982|
|ridge_nohistory_SKIP|0.000499189|0.000169006|

## 全部留出结果

六臂为整程WAIT、condition、onceWAIT、onceSKIP、history、nohistory。所有once臂在首次已用至少6且仍有容量的非空公开机会替换一次，再永久恢复pi0。onceWAIT/onceSKIP是内部机制诊断，不是发表baseline。

|policy|tasks|queries|fixed first4 restricted time|
|---|---:|---:|---:|
|WAIT|348|0|46577.5259720|
|condition|344|128|46656.1162270|
|once_WAIT|344|128|46656.1162270|
|once_SKIP|344|128|46653.7824590|
|once_history|344|128|46656.1162270|
|once_nohistory|344|128|46656.1162270|

|world|WAIT|condition|once_WAIT|once_SKIP|once_history|once_nohistory|
|---|---:|---:|---:|---:|---:|---:|
|empty-32-32_test_101301_IID|35|35|35|35|35|35|
|empty-32-32_test_101301_SHIFT|35|35|35|35|35|35|
|empty-32-32_test_101302_IID|44|44|44|44|44|44|
|empty-32-32_test_101302_SHIFT|44|44|44|44|44|44|
|random-32-32-10_test_102301_IID|53|51|51|51|51|51|
|random-32-32-10_test_102301_SHIFT|53|51|51|51|51|51|
|random-32-32-10_test_102302_IID|42|42|42|42|42|42|
|random-32-32-10_test_102302_SHIFT|42|42|42|42|42|42|

按四个family合并IID/SHIFT，相对condition的主任务差：

- WAIT: {'101301': 0, '101302': 0, '102301': 4, '102302': 0}
- condition: {'101301': 0, '101302': 0, '102301': 0, '102302': 0}
- once_WAIT: {'101301': 0, '101302': 0, '102301': 0, '102302': 0}
- once_SKIP: {'101301': 0, '101302': 0, '102301': 0, '102302': 0}
- once_history: {'101301': 0, '101302': 0, '102301': 0, '102302': 0}
- once_nohistory: {'101301': 0, '101302': 0, '102301': 0, '102302': 0}

## 持久性与实际参与

所有分支及测试实际安装SKIP 42次，42次在accepted normal END清除；原合法候选再次出现118次，全部持续屏蔽，同occurrence查询为0。30支实际出现同agent后继可见候选，证明未误伤后继；35支查询了condition未查询的其它occurrence。每支安装后预算保持、END清除时预算、首个后续QUERY和新旧查询身份都保留；全程查询总数差与具体saved-unit因果归属不混淆。

|policy|replacements|actual action changed|SKIP selected|full service records changed|
|---|---:|---:|---:|---:|
|once_WAIT|8|8|0|0|
|once_SKIP|8|8|8|2|
|once_history|8|2|0|0|
|once_nohistory|8|0|0|0|

实际替换候选数为[1]；替换前已启动ordinal64 MOVE的臂为0/32。没有预算预留或事后移动触发点。早于SHIFT的干预不是漂移后的在线适应；训练多候选不能代替留出多源排序证据。MECHANISM_DIAGNOSTICS逐臂保留当前WAIT后同MOVE是否再查询，以及全部服务记录差异；SKIP_LIFETIMES给出实际physicalEND/acceptedEND和后继ID。

## 独立审计与边界

原Move3、World物理/几何/服务/FIFO/run loop和候选提取逐字不变；normalEND函数只在accepted公共END之后增加skip清除，另两处改动为query候选mask/安装，剩余修改限actor状态/评分及策略名称。原Geometry/Index/PositionCommit/ReferenceController、最多4承诺MOVE、cell访问依赖、N<=16 guard不变。R7/R8/R9冻结文件、9生产头、17作者对象、bridge/config及原地图场景SHA均复核。没有改原稿或入口README。

156臂通过独立70位Decimal物理、闭几何、owner、ADG和FIFO重放，逐候选复算24特征、两种动作的有理评分/同分、剩余预算和公开skip集合。98标签独立核对完整物理/公开前缀、同活pi0续策和精确目标；同首动作完整轨迹恒等对照44支。四头增广加权lstsq复拟合通过。14负控均拒绝，包括privateEND提前清除、漏清除、agent/action alias、SKIPscore、错误尾策略、遗漏候选、漏扣次数、未来头、证书/任务服务及WAIT同刻补查询。root另行复拟合/留出检查文件包含在交付。

初始native4后代峰RSS240259072字节，据测量root批准native6；probe峰592072704字节，auditor2、compile1。调度耗时只是宿主测量，未变成生产COST。一个外部隔离PID命名空间取样的零值明确标为无效，未用于资源批准。审计实现于初始registration之后、任何科学运行之前升级；AUDITOR_FREEZE_BEFORE_RUNS保留其独立冻结SHA，实验源未改。

raw分9个互斥压缩包，最大13,850,574字节，全部936成员逐SHA复核，每包<45MB；runs/build/cache和展开audits不进发表白名单。worker未执行Git，root负责审阅和发布。

本轮仅四个测试family、两张训练出现的图、N16和一次替换。IID/SHIFT相关，候选/机器人/primitive不是独立重复；次数容量不等于主线真实费用。作者OBJ3通过已承诺公开frontier适配，不声称作者全套物理重规划benchmark复现、外部baseline优越性或生产COST/AUTH。后续应先获得独立family中稳定的任务改进和有辨识力的合法机会，再讨论多次部署或更复杂模型。
