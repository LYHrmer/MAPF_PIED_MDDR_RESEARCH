# R13 Astra 三线非盲后评

2026-10-04，实际 GPT-6-Astra / ultra。本人实现主线，独立读取查询与第三线的完整结果及根审计；这是知晓结果后的技术判断，不是独立盲审。事前判断保留于 [ASTRA_PREEXEC](ASTRA_PREEXEC_20261004_R13.md)，本轮没有按 TEST 追加训练或实验。

本轮三条线都完成了实际推进。主线的信息接口已落地，查询模型在真实晚点实际激活，第三线完成作者异图的合法执行。科研判断仍应分开：查询的 full 尚未超过固定 LD；去概率特征模型存在一个家族贡献的小时间收益；第三线有真实的采用价值正负例，但还没有学习或付费证据价值实验。我支持继续做条件价值学习，当前最有意义的工作是明确它利用了什么信息、改变了哪个真实选择，而不是扩大网络。

## 主线：完成了信息接口收束，未产生新的性能优越性结论

原 12 臂、16 tick、供给和收费合同保持。正常 END 的公开接口仅携带完整身份、公开时刻及确认状态；完整 SOURCE/history、精确重建和缓存留在私有 verifier；调度器使用合法公开状态；付费 POSITION 仍经原独立证据通道安装。编译负控、身份/时点拒绝和真实开放 SOURCE 读取检查已完成。12 臂与 R11 的 1,388 个非费用/host 事件相等，18 个 guest ELF 隔离重编一致，根逐段/逐作业费用及 14,948 个父文件保护复核通过。依据为本机 ignored 工件：[REPORT](</home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/information_separation_20261004_r13/REPORT.md>)、[ROOT_COMPARE](</home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/information_separation_20261004_r13/ROOT_COMPARE.json>)。

这是受信 guest 内的类型/能力合同，不是硬件隔离或抵抗任意恶意 native 的证明。旧 selector 没有实际消费开放进度，不能倒推此前发生了性能性泄漏。Normal SOURCE 的真实读取和核验仍计费；两条不同身份开放历史的公开投影检查也不是同身份任意替代世界的非干扰证明。每 agent 保留完整最新 history/root，空间仍 O(H)，未测峰值字节；服务时清理动态内容的事实不能扩大为全部 guest 内存释放。

Natural actual 相对 R11 六个输入的增量为 `+2638300 / −26692 / −3430675 / −649588 / −607428 / +3368044`；Strict charged 容量段增量为 `0 / −1 / −2 / 0 / 0 / +1`。费用有增有减，不称统一加速。长例仍各完成 4 项，paid 的服务时刻和由 50 降到 44，但增加 Natural actual 122,869,778；这是认证放行的时间—费用取舍，未证明净效用或 WAIT 信息论上完全未知。原复制 runner 缺少每条命令执行前的源码/ELF 快照；完整收据、运行时绑定及隔离重编补强实际执行证据，显式 POSTRUN 归档不能补写成事前快照。该限制已保留于报告。

下一步主线应把已分离的信息合同接到共同选择点，并计入真正参与决策的读取、核验、特征、推理和复制费用。继续只做初始化微优化，已不是最有价值的主要研究推进。

## 查询线：学习真实激活，但任务收益由固定 LD 同样解释

160 次 native 全部完成：64 次 TRAIN/CAL 完整 C/LD 后果、96 次 TEST，原物理审计、根完整宏/尾策略审计和导师独立标签/系数/部署复算通过。12 个 TRAIN 族的 24 个预算上下文中，LD−C 任务标签为 3 正、19 零、2 负；CAL 冻结 margin 0.1。full 在 TEST 实际调用 16 次，选择 10 LD / 6 C，执行 20 个 SKIP，不再是 R12 的全部回退。完整证据：[REPORT](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/late_budget_choice_20261004_r13/REPORT.md)、[根 TEST 复算](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/late_budget_choice_20261004_r13/ROOT_TEST_RESULTS.json)。

| TEST 策略 | 全 FIFO 完成任务 | QUERY | 相对固定 LD 的前四 FIFO 时间收益 |
|---|---:|---:|---:|
| condition | 712 | 192 | [−4.965087, −4.963686] |
| 固定 LD | 713 | 192 | 参照 |
| TRAIN 预算查表 | 712 | 192 | [−6.363696, −6.362295] |
| full | 713 | 192 | [−0.000700, +0.000702] |
| no_history_prob | 713 | 192 | [+0.713076, +0.714478] |
| 整程 WAIT | 708 | 0 | [−86.398245, −86.396848] |

正时间收益表示更快；区间是数值记录精度界，不是统计置信区间。实验单位是 8 个登记 TEST family，各重复 B8/B16，不能写成 16 或 96 个独立样本。这 8 个 family 来自两张地图各自 scenario-2 的不同任务行块和独立误差 seed，不是 8 份独立官方 scenario 文件，也不是文件级或跨地图留出；不能据 family 数量直接赋予更强的统计独立性或泛化资格。预算是外部给定，模型改变其分配位置，未学习总预算大小；192 次 QUERY 也不是主线实际生产费用。

full 相对 C 多 1 项且时间改善约 4.964，任务增益来自 `random132301/B16`，固定 LD 同样取得。full 相对 LD 的两项时间差——`random132302/B8` 快约 0.5834、`random132304/B16` 慢约 0.5834——在总和中相抵。不能把总和近零说成所有轨迹相同，也不能把相对 C 的增益全部归给条件模型。B8 时四种主动选择均 356 项、C 时间最好；B16 时 LD/full/mask 为 357 项，C/查表为 356 项。这说明冻结 TRAIN 查表未泛化为稳定的预算规律。

no_history_prob 与 full 有 3 次选择分歧、1 个完整服务记录变化；额外收益来自 `empty131303/B8` 避免一次约 0.7138 的损失。其相对固定 LD 的总时间正向应保留，是一个有限的条件选择信号。但它没有新增任务收益，也未形成广泛家族优势，不能见 TEST 后升格为已验证最佳模型。该消融仅移除概率及其结构乘积两个槽，eligibility/rank/尾策略仍用历史；不能说整个历史系统无用。

根的 [冻结分数诊断](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/learned-query/exploration/learned_query/late_budget_choice_20261004_r13/ROOT_MODEL_DIAGNOSTICS.json) 显示：固定模型与阈值下，事后删除时间项使 0/32 个选择改变。这不是重新训练的时间头消融，却足以限制本轮归因——尚不能把实际选择收益归给时间价值头。任务差主要为零而回归任务分数仍主导阈值，是下一轮值得识别的问题；没有证据表明换大网络即可解决。

我的最小推进建议是保留 C/LD 完整宏和强对照，在新 TRAIN/CAL 明确比较当前联合分数与一种任务风险校准后处理近似任务持平情形的时间选择规则；容差、校准和目标权衡必须先定，不能用真实 TEST 任务标签触发规则。固定 full/mask、C、LD、WAIT 继续留在独立新 family 测试中。先检验新增时间选择是否改变实际动作，并在任务主项不被掩盖时胜过固定 LD；此时才讨论扩大容量。现有数据足以支持继续检验，不足以支持普遍的预算学习优势。

## 第三线：已形成真实采用后果，下一步先过有价证据接口资格

24 次作者 GSES/Improved GSES 调用全部返回且实际采用不同图，36 条 continuation 的事件/资源及根精确连续几何核验通过。真实采用下 ΣT 有 18 改善、6 退化，收益范围 −17 到 +53；makespan 为 0 改善、12 退化、12 相等。所有 random 配对都是 ΣT 改善而 makespan 变差，不能只挑一个指标概括为全面改善。这里只是 2 个原作者实例、12 个 checkpoint/profile 上下文，尚无学习与独立新实例泛化证据。依据：[REPORT](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/gses_online_adoption_20261004_r13/REPORT.md)、[独立配对结果](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/explore/error-aware-guidance/exploration/error_guidance/r13_root_review/ROOT_PAIRED_RESULTS.json)。

对于当前固定批次，我建议下一合同以平均完成时间 ΣT/n 为主，并单列事前固定的 makespan 容许退化条件；费用用硬预算/Pareto，暂不把 host 毫秒任意兑换成物理完成时间。当前求解期间虚拟时钟冻结，不能主张异步求解延迟已经被处理。

三 option——继续原图、公开信息调用、付费证据后调用——值得实作，但它们是否真正不同尚待验证。本次 [近邻全文与源码核查](NEIGHBOR_METHOD_AUDIT_20261004_R13.md) 发现两个具体入口问题：作者权重虽然是 float，冲突/启发式仍含单位间隔假设；当前适配器又要求 public 包完全等于自身序列化结果，不能直接塞入修改后的证书估计。第一版应明确 public_base / verified evidence / search_view，仅用事前确定的整数残余估计影响候选评分，lift 恢复原执行 type1/current 与所有 active guard。POSITION 不能替代实际 ARRIVE；粗占用本已公开，整数取整还可能抹掉证书全部增量。

所以接下来先做少量完整成对机制运行，记录证书、量化权重、作者候选、实际采用后果这四层是否变化，再采集新实例完整 option 标签训练。若公开调用与付费调用完全相同，应如实报告信息或量化瓶颈；早释放或小数权重都需要另立适配与正确性合同。这个前置工作能直接决定学习对象是否存在，胜过在尚未接通的接口上堆积标签。

## 本轮后的优先级与论文边界

我的优先次序是：先让主线合法证据实际影响作者候选的评分并保持原承诺，再用完整后果训练小型条件选择；查询现有 C/LD 学习作为并行可复现实验，检验稀疏任务信号与时间头的可辨识作用。三线已经各补上了实质环节，但不能将三套执行器、QUERY 次数、host 时间和 guest 收费直接合成一个已完成的端到端净收益结果。

最近邻已经覆盖完整 SOC 标签的重规划门控，以及执行时间预测驱动的固定路径重排；Should I Replan 还额外报告求解开销。可争取的贡献应落到有限有价物理证据怎样改变执行承诺约束下的完整决策价值。原作者 Improved GSES 是当前可立即复现的正式外部锚点，公开信息价值门控还需最近学习方法的公平适配对照。现有结果支持持续推进这个问题，不支持仅凭工程完成量、合成样本数量或期刊目标宣称论文贡献已成立。
