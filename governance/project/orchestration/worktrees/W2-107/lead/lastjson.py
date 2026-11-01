"""Prints the result of the last JSON object in a worker's log (the launcher's own lines may come first)."""
import json
import sys

text = open(sys.argv[1], encoding="utf-8", errors="replace").read()
decoder, found, at = json.JSONDecoder(), None, 0
while True:
    at = text.find("{", at)
    if at < 0:
        break
    try:
        value, end = decoder.raw_decode(text, at)
    except ValueError:
        at += 1
        continue
    if isinstance(value, dict) and "result" in value:
        found = value
    at = end
if found is None:
    print("no result object; tail:")
    print(text[-2000:])
else:
    print("session_id", found.get("session_id"), "turns", found.get("num_turns"), "ms", found.get("duration_ms"),
          "error", found.get("is_error"))
    print(found["result"])
