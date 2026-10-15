# SADG 共同问题适配与许可

`author_events.py` 为本项目新增适配代码，AGPL-3.0-or-later。它动态使用固定作者提交 `c2626d996121a9d6c128844a167b917db24418ac` 的 Vertex、Dependency、Status、PlanTuple、Location；导入前逐项核对 R16 留存哈希和包初始化文件，导入后核对真实模块路径。没有复制、修改作者源码，也未用替身模块。

作者与许可：Alex Berndt；Niels van Duijkeren, Robert Bosch GmbH。作者仓库 https://github.com/alexberndt/sadg-controller 。完整许可已随本分支保留于 [R16 AUTHOR_LICENSE](../error_guidance/sadg_preflight_20261004_r16/AUTHOR_LICENSE)。作者 R0 和优化器验收复用 R16/R17；本轮仅作事件 API 合同检查，无优化器/ROS/world 运行。

虚拟 CLEAR 节点表示完整允许后缀证书已成立，A 的物理动作仍 IN_PROGRESS。零长度事件不意味着机器人停车，也不进入作者的名义时长优化器。B 的固定依赖由作者 `can_execute()` 检查。该适配显式增加空间 guard 和事件节点，必须称为“SADG 共同问题适配”，不能称作者原版已有这个空间模块，更不能继承其完备性或无死锁结论。

R1 将相同证书交给自有 guard 和作者固定依赖，二者放行相同。因而更细释放事件本身尚不能作为本项目独有贡献；必须在同几何、同反馈、同事件粒度的强对照下核验。

`verify_integration.py` 是三个活动工作区的共同合同检查入口。原 S1 的 interface.py、fixture.json、verify.py、STATIC_CHECK.json、MANIFEST.json 保持冻结；新增集成不回写旧证据。闭式源探针不属于实测样本，也不构成有限科学批次运行。

R2：联合检查累计 38 项。每种几何分别比较自有 guard 与同信息作者事件适配：方向性均在 3.43 s、圆形均在 3.93 s 满足该接口例的放行条件；消息数和字节相同。它们是合同例的时刻，不是 world 点估计或算法加速结果。重入后缀、承诺改变及普通 END 均无法绕过检查。

结论：本例没有独立于几何表示和事件细分的调度增量，停止把这部分解释为新贡献；不追加学习或挑选新任务追求正结果。第三轮只做共同合同完整性与收缩验收。连续安全仍来自 S1 允许集的后缀证书，作者节点的无环/完成状态单独不能证明它。

R3：新增 `session.py`，把源合同、车身/朝向范围、完整起点等待、运动及终点占用、合法进度和固定 SADG 事件绑定到同一接收接口。拒绝欠覆盖外包、单位/路径/控制器不匹配、承诺内容变化、收件时钟倒退及 B 尚未放行的 END。完整 A-END 由本地控制器产生，中心仍需其公开定位及完整后缀检查，不能靠普通 END 放行。

最终 66 项联合检查与冻结 S1 的 37 项检查通过。两套结果分别保留，不能合计为 103 个独立实验。五个完整公共消息例均走到 A/B 的 END，但没有 world 时间步、碰撞检测轨迹、优化器运行、训练或独立任务样本；完整执行净收益 UNKNOWN。③查表、④学习仅保留预登记比较方案，未伪造实现或结果。

精确复核命令（默认核对跨分支文件与作者导入文件 SHA，任何变更拒绝）：

```bash
rtk proxy python3 -B /home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE/exploration/spatial_constraints_s1_20261016/verify_integration.py
```

输入固定为同目录 fixture.json、三个活动模块和 R16 作者来源清单，文件身份见 INTEGRATION_MANIFEST.json。输出只到 stdout，不启动 solver/world。核验失败立即退出，不自动修补来源、不重试、不消费科学运行许可。固定源检验依赖三个原工作区及已留存作者 checkout；此依赖如实记录，并非单分支独立安装包。

未生成“已就绪”的新 world 批次或科学运行授权：同信息等价已触发收缩，继续扩场景/训练不符合停止判据。若以后有新的明确决策缺口，必须先补实际执行器、连续轨迹评估、输入与监督预算，再提交具体运行清单；旧 G2c 许可不可转用。
