# 首版数据scope补充

首版DATA_SCHEMA/manifest/audit已分别保留在`DATA_SCHEMA_initial.md`、`dataset_manifest_initial.json`、`dataset_audit_initial.json`。原始datasets和trial raw没有改写。

首版把基线的episode描述为“完整原格MOVE”不准确：exporter按首次实际非零MOVE命令时**已派发queue尾node**固定episode，作者ADG可能只派发第一半MOVE。因此其0.5m原生队列段及可能合并的段，都应称“已派发原生MOVE队列段”；`future_episode_final_ACK`对应这个已公开队列span最后节点，不应自动解释为原规划器整格MOVE结束。code/data数值正确，scope文字已明确纠正，未替换或重跑试验。

`motion_supplement.py/json`另按实际公开proposal的整格start/goal及后续真实admit的最后M节点，独立导出`original_step_targets.jsonl`，包含完整原格MOVE的真实progress/lateral及正常最终END/删失，全部为离线target、不追加到online features。触发的原格MOVE是proposal1/agent0，first nonzero command58，最终node3 ACK84/104；干预作用于其未ACK第一半node2，ACK68/88。两种scope都保留，不能混算为同一训练目标。

原`audit.json:event_count`来自删除新增控制日志后的父mapping replay，原raw事件数在motion_supplement中单列。父mapping独立检查的覆盖保留；新增trigger/wheel/pause/resume均由r3 auditor另行严格审计，所有原raw sequence连续性直接检查。
