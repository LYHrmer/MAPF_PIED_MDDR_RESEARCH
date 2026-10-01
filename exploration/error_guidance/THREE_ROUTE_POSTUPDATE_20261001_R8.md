# R8三线实绩、两类判断与下一步

本轮由实际指定的GPT-6-Astra/ultra子智能体、按research-mentor技能工作的科研导师子智能体分别先读R7证据并独立预审，随后分工实施；第三个子智能体推进查询学习，root另作独立数值/事件审计。预审互不先读结论；实施后评已接触实验结果，明确为非盲复盘。没有将主智能体身份或普通子智能体伪称为Astra。

我的推进建议是：**主线与查询价值学习并行，第三线继续作为误差建模与执行接口的备选方向。** 学习值得继续，但应解决“有限预算内向谁、何时取得有用进度证据”这个任务问题。当前两种已训练模型都还没有稳定超越同信息规则，不能因加入模型就增加论文创新项。

## 两类判断分别是什么

- [Astra独立预审](ASTRA_PREEXEC_20261001_R8.md)优先补主线普通END、过期查询与WAIT计费，再扩大查询价值数据，第三线先开放合法局部执行机会。[实施后的技术复判](ASTRA_POSTEXEC_20261001_R8.md)进一步指出：单次查询后始终等待的监督目标不等于多次有预算部署的价值；原ADG提前入队也使admit→END不能直接当单步运动时间。
- [科研导师独立预审](MENTOR_PREEXEC_20261001_R8.md)要求先建立作者工件、真实服务和内部消融的可比关系，再判断学习贡献。[实施后的导师复判](MENTOR_POSTUPDATE_20261001_R8.md)将论文贡献集中到明确的问题、合法信息和任务收益；不把三线拼成一个模块堆叠的总包，也不把工程闭环直接当整体性能优势。

两个判断都支持继续实现；区别是Astra侧重机制与测量定义，导师侧重论文论证、外部基线及证据能支持的主张。SCI二区/三区是目标，需要创新机制与有说服力的完整比较共同支撑，不能由工具调用量、训练次数或分支数量推定。

## 主线：普通END与真实付费闭环已完成

本机证据：[完整报告](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/normal_end_lifecycle_20261001_r8/REPORT.md)、[交接](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/normal_end_lifecycle_20261001_r8/HANDOFF.json)、[root独立复核](/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/R8_MAIN_ROOT_VERIFY.json)。按现有仓库范围，主线实现保留在本地忽略目录，公共main只更新四份入口文档。

新增Center Business绑定的普通END SOURCE，guest付费读取原历史、重放原控制器、核对身份及真实终点零速度，再提交原PositionCommit生命周期并放行后车。它是registered direct SOURCE；跨通道AUTH END并未冒称已实现。

|前车长度|后车RUN时刻 WAIT / paid|fixture服务时刻和 WAIT / paid|Natural完整guest费用 WAIT / paid|
|---|---:|---:|---:|
|3|3 / 3|10 / 10|49,687,854 / 138,931,620|
|12|6 / 6|16 / 16|67,774,408 / 168,450,776|
|27|9 / 6|22 / 19|111,707,051 / 221,131,986|

三输入×WAIT/paid×Natural/Strict共12臂全部完成，728段完整核账。短输入END先到，迟到POSITION不更新root、不产生成功receipt，四个真实费用terminal仍结清；中输入保留已成立的POSITION成功事实，同刻END优先；长输入仍在前车未闭合时提前放行3个模型时间单位。成功receipt和下一选择调用完成不等于断言下一选择有可用quote。

792个物理帧、715项父文件、18份ELF及逐费用段均核验；隔离全量重编18/18逐字节一致。错误身份/未闭合SOURCE无提交，重复END在全部正式guest中无副作用。前两负控的异常诊断仍进入fail-stop，尚非可恢复错误路径。

下一项是**所有活动MOVE、真实后车END和任务服务/FIFO**，至少连续两次动作交接；随后改进有界事件证据，降低全历史重放成本。当前后车服务仍是fixture，宿主fixture CPU不在guest费用模型，未把模型时钟映射成硬件吞吐。费用增加与时间改善并列报告，不虚构兑换率或净收益。

## 查询线：价值训练和新留出已形成，历史暂未带来任务优势

证据位于[查询R8报告](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/stratified_value_20261001_r8/REPORT.md)。沿用原作者持久OnlineGGO OBJ3、当前head FIFO和公开承诺frontier，固定合法信息、每次查询后的原资源检查，以及相同预算。

按四个公开时间段事前选择single/multi候选机会，每个入选机会全部候选反事实续跑，形成115标签：87训练、28校准，来自6个train与2个cal世界、88个机会。123个WAIT/探针完整运行；训练只有4条任务数+1，其余任务增益为零，标量目标也无负样本。每机会总权重为1，任务主指标不被次级完成时间颠倒；有/无历史ridge使用同数据、同架构、同正则并在测试前冻结。

|N16策略|8个留出条件的任务总数|查询总次数|
|---|---:|---:|
|WAIT|346|0|
|RR|350|128|
|条件规则|350|128|
|分时预算条件规则|344|120|
|分时预算有历史ridge|345|122|
|分时预算无历史ridge|345|122|

这48臂来自4个地图/任务family，各有IID和SHIFT，不能当48个独立样本。模型比相同分时规则多1任务，但比WAIT少1、比不分时的简单规则少5；有/无历史在每个world的任务数都相同。因此不能挑“比某个消融多1”作为学习有效的主要结论。原始FIFO、实际评分、分时容量、证书及正常服务已逐事件审计。

N32两地图的任务总数：WAIT171、RR/条件170、分时条件169、有历史166、无历史168；非WAIT策略都查询32次。历史模型在规模迁移中也没有优势。原12臂因继承的N≤16输入guard启动拒绝，未进入物理运行；失败和冻结源码保留，独立后继仅将上限改为32，使用完全相同12个场景/策略输入和原冻结模型，全部成功。它是事后接口兼容修复，不能当作新独立测试集。总计195attempt中183成功、12原输入guard失败；root独立核验60个完成留出的真实任务、查询次数、分时预算、逐次模型分数，以及后继唯一源码差异和相同输入。完整图见[全部配对](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/stratified_value_20261001_r8/ROOT_FIGURE_CAPTION.md)。

本轮定位了可修正的目标问题：标签使用“一次查询后一直WAIT”，部署却可多次查询；单次正作用不保证预算内连续干预有利。下一方法在公开状态h和剩余预算b下，用相同冻结尾策略π₀比较query与当前WAIT的成对后继价值；先只替换一次决策，确认任务增益，再做逐轮采样的多次策略改进。具体公式、数据隔离和因子对照见[下一方法合同](NEXT_METHOD_CONTRACT_20261001_R8.md)。

## 第三线：局部执行接口有效，模型监督单位需要修正

[完整报告](local_dependency_20261001_r8/REPORT.md)、[root独立执行审计](local_dependency_20261001_r8/ROOT_EXECUTION_AUDIT.json)、[独立重拟合审计](local_dependency_20261001_r8/ROOT_MODEL_REFIT_AUDIT.json)、[完整配对图](local_dependency_20261001_r8/FIGURE_CAPTION.md)。

用同一官方planner和当前任务头在停稳边界生成两步承诺，交给原parser/ADG/ACK。local在缓冲内按原依赖放行，global额外加共同等待门；后者是内部消融。六机械关验证独立机器人可先走第二步、依赖后继仍等正常ACK，以及中途到目标只进行一次真实STATION服务。随后两图×两任务seed×两误差条件×两执行方式×三策略，共48个400秒留出完成。

|执行接口|原hm任务|同历史规则任务|学习模型任务|
|---|---:|---:|---:|
|附加global门|174|177|177|
|原ADG局部放行|200|201|201|

全部16个学习/历史配对的任务差为0；local下学习的固定FIFO截尾完成时间还多98tick。朝向编码问题已在测试前修正，仅用旧训练/校准公共事件重建6062/3010标签、重新拟合并冻结；没有用R8test调模型。

本轮事后另发现第二步batch→END累计时长写入单步历史，且ADG允许多个自身前序未结束的primitive先入队。下一模型必须按真实队列事件分离依赖等待、入队排队与本节点耗时；不能用更深网络拟合这个混合量。所有54臂通过原依赖、正常ACK、FIFO和服务审计；1,543,200次几何采样保留，但不声称连续时间安全证明。批末屏障仍在，不把两步局部执行写成无限异步重规划。

## 论文基线和下一轮的具体顺序

已核验[PIE-D正式论文](https://ojs.aaai.org/index.php/AAAI/article/view/34506)、[OnlineGGO正式论文](https://ojs.aaai.org/index.php/AAAI/article/view/33614)及相应现用作者工件；RR、条件规则、history、global门都是内部消融。若下一方法改变通行顺序，优先接入[Improved GSES作者仓库](https://github.com/DiligentPanda/STPG)；若主张减少执行依赖同步，优先[P3GASUS作者仓库](https://github.com/marmotlab/P3GASUS-graph-creation)。尚未运行的作者方法不列为已比较或已超过。

[REMAP/ExecTimeNet/ESADG](https://arxiv.org/html/2511.21886v2)与[Should I Replan?](https://arxiv.org/html/2604.25567v1)已覆盖执行时间建模、昂贵模型调用或延迟重规划收益等方向；本轮阅读了相关方法正文。仅增加预测网络、GNN或重规划触发不构成明确差异。候选差异应落在有成本的物理进度证据、合法释放和持续服务之间，并用相同信息/计算预算验证。详见[近邻比较](NEIGHBOR_COMPARISON_20261001_R8.md)。

下一轮三个具体交付并行：主线连续动作与真实服务；查询线相同续策的预算优势数据和一次学习替换；第三线按原primitive/队列语义重建监督并冻结新模型。完成后再用新任务family扩大到更多公开地图和机器人规模，按family报告配对效应；选择最有任务证据的一条学习贡献进入论文，不把三线当前结果合并声称模型有效。
