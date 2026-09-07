# 72L3：根不用skill的近邻比较范围与独立来源复核

2026-09-07，BOUNDED PRIMARY NOTES / NONBALLOT。固定72不修改；不是新候选或正式逻辑审查，不生成/读取受限载荷，不实现/构建/测试/仿真/调参，保护参数未赋值。以下为本轮根实际访问，旧全文阅读身份不因本轮窗口阅读而重计。

| 一手来源 | 本轮实际阅读范围及结果 | 限定比较依据 |
|---|---|---|
| [Zhong/Rossi/Shell，Planned synchronization](https://link.springer.com/article/10.1007/s10514-025-10225-4) | 官方714行HTML，本轮open返回L0–208；定点find返回§6.1相关L495–530及结论L539–544；并非本轮新读全文或公式版面审计 | 已有动作/观察/重排成本和全状态check-in的MDP。§6.1处理不一致观察及观察耗时，故不能称其只会处理完美反馈。结论列选择性部分观察为未来方向。 |
| [Liu等，Robust and effective multi-agent path execution with timing uncertainty](https://www.sciencedirect.com/science/article/abs/pii/S0004370226001128) | 直接正文open Internal Error；DOI检索实际返回官方摘要/预览、题名及AI358 article104586；未读全文 | 预定路径的延迟执行，联合选择移动集合及剩余执行可行性检查值得核；未核空间包络、可信观测费用或完整可适配算法。 |
| [Wang等，Protocol-observation discrepancy calibration](https://www.sciencedirect.com/science/article/pii/S0921889026003726) | 直接open Internal Error；DOI检索实际返回官方摘要/引言/方法与结论片段；未读全文 | 类型化占用/预留/队列/进度差异与局部恢复是直接近邻。片段不能证明其对延迟可信消息、持续实体占用的保证或缺失；不引用所列性能数字为已核实验。 |

根独立判断：这里真正影响可比性的是输入和允许动作的映射，而不只是都出现“付费观察”。固定72的查询者只持历史证据及下界，决定一次POSITION对象，不能另选新MOVE。若一个比较方法需要当前联合状态、状态转移概率和联合动作控制，直接给它这些输入会增加权限；把它换成只选择观察的belief模型又是新适配，不能继续称原论文原算法。两种映射均须有单列定义和能力对等，当前均未构成现成的同域已发表基线。因此M03/NR3继续UNKNOWN；可以借用信息价值和计划观察的结构，但不能将这些概念据为首创，或用仅标题相似就否决全部组合。

一个根自行给出的输入区分论证：存在两条已交付账本完全相同、但隐藏物理进度不同的历史；72查询策略必须给相同选择。一个读取当前联合状态的控制律可能区分它们。这个可能性足以否定“接口当然相同”的无证推断，但不证明任何具体已发表策略在这两条历史必给不同动作。没有由此构造论文不存在的算法行为或声称新颖性空白。

## 根独立复核72L2中的两个固定源对象

根通过GitHub只读工具实际取得固定R0 commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357 的README与LICENSE完整内容，逐字读完。对工具返回UTF-8字节只作内存身份计算，未写源文件、未执行README中的任何命令；所得Git blob hash与72L2固定tree一致。

| 对象 | 根实算bytes/换行数 | 根实算SHA256 | 根实算Git blob |
|---|---:|---|---|
| [README.md](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/README.md) | 2730 / 86 | 335709410787bf335fadedcfc514b8f722d66ab6d9c0785c52992ca24d90738b | a4578f87f918dab4b67b50cd404e3ec901a8f636 |
| [LICENSE](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/LICENSE) | 1084 / 21 | f7f63f9810a4de1d4db59c034bcbbb5f33aa8ec3a1c07b21e774033f6bac2a94 | 1f4b6eadac278447824a47d409bb4de04ea7f3ee |

根确认README链接与MIT文本的有限结论。素材覆盖仍未获证，不推出无许可或违法；未读地图、配置、任务或delay载荷，也未核上游对应字节。README末尾对dummy goal/消失的说明是来源文字，不能替源调用链或把真实实体从本实验世界删除。

本轮搜索也返回若干二手聚合站，未用其内容支持技术结论。全部访问成功/失败范围已区分；没有收到旧69L1/69E1原回执，本文不替代它们。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。
