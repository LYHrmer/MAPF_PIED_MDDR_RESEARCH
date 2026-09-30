# 2026近作核查：收窄贡献与基线候选

核查日期：2026-09-30。这是两项定向更新，不是穷尽查新；论文事实来自作者原文、期刊页面及作者仓库。下文研究取舍是本项目判断。

| 近作 | 已核事实 | 对本项目的直接影响 |
| --- | --- | --- |
| Zheng等，Learning-guided Prioritized Planning for Lifelong Multi-Agent Path Finding in Warehouse Automation，JAIR 85，2026，DOI 10.1613/jair.1.20611 | RL-RH-PP把动态优先级建模为POMDP，以注意力网络自回归产生排序，再由滚动PP规划。期刊身份、原文和作者代码入口均已核验。 | 不能以“学习动态优先级＋lifelong规划”作为独立创新。若改做优先级学习，它是需要正面对照的近邻；当前执行残差引导路线先保留OnlineGGO作为学习对照，避免无条件增加不同作用层的算法。 |
| Liu等，Robust and effective multi-agent path execution with timing uncertainty，Artificial Intelligence 358:104586，2026年9月，DOI 10.1016/j.artint.2026.104586 | 作者和出版社确认发表信息。论文在预定路径上用Location Dependency Graph及剩余执行可行性测试协调并发运动，应对未预期延迟；是SoCS2024工作的扩展。 | “动态组合放行”“执行延迟下维持可行性”已有直接工作。主线须解释空间占用承诺、有限证据及真实查询成本与该问题的差异。它可进入执行层基线候选清单，作者代码与同接口复现尚未核验，不能填写为已运行基线。 |

RL-RH-PP证据：[期刊页面](https://www.jair.org/index.php/jair/article/view/20611)、[作者原文](https://arxiv.org/html/2603.23838v1)、[作者仓库](https://github.com/MikeZheng777/RL-RH-PP)。仓库公开训练入口、地图与网络代码；本轮没有克隆、构建、训练或验证其权重。网页存在不等于已完成R0。

LDG执行工作证据：[出版社摘要及章节预览](https://www.sciencedirect.com/science/article/abs/pii/S0004370226001128)、[作者主页发表记录](https://www3.ntu.edu.sg/home/asxytang/)。本轮核对摘要、问题设定和方法概述，未声称已逐页读完付费全文。作者所述冲突/死锁保证不能直接转移为本项目连续空间误差保证。

据此，三线的问题应保持明确：主线补齐可计费的安全执行反馈；查询线检验同容量、同公开任务下的信息价值；替代底座线检验解析运动与等待模型之外的执行残差能否改善实际任务完成。世界模型、RL或GNN只在这些具体问题需要它们时引入。

实验继续采用两层记录：作者原生R0；公开全部适配的共同执行环境R1。GPIBT配LSMART是R1组合，LSMART是试验台；内部AR/lag2/RR/admission属于预测器或消融，均不充当已发表的竞争方法。新近作不改变本轮冻结的小规模实现参数，也不触发无目标的大规模扫参。
