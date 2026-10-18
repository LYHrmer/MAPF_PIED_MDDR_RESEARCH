# SCI MAPF 支线索引

工作树`/home/lyh/MAPF_SCI_RESEARCH`，分支`research/sci-mapf`。main只维护索引；当前实现与明细见[本线入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/b0fa19e2b01d043968228a2d9e9c285eb3d3d9f7/tracks/sci/README.md)。

问题是给定合法初解，在有限总计算预算内改善MAPF路径质量。以ADDRESS为实现主干，BALANCE/TACKLE提供针对性参考，确需神经表示时再看NNS。下一机制候选为有界后段失败恢复，先核对限制与可复用条件，不把回退本身称为创新。

- [完整ADDRESS功能结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/eb4a60f236447505e6bb2cb0cc7e0e96cdfaa919/tracks/sci/ADDRESS_DEV_RESULT.md)：两项成功、第3项失败，后三项停批未运行，零重试；原许可已关闭。
- [旧失败离线诊断及具体候选](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/032bf223b78e6698821cbdee14a63cb8c8bc7718/tracks/sci/LATE_FAILURE_DIAGNOSIS.md)：不代表完整ADDRESS已证实同样瓶颈。
- [根界修补批结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/65a968c7138cfdc6097a81178362c6e03f2dfbd3/tracks/sci/ADDRESS_GUARD_RESULT.md)：1项完成、1项失败、2项未运行，许可关闭；原失败保留。
- [共同预算三项结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/97d88a2e49a5a77078f56d6447e632fd5692d401/tracks/sci/ADDRESS_BUDGET_RESULT.md)：全部COMPLETE、零重试、许可消费；random32本次构组软截止后合法返回。SIPP内部到期和预处理回退尚无真实任务覆盖，工程修补不作贡献；不据此认定恢复有效。
- [当前恢复与日志实现](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/b0fa19e2b01d043968228a2d9e9c285eb3d3d9f7/tracks/sci/ADDRESS_RECOVERY.md)：内部预算和事务回滚已统一，轻量trace记录真实调用位置/原因；软件及编译/help通过，没有新科学结果。[两项无恢复记录清单](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/b0fa19e2b01d043968228a2d9e9c285eb3d3d9f7/tracks/sci/ADDRESS_TRACE_CHECKLIST.md)待新授权，先核对正常失败机会。
- [冻结六任务结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/535ee1adf3135ab79565e0b3aa5d189348fe7ab2/tracks/sci/PROFILE_RESULT.md)：原传统策略DEV；许可已消费，没有恢复、学习或独立性能证据。

算法只在SCI维护，硕士引用固定版本。学习保留条件，不重启旧查询、L20/L21或零余量材料训练。总研究决定见[main计划](../../docs/RESEARCH_PLAN.md)。
