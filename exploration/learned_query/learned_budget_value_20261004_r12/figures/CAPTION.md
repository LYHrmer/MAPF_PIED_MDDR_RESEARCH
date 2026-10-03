# R12 留出测试配对结果图

`r12_test_comparison.pdf`、`.svg`和600 dpi `.png`由 `root_test_results.py`读取独立原始日志审计的结果生成；`preview.png`供快速查看。图中每格是同一任务family、执行误差种子和预算下相对于condition的配对差。四个独立family分别在B8和B16运行，不能将八行当作八个独立样本。

(a) 全部在线FIFO已完成任务数：方法减condition，正数表示多完成任务。这是主指标。(b) 每个机器人预先固定的前四项FIFO任务的受限完成时间之和：condition减方法，正数表示更早完成；截至H128仍未完成的任务计128。该项不只统计已完成任务，也不代替(a)。精确时间区间包含零的格标为“≈0”，绘图显示零，不将区间重叠解释成已证明严格相等。(c) 查询次数：condition减方法，正数表示少用查询。查询计数不等于包含推理和维护在内的生产计算费用。

Budget lookup仅用TRAIN为B8、B16分别固定选一条宏；Full model在首个合法机会用公开特征选择完整宏；No history和No budget分别重新拟合遮蔽对应输入槽的模型；Task head only复用Full任务头、去掉时间头。四种学习器使用同一个由Full在CAL选出的margin。No history仍保留基于历史的公共资格和condition续策，No budget仍受硬预算约束并执行宏内预算规则，Task head only也共享含时间次级排序的CAL；它们是明确限定的选择器消融。

全部方法沿用同一作者planner和原执行层。图中的WAIT、condition及Budget lookup是模块对照，不是新造的外部论文基线。本图支持四family的描述性留出判断；完整数值、区间及按family汇总见 `ROOT_TEST_RESULTS.json`，原始选择、SKIP和服务核验见 `ROOT_MACRO_AUDIT.json`。颜色在每个面板内对称归一，跨面板不能按颜色深浅比较不同单位的收益。
