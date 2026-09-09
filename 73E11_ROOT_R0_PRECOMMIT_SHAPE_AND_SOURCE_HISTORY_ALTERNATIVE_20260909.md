# 73E11：R0 提交切分前置形状合同与源历史替代入口

2026-09-09，/root 独立直接分析，NO-SKILL / CONSTRUCTIVE / NONBALLOT。输入73为 SHA256 1881a85c7a21e5e5fe55e602e246cc057b964df4114dc6c8ab4bbde42f200a54，130281 bytes /466 LF。E6已完整读取，本件细化其“在 commitPath 前检查形状”，不覆盖E6已完成回执；E10仍是独立未采用服务模型备选。未实现、写伪代码、构建、研究测试、仿真、调参、生成实验载荷或结果。保护参数原义不变且未赋值。HOLD。

## 1. 本次真实来源身份和阅读范围

固定仓库 YueZhang-studyuse/LMAPF-delay，ref 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。通过 GitHub 连接器按下列三个确切源路径取得完整UTF-8对象，根用只读字节计算独立复核Git blob和SHA256；没有打开配置、地图、任务或结果。第三对象为完成本件时沿E5明确路径作的一次定点补核。

| 源对象 | Git blob | SHA256 | bytes / LF | 实际语义阅读 |
|---|---|---|---|---|
| [src/MAPFPlanner.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPFPlanner.cpp) | 94afb42df1a70f5e312a382e61cf83576fd7360e | c81952afaa94157abd7138bdaae71edc7b19b59dee60b653bb380ef16e681be1 | 6125 /208 | 全文，包括注释掉的非活动路径 |
| [src/MAPF-LNS2/src/LNS.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/LNS.cpp) | 1fb0e54f8f2bb00af05de53233ae600774e36f2a | 0113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2 | 53100 /1486 | checkReplan 383–443；fixInitialSolutionWithLaCAM/getInitialSolution 496–542；vector<Path> loadPaths 1186–1216；commitPath 1236–1339；setStartGoal 1341–1358；clearAll 1360–1430；validateCommitSolution 1433–1482 |
| [src/MAPF-LNS2/src/PathTable.cpp](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/src/MAPF-LNS2/src/PathTable.cpp) | 1dd06d5c8ef71841409a88517cc419df841fefb8 | 96cb8eaef095e01f99f69b91951372c5c2d2f966c6c2c126f315bdbdc429321c | 12025 /373 | 1–40行，完整insertPath与deletePath |

完整对象取得和hash不表示LNS其余函数本次逐行审完。此表只确认源事实，不确认未来构建或库绑定。

## 2. 原调用链确实在哪里访问了容器

MAPFPlanner::planner_commit 146–150首先清空每个 agent 的 future_paths 和 commited_paths，152行以 skip_start=true 调 LNS::commitPath，153行以后才做原验证，159–164行复制至调用者 curr_commits。因此“先调用完整提交函数，再检查输出是否为空”不能保护切分函数内部访问。

LNS::commitPath 的短路径分支先跳过首状态，再把剩余状态写入 commit_path；1318行用已有 commit_path.back()补齐，1330行还会再次读取这个 back()。当给定源路径为空或只有被跳过的首状态、且走到该分支时，刚清空的提交容器没有任何元素可供 back()。screen==3 的1241行还有原路径 front() 与队首目标访问，不能靠关闭日志掩盖路径本身的必要前提。

这是对确切输入形状和分支的静态结论；本件没有构造实验样例，也没有声称已观察到运行崩溃或该形状在所有合法R0输入上一定可达。plan 的签名为void；纯LACAM后继分支71行没有向外传递 fixInitialSolutionWithLaCAM 的bool。该函数本身有明确false返回，因此调用者也不能用“plan正常返回”替代源输出形状或完整成功证据。

原 validateCommitSolution 的1439行重新构造Agent，1442行按索引访问提交容器，1450行从每条已切分路径的第二个状态开始检查相邻移动；1465行后的两两冲突检查也从这个索引开始。既有原函数仍保留，但它本身不覆盖冻结历史锚点到第一个提交状态的边，也不能替代中心完整前缀/版本验证。原调用者curr_commits还必须事前具有全体agent对应的合法可写槽，且不能带未声明旧内容供push_back累积。

## 3. 声明式 PRE_COMMIT_SHAPE 合同

此合同是固定来源适配器的付费外层输入资格，不是另一个规划算法。它位于原 plan 完整返回后、原 planner_commit 的第一条清容器动作之前；源体仍处于唯一隔离执行域，禁止并发改变待查状态。检查读取的是本次job已有的私有源状态及冻结输入，不读取实际实体位置或未来任务。

合格条件包括：初始化后对象/指针和agent编号对应关系仍有效；instance/env/agents、commited_paths、future_paths、curr_commits及stay_target等实际被索引对象相容；固定预算/原切分量属于既定合法来源整数域且全部长度/计数转换、加法和索引可表示；每个会切分的源路径含被跳过的锚点及至少一个后继状态，源锚点、每个位置和合法边与本次冻结输入相容；原切分分支在跳过首状态后至少生成一个已提交状态；任何可达日志访问的目标队首非空。上述“至少一个后继”是函数内容器定义域条件，不是给H、密度或任何受保护实验参数赋值/范围。

按原 source commit 的正整数合法域，路径长度大于切分量时，跳过首状态后原长分支会生成相应提交前缀及共享边界；路径不长于该量时，只要已有一个后继，短分支先产生非空commit_path，其后的back填充才有定义。这证明上述局部充分条件保护本次所列空容器访问，不证明整个solver或标准库全部定义域，也不授权静默扩大任何整数域。

检查还须验证原提交函数所需的其他已知可达后条件；发现新前提就保持资格UNKNOWN，不能只因本节列出了几个字段便宣称C++源已完全安全。源状态元数据检查、全部扫描、日志封存、失败结果构造和后继验证均属于同一共同收费合同，空路径失败也付已发生工作；不能把对照失败检查放在免费监管层。

不合格时不调用原planner_commit、不补写人工WAIT或替代路线。可确证为正常源返回而无可切分完整提议的情形登记 NO_PROPOSAL_SHAPE；若有已发生未定义行为、结构不一致、异常或无法证明继续调用有定义，则登记 SOURCE_BROKEN / UNVERIFIABLE，隔离该源生命周期。即使一个单点路径在几何上代表已经到目标，外层也不能替源码添加一条动作，再冒称原PIE生成。原已接受物理责任按已有HOLD/执行规则继续，真实任务只按共同SERVICE_TRUE记账。

NO_PROPOSAL_SHAPE与SOURCE_BROKEN的区别必须有证据：前者不自动意味着整个内部源状态可安全用于下一次调用。当前 accepted-only profile 对该次未接纳状态按既有回滚合同处理；如果改用保留历史的profile，需另证明可继续域，不能拿“正常return”当万能恢复许可。

## 4. 沿调用边实际排除一个空路径疑点

loadPaths(vector<Path>)在1188–1190行先按instance agent数量索引输入外层，空内层则跳过；非空内层会由原源码自己复制并按原commit填充。这个已有行为可保留，但它不意味着外层可以把任意遗留路径当合法冻结未来段。loadPaths之后的checkReplan在发现已复制路径没到当前目标时会清空它；随后的无碰撞分支仍可能把该空路径传入path_table.insertPath。根实际补取固定PathTable.cpp并全文读取该函数：5–6行首先对path.empty()直接返回，因此这一调用的空路径本身不会到达下方back/表索引。删除函数也有同类早返回。不能将该处继续列为“空路径必然非法”或借此增加源码修补。

checkReplan仍把清空后的长度减一计入initial_sum并将agent放入complete_agents；这属于原函数的具体状态行为，不能从负项直接推整个求解失败。输入级的完整目标/锚点、未执行未来段资格和被调函数契约是不同责任点。不能为了避开该分支自行给不完整路径加未来目标或筛掉困难任务。上述补核只关闭insertPath空路径疑点；非空路径的位置/重复goal等原断言与全下游仍按已有资格核验。若后续确需来源修补，必须说明确切改动、共享源臂相同应用和对提议分布的影响；本件没有新增内部算法改动。

## 5. 为何值得单独评估源状态保留

原MAPFPlanner::plan的initial_run/initial_success会随调用改变；后继loadPaths只有在initial_success且非initial_run时才重装。clearAll虽清许多路径/统计/目标缓存，整个函数不恢复一个先前进程快照；例如stay_target在已完整读取的clearAll体内没有重置，而commitPath会写它。不能把clearAll称为全部源状态/RNG回滚，也不能声称每次调用本来无状态。

本次两个对象没有中心计划版本CAS或外部拒收后的回滚入口。这不证明R0整个driver没有任何其他管理语义；它足以区分目前73自行要求的accepted-only事务profile与另一种方法定义：内部源按每次正常完整调用顺序保留历史，外部可执行计划仍只按中心合法CAS接纳。

根提出将这另一种定义称为 ALWAYS_ADVANCE，交给独立E12从公平和失败语义构造，不在本件自动采用。若其可行，常驻单一源worker无需仅为“中心拒收了这条候选”而保存与恢复整进程快照；外部源输入仍必须由已接纳执行历史/最新合法任务投影冻结，不能把被拒候选路径塞进已执行历史。源内部缓存影响未来搜索可以属于明确方法语义，但需要与外部计划提交严格分开并记入完整调用历史。

它改变accepted-only反事实源历史；不能说与当前73逐次输出相同，也不能给D用保留历史、给R/E0用回滚而把差别归因于QUERY。硬失败、未能证明安全继续的NO_PROPOSAL、内部异常和强制退出仍需fail-stop；不允许免费重启、重新播种直到好结果。即使解决快照负担，E10的公共时钟、非抢占服务尾部和宿主噪声推断仍未解决。两项独立选择应明确分别命名：服务模型与源历史profile。

## 6. 根取舍

接受PRE_COMMIT_SHAPE作为E6既有前置资格的具体必要补充，并在73注明其放置顺序及“禁止自行补动作”。保留源所有原成功提交主体，仍只有先前第五堆关系这一项已选内部修补；本件不修改源代码。

ALWAYS_ADVANCE只是有明确潜在简化收益的建设性替代；等待独立合同后判断，不偷偷从正文删除回滚要求。insertPath空路径接口本次已核有明示早返回，不再作未核缺口；源状态继续域及整体执行后端继续UNKNOWN。没有性能结论，没有把找到源缺陷当方法优势。六门维持2 PASS /3 UNKNOWN /1 FAIL；73未固定/未送审/未接受。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。
