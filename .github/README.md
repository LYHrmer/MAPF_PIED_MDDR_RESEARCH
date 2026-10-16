# MAPF 空间占用与执行约束

## 本轮增量审查（2026-10-16）

第2轮完成成本调用链核对：8738→446只减少首次22个窗口的外包求值，未减少make_problem构造、承诺逐次比较、相位/定位校验、差分约束、每次放行全车对时间检查和最终END/日志。当前缓存不提供跨放行请求的连续证书复用。完整口径分冷启动/复用、中心在线/仿真评估、总wall/CPU/峰值内存，嵌套计时不相加。若该求值仅占总成本10%，忽略新增开销的理想加速也仅约1.105倍；非实测。

第1轮核对费用近邻：PSIPP/CTC已有几何预处理、缓存查询及区间更新；MAPF-X缓存动作预测和后继；ESADG预印本已有廉价递推筛选。8738→446是本地旧/新构造器的外包求值数，两比较臂已同时采用；不能据此报完整计算提速。下一轮逐项列出首次构造、每次反馈更新、缓存失效、控制和日志的总费用边界。证据见[main最新审查](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)。公共工具保留，旧查询学习停止，后继有限清单尚不准备。

**最新：后继三轮已完成，99项累计静态检查通过。** 修正跨车辆回溯放行；等价窗口构造求值8738→446；两/三车完整消息配对仍无独有放行或保证。总实耗未测，当前同证书接线贡献候选关闭，保留工程接口。本轮仅静态核验，不运行、不训练。[当前说明](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/QUALIFICATION_NOTICE.md)。下文为T1基座背景。

2026-10-16。`explore/query-value-feasibility`：实际输入相位反馈、完整END与计费工具。四个活动分支服务同一个论文问题，旧查询学习继续归档。

最新已完成 T1：任务初态联合传播、保留物理时间的连续占用、时序/制动/承诺检查及两三车完整公共消息会话。87项新静态检查和63项C1回归通过；保留所有冻结证据与旧失败。固定消息夹具中，两臂放行、完成时间、消息流和证书工作量相同，没有独有保证；总运行实耗未测，不宣称相对强基线的创新。

- [本分支当前入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/query-value-feasibility/exploration/execution_feedback/timed_protocol.py)
- [统一方案与具体约束表](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/SPACE_TIME_INTERFACE_PLAN_20261016.md)
- [当前公共进度](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/GITHUB_PROGRESS.md)
- [有限运行清单：未授权未执行](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/spatial_constraints_s1_20261016/TIMED_RUN_CHECKLIST.md)
- [工作区、归档和恢复](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/main/REPOSITORY_NAVIGATION.md)

科学事件循环、world、优化器和训练本次均0。G2c两次许可已消费，短IPC清单仍未授权未执行；旧拖车不阻塞主线。L20/L21、旧查询学习、RL/换序/LMAPF和实物后置。当前同证书接线若无约束、算法成本或保证增量，结束候选并保留接口，不增加场景寻找正结果。

冻结文件保留本机原路径；Git入口精简不代表已物理删除数据。支线旧根README属于冻结历史，日常从本页及main进入。
