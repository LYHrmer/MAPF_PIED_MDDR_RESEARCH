# 73C14：可信参考进度精度与付费数值证书窄建设题

新题 NO-SKILL / CONSTRUCTIVE / NONBALLOT，不是正式审查或资格票。禁止工具、skill、搜索、代码/伪代码、运行/仿真、参数赋值、生成载荷；只分析下列已亲核科学条款和一手接口。末尾必须 END-C14。不得重跑 C12；它已 timeout/exit124 且无意见。不要看成要把现候选强行评为可行。

输入73在捕获时完整身份为 SHA256 656cfdc496154a0d1a640f7ac7364a7fa854a0a5be120be33c29204dbe8151e2，178035 bytes /575 LF，文件73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md。本代理科学读§3/6/15及§5精度与§9必要服务窗口；根后继可能改其它窗口，以下只绑定这一输入。所有资格 HOLD，不给任何保护参数数值、默认或范围，也不偷设 epsilon=0。

模型§3：同原边u→v，ell>0，e=(v-u)/ell，实体 X=u+s e+z+F；z_dot=-kappa z+w，w有界可测，Z包络及实体偏差与参考进度分开。参考 s_dot=v_ref，v_ref_dot=a_cmd+eta，|eta|≤delta；已有符号条件0<delta<a_lo<a_hi、a_launch>0。s单调，0≤s≤本地已安装累计cap C≤中心已授b≤ell，v_ref²≤2a_hi(C-s)。算法不直接知道s或C，不允许从pose/普通反馈拿可信进度。

LAUNCH：xi=C-s>0且v²<2a_lo xi时 a_cmd=a_launch+delta，直到首次v²=2a_lo xi。APPROACH：xi>0，r=v²/(2xi)处于[a_lo,a_hi]，a_cmd=-r+delta(a_hi+a_lo-2r)/(a_hi-a_lo)，r_dot=(v/xi)(r+a_cmd+eta)。到cap按理想混合接点延拓s=C、v=0、HOLD，不算0/0。BRAKE：a_cmd=-a_hi-delta直到首次零速，之后HOLD。参考HOLD是模型公理，实体z继续动。cap安装不跳s/v/z；若原LAUNCH/APPROACH，按新r选择LAUNCH/APPROACH；BRAKE不可提前取消；HOLD安装后仍HOLD，需要后继新的RUN。同刻旧cap到达先HOLD、后安装，不能自动续跑。原ell的END永久关闭旧tid。

POSITION§5/6：固定服务profile事前给精度epsilon_i，与实体跟踪误差不同，不为组是否通过而临时选。合法同tid采样须有max(0,s-epsilon_i)≤q_sample≤s。初始组 c_i 来自有限几何阈值，l_i=max(0,c_i-epsilon_i)；组B包络用这个下界。只含真值却总给[0,ell]不足以证明组可推进。

服务：QUERY先在Srv_C付费选择已知阻塞者，只提交一个POSITION请求；Srv_E(i)新鲜authority作业首个语义操作是付费原子CAPTURE，发生于公共行物理推进及先前结果发布之后。没有完整CAPTURE容量就不采样。只匹配指定当前tid或保留同tid终点记录，NO_MATCH不能当清空。CAPTURE固定唯一sample_point和不可变版本根；后续数值计算/复制只读冻结内容。作业处理期间世界照走，AUTH_COMPLETE不得刷新采样点；后继通道发送/接收/验证/中心退休均收费，中心之后才max更新同tid q。旧tid q不能用于新MOVE；E0不请求POSITION，F_cap只记q_evidence不退休。传感创新若用，只能按当前请求key，不可用未来真值。

公共O有限，PROCESS_SLICE每行给固定server有限容量，单writer/单作业槽，作业跨行续算但不新增机会/容量；全部请求、CAPTURE/区间数值封装/复制/位长/消息/验证/失败/GC收费。物理控制/守卫及真实环境服务另有共同明列费用，不被应用槽锁住；不能把业务计算藏进元评价器免费完成。CAPTURE即使固定大历史也只能先pin不可变根，后续遍历另费。无后续容量可到Stop而不完成，失败不能退款。严格指令/服务后端尚未合格，不调查QEMU。

§15进展是条件命题：合法组的成员最终到各自初cap后，还需真实的后cap新鲜CAPTURE、足精度证书付费交付和q_release提交，或完整物理END到中心FINISHED链。早采样晚送达不算后cap采样。有限O不会自动提供后续服务。精度未闭时NO_CERTIFIED_GROUP；不能靠永不出证书的安全包装宣称具备有用精度。

当前识别的难点，请独立核而非顺从：只给命令和eta界，不给实际已发生eta，初期合法LAUNCH中两条eta取相反允许端的轨迹可有相同可见信息但不同s；其进度差随该段时间增长。对任何共同下界，若两条可行s间距大于给定epsilon，就不可能同时安全且满足精度。提高浮点位数不能消除这类信息不确定性。不能把全知评价器的s或未来eta/w从私有seed/日志免费移给策略。

一个供挑战的具体下一路线（尚未采用）：可信参考子系统私有保存从原tid锚点到当前的有限命令/已安装cap/实际模式及已发生驱动系数的不可变表达式历史，WORLD和该子系统的一致性必须认证，算法拿不到history/seed/eta/pose。纯仿真表示profile可选择eta在已有公共O的相邻不同时刻之间分段常值，每段系数由原世界私有创新接口生成且可有限精确表示；不增加采样窗口或机会，值/分布/manifest未赋。这只是原有界可测域的一个明确可计算子类，不能冒称等价于所有原扰动。CAPTURE只pin截至采样点的历史前缀，截去未发生尾；后续可在Srv_E付费重新包围该时点s，不能读刷新后的状态。维护历史、精确系数解码、证明/区间更新若属于控制公共能力也须明列成本，不能以共同底座为由免费替POSITION做好业务计算。

有限表示目标：证书用精确有限dyadic端点L/U（整数及二进制指数），且含采样时真实s；传输保持这两个有理数不经裸double/无半径十进制破坏下界。q=max(0,L)。若含真值及实际外向端点宽度U-L≤已登记epsilon，则q≤s，且s-q≤epsilon。可直接用L作wire下界，没有暗增一次未计量量化误差。epsilon来自固定服务合同，不是为几何挑的精度；不足则继续原作业付费细化或到Stop失败，不补容量。问题是如何构造含真且收窄的L/U，不能把它重写成愿望。

供核的局部APPROACH计算：在固定C、常值eta且不跨模式/命令更新的合法段，令D_a=a_hi-a_lo，k=2delta/D_a，r_star=(a_hi+a_lo)/2+eta D_a/(2delta)，y=sqrt(C-s)。从原方程可推 y_dot=-sqrt(r/2)，r(y)=r_star+(r0-r_star)(y/y0)^(2k)。因此经过时间是积分 Phi(y)=integral_y^y0 sqrt(2/r(z)) dz。r_star与r(y)均在原合法带内，积分核正、连续且单调；可用有限二进制分割、外向端点包围的上下Riemann和，再用正斜率界包围逆函数y(t)，最后外向算s=C-y²。到y=0积分有限，避免原r_dot中除xi的奇点。积分核的单调性给和差受最大分割宽度乘其端点变化界控制；端点算术误差另显式计入。LAUNCH/BRAKE常eta时为多项式运动与其原首次守卫根；HOLD为常参考进度。这是数学推导待你复算，不是已实现求积/仿真器。

精确混合判序是更强潜在阻断：原cap到达与同刻cap安装必须到达/HOLD优先。即使进度s的区间能任意收窄，比较一般可计算到达时刻与公共时刻是否完全相等也未必有有限判定；若数值近似误选“尚未到达后扩cap”，可能继续运动，而原“先HOLD后安装”须等待RUN，后继差别不再是小舍入误差。不能凭double相等/固定tolerance偷改。若不能确认事件顺序，本题候选只能明确NUMERICAL_ORDER_UNRESOLVED、不给证书/不给错误控制，或者提出严格更小且有据的处理；不许隐藏为总能精确判定的oracle。只有局部段可计算不自动使全混合世界可计算或所有合法请求都在有限O内完成。

本次唯一新一手资料为 FLINT 官方 https://flintlib.org/doc/arb.html ，实际页面标题FLINT3.7.0-dev，读了开头球算术包含性/精度解释，以及arb_get_interval_arf、arb_pow、arb_sqrt、arb_eq/lt/le相应正文。接口承诺球运算包围精确结果，arb_get_interval_arf导出外包端点；精度参数不自动给目标有效位，输入不确定性/NaN/全区间不会因加位数消失，比较返回真要求输入区间内全部点都满足关系。arb_set_d只接收那个double值，不能自动给其上游模型误差。没有取得固定发布版/本机ABI/运行实证；该接口只支持基础包围算术，不提供本文混合系统完整求解器或本项目精度证书，不把其API存在当后台已资格。

请只交付四项：1）是否能在现有原模型直接闭精度，或必须明确增加已发生参考驱动的可信来源/有限表示；给最强信息反例但别给参数值。2）核上述APPROACH变换、积分/逆包围与dyadic下界证明，指出真实数学错处、前提和成本，不用“高精度工具足够”代证。3）选唯一可审查方案，处理CAPTURE前后版本、过去/未来隔离、同刻混合guard、队列占用、失败/Stop与D/R/E0同能力成本；无法全闭就精确判定闭到哪层，别把每次数值失败洗成合法算法零分。4）说明对§15条件进展的实际影响及最小未闭接口，区分条件模型、数学有限构造、实际后端资格，不扩大为通用硬件仿真或未来实验。给完整建设性意见，末尾END-C14。
