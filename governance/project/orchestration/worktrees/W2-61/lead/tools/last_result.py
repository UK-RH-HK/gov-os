"""Print the last JSON object's result, session id and permission denials from a launched worker's log."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
start = text.rfind('{"type":"result"')
if start < 0:
    start = text.find("{")
doc = json.loads(text[start:])
print("session_id:", doc.get("session_id"))
print("denials:", json.dumps(doc.get("permission_denials"))[:3000])
print(doc.get("result"))
