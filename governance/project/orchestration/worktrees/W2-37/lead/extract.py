"""Prints the launcher's lines and the last JSON object's result of a worker log; writes <log>.result.txt."""
import json
import sys

path = sys.argv[1]
text = open(path, encoding="utf-8").read()
decoder, objects, i = json.JSONDecoder(), [], 0
while i < len(text):
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = decoder.raw_decode(text, j)
        objects.append(obj)
        i = end
    except ValueError:
        i = j + 1
first = text.find("{")
print("before:", text[:first][:800] if first > 0 else "")
result = [o for o in objects if isinstance(o, dict) and "result" in o][-1]
for key in ("session_id", "is_error", "num_turns"):
    print(key, result.get(key))
open(path.rsplit(".", 1)[0] + ".result.txt", "w", encoding="utf-8").write(str(result["result"]))
print(result["result"])
