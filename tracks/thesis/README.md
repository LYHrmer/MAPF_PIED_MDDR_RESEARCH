# 硕士论文支线索引

工作树`/home/lyh/MAPF_THESIS_RESEARCH`，分支`research/thesis-integration`。main只维护索引；实现与明细见[e507702本线入口](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/e5077026e16a869499fc03444f03bb433665cce8/tracks/thesis/README.md)。

[等成本改路与资格诊断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/aea4ffad2dfdf59a163436a21ee35c0f7b75c333/tracks/thesis/PATH_DIAGNOSTIC.md)已离线完成。简单保留/转向规则在整方案上选择，复用固定SCI同一validator，所有混合方案必须全车合法；只在软件夹具验证，尚未生成真实任务新对照。

无误差原语与完整多车时序已有[保守参考实现](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/e5077026e16a869499fc03444f03bb433665cce8/tracks/thesis/nominal_motion.py)：统一转向barrier、移动共用进度、车身圆外包、闭障碍与终点驻留检查；8项软件夹具通过，尚未应用真实任务比较，实际共享phase反馈执行未实现。后续先冻结运动参数并验证离散收益是否保留，再处理空间误差。v2仅支持整任务初始位姿偏差，需核对适用条件，不逐动作重置、不自动缩放或扩域。LIMO自身定位不能充当独立真值。

传统方法、学习辅助、运动与误差验证为条件式组织；不预先承诺RL章或三个创新点。SCI算法只维护一份，通过固定提交和锁文件引用。学校与导师具体要求仍待核定，详见[总体计划](../../docs/RESEARCH_PLAN.md)。
