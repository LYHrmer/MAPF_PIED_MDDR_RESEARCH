# 73E20：根单已知任务、目标引导及交换局部进展独立构造

2026-09-10，根 /root。NO-SKILL / CONSTRUCTIVE / NONBALLOT。根全文读取C15实际返回，直接核固定来源并独立纠正、构造和修改73；没有使用任何科学skill或给资格票。六门仍2 PASS /3 UNKNOWN /1 FAIL；73仍DRAFT / NOT-FIXED / NOT-REVIEWED / NOT-ACCEPTED，HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 1. 实际输入、终态与正文身份

本题进入时73为ab0283a5ef6fb9b3a408f0d453fb763340f9241b01a63928851ceb5ddef48939，181390 bytes /583 LF；已与本地HEAD和远端main d34579c7556d5c256ea46f63b92a8f0d56d489fc对应核验。只读API另外确认LYHrmer/MAPF_PIED_MDDR_RESEARCH、private=true、default_branch=main；第一次仓库元数据请求受沙箱代理socket阻止，正常升级只读重试exit0，未绕过审批。此处Git核验不是科学资格证据。

C15是单一新建设题，不是C12或C14重试。提示SHA256 db55075b58b55ec15cc1550a713b0eeb2dac26381a647ca5420ce13691ca271d，17187 bytes /349 LF；原JSON 6af8204fbfda82187e8d995a6c3b9cd15f9d6fe9ab9529d14edc09a8d8024007，18372/1；完整回执8697619e9c857db5c28edc6c1705c23444bfacddac705488f0389cf024cb1d45，18819/120。三件全文读回与预备提示/实际stdout/包含原result的回执逐字一致。返回正文内的错误不因原样保全而获采纳。

原exec34155仅续等，没有重复启动；首chunk3fa09c，终chunk7d8361 /exit0。JSON为result/success、is_error=false、terminal_reason=completed、stop_reason=end_turn，实际modelUsage claude-opus-5/firstParty，duration303133ms，CLI293f850f-94b0-43d1-8117-be0d0c158430，uuid b4b526dd-f349-4afc-9a6c-0d855b54470e，最后END-C15完整。根核完整正文后不把该终态当意见正确或正式审查完成。C14的实际拒绝另保失败原文，不能拿C15替换。

本轮来源修订后73实读回为 **c59c96cb29af0f167a8942e26b82ce8f126a83d05167b1537dd477558778ed75，185290 bytes /593 LF**，全文与预备整稿逐字一致。本件记录这一中间科学身份；后续精度章节若改稿另记新身份，不能把C15已读窗口冒充后续全文。此次改动限§9来源和W81–82/总范围，不改源代码、参数或真实实验输入。

## 2. 根直接来源与实际阅读强度

固定原来源为YueZhang-studyuse/LMAPF-delay，commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。本轮实际通过GitHub文件API取得以下六个完整文本对象，再以UTF-8字节独立重算Git blob SHA1及SHA256；六项原blob全一致，不把窗口的hash冒充完整对象。文本只在工具内存使用，不落源码或读地图/场景/任务载荷。

| 相对路径 | 原Git blob SHA1 | 完整文本SHA256 | bytes / LF |
|---|---|---|---:|
| src/MAPF-LNS2/src/lacam2/planner.cpp | 4f46f988d2c16f09c5a6f65bb9cd70e8e01aa483 | 8d2fa9131f0691b109a00dd6267b3b48f80df7778643daeb806ff82e20fe2789 | 19115 /615 |
| inc/MAPF-LNS2/inc/lacam2/planner.hpp | 48ec12187373e87d6a233bfebea5eaf8b26c9304 | 8e7c6b7221828ef17a73730a3a33c39d5fcc9ccd9f73a6697c7434162ae7312c | 3850 /132 |
| src/MAPF-LNS2/src/Instance.cpp | 2183ba41c4a04278fafa0c4ed0605762abd5fb7c | dcfd6fb4b134dcc437b6124d5bf099e4fd6a977e9f749607446e87b7fedae2ac | 14658 /454 |
| src/MAPF-LNS2/src/LNS.cpp | 1fb0e54f8f2bb00af05de53233ae600774e36f2a | 0113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2 | 53100 /1486 |
| inc/MAPF-LNS2/inc/lacam2/lacam_instance.hpp | 7ada1b5832c0f45a510bb9c98cb97b459731d3f8 | 97d98a8807b64c0cf56ec71ba57bdd6f31c8a15b4fb1155972645d416f38ff1b | 1205 /46 |
| src/MAPF-LNS2/src/lacam2/lacam_instance.cpp | 50f18e9ce8295ba94e4a7d5caa293d5affca0688 | 840d442a5f3a0804ae751e1c39797a3f669dd43dcadf48786b73b1fc0e2db1c4 | 4137 /139 |

原[planner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/lacam2/planner.cpp)本题实际分窗口覆盖完整HNode构造/析构、Planner构造/solve、rewrite、辅助/低层扩展、get_new_config、funcPIBT、交换函数至文件末尾；并对reach_goal/goal_index作完整对象标识符定位。头文件两件实际完整显示阅读；Instance.cpp读L1–80覆盖prepareDummy，LNS.cpp读L648–714覆盖runLACAM2及相关标识符，不称两大文件全文精读。lacam_instance.cpp全文显示，重点亲核SharedEnvironment构造L19–38；读取源中解析器本身不等于读取其目标载荷。误猜一个instance.cpp路径的404不计来源，随后按真实include转到lacam_instance.cpp。

## 3. 值域证明与真正的单任务缺口

固定hpp L55明确std::vector<int>，新HNode从默认空向量resize；int新增分量值初始化为0。根分支逐个写0；后继若parent分量大于0只复制，若为0只可能在首次目标匹配时自增一次。因此对成功构造的合法对象按构造顺序归纳，范围为{0,1}。头文件也明确num_agent_reached及curr_time初值为0，解决C15因未读头文件而列出的窗口外前提。这个局部值域证明不预设重写后的parent链仍编码原构造历史；rewrite不改这些分量，不能据此推全部路径历史语义。

HNode L64、funcPIBT L411、is_swap_required L509/L511把该标志放到目标项索引。只要已置位分量参与相应读取且队列仅一项，原无界下标就超出合法项；这是一条具条件的源码未定义访问，不是已经运行出的故障。队首合法只保护索引0。LACAMInstance构造仅复制每行front到ins.goals，prepareDummy写另一个容器，runLACAM2中的update_dummygoals调用已被注释，均不在env里制造索引1。

空任务队列必须更早处理：实例构造L34已经front读取，先于solve。根明确拒绝C15把任一空队列导向空H_goal分流的写法。§8 PROJECT/输入资格在源安装之前NO_INPUT/HOLD；已经安装的冻结输入若在源码内部违反已核非空/身份/顶点不变式，属于来源错误及FAIL_STOP_SOURCE，不能晚等空H_goal或把源内错误回归普通无任务。原null-goal守卫只解决其自身具名分支。

## 4. 采用的统一引导与自身行修订

四处读取共用一个语义定义：对当前agent，标志0取冻结队首；标志1且真实已知第二项存在时仍取第二项；标志1而仅一项时取同一个已合法分配首目标顶点作为搜索内部终端引导。它只读已冻结合法输入，不改任务队列或实例，不产生TASK、Q或未来任务，不复位原标志，不添加WAIT或动作；任何提议仍经过既有PRE_COMMIT_SHAPE和全路径/物理授权合同。

“已访问”在这里是搜索历史中的标记，不是已真实交付。当前真实服务还要求SERVICE_TRUE，且之后有固定派单/付费知识延迟。不能因单任务引导回到目标就把该任务服务视为已发生。若未来算法需要独立停泊/辅助目标，那应另列推导和提议语义；辅助引导并不自动等同伪造任务，本件只选择较小的已知目标修订。

is_swap_required的puller端明确取puller自己那一行和标志，再用同一引导定义。原实际写的是pusher行搭puller标志；在单任务非空修订下保该行会使双方引导恒相同，交换提前返回。后继四距离分别用于双方偏好比较，故更正两方数据所有者有具体字段依据；该改变仍是源行为修订，不是保原字节。

不采C15若干过强判断：在已证明标志0/1且队列非空的域，索引钳位到合法末项与所选目标值可以相同，并非必然在长队列静默给不同结果。选择显式语义是为了约定清晰，不能靠虚构差异排除备选。没有采用的dummy引导也不凭“不是任务队首”就普遍非法。原叶节点排除使用首目标，其他引导有时用第二项，可以各自承担不同角色；差异本身不足以证明算法自相矛盾。本件不另改该排除。

## 5. 根新增的交换循环有限进展修订

根独立读到L561–564的四个int声明位于内层while作用域，它们没有更新L520–526的外层距离。原条件和return仍看初始数值；有限图环上的潜在重复需当条件风险，不宣称运行时已挂死。C15指出此处，但未给完整有限域证明；仅启用正确puller行而完全略过该循环，将留下可见的关键路径空缺。

根采用的第三项纸面差异只令顶点对推进后的四个距离更新原外层绑定，不改变原邻接遍历/叶节点筛选、跳出、双侧返回式、随机或超时语义。在一次调用内，前提是pusher引导固定、图/对象与邻接合法、距离读取在有限顶点集V上全定义且保持不变。每次进入while满足D_p(v_puller)<D_p(v_pusher)；执行推进后新的v_pusher是旧v_puller，故下一次若仍入循环，pusher距离形成严格下降序列。有限表可取值集合不能容纳无限严格下降，局部循环有限。这个论证甚至不依赖人为给距离额外数值下限；图/表本来有限即可，不能替未闭的数值/索引域。

局部结束还可能因原分支更早发生。证明不说整个Planner有限完成、搜索正确或预算足够；原预算仍未赋值，收费途中仍可能截止。它也不把原距离表一定精确最短路当已实证，域/表构造/整数表示仍须各自资格化。四距离计算与新增读写/比较产生真实成本，不能用有限性证明免计。

## 6. 范围、费用和未闭义务

原source身份仍为固定R0，纸面修改版工作名称继续R0-REPAIRED-LACAM-ADAPTER / ALWAYS_ADVANCE / FAIL_STOP_SOURCE，并逐项列新增差异；没有代码产物便没有“修订后源码hash”。所有内部引用臂同一来源规范，按自己的实际合法已知输入运行；既不要求整个roster都两项，也不限制整个研究仅一项，更不在结果后筛掉某臂失败block。没有既有实验结果可迁移或宣称复现。

引导和交换改变可能改变提议/递归、MT消费位置、源缓存/时钟与后继软STALE历史，进而改变费用与Q。读队列、分支、表查找、正常和失败路径、原对象及回收都收费；不补抽随机使次数表面相等，不给H19虚收未用R0对象。不声称与原native逐结果、逐墙钟或论文效果等价。这些共同修订不能认领为D查询贡献。

C15的走廊例子不足以证明无限饥饿：原get_new_config的低层约束可覆盖已设v_next，消失agent未记占有还可能生成待拒提议；真实TASK_SERVICE/后继派单与知识也未被完整覆盖。根仅保留无吞吐/完备保证的边界，不采用其“无限不动点/无新派单”作反例定理。不能把形状/冲突后验检查误当修好了更早索引未定义，也不由定义域修订推整个源有效。

剩余具名问题为消失agent占有及全路径输出、EXPLORED键/所有权、弹出L在截止分支的清理、真实ABI/有限整数域和跨合格历史继续域。73E21作为下一独立有界题处理键/所有权，不再扫无入口全仓；其报告/Claude回执尚未完成时不计意见。P13/C14精度题另行根分析，不用本源结论代证物理事件判序。

W81–82只写未来可区分行为，均NOT_IMPLEMENTED/NOT_RUN。本轮无源码编辑、伪代码、构建/测试/仿真/调参、种子/地图/任务/事件载荷、研究结果或保护参数赋值。旧完成件与冻结52/52R1、69–72均保字节，35–38及受限载荷禁读，桌面未改。正式导师skill→根不用skill→Nature→根不用skill→完全无skill独立逻辑→根验收尚未启动；目标active，科学进展不等于研究完成。
