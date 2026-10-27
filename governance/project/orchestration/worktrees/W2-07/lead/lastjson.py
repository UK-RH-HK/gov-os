"""Print the `result` of the last JSON object in a worker log (the launcher's own lines may come first)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
start = text.rfind('{"type":"result"')
if start < 0:
    start = text.find('{"duration_api_ms"')
if start < 0:
    start = text.rfind("\n{") + 1
data = json.JSONDecoder().raw_decode(text[start:])[0]
print("session_id:", data.get("session_id"), "is_error:", data.get("is_error"), "turns:", data.get("num_turns"))
print(data.get("result"))
