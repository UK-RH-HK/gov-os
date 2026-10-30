"""Print the result of the last JSON object in a launch log (the launcher may print lines before it)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
start = text.rfind('{"')
obj = None
while start != -1:
    try:
        obj = json.loads(text[start:])
        break
    except json.JSONDecodeError:
        start = text.rfind('{"', 0, start)
if obj is None:
    print(text[:2000])
    sys.exit(1)
pre = text[:start].strip()
if pre:
    print("LAUNCHER LINES:\n" + pre[:2000] + "\n---")
for key in ("session_id", "is_error", "num_turns", "subtype"):
    print(f"{key}: {obj.get(key)}")
print(obj.get("result"))
