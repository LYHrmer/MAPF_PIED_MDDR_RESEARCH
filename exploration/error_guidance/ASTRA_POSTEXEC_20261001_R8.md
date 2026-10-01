# Astra R8 非盲技术后评与下一方法定义

此判断形成于实现和审计之后，不替代此前独立预审，也不是下一轮事前注册。本次补充实际读取查询R8 CONTRACT、115条TRAIN_CAL_LABELS、标签复核器、tail_diagnostics和native特征/预算选择代码，以及第三线REPORT、label_shift、public_model和实际ADG/ExecutionManager代码。查询最终48个N16臂及12个N32兼容后继臂现已完成；已读取两份root独立审计，并从原生receipt重新汇总任务数、查询数及全部attempt。本文只作非盲后评，不据这些留出结果修改模型。本次只修改本文，没有新增native或改动封存实现。

## 主线：只推进当前最近一项

12臂、728费用段、792物理帧和18份ELF干净重编支持本轮有限案例闭环。下一项是把现有付费绑定SOURCE和guest资源事务扩展到前后车正常END、同一机器人连续两次MOVE及真实任务服务/新head，验证旧action迟到POSITION、resident与新demand交接；错误输入返回显式拒绝，补掉当前异常诊断进入RV fault的路径。保持原计费和物理合同，不先扩模型，不把rear fixture算作完整在线服务。跨通道AUTH END与当前registered direct SOURCE继续分开。

## 查询：把学习目标改成同一预算尾策略下的一次干预

完整结果明确显示：当前学习模型没有通过任务增益验证。下表“任务/查询”是各条件总和，查询数不是生产guest费用。

|集合|WAIT|RR|condition|paced_condition|history|nohistory|
|---|---:|---:|---:|---:|---:|---:|
|N16，8条件|346/0|350/128|350/128|344/120|345/122|345/122|
|N32，2图|171/0|170/32|170/32|169/32|166/32|168/32|

N16学习策略较同节拍规则多1任务，但较WAIT少1、较未节拍规则少5；history相对nohistory任务差为0。N32的history较WAIT少5、较同节拍规则少3、较nohistory少2。局部比较的+1不能写成已取得一般任务优势，固定前缀时间改善也不能抵消任务损失；结果不支持“公开历史学习已改善服务”或规模迁移优势。N16只有4个map/task家族，IID/SHIFT相关；N32只有2个world，不作总体显著性宣称。

运行账目为195次attempt=183成功+12原N32启动guard失败。原12次在robots≤16检查处拒绝，尚未物理运行，不计作0任务科学负例。独立scale_guard_successor唯一native改动是上限16→32；12份原输入、原模型SHA c7d744e6a5dce31c41cd458d5a6894a416388e7fab8cfda28d01dafab29e6004及原freeze保持。后继补足原登记的两个N32 world，不是额外12个独立测试；原失败全部保留。ROOT_HELDOUT_AUDIT与ROOT_SCALE_SUCCESSOR_AUDIT均PASS，后者与successor receipts相符。这证明执行/核账完成，不等于方法有效。

实际标签分布为train87条（73零、14正；任务差83零/4正），cal28条（25零、3正；任务差全部零）；115条没有负任务差，也没有负scalar advantage。当前样本不提供“何时有害”的监督证据。不能人为补负标签，也不能读取留出损失后筛选新训练状态。

R8确实计算了单次查询相对WAIT的优势，不是把WAIT伪造成全零特征；但其准确含义是

\[
A^{\mathrm{WAIT\ tail}}(h,a)=J_H(a\to\mathrm{WAIT\ forever})-J_H(\mathrm{WAIT\ forever}).
\]

部署却允许16次查询，并由公开时段给出累计4/8/12/16额度。这些策略在首次查询后会改变未来状态、候选、剩余预算与查询次序，因此上述标签不是部署策略的多次预算优势。单次查询非负不推出多次策略非负；增大相同标签数据量不能修正这个估计对象。代码中capacity和allowance仅作合法性门，原20维评分特征没有剩余预算、距H时长或剩余额度。

下一方法固定一个可执行且只读公开信息的尾策略π₀，首选原paced_condition；仍用相同预算16和节拍规则。令z=(h,b,t,c)，h为公开历史及已承诺frontier，b为剩余总预算，c为本时段尚可用额度，t为模型时间。最终效用保持R8任务优先的定义：J_H=N_H−F₄/(2HN·4+1)，F₄为固定首4项/agent的截尾完成时刻和。查询次数只作为预算与诊断；本线尚无生产COST，不能凭空扣成任务或声称净费用最优。

对同一真实前缀分别执行首行动a与一次WAIT，之后都执行冻结π₀到H：

\[
A^{\pi_0}(z,a)=\mathbb E[J_H(a\to\pi_0;z)-J_H(\mathrm{WAIT}_{once}\to\pi_0;z)],\qquad A^{\pi_0}(z,\mathrm{WAIT})=0.
\]

这里WAIT只放弃本次机会，从下一真实决策事件起恢复π₀，绝非之后永久WAIT。查询分支实际扣预算，WAIT分支保留；π₀读取各自自然演化的状态和预算，不强迫两个分支使用相同未来候选或同一查询名单。预算的机会成本已通过未来少一次可用查询进入标签，不另造惩罚权重。两分支重放同一前缀与预先固定的外生误差带，离线私有状态只用于反事实环境，不成为模型输入。响应过期、无收益、失败、尾部未完成均原样保留。

可执行的第一轮安排如下：

1. 用π₀完整训练运行收集其实际到达的z，事前按公开时间、预算区间和候选数抽机会；每个被选机会运行WAIT和全部合法query的同π₀尾部。完整记录未选机会，按world/family划分train/cal/test；候选行不充当独立world。
2. 沿用固定lambda1 ridge，不先更换网络。保留原20维并加入上述预算、剩余时长、节拍额度；输入只能取决策之前的公开信息。WAIT优势恒为0，预测正值才允许查询，等值WAIT。无历史消融仅移除同一历史字段；新旧标签对比须用相同预算尾部评估。
3. **首次验证只允许每episode一次学习替换。** 先运行π₀到一个事前按公开规则指定的机会（例如注册时段内第一非空合法机会），由冻结模型选择query或WAIT，然后永久恢复π₀。本episode仍可有π₀的多次预算查询，但学习只改一个决策；这与训练的尾部严格一致。对照完整π₀及在同一机会强制WAIT后回π₀，先评任务差，再评固定FIFO时间。
4. 若要在每个机会反复用模型，必须明确变成新策略π₁，重新采其训练状态，并以冻结π₁重做下一轮优势标签；每轮冻结后只用新留出评价。精确优势的策略改进直觉不为有限特征、有限样本回归提供保证。不能把A^{π₀}标签直接称为A^{π₁}，也不能把一次替换成功写成16次学习决策成功。

停止条件也明确：如果同尾策略配对仍几乎全零，或一次学习替换在新family无主任务优势，先报告信息价值稀疏/预测无效；不以更多正例采样或更复杂模型绕过这个事实。小的固定前缀时间改善不能抵消任务损失。本轮完整留出损失属于未来训练假设的动机，不是可回填的训练集。对齐续策价值目前仍是下一轮可证伪假设；这次负结果既不验证该新目标有效，也不允许用它改写R8原模型的失败结论。

## 第三线：先定义时间边界，再谈残差或占用

本轮hm global/local任务174/200，history及learned各177/201，学习的16个配对任务差均零。7/16动作分叉证明进入决策，不证明任务收益。label_shift在相同hm事件上显示global/local第一步实际平均残差−6.31/−3.68ticks，而历史均值+23.61/+16.11；第二步batch→END分别103.47/85.40ticks，被混入单步历史。这是目标污染。第1步learned MAE更差、第2步较好，不合并宣称改进。

源码给出的约束比笼统“ready→admit→END”更具体：ExecutionManager的admit发生于obtainActionsFromADG/getPlan，表示一组节点入队；ADG允许同机器人多个节点提前入队。因而本节点admit可能早于自己的前序节点END，不能把admit当control start，也不能要求全部type1/type2前序END先于admit。control phase=front是独立事件，目前只用于离线审计，不在PublicHistory公开输入白名单。

具体源码：第三线 `source_snapshot/server/src/ADG.cpp:424` 的getAvailableNodes从finished+1向后扫描，429行计算剩余队列容量，443行仅检查原有效入边/容量及新增global门，450—452行把未入队节点逐个追加；`ADG.cpp:576` 的getPlan在596行实际压入队列。`ExecutionManager.cpp:564—565`在getPlan返回后记录admit。原生反例来自主线ignored证据 `local_dependency_20261001_r8/runs/mechanical_mechanical_941800_nominal_global_hm/events.jsonl`：87行（tick10、seq86）同时admit机器人0的节点0(T)、1(M)、2(M)；节点0的accepted END在200行tick19，节点1在413行tick36，节点2在622行tick53。节点2的首次control front为414行tick36。因此对节点2，A=10，E_prev=36，B=36，E=53；队列驻留43ticks包含26ticks前缀，D仅17ticks。无需增加运行即可直接证伪admit等于control start或全部自身前序END先于admit。

下一版以原parser primitive节点v为监督单位，先保留节点身份、动作类型/几何、逻辑步和真实事件序列。定义以下边界；同tick用sequence判先后，时长仍以tick计：

- P_v：原proposal/parse公开绑定该节点的时刻。
- R_v：按原getAvailableNodes扫描语义，至v的队列前缀不再被有效type2入边阻塞的首次时刻；不包含容量上限或global附加门。它是可入队依赖下界，不要求自己的前序已END。当前没有ready事件字段，应从固定parser/ADG关系和accepted END因果重建并交叉核验，或新增只含这些公开事实的ready记录。
- A_v：实际admit事件；E_v：该节点唯一accepted normal END。
- B_v=max(A_v,E_{prev(v)})，其中prev为同机器人原FIFO直接前序；无前序使用已知初始边界。B是已入队且自身前序正常关闭的公开下界，仍不等于物理control start。

于是逐节点可检查

\[
E_v-P_v=(R_v-P_v)+(A_v-R_v)+(B_v-A_v)+(E_v-B_v).
\]

四项依次是原依赖等待、调度/容量等入队等待、自身队列前缀等待、前序关闭后的END时长。global门归第二项，不混入物理误差。首轮建议监督D_v=E_v−B_v，并按primitive类型/几何减去相同单位的nominal d₀(v)得到残差；它仍包含派发、暂停和停稳，名称不得写成纯电机误差。若只有A、E，则E−A只能称队列驻留时间，不能冒充D。原45+10·turn是整格步标尺，不可直接用于半格MOVE、ROTATE或STATION；STATION20tick单列作已知服务，不混训运动残差。

完成的D_v只有在其normal END已交付后才能进入后续历史。规划时预测特征冻结于P（或明确登记的规划调用时刻），不能使用本动作未来的R/A/B、结束时间或私有位姿。两步的实际朝向都使用已修正映射及对应虚拟frontier；未完成动作保留右删失，不能当完整时长或无理由删除。公开节点谱系/ready若需新增投影，只能来自已承诺计划与已交付ACK，须单独登记信息边界。

将primitive预测转换为整格边代价时，应按相同parser分解聚合D及明确的等待项；不能把累计batch→END或含前序排队的E−A再除一个nominal就叫occupancy。第一版可继续作为非负时长惩罚启发式，真实空间占用仍由原ADG及正常ACK决定。标签诊断中“第二步END减第一步MOVE END”也不自动等于D：它可能包含STATION、入队或外部依赖等待，必须先完成节点映射。

下一实验先用新的train/cal世界同时覆盖两步global/local，以相同公开事件集比较history与learned；检查四项逐节点非负及总时长守恒、跨步无前缀污染，再冻结同单位模型。为分离均值预测贡献，history/learned先共用一套预定校准余量，或把余量单独作因子，不能继续将不同余量的任务差全归给均值。最后在新family上保持执行接口相同，仅比较学习增量；批末屏障减少收益另列。

三线共同原则是先令监督对象、可见信息和实际决策作用一致。主线目前提供机制闭环；查询研究有限预算的证据价值；第三线提供正确的时间监督及可改变的调度决策。三者的收益不可相加归为“学习收益”。最终取舍是保留主线机制成果和第三线去附加全队门的执行成果，明确两条学习线尚无独立、稳定的主任务优势；下一步优先修正决策目标与时间单位，而非堆叠模型。

原始依据：[查询合同](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/stratified_value_20261001_r8/CONTRACT.md)、[查询标签](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/stratified_value_20261001_r8/TRAIN_CAL_LABELS.json)、[第三线报告](local_dependency_20261001_r8/REPORT.md)、[标签迁移诊断](local_dependency_20261001_r8/label_shift.json)。这些是下一轮方法定义的依据，不是已完成的验证。
