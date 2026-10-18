# 两线最新进度

2026-10-18。唯一当前决定：[docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md)。两线均为候选问题验证阶段；main维护总体决定，详细数值集中在各线报告。既有科学DEV许可全部消费，本轮没有新科学运行或训练。

## 当前交付

| 研究线 | 已完成 | 下一项与边界 |
|---|---|---|
| SCI：给定合法初解，在有限总预算内改善路径质量 | 以ADDRESS为主干。共同宿主的路径检查复用/细分计时已实现；完整ADDRESS共同初解、显式随机源、原推荐配置和总预算wrapper已实现、编译及无搜索检查。旧17次失败已离线重建 | 新六项完整ADDRESS功能清单已固定SHA，inspect通过，待授权；尚无真实完整基线闭环或新方法比较。下一机制只候选有限后段恢复 |
| 硕士：同一优化器的运动与误差扩展 | 等成本改路分解、全方案保留/转向规则与v2必要位移资格检查完成；通过固定Git对象引用SCI模块 | 简单规则仅在软件夹具检查，未生成六任务新比较。先无误差原语时序/连续占用，再检查误差改变哪些约束；连续执行未实现 |

SCI实现与证据：[本线入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/032bf223b78e6698821cbdee14a63cb8c8bc7718/tracks/sci/README.md)、[完整ADDRESS适配](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/032bf223b78e6698821cbdee14a63cb8c8bc7718/tracks/sci/ADDRESS_ADAPTER.md)、[新功能清单](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/032bf223b78e6698821cbdee14a63cb8c8bc7718/tracks/sci/ADDRESS_RUN_CHECKLIST.md)。宿主41项、ADDRESS适配7项软件检查通过；它们不是性能实验。两处构建失败收据/二进制身份关联问题已修复，作者缓存未改。原生完整循环没有逐次Python RPC，不能将两种架构的开销差额称为算法增量。

[失败诊断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/032bf223b78e6698821cbdee14a63cb8c8bc7718/tracks/sci/LATE_FAILURE_DIAGNOSIS.md)保留全部17项：13项失败位置在组后半；7项失败车旧路径无阻挡但超当次cap，10项旧路径在cap内而与新prefix冲突。它们来自固定ID组探针，尚不能认定完整ADDRESS有同样瓶颈。候选为失败车旧路径前移、保留未受影响前段、最多一次尾段重算；未执行、未证明能恢复或节省成本。回退本身不是创新，需对照直接放弃、随机重排与适配后的优先级搜索。

硕士[路径诊断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/aea4ffad2dfdf59a163436a21ee35c0f7b75c333/tracks/thesis/PATH_DIAGNOSTIC.md)核实random32的29条等成本实际改路增加113个四分之一圈，另两条成本改变路径合计减少5个；这不是实际运动时长。新增整方案规则复用固定SCI校验器，混合方案必须全车合法。9项路径/规则检查通过。1m/格下六案均不满足原v2的8m必要轴界；仓储两案在“一格边一个原MOVE、统一尺度”条件下也不存在同时满足最小MOVE长度与位移界的尺度。没有静默缩放或扩域。

## 冻结科学结果

- [SCI六项16/32车诊断，535ee1a](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/535ee1adf3135ab79565e0b3aa5d189348fe7ab2/tracks/sci/PROFILE_RESULT.md)：全部成功、零重试；两项局部修复与一项全体重排的SOC改善为1/2/1步，makespan不变。回调中79%—86%在RPC之外，不能全归于校验。旧train/DEV、任务嵌套、单次计时，不是独立性能证据。
- [SCI旧8车六臂，c0bd134](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/c0bd1345b8e192380ce2b1313e11475b54bbfa3d/tracks/sci/DEV_RESULT.md)：三份初解达到同模型下界，经典根界解释全部搜索减少，最终方案相同。该界作为独立贡献和该材料上的学习投入已停止。
- [执行旧四项闭式DEV，ae058c5](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/ae058c5025eaaa61a424ef7627515d40c2e83997/exploration/spatial_constraints_s1_20261016/PREEXECUTION_DEV_RESULT.md)：公共END与费用已核，两/三车均保留原安排，无枚举收益，来自同一R16相关投影。
- [硕士日志再导出，6771137](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/677113791c780e38333c9638632e6f02928e1a6a/tracks/thesis/README.md)及[原几何诊断，32db58f](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/32db58f1cd4c45b905b5557a26203a31bf49b7d8/tracks/thesis/README.md)均是旧证据离线解析，原产物字节保留。

## 范围与入口整理

学习是条件模块，不承诺独立RL章；ADDRESS已有在线学习，BALANCE/TACKLE/NNS按具体机制参考。大论文保留误差研究：先名义运动，再在同一允许初态、原语、信息与调度器下比较固定/传播外包。v2只支持整任务初始位姿偏差和同步同实际输入，不是一般持续跟踪误差；LIMO自身定位不作独立真值。

SCI算法只维护一份。硕士固定SCI`535ee1a`的输入/结果及原验证器，公共读取器固定`4a89183`，v2条件文档固定来源`16b1ee0`，不互读最新树。两研究树的README/总体计划/进度/导航已改为指向main及本线入口，旧快照通过固定Git提交保留；旧探索分支和冻结路径未移动或删除。

主仓`MANUSCRIPT_PREEXPERIMENT.md`仍仅保留原未提交修改，SHA `204316c27e17ecb37a8646d53cb5941a9b11b6c8eff3378ce55e80878b271452`。C1、Q/P/T/W、L20/L21与全部失败保留，不更名恢复停止路线。
