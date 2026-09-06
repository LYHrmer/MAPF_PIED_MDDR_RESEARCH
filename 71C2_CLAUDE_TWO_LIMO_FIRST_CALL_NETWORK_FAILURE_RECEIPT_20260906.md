# Claude 71C2 首次调用网络失败：完整实际回执

NONBALLOT；实际 exec 91127 已终结，exit=1，零 input/output tokens；没有建设性建议，不计审稿或成功。提示为 71C2_CLAUDE_TWO_LIMO_EVIDENCE_FEASIBILITY_CONSTRUCTIVE_PROMPT_20260906.md，SHA256 0b042682241cafbe3b203d60cacbca80fb00868e21f6f1c47035c66497229571 / 4323 bytes。完整 stdout 如下；subtype 的 success 字符串不能覆盖 is_error=true 与实际 exit=1 / api_error。

```json
{"is_error":true,"duration_api_ms":0,"num_turns":1,"stop_reason":"stop_sequence","session_id":"ff606f8a-1b53-4d7c-9dd2-f5543aea768e","total_cost_usd":0,"usage":{"output_tokens_details":{"thinking_tokens":0},"input_tokens":0,"cache_creation_input_tokens":0,"cache_read_input_tokens":0,"output_tokens":0,"server_tool_use":{"web_search_requests":0,"web_fetch_requests":0},"service_tier":"standard","cache_creation":{"ephemeral_1h_input_tokens":0,"ephemeral_5m_input_tokens":0},"inference_geo":"","iterations":[],"speed":"standard"},"modelUsage":{},"permission_denials":[],"terminal_reason":"api_error","fast_mode_state":"off","fast_mode_disabled_reason":"sdk_opt_in_required","subtype":"success","api_error_status":null,"result":"API Error: Can't reach the API server — check your internet or DNS (FailedToOpenSocket)","type":"result","duration_ms":176880,"uuid":"ebe1f4bc-c3e4-476d-877f-77213431854b"}
```
