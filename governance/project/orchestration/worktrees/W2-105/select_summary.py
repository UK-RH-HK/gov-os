import json, sys
d = json.load(open(sys.argv[1]))
for k, v in d.items():
    if isinstance(v, list):
        print(k, "list", len(v), v[:40] if k not in ("pytest_options",) else "")
    elif isinstance(v, dict):
        print(k, "dict", list(v)[:20])
    else:
        print(k, repr(v)[:300])
