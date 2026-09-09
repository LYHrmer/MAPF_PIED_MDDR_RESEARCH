# 73：原边空间证据、终点交接与付费服务——实验前整合草稿

起稿2026-09-08，根局部修订2026-09-09；**DRAFT / NOT-FIXED / NOT-REVIEWED / NOT-ACCEPTED**。完整章节草稿供进一步构造核对，当前仍以整边准入执行模块为工作版本；同原MOVE前缀扩展在§15比较，尚未混入其保证。它不是已选定的唯一最终路线。72三路审查及72R4根综合已齐后才创建本实质新编号；69–72及其报告不改、不封存。本稿固定后仍须科研导师skill→Nature reviewer skill→无任何skill独立逻辑→根验收。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT；不自授新资格门。

## 1. 研究问题、主张和动作边界

真实机器人有尺寸及跟踪偏差；按名义格点判断通道清空可能不安全，而一直保留整段占用又会延迟后车。研究问题是：在保留 PIE-D 新 MOVE 提议来源时，付费取得可信参考进度、只释放已经证明不再需要的空间，能否在持续任务中取得正的净服务率增量。普通反馈误报/迟报、真实空间偏差和处理耗时分别建模，随机 no-start 不能改名为定位误差。

规划层为离散四邻接图，执行层保留连续实体足迹、连续参考运动和有界跟踪误差。方法不改变原边、目标或新 MOVE 顺序；只允许接受原 MOVE、合法 COMMITTED_WAIT、阻塞 HOLD、继续旧 tid 或在已证明可行域内制动/保持。没有主动绕行、补邻边、伪目标或在 unsafe proposal 上偷偷换轨。底层参考控制是假设明确的理想执行模型，不声称已经装进 LIMO。

主共享四臂为 D-S、R-S、D-F、R-F：D 为阻塞导向查询，R 为轮询；S 为途中后缀退休，F 为整段持有至终点交接。唯一确认主比较是 NATURAL 中 D-S−R-S 的固定总体真实服务率差；策略自己的查询/处理/维护工作计入，同费用函数及服务容量。STRICT 预付等容量的机制比较、退休因子及交互另列，不择显著者充当主结果。方向性假设 HYP-NET 为该差的期望正；零或负、队列成本吞掉收益、提前取得证据却没有真实服务增量都能推翻它。不是“只要安全就算有效”。

本候选保留的具体路线是受限平移模型下的原边安全接入、空间退休与付费观测调度，不改题目去声称已解决任意速度/姿态的窗口可达集合接入。主比较的R-S已使用同一固定裕量和合理的途中退休；F只是一种明确的保守释放因子，不能代表所有固定裕量方法。另设必报实用性对照E0：不主动购买途中POSITION，仅凭共同付费ENTRY/READY终点交接；不为E0构建无用途的阈值表。D胜R而输E0，只支持限定查询制度内的选择改进，不足以宣称途中主动观测整体划算。G/N几何实现比较另列，不扩充为事后可任选的确认主检验。

真实横向跟踪偏差和可信信息滞后为主机制；普通不可信反馈错误不改变共同安全权限，单列其负荷/压力效果，不认领为D独有鲁棒性。准确的采样内容仍可能付费且迟到；它不等于免费即时全状态。主设计不向任何臂赠送实际pose、逻辑cursor、任务账本或控制器状态。若未来改为免费全状态或一般集合接入，须重新定义主效应与协议，而不能用本D−R结果代替。

用户要求大规模 lifelong 仿真为主：必须考察持续任务吞吐、失败、处理/通信/内存及首次/复用成本，不能由局部清空例子外推规模收益。小场景用于解释机制和反例；两台已有 LIMO 仅可选有限现实证据。无硬件本身不否决纯仿真，但有界模型、可信接口、全成本与外部效度必须显式。未确认实车定位/控制配置，未开始实物、实现、构建、测试或仿真。

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
| Yan/Smith/Li，WinkTPG，[arXiv:2508.01495v2](https://arxiv.org/html/2508.01495v2)，2026-04-26 | 根定点读III–VI相关方法与结论、核版本；非全文逐式审计，HTML自述accepted不替正式期刊题录 | 给定路径速度优化、冲突依赖数选择、保留enqueued前缀及窗口重算已有近邻；其对象与本付费POSITION选择不同，不等于无重叠 |
| Okumura等，MAPF-X/Tree-LaCAM，npj Robotics4,20，2026-03-14，10.1038/s44182-026-00083-2；[官方正文](https://www.nature.com/articles/s44182-026-00083-2) | 根完整方法/讨论的指定窗口，补充材料未读 | 时空预测、不确定性、离散规划与MPC/CBF已结合；形式搜索完备性不等于真实系统无条件安全，整个替换改变本MOVE来源 |
| Cao，SCALE，[arXiv:2607.00591v2](https://arxiv.org/html/2607.00591v2)，2026-07-03 | 根核版本及III/IV相关窗口、非全文逐式/图表审计；按指定预印本记 | 已有扫掠占用、released前缀、未放行路径局部修复与接续，不能将冻结前缀/授权执行泛称空白；未搜到error不证明其无误差处理 |

选此组合的依据是实际空间包络与同原动作域可自给证明、净费用可以配对检验；不是因为71已经写了长稿。单中心是范围明确的替代，减少多owner的提交负担但引入中心队列瓶颈。异步轻量调度、局部复用和几何/控制方法继续作为机制比较对象；若需改路才能消环，就列独立规划算法域，不能潜入本wrapper。没有任何论文或当前见证保证本主总体正效应。近邻若证实已覆盖关键组合，须缩小主张、增加匹配对照或另编号换路线。

## 3. 物理域、可信条件与有限参考到达

参考边从u到v，ell=||v-u||>0，e=(v-u)/ell；本模型为固定世界朝向平移，F为非空紧足迹，Z为给定闭盒。实体 X(t)=u+s(t)e+z(t)+F；z_dot=-kappa z+w，kappa>0、|w_j|≤kappa zbar_j、|z_j(0)|≤zbar_j。变分公式 z_j(t)=exp(-kappa t)z_j(0)+integral exp(-kappa(t-a))w_j(a)da 给 |z_j(t)|≤zbar_j。因此实体速度可因 z_dot 回摆，参考 s 单调不代表真实位置单调。普通 y/COMPLETE/pose 可有错误、缺失、迟到和重放，但不驱动可信控制状态或授权退休。

参考状态 s_dot=v_ref≥0、v_ref_dot=a_cmd+eta，|eta|≤delta。选符号常数 0<delta<a_lo<a_hi 与正 launch 下界 a_launch，执行器允许下面命令范围；这些是待合法绑定的模型条件，不给实验参数数值。LAUNCH 取 a_cmd=a_launch+delta，从v_ref=0、xi=ell-s>0出发，直到首次 v_ref²=2a_lo xi。因为 F_L=v_ref²+2a_lo(s-s0)-2a_lo xi0 的导数为2v_ref(a_cmd+eta+a_lo)>0，且 F_L≥a_launch(a_launch+a_lo)t²-2a_lo xi0，交点在有限时间内且xi>0；上界 sqrt(2a_lo xi0/[a_launch(a_launch+a_lo)])。到边终点前必过该交点。

APPROACH令r=v_ref²/(2xi)，a_cmd=-r+delta(a_hi+a_lo-2r)/(a_hi-a_lo)。在xi>0时 r_dot=(v_ref/xi)(r+a_cmd+eta)；r=a_lo时括号delta+eta≥0，r=a_hi时为-delta+eta≤0，闭带[a_lo,a_hi]不变。d sqrt(xi)/dt=-sqrt(r/2)，故从xi0到参考终点的剩余时间在[sqrt(2xi0/a_hi),sqrt(2xi0/a_lo)]内。到达时按混合端点规则延拓s=ell、v_ref=0、reference HOLD；不在端点计算0/0或把有限到达写成无限趋近。

BRAKE只在v_ref²≤2a_hi xi的可证域进入，命令-a_hi-delta使实际参考减速度至少a_hi。b=2a_hi xi-v_ref²满足b_dot=-2v_ref(a_hi+a_cmd+eta)≥0，首次v_ref=0前距离≤v_ref²/(2a_hi)≤xi，随后reference HOLD。LAUNCH首次交点前及APPROACH带内均在该域。保持中的参考零加速度、边端点接触规则和连续底层闭环为显式理想混合公理；不从有噪普通反馈推得。恢复同一旧tid只能从合法HOLD重入LAUNCH，方向和原边不变。界外侧滑、转向、未证制动或可信控制故障不在定理域，照故障/评分合同保留。

称P1为上述条件下每次未再受中断的合法旧边参考运动有限到达。它不证明全系统无死锁/无饥饿、任意丢包后恢复或实际LIMO误差界。任一可证明的界内碰撞都仍是反例，不能事后把条件改为不成立。

P5受限端点拼接：写世界参考p、实体平移基点x=p+z。旧原边(u,v)在tau到达后，直到新原边(v,b)在sigma≥tau合法进入，p=v保持，z仍按同一世界坐标闭环演化且属于Z；一般z(sigma)不等于z(tau)。要求w有界可测且无冲量，x/z无跳变重置，F、Z、kappa及控制律不因换边改变。新边只把边局部(s',v_ref')设为(0,0)，不清零真实误差。于是p(sigma−)=u+ell e=v=p(sigma+)，z(sigma+)=x(sigma)−p(sigma+)=z(sigma−)，新旧参考速度也都为零。固定世界Z的正不变性可以按连续流和恒等误差重置归纳组合。

新xi'=ell'>0、v_ref'=0满足制动锥并是合法LAUNCH初态，故P1可重新应用于这条已由PIE提出、全U'(0)静态合法、执行器方向假设适用且已授资源的新边。允许参考加速度有限跳变；没有额外jerk、转向、轮速、控制器记忆或驱动滞后限制，这些是理想平移公理，不由四邻图推出。实际x_dot=p_dot−kappa z+w仍可非零，有界可测w下也不承诺实际速度处处存在/连续。P5不把参考零速等同于实体停车，不认证旋转或非零参考速度拼接。

等待期间X⊆E=v+K；旧U(q)包含E，中心终点改tag仍保留Mask(E)，而E⊆U'(0)。新grant先完整保留、随后gate进入，使终点认证/排队/READY/新授权等待均无覆盖空隙。任意长合法HOLD不破坏不变性；有限日历完成还需等待和中断最终结束，不从P1推出。若新参考起点为v+d，保持x不跳时误差变成z−d，可能越界；若新Z缩小、F旋转或带非零速度转向，现拼接假设亦不成立。它们是必要前提见证，不是满足P5前提的反例；满足全部前提的失败则必须反驳P5。

## 4. 后缀几何与可计算预处理

K=Z⊕F；U(q)=union_{s∈[q,ell]}(u+se+K)，q∈[0,ell]。执行域由有限闭瓦片覆盖，Mask(S)包含所有与S相交的瓦片；边界接触也计冲突。静态障碍及工作域可行性对完整U(0)检查，初始实体/保持包络须合法且不同agent的初始资源不交。格图可通不自动代表有尺寸实体可通；不合法的静态域明确登记，动态失败不得用于筛图。

P2（前向证据定理）：每个通过验证的同tid样本j只给q_j≤s(t_j)，t_j是该样本付费CAPTURE时刻。设中心已提交旧下界q_old，候选融合q_new=max(q_old,max_j q_j)，本次退休在公共全序的时刻R原子提交；所有被使用的t_j≤R且q_old≤s(R)。同一tid的s单调，故对任意R≤t≤该tid的END有s(t)≥s(R)≥q_new，z(t)∈Z进一步给X(t)⊆U(q_new)。采样完成、消息接收、融合计算与退休发布是不同时间；只对实际退休提交之后声明新集合覆盖。对每一单样本也可分别自其t_j声明U(q_j)覆盖，但融合最大值不能回溯到较旧迟到包的t_j。乱序/重复不破坏前向证明，未验证或未来样本不参与融合。下一MOVE重新取得自己的U(0)，旧q不跨occurrence；endpoint E=v+K属于每个U(q)，不能退休为空集。

对r∈M0=Mask(U(0))，I_r={s∈[0,ell]:(u+se+K)∩r≠空}。K紧、r闭使I_r为紧区间[0,ell]的闭子集，且非空，因此lambda_r=max I_r存在并取到。于是r∈Mask(U(q))等价于I_r∩[q,ell]非空，等价于q≤lambda_r；充分性直接取s=lambda_r，不要求I_r连通。删除必须lambda_r<q，等号保留；endpoint资源恰为lambda_r=ell。r不在M0时不定义lambda。此为P4几何阈值定理，不是引用PSIPP的相对出发时差条件。

有限算法域另要求Z为有限有理闭盒、F和瓦片为有限有理凸多边形或其有限并，边端点精确可表；以u+t(v-u),t∈[0,1]避免单位向量根式带来的不明近似。逐凸块线性规划最大化t，约束u+t(v-u)+z+f=x、z∈Z、f∈F、x∈r；取非空块的最大值并精确换回s。一般紧集不自动有此算法。数值近似只可用经证上界lambda_hat≥lambda，称保守退休；未经证上界不许删除。

表按(lambda,r规范key)排序。每tid指针只前进；收到新的可信q后，逐个退休所有尚在表中且lambda<q的资源。证书数c、初始资源数m，几何比较/枚举为每次O(1+d)、全tid O(c+m)，d为本次跨过的阈值数；账本检查/写入、可信服务、位复杂度与消息另收费。建表须计候选发现、精确几何、O(m log m)排序和O(m)表项；多边—瓦片关系可稠密，不能称全地图线性或整算法O(1)。地图/几何/包络/表示版本变化必须失效重建。四共享臂使用同一预处理与缓存制度、计首用/复用/内存；F臂只是不途中删除，不获得较差几何能力。

强固定裕量参考函数N-GEOM：沿用同K/M0/Mask(E)及同证据，验证后取q'=max(q_old,q_sample)。q未增时可跳过几何，验证已发生费用照计；q增加时在私有工作区构造[u+q'e,v]⊕K，按规范瓦片序精确求M_N(q')={r∈M0:r∩U(q')非空}，发布时只删除仍属此tid且不在M_N的资源。允许缓存静态集合和只检查仍持有资源，不能故意禁用明显优化做弱对照。未知几何不得删除；近似算法各自给保守合同。

P6精确等价：r∈M_N(q) iff I_r∩[q,ell]非空 iff q≤lambda_r，因此朴素全几何和阈值表G-GEOM计算相同的安全集合。另lambda_r=ell iff r∈Mask(E)，故D的可中途退休条件也可用r∉Mask(E)，无需暗中赠N-GEOM阈值表。同原边/版本/证据及相同提交前状态的语义结果可归纳相等；不同近似界未必相等。在NATURAL中两者费用不同可改变完成、采样和轨迹，P6不承诺闭环逐迹相同。G/N只检验相同函数的计算组织，D/R检验查询对象，S/F检验释放时机；所有候选都用固定裕量，不将G-S改称动态误差管。计算比较固定相同查询策略及S，E0可省无用途G；其费用合同与受控四臂分开明示。

## 5. 中心状态机、发出授权与不可逆终点交接

信任域：唯一中心资源authority与各低层gate不分叉、会话内状态持久不回滚；授权和可信证书不可被普通错误包伪造。中心同一时刻只执行一个可暂停资源作业，所有检查/计算/资源访问付费，在完成后的发布点一次原子应用私有增量；计算期间物理继续、外部不能见半更新。已计算完但未发布的结果仍占据中心作业槽，后继中心作业在它发布或明确失败前不能开始读取旧账本。此是单机串行提交模型，不是假设跨owner免费原子事务。中心fail-stop不重启/清空/重新分配；当前授权和物理覆盖继续保留，不承诺恢复活性。

每资源owner为FREE或(agent,tag)，tag为resident gamma或活动tid。每agent有当前resident/活动记录、连续关闭请求水位d_i和至多一个未关闭请求e=d_i+1；tid=(session,i,e)，原slot、原边、parent gamma、M0、几何版本不可变。未授状态UNGRANTED、已授GRANTED；关闭结果为ABORTED或FINISHED。中心拒绝e≤d_i的任何首次/重复请求，不可复用序号；e>d_i+1拒绝而不跳过未知责任。标准数学整数无回绕，位成本仍随序号增长。普通消息无权生成新的可信序号/原步。

slot=k表示原occurrence从Π_i[k]到Π_i[k+1]，消费前真实c=k、消费后c=k+1；slot不是目标下标。请求保留起始slot、两端点及MOVE/WAIT类型，避免把PRECHECK的c相等与外部plan[c+1]混成不同索引。计划代际plan_epoch在整个合法episode固定，append只增独立revision；追加未来段不使已有cursor证书失效。

executor显式持久phase为BOOTSTRAP、RESIDENT_OPEN、GRANT_ARMED、MOVE_LIVE、TERMINAL_UNCONSUMED或QUARANTINE。BOOTSTRAP只允许原世界给定的参考HOLD及其误差闭环，不允许新MOVE/WAIT消费/PRECHECK；软件未就绪的应用角色除INIT外返回付费NO_APPLICATION_READY，不将未安装索引当空集合。INIT合法转交后才RESIDENT_OPEN，其有合法resident_gamma与resident_ref、active_tid=NONE、pending=NONE；GRANT_ARMED已接纳唯一grant但尚未START；MOVE_LIVE已START、原occurrence未END，允许同tid运动/制动/HOLD；TERMINAL_UNCONSUMED为END已发生且旧槽未消费。原occurrence=(session,plan_epoch,i,k)，计划代际不随append改，revision单列。END建立pending=(tid,occurrence,u,v,parent_gamma,gamma_prime,closed=true,ready_verified=false,consumed=false)，c仍k；中心FINISHED、READY在途或已验证均不使其退出该phase。已消费历史由单调c/关闭水位及当前必要closed记录拒绝重放，不要求无限位图。QUARANTINE禁止新作用并保留既有物理责任，不暗含域外机器人瞬时安全停车。

MOVE请求必须由中心SOURCE_REQUEST角色用已验证Kc指定的原Π步产生，带parent gamma。PRECHECK的付费CAPTURE必须同时验证：session/authority/tid/原occurrence及不可变源记录匹配；phase=RESIDENT_OPEN、active_tid=NONE、pending=NONE；resident_gamma=parent_gamma且resident_ref等于原边起点u，参考HOLD且v_ref=0；true c=k、该occurrence未消费且未END；相关命令/原记录/几何依赖版本有效。证明完整绑定这些谓词及采样身份，失败仅给付费DEFERRED_REJECT，不回真实c/位置或正确下一槽。成功采样后的当前槽是MOVE，无grant不能消费它，没有pending便没有可消费该槽的旧READY；较旧READY已消费、较新READY不匹配。因此在未接纳当前grant且parent/版本未变时，迟到READY不会推动c越过该MOVE。准入仍在实际接纳点复核phase、pending空、原起点、c/未END和完整绑定；不能以旧快照覆盖已发生的新授权或版本变化。中心使用该ENTRY只作限定准入事实，不据它更新Kc或生成下一槽。

原子授予：M0全部FREE或同agent的当前parent resident资源才可接受；其他同agent tag也不能随意吞并。parent E包含于新U(0)，在同一次中心提交中将M0标为tid、记录GRANTED并封存grant，之后才允许发送。该变更不使parent实体覆盖中断。资源冲突则保持UNGRANTED、不部分预留，保留当前阻塞请求供重试；其他输入/版本错误返回明确拒绝。未发grant不表示可以省略所有失败访问费用。

CANCEL须可信且绑定完整当前请求身份，包括尚未首次登记的合法e=d_i+1。在同一中心序列中，若尚未GRANTED，则原子记录ABORTED、推进关闭水位并持久化之后才回CLOSED；不改resident、不消费c、不释放不存在的部分预留。迟到首次/重复REQUEST均因e≤d_i拒绝。若GRANT先提交，CANCEL返回DENIED_GRANT_LIVE，不能回“已释放”成功ack。证明两局部顺序：CANCEL先使吸收性水位成立所以GRANT不可再产生；GRANT先使取消分支不可进入。没有多owner“此刻FREE”的清理推断，也不允许已发grant超时回收。请求重试只在确知当前请求已关闭后换新e，旧逻辑slot可仍未消费。

gate有自己的持久关闭标记g_i：初始为未执行过授权的前哨，只在其旧tid不可逆END时提升为该已执行请求的e。它不免费读取中心d_i；d_i还包括未执行的ABORTED请求，两者不是同一变量。验证grant须会话/签发authority有效、e>g_i、slot等于gate当前真实c，并匹配原边、parent及当前唯一授权；不要求e=g_i+1，因为中心取消可留下从未发grant的序号。中心的未授取消不可能产生可重放的有效grant，已发grant又不允许取消；已执行旧grant则由g_i/幂等标志拒绝。这些条件与中心d_i共同保护重放，不需要免费同步两端水位。

付费grant验证在实际接纳点通过上述RESIDENT_OPEN完整谓词后，原子转GRANT_ARMED，保留唯一active_tid和started=false；后继合法ACTUATOR再以同tid/slot/parent/命令和起点HOLD进行一次START并转MOVE_LIVE。no-start不消费、不重发tid、不释放M0。重复同grant/START幂等，旧epoch不回退s/c。已授未进入时q=0、整个U(0)保留；进入后可信q按P2前向退休；F保留M0至终点交接。错误phase、pending非空、该occurrence已END或原起点不匹配的首次grant/START均拒绝，不重新打开旧边。

只有MOVE_LIVE同tid在可信s=ell、v_ref=0且c=k时发生END。物理阶段不可逆关闭旧tid入口、提升gate已执行关闭水位，建立gamma_prime及pending、转TERMINAL_UNCONSUMED并HOLD；同一次本地提交令active_tid←NONE、resident_ref←v、resident_gamma←NONE。旧tid及候选新gamma_prime保存在pending，NONE表示本地尚未接纳中心的新resident身份，不表示实体或中心资源为空。该记录是物理/控制事实，不免费传给中心、不消费c、不改中心owner。保存至其合法一次消费及后继责任建立后才能按引用规则回收；单独清active_tid或普通COMPLETE不替END。此时参考顶点已经是v而未消费原边仍u→v，故明确禁止旧槽再次PRECHECK。

中心取得付费ENTRY END证据后，在串行提交复核当前GRANTED tid、occurrence、原终点/parent/gamma_prime/closed，将Mask(E)从tid转同agent resident gamma_prime，清其余、记录FINISHED及d_i=e，再发布READY。本地收到并付费验证匹配pending的READY，只设置ready_verified，不先消费。LOCAL_POLICY的后继实际提交须再次检查TERMINAL_UNCONSUMED、c=k、匹配原MOVE/closed/pending/ready_verified且consumed=false、active_tid=NONE、resident_ref=v、resident_gamma=NONE、HOLD于原终点及gamma_prime绑定；一次提交先从已匹配pending复制resident_ref←v、resident_gamma←gamma_prime，标消费、c←k+1、保持active_tid=NONE，再清当前pending并转RESIDENT_OPEN，不连锁处理下一槽。这些写入是一项本地原子转移，不能先清pending后丢失新身份。旧/不匹配READY拒绝且不改相关命令版本；重复已消费READY不能作用到下一槽。中心FINISHED不打开本地入口，READY本身不写Kc。下一MOVE仍须新PRECHECK及预留，迟到旧释放因tag/tid/水位不匹配不改新holder。

P3覆盖归纳：WORLD_GIVEN的bootstrap由§3同世界z不变性及固定参考HOLD持续覆盖实体，而不只在初始瞬间分离；软件INIT核验并同agent同包络接续所有bootstrap责任，不删其他未激活agent的占有；授予先完整预留、parent包含于M0，同agent改tag无空隙；gate只有覆盖已存在才进入；P2使中段退休后实体仍在剩余集合；终点改tag保持E、清其余不删实体所在资源；CANCEL未授无资源变化，已授取消拒绝；旧消息不改变新tag。不同agent的bootstrap和软件资源责任共同互斥，任何实体交点落在共同闭瓦片而违反该互斥，故界内无实体碰撞。该证明不保证无死锁、吞吐正或永久丢包后的释放。中心故障/失联不使grant/bootstrap/实体消失；界外信任破坏另记，不能借此掩盖前提成立时的反例。

## 6. 真实游标、付费采样与共享知识

真实c_i由executor私有持久维护；中心SOURCE_REQUEST/QUERY/planner仅持已交付Kc_i，不可解引用私有c。LOCAL_POLICY、CURSOR/ENTRY可信authority按各自限定权限付费读自己的c，不因此让中心免费获得。Kc是同计划代际CURSOR证书中c的最大值，未知不推0；软件INIT合法提交可给予已计共同初始证据。MOVE仅匹配READY后的LOCAL_POLICY一次消费，WAIT仅合法RESIDENT_OPEN一次消费；HOLD/no-start/grant/普通反馈不消费。即使同进程也不能通过别名、日志或队列业务旁路传私有新cursor。

公共CURSOR机会按固定agent规范顺序逐一轮询，初始前哨在第一key之前，空fleet属于输入非法；每机会请求一个agent，包括resident/NONE/纯WAIT，资格不由算法当前需求改变。CURSOR只返回(session,plan_epoch,agent,request_id,sample_id,c,sample_point)，不顺带给q或实体真值。POSITION是独立付费服务，请求必须指定tid；仅匹配gate当前活动tid或保留的同tid终点记录才给含真参考区间，NONE且无匹配记录返回NO_MATCH，不能推断清空。ENTRY含PRECHECK或END两种完整绑定证明；TASK服务的算法可见回执另定义。四臂和guarded TIP有同一可购买能力，不跨反事实臂转移payload。

所有可信服务统一捕获规则：机会只登记通用作业，具体请求经§9付费生成并提交后才入authority队列。authority作业首个语义操作是付费CAPTURE，不足以支付该原子读取则本次没有采样。其在PROCESS_SLICE行的物理推进及先前结果发布全部完成之后、该作业其他语义工作之前，原子固定一致authority视图，记sample_point=(公共行,子事件序,CAPTURE)、request/sample序号与输入版本。此前已提交的POLICY更新计入，此点之后不计入；大快照以不可变版本根固定，后续字段复制另付费。AUTH_WORK只是此authority工作步骤的别称，不是O的额外免费事件。余下处理只能操作冻结内容；AUTH_COMPLETE指作业完成、不刷新，DELIVER指严格后继NETWORK/接收验证作业的付费提交、不赠送状态。算法只在其后付费POLICY/QUERY的实际输入捕获点读取已交付知识。CAPTURE失败或完成后丢失不更新知识，已发生费用不退。TASK的全部字段必须来自这个固定全局修订，不能拼跨修订局部片段。

重传已存在证书保持原request_id/sample_id/sample_point/payload，只收实际缓存/通信/验证费；新鲜采样必须有新请求序号和重新付费CAPTURE。区间生成的确定性封装及传感创新只以本请求语义key取值，并必须包含捕获时真实s；已确认不包含为可信模型破坏，不是普通误报。q_sample取区间下界与合法[0,ell]保守处理，中心只在同tid验证后取max更新；旧tid的大q不能用于新MOVE。

pure WAIT链：POLICY合法使私有c:k→k+1，位置和resident不变、算法Kc不变；共同CURSOR请求排队→首个付费CAPTURE冻结k+1→期间可再消费WAIT而证书不变→付费完成/投送→后继算法机会才更新Kc。若CAPTURE在原WAIT之前只能冻结k。主PIE的barrier/PROJECT与该臂TIP均可复用已付费证据，不按使用者名字重复收采样费；实际读取/计算/广播接收工作照收。POSITION不提供pure WAIT逻辑进度，主算法也不能绕过CURSOR读取c。

## 7. 阻塞导向与轮询的总定义

Active为中心已提交GRANTED但尚未提交FINISHED的tid集合，按本臂已认证/已提交账本计算；UNGRANTED、ABORTED与FINISHED排除，已发未启动、运动、制动、已在gate终点但中心尚未知者包括。不按隐藏真实s或未送达终点信息删除成员。两策略遵守同一谓词，不强制跨臂私有历史产生完全相同集合。

RR状态last初始为小于所有合法(session,agent,e)的前哨。每QUERY作业在付费捕获的非空Active中取规范序中严格大于last的最小key，没有则回绕最小key；空集返回NO_QUERY、不改last。按§9成功提交选择请求时推进last，此后的采样失败/失联不回退；中途废弃或未提交不推进。删除不重置last，插入按该全序参与下一次计算。集合来源、初次选择、空集和动态成员均唯一，不靠“上一次”未定义初态。

中心每agent至多保留一个UNGRANTED原请求p，阻塞请求集合P只含结构/PRECHECK有效且最近因资源冲突未授予者；重复传输不产生新p。授予、关闭、版本/parent失效则移除。QUERY计算当前owner重查这些静态M0，score(t)为不同p中存在r∈M0(p)、owner(r)=t且r∉Mask(E_t)的个数；依P6等价于lambda_(t,r)<ell_t，同p多个r只计一次。所有字段来自源提议、已收费几何和中心账本，不读真实blocker/进度。D取score最大正值者；tie以所有实际贡献该tid分数的p之首次加入P行的最小值，再以tid规范key排序，无正值退回同RR规则，Active空则NO_QUERY。任何实际选择也更新自己的last，避免回退状态未定义。查询晚、重复、没有跨阈值或不能解除全部阻塞仍是合法负结果。

实现合同首先采用完整枚举P和相交资源的确定性参考计算，计全部扫描/去重/排序费用，不把仅“受影响”作为无证复杂度承诺。若后继实际实现用反向索引，必须在同知识快照上与此总函数等价，计索引维护/失效及最坏输出规模；未证等价不能静默换策略。本候选的阈值优化只减少几何判定，不能宣称消除了全局查询选择成本。

POLICY的主体标记预先为SOURCE_REQUEST(i)或LOCAL_POLICY(i)，不是根据私有c临时分派。中心SOURCE_REQUEST只读Kc、已提交模式/parent/d_i/唯一请求与不可变Π；已有未关闭请求只重试同绑定；Kc未知、Kc=L或对应原WAIT分别返回NO_SOURCE_INPUT/NO_REMAINING_SLOT/NO_MOVE_REQUEST；只有Kc<L且原槽为MOVE才生成该原请求，不从PRECHECK拒绝猜正确槽。LOCAL_POLICY的唯一顺序为：符合完整pending/READY一次消费谓词则消费一个MOVE；TERMINAL_UNCONSUMED尚不可消费则HOLD；GRANT_ARMED/MOVE_LIVE继续原责任；RESIDENT_OPEN且无剩余槽则HOLD；该phase下当前原WAIT经c/原顶点/无active/pending/未消费检查后消费一个；当前原MOVE则等待中心，不自行发请求；记录矛盾QUARANTINE。一次token仅一个角色、最多一次消费或一个请求；消费不连锁生成下槽请求。角色token来自共同公共描述符，不能只有本地看到MOVE才给中心额外机会。纯WAIT链可本地逐次推进但Kc仍滞后；进入后续MOVE可能等待CURSOR费用和交付。

共享模式ACTIVE允许本臂查询策略；SHARED-OFF停止新途中POSITION，仍验证已有证据、保留资源、执行原责任及付费终点交接；DRAIN再停止新规划承诺与新原occurrence，对未授请求可按CANCEL关闭，已发grant不可撤销。DRAINED仅表示所有agent均有可证resident且无未闭请求/活动运动责任、待提交中心变更；resident资源不清空。旧包由水位拒绝，处理费用仍留。通信永久缺失时不假定达到DRAINED。恢复ACTIVE不回滚q/c/水位、不重放START。E0在整个共享评价中不生成途中POSITION，独立终点ENTRY能力不因QUERY候选为空而消失。

NATIVE-COLD-OFF是独立原生定义域的冷启动旁路：在任何共享INIT/副作用前决定，完全不创建新mask/证据/状态、调用原源码和原输入/时钟/随机接口；供原样身份机械合同使用。它与有实体误差的SHARED-OFF不同，不能在在途责任未解除时热切到旁路来声称恢复bitwise原版。触发式refinement合同对应共享ACTIVE/SHARED-OFF/DRAIN的责任保持，触发只来自已交付知识/公开模式事件，不读注入真值；共同安全底座在错误未被触发器发现时也不能停用。上述模式不重定义或赋值原保护参数。

## 8. PIE、真实任务与冻结规划作业

固定官方 R0 为 [YueZhang-studyuse/LMAPF-delay](https://github.com/YueZhang-studyuse/LMAPF-delay/tree/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357)，commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。新MOVE只能是该固定核心经下述显式共享接口接纳的输出；原生 NATIVE-PIE-D 原字节/原误差域另轨保留。共享接口改变执行、观测、任务同步和计时注入，不宣称整个native轨迹等价，不把接口成本或原源失败当查询策略收益。

联合历史Π_i[0..L]使用共同逻辑槽，每slot映射原job/segment/source/input/原边或WAIT，提交后不可改。真实c_i≤L，已知Kc_i≤c_i，未知则不为该agent提即时MOVE；Π_i[0]为合法起点，初始L=S=c=Kc=0是空历史索引定义，不是实验保护参数。MOVE只在对应READY后消费，COMMITTED_WAIT在合法POLICY消费，HOLD不消费。即使主算法使用Kc提出旧slot，gate也只能经PRECHECK及grant执行其真实当前原MOVE，不按未来PROJECT输出自行改路。

最多一个规划作业及一个待提交结果。S为最新提交段的起点；只有all Kc_i≥S且无上述作业时，才可请求在尾L追加。接纳后S←old L、L←new L，new L>old L；未追上的前段不能无限追加。段首与旧尾同一槽，不重复消费/服务。旧承诺不因预测目标改变而撤销。在线路径可保留从min Kc起到L及被当前作业pin住的前缀，只有无仍有效引用才可GC；完整审计历史另追加归档，不能把在线窗口界称为总存储有界。

真实任务账本A与已知K_task分开。唯一主服务谓词SERVICE_TRUE(i,j,t)为：j是此刻真实A中分配给i且尚未服务的有效队首；参考处于合法初始驻留或已END原MOVE的终点驻留（尚未消费亦可），其参考顶点等于j的任务顶点且v_ref=0；整个真实实体X_i(t)⊆ServiceRegion(j)；共同服务机会存在且未达Stop。这里的物理驻留事实不以软件INIT_READY、中心READY、resident_gamma的已知性或算法证书送达为前提；原边中途cap HOLD不冒作终点驻留。主域不另要求真实实体速度为零或额外驻留时间，不把参考零速当作实际停稳；需要停稳的任务属于另行定义的扩展域。固定TASK_SERVICE机会据此每agent至多服务一个合法队首，再按固定原任务策略补给：greedy按agent规范顺序填已分配队列；Fixed用各自原序列；Inf用原tasks[(counter_i*num_agents+i) mod tasks_size]并递增counter。补给深度/原CLI意义保持而本阶段不绑定数值；tasks_size为空或接口非法不做取模/假目标。先服务再补给是明确共享顺序，不冒称native三种策略的sync相同。

初始合法resident可真实服务，无MOVE也可能Q>0。每实例有独立task_instance_id，即使目标相同仍区分；service_id=(block,agent,TASK_SERVICE行,task_instance_id)，全局task_revision单调，记录分配前后和去重。Q来自独立真实服务记录，不等待POSITION、ENTRY、READY或TASK回执。真实派单不为规划冻结，也不按查询归因筛服务。

K_task仅由付费TASK请求在CAPTURE处捕获的单个原子全局快照或同修订序列的连续完整batch更新，含已分配队列、共享剩余序列、计数器和服务去重；不同修订局部字段不能拼接，乱序等待缺段，普通COMPLETE不更新。TASK捕获authority是独立真实任务账本，CURSOR捕获executor，POSITION捕获可信参考状态，角色与费用不能混为免费全知传感器。

PROJECT(K_task,Kc,Π,L)仅复制每agent已合法分配且未被可信确认完成的队列W_i。从Kc_i之后至L逐公共槽k，对该agent检查Π_i[k]匹配队首则最多虚拟弹一个；起始槽不另检查，WAIT各槽也最多一次。不把未实际分配的greedy共享任务虚拟派给agent，Fixed/Inf也不生成尚未分配项；空返回空、字段不一致返回NO_INPUT。虚拟弹出不改A/K_task、不产Q。这是基于滞后下界的所有权受限预测，不保证准确未来；任务耗尽而原core不支持空目标时NO_PROPOSAL/HOLD，保留停滞/未完成，不造当前位置伪目标。新可信快照可触发再规划。

每作业冻结 SharedEnv：num_of_agents/rows/cols/map/map_name来自同一公共manifest；curr_states为Π_i[L]的原State位置/平移方向与逻辑槽，非真实in-progress pose；curr_timestep=L；goal_locations为PROJECT剩余合法任务及可信reveal字段；unexecuted_paths仅复用前次接纳future_path且完整锚点/格式有效，否则空；file_storage_path仅未来合法输出合同，当前不创建。源身份、参数版本、地图与任务/游标已知视图版本一并冻结。不能保留到可变真实环境的引用。

规划worker包含核心可变对象、缓存与C/MT随机状态的隔离副本，所有工作包括丢弃都计费。输出须全agent非空、有共同延长长度、首点等于尾锚点、后续每步四邻接或WAIT、全段vertex/swap合法、索引和端点有效。原commitPath规范化后全检；空/越界/非法输出只能报SOURCE_ERROR/INVALID_OUTPUT，不造路补救。接纳前以最新已知K_task/Kc重算PROJECT；完整planner-visible目标、源/参数/锚点/尾/待追加区间/环境及future_path版本匹配才在一次提交CAS中append。Kc前进不自动使结果失效，但目标变化或CAS期间版本变化须拒绝；丢弃内部状态不进入后继接纳流。

作业总返回为ACCEPTED_SEGMENT、NO_INPUT、NO_PROPOSAL、PENDING、SOURCE_ERROR、INVALID_OUTPUT、STALE、STOPPED；只有首者新增原MOVE。未完成规划不阻塞物理回调；源_exit/异常只能结束隔离worker并保留外部账本/物理状态，不能杀死评价器。安全证明不依赖原core最优性或全场景活性，仍须区别源未定义行为与合法搜索失败，前者不用于制造相对优势。

## 9. 原时钟、随机输入与有限收费事件

一手源码新增实核：LNS/InitLNS为Time=high_resolution_clock、fsec=duration<float>；LaCAM2 Deadline为steady_clock，毫秒duration_cast后严格elapsed>limit；SIPP超时为经过秒数>=timeout。InitLNS存在增加time_limit、continue绕过runtime更新、初始逐agent传完整预算及后处理；不能统一改写成全流程硬CPU截止。明示MAPFPlanner→LNS(use_sipp=true)→BasicLNS Agent选择SIPP，避免该对象进入SpaceTimeAStar空超时入口，其他配置不自动豁免。mcp.cpp的clock()/CLOCKS_PER_SEC是CPU起止日志，不是上述经过钟停止条件。

37个固定规划源/头对象已完成完整关键词检索并核对象身份（304149 bytes/8713行），人工语义阅读限命中/必要窗口；根另亲见MCP L14–72及SingleAgentSolver.h L35–100。rand()还在比较器/路径表；默认random_shuffle、LaCAM局部mt19937和分布后端必须登记。LaCAM每次runLACAM2重建其源码指定MT初态，不能偷改成共享主流。随机比较器不等于固定严格弱序，不能承诺跨编译器/容器调用顺序相同；native定义域/运行合同必须保留此风险，不静默修比较器再称原字节。限定集合没有额外直接OS取时/熵/sleep调用的关键词证据，不排除未搜索顶层入口/动态库；既有源清单仍非完整运行覆盖。

共享适配选择明确的虚拟时钟，而不是把wall时间当CPU：每个原chrono now调用返回其执行所在公共事件的物理时刻t，按冻结ABI的clock duration period换为floor(t/period)计数；同一事件内多个调用可同值，暂停/排队时世界t继续，恢复读钟包含该间隔。源码中的起点、差、float秒转换、duration_cast截断、比较符号、预算增量/覆盖及局部重置照原指令执行，不替换为统一timeout。high_resolution_clock的平台alias本身尚未实核，适配明确把它映射为此单调物理钟，不冒称native alias已证明或与native逐输出相同。

CPU clock单独映射为该隔离worker自出生以来已实际完成的收费指令CPU服务量，按固定CLOCKS_PER_SEC和CPU服务单位换算；暂停/排队不增加，其他worker不倒灌。原日志的绝对CPU读数保留为此虚拟域并标注adapter，不假称主机CPU测量。主总费用账本仍包含所有worker/失败工作，与这个单worker日志读数分开。未知外部时钟/熵/阻塞调用一律FOREIGN_INPUT_UNMAPPED，不用主机当前时间偷偷填充；对应配置不可宣称可重放并进入修订。

C PRNG初态作为显式ADAPTER输入由独立block根和固定核心角色映射，具体种子不在本阶段生成；之后包括比较器rand及默认shuffle后端的全部调用/状态均在冻结标准库与worker内保存。接纳副本的状态可进入后继，丢弃副本不污染它；失败费用仍留。原局部MT的源码构造/重置不变。编译器/ABI/标准库/库版本、机器指令语义、浮点模式、随机接口/初态和外部调用表为未来manifest必需项；不同版本是不同profile，不能把“seed相同”当跨平台相同执行。原native轨道不注入此适配时钟/PRNG，明确分域。

公共有限机会表O按(t,row_id)全序、t非减，含INIT、POLICY(role,i)、ACTUATOR(i)、REPORT(i)、QUERY、CURSOR、ENTRY(i,kind)、TASK_REQ、TASK_SERVICE、NETWORK(channel)、PROCESS_SLICE(server)、MODE(scope,kind)、FAULT、CUTOFF、STOP。role必须为§7两个公共主体之一，不能由私有状态现选。不得依某臂已观察收益改O。每行先推进物理到t并处理有限自主切换，再按job规范key发布前行已完成的有限结果，最后只执行本行类型；缺输入为明确空结果，不从未来补对象。新生工作/消息/结果可见发布均在严格后继行，单行不递归自触发。本段是未实例化的文法，不生成实际O。

机会、作业、提交三层语义：上文POLICY/QUERY/CURSOR/ENTRY/TASK_REQ/NETWORK/REPORT/MODE等名称既标识公共机会类型，也标识其后付费作业类别；本候选所有“选择、读取、生成、消费、更新模式”均发生于该类别作业的付费步骤及合法提交，不能在机会到达时先免费执行。机会只提供预先类型/公共subject/不透明输入引用，不携带根据真实进度、阻塞数或任务算出的答案。输入token由元调度器按固定FIFO登记；固定描述符/队列槽的有界控制开销按公共供给预付并单列，不再递归生成一个排队作业。策略生成请求、复制/解析字段、日志或遍历业务队列均是付费应用工作，不能藏在token登记中。

每个可变应用状态有指定writer：中心管理owner/P/d/查询last/轮询状态/臂模式/Kc/K_task/Π及规划接纳版本；各executor管理自己的命令/c/READY消费状态；真实任务环境独占A的真实变更；独立planner仅改自身私有求解状态。各应用writer至多一个计算或待发布槽，彼此不跨槽持锁等待。CAPTURE固定不可变根，字段复制/遍历/计算随后收费。真实A和物理/闭锁事实的自主变化不是应用writer锁内的步骤，按公共全序和快照版本处理；不因snapshot作业占槽而冻结实际服务或END。

这里的writer槽串行化算法作业，不给连续物理状态加锁。executor区分命令/逻辑状态(session,tid,parent,slot,c,command_revision)与连续流及既定混合模式(s,v_ref,z,LAUNCH/APPROACH/BRAKE/HOLD、closed latch)。先前已接纳控制器的流、自主切换和不可逆END先在每行物理阶段演化；END只关旧tid并建立其终点latch，不消费c、不改中心owner、不生成免费证书。其余修改只能在该executor规定的付费提交或ACTUATOR接纳点生效，依世界全序排列。待发布POLICY或gate作业不能阻止旧控制器到达或制动，也不能因占槽把旧物理快照当当前状态。

发布依赖分开记录：c消费绑定plan_epoch/slot及未消费状态；新grant接入绑定session/tid/parent/command_revision和已验证原边；END绑定不可逆closed记录；q证书绑定采样时原tid/几何版本/进度下界。正常连续s/z演化不会冒充命令改写，command_revision相同亦不证明瞬时模式不变。需要HOLD的RESUME、首次START等在实际接纳点还须付费检查规定离散模式/幂等标志；模式不符则拒绝或等待，不用当前pose免费重算可行域。PRECHECK的合法resident保持、END的单调closed以及q的P2包含性各有自己的保持证明，不能共用一个含糊“证书未过期”。同一旧tid只发生有限既定切换，混合守卫/模式/原tag保存的成本归共同控制项且按实际字段位长计，不称无成本业务操作。

应用作业完成后，在严格后继行的有限控制发布容量中执行已列明的版本/tag/幂等检查与准备好的增量；不足支付完整检查/发布则不产生效果、继续占槽。控制发布容量是future O/容量表的显式部分，费用依访问字段与字节长度计，不把随epoch增长的大整数或任意扫描称免费O(1)。验证需要新的几何/全局推导时退回新付费作业，不能在发布点顺便重算。物理在等待期间照常推进；版本稳定只排除离散命令改写，连续安全仍需P2/P5及完整原责任的保持性，不能以相同version替代物理证明。

INIT机会登记软件初始化作业，经付费验证固定输入、持续有效的bootstrap包络/资源互斥/角色身份并完整提交后，才建立应用可读的resident索引与初始游标证据；它接续已存在的世界责任，不创建物理机器人或另起评分世界。gate激活消息延迟时对应bootstrap/已接续resident仍保留，不能在其他agent启动时被当作FREE。初始化及预处理实际成本单列并纳入首次总成本，公共E不因某臂初始化慢重开。POLICY按公共角色只读允许知识，最多消费一槽或生成一个请求；软件未就绪时除初始化外的应用业务不运行。ACTUATOR只执行已验证发布的命令，REPORT不改可信知识；物理BOOTSTRAP HOLD与真实任务环境依§12独立继续。

QUERY机会只入队通用SELECT作业。中心在它的付费CAPTURE固定已提交Active/P/owner/Mask(E)/last及模式，随后按§7付费扫描/去重/比较，最多准备一个POSITION请求；结果通过后继发布的版本/模式检查并提交后，才生成该请求且更新last。未选中、过期、发布失败不推进last；已经提交的选择后来采样/网络失败仍推进且不回退。重放同选择提交幂等。中心单writer槽排除其他中心作业先改所依赖状态；若外部明确失效或版本不符则丢弃/重新付费，不发送陈旧选择。POSITION随后在自己的authority作业实际读取参考进度，SELECT不先偷读q。

CURSOR作业以同样付费读取/选择/后继提交推进固定agent轮询；POSITION与其字段权限仍分开。ENTRY只对指定PRECHECK或END阶段付费处理，不存在则NO_REQUEST；TASK_REQ生成单个全局快照请求。NETWORK的付费作业才从指定channel已可发送的不透明队列中取规范最小payload、编码和传输，提交后按本消息外生故障key作用；读取不存在的重放目标为NO_REPLAY_TARGET，不填别臂payload。其队列FIFO是传输规则，不由元调度器提前替策略解析消息或获得发送方新状态。

POLICY(SOURCE_REQUEST,i)在中心收费槽执行§7来源总函数，只用允许的Kc/Π/中心状态；POLICY(LOCAL_POLICY,i)在本地收费槽读c/pending/已验证READY并执行§7消费总函数。输入捕获与实际消费发布均付费，slot/未消费/phase/绑定不符就丢弃，未发生消费不回写影子c；消费后也不回滚。两个角色不能在同一token串行连做，不由本地私有分支触发中心免费token。PRECHECK/END/gate在接纳前以其各自保持证明和当前守卫复核；ACTUATOR不临时重规划/重算碰撞，旧运动/自主END不被计算槽阻塞。

TASK_SERVICE为固定机会的真实环境操作，按§8已分配队首与实体/模式判断并转移A，不要求某策略额外申请才可计分；资格检查/任务转移的环境服务费用及宿主成本单列，公共容量与规则各臂相同，不把算法可见真值作为副产品。此前已真实发生的服务不因策略未查询TASK而消失。元评价器推进物理、查O、维护不透明token的宿主耗时与应用工作分账，二者均报告；任何业务选择/信息读取不得记入元评价器来规避费用。

PROCESS_SLICE为固定server提供有限正工作容量。server内FIFO，按入队行/job_id打破同时性，运行一个队首job，剩余容量不在本行递归运行新生job。中心账本job检查/更新在私有副本中分步收费，完成后等待后继发布才原子生效；CAPTURE是authority job的首个收费原子操作，具体发生于本PROCESS_SLICE行物理推进后的操作起点。它与其他同server作业串行；不同authority共享世界全序，不能有含糊同一时刻的前后快照。容量不足完成该原子操作时不读取状态，保留至以后。每条已执行操作不可撤销计费，未执行未来容量不算真实工作。

费用表必须列请求生成、CAPTURE/数值封装、资源/索引读取和写入、原子提交记录、grant/证书、网络字节/每接收端、验证、重复/失败处理、planner、日志/GC及预处理；所有动作正费用或由明确共用已付费对象复用，不能隐含免费全局扫描。NATURAL计实际工作与竞争同公共服务容量；STRICT在同O/容量下连空闲未用供给也预付，实际工作向量仍分别报告，不能强迫两臂实际工作量相同。处理排队/物理推进/来源停止互相作用纳入闭环，不能为费用对齐冻结实体。

服务拓扑合同：每臂用同一个有限角色图。Srv_C是中心单服务站；Srv_E(i)是每agent的本地应用/可信捕获服务站；Srv_P为该臂唯一隔离规划worker；Srv_A为任务快照复制服务站；Srv_N(u,v)为每个已登记有向消息通道的服务站。通道/角色由公共合法主体关系固定，不按某臂产生的负荷增设服务器。实体运动/已接纳混合守卫与真实TASK_SERVICE由共同物理/环境引擎提供，其容量与费用独立明列；它们不被某算法应用writer锁住。各站FIFO及同刻key沿用上述规则，能力数值仍未绑定。改变分站/共享关系必须另立预注册profile且各臂相同，不能以只相同单价掩盖不同队列拓扑。

| 作业族 | 允许输入及唯一写域 | 固定server | 发布目标和费用责任 |
|---|---|---|---|
| 软件INIT/几何缓存/资源验证 | 固定输入、共同bootstrap身份；中心私有副本→合法中心状态 | Srv_C | 后继中心发布；全部解析/几何/建表/核验/复制/首次提交计费 |
| SOURCE_REQUEST、QUERY、CURSOR选主体、模式 | 已交付知识/中心账本；中心状态、请求和last | Srv_C | 封存不可变请求/模式结果，发布后释放本writer；选择/空结果/去重/版本检查均收费 |
| PRECHECK/END/CURSOR/POSITION捕获与封装 | 指定agent的允许真值、当前phase或保留closed记录；仅本作业冻结payload/本地outbox | Srv_E(i) | 向中心的后继消息；先付原子CAPTURE，余复制/封装/失败另费；不写中心知识 |
| grant/READY/控制命令接收验证与LOCAL_POLICY | 本地已交付消息/c/phase/pending；本地命令、消费状态 | Srv_E(i) | 当前合法守卫的后继本地提交；不能在此顺发新原MOVE；接纳与拒绝都计费 |
| 中心接收证书/资源退休/授予/CANCEL/FINISHED | 已投送证书与中心当前版本；中心唯一账本 | Srv_C | 原子中心增量和后继grant/READY消息；所有资源读写/原子记录/签发计费 |
| planner输入/输出管理 | 已交付Kc/K_task、不可变Π和版本；中心管理记录 | Srv_C | 完成的冻结输入交Srv_P，返回后再付费完整检验/CAS，不持中心槽等待worker |
| 原core求解 | 冻结SharedEnv、该worker源状态/clock/RNG；只写worker私有状态 | Srv_P | 完成后封存结果，中心另作业接收；超时/丢弃/源失败全计工作 |
| TASK_REQ生成/任务知识接收 | 中心已知版本、请求身份；中心请求或K_task | Srv_C | 请求后释放中心槽；完整快照交付后另作业验证/更新 |
| TASK CAPTURE及快照复制 | 同一真实A修订的不可变视图；只写快照payload/outbox | Srv_A | 向中心的后继消息；固定根不赠送整账本复制，不阻塞真实环境更新A |
| NETWORK(u,v) | 指定通道已发布不透明消息；该通道发送/传输状态 | Srv_N(u,v) | 成功传输后仅登记目的角色的后继接收token；编解码/字节/副本/每接收端费 |
| REPORT普通观测 | 该臂指定普通观测能力；普通payload | Srv_E(i) | 后继通道传输，不能写可信q/Kc；普通故障/处理费归该臂 |
| ACTUATOR实际接纳 | 已付费验证并发布的同tid命令及当前必要模式/幂等守卫 | 共同控制引擎的该agent容量 | 只执行已有合法权限；控制/守卫/位长/物理引擎宿主成本完整记录 |
| 真实TASK_SERVICE | 真实A、实体/服务谓词和Stop界；唯有环境改A/Q | 共同任务环境容量 | 自主真实服务，无算法可见副产品；资格/派单/去重/宿主成本完整记录 |
| 日志/GC/索引维护 | 各写域已授权状态 | 所属写域的原server | 不设免费后台线程；独立审计器仅留证据，不反向供算法选路 |

异步交接不跨writer嵌套锁：发送者只在自己的提交中封存不可变envelope并产生目的通道的不透明token，随后释放自己的槽；通道作业再付费读取/编码，完成才产生接收角色token；接收角色自己的后继作业付费验证后改自身状态。元调度器只登记有限不透明引用，固定描述符开销单列预付；业务payload读取/复制、FIFO取项和解析不由元调度器代劳。不能在持中心槽时同步等待Srv_E/Srv_P/Srv_A回复，也不能让Srv_N直接写中心owner或本地c。跨角色引用在所有仍有效使用方结束前保留，GC/保留内存也计费。发布的版本/tag检查使用对应writer的显式控制发布容量，不借用另一站空闲供给；不足时继续占自己的槽，不借机冻结其他物理进程。

故障创新由独立block根派生，key=(角色,公开行或请求/作业语义id,有限copy/attempt序号)。同block各臂共享创新函数而输入自己产生的对象；调用次数不同不顺移公用PRNG磁带。ordinary假反馈、no-start、空间/运动扰动、通信错误、处理容量分别有类型；给普通包加时间偏移不等于实体误差。ROOT独立性只对block成立，臂间配对相关允许。当前不生成根、种子、O、manifest、tape或载荷。

MODE的有限kind为QUERY_ON、QUERY_OFF、DRAIN、BRAKE、RESUME。前三者scope为本臂，按§7更新模式而不删责任；后两者scope为指定agent，只生成付费控制请求，验证后到后继ACTUATOR才作用。BRAKE在P1制动域内继续旧tid，无在途对象则NO_MATCH；RESUME只有旧tid的合法参考HOLD且未终结可重入LAUNCH，BRAKE尚未停则等待，不跳过停车条件。E0的QUERY_ON不使其获得主策略之外的POSITION，返回STRATEGY_DISABLED；NATIVE旁路不接受共享MODE。非法scope/kind为INPUT_INVALID。每行只推进一阶段，不在模式切换时自行产生新MOVE。

FAULT的类型记录为(公共行,role,subject,kind,该profile已规定的载荷语法)。ORDINARY_VALUE只能改变普通pose/COMPLETE字段或其序号/时标，不伪造可信签发；NO_START只影响指定ACTUATOR尝试；SPACE_W与REF_ETA分别提供有界可测物理输入，不互相替代；NET_DROP/NET_DELAY/NET_COPY只作用于本臂已存在的消息，有限副本数受O/profile限制；CENTER_FAIL_STOP使中心停止新服务/发布，已提交账本不回滚，未提交私有工作无外部效果但费用保留；WORKER_FAIL只终止隔离planner作业，不消失实体。CLOCK_LABEL_SKEW只修改非权威本地标签，授权不依赖租约/标签时间。可信状态回滚/签发伪造、控制闭环失效、实际w/eta越界或未覆盖的形体/障碍变化属于TRUST_OR_PHYSICS_BREACH压力域，不继续调用P1–P5保证。未列kind或缺对应subject不能猜默认，分别INPUT_INVALID/NO_REPLAY_TARGET。

瞬时故障与迟到消息用公开行序区分：FAULT前已发布的grant继续有效；中心已计算未发布的grant在fail-stop后不发布。失联/中心停止服务本身不令正在运动的机器人停车或让已预留空间消失，物理与真实TASK_SERVICE按其仍合法的模式继续。各分量停止、全臂评价Stop及主机评价器故障在§12分开。有限自主运动每旧tid只按LAUNCH/APPROACH/END或BRAKE/HOLD这些既定守卫推进；若数值过程产生未定义/Zeno级联，不把无限内部工作塞进一个公共行，返回不可认证并按§12处理。

新增来源73E1已经完整读取六个固定R0对象（101756 bytes/2869逻辑行），证实官方CLI类别“LACAM only”和具名分支初始/重试/修复经getInitialSolution→runLACAM2→solve→Planner::solve，不需要修改源才有此模式。它仍复用LNS对象、随机洗牌/预采样tie等；不是无随机、无SIPP对象或整个生命周期契约已闭。73E3/E4现已实际完整返回；73E5亦完整返回并经根全文读取，不能再按历史时态记待回；原73E2仍缺，不用新报告冒充。根另独立核固定头文件/driver全文和相关完整函数窗口，确认init_time_limit在所见构造与driver路径未初始化却在simulate首次按值传给plan，plan体内覆盖不能消除调用前读取；初始化失败未向simulate传成停止，future完成仅join不get不能识别其异常；computeAllPair另有局部第五个pairing_heap，其>=比较不满足严格弱序，且位于LACAM分支选择之前。这些源合同问题不能由纯LACAM名称或种子消除，不等于已运行观察到崩溃或性能损失。实际Boost版本尚未绑定，72E5所核单一版本只给条件合同。后继可明确设计修复适配器，但须列初始化/失败/线程生命周期/比较器及预处理费用的完整修改合同，保留原版身份；当前没有修改源码或据此计查询策略优势。此草稿尚未将LACAM类别或任何修复适配器静默定为主源，最终选择和scope须在固定前唯一登记。

## 10. 外部原法、守卫适配与原样检查合同

外部原版固定 [Kei18/time-independent-planning v1.0](https://github.com/Kei18/time-independent-planning/tree/755a7ce740d49543b1165403371752c08e342ca4)，commit 755a7ce740d49543b1165403371752c08e342ca4。NATIVE-TIP保持原字节与原误差/通信域；共享比较器明确称TIP-MCP guarded adapter。源mcp.cpp先nextNode后isStable、末下标访问plan[t+1]的静态缺口已亲见，不先修原版也不把其越界记作本方法优势。

守卫版每次激活先验证c的定义域；本地末下标直接HOLD不访问nextNode，否则唯一下一原步plan[c+1]。WAIT仅合法POLICY消费一次，MOVE no-start/在途不消费；仅中心READY后消费并转CONTRACTED，在此之前用保守EXTENDED表示tail=plan[c]、head=plan[c+1]。他者getT只用同计划代际已交付Kc下界和固定原计划依赖，未知返回WAIT；同一臂已付费CURSOR证据可复用，不免费读他者真实c/head/tail。守卫、单中心/物理接口和付费通信是显式变化，不宣称恢复原最小通信量定理。

补充匹配计划族在每公共block以同固定源和确定的R0计划输出供全部比较臂，生成授权之前先登记来源/作业/计划身份，不能从某策略成功结果挑计划。计划必须非空、vertex及完整no-following合规，含末端永久驻留；不适用登记INAPPLICABLE全行保留，主lifelong仍保留该公共来源。该族是有限计划的完成/服务/成本比较，不冒称TIP有相同lifelong分配算法。没有合法匹配block则补充族UNINSTANTIATED/UNESTIMABLE，不能隐去外部基线。下一episode只有全部旧责任合法drain后同规则重新INIT，不能reset未完成机器人。

另保留真实已发表lifelong外部候选Hönig等RA-L2019：原文IV-C/Algorithm2有ADG前驱闭合commit cut和规划执行重叠，不能称其只有single-shot。73L1完整作者PDF及两个作者库头文件已核；当前库4c75fa20c435c440d8b6bd6dc81668ddc7296ba0不是已证2019实验提交，尚未取得整套ADG/monitor/仓库任务驱动原始身份。其native必须保留原动作状态/Type-1与Type-2依赖/任务规划及适用前提；若用共同PIE来源则必须明确叫共同来源ADG执行适配，不能冒称整法原样。

guarded Hönig候选要求共同K/控制、付费完成证据/队列信息、不可撤销旧动作、cut快照与接纳检查、真正服务计数及全部ADG/规划/通信费用；新gate只延后原动作、不偷换MOVE，不继承原活性/平滑性保证。原法允许队列连续执行而本底座要求逐边参考零速和付费交接时，须公开适配限制、分列native/guarded，不能把新增等待归罪原法。该比较的整法身份、任务接口及组合合同尚未全闭，当前不能宣布主lifelong外部对照已冻结；内部R-S/E0与有限TIP族不能抵销此缺口。

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

## 11. 公共来源、完整选择器与比较预注册

只登记已经核验的公共源元数据与未来选择函数，不读取旧35–38、Q-CAL/Q-CONFIRM载荷或桌面。R0 lifelong tree=22ae3c8b3ad1f4791bd8c15b7d7b5521ed043c17；city=3e12a4483e615cd1a261d1e2476a29294fa4d0d1、game=8d8f8fbe8d16d80f5dab7a5cbf5ab6f3a341215a、random=2264326dfda14559e0db92e1649aaf512f9ff98f、warehouse-s=60b252f11972fed7d12f00960a7c6738b3f35a19；delay tree=4e3fe329a547e682d1520047bf767a5397b3b43f。它们不是已生成的实验实例。

未来获准合法绑定后，按固定树规范相对路径的字节序枚举四类别全部JSON；用原driver的mapFile、teamSize、agentFile、taskFile、delayFile字段，位置为L101/112/114/115/150，固定driver SHA256 3198636d1114e4901c9aae48d549787c9fb3bc3a0bdfd49b6445d81bb5fc4f44。引用相对JSON父目录解析，规范化后须仍处同一固定公共树；拒绝外部绝对路径、未解释符号链接、缺blob、非法编码/语法。源图/agent/task/delay的索引/长度/静态通行和初态合法性分别给理由。teamSize只待density N合法绑定后检验原义相容，本阶段不按文件名取N或猜robotFile字段。

规范source_id=(category,map_blob,agent_blob,task_blob,delay_blob,assignment_strategy,parsed_semantic_options)。同语义别名合并并保留全部alias；同task跨地图建立incidence，不假设严格嵌套。各类别完整采用所有静态合法来源，不按原规划是否快、某策略能否成功、预期效应/可见性筛选。静态排除保留路径、身份、失败谓词与证据，动态失败不改roster。任一必需类别无合法来源即UNINSTANTIATED，不拿另一类补齐或重新分权。

future manifest必需字段：全部源身份/alias/解析字段；官方与适配版本；原任务策略与合法分配初态；物理、可信观测、普通错误及故障profile的有限函数/语法和适用域；几何表示/初态证明；原参数语义和待授权绑定；公共O、固定评价窗口/设计暴露E与cutoff；服务能力、费用、精度、指令/浮点语义、编译器/ABI/库版本、clock/RNG外部接口；重复索引和独立block根的角色派生规则；各臂及native/外部族适用性；计分、停止、缺失、权重、推断和报告合同。当前各载荷、种子、表和绑定均未生成，manifest状态UNINSTANTIATED并不伪装实际检查通过。

共享四臂D-S、R-S、D-F、R-F维持相同物理控制/静态K、原PIE提议及参数含义、可信字段与可购买能力、共同O/容量/费用函数、原任务流/分配规则及外生创新函数。真实派单/请求/payload按各臂自身闭环产生，规则相同不要求实际派单次序或证书逐字相同。它们共同使用G-GEOM建表制度以分离D/R与S/F；这不能代表最便宜的F实现。E0不主动生成POSITION，也不做无用途lambda预计算，保留同M0/Mask(E)检查、CURSOR/TASK/PRECHECK/END/grant/READY等必要共同服务，费用照自身实际工作计。它没有更差的底层控制或信息真实性，只选择不购买途中进度。N-GEOM/G-GEOM的补充比较固定同一查询策略与S，在同输入的离线集合函数合同之外另报NATURAL闭环费用，不能为同迹强行冻结物理。

唯一确认主估计仍为NATURAL的D-S−R-S；STRICT仅检验固定预付供给的机制，S/F、G/N与交互为预先列明的次要分析，不择显著者替主效应。E0是必报实用性比较：对D-S−E0给同总体的点估计和预定有效区间；声称“中途观测值得购买且值得定向分配”必须两项均有正证据，任何一项不支持都保留。三臂分数不齐不能给这个合取结论。主D/R比较本来已用固定Z的合理S，新增朴素几何不是首次补上空间安全。

权重固定为四类别等权、每类不同map_blob等权、每map内不同合法source_id等权、每source内全部预注册profile等权、每profile内固定重复索引等权，其乘积为w_b。不按运行后可发布性、完成时长、成功或故障删行/重归一化。目标仅是这个固定来源组成下的创新期望，不代表所有未来仓库。计真实Q/E，另报实际到达、最小间距/安全认证状态、未完成和停滞、全队/局部等待、观测采样至交付时滞、planner超时、中心排队、通信/实际工作/内存、首次/复用/失效成本；退休次数与瓦片数是机制量，不替代Q。

空间profile必须包含不能由时间重参数化消除的横向偏差见证，并区分无普通误报的准确采样层与普通误报/丢包压力层。配置选择由明确模型/控制假设和预先登记来源决定，不以调大误差或延长处理人为制造收益。两台LIMO不赋density N，现有平台接口只支持可选现实假设检验；大规模lifelong纯仿真为主，连续安全评估不可退化成只检离散端点。native与guarded外部族按§10保留，适用性缺口不由共同底座消除，原源码失败不当新方法获胜。

profile总体分层必须事前唯一：MAIN_IN_MODEL只允许§3可信物理条件及§9所列模型内通信、普通反馈、no-start和分量故障机制；STRESS_TRUST_PHYSICS专门声明会破坏这些前提的机制。成员资格依据生成机制/支持集及来源定义，不根据运行后是否真的breach归类。MAIN中的意外breach保持原主行及失败标志，不能改挂压力层后删去；压力层单列自己的固定权重和描述，不能在主显著性不够时混入。四类别/map/source/profile/repeat的主w_b仅在MAIN_IN_MODEL的完整事前roster定义；任何类别/必需profile无合法成员时UNINSTANTIATED，不运行后重归一化。静态合法性、软件初始化成败与实际结果选择是三种不同事项。

来源补核73L2只证明Moving AI官网明示ODC-By及其数据/独立素材权利区分、游戏地图研究分发说明；未建立R0四类具体blob到其上游的连接。R0 MIT与官方目录非空不能关闭全部素材来源链，72L2/73L2均未读map/task/config载荷。此草稿的选择器仍是未来静态合同，不冒称合法source_id已实例化或某篇论文官方样例已经复现。

## 12. 故障停止、总分类、评分与固定总体推断

本稿新增、待审的基础区分是WORLD_GIVEN与软件INIT。给定静态合法设计X，数学初态t=0已规定每agent真实位置/参考原点HOLD/误差z、真实任务账本A和bootstrap resident覆盖E_i；各E_i的Mask不交且静态安全。这是所有共享臂相同的纯仿真世界/可信基础设施初态，不是某算法免费读到真值或已完成几何建表的结论。软件未就绪时低层只能持续该bootstrap HOLD，原世界z闭环仍演化；中心失效/INIT未完均不得删除bootstrap责任或让机器人消失。中心的应用索引、可读知识及规划worker尚未建立，仍须付费INIT才能使用，不从数学初态直接给查询策略全图/全状态。

软件INIT只在自身付费输入复制、核验、索引和协议初始化完成后，以相同agent/起点/几何/会话绑定，将已经给定的bootstrap责任原子接续为软件可用resident，并发表共同初始知识。失败/延后不部分转交、不发新MOVE，初始实体覆盖一直保留；成功转交前后均为同E_i，不能新造安全空隙。其保持理由是BOOTSTRAP期间参考原点不变、§3的z闭环持续在Z、F/障碍/会话未改变，因此整个E_i一直有效；并非以过时的一个t=0真实点证明接管时几何。底层HOLD和可信身份必须已具备，不得反过来依赖尚未完成的软件INIT才能执行。前提破坏按预设Stop/flags，不能继续引用保持证明。这比72的“软件INIT之后才有物理评分域”有实质变化，须独立审查，不由旧INIT证明自动继承。

真实TASK_SERVICE从公共世界t=0起按同A、实体资格及Stop规则发生，软件初始化本身不是服务资格：未初始化算法保持初始位置也可能已在合法目标上服务，是否Q=0由真实事件决定，不能由INIT状态赋分。所有软件INIT/预处理费用纳入同固定E和服务容量，世界创建/仿真宿主/共同控制基础设施的实际成本另完整报告，不能将算法特有工作改名世界创建。数学上给定合法初态不等于真实机器人免费标定/部署；本主θ是该共同合法待命世界中的lifelong任务效应，初始化成功、真正MOVE启动、首次总费用和可观测评分联合报告，不能只给稳态曲线。

静态WORLD输入非法或未绑定时没有合法设计X，保留完整静态排除理由并不产生数值推断。已入固定roster的世界丢失/主机未发起不能事后改记静态非法来删行。HOST_NOT_LAUNCHED/日志丢失不同于软件INIT未就绪：即使数学潜在轨迹在合法X下有定义，也没有观察证据据以输出某个Q。源未定义行为/算法映射不闭仍导致INFERENCE_UNAVAILABLE；本世界初态约定不能修复源码语义缺口。

任务环境必须独立软件READY而总定义：A的初态、每个有限TASK_SERVICE行的至多一次合法队首完成、§8的共同补给/空任务规则、全局次序与去重都由可信世界环境继续执行，不能下一任务突然改由未初始化的中心创造。评价器知道真值只用于定义/核验世界事件；执行基础设施只维持已给HOLD或已证旧控制责任，不免费替中心核验新MOVE、读全局阻塞或发布进度。新增动作准入/证书仍走全付费接口。

本E的起点是“共同合法待命物理世界已给定、应用初始化尚可未完成”，因此包括软件INIT/运行费用，但不自动等于从真实机器人上电开始的部署性能。世界/可信底层准备成本即使另报，也不能将本θ改称完整硬件部署吞吐；算法特有的建表/校准不能迁入公共世界准备。是否保留与72相同的静态支持集须按§4原先已有的初始Mask不交与§11选择器逐项比对；本稿未求值roster，不提前称支持集等价通过，也不以更窄INIT成功族替代用户的大规模任务。初始化分离的接口、费用、总轨迹和支持集仍是固定前核对项，不提前判S4已闭。

先区分分量故障与全臂评价Stop。合法no-start、普通误报/重放、通信分区、中心fail-stop、planner合法超时/NO_PROPOSAL等在模型内按既有责任继续物理推进至预先cutoff；不能因中心已停止就把在途机器人或后续合法服务计成不存在。planner隔离worker的SOURCE_ERROR/INVALID_OUTPUT亦不清空物理世界；保留故障标志，只有已接纳原段可继续，没有新原段时合法HOLD。明确原停止预算可禁止后续新工作，旧物理仍遵守覆盖与模式合同。

全臂Stop只取公共顺序最早的预设CUTOFF/STOP、不可认证的物理推进、物理/信任前提破坏或无法维持定义的协议状态；事故触点可被精确认证时截断到该触点。并列按下述主类优先级记录，同时保留全部次级flags。Stop截断原区间，之后不再服务、不继续到刚好完成、不释放责任；这是评价函数的终止约定，不是声称真实车辆已安全停下。评价器/日志损坏没有可证Stop前缀时属于未知评分，不伪造零结果。

Classify为总函数并与Score分开：缺设计绑定→UNINSTANTIATED；静态WORLD初态不合法→INPUT_INVALID/NOT_ADMITTED；主机/评价器未实际发起或无其可信回执→NOT_LAUNCHED；WORLD已成立而软件INIT未形成合法应用提交→INIT_INCOMPLETE；界内可证实体碰撞/互斥破坏→SAFETY_VIOLATION；物理/信任越界→MODEL_BREACH；协议/身份/因果或源未定义访问→PROTOCOL_OR_SOURCE_INVALID；数值不能认证→UNKNOWN_NUMERICAL；评分前缀缺失/不可信→UNVERIFIABLE；其余已证不可恢复执行故障→EXECUTION_FAILURE；完整合法窗口至预定末端→COMPLETED_EXPOSURE；早于末端的合法cutoff/STOP→ADMIN_CENSORED；其余TRACE_INVALID。按此优先主类同时保留所有flags。INIT_INCOMPLETE只描述软件状态，不能自动取消已经存在的WORLD物理前缀、直接填零或推评分缺失；NOT_LAUNCHED也不能与之混用。安全域独立为VIOLATED、VERIFIED_ON_PREFIX、UNKNOWN或OUTSIDE_MODEL，没发现碰撞不等于已验证。

软件INIT_READY是对给定WORLD初态/身份的付费应用核验、索引初始化及bootstrap责任合法接续，和首次ACTUATOR成功START不同。初始化/预处理费用在同E内，慢臂不重开窗口。WORLD_GIVEN成立但INIT未完时仍有合法HOLD物理前缀；以完整真实TASK_SERVICE计数可Q=0或Q>0，不从INIT标签直接赋值。已有合法世界后立即发生可定义Stop、零前缀可验证且无此前服务时可Q=0；主机未发起臂、日志损坏或不知道WORLD/前缀是否合法时仍UNVERIFIABLE。任何数学潜在量与实际已观察分数都须分开。

全roster还必须报告联合结果，不将它们任意加权成一个奖励分：各臂软件INIT是否在固定E内完成、首次MOVE是否发生、INIT完成时间（未完成/未知明示）、INIT/预处理及全部费用、WORLD/前缀/评分证据可用状态。所有概率/比例分母按固定roster；状态未知只给已证真/已证假/未知及相应识别界，不装作已知失败。主机缺日志只能给本来有定义的指示量/分数的观察不确定性，不能反推初始化失败。不得改报各臂成功初始化者各自的条件吞吐差来替代主θ，亦不选择事后共同成功样本。

observedExposure为Stop前已证物理区间长度之和，空则为0；合法resident HOLD也算，未认证积分步、仅排队的主机时间不算。设计分母E_b>0由预先固定完整评价窗口给出，保持既有保护参数含义，不以observedExposure、初始化完成时刻或实际完成耗时替换。比较对象是固定窗口中的服务表现，不能事后缩短失败臂分母。

每agent每公共TASK_SERVICE行最多服务一个合法已分配队首；相同目标的不同task_instance_id可分别完成，同一实例/重传不重复计数。评分证据包含assignment/task_revision前后、service_id、真实模式/实体服务区域的证据、行序、Stop边界及去重。Q只取完整真实服务前缀；Stop前已发生而证书后送达的服务仍计入，普通COMPLETE、查询归因或READY是否到达不决定Q。Stop后约定无新服务，不再仿真补满E。

Score输出VERIFIED(Q,observedExposure,E,flags)或UNVERIFIABLE(reason)，以WORLD_GIVEN及完整可证真实服务/Stop前缀为根据；不以软件INIT_READY或首次START作为潜在Q定义的必要条件。缺日志/主机未发起不能填零。源未定义行为、适配语义未闭或同能力对照不成立时，即使物理服务可数也仅作描述，相关因果比较INFERENCE_UNAVAILABLE；合法搜索超时/无解/模型内通信或软件初始化失败则保留全roster分母和实际可证物理服务。主D/R推断需两臂所有预定block评分完整，D/E0与合取需三臂；缺失整项比较UNESTIMABLE，不删行/改权重。

条件于固定合法WORLD设计X及全部方法动态映射良定义，主d_b=(Q_D-S,b−Q_R-S,b)/E_b，theta_DR=Σ_b w_b E[d_b|X]，Delta_DR=Σ_b w_b d_b。Q是物理世界真实服务数，软件INIT未完不使其消失；若bootstrap/环境轨迹定义本身缺失，此X不能满足本条件，不套区间。Qmax_b为公共O允许服务的(row,agent)对数，每臂0≤Q≤Qmax_b、|d_b|≤U_b=Qmax_b/E_b。创新根只按block相互独立，块内各臂可相关；同地图不证明独立，跨block共享扰动或按结果改排程/学习违反条件。

沿用既定95%约定alpha=0.05（不是保护实验参数赋值）：radius=sqrt(log(2/alpha)/2 × Σ_b(2w_bU_b)^2)。CI_DR为[Delta_DR−radius,Delta_DR+radius]与已知目标范围[−Σw_bU_b,Σw_bU_b]的交。全U=0时theta=Delta=0，返回退化区间，不除零。缺绑定/空必需类别→UNINSTANTIATED；必需评分未知→UNESTIMABLE；权重/E/bound/独立性或来源比较域无效→INFERENCE_UNAVAILABLE，均不输出虚假数值CI。

证明：Y_b=w_b(d_b−E[d_b|X])的支撑跨度为2w_bU_b。有界变量对数矩母函数的二阶导为倾斜分布方差，至多跨度平方/4；在0处函数与一阶导均为0，积分得E exp(lambda Y_b)≤exp(lambda²(2w_bU_b)²/8)。block独立给乘积界，Markov并优化lambda得单尾exp(−2r²/Σ(2w_bU_b)²)，双尾并合给上述区间。无需正态、对称或可交换假设，不对固定地图重采样来冒充泛化。

对theta_DE0用相同设计/权重/界构造其预定点估计与同水平CI。确认主结论只对应theta_DR；若另声称二者均正，仅在两个预定CI下端均>0且三臂评分可用时发布这个合取。原假设是至少一个分量≤0；合取拒绝是任一真实零假设分量的拒绝事件子集，故各分量有效水平不超过alpha即可使此合取错误率不超过alpha，臂间相关不破坏该逻辑。不能据此宣称两个CI同时95%覆盖或任选一个显著就成功，不更换主量为事后min或择优对照。

若固定合法机制下全部潜在分数有定义，则P(发布数值区间且未覆盖对应theta | X)≤alpha；缺失时整次该比较UNESTIMABLE保留此错误发布界。“可发布”可能依赖随机结果，不能再宣称条件于已发布自动95%覆盖；若潜在评分机制本身未定义，界也不可用。区间可能很宽，无权事后删图/改bound/增减重复/调保护参数取得显著。安全反例、停滞和E0负结果不能被主D/R的正估计抵销。

## 13. 效果充分条件、失败见证及未运行机械合同

横向偏差的独立机制：取两条同时运动的平行名义轨迹，实体支撑半宽为r_i/r_j，名义间隔d满足r_i+r_j<d<r_i+r_j+rho_i+rho_j，两者误差向内且合法时可几何相交。名义参考时间可完全相同，调时间不能把横向位移重新解释成沿原线的位置；这是误差类型见证，不是说任何时间避让都不能消除碰撞。共享稳健底座必须对同扰动保护所有臂，不能仅让原生离散PIE在新增域碰撞然后宣布新法有效。此处都是符号关系，不为保护参数绑定数值或生成运行场景。

空间退休见证可以在资源瓦片与规划格一致时成立。考虑边长ell的格图，闭瓦片以格点为中心、边长ell；K位于半宽rho的世界盒且rho<ell/2。A原边u=(0,0)→v=(ell,0)，B原边w=(0,−ell)→u，C的原边和掩码远离二者。B完整掩码只在x∈[−ell/2,ell/2]的这一列，A在q>ell/2+rho且q<ell时后缀与该列全部瓦片分离，origin资源可在到终点前退休。闭边界等号仍不可退；initial resident分离、完整原边静态合法须成立。若用更粗资源或rho关系不成立，该充分见证失效，但不能据此证明全部S均无效。任何细化瓦片的替代都须计资源数/预处理成本，不暗中改变几何分辨率来造收益。

费用及真实服务见证还需要独立事件关系：A已合法在途、B唯一原请求因A旧origin资源阻塞、RR下一个对象为C而D唯一选A；没有其他外国holder或免费终点反馈可提前释放B。存在一条满足全部费用/容量/付费采样发布规则的有限公共轨迹，使D取得足够q、完成退休和B新授权验证，并在一个公共ACTUATOR机会成功START，时间上界f；RR和E0使B首次可能START的下界分别r_R/r_E，要求f<min(r_R,r_E)。下界须涵盖所有合法中途/终点释放通路，不能只比较两个不完整的下界。

若B各臂无后续中断，且相同初态与时间平移不变的合法控制/扰动使其参考运动同长tau_B，参考终点到达分别为D≤f+tau_B、对照≥min(r_R,r_E)+tau_B；一般不同段时长须分别证明f+tau_D_upper<r+tau_other_lower。再选定一条事前公共TASK_SERVICE行t*满足f+tau_B≤t*<min(r_R,r_E)+tau_B且t*<E；它不是观察后挑的cutoff。要得到真实服务还须：D在t*仍处该目标的reference terminal/resident并未Stop；B此时仍是同一有效未服务队首、未重分配；其真实实体满足§8唯一SERVICE_TRUE全形体谓词。一个足够的几何条件是目标参考点v加K完全包含于ServiceRegion(B)，如此任意允许z都满足X⊆ServiceRegion(B)。对照未到参考终点排除其服务，还须确认同一任务实例未曾由该对照的其他合法匹配终点驻留服务，不能仅用本次到达下界排除过去服务。中心型、沿途型或额外真实停稳型服务均不是本稿主服务定义；如改用它们须重写该见证和公共任务合同，不在实例绑定或看到结果后择用。

从B的单次事件到总Q另需完整计数前提：截至t*前B在D/两对照均未计数、对照截至t*仍不具服务资格，所有B之外服务事件的总计数在D不小于相应对照（可用相同实体轨迹/同队列/同Stop及同服务序列的受限见证充分保证）。此时Q_D(t*)≥Q_R(t*)+1及Q_D(t*)≥Q_E0(t*)+1。只证明B早一次而没有补集计数条件时，只能声称B的局部机制。上述充分条件并不声称实际D必然保持其他机器人的服务数；共同参考轨迹也只有在实际误差/任务与Stop条件相同后才能推出共同服务。

局部增量不能推出全固定E正差。纸面反例：预定t_1<t_2<t_3<E，D在t_1、R在t_2完成同B，随后共同C/共同行程tau；D多支付等待c，满足t_2+tau≤t_3<t_1+c+tau。若此前C无其他合法服务、t_3之后至E无其他服务行，早期D多一次，t_2追平，t_3时R完成C而D不能，固定E为Q_D=1、Q_R=2。这里c>t_2−t_1，规则/窗口均先定；这只是符号反例，无实验参数绑定或载荷。主HYP-NET必须用全roster固定E端到端比较检验，不能只保留早期见证或删除后来追平的行。

这个见证还要求固定R0确实输出上述原MOVE及匹配合法任务的来源证据；当前未生成该运行输出，所以它是结构性充分条件，不是已找到公开主roster上的获益实例，更不是主总体theta正的证据。不得为实现见证事后选cutoff、地图、profile或删无跨越样本。预注册全来源会同时保留无中途clearance、RR恰先选关键者、D反复查询失联holder、几何表低复用、中心队列拥塞、终点已足够便宜等零/负效应。

活性反例必须正面保留：在走廊/tree缺少绕行时，互相占着下一原边需要的resident可形成等待；交叉口/环路上的多agent原MOVE可能各需其他agent的起点资源。单中心整M0独占准入不自动完成同步环形轮转；查询或WAIT也不能凭空消环。全原MOVE合法不推出本连续保守wrapper有执行解。不同阻塞图component因新请求合并，仍用同一全球资源key与中心owner，不分发新authority、不让相同资源获得两owner；对独立未准入fleet的合并必须重新满足INIT/授权合同。无活性保证的失败不通过排除动态样本掩盖，也不以全HOLD安全冒称实现了lifelong效益。

封闭循环的充分负例可直接证明：取一组尚未启动且原occurrence不变的请求，每个目标顶点为组内下一agent当前resident。其M0包含该外国resident的非空终点mask，而每个resident只有自己的合法运动/交接才可能腾空；故组内没有第一个grant、正进度或原点退休。查询未启动者、未消费槽的HOLD与增大包络不能在这个封闭状态产生突破。这只是组内阻塞的充分条件，不是“存在环 iff 全队不启动”；环外可继续，无环亦可能因故障/容量不足停滞。

不能用部分预留自动修复：在当前同尺度闭瓦片、边向支撑恰为±rho且rho>0时，停在不碰终点瓦片的参考位置需s+rho<ell/2；让后继安全取得旧origin瓦片则需已证q−rho>ell/2，同时q≤s，三式不可能同真。若终点争用资源还必须等下一agent完成终点READY才移交，分段启动后仍可全部卡在终点等待环。这个推导只否定上述具体分段方案；细分资源、允许经连续认证的同瓦片联合占用或相对进度控制均需新的状态/不变量/成本与独立工件，未并入72。

同一循环也不必意味着真正连续运动无解：对正方形环的各原边，令同一进度alpha(t)从0到1，参考中心分别为(alpha ell,0)、(ell,alpha ell)、((1−alpha)ell,ell)、(0,(1−alpha)ell)。若各实体相对参考包络K为世界闭盒、半宽rho且4rho<ell，则任意相邻中心的一个坐标差至少ell/2>2rho，对角中心至少一个坐标差为ell，故所有同时刻包络互不相交。这是几何可行性的符号见证，不是已实现公共启动器或加入实验规模赋值。独立no-start/任意异步进度破坏共同alpha，因而不能把该路径当当前故障域的安全执行证据；后继若采用联合运动，须证明包含启动/制动和付费滞后信息的可达集合，而不能仅展示同步动画。

下表是纸面故障与检查覆盖合同，全部**NOT_IMPLEMENTED / NOT_RUN**，不是生成或执行测试。每项未来必须给条件、付费事件顺序、预期不变量/分类及最小失败前缀；未满足输入条件返回INAPPLICABLE/UNKNOWN而非PASS。

| ID | 触发与必须核验的结论 |
|---|---|
| W01 | 一次原MOVE：PRECHECK原slot、完整中心grant在实际START前；途中q退休、终点改resident后READY；消费恰一次 |
| W02 | 普通错pose/过早COMPLETE/未来时标：不更新可信q/c/K_task/资源或真实Q；错误未触发查询仍保守 |
| W03 | 同tid新样本先到、旧样本后到；分别检查单样本下界、融合最大值和退休提交R；只要求R之后覆盖，不回溯到旧t_j，不跨tid/几何代 |
| W04 | q=lambda闭边界、数值只有未经证近似：均不退休；合法上界近似可能更保守 |
| W05 | 参考s单调而真实z回摆：旧后缀仍覆盖；不从实体非单调错误推出可回收终点 |
| W06 | 已授未START/no-start/重复grant：全U(0)保留，不重复执行或重置s |
| W07 | BRAKE域、LAUNCH/APPROACH端点：有限参考到达、制动不越原边、HOLD延拓不计算0/0 |
| W08 | RESUME早于BRAKE结束、HOLD无限：等待合法恢复，不换边，有限P1不冒称有限等待 |
| W09 | P5同点零参考速拼接：真实z不清零；起点错位/Z缩小/F旋转/非零速是明示必要前提见证 |
| W10 | CANCEL先于首次REQUEST：合法未见e吸收性关闭，迟到首次拒绝，不出现新grant |
| W11 | GRANT先于CANCEL：取消返回DENIED_GRANT_LIVE；不发成功CLOSED，不按超时回收 |
| W12 | 中心私有作业未发布时故障：无半grant/半释放，已付费用保留；后继job不能先读旧版 |
| W13 | 终点gate latch/活动NONE而中心未知：旧端点覆盖继续，匹配lastClosed可查；NONE不当清空 |
| W14 | READY/终点ACK丢失、旧ENTRY迟到：保留或取同一收据，不重复服务/消费、不删新tag |
| W15 | 已退休旧资源授给新holder后到达旧release：expected-holder/tid不符拒绝，不删新owner |
| W16 | 同agent其他tag重叠：非当前parent不得吞并；parent E到newU(0)转换无空隙 |
| W17 | 中心partition/fail-stop、无界延迟：无新中心发布，旧运动按合法模式继续，资源不消失；不假drain |
| W18 | LOCAL CLOCK skew与消息重放：标签不授租约/清空权，权威事件序与原chrono/CPU域分离 |
| W19 | ACTIVE→SHARED-OFF→DRAIN→恢复：停止新查询/新承诺的范围明确，resident保留，旧START不复活 |
| W20 | NATIVE-COLD-OFF：共享side effects为零的原样旁路合同；不把共享OFF称bitwise原法 |
| W21 | RR初态/成员插删/空集/查询失败：同规范总规则，last按实际选择推进，不看真实s |
| W22 | D分数同p多资源、tie、无正分：去重、最早贡献p再tid、回退RR；全扫描/索引维护计费 |
| W23 | QUERY选择尚未完成：没有可见POSITION；不能免费读全局再事后补费用 |
| W24 | CURSOR在pure WAIT前后CAPTURE：所见c按唯一采样点区分，后送达不刷新；POSITION不代cursor |
| W25 | 证据作业CAPTURE不足容量/冻结后再执行：未采样或旧不可变payload，完成/交付不是新真值 |
| W26 | 原WAIT/HOLD/MOVE槽：起始slot k、目标k+1、READY前不消费，初始驻留可合法服务 |
| W27 | 真实greedy任务次序与滞后快照：不虚拟抢未分配目标，不拼修订，不按查询归因筛Q |
| W28 | planner期间c推进、目标改变、过期CAS：重验最新已知输入，拒绝陈旧结果并保留丢弃费用 |
| W29 | 原chrono暂停/排队与CPU日志：经过钟含世界流逝，CPU钟只累已供CPU，保留源预算/比较语义 |
| W30 | 空目标/非法路径/源_exit/随机比较器定义域：NO_INPUT或显式源失败，不补MOVE、不杀真实评价器、不计优势 |
| W31 | TIP末端nextNode越界与guarded定义域：原问题保留，守卫不越界；完整no-following不适用全列 |
| W32 | 无对应本臂消息/有限copy/同t多行：NO_REPLAY_TARGET，严格后继发布，无跨臂payload或零时无限级联 |
| W33 | 静态WORLD非法、HOST未发起/缺日志、WORLD合法而软件INIT未完、合法全HOLD/零前缀Stop分别判断；软件INIT标签不直接决定Q，完整物理服务前缀才可评分 |
| W34 | cutoff穿过物理段、先真实服务后送证书：精确截断，不补末后服务；完整先前真实服务仍计 |
| W35 | 数值不能认证或评分日志缺失：UNKNOWN/UNESTIMABLE；空合法前缀暴露为0不自动SAFE |
| W36 | 同目标不同实例/同实例重复：分别可服务和幂等；Q≤预先公共TASK_SERVICE对数 |
| W37 | G/N同输入精确集合及不同处理时刻：语义相等不强迫闭环同迹；E0不付无用途阈值费 |
| W38 | D胜R但不胜E0/无服务跨越：只保留限定增量，不宣称整体观测划算或用局部见证外推规模 |
| W39 | 空必需类/动态删样/改权重/跨block随机共享/按发布挑结果：禁止对应固定总体区间或明确不可估 |
| W40 | 走廊/tree、交叉口循环、饥饿、component合并：覆盖不等于活性，失败进入全roster，不私添绕行 |
| W41 | 可信Byzantine/实际控制或几何界外：MODEL_BREACH并保留碰撞；界内反例不得重新归入界外免责 |

未来机械接口：VerifyManifest检查固定来源/字段/alias/适用性、未改原参数意义、有限O/费用/精度/独立根/权重，返回VALID/UNINSTANTIATED/INVALID及证据；CheckProposal将每个原MOVE/WAIT、slot/c及append对应回固定源job/输入/输出版本；FoldLedger按付费发布全序重放owner、watermark、PRECHECK、grant、closed、READY、CANCEL及模式，失败给最小行前缀；CheckGeometryAndControl以精确或保守区间检查整个连续段及P1–P6条件，不能决定则UNKNOWN，不以端点采样代替扫掠；CheckEventsAndCosts验证每种机会、实际作业/采样/发布/attempt/copy/clock/RNG与所有队列/失败费用；ClassifyAndScore按§12给全部类/flags、安全域、Q/暴露/E和缺失理由；Estimate按固定比较所需臂/范围输出估计/区间或明确不可实例化/不可估/域无效。

另有NativeIdentity合同：固定源码与编译/依赖/原输入/时钟随机环境，比较冷旁路与直接原入口的用户可见输出及原状态副作用身份，不借新共享初始化改变原随机消费；实际并发/时钟环境无法固定时不得声称bitwise等价。TriggeredRefinement合同检查公开触发/已知前缀决定模式、动作仍只原MOVE、保护未触发时资源责任不断、切换/取消/退休全合法。两项当前未实现未运行，与共用物理adapter和原生域的边界必须同报。

所有未来检查绑定被检程序/依赖/输入/科学规格版本、覆盖域及原始输出。即使某checker全绿，若漏W01–48、仅逐帧看图或把自写期望复述一遍，不构成验收。现在不创建测试、运行模拟器或读取受限载荷给这些合同补假回执。

新增纸面合同同样NOT_IMPLEMENTED/NOT_RUN：W42，END/FINISHED后READY未消费，旧Kc再次提原u→v必须因pending/未END/原起点至少一项拒绝；W43，后继PRECHECK成功后旧READY重复不改c/parent/相关版本；W44，LOCAL_POLICY逐个纯WAIT消费而中心Kc滞后，不靠本地分支免费派SOURCE_REQUEST机会；W45，参考到达但实体不满足服务域，不能计真实B；W46，局部B领先而补集计数变差或固定E追平/反超，不能套总Q充分条件；W47，Srv_C持槽等待远端回复的错误安排应违反服务合同，正确异步消息流各自释放槽且所有传输/接收付费；W48，WORLD物理初态、算法INIT状态、HOST日志可得性分别按下述新初始化合同判定，禁止将软件INIT标签直接变成零分或丢行。

## 14. 继承异议、证据范围与最终验收要求

71R4六个主题逐项承接：T1迟到首次请求/关闭竞态对应§5的UNSEEN取消和已授拒绝；T2 RR全集/初态对应§7；T3源时钟/暂停/原预算对应§9；T4采样线性化对应§6/9；T5可信逻辑cursor与pure WAIT公平对应§6/8/10；T6 INIT与首次MOVE评分对应§12。它们是新候选提出的关闭证据，不回改71的十条原意见、69的九条或任何审稿票，不能以删去一种协议的名称代替其安全责任。

完整方案对早期交接要求的对应也必须核：实际空间误差而非delay改名（§1/3/13）；保留PIE原提议与可证制动/HOLD（§3/5/7/8）；唯一authority、资源ID/epoch/fencing/幂等与origin释放/destination接入/edge-in-progress（§4–6）；lost ACK、分区、无界延迟、clock skew、走廊/tree/交叉口/饥饿/component merge（§9/12/13）；原样与共享适配、inactive与triggered机械合同（§7/10/13）；纯仿真全成本/主次比较、公共源、独立配对、失败分母/缺失/删失/固定目标推断（§9/11/12）；全部来源阅读强度与近邻（§2/10）。静态几何mask同时覆盖顶点、同向/反向边扫掠及实体起终点；若某未来adapter只检vertex/swap而忽略连续mask，不能继承P3。

来自72M1的P5构造、72B1的朴素几何/P6/强对照及追加统计建议、72D1A的网页路线分析、72C1的Claude完整建议，以及71E2–E4、72E1等来源回执均为实际NONBALLOT协作，根独立筛选后写成本正文的自给规则。顾问只读的旧72快照不能冒作现在字节的审查。普通报告错误共同隔离、几何阈值、阻塞数量启发式、中心事务与冷旁路都不能各自重复认领为原创；Zhong等已联合考虑观测与重排费用，WinkTPG/SCALE等已有冲突选择/前缀保留近邻。没有根已核的一手证据证明本组合无人做过或在大规模必然正效应。

六门含义维持：G1实际误差问题；G2已发表锚点与诚实路线比较；G3固定R0/适配/原样合同；G4已发表外部基线与适用域；G5公开来源和场景协议；G6物理/算法/资源/费用/评价公平闭环。最新有效根裁决是72R4的2 PASS/3 UNKNOWN/1 FAIL；本73草稿不自授资格。S1前向证据、S2终点/权限、S3真实服务、S4WORLD/软件INIT/总体、S5服务拓扑在本稿提出实质修订，均须新字节核对和顺序审查。S6源定义域、S7素材来源/合法source、S8主lifelong外部比较、S9规模/可证伪范围仍有明确待补证据；不能由章节齐全判闭。

最终完成性审计逐项指向实际证据：交接文件与全部任务真实状态/身份；至少十二项相关一手来源及四份期刊全文的真实阅读、其他来源缺口和差异矩阵；原源码接口/许可/原法检查合同及外部公平域；P1–P6与所有资源/事件/模式/失败总函数；全roster与各比较/评分/区间的适用性；W01–48及所有未运行机械合同；本新字节完整固定后的科研导师skill→Nature reviewer skill→完全不使用任何skill且不读他路意见的独立逻辑→根逐条验收；每份必要skill意见后根另做不用skill的直接分析；私有GitHub精确同步和全历史冻结/只读/保护边界。阅读缺失、报告无效、间接一致或仍UNKNOWN均不能计完成。

H、T_delay、B_CAL、B_max、B*、P_active、density N原义保留未赋值；只进行来源阅读与文档构造，未实现、构建、创建或运行测试、仿真、调参、生成seed/tape/实验载荷/结果或实车动作。旧35–38及受限载荷禁读、桌面只读；69–72及其报告不改不封存。本稿尚未固定或送审，所有来源/协议/资格及顺序审查闭合前保持HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。实验前目标未完成，不以版本/篇幅或审查次数宣布完成。

## 15. 前缀扩展备选：已证层、尚缺层与采用条件

73M1与73P1完整建设性回执给出同原MOVE的单调cap数学构造；这是针对整M0在同步环上不能启动的实质备选，不把整边版作为唯一最终答案。初步能力链是0≤q≤s≤C≤b≤ell：q为已发布可信下界，C为本地已安装cap，b为中心已兑现保留cap。中心先预留Mask(U(q,b'))再发布b'，不撤回旧cap；迟到/未接收扩展仍可按旧C运动或HOLD，不允许中点END或消费原c。

控制接入：合法cap增量保持v²≤2a_hi(C−s)。正在运动时新r=v²/[2(C_new−s)]落至a_lo下，可用原正LAUNCH从非零v有限重新相交，G=v²−2a_lo(C−s)有导数2v(a_launch+delta+eta+a_lo)>0；新r在原带内继续APPROACH。BRAKE优先保持至HOLD，cap扩展不自动恢复；仅真正到ell才原END，最终HOLD/no-start不推出有限到达。真实z全程不重置。这里新增混合接入尚未纳入§3工作版。

有限闭凸有理矩形瓦片与凸K给I_r=[a_r,b_r]（可空），于是r∈Mask(U(q,b)) iff q≤b_r且b≥a_r。一般闭非凸瓦片不保证区间；有限凸分解才可给有限区间并。联合q退休与cap扩展必须从同串行快照原子提交新增/删除，验证q'≤当前s≤旧b，前后均覆盖实体；已发未收cap不能因超时回收。凸情况下单occurrence每瓦片至多空→占→空两次，有限并集至多两倍区间数；不界定失败重试、消息负载或全队总成本。它是精确几何/覆盖定理，不是大规模吞吐或新颖性证明。

根已纠正73M1支持函数反例：实体当前z固定，不能对任意z把包络support当实体support；存在性反例需明确选Z投影极值并用合法常w=κz保持。73P1又纠正原提示仅闭瓦片的凸性缺口，原报告字节保留。前缀数学和旧T1角色可组合的方向已有依据，正式采用还必须自给固定cap请求/扩展总策略、途中HOLD证据/恢复费用、D/R/E0同能力、所有事件server/写域及故障/窗口交接；不能把两份NONBALLOT相加即作全协议通过。

采用前缀应保留整边基座作可解释对照，并让强R-S/E0也拥有相同分段权限/控制；D的增量才是付费证据选择。闭瓦片与规划格同尺度时的旧中点矛盾仍是失败机制，细化资源要计数量/索引/预处理及内存，不能免费换分辨率。最终主路线须由完整协议、已发表近邻和公平主比较证据选定，不能因为某种较窄模型更容易通过就代替用户大规模lifelong目标。
