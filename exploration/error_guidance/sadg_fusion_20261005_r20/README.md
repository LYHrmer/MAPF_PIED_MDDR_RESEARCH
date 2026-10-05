# R20 新位置条件融合的共同执行实验

先读[三线结果及判断](REPORT.md)、[完整结果表](RESULT_TABLES.md)和[下一方法](NEXT_METHOD.md)。五臂共享原作者SADG；90条新执行全部完成，主要对比18对最终完成时间相同，新模型的二级预测误差下降。已有结果不自动证明学习调度优势。

## 文件与复现

- `EXPERIMENT_REGISTRATION.json`：启动前模型、代码、输入、预算与样本矩阵；`THREE_ROUTE_DECISION.md`：资格与事前问题。
- `position_model/`：冻结位置头；`model/`：保留原R19 END头；各自PROVENANCE指明跨分支来源。
- `SUMMARY.json`、`ANALYSIS.json`：完整逐世界结果及配对统计；PDF/SVG/600dpi PNG为描述性数据图，图数值来自冻结ANALYSIS。
- `INDEPENDENT_AUDIT.json`：90条独立审计；`review/`：独立数学、物理检查、负控与源码交叉复核。
- `solver_failure_review/`：全部8个候选拒绝/7个唯一输入的约束残差与源绑定；`mechanism_review/`：零新求解的72组因果顺序诊断。
- `publication_delta/MANIFEST.json`及分卷：仅新R20原始数据、90条episode/收据、CAS、作者缓存、R0和审核文件。旧R18/R19证据不重复打包；每成员校验SHA256并完成解包回读验证。

验证归档而不运行科学实验：

```bash
rtk proxy python3 -B exploration/error_guidance/sadg_fusion_20261005_r20/restore_delta.py
```

向隔离目录还原使用 `--destination <directory>`。相同文件可复用，不同文件拒绝覆盖。重跑科学实验应在新工作目录和新注册下进行，不能删去本轮STARTED/收据绕过单次规则。

完整审计依赖R18公开数据与原作者工件；历史绝对路径通过审计器`--path-map old=new`映射。本目录不是脱离历史工件的独立容器，也不重复上传外部作者二进制。具体许可/构建入口沿用既有R18/R19工件。主线真实计算费用与此处仿真查询计数分开报告。

## 图件边界

图表示18世界的总完成时间相对旧线性学习臂的比例及查询数，不表示置信区间或跨族平均。族级统计在RESULT_TABLES。所有方法名是内部预测/查询因子，外部Improved GSES资格在相邻独立目录。点机器人执行检查不等价于实体足迹、动力学或真实机器人验证。
