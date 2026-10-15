# SADG 共同问题适配与许可

`author_events.py` 为本项目新增适配代码，AGPL-3.0-or-later。它动态使用固定作者提交 `c2626d996121a9d6c128844a167b917db24418ac` 的 Vertex、Dependency、Status、PlanTuple、Location；导入前逐项核对 R16 留存哈希和包初始化文件，导入后核对真实模块路径。没有复制、修改作者源码，也未用替身模块。

作者与许可：Alex Berndt；Niels van Duijkeren, Robert Bosch GmbH。作者仓库 https://github.com/alexberndt/sadg-controller 。完整许可已随本分支保留于 [R16 AUTHOR_LICENSE](../error_guidance/sadg_preflight_20261004_r16/AUTHOR_LICENSE)。作者 R0 和优化器验收复用 R16/R17；本轮仅作事件 API 合同检查，无优化器/ROS/world 运行。

虚拟 CLEAR 节点表示完整允许后缀证书已成立，A 的物理动作仍 IN_PROGRESS。零长度事件不意味着机器人停车，也不进入作者的名义时长优化器。B 的固定依赖由作者 `can_execute()` 检查。该适配显式增加空间 guard 和事件节点，必须称为“SADG 共同问题适配”，不能称作者原版已有这个空间模块，更不能继承其完备性或无死锁结论。

R1 将相同证书交给自有 guard 和作者固定依赖，二者放行相同。因而更细释放事件本身尚不能作为本项目独有贡献；必须在同几何、同反馈、同事件粒度的强对照下核验。

`verify_integration.py` 是三个活动工作区的共同合同检查入口。原 S1 的 interface.py、fixture.json、verify.py、STATIC_CHECK.json、MANIFEST.json 保持冻结；新增集成不回写旧证据。闭式源探针不属于实测样本，也不构成有限科学批次运行。
