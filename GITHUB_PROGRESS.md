# 两线最新进度

2026-10-18。唯一当前决定：[docs/RESEARCH_PLAN.md](docs/RESEARCH_PLAN.md)。SCI与硕士论文两条线共享必要底座；旧执行/来源/工具分支仅作交接。两线仍是候选问题，尚未证明独立算法创新。

## 最新真实运行：六任务全部完成

用户对本批请求回复“授权继续”后，按原清单执行六项16/32车诊断，全部COMPLETE、零重试，未放宽预算。SCI证据提交为[535ee1a](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/535ee1adf3135ab79565e0b3aa5d189348fe7ab2/tracks/sci/PROFILE_RESULT.md)。**六项许可已全部消费，不能重跑。** 执行HEAD为`57c3d69`，五个运行文件仍与`818f1e9`一致。

| 任务 | 初始SOC | 同模型静态h之和 | 最终SOC | 搜索调用 | 完整工作进程wall，ms |
|---|---:|---:|---:|---:|---:|
| maze s01/n16 | 690 | 680 | 689 | 54 | 163.438 |
| maze s01/n32 | 1873 | 1733 | 1871 | 82 | 395.149 |
| random s01/n16 | 407 | 407 | 407 | 0 | 92.692 |
| random s01/n32 | 771 | 769 | 770 | 61 | 173.325 |
| warehouse s01/n16 | 1112 | 1112 | 1112 | 0 | 92.508 |
| warehouse s01/n32 | 2486 | 2486 | 2486 | 0 | 112.543 |

SOC单位为离散步，不是秒；makespan均未改善。48次尝试包含28次根界拒绝、17次当前cap/固定前缀下穷尽和3次接受，共197次SIPP调用、12,177个展开。maze16/32是局部组收益，random32来自全体逆序，不能归为局部修复收益。接受后更新当前解，固定顺序不是局部/全体两方法的配对实验。

三个有搜索任务中，search回调wall的79.03%—85.92%在原生RPC之外。源码存在每次调用前后重复全量校验，但当前计时不能把全部差额归为校验；RPC也包含原生路径表构造和通信。完整费用、零搜索任务和所有无改善均保留；嵌套wall/CPU不重复相加。每任务仅一次、16/32车嵌套且来自旧train/DEV，不能报告稳定加速或独立泛化。

输入SHA `be1e912e1e2ea3f59fcdc5d0c5737118e7f96d92227be536ada605f6751c0e5b`；清单SHA `cff28cdbac11caf58f1eab952d954e907c877fa8355c5f4c38bec095f8987039`。50份原始/汇总/费用文件共465,457字节，原配置字节未重写，真实授权引用在attempt记录。每任务工作组wall≤15秒、算法≤10秒、Python/原生各CPU≤10秒且地址空间≤512 MiB、搜索≤128；实际最多82次，无超时/失败/未知/异常前缀拒绝。

## 两线的具体判断与下一项交付

| 研究线 | 新证据与判断 | 下一项实质交付 | 继续/停止条件 |
|---|---|---|---|
| SCI：有限预算下MAPF局部路径修复 | 传统策略有微小完整合法收益，但当前宿主费用占比较高；暂停“学习跳过昂贵SIPP”，尚无相对完整ADDRESS优势 | 复用不变路径合法性检查、保留增量与最终完整校验，分阶段计时；完成原版ADDRESS共同初解/随机性适配 | 工程优化由各方法共享；强基线后仍有稳定残余瓶颈，才提出方法增量和新比较。否则停止当前具体候选，不为三个正例训练 |
| 硕士：同一修复算法的运动代价与执行扩展 | [32db58f](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/32db58f1cd4c45b905b5557a26203a31bf49b7d8/tracks/thesis/README.md)已通过14个固定Git对象消费SCI`535ee1a`，六任务几何分解完成。三个SOC改善案例内部方向转动量增加11/18/108个四分之一圈 | 声明少量运动原语，转换固定路径并检查全车时序、转弯、等待、终点驻留；目前尚无连续执行结果 | 先看离散收益能否保留，再判断接受/修复规则的必要差异；若已有运动学适配已做到，保留分析/系统验证而不强称新算法 |

硕士新增产物为`OFFLINE_GEOMETRY_OF_EXISTING_SCI_PLANS`，不是新科学运行。计入任意共同首末朝向后，三个方向转动增量区间为[8,14]、[16,20]、[80,136]；只适用车头沿格边移动、采用最短转向的方向序列，不等于物理时长、实际车身转动或连续安全。四项新增软件检查通过；其余三任务零变化也保留。数据SHA `89e79538e5ee1f9bb849e76973c126157eec2307165a7bf86b19551e201b6f30`。

完整ADDRESS工件见SCI[57c3d69](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/57c3d6999e27e50e05164af0686ab6f461dfe1bf/tracks/sci/full_address_build_receipt.json)：86份固定作者文件树外编译，仅执行help，尚未科学运行。它不是本批SIPP桥接程序。完整公平适配仍缺共同初解、完整随机性和费用/奖励语义；原driver不接收外部初解，默认0次修复，Thompson随机源不完全受CLI seed控制。作者树未改。

## 保留的旧证据与边界

- 执行[ae058c5](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/ae058c5025eaaa61a424ef7627515d40c2e83997/exploration/spatial_constraints_s1_20261016/PREEXECUTION_DEV_RESULT.md)：四项闭式DEV全部SUCCESS，公共END/费用已核。两/三车完成时间之和均为54.315625/70.315625秒，枚举保留原安排、收益为零。只有一个组且源于同一R16投影；许可已消费。
- SCI第一批[c0bd134](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/c0bd1345b8e192380ce2b1313e11475b54bbfa3d/tracks/sci/DEV_RESULT.md)：三个8车初解均达到同模型h，六臂全完成，原控制48次搜索/增强0次且最终路径相同。经典根界解释全部减少，独立贡献与该材料上的学习停止；许可已消费。
- 硕士[6771137](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/677113791c780e38333c9638632e6f02928e1a6a/tracks/thesis/README.md)：262条同刻日志、10条接受且送达END支持的完成记录，仅是原四案离线再导出。没有将传输滞后当轨迹时间偏差，未测碰撞/覆盖率保持未测。
- C1同信息放行相同、Q/P/T/W、L20/L21及全部失败原位保留，不更名重启查询/组选取学习。R18超出原v2适用范围只限制误差模型，不自动否定标准离散MAPF用途。
- 原v2只覆盖整任务初始位姿不确定性和同实际输入/同步时钟，不是一般持续跟踪误差；LIMO里程计不充当独立真值。无world或训练，后继新科学比较须新清单与真实授权。

公共读取器固定`4a89183`，旧代码仍固定执行`81f5866`、来源`43806cf`、工具`5589a7b`；交接分支分别为`ae058c5`、`16b1ee0`、`c3bdef5`。SCI算法单份维护，硕士用锁文件消费固定提交，不互读最新工作树。主稿未提交修改保留，SHA `204316c27e17ecb37a8646d53cb5941a9b11b6c8eff3378ce55e80878b271452`。

[迁移前进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/c9985fb/GITHUB_PROGRESS.md)与[旧空间方案](SPACE_TIME_INTERFACE_PLAN_20261016.md)仅作历史恢复，不授予新运行或恢复旧路线。
