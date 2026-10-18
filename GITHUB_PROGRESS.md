# 两线最新进度

2026-10-18。唯一当前决定：[docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md)。两线均为候选问题验证阶段。新授权的SCI两项逐次失败记录DEV已全部COMPLETE，零重试、许可消费；当前材料没有符合原后段门槛的正常空返回，停止该恢复候选。大论文运动比较未获授权、未运行；此前停批许可保持关闭。

## 当前交付

| 研究线 | 已完成 | 下一项与边界 |
|---|---|---|
| SCI：给定合法初解，在有限总预算内改善路径质量 | 两项逐次失败记录已核；17次成本停止，2次前半段正常空返回，没有符合原门槛的后段失败 | 停止当前材料上的后段恢复候选；下一项定点核查非runPP费用与等成本/变差接纳条件，暂不准备恢复比较或训练 |
| 硕士：同一优化器的运动与误差扩展 | 三臂完整任务接口接通原方案、固定SOC方案和经全车检查的转向感知方案；共用运动参数、初向和等待，分解完成时间与等待、保留拒绝和全部成本 | 新六项×三臂比较待授权，固定引用旧SCI535方案，不冒充完整ADDRESS结果。共同等待保守性、空间误差及反馈执行边界明确 |

SCI[共同预算结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/97d88a2e49a5a77078f56d6447e632fd5692d401/tracks/sci/ADDRESS_BUDGET_RESULT.md)：科学代码固定`101f18c`、清单SHA `edcef325…67cd1`，三项全部在15秒总准入/各进程10秒CPU/512MiB原限内正常输出。random32的SOC771不变，总9.169秒；maze32为1873→1866，总0.470秒；warehouse32为2486不变，总0.284秒，三项makespan均不变。完整路径与37个工件独立复核通过，总收据SHA `e39e60…b3ab`。random32实际触发GROUP阶段CPU软截止；三项均未触发SIPP内部deadline或预处理fallback，后两者仍只有软件证据。预算层是共同基线完善，不是性能优势或任意规模硬实时保证。

硕士[三方案接口与清单](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/a4ad94c5c84dc9f2239bc9b77e00a36740f70d2f/tracks/thesis/MOTION_RUN_CHECKLIST.md)冻结0.5m/格、0.22×0.16m声明仿真车身、共同E初向与运动参数，非LIMO实测。报告完成时间之和、makespan、转向barrier/离散等待及几何充分条件状态；永久驻留不算无限等待。共用保守障碍窗口，剩余候选仍精确检查。清单SHA `dfac22c0…3b7c`，6项各含3臂、每项60秒总准入/45秒CPU/512MiB，零重试；未构造六任务的新运动日程。

SCI[根界修补批报告](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/65a968c7138cfdc6097a81178362c6e03f2dfbd3/tracks/sci/ADDRESS_GUARD_RESULT.md)：random16保持SOC407/makespan53，完整准入128.565ms；random32原生退出−9，无有效最终输出，完整准入10161.731ms；warehouse两项未运行。独立离线BFS核对random32下界为769、初解771，根界在初态不触发。日志至少六次组修复已返回，最终停在构组或搜索尚不能确定；不能宣称故障整体解决。共同软截止需进入单次SIPP，保留末检预算与原硬限；DEADLINE不得作为搜索穷尽或恢复标签。23项工件已核，原失败证据未变；许可全部关闭。

SCI[上一批完整报告](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/eb4a60f236447505e6bb2cb0cc7e0e96cdfaa919/tracks/sci/ADDRESS_DEV_RESULT.md)保留maze16/32的SOC改善3/7步及random16失败，后三项未运行。根界修补属于共同工程条件，不计作贡献；旧结果与新结果不构成独立配对性能对照。

[失败诊断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/032bf223b78e6698821cbdee14a63cb8c8bc7718/tracks/sci/LATE_FAILURE_DIAGNOSIS.md)保留全部17项：13项失败位置在组后半；7项失败车旧路径无阻挡但超当次cap，10项旧路径在cap内而与新prefix冲突。它们来自固定ID组探针，尚不能认定完整ADDRESS有同样瓶颈。当时提出失败车旧路径前移、保留未受影响前段、最多一次尾段重算；后续完整ADDRESS记录未通过原后段门槛，当前材料上的该候选已停止。回退本身不是创新，需对照直接放弃、随机重排与适配后的优先级搜索。

[当前恢复实现](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/b0fa19e2b01d043968228a2d9e9c285eb3d3d9f7/tracks/sci/ADDRESS_RECOVERY.md)已统一诊断、私有占用表、搜索、完整校验和提交的wall/CPU/原repair期限；私有完整候选交换提交，到期逆交换或走作者原rollback。实际生成控制流的假时钟/假搜索夹具覆盖提交与全检取消，两个变体完整编译/help通过，不是恢复科学结果。`budget_guard --attemptTrace`记录primary真实调用位置、车辆、返回分类及费用，不做阻挡诊断；外部核对日志与搜索/rollback计数。恢复runner仍拒绝该变体，裸基线不承担恢复诊断费用。

[两项记录结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/7e77e9a4310928a7a273d4dac458d5536e7450d4/tracks/sci/ADDRESS_TRACE_RESULT.md)：科学代码`b0fa19e`，两项全部COMPLETE、零重试、许可消费。random32 SOC771不变、总9.176秒；maze32为1873→1866、总0.490秒，makespan均不变。21次修复中17次成本停止的全部单车调用均FOUND（9等成本、8变差）；两次空返回发生在第2/6辆、第4/8辆，不满足预设后段门槛。总收据SHA `308e5a65…a8632`、27项原工件和完整32车方案经独立离线复核。停止当前材料上的后段恢复候选，不放宽门槛、不追加场景追求正例；这不是所有恢复无效的证明。random的已测runPP仅约6.1ms，余下时间尚未细分，不能全归为可省构组开销。

硕士[路径诊断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/aea4ffad2dfdf59a163436a21ee35c0f7b75c333/tracks/thesis/PATH_DIAGNOSTIC.md)核实random32的29条等成本实际改路增加113个四分之一圈，另两条成本改变路径合计减少5个；这不是实际运动时长。新增整方案规则复用固定SCI校验器，混合方案必须全车合法。9项路径/规则检查通过。1m/格下六案均不满足原v2的8m必要轴界；仓储两案在“一格边一个原MOVE、统一尺度”条件下也不存在同时满足最小MOVE长度与位移界的尺度。没有静默缩放或扩域。

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
