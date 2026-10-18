# SCI MAPF 支线索引

工作树`/home/lyh/MAPF_SCI_RESEARCH`，分支`research/sci-mapf`。main只维护索引；当前实现与明细见[本线入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/6bee04b2cedf554a5b8ef0a6b58fc25bca319948/tracks/sci/README.md)。

问题是给定合法初解，在有限总计算预算内改善MAPF路径质量。以ADDRESS为实现主干，BALANCE/TACKLE提供针对性参考，确需神经表示时再看NNS。后段恢复候选保持停止；正延迟初始种子规则已完成八项开发对照，保留为朴素强对照，不把必要条件或共同工程优化称为创新。下一项准备未参与规则设计的完整任务输入和预先固定多seed的有限清单，尚未启动；当前random仅一个正延迟候选，不支持训练其种子排序。

- [最新种子开发对照](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/fde3409c17b9de68691f9233161cc2dcca03dbef/tracks/sci/ADDRESS_SEED_RESULT.md)：8项全部COMPLETE、零重试、许可消费。固定总预算maze有SOC改善与makespan退化，random只有更多修复而无质量收益；固定次数对照截尾原样保留，不能用更快完成16次代替最终质量。全部费用与独立审计见报告。
- [完整ADDRESS功能结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/eb4a60f236447505e6bb2cb0cc7e0e96cdfaa919/tracks/sci/ADDRESS_DEV_RESULT.md)：两项成功、第3项失败，后三项停批未运行，零重试；原许可已关闭。
- [旧失败离线诊断及具体候选](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/032bf223b78e6698821cbdee14a63cb8c8bc7718/tracks/sci/LATE_FAILURE_DIAGNOSIS.md)：不代表完整ADDRESS已证实同样瓶颈。
- [根界修补批结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/65a968c7138cfdc6097a81178362c6e03f2dfbd3/tracks/sci/ADDRESS_GUARD_RESULT.md)：1项完成、1项失败、2项未运行，许可关闭；原失败保留。
- [共同预算三项结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/97d88a2e49a5a77078f56d6447e632fd5692d401/tracks/sci/ADDRESS_BUDGET_RESULT.md)：全部COMPLETE、零重试、许可消费；random32本次构组软截止后合法返回。SIPP内部到期和预处理回退尚无真实任务覆盖，工程修补不作贡献；不据此认定恢复有效。
- [两项真实失败记录结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/7e77e9a4310928a7a273d4dac458d5536e7450d4/tracks/sci/ADDRESS_TRACE_RESULT.md)：全部COMPLETE、零重试、许可消费；没有符合原门槛的后段正常空返回，停止当前材料上的恢复候选。预算和日志实现保留，不扩大为恢复收益结论。
- [冻结六任务结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/535ee1adf3135ab79565e0b3aa5d189348fe7ab2/tracks/sci/PROFILE_RESULT.md)：原传统策略DEV；许可已消费，没有恢复、学习或独立性能证据。
- [两项非修复费用结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/d51fff2855686c1dffb5fe84fc9de8fa3b205e88/tracks/sci/ADDRESS_PHASE_RESULT.md)：random主要耗在反复选种子/构组，maze主要耗在修复；完整路径、阶段计时与总成本已独立复核。[清单](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/d51fff2855686c1dffb5fe84fc9de8fa3b205e88/tracks/sci/ADDRESS_PHASE_CHECKLIST.md)两项均COMPLETE、零重试、许可消费。后继适配须保留共同预算与完整校验，不能据本批认定加速。

算法只在SCI维护，硕士引用固定版本。学习保留条件，不重启旧查询、L20/L21或零余量材料训练。总研究决定见[main计划](../../docs/RESEARCH_PLAN.md)。

已完成[DyMAB窗口奖励接口核对](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/6bee04b2cedf554a5b8ef0a6b58fc25bca319948/tracks/sci/REFERENCE_REPRODUCTION.md)：原辅助模块编译与人工奖励夹具确认窗口/参数/选择差异，完整DyMAB与科学性能未复现。下一项在同一ADDRESS主干明确候选奖励、提交收益与截尾的结算接口，之后才比较共享条件下的累计与窗口记忆；CPLNS/X*继续作方法参考。首次检查脚本失败与修正后核验均保留，未消费或重用科学许可。
