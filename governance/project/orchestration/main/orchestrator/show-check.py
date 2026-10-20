"""Print one line per family of a gov check envelope: python3 show-check.py <label> [family to print in full]."""
import json
import sys

L = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/"
d = json.load(open(L + "check-" + sys.argv[1] + ".json", encoding="utf-8"))
r = d.get("result") or d.get("error") or {}
print("ok:", d.get("ok"), "|", r.get("code"), "|", r.get("message"))
details = r.get("details") or r
fams = details.get("families") or {}
for name, f in fams.items():
    print(f"{f.get('status')!s:8} {name}")
    if len(sys.argv) > 2 and sys.argv[2] in name:
        print(json.dumps(f, indent=1)[:8000])
for k, v in details.items():
    if k != "families":
        print(k, ":", json.dumps(v)[:300])
