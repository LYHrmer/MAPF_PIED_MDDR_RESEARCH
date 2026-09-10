# 73C9：群组退栏、控制尝试与模式的有界独立建设

你是独立建设顾问，本题不是正式审稿、盲审或资格投票。NO-SKILL：不加载任何skill，不使用工具、文件、网络或外部记忆中的项目报告；只依赖下列亲核原文。不要编写代码/伪代码、实验、配置或载荷，不给保护参数任何值/范围/默认值。保持HOLD。本题不要求评估源后端或文献新颖性。

被核输入：73_PIE_SPATIAL_EVIDENCE_TERMINAL_HANDOFF_AND_PAID_SERVICE_PREEXPERIMENT_DRAFT_20260908.md；SHA256 0beccea730aced26203406f8ffa69f5ffa93247f80cec64f00ec9de265065965，155562 bytes / 531 LF，DRAFT/NOT-FIXED/NOT-REVIEWED。下文是该整合稿的必要原文摘录；省略的几何证明前提暂按成立，不把省略当正文没有。摘要背景：唯一中心管理owner与组围栏，各agent低层执行同一原MOVE的累计cap；q只由付费可信证据增长，中心b先保留资源，本地C后安装。闭合END不可逆且需付费中心FINISHED、READY和本地消费才接下一原MOVE。每项检查/计算/消息/拒绝均付费，共同有限机会O不因私有进度补行。

## 亲核原文：组生命周期

“组准入围栏与物理owner分别记录，agent的组成员关系保持至付费退栏，不能仅因旧tid FINISHED便消失。”

“F_G是有未来排他能力的准入围栏，不是第二物理owner或清空证书。它禁止非本组登记责任新增占用F_G；当前无物理owner的围栏资源也不能对外称完全FREE。检查A/B、PRECHECK保持条件、组版本及全部记录/消息槽容量后，一次中心提交设栏，给每成员唯一原tid登记c_i/l_i/B_i及初始b_i=c_i，把A_i从合法parent改tag给该tid，转GRANTED并持久保存各累计grant；未完整完成则无部分预留/半组围栏。”

“组员真正END后的同agent gamma_prime允许接续旧组责任；FINISHED、READY及消费不释放F_G，也不允许该agent下一原MOVE绕过围栏。新增公共GROUP_RETIRE角色在Srv_C付费扫描组，按组建立行/规范key选择首个满足全部成员中心FINISHED、终点resident合法接续、旧cap/RUN受永久关闭守卫约束者，提交退栏并解除组成员的新MOVE限制；没有则收费空结果。GROUP_RETIRE与GROUP_ADMIT为两个独立token角色，不能同一token退栏后再准入，不由真值或FINISHED私下追加公共容量。退栏不删任何endpoint owner；组/消息历史GC仍等全部引用结束另付费。中心fail-stop、永久no-start/失联/未闭tid不因超时撤栏，长期围栏及外部等待是必须保留的负结果。”

## 亲核原文：累计cap和控制

“同tid后续包只在GRANT_ARMED/MOVE_LIVE接受且b_packet≥C，低于C拒绝、同值幂等。封存与真实接纳间再核当前phase/原END/关闭水位/身份，包不能改s/v_ref/z/c或原目标；本地不需知道最新中心b，只需合法签发的不可撤销lineage。”

“cap与RUN/STOP是独立权限；初始中心control_epoch含明确RUN_ALLOWED意图，MODE BRAKE的付费控制提交推进代际为STOP_LATCHED，MODE RESUME推进为RUN_ALLOWED。每次CONTROL_RETRY按中心已知tid/代际产生绑定该公开行的一次尝试，不读取本地C/s/模式。Srv_E付费验证后，实际ACTUATOR按原tid/slot/parent、当前phase、制动域和已安装cap处理。新RUN在起点或中点HOLD且C>s、no-start未阻止时才START/RESUME；运行中无作用，C=s无作用，缺grant拒绝；BRAKE已开始必须先到零速，此次RUN不留下自动启动钩子。后继需另一个明确新尝试。”

“本地保持最大已验证control_epoch和已处理控制尝试key水位；低代际不覆盖高代际，同代际矛盾模式拒绝。认证通过的新尝试在实际处理点登记水位，成功、no-start、缺grant、C=s、运行中无作用或phase拒绝均消费该尝试，副本及更旧尝试不得以后生效；未认证包不推进水位。乱序丢包靠共同后继累计cap重传与新RUN恢复，不延长旧无作用RUN的寿命；整数位长、持久化、拒绝均收费，无序号回绕或无限免费位图。”

“MODE产生的首次控制命令同样绑定其公开MODE行并进入上述控制尝试水位，不额外派生CONTROL_RETRY机会。本平台不向中心发送cap安装/到达/START结果ACK，审计器日志不可供中心策略读取。”

## 亲核原文：公共角色和模式

“每agent的既有SOURCE_REQUEST公开出现次序从零编号n_i，用n_i modulo 3固定为SOURCE_OR_EXTEND、RESEND_CAP、CONTROL_RETRY；空结果/丢包/私有进度不改变相位。”

“SOURCE_OR_EXTEND只按中心已知Kc、模式/parent/d_i/唯一请求/组成员关系与不可变Π取一个总分支：中心未就绪或失效则限定空/失败；当前GRANTED且b<ell尝试一次最大合法扩展，b=ell则NO_EXTENSION；当前UNGRANTED只重试同绑定普通整边及所需PRECHECK链，不同时组准入；无未闭请求但仍是未退组成员则GROUP_HELD；否则Kc未知、Kc=L或对应WAIT分别给NO_SOURCE_INPUT/NO_REMAINING_SLOT/NO_MOVE_REQUEST，只有Kc<L且原槽MOVE才生成一个原请求。”

“共享ACTIVE允许本臂新POSITION策略及符合条件的新组/原occurrence。SHARED-OFF停止新途中POSITION，保留已在途证据处理、已有责任的cap扩展/重传/RUN及原终点交接；DRAIN再停止新规划承诺、新组与新原occurrence，未授请求可CANCEL，已授不可撤销。DRAIN不要求停掉为完成已授MOVE必需的合法cap维护，但新POSITION仍停，故未清组可能无法排空；不能假定必达DRAINED。MODE BRAKE/RESUME改变独立控制代际，已开始BRAKE优先规则不变。”

“MODE的有限kind为QUERY_ON、QUERY_OFF、DRAIN、BRAKE、RESUME。前三者scope为本臂，按§7更新模式而不删责任；后两者scope为指定agent，中心付费提交推进control_epoch和对应意图，并产生绑定该MODE公开行的首次控制尝试，经后继付费验证/ACTUATOR才作用；之后CONTROL_RETRY重发当前意图但使用新的公开尝试key。所有两种来源的控制尝试进入同一本地水位，不能因MODE身份省去幂等或制动守卫。BRAKE在P1制动域内继续旧tid，无在途对象则NO_MATCH；RESUME只有旧tid未终结、合法参考HOLD且C>s时可重入LAUNCH。”

## 亲核原文：writer与发布

“每个可变应用状态有指定writer：中心管理owner/P/d/b、组围栏/成员/区间事件计数、控制意图/代际、查询last/轮询状态/臂模式/Kc/K_task/Π及规划接纳版本；各executor管理C/控制代际与尝试水位、自己的命令/c/READY消费状态”。“各应用writer至多一个计算或待发布槽，彼此不跨槽持锁等待。”

“应用作业完成后，在严格后继行的有限控制发布容量中执行已列明的版本/tag/幂等检查与准备好的增量；不足支付完整检查/发布则不产生效果、继续占槽。”

“ACTUATOR只执行已验证发布的命令”。“ACTUATOR实际接纳”允许输入为“已付费验证并发布的同tid命令及当前必要模式/幂等守卫”，服务站为“共同控制引擎的该agent容量”，费用责任为“只执行已有合法权限；控制/守卫/位长/物理引擎宿主成本完整记录”。

请独立只找一处最有分量的真实组合漏洞，给最小合法事件前缀、精确冲突条款及直接可改稿修复；若不足以确认漏洞，请给条件证明并标清需要补的最小定义，不凭省略猜源码或默认参数。重点是群组退栏/下一原MOVE与两种控制尝试来源、模式/代际/本地水位、writer和ACTUATOR顺序能否组成总接口。区分安全漏洞、合法停滞与定义歧义；不得把已有明确条件活性误读为无条件完成。请输出完整中文分析，约1500–2500汉字，结尾声明NO-SKILL/NONBALLOT/HOLD。
