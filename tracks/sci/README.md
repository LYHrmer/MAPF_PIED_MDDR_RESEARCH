# SCI MAPF 支线索引

工作树`/home/lyh/MAPF_SCI_RESEARCH`，分支`research/sci-mapf`。main只维护索引；当前实现与明细见[本线入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/b4372b18c679cd7ce9bbe4ce6307a7bfe90dfaab/tracks/sci/README.md)。

2026-10-25已完成[四项预算合同功能验证](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/4fcf289347bcf8f93410e61ae15cf2b1bb37e3fa/tracks/sci/ADDRESS_SHARED_BUDGET_RESULT.md)及[十二项配对收益DEV](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/b4372b18c679cd7ce9bbe4ce6307a7bfe90dfaab/tracks/sci/ADDRESS_SHARED_BUDGET_GAIN_RESULT.md)。maze三个新seed分别降低SOC 42/39/43，makespan增加4/2/4；random三对均无质量差异。两任务均为已知开发材料，工程作用已观察到，泛化与独立算法贡献仍待；全部费用和退化保留。各批零重试、许可消费，默认legacy/all未自动切换。

问题是给定合法初解，在有限总计算预算内改善MAPF路径质量。以ADDRESS为实现主干，BALANCE/TACKLE提供针对性参考，确需神经表示时再看NNS。后段恢复候选保持停止；正延迟初始种子规则已完成八项开发对照，保留为朴素强对照，不把必要条件或共同工程优化称为创新。当前已完成四个未参与本轮设计的历史完整任务和多seed三模式比较，未建立稳定质量优势；不把旧random的单一正延迟候选作为种子排序训练依据。

- [最新种子开发对照](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/fde3409c17b9de68691f9233161cc2dcca03dbef/tracks/sci/ADDRESS_SEED_RESULT.md)：8项全部COMPLETE、零重试、许可消费。固定总预算maze有SOC改善与makespan退化，random只有更多修复而无质量收益；固定次数对照截尾原样保留，不能用更快完成16次代替最终质量。全部费用与独立审计见报告。
- [完整ADDRESS功能结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/eb4a60f236447505e6bb2cb0cc7e0e96cdfaa919/tracks/sci/ADDRESS_DEV_RESULT.md)：两项成功、第3项失败，后三项停批未运行，零重试；原许可已关闭。
- [旧失败离线诊断及具体候选](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/032bf223b78e6698821cbdee14a63cb8c8bc7718/tracks/sci/LATE_FAILURE_DIAGNOSIS.md)：不代表完整ADDRESS已证实同样瓶颈。
- [根界修补批结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/65a968c7138cfdc6097a81178362c6e03f2dfbd3/tracks/sci/ADDRESS_GUARD_RESULT.md)：1项完成、1项失败、2项未运行，许可关闭；原失败保留。
- [共同预算三项结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/97d88a2e49a5a77078f56d6447e632fd5692d401/tracks/sci/ADDRESS_BUDGET_RESULT.md)：全部COMPLETE、零重试、许可消费；random32本次构组软截止后合法返回。SIPP内部到期和预处理回退尚无真实任务覆盖，工程修补不作贡献；不据此认定恢复有效。
- [两项真实失败记录结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/7e77e9a4310928a7a273d4dac458d5536e7450d4/tracks/sci/ADDRESS_TRACE_RESULT.md)：全部COMPLETE、零重试、许可消费；没有符合原门槛的后段正常空返回，停止当前材料上的恢复候选。预算和日志实现保留，不扩大为恢复收益结论。
- [冻结六任务结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/535ee1adf3135ab79565e0b3aa5d189348fe7ab2/tracks/sci/PROFILE_RESULT.md)：原传统策略DEV；许可已消费，没有恢复、学习或独立性能证据。
- [两项非修复费用结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/d51fff2855686c1dffb5fe84fc9de8fa3b205e88/tracks/sci/ADDRESS_PHASE_RESULT.md)：random主要耗在反复选种子/构组，maze主要耗在修复；完整路径、阶段计时与总成本已独立复核。[清单](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/d51fff2855686c1dffb5fe84fc9de8fa3b205e88/tracks/sci/ADDRESS_PHASE_CHECKLIST.md)两项均COMPLETE、零重试、许可消费。后继适配须保留共同预算与完整校验，不能据本批认定加速。

算法只在SCI维护，硕士引用固定版本。学习保留条件，不重启旧查询、L20/L21或零余量材料训练。总研究决定见[main计划](../../docs/RESEARCH_PLAN.md)。

历史[36项结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/13d4749d8ecc12cefba4c2de72d96dc4c84105b0/tracks/sci/ADDRESS_REWARD_RESULT.md)全部完成但无稳定质量优势，已停止扩大该候选。随后6项费用诊断定位到项目适配层冗余认证；此前[4项接纳门控结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/f9c651ad0680679cf99a4973f722b65fd6f7aa97/tracks/sci/ADDRESS_VALIDATION_RESULT.md)已按授权完成、零重试、许可消费。候选校验减少，maze最终SOC却退化23，random持平且完整准入略增；未建立完整加速或质量优势，默认all保留。原清单邻域参数8被误写为硬上限，实际出现9，偏差单列。原始日志、全部费用和退化原样保存，不因这项工程变化启动学习。
