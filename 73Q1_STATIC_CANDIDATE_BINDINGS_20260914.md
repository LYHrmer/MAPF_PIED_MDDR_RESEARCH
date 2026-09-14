# 73Q1：实施前的具体静态绑定

2026-09-14，建设中，可更新。本工件承接[73R4已完成的设计验收](73R4_ROOT_DESIGN_ACCEPTANCE_20260914.md)，记录具体源码和表示证据，不重开三路审查、不改固定73。第4节具名ECBS包已经完成；随后[73Q2](73Q2_MAIN_EXECUTION_IMPLEMENTATION_BINDINGS_20260914.md)为PIE-D主方法纯几何核心新增限定源码准入。整个候选实现与主实验资格仍未取得；本文件较早“仅ECBS”口径只描述当时阶段，当前包范围以Q2及项目入口为准。

## 1. R0跨调用统计与路径表示界：根直接建设

来源固定为R0 `0b5b33649fc367abcb1cd0a7ad5ac03511bf9357`。根本轮直接以git show读取MAPFPlanner的入口与提交函数、LNS/BasicLNS字段、LNS构造/loadPaths/checkReplan/fix/getInitialSolution/runLACAM2/commitPath/clearAll、PathTable的reset/insert及Instance::hasCollision相关正文；定位工具为a3566f/b9d7fc/e1950e/ed3c33/6314fd/78aa8f/8d29d5/de243d/2f2d36/b4c25f/6b32f2。未运行源码，未声称全文重读所有依赖。

以下只用固定73已批准的唯一worker、固定fleet、LACAM-only、已有共同源码修订、合格缓存安装和正常调用包。记n为fleet的数学计数，k为原k_commit，P为覆盖所审继续域中所有输入路径（含原补齐）和完整搜索输出层数的事前长度上界，P≥k+1≥2。P不是新增实验参数，也不允许从成功结果中挑选；§1.4现给出一个由既有图/身份域导出的条件实例。源int最大值记M_int；源容器自身max_size、分配及生命周期前提另保留。

### 1.1 实际重载与旧路径覆盖

SharedEnv.h直接声明unexecuted_paths为vector<Path>；common.h声明Path为vector<PathEntry>，PathEntry只有int location。故MAPFPlanner::loadPaths实际调用LNS.cpp L1186–1215的vector<Path>按值重载，而不是vector<list<int>>重载。两者相似不能据此漏计真实复制类型；首次initial_run分支不进入loadPaths。

正常后继initial_run=false。initial_success=false时，loadPaths不进入，plan先clearAll再getInitialSolution；initial_success=true时，loadPaths先clearAll、装本次冻结缓存、checkReplan，随后fix仅复用本次合格缓存或再次clearAll重算。因此旧STALE提议中的agents[].path不成为下一job的隐含输入。PathTable::reset实际销毁所有内层向量，再恢复同地图大小的空外层、重置goals及makespan；这证明该表内容被清除，不声称其它成员或容器capacity均重置。

### 1.2 不随job数累积的量

令C=n(P−1)。在所有相关长度/加法可表示且所列函数按批准入口正常执行时，以下界覆盖这些统计更新的中间前缀，而不仅是成功返回值：

| 字段或阶段 | 静态界与理由 |
|---|---|
| complete_paths | 0到n。构造为零；每次可能调用checkReplan之前clearAll重新置零，checkReplan每agent最多加一，重算前另清零。 |
| restart_times、delete_timesteps、num_of_failures | 批准纯LACAM入口中保持初值/clearAll给出的零；原增加写点属于未批准的LNS/runPP/路径删减入口，不能把其它轨道的行为套入本域。 |
| runLACAM2的局部soc、neighbor.sum_of_costs | 每agent保留的层数不超过P，正常非空solution下soc在0到C；getInitialSolution先把neighbor.sum_of_costs置零，原局部soc不会跨job累计。 |
| initial_sum_of_costs及sum_of_costs | 保守区间为[−n,2C]。导入后checkReplan先置零；其中未达到目标的路径可能被清空后仍进入无碰撞统计，单项可为−1，不能错误断言统计始终非负。重新计算成功时getInitialSolution已赋soc，fix的原L506又加soc，因此上界须覆盖2soc；保留原源行为，不把这项重复统计暗改掉。 |
| PathTable.makespan | reset给零；每次非空insert更新到不超过P−1，空路径在任何back/下标读取前返回。 |

充分算术条件可取P≤M_int、2n(P−1)≤M_int，并在数学整数中核验，而不在源int中先溢出后检查。由于P≥k+1，原补齐循环最后一次i/step递增也有k+1≤P的界。loadPaths的size_t混合表达式仍保留源的无符号转换语义及所选ABI的窄化规则，不以实数代数擅自替换源求值次序；上述条件保证最终应写入的数学统计值落在int范围，具体类型映射继续归源表示资格。

与这些量不同，stay_target确实跨正常包保留，仍使用固定73已经证明的J_plan·max(k−1,0)界，J_plan包括最终STALE的正常job。不能把中心接纳次数替代源commit次数，也不能给上述逐轮重置的统计再无依据乘J_plan。

### 1.3 跨历史普通vector容量归纳

批准域中agents[].path只经clear、有限追加或resize修改，没有从更大未登记对象move/swap转入。结合固定73已核GNU11普通vector增长规则：若此前size/capacity分别不超过P/2P，下一目标size不超过P，则无需扩容时保持界；需要扩容时size+max(size,新增量)≤2P，原max_size截断只会减小新容量。构造基例为空，故每agent此路径capacity在整个合格历史不超过2P，STALE不会破坏归纳。clear保留容量的实际费用和存储仍计。

同理，PathTable每个内层时间向量在一次reset至下一次reset间至多有P个元素，其容量不超过2P；reset销毁内层后重新建立基例。此结论不推广到deque/hash/Boost容器，也不直接给总申请量：多次分配、嵌套外层、按值复制、其它缓存和长期审计仍须逐项计费/计存储。

**本节关闭范围：** 已给上述具体统计字段和普通路径向量的跨job条件归纳，澄清了真实输入重载及原重复统计。完整AA仍须把实际P来源、批准搜索的正常对象/数值后条件、其它字段和导入表示合入；本节不把“正常返回”本身当这些前提的证明。原fresh时限链也已由根直接接齐：MAPFPlanner L56的原setRuntimeLimit(1)→getInitialSolution→LNS L655的(time_limit−0.1)×1000，是原代码常量而非实验参数赋值。

### 1.4 P的事前来源及缓存闭合

原design_exit_remaining_work的Astra Ultra限域建设已完整收件，其缓存子任务按既有源/规范核验，没有读实际输入或改文件。根f96f27直接读固定planner.cpp L218–309，4567ac核HNode构造，e0351b核真实字段，7ad9f0核LNS.cpp L1186–1339，5b5b87核L648–713，d579ec核MAPFPlanner.cpp的原提交，2f38f3核固定73已登记的唯一身份、PRE_COMMIT_SHAPE及空输出容器合同。这里不是原样R0的正确性证明，使用的是固定73 §9.2已选共同修订。

令v为所审稳定图合法Vertex身份数（可保守取|ins.G.V|），S_key=2^n v^n，P=max(k+1,S_key)。均为事前数学计数，未生成图或给实验参数赋值。同一后继(C_new,F_new)用于查找、创建和发布、真实配置/0–1 flags比较且不覆盖旧代表的既有修订，保证一次搜索已发布HNode至多S_key。不要求配置位置互异，也不把此身份宣称完整Markov状态；OPEN的重复引用不增加代表数。

原get_edge_cost恒为1，get_h_value恒为0；新节点的g=parent.g+1，rewrite仅在候选g严格小于旧g时更新g/f及parent。在这些实际加法不回绕的批准源域中，任意当前parent边满足g(parent)<g(child)：新建和换父时相差1，旧父g后来降低只扩大该边间隔。因此当前parent链不重复节点，原L247–256回溯层数M≤S_key。没有把旧depth当成当前回溯长度，重写旧父链也不破上述不变量。若已创建h个代表，则其g≤h−1，新建/重写候选加法≤h≤S_key；这是按创建次数及仅降g的归纳。

runLACAM2转成agents[].path时只保留整个solution或首达目标的前缀，故不加长。进入commitPath前仍须通过既有PRE_COMMIT_SHAPE，尤其每行有跳过锚点后的后继，即m≥2；m=0或1不能用下面公式掩盖原短分支的back读取，按既有源失败规则不进入commit。对合格行，长分支m>k给future长度m−k；短分支2≤m≤k补末点WAIT后给单项future，故f=max(1,m−k)。导入非空缓存实际补为max(f,k+1)层。

从首次fleet空缓存归纳：搜索行≤P；已接纳future≤P−k（P≥k+1）；后继原导入/补齐仍≤P。固定73 §8仅允许CAS接纳的sealed future作为下次输入，STALE不覆盖它；原load前clearAll不把被拒提议的path追加进新行。因此该P覆盖正常跨job路径历史，无须乘job数。每job外层curr_commits须为fleet个空Path，原planner_commit只追加而不清调用者行；该要求已在固定73 L423登记，本处具体接到源码，不新增一项资格门。内部vector<list<int>> future封存成输入vector<Path>时须逐行保持location、顺序及元素数，该转换的实际实现另验。

采用上述充分界时，可在数学整数中检查S_key≤M_uint及§1.2的P≤M_int、2n(P−1)≤M_int。g候选、h=0时f以及新建depth/curr_time由上述创建数界覆盖；所选P条件也覆盖这些int字段。HNODE_CNT跨job累计、其它字段/容器/分配、Π跨接纳段累计与真实库/后端对应仍独立核，不套单次P。

根接纳的是**P的条件来源、当前父链有限性及缓存长度归纳**。指数身份界与相应int不等式只是一个很松的充分证书，不能成为所有大规模主实例的必要筛选条件；某域未满足时须用它自己的更紧事前节点/路径证据或已登记的具体表示合同，不能由一次成功结果反选P。原样R0的错键/比较器没有被本证明自动修好，实际共享修订与完整AA仍待完成。

### 1.5 priorities与HNODE_CNT的全历史字段合同

同一Astra Ultra代理的下一限域字段包已终态；根4567ac亲读HNode初始化/两处fractional reset/+1，6e15ff核排序及H_goal赋值即break，582395在具名LaCAM组件与批准MAPFPlanner/LNS调用者内核HNODE_CNT全部四处出现，a4d98f核唯一诊断读点。沿已选binary32 round-to-nearest/ties-to-even、确定中间求值/存储和int32表示，不改原表达式。

新priorities向量先值初始化为零。根的(float)i/N在合法正fleet和单调整数转换下给[0,1]，允许因舍入得到1或不同agent同值。对任意已完成构造，归纳有0≤p≤2^24：p<2^24时其最大可能binary32值为2^24−1，加1后不超过2^24；p=2^24时精确和位于两个相邻float中点，ties-to-even返回2^24。因此长历史的+1不导致Inf/NaN，无需把节点数或S_key压至2^24。

两个原fractional reset中的(int)p均在[0,2^24]，落在int32域；该整数转回binary32精确，p−floor(p)精确可表示且在[0,1)。父已达首目标、但当前未到引导目标的原分支没有赋值，当前新分量保留零，不能误称继承父优先级。rewrite不改priorities；原排序只比较有限值的>，允许并列，故在此域满足严格弱序。其它索引、对象及实际浮点后端仍按既有合同核，不由本字段证明替代。

HNODE_CNT在planner.hpp L39声明static uint，planner.cpp L15静态初始为零，L30每次进入HNode构造体递增；没有每solve重置或析构递减。所审调用域中唯一读点是planner.hpp L129的solver_info诊断，没有身份、索引、分配大小或搜索条件消费者。原32位unsigned值恰为实际递增次数模2^32，回绕有定义，不能另加全历史不回绕门或把它当唯一身份。递增早于L31子LNode分配，后续失败仍可能已增，因此也不等于成功构造数或活节点数。

批准solve中H_goal初为空，首次非空赋值立即退出循环；rewrite中的非空有效邻居不会等于空H_goal，唯一solver_info调用条件不成立，符合固定73既有诊断裁决。原计数递增仍保留并收费；其它合法入口若读它，读取的是当时uint位型，不擅改为无限累计总数。根接纳这两个具名字段的条件全历史数值合同，完整AA及实际实现仍另验。

## 2. H19纯ECBS整批编号守卫：具体选择已接纳

独立建设代理external_static_binding完整读取固定73 §10/73L22相关段及作者组件commit `4c75fa20c435c440d8b6bd6dc81668ddc7296ba0`的三个完整头；原H19论文对应承接已有证据，本轮未重新读论文。

| 固定对象 | Git blob |
|---|---|
| include/libMultiRobotPlanning/ecbs.hpp | d93fbe2bd60b472af61a77c0365a3140a8c9065e |
| include/libMultiRobotPlanning/a_star_epsilon.hpp | 1b6b90a895ff14fbdb41c7eba33ecfe0b6b7a288 |
| include/libMultiRobotPlanning/planresult.hpp | 437392fd4367955813bc1c07bf7cdbc2998d183c |

根743e91/ac1773直接核ECBS调用点及根初始化，f70700/45d3c7核低层输出更新和结果字段。ECBS L150设int id=1，L248的createConstraintsFromConflict完整返回后才在L249开始遍历；L254给孩子赋id，L283无论低层成功或失败都会递增。这里有现成的整批前边界，不必修改原ecbs.hpp才能保护这些增量。

记C_prev为此前完整处理批次的child-map条目总数，m为本批完整条目数，M_int为原int最大值。批入口id=1+C_prev；完整map只有在m≤M_int−1−C_prev时才提交。批中第j个孩子获得C_prev+j，最后递增到1+C_prev+m，因此赋值和最后一次递增均可表示。仅检查最后孩子标签≤M_int会漏掉最后一次++id。

根选择在该既有回调中付费准备完整map、检查上述界并封存本批预留；累计记录包含成功与失败孩子。预留整批不等于已经执行所有孩子：暂停保留同一次source/batch身份；批中硬失败结束来源会话，不能把预留计数重置后继续原search。返回之前表示不足走固定73既有具名表示不足终态，不能返回空map假装无解、删除一部分孩子或自动重启。已经提交批次的原孩子集合、顺序和编号不变，检查及失败工作两H19臂同费。此选择落实固定73 §10已允许的“覆盖整批的严格表示界”，没有新搜索预算或算法路线变更。

可选的更强事前充分界沿原J内搜索域：n个agent、v个可通行顶点、d条合法有向MOVE/WAIT转移给出约束原子数上界U=n[Jv+(J−1)d]。每孩子须新增至少一个当前路径违反的原子，故每支深度≤U；合法child-map每agent至多一项，包含失败孩子的全树尝试数≤Σ_{r=1}^{U}n^r。其加一≤M_int可证明整次无编号耗尽；这个很松的充分界不作为采用逐批守卫的必要条件，不假设全局去重，也不新增参数赋值。

### 2.1 低层正常false后的字段

AStarEpsilon::search进入时清states并加入(startState,0)、清actions、置cost=0，不重置fmin；成功时L209–210才同时给cost/fmin赋值。ECBS根低层失败在L130–131立即返回，不先读该fmin。非根孩子由有效父节点复制，失败后未写fmin保留父计划的已定义值。因此在父字段有效的批准调用域内，失败更新为cost_child=cost_parent−cost_i、LB_child=LB_parent；这项读取不是未初始化，失败孩子也不进入open。

在原单位代价、J层内搜索和可达静态距离合同下，g≤J−1、h≤v−1、f≤J+v−2，可据此给父cost≤n(J−1)、LB≤n(J+v−2)的条件数值界。不可达哨兵不得参与算术。根ffdb4e另实核73L4 §4.4：批准入口使用新job局部Environment和空旧解，根不走warm-start；不为当前入口追加一项不需要的热启动资格。源L272在success判断前仍调用focalHeuristic，其实际partial域按下一节给出具体绑定。

**本节关闭范围：** 根已接纳整批编号守卫的精确表示规则及既有回调接缝，关闭这一具名设计选择；低层失败fmin的来源已查清。尚未证明全部focal/浮点/handle/布局及完整共同域，也未授整个ECBS运行资格。原样检查轨道保持原字节，具体适配和真实验收在相应阶段执行。

### 2.2 focal实际partial域与作者几何排序

同一建设代理进一步全文读固定example/ecbs.cpp（blob a068eee96d2d6c072d423cdab0d9bb16301a5bb4，19186 bytes）及73L4 §4.1–4.4；根a075d1/a29965直接核作者三个focal回调及getState，531e88核LowLevelEnvironment→setLowLevelContext/isSolution的调用，ffdb4e核此前已登记的失败无候选、ADG附加项和新Environment/空旧解规则。

根初始化期间仅低层两个focal面对尚未求解的空他者，原作者已经跳当前agent和空他者；根某低层失败立即返回，不调用完整focal。孩子从有效父节点复制，重规划时其它agent均为有效父路径，失败后完整focal只需排除本次失败agent；不能从start-only形状猜失败，因为合法零动作成功也有同一形状。

具体选择：新Environment以无当前低层调用初始化；setLowLevelContext为本次调用绑定agent/身份并清一个终端标记，原终止谓词返回true时付费置标记。固定低层此后重建并正常成功返回，期间不再调用focal。完整focal据本次标记纳入或排除当前agent，其余非空有效父路径照旧纳入。标记为真后的重建若硬失败，按来源失败终止，不携半输出进入完整focal。禁止用跨sibling的逐agent失败位：新sibling重新复制父路径后，那种旧位会错误排除一个已恢复的有效候选。标记不证明实际任务服务或外部输出接纳。

用K表示完整focal中上述有效候选集合。各轨迹有同一起始层τ₀，当前层先转换为相对下标k=τ−τ₀，不能把平移后的绝对层直接拿去索引states。对j∈K，令L_j=|states_j|−1，p_j(k)=vertex(states_j[min(k,L_j)])；它保留作者不消失模式的末点驻留。空候选不求长度减一、不读back；位置比较忽略visited，State身份和终止仍保留visited。

低层状态项保留对其它非空路径的Σ_j[p_current=p_j(k)]；转移项保留Σ_j[p_current_before=p_j(k+1)且p_current_after=p_j(k)]。当前位置来自回调参数，不读取当前start-only输出。各项≤n−1，初始Node的focal为零，至多J−1步的累计≤2(J−1)(n−1)。

完整几何项保持作者精确顺序所定义的值：令L=max({L_j:j∈K}∪{0})，则F_geo=Σ_{k=0}^{L−1}Σ_{i<j,i,j∈K}([p_i(k)=p_j(k)]+[p_i(k)=p_j(k+1)且p_i(k+1)=p_j(k)])，上界为(J−1)n(n−1)。保留作者k<L，不能为修partial顺手加入末层顶点评分；相同位置的WAIT对同时满足两项时仍计两次，不新增“必须移动”的条件。实际安全冲突检测仍按固定73完整末端规则，不由启发式的计数范围替代。

73L4已登记F_geo之外的ADG违反加项，但此前没有唯一计数口径。根选其最小明确实例化：F=F_geo+1[在K的候选ADG中既有规范首环检查找到环]，故F≤(J−1)n(n−1)+1。图及动作身份、首匹配和规范首环规则沿固定73，不枚举所有简单环，不改变两个低层项。这是本H19适配已登记加项的具体选择，作者example没有该加项；只宣称正常几何分量保持作者原值，不宣称整个适配排序与作者相同。选择不依据效果或删弱/强实例，两个H19臂共用。

所有标记/身份、相对下标转换、轨迹读取/延拓、图/环检查及计数实际收费。表示不足须在有风险的实际算术前沿既有来源表示不足出口处理，不饱和、不回绕、不填零。完整focal在失败孩子仍实际调用并计费，其值不把失败结果改为合法计划。根接纳此处partial身份和有限计数的绑定；剩余ECBS堆/浮点/全部资源和后端符合性仍未由本引理关闭。

### 2.3 两层FOCAL集合与已选重建修复

实际gpt-6-astra/ultra的astra_ultra_ecbs_focal_closure已完整读取固定两个搜索头、当前Q1及指定Boost 1.74 mutable d-ary堆/GNU11普通list iterator定义，交付具名归纳。原文论文/实例不在本轮新读取范围。根根据已亲读的两头选择下面的明确源修复；不将原默认高层尚未关闭的条件隐藏成一个免费运行检查器。

限定数值条件：Cost=int，各实际长度/代价/计数算术先满足原类型域；原float w有限、非NaN且满足既定w≥1。令r_f(x)为实际int→float转换，T_w(x)为相同冻结求值顺序下的float乘积。对非负源整数需要r_f和T_w单调且r_f(x)≤T_w(x)，相关乘积有限。binary32、round-to-nearest、无fast-math/超额精度的参考选择满足这些性质；不要求所有整数转换精确或严格单调，不把全J状态上界强制缩至binary32精确整数范围。

默认低层已经有条件闭合：单位步及完整time身份使同State的g相等，更优路径改键分支不可达；静态图距离在首次visited切换及之后均满足h(s)≤1+h(s')，故生成节点f不小于当前展开f，循环最小f非降。阈值上升扫描仅加入新跨过区间的节点，新发现状态至多插一次；每次取顶前FOCAL恰含当前阈值内OPEN句柄且各一次。最小f节点满足自身比较，OPEN非空即FOCAL非空。原先pop FOCAL再erase OPEN的顺序使堆比较时借用均有效，成功分支在删除前读取最小f也有非空保证。

默认高层则不能把两个性质混同。它仍覆盖当前cost阈值内所有有效OPEN成员，所以“cost下降便空FOCAL”不是成立的反例；但旧阈值成员从未移出。若随后最小cost从b_old上升至b_new，而一个已在FOCAL的h又满足r_f(C_h)>T_w(b_old)且r_f(C_h)≤T_w(b_new)，原L183会再次推入。以后选中它只pop一份却erase OPEN实体，另一份可成为失效借用。重复并不保证每条执行都实际解引用；若立即正常返回可只销毁剩余副本。当前只有这个精确源级失败谓词及抽象堆历史，未声称已构造H19几何输入或观察运行故障。约束增加不能直接推出次优低层实际返回cost单调，故不把所需单调性当已证前提。

作者已有REBUILT_FOCAL_LIST分支每轮清空/重建，但原高层L155使用open.top().LB，而OPEN仍按cost排序；它不是全OPEN最小LB。直接采用它必须另证明聚合机器比较r_f(C_top)≤T_w(LB_top)，各低层机器比较不能未经舍入分析直接求和。

根选择更小的筛选语义改动：**定义REBUILT_FOCAL_LIST，不定义USE_FIBONACCI_HEAP或CHECK_FOCAL_LIST；高层L155重建阈值基数从open.top().LB改为open.top().cost。** 这是有明确身份的两个H19臂共同ECBS组件修复，保留作者默认cost阈值含义；原样轨道保持原字节。每次取顶前清空FOCAL、按OPEN的cost有序迭代，每个合格节点仅推一次；转换单调保证遇第一个不合格可break，最小cost节点自身必合格。因此不依赖cost历史单调或LB聚合即可得到非空、精确成员和唯一句柄。

全局宏同时重建低层，合格集合和比较器与上述已证默认低层相同，完全并列的插入/选择顺序可能改变。重建分支的bestCost/bestFScore保留初始值，会影响扩展期间的临时推入；下一次选择前必clear/rebuild，故不影响取顶时的集合归纳，但临时操作、每轮清空/扫描/重新入堆及内存工作仍全部收费。不得宣称输出逐一相同、原默认字节行为等价，或继承尚未证明的原次优因子定理。

选定普通Boost mutable d-ary堆使用list实体，push创建独立实体，其它句柄不因堆数组重排失效；源在push之后、任何FOCAL插入/有序扫描之前把存活节点的handle重绑为新句柄。已选重建保证被删除OPEN实体在FOCAL中没有残留副本。代理最终补注撤回“字段复制不解引用就足以证明失效iterator可复制”的过强说法，根不采作标准保证。

根选择第二项具体共享修复：HighLevelNode复制构造仅复制solution、constraints、cost、LB、focalHeuristic和id，目标自身handle独立默认构造，不读取源handle，并保留根节点默认构造能力。这样L228的P、L253的孩子和L276入堆复制都不复制失效或空handle；存活节点仍由原L144/L277用有效新句柄覆盖后才进入FOCAL。默认handle只销毁或接受有效赋值，不要求可解引用，不改变原L233删除时机及父实体峰值。普通d-ary堆搬动list iterator、节点主比较仅读cost；这不声明任意复制整个heap后自引用字段会正确。未采用“父OPEN实体留到批末再删”的另一候选，不扩大父实体驻留来回避复制问题。

### 2.4 原int运算及binary32阈值的具体资格

external_static_binding的限域数值建设已终态。根由已封存的固定两头再次直接核ecbs L109–145/227–283、a_star_epsilon L88–110/191–245的实际顺序（e3da65同次源窗口输出），采用以下预检/回调绑定。继续使用新Environment、空旧解、单位代价及完整time身份；不增加warm-start，也不再审§2.2/2.3已关闭问题。

令M=INT_MAX、G=J−1、D=v−1。全域的一个充分算术证书为0≤τ₀、τ₀+G≤M，且max{G+D,nG,2G(n−1),Gn(n−1)+1}≤M。各式先在数学整数/合格检查算术中求值，不先用源int乘加；G+1、容器长度与下标还须满足实际size_t/max_size。本证书不必要：不满足这组保守界不等于几何无解，不要求所有主实例采用它。

| 原实际写点 | 已具体接纳的范围或前置 |
|---|---|
| 初始Node与新邻居的g/f | 初始g=0、f=h；单位步得到g′=g+1≤G，h∈[0,D]，f=g′+h≤G+D。邻居构造前保护time+1；启发式返回前保护实际g+h。不可达哨兵不参与加法。 |
| 低层focal累加 | 初值零，每步两项各在[0,n−1]，后继层累计≤2g′(n−1)。各项非负，原两个加法的中间值亦被覆盖。两个回调调用次序未指定，不能只让“后一个回调”执行守卫。 |
| 成功cost/fmin | cost_i=g≤G。终止时h=0，current尚在OPEN，故0≤fmin_i=min_OPEN f≤current.f=g。此处比§2.1的早期松界更强，不修改低层输出。 |
| 根逐agentcost/LB | 第r个成功结果后的前缀均≤rG，且LB≤cost。根新search的每次成功终端返回之前保护本次cost前缀S+g；随后源L134–135两个加法均安全。 |
| 孩子减去旧分量 | 有效父节点的cost/LB分别为非负分量之和，原L262–263减法非负；余项上界为(n−1)G。 |
| 孩子成功/失败后的加法 | 成功时两和≤nG且LB≤cost；失败时新cost_i=0而fmin_i保留旧有效值，结果为cost_parent−old_cost_i、LB_parent。失败孩子可有LB大于其cost，但不入OPEN，不误套成功父节点不变量。 |
| 完整focal与编号 | 原几何分量和已选首环指示合计≤Gn(n−1)+1；实际逐项累加及最后加指示在操作前查范围。编号沿§2整批守卫，不重作全树必要界。 |

为避免将松的全域界强制为主实例前置，根采用同一既有继续域下的具体守卫接缝：getNeighbors在构造下一time/单位步之前核下一值；admissibleHeuristic在返回有限h之前核本状态g+h；两个低层focal各自具备后继层2g′(n−1)的充分累计保护；完整focal按实际计数逐增量检查。真正到数学J末层可以无后继，尚未到末层而下一个time不能表示则走既有表示不足终态，不以返回空邻居、零启发式或假目标偷换失败，也不把J改为机器上限。

根成功成本前缀属于本次search，在isSolution返回true前检查g≤M−S。孩子则沿实际onExpandHighLevelNode(P.cost)→getFirstConflict(P.solution)→child批顺序，付费绑定同次有效父cost C_P及各原分量c_i；当前agent成功返回前检查g≤M−(C_P−c_i)。其它父fmin分量之和不超过其它父cost，新fmin≤g，因此此检查也保护后续无回调间隙中的LB加法。父分量可付费保留必要副本并绑定当前批，不在P生命周期结束后继续读取其旧引用。终端后重建硬失败则停止会话，不能沿未完成输出继续维护前缀。等到L272完整focal或下次展开才检查已经太迟，源L270–271加法此前已发生。

这些条件关闭的是明确可实现的检查位置和数学范围，不是一项任意判定内部状态的万能检查器。实际字段/身份读取、检查算术、容器循环及失败工作均收费，具体类型和检查覆盖在实现后逐项对应；其它回调/几何/图/库表示并未由本小包代证。两搜索头为此无需再加接口或新搜索修订。

浮点预检沿§2.3冻结的实际binary32 w≥1、有限非NaN、round-to-nearest、无fast-math/超额精度语义。记r为原int→binary32转换。当前阈值基数只有低层f与高层cost（含重建分支保留的初始阈值）；LB和focal计数不是这些基数。全域证书可取B=max(G+D,nG)；采用局部int继续域时可保守取B=M。在精确二进制有理语义核r(B)·w≤FLT_MAX，就给0≤x≤B上的有限乘积、单调转换/阈值及r(x)≤RN32(r(x)w)。不以可能向上舍入的普通float除法代替此充分检查，不把r(M)再窄化回int。

这不要求所有整数转换精确或严格单调，不把整个J限制在binary32精确整数范围，也不追加原次优因子定理。任一实际继续域表示检查失败沿既有来源表示不足终态记录字段/作业/批身份和已付费用，不返回算法false冒充穷尽。根接纳该数值设计包；Environment代码、编译/浮点环境和运行符合性未由本次静态接纳完成，G4不据此整体PASS。

## 3. 同一X/X_0/A的FIT建设

原Astra Ultra代理paid_service_closure的数值构造及三项边界补注均已完整收件。根直接复算下列全部和/不等式，另以d68636核固定73首轮操作表、29d249/127546核Planner/HNode/LNode与Graph字段、4417ec核具名LaCAM目录的reserve/resize调用。根接纳**这一有限参考表示和数学首轮子族的源容量存在性证书**；不是本机编译后ABI符合、全历史AA、其它站或完整roster资格。数值为存在性见证，不采用为实验配置。

### 3.1 所选数学表示及描述符子族

参考X采用GNU11普通C++14容器、新字符串ABI、原默认allocator/traits、LP64原类型：char为8位，int/unsigned为32位，long/size_t/ptrdiff_t/pointer为64位，原binary32/binary64及已登记浮点语义保持；不用debug容器、附加alignas或packing。模型字为8字节；这里实际原生类型的对齐≤16字节，故原生请求q≤2。没有扩大原源int/size_t/pointer域。

采用既有四顶点水平路径s₁—g₁—g₂—s₂、两端起点及其相邻首目标，原正k_commit取其最小数学成员。M_grid=V=4、n_f=2、e=3、N_vis=16、N_adj=24、B_bucket=4、K=2。完整输入每PROJECT行一个合法目标，首次缓存为fleet个空Path；两个源字符串长度各≤256字节，身份字段用至多256位固定编码。这是首轮证明中的有限描述符子族，不生成任何实际地图/输入/O/seed/config，不改变主roster，不赋保护参数。

字段展开给普通vector本体3字；list/tree/deque/标准和Boost hash/pairing单容器头统一保守≤32字。最大源类LNS含BasicLNS、Neighbor、PathTable少于24个此类头和128个标量/指针字，24×32+128=896<1024；其它首轮具名本体/节点同被1024字覆盖。MT按624+1=625字独计于这个界内，不把它当vector数据。已读allocator/vector的max_size给相关分配类型至少floor((2^63−1)/8192)=2^50−1个元素的共同保守下界；实际小请求另核各容器接口，不把这句推广为所有库对象的任意容量保证。

### 3.2 原生申请的结构计数

可能产生数据申请的vector生命周期按六组归属，每组以32个充分覆盖：输入/Instance/MAPFPlanner；常驻LNS/solver；dummy/Graph/LACAMInstance；Planner/HNode/LNode；键/hash/回溯；提交验证/输出。最满的节点组为Planner五成员+C_new共6、两H各4、四L各2，合计22；输入组为SharedEnvironment 8、Instance 10、MAPFPlanner两输出外层2，合计20。其余四组分别不超过18、11、15、11。为覆盖同一已列分组取6×32=192，再保守上取256；空成员也计入上界。纯移动不新申请vector数据，实际复制和两层回溯的Config复制仍计。

该最小首轮每个对象的目标size/reserve≤8，原操作序列每对象至多八次可能申请。普通vector请求数≤256×8=2048，每次容量≤16元素；每元素以1024字充分覆盖。标准EXPLORED的两插入及一次未命中查询按已读GNU11分支至多调用RConfigHasher四次，Config按值副本纳入上述键组，不留任意hash次数常数。

其它原生申请用128次覆盖：16个pairing节点、34个list节点、两个标准hash节点、两个Boost节点及保守一个dummy节点、一个set节点、至多19个源对象本体、两桶数组、六次空deque初建的12个map/block申请，以及具名源字符串/后继描述申请。pairing整轮16次分配与同时最多4节点是不同量，不能互换。

非vector块不套“至多16元素”：Boost raw ptr_bucket只有一个指针，18元素块为18字；标准13桶块为13字。deque保存HNode*/LNode*，GNU11初map为8指针字、初数据块为512字节即64字；root queue尾最多推进至3、子queue至1、OPEN至2，均无第二块或扩图。C++14两个queue和OPEN临时移动未固定消除时保守六次初建，已撤回的五次不再使用。其它对象/节点块≤1024字。因此所有这些块均小于所取的16×1024=16384字上界。

每次原生请求再加至多1字对齐损耗，得到S_native≤(2048+128)(16384+1)=35,653,760字。此量是申请累计充分界，不是实测峰值或应收费的虚构操作数。

### 3.3 明确的新增记录和辅助区

新增模型记录均按模型字对齐(q=1)，多字值使用固定字编码，不把原生16字节对象直接放进仅8字节对齐的字段。

| 新增申请 | 布局及首轮上界（字） |
|---|---|
| 唯一拥有者登记 | 8个4字段记录，对象句柄/next/kind/phase；8×4=32。三根12字及最多四个4字局部责任槽在辅助区计。借用边不重复拥有，LNode仍由原queue或当前迭代拥有。 |
| 诊断 | 原十一处正常表达式的固定文本、字段及位型使各d_j≤256；保留原四字头/正文，另加一个私有next，11×257=2827。逐字段编码，不引入十进制格式器。 |
| 源边界记录 | 16×256=4096。每记录四字头、至多32个四字身份/版本、64标量字及两份最多16字的agent小记录，合计≤228；涵盖worker、INIT/job、输入/输出绑定、正常结束节点及处置/收件。按阶段更新同一作业字段，不按基本步新造历史记录。16仅是首轮结构计数，不是新增运行上限。 |
| AUTH原件及必要完整副本 | 首轮P的INIT、规划请求/结果和处置信封不足八个逻辑对象，每件保守含原件及一个必要副本；正文≤1024、受保护描述符≤256，16×1280=20,480。仍完整封存/复制/验证，不使用免费远端注册表。 |

故S_P≤35,653,760+32+2827+4096+20,480=**35,681,195字**。

辅助区计算参考过程续体，不声称测得原生C++栈。一个参考激活记录≤1024字：含MT的记录由625字MT、至多八个容器头和128其它字覆盖，合计1009；其它记录同由具名字段界覆盖。活跃深度由源入口/适配控制14层、容器/成员构造清理16层、有限递归8层、allocator/固定字编码导入16层组成，54≤64。最长源求解链及四层边界控制、最多四节点pairing的合并递归、顺序成员清理均在该分解内；首轮没有PIBT继承/swap帮助递归，循环复用槽而不免其工作。

再保守计非堆本体/固定状态16×1024字、附加1024字、拥有者根/槽28字、诊断根3字及16字控制，R_needed≤64×1024+16×1024+1024+28+3+16=82,991字。选择数学R_aux=2^17=131,072字足够。一般历史及异常展开不由这个正常首轮深度界覆盖；实际后端对这些参考状态的符合性后验检查。

### 3.4 同一容量的阳性不等式及根裁决

取数学A=2^26=67,108,864字、D_X=D_flat=2^28=268,435,456字。完整模型区为2^31字节；存在正16字节对齐基址使整个区间低于2^32，不指定宿主地址，亦不超过原LP64 pointer/size_t/ptrdiff_t域。源模型地址的表示不改变规划图的原int索引。

根独立复算：S_P≤35,681,195<A；3A+R_aux=201,457,664<D_flat；A_max=floor((D_flat−R_aux)/3)=89,434,794>A。因此源容量条件在同一个明确X/A上确有数学满足者，不再仅写“存在足够大的内存”。同一个A用于first-fit扫描费用，不能拿更小A的旧费用套过来。原首次时限、六次deadline检查及同τ嵌入沿已有有限参考工作证明，网络/INIT/E/服务窗口仍为独立条件。

根接纳范围仅为**已列参考组件、具体记录布局和首轮数学子族的源存储FIT存在性**。未把实际主实验参数、公开实例、全AA历史或其它站取成该小结构；未证明实际修订程序、发行包二进制、暂停/计量和全部WORLD符合性。73R4的固定历史未知项保持原字节，本新增存在性证据由本工件承载；G3/G6整体仍有其它资格义务。

布局的代理直接证据包括GNU11 stl_vector.h L91–117/1776–1786、stl_list.h L81–110、stl_tree.h L101–110/168–172、stl_deque.h L89–99/454–459/488–525/618–653、new_allocator.h L197–204、hashtable.h及hashtable_policy.h上述首轮分支；Boost implementation.hpp L2574–2586/2735–2759/2948–2955/3177–3203及pairing/heap_node/stable_heap具名字段；random.h L647–648。其证据是原生字段与选定参考ABI，不升级为未经执行的编译器布局实测。

## 4. 阶段边界

用户完整目标授权实验前必要准备；在上述两处源修复已具体选择并完成限域静态论证后，根为implementation/h19_ecbs/源码包授予限定实施准入。包内仅包含固定上游必要代码头/许可、修复后的ECBS头、独立翻译单元的宏绑定、声明型编译检查及修改说明。原安排由Claude Opus写精确patch；C36两次均未取得有效正文，重试超过30分钟后中止，根接手同一具名范围并完成差异/来源/真实编译核验。这不是新的研究审查，也不循环要求已经有修复程序才准许写修复程序。

允许的检查为C++14的-fsyntax-only静态编译，覆盖实际模板实例化和复制合同；不链接/执行算法、研究测试或仿真，不生成实验输入/参数/配置/manifest/结果。原始来源树只读，修复身份与原样轨道分开；源码包暂不并入整体工作后端，不上传未另核过的代码或受限材料。普通实现在其它模块仍未准入，主实验仍NO-GO。

固定73/73R1–R4及受限输入边界不变。完整来源/场景绑定、PIE-D与H19其它资格、整个候选实现及实际验证仍未完成；本节具名代码包准入和局部关闭不换算为整个目标完成比例。

**当前包已验收：** 73C36_ATTEMPT_AND_ROOT_IMPLEMENTATION_RECEIPT_20260914.md记录两次真实调用终态和根实际实现。implementation/h19_ecbs/README.md给固定源blob、两处完整差异及精确检查命令。最终64fd2c以g++-11 11.4.0、C++14 -fsyntax-only实际实例化搜索模板，exit0且无诊断，覆盖默认构造、父/子数据复制和mutable堆插入。代码由根实现，不归为Claude输出。该包静态编译交付完成；不是运行正确性、实际Environment或整个H19资格。当前保持本地，未上传代码。

## 5. 进度口径与有限退出包

固定73的参数化科学设计和正式审查已经完成。其后的具体候选资格、实际实现符合性及完整实验前交付分别记账，不把它们继续统称为“仍在做整轮设计核验”。根以当前R4/Q1实际证据盘点，另由Astra Ultra的design_exit_remaining_work仅核现有义务归属；该任务不重新审科学方案，也不增加新的验收门。

| 当前工作包 | 具体剩余与退出条件 | 后续阶段负责 |
|---|---|---|
| R0继续域和表示绑定 | 沿现有AA/字段/修订/接口表，补P事前来源、尚余正常搜索对象/数值后条件、导入表示及参考控制对应。已有义务都有具名来源、条件和阶段归属时，结束该包静态资格。首轮FIT及本文件已接纳字段不重做。 | 实际二进制/后端的隔离、暂停、计量等符合性在实现后验证；不以尚未存在实现为写实现的循环前置。 |
| 来源及外部共同域绑定 | 沿现成矩阵完成selector/alias/有效delay/WORLD/服务区/roster所需条件，以及PIE-D两轨/H19剩余适配差异与资源、共同适用条件。将来源/适用性/差异/静态排除依据逐项交接；受限未核输入保留明确未核状态。 | 完整实际实例合法性和忠实实现须有对应阶段的实际证据；不重读L23顶替全来源资格，也不在缺证据时宣告G4/G5通过。 |
| 已准入实现交接 | 当前仅收完§4的ECBS两处源修复、宏绑定、声明型模板实例化，由根核来源/差异及真实-fsyntax-only结果即结束当前包。 | 全部运行验证、W01–99实际覆盖、预注册/工具冻结/实验前稿及复现包仍属完整实验前目标。 |

前两包承担剩余具体静态资格；第三包及后续实际符合性不再算未完成的整轮科学设计审查。包数、门数及文件量不能换算为完成百分比或可靠工时。首轮容量存在性已接纳，FOCAL/handle已具名修复，不继续沿旧活状态记“未收件”；冻结R4保留其历史状态。

## 6. 全来源输入事实核验的具体范围：已准备，尚未扩读

external_static_binding的来源交接已终态，仅使用固定73/L23/L23A/已有矩阵与固定Git树元数据；根03b68d独立完整取得四配置目录和delay目录的482条路径/mode/blob/size，未读新增正文。481项mode100644、一项100755，均普通blob且身份互异；可执行位不等于执行许可。5cb8e0核L23已有对象表和“原载荷未缓存”记录。

固定版本仍为R0 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。配置范围是lifelong_benchmark/city/、game/、random/、warehouse-s/四目录中直接子项*.json，规范相对路径字节序。各91份，总364份、97,572 bytes；扣L23已核四份后，剩余360份、96,495 bytes。旧四份分别是city/game/warehouse-s下agent-1000_scen-delay-0.001-1.json及random下agent-100_scen-delay-0.001-1.json，不重复它们的基础存在性核验。

| 固定目录 | JSON | agents | tasks | maps |
|---|---:|---:|---:|---:|
| city | 91 | 18 | 18 | 1 |
| game | 91 | 10 | 10 | 1 |
| random | 91 | 7 | 7 | 1 |
| warehouse-s | 91 | 15 | 15 | 1 |
| 合计 | 364 | 50 | 50 | 4 |

delay目录另有13对象，random/.DS_Store一项不属于正常来源候选，故482=364+50+50+4+13+1。潜在数据池117项，L23已核其中13项；根按原报告13个blob核元数据差集，首次未核上界104项、255,889,455 bytes。104仅为目录池上界，不是已经证实的引用闭包或必须全部读取的清单。

下一有限只读包分两步：先读取剩余360份配置的实际driver字段、类型和有效语义选项，规范化相对引用并核固定树身份；再仅取这些配置实际引用、且为相应静态谓词所需的数据对象。数据池仅限四类别各自agents/tasks/maps子目录与lifelong_benchmark/delay/；池外引用先登记路径/角色/元数据，不自动扩读。mapFile/teamSize/agentFile/taskFile/delayFile/taskAssignmentStrategy按原消费者解释；numTasksReveal等未消费字段保留原记录，不升级成有效深度或实验参数。

需要核查地图形状/字符/索引、agent/task的计数/整数/记录语义、每个实际配置组合相对其地图的通行/起点互异及所需分量关系、任务分配与delay行/宽度。只读取实际引用闭包并按blob去重；不运行规划器或仿真，不生成实验配置/manifest，不采用公开文件数值作为保护参数。

L23只保留身份和计数/检查摘要，原正文只在当次内存中，不能从这些摘要重建完整地图、位置序列或delay矩阵。因此新agent/task相对旧地图的交叉核验可能需要按需重新取得同blob地图；新WORLD或有效delay投影也可能需要相关旧blob。此为新谓词的数据依赖，不重做L23原基础结论。下一授权范围须包含这类按需读取，不能声称旧总计数足以验证新组合。

完整selector、delay接ACTUATOR秩、source_id/alias字段、服务谓词和层级等权roster的规则已在固定73 §8–§12给定，不再列为“路线未定”。本包仅补全配置/引用的输入事实；全部profile/O、effective_delay投影、WORLD嵌入/F/Z/驱动、具体服务区和合并后roster/权重仍需对应绑定。公开任务顶点本身没有服务区几何字段，原delay总1数不证明任意投影相等。

PIE-D两条身份轨道及固定完整作者候选沿73 §10 L597–614；H19论文ADG/cut重构、ECBS-FA及visited合同沿L626–648，当前源数值修复沿本文件§2。native离散delay消费与共享ACTUATOR投影不能混同，也不能继承共享alias分组。已有L18/L19的用途和对象对应依据继续使用，不再选择新基线。

**权限状态：本节只读报告和元数据，新增正文核验未执行。** 当前用户此前仅批准L23四类首配置及其引用的一次有限核验；上述剩余360份及按需引用/交叉读取超出该次范围，须在这个明确包上取得扩大只读范围的确认。其它已授权准备可继续，不以此把整个目标标记完成或首次即标blocked。
