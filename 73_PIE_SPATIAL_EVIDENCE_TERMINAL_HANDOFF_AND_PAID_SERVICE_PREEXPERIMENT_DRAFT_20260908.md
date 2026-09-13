# 73：原边空间证据、终点交接与付费服务——实验前整合草稿

起稿2026-09-08，根整合修订2026-09-13；**DRAFT / NOT-FIXED / NOT-REVIEWED / NOT-ACCEPTED**。本轮主工作平台选择同原MOVE的GROUP_PREFIX，把有限组准入、累计cap/显式RUN、空间退休及完整付费角色合入正文；整边作为明确机制参照保留。选择工作草稿不表示资格通过或唯一最终路线，信息精度/来源/外部组合等未闭仍需修订。72三路及72R4已齐后创建本编号，69–72和报告不改。本稿固定后仍须科研导师skill→根不用skill分析→Nature reviewer skill→根不用skill分析→无任何skill独立逻辑→根验收。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT，不自授资格。

## 1. 研究问题、主张和动作边界

本文明确以 Zhang、Chen、Harabor、Le Bodic 与 Stuckey 的 **PIE-D** 为改进框架：[Concurrent Planning and Execution in Lifelong Multi-Agent Path Finding with Delay Probabilities](https://ojs.aaai.org/index.php/AAAI/article/view/34506)，AAAI 2025，39(22):23387–23394，DOI 10.1609/aaai.v39i22.34506。具体复用其作者固定仓库的LACAM-only规划入口及承诺/未来路径切分链，采用§9.2登记的共同源码修订；执行、状态获取、预测、任务同步和计费按本稿重新定义。此适配不等于原论文的完整PIBT-D＋A实例，未保留A的旧路径指导启发式或MAPF-LNS改善阶段，§10逐项列明。本稿研究有限尺寸/横向跟踪偏差下的安全执行，以及可信途中信息与空间释放的净成本效益；共享源修复和模拟计算适配不作为D策略创新。DARI已淘汰，不是前置任务或待恢复方法。

真实机器人有尺寸及跟踪偏差；按名义格点判断通道清空可能不安全，而一直保留整段占用又会延迟后车。研究问题是：在保留 PIE-D 新 MOVE 提议来源时，付费取得可信参考进度、只释放已经证明不再需要的空间，能否在持续任务中取得正的净服务率增量。普通反馈误报/迟报、真实空间偏差和处理耗时分别建模，随机 no-start 不能改名为定位误差。

规划层为离散四邻接图，执行层保留连续实体足迹、连续参考运动和有界跟踪误差。方法不改变原边、目标或新 MOVE 顺序；只允许接受原MOVE、同MOVE单调前缀cap、合法COMMITTED_WAIT、阻塞HOLD、继续旧tid或在已证明可行域内制动/保持。没有主动绕行、补邻边、伪目标或在 unsafe proposal 上偷偷换轨。底层参考控制是假设明确的理想执行模型，不声称已经装进 LIMO。

主共享四臂为D-S、R-S、D-F_cap、R-F_cap：D为§7纯阻塞导向查询，R为轮询；S按已付可信进度退休当前前缀后方，F_cap只增已授前缀、原END前不退休，实际q_release=0。四臂共享GROUP_PREFIX及相同cap/组/重试能力。F_cap不同于旧整边启动时已占M0的F，旧2×2的释放因子含义不直接继承。唯一确认主比较是 NATURAL 中 D-S−R-S 的固定总体真实服务率差；策略自己的查询/处理/维护工作计入，同费用函数及服务容量。STRICT 预付等容量的机制比较、退休因子及交互另列，不择显著者充当主结果。方向性假设 HYP-NET 为该差的期望正；零或负、队列成本吞掉收益、提前取得证据却没有真实服务增量都能推翻它。不是“只要安全就算有效”。

2026-09-12明确选择共同确定性模拟计算法P_model作为本未固定稿的工作路线：所有部署算法、源规划、观测和控制检查的计算供给按§9有限基本步定义，真实宿主CPU/经过时间/内存完整另报且不反向决定虚拟Q、源时钟或故障。处理等待仍由已付工作和原公共供给形成，不删除处理延迟。主theta现在明确是在P_model下的固定来源效应；保留原配对、w、E及所有主次比较，不声称与实测宿主elapsed模型的theta数值相等。旧稿严格物理机器指令计量和P29真实elapsed备选不作为当前规范。此选择来自S2、C25–C27及根独立取舍，未等于后端、来源非空或整稿审查通过。

本候选保留的具体路线是受限平移模型下的原边安全接入、空间退休与付费观测调度，不改题目去声称已解决任意速度/姿态的窗口可达集合接入。主比较的R-S已使用同一固定裕量和合理的途中退休；F_cap只是一种明确的保守释放因子，不能代表所有固定裕量方法。另设必报实用性对照E0：不主动购买途中POSITION，仅凭共同PUSH_RECOVERY付费终点推送/READY交接；E0只付自身cap/组功能需要的几何，不构建无用途退休或D分数索引。D胜R而输E0，只支持限定查询制度内的选择改进，不足以宣称途中主动观测整体划算。G/N几何实现比较另列，不扩充为事后可任选的确认主检验。

真实横向跟踪偏差和可信信息滞后为主机制；普通不可信反馈错误不改变共同安全权限，单列其负荷/压力效果，不认领为D独有鲁棒性。准确的采样内容仍可能付费且迟到；它不等于免费即时全状态。主设计不向任何臂赠送实际pose、逻辑cursor、任务账本或控制器状态。若未来改为免费全状态或一般集合接入，须重新定义主效应与协议，而不能用本D−R结果代替。

用户要求大规模 lifelong 仿真为主：必须考察持续任务吞吐、失败、处理/通信/内存及首次/复用成本，不能由局部清空例子外推规模收益。小场景用于解释机制和反例；两台已有 LIMO 仅可选有限现实证据。无硬件本身不否决纯仿真，但有界模型、可信接口、全成本与外部效度必须显式。未确认实车定位/控制配置，未开始实物、实现、构建、测试或仿真。

当前任务设施明确采用理想外部世界合同：真实服务仍按固定TASK_SERVICE行及全实体/队首条件发生，求出该真值的仿真宿主计算完整另报，不受模拟内该任务行CPU工作配额约束；原任务服务机会限制及全部部署算法/控制/观测的有限供给保持。该模型修订由P21及根P22明确，主Q/E衡量给定设施下的虚拟lifelong表现，不是含真实任务识别/派单处理器瓶颈的全硬件部署吞吐，也不是Q除仿真宿主耗时。不能将算法工作挪入世界费或以理想设施承诺实际后端通过。

## 2. 一手来源与备选路线

下表保留亲见强度；全文为完整提取文本，不等于每幅图或所有排版公式已核。根的阅读/身份审计已归档，但不把部分材料或顾问转述计为自己全文。旧 69L1/69E1 原句柄不可访问、约定完整报告仍缺，新增定点证据不冒充旧任务返回。

| 来源 | 实际范围 | 可以支持的机制比较 |
|---|---|---|
| Hönig 等，RA-L 2019，10.1109/LRA.2019.2894217；[作者 PDF](https://whoenig.github.io/publications/2019_RA-L_Hoenig.pdf) | 根完整7页/873提取行 | ADG 执行依赖及实际机器人背景；准确控制/及时完成通知前提不等于任意空间偏差和假完成保护 |
| Zhong/Rossi/Shell，Autonomous Robots 50 article5，2026，10.1007/s10514-025-10225-4；[官方全文](https://link.springer.com/article/10.1007/s10514-025-10225-4) | 根完整HTML；109306字符；原HTML SHA256 6d1bd846552a9c29bd6fb1f4d40b78c434eaffc7f8ed5f2d64930af4f512e741 | 主动观测与同步成本已有直接近邻，不能将付费观察本身称首创 |
| Zhu/Brito/Alonso-Mora，Autonomous Robots46(2)，2022，10.1007/s10514-021-10029-2；[作者PDF](https://autonomousrobots.nl/assets/files/publications/22_zhu_auro.pdf) | 根完整20页/77578字符；PDF SHA256 6de59654091de1bdf388f1544c00e7ce4be1236f2b1aad89dfd682c7897e2e83 | B-UAVC 直接针对位置不确定性，但概率几何/控制域不同，不是保持原 MOVE 的同能力 wrapper |
| Shahar 等，JAIR70，2021，10.1613/jair.1.12397；[公开原文](https://par.nsf.gov/servlets/purl/10297272) | 根完整32页/87953字符；SHA256 def08325da0ee2d4d12e01fd5ed864acaa224b87b0421f402803b9e4a68023bd | 有界时长占用与感知/通信；不能据此把任意空间偏差归为延迟 |
| Zhang/Chen/Harabor/Le Bodic/Stuckey，PIE-D，AAAI2025，10.1609/aaai.v39i22.34506；[官方论文](https://ojs.aaai.org/index.php/AAAI/article/view/34506/36661) | 根已补齐完整8页/793行；此更新发生在71固定之后 | 必留的原提议核心、并行规划执行和原 no-start 域；不认证共享适配的 native trace 等价 |
| Okumura/Tamura/Défago，AAAI2021，10.1609/aaai.v35i13.17347；[官方PDF](https://cdn.aaai.org/ojs/17347/17347-13-20841-1-2-20210518.pdf)；Ma/Kumar/Koenig，AAAI2017，10.1609/aaai.v31i1.11035；[官方PDF](https://ojs.aaai.org/index.php/AAAI/article/download/11035/10894) | 根分别完整9页/803行、8页/960行 | 外部 TIP/MCP、no-following、末状态/WAIT/MOVE语义；两个同名 MCP 不因此逐字等价 |
| Kim等，TII22(8):6859–6870，2026-08-01，10.1109/TII.2026.3681327；[作者机构](https://pure.korea.ac.kr/en/publications/a-scalable-framework-for-lifelong-multiagent-path-finding-with-as/) | 当前正式卷期与完整摘要已核，非正文 | 异步先后调度、剩余路径复用/重新同步值得比较；完整换其规划器/派单改变动作来源，空间/反馈错误覆盖未知 |
| Zhuang等，RA-L10(5):4652–4659，2025，10.1109/LRA.2025.3554099；[作者学校](https://faculty.xidian.edu.cn/HT2/zh_CN/index.htm) | 作者题录/Crossref，未核一手摘要/正文 | active conflict/decentralized execution为近邻线索；不能从标题构造其算法或引用第三方性能数字 |
| Kasaura/Nishimura/Yonetani，RA-L7(4):10494–10501，2022，10.1109/LRA.2022.3187265；[作者项目](https://omron-sinicx.github.io/PSIPP-CTC/) | 根完整项目/34页作者幻灯片文字；代理读原文转录但未核上传者/原生PDF及逐符号图，不增记根期刊PDF全文 | 几何冲突关系预计算可减在线工作；整个优先规划器不完备，multi-query不等于lifelong；固定出发时差CTC不替本后缀证明 |
| Lehoux-Lebacque等，ECAI2024，10.3233/FAIA241017；[官方PDF](https://journals.sagepub.com/doi/pdf/10.3233/FAIA241017) | 根完整9页/857提取行，会议非期刊 | 动力学/朝向/占用与依赖任务，有条件安全等待位置；整套VP*改变路径来源，时长扰动不等于空间偏差 |
| RAS 10.1016/j.robot.2025.105295；[出版商](https://www.sciencedirect.com/science/article/pii/S0921889025003926)；Sensors 10.3390/s26134139；[出版商](https://www.mdpi.com/1424-8220/26/13/4139) | 官方摘要/章节片段，非全文 | 安全区间/预计算与局部受影响者重规划可比较，不能据片段泛化完备性或反馈鲁棒性 |
| AI 10.1016/j.artint.2026.104586；[出版商](https://www.sciencedirect.com/science/article/pii/S0004370226001128)；RAS 10.1016/j.robot.2026.105701；[出版商](https://www.sciencedirect.com/science/article/pii/S0921889026003726) | 官方元数据/预览，非全文；编排刊期不等于已核在线日期 | 直接时序执行/协议观测近邻，全文排除和强新颖性仍OPEN，不宣称对方缺少本机制 |
| Chen/Li/Fan/Williams，S2M2，AAAI2021，10.1609/aaai.v35i13.17340；[官方九页PDF](https://ojs.aaai.org/index.php/AAAI/article/view/17340/17147) | 新有界代理读完全部988行可提取文本；根另读模型及§4方法窗口至L718，非全文/逐式版面审计，截图失败；会议非期刊 | 控制模型/初集/扰动决定误差界，段间状态集合包含已有先例；定时扫掠占用不自动覆盖任意迟启或超窗停留，MILP/PBS整体会改变新MOVE来源 |
| Yan/Smith/Li，WinkTPG，[arXiv:2508.01495v2](https://arxiv.org/html/2508.01495v2)，2026-04-26 | 根补读模型/实证/结论窗口并亲核II-A与VI假设；独立代理读II–VIII全文文字、表格文字及页尾，未审图像/PDF/源码；HTML自述accepted不替正式题录 | 给定无cycle conflict路径的速度优化、依赖数选择、状态更新和前缀保留已有先例；形式扰动为通行时间，另有真实反馈控制实验及计算/通信开销报告。本付费POSITION与空间包络、lifelong净Q/E须论证具体增量，目标差异不证明优越 |
| Okumura等，MAPF-X/Tree-LaCAM，npj Robotics4,20，2026-03-14，10.1038/s44182-026-00083-2；[官方正文](https://www.nature.com/articles/s44182-026-00083-2) | 根完整方法/讨论的指定窗口，补充材料未读 | 时空预测、不确定性、离散规划与MPC/CBF已结合；形式搜索完备性不等于真实系统无条件安全，整个替换改变本MOVE来源 |
| Cao，SCALE，[arXiv:2607.00591v2](https://arxiv.org/html/2607.00591v2)，2026-07-03 | 根核版本及III/IV相关窗口、非全文逐式/图表审计；按指定预印本记 | 已有扫掠占用、released前缀、未放行路径局部修复与接续，不能将冻结前缀/授权执行泛称空白；未搜到error不证明其无误差处理 |

选此组合的依据是实际空间包络与同原动作域可自给证明、净费用可以配对检验；不是因为71已经写了长稿。单中心是范围明确的替代，减少多owner的提交负担但引入中心队列瓶颈。异步轻量调度、局部复用和几何/控制方法继续作为机制比较对象；若需改路才能消环，就列独立规划算法域，不能潜入本wrapper。没有任何论文或当前见证保证本主总体正效应。近邻若证实已覆盖关键组合，须缩小主张、增加匹配对照或另编号换路线。

P15/P17名义参考备选经P16独立分析后仍保留，但本轮不采用删除eta/原APPROACH的控制变更。根P20独立复算C18完整Opus建设回执后，选择NOISY_ALGEBRAIC_REFERENCE_PROFILE为当前未固定工作profile：保留原eta及LAUNCH/APPROACH/BRAKE/HOLD，明确以a_hi−a_lo=4delta与有限实代数输入/有限常值驱动域换取参考状态和事件的代数闭合。这是解析控制设计关系，不是原整个参数域等价或事后调参；各内部/外部共同底座相同，真实执行器和完整roster是否支持仍须资格核验，不能静默剔除不合格成员。原广域条件安全证明单列；H19原T_nom保守界仍适用，不混入名义参考备选的新时间式。数学可计算不保证实际费用/容量和净吞吐，合法信息若已确定实际历史，各臂可付计算费推断，不能禁止合法推断或强制证书制造POSITION收益。

根P19给固定TASK_SERVICE行的全实体判定提供独立条件证据，P20将其有限空间驱动子域与当前保留eta的参考profile组合：w在原公共O相邻不同时刻间为精确实代数常值，kappa/z初态/段界与服务行时刻精确可表，F沿已给有限凸多边形或凸分解，ServiceRegion为有限闭凸多边形。变分公式每个z分量是有限个代数系数乘exp(代数指数)之和，不要求z本身代数；全实体包含化为有限facet/vertex不等式，精确合并相同指数后，系数全零给真实闭边界，否则由[Steinberg与Redheffer的Lindemann定理表述](https://msp.org/pjm/1952/2-2/pjm-v2-n2-p11-s.pdf)和认证外包细化判非零符号。保留原包络内非零横向w/z，不把随机延迟改名；明确限制原任意有界可测驱动和一般服务区，不能事后缩roster。此点值判定不解决连续首次事故/Stop触点或实际世界计量，不能不可判就算未服务、延迟真实A或用零填Q；全部资格仍未闭。

## 3. 物理域、可信条件与有限参考到达

参考原边从u到v，ell=||v-u||>0，e=(v-u)/ell；本模型为固定世界朝向平移，F为非空紧足迹，Z为给定闭盒。实体X(t)=u+s(t)e+z(t)+F；z_dot=-kappa z+w，kappa>0、|w_j|≤kappa zbar_j、|z_j(0)|≤zbar_j。变分公式z_j(t)=exp(-kappa t)z_j(0)+integral exp(-kappa(t-a))w_j(a)da给|z_j(t)|≤zbar_j。因此实体速度可因z_dot回摆，参考s单调不代表真实位置单调。普通y/COMPLETE/pose可有错误、缺失、迟到和重放，但不驱动可信控制状态或授权退休。

主工作平台改为同一原MOVE的GROUP_PREFIX：中心已兑现cap为b，本地已安装cap为C，S制度实际退休下界为q_release；0≤q_release≤s≤C≤b≤ell，v_ref≥0，v_ref²≤2a_hi(C-s)。b只由先预留后的中心提交增加，C只由合法累计授权增加，q_release只由可信证据及付费退休提交增加；中心不因此知道C或s。原边、tid、slot、目标、世界误差状态始终不变。F_cap/E0在原END以前保持q_release=0，另有POSITION证据也不得混用为退休值。

参考s_dot=v_ref、v_ref_dot=a_cmd+eta，|eta|≤delta。符号控制条件0<delta<a_lo<a_hi、a_launch>0保持，执行器允许所列命令范围；这些是待合法绑定的模型条件，不给保护参数数值。令xi=C-s。LAUNCH在xi>0且v_ref²<2a_lo xi时取a_cmd=a_launch+delta，直至首次v_ref²=2a_lo xi。从零速开始，F_L=v_ref²+2a_lo(s-s0)-2a_lo xi0的导数为2v_ref(a_cmd+eta+a_lo)，且F_L≥a_launch(a_launch+a_lo)t²-2a_lo xi0，故有限交点在cap之前出现，上界sqrt(2a_lo xi0/[a_launch(a_launch+a_lo)])。合法非零速重入时G=v_ref²-2a_lo(C-s)<0，其导数同为2v_ref(a_cmd+eta+a_lo)；速度至少按a_launch增加，积分给有限首次过零且此时xi>0，不假设重入速度为零。

当前有限工作profile另要求a_hi−a_lo=4delta；保持delta/a_lo/a_hi原意义与原命令能力假设。对既定a_hi和delta，可满足原delta<a_lo当且仅当a_hi>5delta，这是解析条件而非赋值/经验选参；真实能力尚未核定，不能反向缩真实扰动界。O时刻、初始参考状态/边几何/控制字段及eta常值均由有限实代数表达式合法绑定，eta只在既有O相邻不同时刻间常值；空间w的同类有限表示见§2/8。两种驱动仅在原O已经允许相应输入更新的行换值，其他行不能自行注入新段或FAULT机会，同刻点值更新不使状态跳变。未生成O、系数、分布、段数、roster或保护参数值。下述广域P1–P5条件安全保留，有限profile是其明示子域，不替代外部适用性证据。

APPROACH令r=v_ref²/(2xi)，a_cmd=-r+delta(a_hi+a_lo-2r)/(a_hi-a_lo)。xi>0时r_dot=(v_ref/xi)(r+a_cmd+eta)；r=a_lo时括号delta+eta≥0，r=a_hi时为-delta+eta≤0，所以闭带[a_lo,a_hi]不变。d sqrt(xi)/dt=-sqrt(r/2)，从xi0到当前cap的剩余时间在[sqrt(2xi0/a_hi),sqrt(2xi0/a_lo)]内。到达按混合接点延拓s=C、v_ref=0、reference HOLD，不计算0/0。若C<ell，只是同MOVE的中点HOLD；只有原s=ell、v_ref=0才可能§5原END。

BRAKE只在v_ref²≤2a_hi xi的可证域进入，命令-a_hi-delta。制动余量B_safe=2a_hi xi-v_ref²的导数为-2v_ref(a_hi+a_cmd+eta)≥0，首次零速前位移≤v_ref²/(2a_hi)≤xi，随后HOLD；B_safe是证明量，不是任何保护预算。HOLD的参考零加速度及连续底层闭环为显式理想混合公理，不由普通反馈推出；实体仍可随z运动。恢复旧tid只在新的明确RUN实际接纳且C>s时重入LAUNCH，原方向不变。界外侧滑/转向/未证制动/可信控制故障不在定理域，按原故障评分保留。

累计cap安装令C_new≥C_old且状态s/v_ref/z不跳。制动余量增加2a_hi(C_new-C_old)，故不变量保持。原运行模式为LAUNCH/APPROACH时，新r不超过旧r；新r<a_lo则LAUNCH，新r仍在闭带则APPROACH。BRAKE优先且必须到首次零速，安装新cap/接到新RUN均不能提前取消已开始制动。HOLD安装后仍HOLD，需后继新的RUN尝试；已处理无作用RUN的副本不能以后复活。若旧cap到达与安装同刻，先发生物理到达/HOLD，再处理安装，不能隐去接点自动续跑；若旧cap就是ell，原END关闭优先，旧cap/RUN一律不能再打开入口。

P1现在明确为固定已安装正cap、合法RUN以及最后不中断活动段下的有限参考到cap命题。每原MOVE的cap来自§4有限CAND且只增，故成功增量次数有限；要完成原ell还需要更大授权、实际安装、必要RUN与后继服务。P1不证明任意丢包/无容量下到原终点、全系统无死锁/无饥饿或实际LIMO误差界。任一满足全部前提的碰撞仍反驳本证明，不能事后改前提。

P5受限原端点拼接保持：世界参考p、实体平移基点x=p+z。旧原边(u,v)在tau真正END后至新原边(v,v_next)在sigma≥tau合法进入，p=v、z按同一世界闭环连续演化；w有界可测无冲量，F/Z/kappa/控制律不因换边改变。新边只设局部(s',v_ref')=(0,0)，不清零z；故p及x/z无跳，参考速度两侧为零。新正cap C'>0与零速满足新制动锥，P1可应用于该PIE原MOVE；完整新原边静态合法仍必需。中点cap不应用这个换边规则、不换parent、不消费原slot。

等待期间X⊆E=v+K。旧已授集合在真正END时b=C=s=ell，始终包含E；中心终点改tag保留Mask(E)，新初始正cap集合又包含新parent E，故READY/消费/新授权等待无覆盖空隙。任意长合法HOLD保持Z不变。P5不把参考零速等同实体停车，不认证旋转、非零速或偏置参考起点拼接；没有jerk、轮速或驱动滞后限制，须如实称为理想平移域。一般新z/足迹缩小或旋转、非零速度转向都不能自动继承。

## 4. 前缀几何、区间事件与可计算预处理

K=Z⊕F；U(q,b)=union_{s∈[q,b]}(u+se+K)，0≤q≤b≤ell；为保留完整原边记号，U(q)专指U(q,ell)。主活动责任是Mask(U(q_release,b))，M0=Mask(U(0,ell))只作完整静态合法及组候选域，不再表示每次初始授权必然已经持有。有限闭瓦片覆盖执行域，Mask包含一切相交瓦片，闭边界接触也计冲突；完整U(0,ell)仍必须静态合法。合法格点路径不自动保证有尺寸实体可通，不用动态失败筛图。

P2前向证据定理：同tid样本j在付费CAPTURE时t_j给q_j≤s(t_j)。中心在R合格提交q_new=max(q_old,max_j q_j)，其中全部t_j≤R且q_old≤s(R)；随后s单调、s≤C≤b及z∈Z，故从R起至原END有X(t)⊆U(q_new,b(t))。融合max不能回溯到较旧样本的时刻。b可后续增大但不能回撤；退休不撤销已发权限，因为q_new≤当前s且后续s不退。F_cap/E0不把q_evidence代入q_release，下一MOVE独立重建原身份和q，旧样本不跨occurrence。

对r∈M0，I_r={s∈[0,ell]:(u+se+K)∩T_r≠空}。算法域保留有限有理凸多边形瓦片或其已给定有限凸分解、有限有理闭盒Z和有限有理凸多边形F或有限凸分解，原边端点精确可表。用u+lambda(v-u),lambda∈[0,1]求各凸块线性约束的可行投影上下端点，再精确合并为有限闭区间并I_r=union_h[a_rh,d_rh]；接触端点不删，非凸一般不能当单区间。根式进度可用lambda表示，不用未证浮点近似跨过闭边界；一般紧集本身不提供可计算算法。未知/未认证几何不准授权或退休。

完整边的lambda_r=max I_r仍存在，旧P4：r∈Mask(U(q,ell)) iff q≤lambda_r；endpoint资源满足lambda_r=ell。主前缀则必须改为r∈Mask(U(q,b)) iff存在h满足a_rh≤b且d_rh≥q。只用最后退出lambda_r会把尚未授到的远处相交算进当前占有，亦不能表示暂时退出后再进入，故旧单指针整边算法不直接继承。

令D_geo为0、ell及全部相交区间端点的去重升序集；每对相邻不同端点加入算术中点，形成有限CAND，含0和ell。若D_geo有J个点则|CAND|≤2J-1；J只是输入计数，不是保护参数或调参量。初始普通授权只尝试ell；只有§5通过全组证明的GROUP_ADMIT可选择严格内点初始cap。已授扩展在CAND中检查全部x>b，选当前可安全兑现的最大者；不按当前效果切换规则，不声称有限CAND保存所有连续调度可行性。

精确参考N-GEOM对每次合法(q',b')按规范瓦片顺序构造[u+q'e,u+b'e]⊕K并求相交集合；允许缓存静态数据、只处理可能变化资源等合理优化。新集合必须经owner/围栏/绑定核验后原子提交；扩展只允许合法新增，退休只删除仍属于原tid且确已不相交的资源。失败/未知不部分发布，已做工作照计。E0只为实际cap/组功能构建有用几何，不被迫建立无用途的退休索引或D分数表。

主G-GEOM采用区间事件的精确同函数组织：分别按(a_rh,资源key,h)与(d_rh,资源key,h)排序。每资源计数n_r(q,b)=#{h:a_rh≤b}-#{h:d_rh<q}。因为q≤b，每个被减区间必已被加，所以n_r≥0且n_r>0当且仅当I_r∩[q,b]非空。从初始(q=0,b)按实际索引建立计数，之后b增大只跨入口事件，q增加只跨严格退出事件；每区间至多各一次，资源仍可先变零后再次变正。所有计数、指针、owner修改均在私有准备后同中心提交，不以指针提前推进丢失失败工作。F_cap不需要无用途的退出事件消费，允许按自身用途省工作。 已提交(q_release,b,n_r,入口/退出指针,owner及相关P版本)必须来自同一事务快照；失败私有增量不发布，已发生费用/日志/保留内存不退。重算从已提交指针开始，除非同一仍有效的私有作业及全部引用/费用继续保留；实际整表复制及大整数运算不免费。

P6现在为上述N/G的同(q,b)精确集合等价，直接由区间非空判据及n_r公式证明；不同数值近似并不自动等价。设合并区间总数M_int、收到更新数c_upd，成功提交路径上每个区间的入口/退出各兑现至多一次，不同事件总数至多2M_int；废弃/重做的私有工作可能重复扫描，全部实际费用另计，每更新的固定开销亦另计；建区间、合并/排序、资源owner/围栏/索引/签发、实际位复杂度与全部重试不包含在这个局部枚举界。只对成功提交、不重复计算的事件组织可给O(c_upd+M_int)局部更新界；失败尝试与重扫次数必须另加，不能写成全算法O(1)或全地图线性。几何/足迹/资源版本变化须失效重建，跨原occurrence不免费复用可变指针。

G/N机制比较固定同查询与S，比较相同集合函数的计算组织；NATURAL中不同真实费用可改变排队、采样和轨迹，语义等价不意味着闭环逐迹相同。D/R比较选谁购买证据，S/F_cap比较何时退休，E0比较不买途中证据的实际经济性。所有臂都用固定空间裕量，不把前缀或G-S称为动态误差管。

## 5. 前缀组准入、累计权限与不可逆终点交接

信任域：唯一中心资源authority与各低层gate不分叉、会话内状态持久不回滚；授权和可信证书不可被普通错误包伪造。中心同一时刻只占用一个可暂停应用作业槽，所有检查/计算/资源访问付费。普通作业只有一个提交单元，计算完后在严格后继发布点一次原子应用私有增量；GROUP_ADMIT的全组仍是不可拆的一单元。§10的ADG_ENQUEUE是明确另定的有限批控制器：在同一占有槽逐个计算、封存和发布单记录单元，前单元成功发布后才可于后继PROCESS_SLICE继续下一单元，批终态处置完成才释放槽。任一时刻至多一单元计算或待发布，外部不能见该单元半更新；普通作业及批的未发布结果继续占槽，后继中心作业不能先读/改账本。此是收费的单机串行提交模型，不是假设跨owner免费原子事务或第二writer。计算期间物理及其他服务站继续。中心fail-stop不重启/清空/重新分配，阻止其后的新计算/发布；已经发布的单元与物理责任保留，不承诺恢复活性。

每资源owner为FREE或(agent,tag)，tag为resident gamma或活动tid。每agent有当前resident/活动记录、连续关闭请求水位d_i和至多一个未关闭请求e=d_i+1；tid=(session,i,e)，原slot、原边、parent gamma、M0、几何版本不可变。未授状态UNGRANTED、已授GRANTED；关闭结果为ABORTED或FINISHED。中心拒绝e≤d_i的任何首次/重复请求，不可复用序号；e>d_i+1拒绝而不跳过未知责任。标准数学整数无回绕，位成本仍随序号增长。普通消息无权生成新的可信序号/原步。 中心活动记录另含b、授权lineage/cap序号、q_release、可选q_evidence、desired_mode及组身份；control_epoch为同session、同agent的持久单调代际，INIT从无历史前哨开始，跨tid、FINISHED和退栏均不重置。本地独立持C、最大已实际处理控制代际及该代际内已处理公共控制尝试水位。初始b与C为无活动授权的零值，首次准入后b>0；记录中的M0只代表完整原边，不等于当前持有集合。组准入围栏与物理owner分别记录，agent的组成员关系保持至付费退栏，不能仅因旧tid FINISHED便消失。

中心唯一请求槽是Active视图的唯一派生来源：同一session/agent最多保留一个未闭请求，Active按agent投影恰为该槽处于GRANTED的完整tid。原请求首次登记、普通/GROUP授予、未授取消和FINISHED均在原中心writer的完整提交中一致更新；同e的异alpha不得覆盖原绑定，合法重复只幂等重放。GROUP成员的agent身份互异且各绑定其唯一UNGRANTED槽，部分cap、扩展、重传、MODE、APPEND/enqueued与后继规划均不能创建第二请求。发生请求槽/Active索引不一致或同agent双Active属于协议矛盾，保留责任并按既定证据故障处理，不以任挑一条、清空或免费扫描修复；所需核验与索引维护计实际费用。这细化原单请求不变量，不增加新的物理资格门或给予查询者真实状态。

slot=k表示原occurrence从Π_i[k]到Π_i[k+1]，消费前真实c=k、消费后c=k+1；slot不是目标下标。请求保留起始slot、两端点及MOVE/WAIT类型，避免把PRECHECK的c相等与外部plan[c+1]混成不同索引。计划代际plan_epoch在整个合法episode固定，append只增独立revision；追加未来段不使已有cursor证书失效。 内部PIE的共同L与外部H19的每agent执行长度L_C,i分别见§8/10；统一slot仍从0编号，长度为L的执行账本有槽0至L−1及顶点0至L。外部源图generation不重置执行plan_epoch或c，APPEND安装不等于消费。

executor显式持久phase为BOOTSTRAP、RESIDENT_OPEN、GRANT_ARMED、MOVE_LIVE、TERMINAL_UNCONSUMED或QUARANTINE。BOOTSTRAP只允许原世界给定的参考HOLD及其误差闭环，不允许新MOVE/WAIT消费/PRECHECK；软件未就绪的应用角色除INIT外返回付费NO_APPLICATION_READY，不将未安装索引当空集合。INIT合法转交后才RESIDENT_OPEN，其有合法resident_gamma与resident_ref、active_tid=NONE、pending=NONE；GRANT_ARMED已接纳唯一grant但尚未START；MOVE_LIVE已START、原occurrence未END，允许同tid运动/制动/HOLD；在这两个phase保留的起点resident字段仅是parent元数据，不能作当前位姿。TERMINAL_UNCONSUMED为END已发生且旧槽未消费。原occurrence=(session,plan_epoch,i,k)，计划代际不随append改，revision单列。pending指向不可变EndRecord和可变TerminalHandshake：前者保存原动作及唯一END事实，后者保存ready_verified、consumed、缓存/重试引用。END时c仍k、两个标志均false；中心FINISHED、READY在途或已验证均不使其退出该phase。已消费历史由单调c/关闭水位及必要closed记录拒绝重放，不要求无限位图。QUARANTINE禁止新作用并保留既有物理责任，已缓存历史收据可收费重放，不暗含域外机器人瞬时安全停车。

MOVE请求必须由中心SOURCE_REQUEST角色用已验证Kc指定的原Π步产生，带parent gamma。PRECHECK的付费CAPTURE必须同时验证：session/authority/tid/原occurrence及不可变源记录匹配；phase=RESIDENT_OPEN、active_tid=NONE、pending=NONE；resident_gamma=parent_gamma且resident_ref等于原边起点u，参考HOLD且v_ref=0；true c=k、该occurrence未消费且未END；相关命令/原记录/几何依赖版本有效。证明完整绑定这些谓词及采样身份，失败仅给付费DEFERRED_REJECT，不回真实c/位置或正确下一槽。成功采样后的当前槽是MOVE，无grant不能消费它，没有pending便没有可消费该槽的旧READY；较旧READY已消费、较新READY不匹配。因此在未接纳当前grant且parent/版本未变时，迟到READY不会推动c越过该MOVE。准入仍在实际接纳点复核phase、pending空、原起点、c/未END和完整绑定；不能以旧快照覆盖已发生的新授权或版本变化。中心使用该ENTRY只作限定准入事实，不据它更新Kc或生成下一槽。 组成员被围栏继续约束时，不允许产生或接纳该agent的下一原MOVE；已有原tid的扩展、合法终点交接/READY消费及WAIT不受此额外原边屏障阻止。中心的组限制不能借PRECHECK读取私有新cursor。

普通初始授予只尝试完整ell：M0全部FREE或同agent当前parent resident且不受外国组围栏/自身未退组限制，完整绑定与PRECHECK仍有效才接受。parent E包含于U(0,ell)，一次提交改tag、b=ell、GRANTED及累计grant，之后才发送。资源冲突保持UNGRANTED与原resident，不试探授任意小cap；一般最大初始cap已被P3反例否定其进展保证。唯一初始部分cap来自下述GROUP_ADMIT，不能在运行中按成败换成未登记策略。

GROUP_ADMIT是新增的公共固定角色，通用token只入既有Srv_C FIFO，不增加容量/优先级。付费捕获全部结构/PRECHECK有效的未授原请求及owner/版本，以请求为顶点、完整M0与另一请求的初始resident冲突为有向边，收费求含循环的强连通分量。每个组按成员规范key排序，候选组按最早请求首次中心登记行、再成员key元组排序；该登记行与需求首次进入P行分别保存，不混用tie依据。只考虑组的完整F_G=union_i M0_i内没有组外owner、没有本组之外的活动tid/外国resident、没有其他组围栏，且组员均为所列合法起点resident的候选。已有未接收/未START的外国grant也算owner，不能先设栏再等其消失。缺请求、未知几何/版本/条件、模式不准新occurrence分别拒绝或NO_CERTIFIED_GROUP，不默认为可行。

事前可信POSITION服务profile还必须有已认证精度epsilon_i：合法同tid CAPTURE在参考进度s给下界max(0,s-epsilon_i)≤q_sample≤s。epsilon_i来自固定服务的信息合同，不根据候选需要临时选择，不等于实体跟踪误差，也不是保护参数；该来源未闭时不能凭假设零误差通过组检查。候选c_i∈CAND_i严格位于(0,ell_i)，l_i=max(0,c_i-epsilon_i)，A_i=Mask(U_i(0,c_i))、B_i=Mask(U_i(l_i,ell_i))；要求A_i两两不交且B_i两两不交，所有几何和资源容量均可认证。

具体有限选择为Theta=union_i{x/ell_i:x∈CAND_i}去重升序；对每alpha取c_i=max{x∈CAND_i:x≤alpha ell_i}，剔除含0/ell的向量，取第一个满足上述条件的alpha。向量数至多sum_i|CAND_i|，不枚举笛卡尔积；不是所有可行向量的完备搜索。按候选组序扫描，单个GROUP_ADMIT只提交第一个合格组或明确空/失败。所有候选失败、排序、分量/几何/owner/版本扫描均收费，不在单token内接着准入第二组。

F_G是有未来排他能力的准入围栏，不是第二物理owner或清空证书。它禁止非本组登记责任新增占用F_G；当前无物理owner的围栏资源也不能对外称完全FREE。检查A/B、PRECHECK保持条件、组版本及全部记录/消息槽容量后，一次中心提交设栏，给每成员唯一原tid登记c_i/l_i/B_i及初始b_i=c_i，把A_i从合法parent改tag给该tid，转GRANTED并持久保存各累计grant；未完整完成则无部分预留/半组围栏。A_i含原resident且两两不交，因此中心原子准入不要求机器人同时安装或START。

已有GRANTED原tid的SOURCE_OR_EXTEND在当前b之后按CAND降序检查，取满足完整身份/模式及新增owner/围栏条件的最大x；目标集合是Mask(U(q_release,x))。无更大合法项给NO_EXTENSION，b不变；成功时先增量预留、保持旧责任并提交新b/累计授权，再发送。q退休是独立先完成的中心事务，不与失败扩展拼半提交。原b与已发送cap不可撤回，无证书也必须保留这些共同尝试机会；到cap不是扩展前提。每条新增占有路径都检查所有围栏，包括普通整边、组准入和其他活动tid扩展。

组内后续扩展无需等所有成员到cap。因为b_i≥c_i≥l_i，新增集合Mask(U_i(q_i,x))减去Mask(U_i(q_i,b_i))包含于Mask(U_i(b_i,x))⊆B_i，且B_i彼此不交。组屏障q_release,i≥l_i或中心FINISHED只是“余下完整扩展均可授”的充分证据，不是拒绝提前合法扩展的必要条件。E0同样可以检查/扩任何当前合法cap，不因不购买POSITION而删去能力。

组员真正END后的同agent gamma_prime允许接续旧组责任；FINISHED、READY及消费不释放F_G，也不允许该agent下一原MOVE绕过围栏。新增公共GROUP_RETIRE角色在Srv_C付费扫描组，按组建立行/规范key选择首个满足全部成员中心FINISHED、终点resident合法接续、旧cap/RUN受永久关闭守卫约束者，提交退栏并解除组成员的新MOVE限制；没有则收费空结果。GROUP_RETIRE与GROUP_ADMIT为两个独立token角色，不能同一token退栏后再准入，不由真值或FINISHED私下追加公共容量。退栏不删任何endpoint owner；组/消息历史GC仍等全部引用结束另付费。中心fail-stop、永久no-start/失联/未闭tid不因超时撤栏，长期围栏及外部等待是必须保留的负结果。 退栏的永久关闭谓词只凭该组固定成员原tid已验证END_PROOF所蕴含的历史本地END事实，不读取本地当前C/s、待ACTUATOR队列或READY消费状态，也不以READY已发送代替。组记录持续引用成员关闭证明及合法接续gamma_prime至退栏完成，不能先GC唯一证据；这不新增安装、到cap、START或消费ACK。

CANCEL须可信且绑定完整当前请求身份，包括尚未首次登记的合法e=d_i+1。在同一中心序列中，若尚未GRANTED，则原子记录ABORTED、推进关闭水位并持久化之后才回CLOSED；不改resident、不消费c、不释放不存在的部分预留。迟到首次/重复REQUEST均因e≤d_i拒绝。若GRANT先提交，CANCEL返回DENIED_GRANT_LIVE，不能回“已释放”成功ack。证明两局部顺序：CANCEL先使吸收性水位成立所以GRANT不可再产生；GRANT先使取消分支不可进入。没有多owner“此刻FREE”的清理推断，也不允许已发grant超时回收。请求重试只在确知当前请求已关闭后换新e，旧逻辑slot可仍未消费。 对未提交的扩展或组私有候选可以废弃计算结果，已提交任意正cap后原tid已GRANTED，CANCEL一律拒绝；不得只撤未安装的b段、改tid或回滚随机/费用来恢复。组部分成员没有安装也不能拆回已原子发出的其余授权。

gate有自己的持久关闭标记g_i：初始为未执行过授权的前哨，只在其旧tid不可逆END时提升为该已执行请求的e。它不免费读取中心d_i；d_i还包括未执行的ABORTED请求，两者不是同一变量。验证grant须会话/签发authority有效、e>g_i、slot等于gate当前真实c，并匹配原边、parent及当前唯一授权；不要求e=g_i+1，因为中心取消可留下从未发grant的序号。中心的未授取消不可能产生可重放的有效grant，已发grant又不允许取消；已执行旧grant则由g_i/幂等标志拒绝。这些条件与中心d_i共同保护重放，不需要免费同步两端水位。

累计CUM_CAP绑定完整原alpha、不可变授权lineage、单调cap序号和值；同序号不得异值，不把以后q退休的一般账本revision当作撤销旧grant的条件。初次包可直接为任意已提交较大cap，无需收到丢失的小包；付费验证及实际接纳点满足RESIDENT_OPEN完整谓词后安装C=b_packet并转GRANT_ARMED，保留唯一active_tid。同tid后续包只在GRANT_ARMED/MOVE_LIVE接受且b_packet≥C，低于C拒绝、同值幂等。封存与真实接纳间再核当前phase/原END/关闭水位/身份，包不能改s/v_ref/z/c或原目标；本地不需知道最新中心b，只需合法签发的不可撤销lineage。

cap与RUN/STOP是独立权限。每次普通或组初始GRANT提交为对应agent的持久control_epoch取严格后继代际，登记当前原tid的RUN_ALLOWED意图；这不自动产生RUN、START或额外token。MODE BRAKE/RESUME只对当前GRANTED原tid取严格后继代际并分别登记STOP_LATCHED/RUN_ALLOWED，无此tid则收费NO_MATCH且不把意图锁存到未来tid。累计cap扩展/重传和CONTROL_RETRY不推进代际。每次控制尝试完整绑定session/agent/tid/slot/parent、控制代际及模式、唯一公共机会的全序位置和来源kind；MODE与SOURCE_REQUEST使用同一公共总序而非两个会碰撞的局部计数器。CONTROL_RETRY只按中心已知当前tid/意图生成本次尝试，不读取本地C/s/模式。Srv_E付费认证后仅发布不可变候选；ACTUATOR按候选实际发布入列的固定次序一次处理一条，在同一有费用保障的原子接纳中复核身份、phase、关闭/代际/尝试水位及运动守卫，再记录处理事实并施加一次作用或无作用结果。新RUN仅在起点或中点HOLD、C>s且no-start未阻止时START/RESUME；运行中、C=s或缺grant无运动作用。BRAKE已开始必须先到零速，本次RUN不留下自动启动钩子，后继需另一个明确新尝试。

本地有效控制代际和已处理尝试水位仅在ACTUATOR实际处理点更新；Srv_E认证通过不提前施加STOP、改变运动模式或废弃旧RUN。低代际不得覆盖高代际，同代际矛盾模式拒绝；同代际已处理位置及更早位置不可再生效。完整绑定且当前身份合格的新尝试，无论成功、no-start、C=s、运行中无作用或BRAKE尚未到零均消费本次尝试；未认证、已永久关闭或属于其他当前活动tid的包不推进当前活动代际/尝试水位。缺grant分支仅在完整认证的原alpha/slot/parent匹配本地RESIDENT_OPEN、真实c、resident和未END原步，active_tid/pending均空且e>g_i时，登记一次已处理拒绝；不是让任意未来或旧tid抬高水位。其他永久失效身份以closed/原步守卫直接拒绝，不保留无限旧尝试位图。候选入列记录由Srv_E发布，消费事实及控制水位由ACTUATOR写入，两者遵守同一本地事件全序；Srv_E不得把验证时旧快照整块写回覆盖后来的ACTUATOR状态。乱序丢包靠共同后继累计cap重传与新RUN恢复，不延长旧无作用RUN寿命；队列、引用、持久化、拒绝和整数位成本均收费，无回绕。

MODE产生的首次控制命令同样绑定其公开MODE行并进入上述控制尝试水位，不额外派生CONTROL_RETRY机会。本平台不向中心发送cap安装/到达/START结果ACK，审计器日志不可供中心策略读取。CUM_CAP不含s/q，到C<ell不产生END首推，不以缺ACK/处理时长/重传次数提高q或触发额外维护机会。本地当前守卫与必要按公开payload位长的有限分支padding占共同控制供给并计费；这只规范该接口，不要求D/R/E0所有算法强制等工作。没有信息论无侧信道总保证，也不能从统计相关性造确定退休下界。

每个原MOVE有完整身份alpha=(session,agent,source_family/source_job,plan_epoch,原action/slot index,u,v,MOVE,几何/控制版本,tid,parent_gamma)。PIE臂原index仍是k，外部SYSTEM臂绑定自己的真实源动作，不改名为PIE。唯一end_id由alpha和不可逆关闭代际确定，gamma_prime随此身份固定，不随推送、轮询或attempt改变。合法grant接纳之前须付费准备此原动作的记录模板、终点记录/握手槽和本地不透明待办描述符；容量/身份准备不成则不得接纳新grant。真实END时只完成下述有限既定字段与事件点写入，记录容量和共同控制费用必须已得到保障，不将无限分配、签名或业务队列扫描藏入物理守卫。

只有MOVE_LIVE同alpha/active_tid、原c=k且未关闭，在可信s=ell、v_ref=0时发生END。它是唯一物理优先的原子本地转移：关闭原入口、提升g_i；将原tid/u/v/ell/parent/gamma_prime/源及几何控制版本、原END守卫/closed事实、权威物理END事件点和记录提交身份写入EndRecord并从此不变；建立pending及未就绪/未消费的TerminalHandshake；转TERMINAL_UNCONSUMED并参考HOLD，active_tid←NONE、resident_ref←v、resident_gamma←NONE，c保持k；登记唯一绑定end_id的本地不透明LOCAL_END_OFFER。NONE表示尚未接纳中心的新resident身份，不表示实体或中心资源为空。该转移及记录/描述符按实际位长承担共同控制费用，不免费签发证书、不向中心发消息、不改owner/Kc/ADG或任务计数；不能因应用槽忙而推迟或重做真实END。不能认证所需物理/记录原子转移时按可信/协议故障合同处理，不能记成功推送。中点cap HOLD不建立EndRecord；旧槽已END而未消费时禁止再次PRECHECK。

主共同终点配置选定为PUSH_RECOVERY：每个真实END只产生严格后继公共行才合格的本地待办，在既有Srv_E(i)队列按正常付费容量服务，不新增PROCESS_SLICE。首次正服务先付费CAPTURE固定已登记不可变EndRecord的引用/版本，再付字段复制、完整绑定检查、封装/签发和本地提交，建立EndProofCache[end_id]及后继发送意图，释放本地槽后才交Srv_N。证书同时保留物理END事件点和首次收费历史记录捕获点，两者不混成新的动态位姿采样。已有正缓存时只收费查验/复制/传输，不新建sample_point。原ENTRY(i,END)轮询能力保留；本主配置该机会返回付费NO_END_POLL，不产生请求，不能在运行中依效果改为另一配置。另立PUSH_AND_POLL或POLL_ONLY须事前单列共同配置。启用轮询时，push/poll在同一本地writer合流至唯一正缓存；真实END前的新请求仅给其固定捕获点的END_NOT_YET/NO_MATCH，旧负回复重传不刷新，后续新鲜检查需新付费请求。消费清pending不销毁尚有引用的EndRecord；迟到服务仅可完成其缓存/发送工作，不能重建pending。

END_PROOF完整绑定alpha/end_id、原END/closed事实、gamma_prime、EndRecord提交身份、两种事件点和签发authority/完整性；它只证明该原动作历史END，不给新c、当前pose、新边q或任务服务。END_PUSH与END_POLL_REPLY的区别仅是取得途径/请求关联，传输attempt不改证据身份。NETWORK送达只登记中心接收token，Srv_C后继收费验证、读取当前账本后才处理：格式/authority/版本或绑定无效则拒绝；当前GRANTED且首次匹配则准备一次完整终点交接；已FINISHED且完整身份相同仅取原READY缓存重发；FINISHED身份矛盾为PROTOCOL_CONTRADICTION；ABORTED/未授/不合法生命周期拒绝且不复活；水位关闭且缓存合法退休返回CLOSED/HISTORY_RETIRED。所有重复、空结果、拒绝均付实际费用，旧包不能修改后来holder。

首次中心终点提交必须原子地复核当前GRANTED及alpha/end_id/parent/gamma_prime，核Mask(E)仍归原责任，将E转同agent resident gamma_prime并清其余原tid资源，记录FINISHED和d_i，移除该tid的Active及失效阻塞/索引记录，持久保存完整可重发READY/FINISH_RECEIPT并登记后继发送意图。READY绑定alpha/end_id/gamma_prime/v、终点包络版本、预定中心提交id、唯一READY id与中心认证；全部核验/索引/封装/签发工作在合法发布之前付费完成，READY只有该原子提交发布后才可发送。禁止先FINISHED后另找机会创建唯一收据；容量不足时所有变更仍私有，原资源完整保留。中心在首次GRANTED处理历史END仍安全，因为旧入口已关闭，合法下一边先依赖此READY消费；若早已进入后继，旧证明只能落重复/历史分支。H19共同适配在收到已提交FINISH_RECEIPT后另付ADG字段/依赖维护费，不从本地待办免费得finished。

本地READY接收作业付费验证中心完整提交证明及当前pending/alpha/end_id/gamma_prime，只令ready_verified=true，c仍k、resident_gamma仍NONE。LOCAL_POLICY的后继实际提交须再次检查TERMINAL_UNCONSUMED、c=k、匹配原MOVE/closed/pending/ready_verified且consumed=false、active_tid=NONE、resident_ref=v、resident_gamma=NONE、参考HOLD于原终点及gamma_prime绑定；一次提交先从pending复制resident_ref←v、resident_gamma←gamma_prime，标消费、c←k+1、保持active_tid=NONE，再清pending并转RESIDENT_OPEN，不连锁处理下一槽。旧/不匹配或已消费READY拒绝且不改当前命令版本；中心FINISHED或READY验证本身不打开本地入口、不写Kc，下一MOVE仍须新PRECHECK及预留。

丢包恢复有两个共同公开角色。END_LOCAL_RETRY(i)在Srv_E收费读取自己的握手/缓存：pending且尚未READY时封存缺失正证书或重发同一END_PROOF，否则收费空结果；不重新动态采END。READY_CENTER_RETRY(i)在Srv_C收费读自己的缓存/已付消费证据，按原tid序选最小尚未核得消费证据的合法READY重发，无对象则收费空结果；不读取私有c/pending，不先要求新END查询。PRECHECK、CURSOR的合法接收同时登记其明确蕴含的旧消费证据，已核消费而等待GC的缓存不参与重试。两条路径共享既有站/通道及有限机会，所有重复费用照计；缓存存在且必要服务/传输最终完成才有条件恢复，永久失联、fail-stop或无后续容量仍可停滞。

本地合法一次消费及新resident责任建立前保留EndRecord、握手和正缓存；以后须所有仍有效作业/编码/在途/审计引用结束，才付费GC。中心只有已付同代际CURSOR证明c≥k+1，或合法后继PRECHECK明确证明旧槽已消费及新resident绑定，且所有引用结束，才可回收READY；PRECHECK的生命周期用途不更新通用Kc。不能因已发送、超时或无ACK删唯一可恢复收据；缺消费证据时继续记保留内存成本，不承诺无限运行的固定内存。FINISHED但收据无故丢失违反原子持久不变量，属于协议/存储问题，不以新动态END采样伪造旧收据；本合同没有增加任意崩溃重启保证。

P3覆盖归纳：WORLD_GIVEN bootstrap按同世界HOLD/Z不变性持续覆盖实体；软件INIT同agent同包络接续所有bootstrap责任。初始普通或组授权均使parent包含于实际正cap集合并先预留后签发；cap扩大只加合法资源，随后本地C只增且不超过已兑现b，§3保持s≤C；P2保证q_release≤s，因此X⊆U(q_release,b)。q退休不回撤原权限，未知真值不删资源；F_cap/E0保留更大集合。END时b=C=s=ell、E始终保留，同agent改tag及READY/消费不产生空隙；中点不改tag/不消费。CANCEL未授无物理资源变化，已授拒绝，旧消息不改新tag。围栏只限制新准入，不取代实际owner覆盖，退栏不删endpoint。若不同agent实体相交，其交点属于共同闭瓦片，两者当前责任都需该资源，与唯一owner矛盾。此条件证明不保证一般无死锁、跨组公平、窗口吞吐正或永久丢包后的释放；满足全部前提的碰撞仍是有效反例。

## 6. 真实游标、付费采样与共享知识

真实c_i由executor私有持久维护；中心SOURCE_REQUEST/QUERY/planner仅持已交付Kc_i，不可解引用私有c。LOCAL_POLICY、CURSOR/ENTRY可信authority按各自限定权限付费读自己的c，不因此让中心免费获得。Kc是同计划代际CURSOR证书中c的最大值，未知不推0；软件INIT合法提交可给予已计共同初始证据。MOVE仅匹配READY后的LOCAL_POLICY一次消费，WAIT仅合法RESIDENT_OPEN一次消费；HOLD/no-start/grant/普通反馈不消费。即使同进程也不能通过别名、日志或队列业务旁路传私有新cursor。

公共CURSOR机会按固定agent规范顺序逐一轮询，初始前哨在第一key之前，空fleet属于输入非法；每机会请求一个agent，包括resident/NONE/纯WAIT，资格不由算法当前需求改变。CURSOR只返回(session,plan_epoch,agent,request_id,sample_id,c,sample_point)，不顺带给q或实体真值。POSITION是独立付费服务，请求必须指定tid；仅匹配gate当前活动tid或保留的同tid终点记录才给含真参考区间，NONE且无匹配记录返回NO_MATCH，不能推断清空。ENTRY保留PRECHECK或END接口；END按§5共同PUSH_RECOVERY默认首推、历史正缓存与可选轮询规则取得，仍是付费完整绑定证明；TASK服务的算法可见回执另定义。四臂和guarded TIP有同一可购买能力，不跨反事实臂转移payload。

新鲜可信服务及首次END历史正证书封存的捕获规则：机会只登记通用作业，具体新鲜请求经§9付费生成并提交后才入authority队列；END历史首推则用§5已在grant接纳前付费准备、真实END后登记的唯一不透明引用，严格后继行才入Srv_E。authority作业首个语义操作是付费CAPTURE，不足以支付该原子读取则本次没有采样。其在PROCESS_SLICE行的物理推进及先前结果发布全部完成之后、该作业其他语义工作之前，原子固定一致authority视图，记sample_point=(公共行,子事件序,CAPTURE)、request/sample序号与输入版本。此前已提交的POLICY更新计入，此点之后不计入；大快照以不可变版本根固定，后续字段复制另付费。AUTH_WORK只是此authority工作步骤的别称，不是O的额外免费事件。余下处理只能操作冻结内容；AUTH_COMPLETE指作业完成、不刷新，DELIVER指严格后继NETWORK/接收验证作业的付费提交、不赠送状态。算法只在其后付费POLICY/QUERY的实际输入捕获点读取已交付知识。CAPTURE失败或完成后丢失不更新知识，已发生费用不退。TASK的全部字段必须来自这个固定全局修订，不能拼跨修订局部片段。

已封存END正证书/READY缓存重放不是新鲜authority采样：服务首步只付缓存与引用检查，沿用原物理END点和原历史CAPTURE点，后继发送/接收点另记。END首推的本地描述符只授权后继Srv_E访问所绑定历史对象，元调度器和中心不能据其类型、队列或到达时刻提前获得真实END业务事实。TASK/POSITION/CURSOR/PRECHECK仍按各自新鲜请求的付费CAPTURE，不从历史缓存推当前真值。

重传已存在证书保持原request_id/sample_id/sample_point/payload，只收实际缓存/通信/验证费；新鲜采样必须有新请求序号和重新付费CAPTURE。区间生成的确定性封装及传感创新只以本请求语义key取值，并必须包含捕获时真实s；已确认不包含为可信模型破坏，不是普通误报。q_sample取区间下界与合法[0,ell]保守处理，中心只在同tid验证后取max更新；旧tid的大q不能用于新MOVE。 S制度的q简称实际q_release；F_cap收到POSITION只可更新独立q_evidence而保持q_release=0，E0不请求POSITION；任何组充分清除判断只能用实际q_release或中心FINISHED，不凭q_evidence释放owner或围栏。中心cap b、安装确认和真实END以前的到cap本身均不是退休证据。

73P13及根P14把POSITION精度义务分开为信息来源、包含性/有限表示和混合事件次序。若同一合法采样信息相容的真进度集合为S_tau，对全部相容世界共用q需要q≤inf S_tau、q≥sup S_tau−epsilon，故diam(S_tau)≤epsilon只是实数证书存在的必要条件，不能从高运算位数推出。相同LAUNCH命令和两端允许eta在仍属该模式的一段可产生delta tau²进度差，条件足以超过既定精度时仅命令/扰动界不够；这不是任意profile都失败的定理，也不更改空间偏差w/z为随机延迟。

当前观测来源仍为FINITE_CAUSAL_REFERENCE_HISTORY：仿真可信参考子系统付费保留实际已安装cap/执行命令及已经发生的eta因果前缀，不向策略开放历史、实际pose/w/z、主seed或未来创新；策略仍仅见规定证书。当前有限profile使用§3明确的实代数字段和O区间常eta，同刻多行不造正时长段。读取实际已发生eta是新增来源能力，不是仅凭原命令/扰动界就已知真进度，也非原任意有界可测输入等价；§3广域条件安全另列。过去常值驱动可以按公开模型产生合法预测信息，任何臂拥有合法确定信息时均可付计算费推断，不以证书形式独占该能力；不读尚未发生尾部。因果日志与world/controller一致、实际费用后端未资格化前，不给执行资格。

来源具体采用CURRENT_SEGMENT_ROOT受限只读视图：可信本地当前段绑定session/agent/原tid或合法同tid终点身份、原边/模型、精确段起点t_a/s_a/v_a、实际模式及已生效C/eta；采样点与段一起冻结。该视图只承接真实已发生因果前缀，不是全知回调或中心可解引用对象。CAPTURE在原物理推进、自主切换和先前合法发布之后固定最新已生效段及必要历史终点索引根，随后才付费查请求tid；只匹配原current/保留同tid EndRecord，否则原NO_MATCH，不扩历史权限。后继cap/eta/END可建新根但不改冻结依赖；版本覆盖实际段语义，command_revision单独不足，顶层与所有代数DAG/几何绑定须传递不可变。内部段修订及模式/eta不成为新wire旁路，算法仅见原证书字段。

若可信控制已合法建立该精确段，POSITION可局部求原采样点，不强制重复重放/积分全部历史；LAUNCH/BRAKE/HOLD及§6已给APPROACH式仅在实际合法段内使用，旧cap/原END先处理，xi=0不代APPROACH。根尚未物化s(tau)时，代入/求值/认证细化仍是本查询Srv_E工作；表达式短不表示DAG/位长或运算恒定。完整历史及控制一致性的证据责任保留，仿真内部变量或浮点地址不自动成为精确受信根。来源、最小权限、原子保留及实际计量后端仍未资格化。

若CAPTURE冻结的合法历史可得到真实s(tau)的外包区间[L_q,U_q]，有限端点以精确二进制有理数编码且实际U_q−L_q≤事前观察profile的epsilon，则q=max(0,L_q)满足max(0,s−epsilon)≤q≤s；不能输出一个丢半径的裸double/截断十进制冒作证书。epsilon来源先于组阈值选择，不能临时调精度或设0；原epsilon须有有效正性/比较表示，或可认证一个不超过它的正有理精度见证；这只用于满足既定精度，不另设可调参数。正精度可认证余量与输入同步细化是一般有限终止的条件，数学实数下界存在本身不保证有限wire可表示。旧同tid q延迟后仍安全，但不保证交付时误差仍≤epsilon，不给新tid/END/CURSOR知识。

根P20独立推导当前noisy代数profile：固定C、常eta的合法APPROACH段，令xi0=C−s0>0、r0=v0²/(2xi0)、r_star=(a_hi+a_lo)/2+2eta、A=r0−r_star，N(tau)=xi0−v0 tau/2+A tau²/8。则s(tau)=C−N(tau)²/xi0，v_ref(tau)=(v0−A tau/2)N(tau)/xi0，最早T_cap=4xi0/[v0+sqrt(2r_star xi0)]。r_star与r全程在原正闭带，y=sqrt(C−s)严格下降至零，A=0不除A，首次接点按原HOLD/END延拓而不穿越cap。常段LAUNCH令a0=a_launch+delta+eta、G0=v0²−2a_lo(C−s0)<0，首次切换为[−v0+sqrt(v0²−a0 G0/(a0+a_lo))]/a0且在cap前；BRAKE常段首次零速为v0/(a_hi+delta−eta)。给定代数外部时间/初值的有限段组合仍为实代数，不假定任意积分值代数。原一般D_a=a_hi−a_lo下的Phi积分及区间反演只保留为更广未闭后继分支，不混作本profile当前实现依据。

当前profile在数学层面可精确比较外部O时刻与自主到达/切换的实代数事件，因而关闭P14中该子域的同刻判序缺口。每次eta实际改变或cap实际接纳后用当前状态重建局部表达式，先处理旧自主边界；旧cap同刻先HOLD、原ell先END、BRAKE不可提前取消、HOLD扩cap不自动RUN完整保留。推进不越过下一公共外部时刻读取未来eta；HOLD仍按理想混合公理维持参考零速，不积分v_dot=eta令其自启动。理论有限过程不证明实际库/计量/容量已合格，不能以浮点容差、概率零或世界引擎标签替代比较；真实物理顺序未认证仍属INFERENCE_UNAVAILABLE，不能洗成普通传感器丢包/零分。只有物理历史已认证而观测工作未完成时可保持世界并记无新证书/完整费用，NO_CERTIFIED_GROUP与HOLD仍可发生。

CAPTURE付费固定tid/sample_point、当前段和必要历史索引的不可变根以及保留登记；其完整原子操作容量不足便未采样，等待原机会并保留实际已做费用。仅查询诱发的复制/持久化、读屏障、额外引用/写入及旧节点寿命延长均由实际购买者支付；不能把新增知识取得移入world/control或P22任务宿主例外。原控制无本查询仍必需的精确段建立只计一次，不为未发生的全史重算虚收费用；实际查询需要的读取、历史查找/遍历、复制、DAG解码、代入/局部求值、精确比较/开方/区间细化、整数位长/分配、封装及失败占原Srv_E同作业和既有PROCESS_SLICE，待完成仍占槽，后继发布/通道/验证/退休/日志/GC照收。物理与END不被查询锁住，旧根仅在实际引用仍有效时保留；自足证书不再引用根时无需只因在途强留DAG。不因计算困难重采样、不加O/容量，冻结后的END不刷新旧样本，下一MOVE不改其tid。捕获后普通计算/分配失败不给新证书、不给假NO_MATCH；只有物理历史已认证时可按查询未完成处理，根失效/与控制不一致仍是来源或协议证据破坏，不能洗成普通丢包。D/R享相同合法来源与费用，E0不虚收查询专用工作；同臂合法已付结果复用只省实际未发生工作，不跨臂共享。无根式表达式不等于固定免费运算，开发版FLINT文档只是API线索；数学有限编码不保证有限O实际完成。

pure WAIT链：POLICY合法使私有c:k→k+1，位置和resident不变、算法Kc不变；共同CURSOR请求排队→首个付费CAPTURE冻结k+1→期间可再消费WAIT而证书不变→付费完成/投送→后继算法机会才更新Kc。若CAPTURE在原WAIT之前只能冻结k。主PIE的barrier/PROJECT与该臂TIP均可复用已付费证据，不按使用者名字重复收采样费；实际读取/计算/广播接收工作照收。POSITION不提供pure WAIT逻辑进度，主算法也不能绕过CURSOR读取c。

## 7. 付费扩展需求、阻塞查询与公共维护

Active为中心GRANTED且尚未FINISHED的完整tid，包含已发未安装/no-start/BRAKE/中点HOLD/物理已END但中心未处理者；UNGRANTED、ABORTED、FINISHED排除。只按本臂已提交知识更新，不强求反事实各臂Active相同。RR按episode内固定(session,agent)稳定键轮询，last_agent初始为第一合法agent键之前的前哨；非空时选严格大于last_agent的最小Active agent，无则回绕最小，再绑定冻结视图中该agent唯一当前Active完整tid。只有本次付费SELECT请求成功原子发布才last_agent←该稳定键；空集、过期、未提交或发布失败不改，已提交后的采样/网络失败不回滚，成员删除、后继原MOVE、模式恢复和H19源generation不重置；重放同提交幂等。此游标与公共CURSOR、SOURCE/cap/APPEND等轮询各自独立。

稳定agent顺序用于R-S、R-F_cap及H19R-S，D无正分也按此回退。对于从某次选择前一直Active的同一tid，若后续执行成功的纯R选择，则至多固定fleet基数个这类选择提交会选到它：循环序中从last_agent到该agent的正向离散距离，在每次选中其他agent后严格减少；新原MOVE不能插入新的agent键。每agent唯一Active使选agent同时唯一绑定该tid；这不赋density N或任何保护参数。该界只计成功选择提交，未提交机会不推进，不能推出有限O有足够选择、采样新鲜、消息到达或真实任务完成；D正分可跨越游标，混合D不继承纯R的次数界。完整Active读取、key/完整tid比较与绑定、版本检查及游标写入均按实际位长和访问收费，可用合法已付索引，不强制基线做旧编号规则的无用工作。

需求集P以原occurrence去重，含两种对象。UNGRANTED项为结构、完整静态几何及PRECHECK有效、曾因物理资源阻塞未授的原请求，其完整需求D_p=M0，首次加入行持久保留。GROUP_ADMIT提交时原UNGRANTED移除，并为b<ell的成员在同一提交建立唯一CAP_EXTEND项，首次加入行固定为组提交行；其完整需求D_p=Mask(U(q_release,ell))，期望同原MOVE最终扩至ell，不是新的PIE动作。部分扩展成功不删除最终需求，也不为每个CAND候选重复计分。普通初始整边b=ell不建CAP_EXTEND；b达到ell、中心合法END关闭或绑定失效时移除相关需求，不从未送达的物理END读退出条件。

QUERY在收费中心快照上重算每个需求的当前owner及全部非owner准入条件；只把忽略外国物理owner时本次完整授权确实可接受、实际又被外国owner阻塞的项纳入评分。MODE/初始化/记录/parent/几何等不满足时排除；任何外国组围栏阻挡的请求均FENCE_BLOCKED，哪怕同时存在物理owner也不计分，因为退休旧owner不能解除围栏。需求的当前几何、q_release和版本更新/失效均收费，不能免费遍历真阻塞图。

主D仍为纯阻塞计数选择：score(t)等于不同合格p中存在r∈D_p、owner(r)=t、t为外国Active、r不属于该tid原最终endpoint Mask(E_t)的个数。同p多资源只计一次；自有责任不计外国阻塞。取最大正score，tie按实际贡献需求的首次加入行最早者，再tid规范key；无正分退回上述RR，Active空为NO_QUERY。任何实际成功选择原子更新本臂last_agent为所选稳定agent键。前缀情况下以endpoint集合直接排除，不能沿用整边lambda判据判断整个当前集合；这个排除是保守启发式，不宣称对非凸多次进入的每个潜在临时释放都最优。查询可能不改变q、证书可迟到/重复、仍有其他阻塞或额外费用超过收益，这些都是合法负结果。

参考总函数完整枚举P、相交资源、nonowner条件并规范去重/排序，全部费用计入。若未来用反向索引，必须同一快照上与此函数等价，计维护/失效与最坏输出规模；“只处理受影响者”不是已经证明的复杂度界。P8的组条件进展证明在§15自给，不能替代一般纯D公平性。C7R付费交替公平构造和L9单剩余阻塞者建议仍另作未采用备选，不在本主D中暗自切换或事后择优。

POLICY主体仍预先为SOURCE_REQUEST(i)或LOCAL_POLICY(i)。每agent的既有SOURCE_REQUEST公开出现次序从零编号n_i，用n_i modulo 3固定为SOURCE_OR_EXTEND、RESEND_CAP、CONTROL_RETRY；每次公共出现均推进n_i，包括业务空结果；丢包、空结果和私有进度不能额外插入、跳过或暂停后续既定相位。这是明确修订公共文法，不新增周期数值。LOCAL_POLICY的主体和机会不因本地看到MOVE才生成中心token。共同PLAN_CHECK、COORDINATE及GROUP_RETIRE由各自预定公共行登记到同Srv_C FIFO；COORDINATE按事前算法身份在内部映射GROUP_ADMIT、在H19映射ADG_ENQUEUE有限批控制器。一个token一个角色，无自动高优先级或额外PROCESS_SLICE；GROUP_ADMIT是内部作业名，不再是与COORDINATE并列的第二种日历机会。

SOURCE_OR_EXTEND只按中心已知Kc、模式/parent/d_i/唯一请求/组成员关系与不可变Π取一个总分支：中心未就绪或失效则限定空/失败；当前GRANTED且b<ell尝试一次最大合法扩展，b=ell则NO_EXTENSION；当前UNGRANTED只在模式允许首次授权时重试同绑定普通整边及所需PRECHECK链，不同时组准入；DRAIN下不给任何UNGRANTED请求首次正cap，只保留可行的CANCEL关闭；无未闭请求但仍是未退组成员则GROUP_HELD；否则Kc未知、Kc达到本臂该agent的已提交执行尾长或对应WAIT分别给NO_SOURCE_INPUT/NO_REMAINING_SLOT/NO_MOVE_REQUEST，只有Kc严格小于该尾长且原槽MOVE才生成一个原请求。PRECHECK与实际授予仍在后继收费阶段，不能在此读真实c或从拒绝猜正确槽。新request_e只在已可信确认旧请求CLOSED后产生，重试不换tid。

内部RESEND_CAP只读当前中心已提交最大b和其合法缓存，重发同一累计授权；无GRANTED则NO_GRANT，不读取本地是否安装/到cap。H19在同一RESEND_CAP角色按§10持久两类交替和封存尾界轮询选择一条cap或APPEND消息，不新增机会。共同CONTROL_RETRY只按当前GRANTED和已声明控制代际/desired_mode发送一个绑定该公共行的RUN/STOP；无则NO_TID。查缓存、复制、签发/认证、通信、接收/拒绝和空结果全收费。初始grant发送以后丢包通过累计重发恢复，运行意图通过新尝试恢复；同一个公开role不能顺带做另一项或附赠q。

LOCAL_POLICY的唯一顺序保持：完整pending/READY可消费则只消费一个MOVE；TERMINAL_UNCONSUMED未满足则HOLD；GRANT_ARMED/MOVE_LIVE保留原责任而不消费；RESIDENT_OPEN无剩余槽则HOLD，当前WAIT在无active/pending及原顶点/slot守卫下只消费一个，当前MOVE等中心；矛盾QUARANTINE。WAIT可在未退组内合法消费，组限制仅阻止下一原MOVE授权，不能把READY消费锁在退栏后造成额外环。一次消费不连锁生成下槽请求，Kc仍等付费CURSOR。

共享ACTIVE允许本臂新POSITION策略及符合条件的新组/原occurrence。SHARED-OFF只停止新途中POSITION，保留已在途证据处理、已有责任的cap扩展/重传/RUN及原终点交接；DRAIN再停止新规划承诺、新组与新原occurrence，任何已登记UNGRANTED原请求也不得首次授正cap；未授请求可CANCEL，已授不可撤销。DRAIN不要求停掉为完成已授MOVE必需的合法cap维护，但新POSITION仍停，故未清组可能无法排空；不能假定必达DRAINED。MODE BRAKE/RESUME改变独立控制代际，已开始BRAKE优先规则不变。GROUP_RETIRE在允许处理已承诺责任的模式继续收费工作，不能在fail-stop后执行。 QUERY_ON的付费模式提交恢复ACTIVE，QUERY_OFF设SHARED-OFF，DRAIN设DRAIN；E0同样可恢复ACTIVE，但其固定策略仍不生成途中POSITION。模式切换不自动生成新规划、请求或RUN。

DRAINED要求全部agent可证resident、无未闭请求/活动运动责任、无未退围栏及待提交中心变更；resident资源保持。恢复ACTIVE不回滚q/c/水位或重放旧RUN。E0全期不生成途中POSITION，但同cap/组/退栏/控制/终点/游标/任务能力均在，不能因QUERY空或到cap无ACK删去其扩展机会。F_cap实际释放下界为0，POSITION仅作明确的因子干预，不能暗中用于清栏/放行。

NATIVE-COLD-OFF仍为共享INIT/任何副作用之前决定的独立原生旁路，不创建新mask/证据/组/状态，按原输入/时钟/随机接口运行以供原样身份合同；不能从在途共享责任热切到旁路声称恢复bitwise。触发式refinement来自已交付知识/公开模式，不能读取注入真值；共同安全底座不能因触发器未发现误差而停用。以上角色与条件不重定义或赋值保护参数。

## 8. PIE、真实任务与冻结规划作业

固定官方 R0 为 [YueZhang-studyuse/LMAPF-delay](https://github.com/YueZhang-studyuse/LMAPF-delay/tree/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357)，commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。内部PIE比较臂的新MOVE只能是该固定核心经下述显式共享接口接纳的输出；原生 NATIVE-PIE-D 原字节/原误差域另轨保留。共享接口改变执行、观测、任务同步和计时注入，不宣称整个native轨迹等价，不把接口成本或原源失败当查询策略收益。 §10具名H19外部系统使用其自己的ECBS-FA原动作；此例外不授内部PIE改变提议来源的权限。

内部PIE的联合历史Π_i[0..L]使用共同逻辑槽，每slot映射原job/segment/source/input/原边或WAIT，提交后不可改。真实c_i≤L，已知Kc_i≤c_i，未知则不为该agent提即时MOVE；Π_i[0]为合法起点，初始L=S=c=Kc=0是空历史索引定义，不是实验保护参数。MOVE只在对应READY后消费，COMMITTED_WAIT在合法POLICY消费，HOLD不消费。即使主算法使用Kc提出旧slot，gate也只能经PRECHECK及grant执行其真实当前原MOVE，不按未来PROJECT输出自行改路。H19的每agent中心/本地已安装尾长L_C,i/L_E,i及只追加消息另由§10给定，不用虚构WAIT凑共同L，消费/原动作守卫和Kc含义相同。

最多一个规划作业及一个待提交结果。内部PIE仅在共同PLAN_CHECK所登记的付费中心作业中检查规划触发：应用/模式允许、all Kc_i≥S、无在途或待处理planner job且PROJECT输入合法，才至多冻结一次在尾L追加的请求；未满足为具名空/等待/输入失败。S为最新提交段的起点，接纳后S←old L、L←new L，new L>old L；未追上的前段不能无限追加。段首与旧尾同一槽，不重复消费/服务。旧承诺不因预测目标改变而撤销。触发、目标预测、冻结、版本检查和空结果均收费，没有未登记的隐式规划循环或TASK自增机会。在线路径可保留从min Kc起到L及被当前作业pin住的前缀，只有无仍有效引用才可GC；完整审计历史另追加归档，不能把在线窗口界称为总存储有界。H19在同一个公共PLAN_CHECK执行§10自己的触发/冻结合同。

真实任务账本A与已知K_task分开。唯一主服务谓词SERVICE_TRUE(i,j,t)为：j是此刻真实A中分配给i且尚未服务的有效队首；参考处于合法初始驻留或已END原MOVE的终点驻留（尚未消费亦可），其参考顶点等于j的任务顶点且v_ref=0；整个真实实体X_i(t)⊆ServiceRegion(j)；共同服务机会存在且未达Stop。这里的物理驻留事实不以软件INIT_READY、中心READY、resident_gamma的已知性或算法证书送达为前提；原边中途cap HOLD不冒作终点驻留。主域不另要求真实实体速度为零或额外驻留时间，不把参考零速当作实际停稳；需要停稳的任务属于另行定义的扩展域。固定TASK_SERVICE机会据此每agent至多服务一个合法队首，再按固定原任务策略补给：greedy按agent规范顺序填已分配队列；Fixed用各自原序列；Inf用原tasks[(counter_i*num_agents+i) mod tasks_size]并递增counter。补给深度/原CLI意义保持而本阶段不绑定数值；tasks_size为空或接口非法不做取模/假目标。先服务再补给是明确共享顺序，不冒称native三种策略的sync相同。

TASK_SERVICE现在明确为全行两阶段世界事务。按原物理/自主事件与前行发布次序取得本行一致前修订A^-；第一阶段仅判各agent在A^-中已分配的有效队首，汇总全部服务/弹出后，第二阶段才按上段固定greedy规范顺序、Fixed/Inf原序列与计数器补给。新补任务不在同一行再次服务。完整A^+、assignment/计数器、去重/实例与service记录及单调后继修订一次发表，Q由完整真实服务记录导出；没有实际服务/补给变更的空行只留已判定空结果。真实A就在该世界行生效，不延到应用后继发布；较早CAPTURE保持原版本，后继CAPTURE见完整新版本，无agent子集或已弹出未补给中间态。行身份只能完整幂等处理，日志不能确定是否发表时不猜测重做；逻辑原子性不替实际存储/崩溃回执。

当前有限服务判定profile沿§2/P19：闭凸ServiceRegion有有限实代数半空间，F沿原有限凸多边形或已给凸分解，真实w在原O区间内为代数常值且z跨边连续。固定服务行处z用全局初态及已发生有限历史直接展开为代数系数指数和，不把一般超越的z当下一段代数初态。SERVICE_TRUE先要求已认证合法原终点/初始驻留，此时参考点实际是任务图顶点；实体包含的点值判定不必借任意途中s代数来成立，但此前驻留/END的认证仍依赖参考事件次序。逐facet/vertex的零值先精确合并指数/系数，其余认证外包判符号；服务真实A的检查/补给/记录及私有数值表示由§9理想任务世界求值完整计宿主费，明确移出模拟内任务CPU行配额；不赠送在线能力。数学终止不等于实际正确性/实时性或宿主扩展性。未完成或未认证是证据缺失，不当谓词false、不延迟真实服务、不按软件状态填Q或添加默认世界Stop。

初始合法resident可真实服务，无MOVE也可能Q>0。每实例有独立task_instance_id，即使目标相同仍区分；service_id=(block,agent,TASK_SERVICE行,task_instance_id)，全局task_revision单调，记录分配前后和去重。Q来自独立真实服务记录，不等待POSITION、ENTRY、READY或TASK回执。真实派单不为规划冻结，也不按查询归因筛服务。

K_task仅由付费TASK请求在CAPTURE处捕获的单个原子全局快照或同修订序列的连续完整batch更新，含已分配队列、共享剩余序列、计数器和服务去重；不同修订局部字段不能拼接，乱序等待缺段，普通COMPLETE不更新。TASK捕获authority是独立真实任务账本，CURSOR捕获executor，POSITION捕获可信参考状态，角色与费用不能混为免费全知传感器。

PROJECT(K_task,Kc,Π,L)仅复制每agent已合法分配且未被可信确认完成的队列W_i。从Kc_i之后至L逐公共槽k，对该agent检查Π_i[k]匹配队首则最多虚拟弹一个；起始槽不另检查，WAIT各槽也最多一次。不把未实际分配的greedy共享任务虚拟派给agent，Fixed/Inf也不生成尚未分配项；空返回空、字段不一致返回NO_INPUT。虚拟弹出不改A/K_task、不产Q。这是基于滞后下界的所有权受限预测，不保证准确未来；任务耗尽而原core不支持空目标时NO_PROPOSAL/HOLD，保留停滞/未完成，不造当前位置伪目标。新可信快照可触发再规划。

每作业冻结SharedEnv：num_of_agents/rows/cols/map/map_name来自同一公共manifest；curr_states为Π_i[L]的原State位置/平移方向与逻辑槽，非真实in-progress pose；curr_timestep=L；goal_locations为PROJECT剩余合法任务及可信reveal字段。三种逐agent容器curr_states/goal_locations/unexecuted_paths的外层均恰为固定fleet大小，前两者字段/目标非空及全部索引在安装前核明；PROJECT为空时走安装前NO_INPUT，不向clearAll的目标[0]传空行。file_storage_path仅未来合法输出合同，当前不创建。源身份、参数版本、图与任务/游标已知视图版本一并冻结，不保留可变真实环境引用。

unexecuted_paths是非承诺规划缓存，不能称其字节均已属于Π。中心仅在接受一个正常job的同一CAS中，关联该job已封存的future_path及新尾锚点/源会话/版本；future_path首点对应新尾，其后部分仍是未承诺提示，不能直接执行。封存、复制/持有和关联提交均收费，引用传递不可变；STALE job只保留worker自身正常历史，不覆盖中心已接纳缓存。下一job只能从该中心缓存复用，不能从worker后来被拒提议的同名future_paths读回。缓存不再引用时的回收及在途引用保留照计。

缓存资格在输入安装前付费完成：同源/身份/当前尾绑定，外层大小及有限表示正确；非空行首点为对应Π_i[L]、顶点和相邻MOVE/WAIT合法，各非空行末顶点互异。原loadPaths把非空短行末点补齐至至少k_commit+1；按这一确定补齐语义核共同索引内的vertex/swap合法性及共同起点互异，不把补齐当已追加Π。该资格只决定是否复用已有提示，不生成新路线。没有缓存或该已定义资格不满足时，整个缓存包改为恰fleet个空行，再走原求解分支；不能传外层空向量，也不按效果挑行保留。检查/补齐语义求值、空行容器、传递及随后原loadPaths的实际补齐各收自身费用，不把检查成本与真正执行成本混同。未认证对象/非法访问或源UB不是普通CACHE_MISS，仍按来源失败/证据缺失处理。

规划worker为唯一持续隔离的源会话，按ALWAYS_ADVANCE / FAIL_STOP_SOURCE保有核心对象、缓存及原C/MT状态；每次完整合格调用包正常结束即保留其历史，无论后继外部计划接受、STALE或合法软撤销。输出须全agent非空、有共同延长长度、首点等于尾锚点、后续每步四邻接或WAIT、全段vertex/swap合法、索引和端点有效；原planner_commit之前先做§9付费PRE_COMMIT_SHAPE，原切分及外层全检不能互相替代。中心接纳前以最新K_task/Kc重算PROJECT，核完整planner-visible目标、固定源/参数/会话、锚点/尾/待追加区间/环境和future_path版本，并绑定本job正常结束节点；不能要求源状态仍等于已被本次调用改变的开始节点。通过CAS才append外部Π并关联上述非承诺缓存；拒收不改这两项，不回滚合格源历史。后继SharedEnv的状态/任务来自已接纳Π及合法已知任务，unexecuted_paths另按上述缓存身份和资格导入；不将拒收内部future_paths冒作已承诺或已执行历史。

作业总返回为ACCEPTED_SEGMENT、NO_INPUT、NO_PROPOSAL、NO_PROPOSAL_SHAPE、PENDING、SOURCE_ERROR、INVALID_OUTPUT、STALE、STOPPED；只有首者新增原MOVE。尚未安装输入的NO_INPUT/排队取消不改源，可在后继机会重新冻结；输入安装开始后出现部分失败、PRE_COMMIT_SHAPE不合格、非法输出或无法证明安全继续，则来源会话fail-stop，无自动重启/重新播种/回滚，不造路补救。源_exit/异常只终止隔离源域、不杀评价器；旧已接纳物理责任与真实服务继续。合法守卫失败与已发生源未定义行为严格分开，后者不能作为相对优势。

## 9. 原时钟、随机输入与有限收费事件

本稿以P_model统一确定性模拟计算语义：处理工作、队列、原规划超时和有限供给共同决定虚拟闭环；宿主elapsed不进入该因果映射。固定配对与独立block条件见§12，旧执行路线的取舍保留在73A3及其原回执。

### 9.1 有限基本步、费用和当前行接纳

采用明确的有限字计算模型：字宽、地址域、编码、指令与输入接口的版本属于预先固定设计X，当前未赋实际值；模型指针和分配次序不使用宿主地址。一个基本步单位记为sigma_work，它不重命名或换算任何保护预算。下表每次固定宽度基本步均先扣一个单位，再执行其总定义状态转移；只在已付读取的固定宽度操作数上作用。多字语义对象的工作按实际执行步数累计；不用“一次几何谓词/认证/搜索”作恒价基本步。

| 基本步族 | 完整作用域与边界 |
|---|---|
| 固定字寄存器/内存读取、写入、复制 | 一次只作用一个已合法寻址字；地址计算和后续字另付。不可读authority内容由导入权限限制，不因可寻址而开放。 |
| 固定字算术、位运算、比较与分支 | 固定位宽操作及状态标志一次付费；表示/溢出/除零规则事前确定。源有符号溢出不得被模型无声改成环绕；须源级守卫或正式登记的修订。 |
| 单固定槽取得、初始化、释放 | 分配算法自身查表/遍历按基本步收费，选择次序确定；一个槽只存固定字。多槽对象、清零、内存增长、复制和回收按实际字步骤，不含免费大块memory.grow。 |
| 具名输入导入 | 只能按已登记权限读取当前虚拟时刻引用、当前合法authority根/字段或本源随机状态。固定记录搬运、解析/数值编码和校验均收费；无一般宿主时钟、文件、环境、随机或业务回调。 |
| 准备好增量的原子根发表 | 只有当前guard已全付费且有效，才在该writer原发布容量内付固定根交换/提交记录的完整费用后发表；任意增量构造、变长epoch比较、签发、复制和日志不包含在根交换内。 |

大整数/有理数/代数DAG、区间外包细化、几何、容器/哈希/排序、密码或可信消息编码、日志与GC均是上述基本步的有限或可暂停组合，不能按上表宏名免费略去内部工作。原程序浮点/转换/排序和容器语义须绑定确定版本；原源UB/未初始化访问仍是来源不合格，不被有限字机器“修好”。模拟内已声明的表示/存储耗尽有具名确定结果；宿主OOM或求值失败只表示证据未得到，不转成模拟算法分支或零Q。固定字、对象编码和全导入映射尚需源码/后端资格；有有限指令表不等于已完成C++到该模型的对应证明。

供给/扣账是明确的理想数学调度设施，只能看当前基本步类别、已付寄存器和该站剩余供给，不能读取业务堆、选择agent或计算候选价值；其宿主成本另完整记录，避免递归给计量器再排计量作业。公共不透明token/描述符的既有控制开销按公共供给单列，业务队列读取及payload处理仍计应用工作。NATURAL只计实际完成步；剩余容量不足下一原子步骤时不执行、不虚扣未用供给、不借其它站容量，也不在同一行运行新生作业。STRICT仍按同O/全供给预付包含闲置，并另报实际步数；不是对每操作补一个未证明的CPU上界。

CAPTURE的固定宽度句柄有效性由先前付费INIT/构造和生命周期不变量建立。取得当前root/time引用与写预备保留槽构成模式明确、可事前全额判定的原子记录操作；不足其全费则未读authority。它不解码完整tid/epoch、代数状态或任务账本。变长字段、引用专用持久化/额外保留、遍历、复制与必要GC另付费；不把无界引用计数增量藏在恒价pin中，不强制无实际工作的逐行人为保留税。句柄相等只证明同一不可变对象，不证明当前连续模式或任意语义标签相等。

动态ACTUATOR/cap或发布guard采用同原行付费尝试：在其原允许全序位置先付CAPTURE，再从该处当前reference/mode/END及合法身份计算完整动态谓词，并在同一次行内处理付费完成最终提交。这个数学处理内部不推进虚拟时间、不插入其它writer；物理及较早合法提交已经按原行序发生。若CAPTURE后剩余容量不足完成guard/提交，已读和已算费用保留、外部状态不改、不推进attempt watermark、不抽取新no-start或补行；下个原合格行重捕获并重算动态部分。只有保持全部依赖、仍合法持有且已付费的静态部分可复用。此明确弱化“未知guard全费不足便从未读过authority”的旧强解释；CAPTURE自身全费不足仍不读取。实际已处理的合法no-start/无作用RUN才按§5原规则消费水位，身份拒绝不统一冒称处理成功。

普通源计算的续体在基本步边界保留，在其原PROCESS_SLICE后继供给恢复；不是P29源完整体非抢占。正常完整调用仍按AA保留源历史，中心STALE不回滚；未完成续体不当成正常结束节点。硬WORKER_FAIL/INIT截止或全臂Stop在原公开行撤销后续模拟步骤/发布，不凭宿主正在算而让模型多走；相关已发表物理责任继续。模拟源终止与实际宿主退出/回收分别记录，宿主尾费不补虚拟源服务。具体backend必须在合法模型边界交还控制或提供等价求值证据，不能仅测到越额再倒填。

有限O与每行有限基本步保证不会把任意源循环免费塞进一行；它们不保证获得运动或服务。送审前仍须给合法符号输入子族上的源正常返回/原MOVE/真实服务及必要guard有限步骤见证，并证明原供给约束可共同满足；只写“供给够大”或用全pending代替合法域不算关闭。该纸面见证不能用于运行后删难图、设置保护参数或声称公开来源已合格。后端实现/重放验证属于之后的资格阶段，未实现本身不作数学反例；已知源访问矛盾和未定义基本步不能后置成普通测试问题。

### 9.2 既有时钟、公共服务与源域的组合

后端必须实现§9.1基本步、具名导入、合法暂停和原行发布语义，并提供与所选源/表示版本的对应证据。现成VM的fuel、yield或指令计数接口本身不证明这些条件；实际导入、批操作和失败边界须在后续实现资格检查中核对。

一手源码新增实核：LNS/InitLNS为Time=high_resolution_clock、fsec=duration<float>；LaCAM2 Deadline为steady_clock，毫秒duration_cast后严格elapsed>limit；SIPP超时为经过秒数>=timeout。InitLNS存在增加time_limit、continue绕过runtime更新、初始逐agent传完整预算及后处理；不能统一改写成全流程硬CPU截止。明示MAPFPlanner→LNS(use_sipp=true)→BasicLNS Agent选择SIPP，避免该对象进入SpaceTimeAStar空超时入口，其他配置不自动豁免。mcp.cpp的clock()/CLOCKS_PER_SEC是CPU起止日志，不是上述经过钟停止条件。

37个固定规划源/头对象已完成完整关键词检索并核对象身份（304149 bytes/8713行），人工语义阅读限命中/必要窗口；根另亲见MCP L14–72及SingleAgentSolver.h L35–100。rand()还在比较器/路径表；默认random_shuffle、LaCAM局部mt19937和分布后端必须登记。LaCAM每次runLACAM2重建其源码指定MT初态，不能偷改成共享主流。随机比较器不等于固定严格弱序，不能承诺跨编译器/容器调用顺序相同；native定义域/运行合同必须保留此风险，不静默修比较器再称原字节。限定集合没有额外直接OS取时/熵/sleep调用的关键词证据，不排除未搜索顶层入口/动态库；既有源清单仍非完整运行覆盖。

共享适配选择明确的虚拟时钟，而不是把wall时间当CPU：每个原chrono now调用返回其执行所在公共事件的物理时刻t，按冻结ABI的clock duration period换为floor(t/period)计数；同一事件内多个调用可同值，暂停/排队时世界t继续，恢复读钟包含该间隔。源码中的起点、差、float秒转换、duration_cast截断、比较符号、预算增量/覆盖及局部重置照原指令执行，不替换为统一timeout。high_resolution_clock的平台alias本身尚未实核，适配明确把它映射为此单调物理钟，不冒称native alias已证明或与native逐输出相同。

CPU clock单独映射为该隔离worker自出生以来已完成的模型工作量，按预先声明、量纲明确的模型工作单位到clock_t/CLOCKS_PER_SEC编码映射返回；映射属于X而本阶段未实例化，不冒称实际CPU秒或物理CPU配额。暂停/排队不增加，其他worker不倒灌，读取/编码本身计本worker工作并采用读取之前的累计量以避免自引用。真实CPU日志独立由宿主审计提供，不作为源输入。主总费用包含所有站、失败、发布与清理工作；未知clock/熵/阻塞导入仍FOREIGN_INPUT_UNMAPPED，不用宿主值填充。

C PRNG初态作为显式ADAPTER输入由独立block根和固定核心角色映射，具体种子本阶段不生成；之后包括比较器rand及默认shuffle后端的全部调用/状态均在冻结标准库与持续worker内保存。每次完整合格调用后的状态及随机消费均保留，中心STALE/合法软撤销不退回；失败会话不自动重播或重播种，完整费用永不回滚。原局部MT按源码构造/重置，不改成另一条永久随机流；公共故障创新不按源随机消费量顺移。编译器/ABI/标准库/库版本、模型基本步/浮点语义、随机接口/初态和外部调用表仍为未来manifest必需项；“seed相同”不表示跨平台相同执行。原native轨道不注入本适配时钟/PRNG，明确分域。

公共有限机会表O按(t,row_id)全序、t非减，含INIT、POLICY(role,i)、ACTUATOR(i)、REPORT(i)、QUERY、CURSOR、ENTRY(i,kind)、TASK_REQ、TASK_SERVICE、END_LOCAL_RETRY(i)、READY_CENTER_RETRY(i)、PLAN_CHECK、COORDINATE、GROUP_RETIRE、NETWORK(channel)、PROCESS_SLICE(server)、MODE(scope,kind)、FAULT、CUTOFF、STOP。POLICY的role必须为§7两个公共主体之一；两个终点retry、PLAN_CHECK及协调/退栏的主体/服务站由公共描述符预先确定；SOURCE_REQUEST的三个子角色按§7公共编号派生，COORDINATE按算法身份固定映射，不由私有状态现选。不得依某臂已观察收益改O。每行先推进物理到t并处理有限自主切换，再按job规范key发布前行已完成的有限提交单元，最后只执行本行类型；缺输入为明确空结果，不从未来补对象。新生工作/消息/结果可见发布均在严格后继行，单行不递归自触发；同一批的下一单元也须后继实际PROCESS_SLICE。此是共同修订但尚未实例化的文法，不生成实际O或另设规划/协调频率。 当前profile要求预定t及其有限字段可由精确实代数表示，实际自主事件由§3/6解析式派生，不因其数学可计算而给额外应用行；本阶段不选择任何时刻或机会密度。

机会、作业、提交单元三层语义：POLICY/QUERY/CURSOR/ENTRY/TASK_REQ/NETWORK/REPORT/MODE/PLAN_CHECK/GROUP_RETIRE标识公共机会及其付费作业类别；COORDINATE按事前身份映射内部GROUP_ADMIT或H19 ADG_ENQUEUE，后者是§10明确限定的有限批控制器。所有“选择、读取、生成、消费、更新模式”均发生于相应作业的付费步骤及合法单元提交，不能在机会到达时先免费执行。机会只提供预先类型/公共subject/不透明输入引用，不携带根据真实进度、阻塞数或任务算出的答案。输入token由元调度器按固定FIFO登记；固定描述符/队列槽的有界控制开销按公共供给预付并单列，不再递归生成一个排队作业。策略生成请求、复制/解析字段、日志或遍历业务队列均是付费应用工作，不能藏在token登记中。批不是免费的一组子作业；它占用原同一槽，逐单元消费真实计算和发布能力。

唯一新增的物理事件所派生应用待办是§5真实END的LOCAL_END_OFFER：它来自已接纳原控制责任，严格后继行才可进入既有Srv_E队列。END事件及其固定记录/描述符单列共同控制费用；不因一臂先END就给额外服务容量或给中心新公共选择信号。中点HOLD、cap安装、普通COMPLETE或本地私有c变化均不能借此规则派生免费业务机会。

每个可变应用状态有指定writer：中心管理owner/P/d/b、组围栏/成员/区间事件计数、控制意图/代际、查询last_agent/其他独立轮询状态/臂模式/Kc/K_task/Π及规划接纳版本；各executor管理C/控制代际与尝试水位、自己的命令/c/READY消费状态；真实任务环境独占A的真实变更；独立planner仅改自身私有求解状态。各应用writer至多一个计算或待发布槽，彼此不跨槽持锁等待。CAPTURE固定不可变根，字段复制/遍历/计算随后收费。真实A和物理/闭锁事实的自主变化不是应用writer锁内的步骤，按公共全序和快照版本处理；不因snapshot作业占槽而冻结实际服务或END。

这里的writer槽串行化算法作业，不给连续物理状态加锁。本地只有一个逻辑状态authority与全序提交：连续流及既定混合模式(s,v_ref,z,LAUNCH/APPROACH/BRAKE/HOLD)先在每行物理阶段演化；唯一真实END执行§5的完整原子写入，包括closed/g_i、EndRecord/pending/握手、phase、active_tid←NONE、resident_ref←v、resident_gamma←NONE及本地不透明待办，c不变。它不只写latch，也不改中心owner或免费生成证书。END之外的命令/消费/READY等应用修改仍只能在规定付费提交或ACTUATOR接纳点生效。占槽作业不阻止控制器到达/制动，后继发布须复核当前phase、END fence/g_i及自身依赖；旧command_revision相同也不能把END前快照覆盖回去。

发布依赖分开记录：c消费绑定plan_epoch/slot及未消费状态；初始grant接入绑定session/tid/parent及已验证原边，累计扩展另绑定不可撤销lineage/单调cap；本地离散命令依赖单列，不把普通q退休账本revision变化当撤销旧cap；END绑定不可逆closed记录；q证书绑定采样时原tid/几何版本/进度下界。正常连续s/z演化不会冒充命令改写，command_revision相同亦不证明瞬时模式不变。需要HOLD的RESUME、首次START等在实际接纳点还须付费检查规定离散模式/幂等标志；模式不符则拒绝或等待，不用当前pose免费重算可行域。PRECHECK的合法resident保持、END的单调closed以及q的P2包含性各有自己的保持证明，不能共用一个含糊“证书未过期”。同一旧tid只发生有限既定切换，混合守卫/模式/原tag保存的成本归共同控制项且按实际字段位长计，不称无成本业务操作。

普通作业的唯一提交单元，或ADG_ENQUEUE当前单记录单元，计算完成后在严格后继行的有限控制发布容量中执行已列明的版本/tag/幂等检查与准备好的完整增量；不足支付完整检查/发布则不产生该单元效果、继续占槽，检查尝试实际费用保留。不赠送未登记跨行结账额度；若没有能支付完整发布的后继行，该单元可保持未完成至Stop。控制发布容量是future O/容量表的显式部分，费用依访问字段与字节长度计，不把随epoch增长的大整数或任意扫描称免费O(1)。验证需要新的几何/全局推导时退回新付费计算，不能在发布点顺便重算。批的单元完成不等于整批完成，已发布前缀不可回滚，未发布增量不可见；普通作业/GROUP_ADMIT的原子性不因批例外被拆小。物理在等待期间照常推进；版本稳定只排除离散命令改写，连续安全仍需P2/P5及完整原责任的保持性。

CUM_CAP在原Srv_E作业的严格后继实际发布点、RUN/BRAKE在既有ACTUATOR实际处理点，分别从此点合法本地authority对当前模式/代际/闭锁、下一局部代数段和记录付费最终核定。不能用早HOLD快照的s/v起点给晚RUN制造已发生位移，command_revision相同不排除自主HOLD/END；不在此免费重做全局几何/查阻塞/暴露s或eta给中心。完整当前核定容量不足则本次无cap/命令效果，未实际处理的尝试不消费水位或记no-start，已发生工作收费并沿原槽/FIFO等下一既有机会；一旦实际处理，无作用RUN/C=s或合法no-start仍消费原尝试，不能用准备重试抽取更有利故障。已接纳自主END仍在真实发生点生效，不等应用切片；共同world/control计算与记录的实际能力仍为待资格化合同。

INIT机会登记软件初始化作业，经付费验证固定输入、持续有效的bootstrap包络/资源互斥/角色身份并完整提交后，才建立应用可读的resident索引与初始游标证据；它接续已存在的世界责任，不创建物理机器人或另起评分世界。gate激活消息延迟时对应bootstrap/已接续resident仍保留，不能在其他agent启动时被当作FREE。初始化及预处理实际成本单列并纳入首次总成本，公共E不因某臂初始化慢重开。POLICY按公共角色只读允许知识，最多消费一槽或生成一个请求；软件未就绪时除初始化外的应用业务不运行。ACTUATOR只执行已验证发布的命令，REPORT不改可信知识；物理BOOTSTRAP HOLD与真实任务环境依§12独立继续。

QUERY机会只入队通用SELECT作业。中心在它的付费CAPTURE固定已提交Active/P/owner/Mask(E)/last_agent、q_release/b/围栏及模式，随后按§7付费扫描/去重/比较，在同一冻结视图内选定稳定agent键和该agent唯一Active完整tid，最多准备一个POSITION请求；不能只封存agent而在发布时改绑其后继tid。后继完整版本/模式和原tid/唯一请求槽检查成功时，才将请求发布与last_agent更新作为同一原子提交。未选中、过期、未提交或发布容量不足不推进；已提交的选择后来采样/网络失败不回退。重放同选择提交幂等。中心单writer槽排除其他中心作业先改所依赖应用状态；物理END本身不更改中心Active，若显式模式/版本或绑定失效则沿原拒绝/重新付费规则，不发送陈旧请求。同agent多个Active或请求槽/索引矛盾不是任选一条/NO_QUERY，而是协议不变量破坏，沿既定PROTOCOL_CONTRADICTION/不可认证分类且不授新请求；不新增自动恢复、清空责任或零分。检查及索引维护收费，不能在发布时免费重算全局选择。POSITION随后才在自己的authority作业读取参考进度，SELECT不先偷读q。

CURSOR作业以同样付费读取/选择/后继提交推进固定agent轮询；POSITION与其字段权限仍分开。ENTRY(PRECHECK)只对指定合法请求付费处理，不存在则NO_REQUEST；ENTRY(END)按§5主配置返回付费NO_END_POLL，预先启用轮询的独立配置才经中心请求、通道和本地历史服务链执行；两个公开终点retry按§5各自站内收费总函数运行；TASK_REQ生成单个全局快照请求。NETWORK的付费作业才从指定channel已可发送的不透明队列中取规范最小payload、编码和传输，提交后按本消息外生故障key作用；读取不存在的重放目标为NO_REPLAY_TARGET，不填别臂payload。其队列FIFO是传输规则，不由元调度器提前替策略解析消息或获得发送方新状态。

POLICY(SOURCE_REQUEST,i)按公共n_i modulo 3在中心收费槽执行§7指定的SOURCE_OR_EXTEND、RESEND_CAP或CONTROL_RETRY，总函数只读允许的Kc/Π/中心/组状态。PLAN_CHECK仅运行该臂§8/10的触发和冻结；COORDINATE在内部运行一项全组原子GROUP_ADMIT，在H19启动§10有限捕获批ADG_ENQUEUE；GROUP_RETIRE在内部运行一项付费退栏，H19无组时为不适用供给。所有扫描、空结果、失败、单元发布与批末清理均用原Srv_C容量，不在首次FINISHED之后免费递归退栏/入队。POLICY(LOCAL_POLICY,i)在本地收费槽读c/pending/已验证READY并执行一次消费；捕获与实际发布都核slot/phase/未消费/绑定，不符合则丢弃，不回写影子c。各token不能连做别的角色，不由本地到cap触发中心机会。PRECHECK/END/gate按各自保持证明复核；ACTUATOR不重规划或重算全局碰撞，旧运动/自主END不被作业槽阻塞。

TASK_SERVICE为原固定机会的理想外部任务世界操作，按§8全行原队首服务/补给与实体/模式判断原子转移A，不要求策略额外申请才可计分。明确取消任务真值宿主求值须在模拟内该任务行CPU工作配额内完成的耦合；原O及每agent每行至多一次服务的设施机会限制保留，全部应用/控制服务容量不变。精确包含、A转移/去重、仅供真值的几何/数值缓存及留证的实际宿主CPU/经过时间/内存和失败完整逐臂另报，不因同O就同账，也不给中心真值、Mask/CAND、查询证书或未来任务的副产品。宿主求值耗时不改虚拟行时刻、不插入HOLD/PROCESS_SLICE、不缩E；不承诺实时仿真或外部实机壁钟同步。元评价器物理/查O/不透明token的宿主耗时与原部署应用/控制工作继续分账，按实际用途收费，任何业务选择/获取知识不可迁入世界逃费。TASK CAPTURE固定不可变A根及后续复制/编码/签发/传输/验证仍付原站费用，来源名称或缓存存在不授免费共享派生对象。

PROCESS_SLICE为固定server提供有限正工作容量。server内FIFO，按入队行/job_id打破同时性，运行一个队首job或其仍占槽的批控制器；剩余容量不在本行递归运行新生job。中心计算的增量保持私有，单元完成后等待后继发布才原子生效；批只在前一单元实际发布后的后继PROCESS_SLICE准备下一单元，不能用前次余量免费继续或同时私备多项。CAPTURE是新鲜authority job及首次END历史封存的首个收费原子操作；已有缓存重放只读既有历史对象并收实际费用、不新建采样点，具体发生于本PROCESS_SLICE行物理推进后的操作起点。批捕获保持已提交图/finished及头尾的有效引用，必要读取/复制/扫描仍逐项收费，独占中心槽只固定中心应用状态、不冻结物理。不同authority共享世界全序，不能有含糊同一时刻的前后快照。容量不足完成相应原子操作时不读取状态，保留至以后。每条已执行操作不可撤销计费，未执行未来容量不算真实工作。 本任务世界修订不新造无上限PROCESS_SLICE；原STRICT也不再为已移除的任务CPU行配额虚构预付空闲账，所有原部署算法/控制供给与任务服务机会照原制度保留，实际宿主用量在NATURAL/STRICT下均另报。

费用表必须列请求生成、CAPTURE/数值封装、区间/CAND/组选择、owner/围栏/索引访问及失效、原子提交、累计cap/控制尝试/证书、网络字节/每接收端、验证/拒绝/padding、重复/失败、planner、PLAN_CHECK/历史钟与代数名义量、cut闭包/合图、ADG批捕获及每记录/批末、APPEND初传/重传/安装与前沿维护、日志/GC及首次/复用预处理；组围栏占用时间/面积与造成的外部等待单列，仍进入全窗口成本，不能只统计已完成组。所有动作正费用或由明确共用已付费对象复用，不能隐含免费全局扫描。NATURAL计实际工作与竞争同公共服务容量；STRICT在同O/容量下连空闲未用供给也预付，实际工作向量仍分别报告，不能强迫两臂实际工作量相同。处理排队/物理推进/来源停止互相作用纳入闭环，不能为费用对齐冻结实体。

服务拓扑合同：每臂用同一个有限角色图。Srv_C是中心单服务站；Srv_E(i)是每agent的本地应用/可信捕获服务站；Srv_P为该臂唯一隔离规划worker；Srv_A为任务快照复制服务站；Srv_N(u,v)为每个已登记有向消息通道的服务站。通道/角色由公共合法主体关系固定，不按某臂产生的负荷增设服务器。实体运动/已接纳混合守卫与真实TASK_SERVICE由共同物理/环境引擎提供，其容量与费用独立明列；它们不被某算法应用writer锁住。各站FIFO及同刻key沿用上述规则，能力数值仍未绑定。改变分站/共享关系必须另立预注册profile且各臂相同，不能以只相同单价掩盖不同队列拓扑。

| 作业族 | 允许输入及唯一写域 | 固定server | 发布目标和费用责任 |
|---|---|---|---|
| 软件INIT/几何缓存/资源验证 | 固定输入、共同bootstrap身份；中心私有副本→合法中心状态 | Srv_C | 后继中心发布；全部解析/几何/建表/核验/复制/首次提交计费 |
| SOURCE_OR_EXTEND、RESEND_CAP、CONTROL_RETRY、QUERY、CURSOR选主体、模式 | 已交付知识/中心账本；中心状态、请求及各自独立游标（QUERY为last_agent） | Srv_C | 封存不可变请求/模式结果，发布后释放本writer；选择/空结果/去重/版本检查均收费 |
| COORDINATE的GROUP_ADMIT、GROUP_RETIRE、围栏/组需求及区间事件维护 | 内部已交付请求/owner/精度合同/中心版本；只写中心私有增量及原子账本 | Srv_C | 全候选扫描/分量/几何/容量/记录费，GROUP_ADMIT全组一单元；退栏不删endpoint，失败及长期保留照计 |
| COORDINATE的H19 ADG_ENQUEUE批控制器 | 已提交图/paid finished、执行尾与cut允许域；中心执行记录/enqueued/独立APPEND意图 | Srv_C | 一槽逐记录封存/后继完整发布，成功前缀不可撤；批末检查/清理后释放，不等待传输或本地安装 |
| H19 APPEND_ACTION接收与安装 | 认证记录/前驱锚/历史L_E；本地安装序列及持久尾锚 | Srv_E(i) | 连续单记录后继安装，旧槽/缺前驱拒绝与缓存/GC全收费，不写c、cap、finished或Q |
| PRECHECK/CURSOR/POSITION新鲜捕获及END首次历史封存 | 指定authority允许字段、POSITION冻结当前段/采样点及历史索引根或绑定EndRecord；只写本作业冻结payload/本地缓存及outbox | Srv_E(i) | 首个正END只封存一次；新鲜/首次历史CAPTURE不足容量不读，查询专用保留/复制、局部求值/精度封装及拒绝逐项另费；不写中心知识 |
| END_LOCAL_RETRY、正END缓存重放及GC | 本地握手/已封存历史及引用；本地writer | Srv_E(i) | 公共固定主体，收费空检查/复用/发送意图或合格回收，不读取新的动态END |
| 真实END及LOCAL_END_OFFER登记 | 已接纳原控制的守卫/预备记录槽；本地状态authority | 共同控制记录容量 | §5完整原子字段写入及唯一后继不透明待办，计记录/位长成本，不提供应用证书或额外Srv_E容量 |
| 累计cap/READY/控制命令接收验证与LOCAL_POLICY | 本地已交付消息/c/phase/pending；本地命令、消费状态 | Srv_E(i) | 当前合法守卫的后继本地提交；不能在此顺发新原MOVE；接纳与拒绝都计费 |
| 中心证书接收/资源退休/授予/CANCEL/FINISHED与READY_CENTER_RETRY | 已投送证书、中心版本及持久READY/消费证据；中心唯一账本 | Srv_C | FINISHED/owner/索引/完整READY缓存同一原子提交，网络后继；重复只缓存重发或拒绝，全部实际工作计费 |
| PLAN_CHECK及planner输入/输出、H19 cut/ADG合图与前沿维护 | 已交付Kc/K_task/合法生命周期证据、不可变Π/图与版本；中心管理记录 | Srv_C | 触发/空结果、名义量/精确比较、冻结/闭包/合图/语义检查全费；输入交Srv_P后释放中心槽，返回后另付完整检验/CAS |
| 原core求解 | 冻结SharedEnv、持续worker源历史/clock/RNG；只写worker私有状态 | Srv_P | 完整合格调用即封存结果及结束节点并保留历史；等待中心终态付费交接、槽释放后才可下个job；失败/拒收全计工作 |
| TASK_REQ生成/任务知识接收 | 中心已知版本、请求身份；中心请求或K_task | Srv_C | 请求后释放中心槽；完整快照交付后另作业验证/更新 |
| TASK CAPTURE及快照复制 | 同一真实A修订的不可变视图；只写快照payload/outbox | Srv_A | 向中心的后继消息；固定根不赠送整账本复制，不阻塞真实环境更新A |
| NETWORK(u,v) | 指定通道已发布不透明消息；该通道发送/传输状态 | Srv_N(u,v) | 成功传输后仅登记目的角色的后继接收token；编解码/字节/副本/每接收端费 |
| REPORT普通观测 | 该臂指定普通观测能力；普通payload | Srv_E(i) | 后继通道传输，不能写可信q/Kc；普通故障/处理费归该臂 |
| ACTUATOR实际接纳 | 已付费验证并发布的同tid命令及当前必要模式/幂等守卫 | 共同控制引擎的该agent容量 | 只执行已有合法权限；控制/守卫/位长/物理引擎宿主成本完整记录 |
| 真实TASK_SERVICE | 真实A、实体/服务谓词和Stop界；唯有环境改A/服务记录，Q由其导出 | 原O任务设施服务机会；精确求值移出模拟内任务CPU行配额，宿主费用逐臂另报 | §8全行两阶段世界事务，无算法可见副产品；真实资格/派单/去重/缓存/留证与失败完整计量 |
| 日志/GC/索引维护 | 各写域已授权状态 | 所属写域的原server | 不设免费后台线程；独立审计器仅留证据，不反向供算法选路 |

异步交接不跨writer嵌套锁：发送者只在自己的提交单元中封存不可变envelope并产生目的通道的不透明token；普通作业随后释放自己的槽。ADG_ENQUEUE的已发布单元同样使该envelope独立可传，但其有限批控制器仍占原中心槽、仅在后继PROCESS_SLICE推进下一单元，批末处置才释放。此例外不等待目的writer、不另占第二槽，不把中心占槽等同持有通道锁。通道作业再付费读取/编码，完成才产生接收角色token；接收角色自己的后继作业付费验证后改自身状态。元调度器只登记有限不透明引用，固定描述符开销单列预付；业务payload读取/复制、FIFO取项和解析不由元调度器代劳。不能在持中心槽时同步等待Srv_E/Srv_P/Srv_A回复，也不能让Srv_N直接写中心owner或本地c。跨角色引用在所有仍有效使用方结束前保留，GC/保留内存也计费。发布的版本/tag检查使用对应writer的显式控制发布容量，不借用另一站空闲供给；不足时继续占自己的槽，不借机冻结其他物理进程。

故障创新除下述固定公开矩阵的no-start外，由独立block根派生，key=(角色,公开行或请求/作业语义id,有限copy/attempt序号)。同block各臂共享创新函数而输入自己产生的对象；调用次数不同不顺移公用PRNG磁带。ordinary假反馈、no-start、空间/运动扰动、通信错误、处理容量分别有类型；给普通包加时间偏移不等于实体误差。ROOT独立性只对block成立，臂间配对相关允许。当前不生成根、种子、O、manifest、tape或载荷。

**公开延迟表的共同接入合同（2026-09-12，C28建设经根纠正）。** 主共享比较的no-start采用固定source延迟矩阵D_src作为X中的确定性输入，不再对同一no-start角色另从Z_b抽样或叠加。每个agent的矩阵行号就是原agent文件记录次序的零基下标，不重排、不按后续轨迹选行。令O中该agent全部原ACTUATOR机会的零基秩为k，当前机会对应D_src[i,k]。索引由原O全序给定，既无新的源时间尺度参数，也不产生额外机会；它将原native的离散时刻列改解释为公共控制机会列，不宣称原生MCP/PIBT/PIBTD与当前连续运动逐迹等价。不同臂同一公共机会用同一位，但处理哪个命令、是否有合法RUN以及其后果仍由各自闭环决定。

空机会、无候选、guard费用不足、已关闭/重放拒绝及合法无作用命令仍占它们原有的公共序位；序位不按实际读取/成功次数压缩。只有已经核明当前身份、RUN_ALLOWED、合法HOLD及C>s等START/RESUME条件的RUN，才需要在本行付费读取该位，并以0允许、1阻止这次启动。读取、索引/位长、相应副作用及提交的完整收费工作均须在原行容量内成立；不足保既定PARTIAL_GUARD语义，没有外部提交或水位推进。已实际处理的no-start和无作用RUN照§5消费尝试，BRAKE保持其原来的模式/代际/水位和制动作用且不受此位取消；运行中既有运动不因该位瞬停。无用途分支不被迫读矩阵烧费。重放已处理命令不得因到了新公共列就复活；后继原机会上的合法新尝试用该新行自己的位，不是重抽旧尝试。

矩阵只由环境/ACTUATOR现有权限使用，不能成为planner、D/R/E0或H19的免费未来信息。POSITION/TASK/CURSOR以及付费API均不授读取未来延迟的能力；已有合法结果/状态的间接信息沿原权限，不新增delay反馈通道。共享模型接受的是§11有效投影的同一规范表示，而不是各raw别名的不同原文本：按§9.1固定字宽记录主体数，再按原agent顺序记录各行长度，0/1按列升序从字的最低有效位装填，末字未用位为0；字段越出表示域依原输入不合法规则，不回绕。各profile对应的有序表示与机会结构一起固定，当前不生成其实际字节。

原始文本的取证、语法检查和有效投影/规范表示的构造，是建立给定外生no-start世界输入X的宿主准备工作；按实际raw别名逐项保留耗时/内存/失败，不能报告原raw处理成本相等。它不计算任何算法专用查询/几何/授权或未来派单，不把业务成本移出计量。模型内初次导入规范对象、必要解码/持有/业务索引及逐次取位的实际工作按原职责收费，并且只能接触这一规范对象；raw路径、原文本长度、未使用尾部和任意宿主分配地址不得进入模型状态、供给、日志身份或F。若未来后端仍让raw处理或别名影响这些模型量，则尚未满足本alias合同，必须先保留raw身份，不能凭投影相等省略费用证明。此处等价仅是声明P_model中输入及费用法相同，宿主准备账允许不同；评价者的静态取证不等于线上应用已取得知识。

delay静态支持要求原输入编码/布尔域、行身份及索引算术有定义，对每agent令K_i为全部原公共ACTUATOR机会数，须其行存在且K_i≤该行实际列宽；涵盖空机会和所有潜在分支，不按已实现尝试筛列。无行/不足列在事前记录为该source/profile静态不适用，必需类别或profile无合法成员仍UNINSTANTIATED；不能补零、循环矩阵、缩E、补O或按结果删来源。运行后发现索引/来源绑定破坏不是合法物理no-start：保原证据缺失/INFERENCE_UNAVAILABLE，不虚造物理Stop或尾部零分。原native另轨仍须其每次current_time至current_time+commit_window−1整个窗口落在实有列内，本秩条件不替该条件。

原文件名、首行第二token和本次1的经验计数不定义随机概率、独立性或故障强度参数。D_src固定于X，其他角色Z_b仍可使潜在Q随机；块内同表及不同block复用同一固定表均不破坏条件于X的独立根论证，但不提供对未知延迟生成机制的总体推断。主效应现在是在所声明公开控制机会表及P_model下的固定来源效应，不称对原生随机延迟法等效。source的有效delay身份、alias及权重按§11的新规则绑定；当前仅定义语义，不实例化K_i、O或合法roster。

MODE的有限kind为QUERY_ON、QUERY_OFF、DRAIN、BRAKE、RESUME。前三者scope为本臂，付费提交分别设ACTIVE、SHARED-OFF、DRAIN而不删责任；E0的QUERY_ON同样恢复ACTIVE，另记POSITION能力仍STRATEGY_DISABLED，不能因其不买观测而禁止它恢复新准入。后两者scope为指定agent，仅对当前GRANTED原tid推进该agent持久control_epoch并改变意图；无合法tid则付费NO_MATCH，不影响未来原tid的初始RUN_ALLOWED。合法时产生绑定该MODE公开行的首次控制尝试，经后继Srv_E付费认证、候选入列及ACTUATOR实际处理才作用；之后CONTROL_RETRY使用新公开尝试key。两种来源共用§5实际处理水位，不能因MODE身份省去幂等或制动守卫。BRAKE在P1制动域内继续旧tid；RUN只有合法参考HOLD且C>s时可重入LAUNCH，已开始BRAKE未停或C=s时本次无运动作用并消费尝试，必须后继另一RUN。NATIVE旁路不接受共享MODE；非法scope/kind为INPUT_INVALID。每行只推进一阶段，不在模式切换时自行产生新MOVE。

FAULT的类型记录为(公共行,role,subject,kind,该profile已规定的载荷语法)。ORDINARY_VALUE只能改变普通pose/COMPLETE字段或其序号/时标，不伪造可信签发；NO_START只影响指定ACTUATOR尝试；SPACE_W与REF_ETA分别提供有界物理输入，不互相替代；当前MAIN有限profile另服从§2/3的O区间常值及精确代数语法，更广有界可测输入只适用原条件安全定理而非当前有限后端资格；NET_DROP/NET_DELAY/NET_COPY只作用于本臂已存在的消息，有限副本数受O/profile限制；CENTER_FAIL_STOP使中心停止新服务/发布，已提交账本不回滚，未提交私有工作无外部效果但费用保留；WORKER_FAIL终止整个隔离planner来源会话且不自动重启，不消失实体。CLOCK_LABEL_SKEW只修改非权威本地标签，授权不依赖租约/标签时间。可信状态回滚/签发伪造、控制闭环失效、实际w/eta越界或未覆盖的形体/障碍变化属于TRUST_OR_PHYSICS_BREACH压力域，不继续调用P1–P5保证。未列kind或缺对应subject不能猜默认，分别INPUT_INVALID/NO_REPLAY_TARGET。

瞬时故障与迟到消息用公开行序区分：FAULT前已发布的grant继续有效；中心已计算未发布的grant在fail-stop后不发布。失联/中心停止服务本身不令正在运动的机器人停车或让已预留空间消失，物理与真实TASK_SERVICE按其仍合法的模式继续。各分量停止、全臂评价Stop及主机评价器故障在§12分开。有限自主运动每旧tid只按LAUNCH/APPROACH/END或BRAKE/HOLD这些既定守卫推进；若数值过程产生未定义/Zeno级联，不把无限内部工作塞进一个公共行，返回不可认证并按§12处理。

新增来源73E1已经完整读取六个固定R0对象（101756 bytes/2869逻辑行），证实官方CLI类别“LACAM only”和具名分支初始/重试/修复经getInitialSolution→runLACAM2→solve→Planner::solve，不需要修改源才有此模式。它仍复用LNS对象、随机洗牌/预采样tie等；不是无随机、无SIPP对象或整个生命周期契约已闭。73E3/E4现已实际完整返回；73E5亦完整返回并经根全文读取，不能再按历史时态记待回；原73E2仍缺，不用新报告冒充。根另独立核固定头文件/driver全文和相关完整函数窗口，确认init_time_limit在所见构造与driver路径未初始化却在simulate首次按值传给plan，plan体内覆盖不能消除调用前读取；初始化失败未向simulate传成停止，future完成仅join不get不能识别其异常；computeAllPair另有局部第五个pairing_heap，其>=比较不满足严格弱序，且位于LACAM分支选择之前。这些源合同问题不能由纯LACAM名称或种子消除，不等于已运行观察到崩溃或性能损失。73E7根已实核本机Boost 1.74头文件/软件包与构造、析构、merge调用窗口，选其为纸面参考依赖合同；实际未来include路径、宏、对象hash及构建仍未绑定，不能由头文件存在推运行通过。原生R0身份保留，修复适配的具体工作选择如下，所有改变共同给予相应内部比较，不据源缺陷制造查询优势。

当前唯一修复来源工作选择为R0-REPAIRED-LACAM-ADAPTER / ALWAYS_ADVANCE / FAIL_STOP_SOURCE，依据73E6、E11、E12及根不用skill独立分析：保留固定R0 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357的PIE/原规划提议链与LACAM类别；另设隔离worker同步入口，绕过原driver/BaseSystem.simulate及其异步planner_initialize线程/脱离路径，在同步initialize前显式选择算法。预处理、首个plan、后继plan预算槽逐项显式传入并保留原义，当前不赋值；不读取未初始化BaseSystem.init_time_limit，不把plan内部覆盖当调用安全。已登记内部源码差异包含computeAllPair局部第五个堆比较器从value>=改为value>、下述Planner::solve空H_goal失败分流，以及E20明确登记的目标引导解析、puller自身行与交换循环距离更新，不改SIPP/A*四种堆所用的两个LLNode谓词、不替换all-pairs/LNS路径。前者只恢复该局部严格关系；后者只封闭具名空目标分支。原样R0另存，这些共同差异和隔离/时钟/形状接口属于修改版来源，不能推所有合法输入或搜索已定域。

73E18与C13完整实际回执经根E19不用skill独立分析，将四堆排除限定为具名条件域：固定具体MAPFPlanner且无未登记虚覆盖，初始化前显式选择LACAM并在会话内不变；agent身份/数量固定、fresh reserve后emplace且不复制持裸solver指针的Agent；唯一worker及原输入权限；仅用loadPaths→plan→PRE_COMMIT_SHAPE→planner_commit包和已登记生命周期，不从诊断/监控调用runPP、LNS::run、LNS2、findPath或getTravelTime。已读构造建立空SIPP，路径维护只改路径/表/标量，纯初次及正常后继均调独立LaCAM；其OPEN为std::stack而非LLNode堆。原提交验证的临时A*只做路径几何检查，也从空构造到空析构。故在有效对象/合法调用与已核参考Boost语义下，四种root由空保持空，正常AA软拒收不新增Compare边；这不是全仓唯一调用者或最弱条件证明。实际include/ABI、完整输入/对象继续域仍须绑定，不把paper条件当自动已满足。

根另直接读取固定planner.cpp的完整solve窗口与lacam2.cpp/外层plan调用：若建结构后首次while因deadline未进入，curr_best/H_goal仍空，原fallback之后cout先解引用，后面的非空if已太迟。预算为原义、结构工作收费且公共时间可前进，不能靠补默认/下限或免费预跑排除此分支。所选纸面修订在首次H_goal读取前分流：非空才进入原目标日志/回溯，空目标不读取、不回溯、不补路径，仍经过原已建立对象清理后返回空solution；构造/清理异常沿原真实退出，不假称成功。runLACAM2的空解失败经本次plan返回后的PRE_COMMIT_SHAPE即NO_PROPOSAL_SHAPE/FAIL_STOP_SOURCE，不进原commit或下一次clearAll重试。外层fix分支没有把false回写initial_success，不能伪造统一失败标志链。守卫/分支/空对象/清理/停止全费，非空路径也不宣称墙钟逐结果等价；目标内部索引覆盖、EXPLORED所有权及全部可达数值域仍未证。

73E20根直接核固定planner.cpp、planner.hpp和LACAMInstance(SharedEnvironment*)，并独立分析C15完整意见：reach_goal为默认空std::vector<int>的resize值初始化，根显式0，后继只保留已置位或从0增至1；get_new_config仅复制给goal_index，故有效对象下是{0,1}闩锁而非任意任务游标。num_agent_reached/curr_time的头文件初值亦已见。原HNode/funcPIBT/is_swap_required共四处用该标志读取目标项；只有一个合法已知目标的输入不覆盖第二项，prepareDummy及LACAMInstance均不补env队列。空PROJECT队列在安装源输入及该构造的front读取前给NO_INPUT/HOLD；这与solve中空H_goal守卫是不同入口，不能借后者保护前者。冻结输入安装后若非空/标志/合法顶点不变式被破坏，则来源失败停止，不钳位或用空解自动重试。

纸面共同修订将四处目标读取统一为搜索内部引导：标志0取本agent冻结队首；标志1有真实已知第二项时保留该第二项，无第二项时仍取同一个已合法分配的首目标顶点。任务队列、实例身份、完成闩锁、PROJECT和真实SERVICE_TRUE不因此改变；预测访问不等于真实交付，不追加目标、WAIT或未来MOVE，不把当前位置变成新任务。is_swap_required的puller一侧明确取puller自身的行和标志，经同一引导解析，而非原pusher行。保留有第二项子域不是限制整个roster必须两任务或只一任务；各臂合法已知输入可不同，失败与未服务仍留原总体。

根另独立补齐与启用交换有关的局部进展：原循环体四个同名int是内层新变量，外层距离和while/return保持初始值。所选纸面差异使这四个已存在的距离在顶点对推进后更新自身外层绑定，保持原邻接筛选、跳出条件和最终双侧谓词。对一个调用内固定且全定义的有限图距离表，每次实际进入循环均有D_p(v_puller)<D_p(v_pusher)；推进后新的pusher为旧puller，下一次若仍进入，其pusher距离严格下降。可取值集合有限，故此局部循环不能无限进入，不需给原预算增下限或新增随机/超时语义。该证明不保证距离表、索引/整数、邻接/对象或整个求解器已资格化；首目标叶节点排除与第二项引导的角色差异保原且单独保留，不从变量名推算法错误或已恢复完备性。

上述差异属于R0-REPAIRED-LACAM-ADAPTER的新增明确纸面来源修订，原commit和原样副本不变，尚无修订后代码身份或执行结果。它们可能改变提议、递归/随机消费、搜索历史、源时钟、失败及Q，各内部引用臂同规则且逐项全费，不声称原样/逐墙钟结果等价；H19自己的ECBS不虚收这些工作。四读点、交换行和局部循环定域不证明源的消失agent占有语义、全路径合法性、EXPLORED键/对象所有权或AA归纳继续域，也不推出吞吐/饥饿/完备性结论。C15的长期饥饿反例未覆盖约束覆盖、后继真实服务/补给，根不采作定理；dummy独立停泊引导/其他来源仍可另证比较，但不由未采用推其一般非法。当前不扩大或缩小固定总体以掩盖源缺口，完整资格仍UNKNOWN。

73E21完整无skill建设报告经根E22直接复核固定planner.cpp及graph.hpp/cpp后，另采用同一修改来源的后继身份/唯一归属包。原get_new_config只把父reach_goal复制给A.goal_index，solve查找的num_reached可能尚未包含C_new首次到达，而HNode构造会更新；原新插入又以父(C,flags)键指向H_new。RCEqual实际把RC2的flag与自身比，原RConfigHasher却混入flags，故某些合法同配置异flags的等价键可能不同hash。不能只改L232或把散列值当节点身份。修订要求先付费建立一次后继F_new/到达事实描述，lookup、创建和发布均用相同(C_new,F_new)；真实比较两边等长配置/flags，逐vertex id及0/1分量相等，同一稳定存活图内等价键同hash。未命中后只插新代表不覆盖旧值，发布前核对象身份相同；异常身份/冲突为源失败停止，不能免费重试。原hash可在合法有限域保留，复制/比较/散列及描述工作均计。

求解期拥有者登记唯一拥有全部已成功构造的HNode及本次Agent；EXPLORED、OPEN、parent/neighbor、H_init/H_goal/curr_best和occupied均只借用。每HNode的search_tree唯一拥有其LNode，pop把拥有责任移给当前迭代直到最后读取；两处deadline break、continue/失败和异常均归同一作用域清理。根见原pop后的L187/L193跳过delete且子L仅复制内容，属条件漏清理；OPEN重复借用或搜索环本身不能证明double-free。原父键覆盖还会丢失索引清理入口，不能靠仅对map values去重找回。

新HNode私有构造不提前把this写进parent->neighbor，初始/展开子L在分配至队列接管间都有唯一拥有责任；完整构造后先登记拥有者，再发布索引/neighbor/OPEN借用。中途任一分配/发布失败停止遍历，已登记由登记清理、未移交由局部拥有者清理。回溯复制须在节点/图仍存活时完成；随后停止所有借用访问、清借用容器及A/occupied别名、释放当前L与全部登记节点/其队列，最后释放本次Agent；parent/neighbor清理不递归删或解引用目标。图/环境保持到引用生命周期终点。原裸delete与新唯一释放不能同时保留；构造尝试计数不回滚、不当活对象计数。

此包对完整setup、正常/空H_goal、两处deadline、回溯扩容失败及有序异常走同一清理责任；源deadline不免清理费用，公共Stop/worker failure若使清理未完成则不是正常可继续节点，不能补免费容量。AA正常软STALE仍保合法源/RNG历史，但本次局部搜索图正常清理，泄漏不是应保留的算法记忆；硬错误fail-stop不恢复随机或自动重启。条件异常析构合同不承诺UB/崩溃/强制终止时一定运行析构，实际退出和全部有限整数/对象域仍待证。

修正键只保证索引身份和对象归属，不把(C,flags)称完整Markov状态：原rewrite更新g/f/parent，却保持depth/curr_time/priorities/order等历史字段，而它们影响后继。当前保留原两字段重复探测及代表历史政策，不新增无限历史键、不声称恢复原LaCAM完备/最优性。原合法正边费用及无整数溢出等条件可支持parent代价严格增加的局部无环论证，完整后继/数值继续域仍UNKNOWN。此包会改变命中、展开/随机到达次序、对象数和费用，同源各臂共同计全部实际工作；不是D创新，外部H19不虚收，未生成修订后源码或结果。C16实际超时无正文不为E21或本根分析背书。

根E23另核runLACAM2、内层solve、真实PathEntry/PathTable及C++14草案条文后，补充唯一直接构造合同：批准链中的命名LACAMInstance直接从冻结SharedEnvironment建立，其Graph不经过同类型临时对象或按值复制；命名Planner同样直接由原实参构造，拥有状态不复制。原CMake主分支声明14，原ins临时初始化若未发生允许但非保证的拷贝消除，可共享裸Vertex并由临时图提前删除；这是条件来源风险，不是已运行故障。内层只借外层ins.G，E22节点清理不删除顶点；回溯后外层在图仍存活时把合法solution顶点index复制到只有整数location的PathEntry，已读PathTable插入只存整数，runLACAM2返回bool。此正常具名输出链不逃逸顶点借用；不推广到PathTableWC、任意回调或非法solution。晚到PRE_COMMIT_SHAPE不能倒保此前解引用，图部分构造异常、全部索引/数值及部署域仍待证。临时对象、图/标量复制、表维护和清理按实际全费，各内部源臂同修订；不称原样等价、不生成代码或运行身份。

根E24进一步针对批准的向量地图Graph构造核部分异常：原new Vertex后V.push_back、后续顶点及neighbor扩容均可能在Graph构造完成前失败，原V裸指针容器的销毁不删除pointee，不能靠正常Graph析构补救。新增纸面唯一顶点拥有者成员须在建图主体之前已建立且寿命包住V/U借用；新Vertex移交前由局部唯一责任持有，移交成功后才发布V/U/neighbor借用。部分移交/发布失败各清自己的对象，原遍历V裸delete随归属迁移移除；邻接不递归删。LACAMInstance后续starts/goals构造失败时完整G按同一拥有者清理，图外不发布未完成实例。只有正规异常/有效对象下的归属归纳成立，强制终止、越界/数值、分配器及完整实际退出域仍UNKNOWN；正常图编号/扫描/邻接顺序保持，拥有者/扩容/异常工作各来源臂同规则全费，硬错误不冒AA正常继续。未改源码或运行。

根2026-09-13直接核[固定Instance.h](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357/inc/MAPF-LNS2/inc/Instance.h#L97)：getDegreeAdvanced的L116以loc+cols−1和左列边界检查左下邻格，却读取loc+cols+1。令输入有R行C列且相关整数运算可表示，倒数第二行最右格loc=(R−1)C−1在C>1时可通过该检查，而读取索引RC恰越过map尾；这是符号边界反例，未运行或读取具体地图。固定MAPFPlanner.cpp的初次LACAM分支L55调用prepareDummy，固定Instance.cpp L19–28遍历自由格并调用该函数，不能当不可达或仅凭图有连通分量就排除。

同一R0-REPAIRED纸面修订仅把该分支的读取目标绑定到它已检查的左下邻格loc+cols−1；不改四邻接规划图或其它七个分支。输入资格须在该遍历前保证正行列、矩形长度、loc及所有加减/行列计算可在冻结源整数类型中表示，不能依靠已关闭的assert保护非法输入或在计算溢出后再判断。满足这些前提，南向索引由上界守卫、北向索引由下界守卫、左右边界由列守卫共同保证八处读取均落在同一合法矩形邻域；固定八次测试的degree属于0到8，原分桶只在d>0时访问d−1。L101的严格0<仍会漏计合法北邻索引0，这不是越界；本修订保留该原有计数行为并明示，不暗中增加启发式改进。prepareDummy、候选容器、shuffle及全部分支/访问费用继续保留，可能改变候选和后继随机消费/费用；各引用R0臂共用，不是D的创新，H19不虚收。此修订不证明全源继续域、正常输出或实际输入资格，未改源码或生成修订代码身份。

四种堆成员对应两个原谓词类型，原随机平局关系不因不调用而变成严格弱序；没有具体库条款或运行证据时，也不把“必须实际落平局且随后出错”当UB的必要三条件。已证本域无该项Compare只免未发生的比较/RNG工作，常驻SIPP与验证临时A*构造/析构及路径维护照实际计费，不拿研究审计成本代替运行成本，不删除空对象给任一臂优势。D/R/F_cap/E0凡引用该来源均同修订、同AA/失败/费用规则；H19不同来源不虚收R0对象费用。未获资格时不造失败实验；未来已资格守卫失败与实际源失效/不可推断分别登记。

同步初始化以公共入队到付费结果接纳的全部经过时间判截止：正常返回、完整后条件与状态封存均完成且中心在截止/取消之前付费验证提交才INIT_READY。仅join、私有函数已返回、未取回异常或超时后才发布均不算成功；异常/无效/未知分别登记。首次planning资格在首次合法事务发布时消耗，即使失败/拒收不回滚；原initial_run的源状态语义另存。initMap/computeAllPair/LNS创建、loadPaths/plan/planner_commit、PRE_COMMIT_SHAPE、输出封存、持续内存/复制/失败/清理全部收费；本profile不做逐job检查点，未发生的快照/回滚工作不虚收。MAPFPlanner.h的lns声明已有nullptr初值，不再制造“未初始化lns”问题；原析构env先于lns的风险由对象生命周期另核，不能凭进程终止忽略已经走过的局部析构或异常展开。

worker只操作自己完整隔离的源对象、SharedEnv、缓存及原随机状态；管理器持代际不透明句柄。每次job从当前持续状态安装冻结输入，保留原loadPaths/plan/受保护commit调用；完整正常且有事前继续域证明的结束节点无条件保留，中心输出接受与否不选择其状态。中心付费处置结果并经既有规划输入/输出通道交回终态，处置消息使用本job事前准备的有限控制收件槽；worker在同一未释放job的后续PROCESS_SLICE阶段付费验证并释放待结果槽后，才可在后继公共机会启动下一job，不能把处置作业排在自己之后而自阻塞；不新增server/容量，等待不假计源CPU。中心不持writer槽等待worker；中心fail-stop不允许凭私有完成继续发新规划。费用、公共时刻、首次资格与取消史永不回滚。每个执行域按LIVE→STOP_REQUESTED→REAP_PENDING→REAPED→RELEASED区分；信号或停止通知不是已退出，完整域退出有证且引用消失才回收，未确认不复用Srv_P。源_exit/异常不杀评价器，Stop后必要回收费用单列且不补服务。

ALWAYS_ADVANCE的继续域必须覆盖合法初始化、全部合格正常历史（包括上次输出被拒收）和下一合法冻结输入的归纳闭包：源入口与返回后的内部容器/对象均有定义。不得假设clearAll等于全状态重置，也不得发明万能运行检查器把此义务消掉。尚未安装输入的拒绝可保留旧状态；安装后的部分失败、PRE_COMMIT_SHAPE不合格或源内生INVALID_OUTPUT均停止来源会话，不将半成品用于后继。不合格结束保留实际审计记录但不给热继续资格。中心外部目标变化/版本CAS失配只属软拒收，已进入作业仍在共同服务容量下收费至正常完成或明示硬失败；硬WORKER_FAIL/INIT截止/全臂Stop则撤销发布并走真实终止回收，不因“算完比较方便”延长合法源历史。当前完整继续域未证明，故仍无执行资格。

73E11根实际核固定MAPFPlanner.cpp全文及LNS.cpp相关完整函数，将E6既有前置资格具体化为付费PRE_COMMIT_SHAPE：必须在plan返回后、原planner_commit首次清容器之前完成，不能放到commitPath之后。逐agent检查对象/编号/容器与目标队首相容、原切分量及索引可表示、路径有被跳过锚点和后继、冻结锚点及边合法、原切分分支必先产生非空提交项。源码短分支会读取commit_path.back，空/单点源路径可能在后验检查之前已不满足其定义域；plan为void且后继修复bool未传出，正常return不证明完整成功。不合格时不调用commit、不人工补WAIT/改MOVE，记NO_PROPOSAL_SHAPE或SOURCE_BROKEN/UNVERIFIABLE；全部已发生费用保留，可继续源状态资格另证。原validateCommitSolution保留，外层另检冻结锚点到首提交边及全体冲突/版本。根还实核PathTable::insertPath空路径有早返回，已排除此具体疑点，不增加臆测修补；本节不是源全闭或运行故障证据。

当前EXECUTION_BACKEND_UNKNOWN指所选修复源/数值/导入到基本步的对应及暂停、回收尚未资格化。设计阶段须写清接口和失败语义、修正已知矛盾；实现后再核具体后端符合性，不能把未构建或尚无效果数据单独当作设计反例。

当前组合为P_model和ALWAYS_ADVANCE：服务模型与源历史制度均已在本稿明确选择，固定PIE新MOVE来源边界保持。未采用的非抢占、逐job检查点、QEMU/Unicorn等路线不再作为当前工作清单，历史证据由73A3索引。

每job的审计联系至少覆盖源会话/前一正常节点、冻结输入与已接纳尾、源执行阶段、PRE_COMMIT_SHAPE和commit是否进入、封存输出/结束节点、中心终态与槽释放；失败保留阶段及费用，拒收也有完成节点。节点身份不等于完整内存快照或重放证明；若另外读取状态指纹/随机记录，扫描/散列/存储均收费且不向查询策略提供新字段。AA的非预知归纳来自仅用合法过去输入及私有源历史，物理安全归纳仍只作用于经完整验证/准入的外部Π和资源责任；两者都不推出吞吐改善。

以下两表限定S6剩余设计义务。已证只指固定源码局部更新或已给条件证明；已定义指当前共享适配的选择，不等于实际实现符合。表本身不充当AA归纳闭包或全费用证明。

| 批准阶段 | 跨请求字段及已核更新 | STALE后保持与剩余设计义务 |
|---|---|---|
| 同步initialize及同一worker | initMap→computeAllPair→LNS；固定env/图/距离表、agent身份、solver对象和原参数；stay_target初始化为零。显式选择LACAM为已定义入口。 | STALE不重建对象、换算法或重置图；尚须把冻结输入安装、固定对象寿命与有限表示前提合入整个批准包，不扩大到未用入口。 |
| 冻结SharedEnvironment安装 | curr_states/goal_locations来自已接纳Π尾/合法已知任务，curr_timestep来自原逻辑槽；unexecuted_paths另取§8与已接纳job绑定的非承诺缓存。 | 外层大小、目标非空、长度/索引/顶点及缓存末点等资格须在源读取之前成立；PRE_COMMIT_SHAPE不能倒保。STALE缓存不覆盖中心缓存。 |
| loadPaths→clearAll→向量loadPaths→checkReplan | 仅initial_success且非initial_run进入；先清agents[].path/path_table并更新起终点，再装输入路径，按原规则补短路径并查缺路/锚点/目标/冲突。 | 本分支不混入上一提议路径；clearAll没有重置全部字段。剩余是PROJECT至源级前置条件、路径表访问及两个后继分支的组合。 |
| 首次/未成功/修复的plan | 首次写initial_success并清initial_run；未成功后继先clearAll；成功后继的fixInitialSolutionWithLaCAM可重算或复用，其bool不回写initial_success。 | 保留真实旗标，不按中心CAS结果改旗标。runLACAM2的succ要求到达全部首目标，非空合法前缀未必succ；不能统一要求可提交正常节点initial_success=true，仍按形状与完整包分别判定。 |
| 每次runLACAM2→solve | 局部MT按原构造重建；持续C随机/静态历史保留。图、搜索节点为本次对象，既有唯一拥有者修订负责回溯后清理。 | STALE保随机消费，不恢复已释放局部对象。余项是批准分支的表示域与基本步对应，非全平台库一致性。 |
| PRE_COMMIT_SHAPE→planner_commit→commitPath及外层验证 | 原commit清commited_paths/future_paths；curr_commits须有正确外层和空行。长路径分支stay_target归零，短路径补齐时递增；clearAll不清它。 | 保留整个正常post，外部Π只经CAS追加；stay_target条件界见下，其它跨调用计数、step/长度界及完整锚点/冲突后条件仍须组合。形状守卫不免原切分费用。 |
| 封存→中心CAS/STALE→同job处置→释放 | 正常源节点保留，接纳才append；预备收件阶段仍属未释放job，处置完成才开下一job。安装后失败/硬失败停会话。 | 下一输入来自新已接纳尾；中心不持槽等P。暂停、发布和代际回收的具体符合性后续验证，不重设计逐job回滚制度。 |

源码定位：固定MAPFPlanner.cpp L35–73/141–165；LNS.cpp L1–52、383–443、496–541、648–713、1186–1215、1236–1339、1360–1429；SharedEnv.h及PathTable.h。当前AA剩余组合证明集中于安装前提、两条后继plan分支和跨调用表示界；源成功旗标与提议形状的区别不得在实现时抹平。

上述安装接缝现由§8的明确容器/缓存合同补齐，可给局部两分支保持引理：从合格正常节点出发，initial_run=false，新冻结输入满足身份/非空目标/表示及缓存资格，且正常对象/分配合同成立。若initial_success=false，loadPaths不进入，plan先clearAll再getInitialSolution；若为true，loadPaths先clearAll，再只装本次冻结缓存并checkReplan，缺路/目标未达/冲突使fix再次clearAll重算，否则复用本次合格路径。因此两分支都先删除旧agents[].path/PathTable，旧STALE提议不经这些路径混入；其它持续状态保留原义。复用分支每行经过当前目标、起点合法、长度至少k_commit+1，原共同提交前缀落在联合冲突检查覆盖内；首次边和外层全检仍保留。此引理只到合法进入重算或复用分支，后续搜索/输出登记的正常后条件和其它累计表示仍未自动证明。

缓存末点唯一是源级必要接缝：PathTable.cpp L14在登记前要求该末顶点目标槽为空，lns_common.h的MAX_COST/MAX_TIMESTEP相等；Instance::hasCollision L373–398只查共同长度且从索引1开始。两条不同长度、共同前缀无冲突但在不同末索引结束于同一顶点的合法路径，足以否定“逐路径格式/锚点合法必可安全载入”的蕴含；这不是已证明由完整接纳链产生的反例。§8在缓存资格中明示末点唯一、共同起点/补齐前缀检查，失败回原无缓存求解，并共同收其费用，不能等assert触发后才补资格。该缓存选择是显式适配，不改变原样轨道，也不把源搜索中其它PathTable写入自动算作已证。

重算输出另有可移除的无消费登记。固定runLACAM2在L693/L706把各agent截后的路径登记到PathTable；批准纯LACAM调用域不读取这两次登记的约束、冲突或目标信息，实际消费者位于已排除的runPP、LNS::run及邻域搜索。求解器不接收该表，下一次正常loadPaths/重算之前又经clearAll重置。当前共同源码修订因此仅删除这两处登记，保留原求解、顶点读取/复制、首达目标截分、soc、succ及后续commit/验证；不重建多目标表，不改变路线或收窄为目标唯一的roster。缓存载入checkReplan的登记及§8资格仍保留。此变换改变分配、清理与费用，所有相关R0内部臂共同采用，未发生的登记不收费；不声称native字节/成本等价，也不推广到启用LNS的外部候选。

此处提交前缀可作条件证明：设完整合法联合solution有M≥2层、原提交量为正整数k_commit。原首达层r_i未找到或小于k_commit时保留全部M层，否则保留r_i+1层。若M−1≥k_commit，每条截后路径都保留共同的前k_commit步；若M−1<k_commit，各条均保留整个solution，再在互异的最终位置补WAIT。因此在完整身份、合法顶点借用、数值可表示及完整联合solution无vertex/swap冲突的前提下，原commit前缀仍合法，无须要求截后所有末点互异。相反，两agent可先后到同一目标x、先到者随后离开，完整共同层仍无冲突；若两次首达均不早于k_commit，截后却都以x结束。这只反驳“完整联合序列合法必使截后PathTable登记合法”，尚未证明当前搜索实际产生该序列。删除无消费登记关闭这一额外前提，不替代完整solution合法性、索引/累计表示、费用及其它源后条件。

其中stay_target有独立的事前界。令J_plan为已固定公共O中PLAN_CHECK行总数，仅为输入计数，不新增预算/赋值；每行最多开启一个job，每job最多进入一次原commit。固定fleet/唯一agent身份及会话内原k_commit不变，批准入口skip_start=true，合法路径长度m≥2。短分支m≤k_commit时初循环结束step=m，随后恰增加k_commit+1−m≤k_commit−1；长分支先置零，初始化为零，固定源没有其它原向量写点。因此每个agent在任意正常包及commit中间前缀均满足0≤stay_target[i]≤J_plan·max(k_commit−1,0)，包括中心后来STALE的包。先以数学整数核右界落在源int域，便排除此特定累计字段的溢出；不能在源int中先乘溢出再检查，不用accepted次数替J_plan。k_commit+1、路径长度/遍历step和其它统计仍分别核；这不是完整AA证明，也不改变原清零/自增行为。

| 费用/表示类别 | 当前已选语义 | 现在的缺口与后续验证边界 |
|---|---|---|
| 时钟/随机/外部导入 | 原chrono比较与预算语义、模型工作clock、持续C PRNG及局部MT；§9.3限定float特化；未登记导入明确失败。 | 绑定所用编码/确定版本及原调用对应；源日志不反向带入宿主时钟。实现后核实际导入，已排除的log依赖不再作为同一特化的义务。 |
| 容器/内存/对象释放 | 固定字步骤；确定分配次序；唯一归属及实际复制/扩容/清理全费。 | “确定次序”还不是完整容器/分配状态变换；批准包所需操作的具体对应仍缺，不能把一次vector扩容或析构记一恒价步。实测峰值/宿主OOM另属后续资格。 |
| 诊断/日志/文件 | 业务日志/编码/持有仍付费；模型禁止一般宿主文件导入。 | 须逐一分类批准链中的输出、静态对象与可能回读，不能声称所有I/O都无业务作用并免费删除；未核导入保持FOREIGN_INPUT_UNMAPPED。C31没有取得构造，不能据其提示关闭本项。 |
| 几何/代数/可信记录 | §2–6的有限表示、精确谓词与原子根提交；展开实际字工作、暂停/失败规则已选。 | 数学可判定不等于给出所有费用展开。首个服务联合见证仍需各实际段和不可跨行guard的事前界；真实后端耗时及重放之后验证。 |

### 9.3 首次非空源输出与付费真实服务的分段见证

本节把两个证明义务分开：先证明一个明确子族的固定源正常非空分支，再证明有预先基本步界时该分支如何嵌入既有付费协议。此处没有实际map、输入配置、种子或O，不改变§11完整roster，也不给ALWAYS_ADVANCE全历史或H19执行资格。以下n_f仅表示已有有限fleet的基数，k_commit仅指原源commitStep的既定值；不是density N或新的调参量。

首次源子族要求n_f≥1，取合法矩形四邻格图的同一连通分量，每个起点s_i为degree-1叶，首目标g_i为其唯一邻点，全部s_i/g_i两两互异。冻结目标外层与curr_states均恰为n_f个合法身份，每行首目标非空；原距离表给精确有限距离且不与MAX_TIMESTEP哨兵相撞。要求本节前述共享源修订及正常初始化成立，进入原纯LACAM首次分支，原initial_run/initial_success、stay_target、路径表保持新建语义，冻结输入不被并发改写；不能凭叶条件豁免对象生命周期、整数表示或原比较器修订。所有邻址/长度/计数运算可表示，k_commit为原正整数且k_commit+1、n_f(k_commit−1)也可在对应源int中表示；传给planner_commit的curr_commits事先恰n_f个空行。分配、有限表示、库调用和输出/清理的正常性尚须下述费用域绑定，不假定任意宿主调用都会返回。

固定Instance.cpp L13–52的prepareDummy仍照常运行。前述左下修订后，原严格上邻判据只可能使loc=cols这一点漏掉唯一北邻0；不能声称所有自由点degree均正。同分量含至少2n_f个互异端点，其余至少一个四邻被计数，故可被收集的合格候选总数至少V_comp−1≥n_f；原程序按度桶累加并在首次达到n_f后停止，因此实际收集量K满足n_f≤K≤V_comp，原shuffle后resize不会因不足而补入伪目标。原runLACAM2中update_dummygoals仍为注释，prepareDummy不改真实目标队首。对每agent，PIBT仅有g_i与s_i两候选；原随机浮点项在[0,1)时，目标距离0严格优于驻留距离1。g_i未被任何当前起点或先前已选目标占用，swap检查跳过空邻点，不进入交换帮助函数或继承递归。所有agent各一次选择后得到全目标子节点；按已修一致目标位，下一DFS先检全目标并结束，不读取第二任务。各原Deadline检查必须未过期，不能删除检查或换预算。

因此原solve正常提议的联合路径恰为[S,G]。固定LNS.cpp L648–713两种reached_goal_time切分都留下每agent的[s_i,g_i]；§9.2共同修订已删除runLACAM2的两处无消费登记，本见证不再依赖该表写入。根另直接核L1236–1339及L1433–1482：k_commit=1时跳过锚点后输出[g_i]；更长原提交量先插入g_i，再由原短路径分支填充终点WAIT，输出恰k_commit项且future为[g_i]，back首次读取前已有元素。validateCommitSolution只见不同目标上的WAIT并返回true；它漏验首边和首层，故PRE_COMMIT_SHAPE与外层完整锚点/冲突检查仍不可删。这里证明正常非空提议分支及原切分的定义域，不把它直接当成已append或获得运动授权。

费用中原地图/距离/图构造、dummy候选及容器、n_f次PIBT、路径复制、n_f·k_commit个提交项、n_f(k_commit−1)次逐路径移动检查和binom(n_f,2)(k_commit−1)次冲突比较都保留；验证器外层成对枚举的空分支也收费。不能由这些计数直接给任意C++库工作恒价。已核的GNU libstdc++ 11特定32/64位优化分支，在本子族的两项std::shuffle中只作一次MT取数，uniform_int_distribution范围2的拒绝阈值为0；其它库分支不能继承此结论。dummy的default random_shuffle至多作K−1次原rand调用而不重抽，K为实际已收集候选数。glibc-2.35已读上游TYPE_3 rand体无循环；只有整个C随机状态独占、锁初态合法、无线程/信号/外部库重入且保留原状态时，wrapper可走固定两原子锁路径。若原调用确有srand，其原30次填表和310次预热照计；不暗加播种或改为另一发生器。具体实体与读证见73A3；该条件性有限路径不自动绑定本机Ubuntu补丁或实际链接。本轮下段另明确修订随机浮点的固定特化；容器分配、日志/清理及完整基本步对应仍须逐项关闭，不把普通“正常返回”当成预先已知的工作界。

2026-09-13新增共享参考库特化，仅作用于原generate_canonical<float,24>(std::mt19937)：由发生器基数2^32和binary32有效精度24，直接取所需取数次数m=ceil(24/32)=1，保留原一次循环、判断/计数、一次原MT取数、转换和后续运算；删除原为求m而调用的两个log、长双商及相关转换。该修改不覆盖其它生成器/实数类型，也不选择或改源种子；未绑定native builtin或FYL2X不能作为等价证据。删除这些计算改变库控制流、费用和可能的浮点标志，故是所有引用R0臂共用的明示源接口修订，既不声称旧native位轨迹/费用相等，也不为H19虚收。新版本未执行的旧log不收费，新版本实际保留/新增的步骤全费；有限字宽与表示的实际绑定仍须资格核验。

此特化绑定binary32的round-to-nearest, ties-to-even、确定的中间存储和无未声明重排/额外精度。原MT返回即使存于更宽uint_fast32_t，其值仍在[0,2^32−1]；减原min=0后转float，不能替换为截取高24位。__sum的先乘后加及结果存储保留；原__tmp*=__r是float提升long double、乘精确2^32、再窄回float，这些转换/乘积在本次__tmp=1时精确但仍各付费，不误称原式全用float。已舍入分子除精确2^32等于指数平移，非零结果至少2^-32且无下溢；等于1时保留原clamp，沿已核nextafterf(1,0)的取位/减一/写位分支得到1−2^-24。原分布默认端点0、1的减/乘/加照计，最终严格在[0,1)，不是任意区间缩放保证。最高有效位最多检查32个位置，舍入最多考察8个丢弃位及25位进位；其它本特化运算只涉及有限格式字段、固定精确常数和上述正常数域。每次字段读取、位运算、分支、写回及MT的有限twist/tempering均按§9.1展开，32/24等是源格式长度而非实验预算；这些计数不冒称完整模型总步数。该纸面修订消除本特化的超越函数/重抽终止义务，不等于已实现位级后端或全源继续域。

与上述源子族组合的物理条件是原整边M0互不相交、与其它agent驻留资源相容，且端点g_i+F+Z包含于对应真实任务服务域；保留非零F/Z、真实z闭环和原扰动界。首目标尚未服务且在本段保持真实有效，初始位置不同于目标，软件INIT可合法接续bootstrap，模式不禁止该原MOVE，消息及首次合格RUN的既定外生分量允许交付/START。这是一个公开说明的非空性证明条件族，不是删去主roster失败项的规则，也不由格图端点互异自动推出连续Mask条件。

完整付费因果次序如下。箭头表示必要依赖；凡跨作业、发送、接收或发布，都沿§9.2严格后继行，不把一箭头当作一个基本步。目的站收件的核验在原接收token与PROCESS_SLICE中进行，不能重新冒作一次CURSOR/TASK_REQ/POLICY/PLAN_CHECK；每个公共机会的计数、轮询和主体保持原义。

| 阶段 | 必须完成的付费操作与可见结果 |
|---|---|
| 初始化与已知输入 | INIT验证/建表/接续/未来发布及各gate激活链；使用已付共同初始Kc，确需追加CURSOR时走其完整轮询请求、双向通道、CAPTURE和中心核验链；TASK_REQ经C→A、全局A CAPTURE/复制/签发、A→C及中心核验形成K_task。 |
| 源请求与计算 | PLAN_CHECK作业触发/PROJECT/冻结，准备该job控制收件槽，经C→P通道安装；P按原切片运行源、PRE_COMMIT_SHAPE、原commit、封存及所需清理，未来发表源结果。 |
| 计划接纳与源处置 | 源结果经P→C；中心收件作业完整验证最新目标/锚点/版本并CAS追加Π。处置再经C→P，P在同一未释放job的预备收件阶段付费核验后retire。P持槽期间不排新的P作业；中心不持槽等待P。append只增加原槽，尚未grant。 |
| 原请求与准入 | 已append后的SOURCE_OR_EXTEND作业产生唯一原请求；C→E及本地付费接收登记后，由原ENTRY(PRECHECK)机会CAPTURE/认证，再经E→C。中心收件/准入作业付全静态几何、当前M0/parent/围栏核验、所有权转交、GRANTED和控制意图记录、CUM_CAP封装及未来发布；本子族走普通整边b=ell。 |
| cap与控制 | CUM_CAP经C→E、付费验证/预分配，严格后继发布时全额当前guard通过才安装C=ell；这不启动运动。SOURCE_REQUEST的原phase 1计数不能略过：仅在它被预先放到grant接纳前时才为付费NO_GRANT。原phase 2 CONTROL_RETRY在cap已安装之后处理并发送RUN；通道、本地认证和未来candidate发布均收费。 |
| START至真实服务 | 原ACTUATOR机会付完整当前身份/模式/代际/尝试guard及当前公共秩delay读取，成功才START。随后§3控制律自主完成原MOVE并发生END；一次合法RUN可完成此段，不以额外ACTUATOR次数替自主控制。固定TASK_SERVICE在真实有效队首与整个实体包含成立时记服务，END证明/READY/消费可仍待付费交付，不能反向成为真实Q的前提。 |

条件嵌入引理：若上述每段展开已有仅依事前编码输入、固定私有源初态及已绑定实体的有限基本步上界，所有不可跨行CAPTURE、当前guard、原子账本段和发布单元也有这样的上界，并且原公共文法/供给约束允许相应有限容量与行数，则可先加入单writer/FIFO、跨发布占槽及原phase轮转边，再取有限拓扑顺序嵌入一个事先定义的符号日历类。不能以DAG同层误判站点不冲突；源等待中心处置的保留收件阶段不是排在自身后的新作业，不产生该自等待环。选择/接收/失败空分支、轮询中间机会和已有必需业务均计入段界，不以“供给够大”替代上述界，也不按实际源完成行数改O。

该类允许源准备阶段的不同row_id共用同一符号时刻tau；依当前原clock映射，源各起止读取相同而elapsed为零，仍实际支付全部基本步并保留原比较/转换。相同物理时刻不等于同一行递归完成。把tau_START定义为该符号日历事前指定、由前段工作界保证已具备合法RUN候选的ACTUATOR行时刻；本首次新MOVE在该行由(s,v_ref)=(0,0)实际START，随后完整cap C=ell固定且不中断，由§3可取解析统一上界T_move=sqrt(2a_lo·ell/[a_launch(a_launch+a_lo)])+sqrt(2ell/a_lo)；LAUNCH首交点剩余距离不超过ell，故两段界之和覆盖原END，与已实现扰动轨迹无关。事前服务行若满足t_service>tau_START+T_move且先于Stop，并保持上述队首/实体包含条件，便计到至少一次经真实原MOVE到达后的任务服务。所有时间关系只是符号条件，未选实际时刻/供给或改保护参数；不得用实现后的到达时刻安排服务。该引理依赖尚未闭合的全展开费用/表示条件，当前不宣称完整源—付费—服务联合资格已通过，更不推出D优于R/E0、一般死锁自由、外部H19同源或整个比较域非空。


## 10. 外部原法、守卫适配与原样检查合同

“已发表基线”必须能追溯到具体论文及其中的算法；作者实现或忠实复现的身份、必要修复、共同域适配和差异均须说明。内部自定义控制规则不获得已发表基线身份，论文引用也不自动认证重组系统。当前比较身份如下：

| 比较对象 | 论文与实现来源 | 在本文可以承担的证据 |
|---|---|---|
| PIE-D 原法 | §1 AAAI2025论文；下述固定74cfba…为PIBT-D＋A作者实现复现候选，§8固定R0另作内部提议来源 | 原问题域内的原法复现和改进底座；共享修复/物理/计费适配另名另报，不能让原法在未宣称支持的横向误差域失败来证明优势。 |
| D/R、S/F_cap、E0及G/N | 本稿自定义机制、对照或消融；共享PIE-D提议来源 | 回答查询、释放和费用组织的内部因果问题。R/E0不是文献算法，D胜R/E0不单独证明胜过PIE-D或MAPF已发表方法。 |
| Ma等的MCP；采用TIP作者库仿真及本稿守卫适配 | Ma/Kumar/Koenig，AAAI2017，10.1609/aaai.v31i1.11035；下述固定TIP仓库明确将FSP/MCP列为仿真对象 | 仅在完整no-following等原条件匹配的有限计划族比较；不是AAAI2021的Causal-PIBT原创算法，也不冒充已有lifelong任务系统。 |
| H19-PR-COMMON-SYSTEM的两臂 | Hönig等RA-L2019论文的ADG/cut；当前固定作者库仅证ECBS组件 | 仍是待核验的论文方法适配候选。原ADG/任务驱动整套实现身份与必要适配的忠实性未闭，当前不能称作者原版或已合格强外部基线。 |

主theta_DR保留为事前限定的机制效应；更广的“基于PIE-D改进且有实用竞争力”结论还须可追溯的已发表方法比较。实验前必须把论文算法、代码分支、原域复现与共同域适配逐项对上，并解释共同安全接口是否掩盖或改变了原执行策略。若H19或其它必需论文比较无法取得忠实实现或匹配适用域，该证据义务仍未完成，不能用自定义R/E0填补、给重组系统换名称或只报较弱比较来宣称完成。原法复现、共同域系统比较和内部消融分别解释，其成本、失败与缺失均按既定规则保留。

PIE-D原文与固定代码的对应不能仅看类名。原文pp23390–23392列MCP、PIBT-I、PIBT-D执行和F/S/A重规划，实验二采用PIBT-D＋A；当前保留范围如下：

| 原文组件 | 固定0b5b336与当前适配 |
|---|---|
| 原执行与Dummy Simulation | 原CompetitionSystem.cpp L238–282/377–402的执行选择和仿真循环在本适配中被绕过，改用本文执行/信息合同。LaCAM内部funcPIBT生成搜索配置，不等于保留PIBT-I/D执行；prepareDummy也不是原文D.Simulate。 |
| A：利用未承诺路径指导全体重规划 | 原文Figure3用距旧路径及沿旧路径距离。固定纯LACAM在LNS.cpp L496–531清路径后全体重算；planner.cpp L411–420和Instance.h L77–80只按静态目标距离加tie排序。当前保留后者，不能称保留A的指导。原文Table1另列目标距离A_N；相似规则仍不证明完整A_N等价。 |
| 规划后的LNS改善及F/S | 纯LACAM的MAPFPlanner.cpp L46–73置迭代为零，未用其它类别的lns->run或F的LNS2修复，也不继承S的原MCP未来仿真链。 |
| 承诺切分/未来提示 | 保留planner_commit→commitPath；已接纳Π、非承诺缓存、PROJECT和付费触发是本文明示接口变化，目标揭示与第二目标修订亦须披露。 |

原域基线尚须完成下述已发表组合的代码忠实性和原域资格，不能把上述修改来源直接标成完整PIE-D基线。固定PIBTDDelaySimulation.cpp L56–62还先按当前位置到计划时刻位置的距离排优先级，累计延误只破平局；与原文按延误优先的描述有具体差异，后续原域复现必须说明处理依据，不从类名自动判通过。此处记录来源差异，不宣称原论文错误或已复现其结果。

作者实现复现候选现固定为官方仓库的[improve_morereveal@74cfba3c81a0c165c2e7044dea6fd4dee8ddf415](https://github.com/YueZhang-studyuse/LMAPF-delay/tree/74cfba3c81a0c165c2e7044dea6fd4dee8ddf415)，对应待复现的已发表PIBT-D＋A组合。此候选不替换当前R0：其[LNS.cpp L465–501](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/74cfba3c81a0c165c2e7044dea6fd4dee8ddf415/src/MAPF-LNS2/src/LNS.cpp#L465)从旧路径去WAIT/环并建立引导；[Instance.cpp L193–246](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/74cfba3c81a0c165c2e7044dea6fd4dee8ddf415/src/MAPF-LNS2/src/Instance.cpp#L193)用多源BFS构造“距引导路径＋沿该路径至终点距离”；planner.cpp L432–440实际消费该值；MAPFPlanner.cpp L82–115接LaCAM修复与LNS::run，CompetitionSystem.cpp L267–285/385–410接PIBT-D和后续窗口。因此不再把寻找含A核心引导/LNS的作者代码列为无来源，完整资格仍须完成。

该候选尚有两项明确的论文/代码差异：原文Figure3按距引导路径破平局，而[Instance.h L73–87](https://github.com/YueZhang-studyuse/LMAPF-delay/blob/74cfba3c81a0c165c2e7044dea6fd4dee8ddf415/inc/MAPF-LNS2/inc/Instance.h#L73)实际元组为常量、引导距离和、直达当前目标距离；PIBTDDelaySimulation.cpp L56–62仍先按距计划位置、再按累计延误排序。复现须分别登记作者代码行为与原文规则，不能假定两种排序等价或静默改后仍称原样。LNS::run→runPP还重新进入当前纯LACAM明确排除的调用域，不继承其局部修复/费用资格；本次未实现、未判完整基线通过。另核官方improve_delay@48f45dc16c88584b8e03eebe31bd69d6d7443c04仅用到旧路径指定时刻位置的指导，不选为A的复现依据；本地pie_upstream@ec410bc63470ed10c768baacd678e2609d9c4076属于PIE.git，不能冒充PIE-D版本。

MCP的已发表方法来源是 Ma/Kumar/Koenig 的 [Multi-Agent Path Finding with Delay Probabilities](https://ojs.aaai.org/index.php/AAAI/article/view/11035)，AAAI2017。所用仿真实现固定为 [Kei18/time-independent-planning v1.0](https://github.com/Kei18/time-independent-planning/tree/755a7ce740d49543b1165403371752c08e342ca4)，commit 755a7ce740d49543b1165403371752c08e342ca4；其[readme第10行](https://github.com/Kei18/time-independent-planning/blob/755a7ce740d49543b1165403371752c08e342ca4/readme.md#L10)明确是FSP/MCP的time-independent仿真，app.cpp也将MCP与CausalPIBT分别构造。本文名称改为MCP-2017-TIP-IMPLEMENTATION及其guarded adapter；旧标签NATIVE-TIP/TIP-MCP只指该仓库轨道，不代表TIP论文全部算法或Ma原作者代码。原字节/原域检查与共享守卫轨道分开；源mcp.cpp先nextNode后isStable、末下标访问plan[t+1]的静态缺口仍保留，不能把越界计作本方法优势。

守卫版每次激活先验证c的定义域；本地末下标直接HOLD不访问nextNode，否则唯一下一原步plan[c+1]。WAIT仅合法POLICY消费一次，MOVE no-start/在途不消费；仅中心READY后消费并转CONTRACTED，在此之前用保守EXTENDED表示tail=plan[c]、head=plan[c+1]。他者getT只用同计划代际已交付Kc下界和固定原计划依赖，未知返回WAIT；同一臂已付费CURSOR证据可复用，不免费读他者真实c/head/tail。守卫、单中心/物理接口和付费通信是显式变化，不宣称恢复原最小通信量定理。

补充匹配计划族在每公共block以同固定源和确定的R0计划输出供全部比较臂，生成授权之前先登记来源/作业/计划身份，不能从某策略成功结果挑计划。计划必须非空、vertex及完整no-following合规，含末端永久驻留；不适用登记INAPPLICABLE全行保留，主lifelong仍保留该公共来源。该族是有限计划的完成/服务/成本比较，不冒称TIP有相同lifelong分配算法。没有合法匹配block则补充族UNINSTANTIATED/UNESTIMABLE，不能隐去外部基线。下一episode只有全部旧责任合法drain后同规则重新INIT，不能reset未完成机器人。

另保留真实已发表lifelong外部候选Hönig等RA-L2019：原文IV-C/Algorithm2有ADG前驱闭合commit cut和规划执行重叠，不能称其只有single-shot。73L1完整作者PDF及两个作者库头文件已核；当前库4c75fa20c435c440d8b6bd6dc81668ddc7296ba0不是已证2019实验提交，尚未取得整套ADG/monitor/仓库任务驱动原始身份。忠实复现可以采用自行实现，但须逐项证明核心状态、依赖、完成及cut/重规划规则对应；原框架允许不同求解器，使用纯ECBS本身不构成失格。当前真正未闭的是完整规则对应、本文visited/触发/逐边停走等改动的影响及共同适用域。其native保留原动作状态/Type-1与Type-2依赖/任务规划及适用前提；若用共同PIE来源则明确叫共同来源ADG执行适配，不冒称整法原样。

H19共同守卫适配保持付费K/控制、完成证据/队列信息、不可撤销旧动作、cut快照与接纳检查、真正服务计数及全部ADG/规划/通信费用；新gate只延后该系统自己的原动作、不偷换MOVE。原法允许多动作预取及连续队列执行，本底座明确保留多动作逻辑入队，却要求逐边参考零速和付费END/READY交接；原未知障碍下清命令队列也不能直接用于此不可撤逻辑账本。native/共同适配分名，公开这些变化，不继承原活性/平滑性/通信保证或把新增等待归罪原法。下文给定所选完整纸面接缝，源及实际数值/服务后端资格仍未知，主lifelong外部对照尚未固定。

当前外部系统工作选择为H19-PR-COMMON-SYSTEM / ECBS-FA：按已发表2019论文重构ADG与前驱闭合cut，共同任务派发下固定各agent已知首个任务，以固定作者库4c75fa20c435c440d8b6bd6dc81668ddc7296ba0的纯ECBS作几何规划组件，产生它自己的原MOVE/WAIT。不是2019整套作者实现已复现，也不是PIE共同来源执行臂。73L4亲读四个固定头对象，指出ECBS-TA默认分支在全部子搜索失败后可能到未判空open.top；纯ECBS工作选择避免该特定额外分配分支，不把它称所有来源定义域已通过。根全文核读L4/L5后作此纸面选择；未冒称根重新全文读取四个原头或已观察异常。

冻结Environment用(time,vertex,visited)；已知首任务是访问义务，重复目标允许，访问后可以离开至互异末端，无任务agent仍占有空间且可以由外部求解器提出合法让路MOVE。visited只记预测访问，绝不更新A/Q。低层终止须同时已完成访问义务，且从当前层起停留不违反本分支全部未来约束；否则继续允许移动/WAIT寻找合法末端，不在返回后反复拒同一早停解。短路径延拓到联合末层作冲突检查，其后永久驻留；层上单位MOVE/WAIT成本只作离散搜索目标，不冒充物理执行时长。已知未访问时用静态图距离作启发式、访问后为零；无路/非法范围明示，预处理/冲突/ADG计算全部付费。ECBS原次优因子保持原意义未绑定；整型范围、浮点关系、hash/equality/容器、合法失败与所有依赖仍待固定定义域，不能以数学有限性掩盖数值溢出。

73L22进一步给出本固定Environment的局部源域收口：一次低层调用从层tau0出发，每个MOVE/WAIT都使层和规划g各增加同一单位，State identity包含time/vertex/visited且算术精确，因此所有抵达同一State的路径都有g=time−tau0。a_star_epsilon.hpp只对严格更小的tentative_g执行原地更新堆键，该分支在本域不可达；不外推变量代价、漏time身份或溢出域，也不证明全部focal/handle正确。ECBS高层id对包括低层失败在内的每个孩子递增；只在整批之前的展开回调查界不足，候选源资格必须在每次实际可能溢出的增量之前保护，或给覆盖整批的严格表示界。若需修改模板，两个H19臂共同登记修改身份和实际费用，不能静默称原样ECBS。

搜索域严格限定为无顶点冲突、无对向交换、无原ADG同层有向环的几何访问问题。原Type-1严格增层、Type-2不倒退，环必全在同层；固定环的所有参与原几何转移若都不变，则该同层环仍在，因此逐一禁止参与者该层转移的分支并集覆盖消除此环的路径。冲突选择先最早层，再固定vertex/swap/环类型和规范身份次序；禁止几何转移而不只禁visited位。该制度排除了同步占满环的无碰撞轮转，不能把这种外部无解说成一般MAPF无解。记J为有限互异联合顶点配置与访问位组合数的上界，根冻结几何问题的合法一步只依相邻状态，重复完整状态可删环，若有解便有至多J−1步见证。带绝对层禁令的CBS孩子不各自享有这条删环结论；正确限定是从一开始搜索J内域，冲突分支至少一子保留根的J内见证。约束需新且确被当前方案违反；这给条件覆盖，不给有限worker必找到、实际服务或固定E内收益保证，J不是新增调参预算。

取消L4曾提出的外部专属TASK确认离站屏障。H19满足原source/cut、ADG、共同运动授权与END/READY消费后可继续后继，不额外等待TASK知识或插入服务驻留时间。它与D/R/E0共享§8 SERVICE_TRUE及同一真实TASK_SERVICE机会和付费TASK接口；离开前若未实际服务，任务仍未完成并保留损失，visited不补造Q。未知完成造成重复访问是此系统策略的代价，与PIE PROJECT的预测机制单列比较。PUSH_RECOVERY只给END及资源交接事实，不免费给TASK或下一任务。

以下H19合同采用根L11、C10R及根独立分析后的L14批量修订，替换旧稿未登记的名义时长/机会和笼统cut条款。它是按原论文适配的明确设计，仍NOT_IMPLEMENTED/NOT_RUN，不能冒称作者2019整套实现或来源资格通过。

名义函数固定为T_nom(MOVE)=sqrt(2 a_lo ell/[a_launch(a_launch+a_lo)])+sqrt(2 ell/a_lo)，其中ell>0及a_launch、a_lo沿§3已登记控制profile的原义。它是完整原边、零速出发、已装整cap且之后不中断的保守解析时长估计，不包括no-start、BRAKE、通信、排队、规划或服务，真实完成仍可无界。T_nom(WAIT)=0只反映共同WAIT的一次逻辑消费无额外物理驻留要求，不使其自动消费/finished，也不免等待及证据费用。空序列/驻留锚点名义量为零，不制造动作。原动作/控制字段按可核有限编码的精确有理值解释，平方根/有限和及与公共已发生时刻的比较按实代数数语义并收实际位长/计算费；缺profile、非法长度、非有限编码或数值域不能认证分别返回BINDING/INPUT/NUMERIC_UNAVAILABLE，不能用主机估计或猜零补缺。数值后端尚未绑定，未为任何保护参数赋值。

H19至多一个冻结planner job及一个待处理结果。h是最近一次已在中心提交终态的attempt从实际付费输入CAPTURE到ACCEPT/STALE/合法失败处置的公共经过时长，包含队列、计算、验证与失败；在途attempt不形成h。首次没有历史只能以合法初始锚点开始，非初始历史缺失为PLANNER_HISTORY_UNVERIFIABLE。共同PLAN_CHECK收费检查初始化/模式/在途状态及下列需求：缺初始计划；尚未妥善处理的已交付TASK语义修订；或某参与agent从中心首个未finished动作起的完整名义余量≤h。参与指有已知未完成访问义务或未finished原动作，二者皆无的空闲agent不以零余量反复触发；已耗尽计划但有义务的参与者余量为零。无已知义务且无待更新队列/后缀时IDLE优先。触发后登记待处置规划需求，冻结输入的TASK修订与已接纳处理标记分开；失败/STALE不伪称该需求已解决，只能于后继实际PLAN_CHECK在模式/来源允许时重试，合法接纳或已证明需求消失才清除。源fail-stop不因待处理标记重启，已有job不重复发起，没有失败同一行递归或私有进度增O。

desired对每agent从中心首个未finished动作起按原顺序累计T_nom，取首次达到h的动作，不足取末动作；h=0且仍有未finished时取首项，全WAIT零和不跳过。无未finished则取合法驻留锚点。还须并入全部已enqueued/执行账本已追加、已登记请求/授权或发送缓存可能生效的原动作，以及历史任一cut已承诺但尚未finished的staged动作，再取旧ADG的Type-1/Type-2前驱闭包和各agent最大动作下标。中心只读已发布图/队列/请求cap责任、已付finished/Kc/TASK及消息记录，不读真实s/C/c或未交付END；没有ACK不能排除已签发责任。既有cut的未入队承诺不能在下一cut被忘掉。

cut只在闭包、原动作连接、互异合法预测锚点、任务与版本检查全部付费完成后一次原子封存cut_id、保留前缀/可替换staged后缀边界和冻结源输入，提交失败无半cut。此后cut外未承诺后缀从权威可调度/desired图移除，只可存为无发布资格的历史；禁止从它入队、请求或授权，规划失败也不自行复活。cut内staged可继续按ADG条件付费入队。已发APPEND/cap/RUN及已承诺cut不可撤，真实执行可继续至保留尾；封存不等于物理到达、服务或新位置观察。

新ECBS输入用每agent保留cut最后原动作的符号终态，空前缀用已认证锚点；任务只取冻结K_task首个未完成实例，visited不改A/Q。令cut_layer为旧保留动作最大离散完成层，新源相对层统一平移至cut_layer，使每个新动作起始层严格大于每个旧保留动作起始层；无旧动作则用原初始层锚点。较早到达的预测cut尾只作共同层驻留延拓的几何核验，不追加虚假可消费WAIT、物理驻留或服务机会。cut_layer是已有层的推导索引，不是新增lookahead/误差预算。

旧保留动作及旧依赖不改。新旧合序列按原Algorithm 1首次匹配/传递链规则核候选依赖，仅安装至少一端为新动作的新增边。严格时标不产生new→old Type-2，跨代Type-1仅旧尾→新首；旧/新各自合法无环时，跨两部的环因缺new→old边而被排除。仍须实际付费验证原端点连续、动作/任务语义、完整原ADG规则、短路径末端永久驻留、§10搜索域及共同连续几何接入，不以证明省略输入/对象检查。欠项为INVALID_SPLICE/GEOMETRY/ADG等具名失败。旧保留部分前驱闭合，新图不向旧动作加新前驱，所以不撤已enqueued合法性；这仅为依赖保持，不推出连续资源守卫无死锁。各agent在自己的旧尾按原Type-2及共同END/READY消费后可入新后缀，不设全队到cut或外部TASK确认离站屏障。

接纳须绑定同一cut/job/source、不可变原动作与执行槽、冻结任务义务及正常源结束节点，并完成数值/依赖/合图资格核验。Kc/finished单调前进或旧任务可信完成不因普通账本revision变化而必然STALE；后来新TASK保留为下一次待处理修订。撤销/改写目标/归属造成冻结义务不相容时拒新后缀，不回滚旧cut。接纳只更新未入队且未承诺的候选后缀，执行历史和旧消息不改。输入错误、合法ECBS穷尽false、公共供给停止、内存/表示不足、源异常、非法输出、合图失败、语义STALE、ACCEPTED分记且全费保留；无法证明源状态安全继续便终止其会话，不自动重启/重新播种或换法造路。无后继时cut尾HOLD和未完成任务保留。

H19执行账本按agent设Π_i[0..L_C,i]，本地只安装至L_E,i，0≤c_i≤L_E,i≤L_C,i；整个episode的plan_epoch固定、append revision另记，源图generation不重置执行历史。原动作id=(源job,agent,源动作下标)唯一，入执行槽后两端点/类型/前一记录身份不可改。staged仅为未入队候选；只有下述ADG_ENQUEUE单元合法中心提交，才连续追加一条执行记录并记enqueued。不同agent无需相同L_C。逻辑enqueued可有多条，不等于物理GRANTED：每agent仍至多一个未闭请求、每gate至多一个活动tid，新原MOVE须原END/READY/消费及下一合法PRECHECK，H19初始授权只取b=ell，不运行GROUP_PREFIX或产生组围栏；本地C仅由真实合法安装取得。

一次COORDINATE为H19启动一个有限捕获批ADG_ENQUEUE，原Srv_C单槽保留已提交合法有限图/允许发布域（当前合法后缀或既有cut保留动作）、各agent执行尾和身份引用。F0为捕获时中心已付费提交的finished集合，E0q为已enqueued集合（不指臂E0）；物理END、在途回执、APPEND安装或预计时长不加入F0。中心槽排除其它中心FINISH/CURSOR/MODE/新图/GC作业并发提交，故本批F0及原依赖固定；保留引用及必要字段读取/复制全部收费，不赠送全图快照。

每agent只能选择捕获执行尾之后原Type-1链的连续前缀：动作在允许域、所有Type-2前驱在F0、存在的首Type-1前驱匹配原尾已enqueued/finished身份，其余Type-1接该前缀上一项；首次不合格即关闭本批该链。原无Type-1初始链头仅在确为唯一原链头、没有前序执行记录且匹配付费INIT起始锚时准入，不造虚拟finished。各链最长合格前缀之并B0为此固定捕获域的唯一最大合格集合。每次按各当前合法链头的（原计划时标、agent规范key、原动作id）最小者选下一记录，成功发布后才推进该链头；所有依赖/身份/比较/头尾维护按实际位长收费，不要求每批重排整张图，也不把批内新enqueued当Type-2 finished。链/图身份损坏须失败关闭，不能伪装无候选。

批内一次只计算一条完整提交单元：首项含捕获/头尾检查、后项含前沿推进，均付选择、槽分配、不可变原记录、APPEND封装、索引/引用及发布增量准备费用。单元完成后封存，等严格后继发布行能付完整核验/发布才原子追加记录、标enqueued、产生独立不可变APPEND发送意图并推进批已发布前沿；不能半追加、预发、先算后条或一次免费发满批。前项发布后控制器仍占同一槽，只在后继实际PROCESS_SLICE继续。最后无候选检查、终态及引用回收/转移也收费，完成后才释放槽；空批照计，不拿一个有限O必能完成B0作保证。GROUP_ADMIT继续全组一个原子单元。

APPEND_ACTION绑定中心提交、session/plan_epoch/agent/槽、原动作/前驱身份、source/generation及几何/控制版本，经Srv_N原通道传输，Srv_E逐记录付费认证并在后继合法点连续安装。缺前驱的乱序包不跳槽，冲突拒绝，重复旧槽不重建记录、控制或c。历史安装长度及尾锚持久保留，前缀GC不能删去验证下一追加的必要锚；旧正文已合格GC时只按安装水位拒绝重装，不声称比较了不存在的正文。无新安装ACK/批送达屏障；中心可据自己的Π和Kc提出请求，但本地未安装时完整PRECHECK限定拒绝，不回报正确私有cursor。已发布envelope在原通道可独立传输，与中心准备后条并行；中心不持槽等待交付或Srv_E回执，不增任何站点/容量。

中心将Kc、生命周期消费下界f_cons、历史安装长度下界f_inst分开。合法CURSOR c=x可给f_cons≥x及f_inst≥x，并按原规则更新Kc；完整成功PRECHECK槽k可给f_cons≥k及f_inst≥k+1，不能给f_cons≥k+1或刷新通用Kc；合法FINISH_RECEIPT槽k可给f_inst≥k+1，不能推进f_cons/Kc。只用同episode/动作/槽的已付验证事实取单调最大，初值来自付费INIT；保持f_cons≤c及f_inst≤L_E≤L_C。MOVE ADG finished还须付费维护FINISH_RECEIPT事实，WAIT finished只凭CURSOR越过其槽或后继PRECHECK严格蕴含已消费并付维护费。finished、消费、安装、资源退休和真实Q均不可互相替代。

H19 SOURCE_OR_EXTEND沿共同Kc/原记录产生或重试当前MOVE，初授仅b=ell；CONTROL_RETRY与控制代际/尝试实际水位完全共用§5/7/9。RESEND_CAP在合法当前cap及APPEND两类均非空时按每agent持久二态交替，初态cap，只有实际发送意图成功提交才切换；仅一类有候选则用它且二态不变，均空为收费空结果，不因tid/generation重置。APPEND只选已中心追加且槽k≥f_inst的缓存；每轮封存当时L_C为尾界，规范槽序扫描，游标随实际发送意图提交推进，到尾后才重开下一轮，新append不延长当前轮。私有失败/未发布不推进，已提交后网络丢失不回退；每token至多一条，扫描/空检查/重传/拒绝均收费，不设入队窗口或新预算。

f_inst只让已证安装记录退出APPEND重传候选；实际缓存GC还须所有引用结束，执行记录/cut/ADG/pending/READY分别按消费/关闭合同保留，批末不能一次抹掉所有已追加记录。不保证无限运行固定内存。恢复仅是条件命题：有限目标槽及必要前驱记录保留、未fail-stop、足够实际选择/发布/传输/本地服务并有按前驱次序的成功投送时，连续安装归纳可恢复目标，不需额外CURSOR才能尝试后继缺口。真正MOVE与WAIT finished仍需各自知识/授权/控制/终点链，真实任务另须SERVICE_TRUE；选中一次或有限批不等于投送、执行或服务完成。两类交替也可能延迟丢失cap、错过RUN/TASK_SERVICE而降低Q；保留此负例及全成本。

批占中心槽期间真实物理/END/任务服务和其他站继续，中心接收/MODE/GC作业排队；尚未中心提交的MODE不得偷读，长批延迟MODE/FINISH正是本适配代价。已生效DRAIN禁止新规划/逻辑enqueue/新原MOVE请求及任一UNGRANTED首次正cap，已授维护/终点/缓存恢复照原规则；外生中心fail-stop或全臂Stop按公共顺序及时阻止后续计算/发布，不等批尾清完才生效。批部分失败保留已经原子发布的前缀及独立APPEND，未发布单元/后缀不新增承诺，失败与清理全费；没有清理机会则保留占用/未完成状态。仅后来真实COORDINATE及合法模式/来源可捕获新批，不复活失效私有增量。物理DRAINED不声称未来逻辑槽全已消费，恢复不回滚旧承诺或水位。

费用须覆盖PLAN_CHECK/历史钟/名义函数及精确比较、desired/闭包/cut/合图、批捕获与每项/终态、APPEND初传/交替重传/乱序拒绝/安装、各前沿与WAIT finished维护、所有私有失败、在途/未安装内存及GC。COORDINATE和PLAN_CHECK使用共同O/原站/容量/单价；H19不产生组，GROUP_RETIRE为不适用供给，NATURAL不虚构无用组几何/退栏扫描，STRICT仍按共同未用供给预付。批的逐条发布可早于全批准备完成而开始预取，但原中心槽可能延迟物理授权/FINISH/MODE；不保证较一整批原子事务或作者原实现更快，更不推出净收益。

固定源关键对象：R0 CompetitionSystem.cpp blob4e9a86921fda3fd15bd616c3c0dff461688254ed（27752bytes/885行完整）；.h 6daf0b9e3fa1015e49893b09be87940577427189（6753/243完整）；MAPFPlanner.cpp 94afb42df1a70f5e312a382e61cf83576fd7360e（6125/208完整）；DelaySimulation.cpp 1e1953d9fa9ccb1eb96ae5d7b8829f425679d113（14733/454完整）；driver.cpp b75764cc26c2374ce51dabb94e13a138e50f166f（6664/172完整）；ActionModel.h/.cpp fb3aa01448d3f9369ca7a423d975d4a148cbe1e8/3292164aa861521beda270f18b8d3892e35fbd21（3757/136、8164/220完整）；SharedEnv.h 7f4b4678ca9da7278e92fd4cdf9eed043f03a8e2（573/27完整）。LNS.cpp blob1fb0e54f8f2bb00af05de53233ae600774e36f2a、SHA2560113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2，仅指定规划/提交/时钟窗口语义阅读，不用完整关键词检索冒称全文语义。

外部mcp.cpp blob51459fc9ea27b3c8831b0a72d2455bca360b2223（1135/68完整）；mapf_dp.cpp 7537e71885496ff9b0a75bf8d49b0f2138044625（3758/170完整）；agent.cpp a5a8f1ba47d295cd93f728cb8ad2cf85caca3b3a（4569/206完整）。原README/CMake/license/headless接口已读：R0 MIT/C++14与Boost，外部MIT/C++17；文档与源码CMake/输入字段存在差异，按实际固定入口，不复制公开徽章token。对象完整目录/37项关键词审计另有证据记录，但本候选不由这些身份表推出依赖全闭或实测复现成功。

ORIGINAL-CHECK当前全部NOT_IMPLEMENTED/NOT_RUN：解除全部设计门之后才可按固定发布字节、官方headless目标及原合法样例记录平台/编译器/依赖/选项、返回码、输出/日志身份，检查非空、索引、合法动作、no-following适用域与真实完成；零返回码缺输入/空结果/未定义访问不算成功。源码异常、构建失败、原定义域失败与合法算法超时分别登记。现在不构建、编写/运行测试或实例化样例来“证明准备完成”。

官方命令的来源合同：R0固定commit的README L26–38与CMake L63–72建立非Python的lifelong；TIP固定commit的小写readme.md L25–33及根CMake建立app、链接lib-time-ind，可视化器另构建。以下仅不可执行的未绑定文本模板，配置/编译、入口帮助、真正实例运行分别记账，路径和运行字段均未实例化；由有界源码代理亲见构建/入口层，根先审合同，未把这次代理阅读冒称根重新全文阅读。

```text
rtk proxy cmake -S <UNBOUND_R0_FIXED_SOURCE> -B <UNBOUND_R0_BUILD> -DPYTHON=OFF -DCMAKE_BUILD_TYPE=Release
rtk proxy cmake --build <UNBOUND_R0_BUILD> --target lifelong
rtk proxy <UNBOUND_R0_BUILD>/lifelong --inputFile <UNBOUND_INPUT> --output <UNBOUND_OUTPUT> --outputSimple <UNBOUND_OUTPUT_MODE> --fileStoragePath <UNBOUND_STORAGE> --logFile <UNBOUND_LOG> --simulationTime <UNBOUND_SIMULATION_TIME> --planTimeLimit <UNBOUND_PLAN_LIMIT> --initTimeLimit <UNBOUND_INIT_LIMIT> --preprocessTimeLimit <UNBOUND_PREPROCESS_LIMIT> --commitStep <UNBOUND_COMMIT_STEP> --mapfPlanner <UNBOUND_PLANNER> --delayPolicy <UNBOUND_DELAY_POLICY> --delaySimulateAll <UNBOUND_DELAY_MODE>
rtk proxy cmake -S <UNBOUND_TIP_FIXED_SOURCE> -B <UNBOUND_TIP_BUILD>
rtk proxy cmake --build <UNBOUND_TIP_BUILD> --target app
rtk proxy <UNBOUND_TIP_BUILD>/app -i <UNBOUND_TIP_INSTANCE> -o <UNBOUND_TIP_OUTPUT> -s MCP
```

R0选项名见固定src/driver.cpp L40–55；commitStep还参与L106–158的任务揭示，不能只当执行窗。initTimeLimit在所读main声明但未见下传，不凭名字授予初始化耗时保证。--help在clock调用之后、notify和载荷读取之前非零退出，不能当成功运行/失败实例。TIP app.cpp L50–72的-s选择solver而非随机种子，L175起调用P->run并写日志，L255起用编译期_PLANDIR_拼计划路径；实例内部字段、默认覆盖及地图/计划均待独立合法绑定。省略未知字段不能自动接纳原运行默认。R0 Boost组件、TIP原生架构编译选项、平台/ABI/传递依赖与样例适用性仍未运行核实；这些模板不授权开始执行。

主内部GROUP_PREFIX不改H19的原动作/ADG/cut。H19所选外部两臂共同为整动作b=ell、无组围栏、付费终点推送与逐边交接：H19E0不买途中POSITION；H19R-S使用与内部R相同的§7稳定agent轮询、last_agent/完整tid绑定及可信空间退休能力并付全部实际费用，但途中清空不放松原Type-2必须finished。两臂都报告，不能运行后只挑较弱者；该共享观察能力不把外部变成PIE来源或内部组策略。§10现给定名义函数、公共机会、批入队/APPEND、cut与不可撤责任的纸面总规则，实际原源/数值/服务后端及全适用域尚未闭，故G4仍UNKNOWN，不能因接口文字已整合自授外部资格。

外部途中观测按阶段解释：未enqueued的staged动作若缺原Type-2已finished前驱，单独提高q_release不补该事实；Type-1仍按原enqueued/finished或同批连续前项规则，不额外要求它必须finished。合法已enqueued及其后续请求的原Type-2条件已在F0满足，finished单调且不向旧动作加前驱，所以“实际已允许请求仍有同一未finished必需Type-2前驱”不是合法负例。途中证据不能代替原END/READY/消费、任务真值或任何其它门。

已enqueued原请求p的局部资源检查严格从拒绝变合格，须原不合格外国owner资源集合B_p非空，且每个阻塞r的实际owner均为可依法退休的当前原tid t，付费提交的新q'_t严格超过r在U_t(0,ell_t)的最后相交进度lambda(t,r)；原endpoint的lambda=ell而q'≤ell，resident或其它保留责任不由此消失。非凸多段相交取最后退出、闭边界等号不清空。所有阻塞均实际消除且其余完整准入条件仍有效才满足该局部谓词，原grant仍需后继付费工作/发布；无阻塞则没有该项从false到true的增益。责任按具体动作而非agent名字绑定，同agent后继原MOVE不是已finished前驱本身。此条件不是实际roster正例，也不从离散ADG默认推出扩展F/Z管道及资源瓦片已完全被其依赖覆盖；缺边源错误不能冒作合法的几何差异。

局部q不能开放ADG或某次未解锁，不推出H19R-S与H19E0全轨迹相同、Q或总成本有固定大小关系。SELECT/接收退休用Srv_C，CAPTURE/封装用Srv_E，通道用Srv_N；新增作业改变各自队列、控制/APPEND/规划输入及真实服务时序，APPEND本身只安装逻辑记录不新增物理owner。Active还包括物理已END但中心未FINISHED者；POSITION可从匹配的历史终点记录取得下界，因此事后须依原采样/END审计点区分未END时的证据与END后历史记录，后者不宣传为运动途中的观测增益，也不因此改变RR资格或把真实END提前告知策略。两个预登记外部臂及固定失败/缺失总体全部报告，从原允许且付费的决策日志区分ADG未就绪、其它门拒绝和额外资源阻塞/清除；缺记录不增免费真值，也不按解锁效果筛roster。内部对H19差异仍按系统效果解释，不全归因于D分数或预写外部观察收益。

## 11. 公共来源、完整选择器与比较预注册

只登记已经核验的公共源元数据与未来选择函数，不读取旧35–38、Q-CAL/Q-CONFIRM载荷或桌面。R0 lifelong tree=22ae3c8b3ad1f4791bd8c15b7d7b5521ed043c17；city=3e12a4483e615cd1a261d1e2476a29294fa4d0d1、game=8d8f8fbe8d16d80f5dab7a5cbf5ab6f3a341215a、random=2264326dfda14559e0db92e1649aaf512f9ff98f、warehouse-s=60b252f11972fed7d12f00960a7c6738b3f35a19；delay tree=4e3fe329a547e682d1520047bf767a5397b3b43f。它们不是已生成的实验实例。

73L6已实际恢复Benchmark-Archive固定引用README与非递归根元数据，根又独立取得纯Git commit对象和其明确tree对象：commit 25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a的tree为6030f1878e6abf48b833b5b7212953259fc81cb1，非递归四项、truncated=false，根按161字节原生tree帧复算一致。README blob为77ddb82e6cba768e590d91976d158ec74dc8ee5f，根亲读全部1008字节/17行，SHA256 1cf7f15a1389560b1fc7e3aa69734c3be69915ea2a10ca7fef5a1d40f116ba61且Git blob复算一致。它自述赛事年度实例/解归档；根树无独立许可文件、README无许可条款，不证明子树/具体素材无授权。此前以commit引用请求tree时顶层sha回显commit的差异已由独立commit→tree及真实tree读取消除身份歧义，未改L6原回执。R0具体对象→该归档上游blob→合法转换/本地身份→具体许可链仍未核；没有读取任一实例、结果或生成脚本载荷。精确来源链接与根阅读范围见73A2。

根73L8进一步实收并复算14个非递归tree端点：归档固定2023 Competition→Example Instances→四domain→maps，以及R0四maps。random-32-32-20.map在两固定入口同为blob b44f5a949e91b251b0e3bb29f3cd0784ce7d80b5、1091字节；此单对象关系已核。Paris同名但blob/大小不同，game/warehouse示例条目不同，不能说四类均直接同源或猜转换原因。根实际读取Moving AI的[grid说明](https://movingai.com/benchmarks/grids.html)、[MAPF说明](https://movingai.com/benchmarks/mapf.html)与[目录](https://movingai.com/benchmarks/mapf/index.html)：四个R0地图名称均列明且说明页明示ODC-By入口；[ODC-By v1.0](https://opendatacommons.org/licenses/by/1-0/)全文已读，其数据库/独立内容权利和告示范围须区分。网站同名不是Git对象一致，页脚也不抹去集合级说明；R0逐项上游版本/转换及agents/tasks/delay许可链仍未闭。全部本次读取限元数据和说明/许可文字，未打开地图/场景/配置/图像或结果载荷。

未来获准合法绑定后，按固定树规范相对路径的字节序枚举四类别全部JSON；用原driver的mapFile、teamSize、agentFile、taskFile、delayFile字段，位置为L101/112/114/115/150，固定driver SHA256 3198636d1114e4901c9aae48d549787c9fb3bc3a0bdfd49b6445d81bb5fc4f44。引用相对JSON父目录解析，规范化后须仍处同一固定公共树；拒绝外部绝对路径、未解释符号链接、缺blob、非法编码/语法。源图/agent/task/delay的索引/长度/静态通行和初态合法性分别给理由。teamSize只待density N合法绑定后检验原义相容，本阶段不按文件名取N或猜robotFile字段。

本次明确修订共享主总体的来源身份为source_id=(category,map_blob,agent_blob,task_blob,effective_delay,assignment_strategy,effective_semantic_options)，替换旧式中的原始delay_blob身份项。effective_delay是§9原输入行序在全部预定共享profile之潜在公共ACTUATOR支持上的有序0/1投影族，并绑定对应机会结构/行身份；不按实际读过或成功的轨迹截取。公共机会结构先由原共同设计和有效的非delay输入确定，不依delay位值、文件alias或尚未定义的source_id，避免source_id→O→投影→source_id循环；后继block身份/创新根才可使用规范source身份。完整raw delay_blob、首行与所有alias保留作出处，未使用行列差异本身不生成额外等权来源。

同语义合并同时要求上述其它有效字段、全部必需profile支持及有效delay相等，而不是只比两个延迟子矩阵。有效语义选项按原driver真正使用项和本稿具名适配解释：例如本次JSON的numTasksReveal未被原driver消费，不能仅因它不同就构造不同native揭示制度。任务揭示深度仍按§8原CLI含义待合法绑定，不从原文件的1设置。合并保留全部路径和对象别名，同task跨地图建立incidence，不假设严格嵌套。若固定O/合法行序/必需profile或有效语义改变，必须在结果之前重新核alias及总体；不存在实际roster时不造合并前后数量。

各类别完整采用所有静态合法来源，不按原规划是否快、某策略能否成功、预期效应/可见性筛选。静态排除保留路径、身份、失败谓词与证据，动态失败不改roster。任一必需类别无合法来源即UNINSTANTIATED，不拿另一类补齐或重新分权。保留后文等权层级公式不证明新旧数值总体相同：effective_delay合并可能改变每map来源数及权重，须在未来固定清单披露原始alias到有效成员的重数与口径。本次已显式改变模型/来源身份目标，不能宣称只是无害重命名；native原样资格继续绑定完整原blob及原时刻消费，不能继承共享投影等价。

future manifest必需字段：全部源身份/alias/解析字段；官方与适配版本；原任务策略与合法分配初态；物理、可信观测、普通错误及故障profile的有限函数/语法和适用域；几何表示/初态证明；原参数语义和待授权绑定；公共O、固定评价窗口/设计暴露E与cutoff；服务能力、费用、精度、指令/浮点语义、编译器/ABI/库版本、clock/RNG外部接口；重复索引和独立block根的角色派生规则；各臂及native/外部族适用性；计分、停止、缺失、权重、推断和报告合同。当前各载荷、种子、表和绑定均未生成，manifest状态UNINSTANTIATED并不伪装实际检查通过。

共享四臂D-S、R-S、D-F_cap、R-F_cap维持相同物理控制/静态K、原PIE提议及参数含义、共同ALWAYS_ADVANCE / FAIL_STOP_SOURCE与相同继续域守卫/单待结果屏障、可信字段与可购买能力、共同O/容量/费用函数、原任务流/分配规则及外生创新函数。真实派单/请求/payload按各臂自身闭环产生，规则相同不要求实际派单次序或证书逐字相同。它们共同采用GROUP_PREFIX、G-GEOM精确集合制度及PUSH_RECOVERY，所有cap/组/退栏/控制能力相同；S/F_cap按实际释放下界分开，F_cap可省无用途退休工作。E0同样使用上述AA来源会话、继续域/失败规则和待结果屏障；它不主动生成POSITION，也不构建无用途退出事件/退休索引，保留同M0/Mask(E)检查、CURSOR/TASK/PRECHECK/PUSH_RECOVERY/grant/READY等必要共同服务，费用照自身实际工作计。它没有更差的底层控制或信息真实性，只选择不购买途中进度。N-GEOM/G-GEOM的补充比较固定同一查询策略与S，在同输入的离线集合函数合同之外另报NATURAL闭环费用，不能为同迹强行冻结物理。

所有共同适配臂，包括E0与H19-PR-COMMON-SYSTEM，均用同一付费真实END首推、缓存重放、两个公共retry、真实服务与READY消费能力，不强迫额外周期END轮询来制造通知差距。共同PLAN_CHECK/COORDINATE及原机会/容量/单价/故障函数相同，触发谓词、每批工作量、实际END时刻、消息数、等待及重复成本由各自闭环决定。内部主平台GROUP_PREFIX的强R/E0同cap/CUM_CAP、RUN水位、组/退栏及无中点END/ACK；H19按§10自己的ECBS-FA/ADG/cut、多个逻辑预取、整动作物理放行及APPEND恢复映射运行。无组省去无用组工作，原队列/合图费用则完整计入，不以“能力共同”推导来源已资格化。

唯一确认主估计仍为NATURAL的D-S−R-S；STRICT仅检验固定预付供给的机制，S/F_cap、G/N与交互为预先列明的次要分析，不择显著者替主效应。E0是必报实用性比较：对D-S−E0给同总体的点估计和预定有效区间；声称“中途观测值得购买且值得定向分配”必须两项均有正证据，任何一项不支持都保留。三臂分数不齐不能给这个合取结论。主D/R比较本来已用固定Z的合理S，新增朴素几何不是首次补上空间安全。

外部预先固定H19E0与H19R-S两条系统臂，均按§10同源ECBS-FA/ADG/cut/批与重传合同。预定系统级次级比较为D-S−H19E0及D-S−H19R-S，两条同报且归§12的明确两比较同时推断族；不择最佳外部回写确认主量，也不以较弱一条替代另一条缺失。它们涉及不同规划机制、队列与放行制度，差异只能解释为整个具名系统在共同世界/供给下的效果，不全归于D查询分数。固定roster、来源适用性和失败/缺失规则一致；某外部在既定域不能合格时登记该比较不可估/不可推断，不运行后缩小地图集合或重分权。

上述效应名称明确对应ALWAYS_ADVANCE / FAIL_STOP_SOURCE闭环profile，包含查询引起的规划次数、过期调用、缓存/随机历史、时间和成本影响；不是固定规划路径下查询的直接效应。AA与accepted-only在相同后继可见输入下仍可因前次正常拒收的随机消费/缓存而给不同提议，不能声称trace等价或普遍优劣。若要分辨状态制度交互，至少需同一S下D/R各自跨AA和accepted-only的预定交叉对照；只有一个R回滚臂不足。当前没有合格回滚后端，不把该交叉当已可实施的新主检验，也不为配齐对照免费删快照费用。共同取消快照的收益属于共享适配，不认领为D创新。

权重固定为四类别等权、每类不同map_blob等权、每map内不同合法source_id等权、每source内全部预注册profile等权、每profile内固定重复索引等权，其乘积为w_b。不按运行后可发布性、完成时长、成功或故障删行/重归一化。目标仅是这个固定来源组成下的创新期望，不代表所有未来仓库。计真实Q/E，另报实际到达、最小间距/安全认证状态、未完成和停滞、全队/局部等待、观测采样至交付时滞、planner超时、中心排队、通信/实际工作/内存、首次/复用/失效成本；退休次数与瓦片数是机制量，不替代Q。

空间profile必须包含不能由时间重参数化消除的横向偏差见证，并区分无普通误报的准确采样层与普通误报/丢包压力层。配置选择由明确模型/控制假设和预先登记来源决定，不以调大误差或延长处理人为制造收益。两台LIMO不赋density N，现有平台接口只支持可选现实假设检验；大规模lifelong纯仿真为主，连续安全评估不可退化成只检离散端点。native与guarded外部族按§10保留，适用性缺口不由共同底座消除，原源码失败不当新方法获胜。

profile总体分层必须事前唯一：MAIN_IN_MODEL只允许§2/3当前有限参考/空间驱动与服务区域子域、原可信物理条件及§9所列模型内通信、普通反馈、no-start和分量故障机制；STRESS_TRUST_PHYSICS专门声明会破坏这些前提的机制。成员资格依据生成机制/支持集及来源定义，不根据运行后是否真的breach归类。MAIN中的意外breach保持原主行及失败标志，不能改挂压力层后删去；压力层单列自己的固定权重和描述，不能在主显著性不够时混入。四类别/map/source/profile/repeat的主w_b仅在MAIN_IN_MODEL的完整事前roster定义；任何类别/必需profile无合法成员时UNINSTANTIATED，不运行后重归一化。静态合法性、软件初始化成败与实际结果选择是三种不同事项。

来源补核73L2给Moving AI的ODC-By/独立素材权利及研究分发说明。新根73L18通过固定LoRR官方归档25ffd5b6a39b6fe30e5bc6cb5e22720a9531ea8a与固定R0的完整Git树元数据，已定位city的Paris_1_256.map（blob0ff641690b48c1c4807fcea7c0c31d167973b221）及random-32-32-20.map（blobb44f5a949e91b251b0e3bb29f3cd0784ce7d80b5）同blob/size对象，全程未读地图载荷；归档README明确比赛实例来源，补上此前首页只有JS壳的入口。该证据不证明复制方向/更早原创权利或适用许可；game的ht_mansion_n、warehouse-s的warehouse-10-20-10-2-1在该归档没有同blob对应，不能用另一同类地图替代。R0软件MIT/归档存在及同名文件均不能关闭全部素材权利，agent/task/delay生成/转换链仍缺。本草稿仍未实例化合法source_id/roster，没有读取受限载荷或复现实验；许可与全部数据资格保持UNKNOWN。 L19完整有界报告经根全文核对，补充官方Moving AI目录把ht_mansion_n列在Dragon Age 2分类、目标warehouse文件列在MAPF集合及仓库更新说明；仅支持具名分类和分发说明上下文，没有官方对象hash。官网两个目录的game尺寸顺序不同不能自行解释为转置/显示约定，名字/状态数不替内容身份；根不冒称已直接抓取代理四页。两目标与R0的完整对象/适用权利链仍未闭，不能套同类许可或扩大论文效度。

2026-09-12用户已允许本次固定官方四类首配置及其引用输入的有限只读静态核验。根L23实读四JSON及13个引用对象（共用一delay），全部内容Git blob重算匹配；四配置的位置记录足数、十进制单位置、起点互异且起点/任务均可通行并位于共同四邻接分量。原delay有5000行、每行2000位，首行第二token53983未被原parser使用，实际numTasksReveal也不由JSON同名字段决定。源文件数值只作已有对象事实，不采用为density N、时间或其他保护参数。该证据关闭这四个对象的基础格式/引用/位置缺口，不等于全364配置、连续F/Z/Mask初态、ServiceRegion、完整源继续、delay支持O或来源权利链通过；未读取其它配置/旧Q，未生成source_id/roster或运行原算法。L23A仅核parser必要条件，C28为非正式建设，均不计本稿通过票。

## 12. 故障停止、总分类、评分与固定总体推断

本稿新增、待审的基础区分是WORLD_GIVEN与软件INIT。给定静态合法设计X，数学初态t=0已规定每agent真实位置/参考原点HOLD/误差z、真实任务账本A和bootstrap resident覆盖E_i；各E_i的Mask不交且静态安全。这是所有共享臂相同的纯仿真世界/可信基础设施初态，不是某算法免费读到真值或已完成几何建表的结论。软件未就绪时低层只能持续该bootstrap HOLD，原世界z闭环仍演化；中心失效/INIT未完均不得删除bootstrap责任或让机器人消失。中心的应用索引、可读知识及规划worker尚未建立，仍须付费INIT才能使用，不从数学初态直接给查询策略全图/全状态。

软件INIT只在自身付费输入复制、核验、索引和协议初始化完成后，以相同agent/起点/几何/会话绑定，将已经给定的bootstrap责任原子接续为软件可用resident，并发表共同初始知识。失败/延后不部分转交、不发新MOVE，初始实体覆盖一直保留；成功转交前后均为同E_i，不能新造安全空隙。其保持理由是BOOTSTRAP期间参考原点不变、§3的z闭环持续在Z、F/障碍/会话未改变，因此整个E_i一直有效；并非以过时的一个t=0真实点证明接管时几何。底层HOLD和可信身份必须已具备，不得反过来依赖尚未完成的软件INIT才能执行。前提破坏按预设Stop/flags，不能继续引用保持证明。这比72的“软件INIT之后才有物理评分域”有实质变化，须独立审查，不由旧INIT证明自动继承。

真实TASK_SERVICE从公共世界t=0起按同A、实体资格及Stop规则发生，软件初始化本身不是服务资格：未初始化算法保持初始位置也可能已在合法目标上服务，是否Q=0由真实事件决定，不能由INIT状态赋分。所有软件INIT/预处理费用纳入同固定E和服务容量，世界创建/仿真宿主/共同控制基础设施的实际成本另完整报告，不能将算法特有工作改名世界创建。数学上给定合法初态不等于真实机器人免费标定/部署；本主θ是该共同合法待命世界中的lifelong任务效应，初始化成功、真正MOVE启动、首次总费用和可观测评分联合报告，不能只给稳态曲线。

任务世界求值的宿主消耗是实际评估成本，不能回写成服务时刻或设施CPU延迟；主Q/E仍在固定虚拟窗口，含原在线应用/控制资源竞争，但不声称完整实机任务设施处理瓶颈。逐臂另报世界准备/精确任务求值/其它宿主CPU、经过时间、内存及记录/失败，用量不要求相等、不临时加权为新效率分；世界求值若昂贵或难以扩展，保留该负结果。纯真值设施与部署应用按用途分界，查询/几何/规划/授权专用工作不能借宿主项规避原容量。当前选择改变了旧任务CPU耦合，不自动继承原闭环效果或费用统计。

静态WORLD输入非法或未绑定时没有合法设计X，保留完整静态排除理由并不产生数值推断。已入固定roster的世界丢失/主机未发起不能事后改记静态非法来删行。HOST_NOT_LAUNCHED/日志丢失不同于软件INIT未就绪：即使数学潜在轨迹在合法X下有定义，也没有观察证据据以输出某个Q。源未定义行为/算法映射不闭仍导致INFERENCE_UNAVAILABLE；本世界初态约定不能修复源码语义缺口。

若任务宿主未完成或未认证某TASK_SERVICE整行事务，只保留此前可证前缀与具名未知项，后继A/服务/规划依赖不从半成品继续。数学世界仍可能已有真实服务，不能将A^-宣称该行后状态、谓词当false、添加物理Stop或给尾部填零；宿主停止产出证据不等于在虚拟时间插入HOLD。行内已认证部分可私存，但不作为完整A发表；既有UNKNOWN_NUMERICAL/UNVERIFIABLE及固定roster/分母/识别界适用，不假定缺失与臂或结果独立。已认证中点HOLD/无合法队首等可以按原谓词明确不服务，精确贴闭边界可判零，不自动归未知。已有物理/信任Stop和预设CUTOFF另依原合同，本段不替连续前缀认证或实际崩溃原子性。

任务环境必须独立软件READY而总定义：A的初态、每个有限TASK_SERVICE行的至多一次合法队首完成、§8的共同补给/空任务规则、全局次序与去重都由可信世界环境继续执行，不能下一任务突然改由未初始化的中心创造。评价器知道真值只用于定义/核验世界事件；执行基础设施只维持已给HOLD或已证旧控制责任，不免费替中心核验新MOVE、读全局阻塞或发布进度。新增动作准入/证书仍走全付费接口。

本E的起点是“共同合法待命物理世界已给定、应用初始化尚可未完成”，因此包括软件INIT/运行费用，但不自动等于从真实机器人上电开始的部署性能。世界/可信底层准备成本即使另报，也不能将本θ改称完整硬件部署吞吐；算法特有的建表/校准不能迁入公共世界准备。是否保留与72相同的静态支持集须按§4原先已有的初始Mask不交与§11选择器逐项比对；本稿未求值roster，不提前称支持集等价通过，也不以更窄INIT成功族替代用户的大规模任务。初始化分离的接口、费用、总轨迹和支持集仍是固定前核对项，不提前判S4已闭。

先区分分量故障与全臂评价Stop。合法no-start、普通误报/重放、通信分区、中心fail-stop、planner合法超时/NO_PROPOSAL等在模型内按既有责任继续物理推进至预先cutoff；不能因中心已停止就把在途机器人或后续合法服务计成不存在。AA来源会话的NO_PROPOSAL_SHAPE/SOURCE_ERROR/INVALID_OUTPUT按既定条件fail-stop且不自动重启，亦不清空物理世界；保留故障标志，只有已接纳原段可继续，没有新原段时合法HOLD。明确原停止预算可禁止后续新工作，旧物理仍遵守覆盖与模式合同。

全臂Stop只取公共顺序最早的预设CUTOFF/STOP、不可认证的物理推进、物理/信任前提破坏或无法维持定义的协议状态；事故触点可被精确认证时截断到该触点。并列按下述主类优先级记录，同时保留全部次级flags。Stop截断原区间，之后不再服务、不继续到刚好完成、不释放责任；这是评价函数的终止约定，不是声称真实车辆已安全停下。评价器/日志损坏没有可证Stop前缀时属于未知评分，不伪造零结果。

Classify为总函数并与Score分开：缺设计绑定→UNINSTANTIATED；静态WORLD初态不合法→INPUT_INVALID/NOT_ADMITTED；主机/评价器未实际发起或无其可信回执→NOT_LAUNCHED；WORLD已成立而软件INIT未形成合法应用提交→INIT_INCOMPLETE；界内可证实体碰撞/互斥破坏→SAFETY_VIOLATION；物理/信任越界→MODEL_BREACH；协议/身份/因果或源未定义访问→PROTOCOL_OR_SOURCE_INVALID；数值不能认证→UNKNOWN_NUMERICAL；评分前缀缺失/不可信→UNVERIFIABLE；其余已证不可恢复执行故障→EXECUTION_FAILURE；完整合法窗口至预定末端→COMPLETED_EXPOSURE；早于末端的合法cutoff/STOP→ADMIN_CENSORED；其余TRACE_INVALID。按此优先主类同时保留所有flags。INIT_INCOMPLETE只描述软件状态，不能自动取消已经存在的WORLD物理前缀、直接填零或推评分缺失；NOT_LAUNCHED也不能与之混用。安全域独立为VIOLATED、VERIFIED_ON_PREFIX、UNKNOWN或OUTSIDE_MODEL，没发现碰撞不等于已验证。

软件INIT_READY是对给定WORLD初态/身份的付费应用核验、索引初始化及bootstrap责任合法接续，和首次ACTUATOR成功START不同。初始化/预处理费用在同E内，慢臂不重开窗口。WORLD_GIVEN成立但INIT未完时仍有合法HOLD物理前缀；以完整真实TASK_SERVICE计数可Q=0或Q>0，不从INIT标签直接赋值。已有合法世界后立即发生可定义Stop、零前缀可验证且无此前服务时可Q=0；主机未发起臂、日志损坏或不知道WORLD/前缀是否合法时仍UNVERIFIABLE。任何数学潜在量与实际已观察分数都须分开。

全roster还必须报告联合结果，不将它们任意加权成一个奖励分：各臂软件INIT是否在固定E内完成、首次MOVE是否发生、INIT完成时间（未完成/未知明示）、INIT/预处理及全部费用、WORLD/前缀/评分证据可用状态。所有概率/比例分母按固定roster；状态未知只给已证真/已证假/未知及相应识别界，不装作已知失败。主机缺日志只能给本来有定义的指示量/分数的观察不确定性，不能反推初始化失败。不得改报各臂成功初始化者各自的条件吞吐差来替代主θ，亦不选择事后共同成功样本。

observedExposure为Stop前已证物理区间长度之和，空则为0；合法resident HOLD也算，未认证积分步、仅排队的主机时间不算。设计分母E_b>0由预先固定完整评价窗口给出，保持既有保护参数含义，不以observedExposure、初始化完成时刻或实际完成耗时替换。比较对象是固定窗口中的服务表现，不能事后缩短失败臂分母。

每agent每公共TASK_SERVICE行最多服务一个合法已分配队首；相同目标的不同task_instance_id可分别完成，同一实例/重传不重复计数。评分证据包含assignment/task_revision前后、service_id、真实模式/实体服务区域的证据、行序、Stop边界及去重。Q只取完整真实服务前缀；Stop前已发生而证书后送达的服务仍计入，普通COMPLETE、查询归因或READY是否到达不决定Q。Stop后约定无新服务，不再仿真补满E。

Score输出VERIFIED(Q,observedExposure,E,flags)或UNVERIFIABLE(reason)，以WORLD_GIVEN及完整可证真实服务/Stop前缀为根据；不以软件INIT_READY或首次START作为潜在Q定义的必要条件。缺日志/主机未发起不能填零。源未定义行为、适配语义未闭或同能力对照不成立时，即使物理服务可数也仅作描述，相关因果比较INFERENCE_UNAVAILABLE；合法搜索超时/无解/模型内通信或软件初始化失败则保留全roster分母和实际可证物理服务。主D/R推断需两臂所有预定block评分完整，D/E0与合取需三臂；缺失整项比较UNESTIMABLE，不删行/改权重。

条件于固定合法WORLD设计X及全部方法动态映射良定义，主d_b=(Q_D-S,b−Q_R-S,b)/E_b，theta_DR=Σ_b w_b E[d_b|X]，Delta_DR=Σ_b w_b d_b。Q是物理世界真实服务数，软件INIT未完不使其消失；若bootstrap/环境轨迹定义本身缺失，此X不能满足本条件，不套区间。Qmax_b为公共O允许服务的(row,agent)对数，每臂0≤Q≤Qmax_b、|d_b|≤U_b=Qmax_b/E_b。创新根只按block相互独立，块内各臂可相关；同地图不证明独立，跨block共享扰动或按结果改排程/学习违反条件。

当前条件概率明确为P_model。给定全部固定设计X，每臂在block b的完整潜在评分必须由确定映射Q_a,b=F_a,b(X,Z_b)给出，Z_b在X条件下彼此独立；源私有状态只在本臂本block内按AA持续，没有跨block的可变模型缓存、随机状态、学习或自适应排程。由独立根的可测函数保持独立，原w/E/U与下述Hoeffding证明在P_model下成立；同一固定地图或全局固定常量不破坏它。host clock、分配地址、未定义访问、平台浮点分支或host OOM一旦进入F，便尚未满足该前提。真实宿主只决定是否/何时得到评分证据，缺失保原UNESTIMABLE及错误发布联合界，不宣称条件于成功记录仍有原覆盖。theta_DR是此明确新执行法下的目标，保公式与研究问题不等于证明与旧real-host目标数值相等。

沿用既定95%约定alpha=0.05（不是保护实验参数赋值）：radius=sqrt(log(2/alpha)/2 × Σ_b(2w_bU_b)^2)。CI_DR为[Delta_DR−radius,Delta_DR+radius]与已知目标范围[−Σw_bU_b,Σw_bU_b]的交。全U=0时theta=Delta=0，返回退化区间，不除零。缺绑定/空必需类别→UNINSTANTIATED；必需评分未知→UNESTIMABLE；权重/E/bound/独立性或来源比较域无效→INFERENCE_UNAVAILABLE，均不输出虚假数值CI。

证明：Y_b=w_b(d_b−E[d_b|X])的支撑跨度为2w_bU_b。有界变量对数矩母函数的二阶导为倾斜分布方差，至多跨度平方/4；在0处函数与一阶导均为0，积分得E exp(lambda Y_b)≤exp(lambda²(2w_bU_b)²/8)。block独立给乘积界，Markov并优化lambda得单尾exp(−2r²/Σ(2w_bU_b)²)，双尾并合给上述区间。无需正态、对称或可交换假设，不对固定地图重采样来冒充泛化。

对theta_DE0用相同设计/权重/界构造其预定点估计与同水平CI。确认主结论只对应theta_DR；若另声称二者均正，仅在两个预定CI下端均>0且三臂评分可用时发布这个合取。原假设是至少一个分量≤0；合取拒绝是任一真实零假设分量的拒绝事件子集，故各分量有效水平不超过alpha即可使此合取错误率不超过alpha，臂间相关不破坏该逻辑。不能据此宣称两个CI同时95%覆盖或任选一个显著就成功，不更换主量为事后min或择优对照。

若固定合法机制下全部潜在分数有定义，则P(发布数值区间且未覆盖对应theta | X)≤alpha；缺失时整次该比较UNESTIMABLE保留此错误发布界。“可发布”可能依赖随机结果，不能再宣称条件于已发布自动95%覆盖；若潜在评分机制本身未定义，界也不可用。区间可能很宽，无权事后删图/改bound/增减重复/调保护参数取得显著。安全反例、停滞和E0负结果不能被主D/R的正估计抵销。

H19系统级次级族事前只含(D-S,H19E0)及(D-S,H19R-S)这两对，使用同一X、w_b、E_b、Qmax_b及独立block根。各配对差按上式构造点估计，将每个区间的错误概率取alpha/2，再与各自已知目标范围相交；并合界给该两区间同时覆盖的错误概率不超过alpha，不要求两对独立。它不声称与确认主CI或其它机制分析合并后仍同时95%覆盖。两对所需评分/来源域必须齐备，缺任一必需评分则整个该族UNESTIMABLE、域不合格则INFERENCE_UNAVAILABLE，不挑可发布或显著的一条作整体胜出。这个族是预定系统比较，未生成运行结果、样本数或参数。

## 13. 效果充分条件、失败见证及未运行机械合同

横向偏差的独立机制：取两条同时运动的平行名义轨迹，实体支撑半宽为r_i/r_j，名义间隔d满足r_i+r_j<d<r_i+r_j+rho_i+rho_j，两者误差向内且合法时可几何相交。名义参考时间可完全相同，调时间不能把横向位移重新解释成沿原线的位置；这是误差类型见证，不是说任何时间避让都不能消除碰撞。共享稳健底座必须对同扰动保护所有臂，不能仅让原生离散PIE在新增域碰撞然后宣布新法有效。此处都是符号关系，不为保护参数绑定数值或生成运行场景。

空间退休见证可以在资源瓦片与规划格一致时成立。考虑边长ell的格图，闭瓦片以格点为中心、边长ell；K位于半宽rho的世界盒且rho<ell/2。A原边u=(0,0)→v=(ell,0)，B原边w=(0,−ell)→u，C的原边和掩码远离二者。B完整掩码只在x∈[−ell/2,ell/2]的这一列，A在q>ell/2+rho且q<ell时后缀与该列全部瓦片分离，origin资源可在到终点前退休。闭边界等号仍不可退；initial resident分离、完整原边静态合法须成立。若用更粗资源或rho关系不成立，该充分见证失效，但不能据此证明全部S均无效。任何细化瓦片的替代都须计资源数/预处理成本，不暗中改变几何分辨率来造收益。

付费信息相对于仅凭命令/时钟预测的局部构造：令q_star=ell/2+rho，epsilon为事前已给的正精度；同一合法O常驱动段内，两世界从同一零速START、C=ell出发，eta分别为−delta/＋delta，a_-=a_launch、a_+=a_launch+2delta。在仍属LAUNCH时s_±(t)=a_±t²/2，切换满足t²=2a_lo·ell/[a_±(a_±+a_lo)]。定义L_t=2(q_star+epsilon)/a_+、U_s=2q_star/a_-、U_L=2a_lo·ell/[a_+(a_++a_lo)]；L_t<t²≤U_s且t²<U_L恰使慢世界未越q_star、快世界任何合格证书q≥s_+−epsilon>q_star，并且两者均未切换/END、q<ell。该时间集合非空当且仅当a_-·epsilon<2delta·q_star及q_star+epsilon<a_lo·ell/(a_lo+a_+)；充要性只针对这一两常加速度构造，后式隐含a_+<a_lo，不宣称任意既有物理/精度profile都满足，不临时调epsilon。cap后续安全仍由§3原证明承担，不另假设APPROACH始终有至少a_lo的实际减速度。

信息结论另带完整前提：若上述两世界直到相应信息截点的全部合法可见历史相同，则任何对全部相容世界成立的预测参考下界q_pred都≤s_-≤q_star；快世界一次合格POSITION可把可认证下界提高到q_star以上。这只证明该阈值的可认证性差，不否定其它合法几何/状态推断；K仅含于盒时q_star不是所有退休方法的必要阈值。相同命令不证明可见历史相同，仍须核合法字段、费用/计数、队列/发布时刻、分配/GC和反馈；只需这对世界的实际可见前缀相等，不人为禁止合法侧信息。真正采样仍发生于原付费CAPTURE，不能由中心任意指定t；合法供给能在该开区间完成捕获/交付及退休尚待联合证明。该构造经C33 Opus建设和根纠正，只补局部信息可能有用的条件，不推出购买的期望非负、D优于R/E0或固定E的净服务收益。

费用及真实服务见证还需要独立事件关系：A已合法在途、B唯一原请求因A旧origin资源阻塞，且B没有可通过§5检查的未授循环组（在途A不能作为初始resident组员），所以B仍只走普通整边初始准入；RR下一个对象为C而D唯一选A；没有其他外国holder或免费终点反馈可提前释放B。存在一条满足全部费用/容量/付费采样发布规则的有限公共轨迹，使D取得足够q、完成退休和B新授权验证，并在一个公共ACTUATOR机会成功START，时间上界f；RR和E0使B首次可能START的下界分别r_R/r_E，要求f<min(r_R,r_E)。下界须涵盖所有合法中途/终点释放通路，不能只比较两个不完整的下界。

若B各臂无后续中断，且相同初态与时间平移不变的合法控制/扰动使其参考运动同长tau_B，参考终点到达分别为D≤f+tau_B、对照≥min(r_R,r_E)+tau_B；一般不同段时长须分别证明f+tau_D_upper<r+tau_other_lower。再选定一条事前公共TASK_SERVICE行t*满足f+tau_B≤t*<min(r_R,r_E)+tau_B且t*<E；它不是观察后挑的cutoff。要得到真实服务还须：D在t*仍处该目标的reference terminal/resident并未Stop；B此时仍是同一有效未服务队首、未重分配；其真实实体满足§8唯一SERVICE_TRUE全形体谓词。一个足够的几何条件是目标参考点v加K完全包含于ServiceRegion(B)，如此任意允许z都满足X⊆ServiceRegion(B)。对照未到参考终点排除其服务，还须确认同一任务实例未曾由该对照的其他合法匹配终点驻留服务，不能仅用本次到达下界排除过去服务。中心型、沿途型或额外真实停稳型服务均不是本稿主服务定义；如改用它们须重写该见证和公共任务合同，不在实例绑定或看到结果后择用。

从B的单次事件到总Q另需完整计数前提：截至t*前B在D/两对照均未计数、对照截至t*仍不具服务资格，所有B之外服务事件的总计数在D不小于相应对照（可用相同实体轨迹/同队列/同Stop及同服务序列的受限见证充分保证）。此时Q_D(t*)≥Q_R(t*)+1及Q_D(t*)≥Q_E0(t*)+1。只证明B早一次而没有补集计数条件时，只能声称B的局部机制。上述充分条件并不声称实际D必然保持其他机器人的服务数；共同参考轨迹也只有在实际误差/任务与Stop条件相同后才能推出共同服务。

局部增量不能推出全固定E正差。纸面反例：预定t_1<t_2<t_3<E，D在t_1、R在t_2完成同B，随后共同C/共同行程tau；D多支付等待c，满足t_2+tau≤t_3<t_1+c+tau。若此前C无其他合法服务、t_3之后至E无其他服务行，早期D多一次，t_2追平，t_3时R完成C而D不能，固定E为Q_D=1、Q_R=2。这里c>t_2−t_1，规则/窗口均先定；这只是符号反例，无实验参数绑定或载荷。主HYP-NET必须用全roster固定E端到端比较检验，不能只保留早期见证或删除后来追平的行。

本轮补充该机制原动作的条件性固定源证据，仍无公开主roster实例或运行输出。取§13已有A/B/C角色，图邻接满足N(w)={u}、N(u)={w,v}，A的首目标v、B的首目标u；由v之后的连通通路接到远处C的叶起点/唯一邻目标，其余起点对若存在也与前三顶点及彼此候选分离。保留§9.3正常首次纯LACAM、精确距离、表示/对象/目标/时钟条件和§9已登记的puller自身行/交换循环外层距离更新，不改PIBT算法。B在源实际float运算和存储之后的根优先级须严格大于其余agent，不能仅由整数ID最大推出。它使第一次低层展开选degree-1的B，原shuffle仍只有两项且当前深度零无额外约束。唯一端点复用g_B=s_A=u，不能沿用§9.3全部2n_f端点互异；本A/B/C族有至少2n_f−1个不同端点，因此仍有V_comp−1≥2n_f−2≥n_f个合格候选，prepareDummy足量。

根直接核固定planner.cpp L393–568：B的唯一最佳候选是u，首次is_swap_required(B,A,w,u)在u扫描排除w，只剩空v；顶点对推进到(u,v)后，pusher目标u的距离关系由0<1变成1<0，循环终止，puller目标v的最终关系也为1<0，返回false并短路is_swap_possible。B先预留u，再唯一一次优先级继承调用A。A的最佳候选v为空；其clear-operation看见仍在w的B，会再调is_swap_required(B,A,u,v)，此时首个1<0已为假，最终puller比较仍假，不反转候选。A预留v并成功返回，后继主优先级循环跳过已经分配的A，远处C及其余叶各选空目标。两次帮助函数仅读各自合法首目标，得到A:u→v、B:w→u、C:s_C→g_C；这是following而不是同层vertex或对向swap冲突。已修目标位使下一DFS命中全目标并返回[S,G]；原目标各异，路径表和原commit切分/外层完整验证条件成立。

这个子族与全叶族的实际费用不同：PIBT仍各agent一次，但有一层继承调用；随机float调用为n_f+1，加一次两项shuffle的MT取数；两次is_swap_required共有一次循环、两邻扫描和十二次距离表查询，四次目标解析及所有分支照计，is_swap_possible未调用。A的候选sort长度三，其余长度二；两HNode、四LNode及原n_f·k_commit提交项的界保留。该证据只关闭三条机制原MOVE的一个源码可产生分支；还须证明A在途、RR下个选C、D唯一选A、真实费用允许的启动差、所有对照释放通路下界以及总Q补集条件，不能把§9.3整边M0互不相交的服务族搬过来——本机制正需B的M0与A的origin重叠。未生成运行结果或声称主总体theta正，预注册全来源仍保留无中途clearance、RR恰先选关键者、D反复查询失联holder、几何表低复用、中心队列拥塞、终点足够便宜等零/负效应。

活性反例必须正面保留：在走廊/tree缺少绕行时，互相占着下一原边需要的resident可形成等待；交叉口/环路上的多agent原MOVE可能各需其他agent的起点资源。WHOLE_EDGE的整M0准入不能自动完成同步环轮转；主GROUP_PREFIX只在§15明示条件下推进，粗瓦片/不合格组/无证据与长期围栏仍可能停滞。全原MOVE合法不推出本连续保守wrapper有执行解。不同阻塞图component因新请求合并，仍用同一全球资源key与中心owner，不分发新authority、不让相同资源获得两owner；对独立未准入fleet的合并必须重新满足INIT/授权合同。无活性保证的失败不通过排除动态样本掩盖，也不以全HOLD安全冒称实现了lifelong效益。

仅对WHOLE_EDGE参照的封闭循环充分负例可直接证明：取一组尚未启动且原occurrence不变的请求，每个目标顶点为组内下一agent当前resident。其M0包含该外国resident的非空终点mask，而每个resident只有自己的合法运动/交接才可能腾空；故组内没有第一个grant、正进度或原点退休。查询未启动者、未消费槽的HOLD与增大包络不能在这个封闭状态产生突破。这只是组内阻塞的充分条件，不是“存在环 iff 全队不启动”；环外可继续，无环亦可能因故障/容量不足停滞。

不能用部分预留自动修复：在当前同尺度闭瓦片、边向支撑恰为±rho且rho>0时，停在不碰终点瓦片的参考位置需s+rho<ell/2；让后继安全取得旧origin瓦片则需已证q−rho>ell/2，同时q≤s，三式不可能同真。若终点争用资源还必须等下一agent完成终点READY才移交，分段启动后仍可全部卡在终点等待环。这个推导只否定上述同尺度分段方案；主GROUP_PREFIX已显式登记更一般有限资源和§15细瓦片充分条件及成本，但不保证主实例满足。联合占用/相对进度控制未采用，不能借同步动画豁免异步证明。

同一循环也不必意味着真正连续运动无解：对正方形环的各原边，令同一进度alpha(t)从0到1，参考中心分别为(alpha ell,0)、(ell,alpha ell)、((1−alpha)ell,ell)、(0,(1−alpha)ell)。若各实体相对参考包络K为世界闭盒、半宽rho且4rho<ell，则任意相邻中心的一个坐标差至少ell/2>2rho，对角中心至少一个坐标差为ell，故所有同时刻包络互不相交。这是几何可行性的符号见证，不是已实现公共启动器或加入实验规模赋值。独立no-start/任意异步进度破坏共同alpha，因而不能把该路径当当前故障域的安全执行证据；后继若采用联合运动，须证明包含启动/制动和付费滞后信息的可达集合，而不能仅展示同步动画。

下表是纸面故障与检查覆盖合同，全部**NOT_IMPLEMENTED / NOT_RUN**，不是生成或执行测试。每项未来必须给条件、付费事件顺序、预期不变量/分类及最小失败前缀；未满足输入条件返回INAPPLICABLE/UNKNOWN而非PASS。

| ID | 触发与必须核验的结论 |
|---|---|
| W01 | 一次原MOVE：PRECHECK原slot、完整中心grant在实际START前；途中q退休、终点改resident后READY；消费恰一次 |
| W02 | 普通错pose/过早COMPLETE/未来时标：不更新可信q/c/K_task/资源或真实Q；错误未触发查询仍保守 |
| W03 | 同tid新样本先到、旧样本后到；分别检查单样本下界、融合最大值和退休提交R；只要求R之后覆盖，不回溯到旧t_j，不跨tid/几何代 |
| W04 | 前缀a≤b入口含等号、d<q退出必须严格；有限多分量/未证数值不能误删；整边才可只看lambda |
| W05 | 参考s单调而真实z回摆：旧后缀仍覆盖；不从实体非单调错误推出可回收终点 |
| W06 | 已授未START/no-start/重复累计grant：保持U(0,b)责任及C≤b，不重置s或由cap自动启动 |
| W07 | BRAKE域及LAUNCH/APPROACH到已安装C的有限界；中点HOLD不END，增cap非零速重入仍在制动锥 |
| W08 | RESUME早于BRAKE结束、HOLD无限：等待合法恢复，不换边，有限P1不冒称有限等待 |
| W09 | P5同点零参考速拼接：真实z不清零；起点错位/Z缩小/F旋转/非零速是明示必要前提见证 |
| W10 | CANCEL先于首次REQUEST：合法未见e吸收性关闭，迟到首次拒绝，不出现新grant |
| W11 | GRANT先于CANCEL：取消返回DENIED_GRANT_LIVE；不发成功CLOSED，不按超时回收 |
| W12 | 中心私有作业未发布时故障：无半grant/半释放，已付费用保留；后继job不能先读旧版 |
| W13 | 终点gate latch/活动NONE而中心未知：旧端点覆盖继续，匹配lastClosed可查；NONE不当清空 |
| W14 | READY/终点ACK丢失、旧ENTRY迟到：保留或取同一收据，不重复服务/消费、不删新tag |
| W15 | 已退休旧资源授给新holder后到达旧release：expected-holder/tid不符拒绝，不删新owner |
| W16 | 同agent其他tag不可吞并；parent E到初始正cap集合转换无空隙，组gamma_prime接续不误当外国责任 |
| W17 | 中心partition/fail-stop、无界延迟：无新中心发布，旧运动按合法模式继续，资源不消失；不假drain |
| W18 | LOCAL CLOCK skew与消息重放：标签不授租约/清空权，权威事件序与原chrono/CPU域分离 |
| W19 | ACTIVE→SHARED-OFF→DRAIN→恢复：停止新查询/新承诺的范围明确，resident保留，旧START不复活 |
| W20 | NATIVE-COLD-OFF：共享side effects为零的原样旁路合同；不把共享OFF称bitwise原法 |
| W21 | RR稳定agent初态/成员动作更替/空集/失败：绑定冻结的唯一完整tid，请求发布与last_agent原子更新，采样失败不回退，不看真实s |
| W22 | D分数同p多资源、tie、无正分：去重、最早贡献p再tid、回退RR；全扫描/索引维护计费 |
| W23 | QUERY选择尚未完成：没有可见POSITION；不能免费读全局再事后补费用 |
| W24 | CURSOR在pure WAIT前后CAPTURE：所见c按唯一采样点区分，后送达不刷新；POSITION不代cursor |
| W25 | CAPTURE自身不足全费则未采样；已捕获后本行动态guard耗尽只保费用，不发表/不消费水位，后继原行重捕获；历史证书计算保原不可变payload，完成/交付不刷新真值 |
| W26 | 原WAIT/HOLD/MOVE槽：起始slot k、目标k+1、READY前不消费，初始驻留可合法服务 |
| W27 | 真实greedy任务次序与滞后快照：不虚拟抢未分配目标，不拼修订，不按查询归因筛Q |
| W28 | planner期间c推进/目标改变/过期CAS：拒绝陈旧外部结果但保留正常源结束节点与费用；后继只从已接纳Π重新冻结，中心终态交接前不得启动下一job |
| W29 | P_model的chrono含虚拟暂停/排队，CPU日志编码只累已执行模型工作；真实host耗时不进源输入/Q；变长操作与imports全计费，保留源预算/比较语义且不烧掉未用供给 |
| W30 | 空目标/非法路径/源_exit/随机比较器域：入口NO_INPUT与安装后失败分开；PRE_COMMIT_SHAPE先于危险commit，不补动作；不合格会话停止且不重播，不杀评价器或把源缺陷计优势 |
| W31 | MCP的TIP仓库仿真实现末端nextNode越界与guarded定义域：原问题保留，守卫不越界；完整no-following不适用全列，不能归为Causal-PIBT方法 |
| W32 | 无对应本臂消息/有限copy/同t多行：NO_REPLAY_TARGET，严格后继发布，无跨臂payload或零时无限级联 |
| W33 | 静态WORLD非法、HOST未发起/缺日志、WORLD合法而软件INIT未完、合法全HOLD/零前缀Stop分别判断；软件INIT标签不直接决定Q，完整物理服务前缀才可评分 |
| W34 | cutoff穿过物理段、先真实服务后送证书：精确截断，不补末后服务；完整先前真实服务仍计 |
| W35 | 数值不能认证或评分日志缺失：UNKNOWN/UNESTIMABLE；空合法前缀暴露为0不自动SAFE |
| W36 | 同目标不同实例/同实例重复：分别可服务和幂等；Q≤预先公共TASK_SERVICE对数 |
| W37 | G/N同输入精确集合及不同处理时刻：语义相等不强迫闭环同迹；E0不付无用途阈值费 |
| W38 | D胜R但不胜E0/无服务跨越：只保留限定增量，不宣称整体观测划算或用局部见证外推规模 |
| W39 | 空必需类/动态删样/改权重/跨block随机或模型状态共享/host分支泄漏/按发布挑结果：禁止对应固定总体区间或明确不可估；只在完整F(X,Z)及独立根前提下用P_model区间 |
| W40 | 走廊/tree、交叉口循环、饥饿、component合并：覆盖不等于活性，失败进入全roster，不私添绕行 |
| W41 | 可信Byzantine/实际控制或几何界外：MODEL_BREACH并保留碰撞；界内反例不得重新归入界外免责 |

未来机械接口：VerifyManifest检查固定来源/字段/alias/适用性、未改原参数意义、有限O/费用/精度/独立根/权重，返回VALID/UNINSTANTIATED/INVALID及证据；CheckProposal将每个原MOVE/WAIT、slot/c及append对应回固定源job/输入/输出版本；FoldLedger按付费发布全序重放owner、watermark、PRECHECK、grant、closed、READY、CANCEL及模式，失败给最小行前缀；CheckGeometryAndControl以精确或保守区间检查整个连续段及P1–P6条件，不能决定则UNKNOWN，不以端点采样代替扫掠；CheckEventsAndCosts验证每种机会、实际作业/采样/发布/attempt/copy/clock/RNG与所有队列/失败费用；ClassifyAndScore按§12给全部类/flags、安全域、Q/暴露/E和缺失理由；Estimate按固定比较所需臂/范围输出估计/区间或明确不可实例化/不可估/域无效。

另有NativeIdentity合同：固定源码与编译/依赖/原输入/时钟随机环境，比较冷旁路与直接原入口的用户可见输出及原状态副作用身份，不借新共享初始化改变原随机消费；实际并发/时钟环境无法固定时不得声称bitwise等价。TriggeredRefinement合同检查公开触发/已知前缀决定模式、动作仍只原MOVE、保护未触发时资源责任不断、切换/取消/退休全合法。两项当前未实现未运行，与共用物理adapter和原生域的边界必须同报。

所有未来检查绑定被检程序/依赖/输入/科学规格版本、覆盖域及原始输出。即使某checker全绿，若漏W01–99、仅逐帧看图或把自写期望复述一遍，不构成验收。现在不创建测试、运行模拟器或读取受限载荷给这些合同补假回执。

新增纸面合同同样NOT_IMPLEMENTED/NOT_RUN：W42，END/FINISHED后READY未消费，旧Kc再次提原u→v必须因pending/未END/原起点至少一项拒绝；W43，后继PRECHECK成功后旧READY重复不改c/parent/相关版本；W44，LOCAL_POLICY逐个纯WAIT消费而中心Kc滞后，不靠本地分支免费派SOURCE_REQUEST机会；W45，参考到达但实体不满足服务域，不能计真实B；W46，局部B领先而补集计数变差或固定E追平/反超，不能套总Q充分条件；W47，Srv_C持槽等待远端回复的错误安排应违反服务合同，正确异步消息流各自释放槽且所有传输/接收付费；W48，WORLD物理初态、算法INIT状态、HOST日志可得性分别按下述新初始化合同判定，禁止将软件INIT标签直接变成零分或丢行。

新增W49–54亦仅为NOT_IMPLEMENTED/NOT_RUN纸面条件：W49，END先于待发布本地作业时，其全部字段写入保持且旧快照发布受phase/g_i fence拒绝；W50，首推与poll先后互换或旧负回复迟到时，仅一个不可变正缓存、不产生新采样点；W51，中心READY发布/首次发送之间失联，缓存恢复不重复退休；W52，两个终点retry只消费各自既有站容量，空检查与重复字节也收费，不发生免费动态END采样；W53，消费清pending后被pin历史仍可用，中心只有已付消费证据及引用消失才GC；W54，中点cap HOLD/安装ACK不产生END事实或q，已END后旧cap/RUN不能复活原边。

W55–58同为NOT_IMPLEMENTED/NOT_RUN：W55，正常源返回后中心STALE不退随机/缓存节点，外部Π不变；W56，输入安装后部分失败或形状拒绝使来源会话停止，费用/真实服务前缀仍保留；W57，结果待处置期间不提前复用Srv_P或把内部future_paths送入PROJECT；W58，相同后继输入而不同拒收历史不强求同提议，AA与accepted-only效应/费用不混报。这里只登记未来核验条件，不生成或运行研究测试。

W59–67均仅为NOT_IMPLEMENTED/NOT_RUN纸面合同：W59，q_release/C/b独立、初始新累计包越过丢失小包、cap到达/安装同刻及旧无作用RUN副本不能复活；W60，区间计数入口/退出事件与N-GEOM精确等价，非凸资源可先退后再申请；W61，GROUP_ADMIT先验A/B分离、完整F_G无外国责任与全部原子提交，失败无半组；W62，所有新增owner路径检查围栏，endpoint接续允许而下一原MOVE等退栏；W63，UNGRANTED到唯一CAP_EXTEND的同提交替换、首次行/tie与FENCE_BLOCKED排除；W64，modulo 3、COORDINATE的内部组角色及GROUP_RETIRE一token一职、同站FIFO、无真进度触发额外供给；W65，T后实际采样/完整终点链与有限日历反例，不把一次有效清除说成一次查询；W66，全部中心FINISHED后付费GROUP_RETIRE，长期失联/退栏等待和组历史GC照计；W67，F_cap/E0同cap能力且q_release=0，不用q_evidence清栏、旧整边F与新因子不混报。

W68–70均为NOT_IMPLEMENTED/NOT_RUN纸面合同：W68，旧原tid经MODE推进代际并真正END后，新tid首次授权获得严格后继代际，旧tid/旧尝试不能抬高新活动水位；W69，新STOP仅在Srv_E验证而未ACTUATOR时不提前覆盖旧RUN，实际处理、同代际去重、缺grant限定拒绝和队列写入遵守唯一全序，未作用尝试不因以后cap安装而复活；W70，DRAIN禁止已有UNGRANTED请求首次正cap，E0的QUERY_ON恢复ACTIVE但仍无POSITION，WHOLE_EDGE本地C等真实安装而非中心准入时预置。它们登记可区分的行为，不是已运行测试或资格回执。

W71–78均为NOT_IMPLEMENTED/NOT_RUN纸面合同：W71，共同PLAN_CHECK、COORDINATE固定角色映射及H19无组费用，不以私有需求新增机会；W72，批单元后继付全费才追加/发独立APPEND，前条发布后才继续，部分失败保留前缀且GROUP_ADMIT不拆；W73，固定F0的Type-2、初始无Type-1合法锚与各链最长前缀，入队/安装不能冒finished；W74，APPEND乱序/重放/前缀GC不跳槽，f_inst/f_cons/Kc严格区分，FINISHED不消费；W75，封存尾界不随新增尾延伸、cap/APPEND持久交替和发送提交水位，有限供给仍可有负净收益；W76，h只取中心已终态attempt、零名义WAIT仍需消费，空闲agent不反复触发，失败需求只在后继公共机会重试；W77，历史cut已承诺staged不撤回，cut外私有历史不复活，新图无new→old而仍完整付费核合图；W78，批占槽期间排队MODE不偷生效、外生fail-stop及时禁止新发布、旧承诺/物理责任保留，外部两个固定比较均报且不因缺失换主量。这些只登记未来可区别的行为，没有实例/事件载荷或已运行检查。

W79–80均为NOT_IMPLEMENTED/NOT_RUN纸面合同：W79，源首次while之前截止且H_goal空时，首次解引用被限定守卫挡住，原已构造对象收费清理/空返回后本次形状拒绝即会话停止，不进commit/自动重试；W80，受限纯来源跨正常AA软拒收只走既定分支，常驻SIPP和临时验证A*保持空，诊断不得新增搜索入口，实际空对象/守卫成本保留而未发生Compare不虚收。这两项不替全部目标索引、所有权/库/后端继续域证明。

W81–82均为NOT_IMPLEMENTED/NOT_RUN纸面合同：W81，冻结目标队列空时在源安装/实例front之前停止，单已知目标的0/1引导不读第二项、不造任务，真实第二项存在则保其引导，标志/对象失效不能归普通观测失败；W82，swap两侧各取自身引导，推进顶点对后四个外层距离同步更新，有限固定表下严格下降论证与全部费用保留，局部循环终止不冒充整个源资格或算法完备。这些没有生成可运行测试、地图或事件载荷。

W83–85均为NOT_IMPLEMENTED/NOT_RUN纸面合同：W83，有限外包端点与实际宽度判定给采样点q下界，wire方向和跨tid/旧样本语义不丢失；W84，authority只遍历因果前缀且把已发生eta来源能力明列，全部数值/存储/失败和占槽成本保留、E0无查询专用虚费；W85，旧cap到达/安装的同刻与严格早于不能被数值近似混同，物理顺序未认证不作普通无响应，只有已认证世界内的观测未完成才保其真实评分。它们是接口义务而非已运行或已获后端资格。

W86–88均为NOT_IMPLEMENTED/NOT_RUN纸面合同：W86，首达目标后的同一F_new供查找/创建/索引，真实键等价与hash一致，新代表不覆盖旧key；W87，已pop L、部分构造/发布及截止分支均有唯一归属，先停止借用再完整收费清理，重复OPEN不重复释放；W88，正常AA软拒收不保留局部泄漏，清理未完成不授热继续资格，修复身份不把历史代表去重宣称完整状态等价。仅登记可区分行为，无实现、运行或资格回执。

W89为NOT_IMPLEMENTED/NOT_RUN纸面合同：唯一直接建立图及Planner，回溯/标量封存时借用均有活拥有者，正常输出不逃逸Vertex；C++14可选拷贝消除、晚到形状验证或fail-stop名称均不能替代入口/生命周期资格，未闭构造异常/索引域不填通过。

W90为NOT_IMPLEMENTED/NOT_RUN纸面合同：Graph部分构造的顶点在移交前后均有唯一拥有者，V/U/neighbor只借用，发布失败/外层实例构造异常不遗失或重复释放；新拥有者与原V裸delete不得并存，普通异常归属不代替全部输入/退出资格。

W91–93均为NOT_IMPLEMENTED/NOT_RUN纸面合同：W91，noisy代数子族保留eta/原命令范围，A=0及非零速入口统一处理，实际旧cap同刻HOLD/原END和较早安装严格判序，不把结构关系冒作整个原参数域或硬件资格；W92，cap后继发布和ACTUATOR实际接纳各付当前根核定，容量不足无效果/不消费未处理尝试，实际no-start照原水位处理且不重抽，早快照不产生虚构位移；W93，真实空间驱动历史指数和在固定合法驻留行作全实体闭包含判定，零边界与未认证不同，w/z不归零、不改名延迟，有限数学终止不冒作计量通过或实际Q。

W94–96均为NOT_IMPLEMENTED/NOT_RUN纸面合同：W94，同一前修订判全部原队首、全行服务后补给，新任务不同行服务，A/服务/修订一次完整发表，早晚CAPTURE不见半行；W95，任务真值宿主求值取消模拟内任务CPU行配额耦合、设施机会及原在线/控制供给保留，逐臂实际费用不强制相同且业务工作不搬入世界；W96，未认证任务事务保留评分未知，不造物理Stop/零尾部/后移服务，闭边界真零及已知中点不服务不被误作数值失败。

W97–99均为NOT_IMPLEMENTED/NOT_RUN纸面合同：W97，当前段与采样点、历史索引及传递依赖一起付费冻结，CAPTURE前合法cap/eta计入、之后END不刷新，不调用后继当前时钟或可变系数；W98，已付精确控制状态允许局部复用，未物化采样值仍收费，查询诱发保留/复制不搬入世界，未发生全史重算不虚收，不跨反事实臂共享；W99，原动作序号更替不让同agent插到循环序的新位置，纯R对持续Active原tid有条件选择次数界，完整tid/唯一请求槽与last_agent同发布，D混合及到达/真实Q不继承该界。

## 14. 继承异议、证据范围与最终验收要求

论文论证只围绕以下既有主张组织；本表是C27建设建议经根纠正后的压缩索引，不增加实验臂、改变§12推断或提供已获结果。安全条件、局部机制、主总体收益与外部系统效果分别承担自己的证据责任。

| 待检验主张 | 所需证据与原比较 | 不支持时的解释边界 |
|---|---|---|
| 已付可信空间证据可安全改变仍在执行的原MOVE资源责任 | P1–P6的条件证明，以及满足全部前提时的安全反例检查 | 一例满足前提的碰撞即可否定相应安全保证；全HOLD安全不证明方法有用 |
| 定向分配查询能提高净真实服务率 | NATURAL中固定权重的D-S−R-S，逐块除原E；费用通过原供给和等待影响Q，不再从Q重复扣一次 | 主区间不支持正效应时不宣称定向策略有效；不显著不等于等效，也不证明效应为零 |
| 途中观测值得购买且值得定向分配 | 前项及必报D-S−E0均支持正效应，按§12原合取规则 | 只胜R不胜E0，仅支持限定购买制度内的选择收益；查询/排队开销可以吞掉提前退休的局部收益 |
| 具名系统在共同世界和供给下有竞争力 | D-S对H19E0、H19R-S两项预定系统比较完整同报 | 不归因为单一D分数；外部来源不合格或必需评分缺失时按原不可推断/不可估处理，不换弱对照 |
| 局部推进机制解释上述效应 | 已列S/F_cap、G/N及前缀/整边的限定机制比较与付费事件关系 | 局部早释放不推出窗口总Q增加；不扩大完整矩阵来寻找显著结果，不把机制名称重复认领为原创 |

主论文结果必须允许净效应为零或负、固定域失败和不可估；负结果的可发表性取决于证据与知识增量，不能由预先包装保证。真实宿主CPU/elapsed/内存另报，不能用模拟基本步排名声称实机速度排名。

71R4六个主题逐项承接：T1迟到首次请求/关闭竞态对应§5的UNSEEN取消和已授拒绝；T2 RR全集/初态对应§7；T3源时钟/暂停/原预算对应§9；T4采样线性化对应§6/9；T5可信逻辑cursor与pure WAIT公平对应§6/8/10；T6 INIT与首次MOVE评分对应§12。它们是新候选提出的关闭证据，不回改71的十条原意见、69的九条或任何审稿票，不能以删去一种协议的名称代替其安全责任。

完整方案对早期交接要求的对应也必须核：实际空间误差而非delay改名（§1/3/13）；保留PIE原提议与可证制动/HOLD（§3/5/7/8）；唯一authority、资源ID/epoch/fencing/幂等与origin释放/destination接入/edge-in-progress（§4–6）；lost ACK、分区、无界延迟、clock skew、走廊/tree/交叉口/饥饿/component merge（§9/12/13）；原样与共享适配、inactive与triggered机械合同（§7/10/13）；纯仿真全成本/主次比较、公共源、独立配对、失败分母/缺失/删失/固定目标推断（§9/11/12）；全部来源阅读强度与近邻（§2/10）。静态几何mask同时覆盖顶点、同向/反向边扫掠及实体起终点；若某未来adapter只检vertex/swap而忽略连续mask，不能继承P3。

建设咨询的原始意见、阅读范围与根取舍由73A3索引，不计正式通过票。创新边界沿§2与本节主张表：共同反馈隔离、几何阈值、冲突计数、事务或前缀名称不能各自认领原创，当前也无组合首创或规模正效应的已获证据。

六门含义维持：G1实际误差问题；G2已发表锚点与诚实路线比较；G3固定R0/适配/原样合同；G4已发表外部基线与适用域；G5公开来源和场景协议；G6物理/算法/资源/费用/评价公平闭环。最新有效根裁决是72R4的2 PASS/3 UNKNOWN/1 FAIL；本73草稿不自授资格。S1前向证据、S2终点/权限、S3真实服务、S4WORLD/软件INIT/总体、S5服务拓扑在本稿提出实质修订，均须新字节核对和顺序审查。S6源定义域、S7素材来源/合法source、S8主lifelong外部比较、S9规模/可证伪范围仍有明确待补证据；不能由章节齐全判闭。

最终完成性审计逐项指向实际证据：交接文件与全部任务真实状态/身份；至少十二项相关一手来源及四份期刊全文的真实阅读、其他来源缺口和差异矩阵；原源码接口/许可/原法检查合同及外部公平域；P1–P6与所有资源/事件/模式/失败总函数；全roster与各比较/评分/区间的适用性；W01–99及所有未运行机械合同；本新字节完整固定后的科研导师skill→Nature reviewer skill→完全不使用任何skill且不读他路意见的独立逻辑→根逐条验收；每份必要skill意见后根另做不用skill的直接分析；私有GitHub精确同步和全历史冻结/只读/保护边界。阅读缺失、报告无效、间接一致或仍UNKNOWN均不能计完成。

H、T_delay、B_CAL、B_max、B*、P_active、density N原义保留未赋值；只进行来源阅读与文档构造，未实现、构建、创建或运行测试、仿真、调参、生成seed/tape/实验载荷/结果或实车动作。旧35–38及受限载荷禁读，桌面旧备份只读、用户明确授权的新阅读包可按任务更新；69–72及其报告不改不封存。本稿尚未固定或送审，所有来源/协议/资格及顺序审查闭合前保持HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。实验前目标未完成，不以版本/篇幅或审查次数宣布完成。

## 15. 前缀平台的条件进展、反例与增量边界

本轮已把73M1/P1/P2/P4及根P8的可用规则整入§3–7/9；主工作选择GROUP_PREFIX，不再把它仅放在附加备选中。P3说明任意贪心初始cap可锁死原本可行次序，所以这里只允许完整普通准入或通过A/B分离证明的初始组准入。P9实际审的是旧P8字节，已由根复算修补；它不是当前整合73的正式审查。几何、权限、付费进展和最终真实Q仍是四层不同结论。

一个组选择可发现的充分见证来自P5/P6：四条顺时针正方形四邻接单步原MOVE，边长ell，K=[-rho,rho]²，事前固定边长h的轴对齐闭方瓦片覆盖完整原包络，r_geo=2rho+h。令A=r_geo+epsilon_obs、B=ell-r_geo；若各边CAND在(A,B)有点，初始c_i满足A<c_i<B且l_i=max(0,c_i-epsilon_obs)>r_geo。初始包络相邻投影间隙至少ell-c_max-2rho>h，未来包络相邻间隙至少l_min-2rho>h，相对边由ell>2rho+h分离，因此各A_i两两不交、各B_i两两不交；闭边界含接触，所以需要严格大于h。不要求机器人同时START或相同进度。

有限CAND存在点的一个充分条件为ell>4rho+3h+epsilon_obs。取A+h<s<B；覆盖有向前沿点u+(s+rho)e的某闭方瓦片，其沿e投影下端m给真实进入阈值a=m-e·u-rho∈[s-h,s]⊂(A,B)，横向也相交，因此a是未被0截断的I_r入口并属于CAND。无需共同晶格/等差阈值。取各d_i=min(CAND_i∩(A,B))、d_max=max_i d_i，alpha=d_max/ell是Theta成员，所得d_i≤c_i(alpha)≤d_max，均在(A,B)；所以§5有限共享阈值族确实会找到合格向量，只要该闭合请求组由当前循环分量定位且无外国owner/围栏/障碍。该推导不证明非等长一般完备，也没有证明固定PIE一定输出这组原MOVE。

一般组进展命题仅用于S制度的实际q_release。条件是组已合法准入、F_G完整排除外国新增占有、没有组外的额外正分竞争，模式允许必要查询/扩展；每成员初始累计grant、必要RUN与最后不中断控制能在某有限时刻使s≥c_i或真正END。令T为这些时刻最大值，它只是分析中的轨迹时刻，不是中心免费信号或实验参数。还必须有T后实际POSITION CAPTURE及付费完整交付/q_release提交，或物理END至中心FINISHED的完整终点链；失效、NO_MATCH、早采样晚交付和无进度重复均不能冒充这条后继链。扩展可授之后亦需实际维护、发送/安装、必要RUN、控制与终点服务。有限O没有剩余机会时不补行，不从“消息最终返回”推出新鲜采样必然发生。

对当前成员j的完整扩展需求D_j=Mask(U_j(q_release,j,ell_j))，若外国成员i持有冲突资源r，则r不在j已拥有S_j；又b_j≥c_j≥l_j，故r∈D_j减S_j⊆B_j。若i已清，即q_release,i≥l_i或中心FINISHED，其当前持有只在B_i；最终endpoint亦在B_i。由B_i与B_j不交，阻塞只能来自未清旧前缀且中心仍Active的非endpoint资源，§7排除endpoint不会漏掉这类组内阻塞。物理END但中心未知者仍未清；合法gamma_prime接续不制造外国插入。

已清集合单调增加。有相关正分时纯D选中尚未清holder；T后真实采样精度给q_sample≥s-epsilon_i≥c_i-epsilon_i，经非负裁剪和付费提交使它已清，或完整终点链先使其FINISHED。若其他在途证据先清，同一次既成清除只算一次；后来重复不再增加集合。至多每成员一次有效清除，不代表一次采样/一次尝试/固定费用。没有正分且非owner条件均合格时，上述引理排除外国阻塞，后继普通扩展可到ell并完成。早扩展新增集合只在B_i，故不破坏这一归纳；已完成成员终点也不挡别人的B_j。对一般跨组竞争，纯D没有由此得到公平性或全局无死锁。

纯R对持续Active成员有§7的成功选择次数界；配合上述T后实际新鲜采样和完整交付条件，也能取得必要证据，所以上述进展不推出D胜R。E0/F_cap直到原END保留q_release=0及旧起点Mask；在P5环若有第一个b=ell授权，此前不可能已原END，而该完整授权必含后继尚持有的起点Mask，与唯一owner矛盾。因此同cap/维护能力仍不能完成第一个原MOVE，不是因E0被删了扩展机会。这个否定只适用于该固定路径/资源制度，不能外推给允许联合占用、不同途中证据或改路的外部方法。

本四机器人同步顺时针单步环包含cycle conflict，位于WinkTPG的II-A与VI明示输入假设之外；只能承担本资源制度的条件机制见证，不能用它判WinkTPG失败或宣称胜过该方法。系统优劣比较必须另有共同适用域及可比费用/目标；本边界说明不扩展主确认矩阵，也不为外部方法补造其未承诺的能力。

从有限到原END到真实服务仍须原任务在预定TASK_SERVICE行有效未服务、尚未Stop、合法原终点驻留、整个X包含ServiceRegion；没有任意预定E内完成保证，也不能免费重复多轮lifelong。主roster是否满足几何/服务条件、固定PIE原输出及精度来源尚未核定，不生成实例见证或声称实际净收益。只含真值而总给[0,ell]的服务不能用于组发现证明；精度不合格须NO_CERTIFIED_GROUP而非暗补即时真值。

保留四类直接负例：同规划格尺度粗瓦片的中点矛盾仍可使无合格组；异长/非对称可行cap不一定在Theta族内；永久no-start/失联/中心故障会长期锁住大F_G；若整边最初已可授，分组/建表/中点停车/重试和外部等待可使前缀净收益为负。退栏必须付费GROUP_RETIRE并等中心全组FINISHED，不能拿物理END或超时提前释放；新原MOVE的组屏障也会增加合法等待。所有失败进入固定roster和完整费用，不以全HOLD安全冒称实现效果。

整边WHOLE_EDGE作为预先登记机制参照保留：普通中心准入提交b=ell，本地C待合法grant实际安装后才为ell，丢包或尚未安装期间不得预置；没有部分cap/组围栏，按旧完整后缀退休和相同原END链。共同供给比较可将不使用的组/cap机会明确空闲；另报告它省去无用途组/候选/累计cap工作的自然经济版本及其固定机会合同，不能强迫整边跑无用代码来显得更慢。前缀与整边比较以相同D/R查询语义及固定世界/费用为条件性机制比较，主确认仍是GROUP_PREFIX内NATURAL的D-S减R-S及必报D-S减E0，不事后择平台或改主量。

新近方法已覆盖前缀释放和局部修复，前缀名称本身不构成创新。根保留实际付费证据如何改变不可撤授权、有限组选择的条件推进及包含失败围栏/查询开销后的净效应为待证增量；不保证它们已超出现有论文。C7R付费交替选择、L9单一剩余阻塞者及单调退栏建议仍是未采用的不同机制，需要分别给总规则/代价/反例，不能在本稿模糊组合。外部cut/批入队/恢复现已有§10明确纸面规则，但当前精度、源码/数值及服务后端、原样/适用域与完整资格仍未闭，必须在固定73之前继续处理，不能用本节长度或NONBALLOT数量放行。
