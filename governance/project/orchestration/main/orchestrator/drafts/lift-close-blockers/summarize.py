import json, sys
for t, rows in json.load(open(sys.argv[1])).items():
    f = [r for r in rows if r["gate"] != "_info"]
    kinds = {}
    for r in f:
        kinds[r["gate"]] = kinds.get(r["gate"], 0) + 1
    print(f"  {t}: {len(f)} findings {kinds}")
    for r in f:
        if not r["gate"].startswith("unmeasured") and not r["gate"].startswith("ratchet"):
            print("      ", r["gate"], "|", r["what"][:200])
