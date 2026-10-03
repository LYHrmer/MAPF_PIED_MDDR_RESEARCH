# Astra R12 独立只读源码审查

阶段一记录：2026-10-04 00:36 Asia/Shanghai。审查者为实际 GPT-6-Astra/ultra 工作代理。只读核对原生选择/宏执行、合同和 runner 参数渲染；仅写本摘要，没有修改实现源码、运行原生程序或读取尚未产生的实验结果。拟合与校准实现尚未提供，本阶段不能替代其后续审查或整轮实验审计。

## 发现与处理

**一项恢复绑定缺口已由实现者修复。** 初读 `runner.py` 的既有 receipt 分支只比较 native 源码 SHA。相同源码下若模型、margin、二进制或容量改变，恢复运行可能静默复用旧部署。该问题是源码中的条件性风险，不是已观察到的错误实验。已直接发送实现者和根；重读 [runner.py:69](runner.py#L69) 确认当前分支同时核对 expected `render(w,models)` 全文和 SHA、world/policy/capacity、native ELF/bridge/config，以及现存 raw/planner/input 的 SHA。失败 receipt 仍保留，没有为此追加原生运行。

**计时口径须保留限制。** [macro_choose.inc:17](macro_choose.inc#L17) 的计时在候选特征和 gate 均值构造之后开始，结束于选定宏。`inference_ns` 因此覆盖此段选择器评分/选择工作，不是完整特征提取、全部策略运行或生产计费；非学习臂记录0也不是其实际运行没有成本。这不改变物理模拟时间或宏语义。

除此之外，本次范围未发现需要阻止冻结的原生策略语义错误。该判断不覆盖尚未核对的拟合、校准、模型数值及真实运行结果。

## 已核对的对应关系

1. [joint_history_native.cpp:145](joint_history_native.cpp#L145) 仅在 `macro_name.empty()` 时形成25维gate并选择宏；赋值后不会因新END或新候选重新选模。公共非空候选由原World3形成；首次选择前没有QUERY，初始容量确认为8或16。选择后在同一调用继续执行early动作，没有漏掉首机会或同点再次选择。
2. gate为原24特征的精确有理数逐槽均值，再加候选数/16。`macro_choice` 保留原gate、六宏任务/时间/总分、共同margin、所选宏与调用次数。固定C、固定W、显式宏、TRAIN预算查表和学习器最终都进入同一宏解释器。
3. [joint_history_native.cpp:163](joint_history_native.cpp#L163) 将 tasks_only 参数名映射到full；只跳过time头，保留同一个任务系数及 `shared_margin`。full/nohistory/nobudget将两个头相加。C分数严格为0，非C必须严格超过margin；相同非C分数按固定K6先后顺序保留，+infinity退回C。模型时间头应已按1/16385缩放，这一点仍须在fit代码核对。
4. 掩码在原生求和时明确执行：nohistory为10..17，nobudget为20/22/23，time槽21保留。原先feature0与19是无历史prior及其交互，未误认成历史输入。现代码未把身份/seed/map名放入gate。拟合端还须核对相同掩码、TRAIN标准化及零系数，不能仅因原生有掩码就判定训练端通过。
5. [joint_history_native.cpp:188](joint_history_native.cpp#L188) 的宏状态机默认W不查询、其他宏采用condition续策。early立即触发；late要求剩余预算正且已用不少于初始容量的一半。double的second判定在首次动作修改stage之前计算，所以不会在同一公共调用执行两个SKIP。第二次只排除原完整(agent,occurrence)，没有错误地排除同agent后继。
6. SKIP目标按真实公开condition分数、agent、完整action ID排序，包括0分候选。实际强制分发沿用单agent一个未结束MOVE的不变量；完整身份用于锚点、遮蔽及正常END解除。不存在第二触发时继续condition，不制造WAIT或另找后见目标。QUERY收费与SKIP生命周期仍由原World3实现。
7. `runner.render` 将每个参数系数经Fraction输出为独立M记录的整数分子/分母；native读取后用exact rational评分。固定宏训练枝无需模型参数；学习TEST需相应变体、full任务头及共同margin参数。TRAIN/CAL/TEST分割、参数格式来源和冻结时点尚待pipeline核对。

## 未改物理层的静态核对

读取两个实际文件后作字节比较：R12从 `struct Move3` 起至 `int main` 前的整个Move3/World3块与冻结R11相同；`macro_choose.inc` 与R12 CPP内联的choose文本完全相同。choose之前的变更只有chrono头、宏名与初始容量状态替换旧单次干预标记。main只更换接受的策略名。这支持“本次改变选择与宏调度，没有改World3物理、owner、公共候选或正常END”的源码范围判断，不等于新模型部署已通过事件/物理审计。

## 本阶段读到的文件绑定

|文件|SHA256|
|---|---|
|joint_history_native.cpp|244fab29a8b36cbfae64c65673f2ebc94d36e1eb0e6a021bdf36c97409646ba7|
|macro_choose.inc|2f4142aa41e866d96b3de7f61e314a03aec92801580d81e6591732de711a4cef|
|CONTRACT.md|b98a6977f5b622ebe62d0064f90f1f5b879a092a6ac90b2e3ed73ed255b5770e|
|runner.py（复用绑定修复后）|3030c40802c3057b6e098b0aa07a77108e057a51269948106de299ed81879c6a|

原runner的SHA为 `0cbe3b1c698d20c2888136c145c0db96450b7477981d3687d303f5e8fa99ff68`，仅用于标识本次发现的先前版本。最终冻结若再修改任一实现文件，需要按实际diff补审，不能把本阶段哈希直接当作最终版本。

阶段一待补事项已在下述第二阶段只读核对；阶段一的哈希和发现记录保留，不改写成当时已审查后续实现。

## 阶段二：标签、拟合、校准与冻结

完成时间：2026-10-04 00:48 Asia/Shanghai。已读实际 `learn.py`、`pipeline.py`、修订后的 `prefix_audit.py`、runner及两份协议。未调用这些执行入口、训练模型或运行native；以下是源码符合性审查，不是尚未产生的拟合/部署结果PASS。

**两个前置/边界缺口在科学运行前补齐。** 初读learn只比较六宏gate均值，不能以此代替完整共同状态前缀；全部TRAIN均无gate时，`assert rs`也缺少已声明无机会边界的处理。提出时首次REGISTRATION刚形成，TC尚未开始。根明确批准在零科学运行下保留ATTEMPT01，增加完整前缀fit前置和零头回退，再建立正式注册；未变宏、数据、原生物理源码、152次预算或实验范围。`PRE_SCIENCE_REGISTRATION_REVISION.json`记录此过程。不是在看到TRAIN/CAL收益后修改方法。

当前 `learn.main` 在标签生成与拟合之前调用 `prefix_audit.main`。后者核每条raw的SHA，比较同一world/B六宏首个macro_choice之前的全部物理/公共记录，以及gate时刻、机会号、初始预算和全部特征；跨预算再核去除预算元数据后的前缀及非预算特征。仅剔除policy标识、无gate最终summary的native_checks，以及跨预算的capacity字段，不删除物理事件或任务服务。无首机会时比较完整轨迹并保留其结果。PREFIX_BEFORE_FIT的SHA进入模型工件。同gate均值不再是唯一前置核验。

若某TRAIN family无gate，完整六宏结果仍在标签、CAL/查表和后续统计中，拟合只排除没有可用决策输入的行。若所有TRAIN均无gate，预先规定每头26个零系数、零均值/单位scale、train_rows=0及空bindings，选择回退C；没有伪造训练观测。实际是否触发和有效训练family数量仍须在结果报告中明确，不能将零头回退称为成功学到了策略。

### 数学和数据范围核对

- `outcome/labels`从完整服务记录计算全FIFO已服务数，并只对每机器人固定前四项任务累加T区间，缺失记128。每宏任务目标为served_macro−served_C；时间目标为两个T区间中点之差(T_C−T_macro)/16385，正号一致。T差上下界另外保留，未用较好的预测或query次数充当服务标签。C本身两个目标为0；CAL行虽随标签保存，但不会进入拟合矩阵。
- 每个非C宏、每个full/nohistory/nobudget变体分别取split=train的有gate行，两预算每行权重1/2。标准化先按掩码置零，再用TRAIN加权均值和方差；极小/常量scale设1。求解式为(XᵀWX+diag(0,1,…,1))β=XᵀWy，截距未惩罚，λ固定1。任务与时间头共享该变体/宏的X、权重和标准化，各自拟合目标。
- 原始坐标系斜率β_j/scale_j、截距β_0−mean·slope的还原与实现一致，并有预测相等断言。原始系数量化到9位小数，经Fraction保存；masked斜率、均值和scale有显式断言。Python离线分数与native使用相同原始输入坐标、相同mask和同一量化参数。tasks_only读取full任务头，既不重新拟合也不另行校准。
- `robust_best`先保留最高总任务数，再剔除其T下界严格大于其他候选T上界者，最后按query数和固定tie排序。这是先算整个未被严格支配集合，再选择，不依赖逐对比较顺序。CAL用full和固定六个margin在四个CAL预算世界的完整宏结果查表；同任务/区间未区分/query数相同则较大margin优先。TRAIN预算查表分别聚合B8、B16的六个TRAIN family，以同样规则和固定K6顺序选择，不读取CAL或TEST结果。
- 模型artifact明确保存三变体共30个头、标准化、未量化与量化系数、每行family/预算/option/权重绑定、共同margin和两项TRAIN查表。无场景身份字段进入设计矩阵。六个TRAIN family、两个CAL family和四个TEST family仍分别计数；B8/B16不算独立family。

### 注册、时点与运行边界核对

`pipeline.frozen_check`在TC和TEST入口检查登记源码、native ELF、作者bridge与config；正式登记包括prefix_audit。TC只生成96个固定宏任务；TEST只生成56个固定七策略任务。测试入口核模型冻结receipt的artifact SHA，再以该artifact中的参数启动native。runner每条记录绑定registration、阶段开始receipt、源码冻结时间、模型artifact及freeze receipt；运行时间必须晚于对应冻结时间。既有receipt恢复还核当前输入及参数全文、world/policy/容量和实际文件SHA。

`learn.main`在拟合前拒绝已有TEST receipt，记录TC receipt SHA、最后完成时间和FIT_START；正式模型冻结receipt记录模型/标签SHA及当时TEST receipt为0。源码里没有按CAL另训消融或在TEST后调margin的通道。最终独立审计仍必须用实际receipt核冻结时序、来源和部署行为，不能仅靠这些声明字段判通过。

本次读到的正式注册时间为1791046018336180121 ns，TC_START为1791046040800626270 ns；顺序正确。读到时TC已由实现者开始，但完成receipt为0，FIT_START、模型冻结和TEST_START均不存在。本审查未查看本轮收益后作选择。

|阶段二实际文件|SHA256|
|---|---|
|learn.py|a51943ae42502c865199c31ca8404140a4f634f5d4f9ba6b1f64428b4eaf075e|
|pipeline.py|8200c9e5c2bdbaf33d05c247dbec55bd75ac23ed79f26444b11dde0aa09faceb|
|prefix_audit.py|755197d2d207fc8370248dbbdb70fca987a2912cc829be080df192606ec38e5c|
|runner.py|9e04a5164babef33fa13be015ae514ca64cc219476cfc7aff54672c27ffc6a93|
|ROOT_PROTOCOL.md|6c8bde98fa547436d6f32475ab3b9aca7405876018548b5266bd0eabc33a32f5|
|CONTRACT.md|fdca9cca32d471bc151fe0a093be4416e1929267dd32141a956990b146120887|
|正式REGISTRATION.json|6e7c1c018e7f732d753ba4c44b6366b4016539e49e9a59fbfce2d8d16eb350dd|
|REGISTRATION_ATTEMPT01.json|048ed9e1e912ffcae11bad8cd1692a1c21545c352fcb8d31577527a04d95c6ad|
|PRE_SCIENCE_REGISTRATION_REVISION.json|19004c40470e75049e0611d88972a2fa1376c709d194899dccda0203dcad0be8|

此时正式注册的全部12个frozen文件SHA与磁盘一致；native CPP及macro片段仍为阶段一所列哈希。两阶段只读范围内，所发现的恢复绑定、完整前缀和空TRAIN gate边界问题均已关闭，未发现剩余的公式、mask或宏续策语义阻断。学习效果、实际拟合数值、完整原生部署、负控及所有时点事实仍待本轮数据和独立审计完成后判断。
