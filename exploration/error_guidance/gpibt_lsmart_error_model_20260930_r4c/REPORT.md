# R4c：真实预测改变动作与任务时刻，未出现学习优势

36/36事前固定run完成800ticks、10Hz，全部native退出0，没有重试、删run或延长窗口。旧R4四十run零动作结果、R4b真实校准gate失败保持独立冻结。本包在预先设计的合法可达FIFO机制中，第一次完成本world已交付执行历史→冻结模型→共同priority接口→官方GPIBT动作→LSMART真实执行/ACK/任务服务时刻的作用链。它是5×5、两机器人机制实验，不能承担标准规模MAPF性能或泛化结论。

模型完全沿用旧R4真实训练的λ1 ridge residual，102 train/48 cal完整运动段样本，SHA `16fac44d6d23c7c472a5caed4bdce87ba19bca632e6a70f7fa16a9ccf14c8094`。没有本轮训练或test调优。六condition×六policy固定执行；三预测共用rank差<1tick归零、否则较长者+1较短者−1，同信息入口相同。zero是共同adapter内部reference，analytic/history和两种常量优先级是内部消融；不能称其为已发表外部baseline，也不能称加了priority adapter的planner为未经干预的原始GPIBT。

|条件|各六臂相同真实服务数|learned首次动作差tick|agent0第三服务 zero→learned|全部匹配服务：提前/相同/延迟|
|---|---:|---:|---|---|
|nominal|10|无|404→404|0/10/0|
|slow065|8|333|528→540 (+12)|0/5/3|
|slow085|9|297|475→461 (−14)|2/6/1|
|axis|9|273|445→460 (+15)|1/6/2|
|unknown_pause|10|无|424→424|0/10/0|
|unknown_shift|7|351|567→568 (+1)|0/6/1|

服务数取实际正常STATION END，非稍后bookkeeping；部分末任务已服务但尚未登记，旧stats字段会少1，不代表臂间吞吐下降。表中时间单位为tick=0.1s，仅机制里程碑；全部owner/FIFO ordinal匹配服务、删失、末pending均保留在`summary.json`。主要任务完成数没有改善，变化有利也有害，不提供统计显著性或总体学习收益结论。

四个作用条件均在proposal index4首次出现动作差，此前完整公开view、snapshot和动作前缀一致。此时starts=[10,6]、当前goals=[21,7]，zero动作[D,E]走[15,7]，learned动作[E,E]走[11,7]。原effective priorities=[2.333333333333333,2.6666666666666665]；真实历史预测给bias=[+1,−1]，实际search order由[1,0]变[0,1]，plan后p/p_copy扣回bias并保持原aging。`summary.conditions.<condition>.comparisons_to_zero.learned.first_actual_action_difference`给完整public view、预测、历史、priority与原native proposal。动作随后真实解析为ADG节点并由控制器完成正常ACK、20tick驻留服务，改变了上表服务时刻。

协议预设的第三请求（index2，回到原起点后同时公开21/7）确有每agent两次正常MOVE/服务形成历史，并有共享cell5的目标递减候选；持久官方guidance已选[D,E]避开这个冲突，实际三预测动作仍等于zero。不能把这个初始请求当成功作用点；真实变化出现在后续index4。旧失败probe没有被覆盖为成功。

analytic、history、learned在全部六条件的完整动作和实际END流均相同；四个作用条件的fixed_agent0也复现主要服务时刻。因此本包证明合法残差信息能进入真实动作，不证明ridge优于强历史、解析或固定偏好。fixed_agent0在nominal/pause有额外更早里程碑（agent0第三服务396/416，zero404/424）；fixed_agent1在部分条件有延迟，全部结果照录。unknown_pause首次真实活动MOVE后连续20tick抑制已执行，预测没有读取未来暂停时长；这个条件最终仍无预测动作效果。

36run独立原生链审计通过，包括原parser/ADG、task owner/id、原ACK谓词、正常整格END、20次timer decrement/21次驻留采样、停稳view、800tick/1600pose与实际轮速、forecast截断、bias绑定及p/p_copy恢复；108篡改负例拒绝。全体最终整格MOVE END点误差最大0.029976787m。8/36run各1个中间半MOVE ACK点距离≥0.03m，最大0.032852674m；作者合并on-the-fly径向ACK谓词仍成立，该更严格点指标失败单列于`audit.json`，没有改变阈值、伪造END或隐藏失败。全体最小采样中心距离0.960761059m；采样中心距不证明连续足迹安全，RPC在线伪END拒绝也未建立。

数据独立复核通过：942个原整格MOVE行=884正常END+58删失，57,378个tick合法输入和offline未来target分文件。监督仍first_nonzero_MOVE→whole_END，排除前置转向/派发，额外总占用诊断保留；活动tick输入未用于mid-MOVE规划。具体合法可见性和各对照实际使用哪些量见`DATA_SCOPE.md`。

唯一新作者源码改动是OneGoalTaskAssigner的FIFO环境适配：复用作者task_file解析器，在非random_task时取front/pop返回location，原Task构造负责id/owner；未来66项/agent环境私有，actor只见当前goal。任务前缀agent0为5→0→21→0…，agent1为15→10→7→10…，seed62；GPIBT初始化seed42，搜索14个官方对象、group2、bridge、控制器二进制与旧R4完全相同。两次Release CMake configure/build退出0，18 binary/object身份、唯一源码patch/snapshot/tree manifest、两个原MIT LICENSE均在包内。`ready_for_trial.json`在任何native前冻结模型、参数、任务、地图、runner和源码身份；每receipt核同一身份。父包47/69/40run和R4b失败证据由完整manifest链保持。

本轮没有再启动实验。下一主证据需要公开地图、密度/agent梯度、固定相同任务流与执行误差时间预算，以及发表GPIBT/OnlineGGO经共同执行接口的比较；定制两机器人机制场景和学习priority本身不够构成论文创新或主要性能证据。该后续范围属于另立协议，不能据当前24/36臂结果事后挑seed、调幅值或选择有利指标。
