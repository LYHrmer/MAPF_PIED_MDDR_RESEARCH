# 73E23 根独立分析：局部图寿命、C++14 拷贝消除与标量输出

2026-09-10，根 /root；NO-SKILL / CONSTRUCTIVE / NONBALLOT。此件从固定源码和语言条文独立推导，不使用 Claude 意见，不是整稿审查或来源资格通过。起始 73 为 SHA256 e72ccb8cd65bbbd037aa2ea005666bd46e307c4f3ae2da860f0cf9a9f2b9fbeb，194152 bytes /619 LF。HOLD / NO-GO-IMPLEMENT / NO-GO-MAIN-EXPERIMENT 保持；仅研究文本，未实现、编译、测试或运行。

## 1. 结论及采用范围

73E22 已要求搜索节点/队列唯一归属及回溯前图存活。本件补到其外层：批准调用链中的 LACAMInstance 与其 Graph 必须从冻结输入直接建立唯一命名对象，不经过中间同类型临时对象或按值图复制；借用关系存续期间，该拥有者不得移动、重建或销毁。源包装器的命名 Planner 也直接由其构造实参建立，避免以后引入 E22 拥有者时隐含可复制性。所有内部来源臂共用这项明确的 R0-REPAIRED-LACAM-ADAPTER 纸面修订，不能称原源码已满足。

在上述条件和合法 solution 结构下，已读正常输出链在 ins 仍活着时把 Vertex 的 index 复制到 PathEntry 的整数 location；PathTable 保存整数，runLACAM2 只返回 bool。由此可以关闭这个具名链上的“正常输出仍持有已毁局部 Graph 的顶点”疑点。它不关闭图构造异常、越界、数值溢出、任意回调逃逸或完整来源继续域。

## 2. 实际来源、身份和阅读范围

所有项目源码属于作者仓库 [LMAPF-delay 固定提交](https://github.com/YueZhang-studyuse/LMAPF-delay/tree/0b5b33649fc367abcb1cd0a7ad5ac03511bf9357)。以下七对象本轮通过 GitHub 文件接口取得完整内容，根从全部返回字节重算 SHA256 与 Git blob，七项 blob 均与返回身份一致；只做文字与身份核验，没有执行源码。PathTable.cpp 全对象取得/散列，但人工语义读取限 L1–100，本结论依赖完整 insertPath L3–17，不称全文审读 373 行。

| 对象 | Git blob | SHA256 | bytes / LF |
|---|---|---|---|
| src/MAPF-LNS2/src/lacam2/lacam2.cpp | 75ee58f4e1adb46ad3b26991cc212929bbff5f60 | 107bdd83cef76baf86831c0a0f3c421d64e65c36381494d7438dfb1f6b1f2f05 | 464 /10 |
| inc/MAPF-LNS2/inc/lacam2/lacam2.hpp | b12113c7e263ac570f53f0af533ec86de9a8bb4d | 64bdb7cc7b0c0d439bd3dc5a029db70102a1e538b21208b8b3ffb129dce1bfa9 | 481 /13 |
| inc/MAPF-LNS2/inc/lns_common.h | 3bddf54ab74388904064a60a92346883a52c10cb | 8994fbaf6e022f7b233b7015741ae277d5773f3c84665845ecc654b44a51ccf6 | 2890 /102 |
| inc/common.h | 9ddeff363a76cbd70a3e6e1ca98cfd79f69c8237 | 6d0aaa271e61201ffc6313e9ae1210f9b4e75fea6711a6edca7117be4dc3b67d | 5954 /224 |
| inc/MAPF-LNS2/inc/PathTable.h | 0ae813e9526367d3076c297deba51fc0ad3a5a76 | 909a0fe4a8ebb89a69819d47cf80db579ed1793a75d1936dc2787edddd5ecbc2 | 3090 /55 |
| src/MAPF-LNS2/src/PathTable.cpp | 1dd06d5c8ef71841409a88517cc419df841fefb8 | 96cb8eaef095e01f99f69b91951372c5c2d2f966c6c2c126f315bdbdc429321c | 12025 /373 |
| CMakeLists.txt | 148459bb9542731723e8125bb8d54da6a3ce954b | ecdf7e3c889ab8290eb9cc839543c0f281419db957982a03b79ae79da25dc899 | 2790 /92 |

表内列出的是原源码身份，不是新研究工件身份。

根另复读已核 LNS.cpp 完整 runLACAM2 L648–714（blob 1fb0e54f8f2bb00af05de53233ae600774e36f2a、SHA256 0113b1911195d630ce98dfa09a28412148e1fadfc0f1aac9f75f1ba4ad2a54b2），graph.hpp 全文及 graph.cpp 析构 L9–14、LACAMInstance 头全文和 SharedEnvironment 构造 L19–38、Planner 头全文及构造/析构/solve 入口窗口。Graph 声明/析构对象身份沿用 E21/E22：graph.hpp bdf87cf5a1b911c039ebcf10374ddf317086fbd4 / SHA256 166b3ecbe68e7ddcd549504044a3c47cc3abb9ca98653b8639a654607480daee；graph.cpp fb8ab481d5b1e3a959a18b826fd5919b69772e7e / SHA256 7bdb71a22dbdf6df873370c20173f0ef9ab97c34fbb649f222c7bcb9fa2813a0。LACAMInstance 头 blob 7ada1b5832c0f45a510bb9c98cb97b459731d3f8 / SHA256 97d98a8807b64c0cf56ec71ba57bdd6f31c8a15b4fb1155972645d416f38ff1b；cpp blob 50f18e9ce8295ba94e4a7d5caa293d5affca0688 / SHA256 840d442a5f3a0804ae751e1c39797a3f669dd43dcadf48786b73b1fc0e2db1c4。

common.h/构造源含解析或其他入口文字不意味着允许读取它们指向的载荷。本件没有读取 map、scen、config、任务/延迟/结果文件，也没有调用这些解析入口。CMakeList 是只读构建声明，读到它不等于启动构建。

## 3. 独立语言核验及条件风险

根实际读取 C++14 工作草案 N4140 的 [class.copy 第 7、9、15、31、31.3 段](https://timsong-cpp.github.io/cppwp/n4140/class.copy)：该域的拷贝消除是允许的优化；用户声明析构会阻止隐式移动构造，隐式拷贝仍可能存在并逐成员复制。本次取得的是草案文本镜像，不是本机编译器或标准库运行证据；官方 PDF URL 本次工具拒绝访问，未下载或绕过。下述风险是根把条文应用于已核源码的推论。

原根 CMakeLists L4 声明 C++14；Python 条件中另有 17 声明，不能替当前纯来源分支保证 C++17。原 LNS.cpp L651 用一个 LACAMInstance 临时对象初始化命名 ins。LACAMInstance 自声明空析构并拥有 const Graph G；Graph 自声明析构，V/U 是裸 Vertex 指针容器，没有自定义深复制或移动。若在允许的 C++14 执行中未消除这次复制，隐式复制会共享顶点指针，而临时 Graph 析构删除顶点，使后续 ins 的指针失效；之后再次按 V 删除还可有重复释放风险。不是“每次必定发生”，也不是观察到的运行故障。Release 或通常编译器会消除复制不足以证明所有批准部署安全。

最小声明修订是直接从同一冻结 SharedEnvironment 实参构造唯一命名 ins；其 G 在已读构造初始化列表中本来就是由地图向量/行列实参直接构造，批准链不使用文件场景重载。修订不改图边、顶点编号、目标、随机初态或算法策略，不把语言标准改成 17 作为隐含前提。将来任何按值复制/迁移拥有图对象都不属于此批准接口，必须重新给所有权证明。

包装器 lacam2.cpp L7 也以临时 Planner 初始化命名 planner。原构造只有容器初始化，此时 A 元素为空，不能把它报成已证的原版顶点 double-free；但 E22 的唯一拥有者设计不应再依赖中间副本能否被消除。故同包声明该命名对象直接构造，不按值复制拥有状态。此项是组合兼容约束，不夸大成原程序在这一行必然崩溃。

## 4. 正常输出链的局部闭合

Solution 是配置向量，Config 是 Vertex 指针向量，Vertex 由 ins.G 拥有。内层 Planner 只借 ins；E22 删除 HNode/低层队列/本次 LACAMAgent 不删除 Graph 顶点。内层回溯必须在搜索节点仍存活时复制配置，然后返回 Solution；返给外层的顶点指针仍借用外层 ins.G。

runLACAM2 在 L659 接收 solution，在 L676/690/703 读取 index；这些操作都早于外层 ins 的作用域结束。L691/704 将 location 写入 PathEntry；真实 PathEntry 在 common.h L41–47 只有整数 location，lns_common.h 中相似定义是注释，不能用注释替真实类型证据。PathTable::insertPath L3–17 将 location 用作表索引，存 agent_id/到达时间/makespan 整数，没有保存 Vertex 或传入 Path 的地址。正常结果是 L713 返回 bool，Path/Table 输出在图销毁后不含图顶点借用。按局部变量逆序销毁，solution 先于 ins；其指针容器销毁也不删除顶点。

这份证明依赖 solution 每一读点结构/agent 维数/指针归属有效、图未提前被别处销毁、整数转换/索引合法，以及批准链没有额外回调保留顶点。它不把先读后验的未知结构风险消掉；现有 PRE_COMMIT_SHAPE 是后继边界，不能倒过来保护此前任意非法解引用。PathTableWC 是另一类型，含 Path 借用，不能从本 PathTable 结论扩展为所有表均纯标量。完整值域、构造中抛异常及未完整 Graph 构造时顶点归属仍是后继明确义务，不以 fail-stop 字样证明免费或完整清理。

## 5. 成本、身份与后继机械合同

图/环境快照、图构造、节点和 Agent、输出标量复制、路径表维护、正常/异常清理、引用保留与整数工作仍按各臂真实发生计费；没有借减少临时对象把任何仍发生的工作免掉。不会先运行原样不安全路径，再通过结果筛选声称采用了本修订。它会改变临时对象数及可能的源时间，须与 E20/E22 一起登记修改来源，原 commit 仅为出处身份；未生成修订后源码或运行身份。H19 的 ECBS 不承担未使用的 R0 图费用。

拟入 73 的 W89 为 NOT_IMPLEMENTED / NOT_RUN：唯一直接建立图/Planner；借用跨回溯和标量封存时均有活拥有者；输出后不逃逸顶点指针；不以 C++14 可选优化或晚到形状检查替代入口/生命周期资格。这只是可区别行为的纸面合同，没有写测试或执行检查器。六门仍 2 PASS /3 UNKNOWN /1 FAIL；73 未固定、未送审、未接受，完整资格不变。
