# 纯调度后继登记

原串行pipeline完成40个世界、120余个native后，单次约6秒，使全598臂约一小时。按root指令改为10独立world并行，每world内WAIT/两候选/实际策略仍序列执行，无共同跨world状态、无科学条件/模型/seed/奖励变化。原pipeline.py/CONTRACT/native源码/binary/inputs和全部回执保持。

原unified exec session79290用Ctrl-C结束，tool exit130；已完成回执与raw保留并按hash复用。未完成在途调用没有可认证的完整capture，本事实单列，不补造完成回执；新后继只执行尚缺成功回执的臂，全部失败/中断材料保留，不择优。默认sandbox进程namespace看不到另一exec中的PID，一次查找无匹配的诊断也不作为native失败。

训练/校准world阶段全部完成后，按worldID/source确定性排列标签，同lambda1及10原特征train-only solve/1e-9有理参数导出并冻结；之后才并行完整两个测试cohort共26世界，不提前读取测试结果选择模型。固定首机会B1、真实联合task/责任生命周期、期限64、counterfactual标签/强简单规则均原样。宿主执行秒改变只作调度限额，不作科学方法速度收益。原raw保持local，归档压缩/逐文件hash后供root独立复核。
