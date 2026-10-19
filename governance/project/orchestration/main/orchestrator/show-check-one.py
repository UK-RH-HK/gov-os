"""Print the checks of one family of a gov check envelope, values of findings cut short: python3 show-check-one.py <label> <family part>."""
import json
import sys

L = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/"
d = json.load(open(L + "check-" + sys.argv[1] + ".json", encoding="utf-8"))
r = d.get("result") or d.get("error") or {}
details = r.get("details") or r
for c in details.get("checks") or []:
    if sys.argv[2] in c.get("family", "") or sys.argv[2] in c.get("id", ""):
        findings = c.get("findings") or []
        print(c.get("id"), c.get("status"), "findings:", len(findings), "provenance:", c.get("provenance"))
        print({k: (v if k != "findings" else "...") for k, v in c.items() if k not in ("provenance",)})
        for f in findings[:40]:
            print(" -", {k: v for k, v in f.items() if k != "stderr"})
            print(str(f.get("stderr", ""))[-3000:])
