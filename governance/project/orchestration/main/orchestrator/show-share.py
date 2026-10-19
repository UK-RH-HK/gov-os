"""One line per share-<name>.json: python3 show-share.py <name> [<name> ...]."""
import json
import sys

L = "/home/usain/Dynamic-Agentic-Engineering-OS/.gov-runtime/scratch/orchestrator/log/"
for name in sys.argv[1:]:
    try:
        d = json.load(open(L + "share-" + name + ".json", encoding="utf-8"))
    except ValueError:
        print(name, ": no envelope;", open(L + "share-" + name + ".err", encoding="utf-8").read()[-300:])
        continue
    r = d.get("result") or d.get("error") or {}
    if not d.get("ok"):
        print(name, ": refused:", r.get("code"), "|", str(r.get("message"))[:300])
        continue
    g = r.get("governance_tokens", {})
    print(name, "| agent", r.get("agent"), "| share", r.get("governance_share"),
          "| gov total", g.get("total"), "| est", r.get("estimated_governance_tokens", {}).get("total"),
          "| out", r.get("tokens_out"), "| cost", r.get("cost"),
          "| not measured:", [(n.get("name"), n.get("reason")) for n in r.get("not_measured", [])])
