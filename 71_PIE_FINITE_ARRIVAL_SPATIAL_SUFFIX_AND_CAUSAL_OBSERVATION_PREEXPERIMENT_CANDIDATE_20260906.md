# 71 PIE 原提议上的有限到达、实体偏差后缀与付费阻塞观测

日期：2026-09-06（Asia/Shanghai）。状态：FIXED-FOR-SEQUENTIAL-REVIEW / NOT-ACCEPTED。
控制：**HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT**。
本文在 70 三路有效回执和根裁决后另立新编号与新字节；不修补、封存或改变 69/70 及其报告。全文完成固定后须依序接受科研导师 skill、Nature reviewer skill、明确无任何 skill 的独立逻辑审查与根验收。目前没有资格通过结论。

本文只含理论设计、静态见证和未执行检查合同，没有实现、构建、测试、模拟运行、种子、场景载荷、调参或实验结果。H、T_delay、B_CAL、B_max、B*、P_active、density N 保持原义，未赋值，不给范围、默认、先验或调参建议。其他物理符号只表达公开模型可行关系，不暗代保护参数。

## 1. 实际问题与可证伪目标

机器人沿原路径运行时，实体可能偏离名义中心线、在一条边中途减速或暂停；调度端也可能收到错误位置或过早 COMPLETE。另一机器人不能因虚假的“已经离开”进入前者仍会占据的空间。始终等整条边完成才放行，又可能浪费已经确实清空的空间。付费可信查询若针对真正阻塞后继原提议的机器人，在全部处理和通信费用计入后，能否比同能力轮询更早完成真实任务，是本研究的问题。

组合分三层：有界实体偏差与连续边内运动的占用底座；持久事务和可信证据释放；共同底座上的查询对象选择。PIE-D 是唯一新 MOVE 提议源，包裹层只接受其原 MOVE、在合法责任下 HOLD/WAIT、继续或制动既有 tid，不换邻边、任务目标或暗用另一规划器。原 no-start 随机延迟仍称延迟，不能代替实体误差；处理时间、空间/执行偏差、普通反馈错误分别建模。

主假设 HYP-Q：同 SUFFIX 底座、查询能力、费用和因果 PIE 流水线下，BLOCKER 相比 RR 的固定公共总体期望真实服务率差为正。共同底座相对 TERMINAL-ONLY 的增量及交互另由 2×2 估计。目标证据包括解析安全域、条件性正收益见证、零/负效应域，以及日后合法预注册的完整结果；不预先承诺显著性、首创、普遍提升或硬件适用。

几何/连续控制、观测/协议、组合三路线保持开放。若查询成本超过清空收益、证据不退休瓦片或原路径不容并发，组合可能无效或更差；不得删负例或把当前路线当唯一答案。真实服务 Q 与收到完成证据的时间分列：查询早拿到回执本身不算吞吐提升。

## 2. 一手来源与路线边界

本节是根代理独立定点来源核验，不冒充原 69L1/69E1 的完整回执。旧真实句柄已查询但当前不可观测，约定报告仍缺，不重派或把超时计通过。全文指完整提取文本，不等于图像、排版公式或全依赖均已审计。

| ID / 一手来源 | 亲见范围 | 对研究的约束 |
|---|---|---|
| J1 Hönig 等，Persistent and Robust Execution of MAPF Schedules in Warehouses，IEEE RA-L，2019，DOI 10.1109/LRA.2019.2894217 | 作者 PDF https://whoenig.github.io/publications/2019_RA-L_Hoenig.pdf ，7 页/873 提取行完整，无 PDF 字节散列 | ADG/提交边界；准确定位/控制和通知前提不等于任意实体偏移或假完成安全。 |
| J2 Zhong/Rossi/Shell，Planned synchronization for multi-robot systems with active observations，Autonomous Robots 50 article 5，2026，DOI 10.1007/s10514-025-10225-4 | 官方 https://link.springer.com/article/10.1007/s10514-025-10225-4 ，在线 2025-12-24；全文 109306 字符；HTML SHA256 6d1bd846552a9c29bd6fb1f4d40b78c434eaffc7f8ed5f2d64930af4f512e741 | 付费观测与同步是近邻，不能称主动观察本身首创；其共享观测前提不证明本通道可信性。 |
| J3 Zhu/Brito/Alonso-Mora，B-UAVC，Autonomous Robots 46(2):401–420，2022，DOI 10.1007/s10514-021-10029-2 | 作者 PDF https://autonomousrobots.nl/assets/files/publications/22_zhu_auro.pdf ，20 页全文/77578 字符；7788136 bytes，SHA256 6de59654091de1bdf388f1544c00e7ce4be1236f2b1aad89dfd682c7897e2e83 | Gaussian chance geometry 与控制改变直接处理定位；动作域不同，单积分器证明不自动覆盖双积分器启发式/死锁。代码 mrca_vc 未固定。 |
| J4 Shahar 等，Safe Multi-Agent Pathfinding with Time Uncertainty，JAIR 70:923–954，2021，DOI 10.1613/jair.1.12397 | https://par.nsf.gov/servlets/purl/10297272 ，32 页全文/87953 字符；1097341 bytes，SHA256 def08325da0ee2d4d12e01fd5ed864acaa224b87b0421f402803b9e4a68023bd；近空页未图像核对 | 有界时长潜在占用、SENSE/SENSE+COM 直接相关；通信/感知前提和计划 SOC 不等于真实服务率。Conformant-CBS 代码未固定。 |
| J5 Atzmon 等，Robust Multi-Agent Path Finding and Executing，JAIR 67:549–579，2020，DOI 10.1613/jair.1.11734 | https://jair.org/index.php/jair/article/view/11734 ，摘要级 | 鲁棒延迟余量不是实体空间误差替代，不据摘要断言缺某机制。 |
| J6 Liu/Tang/Cai/Li，Robust and effective multi-agent path execution with timing uncertainty，Artificial Intelligence 358:104586，2026，DOI 10.1016/j.artint.2026.104586 | 官方 ScienceDirect PII S0004370226001128 摘要/元数据和作者表，非全文 | 直接近邻；Crossref published=2026-09、Elsevier coverDate=2026-09-30 属编排刊期，非已核在线日期。API 只有 coredata/openaccess=0；1824 bytes，SHA256 802321eb449a00b8d3745840cc5bcec23dd1639a7190af84f30f52ca8edf4a0e。 |
| J7 Wang/Zhang/Shi，Protocol-observation discrepancy calibration...，Robotics and Autonomous Systems 206:105701，2026，DOI 10.1016/j.robot.2026.105701 | 官方 ScienceDirect PII S0921889026003726 摘要/highlights/引言和章节片段，非全文 | 占用/预留/队列/进度偏差是最近路线，不从正文缺失推断其无可信释放/事务。published=2026-12、coverDate=2026-12-31；API 只有 coredata，1867 bytes，SHA256 f9aa84550174c2418c5ec650d6d9780116dcfe264ee190f7d95675a639863a1e。 |
| J8 Serra-Gómez 等，Learning scalable and efficient communication policies for multi-robot collision avoidance，Autonomous Robots 47(8):1275–1297，2023，DOI 10.1007/s10514-023-10127-3 | 官方 Springer 摘要/引言/相关工作，非全文 | 学习通信与 NMPC 改控制，不是同 PIE 动作域的直接比较器。 |
| J9 Zhou/Wang/Bandyopadhyay/Schwager，Fast Online Collision Avoidance... BVC，RA-L 2(2):1047–1054，2017，DOI 10.1109/LRA.2017.2656241 | https://msl.stanford.edu/bibliography/zhou_fast_2017 ，摘要/BibTeX，IEEE 7828016 | 缓冲几何相关，摘要不能授予本模型定理。 |
| C1 Luo/Sun/Kapoor，PrSBC，NeurIPS 2020 | 官方 papers.nips.cc/paper_files/paper/2020/hash/03793ef7d06ffd63d34ade9d091f1ced-Abstract.html ，摘要 | 有限支持误差/机会约束 QP 改控制，须标明动作差异。 |
| C2 Carr/Jansen/Junges/Topcu，Safe RL via Shielding under Partial Observability，AAAI 2023，DOI 10.1609/aaai.v37i12.26723 | https://ojs.aaai.org/index.php/AAAI/article/view/26723 ，摘要/首页 | 知识状态 shielding 近邻，不等于资源/物理时间定理。 |
| C3 Zhang/Chen/Harabor/Le Bodic/Stuckey，PIE-D，AAAI 39(22):23387–23394，2025，DOI 10.1609/aaai.v39i22.34506 | https://ojs.aaai.org/index.php/AAAI/article/view/34506/36661 ，8 页/793 行；已读 0–107、169–233、254–314、431–477、511–698，非全文；源码脚注亲见 | 必留原法及唯一新 MOVE 源，不把 no-start 延迟改名。 |
| C4 Okumura/Tamura/Défago，Time-Independent Planning for Multiple Moving Agents，AAAI 35(13):11299–11307，2021，DOI 10.1609/aaai.v35i13.17347 | https://cdn.aaai.org/ojs/17347/17347-13-20841-1-2-20210518.pdf ，9 页/803 行完整 | 原 no-following 计划和通信域须保留；官方 MCP emulation 与原理论分开。 |
| C5 Ma/Kumar/Koenig，Multi-Agent Path Finding with Delay Probabilities，AAAI 31(1):3605–3612，2017，DOI 10.1609/aaai.v31i1.11035 | https://ojs.aaai.org/index.php/AAAI/article/download/11035/10894 ，8 页/960 提取行完整，无 PDF 字节散列 | 末状态不动作、WAIT 消费索引、MOVE 失败不推进；最小通信 DAG 不等同 TIP getT 门控。 |
| S1 Hoeffding，Probability Inequalities for Sums of Bounded Random Variables，JASA 58(301):13–30，1963，DOI 10.1080/01621459.1963.10500830 | https://www.tandfonline.com/doi/abs/10.1080/01621459.1963.10500830 ，官方题录/摘要，本轮未读全文 | 后文自给矩母函数推导，不冒称全文已读，也不拿统计来源充当领域文献。 |

路线 A 几何/控制（J3/J9/C1）直接改变实体风险，但常改控制/目标并依赖概率模型；B 时序执行（J1/J4/J5/J6/C4/C5）处理延迟和顺序，单独不覆盖假反馈/实体偏移；C 观测/协议（J2/J7/J8/C2）减少知识保守性，释放依赖可信因果证据。71 选择受界跟踪管道、原提议执行和阻塞观测的组合，因为可以写同动作域证明和费用匹配反事实，不宣称压倒每篇算法。

强新颖性排除仍 OPEN：J6/J7 正文和旧扩展任务完整回执未得。只主张检验定义明确组合的条件性增量；近邻若覆盖核心机制，须缩小主张、增加匹配基线或另编号改路线，不能隐去。


## 3. 官方源码身份、差异与原法检查合同

固定 R0：https://github.com/YueZhang-studyuse/LMAPF-delay/tree/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357 。外部官方 tag v1.0：https://github.com/Kei18/time-independent-planning/tree/755a7ce740d49543b1165403371752c08e342ca4 。通过官方 API 将指定对象读到内存并复核 Git blob SHA1/SHA256，未 clone、构建或运行。以下 SHA1 是对象身份，不冒充完整依赖审计。

| 固定对象 | Git blob SHA1 | 亲见覆盖 |
|---|---|---|
| R0 CompetitionSystem.cpp | 4e9a86921fda3fd15bd616c3c0dff461688254ed | 27752 bytes，885 逻辑行完整；SHA256 fe7532c9fe4e4dfe19d8e5e7c2192635c99a5fbd8c4d95db728ae02336839604 |
| R0 CompetitionSystem.h | 6daf0b9e3fa1015e49893b09be87940577427189 | 6753 bytes，243 行完整；SHA256 e4e0b26e30412503e496d56af1b1fd841fe9ff01b99ca425316027538bcc0f55 |
| R0 MAPFPlanner.cpp | 94afb42df1a70f5e312a382e61cf83576fd7360e | 6125 bytes，208 行完整；SHA256 c81952afaa94157abd7138bdaae71edc7b19b59dee60b653bb380ef16e681be1，本轮只补核完整摘要 |
| R0 DelaySimulation.cpp | 1e1953d9fa9ccb1eb96ae5d7b8829f425679d113 | 14733 bytes，454 行完整，no-start 与真实递归推进 |
| R0 driver.cpp | b75764cc26c2374ce51dabb94e13a138e50f166f | 6664 bytes，172 行完整，真实 JSON/CLI 入口 |
| R0 ActionModel.h / .cpp | fb3aa01448d3f9369ca7a423d975d4a148cbe1e8 / 3292164aa861521beda270f18b8d3892e35fbd21 | 3757/8164 bytes，136/220 行完整；有效离散平移动作和 WAIT，旋转相关代码注释 |
| R0 LNS.cpp | 1fb0e54f8f2bb00af05de53233ae600774e36f2a | 53100 bytes，仅 383–443、496–542、1154–1216、1236–1387、1433–1483 指定函数；SHA256 0113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2 |
| R0 Instance.cpp | 2183ba41c4a04278fafa0c4ed0605762abd5fb7c | 14658 bytes，仅 L1–55 和字段定位 |
| R0 内部 mcp.cpp | ec7c149fa01206752ae1eeebff64f699facc2bb2 | 13558 bytes，仅 L1–130，不称内部算法全文审计 |
| R0 SharedEnv.h | 7f4b4678ca9da7278e92fd4cdf9eed043f03a8e2 | 573 bytes，27 行完整；SHA256 8acce1b85b0878e575606e0058e10b46366bdc1eae4e4d9982dd5f355e627de0 |
| 外部 mcp.cpp | 51459fc9ea27b3c8831b0a72d2455bca360b2223 | 1135 bytes，68 行完整；SHA256 d2c53110803ef784a28419298c24d86477ff93e18bdbb957459dcd697fe90ad7 |
| 外部 mapf_dp.cpp | 7537e71885496ff9b0a75bf8d49b0f2138044625 | 3758 bytes，170 行完整；SHA256 f0f3d23be2ccd8f004b850b29cb336a6fabf5f2e77c9407df01fd305e284c5e0 |
| 外部 agent.cpp | a5a8f1ba47d295cd93f728cb8ad2cf85caca3b3a | 4569 bytes，206 行完整；SHA256 1e1700c650424f0ea7bcb9951dea697f799d15a64872fbbb2318234ff0c6bb15 |
| 外部原 sample instance | 842958a104943a6d7cad2474547ee5665c427b37 | 620 bytes，38 行完整，仅核原引用 |
| 外部原 map / plan | 1b27a7e3384ab9dbe984d452e6b481b6d11d8469 / b7ad38d85756c6b26d57dd0169fb29533660e416 | 62/490 bytes，仅身份，不形成项目输入载荷 |

此前还完整读 R0 MAPFPlanner.h、license/CMake/README/输入说明和外部 mcp.hpp/mapf_dp.hpp/app.cpp/license/CMake/README/子模块元数据；此表不补造未保留的散列。R0 MIT、CMake 最低 3.16、C++14、Boost 最低 1.49 所列组件、headless lifelong 入口。README compile.sh/示例路径与树内容有差异，输入说明 robotFile/rotation 与实际 driver 有差异。外部 MIT、C++17，源码 CMake 3.1 与 README 3.16 不同，native architecture flags 应记录；openFrameworks 是可视化依赖而非 headless 必需。公开徽章 token 不复制或使用。原样例数值仅属于源码，不给本项目赋值。

ORIGINAL-CHECK 全部 NOT_RUN：只有解除全部门后，分别对固定发布字节、官方 headless 目标和原合法样例，记录平台/编译器/依赖/选项/返回码/输出语法/日志身份，核查非空计划、索引定义域、逐步合法性、no-following 适用条件、真实完成与缺输入区别。返回码为零但缺输入、空结果或未定义访问不算成功。现在不能先构建/跑一次来补证据，本合同不创建测试或输入。

外部 ROOT-S01：mcp.cpp actContracted 在 isStable 前调用 nextNode；nextNode 对末下标访问 plan[t+1]。Agent.activate 未先阻 stable，MAPF_DP.run 在他者尚未完成时可再激活已完成机器人，app 读取有限计划未无限填充。静态见证 A:(u,u)、B:(w,x)，三顶点不同；A WAIT 后到末端，B EXTENDED 后下一轮失败，A 再激活可达越界表达式。未运行，不声称所有样例崩溃。upstream b2e9e650a1f5446b88cd7b9394504e97435e7f38 中三个关键 blob 相同，但 current app/全依赖未读，不称整版无修复。守卫适配必须显式修补定义域，原版保持未改；源码缺陷不得成为本方法收益。

## 4. 物理、观测与有限空间后缀

一条 MOVE 是原四邻接边 u→v，长度 ell>0、单位方向 e。固定朝向紧凸足迹 F、世界坐标盒 Z={z:|z_j|≤zbar_j}，障碍为闭集合；允许平移/沿边暂停后转下一条原边，不声称差速轮转向/三维姿态通用性。真实实体 X(t)=u+s(t)e+z(t)+F，参考进度 s∈[0,ell]、参考速率 v_ref≥0；真实速度为 v_ref e+z_dot，可在盒中回摆。v_ref=0 不等于真实静止，v_cap 只约束参考速率，不能直接当实体速度上限。

纵向 s_dot=v_ref、v_ref_dot=a_cmd+eta，|eta|≤delta；偏差 z_dot=−kappa z+w，kappa>0，逐分量 |w_j|≤kappa zbar_j。初值 z∈Z 时，|z_j(t)|≤exp(−kappa t)|z_j(0)|+(1−exp(−kappa t))zbar_j≤zbar_j。这是实体偏差及执行扰动，不是 no-start 延迟。普通定位 y=p+epsilon 可叠加后述错值/时延/丢失/重放，普通 COMPLETE 可任意过早；都不能使资源退休。

可信低层读取参考 s/v_ref，不从普通 noisy pose 偷推精确进度。明示低层连续反馈精确、执行器无滞后、驻停制约理想有效，可信服务对 s 返回含真的区间并带身份。owner/gate 可 fail-stop/重启，消息可丢/延迟/乱序/重复，但持久权威状态不丢、不分叉，可信服务不 Byzantine，恢复先重建 fencing 再接运动命令。永久失联可以保持安全占用，但不保证活性。物理/制动/持久性/证据不可伪造前提失效则 MODEL_BREACH，撤回定理；不能靠事后检测重新索回已退休资源，也不能用“可信 latch”循环证明物理界。这是可审查的理想纯仿真假设，非硬件认证。

公共有限工作区域用闭瓦片资源 R 覆盖，几何输入 zeta>0 未赋数值；边界接触的全部瓦片计入，越工作区视为障碍。Mask(A)={r∈R:r∩A≠∅}，
U(q)=({u+sigma e:q≤sigma≤ell}⊕Z⊕F)，M(q)=Mask(U(q))；
resident 占用为 U_res(u)=u+Z+F。q≤s 且单调时，当前和未来实体始终在 U(q)，无需真实投影单调。q 增大使 U/M 嵌套缩小。计算用保守外包；不能确认包含/不交则 UNKNOWN，不以浮点近似不等当安全。几何部分为有限凸多面体与闭瓦片交集/不交判定，包含边界；有理外包、面/顶点枚举和分离证书均须保存。

可信 QUERY 证书字段为 (agent,tid,proposal_occurrence,edge,geometry_hash,generation,sample_time,sequence,[s_lower,s_upper],gate_phase,authority_epoch,auth)。区间须含采样时 s；q_new=max(q_old,max(0,min(ell,s_lower)))，先持久化再退休 M_old∖M_new。区间向外取整；错 tid/代/几何/fence/认证拒绝，历史证书只在同一可达历史验证后生效。普通报告永不更新 q。恢复只读取原持久 q，不能重新占有已退休部分。TERMINAL-ONLY 同样可知 q，但 held_mask 始终为 M(0) 到终结；知识和权利字段分列。

新 MOVE 完整 M(0) 必须无障碍，并取得全部资源；几何过宽/贴障不能裁剪掩码以放行。转下一边只在纵向终点与 resident_ready 后：旧 s=ell 变为新 s=0，u'=旧终点，z'=z，F 朝向不变，实体连续。终点是 v_vertex+Z+F 内区域，不要求欧氏精确顶点。

## 5. 有限到达、制动、驻停及解析证明

令 0<a_lo<a_hi≤a_brake、a_launch>0、delta≥0，v_cap²≥2a_hi ell；执行器容许 a_cmd∈[−a_hi−delta,a_launch+delta]。都是未绑定数值的物理可行关系。新入口从 rest 或本节可认证不变集进入，不能接管仅符合旧较弱刹车锥的任意运动状态。删除 70 的 h_dot≥−gamma h，仅保留 h=2a_brake(ell−s)−v_ref²≥0；旧指数条件从 h>0 推出任意有限时 h>0，不能与有限精确终点并用。

LAUNCH：s<ell、rest，a_cmd=a_launch+delta，首次 F_L=v_ref²−2a_lo(ell−s)=0 时切 APPROACH。v_ref_dot∈[a_launch,a_launch+2delta]，启动后 F_L_dot=2v_ref(v_ref_dot+a_lo)>0，首次交点唯一且在端点前。初始余长 xi_0 时 tau_L≤sqrt(2a_lo xi_0/[a_launch(a_launch+a_lo)])，是解析上界而非实验 cutoff。

APPROACH：xi=ell−s>0，r=v_ref²/(2xi)，r_c=min(a_hi,max(a_lo,r))，
a_cmd=−a_lo+delta−[(a_hi−a_lo+2delta)/(a_hi−a_lo)](r_c−a_lo)。
r_dot=(v_ref/xi)(r+a_cmd+eta)，下边界 r=a_lo 时非负、上边界 a_hi 时非正，因此闭带不变。输入在执行器界内，v_ref²≤2a_hi xi≤v_cap²。xi>0 每个紧子域上反馈局部 Lipschitz、扰动可测有界，Carathéodory 解存在唯一。sqrt(xi)_dot=−sqrt(r/2)，所以 sqrt(2xi_L/a_hi)≤tau_A≤sqrt(2xi_L/a_lo)；有限末时 xi→0、v_ref→0，连续延拓到 (ell,0)，不计算端点 0/0，不用容差、瞬移或瞬间清零。

BRAKE：暂停/containment 时沿原边取 a_cmd=−a_hi−delta，直至首次 v_ref=0，恢复命令排队且须先完全停止。v_ref_dot∈[−a_hi−2delta,−a_hi]，停车距离≤v_ref²/(2a_hi)≤xi，时间≤v_ref/a_hi；b=2a_hi xi−v_ref² 满足 b_dot≥0。若恰到端点进入 terminal，否则 HOLD 后同 tid 再 LAUNCH，不换边或重置 q。仅有旧 h≥0 且 v_ref²>2a_hi xi 时停车可能越端点，所以不在新模式准入域。

HOLD/TERMINAL 另有理想非负参考速度制约：v_ref>0 按 BRAKE ODE，到零后接触/驻停约束使 v_ref_dot=0，即使 eta 非零。此为混合物理公理，不是普通单值反馈自动抵消未知扰动的推论；s 保持而 z 继续 ODE。TERMINAL 纵向吸收并在低层持久关闭旧 tid，偏差盒不消失。下一原边须新 generation 许可才可 LAUNCH。

P1 有限区域到达：合法初值与本节前提，且从某时起既有 tid 持续允许运动、无永久 no-start/暂停/处理阻断，则有限 LAUNCH+APPROACH 到终点区域。有限次暂停可分段应用；无限外部打断不保活性。局部有限机会、BRAKE 完成先于恢复排除外部 Zeno，每次 LAUNCH 只一次带切换、终点吸收。此结论不是实体精确点或硬件已验证。

P2 后缀包含：Z 不变、s 单调、q≤s 推出当前 tid 负责的原边阶段内 X(t)⊂U(q)，覆盖跨 tick 沉默运动、暂停和真实局部回摆。“以后不可再进”只针对该旧 tid；后继原 MOVE 若重入同一空间，必须重新取得其完整资源，不声称机器人整个未来永不返回。资源清空必须检验与 U(q_new) 不交；仅 q 增大或超过资源中心不够，Z⊕F 沿边后向支持半径必须进入判据。


## 6. 资源事务、逐 owner 终点交接与恢复

状态均为持久权威状态；“原子”只指一个 owner 的记录，或独立决策记录的一次线性化更新。没有跨资源原子大步骤。时间戳/等待超时不产生释放权。资源、entry、decision 各有单一可恢复权威 epoch，迁移只能继承全部未解除责任；无权威或 epoch 分叉则 HOLD/QUARANTINE，不以旧签名代替当前权威。

MOVE occurrence=(agent,committed_segment_id,logical_slot,original_edge_hash)，tid=(occurrence,attempt_generation)。每次尝试绑定固定 M(0)、几何身份、父 resident generation、参与者清单和 entry。每 agent 至多一个可启动 successor；既有 tid 不因失败重传而重新编号，只有 D=ABORT 且旧 gate 永久关闭、所有旧 PREPARE 清理可证后，才可对同 occurrence 新尝试。generation 严格增且不回绕，解析溢出则拒绝。

资源 owner 记录 FREE、RESIDENT(agent,g)、PREPARED(tid,parent_or_none)、HELD(tid)、CONVERTED_TO_RESIDENT(tid,agent,g')、RETIRED(tid,proof)。历史 tombstone 和当前 holder 分开保存。父 resident 的自重叠准备是同 owner 内的复合状态 RESIDENT+PREPARED，同一实体的保护不断；不是把资源当 FREE。只有同 agent、确切父 g、唯一已授权 successor 可以使用这个例外，任意同 agent 的其他旧 tid/代仍算 BUSY。

决策 D_tid 初为 UNDECIDED，只有一次 CAS 变 COMMIT 或 ABORT，终态不反转。PREPARE 逐 owner 检验固定参与者/几何/合法父关系/当前 holder；FREE 或合法父 resident 可持久预留并返回绑定 authority_epoch 的收据；外国权利返回 BUSY，未知权威返回 UNKNOWN；重复同 tid 返回原收据。协调器收齐完整 M(0) 和 entry 的 PREPARE 收据后才允许尝试 COMMIT；任何不可证则不发 START。请求者可在 UNDECIDED 时要求 ABORT，只有实际 D=ABORT 证明才能清理未启动 PREPARE；D 未知保留，不用 timeout 猜 ABORT。

entry 状态为 RESIDENT_CLOSED(g)、PREPARED(tid,g)、ISSUED(tid)、RUNNING(tid)、BRAKING(tid)、TERMINAL_CLOSED(tid,latch)、RESIDENT_READY(g')、QUARANTINE。entry PREPARE 要求正确父驻留、无其他可启动 tid、原 MOVE 身份与闭合资源表。START 必须由 entry 同时验证唯一 COMMIT 和完整 owner PREPARE 证据，在持久 ISSUED 后才交低层执行。各 owner 尚未收到 COMMIT 时 PREPARED 本身也保有排他覆盖，不能自行超时清除。低层首次接受 tid 时记录启动身份；重复 START 只返回历史状态，不把 s 重置为零，不重新执行已终结边。

父 resident 的消费必须显式记录：entry 对唯一 tid 准备后禁止父 g 再授权其他 successor；D=COMMIT 时 g 的责任转由该 tid 的完整 M(0) 承担。owner 收到 COMMIT 或首次带有效 COMMIT 的进度/交接请求时，在同一次局部更新将 RESIDENT(g)+PREPARED(tid) 规范化为 HELD(tid,parent_consumed=g)，覆盖不断；COMMIT 前 ABORT 仅删 PREPARED，保留 resident。之后合法 RETIRE 匹配这一复合状态并先规范化再退休，不能留下一个永远锁住原起点的孤立父 claim，也不能在 ABORT 分支误删父驻留。历史 g 仅作 fencing/tombstone，不再作为第二个可启动权利。

物理 ACTUATOR 机会可在 ISSUED 时 no-start 失败并保留全占用；成功进入 LAUNCH，途中继续/制动都仅在原边。PREPARE/COMMIT/ISSUED 本身不等于物理进展，更不消费 PIE 槽。D=COMMIT 后不能撤回作 ABORT；业务取消、模式关闭或故障只能 containment 并承担原责任，直至合法退休/交接。事件处理函数不等待网络同步返回，单次返回 ACK/BUSY/UNKNOWN/PENDING/REJECT 之一，挂起项在后续机会重查。

可信 q_new 持久提交后，SUFFIX 逐 owner 对 r∈held_mask∖M(q_new) 发 RETIRE(tid,expected_holder,progress_proof)。owner 校验同 tid/代、证据下界、r 与后缀不交，然后在本资源内释放旧 claim、留 tombstone。丢 ACK 可重查，重复退休只回原结果；已经转换或归新 tid 的当前 holder 不会被旧 expected_holder 匹配而删除。TERM-ONLY 不执行这种中段退休。只有该策略实际退休成功的资源才从 held_mask 删除，不能把知识 mask 当已释放状态。

终点 refinement 分成以下不可交换的步骤，不能一笔“原子转成 resident”：
1. 低层到 (s=ell,v_ref=0) 后纵向吸收，持久关闭旧 tid 的所有未来启动权限；终点证书须包含 gate_closed 与 reference_endpoint，普通到达包不足。
2. durable latch 以旧 tid 为键 CAS 绑定唯一 (agent,g',E_tid,geometry,terminal_proof)，其中 E_tid=Mask(v_vertex+Z+F)。重启或不同协调者不能另选 g'。低层关闭先于证书可发，证书生成/验证/传输在收费服务机会进行。
3. 每个 r∈E_tid 的 owner 验证 latch 与当前旧 claim，局部原子 HELD/PREPARED(oldtid)→RESIDENT(agent,g')，保持同实体排他覆盖。端点资源从未由中段 q 退休，因为 E_tid⊂M(q)。混合旧/new 标记安全，转换后不允许回滚到 FREE。
4. entry 只有拿到完整 E_tid、当前权威可恢复的转换收据集，才持久登记 RESIDENT_READY(g')。这是完整性屏障，不是全资源同时快照；屏障前端点转换权利不可被其他流程撤销，因此不同时取得的收据能共同证明覆盖。READY 之后才准许下一 occurrence 使用父 g'。
5. 非端点旧 claim 可凭终点证明另行退休；若下一边与这些尚未退休 claim 重叠，仍需先合法解除，不能笼统同 agent 豁免。DRAIN 需旧责任清单每项都有退休/转换/关闭/终态收据，READY 本身不等于 DRAIN。

恢复表：latch 前崩溃保留旧占用、重查低层永久关闭；latch 后部分转换按同一个 g'/操作标识重放；全转换 ACK 丢失重取持久收据，不生成新代；READY ACK 丢失且后继已推进时返回历史完成并附当前 generation/后继状态，历史 READY 不能再次授权启动；迟到旧 RELEASE 不能删新 holder；迟到旧 START 由执行端持久 closed fence 拒绝，旧 COMMIT 不覆盖 closed；记录缺失/不可验证/权威失联均保持责任并 HOLD，不宣布 DRAIN。

合法知识集合 K 是与全部已接受可信记录、单调性、模式和物理界相容的状态集合。普通消息只能作为咨询。K 非空时，准入仍须完整资源证明，不能仅取某个乐观状态；K 为空或互相矛盾时 QUARANTINE：不新增授权，旧已提交占用/驻停约束继续，发付费恢复/核查请求。它不声称无可信物理前提仍可救援。

P3 事务 refinement 安全：对局部状态转换归纳。INIT 每实体被 disjoint resident masks 覆盖；PREPARE 和 COMMIT 不去除已有覆盖；START 前全部未来占用已由 PREPARED/HELD 排他保有；P2 保证物理进展始终在未退休后缀；退休有永不再进证明且先持久化；终点逐 owner 仅换同实体标签，不出现空隙；READY 必須完整端点覆盖；新 MOVE 仍重新满足全部准入。故任何两个实体如在一点相交，覆盖该点的公共闭瓦片应同时受两个实体排他权利保护，与 owner 规则矛盾。此证明依赖物理/可信/不分叉前提，未证明无死锁或永久失联后完成。

## 7. 总决策、查询策略与模式

每次 POLICY 机会最多消费一个原槽或尝试一个新 MOVE。顺序为：若有可信终结且 READY 的现 occurrence，提交一次槽消费；若旧 tid 尚在执行/制动/处理中，输出 CONTINUE_OLD 或 BRAKE_OLD/PENDING，不提新边；若没有剩余提交槽，尝试合格规划事务或合法驻留 HOLD；若下一槽等于当前位置，为 COMMITTED_WAIT，在 gate/父 resident 可证时消费一次，否则 HOLD；若为合法原 MOVE，创建/重查该 occurrence 的资源事务，完整证据后 ISSUE_OR_PENDING，否则 HOLD。无正确驻留/旧承诺覆盖的状态不能输出“安全 WAIT”，只 QUARANTINE。所有分支输出状态与原因，不返回未定义动作。

blocked proposal 是尚未发令的唯一原 occurrence 及其 M(0)、first_seen 公共行序号、冲突资源与权威 holder 证明；拒绝几何/输入错误另记，不伪装成可查询 blocker。QUERY 机会先刷新可用记录、去重按 occurrence，不用真值判断谁已经前进。候选 blocker tid 必须当前持有阻塞资源、尚非可信终结、且几何上 M(q)∖M(ell) 可能非空。此可退休性只依据几何/知识，不能查看真实 s。BLOCKER 按所阻不同待发 occurrence 数降序、first_seen 升序、tid/资源规范字节序选择；同一 tid 被多个资源阻塞只计一次对应 proposal。预算不足返回 DENIED；没有候选返回 NO_EVENT，不偷换为免费终结查询。

RR 在相同 active tid 集上按规范 tid 序循环，选择大于上次实际选择 key 的首项，否则环回首项；集合增减不重置到对候选有利位置，空集合 NO_EVENT。一次合法选择即推进 cursor，丢失/无进度/失败也消耗机会与该次查询 ordinal。查询返回只按 §4/6 处理，不能假定选中者一定有可退休进度。所有原 proposals 与 blocker 记录从当前臂自身历史产生。

模式 NATIVE-COLD-OFF 完全独立：无 shared sidecar/init/主动观测/自定义 mask 或持久字段，只运行固定原版及原生误差域，检查原样随机/时钟/线程/参数和输出身份，不把新协议影响冒作“关闭后原版”。

共享 ACTIVE、SHARED-OFF、DRAIN 则都保有同一物理/资源责任。ACTIVE 允许对应查询策略；SHARED-OFF 停止新的中段主动查询但继续已有事务和收费终结/恢复服务，退休按已选择因子，不突然释放或删账本；DRAIN 不生成新 occurrence/规划承诺，旧 tid 可在完整旧覆盖下继续/制动并请求终结/恢复，直到全部旧责任清单清零。切换模式不是取消 COMMIT，禁用功能不等于安全原版。恢复 ACTIVE 只在当前代完整可证后继续，不重放旧 START。

终结服务与查询策略独立存在：固定 ENTRY_SERVICE 机会轮到指定 agent 时，可对本 agent 最老未闭责任查询低层 closed/latch/owner 转换/READY，按确定阶段一次推进；没有责任则 NO_EVENT。ACTIVE/SHARED-OFF/DRAIN 均用相同能力和收费，不因 BLOCKER 候选为空就永远无法终结，也没有免费 truth push。DRAIN 若未来服务/通信永远缺失可无限未完成，控制仍 NO-GO；不以 timeout 伪造 drain 完成。


## 8. PIE 原提议的因果流水线和任务适配总函数

源事实与新增适配分开：R0 CompetitionSystem.cpp move L14–41 以真实离散状态每 agent 每次最多完成一个队首；sync L52–98 预测承诺尾；执行循环 L384–488 同步、规划、承诺和执行；FixedAssignSystem/TaskAssignSystem 在头文件的 sync 是空实现，不能声称原三策略都有同一预测。MAPFPlanner loadPaths/plan/planner_commit 与 LNS commitPath 产生承诺/未来路径；LNS 验证含 vertex/swap 和动作合法性，不自行证明连续安全或 no-following。下述共享适配保持原规划核心/参数含义与唯一提议来源，明确替换真实执行/反馈接口；不是未经证据的整个原生轨迹等价。

持久联合历史 Π_i[0..L] 使用共同逻辑槽，所有 agent 在每槽各有一个名义顶点。c_i≤L 是可信消费游标，INIT 时 c_i=0，Π_i[0] 为公开合法起点；初始 S=L=0 是空历史的索引定义，不给实验保护参数赋值。每个提交段有唯一 job_id/segment_id/source_blob/input_hash，slot→原 edge/WAIT 的映射不可变。预测锚点 Π_i[L] 与物理/知识当前 Π_i[c_i] 分开；各 agent 异步推进不把共同槽当物理时间。普通反馈、PREPARE、COMMIT、ISSUED、不带 READY 的终点均不消费 c。COMMITTED_WAIT 只在 POLICY 合法驻留机会消费一槽；因阻塞/规划的 HOLD 不消费；MOVE 只在对应终点 READY 后 POLICY 机会消费一次。一次机会不连锁消费多个槽。

流水线最多一个最新段及其尚未完全追上的前段：S 是最新承诺段起点。只有 all c_i≥S、当前没有规划作业且没有待提交结果时，才可为尾 L 请求后继；接纳后 S←old L、L←new L，必须 new L>old L。这样旧段未追上时不能无限追加；失败/空/陈旧作业不扩展窗口，旧责任继续。新段首锚点与原末锚点同一槽，不二次消费或服务。

真实任务账本 A 与算法已知副本 K_task 分开。真实服务按固定 TASK_SERVICE 机会：先按真实纵向 terminal/resident 模式与当前真实合法队首目标的服务区域判定，每 agent 最多提交一个任务完成；然后执行公开指定原任务策略的补给顺序。greedy 的共享队列按 agent id 顺序填补可用已分配队列，Fixed 使用各自原有任务序列，Inf 取源公式 tasks[(counter_i*num_agents+i) mod tasks_size] 并递增 counter。具体补给深度/原 CLI 选项取固定原含义而本阶段未绑定；tasks_size=0 或字段缺失为 INPUT_INVALID，不能取模或造目标。这里“先服务再补给”是共享适配明确的事件顺序，不冒称已验证 native 所有调用阶段；固定原法轨道仍以原字节为准。

服务谓词要求真实 reference endpoint 与对应任务顶点一致、X 属于其公开服务区域，低层已处于纵向驻停/关闭；初始合法 resident 同理。每次真实服务提交生成单调 global_task_revision 和唯一 service_id=(block,agent,TASK_SERVICE row,front_task_id)，含 allocation_before/after、真实状态证据和真实服务时刻，Q 只由此真实记录累加；不等待 QUERY/ENTRY_READY/TASK_RECEIPT 到达。真正完成和认证知识分列，重传不得多计。物理任务是否已服务不改变该 tid 的占用证明。

K_task 只能由收费可信 TASK_RECEIPT 传入：原子全局任务快照，或同一 global_task_revision 序列的连续完整批次，包含所有已分配队列、共享剩余序列、计数器与服务去重表。不同修订局部消息不能拼成新快照；重复忽略、乱序等待缺段、认证失败拒绝。算法只知道最新已完整送达的状态，不拥有 scorer 未送达真值。普通 COMPLETE/pose 不改 K_task。真实任务服务和派单不能为规划冻结或保留预测归属。

预测函数 PROJECT(K_task,c,Π,L)：为每 agent 复制其已合法分配、未被可信确认完成的有序队列 W_i；逐公共槽 k 从当前各 c_i 之后至 L，仅对 c_i<k≤L 的 agent 检查 Π_i[k] 是否匹配 W_i 的队首，匹配最多弹一个，不匹配不动。起始槽 Π_i[c_i] 不另检查；WAIT 可在不同槽各检查一次，MOVE/COMMIT/证书到达不额外检查。虚拟弹出不改 A/K_task、不产服务或 Q。未实际分配的 greedy 共享任务不能虚拟派给 agent 后作为合法目标；Fixed/Inf 也不把未分配生成项当已分配。耗尽合法返回空，输入不一致返回 NO_INPUT，不造当前位置伪目标。

该 PROJECT 是所有权受限的预测，非异步未来任务的精确模拟。真实 greedy 完成顺序可改变后续分配，不能将每 agent 独立推演冒称共享队列的一致未来。若某合法输入产生空目标而固定 PIE core 不支持，则 NO_PROPOSAL/HOLD，服务/派单/旧 tid 继续；新合法回执可触发再规划。有限任务某 agent 耗尽而其他未完成时可能因此停滞，必须计失败/未完成，不能删除该来源行或补假目标。保留原 lifelong 任务流和分配口径，但不声明全部场景活性；这一前瞻限制是所有 shared 比较臂共同采用的显式适配代价。

冻结 SharedEnv 字段如下，未列的可变共享状态禁止旁路读取：
| 字段/状态 | 映射 |
|---|---|
| num_of_agents、rows、cols、map、map_name | 来自同一已验证公共 manifest/地图；本阶段实例化未开放 |
| curr_states | Π_i[L] 对应固定原 State 的位置/原方向字段与逻辑时间，不是真实 in-progress pose；方向沿原平移表示，不添加旋转 |
| curr_timestep | 共同逻辑槽 L，不是物理秒数或 observed exposure |
| goal_locations | PROJECT 剩余合法任务及其可信 reveal 字段；空目标按上述总分支处理 |
| unexecuted_paths | 前次接纳的 future_path 仅当完整起始锚点和几何/输入格式一致才复用，否则空；不能把丢弃作业缓存当接纳状态 |
| file_storage_path | 未来授权输出位置合同；当前不创建运行文件 |
| planner 内部可变状态 | 属作业事务副本，包括 lns/instance/commit/future 缓存与随机/时钟状态；丢弃作业不得泄露状态到接纳流 |

每个作业只读冻结环境、源身份、原参数版本和自己语义随机流；处理时真实世界持续运动。作业异常/未终止到既定停止条件则显式 ERROR/PENDING/STOP，不空等阻塞物理回调。输出必须每 agent 非空、有共同延长长度、首点等于锚点，后续均四邻接原步或 WAIT、全段无 vertex/swap 冲突、名义端点唯一且索引/边界有效。源 commitPath 的跳过首点/短路填充须按其原输出规范化后再次全检，空向量/非法 back/front 只能源失败，不在适配中生成新路修补。校验不要求 no-following 以替换主 PIPE 域，外部限定比较另验。

结果接纳前用最新完整 K_task 和当前 c 重算 PROJECT；消费前进本身不一定使作业失效，但完整 planner-visible 目标字段改变则拒绝。目标相同仍须匹配 job_id、原锚点/当前尾、待追加槽、参数/地图/环境版本、future_path 身份；在一次共享提交记录 CAS 中验证这些版本并 append。验证与 append 间变更则失败重试，不接纳陈旧结果。任务预测错了不撤销既有原提交/执行权利，只能影响尚未承诺输出；物理准入由 §6 重新验证实际责任，名义共同槽无冲突不等于异步实体可同时进入。

总返回状态为 ACCEPTED_SEGMENT、NO_INPUT、NO_PROPOSAL、PENDING、SOURCE_ERROR、INVALID_OUTPUT、STALE、STOPPED；除 ACCEPTED_SEGMENT 外均不新增 MOVE，所有返回都保有旧 tid/HOLD 责任。原生 NATIVE-COLD-OFF 单列，shared 各臂使用同一上述适配，不能将共享适配与原字节称为完全 trace-equivalent。

## 9. 外部原法与守卫比较器

外部已发表锚点为 C4 的官方 TIP-MCP emulation，并用 C5 原始 MAPF-DP/MCP 核对语义。C5 最后局部状态不动作，WAIT 消费一个局部索引，MOVE no-start 失败不推进；原 DAG 的依赖边和最小通信主张，不自动属于 TIP getT 门控。不得以名称 MCP 相同宣称所有策略逐字等价。

NATIVE-TIP 原字节单列，ORIGINAL-CHECK NOT_RUN，保留 ROOT-S01 源索引缺口。明确的新比较器名为 TIP-MCP guarded adapter。它只作必要定义域守卫：本地 c 超出合法范围→ADAPTER_INVALID；c=末下标→HOLD 并绝不访问 nextNode；否则取唯一 plan[c+1]。WAIT 在 POLICY 机会消费一次，MOVE 启动失败不消费；PREPARE/COMMIT-before-start/在途以保守 EXTENDED 表示，tail 为 plan[c]、head 为原 plan[c+1]，只有物理终点及 READY 后消费且转 CONTRACTED。认证游标低界用于 getT 门控，未知依赖返回 WAIT；不免费读取他者真实游标/head/tail。所有依赖信息经同类型收费服务和同故障渠道，公共 owner 准入仍必需。适配与信息保守性明确，不能称已复现原最小通信量。

匹配固定计划的外部比较是补充研究族，不能替代 §8 主 lifelong 2×2：每个公共 block 用同一固定公开来源和同一确定性 R0 计划输出供所有臂，未来产生前先登记源/作业/计划身份，不按某臂结果选择。计划须非空，检查 vertex 和 no-following（含末端永久驻留的语义，而不是 C++ 越界访问）。不满足外部原域的计划登记 INAPPLICABLE，保留完整行，不把它计为候选击败基线；主 lifelong 对照仍保留该公共来源。守卫版是否通过全部纸面映射和日后原法检查尚需审查，未宣称已运行。

补充族为有限计划的服务/到达和资源费用，不冒称 TIP-MCP 有新 lifelong 分配算法；下一 episode 只能在全部上一责任 drain 且所有臂按同样规则重新 INIT 后出现，不强制 reset 未完成机器人。原法未定义访问、构建失败、输入缺失均属来源/适配失败，不能计为查询策略收益。若无合法匹配 block，补充比较整体 UNINSTANTIATED/UNESTIMABLE，不隐去比较器，也不凭适配标签授予 G4 PASS。


## 10. 有限机会语法、因果展开与处理费用

本节是符号输入/输出合同，不生成任何机会表、随机 tape、种子或可运行载荷。将来每个 block 的公共设计 X 须包含有限 opportunity 表 O，行键 (physical_time,row_ordinal) 严格全序、time 非降、row_ordinal 唯一；物理 cutoff、源/模型/费用/故障 profile 身份和所有字段在看结果前固定。表缺失为 UNINSTANTIATED，不偷偷补默认。每种机会有 subject_agent 或固定权威服务主体，未有 tid 也消耗公共机会序号。零时间子消息可入队，但只在严格后继行处理，禁止同一回调递归触发新回调；每行有限 payload/有限复制数/有限参与者。物理模型内部守卫由 §5 证明有限切换，外部暂停次数受有限表限制。

完整事件枚举为 INIT、POLICY_OPPORTUNITY、ACTUATOR_OPPORTUNITY、REPORT_OPPORTUNITY、QUERY_OPPORTUNITY、ENTRY_SERVICE_OPPORTUNITY、TASK_SERVICE_OPPORTUNITY、TASK_RECEIPT_OPPORTUNITY、NETWORK_OPPORTUNITY、PROCESS_SLICE、MODE_OPPORTUNITY、FAULT_OPPORTUNITY、CUTOFF、STOP。任何其他 tag 为 TRACE_INVALID，不能在后文默默新增机会类型。状态记录/请求/ACK 是这些机会生成的有限输出，不是隐含额外机会。每行统一字段含 block/source/profile/version、time/ordinal、kind/subject、mode_before/after、parent_ids、semantic_key、request/response status、input/output hashes、cost/job fields、physical_interval 与验证状态。

| kind | 必要输入及一次展开，所有条件均用本臂当前状态 | 无动作/失败分支 |
|---|---|---|
| INIT | 固定图/实体/合法初态、任务分配快照、无重叠 resident masks、entry/owner authority 身份；逐资源覆盖与初始低层模式可证后建共同槽起点 | 缺字段/重叠/障碍/模型不满足→INIT_INVALID，不把未启动臂当零成功 |
| POLICY_OPPORTUNITY | subject agent，运行 §7 一次；规划发起/结果接纳或一个 slot 动作，所需计算产生待处理 job | 不可证驻留→QUARANTINE；其余按明确 HOLD/PENDING/REJECT，不连锁消费 |
| ACTUATOR_OPPORTUNITY | subject agent，若有合法 ISSUED/旧 RUNNING/BRAKING，则验证 gate，推进一次启动尝试/继续/停止命令；真正 ODE 发生于物理间隔 | 无 tid→NO_EVENT；每次合法 pending COMMIT 启动尝试包含失败都递增 (agent,occurrence,actuator_attempt)；不以资源代作物理尝试主体 |
| REPORT_OPPORTUNITY | subject agent，backend 从本臂真实 p/reference phase/ordinary state 生成普通 payload，按本行创新变换位置/phase/COMPLETE，再进普通出站队列 | 无相应实体→NO_EVENT；不能复制另一臂真值，不能伪造可信 auth |
| QUERY_OPPORTUNITY | subject query scheduler，按 BLOCKER/RR 选一次；选择计 ordinal，发可信参考 QUERY job，生成/传输/验证各有费用 | 无候选→NO_EVENT；限额不足→DENIED；失联/丢失/无进度仍消耗本次机会且不退休 |
| ENTRY_SERVICE_OPPORTUNITY | 固定 subject agent，对最老未闭责任按 terminal证据→latch→端点转换→READY→非端点退休→drain 顺序处理当前首个未完成阶段，最多发参与者有限清单 | ACTIVE/SHARED-OFF/DRAIN 相同可用；缺证据 PENDING，空责任 NO_EVENT，无免费终结 |
| TASK_SERVICE_OPPORTUNITY | 固定所有 subject agent 的一次真实服务检查，采用 §8 确定顺序及唯一 service_id；scorer 真值与算法知识分离 | 未达真实服务条件→NO_SERVICE；停止后不能新增 Q；证书未到不阻真实计数 |
| TASK_RECEIPT_OPPORTUNITY | 对指定权威/agent 的最老未确认完整任务修订发收费快照/批次查询；收到连续认证批次才更新 K_task | 缺段/乱序缓存，重放去重，认证失败拒绝，不补真值 |
| NETWORK_OPPORTUNITY | direction 字段只能 SEND 或 RECEIVE。SEND 对固定发送端按 (enqueue_row,message_id) 取一个包，应用其语义创新 drop/copies/delivery delay，每副本有限且独立 id；RECEIVE 对固定接收端按 (delivery_eligible_time,copy_id) 取一个已到期副本，提交有费用的解析/认证 job | 无包 NO_EVENT；丢失不等于未消耗带宽/费用；未到期仍 pending；非法 direction 拒绝 |
| PROCESS_SLICE | 固定 processor_id、可用 work_units、preemption 边界；FIFO 按 (enqueue_row,job_id) 消耗该处理器待处理作业前缀，结果完成后只入队，后继行才可发布状态变更 | 空队列 IDLE；未完成 PENDING；执行/验证异常 ERROR；不能冻结物理时间等 worker 完成 |
| MODE_OPPORTUNITY | 明确目标模式与合法状态前提，调用 §7 模式转换一次 | 非法转换拒绝，COMMIT 责任不清零 |
| FAULT_OPPORTUNITY | 固定 subject 与类型：普通通道错误、网络故障、权威 fail-stop/recovery、物理模型内扰动或单列模型外压力；不凭 oracle 选择“最伤某臂”的时刻 | recovery 不可证持久状态→QUARANTINE；可信 Byzantine/界外物理为 MODEL_BREACH |
| CUTOFF | 预先固定共同停止端点，截断物理积分/消息及计分，只纳入有序端点以前的事件 | 不继续运行等待任务完成来改善分数 |
| STOP | 最早已满足的停止原因、原因证据、有效前缀终点及 outstanding responsibilities | 总分类见 §12，不用 stop 自动宣告 safe/drain |

请求和消息规范字段额外含 message_id、sender/receiver、authority_epoch、tid/occurrence 或明确 NONE、causal_parent、sample_time、issue_time、delivery_eligible_time、attempt_ordinal、copy_ordinal、payload_type、payload_hash、auth_scope、result_code。PLAN_JOB 还含 frozen_env/job/source/param/future_state hashes、input_version、work_consumed、completion_row、output_identity；GEOMETRY/QUERY/OWNER/ENTRY/TASK_VERIFY job 记录对应输入对象数、约束数、字节数和验证结果。START 发令 id、ACTUATOR 尝试 ordinal 和成功物理启动事件分开；重传同 START 不重置进度。MODE/DRAIN 服务也使用同类型请求，不能增设免费专门通道。

每个公共行有固定 PRELUDE：在物理积分至该行以后、该 kind 主处理以前，从严格较早行已完成工作的结果队列按 (completion_row,job_id) 最多发布一个结果。此非新增机会或递归调用，工作/认证/CAS 尝试已计入对应 job。接收认证结果只能更新其类型允许的本臂知识或提交一次 owner/decision/entry 局部 CAS；expected_version 不符则发布 STALE 并排队重新处理，不能在该行无偿循环。PLAN 结果只标 READY，仍由 POLICY 作 §8 完整版本接纳；产生的消息在后续 SEND 行处理。已 STOP/CUTOFF 的行不发布会增加 Q/启动/授权的新效果。没有结果则空 PRELUDE，因此所有 job 的完成、可见性、资源更新与消息接收均有有限公共发布点。

普通故障变换是完全指定的有限字段操作：从本臂当前真实 payload 出发，按公共 profile 对指定字段加有限向量偏差或替换为该行声明的值，丢弃、复制、延迟或重放同一主体已存在的历史普通包。不存在的历史包返回 NO_REPLAY_TARGET，不造过去真值；不可修改可信 auth。可信进度区间由本臂采样 s 和同语义创新给出的有界误差，经向外取整产生含真的区间；不满足界/精度时 INVALID_CERT。可信通道可丢/延迟，但“假可信”属于明确模型外实验族，不能仍计入安全定理域。

创新键不用臂名或不稳定全局请求序号：物理/普通外生创新键=(block,agent,opportunity kind,public ordinal)；按需 QUERY/START/消息创新键=(block,agent,occurrence,request kind,attempt ordinal,copy ordinal)。不同臂没有该语义事件时记 NO_EVENT，无随机值的科学消费；不向未请求臂生成带真值的假响应。相同语义事件可用共同创新，payload 必须各自闭环生成。不同 block 的全部随机根独立，同 block 内四臂任意相关；共享静态地图/task 字节不等于共享随机根，不能跨 block 在线学习或自适应修改未来设计。

物理演化：每两公共行之间按已发低层命令积分本臂连续状态，覆盖 LAUNCH/BRAKE/terminal 守卫与 cutoff；处理、验证、网络等待时同样演化。结果在完成费用/排队后才向 policy 可见，sample_time 与 delivery_time 分开。物理 solver 须给保守轨迹包络、守卫时间区间和集合包含/不交证据；无法确认则 NUMERICAL_INCONCLUSIVE 并 STOP，不以取整到终点作到达。当前只定义合同，不实现 integrator 或构建其测试。

处理费用为显式抽象计算模型，不冒称已标定硬件 wall time。公共输入声明有限编码/数值精度、处理器服务、单位费用 c_inst/c_byte/c_auth/c_geom，以及固定官方 core/依赖/ABI 和可暂停指令计数模型；未绑定则 UNINSTANTIATED。每 job 的工作是该固定程序/有限验证程序实际消耗的指令、编码字节、认证操作、几何约束操作向量，过程按 PROCESS_SLICE 逐前缀计费，所有库/重试/失败/丢弃作业包括在内；结果未完成不能提前给 policy。不可计数或未定义源访问为 SOURCE_ERROR，不用未定义 g_category 或预知未来结果充当工作函数。语义相同服务所有臂用同一费用表；低层连续控制/真实 scorer 是共同环境模型，费用独立列为公共固定成本，不能把某臂额外高层验证混入免费环境。

STRICT 主对照采用相同的**预付服务容量**：每个公共机会/处理槽为每臂保留相同能力和付费容量，空闲或 NO_EVENT 也支付容量费，超容量工作排队到后继槽，不能免费立即完成。预付费用取固定 O/容量表，因此各臂相同；实际指令/字节/认证/几何工作及真实 RPC 次数另逐项报告，不能说实际工作量相等。它回答同付费资源供给下的 Q/E 增量。NATURAL 辅助对照按实际消耗收费、共享相同单价/最大可用服务规则，不强配 realized work；同时给 Q、费用及等待的 Pareto 关系，不设事后权重把它合成有利净分。不得用其他臂实际费用的最大值反向决定本臂时间/费用，也不根据结果调容量。所有用于运行的具体容量/物理参数在门未开时均不实例化。


## 11. 公共来源选择器、全 roster 与纯仿真配对

本阶段只登记固定公共 Git tree 与选择函数，不读取旧 35–38、Q-CAL/Q-CONFIRM 或其任何科学载荷/结果，不读桌面备份，不生成参数、实例 roster、种子/tape。R0 lifelong tree=22ae3c8b3ad1f4791bd8c15b7d7b5521ed043c17；四个指定类别子树 city=3e12a4483e615cd1a261d1e2476a29294fa4d0d1、game=8d8f8fbe8d16d80f5dab7a5cbf5ab6f3a341215a、random=2264326dfda14559e0db92e1649aaf512f9ff98f、warehouse-s=60b252f11972fed7d12f00960a7c6738b3f35a19；delay tree=4e3fe329a547e682d1520047bf767a5397b3b43f。这些是已核公共元数据，不是执行实例。

将来合法绑定后，按固定 tree 的规范相对路径字节序枚举四类别全部 JSON 候选，用 driver 原实际字段 mapFile、teamSize、agentFile、taskFile、delayFile 解析。字段在固定 driver L101/112/114/115/150 亲见；本轮恢复丢失缓存所需的这些精确行，SHA256 3198636d1114e4901c9aae48d549787c9fb3bc3a0bdfd49b6445d81bb5fc4f44。引用相对该 JSON 父目录解析，消去 . 和 .. 后必须仍在同固定公开仓库树，拒绝外部绝对路径、未解释符号链接、缺 blob 或非法编码；不从字段名猜输入说明中的 robotFile。teamSize 只在 density N 获合法绑定后做原义相容检查，本阶段 N 不赋值、不据文件名选值。地图/agents/tasks/delay 的语法、索引、长度、可通行/起点合法性与源接口条件全部记录；不同失效原因分别保留。

规范 source_id=(category,map_blob,agent_blob,task_blob,delay_blob,assignment_strategy,parsed_semantic_options)。相同语义身份的路径别名合为一行并留全部 alias；同一 task blob 跨地图建立 incidence 索引，不假装天然嵌套。对同类别的所有合法来源采用全枚举，不按规划是否快、候选是否成功、故障是否可见或预期收益筛选。每个排除保留静态证据、理由与原路径，动态失败绝不改 roster。任一必需类别无合法来源，输出 UNINSTANTIATED 与空类原因，不能用另一类补齐或重分配权重。

future manifest 的完整必需字段为：源树/blob/规范路径与全部 alias；源和适配版本；任务策略/合法已分配初态；误差/故障/处理/服务机会 profile 身份及有限声明；几何/物理可行证明域；四臂与 native/外部补充的适用性；公共 O、设计暴露 E、cutoff/原停止语义；费用表/容量表/精度/计算模型；ROOT 独立创新声明与可重放键；固定重复索引集合；原保护参数绑定审计（本阶段空）；计分/分母/区间和所有输出状态。本阶段函数可审查而 manifest 是 UNINSTANTIATED，不能为填表偷生成实验载荷。

主四臂为 BLOCKER+SUFFIX（FULL）、RR+SUFFIX、BLOCKER+TERMINAL-ONLY、RR+TERMINAL-ONLY。每 block 使用同 source、真实任务流/分配规则、原 PIE core 与参数语义、物理低层、可信能力、公共机会/费用、外生创新；各臂闭环请求与 payload 可不同，不能重放另一臂实际状态。主 contrast 为 STRICT 下 FULL−RR+SUFFIX。退休因子平均效应/交互与 NATURAL 整个策略效应另列，后两者不挤入主确认结论。原生 PIE-D 和官方 TIP 的 native 原误差域轨道保留，不能让它们在没有相同物理能力时假称公平同域；外部匹配计划适用/不适用全列。不会凭 baseline crash/未定义访问制造领先。

固定目标的权重为四类别等权；每类内不同 map_blob 等权；每 map 内不同合法 source_id 等权；每 source 内全部预注册 profile 等权；每 profile 内固定重复索引等权。乘积给 w_b，不能在运行后删失败、改权重或按完成耗时重归一化。这些是目标的定义，不声称公开来源自然代表所有仓库或新地图分布。指标主要 Q/E，另外给真实到达、认证延迟、碰撞/约束状态、未完成比例、实际工作向量、预付/实际费用、resident/旧责任等待、查询有效退休次数与对应瓦片数；后两项是机制量，不替代真实任务结果。

## 12. 停止、总分类、总评分与固定总体推断

Stop 取公共顺序中最早出现的有效条件：预设 cutoff、原有资源/处理停止条件、源/协议错误、物理模型前提破坏、数值不能确认、不可恢复合法执行失败；并列按以下 Classify 优先级记主类，所有次级 flags 仍保留。超时只停止新的处理，不释放资源或把未知改安全。物理间隔必须截断到 stop/cutoff，不计终点以后的服务；不继续模拟到“刚好完成”。

Classify 是穷尽总函数：缺必需设计/输入→UNINSTANTIATED/INPUT_INVALID；未合法 INIT/launch→NOT_LAUNCHED；已可证碰撞或权利冲突且所有相关定理前提成立→SAFETY_VIOLATION；有物理/信任界外事件→MODEL_BREACH（碰撞等另留）；协议语法/身份/因果/源未定义访问不成立→PROTOCOL_OR_SOURCE_INVALID；数值不能认证区间/守卫或评分证据不可验证→UNKNOWN_NUMERICAL/UNVERIFIABLE；其余已证执行崩溃→EXECUTION_FAILURE；合法行政 cutoff/原停止条件→ADMIN_CENSORED；完整合法暴露结束→COMPLETED_EXPOSURE。仍不符合任何分支的输入一律 TRACE_INVALID，不能 falling-through 当 SAFE。安全结论字段独立为 VIOLATED / VERIFIED_ON_PREFIX / UNKNOWN / OUTSIDE_MODEL；没有发现碰撞但包络无法验证只能 UNKNOWN。

observedExposure 是 stop 前已认证合法物理区间的时长之和；尚无任何合法物理间隔时为零。尝试启动/未验证积分步/单纯主机等待不能充当已证暴露；合法 resident HOLD 的物理积分则仍可构成暴露。设计分母 E_b>0 来自预先固定完整评价窗口，保持既有 P_active/其他原窗口含义，不以 observedExposure 或实际完成时间代替 E_b，不暗改保护参数。

每个真实任务实例含唯一 assignment/task_instance_id，即使目标位置相同也不同；每实例至多一次真实服务，每 agent 每公共 TASK_SERVICE 机会最多一次队首服务。评分日志必须含 task revision 的前后、service_id、真实模式/区域证据、公共行序、Stop 边界和去重证据。普通证书重传不增加 Q；Stop 前已持久真实服务、之后才补送证书仍计入，Stop 后新服务为零。没有查询的真实完成同样计分，不要求查询因果链或事后“归因成功”才计数。

Score 总返回：
- 必需臂未合法发起、整份评分日志丢失/损坏、无法验证完整真实服务前缀→该分数 UNVERIFIABLE，主 Δ/CI 均 UNESTIMABLE。
- 合法启动后立即 crash 且可验证零前缀→Q=0；这与未启动不同。
- 有可验证 Stop 及完整前缀→只计此前真实服务，之后新增完成约定零，分母仍 E_b；不为填满暴露继续仿真。
- 所有必需臂合法、前缀与停止可验证→照原 roster/权重计算。任何必需分数未知都不填零、不删 block/臂、不改分母/权重；可描述已见臂但主比较不可估。

统计目标条件于固定设计 X：d_b=(Q_FULL,b−Q_RR-SUFFIX,b)/E_b，theta=Σ_b w_b E[d_b|X]，Delta=Σ_b w_b d_b。Qmax_b 为 O 中所有允许真实服务的 (row,subject_agent) 对数，故每臂 0≤Q≤Qmax_b、|d_b|≤U_b=Qmax_b/E_b。各 block 创新根独立，块内任意依赖；静态地图/task 共享不是随机独立证明，跨块共享随机扰动/自适应学习/按结果共同排程违反条件。

主区间保持既定 95% 置信约定，alpha=0.05：
radius=sqrt((log(2/alpha)/2) Σ_b (2 w_b U_b)^2)，CI=[Delta−radius,Delta+radius]，可与已知目标范围 [−Σw_bU_b,Σw_bU_b] 相交。所有 U 为零时 Delta=theta=0，返回退化区间而不除零。权重非法、E 非正、bound 或独立根声明不可验证→INFERENCE_UNAVAILABLE；源/参数/roster 未实例化→UNINSTANTIATED；必需分数缺失→UNESTIMABLE，均无数值区间。

证明：Y_b=w_b(d_b−E[d_b|X]) 的支撑跨度 2w_bU_b。有界变量的凸性矩母函数引理给 E exp(lambda Y_b)≤exp(lambda²(2w_bU_b)²/8)；可由将变量在支撑两端线性外包、中心化后对数矩母函数二阶导≤跨度²/4 积分得到。独立性使乘积上界成立，Markov 后优化 lambda 得单尾≤exp(−2r²/Σ(2w_bU_b)²)，双尾并合得到上述 alpha。无需正态、符号对称、交换性或重采样固定地图；不以独立性自动授予符号置换区间。

覆盖的限制必须同报：若固定合法机制下完整潜在 d_b 始终有定义，则 P(发布数值 CI 且未覆盖 theta|X)≤alpha；缺失时整次 UNESTIMABLE 保留这一无条件错误发布界。但“本次可发布”可能依赖随机结果，不能宣称条件于成功发布仍有 95% 覆盖，除非另证可发布事件不改变创新分布。若连潜在合法评分机制未定义，则此界也不可用。区间可能很宽，不能为缩窄而事后调样本/删地图/改界；只按预注册固定主分析一次判主 contrast，其他 nominal 区间不作多重确认或任选显著结果。没有对未见新地图超总体的推断。


## 13. 条件性效果见证、负例与机械检查合同

正收益见证只证明存在满足全部规则的输入关系，不是实验参数、结果或主实验选择准则。取原边 A:u=(0,0)→v=(ell,0)，B:w=(0,−ell)→u，C 在与二者全部掩码不交的远处原边；F 包含参考原点，Z⊕F 被世界半宽 rho 的盒包含。初始三实体 resident masks 不交且全原边无障碍。B 原边所有相交闭瓦片的 x 上界≤rho+zeta；A 后缀 x 下界≥q−rho，因此 q>2rho+zeta 时两掩码不交，与栅格原点偏移无关，严格不等用于避免闭边界相切。参考 q 提高不抹去 Z，真实回摆仍被包含。存在 q<ell 的充分关系是 ell>2rho+zeta；若可信 pose-to-reference 采样形式是 ŝ=s+eps 且 |eps|≤eps_obs，s≥q+2eps_obs 足以让最坏下界 ŝ−eps_obs≥q。这里观测的是可信参考 s，不是普通 noisy pose。

公共顺序预先固定：A 已合法在途、B 的唯一原提议被 A 的旧 mask 阻挡；RR 游标下一项 C，BLOCKER 按规则唯一选 A。其他 B 所需资源均无外国责任。规定一个符合模型的有限服务/排队轨迹，使 FULL 的 query形成/传输/验证、持久 q、全部相关退休、B 准备和 COMMIT 在公共时刻 f 之前完成；f 是这条轨迹的可证上界，包含实际所有费用/等待，不是只加某些平均服务时长。RR 在同 public QUERY 行选 C，其能使 A 相关资源可用的最早事件下界 r 是下一次对 A 成功认证退休与 A 终点退休两种合法路径的较早下界，必须验证 r>f。没有其他普通报告、timeout、免费终结或替代路线能释放 A，故 RR 不能早于 r 授权 B。

若固定公共 ACTUATOR 机会 a 满足 f≤a<r，则 FULL 在 a 可以成功启动 B，而 RR 在 a 不可启动；取所有相关首次启动无失败、B 两臂相同初始 z 与同一时间平移不变的合法扰动/闭环、无后续暂停，则其行驶时间相同且有限，故 FULL 的真实到达更早。可选非零常量 z_0∈Z、w=kappa z_0 保持真实偏差不为零；不以 no-start 延迟充当空间误差。若 B 的目标服务区域满足 §8 且某个**预先固定** TASK_SERVICE 时刻 t_k 满足 arrival_FULL≤t_k<arrival_RR，FULL 在该机会多一个真实服务；若没有这样的公共机会，虽到达更早，Q 增量仍可为零。不得为见证事后挑主 cutoff、来源/profile 或删无跨越场景。此为充要条件以外的足够见证，不声称两个 START 下界就能比较先后，也不从该见证推主总体期望必正。

该充分几何关系失败只表示本见证不可用，不证明所有几何 SUFFIX 均无收益。其他零/负效应包括：A 尚无可认证进展；另一 owner 同时阻塞 B；轮询已选 A；中段退休/排队晚于终结；严格容量不足；无服务机会跨越；BLOCKER 反复选高阻塞但失联对象而饿死可释放者；狭窄几何导致所有原 MOVE 都不可接受。NATURAL 查询次数/费用不同仍能比较完整策略总效应，但不能把全部差归于“只改查询对象”。可信物理界外、非法原计划或改变任务/信息能力属于适用域/协议差异，不能做同域优势宣称。

下列纸面 witnesses 是机械检查必须能表达的合同，不是已创建或已执行测试。每项 future checker 必须返回匹配的可验证状态/反例；现在不生成具体运行载荷。

| ID | 触发 / 必须出现的裁决或不变量 |
|---|---|
| W01 | 正常一次原 MOVE：完整 PREPARE+COMMIT 在 START 前，q 持久后退休，终点逐 owner 转换后 READY |
| W02 | 普通过早 COMPLETE/错 pose：q/held_mask/cursor/真实 Q 不因它变化 |
| W03 | 同 tid 迟到进度证书：仅认证可达历史可更新；错 tid/代/几何/签名拒绝 |
| W04 | q 前进但仍与同瓦片相交：不退休；闭边界相切也不退休 |
| W05 | 已退休后真实 z 局部回摆：仍在 U(q)，不得重新认领后方 |
| W06 | 合法 no-start 失败：attempt 消耗、s 不启动、完整占用不丢 |
| W07 | 运动中 BRAKE：保持旧 tid、在新制动锥内停住；只有旧弱锥则准入拒绝 |
| W08 | 收到恢复早于停车：排队至 BRAKE 完成；不反向/换边 |
| W09 | 终点精确参考模式：有限到达且不算 0/0，z 可不为零，不瞬间归点 |
| W10 | 多 owner 部分 PREPARE、ACK 丢失：D 未知/PENDING，不能 timeout 释放 |
| W11 | COMMIT 与 ABORT 竞争：唯一 D 终态，COMMIT 不能被业务取消改 ABORT |
| W12 | START 重放/terminal 后迟到：不会重置 s、重复 MOVE 或重新启动已关闭 tid |
| W13 | q 持久化前崩溃：不得依据未持久进度退休；已持久退休后恢复保持 q |
| W14 | terminal 部分转换崩溃：端点旧/new 标签混合仍同实体覆盖，重放同 g' |
| W15 | 转换 ACK 丢失：重取历史收据；READY 未齐不得启动下一 MOVE |
| W16 | 旧 release 命中新代资源：expected_holder 不符而拒绝，不删新 resident/后继 |
| W17 | 非端点旧 claim 尚存且与下一边重叠：同 agent 不构成豁免 |
| W18 | K 为空/可信记录矛盾：QUARANTINE，不输出没有覆盖的 safe WAIT |
| W19 | ACTIVE→SHARED-OFF→DRAIN：COMMIT 责任不断，独立收费 ENTRY 服务仍存在，永久失联不假 drain |
| W20 | RR 集合变化与 BLOCKER tie：用固定 key/cursor，失败也消耗选择，不看真实 s |
| W21 | 名义 WAIT 与阻塞 HOLD：前者最多消费一槽、后者不消费；真实服务由独立机会判定 |
| W22 | greedy 真实完成次序颠倒：未分配任务不虚拟抢占，任务快照不能混代，旧提交不因预测错而解除安全责任 |
| W23 | planner 期间 c 推进/新任务回执：重算完整目标和版本，陈旧输出不 append，丢弃内部缓存不泄露 |
| W24 | 空目标/空 plan/越界/source failure：明确 NO_PROPOSAL/SOURCE_ERROR，不能补目标/替代路径/删来源 |
| W25 | 外部末端索引 ROOT-S01：原法标定义域缺口，guarded 末端 HOLD，不冒原字节；no-following 不适用独立登记 |
| W26 | 普通包重放目标不存在：NO_REPLAY_TARGET；某臂无语义事件：NO_EVENT，不复制另一臂真值 |
| W27 | 零时间消息级联：只在严格后继行发布，有限表耗尽后 pending 不递归 |
| W28 | 处理/网络跨 tick：物理继续积分；结果在全部工作/排队后可见；费用包含失败/重试/丢弃 |
| W29 | NUMERICAL_INCONCLUSIVE 早于 cutoff：显式 UNKNOWN，合法物理区间为空时 observedExposure=0，不能 SAFE |
| W30 | 未启动必需臂/日志丢失 vs 合法立即 crash：前者 UNESTIMABLE，后者仅在零前缀可证时 Q=0 |
| W31 | cutoff 正好切穿物理步、Stop 前真实服务后补证书：截断后不加 Q，前缀真实服务仍计，不按查询归因删 |
| W32 | 同目标不同 task 实例 vs 同实例重传：前者可各次合法服务，后者永不重复计数 |
| W33 | 固定地图组成重采样、跨块共享创新或事后挑可发布结果：不得授予本固定总体/条件覆盖声明 |
| W34 | 正几何/事件顺序与无服务跨越反例：分别支持更早到达、真实 Q 正增量或 Q 零增量，不混称 |
| W35 | 参数/roster 未绑定、空必需类别、适用基线全空：UNINSTANTIATED，保留行与原因，不造默认或重新加权 |
| W36 | 界外物理/可信 Byzantine 压力：MODEL_BREACH/UNKNOWN，不能仍把条件定理当无条件保证 |

机械检查接口均为未来设计合同，**NOT_IMPLEMENTED / NOT_RUN**：
VerifyManifest 返回 VALID/UNINSTANTIATED/INVALID，检查源 blob/alias/路径/字段、物理关系/原参数含义、机会有穷全序、固定臂/权重/暴露/根独立性声明及无结果筛选；
FoldLedger 按所有行和局部 CAS 记录重放 owner/decision/entry/generation/tombstone，检查先持久后退休、无丢覆盖、无旧代复活和 drain 清单，失败返回首个最小行前缀；
CheckProposal 把每个 MOVE/WAIT occurrence 对应回固定 source job/环境版本/原输出与消费槽，拒绝合成边/目标、非法填充及陈旧 append；
CheckGeometry 给真实轨迹的保守包络、瓦片集合与障碍/其他实体的可证关系，不能决定时 UNKNOWN，不以缺碰撞日志当证据；
CheckEventsAndCosts 重放全部有限类型、前后因果/attempt/copy、真实时间/处理工作/队列/费用及 NO_EVENT，拒绝未枚举 tag、未收费路径和提前可见结果；
ClassifyAndScore 按 §12 产生主类/全部 flags、安全域状态、Q/observedExposure/E、全部 missing reasons，保留所有必需臂；
Estimate 检查固定 X、完整评分和独立根条件，输出明确估计/区间或 UNINSTANTIATED/UNESTIMABLE/INFERENCE_UNAVAILABLE。
检查报告必须绑定输入/程序/依赖/版本和覆盖范围；future “全绿”若未覆盖 W01–36、上述接口及完整纯仿真域，不能宣布完成。任何检查所需实际数据仍待控制门解除，当前不读取受限材料替代它。

## 14. 修复对应、合作来源与验收边界

70 的 14 条原始 bearing 不改票、不回溯关闭：导师/Nature 的有限终点对应 §4–5；三路 terminal 细化对应 §6；PIE/MCP 适配对应 §8–9；机会/模式/费用对应 §7/10；缺失分数对应 §12；固定总体推断对应 §11–12；逻辑新增数值总分类对应 §12；根 ROOT-S01 对应 §3/9。这里是候选关闭证据的位置，不是根代理宣布它们已通过。论文访问缺口和原 69L1/69E1 回执状态仍公开。

根代理构造利用了实际完整 NONBALLOT 建议：70C1 的有限到达带、70C2 的事件/统计问题素材，71 两项内部数学/协议协作与适配协作，以及 71C1 Claude 第二次完整回执。错误建议已独立留原文并拒收，尤其不保留旧指数屏障、不把 resident_ready 到达等于真实 Q、不从两个时间下界推先后、不按查询归因删任务、不以独立性证明符号置换、不声称条件于可发布仍自动 95% 覆盖。它们不替代任何正式审查，也不代表性能实证。

前置六门要求分别是：G1 可解释的实际误差问题；G2 已发表直接锚点及诚实路线比较；G3 固定官方 PIE-D 与可核适配/原法合同；G4 已发表外部固定基线与公平适用域；G5 公共场景/来源和闭合数据协议；G6 物理—算法—事务—费用—评价的公平纯仿真链。71 不自授门票，最新有效根裁决仍 70R4 的 2 PASS / 3 UNKNOWN / 1 FAIL。任何承重意见须后继新编号修复，不在受审字节上打补丁或封存 69/70。

最终完成审计须逐项核：交接/真实句柄/约定报告与固定身份；至少当前四份期刊完整文本及所有声称的读取强度；近邻和原来源任务缺口如何关闭；唯一原提议、真实偏差/可信界、P1–P3 与资源恢复；全部源适配/事件/模式/Stop/评分/估计总函数；公平全 roster/2×2/外部适用域/负例/机械合同；本工件三路有效完整顺序回执及根验收；私有 GitHub 精确文件同步；全部冻结/桌面/旧 35–38/受限载荷/未赋参数/禁止实施边界。证据缺失、间接或不确定都不得算完成。

在本工件完整固定和全部审查/六门闭合前，目标继续 ACTIVE，保持 HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。没有预先生成未来实验载荷或结果；后续是否实施不由文档篇幅、候选编号或审查次数决定。

71 CANDIDATE COMPLETE FOR SEQUENTIAL REVIEW — NOT ACCEPTED; NO IMPLEMENTATION OR EXPERIMENT AUTHORIZATION.
