# 官方源码、许可证与隔离身份

直接父[gpibt_lsmart_integration_20260930_r2](../gpibt_lsmart_integration_20260930_r2/REPORT.md)冻结链保持，包括原task_id wire修复和前轮失败身份。全部78文件SHA另固定在previous_archive_manifest.json。

GPIBT官方[nobodyczcz/Guided-PIBT](https://github.com/nobodyczcz/Guided-PIBT/tree/7f4b91e4ed134229710945a4670a78639cf008d5)，commit `7f4b91e4ed134229710945a4670a78639cf008d5`；GPIBT_LICENSE.txt原MIT文本与Copyright2023 Zhe Chen完整附带。原作者算法14个objects及公开seed42/group2 bridge从父逐字节复制，OBJECTIVE1/GUIDANCE/GUIDANCE_LNS/INIT_PP/RELAX100/FOCAL_SEARCH2/ROBOT_RUNNERS等父配置不变；N2的group2是已披露公开参数R1设置，不能冒称原group10 R0。

LSMART官方[smart-mapf/lifelong-smart](https://github.com/smart-mapf/lifelong-smart/tree/a3780a45eb101f5b6834236f86bad39025f1e99f)，commit `a3780a45eb101f5b6834236f86bad39025f1e99f`；LSMART_LICENSE.txt原MIT和Copyright(c)2026 as distributed完整附带。继承fmt兼容、同步停稳view、因果观察和wire修正，parser/ADG/PID/参数/服务计时器不改。controller的actuator转发wrapper保存同一参数并原样调用，新增首次活动MOVE干预分支和实际命令日志；仅cpp/h两源变化。该试验台不是竞争算法。

native新树`/home/lyh/MAPF_PIED_MDDR_RESEARCH/implementation_binding_evidence/gpibt_lsmart_active_20260930_r3`独立，完整父/子source tree SHA、两文件diff和快照公开。未改server源码；server的父正确wire二进制和官方bridge复制到新运行路径，SHA与父相同。实际重建client（含原loop-functions），build receipts及其真实.d列出的cpp/h绑定可核。源码/对象/二进制manifest、ready_for_trial及每trial receipt列出的启动身份一一匹配，原生build产物留ignored目录。

部分准备失败native树另留`.../gpibt_lsmart_active_20260930_r3_prepare_attempt01`，尚无native trial；未拿成功的编译/二进制身份追认失败。所有公开patch/snapshot/桥接源与原许可证一起交付，未下载新源码、修改官方训练入口或以自写算法替代官方对象。
