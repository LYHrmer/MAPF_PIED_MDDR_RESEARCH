# 69C1: Opus constructive advice transport receipt

- Date: 2026-09-05 (Asia/Shanghai).
- Role: constructive NONBALLOT adviser; this is not a formal review or a qualification decision.
- Requested model alias: `opus`.
- CLI-reported model: `claude-opus-5`; this identifies the client receipt, not independent attestation of the provider backend.
- Local execution handle: `6394`; exit code: `0`.
- CLI session: `0070e914-b42b-41db-8af8-e081f13aa1a9`.
- Receipt: nonempty JSON, `is_error=false`, `terminal_reason=completed`, final response marker `ADVICE-COMPLETE`.
- Candidate context reference: `e07cc5c7dd3e87d4e03d6e7cd544dedad5f05b686585494630c497f4ae1eb80d`.
- The adviser received a synopsis, not the candidate bytes. No candidate full-read, start/end identity, formal-review validity, or approval is claimed.
- Root disposition: TRANSPORT-VALID / NONBALLOT / NOT-ADOPTED-AS-WRITTEN.
- Project disposition: HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT.

## Root acceptance boundary

The reply contributes possibilities for observation-feasible sets, causal propagation of delayed evidence, and abstraction refinement. These remain design suggestions requiring derivation and independent review.

The following parts cannot be adopted as written:

- Replacing an individual MOVE with WAIT is not generally safety-preserving. Following traffic and already committed motion require complete dependency closure and physical holding checks. The reply's G2 is false without these conditions.
- A signature, epoch, software token, or new owner does not certify that an old physical occupant has cleared a resource. In-flight actions and origin release still need physically sound evidence.
- Safety cannot be inserted into an estimator as an assumed mutual-exclusion constraint and then established by that same estimator. Initial-state and transition premises must independently justify every pruning step.
- A CLEAR observation does not, by itself, rule out an approaching robot or an irrevocable old authorization. The worked example needs those additional exclusions.
- The displayed delayed-observation update leaves the union over possible generation instants and compatibility with subsequent evidence underspecified. It is not an accepted executable recurrence.
- Existence of a safe recovery action in each hidden state does not imply an observation-based controller can select one common safe recovery action. Detection delay, actuation, and recoverability assumptions cannot turn statistical coverage into unconditional safety.
- Different modalities, clocks, roots, or authentication mechanisms alone do not prove statistical independence or physical truth.
- Protected project symbols must retain their existing meanings. The reply's uses of H, T_delay, B_CAL, B_max, B*, P_active, and density N do not redefine, assign, calibrate, or unlock them.
- Claimed density-dependent benefits, irrecoverability exclusion, sensitivity properties, and preservation of planning properties are unproved hypotheses, not research findings.

The complete received reply is archived below for attribution and audit only. No raw advice overrides a bearing objection or authorizes implementation.

## Prompt supplied to adviser

```text
你是建设性NONBALLOT顾问，请给可落地的数学与协议设计，不做正式审稿，不使用工具或读取文件。研究背景：MAPF，PIE/PIE-D保持唯一默认MOVE提案源；外层只能保留原MOVE或降级为安全WAIT/containment。导师希望主问题来自真实误差，可联合处理延迟，不能只把随机延迟改名误差。候选69注册hash e07cc5c7dd3e87d4e03d6e7cd544dedad5f05b686585494630c497f4ae1eb80d，此处只给概要不是全文，你不能声称读过候选或审查通过。已有方案是进度状态集合、提交证据、逆向WAIT闭包、资源fencing与按需获取可信证据。请独立构造一个能真正利用含误差观测减少保守性的有限状态/集合方法：分别处理有界误差、仅分布假设、任意错误，给状态转移与观测可行集合的精确更新规则、处理延迟的因果时间对齐、不重复计算相关证据、空集合故障与重新初始化条件；解释不依赖完美传感器时什么安全保证仍可能成立，并给反例。给一个纯符号的最小机器人共享资源示例，说明比无视观测并全局停车多保留哪条原提案MOVE、为什么安全，以及何时没有收益。给2个建设性替代方向和优先推荐，不假造论文/实验结果，不承诺新颖性或录用。不把SCC原子软件提交等同于物理同步执行；不把任何WAIT当作自动安全。H、T_delay、B_CAL、B_max、B*、P_active、density N只保留未赋值符号，不给数值或范围。不得给实验参数。纯仿真为主，不实现/测试/跑仿真。请用中文输出约2500-4000字，结尾写 ADVICE-COMPLETE。
```

## Complete received reply

下面是一个独立构造的方案骨架。声明：我没有读过候选 69 的全文（仅见你给的概要与注册 hash e07cc5c7…eb80d），以下不构成对该候选的审稿意见、不判断其新颖性或结论，也不引用任何论文或实验数字；所有量均以未赋值符号出现。

## 0. 设计目标的重述

外层是**单调门（monotone gate）**：只能保留 PIE/PIE-D 给出的原 MOVE，或降级为 WAIT/containment。因此"利用含误差观测降低保守性"在数学上只有一条通路：**缩小外层用于判定的假设集合**，使"所有残余假设下 MOVE 都安全"这一全称命题更容易成立。观测不能创造新动作，只能**认证旧动作**。这一点决定了全部更新规则必须是**外近似（over-approximation）**意义下可靠的：宁可集合偏大（保守、损失活性），不可偏小（不安全）。

同时要回应导师的两点：误差必须从**观测映射**进入（它裁剪的是进度状态的**类别**），延迟从**因果对齐窗口**进入；两者通过"回溯—再预测"的复合算子耦合。若某"误差"只等价于把窗口 [Δ_lo, Δ_hi] 加宽，那它就是被改名的延迟，不是误差——第 4 节给出可机械检验的判别式。

## 1. 基本对象：双层有限自动机 + 可能性集合 + 约束网络

对每个机器人 i 设两个有限自动机：

- **决策自动机** A_i^d = (Q^d, Σ^d, δ^d)：状态如 IDLE、REQUEST(r)、COMMIT(r)、REVOKE(r)、DONE(r)。它可以由软件层原子提交（例如 SCC 意义的原子写）在一个逻辑时刻改变。
- **物理自动机** A_i^p = (Q^p, Σ^p, δ^p)：状态如 FREE、APPROACH(r)、OCCUPY(r)、CLEAR(r)。它**不**与决策同刻变化。

**关键约束（不把软件原子性当物理同步）**：耦合关系 L 只断言"若决策在逻辑时刻 k 进入 COMMIT(r)，则物理进入 OCCUPY(r) 的时刻落在 [k+a_lo, k+a_hi]"，其中 a_lo, a_hi 为符号化的执行滞后界；反之"决策未 COMMIT(r)"只能推出"物理在 k+a_lo 之前不 OCCUPY(r)"。所有 fencing 只约束决策变量，安全不变式写在物理变量上，二者靠 L 桥接。这是把"原子提交 ≠ 同步执行"显式建模的地方。

**可能性集合**：S_k = ( S_k^{i,d} ⊆ Q^d, S_k^{i,p} ⊆ Q^p )_i，加上耦合约束集 C（互斥：∀r，至多一个 i 处于 OCCUPY(r)；L；以及路径拓扑约束）。联合集合不显式枚举，用**弧一致性/路径一致性投影** Π_C 做剪枝。Π_C 只删除局部不可行元素，**可靠但不完备**：不完备只带来额外保守性，不带来不安全。这条"不完备即保守"的性质要在文中作为引理明确。

## 2. 观测作为约束：安全单侧性（最重要的一个设计选择）

对观测 z 定义**观测可行集** Y(z) ⊆ Q（或其笛卡尔分量），要求：

> **可靠性公理**：若真实状态为 q 且误差在其规定模型内，则 q ∈ Y(z)。

于是更新只是交集 S ← S ∩ Y(z)，其可靠性平凡成立、且**交是幂等且单调**的（这一点在第 5 节被用来简化"重复证据"的处理）。

工程上最有价值的是**安全单侧观测**：只允许在"误差方向被认证为单侧"的分量上收缩。例如占用检测器满足"无假 CLEAR"（可能把空报成占用，不会把占用报成空），则 z = CLEAR 时 Y(z) 可以剔除 OCCUPY 类状态；z = BUSY 时 Y(z) = Q（不收缩，只用于活性启发或故障监测）。这样廉价、误差大的传感器也能**合法**降低保守性，因为我们只使用它误差被界定的那半边。设计规则：每个传感通道必须在接口上申报 (方向, 误差模型, 界符号)，门只接受申报为安全方向的收缩。

## 3. 三种误差层级的精确更新规则

用三层证据分级，分别对应三种假设强度；三层不混用，各自维护自己的集合。

**(A) 有界误差（hard tier）**
证据自带界符号：标称/在线校准界 B_CAL，认证的最坏界 B_max。规则：

- 用于**安全判定**的收缩只允许使用 B_max 诱导的 Y_{B_max}(z)（更大、更保守的集合）；
- B_CAL 诱导的 Y_{B_CAL}(z) 只允许用于**活性排序**（在若干均已被认证安全的选择中挑一个）与故障监测；
- 记录**所需裕度** B*：即使 MOVE 被认证，也计算"若界放大到多少就不再可认证"的临界符号量 B*，作为敏感性标签随决策一起输出。B* 与 B_max 的关系（是否紧贴）是评估该决策脆弱性的唯一合法指标，不给数值。

更新：S ← Π_C( S ∩ ⋂_{z ∈ Z_k^{hard}} Y_{B_max}(z) )。此层保持**不变式安全**（在界成立的前提下）。

**(B) 仅分布假设（soft tier）**
此时交集不再可靠，改用 α 级可信集 Y_α(z)（后验/置信意义下最小的、覆盖概率 ≥ 1−α 的状态集）。两条硬性设计：

1. **风险账本**：为水平线 H 维护一个风险台账，每次用 soft 证据收缩就登记一次消耗；同一"相关块"（共源、共时隙、共标定）内用并集界叠加，跨块只有在设计上论证了独立性（异构模态、独立时钟、独立标定）时才允许乘性组合。台账不给数值，只给可加性与守恒规则。
2. **可恢复性必要条件（本层的核心）**：只有当被 soft 证据排除、但仍属 hard 层集合的那些假设 h 满足"若 h 为真，则在被检测到之后于 T_delay 内仍存在可执行的 containment，使不变式不被破坏"，才允许用 soft 证据保留 MOVE。形式化：
   ∀h ∈ (S^{hard} \ S^{soft})，∃ 动作序列 a 使 Reach_{[0,T_delay]}({h}) 在 a 下不进入 Bad。
   这把"以概率 1−α 安全"改造成"以概率 1 不发生不可挽回后果、以概率 1−α 不损失活性"，是真正值得追求的保证形态。

**(C) 任意错误（no-model tier）**
观测可能任意错，**不得**用于收缩。它有三种可靠用途：

1. **一致性监测**：若 Y(z) ∩ S = ∅（在 hard 层模型下），则模型被伪证 → 触发第 6 节流程。只用于变得更保守，故可靠。
2. **平局裁决**：在所有候选均已被 hard/soft 层认证安全时用来选择。
3. **可自证证据的替代**：把"传感"换成"协议构件"——带签名、带纪元号、带撤销延迟承诺的租约/令牌。只要认证消息通道的失效模型是有界的（可检测的丢失/延迟），令牌就属于 hard 层，即使物理传感是任意错的。此处必须显式区分"任意错误的感知通道"与"可验证的协议通道"，只对后者做交集。

## 4. 延迟的因果时间对齐：回溯—再预测

每条证据携带 (t_gen 的界, t_recv)，陈旧度 Δ ∈ [Δ_lo, Δ_hi]（符号）。**错误做法**是把 Y(z) 直接与当前集合相交。正确算子是固定滞后的集合平滑：

  S_k ← Reach_{[Δ_lo, Δ_hi]}( Π_C( S_{k−Δ} ∩ Y(z) ) )

其中 S_{k−Δ} 取自长度 H 的有界历史缓存（H 为符号）；若 Δ_hi 超过 H，则该证据只能以其 Reach 闭包形式使用（通常退化为无信息）。要求：

- **非预期性**：纪元 k 的判定只使用 t_gen ≤ k 且 t_recv ≤ k 的证据；
- **窗口认证**：门必须认证的不是当前时刻，而是窗口 W = T_delay + 动作执行跨度上的 Reach 闭包：
  保留 MOVE_i ⟺ Reach_{[0,W]}(S_k) ∩ Bad(MOVE_i) = ∅；
- **WAIT 不自动安全**：降级动作 a（WAIT 或 containment）同样要过 Reach_{[0,W]}(S_k) ∩ Bad(a) = ∅，并且要求存在非空的逆向 WAIT 闭包（即在窗口内每一点仍有可用的停车/收容后继）。若 MOVE 与所有 a 都不可认证，进入应急分支（第 6 节）。

**误差 vs 延迟的判别式**（回应"不能改名"）：定义信息增益条件

  Reach_{[Δ_lo,Δ_hi]}( S_{k−Δ} ∩ Y(z) ) ⊊ Reach_{[Δ_lo,Δ_hi]}( S_{k−Δ} )。

若对某族观测该真包含仅在缩小 [Δ_lo, Δ_hi] 时才成立，则该"误差"是延迟的重述；若在窗口固定时它已经剔除了整类进度状态（例如剔除全部 COMMIT(r) 分支），则误差确实是独立的信息维度。论文的主问题应当围绕后者构造，并把**Reach 闭包饱和**（窗口宽到足以从任意非冲突状态走到冲突状态）作为"延迟吃掉观测价值"的临界现象来分析。

## 5. 相关证据不重复计算

- **证据 DAG**：每条证据带 (source_id, 纪元, 祖先集)。转发/派生的证据继承祖先。
- **hard 层**：交是幂等的，重复应用同一证据无害；真正的危险是**循环自证**——A 的集合被用来推导 B 的断言，B 的断言又回来收缩 A。对策：为每个集合附**假设多重集**标签（它依赖了哪些 α 级假设、哪些界符号、哪些主体的自述），禁止与任何祖先集中含"本主体当前待证假设"的集合求交。
- **soft 层**：禁止对同一相关块内的多条证据做乘性更新；块的划分必须由设计（硬件/时钟/标定的物理隔离）给出，不由数据估计。
- **法定人数式计数**：计"不同根祖先"的个数，不计消息条数，避免转述被当作独立佐证。
- **按需取证**：请求必须指明目标纪元；同源同纪元的重复查询返回同一 evidence_id（幂等）；只有祖先不交的跨源查询才允许进入不同的相关块。取证预算按纪元分配，避免在高争用时用查询风暴换取虚假的独立性。

## 6. 空集故障与重初始化

S = ∅（或 Π_C 检出不可行）意味着模型被伪证，可能原因：B_max 偏小、δ 缺失未建模事件、Δ_hi 超出 H、共模标定漂移、对等体违约。协议：

1. **立即 fail-closed**：切到不依赖估计器的收容模式——只用已持有的物理 fencing 与**离线预计算的收容证书**（几何/运动学层面自足的停车可行性），不使用任何在线集合。注意此模式必须在离线阶段就被证明存在，否则"空集"时无处可退。
2. **诊断阶梯**：按信任度逆序松弛证据（先丢 soft 层，再丢 B_CAL 层，最后只留 B_max 与协议令牌），求**极小冲突集**（minimal unsatisfiable subset）。
3. **重初始化**：S ← 顶元素（各分量取全集），再交上物理不变式与仍在有效期内的可验证协议令牌；历史缓存清空并重新计时。
4. **隔离**：极小冲突集中的源进入隔离，直到通过再认证（交叉模态一致性、时钟再同步）。
5. **恢复条件**：仅当存在非空 S 且存在有效收容证书时，才重新开启门；否则保持收容。
6. **反向监测（防止"永不为空"的虚假健康）**：过宽的 δ 会让集合永不为空，从而掩盖故障。为此监测"证据无信息率"（Y(z) ⊇ S 的比例）与"约束松弛度"，作为抽象过宽的定性信号（不给阈值数值）。

## 7. 不完美传感器下仍可能成立的保证，以及反例

**仍成立**：
(G1) 在 B_max 成立的条件下，hard 层保持不变式安全（交集外近似 + 窗口 Reach 认证）。
(G2) 单调降级性：门只能弱化 MOVE，故不会破坏 PIE/PIE-D 的既有计划层性质；门只能损失活性。
(G3) fail-closed：空集 ⇒ 收容（前提是收容证书离线存在）。
(G4) soft 层给出"H 上的概率不变式 + 不可挽回事件被 hard 层排除"的双层保证。
(G5) 任意错误层给出故障检测与平局裁决，不破坏 (G1)。

**反例（说明界限）**：
- **共模偏差**：地面反光/同批标定漂移使所有里程计同时超出 B_max。集合非空（因为一致地错），MOVE 被认证，两机器人进同一格。教训：非空性诊断隐含"源独立"，共模失效必须靠异构模态显式监测。
- **不可挽回的 α 分支**：soft 证据排除了"对等体已进入交叉口"，而该假设一旦为真，检测到时已超出 T_delay 无法中止。此时安全性确实以概率退化——必须被第 3(B) 节的可恢复性条件禁止。
- **WAIT 致害**：A 在走廊格停车，而 B 的 MOVE 已物理进入不可中止段，唯一出口被占 → 停车导致碰撞或死锁。说明必须对 WAIT 做同样的窗口认证与逆向闭包检查。
- **循环自证**：A 依据"我持令牌"推出"B 已释放"，转发给 B；B 回传，双方各自认证 MOVE。由假设标签禁环规则阻止。
- **陈旧证据（安全但无收益）**：释放令牌迟到超过 H，只能用 Reach 闭包 → 退化为无信息 → 降级。这是活性损失而非安全损失，正好与前两例对照，用于说明"哪些不完美只吃活性"。

## 8. 纯符号最小共享资源例子

对象：机器人 R1、R2；资源为交叉格 j；R1 的路径 …→ p1 → j → q1，R2 的路径 …→ p2 → j → q2。PIE/PIE-D 的默认提案：MOVE_1 = R1 由 p1 进入 j；MOVE_2 = R2 保持在 p2 之前的段（其提案与 j 暂不冲突）。

**无视观测 + 全局停车**：外层必须在假设集合中保留"R2 的物理状态可能已是 OCCUPY(j)"（因为释放/提交信息可能陈旧），于是 Bad(MOVE_1) 与残余集合相交 → MOVE_1 被降级为 WAIT，R1 停在 p1。

**本方案**：
1. R1 持有 j 的 fencing 令牌（决策层原子提交，属可验证协议通道 → hard 层）。由 L 得：R2 的决策集合不含 COMMIT(j)，故 R2 的物理集合中 OCCUPY(j) 只能来自 t_gen 之前已提交的分支。
2. 一次安全单侧占用观测 z = CLEAR（无假 CLEAR，误差界 B_max），生成时刻界 t_gen，陈旧度 Δ ∈ [Δ_lo, Δ_hi] ≤ H。按第 4 节：先回溯到 k−Δ 与 Y_{B_max}(CLEAR) 求交（剔除 OCCUPY(j) 与其不可中止前驱），再用 δ^p 前推 [Δ_lo, Δ_hi]。
3. 令牌约束使前推不会重新引入 OCCUPY(j)（因为重新进入需先经 COMMIT(j)，而 COMMIT(j) 已被令牌排除）。
4. 门检查窗口 W = T_delay + R1 穿越 j 的跨度上的 Reach 闭包与 Bad(MOVE_1) 不交；同时逆向 WAIT 闭包在窗口内每点非空（R1 若中途撤销，可退回 p1 或在 j 前停住）。
5. 结论：**MOVE_1 被保留**，R1 不停车；R2 的提案不受影响。

**为什么安全**：残余假设集合中不存在"R2 在 R1 穿越窗口内占用 j"的状态；该结论只用了 (i) 交集的外近似可靠性、(ii) 令牌的可验证性、(iii) 单侧误差方向、(iv) 回溯—再预测的因果正确性；且保留了备用收容路径。注意它**不**依赖传感器完美，只依赖"无假 CLEAR"与 B_max。

**何时没有收益**：
(a) 令牌不可用（决策通道降级）→ 前推重新引入 OCCUPY(j)，观测被 Reach 闭包吃掉；
(b) Δ_hi 大到使闭包饱和（R2 从任意非冲突态都能在窗口内到 j）→ 观测无信息；
(c) PIE/PIE-D 本身提案就是 WAIT → 门不能上调；
(d) 几何/运动学残差要求 B* 严于 B_max → 不可认证；
(e) 密度 N 与活跃比例 P_active 升高时，争用使残余集合几乎总含冲突态，且 Π_C 的弧一致性剪枝变弱，收益趋零——这应作为方案的**已知失效区**主动报告，而不是被掩盖。

## 9. 两个替代方向与优先推荐

**替代方向 I：租约/义务式解耦（协议优先）**。不去估计对等体状态，而让每个机器人发布**带纪元的义务**："在纪元 e 之前不占用 j，除非先发布撤销，且撤销后我自身在 T_delay 内可安全中止"。外层只做**契约算术**（纪元 + 撤销延迟 + 执行滞后界的区间运算），观测降为契约违约监测。优点：对任意传感误差鲁棒，延迟被一等公民化，可在纯符号层证明；缺点：需要可靠认证通道，且义务过紧会自我保守。

**替代方向 II：抽象精化驱动的保守性削减（CEGAR 式）**。保持观测能力不变，转而在离线循环中记录每次门"起约束作用"的极小冲突集，据此**分裂抽象进度状态**（例如把 APPROACH(r) 拆成可中止/不可中止子类），重算收容证书。效果是所需分辨力 B* 变松，于是廉价传感器也够用。优点：纯仿真可闭环、无需新硬件假设、与 PIE/PIE-D 的接口不变；缺点：状态空间增长与证书重算代价，需给出终止/单调性论证。

**优先推荐**：先做 I，再叠 II，最后把第 3(A) 节的 hard 层观测门作为 I 的补强；soft 层只作为活性优化并强制可恢复性条件；任意错误层只做监测与 fail-closed。理由：(1) I 直接同时承载"真实误差 + 延迟"的联合处理，且不引入分布假设，答复导师"不能只是随机延迟改名"最有力；(2) II 提供可度量的保守性下降机制，而其度量对象（哪条 MOVE 被保留、B* 的紧度）是纯符号可陈述的；(3) hard 层观测门的边际收益在低 N、低 P_active 区最明显，适合作为案例研究而非全局主张。

## 10. 纯仿真下的最小验证计划（不含参数）

只报告三类符号化量：被保留的原 MOVE 的**集合级刻画**（在哪些残余集合形态下可认证）、B* 相对 B_max 的紧度、Reach 闭包相对 Δ_hi 的饱和临界；配以四个可复现的构造性场景（令牌缺失、闭包饱和、共模偏差、WAIT 致害），每个场景给出"应当降级"与"应当保留"的期望判定，用作门的正确性回归。不做任何数值声明、不预设收益幅度、不主张新颖性。

ADVICE-COMPLETE

## Transport metadata

```json
{
  "is_error": false,
  "duration_api_ms": 271086,
  "num_turns": 1,
  "stop_reason": "end_turn",
  "session_id": "0070e914-b42b-41db-8af8-e081f13aa1a9",
  "total_cost_usd": 0.39502875000000004,
  "usage": {
    "input_tokens": 2,
    "cache_creation_input_tokens": 915,
    "cache_read_input_tokens": 0,
    "output_tokens": 15572,
    "output_tokens_details": {
      "thinking_tokens": 0
    },
    "server_tool_use": {
      "web_search_requests": 0,
      "web_fetch_requests": 0
    },
    "service_tier": "standard",
    "cache_creation": {
      "ephemeral_1h_input_tokens": 0,
      "ephemeral_5m_input_tokens": 915
    },
    "inference_geo": "",
    "iterations": [
      {
        "type": "message",
        "input_tokens": 2,
        "cache_creation_input_tokens": 915,
        "cache_read_input_tokens": 0,
        "cache_creation": {
          "ephemeral_5m_input_tokens": 915,
          "ephemeral_1h_input_tokens": 0
        },
        "output_tokens": 15572
      }
    ],
    "speed": "standard"
  },
  "modelUsage": {
    "claude-opus-5": {
      "inputTokens": 2,
      "outputTokens": 15572,
      "cacheReadInputTokens": 0,
      "cacheCreationInputTokens": 915,
      "webSearchRequests": 0,
      "costUSD": 0.39502875000000004,
      "contextWindow": 200000,
      "maxOutputTokens": 64000,
      "canonicalModel": "claude-opus-5",
      "provider": "firstParty"
    }
  },
  "permission_denials": [],
  "terminal_reason": "completed",
  "fast_mode_state": "off",
  "fast_mode_disabled_reason": "sdk_opt_in_required",
  "subtype": "success",
  "api_error_status": null,
  "ttft_ms": 129771,
  "ttft_stream_ms": 1680,
  "time_to_request_ms": 22,
  "type": "result",
  "duration_ms": 271110,
  "uuid": "cce600dc-07f6-48ec-a52e-f5972379b6c5"
}
```
