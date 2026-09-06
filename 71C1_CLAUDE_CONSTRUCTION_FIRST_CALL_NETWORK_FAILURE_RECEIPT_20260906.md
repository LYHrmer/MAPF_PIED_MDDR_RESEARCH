# 71C1 首次调用网络失败实际回执

NONBALLOT。实际 exec session 80351 已终结，exit=1；完整原始 stdout 如下。API 未接收有效推理，input/output tokens=0，没有科研意见，不计完整建议或通过。当前工具已明确终态，因此可对同一固定提示按沙箱网络升级规则重试；不把观察超时当终止。

```json
{"is_error":true,"duration_api_ms":0,"num_turns":1,"stop_reason":"stop_sequence","session_id":"717d7fff-38a1-46df-a100-39e42ed7a63b","total_cost_usd":0,"usage":{"output_tokens_details":{"thinking_tokens":0},"input_tokens":0,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{},"permission_denials":[],"terminal_reason":"api_error","fast_mode_state":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subtype":"success","api_error_status":null,"result":"API Error: Can't reach the API server — check your internet or DNS (FailedToOpenSocket)","type":"result","duration_ms":176022,"uuid":"3803b1d0-6660-44dc-83dc-a6e1257f6c8a"}
```
