# OnlineGGO：官方学习代价评估器已构建，训练策略仍待权重

2026-09-30 第二轮。此前仅有 OBJECTIVE=3 静态程序；本轮在独立目录实际构建官方 **OBJECTIVE=4 / OBJ::NN** 的 Python绑定，运行作者原生 `set_network_type → set_network_params → plan → network.forward` 路径。未修改算法源码。它补齐学习策略评估的执行入口，尚不构成已训练 OnlineGGO 外部基线。

来源：[AAAI2025论文](https://ojs.aaai.org/index.php/AAAI/article/view/33614)、[官方仓库](https://github.com/zanghz21/OnlineGGO)，固定 `ff6d830e2fd5bf85ccbb72eaec0fb8df1cf1c256`。按作者 compile.sh 的 neural/no-LNS 设置编译，使用既有系统Eigen和固定官方pybind11/MiniDNN；submodule、源码和二进制身份见 [source identity](raw/source_identity.json)、[binary identity](raw/binary_identity.json)。配置1.130秒、构建33.057秒，均在120秒事前上限内。宿主时间只描述构建成本，不作为算法性能。

## 实际执行和独立核验

输入为此前归档的原作者 GPIBT `visualizer_example_sts.json`：33×57 sortation地图、10机器人、原起点/任务、reveal=1、100离散步。这是公开输入上的评估器资格试验，**不是 OnlineGGO 原论文实验配置或共同连续误差比较**。一个明确未训练的560值常量向量（全5，作者优化初始化均值）用于接口诊断；另一个559值向量由官方程序拒绝。常量向量不占论文外部基线结果栏，不声称学习收益。

有效接口运行完整产生1000动作、1010位置、27个真实任务完成与10个截止待服务任务。独立重放边界、障碍、邻接、顶点、反向交换及原roundrobin分配/服务，匹配全部实际任务事件和目标。未采用上游 AllValid、空errors或硬编码 MAPF_T 标签为安全证据。只验证离散轨迹；不外推连续空间误差安全。原优先级仍使用random_device，没有确定性配对或跨算法排名。

首次两个smoke在不存在的输入路径处失败，尚未进入网络形状检查。保留全部失败日志；修正为已经归档且逐字节核验的公开作者输入后，第二次无效形状明确输出“should be 560, but receive 559”，有效运行正常结束。没有删除失败、扫参或选最好一次。

[audit.json](audit.json)及[audit.py](audit.py)另外拒绝8种权重身份负例：形状错误、boolean、非有限值、缺来源、hash错误、train/test重叠、作者版本错误、权重缺失。权重检查只核所提供的元数据/参数，不自动认证其训练过程。

## 训练权重缺口与下一步

固定仓库tracked文件中未发现 `optimal_update_model.json` 或训练checkpoint；[官方README](https://github.com/zanghz21/OnlineGGO#evaluation)说明从训练日志提取参数，[release页面](https://github.com/zanghz21/OnlineGGO/releases)暂无release资产。此结论只覆盖本次检查范围，不能据此断言作者从未在其他渠道提供权重。不能用随机权重、手写参数或静态OBJECTIVE=3补位。

已经提供严格[evaluator入口](preflight.py)：`evaluate` 必须显式给出 `--weights`、`--provenance` 和新的 `--job`，随后使用本次已核身份的官方NN模块；缺失权重立即失败。当前支持输入固定100步，正式R0仍须匹配训练配置、核实际日志与留出，并使用原文所需负载/时间预算。后续选择是取得可核作者权重，或预注册作者训练流程和足够预算后实际训练；不可把本次常量诊断写为训练完成。

本机二进制保留在主仓库 ignored `implementation_binding_evidence/onlineggo_neural_r0_20260930_r2/build_nn`。公开包交付事前协议、构建/执行脚本、许可证、源码/配置/二进制SHA、所有失败与成功raw及独立重放。它是第三线可信学习基线的具体前置进展，未锁题或宣称方法优于已发表工作。
