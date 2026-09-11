# C20：动态原动作身份下的强轮询基线——有界数学建设

2026-09-11。NO-SKILL / CONSTRUCTIVE / NONBALLOT。只用下述自足合同，不用任何skill、工具、MCP、网络或文件，不写代码/伪代码、不做数值例子或生成实验载荷，不给任何模型/保护参数赋值。不是正式审稿、不是C14观测authority拒绝题或C17宽路线超时题的重试。以中文给不超过约700英文词的三个短部分，并以独占末行END-C20结束。允许明确否定根的建议。

固定有限机器人集合，episode中(session,agent)身份不更换，每个agent在中心至多一个GRANTED且未FINISHED的原MOVE tid；H19可以多条逻辑enqueued，但物理未闭请求同样至多一个。Active只是中心已提交知识，包含已发未安装/no-start/BRAKE/中点HOLD/物理已END但中心未知；真正FINISHED后同一agent可合法进入下一个原MOVE，动作序号e增加。每次QUERY只入队SELECT，付费固定中心Active/last等根，后继完整版本/模式验证并提交才生成指定tid的POSITION请求并推进last；未提交/过期不推进，采样/网络失败不回滚。中心writer串行，不从真实进度读谁已完成。公共有限O、容量/费用均保留，有限O可能没有足够成功选择。

当前R：last按(session,agent,e)全序，选Active中严格大于last的最小key，否则回绕最小；空Active不改last。根怀疑动作身份更替会让同一agent重复抢到另一持久Active成员之前：设稳定agent顺序a<b，选中(a,e)后，在下一次选择前a已合法结束并新进入(a,e')，e'>e，而(b,f)一直Active。此时(a,e')仍大于last且小于(b,f)，又选a。是否足以反驳“固定有限fleet即可保证在一次fleet轮询内选到持久成员”？这是中心状态选择规则的符号序列，不声称已证明官方R0实际输出这样的全部轨迹或运行了场景。

拟改法：Active资格仍按完整tid，但选择顺序只按固定(session,agent)。last_agent是稳定agent键，初始前哨；非空选择严格大于它的最小Active agent，若无则回绕；绑定此agent当时唯一Active tid请求POSITION。只有选择成功发布才last_agent←该稳定键；空集/失效/未提交不变，采样/网络失败不回退，删除及后继原MOVE不重置last_agent。若同agent出现多个Active tid即协议不变量破坏，不偷偷选其一。同一规则给R-S、R-F_cap及外部H19R-S。D仍纯阻塞计数：最大正分、原需求加入时间再完整tid tie；无正分回退该RR；每次D实际选中也推进last_agent，但不因此宣称混合D有RR公平保证。

请独立给：
1. 旧规则问题是正确的有限fleet轮询反例还是根漏了关键条件；明确它只影响何种公平声明，不泛称实际发生无限饥饿；
2. 新规则对于从某次选择前持续Active的同一tid，是否能在至多固定fleet基数个后继成功纯R选择提交内被选中，即使其他agent原MOVE更替；给简洁证明或最小符号反例。区分成功选择提交、实际CAPTURE新鲜度、消息到达和有限O整体进展；
3. 必要版本/费用/公开知识责任，以及为什么D正分更新同一cursor不能直接继承该界。不要承诺该更强R一定更好、D仍有正净收益或任何资格PASS。
