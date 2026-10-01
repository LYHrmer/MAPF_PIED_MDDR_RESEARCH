# R6 第三线独立复核与发布

root 在每组 native receipt 完成后，以四个只读工作进程调用冻结的全链审计器，并用独立程序重新计算每个物理 tick 的机器人圆形包络与实际 XML 障碍间距。该过程不启动规划器、不补写 END、不改任务和模型。

`CONTINUOUS_EXECUTION_ROOT_20261001_R6.json` 同时保存全链审计与独立采样几何结果；`verify_physical_clearance_20261001_r6.py` 是独立几何计算；`collect_continuous_audits_20261001_r6.py` 是只读调度程序。采样采用覆盖 base/gripper 的 0.095036758 m 圆形半径，未观测连续子步接触，不能据此宣称连续安全证明。

`finalize.py` 只在完整 24 组到齐后导入原始审计，汇总结果并核对三个冻结版本的所有引用 SHA。原单进程监视器的部分结果保存为 R6c `audit_monitor_partial.json`。`publication_manifest.py` 逐成员解压校验全部八个归档，列出显式 Git 发布白名单；不发布 native 编译缓存或再次复制未压缩日志。

复现依赖同分支早期作者复现包及其固定的 OnlineGGO/LSMART/ARGoS 版本、RPC/系统库和编译工具链；原回执中的绝对路径保留。`native_source_manifest.json`、`official_object_manifest.json`、编译命令/回执与 `binary_manifest.json` 用于核对来源，二进制本体不随本包发布。原生重跑需本机 loopback RPC 权限。审计可从四个对应地图/规模归档恢复完整原始运行；不能把本包描述为无外部依赖的一键容器。
