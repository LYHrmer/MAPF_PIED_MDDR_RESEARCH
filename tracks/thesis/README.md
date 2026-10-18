# 硕士论文支线索引

工作树`/home/lyh/MAPF_THESIS_RESEARCH`，分支`research/thesis-integration`。main只维护索引；实现与明细见[4fc3a54本线入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/4fc3a549afeac751fb54deac0056efee4b88a657/tracks/thesis/README.md)。

[等成本改路与资格诊断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/aea4ffad2dfdf59a163436a21ee35c0f7b75c333/tracks/thesis/PATH_DIAGNOSTIC.md)保留既有离线证据。本轮[六任务三臂结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/4fc3a549afeac751fb54deac0056efee4b88a657/tracks/thesis/MOTION_RESULT.md)已经完成；原方案、冻结SOC方案、转向感知整方案均通过全车离散和声明模型下的连续充分条件检查，许可已消费。三个SOC缩短任务中仅maze32略降运动完成时间；maze16与random32更慢。简单整方案保留规则只在maze16额外改善，其余结果与非法混合候选拒绝均保留。

本批科学代码固定`a4ad94c`，旧SCI结果固定`535ee1a`；不能把运动收益归于本次ADDRESS种子规则。转向、离散等待、全局转向同步等待与计算成本分别统计，统一等待具有保守性，结论仅限共同phase理想参考；尚无实际控制闭环或误差安全结论。0.5m/格下六任务均超旧v2的8m必要范围，下一项先准备满足原v2全部条件的独立短程完整任务，不扩域、不截段重置误差，未生成/运行新的误差任务。v2只支持条件内的整任务初始位姿偏差；LIMO自身定位不能充当独立真值。

传统方法、学习辅助、运动与误差验证为条件式组织；不预先承诺RL章或三个创新点。SCI算法只维护一份，通过固定提交和锁文件引用。学校与导师具体要求仍待核定，详见[总体计划](../../docs/RESEARCH_PLAN.md)。
