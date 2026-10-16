# MAPF 空间占用与执行约束

## 本轮增量审查（2026-10-16）

第3轮验收：v2范围在原同步实际输入和不可变承诺内维持覆盖资格；没有额外安全定理。硬安全关联等价命题不适用于机会约束/跨车耦合/观测缩域。任何下一候选须指出究竟缩小哪一时刻的允许占用或哪一禁行时段，并证明TURN/制动/等待/永久驻留仍覆盖；不能靠换动作重置误差。当前不扩大动力学、不训练，不准备新来源运行。

第2轮完成量词推导：跨车允许参数域为直积、固定运动与全时刻硬安全时，∀参数∀时刻的碰撞规避等价于每时刻精确边际占用分离。因此共享跨时刻参数主要保证覆盖合法；若边际集合不变，关联本身不增加可行安排。当前中心/车身同δ的公式最终仍经轴对齐盒和TURN整圆松弛；定位反馈只作一致性校验，没有历史参数交集。机会约束、跨车耦合或观测缩域不在此等价命题内。

第1轮对照作者模型：PSIPP/CTC固定圆形/线段的解析冲突与转向耗时映射已经存在；MAPF-X将预测空间偏差用于路段膨胀。二者均不能直接充作v2共享初态矩形旋转的覆盖证明，但这个模型差异本身也不证明方法创新。dSLAP的条件安全定理不随范围预测接口迁移。下一轮分清“跨动作传播正确”与“同条件下减少保守性”，推导共享参数在全时刻硬安全中的具体作用。固定源码及原文见[main最新审查](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)。来源代码与旧失败保持冻结，不准备训练或新来源运行。

**最新：后继三轮已完成，99项累计静态检查通过。** 修正跨车辆回溯放行；等价窗口构造求值8738→446；两/三车完整消息配对仍无独有放行或保证。总实耗未测，当前同证书接线贡献候选关闭，保留工程接口。本轮仅静态核验，不运行、不训练。[当前说明](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/QUALIFICATION_NOTICE.md)。下文为T1基座背景。

2026-10-16。`explore/gaussian-mapf-feasibility`：任务共享初态、物理时间占用与运动条件。四个活动分支服务同一个论文问题，旧查询学习继续归档。

最新已完成 T1：任务初态联合传播、保留物理时间的连续占用、时序/制动/承诺检查及两三车完整公共消息会话。87项新静态检查和63项C1回归通过；保留所有冻结证据与旧失败。固定消息夹具中，两臂放行、完成时间、消息流和证书工作量相同，没有独有保证；总运行实耗未测，不宣称相对强基线的创新。

- [本分支当前入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/gaussian-mapf-feasibility/exploration/spatial_source/TIMED.md)
- [统一方案与具体约束表](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)
- [当前公共进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md)
- [有限运行清单：未授权未执行](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/TIMED_RUN_CHECKLIST.md)
- [工作区、归档和恢复](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/REPOSITORY_NAVIGATION.md)

科学事件循环、world、优化器和训练本次均0。G2c两次许可已消费，短IPC清单仍未授权未执行；旧拖车不阻塞主线。L20/L21、旧查询学习、RL/换序/LMAPF和实物后置。当前同证书接线若无约束、算法成本或保证增量，结束候选并保留接口，不增加场景寻找正结果。

冻结文件保留本机原路径；Git入口精简不代表已物理删除数据。支线旧根README属于冻结历史，日常从本页及main进入。
