import json
import sys

text = open(sys.argv[1]).read()
dec = json.JSONDecoder()
last = None
i = 0
while True:
    j = text.find("{", i)
    if j < 0:
        break
    try:
        obj, end = dec.raw_decode(text, j)
        if isinstance(obj, dict) and "result" in obj:
            last = obj
        i = end
    except ValueError:
        i = j + 1
pre = text[: text.find("{")] if "{" in text else text
print("PRELUDE:", pre[:2000])
if last:
    print("SESSION:", last.get("session_id"), "is_error:", last.get("is_error"), "turns:", last.get("num_turns"))
    print(last.get("result"))
