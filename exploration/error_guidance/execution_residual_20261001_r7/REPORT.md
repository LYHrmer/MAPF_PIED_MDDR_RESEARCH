# R7：真实执行残差学习进入作者引导边代价，尚无任务完成优势

本轮完成 **18 组新训练/校准原生执行和 24 组冻结留出执行**，全部实际运行4000 ticks（10 Hz，400秒）、正常退出并通过完整动作/ACK/FIFO审计。新ridge由真实正常END耗时训练；相对使用相同历史的非学习规则，它在4/6留出world改变实际动作，并在一个world改变真实服务时刻。但learned与history都完成119项任务，原作者hm+GPIBT完成120项；尚无学习提高任务完成数的证据。所有失败、零差异和负结果均保留。

旧R6c的24组完整日志先做了逐agent-tick分解，**2,304,000个时刻全部守恒**。MOVE控制1,223,748、TURN控制193,297、STATION控制28,600、全队屏障空闲613,140（26.61%）、原ADG依赖等待2,531（0.110%）、派发等待97,431、物理停稳70,121、全空规划边界74,972、活动暂停160。依赖由原一整步parser时间与ADG type-2规则重建，逐个真实admit核对前驱已END。队列空闲与尚未物理停稳分列；轮速内部量没有当成实测刚体速度。这个结果说明当前接口主要等待来自全队屏障，不能把所有空闲算作局部依赖延迟。[逐agent台账](r6_agent_tick_accounting.csv)、[诊断重建](r6_diagnosis.json)保存全部项。

候选保留共同S1、原正常ACK、20tick STATION、current-head/FIFO和joint-settled接口，只在作者OBJ3搜索边代价加一个非负项。actor仅用当前公开任务/网格状态和已交付proposal、admit、正常END；进入模型之前丢弃全部observation/control。标签为最终整格MOVE的正常END tick减proposal tick，**包括派发、依赖等待、转弯和两段半MOVE，排除随后STATION驻留**；因此这是发出动作到完成的耗时残差，不能改称私有运动进度或纯电机误差。

原OBJ3 hm+GPIBT、OBJ4 OnlineGGO均调用同一正式作者版本 `ff6d830e` 的原对象与R6c桥接器；OBJ4仍是旧sortation、200候选缩短训练的560权重，不代表完整发表训练的最强模型。history/learned是新的引导代价扩展，属于探索候选/消融；新search.cpp对象有明确patch，未冒称算法完全没改。[正式OnlineGGO论文](https://ojs.aaai.org/index.php/AAAI/article/view/33614)、[源码与许可证身份](SOURCE_AND_LICENSE.md)、[构建/对象绑定](candidate_identity.json)可追溯。没有复用R4的priority偏置。

新任务流种子为训练931701/931702、校准931711、测试931721，整run隔离，第一目标也重新事前生成。两张公开地图沿用原官方起点；均为8机器人、400秒，不能称跨新地图验证。训练/校准各含nominal、slow065、axis；留出含nominal、axis、unknown_shift。误差来自原确定性执行器，不虚构随机error seed。所有方法共享同world完整FIFO。未知shift仍是原活动MOVE后agent0轮速×0.55的明确条件，没有向actor提供条件名。

实际训练有6062完整标签、校准3010标签；94个未完成MOVE保留。λ=1 ridge、训练均值/尺度、未惩罚截距、特征和[代价映射](PROTOCOL.md)事前固定，未按test放大代价。预测持续时间加各自校准90%绝对误差余量，除以名义45+10×转弯次数ticks，得到无量纲比；按两跳公开最短路投影、1与1/2折扣加入其他机器人的占用代价，自身投影排除。原作者何时更新guidance保持不变。校准余量是经验保护量，不宣称时间相关/shift下的分布无关覆盖保证。

|预测数据与指标|同历史history|learned|
|---|---:|---:|
|校准3010标签 MAE / ticks|9.36596|6.82858|
|校准 RMSE / ticks|11.66980|8.70856|
|校准90%绝对误差余量 / ticks|19.50000|14.49356|
|六个原hm测试world同2904标签 MAE / ticks|9.38596|6.89690|
|同2904标签 RMSE / ticks|11.82417|8.95368|
|同2904标签落在各自余量内|89.084%|89.394%|

[模型冻结](model_freeze.json)SHA为 `15f3d3042a71c9b851d9e6b0ade27318748abddcbea47f2f2718533bfb57b2b3`，在任何test前完成。root另从18份public_events独立重建9072完整/94删失、因果特征与增广最小二乘，最大系数差约2.55e−11。[独立模型审计](ROOT_MODEL_AUDIT.json)没有导入候选特征/拟合函数。

校准的前4个公开head变化状态×6run，共24状态，零代价overlay均与原OBJ3的动作/priority完全一致。history/learned各在12状态改变作者动作，实际非零边调用225/219，但二者在这24状态动作相同。该检查只执行一个候选调用，不伪造候选的物理续跑；未据此改参数。[校准敏感性](calibration_sensitivity.json)保留全部零结果。

|留出world|原hm OBJ3|旧OBJ4|history|learned|learned/history首次动作分叉tick|
|---|---:|---:|---:|---:|---:|
|empty nominal|25|20|25|25|无|
|empty axis|23|19|22|22|2023|
|empty unknown_shift|17|15|17|17|无|
|random nominal|21|17|21|21|3059|
|random axis|19|16|19|19|3249|
|random unknown_shift|15|13|15|15|3935|
|合计|120|100|119|119|4/6 world|

数字均为正常STATION END。4个学习/同历史动作分叉前的公开view和完整snapshot相同；实际边代价非零调用learned520、history518。相对原hm的首次动作变化均在本world历史尚空的index0，因此这部分主要来自新增公共占用代价和离线先验，不能归功于本world的历史学习。learned与history的差别还包含各自校准余量，当前不能单独归因于预测均值。

empty-axis的22项共同已服务FIFO任务中，learned使8项提前、12项相同、2项延后，完整完成时刻之和 **47,940→47,798 ticks（累计净减142 ticks，即14.2秒）**。两项延迟各10ticks，八项提前分别20、20、10、50、10、20、20、12ticks。另三个动作分叉world的全部共同已服务时刻仍相同，尾部差异尚未传播到服务；没有延长时域挑收益。[summary.json](summary.json)按owner/FIFO ordinal列出所有正/零/负差。

为完整呈现配对时间结果，事后补充一个**探索性**指标：全部8×1002=8016项事前FIFO任务的受限完成时刻和，每项正常服务取实际tick，未完成或尚未公开均取4000。它不是预注册主指标，也不是released-flow，绝大多数项被删失，因此不报告夸张百分比。

|world|history受限tick和|learned受限tick和|learned−history|learned−原hm|
|---|---:|---:|---:|---:|
|empty nominal|32021226|32021226|0|−180|
|empty axis|32023940|32023798|−142|+460|
|empty unknown_shift|32033694|32033694|0|−46|
|random nominal|32029728|32029728|0|+367|
|random axis|32032714|32032714|0|+425|
|random unknown_shift|32039185|32039185|0|+281|

六world相对原hm累计多1307ticks；不能只报告empty-axis相对history的有利时间差。测试各臂仍有48个已公开未服务head；未完成MOVE数量分别34/38/21/21。每张地图只有一个新task seed，扰动之间共享任务，不能把6条件当成6个独立任务种子做总体优越性统计。

六world累计规划请求wall为hm 0.28429秒、OBJ4 0.45573秒、history 1.07763秒、learned 1.09483秒；候选预测/BFS/代价图构造另耗history 5.12877秒、learned 5.11443秒，分别369请求。约13.9ms的候选构造包含Python与BFS，并非纯ridge乘加耗时。公开事件投影与日志写入未纳入这两个子计时，但纳入整进程wall；两进程并发的整进程wall不作为算法加速证据。[逐run汇总](summary.csv)保留全部计时口径。

42run通过原parser/顶点交换/ADG、正常ACK、当前点端点、FIFO、真实服务、因果历史与预测请求绑定。最大ACK端点误差0.02992318m，原EPS=0.03m未改变。1,344,000个物理采样以半径0.095036758m圆包络复核，最小机器人间gap0.30354910m、障碍gap0.37115540m；全部采样分离，未宣称连续子步/contact安全。训练/test冻结146/152项最终SHA全一致。

最初18次沙箱socket拒绝均0decision，原回执和日志保留；权限恢复后同合同完成，没有删科学失败或重选样本。全部512个原始/失败/候选native文件共1,502,156,755 bytes，压缩为118,236,880 bytes，最大单包11,761,349 bytes；逐成员回读SHA全部通过。[归档清单](archive_manifest.json)可核验。源码/输入/独立root审计另打包；继承的外部native依赖仍按路径和SHA引用，不冒称已提供无依赖容器。

本轮得到的是“新训练改善耗时预测，模型差异可进入正式作者引导并改变真实动作/局部服务时刻”的闭环；主要任务完成尚未胜过同历史规则或原hm。下一步优先检验全队屏障下的机会损失，保持此checkpoint与全部负结果，不再按本批test调整尺度或堆网络。
