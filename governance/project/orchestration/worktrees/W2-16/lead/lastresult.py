"""Print the session id, denials and result of the last JSON object in a worker's log."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
decoder, found, at = json.JSONDecoder(), None, 0
while True:
    start = text.find("{", at)
    if start < 0:
        break
    try:
        value, end = decoder.raw_decode(text, start)
    except ValueError:
        at = start + 1
        continue
    if isinstance(value, dict) and "result" in value:
        found = value
    at = end
if found is None:
    print(text[-3000:])
    sys.exit(1)
print("session_id:", found.get("session_id"), "| turns:", found.get("num_turns"), "| error:", found.get("is_error"))
print("permission_denials:", json.dumps(found.get("permission_denials"))[:3000])
print(found["result"])
