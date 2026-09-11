# C18 有界建设：保留参考扰动的 APPROACH 代数子族

2026-09-10。CONSTRUCTIVE / NO-SKILL / NONBALLOT。这是新的控制设计数学子题，不是C14观测精度/authority来源题的重试，也不是C17方法路线宽题的重启。只用以下完整局部方程；不用任何skill、工具、文件、MCP或网络，不编写代码/伪代码、不做数值例子/实验/仿真，不赋任何模型或保护参数数值/范围/默认，不声称任何source或整个方案通过。请求Claude Opus/high；根只认可实际完整回执，之后独立分析。

研究需要在不把随机延迟称为空间误差的条件下研究付费进度证据。实际实体X=u+s e+z+F，z_dot=-kappa z+w，真实w/z允许非零且本题不改它。另有参考s_dot=v、v_dot=a_cmd+eta，|eta|<=delta，0<delta<a_lo<a_hi，a_launch>0。本題只考虑已给定合法原MOVE的本地实际cap C；0<=s<=C、v>=0、v²<=2 a_hi(C-s)。

原控制：LAUNCH在v²<2 a_lo(C-s)取a_cmd=a_launch+delta；APPROACH在a_lo<=r<=a_hi，r=v²/[2(C-s)]，取
a_cmd=-r+delta*(a_hi+a_lo-2r)/(a_hi-a_lo)。
BRAKE取-a_hi-delta到首次零速，随后HOLD；显式BRAKE不能被扩cap或RUN提前撤销。扩cap保持s/v连续，C只增；运行时若新r<a_lo转LAUNCH，否则继续APPROACH。HOLD扩cap不自动RUN；旧cap到达与扩cap同刻先HOLD，原ell终点关闭优先，中点不END。

当前更广控制证明以任意有界可测eta给APPROACH闭带不变与有限到cap；实际有限表示候选只允许已发生eta因果前缀在公共O相邻不同时刻间为精确常值。不选O/系数/段数/分布。原合格字段可要求有限实代数表示，但不得默认任意积分值也代数。旧一般APPROACH在固定C、常eta时可写：D=a_hi-a_lo，k=2delta/D，r_star=(a_hi+a_lo)/2+eta*D/(2delta)，y=sqrt(C-s)，r(y)=r_star+(r0-r_star)*(y/y0)^(2k)，y_dot=-sqrt(r/2)。一般积分到达值与外部时刻的判等尚未关闭。

根提出新的、尚未采用的分析对象：只检查结构关系 **a_hi-a_lo=4delta**。它不给任何符号数值，也不改原a_cmd公式、实际eta或原执行器命令范围；但确实限制参数子域，不能冒充原整个参数域等价，更不能为过关做经验调参。若把它作为未来控制profile选项，必须检验与真实制动能力/其余原条件可共同满足，且事前披露/对所有臂相同。另有一个“删除参考eta的名义发生器”备选尚未采用；本题不重复评审那个备选，只说明此子族是否避免删除eta这一科学代价。

请独立核验下面待证推导，而非默认它正确。在该关系下令A=r0-r_star，r_star=(a_hi+a_lo)/2+2eta，h0=sqrt(r0)。猜想在首次到cap之前：
y(tau)=y0-h0*tau/sqrt(2)+A*tau²/(8y0)；
sqrt(r(tau))=h0-A*tau/(2sqrt(2)y0)；
T_cap=2sqrt(2)y0/(sqrt(r0)+sqrt(r_star))。
若为真，s=C-y²、v=sqrt(2)*y*sqrt(r)可在任一给定代数tau精确表示，T_cap亦代数，A=0不必除A。请检查最早根/分支正性、r_star/带界、合法非零速入口、eta/cap切换后重置局部常量的有限组合、LAUNCH/BRAKE是否同样代数以及同刻旧cap/HOLD优先是否仍必须保留。

给三个短部分，合计不超过1000英文词或相当中文长度：
1. 真正成立的推导或一个明确符号反例；
2. 这个子族保留/限制了什么物理及参数范围，是否偷偷要求更强执行器或免费测eta；
3. 一个清晰建议：是否值得作为不同的后继工作选择比较，以及仍不能据此声称实际计费后端、观测信息/精度、有限O进展或净吞吐通过。
只有数学表达式与说明，无实现/伪代码或实例参数。允许说推导不成立或不值得采用。请以独占最后一行 END-C18 结束。
