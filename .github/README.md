# MAPF 空间占用与执行约束

**最新：活动行建议、精确证书与矩形裁剪回退已实现。** [active_advice.py](../exploration/spatial_constraints_s1_20261016/active_advice.py)只接受行编号，按当前系数重验原始/对偶可行及零间隙；失败共享一次裁剪回退，证书不授权放行。60条固定断言通过，五对十个极值等于冻结结果。裁剪20次交点/82次顶点检查已构成强非学习对照，完美建议尚无全成本优势，不为该小问题开训。旧解析几何界1.738392026978 s及放行负结果保留；旧构造未替换，未接入控制会话，无新科学运行。[现有说明中的完整结果与证明](../exploration/spatial_constraints_s1_20261016/DEPARTURE_NOTICE.md)。以下为前轮状态。

**最新：同几何直接相位对投影已实现，固定11动作对静态核验通过。** A₀→B₂局部空间上界缩小63/64 s，但原END关系覆盖它，11条有效下界均相同；全局边界仍1.74546875 s，外包求值446→542。本例原先验下剩余有序边界收紧量至多约17.473 ms，非已实现收益。当前候选停止，未接入放行/控制会话，不准备新运行。[构造、证明及结果](../exploration/spatial_constraints_s1_20261016/DEPARTURE_NOTICE.md)。

## 前轮增量审查（2026-10-16）

第3轮验收：当前同证书接线无独有合法安排或保证，后继运行资格未通过。保留现有代码与负结果；未来只在新构造器给出同允许族、同反馈/粒度、同原次序下的具体禁行集合差异和完整连续证书后再判断。共享证书对照不能单独否定一个未来新构造器；其比较对象应是充分适配的已有连续冲突算法。旧T1运行入口保留历史状态，本轮不准备后继清单。

第2轮已从冻结12条约束精确计算瓶颈：A₂→B₂下界1.85046975 s，次紧A₀→B₀为1.8491025625 s，差7/5120 s。在既定9.45 s放行时全部有余量；仅收紧TURN相关非瓶颈窗口不降低最大下界。晚到反馈不能用于追溯放行，上述不是更早合法调度或任务收益。新增候选必须提供同信息、同原次序、完整物理时间安全下的严格禁行集合差异；不能只列边数变少。

第1轮已完成作者接口定点核对：SADG固定核心可以承载合法预约事件，WinkTPG已有离开上界/进入下界预约；PSIPP/CTC已有非共同路点的连续点—边、边—边冲突及多安全区间，MAPF-X也检查膨胀路段。故“新增空间边、提前释放、保留时间”不足以构成独立执行算法。原C1/T1及99项收据复用，当前相同信息放行一致的负结果保留。作者函数、版本和证据见[main最新审查](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)。本分支下一轮只核当前约束的实际瓶颈，不创建后继运行清单。

**最新：后继三轮已完成，99项累计静态检查通过。** 修正跨车辆回溯放行；等价窗口构造求值8738→446；两/三车完整消息配对仍无独有放行或保证。总实耗未测，当前同证书接线贡献候选关闭，保留工程接口。本轮仅静态核验，不运行、不训练。[当前说明](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/QUALIFICATION_NOTICE.md)。下文为T1基座背景。

2026-10-16。`explore/error-aware-guidance`：连续时空约束、完整任务接口及强基线适配。四个活动分支服务同一个论文问题，旧查询学习继续归档。

最新已完成 T1：任务初态联合传播、保留物理时间的连续占用、时序/制动/承诺检查及两三车完整公共消息会话。87项新静态检查和63项C1回归通过；保留所有冻结证据与旧失败。固定消息夹具中，两臂放行、完成时间、消息流和证书工作量相同，没有独有保证；总运行实耗未测，不宣称相对强基线的创新。

- [本分支当前入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/TIMED_NOTICE.md)
- [统一方案与具体约束表](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)
- [当前公共进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md)
- [有限运行清单：未授权未执行](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/TIMED_RUN_CHECKLIST.md)
- [工作区、归档和恢复](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/REPOSITORY_NAVIGATION.md)

科学事件循环、world、优化器和训练本次均0。G2c两次许可已消费，短IPC清单仍未授权未执行；旧拖车不阻塞主线。L20/L21、旧查询学习、RL/换序/LMAPF和实物后置。当前同证书接线若无约束、算法成本或保证增量，结束候选并保留接口，不增加场景寻找正结果。

冻结文件保留本机原路径；Git入口精简不代表已物理删除数据。支线旧根README属于冻结历史，日常从本页及main进入。
