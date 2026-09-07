# 73C1：首次调用网络失败实际回执

真实exec91679，exit1，duration176078ms；无建议正文、零usage，不计完成。确认终态后同一提示获准升级重试，真实exec97292，完整回执待回。提示SHA256 cab7c5bae9d71f2a75f7d14e4526172a771520deb87e50e1c790cb29b46d66c5。

下列为实际返回JSON对象的原值序列化；不是数学建议或正式审查。

```json
{"is_error":true,"duration_api_ms":0,"num_turns":1,"stop_reason":"stop_sequence","session_id":"e6584377-b715-4cf4-a3d2-5cc9c077364f","total_cost_usd":0,"usage":{"output_tokens_details":{"thinking_tokens":0},"input_tokens":0,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{},"permission_denials":[],"terminal_reason":"api_error","fast_mode_state":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subtype":"success","api_error_status":null,"result":"API Error: Can't reach the API server — check your internet or DNS (FailedToOpenSocket)","type":"result","duration_ms":176078,"uuid":"4caff8b1-c3db-4cc6-ac58-c5b19a2a50c5"}
```
