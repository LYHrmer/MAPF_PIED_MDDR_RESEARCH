# 72C5：首次调用真实网络失败回执

NONBALLOT / NO-ADVICE。真实exec 79797 已终态 exit=1；is_error=true、terminal_reason=api_error，FailedToOpenSocket；usage为零，无建设性建议。JSON的subtype=success不是本次调用成功。根确认终态后才获准沙箱外重试同提示；新句柄另记，不把失败当通过，不与旧缺失任务混同。以下为实际完整返回JSON，没有凭状态补建议。

```json
{"is_error":true,"duration_api_ms":0,"num_turns":1,"stop_reason":"stop_sequence","session_id":"9456f49e-e2ed-42a3-b660-fc47267d38ad","total_cost_usd":0,"usage":{"output_tokens_details":{"thinking_tokens":0},"input_tokens":0,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{},"permission_denials":[],"terminal_reason":"api_error","fast_mode_state":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subtype":"success","api_error_status":null,"result":"API Error: Can't reach the API server — check your internet or DNS (FailedToOpenSocket)","type":"result","duration_ms":173512,"uuid":"972f9d3b-f971-48a5-8ca2-2d9ea48ea5e1"}
```
