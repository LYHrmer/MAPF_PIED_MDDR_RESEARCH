# 硕士论文支线索引

工作树`/home/lyh/MAPF_THESIS_RESEARCH`，分支`research/thesis-integration`。main只维护索引；实现与明细见[本线入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/906ba90aa7274f4035cf56d1b2cc323a642b1516/tracks/thesis/README.md)。

[等成本改路与资格诊断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/aea4ffad2dfdf59a163436a21ee35c0f7b75c333/tracks/thesis/PATH_DIAGNOSTIC.md)保留既有离线证据。本轮[六任务三臂结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/4fc3a549afeac751fb54deac0056efee4b88a657/tracks/thesis/MOTION_RESULT.md)已经完成；原方案、冻结SOC方案、转向感知整方案均通过全车离散和声明模型下的连续充分条件检查，许可已消费。三个SOC缩短任务中仅maze32略降运动完成时间；maze16与random32更慢。简单整方案保留规则只在maze16额外改善，其余结果与非法混合候选拒绝均保留。

本批科学代码固定`a4ad94c`，旧SCI结果固定`535ee1a`；不能把运动收益归于本次ADDRESS种子规则。转向、离散等待、全局转向同步等待与计算成本分别统计，统一等待具有保守性，结论仅限共同phase理想参考；尚无实际控制闭环或误差安全结论。0.5m/格下六任务均超旧v2的8m必要范围，不直接套用或截段重置。v2只支持条件内的整任务初始位姿偏差；LIMO自身定位不能充当独立真值。

新增[同参数名义—初始位姿误差接口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/6a51a3bd84c4e64481bcdcec21bb4fb518669720/tracks/thesis/V2_MOTION_COMPARISON.md)复用固定来源和R16完整两/三车投影；共同参数、连续圆外包、转向槽补等待和永久终点检查已实现，27项人工测试通过。两项相关DEV清单已冻结但未运行，待本批新授权；同日程只检验可行性与费用，独立任务和作者完整执行系统的公平比较仍缺。旧两项须使用冻结`5d85f62`代码树，当前新增schema不能静默重签旧清单。

[局部调度结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/906ba90aa7274f4035cf56d1b2cc323a642b1516/tracks/thesis/SCHEDULER_RESULT.md)已完成maze16和random16共12臂，零硬失败、零重试、许可消费。maze的SOC缩短在局部调度下仍增加完成时间之和，简单转向整方案的小幅收益保留；random三路径零差异。局部构造和全检更贵，详细成本见报告；项目ADG语义对照不称完整SADG复现。误差、反馈执行与旧R16不在本批范围。

传统方法、学习辅助、运动与误差验证为条件式组织；不预先承诺RL章或三个创新点。SCI算法只维护一份，通过固定提交和锁文件引用。学校与导师具体要求仍待核定，详见[总体计划](../../docs/RESEARCH_PLAN.md)。
