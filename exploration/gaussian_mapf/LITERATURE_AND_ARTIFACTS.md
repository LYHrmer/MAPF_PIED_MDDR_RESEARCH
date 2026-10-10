# 文献与作者工件核查

核查日期：2026-10-10。仅选与本次决策直接相关的锚点，不替换已有五篇或拟选 55 篇综述，不以文献数量推断录用率。

## 文献定位

| 文献 | 用途及边界 |
|---|---|
| Theurkauf 等，Chance-Constrained Multi-Robot Motion Planning under Gaussian Uncertainties，IEEE RA-L，2024，9(1):835–842 | 高斯支线的外部方法候选。连续动力学 MRMP/CBS，不能不加说明地当成标准网格 MAPF |
| Okumura 等，Concrete Multi-Agent Path Planning Enabling Kinodynamically Aggressive Maneuvers，npj Robotics，2026 | MAPF-X：直接检查图上 MAPF 与学习的执行不确定性接口；学的是偏离/耗时分布，与逐时刻位置高斯不是同一对象，也不是 RL |
| Cheng 等，Scalable and Safe Multi-Agent Motion Planning with Nonlinear Dynamics and Bounded Disturbances，AAAI，2021 | S2M2：有界扰动进入多机器人规划的正式先例，说明有界模型可用于规划论文；这是会议论文 |
| Safe Multiagent Motion Planning Under Uncertainty for Drones Using Filtered Reinforcement Learning，IEEE T-RO，2024 | 支持学习与传统安全处理结合的可行性；无人机连续运动规划，只作方法迁移，不作本项目查询/MAPF 基线 |

来源：

- CC-K-CBS：[作者全文 v4](https://arxiv.org/html/2303.11476v4)、[作者项目](https://justinkottinger.com/projects/CCK-CBS/)、[正式论文 DOI](https://doi.org/10.1109/LRA.2023.3337700)。v4 §II-D 式 (6a) 的风险按机器人和离散时刻定义；§III-A 的预期状态协方差并非只有在线滤波协方差。不同稿版公式编号可能变化。
- MAPF-X：[期刊页面](https://www.nature.com/articles/s44182-026-00083-2)、[作者项目](https://proroklab.github.io/agile-mapf/)、[作者仓库](https://github.com/proroklab/agile-mapf)。本轮期刊页面直接提取失败，作者项目/工件与独立核查用于交叉确认；没有核定新刊影响因子、SCIE/JCR 状态，不据 Nature 品牌称其“已核顶刊”。
- S2M2：[AAAI 正式记录](https://ojs.aaai.org/index.php/AAAI/article/view/17340)、[作者实验与模型说明](https://aeroastro.mit.edu/realm/research-blogs/scalable-and-safe-multi-agent-motion-planning-with-disturbances/)、[作者仓库](https://github.com/jkchengh/s2m2)。
- Filtered RL：[研究机构发表与全文入口](https://merl.com/publications/TR2024-048)。

## 作者工件固定版本

### CC-K-CBS

- 官方仓库：<https://github.com/aria-systems-group/Chance-Constrained-K-CBS>。
- 固定提交：[`58f152dcbb4c549261c0cd250079ea188c1d8eb8`](https://github.com/aria-systems-group/Chance-Constrained-K-CBS/tree/58f152dcbb4c549261c0cd250079ea188c1d8eb8)，提交时间 2023-12-28 UTC；检查时默认分支 `main`。
- GitHub 许可标识：GPL-3.0。拟复用源码前须按该版本许可要求处理，不直接混入现项目。
- 固定版本 README 明确依赖 OMPL，且区分本方法与另一仓库中的普通 K-CBS。仓库含 CMake/Docker 入口；具体依赖版本、构建命令和最小科学运行仍需逐项核对。
- 扩展点先从论文的 `validatePlan` 概率冲突检查与约束生成对应关系查起；尚未完成代码调用路径审计，不宣称已有兼容接口。

### MAPF-X / agile-mapf

- 官方仓库：<https://github.com/proroklab/agile-mapf>。
- 固定提交：[`8eda15f0b8384f195ccb65a2eac910bf2aa094c8`](https://github.com/proroklab/agile-mapf/tree/8eda15f0b8384f195ccb65a2eac910bf2aa094c8)，提交时间 2026-03-13 UTC；检查时默认分支 `mapfx`。
- GitHub 许可标识：MIT。
- 固定版本 README：C++17、CMake≥3.16、yaml-cpp、Eigen3；核心用 argparse/cnpy 子模块，openFrameworks 可视化为可选依赖。
- 文档构建入口为 CMake，测试入口为 CTest，主程序 `build/main`；图示例 `assets/example-graph.txt`，学习模型示例前缀 `assets/robomaster_example_model/best`。
- 先审查动作模型输出怎样进入占用、边耗时及冲突判定。作者 README 指向 `action_model_torch.cpp`；未完成源代码/最小运行验证，不宣称已复现。

## 核查限度

两个作者工件均未克隆、构建或执行。本轮核验了远端身份、commit、许可标识和 README；具体许可证全文适用、递归依赖固定版本、场景输入与运行验收尚待后续确认。作者仓库存在不等于官方工件 R0 通过，两个候选都保持 `UNKNOWN`。

文献能证明已有相关方法，不能证明我们的待研究差异具有新意，更不能证明某种模型更容易录用。后续只查能够决定这条支线去留的近邻和接口，不重开整个项目的全面审查。
