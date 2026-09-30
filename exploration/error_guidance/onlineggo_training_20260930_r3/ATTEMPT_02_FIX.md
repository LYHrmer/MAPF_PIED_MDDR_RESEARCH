# 保留首次接线失败后的固定重试

首次attempt在gen0首次收集future时抛AttributeError：多个线程首次加载官方config.py，
一个线程读到了sys.modules中尚未完成定义的模块。原200项均已提交，ThreadPool上下文
等待已排队任务后才退出：158次native完成、42个目录在写job前失败；无tell、无训练checkpoint。
原脚本、training/事前冻结及全部raw保留，不纳入正式训练结果。

另外，兼容性单项检查发现作者自定义GridArchive.best_elite()读取旧私有字段
`_objective_values`，而作者要求的pyribs0.5已改字段。它是我们新增日志/选择调用，
尚未在首次attempt训练中执行。第二次仅改读取为pyribs0.5自己的best_elite property fget，
仍取archive最高objective，不改官方四个类源码、ask/tell、训练目标或选择准则。

common_v2在协调主线程一次调用原gen_sim_kwargs，得到固定template；每个worker复制
字典后只设同原规则network_params/seed/save_path。train_v2保留原协议、seed和200候选预算，
独立training_02/及raw attempt02。异常会取消尚未开始的future，再等待已开始进程退出。
没有使用首attempt吞吐选择参数、改预算或改场景；留出尚未运行。
