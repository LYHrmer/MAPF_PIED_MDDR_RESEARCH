# 73Q2：PIE-D误差执行主线的具体实现绑定

2026-09-14，建设中，可更新。承接固定73与73R4，主线是误差包络、原MOVE前缀授权、可信进度和空间释放。这里补具体接口与代码包，不重开完整设计审查，不改变参数化模型、比较或主roster。ECBS包保持既有完成状态。

## 1. 纯几何核心：根接受的数域、数据和操作

geometry_binding已完整交付/tmp/mapf_geometry_binding_20260914.md（END_GEOMETRY_BINDING），根全文接收并逐项核对固定73 §3–6。下列为本次可实施合同；原报告不替根判断。根接受理由是有限凸片差集与直线的精确闭投影、单调参数缩放、闭区间并及同快照事件计数，均覆盖当前已声明输入域。

- 原MOVE的u/v可为有限实代数坐标，Delta=v−u、ell=sqrt(Delta·Delta)>0。F、Z、瓦片凸片按原域保持有理。若u/v代数，则归一化区间端点一般也代数；不能只用有理数或binary64实现完整核心。
- q、b保持物理距离，进入几何时分别精确换成q/ell、b/ell；q为dyadic不使q/ell必为有理。固定73旧“lambda_r=最后退出”是物理进度，本包归一化参数单独标明，不复用混义字段。
- 每个凸片的输入语义是有限有理生成点的闭凸包，允许EMPTY、点、线和二维片。外来polygon ring须由导入层核其原凸片或权威凸分解，不能直接凸化非凸边界。F与每个T_r按给定凸片取并，不填洞、不删共边，不要求不同片互斥。
- Z用有理闭盒上下界，允许零宽，拒绝倒置；模型外层仍核它与声明误差盒一致。总F非空；MOVE长度为零、进度越界、缺绑定、重复冲突资源key均为输入/绑定错误，不裁剪成合法数据。空相交与数值未知分开。
- 输入携完整数编码/坐标系/几何版本和原MOVE绑定，资源key采用确定全序。核心不认证目录覆盖了整个执行域、不认证障碍可通、不读取实际来源文件或q<=真s，这些由原外层合同负责。

对非空凸片对(j,k)，Q_rjk=T_rk+(−F_j)+(−Z)为有理紧凸集；原相交等价于u+lambda Delta属于Q。对Q的每条闭半空间A·x<=c，精确代入为beta lambda<=gamma。beta正/负分别给闭上/下界；beta为零时gamma负即EMPTY，否则不收紧。点和线用坐标或仿射等式的两向闭不等式及端点界表达。连同[0,1]得闭区间或单点；所有片对区间精确合并，相接端点归同一闭连通分支。

D_geo^lambda为0、1及全部合并区间端点的精确去重升序集，CAND再加入相邻端点中点。乘正ell保持顺序、端点和中点，故与原物理CAND逐项对应。零长度区间不删除，数值相等按精确值判断，不按地址、表达式字节或浮点容差。

### 1.1 独立N与G

N直接构造各凸片的当前扫掠凸包：两个参考端点u+(q/ell)Delta、u+(b/ell)Delta加F_j和Z的生成点，再与各T_rk作精确闭凸相交。实现可用精确凸包、极点包含和闭边相交；点/线/面分别处理，共线、相切和闭端点保留。N不读G区间/计数/缓存Mask来产出答案；可共享权威凸片与数值/凸包等通用原语。

G按(a,resource_key,h)、(d,resource_key,h)排序入口/出口。计数为
n_r(q,b)=#{h:a_h<=b/ell}−#{h:d_h<q/ell}。
因q<=b，被减项必已加入，n_r>=0且n_r>0等价于N的相交存在性。入口先处理新增部分再处理退休出口，可维持私有中间计数；外部仅见最终净集合差，不能将同点批次内部次序当作先FREE再占用。

G初态q=0，当前b合法；更新只接单调合法q'/b'。可允许纯函数同时变化两者以定义总函数，但中心实际退休与扩展仍遵守固定73的分开提交。F_cap/E0的退休模式关闭时q严格保持0，可不建/消费无用途出口索引。新MOVE独立初始化可变指针；真正不变的几何缓存复用仍付实际引用/复制费用。

### 1.2 私有结果和源级实现边界

核心只返回私有精确Mask、CAND或G后继快照与净增删。结果携原输入绑定、物理q/b及base快照身份；不自行读取/修改owner、围栏、P、权限、证书、公共机会或任务计数。中心再按原writer/版本/全部守卫一次提交相应完整状态。失败、过期或未完成没有部分几何发布；原已提交状态保持，已发生工作不退款。

本次代码可采用C++14泛型精确数接口：合法有限实代数值、准确零/一构造、加减乘除、非负平方根、三分比较、实数和有理性检查。除法前证明非零，未知/失败以明确异常或失败对象传播，不能返回零或EQ。数接口的具体候选为第2节FLINT；声明型编译检查不伪造数值实现，不把模板通过当库符合性通过。

所有容器计数/地址为所选有限类型并在可能溢出、窄化或扩大申请前检查。凸包删除、循环下标及候选长度必须源级有定义。输入对象在操作期间只读，修改集中于新值/私有快照；异常不改原快照。宿主bad_alloc/库abort不由本核心擅自映射成模型内普通失败，模型壳另按原合同区分表示耗尽与未取得证据。

### 1.3 组epsilon的外层接缝

POSITION拥有0<eps_w<=epsilon的有理见证，不自动使原epsilon属于实代数。GROUP中的l=max(0,c−epsilon)必须使用原epsilon：可由原profile提供代数epsilon，或提供对相关代数阈值的含等号精确比较。特别是ell*d>=l等价于epsilon>=c−ell*d。不能用较小eps_w替代epsilon改变原组选择。该接缝属于组适配，当前纯几何核心不实现组选择，不因它重开已接受的集合定义或缩小主roster。

## 2. POSITION数值候选：固定FLINT v3.3.1

astra_ultra_position_backend实际使用gpt-6-astra/ultra，已完整交付/tmp/mapf_position_backend_binding_20260914.md（END_POSITION_BACKEND_BINDING），根完整读取。根另直接读取固定commit的qqbar/root_ui.c、arb/get_interval_arf.c、arb/get_lbound_arf.c，工具fb107e/0662c0/c760cd，确认早退与有向舍入分支；web取得失败没有当作证据。

候选为[FLINT v3.3.1](https://github.com/flintlib/flint/releases/tag/v3.3.1)，完整commit 17950040404e6ed797a4becd8a866fb3f62b5c5e，含qqbar/Arb/Arf/fmpz/fmpq，源文件采用LGPL-3.0-or-later。官方tar.xz元数据为5,921,132 bytes、公布SHA256 5ee67f09ce810a0ab9f3a9de99945521b864e02064b09d6f178c60e743a8df62；此前代理只核可获取和tag指向；现根已实际下载源包、核得相同SHA256并解包到third_party/flint-3.3.1。MPFR-dev 4.1.0-3build3已下载并仅解包到third_party/host_sdk，包SHA256为ee3fc55ad08686f89a1839b5673e38c2dd269b0335bc80f8e881e4b641259116；系统GNU11.4、GMP-dev6.2.1复用。未全局安装、未构建或运行FLINT数值库。

qqbar_t承接合法实代数叶和表达式值；qqbar_add/sub/mul/div/sqr与精确比较承接已接受的各模式公式。HOLD使用已合法建立的值，APPROACH不在xi0=0求值；采样点采用已发生的同一冻结段。qqbar_set_d/guess不能认证真实状态，未验证的serialized struct也不能导入。数值相等或C地址相等不代原tid/sample/model身份。

### 2.1 认证外包链

给定同一合法冻结输入，先有s_true(sample)=s_alg；qqbar_get_arb给认证有限球B。arb_get_interval_arf以FLOOR/CEIL分别取得有限端点Lf/Uf，再用arf_get_fmpz_2exp编码各自准确的(m,e)，即m*2^e。分别保留指数，不强制统一指数造成额外巨大展开。

宽度成功关系采用向上界D_plus>=Uf−Lf；原精度有理见证经认证向下界得到0<eps_minus<=eps_w<=epsilon。只在有限、Lf<=Uf及D_plus<=eps_minus均已验证时签发，故真实宽度U−L<=epsilon。精度位数p本身不是绝对误差证据，细化也不重新CAPTURE。取q_sample=max(0,L)保持原历史下界；证书字段与重放身份不增加。

### 2.2 具名失败和所有权

- qqbar_sqrt调用qqbar_root_ui(...,2)。固定源对部分degree位长条件只打印并void早退；实现须在进入该实际分支前识别，不因输出仍像合法数字就使用旧scratch。此为库表示边界，不给科学参数或主roster另定数值范围。
- enclosure_raw的内部次数/精度守卫可flint_throw；除零/分配失败及abort不能自动当作已定义模拟内返回。库资源不足不证明几何EMPTY，也不转为普通丢包或零Q。正常完成的API语义与所有输入必成功是不同结论。
- qqbar对象可变，冻结根及传递系数/球/DAG须由所有权层保持。qqbar_set实际复制，qqbar_cache_enclosure会写原对象，不能用于已冻结输入；只读求值使用独立输出/scratch。采样引起的额外复制、引用、保留和回收归本查询费用。
- 实际CURRENT_SEGMENT_ROOT生产者、传递不可变、异常收束及P_model执行对应尚未实现。本节关闭具名数值API和证书关系，不认证实际控制来源或整个POSITION服务。

主要一手依据：[固定版qqbar头](https://github.com/flintlib/flint/blob/17950040404e6ed797a4becd8a866fb3f62b5c5e/src/qqbar.h)、[固定版qqbar文档](https://github.com/flintlib/flint/blob/17950040404e6ed797a4becd8a866fb3f62b5c5e/doc/source/qqbar.rst)、[root_ui源码](https://github.com/flintlib/flint/blob/17950040404e6ed797a4becd8a866fb3f62b5c5e/src/qqbar/root_ui.c)、[端点外包源码](https://github.com/flintlib/flint/blob/17950040404e6ed797a4becd8a866fb3f62b5c5e/src/arb/get_interval_arf.c)。代理阅读强度为实际所需头/API和必要函数源码；不是全库审计。

## 3. 代码包准入与实际完成口径

用户完整实验前目标已授权必要建设。根依第1节的完整数域/算法接缝和第2节的实际精确数候选，为implementation/pie_geometry/授予限定源码实施准入：纯几何数据/验证、静态区间/CAND、独立N、G私有快照转换、精确数接口、声明型编译检查及说明。后端尚未实现的符合性不循环变成写这些源函数的前置。

允许C++14 -fsyntax-only实际模板实例化检查；本包暂以声明型精确数接口编译，不假装已链接FLINT或有完整数值后端。不链接或运行研究算法/测试/仿真，不生成地图、场景、实验参数、O/seed/tape/manifest或结果。不含GROUP策略、owner发布、POSITION来源实现、主规划器或外部对照修复；其它模块的阶段边界保持。

这些源函数及全部容器/数值库工作将进入原P_model部署计算，不能留作免费native几何导入、按一次库调用计一个基本步或按事后host耗时倒填费用。具体计算后端候选由astra_ultra_compute_backend建设；在实际接入/暂停/计量验证前，本包不能用于发布研究结果。本轮源码交付与后端验证分开记，完整实验前目标仍未完成。

三个文件include/pie_geometry.hpp、checks/compile_contract.cpp、README.md已由Codex geometry_binding实际交付。根已全文审阅闭凸退化、物理进度转换、闭端点/re-entry计数及私有快照异常保持，并独立执行g++-11 -std=c++14 -fsyntax-only -Wall -Wextra -pedantic的完整Geometry声明型模板实例化；工具219cab退出0、无诊断。源文件SHA256及精确命令见73C37_ATTEMPT_AND_GEOMETRY_IMPLEMENTATION_RECEIPT_20260914.md。当前结论是纯核心源码和这一级静态检查完成，不是数值行为、VM费用或端到端运行已验证。

## 4. 有限计算后端候选与根取舍

astra_ultra_compute_backend实际使用gpt-6-astra/ultra，报告已完整终态；根全文接收，并独立核固定版CPU逐指令、native bulk、默认RDTIME和标量load源码。根选定[此份报告](implementation_binding_evidence/compute_backend_candidate_20260914.md)的libriscv v1.20 / commit 12055fb051bbdf3cfdec48b3386d06e38d038cf4作为下一项后端建设候选，不重搜同类VM。它是工程底座，不写作本文算法贡献；当前没有授予整个VM实现或研究运行资格。

候选为RV64IMA、LP64、单hart/私有worker及GNU11.4 guest软件浮点，延续有关int/pointer/binary32/64源含义。FLINT及实际GMP/MPFR/运行库闭包编入guest，数值库内部循环也计费；不为每个FLINT函数手写恒价公式。完整guest依赖与long double/fenv等实际可达语义仍须具名对应，不能将主机已装GNU11包当作完成交叉构建。

根直接核定的四处源码：step_one在execute与PC推进之后才加instruction counter；native memcpy/memset整块做完才penalize；默认RDTIME读宿主steady_clock；单条LOAD还包括寄存器读取、地址算术、内存读及写回。因此现成fuel或step_one不直接满足固定73逐基本步先付费。上一沙箱curl失败没有被管道末尾exit0掩成读取成功，授权重试实际取得正文；原库代码未修改或执行。

| 后端包 | 按原规格需要完成的具体适配 |
|---|---|
| B1 | 允许的有限标量指令展开为已付固定字操作与可保留续体，在下一未付步骤前暂停；完成前缀、PC、寄存器和私有临时值一起保持。不能整指令后倒记账。 |
| B2 | 不接native bulk、native heap、JIT/翻译及guest线程快捷路径；复制/编码/数值运算按guest实际工作执行。 |
| B3 | 接固定73已有first-fit arena与确定guest地址，C/C++及数值库分配接口统一落到所选模型；扫描、对齐、复制/清零和释放照计。 |
| B4 | 绑定实际guest运行库、初始布局/字段与INIT费用；未初始化对象不因宿主页为零变合法，不使用上游默认容量作为实验值。 |
| B5 | 具名imports和AUTH隔离；未知入口明确拒绝，普通字/猜地址不能制造受保护来源标签。 |
| B6 | 虚拟chrono、此前已付工作clock及源PRNG/MT历史映射；禁默认宿主RDTIME及未登记cycle/instret旁路。 |
| B7 | 接原共同队列、CAPTURE、动态guard、后继发布及模型/宿主失败边界；私有暂停不发布半成品，Stop不撤已承担物理责任。 |

这七项是原资格义务的实现落点，不增设七轮审查或全库人工普查。后端只有在对应实现、链接闭包及实际暂停/费用/权限验证完成后才支持研究运行；当前仅关闭“缺少具名可建设执行底座”的来源选择。原六门的整体状态不因候选存在改为PASS。

一手固定源码：[step_one](https://github.com/libriscv/libriscv/blob/12055fb051bbdf3cfdec48b3386d06e38d038cf4/lib/libriscv/cpu.cpp#L383)、[native bulk](https://github.com/libriscv/libriscv/blob/12055fb051bbdf3cfdec48b3386d06e38d038cf4/lib/libriscv/native_libc.cpp#L205)、[默认RDTIME](https://github.com/libriscv/libriscv/blob/12055fb051bbdf3cfdec48b3386d06e38d038cf4/lib/libriscv/machine_defaults.cpp#L32)、[标量load](https://github.com/libriscv/libriscv/blob/12055fb051bbdf3cfdec48b3386d06e38d038cf4/lib/libriscv/rvi_instr.cpp#L98)。GCC软件浮点的直接来源与实际阅读强度见报告，未声称根逐字重读全部运行库。

三份实际完整建设报告保留于implementation_binding_evidence/：geometry_binding_20260914.md、position_backend_binding_20260914.md、compute_backend_candidate_20260914.md。它们是本轮终态证据，不再以旧运行时态重启；下一任务直接用本Q2及具名代码包。

## 5. 数值适配的固定依赖准备

为使后续精确数封装能对真实头文件作静态编译，根准入必要的本地依赖准备：下载并核验上述官方FLINT 3.3.1源包；获取Ubuntu当前已登记的MPFR-dev 4.1.0-3build3头和开发库文件并仅解包到项目third_party；复用本机GMP 6.2.1。允许依赖的configure生成所需构建头及其标准编译器/类型探测；不执行FLINT研究数值函数、make check或实验，不全局安装库。源包原件/哈希、配置环境和实际生成物分开记录。

这只准备宿主声明型/源文件静态检查所需SDK，不代表RV64 guest依赖构建、数值结果、计量或ABI资格。精确数适配实现仍须其已具名正常运算/错误/所有权合同明确后单独接纳；不借依赖准备执行未准入研究代码、输入或参数。当前全部实验载荷与运行边界保持。

本项已实际完成：geometry_binding在third_party/flint_host_config作out-of-source configure，8f5fee退出0，真实生成config.h/flint-config.h/flint.h；本地host_sdk建立固定源/生成头布局并补齐MPFR开发链接，没有全局安装或make。完整命令和生成头hash见[SDK回执](implementation_binding_evidence/flint_host_sdk_receipt_20260914.md)。后继适配所需SDK参数仅-I third_party/host_sdk/usr/include。根随后实际C++14编译qqbar/fmpq/fmpz_poly头并断言固定版本与slong类型，900a8b退出0无诊断；首次检查误用了不存在的版本宏，按生成头的真实__FLINT_VERSION系列纠正后通过，没有改库头。

## 6. 精确数值适配源码包

Astra Ultra的[FLINT值适配合同](implementation_binding_evidence/flint_value_adapter_contract_20260914.md)已完整交付（END_FLINT_VALUE_ADAPTER），根全文接收，并直接核固定源的composed_op尺寸积、root_ui早退、roots_fmpz_poly非恒定根填充/排序及fmpq_canonicalise零分母边界。本合同已足以实施，不新增方案审查轮次。

根准入implementation/pie_geometry/include/pie_geometry_flint.hpp和checks/compile_flint.cpp，以及包README的对应集成说明：C++14私有qqbar_t RAII值、准确零/一、合法有理和一般实代数根入口、完整Geometry所需Ops。值复制独立，copy assignment先复制后swap；move构造init后swap不虚称无分配，move赋值交换两个合法值。零分母/除数、负平方根、根索引/次数、根数组长度、已见二元次数积和sqrt真实早退条件在进入非法路径前检查。原生中止不伪装成C++可恢复普通算法失败，不公开可写原生指针，不添加浮点猜值或序列化旁门。

允许以上源码及对固定FLINT真实头文件的-fsyntax-only模板实例化，不链接或执行数值/几何/研究测试。host SDK只证明头和签名接入，实际RV64构建、计量、真实POSITION来源与运行仍待实施验证；其它原实验输入/参数边界保持。用户现明确采用Astra Ultra定方案、Claude Opus编码，故将此新代码包交Opus，根负责核源码并执行实际检查。失败调用及时接手，不借调用次数延迟主线。

本项源码现已完成。C38真实Opus请求240秒后终态exit124，modelUsage为空、无代码；Codex astra_ultra_position_backend依既定备选完成237行值适配头及45行真实Geometry<FlintOps>实例化夹具。根全文核对所有权、零分母先验检查、一般代数根入口、位长/尺寸守卫及原生异常边界，并独立执行g++-11 C++14 -Wall -Wextra -Werror -pedantic -fsyntax-only，d216b3退出0、无诊断。源hash及真实调用见73C38_FLINT_VALUE_ADAPTER_RECEIPT_20260914.md；README记录实际接入。尚未链接或运行精确运算，不能将静态接入记为运行正确性或完整POSITION服务。

## 7. 当前阶段的准确剩余口径

参数化问题、主方法、比较与形式设计审查已完成。纯几何源码、FLINT真实值适配及它们的静态集成编译已完成；逐基本步执行合同现已完整收到，按§8转入有限源码实现。库/VM链接、真实主线接口和端到端检查属于实验前工程准备，不继续计作未完成的数学审查。

完整官方输入与基线共同域仍须核实。Q1 §6已给出剩余360配置及其实际引用闭包的具体只读范围；此前L23只授权四个首配置及有限引用，扩大正文读取的许可尚未到达。已有获准资料和独立工程准备继续推进，不能将该一项等待误报为全部工作停滞。

距离大规模启动的实际关键路径是：主方法与费用/进度接口完成接入→输入共同域确认→有实际执行证据的端到端检查及实验冻结。当前尚无首次完整运行据以估时，因此不报无依据的小时数或完成百分比；不再重开三轮正式审查、不扩ECBS、不复活DARI。

## 8. B1逐基本步执行源码包

根已全文接收Astra Ultra的[242行B1合同](implementation_binding_evidence/rv64_basic_step_contract_20260914.md)，并直接核固定73 §9.1。接受87个RV64I/M/A编码、13字续体（含建筑状态共48字）、完整有限微阶段图、付费后单步作用、严格后继恢复和失效边界。根独立核算SC最长正常路径为26步；这是模板的表示长度，不是实验预算或整指令单价。

根另直接读取RISC-V v20260120的[基础规范](https://docs.riscv.org/reference/isa/v20260120/unpriv/rv32.html)和[A扩展](https://docs.riscv.org/reference/isa/v20260120/unpriv/a-st-ext.html)：确认JALR清最低位、分支/跳转的对齐异常位置、x0 load仍有访存效果、保守FENCE，以及SC退休前的权限检查、预约写域包含和消费规则。A页首次直开失败，随后从基础页官方链接实际取得，失败不算阅读证据。未将单hart混宽预约选择冒称与上游仅比较地址的实现完全相同。

取指、源寄存器、运算、地址/内存/预约及PC等应用状态转移按合同收费；固定代码语法到微模板的解释和已存续体的阶段选择归求值设施，宿主另报，不能递归收解释器switch或暂停保存税。guest自身解码/遍历仍全部收费。采用此精确口径收窄早期候选报告的笼统措辞，不改固定73的业务计算供给。

根准入implementation/pie_rv64_b1/下三个文件：include/pie_rv64_b1.hpp、checks/compile_b1.cpp、README.md。实现合同中的固定编码/位运算/状态及所有I/M/A微阶段、逐步先扣费和可恢复私有副作用。允许C++14实际模板实例化与-fsyntax-only，不链接或执行guest/研究测试。首次包的CPU/Memory与计费接缝可用类型明确的窄接口和声明型实例化，使该独立状态机先可编译；实际libriscv对象、内存权限/加载、外层收费账和导入生产者随后接入，不能以接口声明冒称整体已运行。

该包不实现B2–B7的业务功能、不开放native bulk/文件/时钟/任意host callback，不生成实际guest输入、参数、O、配置或结果。B1不能给source C++ UB免责，也不能把宿主求值失败折成普通guest fault或继续同一可能有副作用的步骤。实现不需要新一轮方案咨询；根按原用户授权继续源码建设与核验，整体实验前目标仍active。

B1三文件已由Codex完成。根全文阅读703行最终头文件、23行声明型夹具及接口说明，逐项对照I/M/A微步顺序、定宽运算、先付/暂停、闭合分支、SC预约消费及故障封闭；独立严格C++14 -Wall -Wextra -Werror -pedantic -fsyntax-only编译81313e退出0、无诊断。头SHA256为6d8f7bdc3009afb2079d36c71a6ca6001a051416663e180c64f79a2a2707de12，夹具为d08df741d7cc1e5354bb54932a3aba1678449f306b06ddaf9ba91f2e4865406d。实现用ctrl保留位48–49标记当前ECALL两个返回寄存器已写，保持13/48字容量；pending_import_number只返回已付a7锁存，不新增未付寄存器读。原静态合同的“余位为0”据此有一处具体内部表示补充，不改变科学计量/业务接口。Backend/Payment仍为声明接缝，不能据此声称实际VM已运行。

## 9. 已验收数值适配的本地运行检查

精确值适配两文件已获根全文审阅及真实头静态集成检查，下一步直接验证该数值组件。用户的完整实验前准备目标已授权必要实现和验证；根因此将此前§5的仅配置头阶段推进到明确的本地构建/数学单元检查，不把缺少运行证据反复留为文档待办。

准入：在现有third_party/flint_host_config执行官方Makefile的library目标（实际all也只依赖library），仅构建已验hash的FLINT 3.3.1及当前本地链接依赖，不全局安装、不运行上游make check或示例。允许implementation/pie_geometry/tests/flint_value_test.cpp的独立C++14数学单元源码、链接与运行。检查对象只含已实现FlintReal/FlintOps及确切整数/有理/代数数：基本数值恒等式与顺序、超过64位的叶值、一般实根与复根拒绝、0/0等输入错误、复制/移动的值保持与输入不变。测试程序的有限数学常量不是实验参数或公开来源输入。

不在此包运行Geometry、主规划器、控制/观测服务、guest、实验或仿真；不生成map/scen/config/agent/task/delay/O/seed/tape/manifest或研究结果。运行结果只证明这组实际数值集成用例，不证明整个实代数域必定成功、计费正确、碰撞安全或论文效果；已见高次数表示限制继续以源码守卫为据，不为测试分配巨型数组或故意触发宿主OOM。原输入读取许可和保护参数边界不变。

C39可把这份短数学单元代码交Claude Opus。C37/C38调用仍保原始失败归属，不重试已完成的同一代码包；新任务改用经CLI帮助确认的流式JSON输出，保完整实际流与终态，只在完整patch后应用，不能把HTTP200或请求模型名当作实际代码交付。边界明确的本地构建与B1源码并行推进。

固定库已实际构建成功：third_party/flint_host_config中make -j4 library，session75322最终exit0（62369c），完整构建日志native_library_build.log，产物libflint.so.21.0.0。该目标依实际Makefile只构建library，没有make check或示例运行。下一项是已准入的独立值单元检查；未取得其运行结果前不记数值验收通过。

产物SHA256为a3cda89463385fd9bae8068c2abe7d2a882665d34eef91d99a068f3d6fa3b745，构建日志SHA256为cfd0390c554096daa4965657f9afe40c6efbc27ab55e2263fb892946c45f66bb。readelf实核SONAME libflint.so.21及MPFR6/GMP10等宿主依赖，RUNPATH指本项目MPFR SDK；这些是x86_64宿主构建证据，不冒称RV64 guest库。

调用包装调整有具体依据：[精确路由诊断](implementation_binding_evidence/cc_switch_route_diagnostic_20260914.md)从C37/C38原session等值关联HTTP200流，区别于只看最终空JSON。后继C39已用流式回执正常完成，待完整可见patch/source核验后记录代码及实际数学检查；不改写早期RAW，不据一次成功宣称上游延迟全部解决。

独立数值运行检查现已完成：C39取得Opus完整patch，Codex仅另补分子/分母分别保持不变的两条检查。根全文审阅433行测试，真实g++-11 C++14 -O2 -Wall -Wextra -Werror -pedantic链接当前FLINT/MPFR/GMP（2c955d exit0），实际执行native测试（717517 exit0）：passed 102，failed 0。覆盖确切有理/代数运算、超64位叶值、实根/复根选择、具名错误及值所有权；不是102次研究实验，也不证明全数域或P_model行为。完整原调用归属见73C39_FLINT_VALUE_NATIVE_TEST_RECEIPT_20260914.md，测试源SHA256为59a309a119d24563fa1263426e931352b5a4277d2444de4e02c23be222b01fa5。

## 10. 已验收纯几何核心的有限数学检查

§3几何源码已验收，§6精确值源码及§9真实数值单元检查现已通过。根继续准入implementation/pie_geometry/tests/geometry_test.cpp：使用已接受的真实FlintOps，对纯Geometry函数作有限、确定、独立数学单元检查并实际链接运行。测试输入限程序内构造的点/线/闭凸片、闭盒和一条参数化线段的确切几何常量；不是公开/本地benchmark地图、场景、agent/task/delay文件、实验配置或研究运行。输入读取授权不因此扩大。

必须核有独立解析答案的闭端点/单点接触、非凸片并的空隙、区间/CAND与物理距离转换、代数端点/非有理长度、N直接几何答案及G入口/严格出口/再进入、退休关闭模式，以及失败时原私有快照保持。N=G只作附加一致性，不能替代已知几何答案。使用有限手工数学用例，不加随机样本/性能调参或追求测试条数，不为检查触发巨型内存分配。

只执行纯几何库函数；不运行主规划、控制/观测、guest、world、任务服务或大规模仿真，不生成实验O/seed/tape/manifest及受限来源正文。通过也只认证所列用例的真实集成行为；费用、AUTH、完整闭环和论文效果仍须后继实现证据。该任务交Opus编写单个测试文件，根全文审阅并实际执行；沿C39已经取得完整交付的流式调用方式，不重开设计审查。

C40现已完整交付。根全文审阅最终数学测试源码，独立编译链接5a3bf6退出0、无诊断；运行ef0109退出0，passed=163 failed=0。解析答案涵盖闭单点接触、非凸片并空隙及退出后再进入、退化闭凸几何、非零误差盒、无理长度/代数端点的物理进度换算，以及具名非法输入/非单调进度/退休关闭。快照保持检查保存独立字段副本，不用共享同一存储的副本充当预期值。源SHA256为4014b109a1d924bad5d8155a953b4a3103da7a6e6d1304863607788752451b17；可执行为8475ba12994630875c5e538a8e843b134a9134e3ceb06df500191a2e41a60988。调用与作者改动见73C40_PIE_GEOMETRY_NATIVE_TEST_RECEIPT_20260914.md；本节补记根后续实际验收，不回改原调用回执。

## 11. 固定RV64IMA / LP64工具链的实际准备

根已全文接收Astra Ultra的[工具链绑定报告](implementation_binding_evidence/rv64_toolchain_binding_20260914.md)，采用固定驱动2023.10.18（b86b2b37d0acc607156ff56ff17ee105a9b48897）、外置GCC 11.4.0与glibc 2.35、驱动固定binutils gitlink及Linux headers，单一rv64ima/lp64 ABI；不拼用Ubuntu现成LP64D sysroot。报告是来源与构建接缝证据，当前尚无该工具链实际产物。

依用户完整实验前准备授权，继续准入third_party内必要的固定官方源码获取、源身份/发行校验、项目本地host依赖准备，以及这套工具链configure和stage2构建。复用§5已有MPFR SDK；缺失host包优先仅解包到项目本地前缀，按实际依赖补齐。限定-j4构建并记录完整日志；不全局安装、不改变共享工具配置、不跑上游check、guest或研究程序。若下载或编译失败，保留准确失败与可恢复进度，修复具名原因，不能无依据扩大ISA/ABI或换用默认GCC 13。

可以实际查询所构建编译器自身版本、目标、multilib、sysroot与运行库路径，静态核产物ELF属性及LP64 stub。编译器及依赖的标准构建探测不是研究执行；这些准备不开放真实benchmark输入、实验参数、主规划或仿真。实际业务guest编译和运行库服务接入仍按已具名后续接缝实施，不以工具链可用代替B1–B7或端到端正确性。

本项已完成：固定源取得、发行校验、本地host依赖重定位、configure及stage2实际构建均成功；原45216在09:17:54 UTC正常exit0，未重启构建。完整证据已归档[工具链实际回执](implementation_binding_evidence/rv64_toolchain_preparation_20260914.md)，SHA256 9a05f1a90a7c42fd4c38fa2f7d944f3bb37d76d66005778298d809d44e86afff。根全文接收回执，读取实际build终态JSON，并独立查询编译器11.4.0与单一multilib（05c391/3b3894），实际readelf核LP64 loader（e4233b）。代理展开11项运行库/启动产物共2761个ELF头，均ELF64/RISC-V/flags0；根读该汇总及具体命令索引，不冒称独立逐条重核全部成员。

固定binutils gitlink实际是2.41发行，而旧.gitmodules写binutils-2_40-branch；保持原gitlink并据实际源身份修正版本口径。ELF的zmmul为该binutils从M自动加入的隐含子集，未放宽到F/D/C。实际guest long double为16字节/113位精度，与x86并非同一表示；只在后续真实可达语义接入处理，不开全库普查。GMP/MPFR/FLINT目标库尚未构建，本工具链成功不冒充数值guest或B5服务可运行。

## 12. POSITION认证数值内核实施

§2和已完整接收的position_backend_binding报告已确定认证外包的实际API及包含/宽度关系；§6/9又完成实代数值表示和真实运算验证。根据此直接推进对应数值内核源码，不再发起完整方案咨询。准入implementation/pie_geometry/include/pie_position_numeric.hpp、checks/compile_position.cpp、tests/position_numeric_test.cpp及包README；允许对pie_geometry_flint.hpp作仅供该数值内核读取合法私有值的最小接入，不公开可写原生对象。

输入为已有合法精确实代数值、原正epsilon的代数表示及满足0<eps_w<=epsilon的有理见证，内核实际核正性/有理性/大小关系。按已接受链qqbar_get_arb→有向区间端点→向上宽度/向下见证→准确独立dyadic整数对形成结果；对全部相关外包作确定精度细化，并在slong精度增长前检查表示范围。保留输入，结果值拥有独立存储；不使用double、未认证近似、共享输入缓存改写或强制共同指数大展开。具体C++接口及实现常量由代理按该既定合同直接落地，工作精度不是科学参数。

允许真实头静态实例化和有限独立数学单元编译/链接/运行：确切有理/无理值的区间包含、正见证下实际宽度、零/负值与具名错误、复制/移动和输入不变。只核数值层，不执行POSITION服务、控制器或guest；不制造CURRENT_SEGMENT_ROOT/AUTH来源、wire身份、真实传感器精度或费用结果。全部后续业务使用仍进入P_model计费，native检查不是免费部署入口。当前没有授权扩读实验输入或赋保护参数。

C41数值代码现已通过根验收。Opus交付281行内核/105行静态夹具/482行数学测试，C++无Codex修正；根全文核对有向包含/宽度、精度增长守卫、四整数所有权及独立端点重建答案，实际编译e6a2c5和运行e4ca24均退出0：267项通过、0失败。源hash和原调用详见73C41_POSITION_NUMERIC_RECEIPT_20260914.md；根另外确认值头去掉仅新增的前置声明/friend两行，SHA精确恢复原1b93a8f…，没有其他接口或运算改动。真实POSITION生产者/AUTH/队列与P_model费用仍未由数值检查替代。

## 13. B1有限指令状态机单元验证

§8源码及根独立静态实例化已完成，继续准入implementation/pie_rv64_b1/tests/b1_test.cpp及包README的实际检查说明。该检查可以编译、链接并运行本地B1状态机，使用程序内有限手工32位指令字、固定小字节数组Backend和单步供给夹具。这是明确的后继运行阶段，包含这些有限指令的实际求值；不冒称仍然只是语法检查，也不编译/加载业务guest镜像或启动libriscv、规划器、控制服务及研究仿真。

以独立预期值核代表性I/M/A编码和非法编码、W截取/符号扩展、零除/极值/移位、高半乘法、跳转异常位置与rd别名；以明确事件/费用预期核无余额状态保持、逐边暂停/恢复、已完成写不重放、LR/SC的混宽包含/消费/权限顺序、AMO旧值与写顺序、ECALL交接/返回防重、撤销与宿主异常终止。暂停与连续运行的一致性只是附加，不能取代独立答案。单元供给数是有限状态检查的驱动值，不赋H、T_delay、B_CAL、B_max、B*、P_active或density N。

固定有限用例，不引入随机/性能扫描或无界测试框架。测试Backend须保自然对齐/子字写和原子错误合同；其存在只验证B1接缝，不能替代真实libriscv内存/加载器、B5权限或主实验工作账。由compute_backend组织Opus生成具体验证代码，并直接修复真实失败；无新证据不扩展同一包或重开方案审查。

本包已通过根独立验收：全文核对981行测试及手算架构/费用答案，严格C++14编译d4f199退出0，实际运行3d36a1退出0，1348项通过、0失败。根686235核测试SHA256为ba863729f7ae86411409166675ed23b90d8cd4a4cfbd4465251cc50ddbbdd55f，B1核心保持6d8f7bdc…未修改。Opus提供实际部分主体，调用截断后由Codex完成/修正；完整过程见73C42_RV64_B1_NATIVE_TEST_RECEIPT_20260914.md，不将C42记成完整Opus交付。有限指令状态机检查已完成，不重复或扩展，后继转实际内存/服务接入。

## 14. 既定参考段的精确表达式实施

根已直接重读固定73 §3及§6的有限常eta实代数profile，继续实施implementation/pie_reference/中的参考段数值组件及有限数学检查。内容仅为已接受LAUNCH/BRAKE/HOLD/APPROACH的合法段输入检查、首次自主边界时长和段内精确(s,v_ref)求值；复用当前真实FlintOps，不新增控制律或改变4delta的既定profile条件。输入/输出为本地精确值，允许源码、严格编译及有限解析答案单元运行。

组件不调度world、不更新真实控制历史、不签发CURRENT_SEGMENT_ROOT或AUTH，不自行处理同刻cap/RUN/eta安装优先级；调用方必须先完成原自主边界，只有实际合法当前段才能作为POSITION来源。段外采样明确拒绝，HOLD不积分eta而自启动。数学夹具中的有限常量不是实际控制能力、实验配置或保护参数赋值；真实控制生产者、来源隔离与P_model计费仍按原接口接入。该独立代码包由根实施，与C41数值证书及C42 B1测试并行，不重开方案审查。

本包已实际完成：根实现只读参考段及其独立解析答案测试，严格C++14编译链接5b92fd退出0、无诊断，运行f98b4b退出0：passed=50 failed=0。检查含零速/非零速LAUNCH、APPROACH的A=0及A非零、首次cap接点、BRAKE时间/距离、非零eta下HOLD、段外/非法模式与输入拒绝。源hash、命令及具体范围见[包README](implementation/pie_reference/README.md)。这关闭段表达式的实际数值实现和所列检查，不声称完整控制事件调度或受信来源已接通。

## 15. 同原MOVE参考控制状态机

§14参考段表达式及其独立数学检查已完成，继续准入implementation/pie_reference/include/pie_reference_controller.hpp、tests/reference_controller_test.cpp及包README。按固定73 §3/6原控制状态转移直接接通已有精确段：同原MOVE内推进到给定非过去时刻、旧自主接点优先、累计cap安装、实际新RUN、BRAKE及已发生eta更新。各方法用精确比较，先推进旧段再处理同刻更新；HOLD增cap不自启动、BRAKE不被RUN/增cap提前取消、原ell终点关闭后不重开，空间z及MOVE身份不在此数值组件中重置。

该包可以实际运行有限手工事件序列的控制状态机单元检查，以独立解析状态和明确事件先后为答案；这是对应组件的后继运行阶段。不是完整world/规划/任务服务/业务guest或研究仿真，不读取/生成实验输入和保护参数。调用方法的前提是外层已经接受的合法命令/已发生扰动；普通反馈不能进入此接口，去重、来源身份、AUTH及全局公共行权限仍由既定外层接缝负责。只读段值可按值冻结供后继数值查询，不能由数值存储存在宣称真实世界来源已经认证。该包由geometry_binding组织Opus C43实施，根负责接入验收；不重开控制律或三路设计审查。

C43已完整交付并通过根独立验收：根全文核379行控制器、653行测试及解析答案；严格C++14编译a68d43退出0，实际运行c68dad退出0，7组278项通过、0失败。根686235核控制器SHA256 a1cf2b7834efe3ccd344b8226a3c5e55c56857d3ac55a3c05281cfde087671ce、测试6a9e0f478d2a56359b7999059cfbec21154b2166c0f45fcd69cf4ebf28721510。两份C++为Opus完整源码，无Codex修正；原段核心不变。C43单次CLI的自动续传及原运行证据见73C43_REFERENCE_CONTROLLER_RECEIPT_20260914.md。局部控制状态机已完成，后继接实际来源/授权与服务，不能用局部检查冒称完整在线闭环或规模性能已通过。

## 16. 数值依赖的固定RV64交叉构建

§11的真实GNU11/RV64IMA-LP64工具链已经接收，继续准入third_party/rv64_numeric_build与独立目标前缀third_party/rv64_numeric_sdk：取得并校验官方GMP 6.2.1、MPFR 4.1.0发行源码，复用已验FLINT 3.3.1原源，按相同单一ISA/ABI依次交叉构建和本地安装目标库。官方发行源及其实际hash另记，不能把与本机发行版包同版本说成字节相同。目标头/库不混入host SDK，关闭不匹配架构的优化/探测，构建并行度-j4。

允许依赖标准configure/build探测、cross编译及真实ELF/链接依赖检查；明确交叉模式，禁止通过qemu/VM/binfmt执行目标探测、make check、示例或研究guest。若需host生成器，用现有host工具构建运行标准生成器并区分产物。项目现有纯数值头可对实际目标头作-fsyntax-only接入核验，不生成研究输入或执行实验。此包只准备数值目标库，实际内存/分配/运行库服务、POSITION来源与逐步计费仍按B2–B7及主线接口接入。

原九阶段构建/安装均已实际退出0，原14586终态；根全文接收[数值库回执](third_party/rv64_numeric_build/NUMERIC_LIBRARIES_RECEIPT_20260914.md)，其中代理检查6项库产物共890个ELF头和实际目标头实例化，不能表述为根独立逐个核验。实际FLINT链接暴露RV64软浮点glibc的fegetround/fesetround未实现；根全文接收[有界诊断](third_party/rv64_numeric_build/FENV_DIAGNOSIS_20260914.md)，接受仅为FLINT configure设置ac_cv_header_fenv_h=no，使用上游已有double认证失败→MPFR→精确有理认证路径。该配置是明确保守关闭不可用能力，不伪称物理缺少头文件，不改算法/ISA或把相关工作免费化。已启动独立flint_no_fenv目录重建，保留原日志/回执；修复终态和受影响对象/ABI检查另补，不运行目标程序。

该具名修复现已完成：新90412的configure/build/install全exit0，根全文接收[修复回执](third_party/rv64_numeric_build/FLINT_NO_FENV_REBUILD_RECEIPT_20260914.md)，并独立核新config.h关闭HAVE_FENV_H（0035ad）、两份真实checker对象无未定义引用（2aebee）及新库hash（a6dc46）。新libflint.a为32e3c4bfbcc6f51f4f893720496e0a516a4cae60ab9108d5f3ad344b2e061f68，so为3e1ddf7f86b6421d37ab03623849fae94543efb1b57a8ec3f5680aedadf7cf06。代理的两条旧警告消失、132项ELF属性及严格目标头检查均通过，GMP/MPFR未改。此项构建接缝关闭，不重复构建或扩全库审计；业务guest与整体运行仍留实际接入。

## 17. 在线性与大规模可行性的当前判断

用户指出原PIE-D以离散动作延迟为主、未把连续跟踪误差和付费查询作为主要模型。根重新读取[官方原文](https://ojs.aaai.org/index.php/AAAI/article/view/34506/36661)的问题设置、Algorithm 1及实验段：目标逐步揭示、延迟持续时长对规划器未知，规划/执行并发；City实验到5000个体，同时报告该尺度规划超时与吞吐下降。原文的规模结果不能直接继承到本文扩展物理/信息/成本模型。

连续参考与资源受限观测在逻辑上不要求离线规划。保留在线因果：策略/规划只用当前合法已交付信息及其推断，查询、规划和消息只在模型内完成后影响后继执行；不能把虚拟时间暂停给算法无限免费计算，也不能把未来任务/真实扰动提前给策略。批量仿真可以快于或慢于墙钟，不改变这条在线性质；离线分析已生成日志亦不等于离线规划。当前P_model是显式确定性资源成本，不是已标定的实机耗时或金钱价格。

已有数值/几何/参考段检查只证所列正确性，不证明千级规模、完整world可计算性或实时部署。当前潜在重项为几何/索引、代数次数和位长/认证精度、逐基本步解释成本，以及world真值评价；需首个完整闭环后直接量实际耗时、内存、查询/队列和任务吞吐，不能继续用文档/测试条数代替规模证据。解析段与事件跳跃、合法已付缓存/共享和等价宿主加速可沿原语义建设；使用不同服务级成本或近似/免费host路径则是需要明确重定口径的模型变更，本次未实施。逐指令解释本身并非LMAPF学科要求，工程底座不作为论文创新。

实验仍面向大规模在线因果仿真：小规模闭环验证信息/安全/费用，主规模比较维持同一物理、信息、计算和评分合同并另报host资源；不能以小规模精确结果搭配不同计费的大规模近似运行直接认定原主效应。原PIE-D原样复现与扩展域中明示共同适配分别命名，不能把原文未承诺的连续误差保障缺失计作原算法失败。此为当前问题澄清和推进优先级，不重开已完成设计审查或宣称新规模试验已准入/完成。

## 18. 实际页面到B1的单字内存接入

按§4现有B2/B4接口继续实施implementation/pie_rv64_memory/。复用固定libriscv 12055fb051bbdf3cfdec48b3386d06e38d038cf4的真实Memory/Page普通页表示，提供B1的fetch32/read/write/probe；只访问已经显式安装的普通页面，完整核自然对齐、单槽范围、地址溢出和所需权限后才读取/写入。fetch核exec、read核read、write核write、probe核全部所需位；错误无payload或页分配副作用。不走缺页回调、CoW、MMIO、flat arena、native bulk、上游CPU/decoder执行；原模型对页稳定及公开撤权的要求保持。

允许固定官方源码和必要构建依赖的本地准备、宿主适配源码/构建，以及固定小页面和手工访问序列的有限内存检查。上游宿主单元采用其所需C++20，B1及guest源保持C++14；不引入实验容量默认值，不加载/执行业务guest，不以页面存在冒充INIT已付或源对象已初始化。该包由compute_backend组织Opus小包实施，根验收；后继INIT/guest arena/站点调度和受限导入按既有合同接入，不扩成完整Linux或全库审计。

本包现已完成并通过根独立验收。C44启动工具等待后被中止，未返回session、RAW或模型代码，不能称为Opus执行/交付；由Codex直接完成80行适配和101行测试。根全文核源码/测试，并直接核固定上游Page属性、数据、trap/CoW与pages()接口；独立严格C++20编译c2c188、实际运行04dde0均exit0，48项通过、0失败。根cc2af1核头hash 8a9593f9742027b53453ed0458bdf42acc5b8295cfa38e821ab6e6fbc8a6e2b3、测试2efb255627e14f4af664490c752cab27415ea9afa26e181fad3c50c1af43e527。固定上游静态库真实构建和完整命令见[内存包README](implementation/pie_rv64_memory/README.md)；仅提取lib/构建元数据/README/LICENSE，未读取其benchmark正文。普通页接口已接通，付费INIT与业务guest仍未由此完成。

## 19. B5读取ABI参数的付费接缝

§8/13现有B1只交付已付a7编号，其它参数不能通过inspect_register免费进入B5。根直接补限定a0–a6的read_import_argument接口：仅ImportWait合法，单次成功先付一字读取再交付当前寄存器位型到B5自有续体；余额不足时保留输出及机器状态。重复实际读取照常收费，不假装首次参数自动冻结；B5须在覆盖返回寄存器前保存自己需要的参数。a7继续只用既有锁存入口，不增普通寄存器任意访问权限。

该源码接缝及有限手工ECALL单元可编译运行；核七个参数值、无供给不交付、重复读取收费、寄存器覆盖前后含义、错误阶段/非法参数和Payment异常。沿现有宿主异常封死/原样传播合同，不增加机器持久字段或修改I/M/A微阶段。对应受影响B1回归只运行一次；不执行真实imports/业务guest，不用该读字接口宣称AUTH或服务闭环已完成。

根已实现并实际验证：新参数测试严格编译d926fa、运行ee5841均exit0，48项通过、0失败；受影响B1回归编译1cb857、运行3b7b00均exit0，1348项通过、0失败。当前头SHA256 99adf592d521f661baaab4dbae44db4d2e6311207e5a0ca07a999af055a4e53a，新测试899fc93219a3f70b26a2e451d037071f16687d773f199b2245495ee2477cb931；C42测试未修改，§8/13原头hash继续只表示原时点。命令与接口见B1包README，无新增Claude调用。

## 20. guest first-fit arena核心

根已直接核固定73:463–469的既定used[A]/len[A]算法，继续实施implementation/pie_guest_arena/。使用外部提供、独占且非重叠的两张元数据表、数据槽数及非空字节基址；以8字节模型槽映射源分配请求，结果区分成功offset、确定无空间和具名布局/调用错误。完整地址/长度换算在运算前防溢出；按beta+8p的实际对齐同余、逐p递增及逐used读至首占用实现first-fit，不将offset0误作失败。free只接精确活块头，核len/边界后逐槽清used并清len；源生命周期和同址悬空别名不由两表认证。

该C++14核心不动态申请宿主存储。used/len从零建立，初始化不写raw payload或创造C++对象；实际部署编入guest，扫描/标记/清理与辅助运算由B1逐步执行和暂停，不另造一份host恒价分配器。malloc/new/数值库hook随后根据实际ABI接入，本包不声称已替换完整运行库。允许固定小表/有限请求与释放序列的native语义检查，以及现有RV64工具链交叉编译/静态检查；不执行guest、研究仿真或设实验容量/保护参数。position_backend组织Opus C45小包，根验收，与§18独立并行，不重开容量证明或全库审查。

本包现已完成并通过根独立验收。C45真实CLI正常终态exit0，Opus交付核心头，Codex完成有限修正、测试及README；完整贡献、命令和原流身份见[原C45回执](73C45_GUEST_ARENA_RECEIPT_20260914.md)，不将混合交付记为Opus独立完成三文件。根全文核237行头、133行测试及说明，独立严格C++14编译fcbfe7、运行c05bfa均exit0，输出`arena finite native fixtures: passed`；不把assert语句数冒作独立实验数。代理的RV64IMA/LP64交叉编译6acf73及ELF检查af24c1也均exit0，未运行目标程序。根d2ad5a核头SHA256 5921c177a64e15e9ab78bc9f9343fedcdc52101079e7d96160a34b166d22eaa4、测试ae0d8e42106b17a724548cf1bec3f8d90f47e6abd52515a146d2c95a64cf898d。first-fit核心已验证，源分配入口、数值库hooks及实际guest中的计量接入仍属后继。

## 21. 宿主开销记录工具

为§17要求的规模证据准备独立Linux宿主记录器pre_experiment_tools/host_run_capture.py。以无shell的显式argv启动单个受控子进程，原样保留stdout/stderr，记录单调墙钟、wait4的用户/系统CPU和峰值常驻集、退出/信号及可选宿主超时；新目录独占创建，不覆盖既有证据，不采集环境或推导模型评分。峰值RSS按Linux wait4的单进程/已等待子孙归并语义标注，不能称为整进程树同时内存之和。宿主超时是观测未完成，不能赋Q=0或反填P_model费用。

允许用固定微小宿主辅助子进程验证输出字节、失败/信号/超时、资源字段及拒绝覆盖行为；不启动规划/控制/VM/研究仿真，不读取旧研究结果。该工具当前没有实际研究运行命令或实验参数绑定，后继只在相应运行范围具备后使用。复用现有build_capture的原始输出/独立目录做法，保留原构建工具不改，不把构建元数据工具误作已有运行资源计量。

该工具由根实现，已运行`rtk proxy python3 -m unittest discover -s pre_experiment_tools -p test_host_run_capture.py -v`，845b3b退出0，7项通过。覆盖实际辅助进程成功/退出7/信号终止/宿主超时、二进制原样日志、独占目录、不存在命令、资源字段及CLI退出传播。记录器SHA256为0e388b540dbc39ddb9b9f4603aebb9c2795a08008a81c6e3632489b205068ba2，测试e6d15f82a60655a8c625be128a84fa3136d7c954d326e9be9f216e568e3e39a1。接口为`--cwd <已存在目录> --record-dir <新目录> [--host-timeout-seconds <宿主时限>] -- <程序> <参数…>`；无shell执行、无默认宿主时限。CPU/RSS范围依[Linux wait4](https://man7.org/linux/man-pages/man2/wait4.2.html)与[getrusage](https://man7.org/linux/man-pages/man2/getrusage.2.html)，子程序须自行等待其子孙；该指标不认证并行进程树总峰值内存或源算法完成。工具及检查完成，尚未运行实际研究作业。

## 22. 总运行量的统计可行性检查

scale_inference_check（实际Astra Ultra）限定核主稿§4.1/4.3/4.5；根直接复核公式。等权、共同正U、m个独立块时，原Hoeffding半径满足r/U=sqrt(2 log40/m)。令rho=theta/U，则r<theta需要m>2 log40/rho^2；这是半径规划条件，不是给定检出概率的样本量保证。rho不等于相对基线提升率，后者还需乘基线服务率相对理论上界的占比。正式分层设计仍用原加权范围平方和；没有用任务数/时间步数替独立块数、没有给实际重复数或保护参数赋值。当前尚无实际效应或单块开销，不能断言现行设计不可行；单块能运行和足够重复的总成本分别核。

代理及根直接读[Maurer–Pontil，COLT 2009，定理11](https://www.learningtheory.org/colt2009/papers/012.pdf)：独立但非同分布的有界变量可用固定样本经验Bernstein界，归一化加权贡献后能保持原目标。它利用样本方差，但共同界、异质均值及有限样本项可能限制收益，不保证总比Hoeffding窄。若采用，必须在结果生成前明确修改区间构造、加权映回、双尾错误预算和原比较族规则，不能事后择更窄者；不需要改变执行模型/评分目标或虚构iid条件。本次仅完成具体可行性诊断与候选一手核对，未修改固定73或主稿§4.5的现行统计合同，后续实际预注册需明确处理此项。

## 23. B1与真实Memory的有限接通验证

§13/18/19分别已通过组件检查，继续运行一个明确跨接口的有限单元：手工SD、LD、ECALL三条指令通过B1实际读写libriscv的两个预装普通页，再经§19参数/返回接口交接。按独立架构位型和11+11+5的入口费用核结果，并在每个基本步前插入零供给核状态/页面保持；另外核真实页面拒绝写入时的GuestFault与无副作用。允许该手工程序的B1有限执行，不调用上游CPU或运行编译生成的guest/研究程序；预装页面和InitialState仍为局部夹具，不冒称付费INIT已实现。根直接实施/运行该接通检查，复用§18已构建库，不重建依赖或扩指令用例。

根已完成该跨接口检查：implementation/pie_rv64_memory/tests/b1_memory_integration.cpp，严格C++20编译738493、实际运行bf9478均exit0，65项通过、0失败。三条真实B1指令入口共27个已付基本步，付费参数读取/返回与PC收尾后累计31步；每步前零供给不改变机器或页面，真实只读数据页拒绝写入时按既定费用进入StorePermission且无数据副作用。源码SHA256为80878b27a19c0883de61007a72bae03189efae56ccfc81188fab517cff5cab79（根269a40核）；重现命令补入[内存包README](implementation/pie_rv64_memory/README.md)。本项接通B1、普通页及ABI交接口，不替代付费INIT、受限业务imports或完整world的实现证据。

## 24. B4静态镜像的付费计算启动前缀

沿§4/18/23落实implementation/pie_rv64_init/，由Astra Ultra直接实施跨接口部分。输入为事前绑定的静态RV64IMA镜像描述符：固定guest基址、整页槽数、文件字前缀、最终R/W/X及明确的x[32]/PC；不猜sp/gp/tp，不使用上游ELF/Linux构造器的免费复制或默认栈。升序、非重叠、地址可表示的普通私有页布局按声明字段检查；描述符读取、比较、寻址、取得8字节槽、镜像字读取/写入或零初始化及循环推进均按既定基本操作先付后做，以阶段/游标/已付锁存保留暂停。

宿主PageData backing只提供私有表示，未付槽、半镜像及未完成的机器状态不能交给B1执行。零供给不读输入、不分配、不写；模型输入/范围错误终止且保留已付前缀，宿主异常毒化并重抛，公开撤权禁止继续。所有镜像页和B1的48字状态完成初始化后才允许一次计算启动交接。现有InitialState构造器只转移已经付费建立的表示，不额外免除应用初始化；后续动态构造仍由B1执行计量。

该包允许固定小镜像描述符、手工机器字和普通页的有限native初始化/暂停/失败/交接检查，并可在完整交接后接§23已限定的手工B1指令；不执行编译业务guest或研究程序。该交接仅为ReadyToExecute，不等于固定73的INIT_READY：WORLD/bootstrap/角色核验、resident索引提交及严格后继发布仍在外层INIT作业内完成。描述符夹具不是实验config/map/task输入，不赋实验容量或保护参数，不扩大真实来源正文读取。根接源码与实际有限检查后记录结果，不因没有完整INIT而阻止这段已具名实现。

本包已由Astra/Codex完成。根全文核310行头、231行测试和README，并独立严格C++20编译13dc59、运行f69a66，均exit0，58项通过、0失败。完整两页夹具初始化为8610步，逐边零供给不读/写/分配，1024次逐字初始化和2次权限封存无重做；交接后真实手工SD/LD/ECALL及参数/返回共31步。根6a2165核头SHA256 b0d3d2027e44590fe048a101d2083d66264c3bacf09f2f684dd4a16cf228c653、测试683e52ef102679d434dc73322208d8ab31a8ef7bdd625f3c627dface8a5637d3。费用表、16字INIT续体及48字B1状态、条件总式338+33n+8W+2K+5P见[INIT包README](implementation/pie_rv64_init/README.md)。该固定解释模板对已付锁存值操作，不重复收宿主相位/表示转移税；源输入读、寻址、逐槽及业务循环已分别展开。未执行编译guest、整体应用INIT或研究仿真。

## 25. GMP/MPFR到guest arena的真实分配入口

继续实施implementation/pie_guest_allocator/，先接一条可真实链接的数值库调用链：GMP 6.2.1的mp_set_memory_functions三回调到§20既有Arena；MPFR 4.1.0使用同一GMP分配入口。安装必须早于任何对应库活对象、缓存或可触发分配的初始化，Context、metadata与payload在其完整生命周期内独占有效，安装一次后不换绑。请求保持源实际大小及满足目标ABI的对齐，不使用宿主分配或前置隐藏分配头替代所选arena。

alloc按既定零长度及ceil(n/8)映射。realloc使用GMP实际传入的old_size/new_size：核精确活块头与长度边界，先取得新块，按源语义逐字节复制min(old_size,new_size)，最后释放旧块；分配失败不先破坏旧块。free核精确活头及声明长度。GMP回调禁止返回空指针、longjmp或C++异常；具名失败记录后进入无分配终止路径，不能从部分失败的库调用热继续。实际运行在guest时这些检查、扫描、复制与清理均经B1计量，不引入native bulk旁路。

允许该短源码包、只调用分配回调的固定有限native用例，以及固定RV64 GMP/MPFR真实调用链的目标静态链接与ABI/符号检查；不运行数值算法、目标guest或研究程序。必要的故意终止用例限隔离的微小native子进程，并禁写core文件。C46交真实Opus编码，根核源码和实际检查。C/C++全局malloc/realloc/new、无old_size的请求记录、异常运行库与FLINT完整六项hooks仍是明确后继；四项FLINT旧setter的对齐fallback会另加内部头，本包未启用，不把未接入部分写为已覆盖。

C46本次实际调用已终态：e2e469 exit1，服务端402每日支出限额，token为零、无模型正文或代码，原RAW和stderr保持。根按已授权失败后接手方式交Codex继续同包，不归属Opus，不重复请求或修改共享路由；实际源和运行结果完成后另记。

该分配调用链现已由Codex完成。根全文核头、实现、native测试、目标链接fixture及README；独立严格C++14编译dea1e2、有限native运行1fd455均exit0，输出`allocator finite native callbacks: passed`。唯一故意失败在禁core的子进程中以SIGILL终止；测试不调用数值算法。代理目标真实GMP/MPFR静态链接a1358d通过；根读ELF/ABI和具名反汇编证据，确认MPFR取GMP三回调、安装地址为pie_gmp_*，目标失败路径写状态后EBREAK。目标ELF未运行，其默认libc分配符号仍存在，未声称完整分配闭包。根4892a8核头89931aff7f36617d202cefab63785318f883993e9dd7f6a510b9cd85329c6c19、实现68d5c2dae26aa5fe026597c65b0d5f0a166fa8726ceb92cb39b50a627f488b30、测试8a7e99173933fb7a7bf2587fac5d8a9095ec1b6deb7af15fd1b965dbf5132fcf、链接fixture 2b321bac9221b7424403dd013f21b58ad3eb74858ada817024de1d3ab29191ea。原C46回执保持调用终态，本地实现证据见[包README](implementation/pie_guest_allocator/README.md)。

## 26. PROCESS_SLICE的有限供给记账接口

根实施implementation/pie_service_meter/，为B1及§24启动续体提供同一个try_pay_one/完整原子费支付口。一个受信ServerMeter对应一个固定服务站和已绑定NATURAL或STRICT制度；每个原PROCESS_SLICE用严格递增的公共行序及明确正容量开始，上一行须先关闭。支付先判足额再扣除，原子操作不足全费时余额不变；行关闭后不能继续支付，后继行不能携带未用余额。NATURAL收费等于本行实际已付工作，STRICT收费为原行全部供给并另报实际工作，支持空工作行。固定宽度计数只在本行容量内作差/扣除，不用累计回绕计数器充当模型总工作或CPU clock。

该对象只实现固定73允许的理想供给判足额/扣账设施。业务guard计算、队列/任务选择、原子费用本身的具名来源、跨行发布及FIFO仍由原站点合同接入；观察接口仅供受信调度和宿主记录，不作为guest免费读取信息/时钟的入口。允许此头文件与明确容量/行序/支付请求的有限native语义检查，并用§13已验证的手工B1指令检查真实暂停接缝；不运行规划、控制服务、编译业务guest或研究仿真，不把局部供给常量作为实验参数。该包不新增服务站、公共机会或虚拟时间，主模型总账由实际各行记录汇总，不因此关闭完整B7。

根已实现并完成实际检查：严格C++14编译f47137、运行2f4a7c均exit0，60项通过、0失败。核足额原子扣费、NATURAL/STRICT实际与收费分开、空行、关闭/重入/倒序拒绝、无剩余结转及uint64完整边界；真实B1 ECALL在两行供给中暂停/恢复，5步入口、1步返回和2步PC尾段均实际计量，两制度架构结果相同。根2ab95e核头SHA256 ec39fbbf1fea011adc440b61d6566dbd527660048640776833973f8f6b8756af、测试29d19ce4519c9102972b269148cdce49e953bd9069932ebee774aa46aa8c842b。接口和命令见[服务供给包README](implementation/pie_service_meter/README.md)，尚无完整站点或研究作业执行。

## 27. 固定编译诊断程序的真实计量链

继续implementation/pie_rv64_compiled_probe/，由Astra Ultra实施一份固定、无标准运行库的C++14诊断程序和链接脚本，以及受限ELF提取/运行检查。固定GNU11.4、rv64ima/lp64、freestanding，显式_start与栈，关闭异常/RTTI/stack protector/PIE及relax；实际可达指令仍须属于B1已支持集合。用volatile固定输入和栈中间值保留实际64位整数算术、32位定宽运算和访存，诊断结果有独立字面量答案，最后以明确EBREAK终止；不用数值库、规划/几何/查询/world、syscall/时钟/RNG或动态构造。

链接固定有限RX代码页与RW数据/结果/栈页面，完整布局用脚本断言和显式初始寄存器绑定；这些地址/栈界和供给表仅是该诊断夹具。提取器只接本包新生成的ELF64、小端、RISC-V、ET_EXEC及flags=0的实际静态形态，核头/表/文件与内存范围、filesz≤memsz、对齐/权限、无重叠和入口，拒绝动态/解释器/TLS/重定位等非本形态；不建设通用Linux loader。文件不足一字的尾部及整页padding在固定镜像中明示为零，事前静态提取不替B4的逐字取得/安装费用。

允许该诊断程序的真实目标编译、静态提取核验以及由Initializer→MemoryAdapter→B1执行；使用§26 ServerMeter和一个事先固定的有限正容量行表，NATURAL/STRICT同表，初始化交接后于下一切片继续同一诊断任务。核结果、实际工作、全供给收费和无余额结转。唯一通过终态为预期Breakpoint且全部结果匹配；其它GuestFault、ImportWait、用尽诊断行表或宿主失败均为检查失败，不补表追求成功。宿主只读诊断结果，不回流guest。该项首次准入的是具名有限编译诊断guest，不是研究/数值库业务guest或完整INIT_READY、服务world/实验；原受限输入与保护参数边界保持。

本链已由Astra/Codex完成，根核源码、提取/运行检查及独立算术/费用答案，严格C++20编译cb4be0→bae118、实际运行3e3fbb均exit0。实际9496字节ELF映射为2段/3页，17项畸形ELF拒绝；10个独立结果字、32寄存器、三页全部字节/权限及1024行实际工作账在两制度间一致。初始化12769步、执行465步，NATURAL收费13234、STRICT收费31744；第412行完成计算启动、第427行在0x100ac预期EBREAK终止，剩余固定行为空工作，没有补表或事后调整答案。根ac4c15核guest SHA256 3cce70701d82dfa1b1bdba95e3dfb99b2a67fe9655549c698b471064c7e28b6c、linker 124209a2ba6ac51ca0652f95eafc089463ef07efd36a2644d5c53f8e4792a0e2、host 5dd420c1e76b3ad296458bbca9c5fed23a80ac66ec50a86b3178b65335a031eb、ELF 3c69034ba65fa7f1b8d8b483a7cbd28c289f60b4f6defff357ac62c9888b0312。精确复现命令、事前指令路径计数和首次链接修复见[编译诊断包README](implementation/pie_rv64_compiled_probe/README.md)。此项关闭具名编译诊断链，后继接数值运行库与业务服务；不重复增加诊断程序或冒称规模性能通过。

## 28. 现行加权Hoeffding区间的数学实现

继续pre_experiment_tools/paired_hoeffding.py和对应有限数学单元，由scale_inference_check实施。保持主稿§4.5现行统计合同：精确有理输入w/d/U和alpha，核维数、归一化、非负权重/界及|d|≤U，以精确有理求加权估计和已知目标范围，按原公式计算半径后裁剪区间。超越函数和平方根须有明确向外误差处理，不能用向内舍入的普通float区间声称原覆盖保证；全零界返回零点区间。允许标准库Decimal的一手文档定点核验、纯数学源码与固定小有理夹具的实际单元运行。

本包不改变区间方法或错误预算，不采用§22的候选EB，不赋重复数或保护参数；不读/生成研究结果、实验roster或config，也不写结果补缺/筛选逻辑。内核只计算已给定合格数值的区间，不认证实际源映射、跨块独立性、评分完备性或总体资格；后续完整分析入口仍须按既有UNINSTANTIATED/UNESTIMABLE/INFERENCE_UNAVAILABLE合同接入。该纯数学检查不构成科研结果或主实验运行。

本包已由Astra/Codex完成，根全文核两个Python文件并独立运行固定数学单元，ec6427 exit0，7项通过。精确有理求和及端点，正值转换/乘法向上舍入，正确舍入的ln/sqrt再取next_plus以形成半径上界，最后精确裁剪；测试以有理atanh级数和严格余项界提供独立对数答案。舍入口径依据[Python Decimal官方文档](https://docs.python.org/3/library/decimal.html)及代理定点核对的本机标准库，不用高精度近似互比代替向外性论证。根ac4c15核实现SHA256 1f07829fa78a107e3d51df62a5c3f81fd8536c58ca3546b5acbe2e6c881158ea、测试6a586f61ee402ae925589a87d2751000c08248ef52d54380dee1824be033d34e。复现：`rtk proxy python3 -B -m unittest discover -s pre_experiment_tools -p test_paired_hoeffding.py -v`。仅算术内核验收，完整分析资格入口仍未完成。

## 29. 四位请求长度记录与 FLINT 六回调后继（2026-09-19）

接续已明确的 tail 方案，在同一 allocator Context 增加外部四位请求记录：每16个数据槽使用一字，活头的请求长度为 `8*len[p]-tail`，tail=8仅用于一槽零请求。新增表在任何元数据初始化之前核完整地址、对齐、容量和不重叠；占用的 `ceil(A/16)` 字纳入原 R_aux，不为 A 或实验参数赋值。GMP sized 接口与 FLINT unsized 接口共用精确长度记录；重分配先申请、复制精确请求字节、最后释放，失败保留旧块。FLINT 使用实际六回调 setter，消除旧四回调对齐 fallback 的隐藏头。

该后继限 Context、库分配回调及其微小 native 内存用例、真实库链接与 RV64 静态 ABI 检查。沿用§25分配回调检查范围，不执行数值业务、研究查询、目标guest或仿真，不新增全运行库普查。规格明确的源码包交实际 Claude Opus；根负责审阅、有限检查和记录真实归属。§25原时点证据不改写；本节完成状态以本轮回执为准。

本包已完成。新的 Opus 流报告 `anthropic/claude-opus-5`，在900秒终止前返回完整核心与旧测试修改，新增测试输出中断；根只提取完整文件，补写独立六回调测试与目标链接夹具，未重试或更改路由。两组严格native编译5fc067/144e0e及实际运行1e74bc/896056均exit0；覆盖精确请求大小、tail跨字/邻字段、实际六hook指针、calloc精确字节、失败保留与不合法布局无副作用。RV64真实三库静态链接15c908→f4d2ef exit0；ABI与具名符号3f98c6/fc424b通过，目标未运行。是Opus核心＋Codex补完验收的混合交付；原RAW保留在本轮implementation_binding_evidence下，完整命令见[allocator README](implementation/pie_guest_allocator/README.md)。全局C/C++运行入口及完整应用仍未完成。

## 30. 已验证 POSITION 到退休提案的接缝（2026-09-19）

Codex 在 `implementation/pie_progress_retirement/` 实现接收侧的确定转换：以外层已经完成认证的证书接口为输入，核五项 geometry/MOVE binding、捕获≤交付≤提交时刻及进度域，按 max 保留非退化下界；只有进度增加时，调用现有 G 将 q 前移而保持 b 不变，产生私有只读退休提案并核没有新增资源。迟到证书不用交付时刻外推；无新进度返回 no-op，数值/构造失败不改变原快照。几何仍按严格退出保留接触和终点。

根以真实 FlintOps 显式实例化接收器和证书接口，`g++-11 -std=c++14 -Wall -Wextra -Werror -pedantic -fsyntax-only` 实际退出0、无诊断（696b25）。夹具只有声明，无 main；没有执行服务或研究算法。该接缝不冒充 AUTH producer 或完整资源提交：真实来源认证、当前活动身份、所有者与base版本复核、付费原子发布和END驻留交接仍须外层完成。查询索引只接最终已提交增量，不使用此私有提案释放资源。命令及接口见[接收器README](implementation/pie_progress_retirement/README.md)。

同一接口随后经既定RV64IMA/LP64工具链和目标数值SDK静态实例化，8d8bf6 exit0、无诊断；没有链接或运行目标业务。

## 31. 空间阈值、依赖与实际成本的查询候选（2026-09-19 至 20）

独立后继候选 `D_SRDC_v1` 已收敛为[确定算法合同](implementation_binding_evidence/query_scheduler_contract_20260919.md)，并实现于 [pie_query](implementation/pie_query/README.md)。固定 cap 下，用所有已进入闭区间的最大物理退出端点作为严格释放阈值；一个需求被同一 owner 占用的全部资源都可清除时，才计一次关系收益。立即准入与部分解除收益按字典序排序，结合一跳执行依赖权重，以已交付且实际结算的兼容查询收据估计工作量和响应等待。预测只选查询对象，不写进度、owner 或 cap；缺历史/真实报价或无正收益时使用成功发布才前进的稳定轮询。采样前等待参与预测，采样后等待只进入响应成本。

源码复用现有 `Geometry::intervals()`，为 cap 建入口游标和退出值缓存，并维护资源/owner/请求反向索引。覆盖非凸重入导致净 mask 不变、无新入口但 cap 严格越过退出值两种必要更新。只接已提交增量，私有退休提案不能提前清 owner；准备与提交分开，发布游标也先完成所有可能失败的构造，再与外层同一次成功付费发布交换状态。初版事务仍复制 map 骨架及受影响反向集合，实际复制/回收和精确数值成本必须计费；并未达到全持久化局部更新成本，亦未宣称千级规模性能。

初次完整主机/RV64严格静态实例化 567a1c/dad69d 均通过；有界接缝检查随后修复Choice移动误标noexcept，补齐无精度来源的可空字段与轮询路径，并把提交后旧根回收留给调用者持有的已消费准备对象。最终使用禁止复制消除的严格C++14主机静态实例化30da2e→8bbb30、RV64IMA/LP64静态实例化241583→1c080b，均exit0、无诊断，覆盖真实FlintOps与不可默认构造Real及移动异常合同。独立纯阈值数学检查编译9eb184、运行72892f均exit0，核严格接触、非凸重入、cap等号、终点、多资源整关系与物理单位。Index/Scheduler未运行；14项机制规范、增量对照重建及实际付费服务闭环的运行核验仍待相应运行范围具备，静态编译不充当这些证据。

规格明确的查询实现曾交真实 Opus；900秒终态仅返回不完整声明，无可采用的实现，未重试或改路由，RAW 保留。实际增量索引由 Astra Ultra/Codex 完成，根完成阈值助手、调度器、检查和文档。候选未覆盖冻结 D、主稿公式或正式实验臂，参数仍未赋值，未运行研究作业或公开推送。本轮交付、文献启发与剩余接口见[本轮记录](implementation_binding_evidence/IMPLEMENTATION_SESSION_20260919.md)。

## 32. POSITION、物理 owner 与查询视图的单根发布（2026-09-20）

`implementation/pie_position_commit/` 将§30退休接收器与§31 Scheduler接通。外层已准入状态导入时从实际Action.geometry构造G快照；普通更新禁止q变化和POSITION证据旁路。认证POSITION准备同时更新q、逐项核对并删除原MOVE几何owner、更新查询关系；对CAP_EXTEND另维护全长未来快照，再用暂存owner表重算非owner条件，避免非凸重入资源在当前退休后从未来需求丢失。达到全长必须撤销CAP_EXTEND；POSITION到达终点仍保留终点责任，不生成END。cap/lifecycle准入和END驻留交接由原外层显式输入。

一个实际不可变Root承载上述状态；准备失败不发布，commit核实际根身份且仅交换已完成状态。即使query发布沿用view字符串，仍改变根身份，使旧POSITION准备失效。旧根留在已消费准备对象中，回收须实际计费。此包没有认证producer、实际cap历史或Srv_C付费槽实现，不把接口名当作真实资格。全表骨架复制和结构校验扫描仍存在，不能宣称全程局部复杂度。

本次Opus正常退出但仅给出准备检查目录的普通文本和形似工具回执的文本，没有真实工具调用或源码交付；根保留RAW后由Astra/Codex完成。同一头文件的严格C++14主机与RV64静态实例化782750→a48ac2、7f5475→a5b331均exit0；主机固定有限用例59061e→8375ad编译/链接exit0，尚未运行。用例覆盖闭接触、非凸未来需求、准备异常、迟到证书、query-only stale、cap扩展/全长与END后旧证书。原始调用、运行范围和局限见[后继记录](implementation_binding_evidence/POSITION_COMMIT_AND_METHOD_20260920.md)与[接口README](implementation/pie_position_commit/README.md)。

随后查询器9组有限native夹具也已完成并严格编译/链接f2a6ad→edc292 exit0；根核源码及最终source/binary哈希d646d8。两份具名native程序的运行确认已一次提出，尚未获答或执行；不扩展科研载荷或服务运行。具体手算/重建对照及公式fixture可达性限制见[运行范围](implementation_binding_evidence/QUERY_POSITION_NATIVE_SCOPE_20260920.md)。真实报价接入仍需按query/job累计实际B1工作，不能把STRICT整行charged_work误接为查询成本。

## 33. 查询方法正文与四类局部勘误（2026-09-20）

独立[方法补充稿](implementation_binding_evidence/QUERY_METHOD_PAPER_SUPPLEMENT_20260920.md)已给问题、贡献、确定公式/伪代码、严格阈值/预测不释放/条件增量等价三项性质和最小验证矩阵。它明确费用乘积与一跳权重是启发式，不声称全局最优、普遍公平或已提高吞吐；新候选不静默替换冻结D或正式臂。定向文献已形成可用启发和近邻限制，不重开完整审查。

主稿§2.2、§4.5及直接联动表述已按实际依据完成四类局部修正：有限窗整数界、效应与点估计区分、已有运动约束下的正时间界、固定裕量及引文归因。根修改前逐字备份了已有未提交稿，其SHA与接续起始一致；其它内容及历史证据保留，文末添加日期勘误。不是恢复远端旧稿，也没有赋实验参数或更换统计合同。具体证明、备份与集成状态见[局部修正记录](implementation_binding_evidence/MANUSCRIPT_LOCAL_CORRECTIONS_20260920.md)。

## 34. 两份有限组件运行与零历时收据修复（2026-09-20）

用户明确允许“这两份有限测试及必要修复复测”，§32所记待答已结束。根实际运行原9组query_native及position_native，9e514a/9d7752均exit0。人工夹具不读实验输入或赋保护参数，不运行规划、控制服务、业务guest或world；源码含独立手算oracle、增量对完整重建，以及q/历史/完整owner覆盖一致的预测例。部分纯评分fixture不冒称物理可达状态。

定点费用接缝随后发现实际合同矛盾：固定73第552行允许不同公共行同物理时刻，B1工作供给不自动增加物理时间；独立候选却误拒正工作零历时收据。根修正Scheduler及候选合同：接纳该合法收据并保留最新身份，候选保持Unpriced/RR，不构造零分母、不补常数、不回用旧正历时报价。第10组回归核正→零→旧晚到→新正恢复、负时序/零工作拒绝及异常状态保持。最终查询器严格编译f2f558→34edba、运行f41bdd均exit0；PositionCommit重新编译d27b4c→d2e9d2、运行98e0c3均exit0；两者输出具名passed。组合RV64静态实例化5595b3→5c00f6 exit0，目标未运行。根df3f27核最新源/二进制哈希；范围与命令见[有限运行记录](implementation_binding_evidence/QUERY_POSITION_NATIVE_SCOPE_20260920.md)。

根同时接纳[Q_CAUSAL_V1收据归属](implementation_binding_evidence/QUERY_RECEIPT_BINDING_20260920.md)作为独立候选后继接口：唯一触发query承担发布后实际业务工作和共享维护，业务尾部关闭后结算；收据报告/传输/安装/自身GC单列ReceiptAccounting全费，从报价标量排除以有限封口。全部工作仍在主总账，失败不退款，profile含归属版本。它不改变冻结73的总计费或正式臂，也不是现成真实收据producer；AUTH、成本schema与实际付费交付仍待接通。

## 35. C/C++公共分配入口与真实目标库链接（2026-09-20）

`implementation/pie_guest_runtime/` 提供不替换宿主的具名core及只显式链接到guest的符号TU。已有Context增加只读installed_context查询，继续唯一绑定；C malloc/calloc/realloc/free/aligned_alloc、C++14 throwing/nothrow/array/sized new/delete共用既有tail长度记录。C普通耗尽返回null、realloc失败保留旧块，坏状态/错误指针trap；new保留真实new_handler和bad_alloc语义。缺少初始化绑定时不建隐藏heap；free(null)可直接返回。GMP/FLINT原有失败终止语义不变。

规格明确源码交实际Opus，68407 ms/单turn正常终态，模型用量标记claude-opus-5并返回完整五路径补丁；根核完整代码后应用，补精确状态类型、实际链接fixture与后继aligned入口。初次RV64链接5df471→cfce9c失败，map证明FLINT合并对象引用aligned_alloc而拉入libc malloc.o导致多定义。根复用已有aligned API补公共符号，未屏蔽重定义、改写库或引入fallback。最终严格host静态38b3bd、目标三库静态链接f767eb→718331均exit0；ELF/ABI6f5527及实际符号/反汇编b90eae、90b79b、acae2f、5b1ad6核new/异常分配至新malloc/core链。

此为Opus核心＋Codex接入验证的混合交付，原task/RAW/patch保留。新runtime/ELF未运行，不受§34两份native授权覆盖。GCC异常池有main前malloc，实际paid INIT须先构造/绑定Context；最终ELF仍有libc内部minimal allocator/启动和其它imports，公共分配符号接通不等于完整运行库闭包。明确可达启动/异常/TLS路径与整体应用仍须后继，详细命令/边界见[运行入口README](implementation/pie_guest_runtime/README.md)。

## 36. 真实费用段的归属/汇总与一次性启动接口（2026-09-20）

`implementation/pie_query_cost/` 接续已采纳的Q_CAUSAL_V1。一个AttributionLane拥有真实ServerMeter，按server/Compute或Publication/制度固定身份；打开行之前复制已建立的唯一job/query账户，关闭行形成不可变源段。实际借记失败不退款，idle严格整行费和实际工作分开。ReceiptBuilder核已准入闭合bundle的段守恒、供给键唯一性、Query账户及时间次序，只将actual_work逐Word精确导入Real并求和，避免固定宽累计溢出；不把STRICT整行供给当查询成本，也不把零历时改成虚构正等待。

核心实际由Opus交付完整单文件补丁，单turn正常终态132108 ms、模型用量标记claude-opus-5；原task/RAW/stderr/patch保留。根核源码并补计量层次、完整实例化和独立大整数夹具。主机2614b5、RV64 0ec1b3静态实例化均exit0；新三组native夹具eb89f0严格编译/链接exit0，**未运行**，不借用§34两程序的有限授权。源码/命令与界限见[费用接口README](implementation/pie_query_cost/README.md)及[交付记录](implementation_binding_evidence/QUERY_COST_CORE_20260920.md)。

源记录载体不等于应用免费读取计量器。inspect至close间不得再借记，更不能把wrapper经同一meter递归自计；native记录开销由宿主记录，真正应用的归属创建/交接、导出/传送/验证/精确汇总仍走已有付费路径。ReceiptBuilder仅转换已认证、已验证完整性且业务尾部已关闭的数据；AUTH、闭合业务协议和实际交付没有被类型/字符串/求和自动建立。没有真实收据时，原调度器仍使用既定Unpriced/RR路径。

同轮新增`implementation/pie_guest_startup/`：常量初始化的稳定Startup槽中真实placement构造Context，一次绑定GMP/FLINT后才可按镜像表运行真实构造器；重复、重入、双对象已有绑定均拒绝。构造器异常保留效果并记录失败后传播，不能解除绑定重跑。5项编译断言固定当前nonthrowing下层合同；最终严格host 01682b、RV64对象e5f744均exit0，未执行。定点真实镜像证据确认标准CRT在preinit前已走Linux/TLS，需显式入口和付费TLS/TCB；frame_dummy已触达线程状态，EH pool实际请求72704字节是该工具链事实，不是实验容量赋值。接口与有限后继见[启动README](implementation/pie_guest_startup/README.md)及[具名证据](implementation_binding_evidence/GUEST_STARTUP_BINDING_20260920.md)。它不构造TLS、不替代完整INIT_READY，也不扩大到整库审查或运行许可。

## 37. 显式数值启动镜像、TLS描述符与成本责任树（2026-09-20）

接续§36，新增`pie_guest_startup/image/`的显式_start、真实数值诊断和链接补充脚本。入口直接调用Startup绑定与真实init表，然后由FLINT计算并核`(2^64+1)^2`，完成本地对象析构才写完成相位。实际Opus交完整三文件，单turn172124 ms、模型用量标记claude-opus-5；根核SDK修正void转换API用法、C linkage及失败状态，保留原补丁/RAW。既定GNU11.4/rv64ima-lp64静态真实库链接708721→72e843 exit0；没有Linux主入口、fallback heap、pthread/syscall成功替身或宿主数值代执行。

新ELF具名检查d97da7/3003d0/7c2158/f62b64：_start直接进入pie_numeric_probe_start，init数组仍只有frame_dummy与真实EH pool两项，无binder动态构造器；五项动态重定位均R_RISCV_NONE。真实LOAD/TLS/gp/栈/结果区及SHA见[镜像README](implementation/pie_guest_startup/image/README.md)。没有执行该镜像或据静态符号宣称所有其它libc路径不可达。固定诊断的payload/metadata/栈尺寸不作实验参数。

TLS规格由Astra/Codex核当前glibc2.35上游与新ELF实际nptl只读描述符/指令，确定pthread1984字节、PRE2016、tid32位offset208、DTV指针tp−16及单模块48字节数组。保留真实112字节tdata和3744字节tbss，独立页存储，不在与init表重叠的.tbss显示地址清零。非零逻辑tid只表示此单hart域身份，不冒充Linux内核注册。所核源码、字段与单线程普通mutex范围见[TLS绑定规格](implementation_binding_evidence/GUEST_TLS_BINDING_SPEC_20260920.md)；不扩大到线程创建、动态TLS或整库模拟。

第二个真实Opus包完整交`pie_guest_tls_image.hpp`，单turn193058 ms，根核后补全区域表示检查和host静态接缝。函数检查地址溢出、页面/模板尺寸、区域互斥及原寄存器合同，在私有StaticImage副本追加RW TLS区域，只设置x4，保留pc/sp/gp；失败不改原输入。严格host C++20编译0d48f9→866d39 exit0。它准备既有Initializer的固定设计输入，没有免费写guest存储或执行构造器；实际付费建立、固定新ELF提取和有限驱动仍待连接。§34两程序运行许可没有扩至此工件。

查询成本后继协议同时收敛：[COST_JOB_TERMINAL_V1](implementation_binding_evidence/QUERY_COST_WIRE_SPEC_20260920.md)按实际发布根及单父业务责任树封口，所有在途/失败/GC责任必须终态，报告网络自身归ReceiptAccounting而不递归开Query成本消息。根限域接纳COST_DOMAIN_V1为独立候选配套的窄证明能力：各站仅证明自己已闭meter段和本地责任终态，经原通道/供给/AUTH交付；特别明示这不是冻结73原Srv_N复制权限。字段顺序、枚举字节值、排序、幂等/冲突处理已确定，独立候选与轮询对照须同协议；现正式臂不替换。真实AUTH、codec/闭合状态机与站点服务尚待实现，不能由接口名称推定完成。

## 38. 两项已授权有限运行、冷缓存成本与终态codec（2026-09-20）

用户明确回复“允许两项及同范围修复复测”，授权覆盖[固定数值guest及费用核心](implementation_binding_evidence/NUMERIC_AND_COST_FINITE_SCOPE_20260920.md)，不再请求同范围。费用核心原三组固定native检查实际9cecc4 exit0、具名passed、stderr空；源码无需修改。它通过实际源段载体/精确汇总检查，不等于AUTH、查询闭合或跨站业务通过。

根完成固定SHA的数值ELF提取/页补齐/TLS接入及Initializer→B1有限驱动，独立核W/K/P和INIT费用、真实终点、数值答案、完整页/寄存器/续体及逐行账。guest在NATURAL实际INIT为14,183,545步、第1732行ReadyToExecute；随后Context绑定及真实两构造器返回。首次a9b2df→a8da77 exit1，为固定供给耗尽。根只补耗尽现场和完整关闭行日志，未改guest或供给，严格编译e188e6→76eb7d exit0；复测d1d572→67f029仍exit1。结果区为[3,0,2,0,0,0,0,0]，执行52,913,860步、总实际收费67,097,405；数值/本地清理尚未完成，STRICT尚未开始，不能写双制度已对账。原失败、8192行已闭账及源码副本保留于[实际结果记录](implementation_binding_evidence/FINITE_NUMERIC_AND_COST_RESULTS_20260920.md)。

定点代码/真实指令诊断证明，FLINT首次缓存初始化必经4064次GMP 16字节申请；仅常驻EH池的9088槽前缀，就要求至少18,466,816次used字读取。现B1实际LD为11步，故保守下界203,134,976步，已超过67,100,672步整张固定表，尚不含INIT等其它工作。根独立-O2镜像只编译并静态核实际扫描，仍满足该下界，因此未运行；原build脚本恢复原字节，未改冻结first-fit、补表或免费预热。此为具体冷启动成本限制，不是错误数值/arena空间耗尽证据，更不据此赋保护参数。调用点、下界及指令出处见[成本诊断](implementation_binding_evidence/NUMERIC_STARTUP_ALLOCATION_COST_20260920.md)。

另实际Opus完整交付独立[pie_query_cost_wire](implementation/pie_query_cost_wire/README.md)的COST_JOB_TERMINAL_V1编码器/解码器，单turn449132 ms、模型用量标记claude-opus-5。原task/RAW/完整补丁及回执保留；Codex只修补丁README前缀、夹具多行注释警告和交付记录，codec行为未改。严格主机7507d8、RV64 baabab静态编译均exit0；固定native夹具44d852编译/链接exit0但未运行，不扩当前两项授权。根定点核字段顺序、大小端、规范排序、剩余长度、供给守恒及结构校验。它只输出DecodedTerminal，不提供AUTH、可信工厂、Collector或真实传输；下一步接本地责任账本。完整证据见[Opus codec回执](implementation_binding_evidence/opus_cost_wire_receipt_20260920.json)。

## 39. 本地查询责任账本与组合提交（2026-09-20）

接续既定责任树协议，新增[pie_query_cost_local](implementation/pie_query_cost_local/README.md)。LocalJobLedger按单query/job/站点/制度绑定，记录实际站点所供的开放lane、已闭费用段、预留/已发布child及本地引用。close核server/job/query、供给身份、容量和actual/charged/unused守恒，转换为owned wire值；原枚举0/1与wire1/2显式switch映射，不靠cast。已取消child、已释放ref、已关闭供给键永久保留使用记录；终态保留失败/取消的全部费用，不能用这些结果删账。

Working→BodyDone须先处理完所有child预留，但允许既有lane及本地尾部继续清理；BodyDone不能再增普通child/ref。只有无开放lane、预留child和活ref才生成完整规范终态，TerminalPrepared起禁止新增业务，Published child尚未完成交由后继Collector等待。所有事件先私有准备，基态/所属对象/消费状态守卫通过才无分配交换根；已消费Prepared继续持有旧根，回收留给调用者相应计费阶段，不在发布点隐式销毁整棵旧树。

根补can_commit供原业务原子事务事前检查，并补prepare_batch：在私有draft上顺序准备多个事件，最后只给原ledger一个(base,next)。因此child发布及其引用交接、多个副本责任可同一次成功业务发布登记，不需先发布业务再补账本。callback仅作有限私有准备，不得进行实际业务发布/I/O或重入原ledger；中间根不公开，异常不改已提交根。首版仍按每事件复制map/set骨架，所有复制和私有/旧根回收按所在阶段计费，不冒称一次复制、最优增量或免费元数据。

实际Opus单次完整交付三文件，session30852→912e82 exit0、414026 ms、terminal_reason=completed，模型metadata为anthropic/claude-opus-5；原task/RAW/完整补丁保留。Codex修字面多余补丁加号及原子发布注释，首次严格host 1bc084、RV64 48ba6c均exit0。根定点核全部状态转换后补上述组合接缝及编译调用形状，最终严格host f16c87、RV64 1244cf均exit0无诊断。编译夹具无main，未运行、未新增native执行请求；这不是功能或性能通过报告。真实归属和哈希见[本包回执](implementation_binding_evidence/opus_cost_local_receipt_20260920.json)。

本地ledger只核站点提供事件的结构与封口条件，不会认证任意struct，也没有实际AUTH、跨站Collector、付费导出或服务dispatcher。原费用源载体仍不能递归自计，应用可见导出和业务引用操作仍须各自真实付费。下一实现接中心完整家族收集和已发布查询/成功POSITION事实，再接既定受保护来源与站点；不增加新的整体审查前置，不运行研究服务或补实验参数。

## 40. 中心事实来源及组合提交预检（2026-09-20）

为接成本Collector，根定点核现有Scheduler/PositionCommit与责任树，收敛[图汇集实现规格](implementation_binding_evidence/QUERY_COLLECTOR_IMPLEMENTATION_SPEC_20260920.md)及[三类准入事实落点](implementation_binding_evidence/QUERY_COLLECTOR_ADMISSION_BINDING_20260920.md)。PublishedRoot必须来自实际SELECT原子发布，CommittedSuccess只来自特定POSITION提交，AdmittedTerminal必须经真实AUTH及合法转发准入；普通struct、任意Prepared或View变化均不能制造能力。action/move_occurrence沿用已接受完整原MOVE规范key，不重新设计其身份；query与request_business_id分开，首网络票据origin绑定实际请求。网络原recipient可能为中继E，必须核最终collector的转发准入并保持原issuer，不能假设N→C直连。

本轮补齐同query多个合法成功副本的确定选择：CenterPositionResultCommit在真实单writer首次成功提交的原子点唯一冻结first_success，后续副本不替换、不签发第二事实，其全部Query费用仍计入；能力重交只重放原记录。合法q不变也可首次成功；Collector不能按能力到达先后、相同物理时刻或job字典序选首次。此前协议未明确这项取舍，已在独立后继条款中明示，未改冻结73或正式臂。

根同时实现PositionCommit的can_commit/try_commit两个noexcept接口，使外层能在所有参与根及付费槽合格后执行无分配、无异常的组合交换。原commit复用相同守卫，保留异常兼容接口。原已授权有限序列补核预检无副作用、查询发布后旧POSITION失效及消费后拒绝重用；严格host 92d234、RV64 f9a762静态实例化均exit0，新binary编译ae5a5a、实际运行32c133均exit0、具名passed。没有运行新服务/guest或扩大输入；源码/哈希和原binary保留记录见[预检接缝](implementation_binding_evidence/POSITION_COMMIT_PREFLIGHT_20260920.md)。真实中心writer/outbox/事实/AUTH组合仍须接入，预检方法不代替它们。

## 41. 中心责任图封口与实际费用报价（2026-09-20）

新增[pie_query_cost_collector](implementation/pie_query_cost_collector/README.md)三文件，将§40规格落实为Collector、限定来源接口及无main静态夹具。终态按完整票据与规范正文去重；核父终态完整清单、所有已知父边的环、跨job费用键重复和固定制度一致性。只有首票据可达责任全部终态且不存在未认领已接收链，才关闭业务家族；失败副本和清理责任保留全费。冲突进入吸收状态并保留触发证据，已安装报价仅保留历史身份。成功接收job的中心归属在成功先到和终态先到两个方向均检查。

封口后将全部Query段按server/row/supply确定排序，显式映射wire枚举，再由现有ReceiptBuilder精确汇总actual，保持STRICT整行charged与业务工作分开。首次成功事实沿§40由真实源端冻结，Collector不按交付顺序决定；源码仅消费该能力。报价准备、准确交付时刻的安装准备及私有batch均使用owner/base/next守卫，无异常交换并保留旧根供相应付费回收。根定点核责任图、成功绑定、报价时序和静态调用形状；首版复制及全图检查的实际成本仍须付费，不宣称最优增量。

一次实际Opus调用session56683→cd2c11在600秒终止，exit124、terminal_reason=aborted_streaming，text_delta为0，没有可采用源码。原始流、空完整补丁占位和终态保留，未再次调用；三文件全部由Astra/Codex接手完成。严格C++14主机f38351及RV64 8c138a均exit0、无诊断，包含真实FlintOps、不可默认构造Real、私有能力负向traits和组合准备接口。没有main、未运行新程序或服务，不能称功能或性能通过；最终源码SHA及真实归属见[交付回执](implementation_binding_evidence/opus_cost_collector_receipt_20260920.json)。

CenterCommitBridge与TerminalAuthBridge仍只有具名声明，没有实际签发器；真实SELECT/POSITION单writer、首次成功latch、AUTH与中继权限、付费终态传输和Scheduler组合安装仍待接通。本节关闭图汇集源码缺口，未关闭来源和站点业务闭环，也未解决§38数值guest固定供给不足或赋实验参数。

## 42. 收据安装的双根组合与原始收件范围（2026-09-20）

新增[pie_query_receipt_install](implementation/pie_query_receipt_install/README.md)，直接绑定现有Collector和PositionCommit。prepare只允许Collector的BusinessClosed或ReceiptPrepared，内部私有batch重新在给定实际交付时刻准备收据并准备Settled，再从该真实Prepared取算术输出，构造只有receipts一项的Scheduler增量。它不接任意外部Receipt或Prepared，不修改q、owner、几何、需求或POSITION证据。旧报价错过交付时刻时重新准备；任一数值/分配或校验失败，两份已提交根均保持。

组合Prepared不可复制或赋值；can_commit先核所属安装器、消费状态及两个真实基态，随后commit无回调、无分配、无异常地交换两根。普通拒绝发生于任何交换之前；单writer前提被破坏导致预检后出现不可能的子提交拒绝时显式fail-stop，不在半提交后返回普通false。消费后两个子Prepared均保留旧根，销毁按实际准备放弃或GC阶段计费。本包完成二组件组合代码，不替代Srv_C付费槽或线程同步。

一次实际Opus调用session23364→976486正常exit0，269522 ms，实际assistant模型metadata为anthropic/claude-opus-5，完整交付三文件补丁。Codex纠正FlintOps命名空间、补两个Ops的完整类实例化、固定context读取的View寿命及文档边界。根全文核头文件及静态夹具；严格C++14主机e6631a→072c35、RV64 45a520→a95ed2均exit0、无诊断。没有链接或运行新程序，原PositionCommit/Collector头未改；原task/RAW/patch、实际结果和最终SHA见[回执](implementation_binding_evidence/opus_receipt_install_terminal_20260920.json)。

上下文比较只核Collector根与外层声明的block/session/center一致；PositionCommit目前没有中心字段，故不得把该比较写成真实跨组件站点身份已验证。实际中心writer须持有并绑定两组件，真实SELECT/POSITION事实、first_success锁存、AUTH、终态交付及实际供给仍待接通。§38数值guest限制保持，不重复盲跑或改保护参数。

根另明确COST_DOMAIN_V1的收件范围：N(u,E)在初次封存时即绑定`{该终点E, 本query中心C}`，合法复制保持完整原信封，实际仍经原N→E→C通道。固定73规定不可变收件范围而非仅单成员，不必新增转发外套格式；仅含E的旧信封不能据E外套扩权。此取舍已写入[成本协议§5](implementation_binding_evidence/QUERY_COST_WIRE_SPEC_20260920.md)及[来源接缝](implementation_binding_evidence/QUERY_COLLECTOR_ADMISSION_BINDING_20260920.md)，未改冻结73。定点确认现B1只有付费参数/返回入口、MemoryAdapter只有普通页权限，实际受保护描述符、合法副本与站点dispatcher仍须实现；不能再用声明式能力代替这个来源缺口。

## 43. 受保护存储后端与实际 guest 字循环（2026-09-20）

新增[pie_auth_memory](implementation/pie_auth_memory/README.md)，将§42的连续存储保护落到已有MemoryAdapter与B1接口。布局明确payload、used、lengths、tails及额外`1+A+ceil(A/16)`字保护表；五段检查包含末字节的可表示性与互不重叠，全部保护表计入真实站点R_aux。普通访问只作固定范围和固定字检查，受保护payload与私有表拒绝读写执行，used/lengths允许分配器读取但禁止改写。tail按最终写值保护对应四位记录，保留同字内其它普通分配的更新；原子操作与成功SC沿B1实际write口检查，失败SC不产生store。

四个C++14 freestanding核函数实现初始化、完整分配claim、同长完整副本及清零后解除保护；无动态分配、数值库或外部memcpy/memset。参数及完整块检查成功后才置Busy并逐字修改，最后Ready；解除保护仍保留实际分配，后续Context释放须正常计费。真实RV64循环必须由原B1执行与跨行续接，不能把host调用或按字虚构单价当成已付执行。可信worker须在普通完整指令边界接管，故障后不伪造Ready；本包仅有该worker前置声明，没有实际worker、AUTH签发或业务来源能力。

本包实际Opus调用在600秒限时结束，exit124、无可用源码，原始记录保留且未重试；代码由Astra/Codex接手。core严格host C++14静态e7ee27、RV64IMA/LP64对象f0a8ba均exit0；未定义符号检查42879f为空，36749b确认四个对运行时参数操作的外部Text符号非空。实际host C++20后端静态17c6f3 exit0，完整实例化真实B1路径。定点核对将tail写掩码检查延至底层Write资格通过后，仅读取一次；未改B1、旧Adapter或Context。源码、调用终态及编译命令见本包README与回执，不能据此声称功能或计费运行通过。

根另备六个真实PageData、32槽Context和手工B1指令的有限native夹具，并独立严格编译/链接。它可检查保护、邻接tail、完整复制擦除、AMO进位及SC最终store，core函数在其中原生执行，不能冒称完整guest核的B1费用验证。最终工件/哈希及30秒具名范围见[有限检查说明](implementation_binding_evidence/AUTH_MEMORY_NATIVE_SCOPE_20260920.md)；该新增程序尚未运行，不扩原两批授权。下一步仍是实际B5 worker/受保护来源和中心业务提交接通；§38数值冷启动供给不足保持，未赋实验参数或启动仿真。

随后用户明确回复“允许此测试及同范围修复复测”，上述待答已结束。根8642ee核待执行SHA仍与具名工件一致，首次实际运行e55253 exit0，输出265项断言通过、stderr为空；无需修复或重复运行。原始日志与哈希见[实际结果](implementation_binding_evidence/AUTH_MEMORY_NATIVE_RESULTS_20260920.md)。该结果推进固定native/手编码B1组件验证，不回改原静态交付回执，也不扩大到后继编译可信kernel、worker或真实AUTH/站点运行。

## 44. 持久可信内核与付费B5执行接缝（2026-09-20）

新增[pie_auth_worker](implementation/pie_auth_worker/README.md)。原普通Machine留在ECALL的ImportWait，持久kernel Machine在同一Memory、同一站点供给上顺序运行，不增加server或并行hart，不免费保存/重建普通寄存器。这里明示采用已有B5服务边界：原ECALL已读a7、清预约并付SYSTEM_EDGE，恢复时只有无Backend访问的NextValue/WriteNextPc两尾；不将ImportWait冒称Retired，也不允许load/store/AMO中途换权限。旧B1和MemoryAdapter未改。

CpuInitializer在已映射Memory上逐字建立额外48字CPU及16字续体，成功334付费步，不加载页；完整Commit后才交唯一对象。普通Backend另拒绝全部kernel code/stack的R/W/X/probe，核与五个arena范围互斥。worker自有5字续体经10步取得/初始化，CPU初始化器仍保留时额外状态合计69字，code/stack/源描述符另计原R_aux。实际GNU11 kernel静态栈128字节，不将此组件事实当实验参数或默认应用容量。

编译kernel启动时通过PULL取六个布局字，此后每请求取operation/first/second三字，实际执行§43四个core循环，再COMPLETE报告a0。所有输入/结果沿原B1付费ABI，worker推进至下一PULL才恢复普通执行；付款不足保留当前阶段和值，成功写不重做。只自动初始化一次，后继仅允许claim/copy/wipe；非法操作编号保留普通ImportWait供外层处理，内核失败或HostUnavailable封住恢复。内核编号不开放为普通AUTH导入，普通结构体不产生来源权限；真实角色准入和AUTH描述符业务仍待接通。

实际Opus一次完整交CpuInitializer两文件，session22442→2576ea exit0、199009ms；Codex修撤权不能回收CPU/覆盖失败，补私有绑定访问器及寿命说明，最终host严格静态66ed56 exit0。root实现kernel/协议/worker，并实际以真实B1、ProtectedBackend、ServerMeter严格host C++20静态集成a75a2d exit0。kernel目标对象f2d598、entry最终430256均exit0；对象为RV64IMA/LP64、无外部运行库helpers、无C扩展，尚未链接或运行。命令、实际SHA与原始Opus归属见[交付记录](implementation_binding_evidence/AUTH_WORKER_STATIC_DELIVERY_20260920.md)。下一步接实际INIT镜像并验证续跑/计费，再接原角色签发和交付；没有以§43新授权执行此包。

## 45. 编译内核固定镜像与双制度检查驱动（2026-09-20）

§44对象已进一步链接成实际固定ELF，非运行通过。新增普通probe真实调用Context构造、分配/释放；六次普通ECALL依次claim源和目标、复制、拒绝非法自复制、wipe目标和源。protected头所在同一tail字的邻接零长度分配随后释放并以5字节请求复用，核四位更新。GNU11 RV64IMA/LP64 ELF严格构建75462f exit0，无未定义符号、重定位、CRT或数值运行库。11个LOAD各一页，普通/内核RX分离，五张arena表32/32/32/2/35字，两个私有用途栈及结果页具名；完整字节SHA及静态符号记录见[有限范围](implementation_binding_evidence/AUTH_WORKER_FINITE_SCOPE_20260920.md)。

一次实际Opus镜像包调用session66664在300秒超时exit124、无可用源码，未重试；Codex完成三文件并保留[原始归属](implementation_binding_evidence/opus_auth_worker_probe_terminal_20260920.json)。两个提取头由Codex绑定实际全文件和全部程序头，严格host静态13d024 exit0，独立W5632/K1024/P11/n11导出INIT期望47860。根编写实际Initializer→CpuInitializer→TrustedAuthWorker/ordinary驱动，完整host C++20 -O2严格链接ad2001→e6dcdb exit0、无诊断，未执行提取器/driver或新guest。

驱动固定两制度各131072行×3组件供给，按真实阶段结束换行，完成后的行空闲；它不是实验参数赋值。额外CPU期望334步、三字请求帧取得/零写6步、6次import比较加18次原B1参数读取24步，其余kernel/普通指令和返回按原实现实际计费。Starved在同一行再调用核无新增费和可见状态变化；部分初始化的页不被审计读取。独立oracle逐请求核payload/metadata和拒绝自复制不改133字arena，完成须精确普通EBREAK及结果同时符合。两制度比较全部映射页/权限、普通寄存器、公开CPU状态、每行actual/unused；不将未暴露的kernel隐藏状态冒称已全量比较。

每行收据包括失败前缀均保留。具名60秒命令与二进制SHA已经具体可审，新增运行尚待明确批准，不重复旧native授权，也不据此改数值guest供给或研究输入。该程序的import17仅是固定夹具入口；无实际AUTH角色签发、中心首次成功writer或站点服务，不能据编译/预期值关闭这些业务缺口。下一步在该有限范围验证真实续跑，同时推进现有Collector/PositionCommit中心writer的具体源接入。

并行已形成一页[中心writer实现顺序](implementation_binding_evidence/CENTER_WRITER_NEXT_IMPLEMENTATION_20260920.md)，限定SELECT发布、POSITION成功和收据安装三入口。首次合法成功即使q不变也在真实提交点锁存，后继副本全费不覆盖；outbox、已发布首责任和不可变事实须同次准备再提交，不能事后补造来源。该页仅施工草案，真实来源及writer实现尚未完成，不新增审查前置。

随后用户明确批准该60秒固定检查及同范围必要修复复测。根a545be核工件SHA与原具名范围一致，首次实际执行87bd97 exit0、stderr为空、无需修复或重跑。两制度均完成全部六请求：镜像INIT47860、CPU334、请求帧6、kernel启动2514、普通Context/指令16058、导入参数24、请求及回传17173，合计actual83969；NATURAL charged83969，STRICT charged393216。每制度27977次Starved重复检查，row28000到达唯一普通EBREAK；全部存储预言、可观察最终状态及逐行actual/unused一致。根319100独立复算完整stdout，确认两份131072行计费均符合固定规则。原始日志/哈希和范围限制见[实际结果](implementation_binding_evidence/AUTH_WORKER_FINITE_RESULTS_20260920.md)，不改先前静态/Opus原回执，也不据此关闭生产AUTH、中心writer、数值启动或规模实验缺口。

## 46. 中心本地请求所有权与首次成功组合提交（2026-09-20）

新增[pie_center_writer](implementation/pie_center_writer/README.md)，在原friend名称CenterCommitBridge下实现真实本地事务；具体[源绑定](implementation_binding_evidence/CENTER_WRITER_BINDING_SPEC_20260920.md)沿固定73的异步通道合同。SELECT私有准备从实际Choice/Action冻结完整身份、几何与精度，按已准入(agent,source)路由核首N票据，调用实际PositionCommit发布准备；同一后继根持有完整不可变请求字节副本、outbox、已用业务身份和Published事实/事件。提交前事实与通道token不可见，提交时先核两根再无异常交换，保留旧根供付费回收。首网络责任在这次本地请求与待办发布成立，并不表示N已执行或可跨站提交N ledger；SELECT不被虚造为Query父job。

POSITION路径核已发布query的source/profile/原请求/完整MOVE及中心接收票据，调用原PositionCommit::prepare_position。首次成功与POSITION同次安装first_success及唯一事件，即使q不变也可成立；后续合法副本不替换事实、不省略实际POSITION路径或费用。接收job保存完整不可变Ticket，同ID仅许同票据重放，且不能碰撞首网络job身份；票据一致性不替代AUTH、样本或生命周期准入。已提交View的实际能力可直接供已有Collector构造和prepare_success消费，收据安装仍复用§42，不另造报价或成功工厂。

不透明ChannelToken持有已发布outbox存储，仅公开业务身份、目的server、票据、publication_row和provenance，没有公开payload接口；按发布行及unsigned-byte job key枚举。严格后继NETWORK资格、实际付费复制及token设施登记仍由真实通道入口承担。本包的生产prepare/commit只向具名但尚未实现的CenterService开放，ChannelTransfer亦仅前置声明；没有测试签发器、authenticated布尔或公共raw资料转能力工厂。它关闭本地事务源码缺口，未关闭生产AUTH/Srv_C槽/真实交付/回收，也未运行服务。

单次实际Opus调用session61343→e79b74在300秒硬限exit124、零源码text delta、无可用patch，未延长或重试；三文件均由Astra/Codex接手。根c40f85/f06d04核完整头的事务/可见性路径，补既有FIFO的发布行/job排序要求，最终60bb14/9fa0cc核该改动及完整无main静态夹具。严格host C++14 c463dc与RV64IMA/LP64 8e4720均exit0、无诊断，覆盖实际FlintOps、无默认/整数构造且移动可抛的声明型Real、完整类和私有POSITION模板显式实例化。原始调用、实际命令与源码哈希保留于[归属回执](implementation_binding_evidence/opus_center_writer_terminal_20260920.json)。此处是静态编译证据，不是业务运行、AUTH来源或大规模仿真通过。

## 47. 独立查询对照和三项消融选择器（2026-09-20）

定点核实现发现原Scheduler只有SRDC及其RR回退，不能直接运行独立RR、COUNT或
三项消融。本轮将研究比较收敛为[结果前登记草案](implementation_binding_evidence/D_SRDC_COMPARISON_BINDING_DRAFT_20260920.md)：共同COST_DOMAIN_V1下的SRDC/RR/COUNT，另分别改工作分母、等待分母或w=1；不交叉扩大矩阵。E0单列，继承主稿配对、Q/E、Hoeffding及失败/未知处理，正式臂和冻结D不被替换。两个候选主比较共同报告，不能结果后择优。

Scheduler已实现六种构造时固定的QueryPolicy，Choice保留实际policy并沿原组合发布，
没有外部拼接动作或运行期换规则。RR直接选稳定agent，不计算SRDC；COUNT逐需求扫
原资源，外国活动owner只要有非原终点资源就计一次，不能用retirable/out代替。
其正分按最早贡献需求加入公共行解平；SRDC原物理时刻解平保持。本轮Index增加
深复制、同需求不可改变的可选joined_row和原endpoint缓存只读接口，真实公共行
仍由生产中心提供，不能从时间猜行。RR/COUNT不维护不用的SRDC关系/out/资源反向图，
也不保留预测历史/报价；共同几何和提交一致性、实际成本协议仍照常承担。

三个消融各只改变指定评分因素，含work-only在内仍要求同一合法正历时报价；
无报价/精度及零历时回退规则不被混入分母消融。完整源码与归属见
[实施记录](implementation_binding_evidence/QUERY_POLICIES_IMPLEMENTATION_20260920.md)。一次实际Opus调用51081在256071ms成功结束c03ebc、exit0，四文件完整交付；Codex补齐独立RR必要工作边界、夹具输入和决策区分，根编写Index接缝。

最终selector严格host65c122、RV64d9ed1c静态通过；根另将PositionCommit、收据安装、
中心writer实际合同联合编译，host2e17e3→fe7deb、RV6461f440→ba1bb2均exit0。
原query/position两份原样夹具在原授权内重链并运行153486/80fdf3，均exit0，
分别输出具名passed。先完成Index时的独立回归及哈希另保存在
[索引记录](implementation_binding_evidence/QUERY_INDEX_POLICY_PREPARATION_20260920.md)，不覆盖此前证据。

新的12组policies_native仅编译/链接；其独立分支运行尚待具体授权，不据旧默认
夹具通过称全部新策略已运行。生产AUTH、CenterService、通道、真实付费服务和
原MOVE闭环仍未接通；本节完成可比较规则的源码与静态接入，未完成规模实验准备。

随后用户明确批准具名12组固定native检查及同范围必要修复复测。根2fead7独立核
最终源码/二进制SHA与送审范围一致，首次实际执行6e76a6、exit0，输出
`QUERY policy selector fixtures: passed`；无需运行后修复或重跑。三分母和w=1
的手算选择区分均通过，仍只是人工组件输入的机制证据。原始执行记录、哈希和
非可达评分输入的范围见[实际结果](implementation_binding_evidence/QUERY_POLICIES_NATIVE_RESULTS_20260920.md)，
不修改Opus交付时“未运行”的原始终态回执。完整业务与规模证据仍未关闭。

## 48. 实际账本终态导出与私有状态存储接缝（2026-09-20）

新增[pie_query_cost_export](implementation/pie_query_cost_export/README.md)，固定绑定
一个LocalJobLedger，只从其已提交TerminalPrepared根保留View并调用真实wire::encode。
准备同时持有原ledger的发布token，但不提前提交。外层封存/outbox完成准备并全根预检
后，才在同一次实际发布中提交账本部分。规范字节自持不可变；byte_count、word_count
和body_word给出确切长度及低字节先排的RV64逐字来源，原wire字段大端编码保持。
移后读拒绝；stale/foreign/已消费token不能提交；成功后保留正文及旧根供付费回收。
缓存正文不是封存信封，不授权新AUTH身份或替代原信封重放。

唯一一次实际Opus调用45997→f00289 exit0完整交付三文件。Codex将其noexcept构造器
中的动态分配改为直接持有已有可无异常移动的ledger token，修正源码来源及寿命说明，
并恢复被嵌套代码围栏截断提取的完整README；原始输出不改。真实host07e559与
RV64b77011严格C++14静态编译均exit0，无诊断。根8503ef全文核提交与逐字访问实现；
本轮未运行该新组件，静态检查不能替代业务计费或AUTH验证。

现有worker另增加默认关闭的private_data跨度，启用时与code/stack及五段arena严格
分离，普通fetch/read/write/probe统一拒访。host实际组合a22ed8与原样driver兼容
编译cbe1c8均exit0；旧具名ELF、driver二进制和运行日志保持，未复写原运行证据。
这只落实后继kernel私有序号/封存状态的保护位置，没有实现该状态机或新INIT。

具体[接缝记录](implementation_binding_evidence/COST_TERMINAL_EXPORT_BINDING_20260920.md)
保留实现边界：账本是结构组件，真实站点仍须提供真正计费事件及角色绑定；导出、编码、
封存和交付全部计入独立ReceiptAccounting，不回填Query造成自计递归。下一实现直接接
生产COST封存入口和原付费通道，再接原MOVE闭环；不新开完整审查或扩大实验运行范围。

## 49. COST本地封存内核与付费worker协议接入（2026-09-20）

新增[pie_auth_cost](implementation/pie_auth_cost/README.md)，将§48的私有状态位置落实为
固定context、有限不回绕序号及每head的Empty/Building/Sealed状态。封存从同一Memory
的真实source读正文，精确核frame/source/target分配及分离、站点前缀与context；先消耗
序号，置Building后实际保护和逐字写完整信封，最后置Sealed。MAX只用一次；后续返回
IdExhausted。专用Copy保留原完整身份，不签发新序号；普通Claim/Copy不能制造Sealed，
Wipe先撤状态再擦正文，实际Context后续释放。可信状态损坏为InvariantBroken并停止，
不按普通拒绝继续。当前verify_local只核本站原件/同arena副本，不等于跨站接收能力。

唯一一次实际Opus调用64907→1a2f7e，exit0、184959ms，完整交付core/静态夹具/README；
原始流与终态保留。Codex修独立context字符串padding、短保护块读取长度守卫和损坏
状态分类，最终host31af79、RV6463f481均exit0。根实现实际guest kernel及对象脚本，
Codex接入worker九字布局、操作4–6和付费状态判断；默认旧六字布局/操作保持。实际
worker组合73065c及原样旧driver静态b12b3e→184052均exit0，未覆盖旧ELF/运行日志。

根首轮对象编译发现初始化函数ADL歧义后改本地函数名；最终c06409 exit0，RV64IMA/
LP64、ELF flags0、无未定义辅助函数。最终对象内部调用无递归，全部静态栈帧和为
1264字节，可作保守调用链上界；不沿用旧kernel的128字节，也不把此数当实测峰值。
新kernel未链接成站点镜像、未执行，启用CostKernelBinding须由具体镜像绑定器给出
实际context及所需私有栈。任意调用者填写绑定值或普通frame不构成角色/job来源证明。

新七组固定native夹具调用真实Context/LocalJobLedger/LocalTerminalExport，检查
109字节正文、34字封装、普通复制不能制造身份、擦除复用、Building及序号耗尽等。
最终严格链接f53e6d exit0，根37225f复核哈希；[工件/命令](implementation_binding_evidence/AUTH_COST_NATIVE_SCOPE_20260920.md)
已备，尚未执行，已请求该新增具名范围授权。不延用原policies_native或旧worker授权。
该fixture不检验B1付费执行、实际暂停、真实站点准入或发布；完整生产来源、付费context
安装、N→E→C原通道/跨站验收及原MOVE闭环仍待接通。具体工件、归属和静态证据见
[封存绑定记录](implementation_binding_evidence/AUTH_COST_KERNEL_BINDING_20260920.md)。

随后用户明确允许该七组固定native检查及同范围必要修复复测，每次最多30秒。
根082a52再次核core/测试源码/产物SHA与具名范围完全一致，首次执行758559 exit0，
完整合并输出为`COST native: 7 finite component groups passed`。没有运行后修复
或重跑；[原始完整回执与结果](implementation_binding_evidence/AUTH_COST_NATIVE_RESULTS_20260920.md)
已归档。验证覆盖真实Context分配、真实账本/codec正文及本地core状态行为；没有执行
新RV64 kernel或站点业务，不能将其表述为B1计费、生产来源或跨站交付已经通过。

下一接入点经具名源码确认：B1/worker已有实际执行、付费ABI及B5暂停，但没有生产
公开业务import dispatcher；CenterService/ChannelTransfer仍为前置声明，ServerMeter
只提供当前行扣费，不选择job或授发布机会。旧fixture的import17不进入生产权限表。
继续实现窄站点当前job拥有者及COST入口，绑定真实登记镜像/独占Memory与worker、
当前账本和原公共机会；guest执行实际导出/封存，outbox发布前保留Prepared。源码建设
不等待另一个整体审查，不以普通JobBinding/角色枚举补造缺失的真实来源。

## 50. 真实guest终态准备、ECALL与付费参数桥（2026-09-20）

新增[pie_station_cost](implementation/pie_station_cost/README.md)的GuestExportJob，固定
一个真实ledger/exporter与Context，实际编码、分配正文/完整目标/三字frame并逐字
打包。prepare不提前发布，成功后仍持Prepared、正文和旧根。普通guest无权读取
protection表；根取消不必要的跨块GC原子要求，不新增检查口或权限。显式清理按
target→frame→source执行，先核可读完整分配，每次真实Context.release成功立即
撤销该块所有权。已交内核目标先由真实Wipe处理或交外部owner；方法名/phase不
证明Free，实际B1 metadata写仍由原保护后端逐步拒绝非法释放。

一次真实Opus调用e6610e/session37884→05be39，exit0、179138ms、claude-opus-5，
三文件完整交付。Codex修Status::ok命名和prepare失败态，移除bool驱动的伪生命周期
示例与成功路径静态诊断缓冲；host a8bc7a、RV64对象efb221→a21e2f均exit0。
原始task/RAW/complete与终态保留，最后注释/README调整单列，不伪称另一次运行。

根另写实际guest Seal/Wipe ECALL：操作a0=4/3，a1取原job的frame/target，a2=0，
a7由真实登记程序绑定提供，不沿用fixture17；Seal先记录Dispatched再ECALL，暂停
保持CPU和job原位，返回a0仍须实际guest判断。CostCallBridge逐字付费取得/清零
三个续体字，沿真实B1 ABI读A0/A1/A2，只在读齐后交原worker；不从host审计寄存器
读参或免费调用exporter。已读参数跨Starved保留，运行期源不可变，实际owner须保持
借用寿命。Complete只是调用返回，Rejected仍须原付费拒绝处理，不当作Seal成功。

host实际worker/meter组合89f4b1 exit0；根calls对象c473a8及两guest对象ld -r组合
6b5f3c均exit0。d8509e核ELF64/RISC-V REL、flags0；b325dd核两条实际ECALL与前置
寄存器/标记写。对象仍含真实标准C++/Context/unwind依赖，没有入口或LOAD，不是
已链接站点镜像；未运行新程序，不借旧七组native授权运行这些guest路径。

具体源码、命令、哈希及[后继实施记录](implementation_binding_evidence/STATION_COST_GUEST_BINDING_20260920.md)
已保留。本节关闭真实导出和普通guest→kernel传参的源码缺口；StationJobOwner、
实际镜像/当前job准入、原公共供给/发布调度、业务费用/责任事件挂接、保护块outbox
及原通道仍待接通。下一包直接贯通这些实际入口，再作完整集成，不增加一轮整体审查
或拿新的零散测试数量解释大规模实验资格。

## 51. 执行拥有者与上下文INIT组合（2026-09-20）

新增CostExecutionOwner，在同一稳定生命周期内持有不可变镜像、Memory、两个
初始化器、普通CPU、可信worker及参数桥。实际step依次完成原INIT和交接，再经
worker执行普通指令；import读取、登记号读取和比较分别付费。匹配时交原bridge，
未知import保持待处理，拒绝沿既有付费路径执行。异常或撤销后停止推进，保留原状态。
该组件完成执行对象拥有与驱动，不替代真实站点当前job、角色及供给调度。

上下文工厂按现有COST格式生成Region，逻辑状态为4+A+C，整页映射和尾部零写仍由
原Initializer取得并计费。组合夹具将worker.private_data绑定逻辑state.words，
将整页region.words保留给实际INIT，避免两种长度混用；所有输入由调用者显式提供。

owner严格host C++20检查a908d5、上下文2c52f5均exit0。组合检查ff0e2b最初因命令
漏include路径失败，补齐路径后68ab83 exit0，无源码修改；没有链接或运行新路径。
根定点核源码，另一路针对移交、借用、付费及import状态核对未发现具体实现错误。
唯一Opus调用在1210ms后API402/exit1，零token、无源码；本包为Astra/Codex实现，
原始失败与终态独立保留，不重试或改变路由。

具体接口见implementation/pie_station_cost/EXECUTION_OWNER.md及CONTEXT_IMAGE.md，
组合夹具为checks/compile_context_owner.cpp；这些源码和原始回执仍保留本地。
owner头SHA256为967d41895e5b4032ba26f85fe8feafb8841e3dfb9d8cd39e99b0099aa326a82d，
上下文头为aa6a0b6d406ce3b86f5fe947f494ecd313185c2c2e78cb17e44536bd668a80b7。
下一步集中接站点/job、发布及通道，形成POSITION→退休→继续执行和异步成本回传
的完整业务流程。已有问题与方法不重开全面审查，准备工作以完整闭环、必要联合
验证、输入与参数绑定收束；当前尚不能据静态组合声称规模运行已经具备条件。

## 52. 首轮原生机制闭环与实际B1工作量反馈（2026-09-21）

用户将目标收束为先取得最小原生闭环，再总结、优化并交接完整计费链。
新增implementation/pie_minimal_loop，两份程序均Astra/Codex实现，未再调用Opus。
原生闭环复用真实ReferenceController、PositionNumeric、Geometry、PositionCommit
和Scheduler。非零足迹/误差盒实际参加mask计算；观测只由冻结控制快照计算，不收
手填lower。无报价时SRDC合法RR，不制造用于正分的费用输入。

严格链接0e9b2a→fb87ed exit0；根首跑6465a7 exit0。10条JSON事件显示后车B先受阻
静止，查询A后q由0推进到2，实际退休cell-1/cell-2；已提交owner允许B获cap/RUN，
下一查询选B，最终两原MOVE终点关闭且无活动动作/需求。这是固定原生机制运行，
不认证AUTH、完整世界/任务服务或任何吞吐优势。

费用反馈程序用真实B1 ADDI跨行执行产生AttributionLane段，经LocalJobLedger的
TerminalPrepared、实际导出/codec与ReceiptBuilder送入Scheduler。初次构建缺FLINT
生成头路径，修正后链接523fa8→b327c3成功；首跑6d728f因诊断owner责任键错误
被真实Index拒绝，保留原失败。仅将fixture responsibility改成原action键，没有
放宽旧组件。最终重链338be8→9ce555、复测c2bc27均exit0。

NATURAL/STRICT各三个负载actual21/56/7、总84步，19段、12条退休指令、16次暂停；
收费分别84/95、未用供给11，下一选择A→B。几何/历史/成功时间属于数学诊断输入，
原生ledger/codec/selector及INIT未计入该B1段，Collector/AUTH未接通；不将此当
整次查询费用或与原生控制路径合称一条完整费用业务链。

原始工具输出分别保存在本地implementation_binding_evidence下的
minimal_native_loop_run_20260921.json、b1_cost_feedback_first_run_20260921.json及
b1_cost_feedback_final_run_20260921.json。最终源/产物SHA、具体复现命令、优化方案
及可复制话术见本地NEXT_CODEX_HANDOFF_20260921.md；主稿既有修改与冻结证据保留。
下一步只补固定业务链的站点/job、费用SOURCE及终态交付来源，复用既有组件，
先量首轮/续轮真实成本再做小规模同口径对照，不增加全面重审或通用框架前置。

## 53. 固定三站点COST接入及实际Opus核账交付（2026-09-21）

接续§52，只围绕固定业务链补接缝。新增pie_station_query，复用原owner、worker、
AttributionLane、ledger/export/codec、COST kernel和Collector类型，没有重启整体审查。
ClosedSegmentSource只接收绑定lane真实close_slice所得段，有限FIFO不能插入手造段；
付费SOURCE41经原B5参数读写送入guest，guest核job/制度后提交原账本，再确认源段。

实际导出44先通过可信worker重新核封存，再付费取得并完整复制独立opaque envelope。
原guest账本发布完成且Wipe/release后才放行到通道。两段付费完整复制保留N及{E,C}，
E在真实guest验证转发身份，C经真实SOURCE45与parser/codec构造AdmittedTerminal；
没有host解码正文后直接制造可信Collector输入。原AUTH serial保持私有。
CenterService另接不可变当前job、私有SELECT/POSITION准备根和严格后继发布机会；
其实际公共机会SOURCE、生产请求/POSITION AUTH仍未实现，不能由结构体冒称存在。

固定N/E/C镜像均为带真实入口、构造器、分配器和TLS的静态RV64产物，分别绑定实际
Memory、INIT和worker。付费检查点驱动同站持久生命周期内两轮，INIT不逐轮重建。
内核私有helper用独立命名空间避免COMDAT落入普通代码；worker私有区绑定逻辑
4+A+C长度，INIT仍覆盖整页。最终三镜像与真实宿主驱动严格静态链接通过；根最终
驱动编译6121bd/session35434→efeed9 exit0，没有启动新二进制。

产物SHA256：N为bb911d881db10d396f4faecff083202597e354d78afa55917962e20e5a931dc5；
E为dc9dc5941b21ead8f0937c9c31fa9d80aa81f306858633b9d966b90b0d1ec2bd；
C为8db83a291cce18d3e6835c1f569d52747eeefcab7513a878b7dad813e52ac9f2；
宿主驱动为0e8dd145130b58cacfa3bc54ed7e08f27d0cf91e280daa2975fcb0d694307979。
固定加载器仅接受实际派生并核SHA/ELF header一致的镜像，未读研究输入。

用户随后要求更多明确任务交Claude Opus。本次新核账任务04e93a/session73189→
e273f3实际exit0，187783ms、一次turn、完整Python源码；CLI modelUsage报告
claude-opus-5。无工具权限，未重启旧402任务或修改共享路由。根接入并修正无效行
污染失败前缀的顺序、补两轮实际Query段要求；57271f AST静态解析通过。它只独立
核对一个显式新日志的逐段算术、站点汇总及顺序，不能证明AUTH或查询收益。原流、
正文、终态和混合交付归属见本地OPUS_COST_CHAIN_AUDITOR_RECEIPT_20260921.md。

源码及具体边界见本地implementation/pie_station_query/README.md和
implementation_binding_evidence/FIXED_COST_CHAIN_SCOPE_20260921.md。用户对已做成的
300秒/两制度各两轮候选明确回复“先只完成实现和静态检查”。因此本轮无新guest
执行或核账运行，没有成本数值、Collector结算/新报价安装、完整POSITION查询或
吞吐结果。人工负载只为费用通道接入，运输对象仍存活，host析构不冒作付费GC。
继续补生产请求/POSITION、公共发布和完整责任家族；本次不是完整业务链验收通过。

## 54. 通信延迟的定点文献启示（2026-09-21）

按用户请求由单一子任务核Robust MADER的RA-L作者终稿及官方代码。RA-L 2024，
9(2):1476–1483，DOI 10.1109/LRA.2023.3342561。Fig.1报告六机mesh平均49.8ms、
最大483ms；Fig.7(a)为实验1–22的汇集直方图，不另造单次六机飞行的样本数量。
III-A/Table VI和Fig.6明确仿真外加0/50/100/200/300ms固定档延迟，不能写作逐包
随机抽样。实际收到消息的时延另受调度/计算影响。官方代码所测接收时间减消息
生成时间属于单向应用消息年龄；缺论文运行commit和时钟校准证据，不改称RTT。

对本研究的启示是另设外生通信延迟因素，先保留无额外注入基线，再做固定档敏感性，
随机分布作为本研究明示扩展。内生查询服务/排队与外生时延分开记录；同规则对照
使用按消息/通道身份对应的共同外生条件，避免按调用次数抽样使不同策略不可比。
仍按原CAPTURE/MOVE版本与严格空间条件释放；已观测最大值不充当确定安全上界，
不直接搬论文毫秒值给T_delay或其它保护参数。当前只记设计启示，未生成RNG/输入。
这不是新的完整文献审查。[作者终稿](https://arxiv.org/pdf/2303.06222v6)、
[官方实现](https://github.com/mit-acl/rmader/blob/master/rmader/src/rmader_ros.cpp)。

## 55. 完整查询的证据、中心结算与发布接线（2026-09-21）

接续§53固定COST工件，用户“只实现和静态检查”的限制持续有效。本次没有运行
新guest/驱动、生成研究输入或随机延迟、赋保护参数。新代码尚未组成完整查询ELF。

CenterService新增实际终态SOURCE准入到Collector的准备，以及原bridge Position根上
的ReceiptInstallation准备/提交；根事实来自实际已发布查询及已锁存FirstSuccess。
提交前后调用同一真实发布进口，旧根保留到付费清理。公开行必须严格后继，物理
时刻允许相等，遵循原机会次序。PublicationSource绑定实际job、原行和供给，先核
已登记不可变指令图的整段可负担性，再逐条B1收费并在同一行结束发布。最长路径
守卫不作实际费用，也未证明所有供给紧张情形下的最早发布等价；真实查询ELF与
有限指令图仍待登记，不能由当前头文件关闭该缺口。

新增pie_query_evidence：实际选择导出请求、原控制器快照生成精确POSITION证书、
真实worker/kernel封存与验证、付费导出及接收SOURCE、guest准入。CAPTURE机会线
格式和私有准入已有实现，但实际原子采样与公共世界时刻/控制根绑定仍待固定驱动。
没有以外部下界或host解码制造证据。现有窄线格式仅接受可精确编码的有理数cap；
不对非有理值近似或填默认值。

根定位中心请求发往E而本地费用终态发往C的上下文冲突，后继实现原INIT一次性
安装两个固定域，发行者身份一致、收件范围独立；新kernel共享唯一serial，分别
核域并联合撤销头状态。逻辑私有区8+2A+C+E与INIT页补零分开，layout SOURCE为
十二字。旧默认COST域及旧make_context_region保留；新kernel代码/栈需实际登记，
不得沿用旧九字kernel配置后宣称完整AUTH已绑定。

两次新Claude Opus调用实际exit0、完整交付：发布guest进口baf9d7/session58535→
b8fc65，47395ms；owner证据进口路由d12ab4/session90153→9fa88a，148463ms。
均为一次turn，CLI modelUsage报告claude-opus-5。根保留原正文/原流，并补发布结束
进口与准确收费说明；owner路由使用实际worker的OperationComplete状态，不修改
worker来迎合提示中的错误状态名。跨模块中心事务、发布SOURCE和双域实现由
Codex完成，混合归属及SHA见本地FULL_QUERY_IMPLEMENTATION_PROGRESS_20260921.md。

证据包严格RV64静态编译/可重定位链接通过，kernel无未解析符号。根将真实证书、
终态/收据、PublicationSource实际worker模板及双域INIT→CostExecutionOwner接法
纳入原组合静态入口，最后f8f525/session54743→7bf5e0 exit0；没有执行程序。
query_kernel.o SHA为b06f0f6c54634d69072057d3d69f6202b9eca34ec5fcf2038c501b0e428385b6；
center_query_bindings.o为c42e4f6dbaeccfc2859ba523d4243d349293a9bea9ef5b15472022f39b800472。
本轮主稿与固定73/R1–R4哈希均保持接续前值，§53旧固定COST工件未覆盖。

当前仍在完整查询集成阶段。剩余实物为新ELF/固定驱动和真实发布图登记、原子
CAPTURE/物理推进、付费消息复制与业务child责任发布、全部Compute/Publication
段及尾部清理进账，再由同一查询的收据驱动后续选择。之后量首轮/续轮真实成本
并开展同口径小规模对照，落实既定输入/参数/运行绑定后扩量。既无完整查询运行
耗时，也无稳态吞吐，当前不报完成百分比或剩余天数，不重开全面审查。

## 56. 实际站点执行器、物理CAPTURE与中心业务顺序（2026-09-21）

接续§55，仍只实现及静态检查。FixedQueryStation已接原owner、真实当前job、
同一Compute lane、固定guest检查点及实际PublicationSource登记。owner支持多个
独立关闭段SOURCE，发布准备行取实际关闭的计算段；Query的计算/发布费用可从
各自来源进入同账本，SOURCE读取限定ReceiptAccounting。唯一world驱动仍须提供
原公开行及原供给；station不内部扩表，也不代替原世界时间推进。

中心outbox改为保留实际封存请求exporter，实际token经ChannelTransfer调用同一
worker导出和Wipe。请求字段核实际选择/行动/精度/几何；C请求出站限Selection，
E POSITION和N转发限Query。N两个方向完整复制原opaque envelope、付费回收原件，
再在同Query lane逐步启动SOURCE至Idle；不读取接收者正文。对外放行必须已有
真实发布且guest到达后继检查点。实际child责任预留/发布业务体仍待接入，不能
由固定job标签或检查点冒充已闭合的责任家族。

FixedCaptureWorld成为实际ReferenceController所有者，按原公开事件执行旧边界
优先推进并保留实际发生的命令。SOURCE在原行原子pin当前不可变物理根，后续历史
读取和guest精确重建分别付费，guest暂停不自行冻结世界。pin可负担性界包括
十四项实际B5原语及原ECALL返回尾段，按实际步骤收费，不预付退款。E SOURCE与
实际当前Query job/Compute lane绑定。原始系数、公开时刻及控制参数限精确有理
profile，内部代数状态照旧精确；完整世界驱动和最终E镜像登记仍未完成。

CenterQueryFlow沿同一bridge串起真实选择/封存/请求发布/运输、POSITION准入和
提交、Query输入清理、终态Collector、原根收据安装及下一choose。POSITION可先
释放/继续MOVE，费用家族异步结算，不人为保证下一对象变化。发布不可能失败
在RV64改为实际EBREAK有限出口，图检查保留全部分支及真实GuestFault收费前缀；
native保持terminate，LocalJobLedger旧base延至付费清理。实际完整ELF的间接目标、
普通返回分支及紧供给下最早发布等价仍需具体绑定，不能由此声明已验证。

新Opus Copy任务首次58ae5d/session13486→f4332d exit1，FailedToOpenSocket，
原流保留；经原命令授权重试c9d576/session60681→0ebbb0 exit0，65808ms、1 turn，
CLI报告claude-opus-5，正文完整。根核原Source未变后接入，再独立补Reclaim与
实际调用链；其他Codex子任务不归为Opus。原始正文、失败/成功流、哈希及细节
见本机FULL_QUERY_STATION_SUCCESSOR_20260921.md。

复用原组合编译入口，纳入实际站点全部公共API、owner/CAPTURE/复制/回收及
中心证书/Collector/收据路径。最终0fda28/session69889→8156c2 exit0，GNU11
host C++14/C++20与RV64严格静态编译通过，没有执行新guest/测试/驱动。
station头SHA为09ebdb7949c7fdf89dc3434052bc2d52047548fa1d88af36b468cf151de3bf6c；
center_query_bindings.o为87bcb16ca537a4cc8bd89b48b3352edfe9a5463741d295e61d33683137e558df。
主稿与冻结73/R1–R4、§53旧四份COST工件哈希均未变。

下一步直接装配C/N/E完整guest、新ELF/发布图、固定脚本和唯一world驱动，接实际
child发布、原MOVE接续、全部费用与末尾回收，再验收真实报价对后继选择的使用。
当前最终COST输入SOURCE仍有保留对象，host析构不计为付费GC。完整查询仍未运行，
尚无真实单次成本、等待改善或吞吐结果。完整查询验收→实测首轮/续轮成本→
小规模同口径对照及既定实验绑定，仍是扩量前的三道关；不新增全面审查或孤立
测试前置，不给无实测依据的百分比/日期。输入、参数和运行边界保持不变。

## 57. 三完整查询guest与实际ELF静态交付；新增开题文献任务

2026-09-21。C/N/E实际完整业务体及固定profile已链接为三份新RV64 ELF；没有执行
guest、driver或测试。详细字节和静态资格见本机
`implementation_binding_evidence/FULL_QUERY_ELF_STATIC_20260921.md`。

C沿真实CenterQueryFlow接请求选择/封存、POSITION准入和原根提交；在已提交
owner状态上准备原B需求的释放与cap，随后从真实movement发布见证停到world确认。
Query输入清理后，真实关闭段SOURCE进入账本，RA准备/封存COST，实际导出先于
终态发布，再Wipe/release。四个真实终态接Collector，收据装入原Position根，再
读取下一次choose；没有人为指定后继对象。E完整核请求后冻结实际CAPTURE来源、
构造证书并发布；N两方向保留原opaque消息，业务child发布与引用转交用同一
账本事务。终态运输新增按字付费RA Reclaim，host析构不算收费回收。

实际Claude Opus一次完整交付N双向业务体，exit0、CLI报告claude-opus-5，原流、
任务和终态见本机`opus_full_network_*_20260921.*`；Codex只改共享finish次序
注释并负责站点movement/reclaim、其余角色及最终集成。首次Ticket构造编译失败
与修正后日志分开保留。三ELF实际链接成功，C随后针对Publication SOURCE非零
异常出口修复重编重链，不抹去旧产物时点。

新loader固定实际SHA、ELF、TLS、INIT、两个context端点和12字kernel布局，显式
要求传入新kernel栈界；GNU11 C++20严格host静态组合通过。三ELF私有代码段逐字
一致；19函数/4391指令实际控制转移闭包检查通过，唯一非return间接分支按实际
0..9 guard与10目标只读表解析。保守栈界为1408 bytes，小于4096-byte实际预留；
来自新双域kernel的调用图和本批.su，而非沿用旧COST默认界。

后继仍需唯一world驱动、固定站点脚本/供给行，以及普通guest从Publication
SOURCE到finish的真实图登记。私有kernel闭包不等于全业务发表图资格；实际B
原MOVE的cap/RUN、全费用和最终GC仍没有运行验收。没有完整查询成本或吞吐数据，
不修改任何保护输入/参数和只实现静态检查的边界。

用户随后明确新增开题文献综述：有界空间跟踪误差约20篇，中心信息滞后及付费
查询约20篇，另查两类交叉；以Introduction/Problem Formulation/Conclusion/Future
分析问题、机制理由和局限，判断本课题价值。全文、阅读卡和综述写到授权新建
桌面独立目录；旧文献备份只读、论文不入公共Git。当前开始执行，不把候选数量
写成已经读完。本轮实现停在上述真实静态交付点，完整查询目标没有完成。

## 58. 开题文献综述及55个独立工作桌面交付

2026-09-21。已完成用户新增的定向综述：A空间误差/安全执行20篇，B信息滞后/
有成本更新20篇，C误差与延迟交叉及边界对照8篇，D最邻近MAPF执行7篇。A含明确
标注的理论基础、概率及运动学对照；C含Robust MADER边界工作，不冒称所有条目
均给出确定性空间误差与网络延迟联合保证。发表信息与实际阅读版本分别记录。

本机桌面`MAPF_开题文献综述_20260921`保存55份选定全文（1029页，162613674字节）、
提取文本和逐篇阅读卡；另存不同版本不重复计数。指定章节为Introduction、
Problem Formulation、Conclusion、Future，没有独立未来工作章节时如实说明。
作者后续方向、阅读者局限判断和本研究启示分列，未宣称逐页核完全部证明。
总索引、CSV、BibTeX、综合综述Word与55篇阅读卡Word均已生成；有效PDF、唯一
ID/规范题名/已给DOI、无重复选定PDF哈希、阅读卡/必填字段和Word包完整性已核。

综合判断为有条件值得继续，而非方法已经有效。B09/B10/B15已研究付费观测或
中心选择对象，B12已联合噪声、时延和丢包；A17/A19、D02/D07分别限制受扰多机、
减少安全更新、主动同步和共享空间互斥方面的宽泛新颖性。建议贡献聚焦可认证
资源退出、阻塞依赖中的非可加信息收益及真实查询成本，在同预算比较中检验。
高度相关POD候选尚未取得全文，单独保留检索入口与不确定性，不计入55篇；这份
综述不是穷尽查新，不据此声称首次，也不改冻结正式比较臂或赋实验参数。

B组4批真实tool-less Claude Opus调用均成功，CLI报告claude-opus-5；受约束的
原文章节、原件及终态在新文献目录保留。Codex核对关键公式/结论与版本，修正
期望预算和逐路径硬预算等混淆，再完成综合归档；其他小组按实际Codex归属。
旧文献备份只读，论文全文与本地阅读包不入公开Git；主稿和冻结73/R1–R4保留。
代码仍停在§57静态交付，未运行新guest/driver/实验，完整查询目标尚未完成。

## 59. 唯一世界驱动、固定站点脚本及真实普通发布图静态装配

2026-09-21。接回完整查询目标，新增full_query_driver.cpp和C/N/E分别20/12/14项
固定脚本，复用三SHA完整ELF、双域loader、actual owner/job/来源与通道。E在原
row201真实pin世界当前A根；C提交POSITION与原B需求的movement发布后，驱动才
执行同一B控制器的cap/RUN。四份COST中N两份经过E原issuer转发，C全部付费清退后
沿原根Collector/Receipt/下一choose；不免费解码消息或把宿主日志总和作为报价。

17个普通发布进口复用8张实际ELF图。全部条件两边、真实EBREAK与两个C finish
虚调用按唯一具体Port的只读槽登记；未知目标或循环拒绝。原B1方法体只加constexpr
作静态编译数据后提取费用界，.o无可执行section、没有创建Machine/Plan或执行。
最大Plan界1240，reserved guard1253，包含前9步准入的整行阈值1262；固定每行
1048576足以覆盖该发布guard。一般紧供给下最早准入等价和全Query可负担性未证明。

构建脚本由一次真实Claude Opus完整交付（claude-opus-5），根补发布图头与脚本
头的显式依赖检查。严格GNU11 C++20/O2组合链接先715b12 exit0，根增添成功出口
Query SOURCE全部导入检查后4c3d85 exit0。新host产物
`/tmp/pie_full_query_driver_20260921` SHA为
`d5a999531b82df135da2333f187b5ffd50b834bf385625bf9a73e36843ba7047`。

源码固定启动窗口与后继单行，沿旧诊断每行容量，不按失败加供给。当前没有完整
Compute/冷缓存可负担性证据；原数值诊断的高成本限制必须继续保留。失败输出保留
真实已付前缀，存在SOURCE pin时不免费析构冒称GC。新成功检查从未执行，完整
查询仍未验证。详情见本机FULL_QUERY_WORLD_STATIC_20260921.md及
FULL_QUERY_PUBLICATION_STATIC_20260921.md。主稿/冻结证据和只静态边界不变。

用户另追问文献对选题的修正，桌面已补《课题修正与导师汇报》：保留问题方向，
收紧贡献为安全释放证据、阻塞依赖与实际查询净收益。随后用户明确要求科研导师
技能独立判断SCI二区/三区创新与工作量，已交付桌面
`00_综述与开题/SCI二区三区_科研导师独立评估.md`。报告结合当前SRDC合同与方法
补充、十张关键近邻卡和B15/D02原文作定点评估，不重开固定73全面审查。

判断为工程工作量充分、目前二区/三区方法投稿证据不足；补齐完整核账与公平
比较后三区有合理潜力，二区仍需更强机制解释及推广依据，不作录用承诺。重点
保留启发式乘积分母、持续正分饥饿和全候选动态评分扫描的边界；B1实路径微步
不自动代表无线时延/能耗。报告费即使不入报价也必须进总账，冷热成本同生命周期
比较，两种费用制度不是独立随机样本。首要待检验的是证据滞后是否真为瓶颈、
计完整成本后选择有无净价值、效果是否仅依赖特殊昂贵模型。没有新增代码/参数
变更、实验运行或重复孤立测试来替代这些主结果。

## 60. 完整查询执行范围、有限冷缓存判定与核账接续

2026-09-21。保持§59三镜像、宿主、供给行、原物理profile和全部保护边界。
已将真实C→N→E→N→C查询、原B继续、四终态付费清理、Collector/Receipt及下一
choose的联合验收写入本机`FULL_QUERY_CHAIN_SCOPE_20260921.md`。该范围为每
制度一次完整查询，不沿用COST-only两轮人工工作，也没有执行授权或新运行。

定点静态检查本批C ELF首个`number(-1,2)`实际走小整数/二次幂分母分支；
`number(±1,20)`的128位包围除法使用limb数组，不能从工作精度推出fmpz大整数
缓存必经。首触发仍UNKNOWN；没有继续扩展全部几何/代数调用图。另一方面已从
当前C ELF独立核实条件下界：首次冷分支若成功完成，4064次16字节GMP申请每次
至少扫描EH持久前缀4544个候选，每次used-load真实收费11步，至少203134976步，
超过C setup的51×1048576=53477376步。不得把条件下界转成此查询必失败/可通过，
也不套旧ELF地址；详见本机`FULL_QUERY_NUMERIC_COLD_CACHE_STATIC_20260921.md`。

另核后继报价：scored先为同profile/精度候选读取合法收据并设置cost_delay，
再评估依赖收益；cursor_choice复制已经填充的Score。本固定A/B均共享p及同精度，
删除唯一extend-B需求后合法RR回退仍可保留报价。因此无需改算法、制造新阻塞或
强制选择对象来通过既有后继报价断言；这只是源码路径证据，未运行该断言。

用户在本轮明确科研导师评估须同时考虑中科院与JCR。桌面原独立报告已由根补充
两种口径，分别标注认可年份、大/小类或JIF学科类别，不按相同区号换算、不自动
要求两套同时满足；未给未经核定的期刊分区。该澄清不改变完整查询目标和运行边界。

原`audit_cost_chain.py`增加显式`--full-query`模式，复用原逐行reader、JSON/
字段/u64校验及bucket算术，按当前driver的真实窗口与行/job/supply顺序核账；
重算四类账户和job_total，检查两制度、C/N/E诊断、完整/失败标志并保留有效前缀。
日志未记录的guest检查点不推断，Finish不冒称CPU halt；host秒仅为元数据。
单次实际Opus600秒超时（exec62180→b7eb5d、exit124）无可用源码，未重试；
Codex直接完成增量，根定点核原driver顺序及owner枚举，随后澄清模块说明。
最终AST检查2abd75通过，旧COST主体字节及默认imports/constants/helpers/
ChainAuditor/HANDLERS/入口守卫AST保持；没有执行审计器、guest或测试，没有
生成示例运行日志。最终源码SHA256
`24d59ce3136f0719afd3913dbe067d134fca9843d2756cd32f274f8cbbe6aac6`，
归属与完整输入/原流/静态检查回执见本机`opus_full_query_audit_terminal_20260921.json`。

## 61. 固定完整查询实测、准备阶段诊断及优化候选撤回

2026-09-24。用户要求推进主线后，恢复原三ELF、固定头和宿主，逐件SHA与§59
原记录一致，实际运行源码内既有固定人工原型及必要诊断/局部候选复测。没有读取
研究输入、赋保护参数、扩Compute供给、改变冻结科学合同或启动规模实验。

原驱动3.713147秒自然exit1，C boot rows1–35结束，setup rows50–100耗尽；C为
boundary1/failure0/owner_status1，仍可执行而供给终止。N/E未开始付费执行，
STRICT未开始，没有查询发布或movement标志。C-business关闭86行，actual及
charged均89129472，其中setup消耗固定53477376步。full-query审计接受全部92条
有效前缀记录并按驱动失败exit1，不以有效前缀冒充完整查询通过或总费用。

一次实际Claude Opus调用（CLI modelUsage为claude-opus-5，完整返回）提供失败后
只读CPU状态诊断，根按真实锚点集成、编译并复现；stdout与原版逐字一致。原失败
PC在first-fit扫描。另用独立宿主副本按实际微相位统计C boot/setup，去重暂停；
86次分配调用尝试、398604次used读取，cold入口及未归属读取均0。最后分配可能
未完成，直接返回点不是完整调用栈。§60批量冷初始化203134976步仍仅为未进入
分支的条件下界，不能用于解释本次失败，不据此切换FLINT后端。

尝试正二次幂对齐用完整地址的位与、其他对齐保留取模，first-fit候选及读取顺序
不变。原有限native检查和460800次与原header的状态/偏移/元数据差分均通过。
隔离新三ELF重新固定SHA并核定实际发布图，全部私有kernel字节与原版相同，
原1408字节栈界继续适用；不将旧镜像账单套到新实现。

候选实际运行3.806931秒仍exit1，setup同额耗尽。独立候选观察宿主再次输出相同
业务日志；在相同窗口只到达74次分配尝试、342961次used读取，16字节尝试由原
77次变为66次，尚未出现原版112字节申请，cold入口仍0。因此否决该候选，生产
arena头恢复原备份逐字一致，候选源码/镜像/失败前缀分别保留。不能把较少读取
称为省费用，也不能把两个预算截断运行外推为查询或任务吞吐回退百分比。

独立Astra Ultra复核指出当前B1的REMU和AND都采用相同8微步ALU模板；候选循环
多了实际付费分支及清零，普通CPU的除法成本直觉不成立。这是局部成本解释，
尚不声称解释全部差额。生产仅保留失败stderr诊断和Owner只读寄存器观察接口，
不将观察结果注入guest、调度或费用。下一项在恢复基线上定位重复16字节申请的
业务来源及该扫描路径占setup实际收费的比例，再决定能否减少必要分配。

完整查询释放/原MOVE继续、责任费用清理、收据安装与下一报价仍未验证，尚无
SRDC净收益或规模结论。详细命令、退出回执、核账、实际Opus原流和归档manifest
均在本机`implementation_binding_evidence/full_query_validation_20260924/`；综述
记录为`implementation_binding_evidence/FULL_QUERY_FIRST_RUN_20260924.md`。主稿
原SHA保持204316c27e17ecb37a8646d53cb5941a9b11b6c8eff3378ce55e80878b271452。

另按用户要求，独立Astra Ultra子智能体比较学习与LMAPF的空间误差方向，已核
OnlineGGO、S2M2、Dynamic Tube MPC等原论文和作者工件。建议优先预检共同空间
误差安全层上的执行占用代价学习及路径引导；当前PIE-D查询价值学习迁移成本
最低，动态误差管学习风险更高。没有实证支持立即换主线；动作完成时间不确定性
不能替代横向空间误差，经验分位数也不替代确定性包络。完整限定与原始来源见
本机`implementation_binding_evidence/LEARNING_LMAPF_DIRECTION_REVIEW_20260924.md`。

## 62. 调用来源、实际费用归属与支线合法 AND 预检

2026-09-24。完成用户明确指定的主线归属与支线并行预检。两个Astra Ultra子智能体
分别实现只读观察宿主与合法空间夹具；真实Claude Opus一次完整返回，CLI报告
claude-opus-5，限观察方法审计。根核代码和意见，实际执行主线、独立复算保存
记录并综合结果。Opus未运行程序或审阅最终观察器，不以模型意见替代证据。

主线保持原三ELF、固定头和供给，仅独立host副本观察。一次运行9.466697 host秒
自然exit1，stdout与原版逐字一致，三站失败CPU快照也相同。真实meter actual
差值逐次归到B1指令，86条关闭段的行、actual、charged与原业务记录相同，全部
仍归scheme0/C/C-business/account2/Compute；没有转嫁准备费给未发布的Query。
full-query审计接受92条有效前缀并正确按失败exit1。N/E未运行、STRICT未开始，
完整查询、释放/原MOVE继续、终态清理及下一报价仍未在这条链上验证。

boot actual35652096，其中初始化16937309、普通CPU5408098、kernel13306640、
其他49。setup actual53477376，其中place指令区间[0x7e4f4,0x7e658)收费52969092
（99.049535%）；其扫描子区间[0x7e54c,0x7e580)收费52909151（98.937448%）。
扫描含推进、对齐、used读取与分支；不是仅load费用，不能与place重复相加。
该阶段其余费用508284步。boot中的place/scan分别663948/399912，不混入setup分母。
逐行、CPU/阶段、PC及每次分配的费用守恒；delta>1、行身份/PC错误、未归属
place/used、计费回退和CPU歧义均0。398604次used-load与该指令4384644步相符。

86次分配尝试中，boot为72704字节EH池申请一次，setup85次。77次16字节全部
发生在首个geometry("move-A",1,4)：number局部初构10、两级返回移动10+9、
rectangle临时Point复制16、内部Piece坐标复制16、geometry外层Piece复制16。
都经qqbar_init及多项式两槽calloc到place，批量mpz冷入口仍0。另8次为几何
容器4×960、2×24、56、112字节存储。77次小申请的place/scan为47893281/
47851915步，另8次为5075811/5057236步。最后一笔16字节未返回，只计已付前缀；
此前85次（含boot）均成功返回。没有把“尝试数”当全部完成次数。

归属基于当前ELF的实际退休控制流后缀、符号与源码语义，ELF无DWARF行映射，
不声称完整栈展开。3次未知转移均早于这些分配后缀，逐次prior计数保留。
实际move构造先init有效零值再swap；不能删init或仅标noexcept。后继优先验证
几何中间复制的等价减少，再绑定新镜像按原供给复测；本轮未修改生产实现或
估计可省总费，不恢复§61被否决对齐候选。保护主稿与原arena SHA保持。

支线`explore/learned-query`新增合法AND夹具与固定源SHA运行器，真实Geometry/
Index/PositionCommit/ReferenceController编译、运行均exit0，530项断言通过。
90闭单位格、共同非零足迹及二维误差盒；检查六个驻留起点互斥和A/B/C全原MOVE
不碰等待起点后，才通过native admitted接口安装原cap。真实几何输出D1/D2均由
A、B阻塞，严格阈值分别33/20、53/20；D3仅由C阻塞。所有比较保持相同原轨迹、
两个固定机会，只提交被查询者证书。AB/BA第二次后可组件准入并安装2个新动作，
AC/BC/CA/CB为1；等号不释放、未查询q不更新、直接mask一致、终点责任保留通过。

该夹具人工证书不是AUTH，其他准入条件明确预设；标量控制器提供同原MOVE可达
见证，未积分二维误差z（可取盒内z=0作为存在见证）。没有完整费用、任务服务
或实际学习/SRDC比较，2对1不是任务完成或策略胜负。它只把此前抽象AND图推进为
给定前提下空间合法的组件见证。后继先同输入/机会/成本隔离单步与有限前瞻，
再固定决策器检验学习；不据此声称真实实例普遍或新模型已增加创新证据。

详细归属、命令、守恒与分工见本机
`implementation_binding_evidence/ALLOCATION_ATTRIBUTION_AND_LEGAL_AND_20260924.md`，
原始日志及构建SHA在`allocation_attribution_20260924/`。支线源码和人工运行
回执在`exploration/learned_query/legal_and_*`，九个依赖头仅只读临时复制；不
公开主线源码/原始二进制。本轮无研究输入、保护参数赋值、扩供给或模型训练。

## 63. 几何复制候选复测与误差路径引导新支线

2026-09-24。延续用户推进主线并新建清晰Git支线的要求，完成一项局部候选的
原生差分、新ELF绑定、原供给复测和独立核账，并在同仓库建立
`explore/error-aware-guidance`（分叉main@af17410，独立工作区
`/home/lyh/MAPF_LMAPF_ERROR_GUIDANCE_EXPLORE`）。旧`explore/learned-query`保留。
主线完整查询仍失败；新支线首次有限路径预检通过，尚未训练模型。

主线候选只把五个cell的`Resource{key,{rectangle(...)}}`改为空pieces后
push_back临时Piece，再移动Resource入cells，消除外层initializer_list的深复制。
FlintReal、rectangle、输入/控制参数、arena、编译flags与供给保持；完整旧/新工厂
在独立命名空间编译，8954项实际native断言通过，含526个直接mask及526个g_advance
比较、绑定/区间/闭接触和独立矩形oracle。直接C++ qqbar_init计数A25306→25266、
B25312→25272，各少40；不是FLINT全库调用计数，也不能外推完整B1费用可负担。

候选C ELF SHA为`6bb6820bee74ccae6b8e6959ed34d87facf8d7be9931fa13010e0f6dc1088f0f`，
N/E与原版相同。普通发布点重新发现、固定并经原资格工具核验；三角色私有kernel
字节/地址/映射相同，保留原栈界。没有沿用旧普通发布地址或增供给。

候选plain与只读observer实际运行分别3.793389、9.478546 host秒，均自然exit1；
两者stdout的92条记录逐字一致、失败CPU快照相同。86条费用段的actual/charged/
account/行身份与原输出守恒，full-query审计均接受有效失败前缀并exit1。
总C-business actual89129410（原版89129472），差62仅来自boot；setup仍53477376。
费用仍属于原C-business，不能转嫁给未发布Query。N/E未执行、STRICT未开始。

候选setup的place为53005667步，扫描52949148步，分别占99.117928%和99.012240%。
86次分配尝试、85次返回、末次截断；used读取398807次对应4386877收费步，
全部健康/归属错误为0，cold入口仍0。新增实际付费ReadPc业务探针记录前两个cell
在row68、87完成、第三个row87开始；原版第三个由分配#81返回/#82进入定位于row98。
末次调用由原第三cell的number返回移动推进到rectangle内部Piece坐标复制。
这支持相同预算下局部前缀改善，不是整次查询收益；两者仍只完成2个cell、0个Geometry。
扫描占比增加也不能独立判退化，因为执行前缀已不同。

候选保存于本机隔离包，原生产profile/default镜像保持，未将它宣称为完整修复。
后继对arena窄只读核验发现固定73第467/473行及实现README明确逐候选、单位步进；
跳到已占槽后一格或利用len跨活块都改变当前扫描合同，不能直接接入原基线。
前者可不依赖len证明first-fit不漏解；后者还依赖合法活块头历史，范围检查不能
防止伪长头跳过空槽。没有实施或运行两者。下一步分析冻结扫描必要成本与源对象
工作；若必须更换分配制度，应明示合同后继及重新核费，不能暗中更换比较身份。

新路径支线使用真实Geometry/Index/PositionCommit/ReferenceController，严格编译
和实际执行均exit0，790项断言通过。273个闭半单位格、固定方形足迹半宽1/10，
同起终点的两条预定路径各完成3个原MOVE。每组请求者和阻塞者均用共同误差盒，
四个配对组合在同一t=4均实际提交一次人工证书；控制系数、阻塞者轨迹相同。

| 误差盒半宽 | 上绕到达模型时间 | 下绕到达模型时间 |
| --- | --- | --- |
| 0 | [6.928203,6.928204] | [8.363081,8.363082] |
| 1/5 | [9.196152,9.196153] | [8.363081,8.363082] |

非零误差上绕第二段被真实Index阻塞，严格退出阈值61/20，从sqrt(3)合法驻留等至
t=4的PositionCommit，再授予下一段全cap。标量控制器实际边界给出到达时间，
没有任意cost table或浮点安全决策；显示区间向外包围精确实代数数。初始互斥、
全mask准入、等待驻留、未观察q不提前更新和阻塞者终点责任保留均检查。

反转是空间误差、固定观察策略与保守准入的条件交互；更早观测可能恢复上绕优势。
路径人工预定，二维z未积分（可取盒内z=0作存在见证），AUTH和END均为明确的
native前提。没有在线规划、真实服务/长期任务流或完整计算/通信费用，不能据此
声称模型有效或优于PIE-D。下一项先做共同观察时机、间隙/误差盒对照，然后比较
简单解析代价；离线反事实可作标签，但不得泄漏进在线特征或跨运行留出划分。

两个Astra Ultra子智能体分别交付主线候选/差分/observer及支线预检；根核实际
源码、完成新镜像装配/主线运行和独立核账。一次真实Claude Opus设计审计完整返回，
CLI报告claude-opus-5、135370ms，未看最终程序或运行；意见取舍另记于新支线
`OPUS_AUDIT.md`，不把模型意见当实验证据。

完整报告为本机`implementation_binding_evidence/GEOMETRY_COPY_AND_ERROR_GUIDANCE_20260924.md`，
主线证据在`geometry_copy_reduction_20260924/`，含ROOT_VERIFICATION.json、native
差分、新绑定和8个逐件SHA核对存档工件。公开内容限四份主线进度文档、分支导航
和新支线自写具名夹具/运行收据/依赖指纹；主线源码和二进制未上传，远端不能
单独复现本机依赖。主稿原修改及SHA保持，无研究载荷读取、保护参数赋值或扩供给。
