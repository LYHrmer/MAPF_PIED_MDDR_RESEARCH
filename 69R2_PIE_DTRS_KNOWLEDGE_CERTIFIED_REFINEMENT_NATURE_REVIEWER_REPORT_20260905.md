# 69R2 正式第二路独立 Nature 审查报告

日期：2026-09-05，Asia/Shanghai。

身份：本会话实际执行任务的 Codex，正式第二路独立 Nature 审查代理。Reviewer 1、2、3 是同一代理依 skill 生成的三个评价权重视角，不是三个真人或三个独立模型。未派出子代理，身份全程未切换。

**审查工作 COMPLETE；完整读取与身份 VALID；候选实验前闭合 NOT PASSED；8 项 OPEN bearing。**

**HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。**

## Review setup

### Input scope、来源与边界

唯一科研输入为[候选69](/home/lyh/MAPF_PIED_MDDR_RESEARCH/69_PIE_DTRS_KNOWLEDGE_CERTIFIED_PROPOSAL_PRESERVING_TRANSACTIONAL_REFINEMENT_PREEXPERIMENT_CANDIDATE_20260905.md:1)。完整应用 [nature-reviewer/SKILL.md](/home/lyh/.codex/skills/nature-reviewer/SKILL.md:1) 及下表七份本地参考文件。未读取第一路科研导师报告、其他审查报告或顾问回执；未读旧35-38、Q-CAL/Q-CONFIRM outcome/scientific payload、桌面备份或根目录进度同步文件。候选中出现的前代文件名和继承裁定不作为本路通过证据。

未访问候选所列外部论文、网页或仓库。因此“官方”、版本、许可和先前研究归属均是稿内事实，未升级为本路外部核验。技能的本地 Nature 来源确定评价轴和角色边界；只用候选提供技术事实，不补造来源内容。

只判断实验前自洽、可计算、可证明、公平及可复核性。不因尚未实施、没有效果或实物数据而拒绝闭合。不执行构建、测试、仿真、调参、载荷生成、原方法复现或 release 更新。H、T_delay、B_CAL、B_max、B*、P_active、density N 全部保持未赋值；本报告不给值、区间、默认、先验、估计或调参方向。参数未赋值可接受，规则主体未定义仍需修复。

### 注册、开始、结束与完整读取账本

用户注册候选 SHA256 为 e07cc5c7dd3e87d4e03d6e7cd544dedad5f05b686585494630c497f4ae1eb80d，50975 bytes，787 lines；首次文件核验匹配。正式开始核验：2026-09-05T05:31:12Z；全文读取及技术判断后的结束核验：2026-09-05T05:37:52Z。

用户未预注册技能哈希。本路实际先完整读取技能、缓存原样返回并登记该快照，随后正式开始的文件指纹、缓存原文指纹和结束指纹一致；不冒充存在更早的用户技能注册。

| 文件 | 读取快照 SHA256；开始和结束均匹配 | bytes | wc -l | 实际内容读取范围 |
|---|---|---:|---:|---|
| 候选69 | e07cc5c7dd3e87d4e03d6e7cd544dedad5f05b686585494630c497f4ae1eb80d | 50975 | 787 | 1-787 |
| SKILL.md | 86e331346aa92daa10de15c1ceb451328ad0f84e0624a3b53b86ba306c1c2735 | 6112 | 127 | 1-127 |
| references/source-basis.md | 41c738a525afc4bf05eac846d91ce7e26617b5d43e8d0bc0f13f2ec020e63d7b | 4527 | 77 | 1-77 |
| references/reviewer-workflow.md | 5f8adfe5db8de8073285e73bbc9f7f5640720b3ea4d5588d4548a239ddf526e2 | 2577 | 56 | 1-56 |
| references/review-axes.md | 56ddd649de9b1a961d649892f235bcddd883836bbcd1c32b352071441fa286ee | 3309 | 58 | 1-58 |
| references/report-structure.md | 419a87f337d1ae234afc8c4740eacfa28bf560f84fefc07931251ab87a7d1548 | 2203 | 66 | 1-66 |
| references/role-boundaries.md | 2ba909a020d9f5de2fe18be693ea359d3c8e247b7557f45d16d4092e98b68af3 | 2529 | 49 | 1-49 |
| references/qa-checklist.md | c1544136ec6100ef61b08af2bfc03483ea891e39dce49c41fa86e5178d3de9de | 1873 | 39 | 1-39 |
| references/editorial criteria and processes.md | 93b46198ecc5c68e6b5fb31bc9c3f77a4d869cef631dfbd6ab361766bc919cdc | 4391 | 45 | 1-46（末行无换行） |

技能和参考文件路径以 /home/lyh/.codex/skills/nature-reviewer/ 为根。主来源有46个逻辑行、45个换行符，末行无换行；末行已读，不是缺段。

每个输入文件仅一次 rtk proxy cat 原文读取。按要求另作的哈希/计数扫描不作为再次内容审读。所有原文返回均非空且成功，缓存按 UTF-8 算得的哈希、bytes、换行数与磁盘元数据逐项相等。

候选一次读入工具缓存，读取预算45000 tokens，返回 original_token_count 为12744；展示区间依次为 L1-L160、L161-L360、L361-L560、L561-L787，互不重叠、完整覆盖。技能及参考文件整份展示。未硬截断，无需补缺段；缓存展示没有再次打开文件。不存在空内容输出、身份变化或未完成读取。

报告目标检查为 REPORT_ABSENT，仅通过 apply_patch 新建本报告，不覆盖已有文件。报告自身 SHA256、bytes、lines 在交付时单独返回，避免正文自引用哈希。

### Shared manuscript claim summary 与可见证据

本稿针对已经由 PIE 提出、可由 PIE-D 延迟策略先缩减的固定动作批次，利用提交时知识集合决定保留原 MOVE、改成安全 WAIT、继续既有事务或不给新授权，不生成替代 MOVE。错误/不可靠的完成和当前状态证据是问题本体，计算处理期间的状态演化也被纳入（L27-L43、L78-L105、L158-L176、L271-L287）。

D-start 明确是延迟；F-false-complete、F-state 是真实发生的反馈载荷错误，不是给延迟换名。但“误差”在此限定为报告内容错误及知识后果，不含连续定位、任意轨迹偏差或制动正确性。仿真可研究这种受限对象，不能自动验证物理传感器与制动接口。

可见证据为形式定义、条件推导、事务表、22个未来见证条目、来源定位和比较/预注册框架；它们不是已经执行的机械证明或实验结果。缺失集中于判定原语、阶段守卫、比较耦合和确定的参数化协议。

## Reviewer 1

评价重点：technical soundness / technical failings；不增加虚构身份。

### Overall assessment

安全组合的方向可信，但“可计算且可独立重算”仍依赖未完全定义的原语。条件前提列表不足以替代操作语义。

### Who would be interested / Major strengths

PIE/PIE-D 执行及异步资源授权研究者会关心错误反馈如何改变可提交集合。L172-L176 分离消息与物理真值，L267 和 L335-L343 分离原子提交与物理联动，L361、L734-L738 分离资源模型与硬件安全。这些基础应保留。

### Major concerns / Technical failings

#### B01：知识域、关联标签与证书原语尚不足以支撑可计算性和复杂度主张

**候选依据：** [L182](/home/lyh/MAPF_PIED_MDDR_RESEARCH/69_PIE_DTRS_KNOWLEDGE_CERTIFIED_PROPOSAL_PRESERVING_TRANSACTIONAL_REFINEMENT_PREEXPERIMENT_CANDIDATE_20260905.md:182)，尤其 L182-L228、L295-L301、L456-L466。

**精确缺口：** lo、hi、holes、choice、txn_tags 被列为字段，但没有给出后两类的有限语法、联合具体化、冲突合并及约束传播规则。CERT 又要求所有资源义务相容，却未明确自身占用、既有事务占用、可联动释放之间的判定关系。有限输入并不自动给出所宣称的多项式检查算法；“传播时检查一致性”也不能代替传播规则。本路没有据此宣称某个满足所有前提的轨迹已经碰撞，也没有凭空断言标签检查必然困难。

**可执行修复：** 在后继文本中固定标签与资源约束的有限语法，定义具体化、join、可信收缩及一致性处理的逐条规则；把 CERT 分解为输入输出明确的可判定谓词。说明物理阶段推进和新命令纳入知识域的转换。为每个索引、传播步骤和扫描给出成本，不能将完整 CERT 重算当作无成本操作。

**客观闭合证据：** 读者仅凭文内定义即可对任意合法编码确定“保留/拒绝/包含性恢复”和所需证据；逐类更新的包含性归纳明确覆盖字段交互；复杂度推导能按编码大小逐项计费。若只能证明更保守的算法，应缩小表示域或修改复杂度结论。这里要求规格闭合，不要求本轮写程序或运行状态枚举。

#### B02：闭包与 PREPARE、最终复核之间缺少完整的阶段输入输出合同

**候选依据：** [L248](/home/lyh/MAPF_PIED_MDDR_RESEARCH/69_PIE_DTRS_KNOWLEDGE_CERTIFIED_PROPOSAL_PRESERVING_TRANSACTIONAL_REFINEMENT_PREEXPERIMENT_CANDIDATE_20260905.md:248)，L248-L261、L303-L331、L427、L431-L435、L499-L501。

**精确缺口：** Seed 包含缺少准备令牌的 MOVE，而状态表在 PROPOSE 就计算最终批次候选，随后 PREPARE 才获取令牌。可以设计一致的多阶段流程，但正文未确定哪次 Seed 使用哪一版令牌、何时固定知识/版本、何时因准备失败重启闭包。L323 要最终独立复核，却没有规定失败后是新种子、分量包含还是整个批次中止。L327 的最小性成立需要固定且完备的强制依赖语义；不能把“由未定义 CERT 发现的关系”直接等同于所有必须传播的资源影响。

**可执行修复：** 给出静态可行性、令牌获取、最终闭包、复核和 append 的有序规格；区分未申请、已拒绝、失效令牌。定义所有 SAFE_HOLD/CONTAIN 变化如何形成依赖，并给复核失败一个唯一结果。明确已入 X 的索引不再入工作队列，说明若依赖会新增，如何保证终止及覆盖。

**客观闭合证据：** 完整决策函数对缺令牌、版本变化、诱导 WAIT 失效和最终复核失败均有确定输出；最小性仅对已定义的强制关系证明，局部性证明能覆盖同一失败路径。对循环依赖不得靠重复入队；对竞争资源不得把一般“冲突”未经定义地当作单向释放依赖。不要求最大移动集，也不把可能的保守抑制误说成违反最大性。

#### B03：纯仿真执行语义与“完整状态机”仍需落到可检查的守卫

**候选依据：** [L136](/home/lyh/MAPF_PIED_MDDR_RESEARCH/69_PIE_DTRS_KNOWLEDGE_CERTIFIED_PROPOSAL_PRESERVING_TRANSACTIONAL_REFINEMENT_PREEXPERIMENT_CANDIDATE_20260905.md:136)，L136-L152、L234-L267、L271-L287、L335-L359、L385-L387、L494-L508、L734-L738。

**精确缺口：** 稿件允许基线联动、事务加 interlock、纯离散原子联合迁移三条路径，但没有给本次证据协议固定一种形式环境，或给出足以机械区分三者的完整语义配置。原子离散分支如何表达独立不启动、部分交付和中途边上故障不能靠同一个“仿真”标签解决。状态表给出 RECOVER 的多个出口，但缺各出口的判定和保留资源集合；ABORT 行的“pre-start”还需与 COMMIT 行的“不允许 postcommit abort”组合成显式守卫。

**可执行修复：** 声明适用的执行语义配置或完整的参数化语义族，为动作阶段、调度、联动、物理许可点、故障转移写出守卫与资源不变量。定义 COMMIT 后尚未启动、ACK 丢失、重启和边上未清空时的恢复决策。明确 COMPLETE 可清除哪些旧资源，目的点持有权仍按 L150 保留。给22个未来见证绑定语义分支与预期不变量，而非立刻生成载荷。

**客观闭合证据：** 每条允许迁移都可从其前置守卫推导资源不变量；在所选语义中不可发生的见证标为不适用，不能拿不支持的故障来证伪该分支。L267、L341 已要求无联动证明则抑制，本路认可这一回退，不要求真实机器人实现 interlock 才能闭合纯仿真；要求的是把假设写到可判真，而非证明硬件可靠。

#### B04：inactive 身份定理、激活切换与主动取证尚未合成一个确定方法

**候选依据：** [L401](/home/lyh/MAPF_PIED_MDDR_RESEARCH/69_PIE_DTRS_KNOWLEDGE_CERTIFIED_PROPOSAL_PRESERVING_TRANSACTIONAL_REFINEMENT_PREEXPERIMENT_CANDIDATE_20260905.md:401)，L347-L361、L401-L409、L413-L427、L441-L452、L628-L643。

**精确缺口：** 外部 activation predicate 未定义；何时进入/退出 active、如何建立知识初始不变量及处理尚未结束事务，也未定。69-B 在相同逻辑调度等前提下是合理的字节恒等陈述，但不能单独证明误反馈发生时的 inactive 决策安全。另一方面，witness-directed repair 只限定可以问谁，没有确定多见证下问哪些、顺序和预算耗尽时如何决策，因此 full 方法尚非唯一可重放的策略。

**可执行修复：** 定义激活可观察输入、切换守卫和不变量交接；明确安全声明覆盖 active 决策、何种 inactive 基线域以及未闭合事务。保留冻结 PIE-D，不通过悄加保护动作来宣称其原样恒等。固定查询选择、稳定排序和额度耗尽规则，全部可写成对冻结配置的符号函数，无需给 P_active 或预算符号赋值。

**客观闭合证据：** 在给定同一合法输入和冻结配置时，激活、查询集合和输出唯一；进入 active 可建立 69-K/69-S 前提；退出 active 不遗忘既有资源义务。字节恒等与条件安全分别列出适用域和检查流。此项是组合域缺口，本路没有假定所有证书前提成立后再虚构一次不安全 inactive 行为。


### Assessment against Nature-style criteria

| 评价轴 | 判断 |
|---|---|
| originality | 五项结合可保留为来源受限候选，不能确认为新。 |
| scientific importance | 防止错误证据释放资源有工科价值，更广意义待证。 |
| interdisciplinary readership | 知识与事务的联系可理解，外推受模型限制。 |
| technical soundness | 条件证明骨架可用，B01-B04 阻止机械闭合。 |
| readability for nonspecialists | 入口清楚，术语后的语义尚不足以复算。 |

### Recommendation posture

支持继续文本与形式闭合，当前候选不能通过。69-I 的不可区分性和 69-B 的受限逻辑身份陈述不因其他缺口而一并作废。理由是定义不足，而不是尚未实现。

## Reviewer 2

评价重点：originality 与 scientific importance；与其余视角共享事实，不假装掌握额外文献。

### Overall assessment

五项结合可作为受限研究候选。L43、L56、L72 承认通用工具属于既有方法，且创新可能被原文证据否定；不应要求先达到 Nature 广泛影响标准才允许工科研究启动。效用论证则必须有公平比较，不能被不同因果历史或伪独立样本混淆。

### Who would be interested / Major strengths

终身 MAPF 与可靠执行研究者会关心局部保留及证据修复是否减少停等。L431-L452 给出可否定的机制，L628-L643 保留 PIE-D R0 和安全/被动对照，L670-L682 分开等计算和自然运行时；尚未把收益写成结果。

### Major concerns / Technical failings

#### B05：相同反馈 trace 尚未定义为对不同闭环历史公平的耦合

**候选依据：** [L609](/home/lyh/MAPF_PIED_MDDR_RESEARCH/69_PIE_DTRS_KNOWLEDGE_CERTIFIED_PROPOSAL_PRESERVING_TRANSACTIONAL_REFINEMENT_PREEXPERIMENT_CANDIDATE_20260905.md:609)，L618-L620、L637-L643、L666、L670-L682。

**最小说明：** 设某次分化后，基线执行原 MOVE(u,v)，候选经合法抑制保持在 u。下一条正确位置报告对基线应指向 v，对候选应指向 u。若 L640 的“相同 delayed/faulted report trace”指逐字节同一载荷，该条在至少一方不再是相同意义的正确观测。这只说明比较协议的歧义，不是对安全定理的反例；若“相同”本来指相同扰动机制，正文就应明确生成与耦合规则。

**可执行修复：** 区分固定提交边界的开环字节重放与各方法继续演化的闭环比较。闭环用相同外生随机创新和确定的故障注入函数，各自产生对应自身真值历史的报告；规定事件缺席、额外查询和重试的配对键。分别声明可信清空通道、普通错误反馈与独立裁判真值的可见性。对处理延迟定义逻辑事件调度和墙钟计费的映射。

**客观闭合证据：** 分化动作后仍能从冻结规则唯一推出各方报告的来源、真值关系和错误类别；裁判真值不能未经许可进入任一算法；额外查询同权同账。严格等计算与自然运行时的暴露量可对齐，吞吐变化不混入不同故障强度。仍保留 PIE-D 的原始比较地位；如另设共同安全适配层，须另标处理组，不能将其悄称原始 PIE-D。

#### B06：独立样本单位与配对比较、主结果汇总尚未一致

**候选依据：** [L649](/home/lyh/MAPF_PIED_MDDR_RESEARCH/69_PIE_DTRS_KNOWLEDGE_CERTIFIED_PROPOSAL_PRESERVING_TRANSACTIONAL_REFINEMENT_PREEXPERIMENT_CANDIDATE_20260905.md:649)，L409、L637-L643、L647-L662、L686-L711。

**精确缺口：** L649 把包含 method 的整次运行称为独立单位，同时各方法复用地图、任务、初态和随机扰动。不同方法在同一外生元组上的结果一般是配对观测，不应仅因 method 不同即计作独立重复。稿件正确排除了把 agents/ticks 当独立样本，却尚未定义跨方法的配对块。效用结局列出多个指标，也没有固定主比较、汇总量及“假设反转”的判定函数。

**可执行修复：** 将不含 method 的外生元组定义为配对块，明确哪些块可作为独立重复；冻结配对效应或描述性汇总函数，区分安全违例的逻辑否证与效用假设的统计/描述性否证。为失败、删失、零 admitted MOVE 等情况规定指标是否定义及展示方式。

**客观闭合证据：** 任一符号化运行登记表能唯一推出配对、分母、汇总和结论规则；增列一种 method 不会凭空增加独立外生样本数。若研究只做描述性分析，明确不作显著性推断并冻结描述函数，同样可以闭合；不强制功效估计，不为受保护符号给值，也不要求本轮真实样本。


### Assessment against Nature-style criteria

| 评价轴 | 判断 |
|---|---|
| originality | 组合候选仍 OPEN；POD 等全文排除未由本路核验。 |
| scientific importance | 可能有执行可靠性价值，收益及适用域待实验。 |
| interdisciplinary readership | 知识与授权边界可能可迁移，未证实广泛意义。 |
| technical soundness | B05-B06 影响比较有效性，B01-B04 同样成立。 |
| readability for nonspecialists | 应清楚区分减少停等的机制与额外安全前提。 |

### Recommendation posture

保留创新路线，先关闭公平性和汇总规则缺口。创新 OPEN 是来源限制，不作为独立 bearing 加票；也不能以合理直觉代替比较证据。

## Reviewer 3

评价重点：interdisciplinary readership 与 readability for nonspecialists。

### Overall assessment

白话问题可理解，但“已冻结契约”和“以后决定规则”混在一起。资格卡称协议完整，正文仍有未来承诺；这影响复核，超出纯行文问题。

### Who would be interested / Major strengths

机器人执行、异步系统与资源协调读者能理解为什么错误反馈会阻止原动作提交。L37-L44、L734-L738 的模型边界清楚；L653 保留失败分母，L730 将破坏安全前提的消融标成负控，均应保留。

### Major concerns / Technical failings

#### B07：公开数据门仍只有来源类别和清单要求，缺少确定的选择规则

**候选依据：** [L609](/home/lyh/MAPF_PIED_MDDR_RESEARCH/69_PIE_DTRS_KNOWLEDGE_CERTIFIED_PROPOSAL_PRESERVING_TRANSACTIONAL_REFINEMENT_PREEXPERIMENT_CANDIDATE_20260905.md:609)，L609-L622、L748。

**精确缺口：** 固定 PIE-D 提交可以定位数据树，但“city 和 warehouse 等来源类别”不是候选所承诺的确定 manifest 规则。L609 说文件将按确定规则选择，正文却没有该规则。两位执行者可在同一提交内挑选不同合法地图、起点和任务，均符合当前表述，却形成不同研究对象。这不是要求马上选定 density N，也不是因为尚未生成载荷而拒绝候选。

**可执行修复：** 固定可允许的数据路径/元数据条件、稳定排序、关联文件匹配、排除理由和缺项处理，写出从冻结树及未来获授权配置到 manifest 的唯一函数。把数据选择与结果隔离，禁止看过比较结果再替换数据。可以保留未实例化的符号配置，但不能把函数主体留到以后自由决定。

**客观闭合证据：** 同一树对象和同一已获授权配置只产生一份清单；每个条目可回溯 map/start/task/delay blob，排除项有预先规定的原因。当前阶段交付完整的选择规格即可，不要求本路下载数据、遍历基准、决定密度或产生新 trace。

#### B08：参数保持未赋值时，停止、暴露与运行协议仍未成为确定的参数化合同

**候选依据：** [L657](/home/lyh/MAPF_PIED_MDDR_RESEARCH/69_PIE_DTRS_KNOWLEDGE_CERTIFIED_PROPOSAL_PRESERVING_TRANSACTIONAL_REFINEMENT_PREEXPERIMENT_CANDIDATE_20260905.md:657)，L537、L655-L662、L670-L684、L695-L713、L749、L753-L763。

**精确缺口：** “method-independent symbolic stopping contract”是要求名称，不是已经给出的停止谓词；“declared run exposure”未定义，基础设施重试、科学失败分类及 roster 冻结规则也未完整展开。不同执行者可以在任务数、逻辑时长或实际墙钟等不同暴露定义下作出不同结论，同时满足这些概括句。符号未赋值本身合理，缺少规则主体才使 PROTOCOL-COMPLETE 过强。

**可执行修复：** 给出 Stop、Exposure、Classify、Retry 和 Roster 的确定函数/决策表，声明观察字段、事件顺序、缺失日志和终止原因优先级。列出未来授权绑定配置所需字段及禁止读取比较结果的冻结程序；任何字段未按程序绑定时仍 HOLD。对假设违例、安全违例、资源耗尽、死锁与恢复不终止作可观察的分类，不能靠有限等待证明“永不终止”。

**客观闭合证据：** 对任意合法运行前缀及同一冻结配置，停止、删失、分母与暴露量唯一；协议能在不填写 H、T_delay、B_CAL、B_max、B*、P_active、density N 的本轮文本中完整描述。理论无限阻塞与有限观测中的删失被区分。先闭合函数再在获授权阶段绑定参数，不等同于现在调参或启动实验。


### Assessment against Nature-style criteria

| 评价轴 | 判断 |
|---|---|
| originality | 组合目标可理解，不能从术语数量推断新意。 |
| scientific importance | 问题有工科意义，无需提前声称重大广泛影响。 |
| interdisciplinary readership | “哪些证据可信、何时还能动”有清楚解释。 |
| technical soundness | B07-B08 阻止协议可复核，机械契约也须一致。 |
| readability for nonspecialists | COMPLETE 标签领先于定义，易误导读者。 |

### Recommendation posture

保留问题和边界，先把未来冻结的承诺写成可检查的参数化规格。无需补实物实验或出版级排版，但当前不能以完整协议身份通过。

## Cross-review synthesis

### Consensus strengths / Consensus technical risks

三视角共同认可：启动失败仍是 delay；认证不等于物理真值；不产生新 MOVE；错误 COMPLETE 不足以释放资源；无法安全 WAIT 时应保持既有义务；原子提交不自动保证联动安全；仿真不自动验证现实定位、制动、扫掠体与 fence。

本报告没有发现并声称一个满足全部定理前提的碰撞反例。B05 是关于比较语义的条件性最小说明，其余以精确缺口立项。不能拿去掉安全前提的负控反驳带有该前提的定理。

| ID | 独立 bearing | 阻断对象 |
|---|---|---|
| B01 | 知识域、关联、CERT 与成本模型 | 可计算、可证明 |
| B02 | 令牌、闭包及最终复核的阶段组合 | 总决策、最小性、局部性 |
| B03 | 仿真语义与事务守卫 | 安全机械合同 |
| B04 | 激活、身份域和查询策略 | 方法确定性与组合 |
| B05 | 分化历史中的故障和信息耦合 | 公平比较 |
| B06 | 配对单位、汇总和效用否证 | 分母与推断 |
| B07 | 数据 manifest 选择函数 | 数据可复核性 |
| B08 | 停止、暴露及冻结合同 | 预注册确定性 |

八项均未闭合。重复关注只登记一次，不把三个视角当三票，不覆盖或继承第一路结论。

### 六门独立裁决

按候选 L742-L749 顺序、采用实验前标准。PASS-BOUNDED 仅说明表列文档义务满足，不代表外部真伪已核验、程序已运行、形式方法全部通过或允许执行。

| 门 | 本路裁决 | 独立依据和边界 |
|---|---|---|
| G1 白话问题契约 | PASS-BOUNDED | L27-L43、L94-L105 已说明处理期间的不确定性与错误反馈，范围不含连续定位/制动正确性。不继承 PASS-INHERITED。 |
| G2 已发表锚点 | PASS-BOUNDED | L60-L72、L541-L545、L579-L590 提供可定位锚点，满足候选定位层；全文归属与创新排除未核验，novelty OPEN。 |
| G3 PIE 官方 R0 | PASS-BOUNDED | L541-L575 提供标称官方链接、完整提交、版本、许可标识、入口、扩展位置和最小审计计划。通过的是实验前审计包结构，未构建不构成失败。 |
| G4 外部已发表基线 | PASS-BOUNDED | L579-L605 有论文、标称官方仓库、固定提交、许可、样例、入口和最小复现计划。公平适配仍受 B05 约束。 |
| G5 公开数据/场景 | OPEN | L609-L622 缺确定选择函数，B07 未闭合；固定仓库不等于唯一数据清单合同。 |
| G6 纯仿真证据链 | OPEN | 已有 oracle、分母、计算轨道和否证框架；B03、B05、B06、B08 使语义和协议仍非唯一，L749 的 PROTOCOL-COMPLETE 不成立。 |

四项有限文档通过、两项 OPEN 不是多数通过制。B01-B04 等实质缺口仍阻止候选整体通过。如果某门另要求外部原文或仓库真伪核验，本路对此额外层为 NOT ASSESSABLE，不能借文档 PASS 冒充完成。

### Where emphasis differs / Broad-interest and significance

Reviewer 1 重可判定原语及不变量，Reviewer 2 重比较结论有效性，Reviewer 3 重确定规格与可复核性。不同权重不改变事实底座。

本稿研究实际错误的反馈载荷及其与处理延迟的组合，没有解决物理轨迹偏差。L734-L738 已合理允许纯仿真研究受限资源模型；B03 要求明确可判真的仿真前提，不要求验证真实硬件。状态机已禁止超时释放、把丢 ACK 重放当 exactly-once、把 mid-edge 当原地 WAIT；不能抹去这些已有保护。L472 承认无限阻塞，69-P 只在 L478-L484 的强条件下评价，不外推至永久分区。

创新仍受来源约束：既不能确认五项结合已排除所有相关方法，也不能断言它只是重命名。POD 全文排除 OPEN，触发 L72 路线否定规则需要对应原文证据。合理工科研究启动不以 Nature 的重大广泛影响为先决门槛；本路未通过理由是技术及协议缺口。

### Most important issues to resolve

先明确 B01-B04 的方法与执行合同，再使 B05-B06 的比较与汇总一致，最后闭合 B07-B08 的参数化登记函数。这个顺序是文本依赖，不授权实现或实验。每项客观闭合条件已在对应 bearing 中给出，可先通过形式定义、静态契约和推导满足。

参数保持未赋值与预注册规则确定可以同时成立；当前缺的是函数主体，而非本路应替用户填数。任何修复遵守 L774 的新编号、新字节后继规则；不修改本候选，不更新根裁决。

## Risk / unsupported claims

- 外部 DOI、提交、许可及论文归属仅据候选；G2-G4 不是外部源核验或官方代码审计完成。
- 没有已证实吞吐、延迟、查询节省或硬件效果；缺少这些结果不单独阻止实验前闭合。
- 69-I 不可区分性依赖相同消息且无独立 interlock 的前提；69-B 仅为声明逻辑域的身份；69-C/69-S 仍需 B01-B03 所要求的可操作原语和守卫。
- 保留 PIE-D R0。共同安全适配、额外查询或更强真值接口必须另标，不能把增强方法冒称冻结基线。
- 可读性可用“普通报告/可信清空/独立裁判”边界表改善；此建议不另计 bearing，不施加发表级排版门槛。
- 唯一候选及必需技能资料已完整读取，指纹匹配，身份有效；未读禁止材料、未派子代理、未执行实验或修改 release。
- 审查工作完成不等于候选通过；本报告不作 Nature 编辑决定，不用投票覆盖第一路。

最终裁定：REVIEW COMPLETE / IDENTITY VALID / CANDIDATE NOT PASSED / 8 OPEN BEARINGS。

HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。
