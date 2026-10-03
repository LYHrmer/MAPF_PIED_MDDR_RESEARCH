# R9：修正 primitive 时长后，出现一个条件的任务正信号，预测 MAE 未改善

本轮完成6个机械关与24个新种子原生留出，全部正常退出并通过事件、原ADG、正常服务和物理采样审计。相同 local 执行接口下，原作者hm、同历史规则、learned分别完成 **184、186、188任务**。learned相对history的2任务增量全部来自random图951922 nominal；其余7个条件任务差为0。这个有限正信号值得保留，尚不构成稳定跨场景学习优势。两步和全部运动类型上，learned的同轨迹时长MAE均较history差，不能把服务改善解释成预测更准。

## 正确时间边界已实际落地

每个原parser节点记录公开proposal P、实际admit A、自身直接前序accepted END Eprev及本节点END E，定义B=max(A,Eprev)、D=E−B。D包含派发及暂停，不称电机时间。首节点Eprev=0；同tick按sequence验证因果。完成D仅在正常END已交付后进入history；特征在P冻结，禁止未来admit/END、私有control front、位姿或隐藏误差条件。

R9机械重现了R8反例：robot0 node2的nominal A=10、Eprev=36、E=53，D=17，而队列驻留E−A=43。真实暂停前一MOVE20ticks后，该节点A=10、Eprev=56、E=73，D仍17；停顿保留在其实际作用的前一primitive。未增加ready trace，因此仅报告A−P、B−A、D与总时长守恒；A−P不能解释成纯ADG依赖等待。

按原parser区分第一半格MOVE、第二半格MOVE、每个90度TURN、STATION。整格预测由实际转向节点＋两半MOVE相加，首次到当前head时另加20tick STATION。两步路径投影传播对应朝向，以其他机器人投影的预测ticks乘固定0.025 author-objective单位/tick形成非负边代价。此量是时长加权启发式，不是物理占用；没有旧45+10turn名义分母，也没有用预测释放资源。history与learned共用0tick余量，模型差异不再混入不同校准余量。

## 复用独立训练数据，实际重新拟合

只读取原R7的12 TRAIN＋6 CAL完整运行，原始公开事件和raw parser/accepted END均可重建。TRAIN为14,774个完整节点，其中运动14,542；CAL为7,379完整节点，其中运动7,252；另保留161个删失节点，包括未admit节点。没有读取R7 TEST或R8 TEST拟合；没有新增训练物理运行。d0由TRAIN中位数固定为半MOVE17/17、TURN9，STATION20单列不混训。

history使用同类型/几何/方向池及自身近期历史的收缩均值；ridge使用同一公开信息，lambda1、TRAIN标准化和未惩罚截距。CAL运动MAE为history1.38516、learned1.40756ticks，RMSE为2.99606、2.87081。未据CAL调部署参数。checkpoint SHA为`415b905515d034e628e79a6f26bb1b3de8d0282906ca64ae3b33f8756ddb95d7`。

不导入候选builder的独立脚本从raw逐节点重建22,153个TRAIN/CAL标签及特征，特征最大差0，增广最小二乘与正式拟合最大系数差9.23e−11。12,919个节点有admit后的自身前序等待。另从30个新运行独立重建33,076个完整标签和全部特征，差0；26,017个节点存在自身前缀等待，STATION D始终20。见[独立拟合](INDEPENDENT_REFIT.json)、[独立新运行标签](INDEPENDENT_LIVE_LABELS.json)。完整节点拟合有完成条件选择，未用删失填值假装生存分析。

根审另以独立脚本直接读24份留出原始events，复算原生parsed/admit/END节点标签、当前head FIFO和20tick服务，未导入候选模块；184/186/188及全部固定FIFO时间和一致，见[ROOT_REPLAY.json](ROOT_REPLAY.json)。

## 留出服务结果

两公开地图、作者scenario起点、N8、新任务种子951921/951922，nominal/axis配对；仅local×hm/history/learned共24运行，每个4000ticks、10Hz。每agent1002项FIFO事前固定，未来head不公开。只有4个map/task family，不能将24臂当24独立world作显著性宣称。

|策略|正常任务END数|固定前10项FIFO受限时间和|作者搜索wall(s)|公开预测/代价构造wall(s)|
|---|---:|---:|---:|---:|
|hm|184|2,233,212|0.424|0.0002|
|history|186|2,237,230|1.695|16.398|
|learned|188|2,232,200|1.767|17.708|

固定集合每策略640项，完成取正常STATION END绝对tick，未完成=4000。learned比history多2任务、时间和少5030ticks；比hm多4任务、时间和少1012ticks。history虽然比hm多2任务，时间和反而多4018ticks。作者搜索与Python预测是分列子计时，不含所有投影/日志开销；并发整进程wall不用作算法加速论点。

|地图/seed/条件|hm/history/learned任务|learned−history固定时间|
|---|---|---:|
|empty951921 nominal|25/26/26|0|
|empty951921 axis|25/25/25|0|
|empty951922 nominal|23/23/23|0|
|empty951922 axis|23/23/23|0|
|random951921 nominal|22/23/23|−1764|
|random951921 axis|22/22/22|−1216|
|random951922 nominal|22/22/24|−1756|
|random951922 axis|22/22/22|−294|

5/8条件有history/learned实际动作分叉，首次分叉前snapshot/view/frontier均相同。random951921两条件在tick1即分叉：完成在线history为0，全部history计数特征均0。例如初始北向机器人预测向东的T+M+M，history为43ticks，learned为45.26791；向南两T+M+M为52与56.85517。这个最早差异来自离线拟合的几何/方向先验及代价形状，不能称在线误差适应。random951922两条件首次分叉时都有427条合法已交付历史，仍不能仅凭“存在历史”证明历史贡献。尚未运行冻结几何先验与在线历史消融，不能区分其任务贡献。[全部首次分叉特征、分方向bias](bias_and_divergence.json)保留完整证据。

## 同轨迹预测反证与边界

在相同8个hm留出轨迹上评价两预测器，避免不同候选轨迹混淆。第一逻辑步运动D均值16.5504，history/learned MAE1.29392/1.48518；第二步D均值16.7027，MAE1.22478/1.38349。第一/第二半MOVE均值在两步中分别约16.96/17.30，旧累计第二步污染已消除；第二步自身排队均值约49.98ticks被明确留在B−A中。

逐primitive×方向12个运动组的learned MAE都高于history。第二半MOVE朝东/西的真D都为17，history MAE为0，learned为0.28411/0.25527；TURN向东/南/西的learned平均bias较history接近0，但绝对误差仍更大，向北bias反由−0.54344变+0.93985。不能选择RMSE或少数bias改善宣称整体时长精度优势。模型可能改变路径权重并在一个条件改善任务，但“误差预测准确→任务改善”的解释尚未成立。

机械pause为额外保留的负例：hm5任务，history/learned各4；机械nominal均5，不并入留出总量，也未用机械结果调参。完整配对、共同已服务任务更早/相同/更晚均在[summary](summary.json)，不隐去单任务延迟。

## 安全、来源和归档

30个最终运行完整验证原parser分解、原ADG type2前驱accepted END、admit与自身FIFO前序、正常ACK端点、任务FIFO、唯一任务与20tick服务、预测公开信息绑定；原安全层和承诺不改。266条原ADG边被审计。7个执行负控和4个标签负控全部拒绝，另明确检测队列驻留误作D。775,200个物理采样按0.095036758m圆包络复核，最小机器人gap0.324156604m、障碍gap0.373105292m；最大ACK端点误差0.029943107m，原EPS0.03不变。只验证采样时刻分离，不称连续子步/contact安全。

原生源码/二进制与R8逐字相同，未编译，执行local。官方LSMART/OnlineGGO commit、MIT许可、原对象和父代source archive均可核；hm保持作者OBJ3，两个候选共用原overlay接口，不自造外部baseline。1634项执行冻结终检逐字不变。首次沙箱socket拒绝产生4个零decision启动失败，单独保留，不作为0任务科学负例。30最终＋4启动失败共34包，原始1,000,300,591B压缩为76,414,594B，最大3,368,231B，所有tar成员逐字回读SHA通过。仍依赖父代官方对象/原始TRAIN/CAL及本机模拟依赖，不声称无依赖容器。

本轮可靠成果是正确的primitive监督与可复核部署，以及一个条件的实际任务正信号。下一验证应先区分静态几何先验、在线历史、方向/turn机制与模型代价效应，再决定学习贡献；不能继续扩网络来替代这一归因检验，也不能把R9的有限结果包装为正式可投稿结论。
