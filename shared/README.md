# 固定提交的公共依赖

`manifest.json`登记12个现有模块的完整提交、仓库内路径、Git blob ID和内容SHA-256；不复制模块、不合并研究分支。执行/来源/工具分别固定在`81f586669c961392dbc27e6f9ae8cb7f32297584`、`43806cff38d70efd868658db898f8f723aa25527`、`5589a7bb1591a919343774babd28ad570b538202`。

四次DEV的25项证据固定在`ae058c5025eaaa61a424ef7627515d40c2e83997`，状态为`PINNED`：总收据、四案events/result/启动标记/process日志、报告、清单、manifest、授权、运行上下文及已消费标记；均保持原仓库路径，只登记对象身份。读取器逐项校验这些文件的commit/blob/SHA及字节，不对证据运行科学函数，也不把已消费授权转成新运行许可。

`pinned.py`只读取本地Git对象并解析Python AST；不导入科学模块，不构造轨迹、证书或优化器，不授予运行权限。它不读取模块工作树内容，不接受分支名、不自动下载，也不回退到HEAD。现有预执行driver仍依赖真实`__file__`；本工具不是它的运行适配。

准备当前索引及运行静态单测：

```bash
rtk proxy python3 -I -B shared/pinned.py --repo . --candidate-manifest shared/manifest.json
rtk proxy python3 -I -B shared/test_pinned.py
```

第一条明确输出`WORKING_INDEX_PREPARATION_ONLY`。第二条仅在`shared/`内创建并清理小型临时Git测试仓库，核验错误commit/blob/SHA/路径及已暂存、未暂存修改隔离；不改研究仓库index。

两条研究线消费时，各自在自身已提交配置中固定main的**读取器与manifest**，不跟随main最新工作树。manifest pin使用以下结构，其中各值必须来自实际提交：

```json
{"commit":"完整40位提交","path":"shared/manifest.json","blob_oid":"完整40位blob ID","sha256":"完整64位内容SHA-256"}
```

将真实pin存成消费者的锁文件后，调用已固定的读取器：

```bash
rtk proxy python3 -I -B /固定读取器路径/pinned.py --repo /公共仓库路径 --manifest-pin /消费者锁文件.json
```

Python接口为`read_blob(repo, pin) -> bytes`、`audit_manifest(repo, manifest) -> audit`及`resolve(repo, manifest_pin) -> {manifest_pin, audit, modules}`；后者的`modules`是字节映射，不是已导入模块。只有索引已被固定Git对象读取的模式才输出`PINNED_GIT_OBJECT`。

固定提交必须由保留并推送的分支或归档标签保持可达；JSON中的提交字符串本身不能防止Git回收。对象缺失即失败，不隐式联网。以后若做运行适配，应逐项提取已核验小文件到每次运行独占的bundle、绑定新运行清单，避免共享可写缓存或`PYTHONPATH`混入另一研究线的版本；不得改写冻结运行及其收据。

本轮工具在主机Python 3.10.12以标准库完成静态核验，不要求LIMO车载系统升级。硕士消费者的`tracks/thesis/shared.lock.json`固定读取器与manifest于公共提交`4a89183cf0827dcae2fa20a7d816c760e4150457`，仅加载所需9份证据。SCI当前不消费这12个误差执行模块，后续有真实公共依赖时才增加pin。

硕士[aea4ffa](https://github.com/LYHrmer/MAPF_PIED_MDDR_RESEARCH/blob/aea4ffad2dfdf59a163436a21ee35c0f7b75c333/tracks/thesis/README.md)的`tracks/thesis/sci.lock.json`继续用同一读取器固定SCI`535ee1a`的14个证据对象（输入、汇总、六份结果与六份收据），供运动结构和等成本改路离线解析。新增`source_contract`固定来源`16b1ee0`的`COMPOSITION.md`，只核对v2条件文档，不代表模型运行或路径资格通过。

同提交的`plan_selection.lock.json`固定SCI`535ee1a`的`pp_repair.py`与`address_backend.py`，在校验Git对象字节后复用原`GridProblem`及完整路径检查，支持SOC、保留等成本路径、转向感知的整方案选择规则；没有复制或启动原生求解器。两份消费者锁由硕士维护，SCI`032bf22`及其后续实现不自动进入该消费者。当前没有新增公共运行接口，也不把SCI专用优化器或证据复制进公共目录。

硕士`e507702`的无误差运动参考继续使用该固定GridProblem入口，不改变锁文件；SCI`eb4a60f`新增的运行结果、共同终止与恢复原型也不自动进入硕士。运动编译器目前只有硕士消费者，留在`tracks/thesis/`，不为形式上的共享复制到此目录。
