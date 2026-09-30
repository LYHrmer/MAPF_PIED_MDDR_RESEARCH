# 官方 OnlineGGO：首次真实训练与独立留出

已完成原作者规模800机器人、1000步的有限预算训练：2代、5个CMA-ES emitter、
200个560维quad参数候选，每候选两个训练种子，共400次真实native。
固定训练最优checkpoint后，初始全5与已训练权重各运行三个独立留出种子。

| 留出任务seed | 初始权重吞吐 | 训练权重吞吐 |
|---|---:|---:|
|930101|8.814|11.509|
|930103|9.056|12.050|
|930107|8.878|12.055|
|均值|8.916|11.871333|

吞吐是1000步内完成任务数/1000；平均增加2.955333，即约33.1%。
这是**已发表作者学习方法相对自身初始化**的结果，不是我们新方法相对GPIBT的优势，
不含执行误差、连续机器人或查询机制，不据此宣称论文创新、跨地图泛化或统计显著。
作者配置训练10000候选，本次200候选，仍不是完整论文R0或收敛性能。

官方来源[OnlineGGO](https://github.com/zanghz21/OnlineGGO)，固定
`ff6d830e2fd5bf85ccbb72eaec0fb8df1cf1c256`。原sortation_small.gin配置与map、
quad560/流量输入、5 emitters×20、sigma5、ranker=obj、selection=mu、restart=basic、
2次评估取mean、初始5、float32 archive保持。四个官方类完整加载且未修改；
原gen_sim_kwargs方法由其源码AST执行，config.py默认值直接加载。
协调器使用本机进程池替代Dask，每次native新进程；运行前协议和源码SHA保存在
`training_02/freeze.json`。初次线程首次导入race被保留后修正；所有首次158个实际native
与42个写job前失败均保留，不进入第二次训练目标。未根据首次吞吐调参。

原CMA重采样100次后仍可能有越界参数；第一代9233个分量低于0.1等范围边界，
保持作者默认行为，没有按收益裁剪。原GridArchive旧best_elite辅助函数与pyribs0.5
私有字段不兼容，第二次只用pyribs0.5原生property读取同一archive最大目标；
ask/tell/排名/选择均不变。纯优化器ask/tell后标准pickle与cloudpickle往返实测均通过；
本机完整优化器checkpoint保留，公开权重和所有候选/目标足以核对本次选择。

第一代最高训练均值10.822，第二代12.1475；最终仅按训练最高值选择一次checkpoint。
`training_02/trained_checkpoint.json`是实际已训练权重，不是预先填好的trained标签。
三个留出seed没有进入400次训练seed，留出未参与选择或追加训练。
原生作者代码部分使用random_device，同任务seed不意味着全部内部随机性严格配对。

`audit.json`从原始job/result/receipt重新核全部400次训练目标与权重、最优checkpoint、
留出隔离，核939个官方Git blob字节保持（包括3个symlink）；3个Git子模块引用单列，
没有谎称再次完整核验子模块内容。原native binary沿用R2已审计OBJECTIVE4构建；
系统Eigen3、Python3.10/NumPy1.26.4/Numba0.60.0与作者容器差异披露。
gin-config0.4.0、pyribs0.5.0版本保持。环境仅写本机隔离venv。

六条留出完整轨迹由独立Python重新执行480万动作/4804800联合位置，核地图通行、
顶点冲突、交换冲突、任务唯一归属/FIFO/实际目标位置/完成时刻，所有结果通过；
每次仍有800项未完成任务，未丢弃。训练400次依赖作者原生结果与退出/身份核验，
没有宣称所有训练轨迹也做了独立逐动作重放。

`native_evidence.tar.gz`保留两attempt的精确job、原stdout/stderr、result、receipt和全部
留出/运行量测trace；`native_archive_manifest.json`逐文件绑定。源码/协议/候选/统计
直接可读，`upstream_context`附作者配置/核心类/地图/MIT许可。独立audit两次源文件类型
处理错误已记录，修复仅离线验证器，没有重跑训练或选择性重跑留出。

这一步关闭“只有模型入口，没有实际训练”的缺口。下一步在共同执行误差接口上比较
冻结的官方学习对照、官方GPIBT、同信息解析/历史预测消融，以及独立训练的剩余占用
时间或阻塞传播残差模型。该新模型尚未在本包训练，不能把作者复现收益归给我们。
