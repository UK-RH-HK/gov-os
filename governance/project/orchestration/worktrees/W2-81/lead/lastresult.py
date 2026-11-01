"""Print the last JSON object's result, session id and cost from a worker log."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
last = None
for start in range(len(text)):
    if text[start] == "{" and (start == 0 or text[start - 1] == "\n"):
        try:
            obj = json.loads(text[start:])
            last = obj
            break
        except ValueError:
            continue
if last is None:
    idx = text.rfind('{"type":"result"')
    if idx >= 0:
        last = json.loads(text[idx:])
if last is None:
    print("NO JSON RESULT; tail:")
    print(text[-2000:])
    sys.exit(1)
print("session_id:", last.get("session_id"))
print("is_error:", last.get("is_error"), "subtype:", last.get("subtype"), "turns:", last.get("num_turns"),
      "duration_s:", (last.get("duration_ms") or 0) // 1000)
print("----")
print(last.get("result"))
