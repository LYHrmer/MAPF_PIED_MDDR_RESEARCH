# 73E7：根实核本机Boost 1.74及相关堆调用合同

2026-09-09，根直接只读核验，NO-SKILL / NONBALLOT。未配置CMake、编译、构建、创建或运行测试、执行规划器、仿真或实验。只读取版本元信息和三个明确系统头文件的指定窗口，不改变本机依赖、源码或环境。此证据用于限定73E5/E6所需库合同，不把任意版本的条件分析冒充本机情况。

## 1. 本机实际观察与限定依赖选择

| 实际只读来源 | 返回事实 | 解释边界 |
|---|---|---|
| /usr/include/boost/version.hpp L18–30 | BOOST_VERSION=107400；BOOST_LIB_VERSION="1_74" | 本机该路径的头文件是1.74；不是CMake解析回执或已部署程序的链接证明 |
| c++ --version | Ubuntu 11.4.0-1ubuntu1~22.04.3，11.4.0 | 该命令实际编译器版本；没有调用编译 |
| dpkg-query：g++ | 4:11.2.0-1ubuntu1 | 元包版本，不用它覆盖上行实际driver版本 |
| dpkg-query：libboost-dev | 1.74.0.3ubuntu7 | 本机安装包元信息 |
| dpkg-query：libboost1.74-dev | 1.74.0-14ubuntu3 | 同上，不能单凭包名证明实际包含了哪个路径 |
| getconf GNU_LIBC_VERSION | glibc 2.35 | 本机返回值，不是对POSIX接口的运行验证 |
| dpkg-query：libc6-dev | 2.35-0ubuntu3.14 | 开发包元信息 |
| uname -srmo | Linux 6.8.0-138-generic x86_64 GNU/Linux | 本机系统/架构快照，未执行任何实验 |

根将后继纸面修复适配器的**参考Boost合同限定为本次已核1.74头文件**。这是一项实验前依赖选择，不修改官方R0的原CMake要求，不声称未来实际build已经绑定。后续获准构建时必须核实际include搜索结果、版本宏及所选对象与此身份一致；如不一致，归为DEPENDENCY_NOT_MATCHED，先重新核合同，不悄悄继承本证明。CMake最低/兼容版本要求不能替代此精确选择。本机其他Boost版本是否安装不在本次查询范围。

## 2. 完整字节身份与实际阅读范围

| 文件 | 完整SHA256 | 亲读范围 |
|---|---|---|
| /usr/include/boost/version.hpp | 90e046b8e3138a61c692abdd9bc2e45c1a95996cc5a8031cce1f110de5e64a70 | 版本宏及其解释L18–30的实际匹配行 |
| /usr/include/boost/heap/pairing_heap.hpp | 668543a7a2ab2b4519452a5f841d36f30761cb99b102e3273d999adb3afe9fcd | L28–100、L220–326、L346–414、L493–540、L650–714 |
| /usr/include/boost/heap/detail/stable_heap.hpp | 24d78657787040120778df3d60396c1b1c16d6f5babc612431a028b9a387e371 | L135–217、L291–387、L428–444、L552–599 |

hash覆盖完整字节不等于全文语义读取。以上窗口完整展示相关构造、pop/erase、析构、合并及比较分发链；未读所有Boost内部实现或证明标准分配器等全库正确。库内部代码没有复制为新的可执行工件。

## 3. 对已明确源码分支的直接结论

pairing_heap普通构造把比较对象传给super并置root=NULL；make_pairing_heap_base仅把比较对象交给heap_base。stable_heap的普通/稳定两类构造复制比较对象，稳定类另置counter_，没有调用比较运算符。对已核为简单比较结构、无自定义有副作用构造的R0比较类型，这些语句不因构造空堆而执行随机比较分支。不能把比较对象的复制与对两个值执行Compare混为一谈。

析构在L279–283明确是while(!empty()) pop()，不是clear()。因此：

- 始终空的堆析构只见root为空，不走pop或Compare。
- 非空堆的pop进入erase；有多个子节点时merge_node_list及merge_nodes可能调用比较器。非空析构可能比较，但不是每个非空结构必调用Compare。
- clear()有自己的clear_subtree/销毁路径，不能以clear的实现替代析构语义。clear_subtree的全部传递实现未在本次重读，因此不额外外推其全部性质。

push先建节点再merge_node。root非空时merge_nodes执行super_t::operator()；非稳定heap_base直接调value_comp().operator()，稳定分支通过internal_compare先后比较两方向，再用稳定序号处理等价值。故给稳定选项或事先固定随机种子，都不能把一个不满足比较合同的比较器自动变成严格弱序。

73E5所识别的四个LLNode相关堆，只有在各自确实从构造到销毁始终为空、且没有另行调用会比较的成员的已限定分支，才可排除这一operator链；这不是对整个R0的不可达证明。LACAM之前的computeAllPair局部第五堆实际有push/top/pop路径，不能套空堆排除。其`value >= value`对相等值为true，破坏非自反性；改为严格`>`只解决这项比较关系问题，不能据此宣称整个搜索、索引、内存或初始化生命周期已经正确。

这里是源码层及库合同分析。没有运行触发未定义行为，没有借源码问题制造新方法的实验优势，没有声称某次原生调用已崩溃。官方原版、计划修复适配器与未来实现证据须分别命名。

## 4. 尚待闭合与传递给根整合的结论

实际本机头文件版本这一项不再完全UNKNOWN；未来构建选择仍NOT_CONFIGURED / NOT_BUILT，不能提前填写已绑定。根已将本机观察传给73E6代理，该代理可引用为根提供的证据，不应冒称其自己亲读。73E6进程隔离/超时回收合同、源字段定义域、外部求解器新增依赖及全部费用仍分别核验。

这是一项有界证据进展，不授予G3或任何六门PASS。保护参数原义未赋值，冻结旧件、35–38及受限载荷禁读边界保持；所有shell及链段rtk，本文仅apply_patch写入研究目录。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT。
