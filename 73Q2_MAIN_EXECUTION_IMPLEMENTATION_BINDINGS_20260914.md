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
