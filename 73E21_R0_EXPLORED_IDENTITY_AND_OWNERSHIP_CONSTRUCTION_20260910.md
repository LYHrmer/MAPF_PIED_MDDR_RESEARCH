# 73E21 固定 R0 的 EXPLORED 身份与唯一对象归属构造

状态：NO-SKILL / CONSTRUCTIVE / NONBALLOT；2026-09-10。本件不是正式逻辑审查或资格票。保持 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。只核本题固定源及直接键依赖，不实现、构建、测试、仿真或生成任何实验载荷；没有保护参数赋值，没有修改 73、行政页、Git、桌面或旧完成件。

## 1. 结论与唯一修订选择

选择继续明确标识的修订版 R0：**统一后继 flags 与索引键、修正键等价、将唯一对象归属从 EXPLORED 索引中分离、给构造和全部退出建立同一清理责任**。不建议仅把 L232 的 H 改成 H_new 后就宣布通过，也不因这些局部问题直接换一个未经核验的新来源。此包改变搜索去重行为和实际成本，必须成为各臂共用的源修订，不能把收益归到 D 的观察策略。

固定源码明确有三个互相关联的缺口：查找用的 flags 不是新节点构造后的 flags；插入用父节点的键指向新节点，破坏键与值的对应并丢失清理入口；RCEqual 忽略两键 flags 而 RConfigHasher 使用 flags。另两处 deadline break 都越过了已 pop 的 L 的 delete。它们分别是身份、归属和退出责任问题，不能合并成“已发生 double-free/UB”。

下面给出单次持有/释放及索引一致性的纸面充分合同；实际修订源码、异常路径和析构行为尚未实施或核验。不由此证明完整 LaCAM 算法、状态合并的语义充分性或 AA 全部继续域。当前其它来源、控制、计量及审查义务保持原状态。

## 2. 原样来源身份与实际阅读

原样来源固定为 YueZhang-studyuse/LMAPF-delay，commit `0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`。本次 API 按固定 ref 取得以下四个源对象；对实际返回内容分别计算 SHA256、bytes/LF，并重算 Git blob SHA1，四者均与 API blob 一致。没有读取地图、场景、配置、agent/task/delay/result 数据载荷或 35–38/Q 限制文件。

| 原对象及一手链接 | Git blob | SHA256 | bytes / LF | 本次实际阅读 |
|---|---|---|---:|---|
| [planner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/planner.cpp) | `4f46f988d2c16f09c5a6f65bb9cd70e8e01aa483` | `8d2fa9131f0691b109a00dd6267b3b48f80df7778643daeb806ff82e20fe2789` | 19115 / 615 | API 全文实际返回；重点逐行核 L3–100、L127–293、L295–391，并核后续函数不回写 goal_index。末行无 LF。 |
| [planner.hpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/planner.hpp) | `48ec12187373e87d6a233bfebea5eaf8b26c9304` | `8e7c6b7221828ef17a73730a3a33c39d5fcc9ccd9f73a6697c7434162ae7312c` | 3850 / 132 | 全文，节点/Planner 字段及析构声明。 |
| [graph.hpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/lacam2/graph.hpp) | `bdf87cf5a1b911c039ebcf10374ddf317086fbd4` | `166b3ecbe68e7ddcd549504044a3c47cc3abb9ca98653b8639a654607480daee` | 1699 / 61 | 全文，仅由 planner.hpp 的键定义依赖取得。 |
| [graph.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/graph.cpp) | `fb8ab481d5b1e3a959a18b826fd5919b69772e7e` | `7bdb71a22dbdf6df873370c20173f0ef9ab97c34fbb649f222c7bcb9fa2813a0` | 4405 / 185 | 只读 L140–185：完整 is_same_config、配置散列、组合散列及中间输出函数窗口；不称全文件科学阅读。 |

本件为定位源路径，另外只检索旧 E18 中 planner.cpp/hpp 的身份行及其邻近命中，不重做 E18。根提供当前 73 为 `c59c96cb29af0f167a8942e26b82ce8f126a83d05167b1537dd477558778ed75`，185290 bytes / 593 LF，以及新增目标解析/puller/交换更新的纸面状态；这些是根提供的当前背景，本件没有读审该新全文，也不把固定原源码当作那些修订已经实施后的源码。

键合同仅补一个规范一手文本：[C++ 工作草案 unord.req.general](https://eel.is/c++draft/unord.req#general)，实际读其 p.3/5/6 对等价、等价键同散列和唯一键的要求。此为维护者发布的工作草案，不是某一已绑定编译器/标准库版本或运行证据。下面只据该要求说明静态合同冲突，不由页面存在宣称本地运行已验证。

## 3. 三个关键构造

**构造一：后继身份的三个不一致点。** get_new_config L339 清零后，L346 将每个 A 的 goal_index 复制为父 H 的 reach_goal；后面的本文件 PIBT/swap 路径只读取它，不因 C_new 首次到达目标回写。solve L202–213 把这些旧 flags 装入 num_reached，再查 (C_new,num_reached)。但 HNode 构造 L59–83 在父尚未到达而 C_new 到达目标时递增 reach_goal，并更新 num_agent_reached。因此首次到达那一步，查找身份和新对象自身状态确可不同；不能把局部变量名 num_reached 当作后继事实的证明。

随后 L232 却以 (H->C,H->reach_goal) 为键存 H_new。若初始 H_init 产生与自身配置不同的第一个可行、未查到的后继 H_new，L140 的初始键会被 L232 的同键赋值覆盖为新指针。这段前提下无需先触发 flags 变化，键已经不再描述其 value。之后如果某候选查到了这个旧键，取得的 value 可以有另一配置；rewrite 接受这个指针并登记 neighbor，代码没有再次核 value 的 C/flags 等于本次候选。它可能因此错认重复状态，不能声称查到的节点一定是那次可行后继。

直接键谓词还有独立问题：graph.hpp 的 RCEqual 在配置相同时比较的是 RC2.second[i] 与其自身；对合法整数 flags 该条件始终为假，所以 flags 不参加相等判定。graph.cpp L174–185 的散列却将逐项 flags 纳入乘积。在同配置、某个非零 vertex id 对应的 flags 不同的键上，谓词可判等而散列不同；例如差异落在最后一个混合分量时，不会被更后面的混合抵消。这违反等价键必须同 hash 的容器合同。是否某次具体运行走到这些键、库如何表现，本件没有运行证据；不能把固定原程序仍当作满足标准容器前提来证明精确运行结果。

**构造二：丢失清理入口不等于重复拥有。** 正常退出只在 L261 遍历 EXPLORED values 并 delete；HNode 析构 L94–100 只删除它尚在 search_tree 队列内的 LNode，不递归删除 parent 或 neighbor。初始节点被上例覆盖后仍可被 OPEN、H_new->parent、H_init 变量或随机重启引用，因此它不是当场悬空指针；但这些都是裸引用，最终没有其它 HNode 删除入口，H_init 及其队列可能漏清理。后续覆盖同一键也可使别的 HNode 从 EXPLORED 清理集失联。

反过来，本文件每个新 HNode 地址仅在新分配分支赋给一个 map value，已有节点的命中分支没有把该地址复制到另一键。若暂以通常容器操作语义分析，values 的地址仍可保持互异；OPEN 中重复压入同一节点、neighbor 中保存指针或形成搜索环，并不创建新 owning delete。故没有证据从这些借用关系直接推出重复 delete。不能用“先对 map values 去重删除”修复遗漏对象：去重本来就不能找回已覆盖的地址。

构造失败另有实际责任缺口。HNode L31 先分配原始 LNode 放入裸指针队列，L39 在完整构造结束前将 this 插入父 neighbor；随后目标/优先级/排序等仍在构造中。若之后抛异常，尚未完成构造的 HNode 不执行完整 HNode 析构；裸指针队列元素也不自动拥有其目标，父 neighbor 中先发布的地址没有本函数清除路径。此为明确的条件异常安全缺口，未声称已观察到一次异常或后继解引用。

**构造三：两个 deadline 分支丢失已出队 L。** L183–184 取得并 pop 一个 L，L185 调用 expand_lowlevel_tree；L187 可能立即 break。另一分支在 L191 get_new_config 后由 L193 break。两者均先于 L195 的 delete L，且 L 已不在 H 的队列里，HNode 析构不会找回它。expand_lowlevel_tree L320 创建的是复制 who/where 的新 LNode；LNode L3–13 没有保存父 L 指针，因此其它队列子节点不拥有被 pop 的 L。若任一截止条件成立，该局部 L 的清理责任确已脱落；这是条件内的泄漏路径，不是 double-free 或某个已跑实例的 UB 记录。

## 4. 单一修订包的身份合同

先从父 H 和已产生的 C_new 形成一次有限、私有的后继事实描述：依原已知目标规则计算新 reach_goal、到达计数及构造会使用的到达判断。查询 EXPLORED 的键与真正创建 H_new 后的不可变身份必须是同一个 (C_new,F_new)，不能继续从未更新的 A.goal_index 冒取新 flags。查找命中不构造试探 HNode；查找未命中时，构造消费同一份后继事实描述，不另做一份可能不一致的目标/到达判断。该调整是纸面接口定义，不是代码或伪代码。

该描述不读取未来任务，也不自行重做根的单已知任务目标解析。原 HNode 对父已到达与首次到达的优先级更新规则仍由现选来源合同负责；这里仅要求 flags 与到达判定不能在查找和构造之间分叉。描述构造、冻结目标访问、距离读取、复制与一致性验证都收费，查找命中也不能免掉已经实际做过的这部分工作。

键的合法域固定为本次求解的同一 N、同一存活图、完整非空顶点条目与对应长度的规范 flags；顶点 id 在求解期间稳定。修正 RCEqual，使两边配置长度和 flags 长度一致后，按各顶点 id 与两边 flags 的真实对应项比较。原 RConfigHasher 可在这一合法域内继续使用，但其输入形状和规范 flags 的整数运算必须受本次来源资格约束；相等 tuple 必须得到相等 hash，碰撞允许且由真正的 equality 分辨。不能把哈希值当唯一节点身份。

未命中时只允许“本键没有既有代表”的插入，不允许用覆盖赋值把旧代表换成新节点。实际索引发布前校验 Key(H_new) 与预先描述一致；插入若报告已有代表或身份不一致，按源不变量失败终止本次求解，不默默替换、继续跑或额外构造 retry 分支。没有并行索引 writer 时，正常未命中后的这种冲突不应发生；失败分支仍须有完整单次清理责任。

## 5. 单一修订包的对象归属与发布顺序

每次 solve 建立唯一的求解期拥有者登记，以唯一拥有句柄负责全部成功构造的 HNode 及本次 LACAMAgent。EXPLORED、OPEN、H_init/H_goal/curr_best、parent、neighbor 和 occupied 缓存均明确是借用关系，不是第二拥有者。HNode 的 search_tree 队列元素改为 LNode 的唯一拥有句柄，原裸 delete 循环相应改为句柄单次释放，不能保留第二次显式 delete；离开队列、正在 expand/get_new_config 使用的 L 由求解迭代的作用域拥有者接管，原读取接口只借用它。

新 HNode 在私有构造期间不得先把 this 发布进 parent->neighbor。初始 LNode 的分配和入队也必须是异常安全的唯一拥有转移；构造未完成时，已创建的 L 仍有明确拥有者清理。完整 HNode 构造成功后先登记唯一拥有者，再发布其 EXPLORED 借用、父 neighbor 借用及 OPEN 借用。任何登记/索引/集合/栈分配失败均停止继续搜索；已经登记的对象由登记表销毁，尚未登记的新对象由局部拥有者销毁。即使某些借用已发布，失败终态也不得继续遍历它们。

expand_lowlevel_tree 每个新子 L 的构造成功到队列接管之间，同样不能有“裸 new 成功、queue.push 失败便失联”的空档。队列 pop 与迭代接管是一次受控的拥有转移；popped L 保持存活直到 get_new_config 不再读取它，随后销毁一次。L187、L193 的 break、get_new_config 失败、普通 continue、异常与正常迭代结束都服从同一规则；不在 break 各自补一段容易重复释放的特殊 delete。

原 HNODE_CNT 是构造尝试中的静态计数，不能把它误作当前活节点数量或 owning 登记。所选包不为了查询先构造临时 HNode、不借清理回滚静态计数；实际构造尝试及其费用照来源版本记录。后继身份修正本身会改变命中/创建次数，故不能承诺计数轨迹或截止输出仍与原 bug 版本相同。

## 6. 全退出清理及 AA 继续域

正常解或 fallback 回溯必须先在 HNode 与图都存活时完成所需配置复制，再停止搜索和所有借用遍历。其后销毁 borrowed OPEN/EXPLORED 入口并清除 occupied/A 缓存别名，清理当前迭代的 L，再由唯一登记逐个销毁所有 HNode；各 HNode 释放其仍拥有的队列 L。parent/neighbor 随所在对象退出只丢弃裸引用或指针容器，不遍历目标、不做递归 owning delete；即便某个被借用 HNode 已先销毁，也没有随后解引用它的清理步骤。任意重复借用或搜索图环都不增加对象销毁次数。最后销毁本次 Agent，令 Planner 成员 A/occupied 中不留可继续解引用的旧 Agent 地址。图和相关环境来源需活到这些借用容器和配置副本的约定生命周期结束。

拥有者登记应覆盖 setup Agents 部分成功、H_init 分配/入栈/入索引失败、新 HNode 构造/发布失败、两处 deadline break，以及回溯或 solution 容器扩张失败。普通分配异常可以有序退出并释放已拥有对象；已经发生的 UB、进程崩溃或外部强制终止不能靠纸面异常处理宣称一定执行了 C++ 析构。本件不借进程退出覆盖未执行的原析构或省略它们的费用。

源内部 deadline 表示停止继续搜索，并不免除已经产生的清理工作。清理属于本次源 job 的真实工作，使用既有计量/槽位；只有清理和继续域检查真正完成，才可返回“正常源调用完成”。若公共 Stop 或 worker failure 使它没有完成，只能按原未完成/源失败合同记账，不能给它新增免费资源把清理补完，更不能因此将仍活对象交给下一次调用。实际外层终态与资源回收接口仍由已有 E6 等合同负责，本题不调查执行后端。

ALWAYS_ADVANCE 只保留一个正常完成且内部状态合格调用所产生的源历史；它不要求把本次局部 HNode 搜索图永久留到下一次。外部计划软拒收时，仍按同一规则完成本次局部清理，再保留原定义的持久源状态/RNG；不得把局部对象泄漏当作应保留的算法记忆。异常、索引冲突、构造失败或 worker 崩溃走 FAIL_STOP_SOURCE，不假装成一个可继续的普通无提案；已发生的源费用和随机消费不退款、不反向恢复。

这里尚未证明整个外层 R0 对所有正常返回都满足 AA 继续域；该包只补此次求解内部已识别的对象/索引责任。原 E11 的输出前置形状、根的新目标解析、外层 init/线程生命周期与源失败要求仍分别成立，不能由本件替代。

## 7. 算法身份与 rewrite 的保留边界

原 rewrite L270 增 neighbor；L280–289 在较小 g 时更新 g、f、parent 并可能入 OPEN，没有同步 depth、curr_time、priorities、order 或 reach_goal。修正 (C,F) 键不会改变这些字段的事实。C/F 在该对象生命期作为索引身份不变，重写 parent 不会直接使键内存失效；但“索引合法”不等于“相同键的两条历史拥有相同后继生成行为”。

至少 depth 已在 get_new_config L348–353 参与占据/已达停驻规则，priorities/order 决定后继约束与 PIBT 顺序；这些是已读源码中的真实历史依赖。因此本包保留原两字段**重复探测策略和首次代表历史**，不把它宣传为完整 Markov 状态等价，也不据此继承 LaCAM 的完备性或最优性证明。这里没有另加无限深度、浮点优先级等字段重新设计搜索键；那会是更大的算法修改，超出此最小包。

原 get_edge_cost L295–309 为固定正步费用、启发式为原源码的零值。本件不将这些源码常量改为项目保护参数。若所有建边确为相应合法后继且整数运算不溢出，严格降低的正费用 parent 重写可支持无 parent 回溯环的局部推理；本件没有取得全输入域下的整数界、所有后继合法性与状态合并充分性证明，不把这一条件性质写成全 solver 正确性。

源修订会改变查找命中、代表对象、构造次数、低层展开与随机重启分支到达次数，也可能改变同一 deadline 下的输出。即便没有新增 RNG 调用，调用顺序/次数仍可能随正确命中分流而变，不能宣称随机消费逐次保真。它保留原样 R0 档案并公开差异，是修订来源合同，不是原固定二进制或 native R0 行为等价证书。

## 8. 同源同费、资格边界与停止调查点

D、R、E0 及相关同源对照必须用完全相同的修订包、键/flags 语义、目标来源、对象清理、随机规则、失败分类和实际计量。所有描述构造/键复制、散列和比较、索引/拥有者登记、额外元数据与峰值内存、容器发布、失败回滚、回溯复制、析构与 GC 都属于该臂实际源成本。内部没有免费身份检查或免费异常清理；没有给任何臂增添规划机会、服务容量或默认预算。

修正漏清理通常会增加一次调用被正确计入的销毁工作，也可能减少错误去重导致的搜索；净运行/输出效果未知。新增拥有者登记本身也有成本。不能把 repaired R0 的稳定性或搜索变化报告成 D 相对 R/E0 的观察收益；各臂同用修订后，剩余比较才属于本研究的策略差异。没有运行原 bug 版与修订版来产生任何效率结果，也不在实验前制造这种结果。

本题可以停止在四个源对象和一份键规范文本：已有足够证据拒绝“仅改 L232 即全闭”以及“重复 OPEN 必然重复 delete”的说法，并给出唯一修订范围。未闭项明确是实际修订源码/对象归属与异常路径核验、完整源继续域、后继/整数/状态合并算法前提及原计量后端；不得再泛扫全仓来把它们凑成通过票。若研究不需要源完备/最优保证，应明确只用其候选生成能力及独立执行守卫，而不是悄悄宣称原算法理论保证被恢复。

## 9. C16 实际终态与本件独立性

本题一次新 C16 Opus/high 调用已取得真实失败终态：exec 29117 / chunk eb81db / exit 124；JSON is_error=true、terminal_reason=aborted_streaming、subtype=error_during_execution，duration_ms=479122。没有 result 字段，没有 END-C16，modelUsage={}，故实际具体模型未由回执确认。只有调用终态完整，科学意见缺失；不重启、不重试，不把超时算意见或通过。

提示 SHA256 `18a7f8ff637d65de7750fd7e424d65aa35eca1278b25fc8266887891959b79f7`，22219 bytes / 560 LF；原 JSON SHA256 `b21ba51e6d2299bb203f92b22b331a3c010e88ff73f9201fe22f75fc2d30d93f`，875 bytes / 1 LF。完整命令、全部观察句柄、原 JSON 和无意见判断见 73C16_R0_EXPLORED_IDENTITY_AND_OWNERSHIP_COMPLETE_RECEIPT_20260910.md。

本件并未收到可逐条采纳或反驳的 C16 科学意见。上述源码构造和修订选择均为本代理无 skill 独立分析；不能引用 C16 作为支持它们的专家意见。根须另行全文读取、核文件身份并独立判断。E21 建设题完成不等于全部实验前准备完成，HOLD 与原六门状态不变。
