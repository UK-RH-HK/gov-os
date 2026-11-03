"""Print the `result` of the last JSON object in a worker log (launcher lines may come first)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8").read()
start = text.rfind('{"')
while start >= 0:
    try:
        obj = json.loads(text[start:])
        print(obj.get("session_id"))
        print(obj.get("result"))
        break
    except ValueError:
        start = text.rfind('{"', 0, start)
else:
    print(text[-3000:])
