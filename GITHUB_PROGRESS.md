# 两线最新进度

2026-10-24。唯一当前决定：[docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md)。用户新授权的SCI6项费用诊断与硕士2项12臂调度比较均已完成，零硬失败、零重试，许可已消费并独立离线复核。旧R16误差两项未获本次授权、仍未运行。两线均为候选验证阶段，后段恢复停止，无训练或world。

## 当前交付

**最新结果：** SCI [65d7211费用诊断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/65d72115437c96e0b64c81535e72c00f50e027d7/tracks/sci/ADDRESS_COST_RESULT.md)固定科学代码`e8edaff`：6项全部合法返回，1893事件闭合。random校验占selection79.41%，其中99.42%用于已COST_STOP的不能接纳候选；maze校验只占8.99%，且搜索/校验均可先触发截止。它定位的是项目奖励覆盖层的共同工程冗余，不能归为作者原版ADDRESS或算法创新。按此实测结果落实下述单一工程改动；奖励和训练暂不改。

**新优化实现：** SCI [2bd1916接纳门控](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/2bd191691b654e8ff8e0e1fc4933e997f07a063b/tracks/sci/ADDRESS_VALIDATION_GATE.md)已完成。依据[IJRR/AIJ定点学习](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/2bd191691b654e8ff8e0e1fc4933e997f07a063b/tracks/sci/REFERENCE_REPRODUCTION.md)，仅以原接纳必要条件跳过必拒候选的昂贵认证，默认all，显式acceptance_eligible；可能提交候选及最终方案全检保留。53项软件夹具、42份旧账本精确兼容、完整编译/help及独立复核通过。新优化没有科学结果；4项配对DEV清单SHA `4aa5d08c…82ad8b`待新授权，每项5秒准入/各进程CPU10秒/512MiB、外层10+2秒，零重试首硬失败停。已消费的6项许可不可复用。

硕士 [906ba90调度结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/906ba90aa7274f4035cf56d1b2cc323a642b1516/tracks/thesis/SCHEDULER_RESULT.md)固定科学代码`76a6a99`：2项12臂均获名义充分分离证书。maze的SOC690→689，局部完成时间和1835.027→1864.734秒，反转仍存在；转向整方案为1829.456秒，makespan三者相同。random三路径相同、零差异保留。局部构造/检查更贵，全部费用见报告。新旧实物、v2或反馈END均未混入。

前一轮三轮实现、人工正反例和预算设计见[冻结交接](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/f5369f3fa34ca36683e4351f05d37d47eacd06f5/GITHUB_PROGRESS.md)；当前消费状态只以上述实际结果为准。

SCI [cb8247b奖励设计与验证](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/cb8247b9136d36a05dc68c3c3b543a7c82d4494c/tracks/sci/REWARD_DESIGN_REVIEW.md)：固定初始SOC归一化实际提交幅度，费用独立；20项软件测试通过，36份冻结账本逐项闭合，独立子任务重算一致。截尾实际收益0与未完成候选收益未知分开；未更换在线选择器，未声称幅度反馈有效。截止/费用实测现已完成，先修共同冗余校验，再决定是否值得进行二元/幅度机制对照；不能将连续值直接送入原Beta。四个旧任务已用于新候选设计，未来独立验证需另隔离任务。

SCI [13d4749结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/13d4749d8ecc12cefba4c2de72d96dc4c84105b0/tracks/sci/ADDRESS_REWARD_RESULT.md)：科学代码`3d44f2d`、manifest SHA `6863861a…fe791`，4个历史完整任务×3seed×3模式全部完成。累计相对原奖励SOC胜/平/负为3/7/2，窗口相对累计为1/8/3，两个random任务全平；没有跨任务稳定收益，按预定标准停止扩容/调W。全部终态、543原工件、21,873条奖励记录及配对已独立核验。每项总准入3.038–3.085秒，完整费用见报告，不作为稳定加速。maze32截尾792/954（83.019%），原阶段标签不能定位首次截止；本轮诊断实现见上，不绕过全检或回填本批。

硕士 [6a51a3b](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/6a51a3bd84c4e64481bcdcec21bb4fb518669720/tracks/thesis/V2_MOTION_COMPARISON.md)：同参数名义—初始位姿误差对照已接通，固定R16两/三车完整投影满足静态资格，27项人工软件测试通过；两项有限任务未运行。相同日程只检验可行性/裕量/费用，不声称减少等待；成熟局部依赖执行对照仍缺。ExecTimeNet/REMAP v2定位同步修正为执行感知CBS/LNS与贝叶斯预测门控，仍标预印本。

| 研究线 | 已完成 | 下一项与边界 |
|---|---|---|
| SCI：有限总预算内分配局部重规划机会 | 36项三模式对照无稳定质量收益；幅度反馈离线闭合；6项费用归因已核 | 6项诊断已完成；先去掉必拒候选的冗余认证，再按完整预算评价工程优化和最终SOC |
| 硕士：同一优化器的运动与误差扩展 | 旧6任务结果保留；新2任务12臂调度比较完成；误差接口保留 | 2项调度比较已完成，maze排序反转仍在；明确运动代价适配差异，R16误差另行处理 |

SCI[正延迟初始种子结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/fde3409c17b9de68691f9233161cc2dcca03dbef/tracks/sci/ADDRESS_SEED_RESULT.md)：科学代码`93af30f`，两份开发任务、单seed、两种策略与两种预算口径，共8项完整合法输出。固定总预算下maze最终SOC由对照1847降至1801，同时makespan由129增至131；random两臂SOC均771，更多修复没有转化为质量收益。固定次数random对照只完成4/16次并在CPU软截止返回，不能算相同16次加速比。零延迟车辆仍可作为邻域成员；筛选至输出全部计费，规则改变随机分布。random32中正延迟候选仅一辆，不能作为继续训练种子排序的依据。完整数值、截尾和独立审计统一见报告；这是朴素强对照，非独立创新。

SCI[两项阶段计时结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/d51fff2855686c1dffb5fe84fc9de8fa3b205e88/tracks/sci/ADDRESS_PHASE_RESULT.md)：科学代码`f6e1d01`、证据`d51fff2`；random32 SOC771不变、总9.172秒，maze32为1873→1866、总0.452秒，makespan均不变。random的选种子/构组四阶段占原生计时窗口98.93%，195157次构组中选中195153次零延迟种子，只进入4次修复；maze窗口92.65%在修复内部。详表及全部成本只在该报告维护。总收据SHA `e64d0824…bf6011`、27原工件、全体路径与费用经独立离线复核；[清单](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/d51fff2855686c1dffb5fe84fc9de8fa3b205e88/tracks/sci/ADDRESS_PHASE_CHECKLIST.md)许可已消费，JSON原SHA不变。预算检查的确定性采样不能外推总费用，旧无profile批次不是配对计时。该诊断促成了上述正延迟种子开发对照；本段保留原阶段计时结果，不与新无profile批次作配对速度比较。

SCI[共同预算结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/97d88a2e49a5a77078f56d6447e632fd5692d401/tracks/sci/ADDRESS_BUDGET_RESULT.md)：科学代码固定`101f18c`、清单SHA `edcef325…67cd1`，三项全部在15秒总准入/各进程10秒CPU/512MiB原限内正常输出。random32的SOC771不变，总9.169秒；maze32为1873→1866，总0.470秒；warehouse32为2486不变，总0.284秒，三项makespan均不变。完整路径与37个工件独立复核通过，总收据SHA `e39e60…b3ab`。random32实际触发GROUP阶段CPU软截止；三项均未触发SIPP内部deadline或预处理fallback，后两者仍只有软件证据。预算层是共同基线完善，不是性能优势或任意规模硬实时保证。

硕士[六任务三臂运动结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/4fc3a549afeac751fb54deac0056efee4b88a657/tracks/thesis/MOTION_RESULT.md)：证据`4fc3a54`、科学代码`a4ad94c`，固定引用旧SCI`535ee1a`，不是本次种子规则输出。18臂均建立声明模型下的连续圆外包充分分离条件；maze16与random32的冻结SOC方案分别增加运动完成时间和25.854/18.566秒，maze32仅减少1.434秒；转向感知整方案只在maze16额外改善，全部零差异/拒绝保留。转向、离散等待、全局转向同步等待及完整费用见报告。0.5m/格、车身/运动参数与初向均为声明仿真条件，统一barrier有保守性，非LIMO实测或误差安全结论。六项许可已消费，管理记录事件及处置也原样保留。

SCI[根界修补批报告](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/65a968c7138cfdc6097a81178362c6e03f2dfbd3/tracks/sci/ADDRESS_GUARD_RESULT.md)：random16保持SOC407/makespan53，完整准入128.565ms；random32原生退出−9，无有效最终输出，完整准入10161.731ms；warehouse两项未运行。独立离线BFS核对random32下界为769、初解771，根界在初态不触发。日志至少六次组修复已返回，最终停在构组或搜索尚不能确定；不能宣称故障整体解决。共同软截止需进入单次SIPP，保留末检预算与原硬限；DEADLINE不得作为搜索穷尽或恢复标签。23项工件已核，原失败证据未变；许可全部关闭。

SCI[上一批完整报告](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/eb4a60f236447505e6bb2cb0cc7e0e96cdfaa919/tracks/sci/ADDRESS_DEV_RESULT.md)保留maze16/32的SOC改善3/7步及random16失败，后三项未运行。根界修补属于共同工程条件，不计作贡献；旧结果与新结果不构成独立配对性能对照。

[失败诊断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/032bf223b78e6698821cbdee14a63cb8c8bc7718/tracks/sci/LATE_FAILURE_DIAGNOSIS.md)保留全部17项：13项失败位置在组后半；7项失败车旧路径无阻挡但超当次cap，10项旧路径在cap内而与新prefix冲突。它们来自固定ID组探针，尚不能认定完整ADDRESS有同样瓶颈。当时提出失败车旧路径前移、保留未受影响前段、最多一次尾段重算；后续完整ADDRESS记录未通过原后段门槛，当前材料上的该候选已停止。回退本身不是创新，需对照直接放弃、随机重排与适配后的优先级搜索。

[当前恢复实现](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/b0fa19e2b01d043968228a2d9e9c285eb3d3d9f7/tracks/sci/ADDRESS_RECOVERY.md)已统一诊断、私有占用表、搜索、完整校验和提交的wall/CPU/原repair期限；私有完整候选交换提交，到期逆交换或走作者原rollback。实际生成控制流的假时钟/假搜索夹具覆盖提交与全检取消，两个变体完整编译/help通过，不是恢复科学结果。`budget_guard --attemptTrace`记录primary真实调用位置、车辆、返回分类及费用，不做阻挡诊断；外部核对日志与搜索/rollback计数。恢复runner仍拒绝该变体，裸基线不承担恢复诊断费用。

[两项记录结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/7e77e9a4310928a7a273d4dac458d5536e7450d4/tracks/sci/ADDRESS_TRACE_RESULT.md)：科学代码`b0fa19e`，两项全部COMPLETE、零重试、许可消费。random32 SOC771不变、总9.176秒；maze32为1873→1866、总0.490秒，makespan均不变。21次修复中17次成本停止的全部单车调用均FOUND（9等成本、8变差）；两次空返回发生在第2/6辆、第4/8辆，不满足预设后段门槛。总收据SHA `308e5a65…a8632`、27项原工件和完整32车方案经独立离线复核。停止当前材料上的后段恢复候选，不放宽门槛、不追加场景追求正例；这不是所有恢复无效的证明。当时random已测runPP仅约6.1ms；后续分项计时见本页最新报告，不能把旧残差全归为可省费用。

硕士[路径诊断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/aea4ffad2dfdf59a163436a21ee35c0f7b75c333/tracks/thesis/PATH_DIAGNOSTIC.md)核实random32的29条等成本实际改路增加113个四分之一圈，另两条成本改变路径合计减少5个；这不是实际运动时长。新增整方案规则复用固定SCI校验器，混合方案必须全车合法。9项路径/规则检查通过。本轮0.5m/格下六案仍均不满足原v2的8m必要轴界；仓储两案在“一格边一个原MOVE、统一尺度”条件下也不存在同时满足最小MOVE长度与位移界的尺度。下一步选满足原v2全部条件的独立短程完整任务，当前未生成或运行；不截长任务后重置误差，不静默缩放或扩域。

硕士当前[无误差运动模块](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/e5077026e16a869499fc03444f03bb433665cce8/tracks/thesis/nominal_motion.py)输出直行/转向/等待/永久终点驻留及物理完成时间。共同进度下的连续相对距离、闭障碍及外边界采用精确有理几何；圆外包重叠只导致充分条件未建立，不当作真实矩形碰撞。此为保守理想参考，尚无控制器、误差或最优性结论。

## 冻结科学结果

- [SCI六项16/32车诊断，535ee1a](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/535ee1adf3135ab79565e0b3aa5d189348fe7ab2/tracks/sci/PROFILE_RESULT.md)：全部成功、零重试；两项局部修复与一项全体重排的SOC改善为1/2/1步，makespan不变。回调中79%—86%在RPC之外，不能全归于校验。旧train/DEV、任务嵌套、单次计时，不是独立性能证据。
- [SCI旧8车六臂，c0bd134](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/c0bd1345b8e192380ce2b1313e11475b54bbfa3d/tracks/sci/DEV_RESULT.md)：三份初解达到同模型下界，经典根界解释全部搜索减少，最终方案相同。该界作为独立贡献和该材料上的学习投入已停止。
- [执行旧四项闭式DEV，ae058c5](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/ae058c5025eaaa61a424ef7627515d40c2e83997/exploration/spatial_constraints_s1_20261016/PREEXECUTION_DEV_RESULT.md)：公共END与费用已核，两/三车均保留原安排，无枚举收益，来自同一R16相关投影。
- [硕士日志再导出，6771137](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/677113791c780e38333c9638632e6f02928e1a6a/tracks/thesis/README.md)及[原几何诊断，32db58f](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/32db58f1cd4c45b905b5557a26203a31bf49b7d8/tracks/thesis/README.md)均是旧证据离线解析，原产物字节保留。

## 范围与入口整理

学习是条件模块，不承诺独立RL章；ADDRESS已有在线学习，BALANCE/TACKLE/NNS按具体机制参考。大论文保留误差研究：先名义运动，再在同一允许初态、原语、信息与调度器下比较固定/传播外包。v2只支持整任务初始位姿偏差和同步同实际输入，不是一般持续跟踪误差；LIMO自身定位不作独立真值。

SCI算法只维护一份。硕士固定SCI`535ee1a`的输入/结果及原验证器，公共读取器固定`4a89183`，v2条件文档固定来源`16b1ee0`，不互读最新树。两研究树的README/总体计划/进度/导航已改为指向main及本线入口，旧快照通过固定Git提交保留；旧探索分支和冻结路径未移动或删除。

主仓`MANUSCRIPT_PREEXPERIMENT.md`仍仅保留原未提交修改，SHA `204316c27e17ecb37a8646d53cb5941a9b11b6c8eff3378ce55e80878b271452`。C1、Q/P/T/W、L20/L21与全部失败保留，不更名恢复停止路线。
