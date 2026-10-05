# 付费执行信息的聚焦新颖性检查

2026-10-05，约5分钟聚焦检索；只读 primary sources，没有新增实验，也不是系统综述。检索组合覆盖 MAPF/LMAPF execution、costly observation、value of information、selective communication、event-triggered communication、delayed information/replanning，并追到以下四项原论文／作者机构记录。

**结论：不能主张“首次在多智能体执行中权衡通信代价和延迟”，也不能主张“首次只获取会改变决策的信息”。** 下表已有明确近邻。本次没有核到完全覆盖“固定路径、可切换依赖组、付费且有年龄的当前位置、送达时刻活动承诺、完整尾部收益”的同一实现；这个检索范围内的缺项不是首创证明。

| 最接近来源 | 已经做过、对本计划的直接挑战 | 与当前拟议问题的差别 |
|---|---|---|
| Bhargava, Muise, Vaquero, Williams，*Managing Communication Costs under Temporal Uncertainty*，IJCAI 2018 | 给定不确定时序网络，选择观察延迟函数以最小化通信成本，同时保证原时序计划的 delay controllability；采用冲突驱动搜索。明确讨论及时消息昂贵、延迟消息较便宜乃至不发送。这是“合法计划＋有代价／有延迟的执行信息”的最直接理论近邻。[正式全文](https://www.ijcai.org/proceedings/2018/0012.pdf)、[MIT作者稿记录](https://dspace.mit.edu/entities/publication/81756d24-5475-4cb4-b506-06d39107720d) | 主要目标是通信成本下的时序可控性，不是 MAPF 固定路径可变通过次序的期望 ΣT；没有因此证明其已实现按当前位置查询的同预算协议。本轮未核作者实现。 |
| Ma, Luo, Pan，*Learning Selective Communication for Multi-Agent Path Finding*（DCC），作者列 RA-L／ICRA 2022 | request-reply 通信；通过邻居是否改变本 agent 的决策来选通信对象，在训练和执行时均使用。因此“决策相关才查询”“学习 STOP／不通信”的宽泛思想已有先例。[作者预印本](https://arxiv.org/abs/2109.05413)、[作者发表列表](https://miyunluo.com/)、[原代码和模型](https://github.com/ZiyuanMa/DCC) | 是部分可观测 MAPF 的学习动作策略与通信联合设计，不是给定路径上的 SADG 顺序优化。已查材料未给出当前提议的送达后可切换集合、持续活动承诺和真实工作费回执；不能因此断言其所有版本都没有延迟／成本。 |
| Ma, Kumar, Koenig，*Multi-Agent Path Finding with Delay Probabilities*，AAAI 2017，Minimal Communication Policies | 已沿计划关键依赖执行，只发送保障下一位置可进入所需的状态消息，并比较消息量和实际执行 makespan。路径／冲突结构筛通信机会并非新方向。[正式论文](https://ojs.aaai.org/index.php/AAAI/article/view/11035)、[全文 MCP 小节](https://ojs.aaai.org/index.php/AAAI/article/view/11035/10894) | 这些消息主要用于依赖释放与安全推进，传递已完成状态；当前 END 保持公共且查询只改善代价估计。它不是“付费 POSITION 能否值得改变未来方向”的同一控制问题，但必须交代边界。 |
| Ren, Li, Huang，*Dynamic multi-agent pickup and delivery under communication uncertainties in robotic cellular warehousing systems*，Transportation Research Part E 212，104900，2026 | 作者机构摘要确认位置相关随机传输延迟、通信感知 token passing，以及按收到更新的时间和位置调整重规划；挑战“首次将通信年龄纳入动态 MAPD 决策”的表述。[作者机构正式记录](https://research.polyu.edu.hk/en/publications/dynamic-multi-agent-pickup-and-delivery-under-communication-uncer/)、[DOI](https://doi.org/10.1016/j.tre.2026.104900) | 订单更新、任务协调和路径重规划同时变化，并非固定路线上的顺序选择。本轮全文入口读取失败，仅据机构摘要确认这些内容；未核其精确事件触发式、通信成本函数、源码或 VOI 目标，不能作更强排除判断。 |

`NEXT_METHOD_PLAN.md` 可继续作为**待验证的方法问题**，但建议把贡献收窄为可测的实现与决策条件：查询捕获到送达期间执行不停，已承诺动作不撤销，候选方向可能在等待中消失；用同一执行内核评价这些条件下的近似期望尾部改善与实际查询工作费。这里“查询价值”本身不是新颖性，DAG 结构筛选本身也不是新颖性；必须说明相对上述时序通信成本、决策因果通信和依赖消息方案，新增了哪些状态／约束以及何种可证或可重复的改进。

最小额外对照设计应先来自这些近邻：保持原安全核和全部公共 END，增加“预测的最优合法方向是否改变”的简单决策差异查询规则，以及仅按关键依赖发送信息的结构控制；明确它们是**受文献启发的本任务适配消融**，不能冒充运行过原作者算法。外部真实调度对照继续按 `EXTERNAL_BASELINE_NEXT.md` 先审既有 ImprovedGSES wrapper。若后来声称低成本通信的理论性质，须专门比较 IJCAI 2018 的成本与可控性模型；若声称 LMAPF，须另做在线任务实验。

边界：未查到同一组合不等于没有，尚未完成系统文献检索、全量引用追踪或上述新文全文审阅。本轮 TEST 不据此改参数；所有建议仅用于下一轮登记。
