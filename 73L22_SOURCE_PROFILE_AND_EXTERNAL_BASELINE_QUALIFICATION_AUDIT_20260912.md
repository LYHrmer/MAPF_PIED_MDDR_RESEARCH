# 73L22：来源 profile 非空资格与外部 ECBS 源域收束

2026-09-12；执行代理 `/root/source_provenance`。NO-SKILL / CONSTRUCTIVE SOURCE AUDIT / NONBALLOT。只写本件，不修改73、旧报告、行政记录或Git；不作正式审稿或六门裁决。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。

## 1. 可收束结论

本轮未识别出一条能够在当前载荷禁读边界内证明**完整固定来源 profile 非空**的证据链。已有软件许可、官方归档对象和解析器说明足以支持若干必要条件，尚不足以证明某个完整source成员同时满足引用关系、素材使用依据、解析语义、共同WORLD初态及必需profile。这里是存在性未证，不是合法域已证为空，也不是断言不读载荷永远不可能取证。若存在可靠的逐对象静态资格证书，可以在不打开正文的情况下核其身份和覆盖；当前已读材料没有提供这种证书。

实质新增有两项。第一，重新从固定原parser及当前§8–12核对后，可以把delay缺口明确限定为“原agent/离散列到新公共ACTUATOR尝试的语义连接，以及该连接如何进入来源权重”，而不是笼统的delay格式未知。第二，固定H19低层在当前单位层、单位代价State合同下有一个可证明的不可达分支：同一完整State不可能获得严格更小的g，因而原A*_epsilon的相应原地改堆键路径不必作为这一受限Environment的动态路径证明。它不关闭其余堆、数值、生命周期或后端资格。

本件把可用条件与剩余凭据分清；没有给出一个实际source_id、roster成员、实验配置或通过记录。外部两臂和四类别总体保持现有定义，没有通过缩小成功域来取得非空证明。

## 2. 实际阅读与身份

完整读20260911最新handoff、L18、L19、L20、L21及H19的L4/L5；当前73读取§8全部、§9的L236–256及全部delay/no-start直接命中、§10–12全部。未作当前73全稿正式审查，未重读历史全部handoff或72三路审稿。研究目录不存在AGENTS.md或.codegraph，适用当前注入的RTK指令，未创建索引。

98df42静态核验所得如下；均是文档身份，不是数据资格。

| 文档 | SHA256 | bytes / LF |
|---|---|---:|
| 20260911 handoff | 2ca36d652c6160eb9b6b403d3eaa13ad56fc39e6a401eee9071957073cadb4da | 30281 /182 |
| 73L18 | e20a7dd2d05b495ece88a31164f2f9d3439439eeeb072aa6019be08ac9da1327 | 7542 /57 |
| 73L19 | 4ee91a0480890f4beae541c6093b098c2190aeafb497852f9ae3cc1941c26f71 | 11912 /83 |
| 73L20 | ee83a72a85ac6018a8525626b2e751e0fdad8966d306a4968976ad0a5bfde136 | 10541 /74 |
| 73L21 | 91fd764c3ec645cf39324d76f8d9dffcae3ed78899894814f84c793a58d2f656 | 11689 /74 |
| 当前73 | 9e06199cc6045ddd750b861b3091ec239c7c6ff2ae7eeaebbdd0e7fde61ec113 | 216498 /665 |

R0固定`YueZhang-studyuse/LMAPF-delay@0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`，H19组件固定`whoenig/libMultiRobotPlanning@4c75fa20c435c440d8b6bd6dc81668ddc7296ba0`。本轮以下正文均由GitHub contents API的raw响应完整读取，没有执行代码或访问README所链接的样例。两棵递归Git树只返回路径/type/SHA/size元数据，`truncated=false`；未取任何数据blob正文。下表Git blob不充作本题重算的内容哈希。

| 固定对象 | Git blob / bytes | 本轮全文回执 |
|---|---|---|
| R0 README.md | a4578f87f918dab4b67b50cd404e3ec901a8f636 /2730 | 0bd32a |
| R0 LICENSE | 1f4b6eadac278447824a47d409bb4de04ea7f3ee /1084 | 7ff8d0 |
| R0 inc/common.h | 9ddeff363a76cbd70a3e6e1ca98cfd79f69c8237 /5954，身份承接L20 | f75d32 |
| R0 src/driver.cpp | b75764cc26c2374ce51dabb94e13a138e50f166f /6664，身份承接L20 | 7d7002 |
| R0 src/Grid.cpp | b78abb1848a74d4c801e6eea6e1e89ccf4f6ddbe /2155，身份承接L20 | 3f7ad2 |
| H19 README.md | 5c092196cbbd426faa1667a102e93108fe89e9ef /2293 | a7057f |
| H19 LICENSE | bdfe1aca78d88fb8cfd976b51423ced252ebdd22 /1064 | 9048cb |
| H19 include/libMultiRobotPlanning/ecbs.hpp | d93fbe2bd60b472af61a77c0365a3140a8c9065e /14871 | 6b1b89 |
| H19 include/libMultiRobotPlanning/a_star_epsilon.hpp | 1b6b90a895ff14fbdb41c7eba33ecfe0b6b7a288 /14047 | 578a7d |

R0树ff0768仅输出具名README/LICENSE/NOTICE/COPYING/CITATION/AUTHORS/PROVENANCE/ATTRIBUTION及名称含generat/delay的源码条目。匹配项只有根README/LICENSE和六个delay执行头/源对象；这不是“所有可能文档中均不存在生成记录”的证明，也没有从文件名断言未匹配源码不会生成数据。H19树cba74b只输出表内四个H19对象及planresult.hpp元数据。

网页工具首次对四个官方源码/许可URL的批请求返回connection failed，没有可读正文。GitHub上述九对象随后成功取得。planresult.hpp的单独contents请求1f334a发生EOF，按工具权限要求正常升级后cc35b1仍EOF/exit1，未再重试；该对象本轮只有固定树元数据及L4旧全文阅读回执，不能记为本轮新读。没有重做L20失败的agent/task跨树比较，没有读取ODC-By的新正文；其范围只承接L18–L20。

## 3. 非空命题的准确层次

当前要证明的不是“某个名字存在”或“某段语法可接受”。§11要求各必需类别都有完整静态合法来源，并要求必需MAIN profile有合法成员；这些成员还要支持固定权重和比较域。可以将证据义务拆成以下逻辑命题，它们不是实际数据清单或新manifest。

| 层次 | 可承认的现有事实 | 尚不能推出的命题 |
|---|---|---|
| 对象存在 | 四类固定树；L18的city/random官方归档同blob；L19的game/warehouse官网同名分类 | 一个JSON确实引用了哪些四类素材，或这些对象满足共同初态 |
| 软件使用声明 | 固定R0和作者ECBS组件均有MIT正文 | 每个独立地图/agent/task/delay素材的权利链都已被逐项覆盖 |
| 解析器语义 | 原driver字段和common/Grid分支可亲读 | 固定数据正文满足这些分支的前置条件，或输入格式相同便有相同任务含义 |
| 条件数学域 | 给定有限合法图/任务/表示，可写共同WORLD与H19访问问题的条件规则 | 必需类别中已存在满足全部条件的固定来源对象 |
| 可评价机制 | 合法无解、慢初始化及HOLD在现稿有保留/评分规则 | 源未定义行为、来源缺证或未知静态输入可以被赋合法失败分数 |

即使所有已登记地图对象都非空，组合引用、agent初态、任务域和delay支持也仍是独立命题。Git SHA把对象身份固定下来，本身不提供token数量、可通行位置、几何Mask不交或素材出处的证明。不能用“哈希固定所以其内容必合法”，也不能用“生成器在某些输入上能产生合格输出”替代“这个固定对象确实是其合格输出”。

若未来有现成的可信静态资格报告，它至少须把固定对象身份、确切解释器/适配版本和所证明的合法性谓词绑定；结论还须覆盖本研究要求的共同物理初态和各必需profile。只有基础MAPF有效性证书不自动覆盖横向偏差、全实体ServiceRegion或bootstrap资源覆盖。证书可以陈述存在性而不展示正文，但不能仅有“官方实例”标签或曾经运行成功。当前未取得这种材料，故保持未实例化和存在性未知；没有建立新的取证授权流程。

固定R0 [LICENSE](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/LICENSE)和作者组件[LICENSE](https://github.com/whoenig/libMultiRobotPlanning/blob/4c75fa20c435c440d8b6bd6dc81668ddc7296ba0/LICENSE)明示软件使用与修改等许可及保留告示条件。这个可核软件事实可登记，无需再次把同一MIT当作新缺口。素材再使用则保留L18/L19的对象精度与声明范围，本件不作特定法域法律结论。

## 4. parser可支持的最小静态资格内容

[固定driver](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/driver.cpp)亲读确认：agent/task/delay均由JSON父目录与具名字段拼接；任务策略直接读取taskAssignmentStrategy；Fixed先按agent容器大小取模分配；delayFile为必读字段，再交set_delay。没有“省略delayFile即可选择无延迟”这一直接入口。原CLI默认值不在本轮采用。

[common.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/common.h)的两种位置读取均只取每条记录逗号首token，注释跳过、EOF/token解引用和atoi仍须输入域保证。delay逐agent行把整数转换成bool，没有逐行支持集证明。不存在有效记录与打开失败返回空向量不能混称为同一种合法任务世界。Fixed的取模以及L21已核Inf的任务取模都须在其实际执行条件下有定义，不能靠后续wrapper有HOLD便认为原构造访问总是安全。

[Grid.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/Grid.cpp)同时存在首行以`t`开头的header分支和逗号维度分支，随后按声明行列数索引；只将`@`/`T`置为障碍。这进一步说明“公共MAPF地图”不是唯一解析语法证书；对同图上游解析器的通行符号解释、维度和位置编码仍须一致。source静态资格应分别证明路径封闭、读取总定义、位置/任务引用语义、共同初态和profile支持，不能只测返回码。

这里可以固定**待核谓词的内容**，不能声称已核到满足它们的固定成员。未知任务容量/几何相容不是动态算法失败；反过来，合法搜索无解、任务耗尽、等待或低吞吐也不能回填为静态非法。本轮没有选择strategy或profile，没有给teamSize/density N或其它保护参数赋数值或范围。

## 5. delay、来源身份与目标权重的接缝

原消费端的依据承接L21完整源码回执：BaseSystem::execution_simulate按agent行及curr_states[0].timestep加commit-window偏移读取原delay矩阵，随后MCP/PIBT/PIBTD按各自离散移动逻辑处理。当前73§9则把故障创新绑定到公共行或请求/作业语义id，并规定NO_START只作用指定ACTUATOR尝试；§5/9还区分准备未完成与实际处理一次尝试。本轮直接读当前命中及§8–12，没有找到delay矩阵列与这一新尝试身份之间的完整绑定规则。

因此仍须分别明确：原矩阵的哪个坐标在新模型中具有作用；由公共时间、公共机会还是某个语义尝试导出该坐标；无待处理尝试的公共行及准备失败如何影响索引；支持集外的读取如何被判定；原delay参数/机制意义和新no-start含义之间保留了什么、改变了什么。上述问题必须在各臂共同的事前机制中回答，不能各臂按自身调用次数移动一条公共磁带，也不能把未知尾部填零。它们是绑定义务，本件不替根选择新映射或生成载荷。

当前source_id明确保留delay_blob，并写有同语义alias合并；原parser又可能把不同整数记录解析为相同bool。由此不能直接断言当前实际存在重复样本，因为未读任何记录，也不能未经选择就将不同blob全部合并。需要分清的是：固定字节出处身份、完整解析/适配语义，以及最终等权单位是否同一个关系。

若一个delay_blob仅留作出处、对主机制没有作用，按字节来源给予不同权重可以定义一个明确的出处加权目标，但不能默称它表示不同延迟语义；这不必然是数学偏差，却会改变科学目标的解释。若拟按有效语义合并，则须先有完整、事前的等价定义和原alias保留规则，不在看到输出或净收益后去重。L21提出的风险据此精确化：**缺的是声明及绑定，不是已证数据重复或已证权重错误。**本件不修改§11的四类别/map/source/profile/repeat权重，也不把地图同名或parser忽略字段当成自动合并依据。

## 6. H19静态源域的一处条件收口

本轮完整亲读[ecbs.hpp](https://github.com/whoenig/libMultiRobotPlanning/blob/4c75fa20c435c440d8b6bd6dc81668ddc7296ba0/include/libMultiRobotPlanning/ecbs.hpp)和[a_star_epsilon.hpp](https://github.com/whoenig/libMultiRobotPlanning/blob/4c75fa20c435c440d8b6bd6dc81668ddc7296ba0/include/libMultiRobotPlanning/a_star_epsilon.hpp)，与当前73§10及L4/L5的State、单位动作代价和全相对层合同对齐。所选仍是纯ECBS-FA，不是ECBS-TA或2019整体作者程序；[作者库README](https://github.com/whoenig/libMultiRobotPlanning/blob/4c75fa20c435c440d8b6bd6dc81668ddc7296ba0/README.md)列的是规划算法库及examples，没有把本研究重构的ADG/cut/TASK世界认领为该库现成整体功能。

对一次低层调用，记起始State的层为τ₀。当前合同要求每次合法MOVE或WAIT都使层增加一个离散单位，并且规划代价也增加同一个单位。若State相等性完整包含time/vertex/visited且时层与代价运算精确、没有溢出，则沿路径归纳得到g(s)=τ(s)−τ₀。这是算法单位定义与符号恒等式，不是H、T_delay、density N或其它实验参数的赋值。

固定低层源码遇到已在stateToHeap中的State时，先判断tentative_gScore≥当前已存gScore并跳过；仅严格更小时才减fScore并调用openSet.increase。在上述合同中两种g相等，故后一个分支不可达。current State已在closedSet时也不再按较低g重新打开。visited加入State不破坏此等式；cut统一平移时间只改变τ₀。这给当前Environment一个有限而实质的源域简化：无需靠变量边代价下的更优路径更新来完成搜索。

前提不能省略：如果时间不在State identity中、WAIT改成零规划代价、邻居跳层、算术回绕或以后采用非单位代价，这个收口即不适用。它也不证明focal始终非空、focal成员和handle生命周期始终一致、全部Cost/启发式加法无溢出、浮点次优因子比较有效或Boost合同已满足。L4/L5数学有限J不等于这些机器源域已闭；没有把纸面归纳称成已运行测试或完整ECBS正确性证明。

## 7. 外部资格仍须覆盖的精确位置

| 剩余位置 | 本轮固定源码/当前稿支持的明确要求 |
|---|---|
| high-level计数 | ecbs.hpp的id为int，每个孩子处理完都会自增，包括低层失败、不入open的孩子；onExpandHighLevelNode在这整批之前。只在展开回调检查当时计数，不能单凭该检查证明之后全部增量安全；须有覆盖整批增量的表示/停止合同，或显式源修订身份。 |
| 失败结果 | ECBS在低层返回后、success判定前仍更新cost/LB并调用完整focalHeuristic；Environment必须接受实际partial容器而不把它作为成功路径访问。不能由“false会被丢弃”省去这些运算的定义域证明。本轮未重新取得planresult正文，不追加对其初始化的猜测。 |
| 回调输入 | conflict所产agent索引须属于当前输入；每个constraint必须新且与该孩子语义一致；空/不完整路径、无任务agent、重复目标和未来驻留约束依L4/L5及当前稿保留。 |
| 时钟与计费 | 这两个模板正文未见直接chrono/clock读取，但Environment回调、日志、库和实际worker仍有外部行为；不能据两个头没有取时函数就宣布整条源链无时钟/I/O。 |
| 同域和失败 | 几何访问无解、ADG不能执行同步环、guard长期阻塞、真实TASK机会错失均保留为本系统结果；来源未定义/适配不闭导致比较不可推断，不能改作另一臂胜出。 |
| 比较解释 | H19E0与H19R-S两臂同报，完整ECBS/ADG/cut/APPEND/授权/END/控制费用与共同供给按§10–12；访问visited、动作finished、消费、空间退休及真实服务各自独立。 |

纯ECBS的使用声明、模板接口和这一条件不可达分支可以作为局部已核证据；完整外部正常继续域、异常/退出、实际共享后端和非空同域来源仍需后继资格。全部剩余项可被具体核查，不需要再把原ECBS-TA缺口误套回已改为纯ECBS的当前选择，也不能把读了库README等同于复现作者整法。

## 8. 收件与边界

本件对G4/G5提供源域条件推导和资格命题拆解，不更新六门票数。主稿可引用第6节的有条件收口，及第5节“delay映射/身份/权重解释尚未绑定”的精确缺口；不能引用本文宣布完整source非空、素材许可通过或准备只剩运行验证。

唯一新输出路径在98df42确认不存在且非符号链接，随后仅由apply_patch建立。全部shell及链段均rtk，源码和文档只读；没有Claude调用、外部消息、Git写操作、实现/伪代码、构建/测试/仿真、参数选择、O/seed/tape/manifest/配置/实例或结果生成。35–38、Q-CAL/Q-CONFIRM及任何实际map/scen/config/agent/task/delay/result正文、地图图片全未读，桌面未触及。原报告冻结字节及当前73保持原样；本研究仍未完成资格与正式验收。
