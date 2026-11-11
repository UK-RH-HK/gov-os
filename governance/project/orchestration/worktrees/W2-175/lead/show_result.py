import json, sys
text = open(sys.argv[1], encoding="utf-8").read()
start = text.rfind('{"type"')
obj = None
for i in [start] + [j for j in range(len(text)) if text.startswith('{"', j)][::-1][:50]:
    try:
        obj = json.loads(text[i:].split("\n--- ")[0].strip())
        break
    except Exception:
        continue
if obj is None:
    print(text[-6000:])
else:
    r = obj.get("result", "")
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 4000
    print(r[:n])
