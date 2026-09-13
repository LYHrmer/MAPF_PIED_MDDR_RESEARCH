# C35 有限来源 arena 构造：完整回执与独立取舍

2026-09-13。建设咨询，不是正式审查票。主稿仍DRAFT / NOT-FIXED / NOT-REVIEWED / NOT-ACCEPTED，HOLD；没有实施代码或运行研究测试。

## 实际调用与完整性

- 实际提示：[C35 prompt](73C35_SOURCE_ARENA_NORMAL_DOMAIN_PROMPT_20260913.md)，按文件重定向传给CLI。
- 完整标准输出：[C35 raw JSON](73C35_SOURCE_ARENA_NORMAL_DOMAIN_RAW.json)。
- 命令：`rtk proxy claude --print --model opus --effort high --tools '' --safe-mode --no-session-persistence --output-format json < 73C35_SOURCE_ARENA_NORMAL_DOMAIN_PROMPT_20260913.md`。
- 首次普通沙箱exec64359（5f2457启动）在024c4f返回exit1，网络FailedToOpenSocket，API时间/费用为零、modelUsage为空，没有模型正文。实际终态后才依网络规则正常升级一次。
- 唯一升级exec86955（855e97启动）在05dcee返回exit0；实际模型claude-opus-5、provider firstParty、session_id 609af705-10c2-4bb4-b019-d95f59bd163d，is_error=false、terminal_reason=completed、stop_reason=end_turn，duration_ms=127477，记录费用0.1942475 USD。END_C35_ARENA_BOUND完整；不再轮询/重试。
- 调用未给工具权限、未用持久会话；原始正文超出提示要求的简短篇幅，完整保留下方，不省略错误段落。

首次网络失败原回执：

```json
{"is_error":true,"duration_api_ms":0,"num_turns":1,"stop_reason":"stop_sequence","session_id":"c27ca465-d598-4774-be40-ca7ef31f7d1c","total_cost_usd":0,"usage":{"output_tokens_details":{"thinking_tokens":0},"input_tokens":0,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{},"permission_denials":[],"terminal_reason":"api_error","fast_mode_state":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subtype":"success","api_error_status":null,"result":"API Error: Can't reach the API server — check your internet or DNS (FailedToOpenSocket)","type":"result","duration_ms":184914,"uuid":"e36047a9-9bf2-4d15-9cbc-5b50f9fcdf5f"}
```

## 模型原文（完整，不以根修正覆盖）

## 交付1：容量条件成立，但需四处修正

**命题（修正后）**：设槽域为 $[0,A)$，请求序列 $(r_j,q_j)_{j=1..m}$ 事前给定，$r_j\ge1,q_j\ge1$。令
$$S=\Big(\sum_{j=1}^{m}(r_j+q_j-1)\Big)-(q_1-1).$$
若初态全空、$A\ge S$ 且 $S\le 2^w-1$，则任意合法交错 free 下 first-fit 均不因碎片失败。

**证明**：设 $h_j$ 为第 $j$ 次分配后的**历史最高已占末位**（$h_0=0$），关键不变式是「$[h_j,A)$ 中每槽从未被标记过」——它成立当且仅当扫描本身不写 used、失败不留标记、且标记只在整段 $[p,p+r)$ 验证成功后一次性完成。于此不变式下，候选 $p^\*=q_j\lceil h_{j-1}/q_j\rceil\le h_{j-1}+q_j-1$ 满足 $[p^\*,p^\*+r_j)$ 全空；first-fit 取最小 $p_j\le p^\*$，故不论 $p_j$ 是否落在 $h_{j-1}$ 之下的空洞（含跨越 $h_{j-1}$ 的情形），
$$h_j=\max(h_{j-1},p_j+r_j)\le h_{j-1}+r_j+q_j-1 .$$
成功只需 $p_j\le A-r_j$，而 $p^\*+r_j\le h_{j-1}+r_j+q_j-1\le S\le A$。$j=1$ 时 $h_0=0$ 已对齐，故可扣 $q_1-1$。free 只清标记、不降 $h$，因此**只放宽**空洞、不破不变式：累计请求量而非活峰值正是必需的量，反例平凡（$q=1$，顺序分配释放 $m$ 个 $r=1$，活峰值 1 而 $h$ 可达 $m$）。

**四处必需修正**（缺任一则原猜想为假或不可用）：
1. **元数据不得计入 $A$**。used[$A$]、len[$A$] 另占同域，故真实约束是 $3A+\text{已计栈/对象容量}\le N$（$N$ 为 X 划出的字槽总数），且续体保存的扫描游标 $p$ 计入已计栈容量。$A\ge S$ 只是其一半条件。
2. **首址 0 必须与失败可区分**。$p=0$ 是合法结果（$0\bmod q=0$），失败须回传域外哨兵或独立布尔，不得用「0 表示失败」；len[0] 亦为正常活块记录。
3. **溢出**：判据只用 $p\le A-r$（先验 $r\le A$），不用 $p+r\le A$；$p^\*$ 用 $p+((q-p\bmod q)\bmod q)$ 且中间值 $\le A$。若先验 $S>2^w-1$，界虽数学成立却不可在模型内表示，条件作废。
4. **零大小与不同 $q$**：原零字节 new 计 $r_j=1$，必须进 $S$；$q_j$ 逐次不同不影响证明（$h$ 为绝对槽标）。可选收紧：若存在 $Q$ 使所有 $q_j\mid Q$ 且 $Q\mid r_j$，则 $S=\sum r_j$。

## 交付2：逐类操作次数上界

单次分配（成功或确定失败同界）：对齐检查 $T_{al}\le A-r+1$（单位步进+取模判据）或 $\lfloor (A-r)/q\rfloor+1$（步进 $q$ 时）；used 读取 $T_{rd}\le r\cdot(\lfloor (A-r)/q\rfloor+1)$（每候选早退于首个已占）；成功标记写 $=r$，len 写 $=1$；失败时二者为 0。free：len 读 1、边界/首址核验 $O(1)$ 个定字比较、清 used $=r$、清 len $=1$。原容器扩容一次：allocate($r(c_{i+1})$) 一次 + 逐元素 copy/move $=c_i$ + destroy $=c_i$ + deallocate($r(c_i)$) 一次；整条增长链的元素搬移总数 $=\sum_{i<k}c_i$，其中容量序列 $c_1<\dots<c_k$ 只能由**已冻结的库规则**给出，不由我拟定。

**到完整基本步数尚缺的固定映射**：(i) $P$ 模型每个已收费原语（字读/写/算术/比较/分支）到基本步的常数；(ii) 已冻结降级下「一次循环迭代」展开为多少个原语（索引自增、界比较、分支、`base+offset` 地址算术、一次 used 读）——该常数 $k$ 必须由降级钉住，不得虚构；(iii) 续体暂停/恢复自身的收费条目；(iv) 常数关于 $A,r,q$ 一致（全部值居于 $w$ 位内，无多字算术）。缺 (ii) 时以上只是操作计数，不能宣称数值步界；整段 scan 绝不记作 1 步。

## 交付3：关闭范围

**真正关闭**：分配为全函数且可判定——每次调用在上述有界操作内给出地址或**确定失败**，无无界搜索、无宿主 heap、无免费外部堆；全部存储来自 $A$ 与 $3A$ 域及已计栈；地址换算的有限性与可表示性；在修正条件下的无碎片性；失败是收费的确定结果而非未定义行为；语义不被归一化洗白（raw 不补 0、零大小仍占正长度故对象地址互异、double free/非首址/悬空/越界仍为源码失败）；无免费 realloc。

**仍欠**：首轮各臂的请求量界 $S$（须由已知对象数、循环计数与冻结容器容量规则事前上界，不得读一次成功结果补算）；容器源操作（元素 copy/move/destroy 收费、增长规则、零大小是否调用 allocate）；本合同与实际后端的对应（regex 显式裁出路径、私有有类型收费日志 sink、纯 LaCAM 输出点）。allocator 不保证算法求解成功（[S,G]、有限图、两 HNode/四 LNode 等另证）；不得以有限 RAM 状态数跳过正常终止与剩余表示义务；不声称全 AA/全净服务已闭。

END_C35_ARENA_BOUND

## 根与GPT-6-Astra Ultra的独立处理

用户本轮明确纠正分工：最难理论应交GPT-6-Astra Ultra，Claude适合承担代码工作。根已实际以model=gpt-6-astra、reasoning_effort=ultra、fork_turns=none派出astra_ultra_arena_closure，限定本题短证明及必要边界；其已完整交付。没有因模型名称给正确性保证，也没有把建设意见当正式票。

采用原始保守充分界S=Σ(r_j+q_j−1)，无需加入Opus首项扣减优化。证明量h取此前已验证保留区间最大右端，合法free不增该量；h之后距下一合格对齐点至多q_j−1，尾部候选存在，first-fit不会取更后的位置。区间验证后逐字标记可以按原私有续体暂停，完成前不发布且无其它arena操作介入即可。主稿新增完整语义、同一有限域容量、逐类计数及可选充分证书，并保持真实费用与后续资格的区分。

原文有以下错误或过强表述，未采用：
1. “当且仅当一次性完成标记”不成立；局部验证/独占保留后允许逐步付费标记，无需大块原子操作。源对象只在完成后发布。
2. 累计请求量不是成功必要条件。q=r=1且每次分配后立即释放，first-fit反复取零，历史最高右端为1，原文声称可达m的例子错误。主稿将其列为可替代的保守充分证书，不增加全roster无失败硬门。
3. offset=0不能直接充当C++指针0。成功偏移需映射到有效非空基址，失败状态独立；实际字节对齐为beta+b_word p≡0(mod a)，同余有解才有合法槽余数类，只有适当基址时才化成p mod q=0。主稿同时核完整字节地址换算。
4. 3A只包含数据和两张元数据表；所有其它预留存储及续体仍占同一个已有限域，并且初始化/访问收费。请求上界与扫描费用若依赖A，须对同一A同时证明相容，不允许事后扩堆沿用旧费用。
5. 原文对p*的加法写法和“中间值≤A”不能替代每个实际有限类型表达式的事前可表示性核验；保留单位步进扫描，其数学证明在整数域，不额外引入可能溢出的实现。
6. vector扩容的搬移/销毁按实际已构造元素数，旧capacity最多是上界；原有平凡复制等优化与嵌套分配照冻结源对应收费，不能把两个等号的虚收量当实际工作。
7. used/len不是全指针验证器，无法独自判定同址复用后的所有悬空/别名错误。free要求有效寿命/归属下精确活块头；源UB保持不合格，不因分配器有定义就得到整体源合法性。

现已关闭：所选分配器的确定扫描/对齐/保留/释放及具名失败语义、元数据容量边界、逐类访问次数和条件性无碎片失败证明。仍须组合批准正常源分支的事前请求界、固定容器操作、基本步映射及有限供给条件；实际后端符合性留后续资格。局部结论不替搜索成功、AA全历史、净服务或整个实验前目标完成。

后续模型分工已写入唯一入口：Astra Ultra承担关键研究推理与取舍，Claude Opus优先承担具备阶段授权和验收条件的实现/修复/调试，普通子智能体做有界事实定位，根整合验证。本次已有Opus任务收回并纠正后结束，不追加重复咨询。
