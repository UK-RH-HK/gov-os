import json, sys
# print the `result` of the last JSON object in a launch log
path = sys.argv[1]
text = open(path, encoding="utf-8", errors="replace").read()
last = None
for line in text.splitlines():
    line = line.strip()
    if line.startswith("{"):
        try:
            last = json.loads(line)
        except Exception:
            pass
if last is None:
    i = text.rfind('{"type"')
    last = json.loads(text[i:]) if i >= 0 else {}
print(last.get("result", "(no result)"))
