# 72C7：首次调用真实网络失败

真实exec49402，exit=1、api_error/FailedToOpenSocket、duration179452ms、零usage，无建议。根确认终态后获准沙箱外同提示重试，真实exec47344已启动，完整建议待回。首次完整JSON原文如下，非科研投票，不以subtype字段掩盖is_error和非零退出码。

```json
{"is_error":true,"duration_api_ms":0,"num_turns":1,"stop_reason":"stop_sequence","session_id":"b0daad15-379c-42e1-8511-178603229571","total_cost_usd":0,"usage":{"output_tokens_details":{"thinking_tokens":0},"input_tokens":0,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{},"permission_denials":[],"terminal_reason":"api_error","fast_mode_state":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subtype":"success","api_error_status":null,"result":"API Error: Can't reach the API server — check your internet or DNS (FailedToOpenSocket)","type":"result","duration_ms":179452,"uuid":"456190b1-cab2-4f3f-8fa1-d05f6bb42aeb"}
```
