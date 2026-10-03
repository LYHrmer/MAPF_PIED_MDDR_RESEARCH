# R10 几何先验与在线历史归因

64 个预注册新留出全部完成。原 hm 为371任务，history、geometry、full均为363；本轮不支持学习带来吞吐优势。完整模型相对history仅在一个条件减少130个固定FIFO累计tick。在线历史在少数共同规划状态上确实改变动作，因此不是“模型未接通”，但这些局部作用没有增加任务数。

## 实现与冻结

两张原公开图，各四个全新FIFO family（961031–961034），nominal/axis，四策略，N8/H4000；八个独立map/task family，误差条件和策略为配对。原生本地ADG、控制器、半MOVE、正常STATION20、作者OBJ3和同一代价overlay全部不变。hm是作者接口基线，其他三个是内部消融，不能称发表方法。

几何ridge仍为14槽，但在训练与预测中将历史槽7–13置零，λ1、预处理规则、d0、裁剪、depth2、0.025代价系数不变。完整ridge直接保留冻结R9对象。训练只含同一R7 TRAIN的14,542条完成运动样本；CAL不选参；R9 TEST只用于提出这次归因假设。`DATA_ISOLATION.json`验证新种子与R7/R9不重叠。模型SHA256 `9222333ca80d7a2b119a9cd51ddfcb03ce74eabce8f411f2617a549f21819704`。1805个执行冻结项保持不变，未调整参数或增补测试臂。

## 任务与FIFO

|策略|任务数|固定前10 FIFO累计tick，缺失=4000|
|---|---:|---:|
|hm|371|4,449,470|
|history|363|4,456,952|
|geometry|363|4,456,942|
|full|363|4,456,822|

full相对history与geometry在16个配对条件的任务差全部0。相对history的−130tick只出现在random961031 axis；八family中1改善、7相同。相对geometry为−120tick，八family中2改善、5相同、1变差；family平均差−15tick，描述性bootstrap95%区间[−49.5,5.25]。相对hm，full少8任务，八family为5负、2零、1正，固定FIFO累计多7352tick。八family任务差均值−1，描述性区间[−2,0.125]；不能把16条件或64臂当独立样本。所有逐条件数据见`RESULTS.md`/`summary.csv`，配对区间与固定种子重采样见`summary.json`。

## 相同轨迹上的预测

在16条hm轨迹上复算同21,566条完成运动primitive，排除已知S20：

|指标，ticks|history|geometry|full|
|---|---:|---:|---:|
|MAE|1.272374|1.747198|1.454623|
|RMSE|2.938554|3.115338|2.915408|
|平均偏差，预测−D|−0.168042|0.287971|0.033349|
|95%绝对误差|8.081364|8.428303|7.776960|

full在12/12个primitive×方向运动组的MAE均差于history，但聚合RMSE、bias和尾误差略好；不能将其概括为所有精度指标都更差。按八family等权汇总的结论相同。`prediction_same_hm_traces.json`还给出逻辑步、方向、相关历史是否存在及family分层。只评价已完成样本；全64臂共1197个删失primitive保留。

目标D=E−max(A,Eprev)仍是公开下界后的完成时长。相同hm运动轨迹平均自身前序排队29.980618tick，proposal到admit6.555968tick；这些不属于D。`dependency_waits.json`另按原ADG重建关键跨机器人前驱等待与就绪后admit等待，仅作事后解释，未成为未来规划特征。

## 零历史与同状态因果干预

16个首次决策均为零历史，各候选无首步动作分叉。history与full只在random961031 axis首次动作分叉：tick3044，已有1033条完成历史，FIFO−130但任务不变。geometry与full在四个条件有后期分叉，详情见`decision_attribution.json`。代价排序只代表公开edge-duration启发项，不冒充作者内部完整动作评分。

`counterfactual_decisions.py`克隆作者bridge并精确重放full的全部request前缀，再在同一个公开frontier及同一持久状态上分别输入full、full-zero-history、geometry和history。36个目标的完整模型基准动作均精确复现；16个首决策、16个事后统一batch10探针都未因清零历史改变动作。四个分叉目标中三个发生full与zero-history动作差，分别为empty961033 nominal/t3435、random961031 axis/t3044、random961034 nominal/t1269。这是对当前动作的直接干预证据，不是未执行zero-history轨迹的任务收益证据。batch10为看过部分运行后加入的描述诊断，不列为事前主要结局，没有新增仿真或选参。

empty961033 axis的真实geometry/full在t3585存在动作分歧，但将geometry预测放入full持久状态时动作没有变化。两真实臂虽公开frontier、priority和search_order相同，历史代价输入不同；未导出的内部状态可能不同。因此该点不能只凭首动作分叉归因于当次预测，更不能把有历史量本身当成因果结论。

## 核验、失败和档案

64臂全部到H4000，原ADG、公开forecast与FIFO审计通过，64物理采样包络审计通过；最小中心距0.499217m，最大ACK端点误差0.029935m。独立算法重建旧TRAIN/CAL22,153标签和新86,985标签，公开特征差0；STATION D恒20。两个ridge用增广最小二乘重算，参数最大差9.24e−11以内。`INDEPENDENT_FIFO_REPLAY.json`不导入候选模块，由原始parsed/admit/END重新得到全部任务/FIFO总数。独立指计算途径独立，同一实施人员撰写，不伪装盲审。

初始四次socket PermissionError为启动失败、0决策，移至sandbox_attempt01后使用相同冻结输入获权限重试。68个逐运行gzip档案完整重解并核对每成员SHA；原始总量2,680,601,107bytes，压缩202,137,636bytes，最大单包3,374,044bytes。源码/许可证继承见`SOURCE_AND_LICENSE.md`，最终冻结核验与公共文件白名单见`FINAL_VERIFICATION.json`和`PUBLICATION_MEMBERS.json`。

本轮应收缩“更准预测提升LMAPF吞吐”的主张。模型改变少数决策是真实的，但完整时长投影本身把原有几何运动和已知服务也当作拥堵代价，三个预测版本一致劣于hm值得先检查这一接入方式。若开展修正，必须另建新协议、新family与新目录，保持本64臂冻结；不能事后把现有负结果调成正结果。正式多图/规模与作者统一比较仍未完成。
