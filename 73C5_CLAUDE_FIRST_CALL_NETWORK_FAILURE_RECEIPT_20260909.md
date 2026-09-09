# 73C5：首次调用网络失败实际回执

NONBALLOT / NO-ADVICE。实际exec会话59349已结束exit=1，返回以下完整JSON。工具无建议正文、无输入输出用量，不能计作Claude完成了路线分析。只有本次实际失败已确认；不替代旧73C4未知重试状态。随后按正常权限机制升级同一新73C5调用。

```json
{"is_error":true,"duration_api_ms":0,"num_turns":1,"stop_reason":"stop_sequence","session_id":"a209466b-5e14-49a9-8499-d901ca524aeb","total_cost_usd":0,"usage":{"output_tokens_details":{"thinking_tokens":0},"input_tokens":0,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{},"permission_denials":[],"terminal_reason":"api_error","fast_mode_state":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subtype":"success","api_error_status":null,"result":"API Error: Can't reach the API server — check your internet or DNS (FailedToOpenSocket)","type":"result","duration_ms":181541,"uuid":"f1f84bd8-7943-4f86-ba86-2b76d72f525f"}
```
