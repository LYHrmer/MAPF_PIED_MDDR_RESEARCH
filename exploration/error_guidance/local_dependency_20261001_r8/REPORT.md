# R8：两步缓冲内合法局部执行提高服务，校正学习模型尚无主任务优势

本轮完成 **6个机械关＋48个新留出原生运行**。48留出全部4000ticks（10Hz，400秒）、正常退出并通过完整事件审计。共享两步缓冲下，局部执行将原作者hm服务总数174提高到200；同历史规则与learned均177→201。收益来自共同执行接口，**learned相对同历史规则的任务优势仍为0**。学习差异真实进入作者搜索并在7/16个同执行条件配对中改变动作，但完成时间有正有负，局部执行下累计受限完成时间反而稍差。

## 合法接口与机械关

没有直接删除joint_settled。每次真实全队停稳后，以持久官方OBJ3依次产生两个联合步；第二次调用的起点是第一步已规划frontier，同一公开当前head不变。两步一次交给原parser/ADG，整批完成后才再次规划，因此只称“**两步缓冲内异步**”，不称无限局部在线规划。两臂共享该合同，global额外阻止逻辑时间1动作进入队列，直到本批时间0全部正常END；local保持原ADG admission/type2边/正常ACK。原S1控制器、半格MOVE端点、20tick STATION不变，没有重写在途action。

官方hm使用全部原OBJ3算法对象；候选只沿用R7非负边代价overlay。虚拟frontier不再被桥接器记为physical completed traffic；本轮固定OBJ3、input_type=flow，所有请求network_forward_calls均0。配置、原对象SHA与两份native修改在 [SOURCE_AND_LICENSE.md](SOURCE_AND_LICENSE.md)、[source_changes.json](source_changes.json)。global是内部额外门消融，不是重新声称复现原作者一步实验。

4agent机械由正式作者planner产生相同前两步。暂停agent0真实活动MOVE20ticks后，local独立agent2第二步实际control front=t53，早于agent0第一整格正常END=t73；global独立第二步到t80才放行。依赖agent1第一整格后半MOVE在前驱半MOVE END56之后admit60；第二步两段分别在原前驱END73之后admit80、前驱END90之后同tick较晚事件admit90。没有用预测时间解除真实依赖。无扰动对照和两个“第一步即到goal”的补充机械均通过：每head只在首次goal点标一次，原多点parser产生唯一STATION，实际完整驻留20ticks且正常END后才发布后续FIFO。6机械总任务只是机制数据，不作为留出学习收益。

## 事前发现朝向bug，重建原训练数据并实际拟合

源码核验发现LSMART公开朝向是E,N,W,S，而规划动作编号是E,S,W,N；R7 quarter-turn直接相减的语义错误会污染残差和历史。R8在任何留出前修正转换，仅读原R7 **12个train＋6个cal** 公共事件，重新因果构造全部特征/残差，再按原lambda1、未惩罚截距和train-only标准化重拟合。没有读取R7test，也没有新增native训练或按R8test调参。

6062训练标签、3010校准标签及94删失全部保留。校准MAE同历史5.24572ticks、learned4.18620；各自90%绝对余量10.0、8.66999。新checkpoint SHA `9af5824e879761a2cd4fbb435533830ca63fca9b61c5e973e01bc75cd7790669`；旧R7checkpoint以诊断备份保留。root不导入候选builder，从原公共事件独立以几何向量重算转角和历史、增广最小二乘拟合，最大权重差2.40e−12；见 [ROOT_MODEL_REFIT_AUDIT.json](ROOT_MODEL_REFIT_AUDIT.json)。这是复用旧数据的语义修正拟合，不能写成新训练场景证据。

## 48留出结果

两张公开地图、原scenario起点、8机器人；新独立任务种子941821/941822，nominal/axis成对；global/local×hm/history/learned，共48臂。完整1002项/agent FIFO在运行前固定，未来head不公开。仅有4个map/task家族；误差条件与策略配对相关，不能把48臂当48个独立world做总体显著性宣称。

|执行|hm任务|history任务|learned任务|hm固定前10时间和|history时间和|learned时间和|
|---|---:|---:|---:|---:|---:|---:|
|global|174|177|177|2,230,276|2,230,630|2,229,594|
|local|200|201|201|2,195,952|2,199,444|2,199,542|

时间和按每agent最初10项事前FIFO任务：实际normal STATION END tick，未完成一律4000；每个执行/策略合计640项。它是固定集合的受限绝对完成时刻，不是动态released-flow。local较global完成任务分别多26/24/24；learned较history的固定时间和global少1036ticks，local反多98ticks。local候选虽然多完成1项，却分别比hm多3492/3590ticks，不能隐去副指标代价。[逐臂LF CSV](summary.csv)、[全部正零负配对与交互](summary.json)保留完整结果。

|地图/种子/条件|global hm/hist/learned|local hm/hist/learned|
|---|---|---|
|empty 941821 nominal|22/22/22|25/25/25|
|empty 941821 axis|21/21/21|22/22/22|
|empty 941822 nominal|22/24/24|25/26/26|
|empty 941822 axis|21/21/21|24/24/24|
|random 941821 nominal|22/23/23|28/28/28|
|random 941821 axis|21/22/22|28/28/28|
|random 941822 nominal|23/22/22|24/24/24|
|random 941822 axis|22/22/22|24/24/24|

learned/history在7/16条件出现首次真实动作分叉，分叉前actual view、完整snapshot及同逻辑步frontier全部相同；其余9条件无动作分叉。首分叉tick与每项服务正/零/负差均在summary。history与learned还使用各自校准余量，差异不能单独归因预测均值。root独立重建全部type2边与正常ACK顺序，local在其他机器人第一步未END时第二步admit数hm/history/learned为5359/5337/5308，global均0；见 [ROOT_EXECUTION_AUDIT.json](ROOT_EXECUTION_AUDIT.json)。这证明放开的确是缓冲内机会，不能把它归功于学习。

## 累计标签迁移是本轮明确缺陷

训练标签来自单步proposal→final MOVE END；R8第二步记录的是**整批proposal→第二步END**，包含前步执行/依赖等待，却继续进入单步history并映射为occupancy ratio。该迁移已事前登记，本轮没有事后改指标或再训练；它仍是需要下一轮纠正的模型单位问题，不能用“迁移”掩盖。

[事后标签诊断](label_shift.json)在同一组16个hm运行的事件上同时评价两个预测器，避免各候选轨迹不同造成评分数据不一致：

|执行/步|标签数|平均batch→END|history MAE|learned MAE|
|---|---:|---:|---:|---:|
|global第1步|2097|43.04|22.47|24.00|
|global第2步|1984|103.47|39.12|37.14|
|local第1步|2286|45.73|15.20|15.80|
|local第2步|2176|85.40|26.08|24.67|

第1步learned更差、第2步较好；不合并总MAE来宣称改善。global第1步实际平均残差−6.31ticks，输入近期历史平均残差却+23.61；local对应−3.68与+16.11，反映累计第二步标签混入历史。另列减去前步MOVE END的事后持续时间，未喂入actor。下一设计应统一“每步就绪/准入→END”的监督单位，并单独建模调度等待，再用全新训练/留出验证，不能继续利用本批test调模型。

## 审计、费用与归档

54最终运行原parser完整分解、逐node admission、全部原ADG前驱正常ACK、端点、FIFO、唯一任务/20tick服务、因果public history与预测请求绑定均PASS；7个故意错误负控全部拒绝。54运行1,543,200个物理采样按0.095036758m圆包络复核，最小机器人gap0.292789727m、障碍gap0.371457201m；最大ACK端点误差0.029776579m，原EPS0.03m不变。仅证明采样时刻分离，不称连续子步/contact安全。

1,536,000个留出agent-tick完整守恒。hm global额外全队门29,511ticks、批末共同等待32,069；local额外门0但批末等待50,632。原ADG依赖global210/local389。局部接口仍有明显批末屏障，[等待分解](wait_accounting_test.json)不会把全部空闲当依赖延迟。队列活跃、派发等待、停稳和全空边界分别统计；这些是日志观察时刻分类，不是实时硬件测量。

8world规划请求wall：hm global/local0.383/0.418秒；history1.784/1.945、learned1.802/1.892秒。候选公开历史预测/BFS代价构造另耗global约10.01/10.06秒、local10.49/10.59秒；Python事件投影/日志不在这两个子计时内。并发整进程wall不用于算法加速论点。

13个前置尝试保留：1次沙箱socket拒绝零decision；4次可变request日志绑定被独立审计拒绝；4次公开朝向/多步重建预检纠正前运行；4次转角重拟合前机械label记录。它们不是被删除的科学负例，均独立归档。最终54＋前置13共67原始包，1,886,954,218B压缩为143,463,955B，最大3,144,021B；逐成员回读SHA全通过。1549项执行冻结最终逐字不变；源码/native二进制另打包，外部官方对象、原train/cal和动态运行依赖仍按路径/SHA引用，不声称无依赖容器。

本轮获得了合法缓冲内局部执行的真实服务改善，并定位了两个可操作的学习语义问题；尚未获得独立于共同执行接口、优于同历史规则的学习主任务优势，也没有据此宣称世界模型或执行协调新颖性。
