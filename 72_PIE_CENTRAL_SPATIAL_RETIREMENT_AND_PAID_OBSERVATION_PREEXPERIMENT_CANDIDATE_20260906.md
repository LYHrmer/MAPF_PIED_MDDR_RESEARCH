# 72：PIE 原提议下的中心空间退休与付费观测——实验前候选

2026-09-06；**DRAFT / NOT-FIXED / NOT-REVIEWED**。正文构造中，未授予任何资格门。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。71 及其报告不改、不封存；本文件是新编号、新字节，固定之后才进入正式顺序审查。

## 1. 研究问题、主张和动作边界

真实机器人有尺寸及跟踪偏差；按名义格点判断通道清空可能不安全，而一直保留整段占用又会延迟后车。研究问题是：在保留 PIE-D 新 MOVE 提议来源时，付费取得可信参考进度、只释放已经证明不再需要的空间，能否在持续任务中取得正的净服务率增量。普通反馈误报/迟报、真实空间偏差和处理耗时分别建模，随机 no-start 不能改名为定位误差。

规划层为离散四邻接图，执行层保留连续实体足迹、连续参考运动和有界跟踪误差。方法不改变原边、目标或新 MOVE 顺序；只允许接受原 MOVE、合法 COMMITTED_WAIT、阻塞 HOLD、继续旧 tid 或在已证明可行域内制动/保持。没有主动绕行、补邻边、伪目标或在 unsafe proposal 上偷偷换轨。底层参考控制是假设明确的理想执行模型，不声称已经装进 LIMO。

主共享四臂为 D-S、R-S、D-F、R-F：D 为阻塞导向查询，R 为轮询；S 为途中后缀退休，F 为整段持有至终点交接。唯一确认主比较是 NATURAL 中 D-S−R-S 的固定总体真实服务率差；策略自己的查询/处理/维护工作计入，同费用函数及服务容量。STRICT 预付等容量的机制比较、退休因子及交互另列，不择显著者充当主结果。方向性假设 HYP-NET 为该差的期望正；零或负、队列成本吞掉收益、提前取得证据却没有真实服务增量都能推翻它。不是“只要安全就算有效”。

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

选此组合的依据是实际空间包络与同原动作域可自给证明、净费用可以配对检验；不是因为71已经写了长稿。单中心是范围明确的替代，减少多owner的提交负担但引入中心队列瓶颈。异步轻量调度、局部复用和几何/控制方法继续作为机制比较对象；若需改路才能消环，就列独立规划算法域，不能潜入本wrapper。没有任何论文或当前见证保证本主总体正效应。近邻若证实已覆盖关键组合，须缩小主张、增加匹配对照或另编号换路线。

## 3. 物理域、可信条件与有限参考到达

参考边从u到v，ell=||v-u||>0，e=(v-u)/ell；本模型为固定世界朝向平移，F为非空紧足迹，Z为给定闭盒。实体 X(t)=u+s(t)e+z(t)+F；z_dot=-kappa z+w，kappa>0、|w_j|≤kappa zbar_j、|z_j(0)|≤zbar_j。变分公式 z_j(t)=exp(-kappa t)z_j(0)+integral exp(-kappa(t-a))w_j(a)da 给 |z_j(t)|≤zbar_j。因此实体速度可因 z_dot 回摆，参考 s 单调不代表真实位置单调。普通 y/COMPLETE/pose 可有错误、缺失、迟到和重放，但不驱动可信控制状态或授权退休。

参考状态 s_dot=v_ref≥0、v_ref_dot=a_cmd+eta，|eta|≤delta。选符号常数 0<delta<a_lo<a_hi 与正 launch 下界 a_launch，执行器允许下面命令范围；这些是待合法绑定的模型条件，不给实验参数数值。LAUNCH 取 a_cmd=a_launch+delta，从v_ref=0、xi=ell-s>0出发，直到首次 v_ref²=2a_lo xi。因为 F_L=v_ref²+2a_lo(s-s0)-2a_lo xi0 的导数为2v_ref(a_cmd+eta+a_lo)>0，且 F_L≥a_launch(a_launch+a_lo)t²-2a_lo xi0，交点在有限时间内且xi>0；上界 sqrt(2a_lo xi0/[a_launch(a_launch+a_lo)])。到边终点前必过该交点。

APPROACH令r=v_ref²/(2xi)，a_cmd=-r+delta(a_hi+a_lo-2r)/(a_hi-a_lo)。在xi>0时 r_dot=(v_ref/xi)(r+a_cmd+eta)；r=a_lo时括号delta+eta≥0，r=a_hi时为-delta+eta≤0，闭带[a_lo,a_hi]不变。d sqrt(xi)/dt=-sqrt(r/2)，故从xi0到参考终点的剩余时间在[sqrt(2xi0/a_hi),sqrt(2xi0/a_lo)]内。到达时按混合端点规则延拓s=ell、v_ref=0、reference HOLD；不在端点计算0/0或把有限到达写成无限趋近。

BRAKE只在v_ref²≤2a_hi xi的可证域进入，命令-a_hi-delta使实际参考减速度至少a_hi。b=2a_hi xi-v_ref²满足b_dot=-2v_ref(a_hi+a_cmd+eta)≥0，首次v_ref=0前距离≤v_ref²/(2a_hi)≤xi，随后reference HOLD。LAUNCH首次交点前及APPROACH带内均在该域。保持中的参考零加速度、边端点接触规则和连续底层闭环为显式理想混合公理；不从有噪普通反馈推得。恢复同一旧tid只能从合法HOLD重入LAUNCH，方向和原边不变。界外侧滑、转向、未证制动或可信控制故障不在定理域，照故障/评分合同保留。

称P1为上述条件下每次未再受中断的合法旧边参考运动有限到达。它不证明全系统无死锁/无饥饿、任意丢包后恢复或实际LIMO误差界。任一可证明的界内碰撞都仍是反例，不能事后把条件改为不成立。

## 4. 后缀几何与可计算预处理

K=Z⊕F；U(q)=union_{s∈[q,ell]}(u+se+K)，q∈[0,ell]。执行域由有限闭瓦片覆盖，Mask(S)包含所有与S相交的瓦片；边界接触也计冲突。静态障碍及工作域可行性对完整U(0)检查，初始实体/保持包络须合法且不同agent的初始资源不交。格图可通不自动代表有尺寸实体可通；不合法的静态域明确登记，动态失败不得用于筛图。

P2：可信证据给匹配tid的q≤s(t_sample)，接收时取q_new=max(q_old,q_sample)，相同tid参考未来不减且z∈Z，因此从采样起至该tid终结，实体一直在U(q_new)内。证据到达晚不会变成未来真值，也不会因延迟失效此包含关系。下一MOVE必须重取自己的U(0)，不声称机器人全未来永不返回。endpoint E=v+K属于每个U(q)，不能退休为空集。

对r∈M0=Mask(U(0))，I_r={s∈[0,ell]:(u+se+K)∩r≠空}。K紧、r闭使I_r为紧区间[0,ell]的闭子集，且非空，因此lambda_r=max I_r存在并取到。于是r∈Mask(U(q))等价于I_r∩[q,ell]非空，等价于q≤lambda_r；充分性直接取s=lambda_r，不要求I_r连通。删除必须lambda_r<q，等号保留；endpoint资源恰为lambda_r=ell。r不在M0时不定义lambda。此为P4几何阈值定理，不是引用PSIPP的相对出发时差条件。

有限算法域另要求Z为有限有理闭盒、F和瓦片为有限有理凸多边形或其有限并，边端点精确可表；以u+t(v-u),t∈[0,1]避免单位向量根式带来的不明近似。逐凸块线性规划最大化t，约束u+t(v-u)+z+f=x、z∈Z、f∈F、x∈r；取非空块的最大值并精确换回s。一般紧集不自动有此算法。数值近似只可用经证上界lambda_hat≥lambda，称保守退休；未经证上界不许删除。

表按(lambda,r规范key)排序。每tid指针只前进；收到新的可信q后，逐个退休所有尚在表中且lambda<q的资源。证书数c、初始资源数m，几何比较/枚举为每次O(1+d)、全tid O(c+m)，d为本次跨过的阈值数；账本检查/写入、可信服务、位复杂度与消息另收费。建表须计候选发现、精确几何、O(m log m)排序和O(m)表项；多边—瓦片关系可稠密，不能称全地图线性或整算法O(1)。地图/几何/包络/表示版本变化必须失效重建。四共享臂使用同一预处理与缓存制度、计首用/复用/内存；F臂只是不途中删除，不获得较差几何能力。

## 5. 中心状态机、发出授权与不可逆终点交接

信任域：唯一中心资源authority与各低层gate不分叉、会话内状态持久不回滚；授权和可信证书不可被普通错误包伪造。中心同一时刻只执行一个可暂停资源作业，所有检查/计算/资源访问付费，在完成后的发布点一次原子应用私有增量；计算期间物理继续、外部不能见半更新。此是单机串行提交模型，不是假设跨owner免费原子事务。中心fail-stop不重启/清空/重新分配；当前授权和物理覆盖继续保留，不承诺恢复活性。

每资源owner为FREE或(agent,tag)，tag为resident gamma或活动tid。每agent有当前resident/活动记录、连续关闭请求水位d_i和至多一个未关闭请求e=d_i+1；tid=(session,i,e)，原slot、原边、parent gamma、M0、几何版本不可变。未授状态UNGRANTED、已授GRANTED；关闭结果为ABORTED或FINISHED。中心拒绝e≤d_i的任何首次/重复请求，不可复用序号；e>d_i+1拒绝而不跳过未知责任。标准数学整数无回绕，位成本仍随序号增长。普通消息无权生成新的可信序号/原步。

MOVE请求必须来自当前已认证Kc指定的原Π步并带parent gamma。先通过付费PRECHECK：gate采样检查自己为对应resident、无活动授权、真实c等于请求slot且该原步是MOVE，返回绑定tid/slot/parent/原边/计划代际的不可变合法证明，失败只给延后拒绝，不暴露真实c或正确下一步。成功采样后，当前原步为MOVE，而gate无grant不能消费它；中心又只允许该agent一个未关闭请求，因此在parent不变时c不能靠后续WAIT悄悄跨过该MOVE。这个稳定性允许延迟PRECHECK用于准入，不靠瞬时读到真值就免费授权未来步。中心仍复核当前parent、无其他活动请求、版本和全资源。

原子授予：M0全部FREE或同agent的当前parent resident资源才可接受；其他同agent tag也不能随意吞并。parent E包含于新U(0)，在同一次中心提交中将M0标为tid、记录GRANTED并封存grant，之后才允许发送。该变更不使parent实体覆盖中断。资源冲突则保持UNGRANTED、不部分预留，保留当前阻塞请求供重试；其他输入/版本错误返回明确拒绝。未发grant不表示可以省略所有失败访问费用。

CANCEL须可信且绑定完整当前请求身份，包括尚未首次登记的合法e=d_i+1。在同一中心序列中，若尚未GRANTED，则原子记录ABORTED、推进关闭水位并持久化之后才回CLOSED；不改resident、不消费c、不释放不存在的部分预留。迟到首次/重复REQUEST均因e≤d_i拒绝。若GRANT先提交，CANCEL返回DENIED_GRANT_LIVE，不能回“已释放”成功ack。证明两局部顺序：CANCEL先使吸收性水位成立所以GRANT不可再产生；GRANT先使取消分支不可进入。没有多owner“此刻FREE”的清理推断，也不允许已发grant超时回收。请求重试只在确知当前请求已关闭后换新e，旧逻辑slot可仍未消费。

gate验证grant的会话、tid、slot、原边、parent gamma、签发authority和当前闭合水位，在付费验证完成后等待合法ACTUATOR机会才首次启动；no-start不消费、不重发新tid，不释放M0。重复同grant不重复执行，旧epoch永远不能使s或c回退。已授尚未进入时q仍为0、整个U(0)保留；进入后匹配可信q可按P2退休，不能再把整条原边钉到READY从而消灭S因子。F全程持有M0直到终点交接。

到达参考终点后，gate先持久关闭旧tid入口、进入reference HOLD并生成新resident latch gamma'，封存(last_closed_tid,slot,v,v_ref=0,closed,gamma')终点记录。该记录在活动槽变NONE后仍可由ENTRY查询，至少保留到新grant合法进入；此前新grant只能在中心处理它完成后产生。当前位置/普通COMPLETE或NONE本身不替代终点证明。

中心取得付费ENTRY终点证据后，在串行提交中复核当前GRANTED tid与完整绑定，将endpoint Mask(E)从tid改同agent resident gamma'，删除该tid其余保留资源，记录FINISHED与d_i=e；然后发布READY。READY是中心交接已完成的确认，不能由gate本地latch单方宣告。算法/执行器只有收到验证过的READY后才可在POLICY消费一次MOVE槽。下一MOVE须新PRECHECK、重新预留；同一POLICY不连锁消费多个槽。迟到旧ENTRY/释放消息因当前tag/tid与水位不匹配不改新holder。

P3覆盖归纳：INIT覆盖所有实体；授予先完整预留、parent包含于M0，同agent改tag无空隙；gate只有覆盖已存在才进入；P2使中段退休后实体仍在剩余集合；终点改tag保持E、清其余不删实体所在资源；CANCEL未授无资源变化，已授取消拒绝；旧消息不改变新tag。不同agent资源互斥，任何实体交点落在共同闭瓦片而违反该互斥，故界内无实体碰撞。该证明不保证无死锁、吞吐正或永久丢包后的释放。中心故障/失联不使grant/实体消失；界外信任破坏另记，不能借此掩盖前提成立时的反例。

## 6. 真实游标、付费采样与共享知识

真实c_i由executor私有持久维护，算法只持Kc_i：同计划代际已验证并交付的CURSOR证书中c的最大值。未知不能作0推断；INIT可用已计初始化工作的共同初始证据给Kc=c=0。MOVE只有匹配终点READY后在POLICY消费，COMMITTED_WAIT只在合法resident POLICY消费一次，HOLD/no-start/发grant/普通反馈不消费。物理状态和c更新不回流为规划器免费共享引用，即使同处一进程也须遵守读接口。

公共CURSOR机会按固定agent规范顺序逐一轮询，初始前哨在第一key之前，空fleet属于输入非法；每机会请求一个agent，包括resident/NONE/纯WAIT，资格不由算法当前需求改变。CURSOR只返回(session,plan_epoch,agent,request_id,sample_id,c,sample_point)，不顺带给q或实体真值。POSITION是独立付费服务，请求必须指定tid；仅匹配gate当前活动tid或保留的同tid终点记录才给含真参考区间，NONE且无匹配记录返回NO_MATCH，不能推断清空。ENTRY含PRECHECK或END两种完整绑定证明；TASK服务的算法可见回执另定义。四臂和guarded TIP有同一可购买能力，不跨反事实臂转移payload。

所有可信服务统一捕获规则：请求机会只生成/入队；authority作业首个语义操作是付费CAPTURE，不足以支付该原子读取则本次没有采样。其在该AUTH_WORK事件的物理推进及更早子事件全部完成之后、其他语义工作之前，原子读一致authority状态并冻结payload，记sample_point=(公共行,子事件序,CAPTURE)、request/sample序号与输入版本。该行之前已完成的POLICY/物理更新计入，此点之后不计入。余下处理只能操作冻结内容；AUTH_COMPLETE不刷新，严格后继DELIVER再付费验证发布，算法只在后继POLICY/QUERY读取已送达前缀。CAPTURE失败或完成后丢失不更新知识，已发生费用不退。TASK快照也在该固定CAPTURE点读取单个全局修订及其全字段，不能拼跨修订局部片段。

重传已存在证书保持原request_id/sample_id/sample_point/payload，只收实际缓存/通信/验证费；新鲜采样必须有新请求序号和重新付费CAPTURE。区间生成的确定性封装及传感创新只以本请求语义key取值，并必须包含捕获时真实s；已确认不包含为可信模型破坏，不是普通误报。q_sample取区间下界与合法[0,ell]保守处理，中心只在同tid验证后取max更新；旧tid的大q不能用于新MOVE。

pure WAIT链：POLICY合法使私有c:k→k+1，位置和resident不变、算法Kc不变；共同CURSOR请求排队→首个付费CAPTURE冻结k+1→期间可再消费WAIT而证书不变→付费完成/投送→后继算法机会才更新Kc。若CAPTURE在原WAIT之前只能冻结k。主PIE的barrier/PROJECT与该臂TIP均可复用已付费证据，不按使用者名字重复收采样费；实际读取/计算/广播接收工作照收。POSITION不提供pure WAIT逻辑进度，主算法也不能绕过CURSOR读取c。

## 7. 阻塞导向与轮询的总定义

Active为中心已提交GRANTED但尚未提交FINISHED的tid集合，按本臂已认证/已提交账本计算；UNGRANTED、ABORTED与FINISHED排除，已发未启动、运动、制动、已在gate终点但中心尚未知者包括。不按隐藏真实s或未送达终点信息删除成员。两策略遵守同一谓词，不强制跨臂私有历史产生完全相同集合。

RR状态last初始为小于所有合法(session,agent,e)的前哨。每QUERY在当前非空Active取规范序中严格大于last的最小key，没有则回绕最小key；空集返回NO_QUERY、不改last。选中后即推进last，查询失败/失联也推进；删除不重置last，插入按该全序参与下一次计算。集合来源、初次选择、空集和动态成员均唯一，不靠“上一次”未定义初态。

中心每agent至多保留一个UNGRANTED原请求p，阻塞请求集合P只含结构/PRECHECK有效且最近因资源冲突未授予者；重复传输不产生新p。授予、关闭、版本/parent失效则移除。QUERY计算当前owner重查这些静态M0，score(t)为不同p中存在r∈M0(p)、owner(r)=t且lambda_(t,r)<ell_t的个数；同p多个r只计一次。所有字段来自源提议、已收费得到的几何表和中心账本，不读真实blocker/进度。D取score最大正值者，tie按首次加入P的公共序及tid规范key；无正值退回同RR规则，Active空则NO_QUERY。任何实际选择也更新自己的last，避免回退状态未定义。查询晚、重复、没有跨阈值或不能解除全部阻塞仍是合法负结果。

实现合同首先采用完整枚举P和相交资源的确定性参考计算，计全部扫描/去重/排序费用，不把仅“受影响”作为无证复杂度承诺。若后继实际实现用反向索引，必须在同知识快照上与此总函数等价，计索引维护/失效及最坏输出规模；未证等价不能静默换策略。本候选的阈值优化只减少几何判定，不能宣称消除了全局查询选择成本。

## 8. PIE、真实任务与冻结规划作业

固定官方 R0 为 [YueZhang-studyuse/LMAPF-delay](https://github.com/YueZhang-studyuse/LMAPF-delay/tree/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357)，commit 0b5b33649fc367abcb1cd0a7ad5ac03511bf9357。新MOVE只能是该固定核心经下述显式共享接口接纳的输出；原生 NATIVE-PIE-D 原字节/原误差域另轨保留。共享接口改变执行、观测、任务同步和计时注入，不宣称整个native轨迹等价，不把接口成本或原源失败当查询策略收益。

联合历史Π_i[0..L]使用共同逻辑槽，每slot映射原job/segment/source/input/原边或WAIT，提交后不可改。真实c_i≤L，已知Kc_i≤c_i，未知则不为该agent提即时MOVE；Π_i[0]为合法起点，初始L=S=c=Kc=0是空历史索引定义，不是实验保护参数。MOVE只在对应READY后消费，COMMITTED_WAIT在合法POLICY消费，HOLD不消费。即使主算法使用Kc提出旧slot，gate也只能经PRECHECK及grant执行其真实当前原MOVE，不按未来PROJECT输出自行改路。

最多一个规划作业及一个待提交结果。S为最新提交段的起点；只有all Kc_i≥S且无上述作业时，才可请求在尾L追加。接纳后S←old L、L←new L，new L>old L；未追上的前段不能无限追加。段首与旧尾同一槽，不重复消费/服务。旧承诺不因预测目标改变而撤销。在线路径可保留从min Kc起到L及被当前作业pin住的前缀，只有无仍有效引用才可GC；完整审计历史另追加归档，不能把在线窗口界称为总存储有界。

真实任务账本A与已知K_task分开。固定TASK_SERVICE机会先按真实reference terminal/resident、任务顶点匹配及真实X处于服务区域判断，每agent至多服务一个合法队首，再按固定原任务策略补给：greedy按agent规范顺序填已分配队列；Fixed用各自原序列；Inf用原tasks[(counter_i*num_agents+i) mod tasks_size]并递增counter。补给深度/原CLI意义保持而本阶段不绑定数值；tasks_size为空或接口非法不做取模/假目标。先服务再补给是明确共享顺序，不冒称native三种策略的sync相同。

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

公共有限机会表O按(t,row_id)全序、t非减，含INIT、POLICY(i)、ACTUATOR(i)、REPORT(i)、QUERY、CURSOR、ENTRY(i,kind)、TASK_REQ、TASK_SERVICE、NETWORK(channel)、PROCESS_SLICE(server)、MODE(i)、FAULT、CUTOFF、STOP。不得依某臂已观察收益改O。每行先将物理状态推进到t并处理已确定的有限自主运动切换；再按job规范key发布先前行已完成的有限结果；最后只执行本行类型。每类处理明示主体，缺输入返回NO_REQUEST/NO_MATCH/NO_REPLAY_TARGET，不从未来补对象。所有新生工作、消息和工作完成的可见发布都严格在后继行，单行不递归自触发至无限。

INIT验证固定输入/初始包络/资源互斥/角色身份，建立共同初始resident与游标证据；初始化及预处理实际成本单列并纳入首次总成本，不把它们藏在稳态速度里。公共评价窗口E与INIT admission条件预先给定，不因某臂初始化慢而重开窗口。初始条件是仿真定义；不宣称现实机器人免费获得共同可信初态。POLICY只消费本行开始已投送前缀、至多一逻辑槽及一个原请求，不直接读其他executor真值；ACTUATOR只执行已完成验证的grant/mode命令。REPORT仅生成本臂普通观测，不能更新可信知识。

QUERY按§7产生最多一个POSITION请求；CURSOR按§6产生共同下一agent请求；ENTRY只处理指定PRECHECK或END请求（不存在则NO_REQUEST），TASK_REQ请求全局快照；TASK_SERVICE是真实环境服务，不直接向算法公开账本。NETWORK从指定channel中先前已完成可发送消息按(enqueue_row,message_id,copy_ordinal)取最小一条，按本消息的外生故障key决定投送/丢失/有限复制/延迟。重放只能引用本臂已生成合法原payload；没有则NO_REPLAY_TARGET，不能用别臂实际证书填空。

PROCESS_SLICE为固定server提供有限正工作容量。server内FIFO，按入队行/job_id打破同时性，运行一个队首job，剩余容量不在本行递归运行新生job。中心账本job检查/更新在私有副本中分步收费，完成后等待后继发布才原子生效；CAPTURE是authority job的首个收费原子操作，具体发生于本PROCESS_SLICE行物理推进后的操作起点。它与其他同server作业串行；不同authority共享世界全序，不能有含糊同一时刻的前后快照。容量不足完成该原子操作时不读取状态，保留至以后。每条已执行操作不可撤销计费，未执行未来容量不算真实工作。

费用表必须列请求生成、CAPTURE/数值封装、资源/索引读取和写入、原子提交记录、grant/证书、网络字节/每接收端、验证、重复/失败处理、planner、日志/GC及预处理；所有动作正费用或由明确共用已付费对象复用，不能隐含免费全局扫描。NATURAL计实际工作与竞争同公共服务容量；STRICT在同O/容量下连空闲未用供给也预付，实际工作向量仍分别报告，不能强迫两臂实际工作量相同。处理排队/物理推进/来源停止互相作用纳入闭环，不能为费用对齐冻结实体。

故障创新由独立block根派生，key=(角色,公开行或请求/作业语义id,有限copy/attempt序号)。同block各臂共享创新函数而输入自己产生的对象；调用次数不同不顺移公用PRNG磁带。ordinary假反馈、no-start、空间/运动扰动、通信错误、处理容量分别有类型；给普通包加时间偏移不等于实体误差。ROOT独立性只对block成立，臂间配对相关允许。当前不生成根、种子、O、manifest、tape或载荷。

## 10. 外部原法、守卫适配与原样检查合同

外部原版固定 [Kei18/time-independent-planning v1.0](https://github.com/Kei18/time-independent-planning/tree/755a7ce740d49543b1165403371752c08e342ca4)，commit 755a7ce740d49543b1165403371752c08e342ca4。NATIVE-TIP保持原字节与原误差/通信域；共享比较器明确称TIP-MCP guarded adapter。源mcp.cpp先nextNode后isStable、末下标访问plan[t+1]的静态缺口已亲见，不先修原版也不把其越界记作本方法优势。

守卫版每次激活先验证c的定义域；本地末下标直接HOLD不访问nextNode，否则唯一下一原步plan[c+1]。WAIT仅合法POLICY消费一次，MOVE no-start/在途不消费；仅中心READY后消费并转CONTRACTED，在此之前用保守EXTENDED表示tail=plan[c]、head=plan[c+1]。他者getT只用同计划代际已交付Kc下界和固定原计划依赖，未知返回WAIT；同一臂已付费CURSOR证据可复用，不免费读他者真实c/head/tail。守卫、单中心/物理接口和付费通信是显式变化，不宣称恢复原最小通信量定理。

补充匹配计划族在每公共block以同固定源和确定的R0计划输出供全部比较臂，生成授权之前先登记来源/作业/计划身份，不能从某策略成功结果挑计划。计划必须非空、vertex及完整no-following合规，含末端永久驻留；不适用登记INAPPLICABLE全行保留，主lifelong仍保留该公共来源。该族是有限计划的完成/服务/成本比较，不冒称TIP有相同lifelong分配算法。没有合法匹配block则补充族UNINSTANTIATED/UNESTIMABLE，不能隐去外部基线。下一episode只有全部旧责任合法drain后同规则重新INIT，不能reset未完成机器人。

固定源关键对象：R0 CompetitionSystem.cpp blob4e9a86921fda3fd15bd616c3c0dff461688254ed（27752bytes/885行完整）；.h 6daf0b9e3fa1015e49893b09be87940577427189（6753/243完整）；MAPFPlanner.cpp 94afb42df1a70f5e312a382e61cf83576fd7360e（6125/208完整）；DelaySimulation.cpp 1e1953d9fa9ccb1eb96ae5d7b8829f425679d113（14733/454完整）；driver.cpp b75764cc26c2374ce51dabb94e13a138e50f166f（6664/172完整）；ActionModel.h/.cpp fb3aa01448d3f9369ca7a423d975d4a148cbe1e8/3292164aa861521beda270f18b8d3892e35fbd21（3757/136、8164/220完整）；SharedEnv.h 7f4b4678ca9da7278e92fd4cdf9eed043f03a8e2（573/27完整）。LNS.cpp blob1fb0e54f8f2bb00af05de53233ae600774e36f2a、SHA2560113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2，仅指定规划/提交/时钟窗口语义阅读，不用完整关键词检索冒称全文语义。

外部mcp.cpp blob51459fc9ea27b3c8831b0a72d2455bca360b2223（1135/68完整）；mapf_dp.cpp 7537e71885496ff9b0a75bf8d49b0f2138044625（3758/170完整）；agent.cpp a5a8f1ba47d295cd93f728cb8ad2cf85caca3b3a（4569/206完整）。原README/CMake/license/headless接口已读：R0 MIT/C++14与Boost，外部MIT/C++17；文档与源码CMake/输入字段存在差异，按实际固定入口，不复制公开徽章token。对象完整目录/37项关键词审计另有证据记录，但本候选不由这些身份表推出依赖全闭或实测复现成功。

ORIGINAL-CHECK当前全部NOT_IMPLEMENTED/NOT_RUN：解除全部设计门之后才可按固定发布字节、官方headless目标及原合法样例记录平台/编译器/依赖/选项、返回码、输出/日志身份，检查非空、索引、合法动作、no-following适用域与真实完成；零返回码缺输入/空结果/未定义访问不算成功。源码异常、构建失败、原定义域失败与合法算法超时分别登记。现在不构建、编写/运行测试或实例化样例来“证明准备完成”。
