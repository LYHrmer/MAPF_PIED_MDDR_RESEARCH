# 本轮公共查询实验的原作者输入和实际轨迹

这是既有官方PIE-D完整分支 `74cfba3c81a0c165c2e7044dea6fd4dee8ddf415` 原生运行的逐字归档，没有新增作者运行。原始result SHA为 `67c10baa0faa4b10200591982d970368c6f8292e87959a47b8f7d0d832849b10`；100机器人×20tick、2000动作、原作者52任务。R2抽出的355跟随关系来自这份完整轨迹，不由查询策略选择性生成。局部实验的96个潜在端点服务不追加到原作者52任务。

[manifest](manifest.json)绑定11个原始文件：完整result、原始命令回执及三份日志、作者输入/map/agents/tasks/许可证、原R0报告。原作者MIT许可证保留在author_inputs/LICENSE。20MB固定delay文件可从该固定作者版本获取，哈希在manifest中；原binary哈希保留但不发布二进制。复跑作者原生程序可能受原未初始化成员和计时因素影响；本包的确定性核验以已发生的冻结轨迹为准，原R0报告披露此边界。

[root独立核验脚本](../public_trace_root_review_20260930_r2.py)会优先读取此归档的result与map，重新推导全部源动作、跟随关系、任务head及因果END选择，不依赖原本机R0目录。它仍需同分支保留的旧查询工件完成字节保护核验；这是保存证据重放，不是新native运行。

重新核验可运行 `rtk proxy python3 exploration/learned_query/public_trace_root_review_20260930_r2.py --output /tmp/query-root-new.json`；输出已存在即拒绝覆盖。[完整实验结果](../public_trace_20260930_r2/RESULTS_20260930_r2.md)保留两次实现失败和原actor输入缺口。
