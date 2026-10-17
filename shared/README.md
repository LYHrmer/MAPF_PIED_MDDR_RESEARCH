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
